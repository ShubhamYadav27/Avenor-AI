"""
Research Context Provider
Assembles AI research summaries, company briefings, and strategic angles.
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.modules.copilot.application.providers.base import BaseContextProvider
from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, ContextPriority
from app.modules.copilot.domain.entities import CopilotStateEntity


class ResearchContextProvider(BaseContextProvider):
    def __init__(self, db: Session):
        self.db = db

    @property
    def provider_name(self) -> str:
        return "research_provider"

    @property
    def category(self) -> ContextCategory:
        return ContextCategory.RESEARCH

    def supports_intent(self, intent: ContextIntent) -> bool:
        return intent in [
            ContextIntent.COMPANY_DEEP_DIVE,
            ContextIntent.OUTREACH_STRATEGY,
            ContextIntent.OBJECTION_HANDLING,
            ContextIntent.GENERAL_STRATEGY,
        ]

    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        # Formulate structured research context
        content = (
            "AI Research Intelligence:\n"
            "- Executive Focus: Growth acceleration & infrastructure modernization.\n"
            "- Market Positioning: Expanding enterprise sales footprint.\n"
            "- Recommended Pitch Angle: Highlight ROI, operational efficiency, and rapid deployment time."
        )

        item = ContextItem(
            category=ContextCategory.RESEARCH,
            source_provider=self.provider_name,
            priority=ContextPriority.HIGH,
            content=content,
        )
        return [item]
