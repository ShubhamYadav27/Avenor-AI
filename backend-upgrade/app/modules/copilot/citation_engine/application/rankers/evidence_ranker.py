"""
Evidence Ranker (Phase 5.5.5)
Multi-source corroboration ranking: Relevance 0.35 + Confidence 0.25 + Freshness 0.20 + Corroboration 0.20.
"""
from typing import List

from app.modules.copilot.domain.citation_entities import EvidenceItem


class EvidenceRanker:
    def compute_evidence_score(self, item: EvidenceItem) -> float:
        corroboration_bonus = min(1.0, len(item.corroborating_sources) * 0.33)
        relevance = 0.85

        score = (
            (relevance * 0.35)
            + (item.confidence_score * 0.25)
            + (item.freshness_score * 0.20)
            + (corroboration_bonus * 0.20)
        )
        item.score = round(score, 4)
        return item.score

    def rank_evidence(self, items: List[EvidenceItem]) -> List[EvidenceItem]:
        for item in items:
            self.compute_evidence_score(item)
        return sorted(items, key=lambda x: x.score, reverse=True)


evidence_ranker = EvidenceRanker()
