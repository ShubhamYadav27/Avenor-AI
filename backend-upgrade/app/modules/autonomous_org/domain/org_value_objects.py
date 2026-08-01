"""
Autonomous Org Value Objects (Phase 6.6)
Domain enums and value objects for Autonomous Revenue Organization Platform.
Zero external framework dependencies.
"""
from enum import Enum


class OrgOperatingMode(str, Enum):
    FULLY_AUTONOMOUS = "fully_autonomous"
    HYBRID_GOVERNED = "hybrid_governed"
    MANUAL_OVERRIDE = "manual_override"


class OrgHealthTier(str, Enum):
    EXCELLENT = "excellent"
    HEALTHY = "healthy"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"
