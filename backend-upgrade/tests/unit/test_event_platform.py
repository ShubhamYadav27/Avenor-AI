import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.event_platform.api.router import router, _manager
from app.modules.event_platform.domain.models import Event, WebhookEndpoint, DeliveryLog, DeliveryStatus, WebhookStatus
from app.modules.event_platform.application.services import EventDispatcher, DeliveryEngine
from app.modules.event_platform.application.crypto import generate_signature, verify_signature

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_webhook_router_list():
    res = client.get("/v1/webhooks/?workspace_id=ws_001")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["url"] == "https://api.mycompany.com/avenor-webhook"

def test_webhook_router_create():
    res = client.post("/v1/webhooks/?workspace_id=ws_002", json={
        "url": "https://api.example.com/hook",
        "subscribed_events": ["opportunity.won"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["url"] == "https://api.example.com/hook"
    assert "secret" in data
    assert data["secret"].startswith("whsec_")

def test_webhook_router_create_invalid_url():
    res = client.post("/v1/webhooks/?workspace_id=ws_002", json={
        "url": "http://insecure.com/hook",
        "subscribed_events": ["*"]
    })
    assert res.status_code == 400

def test_hmac_signature_verification():
    payload = {"data": "test_payload"}
    timestamp = "1672531200"
    secret = "whsec_test_secret_123"
    
    # Generate
    sig = generate_signature(payload, timestamp, secret)
    assert len(sig) == 64 # SHA-256 hex length
    
    # Verify exact match
    assert verify_signature(payload, timestamp, sig, secret) is True
    
    # Verify failure on tampered payload
    tampered_payload = {"data": "test_payload_hacked"}
    assert verify_signature(tampered_payload, timestamp, sig, secret) is False

def test_event_dispatcher_wildcard_matching():
    ep = WebhookEndpoint(
        id="ep_1", workspace_id="ws_1", url="https://x",
        subscribed_events=["company.*"], secret="sec"
    )
    
    assert ep.matches_event("company.created") is True
    assert ep.matches_event("company.deleted") is True
    assert ep.matches_event("opportunity.won") is False

def test_delivery_engine_success():
    ep = WebhookEndpoint(id="ep_1", workspace_id="ws_1", url="https://x", subscribed_events=["*"], secret="sec")
    event = Event(id="evt_1", type="company.created", payload={"id": "comp_1"})
    log = DeliveryLog(id="del_1", endpoint_id="ep_1", event_id="evt_1", status=DeliveryStatus.QUEUED)
    
    def mock_success_client(url, headers, body):
        assert "X-Avenor-Signature" in headers
        assert "v1=" in headers["X-Avenor-Signature"]
        return 200, "OK"
        
    engine = DeliveryEngine(mock_success_client)
    engine.process_delivery(log, event, ep)
    
    assert log.status == DeliveryStatus.DELIVERED
    assert log.attempts == 1

def test_delivery_engine_failure_to_dlq():
    ep = WebhookEndpoint(id="ep_1", workspace_id="ws_1", url="https://x", subscribed_events=["*"], secret="sec")
    event = Event(id="evt_1", type="company.created", payload={"id": "comp_1"})
    log = DeliveryLog(id="del_1", endpoint_id="ep_1", event_id="evt_1", status=DeliveryStatus.QUEUED, max_attempts=2)
    
    def mock_fail_client(url, headers, body):
        return 500, "Internal Server Error"
        
    engine = DeliveryEngine(mock_fail_client)
    
    # Attempt 1 -> FAILED
    engine.process_delivery(log, event, ep)
    assert log.status == DeliveryStatus.FAILED
    assert log.attempts == 1
    
    # Attempt 2 -> DEAD LETTER QUEUE
    engine.process_delivery(log, event, ep)
    assert log.status == DeliveryStatus.DEAD
    assert log.attempts == 2
