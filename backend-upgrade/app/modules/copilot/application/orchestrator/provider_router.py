"""
Provider Router
Manages provider selection, fallback chains, retry strategy, and capability resolution.
Decoupled from ProviderFactory.
"""
from typing import List, Tuple
from app.modules.copilot.config import copilot_settings
from app.modules.copilot.domain.interfaces import ILLMProviderAdapter
from app.modules.copilot.infrastructure.adapters.factory import provider_factory
from app.modules.copilot.infrastructure.registry.model_registry import model_registry


class ProviderRouter:
    def __init__(self):
        self.factory = provider_factory
        self.registry = model_registry

    def resolve_provider_chain(
        self, preferred_provider: str | None = None, preferred_model: str | None = None
    ) -> List[Tuple[str, str]]:
        """
        Returns an ordered fallback list of (provider_name, model_name) tuples.
        Example: [("gemini", "gemini-1.5-pro"), ("openai", "gpt-4o"), ("mock", "mock-model")]
        """
        primary_provider = (preferred_provider or copilot_settings.llm.default_provider).lower()
        fallback_provider = copilot_settings.llm.fallback_provider.lower()
        primary_model = preferred_model or copilot_settings.llm.default_model

        chain = []
        # Primary
        chain.append((primary_provider, primary_model))

        # Secondary fallback
        if fallback_provider != primary_provider:
            fallback_model = "gpt-4o" if fallback_provider == "openai" else "gemini-1.5-flash"
            chain.append((fallback_provider, fallback_model))

        # Ultimate mock fallback for absolute reliability
        if ("mock", "mock-model") not in chain:
            chain.append(("mock", "mock-model"))

        return chain

    def get_adapter(self, provider_name: str) -> ILLMProviderAdapter:
        return self.factory.create_provider(provider_name)


provider_router = ProviderRouter()
