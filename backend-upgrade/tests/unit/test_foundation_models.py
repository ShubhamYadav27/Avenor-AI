import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.foundation_models.api.router import router
from app.modules.foundation_models.application.services import ModelRegistry
from app.modules.foundation_models.domain.models import PredictionTarget

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_registry():
    ModelRegistry._registry.clear()
    yield

def test_prediction_fails_without_champion():
    # Target has no models
    res = client.get("/v1/models/predict/deal_risk/ent_123")
    assert res.status_code == 400
    assert "No active Champion" in res.json()["detail"]

def test_model_registry_promotion_and_inference():
    # 1. Register a V1 model
    res1 = client.post("/v1/models/registry/register", json={
        "target": "buying_window",
        "version_tag": "v1.0.0",
        "accuracy_score": 0.82
    })
    mod1_id = res1.json()["model_id"]
    
    # 2. Promote V1 to Champion
    res_promo1 = client.post(f"/v1/models/registry/{mod1_id}/promote", json={"target": "buying_window"})
    assert res_promo1.status_code == 200
    
    # 3. Register a V2 model
    res2 = client.post("/v1/models/registry/register", json={
        "target": "buying_window",
        "version_tag": "v2.0.0",
        "accuracy_score": 0.89
    })
    mod2_id = res2.json()["model_id"]
    
    # 4. Promote V2 to Champion (V1 should be demoted automatically in backend)
    client.post(f"/v1/models/registry/{mod2_id}/promote", json={"target": "buying_window"})
    
    # 5. Run inference and verify the output structure
    res_predict = client.get("/v1/models/predict/buying_window/ent_acme")
    assert res_predict.status_code == 200
    
    prediction = res_predict.json()
    assert prediction["model_version"] == "v2.0.0" # Verified V2 was used
    
    # 6. Verify Explainability is strictly enforced
    explain = prediction["explainability"]
    assert len(explain["top_contributors"]) > 0
    assert "decision_maker_engaged" in explain["top_contributors"][0]["feature"]
    assert len(explain["supporting_evidence"]) > 0
