from __future__ import annotations

from typing import Any

from app.repositories.factory import get_repositories
from app.services.entity_creation_service import create_entities_from_skill_output
from app.skills.registry import get_skill


class SkillRunner:
    async def run(
        self,
        *,
        user_id: str,
        skill_name: str,
        input_payload: dict[str, Any],
        project_id: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> dict[str, Any]:
        repositories = get_repositories()
        skill_run = await repositories.skill_runs.create(
            user_id=user_id,
            project_id=project_id,
            skill_name=skill_name,
            input_payload=input_payload,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            status="running",
        )

        try:
            skill_fn = get_skill(skill_name)
            output = await skill_fn(
                {
                    "user_id": user_id,
                    "project_id": str(project_id) if project_id else None,
                    "skill_name": skill_name,
                    "skill_version": "v1",
                    "locale": input_payload.get("locale", "zh-CN"),
                    "input_payload": input_payload,
                }
            )

            await repositories.skill_runs.mark_succeeded(
                skill_run_id=skill_run.id,
                user_id=user_id,
                output_payload=output,
            )

            await repositories.ai_generations.create(
                user_id=user_id,
                project_id=project_id,
                skill_run_id=skill_run.id,
                generation_type=skill_name,
                title=output.get("summary"),
                content_json=output,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
            )

            created_entities = await create_entities_from_skill_output(
                user_id=user_id,
                project_id=project_id,
                output=output,
            )

            return {
                "skill_run_id": str(skill_run.id),
                "status": output.get("status", "succeeded"),
                "output": output,
                "created_entities": created_entities,
            }

        except Exception as exc:
            await repositories.skill_runs.mark_failed(
                skill_run_id=skill_run.id,
                user_id=user_id,
                error_message=str(exc),
            )

            return {
                "skill_run_id": str(skill_run.id),
                "status": "failed",
                "error": str(exc),
            }


skill_runner = SkillRunner()
