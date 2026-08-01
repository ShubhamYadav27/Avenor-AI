"""
Citation Package Builder (Phase 5.5.5)
Assembles CitationPackage with formatted markdown footnotes and provenance chain.
"""
from typing import List, Optional
import uuid

from app.modules.copilot.domain.citation_entities import CitationMetrics, CitationPackage, CitationRegistry, EvidenceItem
from app.modules.copilot.domain.context import ContextIntent


class CitationPackageBuilder:
    def build_package(
        self,
        workspace_id: uuid.UUID,
        intent: ContextIntent,
        evidence_items: List[EvidenceItem],
        registry: CitationRegistry,
        thread_id: Optional[uuid.UUID] = None,
        metrics: Optional[CitationMetrics] = None,
    ) -> CitationPackage:
        footnotes: List[str] = []

        for citation_id, marker in registry.citations_map.items():
            footnotes.append(
                f"- [{citation_id}] {marker.title} (Confidence: {marker.confidence_score * 100:.0f}%, Verified: {marker.verified})\n  Snippet: \"{marker.snippet}\""
            )

        formatted_footnotes = "\n".join(footnotes) if footnotes else "No citations registered."

        return CitationPackage(
            workspace_id=workspace_id,
            thread_id=thread_id,
            intent=intent,
            evidence_items=evidence_items,
            registry=registry,
            formatted_footnotes=formatted_footnotes,
            metrics=metrics or CitationMetrics(total_evidence_items=len(evidence_items)),
            overall_confidence_score=registry.overall_grounding_score,
        )


citation_package_builder = CitationPackageBuilder()
