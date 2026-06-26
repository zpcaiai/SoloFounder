from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from app.core.config import get_settings


class AIProvider(Protocol):
    async def generate_json(
        self,
        *,
        skill_name: str,
        prompt: str,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
    ) -> str:
        """Return a JSON object string for the requested skill."""


@dataclass(slots=True)
class DeterministicRevenuePilotProvider:
    """Local provider used for tests and development without an API key."""

    async def generate_json(
        self,
        *,
        skill_name: str,
        prompt: str,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
    ) -> str:
        return json.dumps(
            sample_result_for_skill(skill_name, input_payload),
            ensure_ascii=False,
        )


def sample_result_for_skill(skill_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    niche = payload.get("selected_niche") or payload.get("niche") or payload.get("target_audience") or "local service businesses"
    offer_name = "7-Day AI Lead Follow-up Sprint"
    persona_name = "Operations-minded Owner"

    samples: dict[str, dict[str, Any]] = {
        "founder_profile_diagnosis": {
            "founder_summary": "The founder has enough practical expertise to sell a narrow productized service before building software.",
            "strongest_assets": ["domain experience", "technical execution", "direct founder time"],
            "hidden_monetizable_assets": ["repeatable workflows", "existing notes", "customer context"],
            "weaknesses": ["limited validation evidence", "thin distribution"],
            "constraints": payload.get("founder_profile", {}).get("constraints", []),
            "business_directions": [
                {
                    "name": "AI lead follow-up automation for immigration consultants",
                    "target_customer": "Small immigration consulting firms that miss inquiries after hours",
                    "pain_point": "Leads go cold because responses are slow and inconsistent.",
                    "possible_offer": offer_name,
                    "revenue_model": "Fixed-scope sprint plus monthly optimization retainer",
                    "scores": {
                        "pain_intensity": 8,
                        "willingness_to_pay": 8,
                        "speed_to_revenue": 9,
                        "delivery_difficulty": 5,
                        "founder_market_fit": 8,
                        "differentiation": 7,
                        "repeat_purchase": 8,
                    },
                    "risks": ["Needs proof that missed leads are measurable."],
                    "validation_steps": ["Interview 5 firms", "Offer one paid pilot", "Measure reply-time improvement"],
                }
            ],
            "recommended_direction": "AI lead follow-up automation for immigration consultants",
            "avoid_list": ["Building a full SaaS before paid validation", "Broad AI consulting"],
            "seven_day_plan": [
                "List 20 target firms",
                "Run 5 discovery calls",
                "Sell one paid pilot",
                "Document the manual workflow before automating",
            ],
        },
        "niche_selection": {
            "niche_rankings": [
                {
                    "rank": 1,
                    "niche": niche,
                    "ideal_customer": "Owner-led businesses with urgent lead response gaps",
                    "painful_problem": "Qualified leads are lost when replies are delayed.",
                    "current_alternatives": ["manual inbox checking", "VA follow-up", "generic CRM reminders"],
                    "why_alternatives_fail": "They do not connect intake context to timely, specific follow-up.",
                    "first_offer": offer_name,
                    "pricing_range": "$750-$2,500 pilot",
                    "first_20_prospect_types": ["solo consultancies", "small agencies", "professional service firms"],
                    "validation_method": "Low-volume personalized outreach plus paid pilot conversations",
                    "main_risk": "Prospects may not know their lost-lead value.",
                    "score": 86,
                }
            ],
            "final_recommendation": niche,
            "why_this_niche_first": "The pain is operational, measurable, and can be solved manually before productization.",
            "niche_positioning_statement": f"AI lead follow-up systems for {niche} that cannot afford slow replies.",
            "next_actions": ["Interview 5 prospects", "Price one pilot", "Create a simple before/after demo"],
        },
        "market_validation": {
            "validation_goal": "Confirm prospects have frequent, costly lead follow-up delays and will pay for a pilot.",
            "core_assumptions": [
                {
                    "assumption": "Slow follow-up causes lost revenue.",
                    "risk_level": "high",
                    "validation_method": "Interview and review recent missed inquiries.",
                    "success_signal": "Three prospects can name recent lost leads.",
                    "failure_signal": "Prospects do not see response time as a business issue.",
                }
            ],
            "seven_day_validation_plan": [
                {"day": 1, "task": "Build a 30-prospect list", "output": "Prospect sheet", "success_metric": "30 relevant prospects"},
                {"day": 2, "task": "Send 10 personalized notes", "output": "Outreach sent", "success_metric": "2 replies"},
                {"day": 3, "task": "Run discovery calls", "output": "Interview notes", "success_metric": "2 pain-confirming calls"},
                {"day": 4, "task": "Draft paid pilot scope", "output": "One-page pilot", "success_metric": "Clear fixed scope"},
                {"day": 5, "task": "Pitch paid pilot", "output": "Pilot proposal", "success_metric": "1 verbal yes"},
                {"day": 6, "task": "Collect objections", "output": "Objection log", "success_metric": "Top 3 objections known"},
                {"day": 7, "task": "Decide go/pivot/stop", "output": "Decision memo", "success_metric": "Evidence-based decision"},
            ],
            "interview_targets": ["owners", "operations managers", "front-desk coordinators"],
            "landing_page_test": {
                "headline": "Stop losing warm leads to slow follow-up",
                "cta": "Book a 15-minute workflow audit",
                "conversion_goal": "3 qualified calls from 30 prospects",
            },
            "pricing_test": {
                "low": "$750",
                "middle": "$1,500",
                "premium": "$2,500",
                "what_to_measure": "Whether price resistance is about budget, trust, or unclear ROI.",
            },
            "go_no_go_criteria": {
                "go": ["At least 3 strong pain signals", "1 paid pilot commitment"],
                "pivot": ["Pain exists but buyer differs", "Budget exists for a smaller scope"],
                "stop": ["No urgent pain", "No willingness to pay"],
            },
        },
        "customer_persona": {
            "primary_persona": {
                "name": persona_name,
                "role": "Owner or operations lead",
                "business_type": niche,
                "company_size": "2-25 staff",
                "revenue_stage": "Revenue-generating and capacity constrained",
                "daily_workflow": "Juggles client delivery, inbox triage, and sales follow-up.",
                "top_pains": ["slow lead response", "manual follow-up", "unclear pipeline status"],
                "desired_outcomes": ["faster replies", "more booked calls", "less inbox anxiety"],
                "buying_triggers": ["missed high-value inquiry", "new marketing spend", "staff overload"],
                "budget_source": "operations or sales enablement budget",
                "decision_criteria": ["clear ROI", "low implementation burden", "fixed scope"],
                "objections": ["Will this sound robotic?", "Will it disrupt my current tools?"],
                "trusted_channels": ["LinkedIn", "referrals", "industry groups"],
                "phrases_they_use": ["I know we are leaving money in the inbox.", "I need this handled without another tool to babysit."],
            },
            "secondary_persona": {
                "name": "Front-office Coordinator",
                "role": "Daily workflow owner",
                "when_to_target": "When the owner delegates intake and follow-up operations.",
            },
            "jobs_to_be_done": ["Capture inquiries", "Respond quickly", "Book qualified calls", "Track next steps"],
            "where_to_find_them": ["LinkedIn search", "local business groups", "industry directories"],
            "research_questions": ["What happens after a web inquiry arrives?", "How many leads wait more than one business day?"],
        },
        "pain_interview": {
            "interview_questions": [
                {
                    "question": "Tell me about the last time a promising inquiry did not turn into a call.",
                    "purpose": "Find recent concrete pain.",
                    "follow_ups": ["When did it happen?", "What did you do next?", "What did it cost?"],
                },
                {
                    "question": "How do new inquiries move from first message to booked call today?",
                    "purpose": "Map current workflow.",
                    "follow_ups": ["Who owns each step?", "Where do delays happen?"],
                },
            ],
            "red_flags": ["No recent examples", "No owner concern", "Problem is annoying but not costly"],
            "buying_signals": ["Mentions lost revenue", "Has tried tools or staff fixes", "Asks about pilot price"],
            "scoring_rubric": {
                "pain_intensity": "1=no issue, 5=visible cost, 10=urgent revenue leak",
                "frequency": "How often the issue appears per month",
                "current_spend": "Money or staff time already spent on workarounds",
                "urgency": "Deadline or trigger forcing action",
                "decision_power": "Can approve a pilot without committee delay",
                "willingness_to_try_paid_pilot": "Will commit money to a narrow test",
            },
            "post_interview_summary_template": {
                "customer_context": "",
                "pain_evidence": "",
                "current_workaround": "",
                "budget_signal": "",
                "urgency_signal": "",
                "exact_quotes": [],
                "recommended_next_action": "",
            },
        },
        "productized_offer": {
            "offer_name": offer_name,
            "one_line_promise": "In 7 days, install a practical lead follow-up workflow that turns slow replies into booked calls.",
            "target_customer": niche,
            "pain": "Warm leads are lost because follow-up is slow, inconsistent, or manual.",
            "desired_result": "A tested intake-to-follow-up workflow with clear owner approval points.",
            "deliverables": [
                {
                    "name": "Lead response workflow map",
                    "description": "Current-state and future-state intake flow.",
                    "acceptance_criteria": ["All lead sources documented", "Owner approves future-state flow"],
                },
                {
                    "name": "Follow-up message kit",
                    "description": "Human-approved email or DM drafts for common lead scenarios.",
                    "acceptance_criteria": ["Includes first response and two follow-ups", "Tone approved by client"],
                },
            ],
            "timeline": "7 business days",
            "pricing": {
                "starter": {"price": "$750", "scope": ["workflow audit", "message kit"], "best_for": "validation"},
                "standard": {"price": "$1,500", "scope": ["audit", "message kit", "CRM setup"], "best_for": "most teams"},
                "premium": {"price": "$2,500", "scope": ["standard", "automation setup", "30-day review"], "best_for": "busy teams"},
            },
            "guarantee": "If the workflow is not approved in 7 business days, the founder adds one revision cycle at no extra charge.",
            "who_this_is_for": ["Teams with inbound inquiries", "Owners who can approve a pilot quickly"],
            "who_this_is_not_for": ["Teams with no lead flow", "Buyers seeking a custom SaaS build"],
            "scope_boundaries": ["No paid ads management", "No legal or compliance advice", "No mass outreach"],
            "client_requirements": ["Provide lead sources", "Approve messages", "Attend kickoff and review"],
            "upsell_path": ["Monthly optimization", "CRM reporting", "Team training"],
            "retainer_path": "$500-$1,500/month for monitoring, testing, and workflow improvements.",
            "first_paid_pilot": {"price": "$750", "duration": "7 days", "deliverable": "workflow audit and message kit"},
        },
        "landing_page": {
            "hero": {
                "headline": "Stop losing warm leads to slow follow-up",
                "subheadline": "A 7-day sprint for owner-led service businesses that need faster, clearer lead response.",
                "cta": "Book a 15-minute workflow audit",
            },
            "problem_section": {
                "title": "Your best leads should not disappear in the inbox",
                "body": "When inquiry follow-up depends on memory and spare time, qualified buyers cool off.",
                "bullets": ["Replies happen too late", "Follow-ups are inconsistent", "No one knows which leads need action"],
            },
            "agitation_section": {
                "title": "Slow response quietly taxes growth",
                "body": "The cost is not only missed calls. It is wasted marketing spend and owner attention.",
                "cost_of_inaction": ["lost revenue", "more manual checking", "unclear pipeline"],
            },
            "solution_section": {
                "title": "A fixed-scope lead follow-up sprint",
                "body": "We map your intake flow, draft human-approved follow-up assets, and set a simple operating rhythm.",
            },
            "deliverables": ["workflow map", "message kit", "handoff checklist"],
            "process": [
                {"step": 1, "title": "Audit", "description": "Review lead sources and handoff points."},
                {"step": 2, "title": "Build", "description": "Create the follow-up workflow and message kit."},
                {"step": 3, "title": "Review", "description": "Approve scope, tone, and next actions."},
            ],
            "credibility": {
                "founder_credibility": "Built for solo operators who need practical systems, not bloated tooling.",
                "proof_points": ["fixed scope", "human approval", "measurable workflow"],
            },
            "pricing_section": {"title": "Pilot pricing", "tiers": ["$750 starter", "$1,500 standard", "$2,500 premium"]},
            "faq": [{"question": "Will this send messages automatically?", "answer": "Outbound content requires human approval before sending."}],
            "final_cta": {
                "headline": "Find the lead leaks this week",
                "button_text": "Book a workflow audit",
                "supporting_text": "Low-volume, practical, and fixed in scope.",
            },
        },
        "sales_outreach": {
            "cold_email": {
                "subject": "Quick idea for faster lead follow-up",
                "body": "Hi, I noticed your team likely handles inquiries across several channels. I help owner-led teams tighten the path from inquiry to booked call without adding a heavy tool. Would a 15-minute workflow audit be useful?",
            },
            "linkedin_dm": "Saw your work with clients in this space. I help teams reduce slow lead follow-up with a fixed 7-day workflow sprint. Open to a quick audit?",
            "wechat_dm": "你好，我在帮小团队优化从咨询到预约的跟进流程。不是群发工具，而是先梳理流程和人工确认话术。方便约 15 分钟看看是否适合吗？",
            "x_dm": "I help owner-led service teams stop losing warm leads to slow follow-up. Worth a quick workflow audit?",
            "follow_up_1": "Following up once. If lead response is already handled well, no worries. If not, I can share a simple audit checklist.",
            "follow_up_2": "Last note from me. Happy to send the checklist even if now is not a fit.",
            "soft_cta": "Would it be useful to compare your current response workflow against a simple 7-day improvement checklist?",
            "objection_responses": [{"objection": "We already use a CRM.", "response": "That helps. This focuses on whether the CRM workflow produces timely, specific follow-up."}],
            "referral_request": "Do you know one owner-led team that loses leads because follow-up is too slow?",
            "content_posts": [
                {"platform": "LinkedIn", "post": "Slow follow-up is often a workflow problem, not a motivation problem.", "cta": "Comment audit if you want the checklist."},
                {"platform": "X", "post": "Before buying another CRM, map the first 15 minutes after a lead arrives.", "cta": "DM for the checklist."},
                {"platform": "WeChat", "post": "很多线索不是没有需求，而是等回复时冷掉了。先做流程体检，再谈自动化。", "cta": "回复“体检”获取清单。"},
            ],
            "human_approval_required": True,
        },
        "crm_deal_coach": {
            "lead_assessment": {
                "qualification_score": 72,
                "fit_level": "high",
                "budget_signal": "Asked about pilot pricing",
                "urgency_signal": "Recent missed lead",
                "decision_power_signal": "Owner involved",
                "pain_intensity_signal": "Revenue leak described with examples",
            },
            "recommended_stage": "qualified",
            "deal_risks": ["ROI not quantified", "No scheduled next meeting"],
            "next_best_action": {
                "action": "Send a narrow paid pilot proposal",
                "reason": "The pain is concrete and the buyer asked about pricing.",
                "deadline": "within 24 hours",
                "message_draft": "Based on what you shared, I suggest a fixed 7-day pilot focused on response time and booked-call conversion.",
            },
            "objection_analysis": [{"objection": "Need to think", "meaning": "Value or scope unclear", "response_strategy": "Clarify pilot outcome and risk reversal"}],
            "forecast": {"probability": 45, "expected_close_date": "within 14 days", "expected_value": 1500},
        },
        "proposal": {
            "proposal_title": "7-Day Lead Follow-up Workflow Sprint",
            "client_name": "Client",
            "problem_summary": "Inbound inquiries are not consistently converted into booked calls.",
            "proposed_solution": "Map the intake workflow, create approved follow-up messages, and define a simple operating rhythm.",
            "scope": ["kickoff", "workflow audit", "message kit", "review session"],
            "out_of_scope": ["paid ads", "legal advice", "mass outreach", "custom SaaS"],
            "deliverables": [
                {"name": "Workflow map", "description": "Lead intake and follow-up flow", "acceptance_criteria": ["Client approval"]},
                {"name": "Message kit", "description": "Approved first reply and follow-ups", "acceptance_criteria": ["Tone approved"]},
            ],
            "timeline": [{"phase": "Sprint", "duration": "7 business days", "deliverables": ["workflow map", "message kit"]}],
            "pricing": {"amount": "$1,500", "currency": "USD", "payment_terms": "50% upfront, 50% on delivery"},
            "client_responsibilities": ["Provide lead examples", "Attend kickoff", "Review drafts within 2 business days"],
            "change_request_policy": "Requests outside the agreed scope are quoted separately before work begins.",
            "terms": "Commercial proposal only; complex contracts should receive formal legal review.",
            "next_step": "Approve proposal and schedule kickoff.",
        },
        "delivery_project": {
            "project_title": "Lead Follow-up Sprint Delivery Plan",
            "client_name": "Client",
            "onboarding_form": ["Lead sources", "Current CRM", "Response templates", "Approval owner"],
            "clarification_questions": ["Which leads are highest value?", "Who approves final message tone?"],
            "milestones": [
                {
                    "name": "Kickoff and audit",
                    "deadline": "Day 2",
                    "tasks": ["collect materials", "map current flow"],
                    "deliverables": ["current-state map"],
                    "review_required": True,
                },
                {
                    "name": "Build and handoff",
                    "deadline": "Day 7",
                    "tasks": ["draft messages", "final review"],
                    "deliverables": ["message kit", "handoff checklist"],
                    "review_required": True,
                },
            ],
            "tasks": [
                {"title": "Collect lead examples", "description": "Gather 5 recent inquiries.", "priority": "high", "due_date": "Day 1", "status": "todo"},
                {"title": "Draft follow-up kit", "description": "Create first reply and follow-ups.", "priority": "medium", "due_date": "Day 5", "status": "todo"},
            ],
            "deliverables": [{"name": "Handoff checklist", "description": "Operating instructions", "acceptance_criteria": ["Client can run workflow without founder present"]}],
            "risks": ["late client feedback", "unclear ownership", "scope expansion"],
            "acceptance_criteria": ["Workflow approved", "Messages approved", "Handoff checklist delivered"],
            "change_request_policy": "New channels or automation beyond agreed scope require a change request.",
            "handoff_checklist": ["confirm owner", "confirm review cadence", "schedule 30-day check-in"],
        },
        "revenue_retention": {
            "revenue_summary": {
                "total_revenue": 1500,
                "current_month_revenue": 1500,
                "average_deal_size": 1500,
                "best_offer": offer_name,
                "weakest_offer": "Unvalidated broad consulting",
            },
            "business_diagnosis": {
                "main_bottleneck": "Not enough qualified conversations",
                "conversion_issue": "Proposal step needs clearer ROI",
                "pricing_issue": "Pilot can move from $750 to $1,500 after proof",
                "delivery_issue": "Client feedback delays need firm review points",
                "retention_issue": "No monthly optimization package attached yet",
            },
            "recommended_actions": [{"action": "Create a 30-day optimization retainer", "reason": "Workflow performance improves through iteration.", "expected_impact": "recurring revenue", "priority": "high"}],
            "retention_opportunities": [{"customer_name": "Client", "suggested_next_offer": "Monthly follow-up optimization", "upsell_reason": "Improve booked-call conversion after launch", "follow_up_message": "Would it be useful to review lead response metrics after 30 days?"}],
            "case_study_candidates": [{"customer_name": "Client", "why_useful": "Clear before/after workflow", "case_study_angle": "From slow replies to consistent booked-call follow-up"}],
            "next_7_day_operating_plan": ["Review pipeline", "Follow up with warm leads", "Package retainer", "Ask for one referral"],
        },
        "content_to_product": {
            "knowledge_asset_summary": "The imported assets contain reusable teaching material that can become a structured product.",
            "core_themes": ["formation", "practical application", "repeatable learning path"],
            "monetizable_angles": ["cohort course", "resource kit", "guided workshop"],
            "recommended_products": [
                {
                    "product_name": "6-Week Guided Learning Cohort",
                    "product_type": "course",
                    "target_audience": niche,
                    "promise": "Turn scattered notes into a guided learning path.",
                    "modules": ["orientation", "core framework", "practice", "reflection", "implementation", "review"],
                    "pricing_model": "cohort fee or church/group license",
                    "sales_angle": "Service-oriented education with practical outcomes.",
                }
            ],
            "course_outline": ["Week 1 foundation", "Week 2 framework", "Week 3 practice", "Week 4 feedback", "Week 5 application", "Week 6 handoff"],
            "training_camp_plan": ["live kickoff", "weekly exercises", "office hours", "final implementation plan"],
            "lead_magnet": {"title": "Readiness Checklist", "format": "PDF", "outline": ["pain", "readiness", "next step"]},
            "next_actions": ["Choose first audience", "Validate promise", "Run paid pilot cohort"],
        },
    }

    try:
        return samples[skill_name]
    except KeyError as exc:
        raise ValueError(f"Unknown skill for deterministic provider: {skill_name}") from exc


_provider: AIProvider | None = None


def _build_provider_from_env() -> AIProvider:
    name = get_settings().ai_provider
    if name in {"anthropic", "claude"}:
        from app.ai.anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    return DeterministicRevenuePilotProvider()


def get_ai_provider() -> AIProvider:
    global _provider
    if _provider is None:
        _provider = _build_provider_from_env()
    return _provider


def set_ai_provider(provider: AIProvider) -> None:
    global _provider
    _provider = provider


def reset_ai_provider() -> None:
    """Clear the cached provider so the next call re-reads the environment."""
    global _provider
    _provider = None
