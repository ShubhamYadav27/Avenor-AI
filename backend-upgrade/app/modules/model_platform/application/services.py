import uuid
from typing import List, Dict, Any, Optional

from app.modules.model_platform.domain.models import (
    Experiment, Run, EvaluationMetrics, DeploymentStrategy, TrafficRule
)

class FairnessViolationError(Exception):
    """Raised when a model fails bias evaluation."""
    pass

class TrafficConfigurationError(Exception):
    pass

class ExperimentTracker:
    """Central MLOps tracking (analogous to MLflow)."""
    
    _experiments: Dict[str, Experiment] = {}
    _runs: Dict[str, Run] = {}
    
    @classmethod
    def create_experiment(cls, name: str, objective: str, owner: str) -> Experiment:
        exp = Experiment(id=f"exp_{uuid.uuid4().hex[:8]}", name=name, objective=objective, owner=owner)
        cls._experiments[exp.id] = exp
        return exp
        
    @classmethod
    def log_run(cls, exp_id: str, model_id: str, params: Dict[str, Any], metrics: EvaluationMetrics) -> Run:
        run = Run(
            id=f"run_{uuid.uuid4().hex[:8]}",
            experiment_id=exp_id,
            model_id=model_id,
            hyperparameters=params,
            metrics=metrics
        )
        cls._runs[run.id] = run
        return run

class EvaluationEngine:
    """Strict gates for model evaluation."""
    
    @staticmethod
    def evaluate_fairness(metrics: EvaluationMetrics) -> bool:
        """
        Enforces AI fairness. Bias score > 0.1 indicates statistical bias 
        against a protected cohort (e.g. company size, region).
        """
        if metrics.bias_score > 0.10:
            raise FairnessViolationError(f"Model rejected: Bias score {metrics.bias_score} exceeds strict 0.10 threshold.")
        return True

class DeploymentManager:
    """Manages the API Gateway traffic router for models."""
    
    # Target endpoint -> List[TrafficRule]
    _routing_table: Dict[str, List[TrafficRule]] = {}
    
    @classmethod
    def set_routing(cls, target: str, rules: List[TrafficRule]):
        """Configures the traffic split for Canary / Shadow testing."""
        live_traffic = sum(rule.percentage for rule in rules if rule.strategy != DeploymentStrategy.SHADOW)
        
        if live_traffic != 100:
            raise TrafficConfigurationError(f"Live traffic rules must sum to 100%. Got {live_traffic}%")
            
        cls._routing_table[target] = rules
        
    @classmethod
    def get_routing(cls, target: str) -> List[TrafficRule]:
        return cls._routing_table.get(target, [])
