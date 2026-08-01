from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.ai_governance.domain.models import RiskLevel, ApprovalStatus
from app.modules.ai_governance.application.services import (
    DecisionGovernanceEngine, HumanApprovalEngine, HallucinationError
)

router = APIRouter(prefix="/v1/governance", tags=["AI Governance"])

@router.post("/decisions/validate")
async def validate_ai_decision(payload: Dict[str, Any]) -> dict:
    """Validates an AI output for hallucinations and routes to HITL if high risk."""
    input_context = payload.get("input", {})
    output_str = payload.get("output", "")
    evidence = payload.get("evidence", [])
    
    try:
        risk_level = RiskLevel(payload.get("risk_level", "low"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid risk level.")
    
    try:
        decision = DecisionGovernanceEngine.evaluate_decision(
            input_context, output_str, evidence, risk_level
        )
    except HallucinationError as e:
        # Strictly block the AI response
        raise HTTPException(status_code=422, detail=str(e))
        
    return {
        "decision_id": decision.id,
        "approval_status": decision.approval_status.value,
        "message": "Routed to Human Queue" if decision.approval_status == ApprovalStatus.PENDING else "Auto-approved"
    }

@router.post("/approvals/{decision_id}/process")
async def process_human_approval(decision_id: str, payload: Dict[str, Any]) -> dict:
    """Human-in-the-loop endpoint to approve or reject a pending decision."""
    reviewer_id = payload.get("reviewer_id")
    is_approved = payload.get("is_approved", False)
    
    try:
        decision = HumanApprovalEngine.process_approval(decision_id, reviewer_id, is_approved)
        return {
            "decision_id": decision.id,
            "new_status": decision.approval_status.value,
            "reviewed_by": decision.reviewed_by
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
