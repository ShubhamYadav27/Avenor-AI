"""
Context Provider Registry
Dynamic registry for registering and resolving context providers by intent and category.
"""
from typing import List
from sqlalchemy.orm import Session

from app.modules.copilot.application.providers.company_provider import CompanyContextProvider
from app.modules.copilot.application.providers.crm_provider import CrmContextProvider
from app.modules.copilot.application.providers.email_provider import EmailContextProvider
from app.modules.copilot.application.providers.research_provider import ResearchContextProvider
from app.modules.copilot.application.providers.sales_coach_provider import SalesCoachContextProvider
from app.modules.copilot.application.providers.signal_provider import SignalContextProvider
from app.modules.copilot.application.providers.workspace_provider import WorkspaceContextProvider
from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.interfaces import IContextProvider


class ContextProviderRegistry:
    def __init__(self):
        self._providers: List[IContextProvider] = []

    def register_provider(self, provider: IContextProvider) -> None:
        self._providers.append(provider)

    def resolve_providers(self, intent: ContextIntent) -> List[IContextProvider]:
        """Returns all context providers that support the specified query intent."""
        return [p for p in self._providers if p.supports_intent(intent)]

    def create_default_registry(self, db: Session) -> "ContextProviderRegistry":
        registry = ContextProviderRegistry()
        registry.register_provider(WorkspaceContextProvider(db))
        registry.register_provider(CompanyContextProvider(db))
        registry.register_provider(SignalContextProvider(db))
        registry.register_provider(CrmContextProvider(db))
        registry.register_provider(ResearchContextProvider(db))
        registry.register_provider(SalesCoachContextProvider(db))
        registry.register_provider(EmailContextProvider(db))
        return registry


context_provider_registry = ContextProviderRegistry()
