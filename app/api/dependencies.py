from __future__ import annotations

from fastapi import Header, HTTPException

from app.core.config import get_settings


async def current_user_id(
    x_user_id: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> str:
    settings = get_settings()

    if settings.environment == "production" and not settings.api_key:
        raise HTTPException(status_code=503, detail="API authentication is not configured")

    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if x_user_id:
        return x_user_id

    if settings.environment == "production":
        raise HTTPException(status_code=401, detail="X-User-Id is required")

    return "demo-user"
