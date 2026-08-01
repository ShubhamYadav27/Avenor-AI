from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid

class KeyStatus(str, Enum):
    ACTIVE = "Active"
    REVOKED = "Revoked"
    EXPIRED = "Expired"

class ApiVersion(str, Enum):
    V1 = "v1"

class RateLimitTier(str, Enum):
    FREE = "Free"
    PRO = "Pro"
    ENTERPRISE = "Enterprise"

@dataclass
class ApiQuota:
    tier: RateLimitTier
    requests_per_second: int
    requests_per_day: int

    @classmethod
    def default_for_tier(cls, tier: RateLimitTier) -> 'ApiQuota':
        if tier == RateLimitTier.FREE:
            return cls(tier, 5, 1000)
        elif tier == RateLimitTier.PRO:
            return cls(tier, 20, 50000)
        else:
            return cls(tier, 100, 1000000)

@dataclass
class ApiKey:
    id: str
    workspace_id: str
    name: str
    prefix: str  # e.g., 'av_live_xxxx'
    hashed_secret: str
    scopes: List[str]
    status: KeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    quota: ApiQuota

    def is_valid(self) -> bool:
        if self.status != KeyStatus.ACTIVE:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def has_scope(self, required_scope: str) -> bool:
        """Simple scope check (e.g. 'read:companies' in scopes)."""
        return required_scope in self.scopes

@dataclass
class ApiError:
    """Standardized API Error format similar to Stripe."""
    status: int
    code: str
    message: str
    request_id: str
    details: Optional[dict] = None
    doc_url: str = "https://docs.avenor.ai/errors"
