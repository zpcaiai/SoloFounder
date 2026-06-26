from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SkillEnvelope(BaseModel):
    skill_name: str
    skill_version: str = "v1"
    status: Literal["succeeded", "failed", "blocked"] = "succeeded"
    summary: str
    result: dict[str, Any]
    recommended_next_actions: list[str] = Field(default_factory=list)
    entities_to_create: list[dict[str, Any]] = Field(default_factory=list)
    entities_to_update: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence_score: int = Field(ge=0, le=100, default=75)
