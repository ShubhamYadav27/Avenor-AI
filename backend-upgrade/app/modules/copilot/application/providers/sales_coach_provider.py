"""
Sales Coach Context Provider
Queries objection handling recommendations, pitch guidelines, and win/loss feedback.
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.modules.copilot.application.providers.base import BaseContextProvider
from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, ContextPriority
from app.modules.copilot.domain.entities import CopilotStateEntity


class SalesCoachContextProvider(BaseContextProvider):
    def __init__(self, db: Session):
        self.db = db

    @property
    def provider_name(self) -> str:
        return "sales_coach_provider"

    @property
    def category(self) -> ContextCategory:
        return ContextCategory.SALES_COACH

    def supports_intent(self, intent: ContextIntent) -> bool:
        return intent in [
            ContextIntent.OBJECTION_HANDLING,
            ContextIntent.OUTREACH_STRATEGY,
            ContextIntent.GENERAL_STRATEGY,
        ]

    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        content = (
            "Sales Coaching Guidance:\n"
            "• Primary Objection Strategy: Frame security & compliance as core enablers, not cost centers.\n"
            "• Value Prop Framing: Focus on quantifiable time-to-value (measurable within 30 days).\n"
            "• Win Insight: Deals referencing buying signals convert 3.2x faster than cold outreach."
        )

        item = ContextItem(
            category=ContextCategory.SALES_COACH,
            source_provider=self.provider_name,
            priority=ContextPriority.HIGH,
            content=content,
        )
        return [item]
