from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import LeadCreate, LeadUpdate

router = APIRouter(prefix="/api/projects/{project_id}/leads", tags=["leads"])


@router.post("")
async def create_lead(
    project_id: str,
    body: LeadCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="leads",
        data=body.model_dump(),
    )


@router.get("")
async def list_leads(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="leads",
        project_id=project_id,
    )


@router.get("/{lead_id}")
async def get_lead(project_id: str, lead_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(lead_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Lead not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your lead") from None


@router.put("/{lead_id}")
async def update_lead(
    project_id: str,
    lead_id: str,
    body: LeadUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(lead_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Lead not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your lead") from None


@router.delete("/{lead_id}")
async def delete_lead(project_id: str, lead_id: str, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(lead_id), user_id=user_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Lead not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your lead") from None
