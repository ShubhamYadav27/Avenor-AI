"""
Memory Engine Value Objects (Phase 5.5.4)
Immutable value objects for Enterprise Memory Engine.
Zero framework or database coupling.
"""
from dataclasses import dataclass
import enum
import uuid


class MemoryCategory(str, enum.Enum):
    CONVERSATION = "conversation"
    WORKSPACE = "workspace"
    COMPANY = "company"
    CONTACT = "contact"
    OPPORTUNITY = "opportunity"
    USER = "user"
    KNOWLEDGE = "knowledge"


class MemoryTier(str, enum.Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryImportance(int, enum.Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    EPHEMERAL = 5


class MemoryStatus(str, enum.Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    ARCHIVED = "archived"
    DELETED = "deleted"


class RetrievalStrategy(str, enum.Enum):
    EXACT = "exact"
    METADATA = "metadata"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    RECENCY_FIRST = "recency_first"
    IMPORTANCE_FIRST = "importance_first"
    CONFIDENCE_FIRST = "confidence_first"


@dataclass(frozen=True)
class MemoryId:
    value: str

    @classmethod
    def generate(cls) -> "MemoryId":
        return cls(value=f"mem-{uuid.uuid4()}")
