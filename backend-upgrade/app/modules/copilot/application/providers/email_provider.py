"""
Email Context Provider
Queries previously generated email templates and outreach history.
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.modules.copilot.application.providers.base import BaseContextProvider
from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, ContextPriority
from app.modules.copilot.domain.entities import CopilotStateEntity


class EmailContextProvider(BaseContextProvider):
    def __init__(self, db: Session):
        self.db = db

    @property
    def provider_name(self) -> str:
        return "email_provider"

    @property
    def category(self) -> ContextCategory:
        return ContextCategory.EMAIL

    def supports_intent(self, intent: ContextIntent) -> bool:
        return intent in [
            ContextIntent.OUTREACH_STRATEGY,
            ContextIntent.GENERAL_STRATEGY,
        ]

    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        content = (
            "Email Outreach Guidelines:\n"
            "- Subject Line Pattern: Personalized trigger-based subject lines (< 6 words).\n"
            "- Tone: Concierge executive strategist tone, avoid aggressive sales pushes.\n"
            "- Call to Action: Low friction invitation (e.g. 'Open to reviewing a 2-minute overview?')."
        )

        item = ContextItem(
            category=ContextCategory.EMAIL,
            source_provider=self.provider_name,
            priority=ContextPriority.MEDIUM,
            content=content,
        )
        return [item]
