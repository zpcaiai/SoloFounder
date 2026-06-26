from __future__ import annotations

import logging

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.skills import router as skills_router
from app.api.routes.workflows import router as workflows_router
from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.core.metrics import MetricsCollector
from app.core.middleware import RequestContextMiddleware
from app.core.rate_limiter import RateLimiter
from app.repositories.factory import get_repositories

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title="RevenuePilot OS", lifespan=lifespan)

    metrics_collector = MetricsCollector() if settings.metrics_enabled else None
    app.add_middleware(
        RequestContextMiddleware,
        rate_limiter=RateLimiter(settings.rate_limit_per_minute),
        metrics_collector=metrics_collector,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(skills_router)
    app.include_router(workflows_router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )

    @app.get("/health")
    async def health() -> dict[str, str]:
        result = {"service": "RevenuePilot OS", "status": "ok"}
        if settings.use_postgres:
            try:
                pool = getattr(get_repositories().skill_runs, "pool", None)
                if pool and await pool.health_check():
                    result["database"] = "connected"
                else:
                    result["database"] = "unreachable"
                    result["status"] = "degraded"
            except Exception as exc:
                result["database"] = "error"
                result["status"] = "degraded"
                result["database_error"] = str(exc)
                logger.warning("health_check database_error=%s", exc)
        else:
            result["database"] = "memory"
        return result

    if settings.metrics_enabled and metrics_collector is not None:
        @app.get("/metrics", response_class=PlainTextResponse)
        async def metrics() -> str:
            return metrics_collector.render()

    ui_path = Path(__file__).resolve().parent / "static" / "index.html"
    if ui_path.is_file():
        ui_html = ui_path.read_text(encoding="utf-8")

        @app.get("/{path:path}")
        async def spa_catch_all(path: str) -> HTMLResponse:
            return HTMLResponse(content=ui_html)

    return app


app = create_app()
