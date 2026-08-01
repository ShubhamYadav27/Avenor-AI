from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class SignalType(str, Enum):
    ENGINEERING_HIRING = "engineering_hiring"
    EXECUTIVE_CHANGE = "executive_change"
    TECH_ADOPTION_CRM = "tech_adoption_crm"
    TECH_ADOPTION_AI = "tech_adoption_ai"
    BUYING_WINDOW = "buying_window"
    PIPELINE_GROWTH = "pipeline_growth"

class SignalBucket(str, Enum):
    """Categorical buckets to replace raw numbers for anonymization."""
    HIGH_GROWTH = "high_growth"
    STABLE = "stable"
    DECLINING = "declining"
    ACTIVE = "active"
    INACTIVE = "inactive"

@dataclass
class ConsentStatus:
    """Explicit opt-in/opt-out status for an organization."""
    organization_id: str
    is_opted_in: bool
    updated_at: datetime = field(default_factory=datetime.utcnow)
    audit_user_id: Optional[str] = None # Who granted/revoked consent

@dataclass
class AnonymousSignal:
    """A data point completely stripped of organizational identity."""
    id: str # UUID, not tied to Org
    anonymized_cohort_id: str # e.g. "cohort_saas_series_b", NOT "org_123"
    signal_type: SignalType
    bucketed_value: SignalBucket
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Pattern:
    """A mathematically discovered correlation between two signals."""
    id: str
    trigger_signal: SignalType
    trigger_value: SignalBucket
    outcome_signal: SignalType
    outcome_value: SignalBucket
    confidence_score: float # 0.0 to 1.0
    occurrence_count: int

@dataclass
class CollectiveInsight:
    """AI-generated strategic insight based on a discovered pattern."""
    id: str
    pattern_id: str
    message: str
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)
