from __future__ import annotations

from typing import Any

from app.repositories.factory import get_repositories


async def get_project_dashboard(*, user_id: str, project_id: str) -> dict[str, Any]:
    repo = get_repositories().business

    revenue_records = await repo.list(user_id=user_id, entity_type="revenue", project_id=project_id)
    deals = await repo.list(user_id=user_id, entity_type="deals", project_id=project_id)
    leads = await repo.list(user_id=user_id, entity_type="leads", project_id=project_id)
    offers = await repo.list(user_id=user_id, entity_type="offers", project_id=project_id)
    delivery_projects = await repo.list(user_id=user_id, entity_type="delivery_projects", project_id=project_id)

    total_revenue = sum(float(r.get("data", {}).get("amount", 0)) for r in revenue_records)
    active_leads = sum(1 for ld in leads if ld.get("data", {}).get("status", "new") == "new")
    open_delivery = sum(1 for d in delivery_projects if d.get("data", {}).get("status", "todo") != "done")

    next_actions: list[str] = []
    if active_leads > 0:
        next_actions.append(f"Follow up with {active_leads} new lead(s).")
    if any(d.get("data", {}).get("stage") == "qualified" for d in deals):
        next_actions.append("Move qualified deals to proposal stage.")
    if offers:
        next_actions.append("Generate outreach kit for your active offer.")
    if not next_actions:
        next_actions.append("Run the idea-to-offer workflow to get started.")

    return {
        "total_revenue": total_revenue,
        "total_deals": len(deals),
        "active_leads": active_leads,
        "open_delivery_projects": open_delivery,
        "offers_count": len(offers),
        "next_actions": next_actions,
    }
