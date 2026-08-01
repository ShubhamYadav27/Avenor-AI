import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.ai_governance.api.router import router
from app.modules.ai_governance.application.services import HumanApprovalEngine

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_governance():
    HumanApprovalEngine._queue.clear()
    yield

def test_ai_hallucination_blocking():
    # Submit a response that includes unsupported facts (Acme is NOT in evidence)
    res = client.post("/v1/governance/decisions/validate", json={
        "output": "We recommend acquiring Acme Corp immediately.",
        "evidence": ["Competitor A has good financials."],
        "risk_level": "medium"
    })
    
    # 422 Unprocessable Entity - The AI Safety Gate blocked it
    assert res.status_code == 422
    assert "AI Safety Block" in res.json()["detail"]

def test_ai_human_in_the_loop_routing():
    # 1. Submit HIGH risk prediction (No hallucination)
    res_val = client.post("/v1/governance/decisions/validate", json={
        "output": "Close $5M deal.",
        "evidence": ["Close $5M deal."],
        "risk_level": "high"
    })
    assert res_val.status_code == 200
    assert res_val.json()["approval_status"] == "pending"
    decision_id = res_val.json()["decision_id"]
    
    # 2. Human explicitly approves the AI's decision
    res_approve = client.post(f"/v1/governance/approvals/{decision_id}/process", json={
        "reviewer_id": "usr_exec_1",
        "is_approved": True
    })
    assert res_approve.status_code == 200
    assert res_approve.json()["new_status"] == "approved"
    assert res_approve.json()["reviewed_by"] == "usr_exec_1"
