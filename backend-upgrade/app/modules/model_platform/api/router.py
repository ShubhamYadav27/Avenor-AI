from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.model_platform.domain.models import EvaluationMetrics, TrafficRule, DeploymentStrategy
from app.modules.model_platform.application.services import (
    ExperimentTracker, EvaluationEngine, DeploymentManager, FairnessViolationError, TrafficConfigurationError
)

router = APIRouter(prefix="/v1/mlops", tags=["AI Model Platform"])

@router.post("/experiments/run")
async def log_experiment_run(payload: Dict[str, Any]) -> dict:
    """Logs an ML run with its evaluation metrics."""
    exp_name = payload.get("experiment_name", "Default")
    model_id = payload.get("model_id")
    params = payload.get("hyperparameters", {})
    
    raw_metrics = payload.get("metrics", {})
    metrics = EvaluationMetrics(
        accuracy=raw_metrics.get("accuracy", 0.0),
        f1_score=raw_metrics.get("f1_score", 0.0),
        roc_auc=raw_metrics.get("roc_auc", 0.0),
        bias_score=raw_metrics.get("bias_score", 0.0),
        avg_latency_ms=raw_metrics.get("latency", 0.0)
    )
    
    # Strictly evaluate fairness before accepting the run
    try:
        EvaluationEngine.evaluate_fairness(metrics)
    except FairnessViolationError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    exp = ExperimentTracker.create_experiment(exp_name, "Evaluation Run", "ml_team")
    run = ExperimentTracker.log_run(exp.id, model_id, params, metrics)
    
    return {
        "run_id": run.id,
        "status": "logged_and_verified"
    }

@router.post("/deployments/canary")
async def deploy_canary(payload: Dict[str, Any]) -> dict:
    """Configures the traffic router for a Canary or Shadow deployment."""
    target = payload.get("target") # e.g. "deal_risk_prediction"
    raw_rules = payload.get("rules", [])
    
    rules = []
    for r in raw_rules:
        rules.append(TrafficRule(
            model_id=r["model_id"],
            percentage=r["percentage"],
            strategy=DeploymentStrategy(r["strategy"])
        ))
        
    try:
        DeploymentManager.set_routing(target, rules)
        return {"status": "traffic_updated", "rules_applied": len(rules)}
    except TrafficConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
