"""
Workspace Context Provider
Fetches workspace metadata, tier, and CRM status.
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.models import Workspace
from app.modules.copilot.application.providers.base import BaseContextProvider
from app.modules.copilot.domain.context import ContextCategory, ContextItem, ContextPriority
from app.modules.copilot.domain.entities import CopilotStateEntity


class WorkspaceContextProvider(BaseContextProvider):
    def __init__(self, db: Session):
        self.db = db

    @property
    def provider_name(self) -> str:
        return "workspace_provider"

    @property
    def category(self) -> ContextCategory:
        return ContextCategory.WORKSPACE

    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        ws = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not ws:
            return []

        crm_info = ws.crm_provider or "None connected"
        content = (
            f"Workspace Profile:\n"
            f"- Workspace Name: {ws.name}\n"
            f"- Subscription Tier: {ws.subscription_tier.upper()}\n"
            f"- Active CRM Provider: {crm_info}\n"
            f"- Monitored Company Limit: {ws.max_monitored_companies}"
        )

        item = ContextItem(
            category=ContextCategory.WORKSPACE,
            source_provider=self.provider_name,
            priority=ContextPriority.CRITICAL,
            content=content,
            metadata={
                "workspace_name": ws.name,
                "tier": ws.subscription_tier,
                "crm_provider": ws.crm_provider,
            },
        )
        return [item]
