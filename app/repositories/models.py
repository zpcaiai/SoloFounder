from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class SkillRunRecord:
    user_id: str
    skill_name: str
    input_payload: dict[str, Any]
    project_id: str | UUID | None = None
    related_entity_type: str | None = None
    related_entity_id: str | UUID | None = None
    status: str = "queued"
    output_payload: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    id: UUID = field(default_factory=uuid4)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class AIGenerationRecord:
    user_id: str
    generation_type: str
    content_json: dict[str, Any]
    project_id: str | UUID | None = None
    skill_run_id: str | UUID | None = None
    title: str | None = None
    related_entity_type: str | None = None
    related_entity_id: str | UUID | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class WorkflowRunRecord:
    user_id: str
    workflow_name: str
    input_payload: dict[str, Any]
    project_id: str | UUID | None = None
    workflow_version: str = "v1"
    status: str = "queued"
    output_payload: dict[str, Any] = field(default_factory=dict)
    skill_run_ids: list[str] = field(default_factory=list)
    created_entities: list[dict[str, Any]] = field(default_factory=list)
    error_message: str | None = None
    id: UUID = field(default_factory=uuid4)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
