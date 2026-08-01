import uuid
import pytest

from app.modules.copilot.application.orchestrator.prompt_builder import prompt_builder
from app.modules.copilot.citation_engine.application.engine import citation_engine
from app.modules.copilot.citation_engine.application.normalizers.evidence_normalizer import evidence_normalizer
from app.modules.copilot.citation_engine.application.rankers.evidence_ranker import evidence_ranker
from app.modules.copilot.citation_engine.application.resolvers.citation_resolver import citation_resolver
from app.modules.copilot.citation_engine.application.validation.citation_validator import citation_validator
from app.modules.copilot.domain.citation_entities import EvidenceItem
from app.modules.copilot.domain.citation_value_objects import EvidenceQuality, EvidenceType, GroundingStatus
from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, UnifiedContext


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_evidence_item_instantiation():
    item = EvidenceItem(
        type=EvidenceType.CRM,
        raw_content="Deal stage updated to Negotiation ($150k)",
        confidence_score=0.95,
    )
    assert item.id.startswith("ev-")
    assert item.provenance_id.startswith("prov-ev-")
    assert item.citation_id.startswith("cit-crm-")
    assert item.quality == EvidenceQuality.VERIFIED


def test_evidence_normalizer_quality_tiering():
    item1 = EvidenceItem(raw_content="  High confidence fact  ", confidence_score=0.98)
    item2 = EvidenceItem(raw_content="Medium confidence fact", confidence_score=0.75)

    normalized = evidence_normalizer.normalize_items([item1, item2])
    assert len(normalized) == 2
    assert normalized[0].quality == EvidenceQuality.VERIFIED
    assert normalized[1].quality == EvidenceQuality.MEDIUM_CONFIDENCE


def test_citation_resolver_registry_building():
    item = EvidenceItem(
        type=EvidenceType.SIGNAL,
        source_type="signal_engine",
        raw_content="Acme Corp posted 12 open DevOps roles in last 7 days",
        confidence_score=0.90,
    )
    registry = citation_resolver.resolve_citations([item])
    assert registry.total_citations == 1
    assert item.citation_id in registry.citations_map
    assert registry.overall_grounding_score == 0.90


def test_evidence_ranker_corroboration():
    item_single = EvidenceItem(confidence_score=0.90, corroborating_sources=[])
    item_corroborated = EvidenceItem(confidence_score=0.90, corroborating_sources=["crm", "signal"])

    ranked = evidence_ranker.rank_evidence([item_single, item_corroborated])
    assert ranked[0] == item_corroborated
    assert item_corroborated.score > item_single.score


def test_citation_validator_unsupported_claim_detection():
    items = [
        EvidenceItem(raw_content="Fact 1", confidence_score=0.95),
        EvidenceItem(raw_content="Fact 2", confidence_score=0.95),
    ]
    res_normal = citation_validator.validate_grounding("What is Acme's buying intent?", items)
    assert res_normal.is_grounded is True
    assert res_normal.status == GroundingStatus.FULLY_GROUNDED

    res_absolute = citation_validator.validate_grounding("Guarantee 100% deal closure tomorrow", items)
    assert res_absolute.status == GroundingStatus.UNSUPPORTED_CLAIMS_DETECTED
    assert len(res_absolute.unsupported_warnings) > 0


@pytest.mark.anyio
async def test_citation_engine_generate_package():
    workspace_id = uuid.uuid4()
    context = UnifiedContext(
        workspace_id=workspace_id,
        intent=ContextIntent.COMPANY_DEEP_DIVE,
        items=[
            ContextItem(
                category=ContextCategory.COMPANY,
                content="Acme Corp is a SaaS enterprise based in SF.",
                confidence_score=0.95,
            )
        ],
    )



    pkg = await citation_engine.generate_citation_package(
        workspace_id=workspace_id,
        query="Analyze Acme Corp",
        intent=ContextIntent.COMPANY_DEEP_DIVE,
        context=context,
    )

    assert pkg.workspace_id == workspace_id
    assert len(pkg.evidence_items) > 0
    assert pkg.registry.total_citations == 1
    assert "VERIFIED EVIDENCE & CITATION REGISTRY" in prompt_builder.build_system_prompt(citation_package=pkg)
