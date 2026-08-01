"""
Tool Orchestration Value Objects (Phase 5.5.3)
Immutable value objects for Tool Orchestration Engine.
Zero framework or database coupling.
"""
from dataclasses import dataclass
import enum
import uuid


class ExecutionPriority(int, enum.Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    RETRYING = "retrying"
    PARTIAL_SUCCESS = "partial_success"


class ExecutionCost(int, enum.Enum):
    FREE = 0          # In-memory context
    VERY_LOW = 10     # Local DB lookup
    LOW = 25          # Cached API lookup
    MEDIUM = 50       # External API call
    HIGH = 100        # AI Research generation
    VERY_HIGH = 200   # Multi-step generation


class FailureReason(str, enum.Enum):
    TIMEOUT = "timeout"
    PERMISSION_DENIED = "permission_denied"
    INVALID_REQUEST = "invalid_request"
    DEPENDENCY_FAILURE = "dependency_failure"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMITED = "rate_limited"
    CIRCUIT_OPEN = "circuit_open"
    INTERNAL_ERROR = "internal_error"


@dataclass(frozen=True)
class ToolId:
    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("ToolId must be a non-empty string")


@dataclass(frozen=True)
class ExecutionId:
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "ExecutionId":
        return cls(value=uuid.uuid4())


@dataclass(frozen=True)
class ConfidenceScore:
    value: float  # 0.0 to 1.0

    def __post_init__(self):
        if not (0.0 <= self.value <= 1.0):
            object.__setattr__(self, 'value', max(0.0, min(1.0, self.value)))
