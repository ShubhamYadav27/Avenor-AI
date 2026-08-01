import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.industry_benchmarking.api.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_percentile_distribution_math():
    # cohort_saas_smb has 10 data points for WIN_RATE
    # [12.0, 15.5, 18.0, 22.0, 24.5, 25.0, 31.0, 35.0, 42.0, 45.0]
    res = client.get("/v1/benchmarks/cohorts/cohort_saas_smb/metrics/win_rate")
    assert res.status_code == 200
    
    dist = res.json()["distribution"]
    
    # Verify calculated percentiles
    assert dist["median"] == 24.75 # Middle between 24.5 and 25.0
    assert dist["p90"] == 42.3 # 90th percentile
    assert res.json()["sample_size"] == 10

def test_privacy_guard_enforcement():
    # cohort_finance_ent only has 3 members. PrivacyGuard requires MIN=5
    res = client.get("/v1/benchmarks/cohorts/cohort_finance_ent/metrics/win_rate")
    assert res.status_code == 403
    assert "Privacy Guard Block" in res.json()["detail"]

def test_insight_engine_higher_is_better():
    # My win rate is 43% (Top 10%)
    res = client.post("/v1/benchmarks/cohorts/cohort_saas_smb/metrics/win_rate/insight", json={"user_value": 43.0})
    assert res.status_code == 200
    insight = res.json()
    assert insight["severity"] == "positive"
    assert "Top 25%" in insight["message"]

def test_insight_engine_lower_is_better():
    # My sales cycle is 110 days. P75 is roughly 75, so 110 is very slow.
    res = client.post("/v1/benchmarks/cohorts/cohort_saas_smb/metrics/sales_cycle_days/insight", json={"user_value": 110.0})
    assert res.status_code == 200
    insight = res.json()
    assert insight["severity"] == "negative" # Because long sales cycle is bad
    assert "significantly longer" in insight["message"]
