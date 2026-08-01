from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.foundation_models.domain.models import PredictionTarget, ModelStatus
from app.modules.foundation_models.application.services import (
    ModelRegistry, InferenceEngine, NoChampionModelError, ExplainabilityRequiredError
)

router = APIRouter(prefix="/v1/models", tags=["Foundation Models"])

@router.post("/registry/register")
async def register_model(payload: Dict[str, Any]) -> dict:
    """Register a newly trained model into the registry as a Challenger."""
    target = PredictionTarget(payload.get("target"))
    version = payload.get("version_tag")
    accuracy = payload.get("accuracy_score")
    
    model = ModelRegistry.register_model(target, version, accuracy)
    return {
        "model_id": model.id,
        "status": model.status.value,
        "version": model.version_tag
    }

@router.post("/registry/{model_id}/promote")
async def promote_model(model_id: str, payload: Dict[str, Any]) -> dict:
    """Promotes a Challenger to Champion."""
    target = PredictionTarget(payload.get("target"))
    
    try:
        model = ModelRegistry.promote_to_champion(target, model_id)
        return {
            "model_id": model.id,
            "status": model.status.value,
            "message": "Successfully promoted to Champion"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/predict/{target}/{entity_id}")
async def run_prediction(target: str, entity_id: str) -> dict:
    """
    Run inference for a specific target on a specific entity.
    Guarantees explainability is included in the response.
    """
    prediction_target = PredictionTarget(target)
    
    try:
        prediction = InferenceEngine.predict(entity_id, prediction_target)
        
        # Serialize the explanation payload
        explainability_payload = {
            "top_contributors": [
                {"feature": f.feature_name, "weight": f.weight} 
                for f in prediction.explainability.top_contributors
            ],
            "supporting_evidence": prediction.explainability.supporting_evidence
        }
        
        return {
            "entity_id": prediction.entity_id,
            "target": prediction.target.value,
            "model_version": prediction.model_version_used,
            "prediction": {
                "score": prediction.score,
                "confidence": prediction.confidence
            },
            "explainability": explainability_payload
        }
        
    except NoChampionModelError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExplainabilityRequiredError as e:
        raise HTTPException(status_code=500, detail=str(e))
