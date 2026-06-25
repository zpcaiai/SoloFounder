from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DirectionScores(BaseModel):
    pain_intensity: int = Field(ge=0, le=10)
    willingness_to_pay: int = Field(ge=0, le=10)
    speed_to_revenue: int = Field(ge=0, le=10)
    delivery_difficulty: int = Field(ge=0, le=10)
    founder_market_fit: int = Field(ge=0, le=10)
    differentiation: int = Field(ge=0, le=10)
    repeat_purchase: int = Field(ge=0, le=10)


class BusinessDirection(BaseModel):
    name: str
    target_customer: str
    pain_point: str
    possible_offer: str
    revenue_model: str
    scores: DirectionScores
    risks: list[str]
    validation_steps: list[str]


class FounderProfileDiagnosisResult(BaseModel):
    founder_summary: str
    strongest_assets: list[str]
    hidden_monetizable_assets: list[str]
    weaknesses: list[str]
    constraints: list[Any]
    business_directions: list[BusinessDirection]
    recommended_direction: str
    avoid_list: list[str]
    seven_day_plan: list[str]


class NicheRanking(BaseModel):
    rank: int
    niche: str
    ideal_customer: str
    painful_problem: str
    current_alternatives: list[str]
    why_alternatives_fail: str
    first_offer: str
    pricing_range: str
    first_20_prospect_types: list[str]
    validation_method: str
    main_risk: str
    score: int = Field(ge=0, le=100)


class NicheSelectionResult(BaseModel):
    niche_rankings: list[NicheRanking]
    final_recommendation: str
    why_this_niche_first: str
    niche_positioning_statement: str
    next_actions: list[str]


class CoreAssumption(BaseModel):
    assumption: str
    risk_level: Literal["low", "medium", "high"]
    validation_method: str
    success_signal: str
    failure_signal: str


class ValidationDay(BaseModel):
    day: int
    task: str
    output: str
    success_metric: str


class LandingPageTest(BaseModel):
    headline: str
    cta: str
    conversion_goal: str


class PricingTest(BaseModel):
    low: str
    middle: str
    premium: str
    what_to_measure: str


class GoNoGoCriteria(BaseModel):
    go: list[str]
    pivot: list[str]
    stop: list[str]


class MarketValidationResult(BaseModel):
    validation_goal: str
    core_assumptions: list[CoreAssumption]
    seven_day_validation_plan: list[ValidationDay]
    interview_targets: list[str]
    landing_page_test: LandingPageTest
    pricing_test: PricingTest
    go_no_go_criteria: GoNoGoCriteria


class PrimaryPersona(BaseModel):
    name: str
    role: str
    business_type: str
    company_size: str
    revenue_stage: str
    daily_workflow: str
    top_pains: list[str]
    desired_outcomes: list[str]
    buying_triggers: list[str]
    budget_source: str
    decision_criteria: list[str]
    objections: list[str]
    trusted_channels: list[str]
    phrases_they_use: list[str]


class SecondaryPersona(BaseModel):
    name: str
    role: str
    when_to_target: str


class CustomerPersonaResult(BaseModel):
    primary_persona: PrimaryPersona
    secondary_persona: SecondaryPersona
    jobs_to_be_done: list[str]
    where_to_find_them: list[str]
    research_questions: list[str]


class InterviewQuestion(BaseModel):
    question: str
    purpose: str
    follow_ups: list[str]


class ScoringRubric(BaseModel):
    pain_intensity: str
    frequency: str
    current_spend: str
    urgency: str
    decision_power: str
    willingness_to_try_paid_pilot: str


class PostInterviewSummaryTemplate(BaseModel):
    customer_context: str
    pain_evidence: str
    current_workaround: str
    budget_signal: str
    urgency_signal: str
    exact_quotes: list[str]
    recommended_next_action: str


class PainInterviewResult(BaseModel):
    interview_questions: list[InterviewQuestion]
    red_flags: list[str]
    buying_signals: list[str]
    scoring_rubric: ScoringRubric
    post_interview_summary_template: PostInterviewSummaryTemplate


class OfferDeliverable(BaseModel):
    name: str
    description: str
    acceptance_criteria: list[str]


class PricingTier(BaseModel):
    price: str
    scope: list[str]
    best_for: str


class OfferPricing(BaseModel):
    starter: PricingTier
    standard: PricingTier
    premium: PricingTier


class ProductizedOfferResult(BaseModel):
    offer_name: str
    one_line_promise: str
    target_customer: str
    pain: str
    desired_result: str
    deliverables: list[OfferDeliverable]
    timeline: str
    pricing: OfferPricing
    guarantee: str | None = None
    who_this_is_for: list[str]
    who_this_is_not_for: list[str]
    scope_boundaries: list[str]
    client_requirements: list[str]
    upsell_path: list[str]
    retainer_path: str | None = None
    first_paid_pilot: dict[str, Any]


class HeroSection(BaseModel):
    headline: str
    subheadline: str
    cta: str


class TextBulletsSection(BaseModel):
    title: str
    body: str
    bullets: list[str] = Field(default_factory=list)


class AgitationSection(BaseModel):
    title: str
    body: str
    cost_of_inaction: list[str]


class TextSection(BaseModel):
    title: str
    body: str


class ProcessStep(BaseModel):
    step: int
    title: str
    description: str


class CredibilitySection(BaseModel):
    founder_credibility: str
    proof_points: list[str]


class PricingSection(BaseModel):
    title: str
    tiers: list[Any]


class FAQ(BaseModel):
    question: str
    answer: str


class FinalCTA(BaseModel):
    headline: str
    button_text: str
    supporting_text: str


