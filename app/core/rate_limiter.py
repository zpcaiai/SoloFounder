from __future__ import annotations

import asyncio
import time
from collections.abc import MutableMapping


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
