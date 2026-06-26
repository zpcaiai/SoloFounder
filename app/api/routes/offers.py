from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import OfferCreate, OfferUpdate
from app.services.skill_runner import skill_runner

router = APIRouter(prefix="/api/projects/{project_id}/offers", tags=["offers"])


@router.post("")
async def create_offer(
    project_id: str,
    body: OfferCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="offers",
        data=body.model_dump(),
    )


@router.get("")
async def list_offers(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="offers",
        project_id=project_id,
    )


@router.get("/{offer_id}")
async def get_offer(project_id: str, offer_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(offer_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Offer not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your offer") from None


@router.put("/{offer_id}")
async def update_offer(
    project_id: str,
    offer_id: str,
    body: OfferUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(offer_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Offer not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your offer") from None


@router.delete("/{offer_id}")
async def delete_offer(project_id: str, offer_id: str, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(offer_id), user_id=user_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Offer not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your offer") from None


@router.post("/{offer_id}/generate-landing-page")
async def generate_landing_page(
    project_id: str,
    offer_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        offer = await get_repositories().business.get(entity_id=UUID(offer_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Offer not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your offer") from None

    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="landing_page",
        input_payload={"offer": offer.get("data", {}), "persona": {}},
        related_entity_type="offers",
        related_entity_id=offer_id,
    )


@router.post("/{offer_id}/generate-outreach-kit")
async def generate_outreach_kit(
    project_id: str,
    offer_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        offer = await get_repositories().business.get(entity_id=UUID(offer_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Offer not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your offer") from None

    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="sales_outreach",
        input_payload={
            "offer": offer.get("data", {}),
            "persona": {},
            "channel": "email_linkedin_wechat",
            "human_approval_required": True,
        },
        related_entity_type="offers",
        related_entity_id=offer_id,
    )
