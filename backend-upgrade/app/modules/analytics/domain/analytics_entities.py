"""
Analytics Entities (Phase 5.6)
Pure domain entities representing predictive forecasts, intent heatmaps, and executive revenue reports.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
import uuid

from app.modules.analytics.domain.analytics_value_objects import HeatmapTier


@dataclass
class PredictiveForecast:
    workspace_id: uuid.UUID
    total_pipeline_usd: float = 0.0
    commit_usd: float = 0.0
    best_case_usd: float = 0.0
    weighted_forecast_usd: float = 0.0
    win_probability_avg: float = 0.78
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AccountIntentHeatmap:
    company_id: str
    company_name: str
    intent_score: float = 0.0  # 0 to 100
    signal_count: int = 0
    surge_tier: HeatmapTier = HeatmapTier.HIGH_SURGE
    primary_topic: str = "Revenue Intelligence"


@dataclass
class ExecutiveAnalyticsReport:
    workspace_id: uuid.UUID
    forecast: PredictiveForecast
    heatmaps: List[AccountIntentHeatmap] = field(default_factory=list)
    total_deals_analyzed: int = 0
    ai_impact_score: float = 0.94
