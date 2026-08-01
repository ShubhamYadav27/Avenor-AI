from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class FeatureType(str, Enum):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    EMBEDDING = "embedding"
    TIME_SERIES = "time_series"

class FeatureStatus(str, Enum):
    DRAFT = "draft"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class FeatureHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"

@dataclass
class FeatureLineage:
    """The cryptographic map of where a feature came from."""
    source_system: str # e.g. "GlobalDataPlatform", "CRMSync"
    source_fields: List[str]
    transformation_logic: str # e.g. "90-day rolling average"
    owner: str

@dataclass
class FeatureHealth:
    """Real-time statistics tracking data quality."""
    drift_score: float # 0.0 to 1.0
    null_percentage: float # 0.0 to 100.0
    status: FeatureHealthStatus
    last_validated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureDefinition:
    """The immutable definition of a feature."""
    id: str
    name: str # e.g. "decision_maker_engaged_90d"
    type: FeatureType
    version: str # e.g. "v1.0"
    status: FeatureStatus
    lineage: FeatureLineage
    health: FeatureHealth
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureValue:
    """The actual materialized value for a specific entity."""
    entity_id: str
    feature_id: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
