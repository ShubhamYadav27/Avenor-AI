"""
Predictive Revenue Engine (Phase 6.1)
Coordinates Feature Extraction -> Buying Window Detection -> Opportunity Scoring -> ICP Similarity -> Recommendation Ranking.
Zero DB ORM coupling.
"""
import time
from typing import List
import uuid

from app.modules.copilot.domain.interfaces import IPredictiveEngine
from app.modules.predictive_intelligence.application.engines.buying_window_engine import buying_window_engine
from app.modules.predictive_intelligence.application.engines.opportunity_scoring_engine import opportunity_scoring_engine
from app.modules.predictive_intelligence.application.engines.recommendation_engine import recommendation_engine
from app.modules.predictive_intelligence.application.engines.similarity_engine import similarity_engine
from app.modules.predictive_intelligence.application.features.feature_builder import feature_builder
from app.modules.predictive_intelligence.domain.predictive_entities import AccountIntelligence, PredictionPackage


class PredictiveRevenueEngine(IPredictiveEngine):
    async def predict_account_intelligence(
        self,
        workspace_id: uuid.UUID,
        company_id: str,
    ) -> AccountIntelligence:
        # 1. Feature Extraction
        features = feature_builder.extract_features(workspace_id, company_id)

        # 2. Buying Window Detection
        bw = buying_window_engine.detect_buying_window(company_id, features)

        # 3. Opportunity Scoring
        op = opportunity_scoring_engine.predict_opportunity(company_id)

        # 4. ICP Alignment & Similarity
        icp = similarity_engine.calculate_icp_score(company_id)

        # 5. Recommendation Ranking
        recs = recommendation_engine.generate_recommendations(company_id)

        return AccountIntelligence(
            company_id=company_id,
            company_name=f"Company {company_id}",
            icp_score=icp,
            buying_window=bw,
            opportunity_prediction=op,
            recommendations=recs,
        )

    async def generate_prediction_package(
        self,
        workspace_id: uuid.UUID,
        company_ids: List[str],
    ) -> PredictionPackage:
        t0 = time.perf_counter()
        results: List[AccountIntelligence] = []

        for cid in company_ids:
            intel = await self.predict_account_intelligence(workspace_id, cid)
            results.append(intel)

        total_lat = (time.perf_counter() - t0) * 1000.0

        return PredictionPackage(
            workspace_id=workspace_id,
            account_intelligence_list=results,
            overall_pipeline_health_score=88.5,
            execution_time_ms=round(total_lat, 2),
        )


predictive_revenue_engine = PredictiveRevenueEngine()
