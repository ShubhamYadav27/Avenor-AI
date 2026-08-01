import uuid

from app.modules.copilot.application.context.budget_manager import token_budget_manager
from app.modules.copilot.application.context.pipeline import context_quality_pipeline
from app.modules.copilot.application.context.ranker import context_ranker
from app.modules.copilot.application.orchestrator.prompt_builder import prompt_builder
from app.modules.copilot.domain.context import (
    ContextCategory,
    ContextIntent,
    ContextItem,
    UnifiedContext,
)


def test_context_item_provenance_and_citation_ids():
    item = ContextItem(
        category=ContextCategory.SIGNAL,
        content="Hiring signal detected",
        relevance_score=0.9,
        freshness_score=0.95,
        confidence_score=0.92,
    )

    assert item.provenance_id.startswith("prov-")
    assert item.citation_id.startswith("cit-")
    assert item.freshness_score == 0.95
    assert item.confidence_score == 0.92


def test_multi_factor_ranking_formula():
    item1 = ContextItem(
        category=ContextCategory.WORKSPACE,
        relevance_score=0.8,
        freshness_score=1.0,
        confidence_score=0.9,
        content="Workspace baseline",
    )
    item2 = ContextItem(
        category=ContextCategory.SIGNAL,
        relevance_score=0.95,
        freshness_score=0.90,
        confidence_score=0.85,
        content="Signal trigger",
    )

    ranked = context_ranker.rank_and_deduplicate([item1, item2])
    assert len(ranked) == 2
    assert ranked[0].final_score > 0
    assert ranked[1].final_score > 0


def test_model_aware_budget_presets():
    budget_gemini = token_budget_manager.resolve_model_budget("gemini-1.5-pro")
    budget_gpt4o = token_budget_manager.resolve_model_budget("gpt-4o")
    budget_mock = token_budget_manager.resolve_model_budget("mock-model")

    assert budget_gemini == 12000
    assert budget_gpt4o == 8000
    assert budget_mock == 4000


def test_context_quality_pipeline_processing():
    workspace_id = uuid.uuid4()
    item = ContextItem(
        category=ContextCategory.COMPANY,
        content="Target account Acme Corp profile",
        relevance_score=0.9,
    )

    unified = context_quality_pipeline.process(
        workspace_id=workspace_id,
        user_query="Tell me about Acme Corp",
        intent=ContextIntent.COMPANY_DEEP_DIVE,
        raw_items=[item],
        provider_health={"company_provider": "healthy"},
        model_name="gemini-1.5-pro",
        prompt_version="v2",
    )

    assert isinstance(unified, UnifiedContext)
    assert unified.overall_confidence_score > 0.0
    assert unified.prompt_version == "v2"
    assert unified.provider_health["company_provider"] == "healthy"


def test_prompt_builder_versioning():
    workspace_id = uuid.uuid4()
    item = ContextItem(category=ContextCategory.COMPANY, content="Company details Acme")
    ctx = UnifiedContext(workspace_id=workspace_id, items=[item])

    prompt_v1 = prompt_builder.build_system_prompt(unified_context=ctx, prompt_version="v1")
    prompt_v2 = prompt_builder.build_system_prompt(unified_context=ctx, prompt_version="v2")

    assert "elite executive revenue strategist" in prompt_v1
    assert "Version 2.0" in prompt_v2
    assert "Citation ID:" in prompt_v2
