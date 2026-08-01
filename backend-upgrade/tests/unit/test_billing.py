import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.billing.api.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_entitlement_engine_allow_within_limit():
    # org_1 is FREE tier, max_agents limit is 1
    res = client.post("/v1/billing/entitlements/evaluate", json={"org_id": "org_1", "feature": "max_agents", "requested_amount": 1})
    assert res.status_code == 200
    assert res.json()["granted"] is True

def test_entitlement_engine_deny_over_limit():
    # org_1 is FREE tier, max_agents limit is 1. Asking for 2 should trigger a 402 Upgrade Required
    res = client.post("/v1/billing/entitlements/evaluate", json={"org_id": "org_1", "feature": "max_agents", "requested_amount": 2})
    assert res.status_code == 402
    assert "Upgrade required" in res.json()["detail"]

def test_entitlement_engine_deny_feature_lock():
    # org_1 is FREE tier, does not have api_access
    res = client.post("/v1/billing/entitlements/evaluate", json={"org_id": "org_1", "feature": "api_access"})
    assert res.status_code == 402

def test_usage_metering_and_invoicing():
    # org_2 is PROFESSIONAL tier
    # 1. Report LLM Token Usage (e.g., 50,000 tokens)
    client.post("/v1/billing/usage", json={"org_id": "org_2", "metric_name": "llm_tokens", "value": 50000})
    
    # 2. Generate Invoice Preview
    res = client.get("/v1/billing/invoices/preview?org_id=org_2")
    assert res.status_code == 200
    invoice = res.json()
    
    # Verify Math: Base Plan ($299) + Usage (50k tokens @ $0.02/1k = $1.00)
    assert invoice["amount_due"] == 300.0
    
    # Verify Line Items
    assert len(invoice["line_items"]) == 2
    assert "Base Plan" in invoice["line_items"][0]["description"]
    assert "LLM Token" in invoice["line_items"][1]["description"]
    assert invoice["line_items"][1]["total"] == 1.0
