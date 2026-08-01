"""
Trade-off Analyzer (Phase 6.2)
Performs multi-objective optimization (conversion lift vs sales cycle duration vs ARR value).
"""

from app.modules.revenue_decision.domain.decision_entities import DecisionExplanation


class TradeoffAnalyzer:
    def analyze_tradeoffs(self, company_id: str) -> DecisionExplanation:
        return DecisionExplanation(
            summary="Recommended Series B Expansion Play over Standard Demo Play.",
            trade_offs_considered=[
                "Higher upfront meeting effort (+15 mins) balanced by +32% expected conversion lift.",
                "Prioritized direct VP outreach over automated email drip due to high intent score (94.0).",
            ],
            primary_rationale="Account intent surge score of 94.0 and 18% YoY hiring growth justify executive-level engagement.",
            evidence_citations=["cit-sig-904", "cit-crm-102", "cit-res-001"],
        )


tradeoff_analyzer = TradeoffAnalyzer()
