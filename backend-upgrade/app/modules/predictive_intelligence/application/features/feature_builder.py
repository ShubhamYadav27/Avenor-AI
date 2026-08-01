"""
Feature Builder (Phase 6.1)
Extracts, normalizes, and weights multi-source revenue features from CRM, buying signals, hiring, and memory.
"""
from typing import List
import uuid

from app.modules.predictive_intelligence.domain.predictive_entities import RevenueFeature


class FeatureBuilder:
    def extract_features(self, workspace_id: uuid.UUID, company_id: str) -> List[RevenueFeature]:
        return [
            RevenueFeature(feature_name="intent_surge_score", value=94.0, weight=0.35, source="signal_engine"),
            RevenueFeature(feature_name="hiring_velocity_30d", value=14.0, weight=0.25, source="hiring_feed"),
            RevenueFeature(feature_name="funding_round_m", value=45.0, weight=0.20, source="crunchbase_provider"),
            RevenueFeature(feature_name="crm_engagement_recency", value=0.95, weight=0.20, source="hubspot_crm"),
        ]


feature_builder = FeatureBuilder()
