import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.feature_store.domain.models import (
    FeatureDefinition, FeatureStatus, FeatureType, FeatureLineage, 
    FeatureHealth, FeatureHealthStatus, FeatureValue
)

class FeatureNotFoundError(Exception):
    pass

class FeatureRegistry:
    """Manages the lifecycle and catalog of all AI features."""
    
    # In-memory mock DB: feature_name -> Dict[version, FeatureDefinition]
    _catalog: Dict[str, Dict[str, FeatureDefinition]] = {}
    
    @classmethod
    def register_feature(cls, name: str, f_type: FeatureType, version: str, lineage: FeatureLineage) -> FeatureDefinition:
        if name not in cls._catalog:
            cls._catalog[name] = {}
            
        initial_health = FeatureHealth(
            drift_score=0.0,
            null_percentage=0.0,
            status=FeatureHealthStatus.HEALTHY
        )
            
        feature = FeatureDefinition(
            id=f"feat_{uuid.uuid4().hex[:8]}",
            name=name,
            type=f_type,
            version=version,
            status=FeatureStatus.DRAFT,
            lineage=lineage,
            health=initial_health
        )
        
        cls._catalog[name][version] = feature
        return feature
        
    @classmethod
    def update_status(cls, name: str, version: str, new_status: FeatureStatus) -> FeatureDefinition:
        feature = cls._catalog.get(name, {}).get(version)
        if not feature:
            raise FeatureNotFoundError(f"Feature {name} v{version} not found")
            
        # If promoting to Production, demote other production versions to Deprecated
        if new_status == FeatureStatus.PRODUCTION:
            for v, f in cls._catalog[name].items():
                if f.status == FeatureStatus.PRODUCTION and v != version:
                    f.status = FeatureStatus.DEPRECATED
                    
        feature.status = new_status
        return feature
        
    @classmethod
    def get_feature(cls, name: str, version: str) -> FeatureDefinition:
        feature = cls._catalog.get(name, {}).get(version)
        if not feature:
            raise FeatureNotFoundError()
        return feature

class OnlineFeatureStore:
    """High-speed low-latency feature retrieval for inference engines (Mocking Redis)."""
    
    # Mock Redis: entity_id -> {feature_name: FeatureValue}
    _cache: Dict[str, Dict[str, FeatureValue]] = {}
    
    @classmethod
    def ingest_value(cls, value: FeatureValue, feature_name: str):
        if value.entity_id not in cls._cache:
            cls._cache[value.entity_id] = {}
        cls._cache[value.entity_id][feature_name] = value

    @classmethod
    def get_feature_vector(cls, entity_id: str, requested_features: List[str]) -> Dict[str, Any]:
        """Retrieves an assembled vector for real-time inference in < 10ms."""
        entity_data = cls._cache.get(entity_id, {})
        vector = {}
        
        for feature_name in requested_features:
            val = entity_data.get(feature_name)
            # If missing, we must impute or return None. For now return None.
            vector[feature_name] = val.value if val else None
            
        return vector

class FeatureDriftMonitor:
    """Continuously monitors data quality to detect model decay."""
    
    @staticmethod
    def calculate_health(feature: FeatureDefinition, null_count: int, total_count: int) -> FeatureHealth:
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        
        status = FeatureHealthStatus.HEALTHY
        if null_percentage > 20.0:
            status = FeatureHealthStatus.DEGRADED
        if null_percentage > 50.0:
            status = FeatureHealthStatus.CRITICAL
            
        feature.health.null_percentage = null_percentage
        feature.health.status = status
        feature.health.last_validated_at = datetime.utcnow()
        
        return feature.health
