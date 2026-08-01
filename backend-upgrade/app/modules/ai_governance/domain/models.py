from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class HallucinationScore:
    """Evaluation of an AI's grounding against factual evidence."""
    score: float # 0.0 (grounded) to 1.0 (hallucinated)
    is_hallucinated: bool
    flagged_segments: List[str]

@dataclass
class AIAuditTrace:
    """Immutable log of how a decision was made."""
    model_version: str
    prompt_version: str
    feature_vector_ids: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AIDecision:
    """An immutable record of an AI prediction requiring governance."""
    id: str
    input_context: Dict[str, Any]
    output_prediction: Dict[str, Any]
    reasoning_summary: str
    confidence: float
    risk_level: RiskLevel
    hallucination_evaluation: HallucinationScore
    approval_status: ApprovalStatus
    audit_trace: AIAuditTrace
    
    # Human-In-The-Loop tracking
    required_approver_role: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
