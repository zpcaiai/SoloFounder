from __future__ import annotations

from typing import Any, TypedDict


class RevenuePilotState(TypedDict, total=False):
    user_id: str
    project_id: str
    locale: str

    founder_profile: dict[str, Any]
    founder_profile_diagnosis: dict[str, Any]
    selected_idea: dict[str, Any]
    selected_niche: str
    market_validation: dict[str, Any]
    customer_persona: dict[str, Any]
    pain_interview: dict[str, Any]
    offer: dict[str, Any]
    landing_page: dict[str, Any]
    outreach_assets: dict[str, Any]

    lead: dict[str, Any]
    deal: dict[str, Any]
    deal_coaching: dict[str, Any]
    proposal: dict[str, Any]
    delivery_project: dict[str, Any]
    revenue_records: list[dict[str, Any]]
    revenue_summary: dict[str, Any]
    retention_plan: dict[str, Any]

    knowledge_assets: list[dict[str, Any]]
    target_audience: str
    desired_product_type: str
    business_goal: str
    content_product_plan: dict[str, Any]

    current_step: str
    next_step: str
    warnings: list[str]
    errors: list[str]
    skill_run_ids: list[str]
    created_entities: list[dict[str, Any]]
    skill_outputs: dict[str, dict[str, Any]]


class WorkflowStepError(RuntimeError):
    def __init__(self, skill_name: str, error: str) -> None:
        super().__init__(f"{skill_name} failed: {error}")
        self.skill_name = skill_name
        self.error = error


def append_step_result(
    state: RevenuePilotState,
    *,
    skill_name: str,
    runner_result: dict[str, Any],
) -> RevenuePilotState:
    state.setdefault("skill_run_ids", []).append(runner_result["skill_run_id"])
    state.setdefault("created_entities", []).extend(runner_result.get("created_entities", []))
    state.setdefault("warnings", []).extend(runner_result.get("output", {}).get("warnings", []))
    if runner_result.get("status") == "failed":
        error = runner_result.get("error", f"{skill_name} failed")
        state.setdefault("errors", []).append(error)
        raise WorkflowStepError(skill_name, error)
    state.setdefault("skill_outputs", {})[skill_name] = runner_result.get("output", {})
    return state
