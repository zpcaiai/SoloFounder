from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from app.repositories.factory import RepositoryBundle
from app.repositories.models import AIGenerationRecord, SkillRunRecord, WorkflowRunRecord


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        return json.loads(value)
    return value


def _uuid(value: str | UUID | None) -> UUID | None:
    if value is None or value == "":
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


class AsyncpgPool:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._pool: Any = None

    async def pool(self) -> Any:
        if self._pool is None:
            try:
                import asyncpg  # type: ignore
            except ModuleNotFoundError as exc:  # pragma: no cover - optional production dependency
                raise RuntimeError("The 'asyncpg' package is required when REVENUEPILOT_DB=postgres.") from exc
            self._pool = await asyncpg.create_pool(
                dsn=self.database_url,
                min_size=0,
                max_size=5,
                command_timeout=30,
            )
        return self._pool


class PostgresSkillRunRepository:
    def __init__(self, pool: AsyncpgPool) -> None:
        self.pool = pool

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
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.skill_runs (
              user_id, project_id, skill_name, input_payload, related_entity_type,
              related_entity_id, status, started_at
            )
            values ($1, $2, $3, $4::jsonb, $5, $6, $7, now())
            returning *
            """,
            user_id,
            _uuid(project_id),
            skill_name,
            _json(input_payload),
            related_entity_type,
            _uuid(related_entity_id),
            status,
        )
        return self._record(row)

    async def mark_succeeded(self, *, skill_run_id: UUID, user_id: str, output_payload: dict[str, Any]) -> SkillRunRecord:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            update public.skill_runs
            set status = 'succeeded', output_payload = $3::jsonb, finished_at = now()
            where id = $1 and user_id = $2
            returning *
            """,
            skill_run_id,
            user_id,
            _json(output_payload),
        )
        if row is None:
            raise PermissionError("Skill run does not belong to this user.")
        return self._record(row)

    async def mark_failed(self, *, skill_run_id: UUID, user_id: str, error_message: str) -> SkillRunRecord:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            update public.skill_runs
            set status = 'failed', error_message = $3, finished_at = now()
            where id = $1 and user_id = $2
            returning *
            """,
            skill_run_id,
            user_id,
            error_message,
        )
        if row is None:
            raise PermissionError("Skill run does not belong to this user.")
        return self._record(row)

    async def get_for_user(self, skill_run_id: UUID, user_id: str) -> SkillRunRecord:
        pool = await self.pool.pool()
        row = await pool.fetchrow("select * from public.skill_runs where id = $1 and user_id = $2", skill_run_id, user_id)
        if row is None:
            raise PermissionError("Skill run does not belong to this user.")
        return self._record(row)

    def _record(self, row: Any) -> SkillRunRecord:
        return SkillRunRecord(
            id=row["id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            skill_name=row["skill_name"],
            input_payload=_json_value(row["input_payload"]) or {},
            related_entity_type=row["related_entity_type"],
            related_entity_id=row["related_entity_id"],
            status=row["status"],
            output_payload=_json_value(row["output_payload"]) or {},
            error_message=row["error_message"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class PostgresAIGenerationRepository:
    def __init__(self, pool: AsyncpgPool) -> None:
        self.pool = pool

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
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.ai_generations (
              user_id, project_id, skill_run_id, generation_type, title,
              content_json, related_entity_type, related_entity_id
            )
            values ($1, $2, $3, $4, $5, $6::jsonb, $7, $8)
            returning *
            """,
            user_id,
            _uuid(project_id),
            _uuid(skill_run_id),
            generation_type,
            title,
            _json(content_json),
            related_entity_type,
            _uuid(related_entity_id),
        )
        return AIGenerationRecord(
            id=row["id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            skill_run_id=row["skill_run_id"],
            generation_type=row["generation_type"],
            title=row["title"],
            content_json=_json_value(row["content_json"]) or {},
            related_entity_type=row["related_entity_type"],
            related_entity_id=row["related_entity_id"],
            created_at=row["created_at"],
        )


class PostgresWorkflowRunRepository:
    def __init__(self, pool: AsyncpgPool) -> None:
        self.pool = pool

    async def create(
        self,
        *,
        user_id: str,
        workflow_name: str,
        input_payload: dict[str, Any],
        project_id: str | UUID | None = None,
        status: str = "running",
    ) -> WorkflowRunRecord:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.workflow_runs (
              user_id, project_id, workflow_name, input_payload, status, started_at
            )
            values ($1, $2, $3, $4::jsonb, $5, now())
            returning *
            """,
            user_id,
            _uuid(project_id),
            workflow_name,
            _json(input_payload),
            status,
        )
        return self._record(row)

    async def mark_succeeded(
        self,
        *,
        workflow_run_id: UUID,
        user_id: str,
        output_payload: dict[str, Any],
        skill_run_ids: list[str],
        created_entities: list[dict[str, Any]],
    ) -> WorkflowRunRecord:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            update public.workflow_runs
            set status = 'succeeded',
                output_payload = $3::jsonb,
                skill_run_ids = $4::jsonb,
                created_entities = $5::jsonb,
                finished_at = now()
            where id = $1 and user_id = $2
            returning *
            """,
            workflow_run_id,
            user_id,
            _json(output_payload),
            _json(skill_run_ids),
            _json(created_entities),
        )
        if row is None:
            raise PermissionError("Workflow run does not belong to this user.")
        return self._record(row)

    async def mark_failed(self, *, workflow_run_id: UUID, user_id: str, error_message: str) -> WorkflowRunRecord:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            update public.workflow_runs
            set status = 'failed', error_message = $3, finished_at = now()
            where id = $1 and user_id = $2
            returning *
            """,
            workflow_run_id,
            user_id,
            error_message,
        )
        if row is None:
            raise PermissionError("Workflow run does not belong to this user.")
        return self._record(row)

    async def list_for_user(self, user_id: str) -> list[WorkflowRunRecord]:
        pool = await self.pool.pool()
        rows = await pool.fetch(
            "select * from public.workflow_runs where user_id = $1 order by created_at desc",
            user_id,
        )
        return [self._record(row) for row in rows]

    async def get_for_user(self, workflow_run_id: UUID, user_id: str) -> WorkflowRunRecord:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            "select * from public.workflow_runs where id = $1 and user_id = $2",
            workflow_run_id,
            user_id,
        )
        if row is None:
            raise PermissionError("Workflow run does not belong to this user.")
        return self._record(row)

    def _record(self, row: Any) -> WorkflowRunRecord:
        return WorkflowRunRecord(
            id=row["id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            workflow_name=row["workflow_name"],
            workflow_version=row["workflow_version"],
            status=row["status"],
            input_payload=_json_value(row["input_payload"]) or {},
            output_payload=_json_value(row["output_payload"]) or {},
            skill_run_ids=_json_value(row["skill_run_ids"]) or [],
            created_entities=_json_value(row["created_entities"]) or [],
            error_message=row["error_message"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class PostgresEntityRepository:
    def __init__(self, pool: AsyncpgPool) -> None:
        self.pool = pool

    async def create(
        self,
        *,
        user_id: str,
        project_id: str | UUID | None,
        entity_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        handlers = {
            "business_ideas": self._create_business_idea,
            "customer_personas": self._create_customer_persona,
            "pain_interviews": self._create_pain_interview,
            "offers": self._create_offer,
            "landing_pages": self._create_landing_page,
            "outreach_assets": self._create_outreach_asset,
            "proposals": self._create_proposal,
            "delivery_projects": self._create_delivery_project,
            "retention_plans": self._create_retention_plan,
        }
        handler = handlers.get(entity_type)
        if handler is None:
            return await self._create_generic_payload(user_id=user_id, project_id=project_id, entity_type=entity_type, payload=payload)
        return await handler(user_id=user_id, project_id=project_id, payload=payload)

    async def _create_business_idea(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.business_ideas (
              user_id, project_id, title, description, target_customer, pain_point,
              possible_offer, scores, risks, validation_steps, status
            )
            values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10::jsonb, 'generated')
            returning id
            """,
            user_id,
            _uuid(project_id),
            payload.get("name") or payload.get("title") or "Generated business idea",
            payload.get("description") or payload.get("possible_offer"),
            payload.get("target_customer"),
            payload.get("pain_point"),
            payload.get("possible_offer"),
            _json(payload.get("scores", {})),
            _json(payload.get("risks", [])),
            _json(payload.get("validation_steps", [])),
        )
        return self._created(row, "business_ideas", payload)

    async def _create_customer_persona(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        primary = payload.get("primary_persona", {})
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.customer_personas (user_id, project_id, name, role, business_type, payload)
            values ($1, $2, $3, $4, $5, $6::jsonb)
            returning id
            """,
            user_id,
            _uuid(project_id),
            primary.get("name"),
            primary.get("role"),
            primary.get("business_type"),
            _json(payload),
        )
        return self._created(row, "customer_personas", payload)

    async def _create_pain_interview(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.pain_interviews (user_id, project_id, interview_goal, questions, scoring_rubric, summary)
            values ($1, $2, 'validate pain', $3::jsonb, $4::jsonb, $5::jsonb)
            returning id
            """,
            user_id,
            _uuid(project_id),
            _json(payload.get("interview_questions", [])),
            _json(payload.get("scoring_rubric", {})),
            _json(payload.get("post_interview_summary_template", {})),
        )
        return self._created(row, "pain_interviews", payload)

    async def _create_offer(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.offers (
              user_id, project_id, offer_name, one_line_promise, target_customer,
              pain, desired_result, deliverables, timeline, pricing, guarantee,
              scope_boundaries, client_requirements, upsell_path, retainer_path, status
            )
            values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10::jsonb, $11, $12::jsonb, $13::jsonb, $14::jsonb, $15, 'draft')
            returning id
            """,
            user_id,
            _uuid(project_id),
            payload.get("offer_name") or payload.get("knowledge_asset_summary") or "Generated offer",
            payload.get("one_line_promise"),
            payload.get("target_customer"),
            payload.get("pain"),
            payload.get("desired_result"),
            _json(payload.get("deliverables", [])),
            payload.get("timeline"),
            _json(payload.get("pricing", {})),
            payload.get("guarantee"),
            _json(payload.get("scope_boundaries", [])),
            _json(payload.get("client_requirements", [])),
            _json(payload.get("upsell_path", [])),
            payload.get("retainer_path"),
        )
        return self._created(row, "offers", payload)

    async def _create_landing_page(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.landing_pages (user_id, project_id, title, payload, published)
            values ($1, $2, $3, $4::jsonb, false)
            returning id
            """,
            user_id,
            _uuid(project_id),
            payload.get("hero", {}).get("headline") or "Generated landing page",
            _json(payload),
        )
        return self._created(row, "landing_pages", payload)

    async def _create_outreach_asset(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.outreach_assets (user_id, project_id, channel, payload, human_approval_required)
            values ($1, $2, $3, $4::jsonb, $5)
            returning id
            """,
            user_id,
            _uuid(project_id),
            "multi_channel",
            _json(payload),
            bool(payload.get("human_approval_required", True)),
        )
        return self._created(row, "outreach_assets", payload)

    async def _create_proposal(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.proposals (user_id, project_id, title, payload, status)
            values ($1, $2, $3, $4::jsonb, 'draft')
            returning id
            """,
            user_id,
            _uuid(project_id),
            payload.get("proposal_title") or "Generated proposal",
            _json(payload),
        )
        return self._created(row, "proposals", payload)

    async def _create_delivery_project(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.delivery_projects (user_id, project_id, title, client_name, payload, status)
            values ($1, $2, $3, $4, $5::jsonb, 'todo')
            returning id
            """,
            user_id,
            _uuid(project_id),
            payload.get("project_title") or "Generated delivery project",
            payload.get("client_name"),
            _json(payload),
        )
        return self._created(row, "delivery_projects", payload)

    async def _create_retention_plan(self, *, user_id: str, project_id: str | UUID | None, payload: dict[str, Any]) -> dict[str, Any]:
        opportunity = next(iter(payload.get("retention_opportunities", [])), {})
        pool = await self.pool.pool()
        row = await pool.fetchrow(
            """
            insert into public.retention_plans (user_id, project_id, customer_name, payload)
            values ($1, $2, $3, $4::jsonb)
            returning id
            """,
            user_id,
            _uuid(project_id),
            opportunity.get("customer_name"),
            _json(payload),
        )
        return self._created(row, "retention_plans", payload)

    async def _create_generic_payload(
        self,
        *,
        user_id: str,
        project_id: str | UUID | None,
        entity_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "id": None,
            "entity_type": entity_type,
            "payload": {"user_id": user_id, "project_id": str(project_id) if project_id else None, **payload},
            "persisted": False,
        }

    def _created(self, row: Any, entity_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(row["id"]),
            "entity_type": entity_type,
            "payload": payload,
            "persisted": True,
        }


class PostgresRepositoryBundle(RepositoryBundle):
    def __init__(self, database_url: str) -> None:
        pool = AsyncpgPool(database_url)
        super().__init__(
            skill_runs=PostgresSkillRunRepository(pool),
            ai_generations=PostgresAIGenerationRepository(pool),
            workflow_runs=PostgresWorkflowRunRepository(pool),
            entities=PostgresEntityRepository(pool),
        )
