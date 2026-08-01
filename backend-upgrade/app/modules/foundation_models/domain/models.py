from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class ModelStatus(str, Enum):
    CHAMPION = "champion" # The active production model
    CHALLENGER = "challenger" # A model being evaluated against the champion
    RETIRED = "retired"

class PredictionTarget(str, Enum):
    DEAL_RISK = "deal_risk"
    BUYING_WINDOW = "buying_window"
    RENEWAL_RISK = "renewal_risk"
    EXPANSION_POTENTIAL = "expansion_potential"

@dataclass
class ModelVersion:
    """Metadata tracking the lifecycle of a trained AI model."""
    id: str
    target: PredictionTarget
    version_tag: str
    status: ModelStatus
    accuracy_score: float # e.g. 0.92 (F1 score)
    deployed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureVector:
    """Standardized inputs extracted from CRM and Graph for inference."""
    entity_id: str
    features: Dict[str, float] # e.g. {"days_since_last_contact": 12.0, "executive_hiring_growth": 0.8}
    extracted_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeatureImportance:
    """The weight of a specific feature in a prediction."""
    feature_name: str
    weight: float # Between -1.0 and 1.0 (negative means it lowered the score, positive means it raised it)

@dataclass
class PredictionExplainability:
    """The enterprise requirement: No prediction without evidence."""
    top_contributors: List[FeatureImportance]
    supporting_evidence: List[str] # Human readable evidence strings

@dataclass
class RevenuePrediction:
    """The final output payload from the Inference Engine."""
    entity_id: str
    target: PredictionTarget
    score: float # The predicted probability (0.0 to 1.0)
    confidence: float # How confident the model is in this specific prediction
    explainability: PredictionExplainability
    model_version_used: str
    predicted_at: datetime = field(default_factory=datetime.utcnow)