class LandingPageResult(BaseModel):
    hero: HeroSection
    problem_section: TextBulletsSection
    agitation_section: AgitationSection
    solution_section: TextSection
    deliverables: list[Any]
    process: list[ProcessStep]
    credibility: CredibilitySection
    pricing_section: PricingSection
    faq: list[FAQ]
    final_cta: FinalCTA


class OutreachEmail(BaseModel):
    subject: str
    body: str


class ObjectionResponse(BaseModel):
    objection: str
    response: str


class ContentPost(BaseModel):
    platform: str
    post: str
    cta: str


class SalesOutreachResult(BaseModel):
    cold_email: OutreachEmail
    linkedin_dm: str
    wechat_dm: str
    x_dm: str
    follow_up_1: str
    follow_up_2: str
    soft_cta: str
    objection_responses: list[ObjectionResponse]
    referral_request: str
    content_posts: list[ContentPost]
    human_approval_required: bool
    warning: str | None = None
    safe_alternative: dict[str, Any] | None = None


class LeadAssessment(BaseModel):
    qualification_score: int = Field(ge=0, le=100)
    fit_level: Literal["low", "medium", "high"]
    budget_signal: str
    urgency_signal: str
    decision_power_signal: str
    pain_intensity_signal: str


class NextBestAction(BaseModel):
    action: str
    reason: str
    deadline: str
    message_draft: str


class ObjectionAnalysis(BaseModel):
    objection: str
    meaning: str
    response_strategy: str


class Forecast(BaseModel):
    probability: int = Field(ge=0, le=100)
    expected_close_date: str
    expected_value: float


class CRMDealCoachResult(BaseModel):
    lead_assessment: LeadAssessment
    recommended_stage: str
    deal_risks: list[str]
    next_best_action: NextBestAction
    objection_analysis: list[ObjectionAnalysis]
    forecast: Forecast


class ProposalDeliverable(BaseModel):
    name: str
    description: str
    acceptance_criteria: list[str]


class ProposalTimelinePhase(BaseModel):
    phase: str
    duration: str
    deliverables: list[str]


class ProposalPricing(BaseModel):
    amount: str
    currency: str
    payment_terms: str


class ProposalResult(BaseModel):
    proposal_title: str
    client_name: str
    problem_summary: str
    proposed_solution: str
    scope: list[str]
    out_of_scope: list[str]
    deliverables: list[ProposalDeliverable]
    timeline: list[ProposalTimelinePhase]
    pricing: ProposalPricing
    client_responsibilities: list[str]
    change_request_policy: str
    terms: str
    next_step: str


class DeliveryMilestone(BaseModel):
    name: str
    deadline: str
    tasks: list[str]
    deliverables: list[str]
    review_required: bool


class DeliveryTask(BaseModel):
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    due_date: str
    status: str


class DeliveryProjectResult(BaseModel):
    project_title: str
    client_name: str
    onboarding_form: list[str]
    clarification_questions: list[str]
    milestones: list[DeliveryMilestone]
    tasks: list[DeliveryTask]
    deliverables: list[OfferDeliverable]
    risks: list[str]
    acceptance_criteria: list[str]
    change_request_policy: str
    handoff_checklist: list[str]


class RevenueSummary(BaseModel):
    total_revenue: float
    current_month_revenue: float
    average_deal_size: float
    best_offer: str
    weakest_offer: str


class BusinessDiagnosis(BaseModel):
    main_bottleneck: str
    conversion_issue: str
    pricing_issue: str
    delivery_issue: str
    retention_issue: str


class RecommendedAction(BaseModel):
    action: str
    reason: str
    expected_impact: str
    priority: Literal["low", "medium", "high"]


class RetentionOpportunity(BaseModel):
    customer_name: str
    suggested_next_offer: str
    upsell_reason: str
    follow_up_message: str


class CaseStudyCandidate(BaseModel):
    customer_name: str
    why_useful: str
    case_study_angle: str


class RevenueRetentionResult(BaseModel):
    revenue_summary: RevenueSummary
    business_diagnosis: BusinessDiagnosis
    recommended_actions: list[RecommendedAction]
    retention_opportunities: list[RetentionOpportunity]
    case_study_candidates: list[CaseStudyCandidate]
    next_7_day_operating_plan: list[str]


class RecommendedProduct(BaseModel):
    product_name: str
    product_type: str
    target_audience: str
    promise: str
    modules: list[str]
    pricing_model: str
    sales_angle: str


class LeadMagnet(BaseModel):
    title: str
    format: str
    outline: list[str]


class ContentToProductResult(BaseModel):
    knowledge_asset_summary: str
    core_themes: list[str]
    monetizable_angles: list[str]
    recommended_products: list[RecommendedProduct]
    course_outline: list[str]
    training_camp_plan: list[str]
    lead_magnet: LeadMagnet
    next_actions: list[str]


RESULT_MODELS: dict[str, type[BaseModel]] = {
    "founder_profile_diagnosis": FounderProfileDiagnosisResult,
    "niche_selection": NicheSelectionResult,
    "market_validation": MarketValidationResult,
    "customer_persona": CustomerPersonaResult,
    "pain_interview": PainInterviewResult,
    "productized_offer": ProductizedOfferResult,
    "landing_page": LandingPageResult,
    "sales_outreach": SalesOutreachResult,
    "crm_deal_coach": CRMDealCoachResult,
    "proposal": ProposalResult,
    "delivery_project": DeliveryProjectResult,
    "revenue_retention": RevenueRetentionResult,
    "content_to_product": ContentToProductResult,
}
