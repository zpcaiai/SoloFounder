from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies import current_user_id
from app.services.dashboard_service import get_project_dashboard

router = APIRouter(prefix="/api/projects/{project_id}/dashboard", tags=["dashboard"])


@router.get("")
async def project_dashboard(project_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return await get_project_dashboard(user_id=user_id, project_id=project_id)


@router.get("/next-actions")
async def next_actions(project_id: str, user_id: str = Depends(current_user_id)) -> dict[str, list[str]]:
    dashboard = await get_project_dashboard(user_id=user_id, project_id=project_id)
    return {"next_actions": dashboard["next_actions"]}
