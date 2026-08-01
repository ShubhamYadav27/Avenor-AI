import pytest
from datetime import datetime
from fastapi.testclient import TestClient

# Import Domain models
from app.modules.marketplace.domain.models import MarketplaceApp, AppCategory, AppType, AppPermission, InstallStatus

# Import FastAPI Router (this initializes our in-memory services)
from app.modules.marketplace.api.router import router, get_registry_service

# Create a FastAPI wrapper for testing
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture
async def setup_marketplace():
    registry = get_registry_service()
    
    # Pre-seed marketplace with a test app
    test_app = MarketplaceApp(
        id="app-123",
        name="Salesforce Sync",
        description="Official Salesforce integration",
        publisher_id="pub-avenor",
        category=AppCategory.CRM,
        app_type=AppType.OFFICIAL,
        version="1.0.0",
        required_permissions=[AppPermission.READ_COMPANIES, AppPermission.WRITE_COMPANIES],
        capabilities=[],
        dependencies=[],
        published_at=datetime.utcnow()
    )
    await registry.publish_app(test_app)
    return test_app

@pytest.mark.asyncio
async def test_browse_apps(setup_marketplace):
    # Act
    response = client.get("/marketplace/apps")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Salesforce Sync"
    assert data[0]["category"] == "CRM"

@pytest.mark.asyncio
async def test_full_installation_lifecycle(setup_marketplace):
    app_id = "app-123"
    workspace_id = "ws-999"
    
    # 1. Initiate Installation
    req_data = {
        "app_id": app_id,
        "workspace_id": workspace_id,
        "installed_by": "user-42"
    }
    response = client.post("/marketplace/installations", json=req_data)
    assert response.status_code == 200
    install_data = response.json()
    assert install_data["status"] == "Pending Permission"
    install_id = install_data["installation_id"]
    
    # 2. Configure and Activate
    config_req = {
        "config": {"sync_frequency": "1h"}
    }
    config_response = client.post(f"/marketplace/installations/{install_id}/configure", json=config_req)
    assert config_response.status_code == 200
    assert config_response.json()["status"] == "Activated"
    
    # 3. Verify Workspace Installations
    list_response = client.get(f"/marketplace/workspaces/{workspace_id}/installations")
    assert list_response.status_code == 200
    installed_apps = list_response.json()
    assert len(installed_apps) == 1
    assert installed_apps[0]["id"] == install_id
    assert installed_apps[0]["status"] == "Activated"
