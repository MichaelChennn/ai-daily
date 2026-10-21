from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from datetime import date, datetime, timezone

import httpx
import pytest

from daily.config import SourceConfig
from daily.window import issue_window

# Issue 2026-10-20 covers 2026-10-19T02:00Z .. 2026-10-20T04:00Z (04:00 .. 06:00 Berlin time, CEST).
ISSUE = date(2026, 10, 20)
IN_WINDOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
BEFORE_WINDOW = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def window():
    return issue_window(ISSUE, now=datetime(2026, 10, 20, 0, 0, tzinfo=timezone.utc))


def source(type_: str, kind: str = "blog", tier: int = 1, id_: str | None = None, **options) -> SourceConfig:
    return SourceConfig(id=id_ or type_, type=type_, name=id_ or type_, tier=tier, kind=kind, options=options)


Route = Callable[[httpx.Request], httpx.Response]


def mock_client(routes: dict[str, object]) -> httpx.AsyncClient:
    """routes: "host/path" -> str | bytes | dict | list | httpx.Response | exception."""

    def handler(request: httpx.Request) -> httpx.Response:
        body = routes.get(f"{request.url.host}{request.url.path}")
        if body is None:
            return httpx.Response(404, text="not mocked")
        if isinstance(body, Exception):
            raise body
        if isinstance(body, httpx.Response):
            return body
        if isinstance(body, (dict, list)):
            return httpx.Response(200, json=body)
        return httpx.Response(200, content=body.encode() if isinstance(body, str) else body)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """Run `async def` tests without needing pytest-asyncio."""
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        args = {name: pyfuncitem.funcargs[name] for name in pyfuncitem._fixtureinfo.argnames}
        asyncio.run(pyfuncitem.obj(**args))
        return True
    return None
