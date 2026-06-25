from __future__ import annotations

from app.services.skill_runner import skill_runner
from app.workflows.graph_compat import END, StateGraph
from app.workflows.state import RevenuePilotState, append_step_result


def _locale(state: RevenuePilotState) -> str:
    return state.get("locale", "zh-CN")


async def run_crm_deal_coach_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="crm_deal_coach",
        input_payload={
            "lead": state.get("lead", {}),
            "deal": state.get("deal", {}),
            "offer": state.get("offer", {}),
            "conversation_notes": state.get("conversation_notes", []),
            "sales_stage": state.get("deal", {}).get("stage", ""),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="crm_deal_coach", runner_result=result)
    state["deal_coaching"] = result["output"]["result"]
    state["current_step"] = "crm_deal_coach"
    state["next_step"] = "proposal"
    return state


async def run_proposal_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="proposal",
        input_payload={
            "deal": state.get("deal", {}),
            "lead": state.get("lead", {}),
            "offer": state.get("offer", {}),
            "customer_pain": state.get("deal", {}).get("pain_summary", ""),
            "agreed_scope": state.get("deal", {}).get("agreed_scope", []),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="proposal", runner_result=result)
    state["proposal"] = result["output"]["result"]
    state["current_step"] = "proposal"
    state["next_step"] = "delivery_project"
    return state


async def run_delivery_project_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="delivery_project",
        input_payload={
            "offer": state.get("offer", {}),
            "deal": state.get("deal", {}),
            "proposal": state.get("proposal", {}),
            "customer_profile": state.get("lead", {}),
            "agreed_scope": state.get("proposal", {}).get("scope", []),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="delivery_project", runner_result=result)
    state["delivery_project"] = result["output"]["result"]
    state["current_step"] = "delivery_project"
    state["next_step"] = "revenue_retention"
    return state


async def run_revenue_retention_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="revenue_retention",
        input_payload={
            "project": state.get("project", {}),
            "offers": [state.get("offer", {})],
            "leads": [state.get("lead", {})],
            "deals": [state.get("deal", {})],
            "delivery_projects": [state.get("delivery_project", {})],
            "revenue_records": state.get("revenue_records", []),
            "customer_feedback": state.get("customer_feedback", []),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="revenue_retention", runner_result=result)
    state["retention_plan"] = result["output"]["result"]
    state["revenue_summary"] = result["output"]["result"].get("revenue_summary", {})
    state["current_step"] = "revenue_retention"
    state["next_step"] = "done"
    return state


def build_deal_to_delivery_graph():
    graph = StateGraph(RevenuePilotState)
    graph.add_node("crm_deal_coach", run_crm_deal_coach_node)
    graph.add_node("proposal", run_proposal_node)
    graph.add_node("delivery_project", run_delivery_project_node)
    graph.add_node("revenue_retention", run_revenue_retention_node)
    graph.set_entry_point("crm_deal_coach")
    graph.add_edge("crm_deal_coach", "proposal")
    graph.add_edge("proposal", "delivery_project")
    graph.add_edge("delivery_project", "revenue_retention")
    graph.add_edge("revenue_retention", END)
    return graph.compile()
