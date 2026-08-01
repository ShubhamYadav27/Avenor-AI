from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.feature_store.domain.models import FeatureType, FeatureStatus, FeatureLineage
from app.modules.feature_store.application.services import (
    FeatureRegistry, OnlineFeatureStore, FeatureNotFoundError
)

router = APIRouter(prefix="/v1/features", tags=["Enterprise Feature Store"])

@router.post("/catalog/register")
async def register_feature(payload: Dict[str, Any]) -> dict:
    """Register a newly engineered feature into the immutable catalog."""
    name = payload.get("name")
    f_type = FeatureType(payload.get("type"))
    version = payload.get("version")
    
    lineage_data = payload.get("lineage", {})
    lineage = FeatureLineage(
        source_system=lineage_data.get("source_system", "unknown"),
        source_fields=lineage_data.get("source_fields", []),
        transformation_logic=lineage_data.get("transformation_logic", "none"),
        owner=lineage_data.get("owner", "system")
    )
    
    feature = FeatureRegistry.register_feature(name, f_type, version, lineage)
    return {
        "feature_id": feature.id,
        "name": feature.name,
        "version": feature.version,
        "status": feature.status.value
    }

@router.post("/catalog/{name}/{version}/promote")
async def promote_feature(name: str, version: str) -> dict:
    """Promotes a feature to PRODUCTION."""
    try:
        feature = FeatureRegistry.update_status(name, version, FeatureStatus.PRODUCTION)
        return {
            "name": feature.name,
            "version": feature.version,
            "status": feature.status.value,
            "message": "Successfully promoted to Production"
        }
    except FeatureNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/online/fetch")
async def fetch_online_vector(payload: Dict[str, Any]) -> dict:
    """
    High-speed retrieval of a materialized feature vector for real-time inference.
    Typically called by the Foundation Models Inference Engine.
    """
    entity_id = payload.get("entity_id")
    requested_features = payload.get("features", [])
    
    vector = OnlineFeatureStore.get_feature_vector(entity_id, requested_features)
    
    return {
        "entity_id": entity_id,
        "vector": vector,
        "source": "online_store_cache",
        "retrieval_ms": 1.2 # Mocked latency
    }
