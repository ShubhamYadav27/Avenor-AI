import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.modules.public_api.api.router import router, get_key_manager, get_rate_limiter, ReturnEarlyException
from app.modules.public_api.domain.models import RateLimitTier

# Create a FastAPI wrapper for testing
app = FastAPI()

# Add global exception handler for our custom early-return error wrapper
@app.exception_handler(ReturnEarlyException)
async def api_error_handler(request: Request, exc: ReturnEarlyException):
    return JSONResponse(
        status_code=exc.api_error.status,
        content={
            "error": {
                "status": exc.api_error.status,
                "code": exc.api_error.code,
                "message": exc.api_error.message,
                "request_id": exc.api_error.request_id,
                "doc_url": exc.api_error.doc_url
            }
        }
    )

app.include_router(router)
client = TestClient(app)

@pytest.fixture
def test_key():
    key_mgr = get_key_manager()
    # Mint a key with 'read:companies' scope, but strict rate limits (2 RPS) for testing
    key, raw_secret = key_mgr.mint_key("ws-123", "Test Key", ["read:companies"], tier=RateLimitTier.FREE)
    # forcefully modify quota to 2 for easier rate limit testing
    key.quota.requests_per_second = 2
    return raw_secret

def test_missing_auth_header():
    res = client.get("/v1/companies")
    assert res.status_code == 401
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "unauthorized"

def test_invalid_auth_token():
    res = client.get("/v1/companies", headers={"Authorization": "Bearer invalid_token_123"})
    assert res.status_code == 401
    data = res.json()
    assert data["error"]["message"] == "Invalid API Key."

def test_successful_auth_and_routing(test_key):
    res = client.get("/v1/companies", headers={"Authorization": f"Bearer {test_key}"})
    assert res.status_code == 200
    data = res.json()
    assert data["object"] == "list"
    assert len(data["data"]) == 2

def test_rate_limiting_enforcement():
    # Mint a fresh key for this test to avoid global singleton rate limit state leakage
    key_mgr = get_key_manager()
    key, raw_secret = key_mgr.mint_key("ws-rl-test", "RL Key", ["read:companies"], tier=RateLimitTier.FREE)
    key.quota.requests_per_second = 2
    
    # Request 1: OK
    res1 = client.get("/v1/me", headers={"Authorization": f"Bearer {raw_secret}"})
    assert res1.status_code == 200
    
    # Request 2: OK
    res2 = client.get("/v1/me", headers={"Authorization": f"Bearer {raw_secret}"})
    assert res2.status_code == 200
    
    # Request 3: TOO MANY REQUESTS
    res3 = client.get("/v1/me", headers={"Authorization": f"Bearer {raw_secret}"})
    assert res3.status_code == 429
    data = res3.json()
    assert data["error"]["code"] == "rate_limit_exceeded"

def test_insufficient_scope():
    key_mgr = get_key_manager()
    # Mint a key WITHOUT 'read:companies' scope
    key, raw_secret = key_mgr.mint_key("ws-123", "No Scope Key", ["read:contacts"])
    
    res = client.get("/v1/companies", headers={"Authorization": f"Bearer {raw_secret}"})
    assert res.status_code == 403
    data = res.json()
    assert data["error"]["code"] == "forbidden_scope"
