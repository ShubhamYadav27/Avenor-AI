"""
Decision Entities (Phase 6.2)
Pure domain entities representing policies, constraints, explanations, decisions, action plans, and packages.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

from app.modules.revenue_decision.domain.decision_value_objects import ActionUrgency, ConstraintType, DecisionType, OutreachChannel, PolicyMode


@dataclass
class BusinessConstraint:
    constraint_id: str
    constraint_type: ConstraintType
    description: str
    is_satisfied: bool = True


@dataclass
class DecisionPolicy:
    policy_id: str
    policy_name: str
    mode: PolicyMode = PolicyMode.STRICT_ENFORCE
    rule_expression: str = ""
    is_active: bool = True


@dataclass
class DecisionExplanation:
    summary: str
    trade_offs_considered: List[str] = field(default_factory=list)
    primary_rationale: str = ""
    evidence_citations: List[str] = field(default_factory=list)


@dataclass
class ContactSelection:
    contact_id: str
    name: str
    title: str
    persona_match_score: float = 0.95
    decision_reason: str = "Decision-maker with authority over Revenue Operations budget."


@dataclass
class PlayRecommendation:
    play_id: str
    play_name: str
    description: str
    recommended_collateral: List[str] = field(default_factory=list)
    expected_conversion_lift: float = 0.32


@dataclass
class ActionPlan:
    plan_id: str = field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:8]}")
    company_id: str = ""
    target_contact: Optional[ContactSelection] = None
    play: Optional[PlayRecommendation] = None
    recommended_channel: OutreachChannel = OutreachChannel.EMAIL
    optimal_timing: str = "Tuesday at 10:00 AM EST"
    urgency: ActionUrgency = ActionUrgency.HIGH
    explanation: Optional[DecisionExplanation] = None


@dataclass
class RevenueDecision:
    decision_id: str = field(default_factory=lambda: f"dec-{uuid.uuid4().hex[:8]}")
    decision_type: DecisionType = DecisionType.NEXT_BEST_SALES_ACTION
    recommended_action: Optional[ActionPlan] = None
    alternative_actions: List[ActionPlan] = field(default_factory=list)
    confidence_score: float = 0.94
    satisfied_constraints: List[BusinessConstraint] = field(default_factory=list)


@dataclass
class DecisionPackage:
    session_id: str = field(default_factory=lambda: f"dec-sess-{uuid.uuid4().hex[:8]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    company_id: str = ""
    decisions: List[RevenueDecision] = field(default_factory=list)
    action_plan: Optional[ActionPlan] = None
    execution_time_ms: float = 0.0
