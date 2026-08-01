from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.global_infrastructure.domain.models import CloudProvider, RegionStatus
from app.modules.global_infrastructure.application.services import (
    RegionManager, GeoRoutingEngine, FailoverManager, NoHealthyRegionError
)

router = APIRouter(prefix="/v1/infrastructure", tags=["Global Infrastructure"])

@router.post("/regions/register")
async def register_region(payload: Dict[str, Any]) -> dict:
    region_id = payload.get("id")
    name = payload.get("name")
    location = payload.get("location")
    provider = CloudProvider(payload.get("cloud_provider"))
    
    region = RegionManager.register_region(region_id, name, location, provider)
    return {
        "region_id": region.id,
        "status": region.status.value,
        "message": "Region registered successfully in Global Control Plane"
    }

@router.post("/route")
async def get_optimal_route(payload: Dict[str, Any]) -> dict:
    """Intelligent Geo-Routing. Falls back automatically if primary region is down."""
    client_location = payload.get("client_location", "Unknown")
    
    try:
        region = GeoRoutingEngine.route_request(client_location)
        return {
            "client_location": client_location,
            "routed_region_id": region.id,
            "region_latency_ms": region.current_latency_ms
        }
    except NoHealthyRegionError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/failover")
async def trigger_manual_failover(payload: Dict[str, Any]) -> dict:
    """Manually triggers a massive Active-Passive disaster recovery failover."""
    failed_id = payload.get("failed_region_id")
    target_id = payload.get("target_region_id")
    
    incident = FailoverManager.trigger_failover(failed_id, target_id)
    
    return {
        "incident_id": incident.id,
        "status": incident.status.value,
        "message": f"Successfully drained traffic from {failed_id} and failed over to {target_id}"
    }
