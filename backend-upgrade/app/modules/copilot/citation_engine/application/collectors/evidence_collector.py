"""
Evidence Collector (Phase 5.5.5)
Collects raw evidence items from UnifiedContext, UnifiedIntelligencePackage, and MemoryPackage.
"""
from typing import List, Optional

from app.modules.copilot.domain.citation_entities import EvidenceItem
from app.modules.copilot.domain.citation_value_objects import EvidenceQuality, EvidenceType
from app.modules.copilot.domain.context import UnifiedContext
from app.modules.copilot.domain.memory_entities import MemoryPackage
from app.modules.copilot.domain.tools import UnifiedIntelligencePackage


class EvidenceCollector:
    def collect_evidence(
        self,
        context: Optional[UnifiedContext] = None,
        intelligence_pkg: Optional[UnifiedIntelligencePackage] = None,
        memory_pkg: Optional[MemoryPackage] = None,
    ) -> List[EvidenceItem]:
        evidence_items: List[EvidenceItem] = []

        # 1. Collect from UnifiedContext
        if context and context.items:
            for item in context.items:
                evidence_items.append(
                    EvidenceItem(
                        workspace_id=context.workspace_id,
                        type=EvidenceType.COMPANY,
                        source_type="context_engine",

                        source_id=item.source_provider,
                        raw_content=item.content,
                        normalized_text=item.content.strip(),
                        confidence_score=item.confidence_score,
                        freshness_score=item.freshness_score,
                        quality=EvidenceQuality.VERIFIED if item.confidence_score >= 0.90 else EvidenceQuality.HIGH_CONFIDENCE,
                        citation_id=item.citation_id,
                    )
                )

        # 2. Collect from UnifiedIntelligencePackage (Tool Outputs)
        if intelligence_pkg and intelligence_pkg.tool_results:
            for res in intelligence_pkg.tool_results:
                if not res.success or not res.data:
                    continue
                ev_type = EvidenceType.SIGNAL if "Signal" in res.tool_name else EvidenceType.RESEARCH
                evidence_items.append(
                    EvidenceItem(
                        type=ev_type,
                        source_type="tool_execution",
                        source_id=res.tool_name,
                        raw_content=str(res.data),
                        normalized_text=f"Tool Output ({res.tool_name}): {str(res.data)}",
                        confidence_score=0.95,
                        freshness_score=1.0,
                        quality=EvidenceQuality.VERIFIED,
                        citation_id=res.citation_id,
                    )
                )

        # 3. Collect from MemoryPackage
        if memory_pkg and memory_pkg.memories:
            for mem in memory_pkg.memories:
                evidence_items.append(
                    EvidenceItem(
                        workspace_id=mem.workspace_id,
                        type=EvidenceType.MEMORY,
                        source_type="memory_engine",
                        source_id=mem.id,
                        raw_content=mem.content,
                        normalized_text=f"Historical Memory ({mem.category.value.upper()}): {mem.content}",
                        confidence_score=mem.confidence_score,
                        freshness_score=0.85,
                        quality=EvidenceQuality.HIGH_CONFIDENCE,
                        citation_id=mem.citation_id,
                        provenance_id=mem.provenance_id,
                    )
                )

        return evidence_items


evidence_collector = EvidenceCollector()
