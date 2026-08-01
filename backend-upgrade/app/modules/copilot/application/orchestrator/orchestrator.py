"""
Intelligence Orchestrator (Phase 5.5.6 Architecture)
Main coordination layer orchestrating ContextEngine -> MemoryEngine -> ToolExecutionEngine -> CitationEngine -> StreamSanitizer -> LLM Provider.
Zero direct DB query logic in orchestrator.
"""
from typing import AsyncGenerator, Optional
import uuid
from sqlalchemy.orm import Session

from app.modules.copilot.application.context.engine import context_engine
from app.modules.copilot.application.orchestrator.history_manager import history_manager
from app.modules.copilot.application.orchestrator.prompt_builder import prompt_builder
from app.modules.copilot.application.orchestrator.provider_router import provider_router
from app.modules.copilot.application.security.rate_limiter import token_rate_limiter
from app.modules.copilot.application.security.stream_sanitizer import stream_sanitizer
from app.modules.copilot.application.services.message_service import MessageService
from app.modules.copilot.application.services.thread_service import ThreadService
from app.modules.copilot.citation_engine.application.engine import citation_engine
from app.modules.copilot.domain.entities import CopilotMessageEntity
from app.modules.copilot.infrastructure.registry.model_registry import model_registry
from app.modules.copilot.memory_engine.application.engine import memory_engine
from app.modules.copilot.tool_orchestration.application.executors.execution_engine import tool_execution_engine


class IntelligenceOrchestrator:
    def __init__(
        self,
        thread_service: Optional[ThreadService] = None,
        message_service: Optional[MessageService] = None,
    ):
        self.thread_service = thread_service
        self.message_service = message_service

    async def execute_stream(
        self,
        workspace_id: uuid.UUID,
        thread_id: uuid.UUID,
        user_query: str,
        user_id: Optional[uuid.UUID] = None,
        model_name: Optional[str] = None,
        prompt_version: str = "v1",
        db: Optional[Session] = None,
    ) -> AsyncGenerator[str, None]:
        resolved_model = model_name or model_registry.get_default_model().name

        # 0. Check Rate Limiter Quota
        if not token_rate_limiter.check_rate_limit(workspace_id):
            yield "Rate limit exceeded for workspace. Please wait before submitting more queries."
            return

        # 1. Fetch History & State if DB provided
        history = []
        state = None
        if db and self.message_service:
            history = await self.message_service.get_thread_messages(thread_id, limit=20)
            if self.thread_service:
                state = await self.thread_service.get_thread_state(thread_id, workspace_id)

        trimmed_history = history_manager.trim_history(history)

        # 2. Phase 5.5.2: Context Intelligence Engine
        baseline_context = await context_engine.assemble_context(
            workspace_id=workspace_id,
            user_query=user_query,
            state=state,
            model_name=resolved_model,
            prompt_version=prompt_version,
            db=db,
        )

        # 3. Phase 5.5.4: Enterprise Memory Engine Retrieval
        memory_pkg = await memory_engine.retrieve_memories(
            workspace_id=workspace_id,
            query=user_query,
            intent=baseline_context.intent,
            thread_id=thread_id,
        )

        # 4. Phase 5.5.3: Tool Orchestration Engine
        intelligence_pkg = await tool_execution_engine.execute_intent(
            workspace_id=workspace_id,
            user_query=user_query,
            intent=baseline_context.intent,
            context=baseline_context,
            thread_id=thread_id,
            db=db,
        )

        # 5. Phase 5.5.5: Enterprise Citation & Grounding Engine
        citation_pkg = await citation_engine.generate_citation_package(
            workspace_id=workspace_id,
            query=user_query,
            intent=baseline_context.intent,
            context=baseline_context,
            intelligence_pkg=intelligence_pkg,
            memory_pkg=memory_pkg,
            thread_id=thread_id,
        )

        # 6. Prompt Building with Citation, Memory, & Tool Packages
        system_prompt = prompt_builder.build_system_prompt(
            unified_context=intelligence_pkg,
            memory_package=memory_pkg,
            citation_package=citation_pkg,
            prompt_version=prompt_version,
        )

        # 7. Resolve LLM Adapter
        adapter = provider_router.resolve_adapter(resolved_model)

        # 8. Stream tokens with StreamSanitizer (Scrub PII & Secrets)
        full_response_text = []
        raw_stream = adapter.generate_stream(
            messages=trimmed_history,
            system_prompt=system_prompt,
            model_name=resolved_model,
        )

        async for chunk in stream_sanitizer.sanitize_stream(raw_stream):
            full_response_text.append(chunk)
            yield chunk

        # 9. Persist Assistant Response if DB present
        if db and self.message_service:
            assistant_msg = CopilotMessageEntity(
                thread_id=thread_id,
                workspace_id=workspace_id,
                role="assistant",
                content="".join(full_response_text),
                model_used=resolved_model,
                intent_detected=baseline_context.intent.value,
                context_snapshot={
                    "tools_executed": [r.tool_name for r in intelligence_pkg.tool_results],
                    "memories_retrieved": len(memory_pkg.memories),
                    "citations_registered": citation_pkg.registry.total_citations,
                    "grounding_status": citation_pkg.grounding_status.value,
                    "confidence": citation_pkg.overall_confidence_score,
                },
            )
            await self.message_service.add_message(assistant_msg)


intelligence_orchestrator = IntelligenceOrchestrator()
