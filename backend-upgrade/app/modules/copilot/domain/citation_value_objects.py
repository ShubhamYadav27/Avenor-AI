"""
Citation Value Objects (Phase 5.5.5)
Domain enums and value objects for Enterprise Citation & Grounding Engine.
Zero external framework dependencies.
"""
from enum import Enum


class EvidenceType(str, Enum):
    CRM = "crm"
    SIGNAL = "signal"
    MEMORY = "memory"
    COMPANY = "company"
    RESEARCH = "research"
    COACHING = "coaching"
    EMAIL = "email"
    FEED = "feed"
    KNOWLEDGE = "knowledge"


class EvidenceQuality(str, Enum):
    VERIFIED = "verified"           # CRM, direct API source (1.0 confidence)
    HIGH_CONFIDENCE = "high"       # Strong signal, corroborated fact (0.85-0.99)
    MEDIUM_CONFIDENCE = "medium"   # Inferred, uncorroborated (0.60-0.84)
    UNVERIFIED = "unverified"       # Weak signal (< 0.60)


class GroundingStatus(str, Enum):
    FULLY_GROUNDED = "fully_grounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    UNSUPPORTED_CLAIMS_DETECTED = "unsupported_claims_detected"
    HALLUCINATION_RISK = "hallucination_risk"
