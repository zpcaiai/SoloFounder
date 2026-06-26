from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.repositories.factory import close_repository_bundle, get_repositories

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    settings = get_settings()
    configure_logging()
    logger.info(
        "startup environment=%s use_postgres=%s ai_provider=%s",
        settings.environment,
        settings.use_postgres,
        settings.ai_provider,
    )

    if settings.use_postgres:
        try:
            repositories = get_repositories()
            # Touch the pool early so connection failures surface on startup.
            pool = await repositories.skill_runs.pool.pool()  # type: ignore[attr-defined]

            if not settings.skip_db_migration:
                from app.core.migrations import apply_pending_migrations

                await apply_pending_migrations(pool)
        except Exception:
            logger.exception("Database initialization failed on startup")
            # Do not crash the server; health checks will report degraded state.

    yield

    await close_repository_bundle()
    logger.info("shutdown complete")
