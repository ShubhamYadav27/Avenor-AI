"""
Citation Entities (Phase 5.5.5)
Pure domain entities representing evidence items, citation markers, registries, and citation packages.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.citation_value_objects import EvidenceQuality, EvidenceType, GroundingStatus


@dataclass
class EvidenceItem:
    id: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")
    workspace_id: Optional[uuid.UUID] = None
    type: EvidenceType = EvidenceType.COMPANY
    source_type: str = "platform_api"
    source_id: Optional[str] = None
    raw_content: str = ""
    normalized_text: str = ""
    confidence_score: float = 1.0
    freshness_score: float = 1.0
    quality: EvidenceQuality = EvidenceQuality.VERIFIED
    provenance_id: str = field(default_factory=lambda: f"prov-ev-{uuid.uuid4().hex[:8]}")
    citation_id: str = ""
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    corroborating_sources: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    score: float = 0.0

    def __post_init__(self):
        if not self.normalized_text and self.raw_content:
            self.normalized_text = self.raw_content.strip()
        if not self.citation_id:
            prefix = self.type.value[:3].lower()
            self.citation_id = f"cit-{prefix}-{uuid.uuid4().hex[:6]}"


@dataclass
class CitationMarker:
    citation_id: str
    title: str
    category: str
    source_url: Optional[str] = None
    confidence_score: float = 1.0
    verified: bool = True
    snippet: str = ""


@dataclass
class CitationRegistry:
    citations_map: Dict[str, CitationMarker] = field(default_factory=dict)
    total_citations: int = 0
    overall_grounding_score: float = 1.0

    def add_citation(self, citation: CitationMarker) -> None:
        self.citations_map[citation.citation_id] = citation
        self.total_citations = len(self.citations_map)
        if self.citations_map:
            avg_score = sum(c.confidence_score for c in self.citations_map.values()) / len(self.citations_map)
            self.overall_grounding_score = round(avg_score, 4)


@dataclass
class GroundingValidationResult:
    is_grounded: bool = True
    grounding_score: float = 1.0
    verified_claims_count: int = 0
    ungrounded_claims: List[str] = field(default_factory=list)
    unsupported_warnings: List[str] = field(default_factory=list)
    status: GroundingStatus = GroundingStatus.FULLY_GROUNDED


@dataclass
class CitationMetrics:
    total_evidence_items: int = 0
    corroborated_items_count: int = 0
    resolution_latency_ms: float = 0.0
    ranking_latency_ms: float = 0.0
    validation_latency_ms: float = 0.0


@dataclass
class CitationPackage:
    workspace_id: uuid.UUID
    thread_id: Optional[uuid.UUID] = None
    intent: ContextIntent = ContextIntent.GENERAL_STRATEGY

    evidence_items: List[EvidenceItem] = field(default_factory=list)
    registry: CitationRegistry = field(default_factory=CitationRegistry)
    formatted_footnotes: str = ""
    grounding_status: GroundingStatus = GroundingStatus.FULLY_GROUNDED
    unsupported_claims: List[str] = field(default_factory=list)
    metrics: CitationMetrics = field(default_factory=CitationMetrics)
    overall_confidence_score: float = 1.0
