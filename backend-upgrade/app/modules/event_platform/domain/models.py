from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class WebhookStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DELETED = "deleted"

class DeliveryStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD = "dead_letter"

@dataclass
class Event:
    """Canonical representation of a domain event."""
    id: str
    type: str # e.g., 'company.created'
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WebhookEndpoint:
    """A registered Webhook destination for a Workspace."""
    id: str
    workspace_id: str
    url: str
    subscribed_events: List[str] # e.g., ['company.*', 'opportunity.won']
    secret: str # Used for HMAC SHA-256 signing
    status: WebhookStatus = WebhookStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)

    def matches_event(self, event_type: str) -> bool:
        """Evaluates if this endpoint is subscribed to the event_type (supports wildcards)."""
        if self.status != WebhookStatus.ACTIVE:
            return False
            
        for sub in self.subscribed_events:
            if sub == "*": return True
            if sub.endswith(".*"):
                prefix = sub[:-2]
                if event_type.startswith(prefix):
                    return True
            if sub == event_type:
                return True
        return False

@dataclass
class DeliveryLog:
    """Tracks the lifecycle of an Event dispatched to a WebhookEndpoint."""
    id: str
    endpoint_id: str
    event_id: str
    status: DeliveryStatus
    attempts: int = 0
    max_attempts: int = 4
    next_retry_at: Optional[datetime] = None
    last_error_code: Optional[int] = None
    last_error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
