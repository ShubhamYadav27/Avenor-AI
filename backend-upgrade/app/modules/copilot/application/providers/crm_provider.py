"""
CRM Context Provider
Queries CRM deals (opportunities), deal stages, and key lead/contact profiles.
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.models import Opportunity, Lead
from app.modules.copilot.application.providers.base import BaseContextProvider
from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, ContextPriority
from app.modules.copilot.domain.entities import CopilotStateEntity


class CrmContextProvider(BaseContextProvider):
    def __init__(self, db: Session):
        self.db = db

    @property
    def provider_name(self) -> str:
        return "crm_provider"

    @property
    def category(self) -> ContextCategory:
        return ContextCategory.CRM

    def supports_intent(self, intent: ContextIntent) -> bool:
        return intent in [
            ContextIntent.CRM_PIPELINE,
            ContextIntent.OUTREACH_STRATEGY,
            ContextIntent.COMPANY_DEEP_DIVE,
            ContextIntent.GENERAL_STRATEGY,
        ]

    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        items: List[ContextItem] = []

        # Deals / Opportunities
        deals = (
            self.db.query(Opportunity)
            .filter(Opportunity.workspace_id == workspace_id)
            .order_by(Opportunity.updated_at.desc())
            .limit(5)
            .all()
        )

        if deals:
            lines = ["Active CRM Opportunities:"]
            for d in deals:
                amt = f"${d.amount_usd:,.2f}" if d.amount_usd else "N/A"
                lines.append(f"• Deal: '{d.name}' — Stage: {d.stage or 'Open'} — Value: {amt}")

            items.append(
                ContextItem(
                    category=ContextCategory.CRM,
                    source_provider=self.provider_name,
                    priority=ContextPriority.HIGH,
                    content="\n".join(lines),
                    metadata={"deals_count": len(deals)},
                )
            )

        # Contacts / Leads
        leads = (
            self.db.query(Lead)
            .filter(Lead.workspace_id == workspace_id)
            .order_by(Lead.updated_at.desc())
            .limit(5)
            .all()
        )

        if leads:
            lines = ["Key CRM Contacts & Leads:"]
            for l in leads:
                name = l.full_name or f"{l.first_name or ''} {l.last_name or ''}".strip() or "Unnamed Contact"
                lines.append(f"• {name} — Title: {l.title or 'N/A'} — Company: {l.company_name or 'N/A'}")

            items.append(
                ContextItem(
                    category=ContextCategory.CRM,
                    source_provider=self.provider_name,
                    priority=ContextPriority.MEDIUM,
                    content="\n".join(lines),
                    metadata={"leads_count": len(leads)},
                )
            )

        return items
