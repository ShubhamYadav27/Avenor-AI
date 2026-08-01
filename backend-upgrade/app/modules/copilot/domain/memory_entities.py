"""
Enterprise Memory Domain Entities (Phase 5.5.4 Architecture)
Defines MemoryItem, MemoryRetrievalPlan, MemoryPackage, MemoryConsolidationResult, and MemoryMetrics.
Zero framework or database coupling.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.memory_value_objects import (
    MemoryCategory,
    MemoryImportance,
    MemoryStatus,
    MemoryTier,
    RetrievalStrategy,
)


@dataclass
class MemoryItem:
    id: str = field(default_factory=lambda: f"mem-{uuid.uuid4()}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    category: MemoryCategory = MemoryCategory.WORKSPACE
    tier: MemoryTier = MemoryTier.LONG_TERM
    content: str = ""
    summary: str = ""
    
    # 1. Confidence & Importance
    confidence_score: float = 0.90   # 0.0 (uncertain inference) to 1.0 (verified CRM fact)
    importance: MemoryImportance = MemoryImportance.NORMAL
    status: MemoryStatus = MemoryStatus.ACTIVE
    
    # 2. Freshness & Lifecycle
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    stale_after: Optional[datetime] = None

    # 3. Provenance & Versioning
    provenance_id: str = field(default_factory=lambda: f"prov-mem-{uuid.uuid4()}")
    source_type: str = "user_conversation"  # crm, research, signal, user_chat
    source_id: Optional[str] = None
    version: int = 1
    previous_version_id: Optional[str] = None

    # 4. Entity Relationships (Company -> Opportunity -> Contact -> Conversation)
    parent_memory_id: Optional[str] = None
    entity_type: Optional[str] = None   # company, contact, deal, thread
    entity_id: Optional[str] = None

    # 5. Explainability & Feedback Loops
    inclusion_reason: str = "Relevant to user query intent"
    explanation: str = ""
    reinforcement_score: float = 1.0    # Boosted on user confirmation
    feedback_count: int = 0

    # 6. Scoring & Vector Search Readiness
    relevance_score: float = 0.80
    final_score: float = 0.0
    citation_id: str = field(default_factory=lambda: f"cit-mem-{uuid.uuid4()}")
    embedding_vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryRetrievalPlan:
    plan_id: uuid.UUID = field(default_factory=uuid.uuid4)
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    intent: ContextIntent = ContextIntent.GENERAL_STRATEGY
    target_categories: List[MemoryCategory] = field(default_factory=list)
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    max_items: int = 10
    min_confidence: float = 0.50
    freshness_required: bool = True
    token_budget: int = 2000


@dataclass
class MemoryMetrics:
    retrieval_latency_ms: float = 0.0
    extraction_latency_ms: float = 0.0
    consolidation_latency_ms: float = 0.0
    ranking_latency_ms: float = 0.0
    memories_queried_count: int = 0
    memories_retrieved_count: int = 0
    memories_consolidated_count: int = 0
    duplicate_count: int = 0
    conflict_count: int = 0


@dataclass
class MemoryPackage:
    workspace_id: uuid.UUID
    thread_id: Optional[uuid.UUID] = None
    intent: ContextIntent = ContextIntent.GENERAL_STRATEGY
    memories: List[MemoryItem] = field(default_factory=list)
    summary_text: str = ""
    overall_confidence_score: float = 0.95
    provenance_chain: List[str] = field(default_factory=list)
    citation_registry: Dict[str, str] = field(default_factory=dict)
    metrics: MemoryMetrics = field(default_factory=MemoryMetrics)
    assembled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MemoryConsolidationResult:
    consolidated_count: int = 0
    superseded_count: int = 0
    new_memories_created: int = 0
    duration_ms: float = 0.0


@dataclass
class MemoryGovernancePolicy:
    workspace_id: uuid.UUID
    scrub_pii: bool = True
    max_retention_days: int = 365
    allow_ai_inference_storage: bool = True
    min_confidence_to_persist: float = 0.60
