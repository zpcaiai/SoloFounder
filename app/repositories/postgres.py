from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.repositories.factory import RepositoryBundle
from app.repositories.models import AIGenerationRecord, SkillRunRecord, WorkflowRunRecord


def _json_default(value: Any) -> str:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=_json_default)


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


def _response_value(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


class AsyncpgPool:
    def __init__(
        self,
        database_url: str,
        *,
        min_size: int = 2,
        max_size: int = 10,
        command_timeout: int = 10,
        max_inactive_time: float = 300.0,
    ) -> None:
        self.database_url = database_url
        self._min_size = min_size
        self._max_size = max(max_size, min_size, 1)
        self._command_timeout = command_timeout
        self._max_inactive_time = max_inactive_time
        self._pool: Any = None

    async def pool(self) -> Any:
        if self._pool is None:
            try:
                import asyncpg  # type: ignore
            except ModuleNotFoundError as exc:  # pragma: no cover - optional production dependency
                raise RuntimeError("The 'asyncpg' package is required when REVENUEPILOT_DB=postgres.") from exc
            self._pool = await asyncpg.create_pool(
                dsn=self.database_url,
                min_size=self._min_size,
                max_size=self._max_size,
                command_timeout=self._command_timeout,
                max_inactive_connection_lifetime=self._max_inactive_time,
            )
        return self._pool

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def health_check(self) -> bool:
        try:
            pool = await self.pool()
            await pool.fetch("select 1")
            return True
        except Exception:
            return False


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

    async def list_for_user(self, user_id: str) -> list[SkillRunRecord]:
        pool = await self.pool.pool()
        rows = await pool.fetch(
            "select * from public.skill_runs where user_id = $1 order by started_at desc",
            user_id,
        )
        return [self._record(row) for row in rows]

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
        opportunity: dict[str, Any] = next(iter(payload.get("retention_opportunities", [])), {})
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


@dataclass(frozen=True)
class BusinessTableConfig:
    entity_type: str
    table: str
    columns: frozenset[str]
    json_columns: frozenset[str] = frozenset()
    uuid_columns: frozenset[str] = frozenset()
    payload_column: str | None = None
    metadata_column: str | None = None
    has_project_id: bool = True


BUSINESS_TABLES: dict[str, BusinessTableConfig] = {
    "projects": BusinessTableConfig(
        entity_type="projects",
        table="business_projects",
        columns=frozenset({"name", "description", "metadata"}),
        json_columns=frozenset({"metadata"}),
        metadata_column="metadata",
        has_project_id=False,
    ),
    "profiles": BusinessTableConfig(
        entity_type="profiles",
        table="profiles",
        columns=frozenset({"display_name", "email", "avatar_url", "metadata"}),
        json_columns=frozenset({"metadata"}),
        metadata_column="metadata",
        has_project_id=False,
    ),
    "founder_profiles": BusinessTableConfig(
        entity_type="founder_profiles",
        table="founder_profiles",
        columns=frozenset(
            {
                "skills",
                "work_experience",
                "domain_expertise",
                "technical_ability",
                "sales_experience",
                "existing_content",
                "audience_assets",
                "personal_network",
                "time_available_per_week",
                "monthly_income_goal",
                "preferred_customer_type",
                "constraints",
                "values_or_mission",
            }
        ),
        json_columns=frozenset(
            {
                "skills",
                "work_experience",
                "domain_expertise",
                "technical_ability",
                "sales_experience",
                "existing_content",
                "audience_assets",
                "personal_network",
                "constraints",
            }
        ),
    ),
    "ideas": BusinessTableConfig(
        entity_type="ideas",
        table="business_ideas",
        columns=frozenset(
            {
                "title",
                "description",
                "target_customer",
                "pain_point",
                "possible_offer",
                "scores",
                "risks",
                "validation_steps",
                "status",
            }
        ),
        json_columns=frozenset({"scores", "risks", "validation_steps"}),
    ),
    "market_hypotheses": BusinessTableConfig(
        entity_type="market_hypotheses",
        table="market_hypotheses",
        columns=frozenset({"business_idea_id", "selected_niche", "suspected_pain", "proposed_offer", "validation_plan", "status"}),
        json_columns=frozenset({"validation_plan"}),
        uuid_columns=frozenset({"business_idea_id"}),
    ),
    "personas": BusinessTableConfig(
        entity_type="personas",
        table="customer_personas",
        columns=frozenset({"business_idea_id", "name", "role", "business_type", "payload"}),
        json_columns=frozenset({"payload"}),
        uuid_columns=frozenset({"business_idea_id"}),
        payload_column="payload",
    ),
    "offers": BusinessTableConfig(
        entity_type="offers",
        table="offers",
        columns=frozenset(
            {
                "business_idea_id",
                "offer_name",
                "one_line_promise",
                "target_customer",
                "pain",
                "desired_result",
                "deliverables",
                "timeline",
                "pricing",
                "guarantee",
                "scope_boundaries",
                "client_requirements",
                "upsell_path",
                "retainer_path",
                "status",
            }
        ),
        json_columns=frozenset({"deliverables", "pricing", "scope_boundaries", "client_requirements", "upsell_path"}),
        uuid_columns=frozenset({"business_idea_id"}),
    ),
    "landing_pages": BusinessTableConfig(
        entity_type="landing_pages",
        table="landing_pages",
        columns=frozenset({"offer_id", "title", "payload", "published"}),
        json_columns=frozenset({"payload"}),
        uuid_columns=frozenset({"offer_id"}),
        payload_column="payload",
    ),
    "outreach": BusinessTableConfig(
        entity_type="outreach",
        table="outreach_assets",
        columns=frozenset({"offer_id", "channel", "payload", "human_approval_required"}),
        json_columns=frozenset({"payload"}),
        uuid_columns=frozenset({"offer_id"}),
        payload_column="payload",
    ),
    "leads": BusinessTableConfig(
        entity_type="leads",
        table="leads",
        columns=frozenset({"name", "company", "email", "source", "status", "payload"}),
        json_columns=frozenset({"payload"}),
        payload_column="payload",
    ),
    "deals": BusinessTableConfig(
        entity_type="deals",
        table="crm_deals",
        columns=frozenset({"lead_id", "offer_id", "stage", "expected_value", "probability", "expected_close_date", "payload"}),
        json_columns=frozenset({"payload"}),
        uuid_columns=frozenset({"lead_id", "offer_id"}),
        payload_column="payload",
    ),
    "proposals": BusinessTableConfig(
        entity_type="proposals",
        table="proposals",
        columns=frozenset({"deal_id", "title", "payload", "status"}),
        json_columns=frozenset({"payload"}),
        uuid_columns=frozenset({"deal_id"}),
        payload_column="payload",
    ),
    "delivery_projects": BusinessTableConfig(
        entity_type="delivery_projects",
        table="delivery_projects",
        columns=frozenset({"deal_id", "proposal_id", "title", "client_name", "payload", "status"}),
        json_columns=frozenset({"payload"}),
        uuid_columns=frozenset({"deal_id", "proposal_id"}),
        payload_column="payload",
    ),
    "delivery_tasks": BusinessTableConfig(
        entity_type="delivery_tasks",
        table="delivery_tasks",
        columns=frozenset({"delivery_project_id", "title", "description", "priority", "status", "due_date", "completed_at"}),
        uuid_columns=frozenset({"delivery_project_id"}),
    ),
    "deliverables": BusinessTableConfig(
        entity_type="deliverables",
        table="deliverables",
        columns=frozenset({"delivery_project_id", "name", "description", "acceptance_criteria", "status"}),
        json_columns=frozenset({"acceptance_criteria"}),
        uuid_columns=frozenset({"delivery_project_id"}),
    ),
    "revenue": BusinessTableConfig(
        entity_type="revenue",
        table="revenue_records",
        columns=frozenset({"deal_id", "offer_id", "customer_name", "amount", "currency", "received_at", "payload"}),
        json_columns=frozenset({"payload"}),
        uuid_columns=frozenset({"deal_id", "offer_id"}),
        payload_column="payload",
    ),
    "retention_plans": BusinessTableConfig(
        entity_type="retention_plans",
        table="retention_plans",
        columns=frozenset({"customer_name", "payload"}),
        json_columns=frozenset({"payload"}),
        payload_column="payload",
    ),
    "knowledge_assets": BusinessTableConfig(
        entity_type="knowledge_assets",
        table="knowledge_assets",
        columns=frozenset({"title", "asset_type", "raw_text", "summary", "tags"}),
        json_columns=frozenset({"tags"}),
    ),
    "customer_feedback": BusinessTableConfig(
        entity_type="customer_feedback",
        table="customer_feedback",
        columns=frozenset({"customer_name", "feedback_type", "content", "rating", "payload"}),
        json_columns=frozenset({"payload"}),
        payload_column="payload",
    ),
}


class PostgresBusinessRepository:
    def __init__(self, pool: AsyncpgPool) -> None:
        self.pool = pool

    async def create(
        self,
        *,
        user_id: str,
        entity_type: str,
        data: dict[str, Any],
        project_id: str | UUID | None = None,
    ) -> dict[str, Any]:
        pool = await self.pool.pool()
        config = self._config(entity_type)
        values = self._prepare_insert_values(config, user_id=user_id, project_id=project_id, data=data)
        columns = list(values.keys())
        placeholders = [self._placeholder(index, column, config) for index, column in enumerate(columns, start=1)]
        row = await pool.fetchrow(
            f"""
            insert into public.{config.table} ({", ".join(columns)})
            values ({", ".join(placeholders)})
            returning *
            """,  # nosec B608
            *values.values(),
        )
        return self._record(config, row)

    async def get(self, *, entity_id: UUID, user_id: str) -> dict[str, Any]:
        config, row = await self._find_for_user(entity_id=entity_id, user_id=user_id)
        return self._record(config, row)

    async def list(
        self,
        *,
        user_id: str,
        entity_type: str,
        project_id: str | UUID | None = None,
    ) -> list[dict[str, Any]]:
        pool = await self.pool.pool()
        config = self._config(entity_type)
        if config.has_project_id and project_id is not None:
            rows = await pool.fetch(
                f"select * from public.{config.table} where user_id = $1 and project_id = $2 order by created_at desc",  # nosec B608
                user_id,
                _uuid(project_id),
            )
        else:
            rows = await pool.fetch(
                f"select * from public.{config.table} where user_id = $1 order by created_at desc",  # nosec B608
                user_id,
            )
        return [self._record(config, row) for row in rows]

    async def update(
        self,
        *,
        entity_id: UUID,
        user_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        config, existing = await self._find_for_user(entity_id=entity_id, user_id=user_id)
        pool = await self.pool.pool()
        values = self._prepare_update_values(config, existing=existing, data=data)
        if not values:
            return self._record(config, existing)

        assignments = [
            f"{column} = {self._placeholder(index, column, config)}" for index, column in enumerate(values, start=1)
        ]
        row = await pool.fetchrow(
            f"""
            update public.{config.table}
            set {", ".join(assignments)}
            where id = ${len(values) + 1} and user_id = ${len(values) + 2}
            returning *
            """,  # nosec B608
            *values.values(),
            entity_id,
            user_id,
        )
        if row is None:
            raise PermissionError("Entity does not belong to this user.")
        return self._record(config, row)

    async def delete(self, *, entity_id: UUID, user_id: str) -> None:
        config, _ = await self._find_for_user(entity_id=entity_id, user_id=user_id)
        pool = await self.pool.pool()
        result = await pool.execute(
            f"delete from public.{config.table} where id = $1 and user_id = $2",  # nosec B608
            entity_id,
            user_id,
        )
        if result.endswith(" 0"):
            raise PermissionError("Entity does not belong to this user.")

    async def count(
        self,
        *,
        user_id: str,
        entity_type: str,
        project_id: str | UUID | None = None,
    ) -> int:
        pool = await self.pool.pool()
        config = self._config(entity_type)
        if config.has_project_id and project_id is not None:
            row = await pool.fetchrow(
                f"select count(*) as count from public.{config.table} where user_id = $1 and project_id = $2",  # nosec B608
                user_id,
                _uuid(project_id),
            )
        else:
            row = await pool.fetchrow(
                f"select count(*) as count from public.{config.table} where user_id = $1",  # nosec B608
                user_id,
            )
        return int(row["count"])

    def _config(self, entity_type: str) -> BusinessTableConfig:
        try:
            return BUSINESS_TABLES[entity_type]
        except KeyError:
            raise ValueError(f"Unsupported business entity type: {entity_type}") from None

    def _placeholder(self, index: int, column: str, config: BusinessTableConfig) -> str:
        placeholder = f"${index}"
        if column in config.json_columns:
            return f"{placeholder}::jsonb"
        return placeholder

    def _prepare_insert_values(
        self,
        config: BusinessTableConfig,
        *,
        user_id: str,
        project_id: str | UUID | None,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        values: dict[str, Any] = {"user_id": user_id}
        if config.has_project_id:
            values["project_id"] = _uuid(project_id)
        values.update(self._prepare_data_values(config, data=data))
        return values

    def _prepare_update_values(self, config: BusinessTableConfig, *, existing: Any, data: dict[str, Any]) -> dict[str, Any]:
        values = self._prepare_data_values(config, data=data, existing=existing)
        values.pop("user_id", None)
        values.pop("project_id", None)
        return values

    def _prepare_data_values(
        self,
        config: BusinessTableConfig,
        *,
        data: dict[str, Any],
        existing: Any | None = None,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {}
        extras = {key: value for key, value in data.items() if key not in config.columns and key != "project_id"}

        for column in config.columns:
            if column not in data:
                continue
            value = data[column]
            if column in config.uuid_columns:
                value = _uuid(value)
            if column in config.json_columns:
                value = _json(value)
            values[column] = value

        if config.payload_column:
            payload = data.get(config.payload_column)
            if isinstance(payload, dict):
                payload_value = payload
            elif existing is not None:
                payload_value = _json_value(existing[config.payload_column]) or {}
            else:
                payload_value = {}
            payload_value.update(extras)
            if payload_value or config.payload_column in data or extras:
                values[config.payload_column] = _json(payload_value)

        if config.metadata_column and extras:
            metadata = data.get(config.metadata_column)
            if isinstance(metadata, dict):
                metadata_value = metadata
            elif existing is not None:
                metadata_value = _json_value(existing[config.metadata_column]) or {}
            else:
                metadata_value = {}
            metadata_value.update(extras)
            values[config.metadata_column] = _json(metadata_value)

        return values

    async def _find_for_user(self, *, entity_id: UUID, user_id: str) -> tuple[BusinessTableConfig, Any]:
        pool = await self.pool.pool()
        for config in BUSINESS_TABLES.values():
            row = await pool.fetchrow(
                f"select * from public.{config.table} where id = $1",  # nosec B608
                entity_id,
            )
            if row is None:
                continue
            if row["user_id"] != user_id:
                raise PermissionError("Entity does not belong to this user.")
            return config, row
        raise KeyError(str(entity_id))

    def _record(self, config: BusinessTableConfig, row: Any) -> dict[str, Any]:
        data = {}
        for column in config.columns:
            value = row[column]
            if column in config.json_columns:
                data[column] = _json_value(value)
            else:
                data[column] = _response_value(value)

        return {
            "id": str(row["id"]),
            "user_id": row["user_id"],
            "project_id": str(row["project_id"]) if config.has_project_id and row["project_id"] else None,
            "entity_type": config.entity_type,
            "data": data,
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }


class PostgresRepositoryBundle(RepositoryBundle):
    def __init__(self, database_url: str, **pool_kwargs: Any) -> None:
        self._pool = AsyncpgPool(database_url, **pool_kwargs)
        super().__init__(
            skill_runs=PostgresSkillRunRepository(self._pool),
            ai_generations=PostgresAIGenerationRepository(self._pool),
            workflow_runs=PostgresWorkflowRunRepository(self._pool),
            entities=PostgresEntityRepository(self._pool),
            business=PostgresBusinessRepository(self._pool),
        )

    async def close(self) -> None:
        await self._pool.close()
