"""
Citation Resolver (Phase 5.5.5)
Assigns deterministic citation IDs (cit-crm-*, cit-sig-*, cit-mem-*) and builds CitationRegistry.
"""
from typing import List

from app.modules.copilot.domain.citation_entities import CitationMarker, CitationRegistry, EvidenceItem


class CitationResolver:
    def resolve_citations(self, items: List[EvidenceItem]) -> CitationRegistry:
        registry = CitationRegistry()

        for item in items:
            if not item.citation_id:
                prefix = item.type.value[:3].lower()
                item.citation_id = f"cit-{prefix}-{item.id[:6]}"

            title = f"{item.type.value.upper()} Intelligence ({item.source_type})"
            marker = CitationMarker(
                citation_id=item.citation_id,
                title=title,
                category=item.type.value,
                confidence_score=item.confidence_score,
                verified=item.confidence_score >= 0.90,
                snippet=item.normalized_text[:120],
            )
            registry.add_citation(marker)

        return registry


citation_resolver = CitationResolver()
