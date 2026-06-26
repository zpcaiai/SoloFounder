from __future__ import annotations

import secrets
from typing import Any

from fastapi import Header, HTTPException

from app.core.config import get_settings


def _decode_jwt(token: str, secret: str) -> dict[str, Any]:
    try:
        import jwt  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyJWT is required for Supabase JWT auth.") from exc

    try:
        payload: dict[str, Any] = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


async def current_user_id(
    x_user_id: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> str:
    settings = get_settings()

    if settings.is_production and not settings.api_key and not settings.supabase_jwt_secret:
        raise HTTPException(status_code=503, detail="API authentication is not configured")

    if settings.api_key and (not x_api_key or not secrets.compare_digest(x_api_key, settings.api_key)):
        if not settings.supabase_jwt_secret:
            raise HTTPException(status_code=401, detail="Invalid API key")

    if authorization and settings.supabase_jwt_secret:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        payload = _decode_jwt(token, settings.supabase_jwt_secret)
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Token missing 'sub' claim")
        return str(sub)

    if x_user_id:
        return x_user_id

    if settings.is_production:
        raise HTTPException(status_code=401, detail="X-User-Id is required")

    return "demo-user"
