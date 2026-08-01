"""
Feedback Collector (Phase 5.5.6)
Ingests explicit user feedback, text corrections, and CRM deal conversion outcomes.
"""
from typing import List, Optional
import uuid

from app.modules.copilot.domain.learning_entities import FeedbackEvent, OutcomeEvent
from app.modules.copilot.domain.learning_value_objects import FeedbackType


class FeedbackCollector:
    def __init__(self):
        self._feedback_store: List[FeedbackEvent] = []
        self._outcome_store: List[OutcomeEvent] = []

    def record_user_feedback(
        self,
        workspace_id: uuid.UUID,
        feedback_type: FeedbackType = FeedbackType.THUMBS_UP,
        rating: float = 1.0,
        thread_id: Optional[uuid.UUID] = None,
        message_id: Optional[uuid.UUID] = None,
        correction_text: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> FeedbackEvent:
        event = FeedbackEvent(
            workspace_id=workspace_id,
            thread_id=thread_id,
            message_id=message_id,
            feedback_type=feedback_type,
            rating=rating,
            correction_text=correction_text,
            user_id=user_id,
        )
        self._feedback_store.append(event)
        return event

    def record_crm_outcome(
        self,
        workspace_id: uuid.UUID,
        outcome_type: FeedbackType = FeedbackType.DEAL_WON,
        deal_id: Optional[str] = None,
        company_id: Optional[str] = None,
        amount_usd: float = 0.0,
        signal_ids_attributed: Optional[List[str]] = None,
    ) -> OutcomeEvent:
        event = OutcomeEvent(
            workspace_id=workspace_id,
            deal_id=deal_id,
            company_id=company_id,
            outcome_type=outcome_type,
            amount_usd=amount_usd,
            signal_ids_attributed=signal_ids_attributed or [],
        )
        self._outcome_store.append(event)
        return event

    def get_workspace_feedback(self, workspace_id: uuid.UUID) -> List[FeedbackEvent]:
        return [e for e in self._feedback_store if e.workspace_id == workspace_id]

    def get_workspace_outcomes(self, workspace_id: uuid.UUID) -> List[OutcomeEvent]:
        return [e for e in self._outcome_store if e.workspace_id == workspace_id]


feedback_collector = FeedbackCollector()
