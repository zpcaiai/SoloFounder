from __future__ import annotations

from typing import Any
from uuid import UUID

from app.repositories.models import AIGenerationRecord


class InMemoryAIGenerationRepository:
    def __init__(self) -> None:
        self.records: dict[UUID, AIGenerationRecord] = {}

    async def create(
        self,
        *,
        user_id: str,
        generation_type: str,
        content_json: dict[str, Any],
        project_id: str | UUID | None = None,
        skill_run_id: str | UUID | None = None,
        title: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | UUID | None = None,
    ) -> AIGenerationRecord:
        record = AIGenerationRecord(
            user_id=user_id,
            project_id=project_id,
            skill_run_id=skill_run_id,
            generation_type=generation_type,
            title=title,
            content_json=content_json,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        self.records[record.id] = record
        return record

    def reset(self) -> None:
        self.records.clear()


ai_generation_repo = InMemoryAIGenerationRepository()
