from __future__ import annotations

from typing import Any
from uuid import UUID

from app.repositories.models import SkillRunRecord, utcnow


class InMemorySkillRunRepository:
    def __init__(self) -> None:
        self.records: dict[UUID, SkillRunRecord] = {}

    async def create(
        self,
        *,
        user_id: str,
        skill_name: str,
        input_payload: dict[str, Any],
        project_id: str | UUID | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | UUID | None = None,
        status: str = "running",
    ) -> SkillRunRecord:
        record = SkillRunRecord(
            user_id=user_id,
            project_id=project_id,
            skill_name=skill_name,
            input_payload=input_payload,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            status=status,
            started_at=utcnow(),
        )
        self.records[record.id] = record
        return record

    async def mark_succeeded(self, *, skill_run_id: UUID, user_id: str, output_payload: dict[str, Any]) -> SkillRunRecord:
        record = await self.get_for_user(skill_run_id, user_id)
        record.status = "succeeded"
        record.output_payload = output_payload
        record.updated_at = utcnow()
        record.finished_at = record.updated_at
        return record

    async def mark_failed(self, *, skill_run_id: UUID, user_id: str, error_message: str) -> SkillRunRecord:
        record = await self.get_for_user(skill_run_id, user_id)
        record.status = "failed"
        record.error_message = error_message
        record.updated_at = utcnow()
        record.finished_at = record.updated_at
        return record

    async def get_for_user(self, skill_run_id: UUID, user_id: str) -> SkillRunRecord:
        record = self.records[skill_run_id]
        if record.user_id != user_id:
            raise PermissionError("Skill run does not belong to this user.")
        return record

    def reset(self) -> None:
        self.records.clear()


skill_run_repo = InMemorySkillRunRepository()
