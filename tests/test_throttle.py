import asyncio

import httpx

from daily.throttle import PoliteTransport


def _transport(responses: list[httpx.Response], sleeps: list[float], **kwargs) -> PoliteTransport:
    queue = list(responses)

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    inner = httpx.MockTransport(lambda request: queue.pop(0) if queue else httpx.Response(200))
    return PoliteTransport(inner, sleep=fake_sleep, **kwargs)


async def test_concurrent_requests_to_a_throttled_host_are_spaced_out():
    sleeps: list[float] = []
    transport = _transport([], sleeps, min_interval={"www.reddit.com": 3.0})
    async with httpx.AsyncClient(transport=transport) as client:
        await asyncio.gather(
            client.get("https://www.reddit.com/r/LocalLLaMA/top/.rss"),
            client.get("https://www.reddit.com/r/MachineLearning/top/.rss"),
            client.get("https://hn.algolia.com/api/v1/search_by_date"),
        )
    assert len(sleeps) == 1 and 2.9 < sleeps[0] <= 3.0


async def test_429_is_retried_after_retry_after():
    sleeps: list[float] = []
    transport = _transport([httpx.Response(429, headers={"Retry-After": "7"})], sleeps, min_interval={})
    async with httpx.AsyncClient(transport=transport) as client:
        response = await client.get("https://www.reddit.com/r/LocalLLaMA/top/.rss")
    assert response.status_code == 200
    assert sleeps == [7.0]


async def test_429_without_retry_after_waits_for_the_rate_limit_reset():
    sleeps: list[float] = []
    transport = _transport(
        [httpx.Response(429, headers={"x-ratelimit-reset": "42"})], sleeps, min_interval={}
    )
    async with httpx.AsyncClient(transport=transport) as client:
        response = await client.get("https://www.reddit.com/r/LocalLLaMA+MachineLearning/top/.rss")
    assert response.status_code == 200
    assert sleeps == [43.0]


async def test_persistent_429_gives_up_with_backoff_and_a_cap():
    sleeps: list[float] = []
    transport = _transport(
        [httpx.Response(429), httpx.Response(429), httpx.Response(429, headers={"Retry-After": "600"})],
        sleeps,
        min_interval={},
        max_retries=2,
        backoff=5.0,
    )
    async with httpx.AsyncClient(transport=transport) as client:
        response = await client.get("https://www.reddit.com/r/LocalLLaMA/top/.rss")
    assert response.status_code == 429
    assert sleeps == [5.0, 10.0]


async def test_long_retry_after_is_capped():
    sleeps: list[float] = []
    transport = _transport([httpx.Response(503, headers={"Retry-After": "600"})], sleeps, min_interval={})
    async with httpx.AsyncClient(transport=transport) as client:
        assert (await client.get("https://example.com/")).status_code == 200
    assert sleeps == [65.0]
