from __future__ import annotations

from app.services.skill_runner import skill_runner
from app.workflows.graph_compat import END, StateGraph
from app.workflows.state import RevenuePilotState, append_step_result


def _locale(state: RevenuePilotState) -> str:
    return state.get("locale", "zh-CN")


async def run_content_to_product_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="content_to_product",
        input_payload={
            "knowledge_assets": state.get("knowledge_assets", []),
            "target_audience": state.get("target_audience", ""),
            "desired_product_type": state.get("desired_product_type", "course"),
            "business_goal": state.get("business_goal", ""),
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="content_to_product", runner_result=result)
    state["content_product_plan"] = result["output"]["result"]
    state["current_step"] = "content_to_product"
    state["next_step"] = "customer_persona"
    return state


async def run_content_persona_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="customer_persona",
        input_payload={
            "selected_niche": state.get("target_audience", ""),
            "idea": state.get("content_product_plan", {}),
            "market_notes": "Generated from existing knowledge assets",
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="customer_persona", runner_result=result)
    state["customer_persona"] = result["output"]["result"]
    state["current_step"] = "customer_persona"
    state["next_step"] = "productized_offer"
    return state


async def run_content_offer_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="productized_offer",
        input_payload={
            "founder_profile": state.get("founder_profile", {}),
            "selected_niche": state.get("target_audience", ""),
            "customer_persona": state.get("customer_persona", {}),
            "validated_pain": state.get("content_product_plan", {}),
            "founder_capabilities": ["knowledge assets", "course content", "teaching material"],
            "locale": _locale(state),
        },
    )
    append_step_result(state, skill_name="productized_offer", runner_result=result)
    state["offer"] = result["output"]["result"]
    state["current_step"] = "productized_offer"
    state["next_step"] = "landing_page"
    return state


async def run_content_landing_page_node(state: RevenuePilotState) -> RevenuePilotState:
    result = await skill_runner.run(
        user_id=state["user_id"],
        project_id=state.get("project_id"),
        skill_name="landing_page",
        input_payload={"offer": state.get("offer", {}), "persona": state.get("customer_persona", {}), "locale": _locale(state)},
    )
    append_step_result(state, skill_name="landing_page", runner_result=result)
    state["landing_page"] = result["output"]["result"]
    state["current_step"] = "landing_page"
    state["next_step"] = "done"
    return state


def build_content_to_product_graph():
    graph = StateGraph(RevenuePilotState)
    graph.add_node("content_to_product", run_content_to_product_node)
    graph.add_node("customer_persona", run_content_persona_node)
    graph.add_node("productized_offer", run_content_offer_node)
    graph.add_node("landing_page", run_content_landing_page_node)
    graph.set_entry_point("content_to_product")
    graph.add_edge("content_to_product", "customer_persona")
    graph.add_edge("customer_persona", "productized_offer")
    graph.add_edge("productized_offer", "landing_page")
    graph.add_edge("landing_page", END)
    return graph.compile()
