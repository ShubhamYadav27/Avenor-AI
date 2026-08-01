"""
Copilot Context Domain Models (Phase 5.5.2 Part 3 Architecture)
Defines UnifiedContext, ContextItem, ContextPriority, ContextCategory, and ContextIntent.
Zero framework or database coupling.
Includes Context Provenance, Citation IDs, Explainability, and Confidence Engine.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import enum
from typing import Any, Dict, List, Optional
import uuid


class ContextIntent(str, enum.Enum):
    COMPANY_DEEP_DIVE = "company_deep_dive"
    OUTREACH_STRATEGY = "outreach_strategy"
    OBJECTION_HANDLING = "objection_handling"
    BUYING_SIGNALS = "buying_signals"
    CRM_PIPELINE = "crm_pipeline"
    GENERAL_STRATEGY = "general_strategy"


class ContextPriority(int, enum.Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class ContextCategory(str, enum.Enum):
    WORKSPACE = "workspace"
    COMPANY = "company"
    SIGNAL = "signal"
    CRM = "crm"
    RESEARCH = "research"
    SALES_COACH = "sales_coach"
    EMAIL = "email"
    CONVERSATION = "conversation"


@dataclass
class ContextItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: ContextCategory = ContextCategory.WORKSPACE
    source_provider: str = "default"
    priority: ContextPriority = ContextPriority.MEDIUM
    content: str = ""
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Phase 5.5.2 Part 3 Enterprise Context Provenance & Quality Metadata
    provenance_id: str = field(default_factory=lambda: f"prov-{uuid.uuid4()}")
    citation_id: str = field(default_factory=lambda: f"cit-{uuid.uuid4()}")
    freshness_score: float = 1.0   # 0.0 (stale) to 1.0 (fresh)
    confidence_score: float = 0.9  # 0.0 (uncertain) to 1.0 (highly reliable)
    relevance_score: float = 0.8   # Computed by ranker
    final_score: float = 0.0       # Computed multi-factor score
    inclusion_reason: str = "Included based on intent resolution"
    exclusion_reason: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None

    # Future Phase Compatibility Identifiers (Phase 5.5.3+)
    memory_ref_id: Optional[str] = None
    tool_call_ref_id: Optional[str] = None

    def __post_init__(self):
        if not self.token_count and self.content:
            # Approximate token count (~4 chars per token)
            self.token_count = len(self.content) // 4 + 5


@dataclass
class UnifiedContext:
    workspace_id: uuid.UUID
    thread_id: Optional[uuid.UUID] = None
    intent: ContextIntent = ContextIntent.GENERAL_STRATEGY
    items: List[ContextItem] = field(default_factory=list)
    workspace_info: Dict[str, Any] = field(default_factory=dict)
    company_summary: Optional[Dict[str, Any]] = None
    signal_summary: List[Dict[str, Any]] = field(default_factory=list)
    crm_summary: Dict[str, Any] = field(default_factory=dict)
    research_summary: Optional[Dict[str, Any]] = None
    coaching_summary: List[Dict[str, Any]] = field(default_factory=list)
    email_summary: List[Dict[str, Any]] = field(default_factory=list)
    total_tokens: int = 0

    # Phase 5.5.2 Part 3 Enterprise Intelligence Pipeline Metadata
    overall_confidence_score: float = 0.95
    provider_health: Dict[str, str] = field(default_factory=dict)  # e.g., {"crm_provider": "healthy"}
    ranking_metadata: Dict[str, Any] = field(default_factory=dict)
    prompt_version: str = "v1"
    assembled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_items_by_category(self, category: ContextCategory) -> List[ContextItem]:
        return [item for item in self.items if item.category == category]
