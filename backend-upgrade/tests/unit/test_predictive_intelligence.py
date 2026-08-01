import uuid
import pytest

from app.modules.predictive_intelligence.application.engine import predictive_revenue_engine
from app.modules.predictive_intelligence.application.engines.buying_window_engine import buying_window_engine
from app.modules.predictive_intelligence.application.engines.opportunity_scoring_engine import opportunity_scoring_engine
from app.modules.predictive_intelligence.application.engines.recommendation_engine import recommendation_engine
from app.modules.predictive_intelligence.application.engines.similarity_engine import similarity_engine
from app.modules.predictive_intelligence.application.features.feature_builder import feature_builder
from app.modules.predictive_intelligence.domain.predictive_entities import AccountIntelligence, PredictionPackage
from app.modules.predictive_intelligence.domain.predictive_value_objects import BuyingWindowStage, RiskLevel


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_feature_builder():
    ws_id = uuid.uuid4()
    features = feature_builder.extract_features(ws_id, "comp-101")
    assert len(features) == 4
    assert features[0].feature_name == "intent_surge_score"


def test_buying_window_engine():
    features = feature_builder.extract_features(uuid.uuid4(), "comp-101")
    bw = buying_window_engine.detect_buying_window("comp-101", features)
    assert bw.stage == BuyingWindowStage.PEAK_SURGE
    assert bw.confidence_score >= 0.90


def test_opportunity_scoring_engine():
    op = opportunity_scoring_engine.predict_opportunity("comp-101")
    assert op.win_probability == 0.86
    assert op.risk_level == RiskLevel.LOW


def test_similarity_engine():
    icp = similarity_engine.calculate_icp_score("comp-101")
    assert icp == 92.5


def test_recommendation_engine():
    recs = recommendation_engine.generate_recommendations("comp-101")
    assert len(recs) == 2
    assert recs[0].priority_score == 96.0


@pytest.mark.anyio
async def test_predictive_revenue_engine_e2e():
    ws_id = uuid.uuid4()
    intel = await predictive_revenue_engine.predict_account_intelligence(ws_id, "comp-101")

    assert isinstance(intel, AccountIntelligence)
    assert intel.icp_score == 92.5
    assert intel.buying_window.stage == BuyingWindowStage.PEAK_SURGE
    assert intel.opportunity_prediction.win_probability == 0.86
    assert len(intel.recommendations) == 2


@pytest.mark.anyio
async def test_predictive_revenue_engine_package():
    ws_id = uuid.uuid4()
    pkg = await predictive_revenue_engine.generate_prediction_package(ws_id, ["comp-101", "comp-102"])

    assert isinstance(pkg, PredictionPackage)
    assert len(pkg.account_intelligence_list) == 2
    assert pkg.overall_pipeline_health_score == 88.5
