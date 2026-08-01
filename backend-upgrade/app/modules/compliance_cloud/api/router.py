from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.compliance_cloud.domain.models import (
    PrivacyRequestType, ComplianceFramework, DataClassification
)
from app.modules.compliance_cloud.application.services import (
    PrivacyManager, ComplianceAuditEngine, DataClassificationEngine
)

router = APIRouter(prefix="/v1/compliance", tags=["Enterprise Compliance"])

@router.post("/privacy-requests")
async def submit_privacy_request(payload: Dict[str, Any]) -> dict:
    """Submit a GDPR/CCPA request (e.g. Right to Erasure)."""
    user_id = payload.get("user_id")
    req_type = PrivacyRequestType(payload.get("request_type"))
    
    req = PrivacyManager.submit_request(user_id, req_type)
    return {
        "request_id": req.id,
        "status": req.status.value,
        "message": "Privacy request received and queued for legal processing."
    }

@router.post("/privacy-requests/{request_id}/execute")
async def execute_privacy_request(request_id: str) -> dict:
    """Administratively execute an approved Erasure request."""
    try:
        req = PrivacyManager.process_erasure(request_id)
        return {
            "request_id": req.id,
            "status": req.status.value,
            "message": "Erasure cascade completed across all datastores."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports/{framework}")
async def generate_compliance_report(framework: str) -> dict:
    """Generate a real-time Readiness Score (e.g. for SOC2)."""
    try:
        fw = ComplianceFramework(framework.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid framework.")
        
    report = ComplianceAuditEngine.generate_readiness_report(fw)
    return report

@router.get("/classification/{level}/policy")
async def get_retention_policy(level: str) -> dict:
    """Get the active retention limits for a data classification level."""
    try:
        classification = DataClassification(level.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid classification level.")
        
    policy = DataClassificationEngine.get_policy(classification)
    return {
        "classification": policy.classification.value,
        "ttl_days": policy.ttl_days,
        "is_legal_hold": policy.is_legal_hold
    }
