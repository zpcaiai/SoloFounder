from __future__ import annotations

from typing import Any, Callable

from app.repositories.workflow_run_repo import workflow_run_repo
from app.workflows.content_to_product import build_content_to_product_graph
from app.workflows.deal_to_delivery import build_deal_to_delivery_graph
from app.workflows.idea_to_offer import build_idea_to_offer_graph
from app.workflows.state import RevenuePilotState


WorkflowBuilder = Callable[[], Any]


WORKFLOW_BUILDERS: dict[str, WorkflowBuilder] = {
    "idea_to_offer": build_idea_to_offer_graph,
    "deal_to_delivery": build_deal_to_delivery_graph,
    "content_to_product": build_content_to_product_graph,
}


class WorkflowRunner:
    async def run(
        self,
        *,
        user_id: str,
        workflow_name: str,
        input_payload: dict[str, Any],
        project_id: str | None = None,
    ) -> dict[str, Any]:
        workflow_run = await workflow_run_repo.create(
            user_id=user_id,
            workflow_name=workflow_name,
            input_payload=input_payload,
            project_id=project_id,
            status="running",
        )
        try:
            graph = WORKFLOW_BUILDERS[workflow_name]()
            initial_state: RevenuePilotState = {
                "user_id": user_id,
                "project_id": project_id or input_payload.get("project_id", ""),
                "locale": input_payload.get("locale", "zh-CN"),
                **input_payload,
            }
            final_state = await graph.ainvoke(initial_state)
            await workflow_run_repo.mark_succeeded(
                workflow_run_id=workflow_run.id,
                user_id=user_id,
                output_payload=final_state,
                skill_run_ids=final_state.get("skill_run_ids", []),
                created_entities=final_state.get("created_entities", []),
            )
            return {
                "workflow_run_id": str(workflow_run.id),
                "status": "succeeded",
                "output": final_state,
                "steps": [
                    {"skill_run_id": skill_run_id, "status": "succeeded"}
                    for skill_run_id in final_state.get("skill_run_ids", [])
                ],
                "created_entities": final_state.get("created_entities", []),
            }
        except Exception as exc:
            await workflow_run_repo.mark_failed(
                workflow_run_id=workflow_run.id,
                user_id=user_id,
                error_message=str(exc),
            )
            return {"workflow_run_id": str(workflow_run.id), "status": "failed", "error": str(exc)}


workflow_runner = WorkflowRunner()
