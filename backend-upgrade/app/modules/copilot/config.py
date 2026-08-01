"""
Copilot Module Configuration & Feature Flags
Phase 5.5.1 Foundation
"""
import os
from pydantic import BaseModel, Field


class FeatureFlags(BaseModel):
    copilot_enabled: bool = Field(default=True, description="Master toggle for Revenue Copilot")
    streaming_enabled: bool = Field(default=True, description="Toggle for SSE streaming response delivery")
    memory_enabled: bool = Field(default=False, description="Toggle for future memory engine (Phase 5.5.2)")
    citations_enabled: bool = Field(default=False, description="Toggle for future citations engine (Phase 5.5.3)")
    tools_enabled: bool = Field(default=False, description="Toggle for future tool orchestration (Phase 5.5.4)")
    voice_enabled: bool = Field(default=False, description="Toggle for future voice support")


class LLMSettings(BaseModel):
    default_provider: str = Field(default_factory=lambda: os.getenv("COPILOT_DEFAULT_PROVIDER", "gemini"))
    fallback_provider: str = Field(default_factory=lambda: os.getenv("COPILOT_FALLBACK_PROVIDER", "openai"))
    default_model: str = Field(default_factory=lambda: os.getenv("COPILOT_DEFAULT_MODEL", "gemini-1.5-pro"))
    max_tokens: int = Field(default=2048)
    temperature: float = Field(default=0.7)
    request_timeout_seconds: int = Field(default=30)
    max_retries: int = Field(default=3)


class StreamingSettings(BaseModel):
    chunk_size_chars: int = Field(default=12)
    ping_interval_seconds: int = Field(default=15)
    keepalive_timeout_seconds: int = Field(default=60)


class CopilotSettings(BaseModel):
    version: str = "v1"
    system_name: str = "Avenor AI Revenue Copilot"
    llm: LLMSettings = Field(default_factory=LLMSettings)
    streaming: StreamingSettings = Field(default_factory=StreamingSettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)


copilot_settings = CopilotSettings()
