from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

from app.ai.provider import get_ai_provider
from app.skills.guardrails import is_regulated_revenue_request, is_spam_like_outreach, safe_outreach_result
from app.skills.prompts import build_skill_prompt
from app.skills.schemas import RESULT_MODELS, SkillEnvelope


def _loads_object(raw: str) -> dict[str, Any]:
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("AI provider returned JSON that is not an object.")
    return value


def _model_dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")


def _summary_for(skill_name: str, result: dict[str, Any]) -> str:
    fields = {
        "founder_profile_diagnosis": "recommended_direction",
        "niche_selection": "final_recommendation",
        "market_validation": "validation_goal",
        "productized_offer": "offer_name",
        "proposal": "proposal_title",
        "delivery_project": "project_title",
        "content_to_product": "knowledge_asset_summary",
    }
    field = fields.get(skill_name)
    if field and result.get(field):
        return str(result[field])
    if skill_name == "landing_page":
        return result.get("hero", {}).get("headline", "Landing page draft")
    if skill_name == "customer_persona":
        return result.get("primary_persona", {}).get("name", "Customer persona")
    if skill_name == "pain_interview":
        return "Pain interview guide"
    if skill_name == "sales_outreach":
        return "Human-approved outreach kit"
    if skill_name == "crm_deal_coach":
        return f"Deal stage: {result.get('recommended_stage', 'review')}"
    if skill_name == "revenue_retention":
        return result.get("business_diagnosis", {}).get("main_bottleneck", "Revenue retention review")
    return f"{skill_name} completed"


def _recommended_next_actions(skill_name: str, result: dict[str, Any]) -> list[str]:
    if isinstance(result.get("next_actions"), list):
        return [str(action) for action in result["next_actions"]]
    if isinstance(result.get("seven_day_plan"), list):
        return [str(action) for action in result["seven_day_plan"][:3]]
    if skill_name == "sales_outreach":
        return ["Review every outbound message before sending", "Personalize each note with real prospect context"]
    if skill_name == "revenue_retention":
        return [str(action.get("action")) for action in result.get("recommended_actions", []) if action.get("action")]
    return []


def _entities_to_create(skill_name: str, result: dict[str, Any]) -> list[dict[str, Any]]:
    if skill_name == "founder_profile_diagnosis":
        return [
            {"entity_type": "business_ideas", "payload": direction}
            for direction in result.get("business_directions", [])
        ]
    mappings = {
        "customer_persona": "customer_personas",
        "pain_interview": "pain_interviews",
        "productized_offer": "offers",
        "landing_page": "landing_pages",
        "sales_outreach": "outreach_assets",
        "proposal": "proposals",
        "delivery_project": "delivery_projects",
        "revenue_retention": "retention_plans",
        "content_to_product": "offers",
    }
    entity_type = mappings.get(skill_name)
    if not entity_type:
        return []
    return [{"entity_type": entity_type, "payload": result}]


def _warnings(skill_name: str, result: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if result.get("warning"):
        warnings.append(str(result["warning"]))
    if skill_name == "sales_outreach":
        warnings.append("Human approval is required before sending any customer outreach.")
    if skill_name == "revenue_retention":
        warnings.append("Operational business analysis only; not tax, legal, accounting, or investment advice.")
    return warnings


async def run_skill(skill_name: str, envelope: dict[str, Any]) -> dict[str, Any]:
    try:
        result_model = RESULT_MODELS[skill_name]
    except KeyError as exc:
        raise ValueError(f"Unknown skill schema: {skill_name}") from exc

    input_payload = envelope.get("input_payload", envelope)
    output_schema = result_model.model_json_schema()

    if skill_name == "sales_outreach" and is_spam_like_outreach(input_payload):
        result = result_model.model_validate(safe_outreach_result())
        result_dict = _model_dump(result)
        envelope_model = SkillEnvelope(
            skill_name=skill_name,
            skill_version=str(envelope.get("skill_version", "v1")),
            status="blocked",
            summary="Spam-like outreach request blocked",
            result=result_dict,
            recommended_next_actions=[
                "Use a low-volume personalized outreach plan",
                "Review every outbound message before sending",
            ],
            entities_to_create=_entities_to_create(skill_name, result_dict),
            entities_to_update=[],
            warnings=_warnings(skill_name, result_dict),
            confidence_score=95,
        )
        return _model_dump(envelope_model)

    provider = get_ai_provider()

    last_error: Exception | None = None
    for attempt in range(2):
        prompt = build_skill_prompt(skill_name, input_payload, output_schema)
        if attempt:
            prompt += f"\nRepair the prior invalid JSON. Validation error: {last_error}"
        raw = await provider.generate_json(
            skill_name=skill_name,
            prompt=prompt,
            input_payload=input_payload,
            output_schema=output_schema,
        )
        try:
            result_data = _loads_object(raw)
            result = result_model.model_validate(result_data)
            result_dict = _model_dump(result)
            status: Literal["succeeded", "blocked"] = "blocked" if result_dict.get("warning") else "succeeded"
            warnings = _warnings(skill_name, result_dict)
            if skill_name == "revenue_retention" and is_regulated_revenue_request(input_payload):
                warnings.append("Regulated advice request detected; output is limited to operational business analysis.")
            envelope_model = SkillEnvelope(
                skill_name=skill_name,
                skill_version=str(envelope.get("skill_version", "v1")),
                status=status,
                summary=_summary_for(skill_name, result_dict),
                result=result_dict,
                recommended_next_actions=_recommended_next_actions(skill_name, result_dict),
                entities_to_create=_entities_to_create(skill_name, result_dict),
                entities_to_update=[],
                warnings=warnings,
                confidence_score=80 if status == "succeeded" else 60,
            )
            return _model_dump(envelope_model)
        except (ValueError, ValidationError, json.JSONDecodeError) as exc:
            last_error = exc

    raise ValueError(f"{skill_name} returned invalid JSON after repair attempt: {last_error}")
