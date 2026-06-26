from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from app.skills.content_to_product import run as content_to_product
from app.skills.crm_deal_coach import run as crm_deal_coach
from app.skills.customer_persona import run as customer_persona
from app.skills.delivery_project import run as delivery_project
from app.skills.founder_profile_diagnosis import run as founder_profile_diagnosis
from app.skills.landing_page import run as landing_page
from app.skills.market_validation import run as market_validation
from app.skills.niche_selection import run as niche_selection
from app.skills.pain_interview import run as pain_interview
from app.skills.productized_offer import run as productized_offer
from app.skills.proposal import run as proposal
from app.skills.revenue_retention import run as revenue_retention
from app.skills.sales_outreach import run as sales_outreach

SkillFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


SKILL_REGISTRY: dict[str, SkillFn] = {
    "founder_profile_diagnosis": founder_profile_diagnosis,
    "niche_selection": niche_selection,
    "market_validation": market_validation,
    "customer_persona": customer_persona,
    "pain_interview": pain_interview,
    "productized_offer": productized_offer,
    "landing_page": landing_page,
    "sales_outreach": sales_outreach,
    "crm_deal_coach": crm_deal_coach,
    "proposal": proposal,
    "delivery_project": delivery_project,
    "revenue_retention": revenue_retention,
    "content_to_product": content_to_product,
}


def get_skill(skill_name: str) -> SkillFn:
    skill = SKILL_REGISTRY.get(skill_name)
    if not skill:
        raise ValueError(f"Unknown skill: {skill_name}")
    return skill
