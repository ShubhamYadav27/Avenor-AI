"""
Revenue OS Value Objects (Phase 6.6)
Domain enums and value objects for Avenor Revenue Operating System (Revenue OS).
Zero external framework dependencies.
"""
from enum import Enum


class OperatingMode(str, Enum):
    FULLY_AUTONOMOUS = "fully_autonomous"
    HYBRID_GOVERNED = "hybrid_governed"
    MANUAL_OVERRIDE = "manual_override"


class HealthTier(str, Enum):
    EXCELLENT = "excellent"
    HEALTHY = "healthy"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"


class CapabilityStatus(str, Enum):
    OPTIMAL = "optimal"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    BOTTLENECKED = "bottlenecked"


class ProgramStatus(str, Enum):
    ACTIVE = "active"
    PLANNED = "planned"
    COMPLETED = "completed"
    PAUSED = "paused"


class PolicyLevel(str, Enum):
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"
