from __future__ import annotations

from typing import Any
from uuid import UUID

from app.repositories.models import WorkflowRunRecord, utcnow


class InMemoryWorkflowRunRepository:
    def __init__(self) -> None:
        self.records: dict[UUID, WorkflowRunRecord] = {}

    async def create(
        self,
        *,
        user_id: str,
        workflow_name: str,
        input_payload: dict[str, Any],
        project_id: str | UUID | None = None,
        status: str = "running",
    ) -> WorkflowRunRecord:
        record = WorkflowRunRecord(
            user_id=user_id,
            project_id=project_id,
            workflow_name=workflow_name,
            input_payload=input_payload,
            status=status,
            started_at=utcnow(),
        )
        self.records[record.id] = record
        return record

    async def mark_succeeded(
        self,
        *,
        workflow_run_id: UUID,
        user_id: str,
        output_payload: dict[str, Any],
        skill_run_ids: list[str],
        created_entities: list[dict[str, Any]],
    ) -> WorkflowRunRecord:
        record = await self.get_for_user(workflow_run_id, user_id)
        record.status = "succeeded"
        record.output_payload = output_payload
        record.skill_run_ids = skill_run_ids
        record.created_entities = created_entities
        record.finished_at = utcnow()
        record.updated_at = utcnow()
        return record

    async def mark_failed(self, *, workflow_run_id: UUID, user_id: str, error_message: str) -> WorkflowRunRecord:
        record = await self.get_for_user(workflow_run_id, user_id)
        record.status = "failed"
        record.error_message = error_message
        record.finished_at = utcnow()
        record.updated_at = utcnow()
        return record

    async def list_for_user(self, user_id: str) -> list[WorkflowRunRecord]:
        return [record for record in self.records.values() if record.user_id == user_id]

    async def get_for_user(self, workflow_run_id: UUID, user_id: str) -> WorkflowRunRecord:
        record = self.records[workflow_run_id]
        if record.user_id != user_id:
            raise PermissionError("Workflow run does not belong to this user.")
        return record

    def reset(self) -> None:
        self.records.clear()


workflow_run_repo = InMemoryWorkflowRunRepository()
