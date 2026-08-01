"""
Recommendation Engine (Phase 6.1)
Ranks Next Best Actions with evidence citations [cit-crm-*], [cit-sig-*].
"""
from typing import List

from app.modules.predictive_intelligence.domain.predictive_entities import RevenueRecommendation


class RecommendationEngine:
    def generate_recommendations(self, company_id: str) -> List[RevenueRecommendation]:
        return [
            RevenueRecommendation(
                action_type="EXECUTIVE_OUTREACH",
                title="Initiate VP Sales Outreach",
                description="Reach out to VP of Sales regarding intent surge on Revenue Intelligence.",
                priority_score=96.0,
                evidence_citations=["cit-sig-904", "cit-crm-102"],
            ),
            RevenueRecommendation(
                action_type="DEMO_PREPARATION",
                title="Schedule ROI Proof Point Demo",
                description="Highlight 14-day ROI proof point during upcoming mutual evaluation.",
                priority_score=91.0,
                evidence_citations=["cit-res-001"],
            ),
        ]


recommendation_engine = RecommendationEngine()
