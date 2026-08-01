import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.compliance_cloud.api.router import router
from app.modules.compliance_cloud.application.services import PrivacyManager, ComplianceAuditEngine, DataClassificationEngine
from app.modules.compliance_cloud.domain.models import ComplianceControl, ComplianceFramework, DataClassification

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_compliance():
    PrivacyManager._requests.clear()
    ComplianceAuditEngine._controls.clear()
    
    # Reset Legal Hold
    DataClassificationEngine.set_legal_hold(DataClassification.RESTRICTED, False)
    
    # Register Mock SOC2 Controls
    ComplianceAuditEngine.register_control(
        ComplianceControl("c_1", ComplianceFramework.SOC2, "MFA Enforced", "Require 2FA", True)
    )
    ComplianceAuditEngine.register_control(
        ComplianceControl("c_2", ComplianceFramework.SOC2, "At-Rest Encryption", "AES-256", False) # Failing
    )
    yield

def test_privacy_erasure_flow():
    # 1. Submit Request
    res_submit = client.post("/v1/compliance/privacy-requests", json={
        "user_id": "usr_abc",
        "request_type": "erasure"
    })
    assert res_submit.status_code == 200
    req_id = res_submit.json()["request_id"]
    
    # 2. Execute Erasure
    res_exec = client.post(f"/v1/compliance/privacy-requests/{req_id}/execute")
    assert res_exec.status_code == 200
    assert res_exec.json()["status"] == "completed"

def test_compliance_soc2_audit():
    res = client.get("/v1/compliance/reports/soc2")
    assert res.status_code == 200
    data = res.json()
    
    assert data["framework"] == "soc2"
    assert data["is_compliant"] is False # Because encryption control failed
    assert data["readiness_score"] == 50.0
    assert "At-Rest Encryption" in data["failing_controls"]

def test_data_classification_retention_policy():
    res = client.get("/v1/compliance/classification/restricted/policy")
    assert res.status_code == 200
    assert res.json()["ttl_days"] == 30
    assert res.json()["is_legal_hold"] is False
