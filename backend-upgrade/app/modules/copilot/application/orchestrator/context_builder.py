"""
Context Builder
Integrates ContextEngine to assemble a UnifiedContext package for the Intelligence Orchestrator.
"""
from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.modules.copilot.application.context.engine import context_engine
from app.modules.copilot.domain.context import UnifiedContext
from app.modules.copilot.domain.entities import CopilotStateEntity


class ContextBuilder:
    async def build_context(
        self,
        workspace_id: uuid.UUID,
        user_query: str = "",
        state: Optional[CopilotStateEntity] = None,
        db: Optional[Session] = None,
        max_token_budget: int = 4000,
    ) -> UnifiedContext:
        return await context_engine.assemble_context(
            workspace_id=workspace_id,
            user_query=user_query,
            state=state,
            max_token_budget=max_token_budget,
            db=db,
        )


context_builder = ContextBuilder()
