import uuid
from app.modules.copilot.domain.context import (
    ContextCategory,
    ContextIntent,
    ContextItem,
    ContextPriority,
    UnifiedContext,
)


def test_context_item_instantiation():
    item = ContextItem(
        category=ContextCategory.COMPANY,
        source_provider="company_provider",
        priority=ContextPriority.HIGH,
        content="Acme Corp company profile details",
    )

    assert item.category == ContextCategory.COMPANY
    assert item.priority == ContextPriority.HIGH
    assert item.token_count > 0


def test_unified_context():
    workspace_id = uuid.uuid4()
    item1 = ContextItem(category=ContextCategory.WORKSPACE, content="Workspace info")
    item2 = ContextItem(category=ContextCategory.COMPANY, content="Company info")

    ctx = UnifiedContext(
        workspace_id=workspace_id,
        intent=ContextIntent.COMPANY_DEEP_DIVE,
        items=[item1, item2],
    )

    assert ctx.workspace_id == workspace_id
    assert ctx.intent == ContextIntent.COMPANY_DEEP_DIVE
    assert len(ctx.items) == 2
    assert len(ctx.get_items_by_category(ContextCategory.COMPANY)) == 1
