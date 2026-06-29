from __future__ import annotations

import asyncio

from app.core.rate_limiter import RateLimiter, RedisRateLimiter, build_rate_limiter


def test_in_memory_enforces_limit():
    limiter = RateLimiter(2)

    async def run():
        return [await limiter.is_allowed("user") for _ in range(3)]

    results = asyncio.run(run())
    assert results == [True, True, False]


def test_build_rate_limiter_defaults_to_memory():
    assert isinstance(build_rate_limiter(10), RateLimiter)
    assert isinstance(build_rate_limiter(10, backend="memory"), RateLimiter)


def test_build_rate_limiter_selects_redis():
    limiter = build_rate_limiter(10, backend="redis", redis_url="redis://127.0.0.1:6390/0")
    assert isinstance(limiter, RedisRateLimiter)


def test_redis_limiter_falls_back_when_unreachable():
    # Redis unreachable / package missing -> must still enforce via in-memory fallback.
    limiter = build_rate_limiter(1, backend="redis", redis_url="redis://127.0.0.1:6390/0")

    async def run():
        return [await limiter.is_allowed("user") for _ in range(2)]

    results = asyncio.run(run())
    assert results == [True, False]
