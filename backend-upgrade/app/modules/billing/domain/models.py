from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class SubscriptionTier(str, Enum):
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"

@dataclass
class Subscription:
    """Represents an active billing plan for an Organization."""
    id: str
    org_id: str
    tier: SubscriptionTier
    current_period_start: datetime
    current_period_end: datetime
    is_active: bool = True

@dataclass
class Entitlement:
    """A feature lock or numeric limit assigned to a SubscriptionTier."""
    feature_name: str # e.g., 'max_agents', 'api_access'
    max_limit: Optional[int] = None # None means unlimited if allowed, or boolean flag
    has_access: bool = True

@dataclass
class UsageRecord:
    """Metered consumption telemetry."""
    id: str
    org_id: str
    metric_name: str # e.g., 'llm_tokens', 'api_calls'
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class InvoiceLineItem:
    description: str
    quantity: float
    unit_amount: float
    total: float

@dataclass
class Invoice:
    id: str
    org_id: str
    status: InvoiceStatus
    line_items: List[InvoiceLineItem] = field(default_factory=list)
    amount_due: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
