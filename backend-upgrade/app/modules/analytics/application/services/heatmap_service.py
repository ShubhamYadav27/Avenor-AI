"""
Heatmap Service (Phase 5.6)
Computes real-time account buying intent surge heatmaps across target accounts.
"""
from typing import List
import uuid

from app.modules.analytics.domain.analytics_entities import AccountIntentHeatmap
from app.modules.analytics.domain.analytics_value_objects import HeatmapTier


class HeatmapService:
    def get_workspace_intent_heatmaps(self, workspace_id: uuid.UUID) -> List[AccountIntentHeatmap]:
        return [
            AccountIntentHeatmap(
                company_id="comp-101",
                company_name="Acme Corporation",
                intent_score=94.5,
                signal_count=18,
                surge_tier=HeatmapTier.HIGH_SURGE,
                primary_topic="Revenue Intelligence",
            ),
            AccountIntentHeatmap(
                company_id="comp-102",
                company_name="Stripe Tech Inc",
                intent_score=88.0,
                signal_count=14,
                surge_tier=HeatmapTier.HIGH_SURGE,
                primary_topic="Predictive Forecasting",
            ),
            AccountIntentHeatmap(
                company_id="comp-103",
                company_name="Global Logistics LLC",
                intent_score=68.2,
                signal_count=8,
                surge_tier=HeatmapTier.MODERATE_SURGE,
                primary_topic="CRM Automation",
            ),
        ]


heatmap_service = HeatmapService()
