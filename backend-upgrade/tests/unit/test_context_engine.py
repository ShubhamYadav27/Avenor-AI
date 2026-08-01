import asyncio
import uuid
from app.modules.copilot.application.context.engine import context_engine
from app.modules.copilot.domain.context import ContextIntent, UnifiedContext


def test_context_engine_fallback():
    workspace_id = uuid.uuid4()
    unified = asyncio.run(
        context_engine.assemble_context(
            workspace_id=workspace_id,
            user_query="What companies should I contact today?",
        )
    )

    assert isinstance(unified, UnifiedContext)
    assert unified.workspace_id == workspace_id
    assert unified.intent == ContextIntent.COMPANY_DEEP_DIVE
