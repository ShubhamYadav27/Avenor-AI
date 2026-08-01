import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.sdk_platform.api.router import router
from app.modules.sdk_platform.application.services import RequestPipelineBuilder, ErrorMapper
from app.modules.sdk_platform.domain.models import SdkConfig
from app.modules.sdk_platform.domain.exceptions import RateLimitError, ServerError, AuthenticationError

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_sdk_discovery_endpoint():
    res = client.get("/v1/sdks/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    assert any(sdk["language"] == "Python" for sdk in data)
    assert any(sdk["install_command"] == "pip install avenor-sdk" for sdk in data)

def test_sdk_discovery_specific_language():
    res = client.get("/v1/sdks/TypeScript")
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "TypeScript"
    assert "npm install @avenor/sdk" in data["install_command"]

def test_error_mapper_resolves_correct_exceptions():
    payload = {"message": "Invalid API Key", "request_id": "req_123"}
    with pytest.raises(AuthenticationError) as exc:
        ErrorMapper.map_http_response(401, payload)
    assert exc.value.status_code == 401
    assert exc.value.request_id == "req_123"

from unittest.mock import patch

def test_request_pipeline_exponential_backoff_retry():
    config = SdkConfig(max_retries=2)
    pipeline = RequestPipelineBuilder(config)
    
    with patch("time.sleep", return_value=None) as mock_sleep:
        # Simulate API call that fails with 429 twice, then succeeds
        call_counts = 0
        def mock_api_call():
            nonlocal call_counts
            call_counts += 1
            if call_counts <= 2:
                return 429, {"message": "Rate limited", "request_id": "req_rl"}
            return 200, {"data": "success"}
    
        result = pipeline.execute_with_retries(mock_api_call)
        assert result["data"] == "success"
        assert call_counts == 3
        # Ensure sleep was called twice (for the two retries)
        assert mock_sleep.call_count == 2
        # Check exponential backoff amounts
        mock_sleep.assert_any_call(0.1) # 2^0 * 0.1
        mock_sleep.assert_any_call(0.2) # 2^1 * 0.1

def test_request_pipeline_max_retries_exceeded():
    config = SdkConfig(max_retries=1)
    pipeline = RequestPipelineBuilder(config)
    
    with patch("time.sleep", return_value=None) as mock_sleep:
        # Simulate API call that ALWAYS fails with 429
        def mock_api_call():
            return 429, {"message": "Rate limited", "request_id": "req_rl"}
    
        with pytest.raises(RateLimitError):
            pipeline.execute_with_retries(mock_api_call)
        
        # Attempted initial + 1 retry = 2 calls
        assert mock_sleep.call_count == 1
