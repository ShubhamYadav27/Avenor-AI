import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.feature_store.api.router import router
from app.modules.feature_store.application.services import FeatureRegistry, OnlineFeatureStore, FeatureDriftMonitor
from app.modules.feature_store.domain.models import FeatureType, FeatureLineage, FeatureValue, FeatureHealthStatus

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_state():
    FeatureRegistry._catalog.clear()
    OnlineFeatureStore._cache.clear()
    yield

def test_feature_catalog_lifecycle():
    # 1. Register v1.0
    res1 = client.post("/v1/features/catalog/register", json={
        "name": "decision_maker_engaged_90d",
        "type": "numerical",
        "version": "v1.0",
        "lineage": {
            "source_system": "CRM",
            "transformation_logic": "sum of meetings in 90 days"
        }
    })
    assert res1.status_code == 200
    assert res1.json()["status"] == "draft"
    
    # 2. Promote to Production
    res_promo = client.post("/v1/features/catalog/decision_maker_engaged_90d/v1.0/promote")
    assert res_promo.status_code == 200
    assert res_promo.json()["status"] == "production"

def test_online_feature_store_retrieval():
    # Manually ingest a mock value (usually done by Materialization Engine via Kafka/Spark)
    val = FeatureValue(entity_id="ent_acme", feature_id="feat_123", value=14.5)
    OnlineFeatureStore.ingest_value(val, "decision_maker_engaged_90d")
    
    # Fetch it online
    res = client.post("/v1/features/online/fetch", json={
        "entity_id": "ent_acme",
        "features": ["decision_maker_engaged_90d", "missing_feature"]
    })
    
    assert res.status_code == 200
    data = res.json()
    assert data["vector"]["decision_maker_engaged_90d"] == 14.5
    assert data["vector"]["missing_feature"] is None # Handled safely

def test_feature_drift_monitor():
    lineage = FeatureLineage("CRM", ["field1"], "none", "system")
    feature = FeatureRegistry.register_feature("test_feat", FeatureType.NUMERICAL, "v1", lineage)
    
    # 1. Healthy (10% nulls)
    health = FeatureDriftMonitor.calculate_health(feature, null_count=10, total_count=100)
    assert health.status == FeatureHealthStatus.HEALTHY
    
    # 2. Degraded (30% nulls)
    health = FeatureDriftMonitor.calculate_health(feature, null_count=30, total_count=100)
    assert health.status == FeatureHealthStatus.DEGRADED
    
    # 3. Critical (60% nulls)
    health = FeatureDriftMonitor.calculate_health(feature, null_count=60, total_count=100)
    assert health.status == FeatureHealthStatus.CRITICAL
