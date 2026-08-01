from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class EntityType(str, Enum):
    COMPANY = "company"
    CONTACT = "contact"
    TECHNOLOGY = "technology"
    SIGNAL = "signal"

class RelationshipType(str, Enum):
    EMPLOYS = "employs"
    USES_TECH = "uses_tech"
    COMPETES_WITH = "competes_with"
    SUBSIDIARY_OF = "subsidiary_of"

@dataclass
class SourceReliability:
    """Pre-computed trust score for a specific data provider (0.0 to 1.0)."""
    provider_name: str
    base_trust_score: float

@dataclass
class Provenance:
    """An immutable assertion of a fact by a specific source at a specific time."""
    provider_name: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0 # Will be computed by ScoringEngine

@dataclass
class EntityField:
    """A field on an entity (e.g. 'revenue') containing the canonical value and its history."""
    field_name: str
    canonical_value: Any = None
    canonical_source: Optional[str] = None
    provenance_history: List[Provenance] = field(default_factory=list)

@dataclass
class Entity:
    """A canonical node in the Knowledge Graph."""
    id: str
    type: EntityType
    fields: Dict[str, EntityField] = field(default_factory=dict)
    global_trust_score: float = 0.0 # Composite score of all its canonical fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Relationship:
    """A directed edge in the Knowledge Graph."""
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    provenance: Provenance
