from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import DeliveryProjectCreate, DeliveryProjectUpdate, DeliveryTaskCreate, DeliveryTaskUpdate

router = APIRouter(prefix="/api/projects/{project_id}/delivery", tags=["delivery"])


@router.post("/projects")
async def create_delivery_project(
    project_id: str,
    body: DeliveryProjectCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="delivery_projects",
        data=body.model_dump(),
    )


@router.get("/projects")
async def list_delivery_projects(
    project_id: str,
    user_id: str = Depends(current_user_id),
) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="delivery_projects",
        project_id=project_id,
    )


@router.get("/projects/{delivery_project_id}")
async def get_delivery_project(
    project_id: str,
    delivery_project_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(delivery_project_id), user_id=user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Delivery project not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your delivery project") from None


@router.put("/projects/{delivery_project_id}")
async def update_delivery_project(
    project_id: str,
    delivery_project_id: str,
    body: DeliveryProjectUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(delivery_project_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Delivery project not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your delivery project") from None


@router.delete("/projects/{delivery_project_id}")
async def delete_delivery_project(
    project_id: str,
    delivery_project_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(delivery_project_id), user_id=user_id)
        return {"status": "deleted"}
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Delivery project not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your delivery project") from None


@router.post("/projects/{delivery_project_id}/tasks")
async def create_delivery_task(
    project_id: str,
    delivery_project_id: str,
    body: DeliveryTaskCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    data = body.model_dump()
    data["delivery_project_id"] = delivery_project_id
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="delivery_tasks",
        data=data,
    )


@router.get("/projects/{delivery_project_id}/tasks")
async def list_delivery_tasks(
    project_id: str,
    delivery_project_id: str,
    user_id: str = Depends(current_user_id),
) -> list[dict[str, Any]]:
    tasks = await get_repositories().business.list(
        user_id=user_id,
        entity_type="delivery_tasks",
        project_id=project_id,
    )
    return [t for t in tasks if t.get("data", {}).get("delivery_project_id") == delivery_project_id]


@router.put("/tasks/{task_id}")
async def update_delivery_task(
    project_id: str,
    task_id: str,
    body: DeliveryTaskUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(task_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Task not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your task") from None


@router.delete("/tasks/{task_id}")
async def delete_delivery_task(
    project_id: str,
    task_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(task_id), user_id=user_id)
        return {"status": "deleted"}
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Task not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your task") from None
