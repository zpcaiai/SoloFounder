from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import current_user_id
from app.services.skill_runner import skill_runner

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillRunRequest(BaseModel):
    skill_name: str
    project_id: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)
    related_entity_type: str | None = None
    related_entity_id: str | None = None


@router.post("/run")
async def run_skill(request: SkillRunRequest, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return await skill_runner.run(
        user_id=user_id,
        project_id=request.project_id,
        skill_name=request.skill_name,
        input_payload=request.input_payload,
        related_entity_type=request.related_entity_type,
        related_entity_id=request.related_entity_id,
    )
