from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class FounderProfileCreate(BaseModel):
    skills: list[str] = Field(default_factory=list)
    work_experience: list[dict[str, Any]] = Field(default_factory=list)
    domain_expertise: list[str] = Field(default_factory=list)
    technical_ability: dict[str, Any] = Field(default_factory=dict)
    sales_experience: dict[str, Any] = Field(default_factory=dict)
    existing_content: list[dict[str, Any]] = Field(default_factory=list)
    audience_assets: dict[str, Any] = Field(default_factory=dict)
    personal_network: dict[str, Any] = Field(default_factory=dict)
    time_available_per_week: int | None = None
    monthly_income_goal: float | None = None
    preferred_customer_type: str | None = None
    constraints: list[str] = Field(default_factory=list)
    values_or_mission: str | None = None


class FounderProfileUpdate(FounderProfileCreate):
    pass


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None


class IdeaCreate(BaseModel):
    title: str
    description: str | None = None
    target_customer: str | None = None
    pain_point: str | None = None
    possible_offer: str | None = None
    scores: dict[str, Any] = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)
    validation_steps: list[str] = Field(default_factory=list)


class IdeaUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    target_customer: str | None = None
    pain_point: str | None = None
    possible_offer: str | None = None
    scores: dict[str, Any] | None = None
    risks: list[str] | None = None
    validation_steps: list[str] | None = None
    status: str | None = None


class PersonaCreate(BaseModel):
    name: str | None = None
    role: str | None = None
    business_type: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class PersonaUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    business_type: str | None = None
    payload: dict[str, Any] | None = None


class OfferCreate(BaseModel):
    offer_name: str
    one_line_promise: str | None = None
    target_customer: str | None = None
    pain: str | None = None
    desired_result: str | None = None
    deliverables: list[dict[str, Any]] = Field(default_factory=list)
    timeline: str | None = None
    pricing: dict[str, Any] = Field(default_factory=dict)
    guarantee: str | None = None
    scope_boundaries: list[str] = Field(default_factory=list)
    client_requirements: list[str] = Field(default_factory=list)
    upsell_path: list[str] = Field(default_factory=list)
    retainer_path: str | None = None


class OfferUpdate(BaseModel):
    offer_name: str | None = None
    one_line_promise: str | None = None
    target_customer: str | None = None
    pain: str | None = None
    desired_result: str | None = None
    deliverables: list[dict[str, Any]] | None = None
    timeline: str | None = None
    pricing: dict[str, Any] | None = None
    guarantee: str | None = None
    scope_boundaries: list[str] | None = None
    client_requirements: list[str] | None = None
    upsell_path: list[str] | None = None
    retainer_path: str | None = None
    status: str | None = None


class LandingPageCreate(BaseModel):
    title: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    published: bool = False


class LandingPageUpdate(BaseModel):
    title: str | None = None
    payload: dict[str, Any] | None = None
    published: bool | None = None


class OutreachCreate(BaseModel):
    channel: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    human_approval_required: bool = True


class OutreachUpdate(BaseModel):
    channel: str | None = None
    payload: dict[str, Any] | None = None
    human_approval_required: bool | None = None


class LeadCreate(BaseModel):
    name: str | None = None
    company: str | None = None
    email: str | None = None
    source: str | None = None
    status: str = "new"
    payload: dict[str, Any] = Field(default_factory=dict)


class LeadUpdate(BaseModel):
    name: str | None = None
    company: str | None = None
    email: str | None = None
    source: str | None = None
    status: str | None = None
    payload: dict[str, Any] | None = None


class DealCreate(BaseModel):
    lead_id: str | None = None
    offer_id: str | None = None
    stage: str = "new"
    expected_value: float | None = None
    probability: int | None = None
    expected_close_date: date | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class DealUpdate(BaseModel):
    lead_id: str | None = None
    offer_id: str | None = None
    stage: str | None = None
    expected_value: float | None = None
    probability: int | None = None
    expected_close_date: date | None = None
    payload: dict[str, Any] | None = None


class ProposalCreate(BaseModel):
    deal_id: str | None = None
    title: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = "draft"


class ProposalUpdate(BaseModel):
    title: str | None = None
    payload: dict[str, Any] | None = None
    status: str | None = None


class DeliveryProjectCreate(BaseModel):
    deal_id: str | None = None
    proposal_id: str | None = None
    title: str | None = None
    client_name: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = "todo"


class DeliveryProjectUpdate(BaseModel):
    title: str | None = None
    client_name: str | None = None
    payload: dict[str, Any] | None = None
    status: str | None = None


class DeliveryTaskCreate(BaseModel):
    delivery_project_id: str
    title: str
    description: str | None = None
    priority: str = "medium"
    status: str = "todo"
    due_date: date | None = None


class DeliveryTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    due_date: date | None = None


class RevenueCreate(BaseModel):
    deal_id: str | None = None
    offer_id: str | None = None
    customer_name: str | None = None
    amount: float = 0
    currency: str = "USD"
    received_at: date | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class RevenueUpdate(BaseModel):
    deal_id: str | None = None
    offer_id: str | None = None
    customer_name: str | None = None
    amount: float | None = None
    currency: str | None = None
    received_at: date | None = None
    payload: dict[str, Any] | None = None


class KnowledgeAssetCreate(BaseModel):
    title: str
    asset_type: str | None = None
    raw_text: str | None = None
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)


class KnowledgeAssetUpdate(BaseModel):
    title: str | None = None
    asset_type: str | None = None
    raw_text: str | None = None
    summary: str | None = None
    tags: list[str] | None = None


class CustomerFeedbackCreate(BaseModel):
    customer_name: str | None = None
    feedback_type: str = "general"
    content: str | None = None
    rating: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class CustomerFeedbackUpdate(BaseModel):
    customer_name: str | None = None
    feedback_type: str | None = None
    content: str | None = None
    rating: int | None = None
    payload: dict[str, Any] | None = None


class DashboardSummary(BaseModel):
    total_revenue: float = 0
    total_deals: int = 0
    active_leads: int = 0
    open_delivery_projects: int = 0
    offers_count: int = 0
    recent_skill_runs: list[dict[str, Any]] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
