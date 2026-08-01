import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.ai_governance.domain.models import (
    AIDecision, RiskLevel, ApprovalStatus, HallucinationScore, AIAuditTrace
)

class HallucinationError(Exception):
    pass

class HallucinationDetectionEngine:
    """Evaluates AI output against factual grounding evidence."""
    
    @staticmethod
    def evaluate(output: str, evidence: List[str]) -> HallucinationScore:
        """
        Mock Hallucination Check. 
        If output mentions 'Acme' but it's not in the evidence, flag it.
        """
        is_hallucinated = False
        flagged = []
        score = 0.0
        
        # Simple mock rule for testing
        if "Acme" in output and not any("Acme" in ev for ev in evidence):
            is_hallucinated = True
            flagged.append("Acme")
            score = 0.95
            
        return HallucinationScore(score=score, is_hallucinated=is_hallucinated, flagged_segments=flagged)

class HumanApprovalEngine:
    """Manages the Human-in-the-loop (HITL) queues for high-risk decisions."""
    
    _queue: Dict[str, AIDecision] = {}
    
    @classmethod
    def enqueue(cls, decision: AIDecision):
        cls._queue[decision.id] = decision
        
    @classmethod
    def process_approval(cls, decision_id: str, reviewer_id: str, is_approved: bool) -> AIDecision:
        decision = cls._queue.get(decision_id)
        if not decision:
            raise ValueError("Decision not found in approval queue.")
            
        if decision.approval_status != ApprovalStatus.PENDING:
            raise ValueError("Decision is not pending approval.")
            
        decision.approval_status = ApprovalStatus.APPROVED if is_approved else ApprovalStatus.REJECTED
        decision.reviewed_by = reviewer_id
        decision.reviewed_at = datetime.utcnow()
        return decision

class DecisionGovernanceEngine:
    """The central gatekeeper for all AI predictions in AVENOR."""
    
    @classmethod
    def evaluate_decision(
        cls, 
        input_context: Dict[str, Any], 
        output_str: str, 
        evidence: List[str], 
        risk: RiskLevel
    ) -> AIDecision:
        
        # 1. Hallucination Check (Hard Block)
        hallucination = HallucinationDetectionEngine.evaluate(output_str, evidence)
        if hallucination.is_hallucinated:
            raise HallucinationError(f"AI Safety Block: Detected unsupported facts: {hallucination.flagged_segments}")
            
        # 2. Risk & HITL Routing
        status = ApprovalStatus.NOT_REQUIRED
        req_role = None
        
        if risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            status = ApprovalStatus.PENDING
            req_role = "Senior Analyst"
            
        # 3. Create Immutable Audit Record
        trace = AIAuditTrace("v2.1.0", "v1.0", ["feat_123"])
        decision = AIDecision(
            id=f"dec_{uuid.uuid4().hex[:8]}",
            input_context=input_context,
            output_prediction={"raw": output_str},
            reasoning_summary="Mock reasoning",
            confidence=0.85,
            risk_level=risk,
            hallucination_evaluation=hallucination,
            approval_status=status,
            audit_trace=trace,
            required_approver_role=req_role
        )
        
        # 4. Route to HITL if required
        if status == ApprovalStatus.PENDING:
            HumanApprovalEngine.enqueue(decision)
            
        return decision
