from __future__ import annotations

from app.workflows.state import RevenuePilotState


def should_generate_persona(state: RevenuePilotState) -> str:
    if state.get("customer_persona"):
        return "skip_to_offer"
    return "generate_persona"


def should_generate_landing_page(state: RevenuePilotState) -> str:
    if not state.get("offer"):
        return "stop"
    return "generate_landing_page"


def should_generate_outreach(state: RevenuePilotState) -> str:
    if not state.get("landing_page"):
        return "stop"
    return "generate_outreach"
