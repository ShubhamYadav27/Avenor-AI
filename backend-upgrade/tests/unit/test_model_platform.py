import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.model_platform.api.router import router
from app.modules.model_platform.application.services import ExperimentTracker, DeploymentManager

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_state():
    ExperimentTracker._experiments.clear()
    ExperimentTracker._runs.clear()
    DeploymentManager._routing_table.clear()
    yield

def test_experiment_tracking_with_fairness_block():
    # 1. Successful run with low bias
    res_success = client.post("/v1/mlops/experiments/run", json={
        "experiment_name": "Test Run",
        "model_id": "mod_1",
        "metrics": {
            "accuracy": 0.90,
            "bias_score": 0.02 # Safe
        }
    })
    assert res_success.status_code == 200
    
    # 2. Blocked run due to high bias
    res_blocked = client.post("/v1/mlops/experiments/run", json={
        "experiment_name": "Biased Run",
        "model_id": "mod_2",
        "metrics": {
            "accuracy": 0.99, # Incredible accuracy
            "bias_score": 0.15 # Fails fairness test
        }
    })
    assert res_blocked.status_code == 422
    assert "Bias score" in res_blocked.json()["detail"]

def test_deployment_traffic_splitting():
    # 1. Invalid configuration (sums to 90%)
    res_invalid = client.post("/v1/mlops/deployments/canary", json={
        "target": "deal_risk",
        "rules": [
            {"model_id": "v1", "percentage": 80, "strategy": "direct"},
            {"model_id": "v2", "percentage": 10, "strategy": "canary"}
        ]
    })
    assert res_invalid.status_code == 400
    
    # 2. Valid configuration (Live sums to 100%, Shadow is ignored in sum)
    res_valid = client.post("/v1/mlops/deployments/canary", json={
        "target": "deal_risk",
        "rules": [
            {"model_id": "v1", "percentage": 90, "strategy": "direct"},
            {"model_id": "v2", "percentage": 10, "strategy": "canary"},
            {"model_id": "v3", "percentage": 100, "strategy": "shadow"} # Doesn't count towards live limit
        ]
    })
    assert res_valid.status_code == 200
    assert res_valid.json()["rules_applied"] == 3
