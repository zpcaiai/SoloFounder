from __future__ import annotations

import asyncio
from collections import Counter


class MetricsCollector:
    """Lightweight, in-memory Prometheus-style metrics collector."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._requests: Counter[tuple[str, str, int]] = Counter()

    async def record_request(self, method: str, path: str, status_code: int) -> None:
        async with self._lock:
            self._requests[(method, path, status_code)] += 1

    def render(self) -> str:
        lines = [
            "# HELP revenuepilot_requests_total Total HTTP requests",
            "# TYPE revenuepilot_requests_total counter",
        ]
        for (method, path, status_code), count in sorted(self._requests.items()):
            safe_path = path.replace('"', '\\"')
            lines.append(
                f'revenuepilot_requests_total{{method="{method}",path="{safe_path}",status="{status_code}"}} {count}'
            )
        return "\n".join(lines) + "\n"
