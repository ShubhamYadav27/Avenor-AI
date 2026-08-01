from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class ComplianceFramework(str, Enum):
    SOC2 = "soc2"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"

class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted" # PII / PCI Data

class PrivacyRequestType(str, Enum):
    ERASURE = "erasure" # Right to be Forgotten
    EXPORT = "export"
    RECTIFICATION = "rectification"

class PrivacyRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"

@dataclass
class PrivacyRequest:
    """A Data Subject Access Request (DSAR) strictly enforcing GDPR/CCPA."""
    id: str
    user_id: str
    request_type: PrivacyRequestType
    status: PrivacyRequestStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

@dataclass
class RetentionPolicy:
    """Enforces Time-to-Live on data to comply with regulations."""
    id: str
    classification: DataClassification
    ttl_days: Optional[int] # None means indefinite
    is_legal_hold: bool # If True, bypasses ttl_days (immutability)

@dataclass
class ComplianceControl:
    """An auditable security rule mapped to a specific framework."""
    id: str
    framework: ComplianceFramework
    name: str # e.g. "CC-1: MFA Enforced for Admins"
    description: str
    is_passing: bool
    evidence_reference: Optional[str] = None
    last_validated_at: datetime = field(default_factory=datetime.utcnow)
