from app.modules.copilot.application.context.intent_detector import intent_detector
from app.modules.copilot.application.context.ranker import context_ranker
from app.modules.copilot.application.context.budget_manager import token_budget_manager
from app.modules.copilot.domain.context import ContextIntent, ContextItem, ContextPriority, ContextCategory


def test_intent_detector():
    assert intent_detector.detect_intent("What objections should I expect?") == ContextIntent.OBJECTION_HANDLING
    assert intent_detector.detect_intent("Show active hiring and funding signals") == ContextIntent.BUYING_SIGNALS
    assert intent_detector.detect_intent("Which deals are in negotiation stage?") == ContextIntent.CRM_PIPELINE
    assert intent_detector.detect_intent("Draft follow up email for Acme") == ContextIntent.OUTREACH_STRATEGY
    assert intent_detector.detect_intent("Give me research briefing on Acme Corp") == ContextIntent.COMPANY_DEEP_DIVE
    assert intent_detector.detect_intent("General strategy question") == ContextIntent.GENERAL_STRATEGY


def test_context_ranker():
    item_low = ContextItem(category=ContextCategory.EMAIL, priority=ContextPriority.LOW, content="Low item")
    item_critical = ContextItem(category=ContextCategory.WORKSPACE, priority=ContextPriority.CRITICAL, content="Critical item")
    item_high = ContextItem(category=ContextCategory.COMPANY, priority=ContextPriority.HIGH, content="High item")

    ranked = context_ranker.rank_and_deduplicate([item_low, item_critical, item_high, item_low])
    assert len(ranked) == 3
    assert ranked[0].priority == ContextPriority.CRITICAL
    assert ranked[1].priority == ContextPriority.HIGH
    assert ranked[2].priority == ContextPriority.LOW


def test_token_budget_manager():
    items = [
        ContextItem(content="Word " * 200, priority=ContextPriority.HIGH),
        ContextItem(content="Word " * 200, priority=ContextPriority.MEDIUM),
    ]

    selected, total_tokens = token_budget_manager.fit_to_budget(items, max_token_budget=150)
    assert total_tokens <= 150
    assert len(selected) >= 1
