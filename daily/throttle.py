"""Polite HTTP: space out requests to rate-limited hosts and retry 429 / 503 after a pause.

Sources run concurrently, so two sources on the same host (r/LocalLLaMA and r/MachineLearning)
would otherwise hit it in the same instant; Reddit answers the second one with 429.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

import httpx

logger = logging.getLogger(__name__)

# Minimum seconds between the starts of two requests to the same host.
HOST_MIN_INTERVAL = {"www.reddit.com": 3.0}
RETRY_STATUSES = {429, 503}


class PoliteTransport(httpx.AsyncBaseTransport):
    def __init__(
        self,
        inner: httpx.AsyncBaseTransport,
        min_interval: dict[str, float] | None = None,
        max_retries: int = 2,
        backoff: float = 5.0,
        max_wait: float = 20.0,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.inner = inner
        self.min_interval = HOST_MIN_INTERVAL if min_interval is None else min_interval
        self.max_retries = max_retries
        self.backoff = backoff
        self.max_wait = max_wait
        self.sleep = sleep
        self._locks: dict[str, asyncio.Lock] = {}
        self._last_start: dict[str, float] = {}

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        retries = self.max_retries if request.method in ("GET", "HEAD") else 0
        for attempt in range(retries + 1):
            await self._wait_turn(request.url.host)
            response = await self.inner.handle_async_request(request)
            if response.status_code not in RETRY_STATUSES or attempt == retries:
                return response
            delay = self._retry_delay(response, attempt)
            await response.aclose()
            logger.info("%s from %s, retrying in %.0fs", response.status_code, request.url.host, delay)
            await self.sleep(delay)
        raise AssertionError("unreachable")

    async def aclose(self) -> None:
        await self.inner.aclose()

    async def _wait_turn(self, host: str) -> None:
        interval = self.min_interval.get(host)
        if not interval:
            return
        async with self._locks.setdefault(host, asyncio.Lock()):
            last = self._last_start.get(host)
            if last is not None:
                wait = last + interval - time.monotonic()
                if wait > 0:
                    await self.sleep(wait)
            self._last_start[host] = time.monotonic()

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        try:
            delay = float(response.headers.get("retry-after", ""))
        except ValueError:  # missing, or an HTTP date
            delay = self.backoff * 2**attempt
        return min(max(delay, 0.0), self.max_wait)
