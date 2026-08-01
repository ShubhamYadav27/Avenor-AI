"""
Learning Entities (Phase 5.5.6)
Pure domain entities representing feedback events, CRM outcomes, reward signals, and learning packages.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.learning_value_objects import DriftStatus, FeedbackType, OptimizationTarget, RewardType


@dataclass
class FeedbackEvent:
    id: str = field(default_factory=lambda: f"fb-{uuid.uuid4().hex[:12]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    thread_id: Optional[uuid.UUID] = None
    message_id: Optional[uuid.UUID] = None
    feedback_type: FeedbackType = FeedbackType.THUMBS_UP
    rating: float = 1.0  # 0.0 to 1.0 or -1.0 to 1.0
    correction_text: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OutcomeEvent:
    id: str = field(default_factory=lambda: f"out-{uuid.uuid4().hex[:12]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    deal_id: Optional[str] = None
    company_id: Optional[str] = None
    outcome_type: FeedbackType = FeedbackType.DEAL_WON
    amount_usd: float = 0.0
    signal_ids_attributed: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RewardSignal:
    reward_id: str = field(default_factory=lambda: f"rw-{uuid.uuid4().hex[:12]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    reward_type: RewardType = RewardType.EXPLICIT_USER
    reward_score: float = 1.0  # -1.0 to 1.0
    target: OptimizationTarget = OptimizationTarget.SIGNAL_WEIGHT
    weight_delta: float = 0.05
    reasoning: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class LearningMetrics:
    total_feedback_count: int = 0
    positive_rate: float = 1.0
    reward_average: float = 0.85
    weight_updates_count: int = 0
    drift_status: DriftStatus = DriftStatus.STABLE


@dataclass
class LearningPackage:
    workspace_id: uuid.UUID
    recent_rewards: List[RewardSignal] = field(default_factory=list)
    active_weights_override: Dict[str, float] = field(default_factory=dict)
    optimization_summary: str = ""
    metrics: LearningMetrics = field(default_factory=LearningMetrics)
