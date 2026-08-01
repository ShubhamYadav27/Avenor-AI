import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.foundation_models.domain.models import (
    ModelVersion, ModelStatus, PredictionTarget, FeatureVector, 
    FeatureImportance, PredictionExplainability, RevenuePrediction
)

class ExplainabilityRequiredError(Exception):
    pass

class NoChampionModelError(Exception):
    pass

class ModelRegistry:
    """Governs the lifecycle and deployment status of all models."""
    
    # In-memory mock DB: target -> List[ModelVersion]
    _registry: Dict[PredictionTarget, List[ModelVersion]] = {}
    
    @classmethod
    def register_model(cls, target: PredictionTarget, version_tag: str, accuracy: float) -> ModelVersion:
        if target not in cls._registry:
            cls._registry[target] = []
            
        model = ModelVersion(
            id=f"mod_{uuid.uuid4().hex[:8]}",
            target=target,
            version_tag=version_tag,
            status=ModelStatus.CHALLENGER, # Always starts as Challenger
            accuracy_score=accuracy
        )
        cls._registry[target].append(model)
        return model
        
    @classmethod
    def promote_to_champion(cls, target: PredictionTarget, model_id: str) -> ModelVersion:
        """Promotes a model to Champion and automatically demotes the current Champion."""
        models = cls._registry.get(target, [])
        target_model = None
        
        # Find target model and demote others
        for m in models:
            if m.id == model_id:
                target_model = m
            elif m.status == ModelStatus.CHAMPION:
                m.status = ModelStatus.RETIRED
                
        if target_model:
            target_model.status = ModelStatus.CHAMPION
            return target_model
            
        raise ValueError("Model not found")

    @classmethod
    def get_champion(cls, target: PredictionTarget) -> ModelVersion:
        models = cls._registry.get(target, [])
        for m in models:
            if m.status == ModelStatus.CHAMPION:
                return m
        raise NoChampionModelError(f"No active Champion model for target {target.value}")

class FeatureExtractionEngine:
    """Standardizes inputs for the Inference Engine."""
    
    @staticmethod
    def extract_features(entity_id: str) -> FeatureVector:
        # Mocking feature extraction from the Graph/CRM
        return FeatureVector(
            entity_id=entity_id,
            features={
                "days_since_last_contact": 14.0,
                "decision_maker_engaged": 1.0,
                "competitor_mentioned": 0.0,
                "recent_funding_round": 1.0
            }
        )

class InferenceEngine:
    """Runs predictions and strictly enforces the Explainability Contract."""
    
    @staticmethod
    def _mock_model_execution(features: FeatureVector) -> tuple[float, float, Optional[PredictionExplainability]]:
        """Mocks a statistical model execution."""
        # Simple deterministic mock
        score = 0.85 if features.features.get("decision_maker_engaged") == 1.0 else 0.30
        confidence = 0.90
        
        explainability = PredictionExplainability(
            top_contributors=[
                FeatureImportance(feature_name="decision_maker_engaged", weight=0.65),
                FeatureImportance(feature_name="recent_funding_round", weight=0.20)
            ],
            supporting_evidence=[
                "CFO opened proposal 3 times in last 24 hours.",
                "Company raised $50M Series B last month."
            ]
        )
        return score, confidence, explainability

    @staticmethod
    def predict(entity_id: str, target: PredictionTarget) -> RevenuePrediction:
        champion_model = ModelRegistry.get_champion(target)
        features = FeatureExtractionEngine.extract_features(entity_id)
        
        score, confidence, explainability = InferenceEngine._mock_model_execution(features)
        
        # The strict architectural constraint: No explanation = No prediction
        if not explainability or not explainability.top_contributors:
            raise ExplainabilityRequiredError("Fatal: The model failed to provide structural explainability for its prediction.")
            
        return RevenuePrediction(
            entity_id=entity_id,
            target=target,
            score=score,
            confidence=confidence,
            explainability=explainability,
            model_version_used=champion_model.version_tag
        )
