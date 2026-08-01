"""
Pydantic contracts for AI Account Research.

`ResearchPayload` is the strict schema the LLM must produce. It is validated
before anything is persisted — an unparseable or off-contract response fails
the generation rather than writing junk to the database.

The API response models mirror the stored columns so the frontend contract is
stable regardless of which provider or prompt version produced the report.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ── Vocabulary shared with the prompt ─────────────────────────

PriorityLevel = Literal["high", "medium", "low"]
RiskSeverity = Literal["high", "medium", "low"]
SignalStrength = Literal["strong", "moderate", "weak"]


# ── LLM output contract ───────────────────────────────────────

class BuyingSignalItem(BaseModel):
    """A buying signal the model identified, grounded in Avenor evidence."""
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    evidence: str = Field(..., min_length=1, max_length=1000)
    why_it_matters: str = Field(..., min_length=1, max_length=1000)
    strength: SignalStrength = "moderate"


class PainPointItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    evidence: str | None = Field(default=None, max_length=1000)
    priority: PriorityLevel = "medium"


class PersonaItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    rationale: str = Field(..., min_length=1, max_length=1000)
    # Populated only when a real Contact exists in the workspace.
    matched_contact_name: str | None = Field(default=None, max_length=255)
    priority: PriorityLevel = "medium"


class OutreachStrategy(BaseModel):
    model_config = ConfigDict(extra="ignore")

    recommended_channel: str = Field(..., min_length=1, max_length=100)
    timing: str = Field(..., min_length=1, max_length=500)
    angle: str = Field(..., min_length=1, max_length=2000)
    opening_hook: str = Field(..., min_length=1, max_length=1000)


class TalkingPointItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    point: str = Field(..., min_length=1, max_length=500)
    supporting_detail: str = Field(..., min_length=1, max_length=1000)


class RiskItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    mitigation: str | None = Field(default=None, max_length=1000)
    severity: RiskSeverity = "medium"


class NextActionItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: str = Field(..., min_length=1, max_length=500)
    rationale: str = Field(..., min_length=1, max_length=1000)
    priority: PriorityLevel = "medium"
    suggested_timeframe: str | None = Field(default=None, max_length=100)


class ResearchPayload(BaseModel):
    """The complete structured report the model must return."""
    model_config = ConfigDict(extra="ignore")

    summary: str = Field(..., min_length=1, max_length=4000)
    buying_signals: list[BuyingSignalItem] = Field(default_factory=list, max_length=10)
    pain_points: list[PainPointItem] = Field(default_factory=list, max_length=10)
    recommended_personas: list[PersonaItem] = Field(default_factory=list, max_length=10)
    outreach_strategy: OutreachStrategy
    talking_points: list[TalkingPointItem] = Field(default_factory=list, max_length=10)
    risks: list[RiskItem] = Field(default_factory=list, max_length=10)
    next_actions: list[NextActionItem] = Field(default_factory=list, max_length=10)


# ── API contracts ─────────────────────────────────────────────

ResearchStatusLiteral = Literal["none", "pending", "running", "completed", "failed"]

EmailStatusLiteral = Literal["pending", "running", "completed", "failed", "archived"]
BriefingStatusLiteral = Literal["none", "pending", "running", "completed", "failed", "archived"]
SalesCoachingStatusLiteral = Literal["none", "pending", "running", "completed", "failed", "archived"]
EmailTypeLiteral = Literal[
    "cold_email",
    "follow_up_email",
    "re_engagement_email",
    "meeting_request",
    "product_demo_invitation",
    "value_proposition_email",
]
EmailToneLiteral = Literal["professional", "friendly", "executive", "technical", "consultative"]
EmailLengthLiteral = Literal["short", "medium", "long"]
EmailCTALiteral = Literal["book_meeting", "demo", "quick_call", "reply", "learn_more"]
EmailVariationLiteral = Literal["A", "B", "C"]


class ResearchMeta(BaseModel):
    """Provenance for a generated report."""

    # The spec fixes these field names; `model_` is a Pydantic-protected
    # namespace by default, so it is cleared rather than renaming the contract.
    model_config = ConfigDict(protected_namespaces=())

    model_provider: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    generation_duration_ms: int | None = None
    input_hash: str | None = None


class ResearchResponse(BaseModel):
    """
    Returned by both POST and GET.

    `status = "none"` means the company is in your workspace but has no report
    yet — distinct from a 404, which means the company is not yours.
    """

    company_id: str
    status: ResearchStatusLiteral
    cached: bool = False
    is_stale: bool = False
    error_message: str | None = None

    summary: str | None = None
    buying_signals: list[BuyingSignalItem] = Field(default_factory=list)
    pain_points: list[PainPointItem] = Field(default_factory=list)
    recommended_personas: list[PersonaItem] = Field(default_factory=list)
    outreach_strategy: OutreachStrategy | None = None
    talking_points: list[TalkingPointItem] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)
    next_actions: list[NextActionItem] = Field(default_factory=list)

    meta: ResearchMeta = Field(default_factory=ResearchMeta)
    generated_at: datetime | None = None
    updated_at: datetime | None = None


# -- AI Email Generator contracts --------------------------------------------

class EmailPayload(BaseModel):
    """The structured JSON object the model must return for one email."""
    model_config = ConfigDict(extra="ignore")

    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1, max_length=6000)
    cta: str = Field(..., min_length=1, max_length=1000)
    reasoning: str = Field(..., min_length=1, max_length=2000)
    variation: EmailVariationLiteral


class EmailGenerateRequest(BaseModel):
    email_type: EmailTypeLiteral = "cold_email"
    tone: EmailToneLiteral = "professional"
    length: EmailLengthLiteral = "medium"
    cta_type: EmailCTALiteral = "book_meeting"
    contact_id: str | None = None
    force_refresh: bool = False


class EmailRegenerateRequest(BaseModel):
    force_refresh: bool = True


class EmailMeta(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_provider: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    generation_duration_ms: int | None = None
    research_input_hash: str | None = None


class EmailResponse(BaseModel):
    id: str
    workspace_id: str
    company_id: str
    research_id: str
    contact_id: str | None = None
    email_type: EmailTypeLiteral
    subject: str | None = None
    body: str | None = None
    cta: str | None = None
    cta_type: EmailCTALiteral
    tone: EmailToneLiteral
    length: EmailLengthLiteral
    variation: EmailVariationLiteral
    reasoning: str | None = None
    status: EmailStatusLiteral
    copy_count: int = 0
    regeneration_count: int = 0
    version: int = 1
    error_message: str | None = None
    meta: EmailMeta = Field(default_factory=EmailMeta)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    archived_at: datetime | None = None


class EmailListResponse(BaseModel):
    company_id: str
    status: Literal["none", "pending", "running", "completed", "failed"] = "none"
    cached: bool = False
    emails: list[EmailResponse] = Field(default_factory=list)
    error_message: str | None = None


# -- AI Sales Briefing contracts ---------------------------------------------

class BriefingSignalItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    evidence: str = Field(..., min_length=1, max_length=1000)
    strength: SignalStrength = "moderate"


class BriefingStakeholderItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(default=None, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    priority: PriorityLevel = "medium"
    rationale: str = Field(..., min_length=1, max_length=1000)


class BriefingContactPriorityItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    contact_or_persona: str = Field(..., min_length=1, max_length=255)
    priority: PriorityLevel = "medium"
    reason: str = Field(..., min_length=1, max_length=1000)


class BriefingEmailItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    subject: str = Field(..., min_length=1, max_length=500)
    variation: str = Field(..., min_length=1, max_length=5)
    summary: str = Field(..., min_length=1, max_length=1000)
    cta: str | None = Field(default=None, max_length=1000)


class BriefingOpportunityItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    rationale: str = Field(..., min_length=1, max_length=1000)
    priority: PriorityLevel = "medium"


class BriefingResponseItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    objection: str = Field(..., min_length=1, max_length=1000)
    response: str = Field(..., min_length=1, max_length=1000)


class BriefingRiskItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    severity: RiskSeverity = "medium"
    mitigation: str | None = Field(default=None, max_length=1000)


class BriefingPayload(BaseModel):
    """The complete structured briefing the model must return."""
    model_config = ConfigDict(extra="ignore")

    executive_summary: str = Field(..., min_length=1, max_length=4000)
    company_overview: str = Field(..., min_length=1, max_length=4000)
    current_buying_signals: list[BriefingSignalItem] = Field(default_factory=list, max_length=12)
    why_buy_now: list[str] = Field(default_factory=list, max_length=10)
    recent_company_changes: list[str] = Field(default_factory=list, max_length=10)
    existing_relationship_summary: str = Field(..., min_length=1, max_length=3000)
    crm_activity_summary: str = Field(..., min_length=1, max_length=3000)
    key_stakeholders: list[BriefingStakeholderItem] = Field(default_factory=list, max_length=12)
    recommended_contact_priority: list[BriefingContactPriorityItem] = Field(default_factory=list, max_length=12)
    existing_ai_research_summary: str = Field(..., min_length=1, max_length=4000)
    previous_generated_emails: list[BriefingEmailItem] = Field(default_factory=list, max_length=12)
    pain_points: list[PainPointItem] = Field(default_factory=list, max_length=12)
    business_opportunities: list[BriefingOpportunityItem] = Field(default_factory=list, max_length=12)
    suggested_value_proposition: str = Field(..., min_length=1, max_length=3000)
    competitive_landscape: str = Field(..., min_length=1, max_length=3000)
    discovery_questions: list[str] = Field(default_factory=list, max_length=12)
    technical_questions: list[str] = Field(default_factory=list, max_length=12)
    business_questions: list[str] = Field(default_factory=list, max_length=12)
    executive_questions: list[str] = Field(default_factory=list, max_length=12)
    possible_customer_objections: list[str] = Field(default_factory=list, max_length=12)
    suggested_responses: list[BriefingResponseItem] = Field(default_factory=list, max_length=12)
    recommended_meeting_agenda: list[str] = Field(default_factory=list, max_length=12)
    meeting_goals: list[str] = Field(default_factory=list, max_length=12)
    recommended_demo_focus: list[str] = Field(default_factory=list, max_length=12)
    recommended_pricing_strategy: str = Field(..., min_length=1, max_length=3000)
    recommended_follow_up_timeline: list[str] = Field(default_factory=list, max_length=12)
    next_best_action: str = Field(..., min_length=1, max_length=2000)
    risk_factors: list[BriefingRiskItem] = Field(default_factory=list, max_length=12)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_explanation: str = Field(..., min_length=1, max_length=3000)


class BriefingGenerateRequest(BaseModel):
    force_refresh: bool = False
    source_email_id: str | None = None


class BriefingRegenerateRequest(BaseModel):
    force_refresh: bool = True


class BriefingMeta(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_provider: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    generation_duration_ms: int | None = None
    input_hash: str | None = None


class BriefingResponse(BaseModel):
    id: str
    workspace_id: str
    company_id: str
    research_id: str
    source_email_id: str | None = None
    summary: str | None = None
    briefing_json: BriefingPayload | None = None
    confidence_score: float | None = None
    status: BriefingStatusLiteral
    cached: bool = False
    error_message: str | None = None
    meta: BriefingMeta = Field(default_factory=BriefingMeta)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    archived_at: datetime | None = None


class BriefingListResponse(BaseModel):
    company_id: str
    status: Literal["none", "pending", "running", "completed", "failed"] = "none"
    cached: bool = False
    briefings: list[BriefingResponse] = Field(default_factory=list)
    error_message: str | None = None


# -- AI Sales Coach contracts -------------------------------------------------

DealStageLiteral = Literal[
    "prospecting",
    "discovery",
    "qualification",
    "demo",
    "proposal",
    "negotiation",
    "closing",
    "expansion",
]

DealHealthLiteral = Literal["strong", "healthy", "at_risk", "blocked", "unknown"]
ObjectionSeverityLiteral = Literal["critical", "high", "medium", "low"]
InfluenceLiteral = Literal["decision_maker", "influencer", "champion", "blocker", "unknown"]


class SalesCoachEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore")

    buying_signals: list[str] = Field(default_factory=list, max_length=10)
    research_findings: list[str] = Field(default_factory=list, max_length=10)
    crm_information: list[str] = Field(default_factory=list, max_length=10)
    briefing_insights: list[str] = Field(default_factory=list, max_length=10)


class SalesCoachSignal(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    evidence: str = Field(..., min_length=1, max_length=1000)
    impact: str = Field(..., min_length=1, max_length=1000)
    strength: SignalStrength = "moderate"


class SalesCoachRisk(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    severity: RiskSeverity = "medium"
    mitigation: str | None = Field(default=None, max_length=1000)
    evidence: SalesCoachEvidence = Field(default_factory=SalesCoachEvidence)


class SalesCoachStakeholder(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(default=None, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    influence: InfluenceLiteral = "unknown"
    priority: PriorityLevel = "medium"
    likely_motivation: str = Field(..., min_length=1, max_length=1000)
    recommended_approach: str = Field(..., min_length=1, max_length=1000)


class SalesCoachObjection(BaseModel):
    model_config = ConfigDict(extra="ignore")

    objection: str = Field(..., min_length=1, max_length=1000)
    severity: ObjectionSeverityLiteral = "medium"
    customer_statement: str = Field(..., min_length=1, max_length=1000)
    why_customer_may_say_this: str = Field(..., min_length=1, max_length=1000)
    recommended_response: str = Field(..., min_length=1, max_length=1500)
    follow_up_question: str = Field(..., min_length=1, max_length=1000)
    goal_of_response: str = Field(..., min_length=1, max_length=1000)
    evidence: SalesCoachEvidence = Field(default_factory=SalesCoachEvidence)


class SalesCoachBattleCard(BaseModel):
    model_config = ConfigDict(extra="ignore")

    competitor_or_alternative: str = Field(..., min_length=1, max_length=255)
    likely_positioning: str = Field(..., min_length=1, max_length=1000)
    avenor_advantage: str = Field(..., min_length=1, max_length=1000)
    risk: str = Field(..., min_length=1, max_length=1000)
    recommended_talk_track: str = Field(..., min_length=1, max_length=1500)


class SalesCoachStageGuidance(BaseModel):
    model_config = ConfigDict(extra="ignore")

    stage: DealStageLiteral
    objective: str = Field(..., min_length=1, max_length=1000)
    coaching: str = Field(..., min_length=1, max_length=2000)
    questions: list[str] = Field(default_factory=list, max_length=8)


class SalesCoachActionItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: str = Field(..., min_length=1, max_length=500)
    rationale: str = Field(..., min_length=1, max_length=1000)
    priority: PriorityLevel = "medium"
    owner: str | None = Field(default=None, max_length=255)
    timeframe: str | None = Field(default=None, max_length=255)


class SalesCoachPayload(BaseModel):
    """The complete structured sales coaching object the model must return."""
    model_config = ConfigDict(extra="ignore")

    executive_coaching_summary: str = Field(..., min_length=1, max_length=4000)
    deal_health_assessment: DealHealthLiteral
    win_probability: float = Field(..., ge=0.0, le=1.0)
    win_probability_explanation: str = Field(..., min_length=1, max_length=3000)
    positive_buying_signals: list[SalesCoachSignal] = Field(default_factory=list, max_length=12)
    risk_factors: list[SalesCoachRisk] = Field(default_factory=list, max_length=12)
    deal_blockers: list[SalesCoachRisk] = Field(default_factory=list, max_length=12)
    decision_maker_analysis: str = Field(..., min_length=1, max_length=3000)
    stakeholder_influence_map: list[SalesCoachStakeholder] = Field(default_factory=list, max_length=12)
    likely_customer_objections: list[SalesCoachObjection] = Field(default_factory=list, max_length=12)
    competitive_battle_cards: list[SalesCoachBattleCard] = Field(default_factory=list, max_length=8)
    competitor_comparison: str = Field(..., min_length=1, max_length=3000)
    pricing_negotiation_strategy: str = Field(..., min_length=1, max_length=3000)
    discovery_coaching: SalesCoachStageGuidance
    demo_coaching: SalesCoachStageGuidance
    negotiation_coaching: SalesCoachStageGuidance
    closing_coaching: SalesCoachStageGuidance
    expansion_opportunity: str = Field(..., min_length=1, max_length=3000)
    recommended_next_best_action: str = Field(..., min_length=1, max_length=2000)
    immediate_action_plan: list[SalesCoachActionItem] = Field(default_factory=list, max_length=8)
    follow_up_strategy: list[SalesCoachActionItem] = Field(default_factory=list, max_length=8)
    long_term_action_plan: list[SalesCoachActionItem] = Field(default_factory=list, max_length=8)
    escalation_recommendation: str | None = Field(default=None, max_length=2000)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_explanation: str = Field(..., min_length=1, max_length=3000)
    explainability: SalesCoachEvidence = Field(default_factory=SalesCoachEvidence)


class SalesCoachGenerateRequest(BaseModel):
    force_refresh: bool = False
    deal_stage: DealStageLiteral | None = None
    briefing_id: str | None = None


class SalesCoachRegenerateRequest(BaseModel):
    force_refresh: bool = True


class SalesCoachMeta(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_provider: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    generation_duration_ms: int | None = None
    input_hash: str | None = None


class SalesCoachResponse(BaseModel):
    id: str
    workspace_id: str
    company_id: str
    research_id: str
    briefing_id: str | None = None
    summary: str | None = None
    coaching_json: SalesCoachPayload | None = None
    win_probability: float | None = None
    confidence_score: float | None = None
    status: SalesCoachingStatusLiteral
    cached: bool = False
    error_message: str | None = None
    meta: SalesCoachMeta = Field(default_factory=SalesCoachMeta)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    archived_at: datetime | None = None


class SalesCoachListResponse(BaseModel):
    company_id: str
    status: Literal["none", "pending", "running", "completed", "failed"] = "none"
    cached: bool = False
    coaching: list[SalesCoachResponse] = Field(default_factory=list)
    error_message: str | None = None
