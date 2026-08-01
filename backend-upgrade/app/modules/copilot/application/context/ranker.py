"""
Multi-Factor Context Ranking Engine (Phase 5.5.2 Part 3)
Multi-factor scoring: Relevance, Freshness, Confidence, and Provider Weight.
"""
from typing import Dict, List
from app.modules.copilot.domain.context import ContextCategory, ContextItem

PROVIDER_WEIGHTS: Dict[ContextCategory, float] = {
    ContextCategory.WORKSPACE: 1.0,
    ContextCategory.COMPANY: 0.90,
    ContextCategory.SIGNAL: 0.85,
    ContextCategory.CRM: 0.80,
    ContextCategory.RESEARCH: 0.75,
    ContextCategory.SALES_COACH: 0.70,
    ContextCategory.EMAIL: 0.65,
    ContextCategory.CONVERSATION: 0.60,
}


class ContextRanker:
    def compute_multi_factor_score(self, item: ContextItem) -> float:
        """
        Calculates multi-factor score:
        Final = (Relevance * 0.35) + (Freshness * 0.25) + (Confidence * 0.25) + (ProviderWeight * 0.15)
        """
        provider_weight = PROVIDER_WEIGHTS.get(item.category, 0.70)
        score = (
            (item.relevance_score * 0.35)
            + (item.freshness_score * 0.25)
            + (item.confidence_score * 0.25)
            + (provider_weight * 0.15)
        )
        item.final_score = round(score, 4)
        return item.final_score

    def rank_and_deduplicate(self, items: List[ContextItem]) -> List[ContextItem]:
        seen_contents = set()
        unique_items: List[ContextItem] = []

        for item in items:
            normalized = item.content.strip().lower()
            if normalized not in seen_contents:
                seen_contents.add(normalized)
                # Calculate multi-factor score
                self.compute_multi_factor_score(item)
                unique_items.append(item)
            else:
                item.exclusion_reason = "Duplicate content detected during quality pipeline"

        # Sort descending by multi-factor final_score
        return sorted(unique_items, key=lambda x: x.final_score, reverse=True)


context_ranker = ContextRanker()
