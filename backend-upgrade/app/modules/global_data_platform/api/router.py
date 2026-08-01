from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.global_data_platform.domain.models import Entity, EntityType, Relationship, RelationshipType
from app.modules.global_data_platform.application.services import MergeEngine, RelationshipBuilder

router = APIRouter(prefix="/v1/intelligence", tags=["Global Data Intelligence"])

# In-memory mock database for the graph
_graph_nodes: Dict[str, Entity] = {}
_graph_edges: List[Relationship] = []

@router.post("/entities")
async def create_or_update_entity(payload: Dict[str, Any]) -> dict:
    """Ingest a fact from a specific provider and merge it into the Graph."""
    entity_id = payload.get("entity_id")
    entity_type_raw = payload.get("type", EntityType.COMPANY)
    entity_type = EntityType(entity_type_raw) if isinstance(entity_type_raw, str) else entity_type_raw
    provider = payload.get("provider_name")
    facts = payload.get("facts", {}) # Dict of field_name -> value
    
    # 1. Fetch or Create Node
    if entity_id not in _graph_nodes:
        _graph_nodes[entity_id] = Entity(id=entity_id, type=entity_type)
        
    entity = _graph_nodes[entity_id]
    
    # 2. Merge facts via Engine
    for field_name, value in facts.items():
        MergeEngine.assert_fact(entity, field_name, value, provider)
        
    return {"status": "merged", "entity_id": entity.id}

@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str) -> dict:
    """Fetch the resolved canonical entity."""
    entity = _graph_nodes.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    # Serialize canonical state
    canonical_state = {
        field_name: field_data.canonical_value 
        for field_name, field_data in entity.fields.items()
    }
    
    return {
        "id": entity.id,
        "type": entity.type.value,
        "data": canonical_state
    }

@router.get("/entities/{entity_id}/provenance")
async def get_entity_provenance(entity_id: str) -> dict:
    """Fetch the deep provenance and conflict history of an entity."""
    entity = _graph_nodes.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    history = {}
    for field_name, field_data in entity.fields.items():
        history[field_name] = {
            "canonical_value": field_data.canonical_value,
            "canonical_source": field_data.canonical_source,
            "history": [
                {
                    "value": p.value,
                    "provider": p.provider_name,
                    "confidence_score": p.confidence_score,
                    "timestamp": p.timestamp.isoformat()
                } for p in field_data.provenance_history
            ]
        }
        
    return {"id": entity.id, "provenance": history}

@router.post("/relationships")
async def create_relationship(payload: Dict[str, Any]) -> dict:
    """Establish a directed edge between two entities."""
    source_id = payload.get("source_id")
    target_id = payload.get("target_id")
    rel_type = RelationshipType(payload.get("relationship_type"))
    provider = payload.get("provider_name")
    
    edge = RelationshipBuilder.create_edge(source_id, target_id, rel_type, provider)
    _graph_edges.append(edge)
    
    return {"status": "created", "edge_id": edge.id}
