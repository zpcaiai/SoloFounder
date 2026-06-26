from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileUpsert(BaseModel):
    display_name: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    metadata: dict[str, Any] = {}


@router.get("")
async def get_profile(user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    repo = get_repositories().business
    items = await repo.list(user_id=user_id, entity_type="profiles")
    return items[0] if items else {"user_id": user_id, "display_name": None, "email": None}


@router.put("")
async def upsert_profile(
    body: ProfileUpsert,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    repo = get_repositories().business
    items = await repo.list(user_id=user_id, entity_type="profiles")
    data = body.model_dump(exclude_none=True)
    if items:
        entity_id_str = items[0]["id"]
        from uuid import UUID

        return await repo.update(entity_id=UUID(entity_id_str), user_id=user_id, data=data)
    return await repo.create(user_id=user_id, entity_type="profiles", data=data)
