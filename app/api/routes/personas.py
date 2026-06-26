from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import PersonaCreate, PersonaUpdate
from app.services.skill_runner import skill_runner

router = APIRouter(prefix="/api/projects/{project_id}/personas", tags=["personas"])


@router.post("")
async def create_persona(
    project_id: str,
    body: PersonaCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="personas",
        data=body.model_dump(),
    )


@router.get("")
async def list_personas(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="personas",
        project_id=project_id,
    )


@router.get("/{persona_id}")
async def get_persona(
    project_id: str,
    persona_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(persona_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Persona not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your persona") from None


@router.put("/{persona_id}")
async def update_persona(
    project_id: str,
    persona_id: str,
    body: PersonaUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(persona_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Persona not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your persona") from None


@router.delete("/{persona_id}")
async def delete_persona(
    project_id: str,
    persona_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(persona_id), user_id=user_id)
        return {"status": "deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Persona not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your persona") from None


@router.post("/generate")
async def generate_persona(
    project_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="customer_persona",
        input_payload={"project_id": project_id},
    )


@router.post("/{persona_id}/generate-interview")
async def generate_interview(
    project_id: str,
    persona_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        persona = await get_repositories().business.get(entity_id=UUID(persona_id), user_id=user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Persona not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your persona") from None

    return await skill_runner.run(
        user_id=user_id,
        project_id=project_id,
        skill_name="pain_interview",
        input_payload={"persona": persona.get("data", {})},
        related_entity_type="personas",
        related_entity_id=persona_id,
    )
