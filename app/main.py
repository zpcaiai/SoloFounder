from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.skills import router as skills_router
from app.api.routes.workflows import router as workflows_router


def create_app() -> FastAPI:
    app = FastAPI(title="RevenuePilot OS")
    app.include_router(skills_router)
    app.include_router(workflows_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"service": "RevenuePilot OS", "status": "ok"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
