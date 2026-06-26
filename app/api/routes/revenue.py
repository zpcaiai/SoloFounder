from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import RevenueCreate, RevenueUpdate

router = APIRouter(prefix="/api/projects/{project_id}/revenue", tags=["revenue"])


@router.post("")
async def create_revenue(
    project_id: str,
    body: RevenueCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="revenue",
        data=body.model_dump(),
    )


@router.get("")
async def list_revenue(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="revenue",
        project_id=project_id,
    )


@router.get("/{revenue_id}")
async def get_revenue(
    project_id: str,
    revenue_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(revenue_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Revenue record not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your revenue record") from None


@router.put("/{revenue_id}")
async def update_revenue(
    project_id: str,
    revenue_id: str,
    body: RevenueUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(revenue_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Revenue record not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your revenue record") from None


@router.delete("/{revenue_id}")
async def delete_revenue(
    project_id: str,
    revenue_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(revenue_id), user_id=user_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Revenue record not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your revenue record") from None


@router.get("/summary/total")
async def revenue_summary(project_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    records = await get_repositories().business.list(
        user_id=user_id,
        entity_type="revenue",
        project_id=project_id,
    )
    total = sum(float(r.get("data", {}).get("amount", 0)) for r in records)
    return {"total_revenue": total, "count": len(records)}
