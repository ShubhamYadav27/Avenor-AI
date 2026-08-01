"""
Enterprise Citation Engine (Phase 5.5.5)
Coordinates Collector -> Normalizer -> Resolver -> Ranker -> Validator -> PackageBuilder.
Zero DB ORM coupling.
"""
import time
from typing import Optional
import uuid

from app.modules.copilot.citation_engine.application.builders.package_builder import citation_package_builder
from app.modules.copilot.citation_engine.application.collectors.evidence_collector import evidence_collector
from app.modules.copilot.citation_engine.application.normalizers.evidence_normalizer import evidence_normalizer
from app.modules.copilot.citation_engine.application.rankers.evidence_ranker import evidence_ranker
from app.modules.copilot.citation_engine.application.resolvers.citation_resolver import citation_resolver
from app.modules.copilot.citation_engine.application.validation.citation_validator import citation_validator
from app.modules.copilot.domain.citation_entities import CitationMetrics, CitationPackage, GroundingValidationResult
from app.modules.copilot.domain.context import ContextIntent, UnifiedContext
from app.modules.copilot.domain.interfaces import ICitationEngine
from app.modules.copilot.domain.memory_entities import MemoryPackage
from app.modules.copilot.domain.tools import UnifiedIntelligencePackage


class CitationEngine(ICitationEngine):
    async def generate_citation_package(
        self,
        workspace_id: uuid.UUID,
        query: str,
        intent: ContextIntent,
        context: Optional[UnifiedContext] = None,
        intelligence_pkg: Optional[UnifiedIntelligencePackage] = None,
        memory_pkg: Optional[MemoryPackage] = None,
        thread_id: Optional[uuid.UUID] = None,
    ) -> CitationPackage:
        metrics = CitationMetrics()

        # 1. Collect Evidence
        raw_items = evidence_collector.collect_evidence(context, intelligence_pkg, memory_pkg)

        # 2. Normalize Evidence
        normalized_items = evidence_normalizer.normalize_items(raw_items)

        # 3. Resolve Citations & Build Registry
        t0 = time.perf_counter()
        registry = citation_resolver.resolve_citations(normalized_items)
        metrics.resolution_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        # 4. Multi-Source Corroboration Ranking
        t1 = time.perf_counter()
        ranked_items = evidence_ranker.rank_evidence(normalized_items)
        metrics.ranking_latency_ms = round((time.perf_counter() - t1) * 1000.0, 2)

        # 5. Validate Grounding & Unsupported Claims
        t2 = time.perf_counter()
        validation_res = citation_validator.validate_grounding(query, ranked_items)
        metrics.validation_latency_ms = round((time.perf_counter() - t2) * 1000.0, 2)

        # 6. Build Citation Package
        metrics.total_evidence_items = len(ranked_items)
        pkg = citation_package_builder.build_package(
            workspace_id=workspace_id,
            intent=intent,
            evidence_items=ranked_items,
            registry=registry,
            thread_id=thread_id,
            metrics=metrics,
        )
        pkg.grounding_status = validation_res.status
        pkg.unsupported_claims = validation_res.ungrounded_claims

        return pkg

    def validate_claim(self, query: str) -> GroundingValidationResult:
        return citation_validator.validate_grounding(query, [])


citation_engine = CitationEngine()
