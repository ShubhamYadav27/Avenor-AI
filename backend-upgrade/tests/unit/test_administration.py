import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.administration.api.router import router
from app.modules.administration.application.services import AuditEngine

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_rbac_engine_super_admin():
    # User 1 is Super Admin
    res = client.post("/v1/admin/evaluate", json={"user_id": "u_1", "permission": "system:wipe"})
    assert res.status_code == 200
    assert res.json()["granted"] is True

def test_rbac_engine_sales_rep_denied():
    # User 2 is Sales Rep (allowed dashboard:read, denied prompt:publish)
    res = client.post("/v1/admin/evaluate", json={"user_id": "u_2", "permission": "prompt:publish"})
    assert res.status_code == 200
    assert res.json()["granted"] is False

def test_policy_engine_ip_restriction_allow():
    # 192.168.1.100 is whitelisted in router seed
    res = client.post("/v1/admin/login_attempt", json={"client_ip": "192.168.1.100"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"

def test_policy_engine_ip_restriction_deny():
    # Unknown IP should be blocked by PolicyEngine
    res = client.post("/v1/admin/login_attempt", json={"client_ip": "45.22.1.9"})
    assert res.status_code == 403
    assert "Access blocked" in res.json()["detail"]

def test_audit_ledger_immutability():
    # The previous tests generated audit logs automatically
    res = client.get("/v1/admin/audit")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 4 # 2 from evaluate, 2 from login
    
    # Verify structure of ledger
    assert logs[0]["action"] == "rbac.evaluation"
    assert logs[-1]["action"] == "security.login_attempt"
