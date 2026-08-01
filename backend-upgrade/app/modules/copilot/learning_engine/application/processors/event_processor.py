"""
Event Processor (Phase 5.5.6)
Queues, validates, and normalizes incoming feedback events and deal conversion outcomes.
"""
from typing import List, Tuple

from app.modules.copilot.domain.learning_entities import FeedbackEvent, OutcomeEvent


class EventProcessor:
    def process_pending_events(
        self,
        feedback_events: List[FeedbackEvent],
        outcome_events: List[OutcomeEvent],
    ) -> Tuple[List[FeedbackEvent], List[OutcomeEvent]]:
        valid_feedback = [e for e in feedback_events if -1.0 <= e.rating <= 1.0]
        valid_outcomes = [e for e in outcome_events if e.amount_usd >= 0.0]
        return valid_feedback, valid_outcomes


event_processor = EventProcessor()
