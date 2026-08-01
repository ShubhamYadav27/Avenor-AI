"""
Memory Ranking Engine (Phase 5.5.4)
Multi-factor scoring: Relevance, Freshness, Importance, and Feedback Loops.
"""
from datetime import datetime, timezone
from typing import List

from app.modules.copilot.domain.memory_entities import MemoryItem

IMPORTANCE_WEIGHTS = {
    1: 1.0,   # CRITICAL
    2: 0.85,  # HIGH
    3: 0.70,  # NORMAL
    4: 0.50,  # LOW
    5: 0.30,  # EPHEMERAL
}


class MemoryRankingEngine:
    def compute_multi_factor_score(self, item: MemoryItem) -> float:
        """
        Calculates multi-factor score:
        Final = (Relevance * 0.35) + (Freshness * 0.25) + (Importance * 0.20) + (Feedback * 0.20)
        """
        # Freshness decay calculation
        now = datetime.now(timezone.utc)
        age_days = (now - item.last_used_at).total_seconds() / 86400.0
        freshness = max(0.1, 1.0 - (age_days / 365.0))

        importance_weight = IMPORTANCE_WEIGHTS.get(item.importance.value, 0.70)
        feedback_weight = min(1.0, max(0.1, item.reinforcement_score))

        score = (
            (item.relevance_score * 0.35)
            + (freshness * 0.25)
            + (importance_weight * 0.20)
            + (feedback_weight * 0.20)
        )
        item.final_score = round(score, 4)
        return item.final_score

    def rank_memories(self, items: List[MemoryItem]) -> List[MemoryItem]:
        for item in items:
            self.compute_multi_factor_score(item)
        return sorted(items, key=lambda x: x.final_score, reverse=True)


memory_ranking_engine = MemoryRankingEngine()
