from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import DealCreate, DealUpdate
from app.services.skill_runner import skill_runner

router = APIRouter(prefix="/api/projects/{project_id}/deals", tags=["deals"])


@router.post("")
async def create_deal(
    project_id: str,
    body: DealCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="deals",
        data=body.model_dump(),
    )


@router.get("")
async def list_deals(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="deals",
        project_id=project_id,
    )


@router.get("/{deal_id}")
async def get_deal(project_id: str, deal_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(deal_id), user_id=user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Deal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your deal") from None


@router.put("/{deal_id}")
async def update_deal(
    project_id: str,
    deal_id: str,
    body: DealUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(deal_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Deal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your deal") from None


@router.delete("/{deal_id}")
async def delete_deal(project_id: str, deal_id: str, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(deal_id), user_id=user_id)
        return {"status": "deleted"}
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Deal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your deal") from None


@router.post("/{deal_id}/mark-won")
async def mark_deal_won(project_id: str, deal_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(deal_id),
            user_id=user_id,
            data={"stage": "won"},
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Deal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your deal") from None


@router.post("/{deal_id}/mark-lost")
async def mark_deal_lost(project_id: str, deal_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(deal_id),
            user_id=user_id,
            data={"stage": "lost"},
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Deal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your deal") from None


@router.post("/{deal_id}/generate-proposal")
async def generate_proposal(
    project_id: str,
    deal_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        deal = await get_repositories().business.get(entity_id=UUID(deal_id), user_id=user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Deal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your deal") from None

    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="proposal",
        input_payload={"deal": deal.get("data", {}), "offer": {}},
        related_entity_type="deals",
        related_entity_id=deal_id,
    )


@router.post("/{deal_id}/generate-delivery-project")
async def generate_delivery_project(
    project_id: str,
    deal_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        deal = await get_repositories().business.get(entity_id=UUID(deal_id), user_id=user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Deal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your deal") from None

    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="delivery_project",
        input_payload={"deal": deal.get("data", {}), "offer": {}},
        related_entity_type="deals",
        related_entity_id=deal_id,
    )
