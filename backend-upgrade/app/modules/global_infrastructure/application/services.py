import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.global_infrastructure.domain.models import (
    Region, RegionStatus, CloudProvider, DisasterRecoveryIncident, DRIncidentStatus, RoutingStrategy
)

class NoHealthyRegionError(Exception):
    pass

class RegionNotFoundError(Exception):
    pass

class RegionManager:
    """Maintains absolute state of all global deployments."""
    
    _regions: Dict[str, Region] = {}
    
    @classmethod
    def register_region(cls, region_id: str, name: str, location: str, provider: CloudProvider) -> Region:
        r = Region(
            id=region_id,
            name=name,
            location=location,
            cloud_provider=provider,
            status=RegionStatus.HEALTHY,
            current_latency_ms=10.0 # Default optimal
        )
        cls._regions[region_id] = r
        return r
        
    @classmethod
    def get_region(cls, region_id: str) -> Region:
        if region_id not in cls._regions:
            raise RegionNotFoundError(f"Region {region_id} not found")
        return cls._regions[region_id]

    @classmethod
    def update_status(cls, region_id: str, status: RegionStatus):
        region = cls.get_region(region_id)
        region.status = status
        region.last_health_check_at = datetime.utcnow()

class GeoRoutingEngine:
    """Intelligent Anycast-style traffic orchestrator with Auto-Failover."""
    
    @classmethod
    def route_request(cls, client_location: str, strategy: RoutingStrategy = RoutingStrategy.GEO_BASED) -> Region:
        """
        Determines the optimal region. If the optimal region is DOWN, 
        it automatically fails over to the next healthiest region.
        """
        regions = list(RegionManager._regions.values())
        if not regions:
            raise NoHealthyRegionError("No regions configured.")
            
        # 1. Find optimal target (Exact location match)
        target = next((r for r in regions if r.location == client_location), None)
        
        # 2. Fallback to latency based if no exact match found
        if not target:
            target = min(regions, key=lambda r: r.current_latency_ms)
            
        # 3. Automatic Failover: If target is DOWN, route to the next best HEALTHY region
        if target.status == RegionStatus.DOWN:
            healthy_regions = [r for r in regions if r.status == RegionStatus.HEALTHY]
            if not healthy_regions:
                raise NoHealthyRegionError("Global Outage: All regions are DOWN.")
            # Route to the healthy region with lowest latency
            target = min(healthy_regions, key=lambda r: r.current_latency_ms)
            
        return target

class FailoverManager:
    """Orchestrates massive Disaster Recovery active-passive failover events."""
    
    _incidents: Dict[str, DisasterRecoveryIncident] = {}
    
    @classmethod
    def trigger_failover(cls, failed_region_id: str, target_region_id: str) -> DisasterRecoveryIncident:
        # Mark the failed region as DOWN so GeoRoutingEngine drains it instantly
        RegionManager.update_status(failed_region_id, RegionStatus.DOWN)
        
        incident = DisasterRecoveryIncident(
            id=f"dr_{uuid.uuid4().hex[:8]}",
            failed_region_id=failed_region_id,
            target_region_id=target_region_id,
            status=DRIncidentStatus.COMPLETED # Fast-forward for synchronous mock
        )
        incident.completed_at = datetime.utcnow()
        cls._incidents[incident.id] = incident
        
        return incident
