from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("")
async def create_project(body: ProjectCreate, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        entity_type="projects",
        data=body.model_dump(),
    )


@router.get("")
async def list_projects(user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(user_id=user_id, entity_type="projects")


@router.get("/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(project_id), user_id=user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Project not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your project") from None


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    body: ProjectUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(project_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Project not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your project") from None


@router.delete("/{project_id}")
async def delete_project(project_id: str, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(project_id), user_id=user_id)
        return {"status": "deleted"}
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Project not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your project") from None
