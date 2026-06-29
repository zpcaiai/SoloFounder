from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import MutableMapping
from typing import Protocol

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory token-bucket rate limiter keyed by caller.

    Suitable for a single process. In a horizontally scaled deployment this
    becomes a per-instance limit, which is usually acceptable for a small
    service; switch to a shared store (Redis) if you need global limits.
    """

    def __init__(self, requests_per_minute: int) -> None:
        self._rate = max(requests_per_minute / 60.0, 0.0)
        self._capacity = max(requests_per_minute, 1)
        self._buckets: MutableMapping[str, tuple[float, float]] = {}
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> bool:
        async with self._lock:
            now = time.monotonic()
            tokens, last = self._buckets.get(key, (self._capacity, now))
            tokens = min(self._capacity, tokens + self._rate * (now - last))
            if tokens >= 1:
                self._buckets[key] = (tokens - 1, now)
                return True
            self._buckets[key] = (tokens, now)
            return False

    async def reset(self) -> None:
        async with self._lock:
            self._buckets.clear()


class RateLimiterProtocol(Protocol):
    async def is_allowed(self, key: str) -> bool: ...
    async def reset(self) -> None: ...


class RedisRateLimiter:
    """Fixed-window rate limiter backed by Redis for multi-instance deployments.

    Uses a per-key, per-minute counter (INCR + EXPIRE). Falls back to an
    in-process limiter if the ``redis`` package is missing or Redis becomes
    unreachable, so a Redis outage degrades gracefully instead of failing
    every request.
    """

    def __init__(self, requests_per_minute: int, redis_url: str) -> None:
        self._limit = max(requests_per_minute, 1)
        self._fallback = RateLimiter(requests_per_minute)
        self._client = None
        self._degraded = False
        try:
            import redis.asyncio as redis_asyncio  # type: ignore
        except ModuleNotFoundError:
            logger.warning(
                "redis package not installed; rate limiting falls back to in-memory. "
                "Install it with: pip install redis"
            )
            self._degraded = True
            return
        try:
            self._client = redis_asyncio.from_url(
                redis_url, encoding="utf-8", decode_responses=True
            )
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.warning("Redis rate limiter init failed (%s); using in-memory fallback.", exc)
            self._degraded = True

    async def is_allowed(self, key: str) -> bool:
        if self._degraded or self._client is None:
            return await self._fallback.is_allowed(key)
        try:
            window = int(time.time() // 60)
            redis_key = f"rl:{key}:{window}"
            count = await self._client.incr(redis_key)
            if count == 1:
                await self._client.expire(redis_key, 60)
            return count <= self._limit
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.warning("Redis rate limiter error (%s); falling back to in-memory.", exc)
            self._degraded = True
            return await self._fallback.is_allowed(key)

    async def reset(self) -> None:
        await self._fallback.reset()
        if self._client is not None and not self._degraded:
            try:  # pragma: no cover - depends on environment
                async for redis_key in self._client.scan_iter("rl:*"):
                    await self._client.delete(redis_key)
            except Exception:
                pass


def build_rate_limiter(requests_per_minute: int, *, backend: str = "memory", redis_url: str | None = None) -> RateLimiterProtocol:
    """Pick the rate-limiter implementation from configuration."""
    if backend == "redis" and redis_url:
        return RedisRateLimiter(requests_per_minute, redis_url)
    return RateLimiter(requests_per_minute)
