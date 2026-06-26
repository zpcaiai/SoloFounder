from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import LandingPageCreate, LandingPageUpdate

router = APIRouter(prefix="/api/projects/{project_id}/landing-pages", tags=["landing-pages"])


@router.post("")
async def create_landing_page(
    project_id: str,
    body: LandingPageCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="landing_pages",
        data=body.model_dump(),
    )


@router.get("")
async def list_landing_pages(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="landing_pages",
        project_id=project_id,
    )


@router.get("/{landing_page_id}")
async def get_landing_page(
    project_id: str,
    landing_page_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(landing_page_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Landing page not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your landing page") from None


@router.put("/{landing_page_id}")
async def update_landing_page(
    project_id: str,
    landing_page_id: str,
    body: LandingPageUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(landing_page_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Landing page not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your landing page") from None


@router.delete("/{landing_page_id}")
async def delete_landing_page(
    project_id: str,
    landing_page_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(landing_page_id), user_id=user_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Landing page not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your landing page") from None


@router.post("/{landing_page_id}/publish")
async def publish_landing_page(
    project_id: str,
    landing_page_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(landing_page_id),
            user_id=user_id,
            data={"published": True},
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Landing page not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your landing page") from None


@router.post("/{landing_page_id}/unpublish")
async def unpublish_landing_page(
    project_id: str,
    landing_page_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(landing_page_id),
            user_id=user_id,
            data={"published": False},
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Landing page not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your landing page") from None
