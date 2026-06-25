from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class EntityMutation(BaseModel):
    entity_type: str
    payload: dict[str, Any]


class SkillEnvelope(BaseModel):
    skill_name: str
    skill_version: str = "v1"
    status: Literal["succeeded", "failed", "blocked"] = "succeeded"
    summary: str
    result: dict[str, Any]
    recommended_next_actions: list[str] = Field(default_factory=list)
    entities_to_create: list[EntityMutation] = Field(default_factory=list)
    entities_to_update: list[EntityMutation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence_score: int = Field(ge=0, le=100, default=75)
