from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import IdeaCreate, IdeaUpdate
from app.services.skill_runner import skill_runner

router = APIRouter(prefix="/api/projects/{project_id}/ideas", tags=["ideas"])


@router.post("")
async def create_idea(
    project_id: str,
    body: IdeaCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="ideas",
        data=body.model_dump(),
    )


@router.get("")
async def list_ideas(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="ideas",
        project_id=project_id,
    )


@router.get("/{idea_id}")
async def get_idea(project_id: str, idea_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(idea_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Idea not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your idea") from None


@router.put("/{idea_id}")
async def update_idea(
    project_id: str,
    idea_id: str,
    body: IdeaUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(idea_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Idea not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your idea") from None


@router.delete("/{idea_id}")
async def delete_idea(project_id: str, idea_id: str, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(idea_id), user_id=user_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Idea not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your idea") from None


@router.post("/generate")
async def generate_ideas(
    project_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="founder_profile_diagnosis",
        input_payload={"project_id": project_id},
    )


@router.post("/{idea_id}/convert-to-offer")
async def convert_idea_to_offer(
    project_id: str,
    idea_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        idea = await get_repositories().business.get(entity_id=UUID(idea_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Idea not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your idea") from None

    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="productized_offer",
        input_payload={
            "founder_profile": {},
            "selected_niche": idea.get("data", {}).get("target_customer", ""),
            "customer_persona": {},
            "validated_pain": idea.get("data", {}),
        },
        related_entity_type="ideas",
        related_entity_id=idea_id,
    )
