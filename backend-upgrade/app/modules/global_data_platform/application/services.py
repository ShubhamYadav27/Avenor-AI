import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.modules.global_data_platform.domain.models import (
    Entity, EntityField, Provenance, SourceReliability, Relationship, RelationshipType
)

# Pre-configured Data Providers and their base trust (0.0 to 1.0)
_PROVIDERS = {
    "salesforce_crm": SourceReliability(provider_name="salesforce_crm", base_trust_score=0.95), # Customer CRM is high trust
    "clearbit_api": SourceReliability(provider_name="clearbit_api", base_trust_score=0.85),
    "public_web_scraper": SourceReliability(provider_name="public_web_scraper", base_trust_score=0.40)
}

class ScoringEngine:
    """Calculates dynamic trust and confidence scores for data assertions."""
    
    @staticmethod
    def compute_provenance_confidence(provider_name: str, timestamp: datetime) -> float:
        """
        Confidence = Base Trust Score * Freshness Decay
        Data loses 1% of its trust score every 30 days.
        """
        provider = _PROVIDERS.get(provider_name)
        if not provider:
            return 0.1 # Unknown source penalty
            
        base_trust = provider.base_trust_score
        
        # Calculate freshness decay (1% penalty per 30 days)
        age_days = (datetime.utcnow() - timestamp).days
        decay_factor = max(0.0, age_days / 30 * 0.01)
        
        final_confidence = max(0.0, base_trust - decay_factor)
        return round(final_confidence, 3)

class MergeEngine:
    """Resolves conflicts and maintains canonical entity state."""
    
    @staticmethod
    def assert_fact(entity: Entity, field_name: str, value: Any, provider_name: str) -> None:
        """Asserts a new fact onto an Entity. Resolves conflict if it already exists."""
        
        timestamp = datetime.utcnow()
        confidence = ScoringEngine.compute_provenance_confidence(provider_name, timestamp)
        
        new_provenance = Provenance(
            provider_name=provider_name,
            value=value,
            timestamp=timestamp,
            confidence_score=confidence
        )
        
        if field_name not in entity.fields:
            # Field doesn't exist yet, simply set it as canonical
            entity.fields[field_name] = EntityField(
                field_name=field_name,
                canonical_value=value,
                canonical_source=provider_name,
                provenance_history=[new_provenance]
            )
        else:
            # Conflict Resolution
            field = entity.fields[field_name]
            field.provenance_history.append(new_provenance)
            
            # Recalculate the winning value (Highest Confidence Score wins)
            # In a real system, this might also evaluate majority consensus, but we use strict confidence here.
            winning_provenance = max(field.provenance_history, key=lambda p: p.confidence_score)
            
            field.canonical_value = winning_provenance.value
            field.canonical_source = winning_provenance.provider_name
            
        entity.updated_at = datetime.utcnow()

class RelationshipBuilder:
    """Forms graph edges between entities."""
    
    @staticmethod
    def create_edge(source_id: str, target_id: str, rel_type: RelationshipType, provider_name: str) -> Relationship:
        return Relationship(
            id=f"rel_{uuid.uuid4().hex[:8]}",
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=rel_type,
            provenance=Provenance(
                provider_name=provider_name,
                value=True,
                confidence_score=ScoringEngine.compute_provenance_confidence(provider_name, datetime.utcnow())
            )
        )
