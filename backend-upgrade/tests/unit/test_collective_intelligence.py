import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.cross_customer_intelligence.api.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_consent_manager_blocking():
    # 1. Attempt to ingest data for an org that HAS NOT opted in
    res = client.post("/v1/collective/signals/ingest", json={
        "org_id": "org_secret_corp",
        "cohort_name": "SaaS",
        "signal_type": "engineering_hiring",
        "raw_value": 15.0
    })
    
    # Must be hard blocked by PrivacyGuard
    assert res.status_code == 403
    assert "Privacy Block" in res.json()["detail"]

def test_consent_manager_opt_in_and_anonymization():
    # 1. Org Explicitly Opts In
    client.post("/v1/collective/consent/org_transparent_inc", json={"is_opted_in": True})
    
    # 2. Attempt to ingest data again
    res = client.post("/v1/collective/signals/ingest", json={
        "org_id": "org_transparent_inc",
        "cohort_name": "B2B SaaS (Series C)",
        "signal_type": "engineering_hiring",
        "raw_value": 25.0 # Raw hiring number
    })
    
    assert res.status_code == 200
    data = res.json()
    
    # 3. Verify absolute anonymization
    assert data["status"] == "anonymized_and_ingested"
    assert "org_transparent_inc" not in data["anonymous_id"] # ID is completely decoupled
    assert data["bucket"] == "high_growth" # Raw 25.0 is stripped and bucketed

def test_insight_engine_generation():
    res = client.get("/v1/collective/insights")
    assert res.status_code == 200
    
    insights = res.json()["insights"]
    assert len(insights) > 0
    
    insight = insights[0]
    # Check that the mathematical correlation was converted to a human narrative
    assert "Organizations experiencing high_growth engineering hiring" in insight["message"]
    assert "82" in insight["confidence"]
    assert "14500" in insight["evidence_base"]
