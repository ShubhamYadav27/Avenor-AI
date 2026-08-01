import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.global_infrastructure.api.router import router
from app.modules.global_infrastructure.application.services import RegionManager, FailoverManager
from app.modules.global_infrastructure.domain.models import RegionStatus

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_regions():
    RegionManager._regions.clear()
    FailoverManager._incidents.clear()
    
    # Register regions
    client.post("/v1/infrastructure/regions/register", json={
        "id": "eu-west-1", "name": "Europe (Ireland)", "location": "Europe", "cloud_provider": "aws"
    })
    client.post("/v1/infrastructure/regions/register", json={
        "id": "us-east-1", "name": "US East (N. Virginia)", "location": "North America", "cloud_provider": "aws"
    })
    yield

def test_geo_routing_and_auto_failover():
    # 1. Normal routing based on Geography
    res = client.post("/v1/infrastructure/route", json={"client_location": "Europe"})
    assert res.status_code == 200
    assert res.json()["routed_region_id"] == "eu-west-1"
    
    # 2. Simulate EU Region Outage
    RegionManager.update_status("eu-west-1", RegionStatus.DOWN)
    
    # 3. Verify Automatic Failover to US East (next available healthy region)
    res_failover = client.post("/v1/infrastructure/route", json={"client_location": "Europe"})
    assert res_failover.status_code == 200
    assert res_failover.json()["routed_region_id"] == "us-east-1" # Successfully failed over!

def test_disaster_recovery_failover_incident():
    res = client.post("/v1/infrastructure/failover", json={
        "failed_region_id": "us-east-1",
        "target_region_id": "eu-west-1"
    })
    
    assert res.status_code == 200
    assert "incident_id" in res.json()
    assert res.json()["status"] == "completed"
    
    # Verify the failed region is actually drained (status == DOWN)
    region = RegionManager.get_region("us-east-1")
    assert region.status == RegionStatus.DOWN
