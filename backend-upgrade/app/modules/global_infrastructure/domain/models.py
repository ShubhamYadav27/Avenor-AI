from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREM = "on_prem"

class RegionStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"

class RoutingStrategy(str, Enum):
    LATENCY_BASED = "latency_based"
    GEO_BASED = "geo_based"

class DRIncidentStatus(str, Enum):
    INITIATED = "initiated"
    DRAINING_TRAFFIC = "draining_traffic"
    REPLICATING_DATA = "replicating_data"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Region:
    """A physical deployment region in the global cloud."""
    id: str # e.g. "us-east-1"
    name: str # e.g. "US East (N. Virginia)"
    location: str # e.g. "North America"
    cloud_provider: CloudProvider
    status: RegionStatus
    current_latency_ms: float
    last_health_check_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DisasterRecoveryIncident:
    """A tracked event orchestrating the failover of a region."""
    id: str
    failed_region_id: str
    target_region_id: str
    status: DRIncidentStatus
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
