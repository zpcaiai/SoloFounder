from __future__ import annotations

from app.services.skill_runner import skill_runner
from app.workflows.graph_compat import END, StateGraph
from app.workflows.state import RevenuePilotState, append_step_result


def _locale(state: RevenuePilotState) -> str:
    return state.get("locale", "zh-CN")


async def run_founder_profile_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="founder_profile_diagnosis",
        input_payload={"founder_profile": state.get("founder_profile", {}), "locale": _locale(state)},
    )
    append_step_result(state, skill_name="founder_profile_diagnosis", runner_result=result)
    state["founder_profile_diagnosis"] = result["output"]["result"]
    state["current_step"] = "founder_profile_diagnosis"
    state["next_step"] = "niche_selection"
    return state


async def run_niche_selection_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="niche_selection",
        input_payload={
            "business_directions": state.get("founder_profile_diagnosis", {}).get("business_directions", []),
            "founder_profile": state.get("founder_profile", {}),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="niche_selection", runner_result=result)
    state["selected_niche"] = result["output"]["result"].get("final_recommendation", "")
    state["current_step"] = "niche_selection"
    state["next_step"] = "market_validation"
    return state


async def run_market_validation_node(state: RevenuePilotState) -> RevenuePilotState:
    selected_idea = state.get("selected_idea", {})
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="market_validation",
        input_payload={
            "selected_niche": state.get("selected_niche", ""),
            "idea": selected_idea,
            "suspected_pain": selected_idea.get("pain_point", ""),
            "proposed_offer": selected_idea.get("possible_offer", ""),
            "time_budget_days": 7,
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="market_validation", runner_result=result)
    state["market_validation"] = result["output"]["result"]
    state["current_step"] = "market_validation"
    state["next_step"] = "customer_persona"
    return state


async def run_customer_persona_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="customer_persona",
        input_payload={
            "selected_niche": state.get("selected_niche", ""),
            "idea": state.get("selected_idea", {}),
            "market_notes": state.get("market_validation", {}),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="customer_persona", runner_result=result)
    state["customer_persona"] = result["output"]["result"]
    state["current_step"] = "customer_persona"
    state["next_step"] = "pain_interview"
    return state


async def run_pain_interview_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="pain_interview",
        input_payload={
            "niche": state.get("selected_niche", ""),
            "persona": state.get("customer_persona", {}),
            "suspected_pain": state.get("selected_idea", {}).get("pain_point", ""),
            "interview_goal": "validate pain",
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="pain_interview", runner_result=result)
    state["pain_interview"] = result["output"]["result"]
    state["current_step"] = "pain_interview"
    state["next_step"] = "productized_offer"
    return state


async def run_productized_offer_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="productized_offer",
        input_payload={
            "founder_profile": state.get("founder_profile", {}),
            "selected_niche": state.get("selected_niche", ""),
            "customer_persona": state.get("customer_persona", {}),
            "validated_pain": state.get("market_validation", {}),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="productized_offer", runner_result=result)
    state["offer"] = result["output"]["result"]
    state["current_step"] = "productized_offer"
    state["next_step"] = "landing_page"
    return state


async def run_landing_page_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="landing_page",
        input_payload={"offer": state.get("offer", {}), "persona": state.get("customer_persona", {}), "locale": _locale(state)},
    )
    append_step_result(state, skill_name="landing_page", runner_result=result)
    state["landing_page"] = result["output"]["result"]
    state["current_step"] = "landing_page"
    state["next_step"] = "sales_outreach"
    return state


async def run_sales_outreach_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="sales_outreach",
        input_payload={
            "offer": state.get("offer", {}),
            "persona": state.get("customer_persona", {}),
            "channel": "email_linkedin_wechat",
            "human_approval_required": True,
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="sales_outreach", runner_result=result)
    state["outreach_assets"] = result["output"]["result"]
    state["current_step"] = "sales_outreach"
    state["next_step"] = "done"
    return state


def build_idea_to_offer_graph():
    graph = StateGraph(RevenuePilotState)
    graph.add_node("founder_profile_diagnosis", run_founder_profile_node)
    graph.add_node("niche_selection", run_niche_selection_node)
    graph.add_node("market_validation", run_market_validation_node)
    graph.add_node("customer_persona", run_customer_persona_node)
    graph.add_node("pain_interview", run_pain_interview_node)
    graph.add_node("productized_offer", run_productized_offer_node)
    graph.add_node("landing_page", run_landing_page_node)
    graph.add_node("sales_outreach", run_sales_outreach_node)
    graph.set_entry_point("founder_profile_diagnosis")
    graph.add_edge("founder_profile_diagnosis", "niche_selection")
    graph.add_edge("niche_selection", "market_validation")
    graph.add_edge("market_validation", "customer_persona")
    graph.add_edge("customer_persona", "pain_interview")
    graph.add_edge("pain_interview", "productized_offer")
    graph.add_edge("productized_offer", "landing_page")
    graph.add_edge("landing_page", "sales_outreach")
    graph.add_edge("sales_outreach", END)
    return graph.compile()
