from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class DeploymentStrategy(str, Enum):
    DIRECT = "direct" # Promoted immediately to Champion 100%
    SHADOW = "shadow" # Receives traffic, computes inferences in background, does not return to user
    CANARY = "canary" # Receives X% of live traffic

@dataclass
class EvaluationMetrics:
    """Standardized metrics required for any model promotion."""
    accuracy: float
    f1_score: float
    roc_auc: float
    bias_score: float # 0.0 is perfect fairness, > 0.1 is failing
    avg_latency_ms: float

@dataclass
class Experiment:
    """A logical grouping of ML runs (e.g. 'Add graph features to deal risk')."""
    id: str
    name: str
    objective: str
    owner: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Run:
    """A specific training/evaluation execution (like an MLflow Run)."""
    id: str
    experiment_id: str
    model_id: str
    hyperparameters: Dict[str, Any]
    metrics: Optional[EvaluationMetrics] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrafficRule:
    """Defines how live traffic is routed to a specific model."""
    model_id: str
    percentage: int # 0 to 100
    strategy: DeploymentStrategy
