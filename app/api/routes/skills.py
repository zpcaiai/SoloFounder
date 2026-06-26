from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.services.skill_runner import skill_runner
from app.skills.registry import SKILL_REGISTRY

router = APIRouter(prefix="/api/skills", tags=["skills"])


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


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


@router.get("/list")
async def list_skills() -> list[str]:
    return list(SKILL_REGISTRY.keys())


@router.get("/runs")
async def list_skill_runs(user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    records = await get_repositories().skill_runs.list_for_user(user_id)
    return [_serialize(record) for record in records]


@router.get("/runs/{skill_run_id}")
async def get_skill_run(skill_run_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        record = await get_repositories().skill_runs.get_for_user(UUID(skill_run_id), user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Skill run not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Skill run does not belong to this user") from None
    return _serialize(record)
