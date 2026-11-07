"""Chat completions for the API route (daily.api_editor): providers, HTTP, streaming and retries.

One OpenAI compatible client (chat completions) for every provider: a model is named
"provider:model" (EDITOR_API_MODEL), and PROVIDERS gives each provider's base_url and the
environment variable holding its key. Adding a provider is one line.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Provider:
    base_url: str
    key_env: str
    min_interval: float  # seconds between requests, to stay under the free tier's requests per minute


PROVIDERS = {
    "nvidia": Provider("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY", 2.0),
}
RETRIES = 3  # after the first attempt
RETRY_DELAY = 15.0  # doubled on each retry, unless the provider says how long (Retry-After)
# Replies stream in, so the limit is on silence, not on the whole reply: NVIDIA NIM may prefill a long
# prompt for minutes before the first token.
CHAT_TIMEOUT = httpx.Timeout(30.0, read=600.0)
MAX_TOKENS = 16384  # reasoning counts too


class LLMError(Exception):
    """A model that cannot be used, or a request that failed for good."""


async def _sleep(seconds: float) -> None:  # replaced in tests
    await asyncio.sleep(seconds)


def resolve(model: str) -> tuple[Provider, str, str]:
    """ "provider:model" -> (provider, model name, API key); LLMError when unknown or unset."""
    name, _, model_name = model.partition(":")
    provider = PROVIDERS.get(name)
    if provider is None or not model_name:
        raise LLMError(f"model must be provider:model with provider one of {list(PROVIDERS)}: {model!r}")
    key = os.environ.get(provider.key_env)
    if not key:
        raise LLMError(f"{provider.key_env} is not set")
    return provider, model_name, key


WHOLE = ("id", "type", "role", "name")  # streamed fields that are not text in pieces


def _merge(message: dict[str, Any], delta: dict[str, Any]) -> None:
    """Add one streamed delta to the message: text arrives in pieces, the rest whole."""
    for key, value in delta.items():
        if key == "tool_calls":
            calls = message.setdefault("tool_calls", [])
            for part in value:
                index = part.get("index", len(calls))
                while len(calls) <= index:
                    calls.append({})
                _merge(calls[index], {k: v for k, v in part.items() if k != "index"})
        elif isinstance(value, dict):
            _merge(message.setdefault(key, {}), value)
        elif isinstance(value, str) and isinstance(message.get(key), str) and key not in WHOLE:
            message[key] += value
        elif value is not None:
            message[key] = value


SKIPPED_KEPT = 5  # non-empty lines that are not events, kept to say what went wrong


@dataclass
class Reply:
    """The assistant message of a streamed reply, and how the stream ended."""

    message: dict[str, Any]
    finish_reason: str | None = None  # "stop"; "length" when max_tokens cut it off
    done: bool = False  # the stream ended with [DONE]
    skipped: list[str] = field(default_factory=list)  # lines that were not events: a bare error?

    @property
    def content(self) -> str:
        return self.message.get("content") or ""

    def describe(self) -> str:
        """How the stream ended, for the log."""
        skipped = f", lines that were not events: {self.skipped}" if self.skipped else ""
        return f"finish_reason {self.finish_reason}, [DONE] {'seen' if self.done else 'missing'}{skipped}"


async def _read_stream(response: httpx.Response) -> Reply:
    """The reply from a chat completions event stream. A stream that ends without both [DONE] and a
    finish_reason was cut off: httpx.RemoteProtocolError, for Chat.send to send the request again."""
    reply = Reply({"role": "assistant", "content": None})
    async for line in response.aiter_lines():
        if not line.startswith("data:"):
            if line.strip() and not line.startswith(":") and len(reply.skipped) < SKIPPED_KEPT:
                reply.skipped.append(line.strip()[:300])  # ": ..." lines are SSE comments
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            reply.done = True
            break
        chunk = json.loads(data)
        if "error" in chunk:
            raise httpx.RemoteProtocolError(f"error in the stream: {str(chunk['error'])[:300]}")
        for choice in chunk.get("choices") or []:
            _merge(reply.message, choice.get("delta") or {})
            reply.finish_reason = choice.get("finish_reason") or reply.finish_reason
    if not reply.done or reply.finish_reason is None:
        raise httpx.RemoteProtocolError(f"the stream ended early ({reply.describe()})")
    return reply


class Chat:
    """Chat completions against one provider, paced and retried for the free tiers."""

    def __init__(self, model: str, client: httpx.AsyncClient) -> None:
        self.provider, self.name, self.key = resolve(model)
        self.client = client
        self.last_request = 0.0

    async def send(self, messages: list[dict[str, Any]]) -> Reply:
        url = self.provider.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.name,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "stream": True,
            # Every reply is a JSON object: JSON mode has the provider hold the model to valid JSON.
            "response_format": {"type": "json_object"},
        }
        for attempt in range(1, RETRIES + 2):
            wait = self.last_request + self.provider.min_interval - time.monotonic()
            if wait > 0:
                await _sleep(wait)
            self.last_request = time.monotonic()
            status, delay = 0, RETRY_DELAY * 2 ** (attempt - 1)
            try:
                headers = {"Authorization": f"Bearer {self.key}"}
                async with self.client.stream(
                    "POST", url, json=payload, headers=headers, timeout=CHAT_TIMEOUT
                ) as response:
                    status = response.status_code
                    if status == 200:
                        return await _read_stream(response)
                    problem = f"HTTP {status}: {(await response.aread()).decode(errors='replace')[:300]}"
                    if response.headers.get("retry-after", "").isdigit():
                        delay = float(response.headers["retry-after"])
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                problem = f"{type(exc).__name__}: {exc}"
            if status not in (0, 200, 429) and status < 500:
                raise LLMError(problem)
            log.warning("chat request %d/%d failed: %s", attempt, RETRIES + 1, problem)
            if attempt > RETRIES:
                raise LLMError(problem)
            await _sleep(delay)
        raise AssertionError("unreachable")
