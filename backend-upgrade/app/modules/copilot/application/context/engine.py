"""
Context Intelligence Engine (Phase 5.5.2 Part 3)
Assembles structured business intelligence into UnifiedContext using ContextQualityPipeline,
async parallel provider execution, per-provider timeouts, and partial context error recovery.
"""
import asyncio
from typing import Dict, List, Optional
import uuid
from sqlalchemy.orm import Session

from app.modules.copilot.application.context.intent_detector import intent_detector
from app.modules.copilot.application.context.pipeline import context_quality_pipeline
from app.modules.copilot.application.providers.registry import ContextProviderRegistry
from app.modules.copilot.domain.context import ContextItem, UnifiedContext
from app.modules.copilot.domain.entities import CopilotStateEntity
from app.modules.copilot.domain.interfaces import IContextEngine

PER_PROVIDER_TIMEOUT_SECONDS: float = 2.0


class ContextEngine(IContextEngine):
    def __init__(self, registry: Optional[ContextProviderRegistry] = None):
        self.registry = registry

    def _get_registry(self, db: Session) -> ContextProviderRegistry:
        if self.registry:
            return self.registry
        return ContextProviderRegistry().create_default_registry(db)

    async def assemble_context(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        state: Optional[CopilotStateEntity] = None,
        max_token_budget: int = 4000,
        model_name: Optional[str] = None,
        prompt_version: str = "v1",
        db: Optional[Session] = None,
    ) -> UnifiedContext:
        # 1. Detect Query Intent
        intent = intent_detector.detect_intent(user_query)

        # 2. Check DB presence
        if not db:
            return UnifiedContext(workspace_id=workspace_id, intent=intent, prompt_version=prompt_version)

        # 3. Resolve Matching Providers
        provider_registry = self._get_registry(db)
        providers = provider_registry.resolve_providers(intent)

        # 4. Asynchronous Parallel Provider Execution with Timeout & Error Recovery
        raw_items: List[ContextItem] = []
        provider_health: Dict[str, str] = {}

        async def _fetch_with_timeout(provider) -> List[ContextItem]:
            try:
                return await asyncio.wait_for(
                    provider.fetch_context(workspace_id, user_query, state),
                    timeout=PER_PROVIDER_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                provider_health[provider.provider_name] = "timed_out"
                return []
            except Exception as e:
                provider_health[provider.provider_name] = f"error: {str(e)}"
                return []

        tasks = [_fetch_with_timeout(p) for p in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for p, res in zip(providers, results):
            if isinstance(res, list):
                raw_items.extend(res)
                if p.provider_name not in provider_health:
                    provider_health[p.provider_name] = "healthy"

        # 5. Process through 11-Stage Context Quality Pipeline
        return context_quality_pipeline.process(
            workspace_id=workspace_id,
            user_query=user_query,
            intent=intent,
            raw_items=raw_items,
            provider_health=provider_health,
            state=state,
            max_token_budget=max_token_budget,
            model_name=model_name,
            prompt_version=prompt_version,
        )


context_engine = ContextEngine()
