"""
Company Context Provider
Queries monitored target accounts, company status, and domain information.
"""
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.models import Company
from app.modules.copilot.application.providers.base import BaseContextProvider
from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, ContextPriority
from app.modules.copilot.domain.entities import CopilotStateEntity


class CompanyContextProvider(BaseContextProvider):
    def __init__(self, db: Session):
        self.db = db

    @property
    def provider_name(self) -> str:
        return "company_provider"

    @property
    def category(self) -> ContextCategory:
        return ContextCategory.COMPANY

    def supports_intent(self, intent: ContextIntent) -> bool:
        return intent in [
            ContextIntent.COMPANY_DEEP_DIVE,
            ContextIntent.OUTREACH_STRATEGY,
            ContextIntent.BUYING_SIGNALS,
            ContextIntent.GENERAL_STRATEGY,
        ]

    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        items: List[ContextItem] = []
        
        # If thread state points to a specific company ID
        if state and state.current_company_id:
            company = (
                self.db.query(Company)
                .filter(Company.id == state.current_company_id, Company.workspace_id == workspace_id)
                .first()
            )
            if company:
                content = (
                    f"Active Target Company Profile:\n"
                    f"- Company Name: {company.name}\n"
                    f"- Domain: {company.domain or 'N/A'}\n"
                    f"- Status: {company.status or 'monitoring'}\n"
                    f"- Industry: {company.industry or 'Technology'}\n"
                    f"- Employee Count: {company.employee_count or 'Unknown'}\n"
                    f"- Location: {company.city or ''}, {company.country or ''}\n"
                    f"- ICP Score: {company.icp_score if hasattr(company, 'icp_score') else 'N/A'}"
                )
                items.append(
                    ContextItem(
                        category=ContextCategory.COMPANY,
                        source_provider=self.provider_name,
                        priority=ContextPriority.HIGH,
                        content=content,
                        metadata={"company_id": str(company.id), "name": company.name},
                    )
                )
                return items

        # Fallback: Query top 5 active/monitored companies in workspace
        companies = (
            self.db.query(Company)
            .filter(Company.workspace_id == workspace_id)
            .order_by(Company.updated_at.desc())
            .limit(5)
            .all()
        )

        if not companies:
            return items

        summary_lines = ["High-Priority Target Accounts:"]
        for c in companies:
            summary_lines.append(f"• {c.name} ({c.domain or 'no domain'}) — Status: {c.status or 'monitoring'}")

        items.append(
            ContextItem(
                category=ContextCategory.COMPANY,
                source_provider=self.provider_name,
                priority=ContextPriority.MEDIUM,
                content="\n".join(summary_lines),
                metadata={"total_companies": len(companies)},
            )
        )
        return items
