"""
Provider Factory
Responsible strictly for instantiating LLM provider adapters.
"""
from typing import Dict, Type
from app.modules.copilot.domain.interfaces import ILLMProviderAdapter
from app.modules.copilot.infrastructure.adapters.gemini_adapter import GeminiAdapter
from app.modules.copilot.infrastructure.adapters.mock_adapter import MockLLMAdapter
from app.modules.copilot.infrastructure.adapters.openai_adapter import OpenAIAdapter


class ProviderFactory:
    def __init__(self):
        self._registry: Dict[str, Type[ILLMProviderAdapter]] = {
            "gemini": GeminiAdapter,
            "openai": OpenAIAdapter,
            "mock": MockLLMAdapter,
        }

    def register_provider(self, name: str, adapter_cls: Type[ILLMProviderAdapter]) -> None:
        self._registry[name.lower()] = adapter_cls

    def create_provider(self, name: str, **kwargs) -> ILLMProviderAdapter:
        provider_key = name.lower()
        adapter_cls = self._registry.get(provider_key)
        if not adapter_cls:
            # Fallback to mock adapter
            return MockLLMAdapter()
        return adapter_cls(**kwargs)


provider_factory = ProviderFactory()
