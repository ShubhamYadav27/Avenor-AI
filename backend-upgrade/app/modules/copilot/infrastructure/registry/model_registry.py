"""
Model Registry
Maintains descriptors and capabilities for supported models across providers.
Future providers/models can be registered dynamically.
"""
from typing import Dict, List, Optional
from app.modules.copilot.domain.entities import ModelCapability, ModelDescriptor


class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelDescriptor] = {}
        self._register_default_models()

    def _register_default_models(self):
        # Gemini 1.5 Pro / Flash
        self.register_model(
            ModelDescriptor(
                provider="gemini",
                name="gemini-1.5-pro",
                capabilities=ModelCapability(
                    supports_streaming=True,
                    supports_tools=True,
                    supports_vision=True,
                    supports_system_prompt=True,
                    context_window_size=1000000,
                    cost_per_1k_tokens=0.00125,
                ),
            )
        )
        self.register_model(
            ModelDescriptor(
                provider="gemini",
                name="gemini-1.5-flash",
                capabilities=ModelCapability(
                    supports_streaming=True,
                    supports_tools=True,
                    supports_vision=True,
                    supports_system_prompt=True,
                    context_window_size=1000000,
                    cost_per_1k_tokens=0.00035,
                ),
            )
        )
        # OpenAI GPT-4o / GPT-4o-mini
        self.register_model(
            ModelDescriptor(
                provider="openai",
                name="gpt-4o",
                capabilities=ModelCapability(
                    supports_streaming=True,
                    supports_tools=True,
                    supports_vision=True,
                    supports_system_prompt=True,
                    context_window_size=128000,
                    cost_per_1k_tokens=0.0025,
                ),
            )
        )
        # Mock / Local Fallback
        self.register_model(
            ModelDescriptor(
                provider="mock",
                name="mock-model",
                capabilities=ModelCapability(
                    supports_streaming=True,
                    supports_tools=True,
                    supports_vision=False,
                    supports_system_prompt=True,
                    context_window_size=32000,
                    cost_per_1k_tokens=0.0,
                ),
            )
        )

    def register_model(self, descriptor: ModelDescriptor) -> None:
        key = f"{descriptor.provider}:{descriptor.name}"
        self._models[key] = descriptor

    def get_model(self, provider: str, name: str) -> Optional[ModelDescriptor]:
        key = f"{provider}:{name}"
        return self._models.get(key)

    def list_models(self, provider: Optional[str] = None) -> List[ModelDescriptor]:
        if provider:
            return [m for m in self._models.values() if m.provider == provider and m.is_active]
        return [m for m in self._models.values() if m.is_active]


model_registry = ModelRegistry()
