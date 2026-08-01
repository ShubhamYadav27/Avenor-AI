import pytest
import asyncio
from uuid import UUID, uuid4
from typing import Dict, Any, AsyncGenerator

from app.modules.integration_hub.domain.models import IntegrationConnection, ProviderMetadata, SyncCursor, ProviderAuthType, ProviderCapability
from app.modules.integration_hub.application.provider_registry import provider_registry, ProviderRegistry
from app.modules.integration_hub.application.oauth_manager import OAuthManager
from app.modules.integration_hub.application.sync_engine import SyncEngine
from app.modules.integration_hub.application.retry_engine import RetryEngine

# --- Mock Providers ---

class MockOAuthProvider:
    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="mock_oauth",
            display_name="Mock OAuth Provider",
            description="A test provider",
            supported_auth_types=[ProviderAuthType.OAUTH2],
            supported_capabilities=[ProviderCapability.COMPANIES]
        )
        
    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        return f"https://mock.provider.com/auth?state={state}&redirect_uri={redirect_uri}"
        
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        if code != "valid_code":
            raise ValueError("Invalid code")
        return {"access_token": "mock_access", "refresh_token": "mock_refresh"}
        
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        return {"access_token": "new_access", "refresh_token": "new_refresh"}

class MockSyncProvider:
    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="mock_sync",
            display_name="Mock Sync Provider",
            description="A test sync provider",
            supported_auth_types=[ProviderAuthType.API_KEY],
            supported_capabilities=[ProviderCapability.COMPANIES]
        )

    async def fetch_records(self, connection: IntegrationConnection, entity_type: str, cursor: SyncCursor = None) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"id": "1", "name": "Test Company 1"}
        yield {"id": "2", "name": "Test Company 2"}

# Register mocks
provider_registry.register("mock_oauth", MockOAuthProvider)
provider_registry.register("mock_sync", MockSyncProvider)


@pytest.mark.asyncio
async def test_oauth_manager_generates_url_and_stores_state():
    manager = OAuthManager()
    url = manager.get_authorization_url("mock_oauth", "https://app.avenor.ai/callback")
    
    assert url is not None
    assert "mock.provider.com" in url
    assert len(manager._pkce_state_store) == 1
    
    # Extract state from URL to test exchange
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    state = qs["state"][0]
    
    # Test successful exchange
    tenant_id = uuid4()
    credentials_id = await manager.exchange_callback(
        provider_name="mock_oauth",
        code="valid_code",
        state=state,
        redirect_uri="https://app.avenor.ai/callback",
        tenant_id=tenant_id
    )
    assert credentials_id is not None
    assert state not in manager._pkce_state_store # state consumed

@pytest.mark.asyncio
async def test_oauth_manager_invalid_state():
    manager = OAuthManager()
    with pytest.raises(ValueError, match="Invalid or expired OAuth state"):
        await manager.exchange_callback(
            provider_name="mock_oauth",
            code="valid_code",
            state="invalid_state",
            redirect_uri="https://app.avenor.ai/callback",
            tenant_id=uuid4()
        )

@pytest.mark.asyncio
async def test_sync_engine_processes_records():
    engine = SyncEngine()
    connection = IntegrationConnection(
        id=uuid4(),
        tenant_id=uuid4(),
        provider_name="mock_sync",
        auth_type=ProviderAuthType.API_KEY,
        credentials_id=uuid4()
    )
    
    # Run sync
    new_cursor = await engine.run_sync_job(connection, "companies")
    
    # In this mock, it just returns None for the new cursor, but it shouldn't crash
    assert new_cursor is None

@pytest.mark.asyncio
async def test_retry_engine_transient_failure():
    engine = RetryEngine()
    engine.base_delay = 0.01 # fast tests
    
    attempts = 0
    async def failing_op():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Rate limit exceeded 429")
        return "success"
        
    result = await engine.execute_with_retry(failing_op)
    assert result == "success"
    assert attempts == 3

@pytest.mark.asyncio
async def test_retry_engine_permanent_failure():
    engine = RetryEngine()
    
    async def hard_failing_op():
        raise ValueError("Auth failed 401")
        
    with pytest.raises(ValueError, match="Auth failed 401"):
        await engine.execute_with_retry(hard_failing_op)
