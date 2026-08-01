import uuid

from app.modules.analytics.application.services.forecast_service import forecast_service
from app.modules.analytics.application.services.heatmap_service import heatmap_service
from app.modules.analytics.domain.analytics_entities import PredictiveForecast
from app.modules.analytics.domain.analytics_value_objects import HeatmapTier


def test_forecast_service_calculation():
    ws_id = uuid.uuid4()
    forecast = forecast_service.calculate_predictive_forecast(ws_id)

    assert isinstance(forecast, PredictiveForecast)
    assert forecast.workspace_id == ws_id
    assert forecast.total_pipeline_usd == 2450000.0
    assert forecast.commit_usd == 1150000.0
    assert forecast.weighted_forecast_usd > forecast.commit_usd
    assert forecast.win_probability_avg == 0.82


def test_heatmap_service_accounts():
    ws_id = uuid.uuid4()
    heatmaps = heatmap_service.get_workspace_intent_heatmaps(ws_id)

    assert len(heatmaps) == 3
    assert heatmaps[0].company_name == "Acme Corporation"
    assert heatmaps[0].surge_tier == HeatmapTier.HIGH_SURGE
    assert heatmaps[0].intent_score > 90.0
