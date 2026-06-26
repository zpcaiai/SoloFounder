from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import OutreachCreate, OutreachUpdate

router = APIRouter(prefix="/api/projects/{project_id}/outreach", tags=["outreach"])


@router.post("")
async def create_outreach(
    project_id: str,
    body: OutreachCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="outreach",
        data=body.model_dump(),
    )


@router.get("")
async def list_outreach(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="outreach",
        project_id=project_id,
    )


@router.get("/{outreach_id}")
async def get_outreach(
    project_id: str,
    outreach_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(outreach_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Outreach asset not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your outreach asset") from None


@router.put("/{outreach_id}")
async def update_outreach(
    project_id: str,
    outreach_id: str,
    body: OutreachUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(outreach_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Outreach asset not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your outreach asset") from None


@router.delete("/{outreach_id}")
async def delete_outreach(
    project_id: str,
    outreach_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(outreach_id), user_id=user_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Outreach asset not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your outreach asset") from None


@router.post("/{outreach_id}/approve")
async def approve_outreach(
    project_id: str,
    outreach_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(outreach_id),
            user_id=user_id,
            data={"human_approval_required": False, "approved": True},
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Outreach asset not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your outreach asset") from None
