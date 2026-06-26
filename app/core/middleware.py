from __future__ import annotations

import asyncio
import logging
import time
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import get_settings
from app.core.metrics import MetricsCollector
from app.core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


def _error_response(status_code: int, detail: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "request_id": request_id},
        headers={"X-Request-ID": request_id},
    )


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Sets request ID, enforces body-size / rate limits, adds security headers, and logs requests."""

    def __init__(
        self,
        app,
        rate_limiter: RateLimiter | None = None,
        metrics_collector: MetricsCollector | None = None,
    ) -> None:
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.metrics_collector = metrics_collector

    async def _record(self, method: str, path: str, status_code: int) -> None:
        if self.metrics_collector is not None:
            await self.metrics_collector.record_request(method, path, status_code)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        settings = get_settings()
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id

        # Body size guard (best-effort based on Content-Length)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > settings.max_request_body_size:
                    await self._record(request.method, request.url.path, 413)
                    return _error_response(413, "Request body too large", request_id)
            except ValueError:
                pass

        # Rate limit by caller (falls back to IP-aware key if no X-User-Id)
        if self.rate_limiter is not None:
            user_id = request.headers.get("X-User-Id")
            if not user_id:
                forwarded = request.headers.get("x-forwarded-for")
                user_id = forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else "anonymous"
            if not await self.rate_limiter.is_allowed(user_id):
                await self._record(request.method, request.url.path, 429)
                return _error_response(429, "Rate limit exceeded", request_id)

        start = time.perf_counter()
        try:
            response = await asyncio.wait_for(call_next(request), timeout=settings.request_timeout)
        except TimeoutError:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.warning(
                "request_timeout request_id=%s method=%s path=%s duration_ms=%s",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )
            await self._record(request.method, request.url.path, 504)
            return _error_response(504, "Request timeout", request_id)
        except StarletteHTTPException as exc:
            await self._record(request.method, request.url.path, exc.status_code)
            raise
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "request_failed request_id=%s method=%s path=%s duration_ms=%s error=%s",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
                exc.__class__.__name__,
            )
            await self._record(request.method, request.url.path, 500)
            return _error_response(500, "Internal server error", request_id)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        # Do not log the API key if it was supplied.
        logger.info(
            "request_completed request_id=%s method=%s path=%s status_code=%s duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        await self._record(request.method, request.url.path, response.status_code)
        return response
