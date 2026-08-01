import uuid
import pytest

from app.modules.copilot.application.orchestrator.prompt_builder import prompt_builder
from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.memory_entities import MemoryItem, MemoryPackage
from app.modules.copilot.domain.memory_value_objects import MemoryCategory, MemoryImportance
from app.modules.copilot.memory_engine.application.engine import memory_engine
from app.modules.copilot.memory_engine.application.governance.governance_engine import memory_governance_engine
from app.modules.copilot.memory_engine.application.rankers.ranking_engine import memory_ranking_engine
from app.modules.copilot.memory_engine.application.validation.validation_engine import memory_validation_engine


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_memory_item_provenance_and_versioning():
    item = MemoryItem(
        category=MemoryCategory.COMPANY,
        content="Acme Corp prefers annual upfront billing.",
        confidence_score=0.95,
        importance=MemoryImportance.HIGH,
    )

    assert item.id.startswith("mem-")
    assert item.provenance_id.startswith("prov-mem-")
    assert item.citation_id.startswith("cit-mem-")
    assert item.version == 1
    assert item.previous_version_id is None


def test_governance_pii_scrubbing_and_tenant_isolation():
    workspace1 = uuid.uuid4()
    workspace2 = uuid.uuid4()

    item1 = MemoryItem(
        workspace_id=workspace1,
        content="User secret sk-123456789012345678901234 in chat",
    )
    item2 = MemoryItem(
        workspace_id=workspace2,
        content="Other workspace data",
    )

    governed = memory_governance_engine.enforce_governance(workspace1, [item1, item2])
    
    assert len(governed) == 1
    assert "[REDACTED SECRET]" in governed[0].content
    assert "sk-12345" not in governed[0].content


def test_validation_and_conflict_resolution():
    workspace_id = uuid.uuid4()
    existing = MemoryItem(
        workspace_id=workspace_id,
        content="Target account uses Salesforce CRM",
        confidence_score=0.70,
    )
    new_duplicate = MemoryItem(
        workspace_id=workspace_id,
        content="Target account uses Salesforce CRM",
        confidence_score=0.95,
    )

    valid_items, dupes, conflicts = memory_validation_engine.validate_and_deduplicate([new_duplicate], [existing])
    assert len(valid_items) == 0
    assert dupes == 1
    assert conflicts == 1
    assert existing.confidence_score == 0.95


def test_multi_factor_ranking_formula():
    item1 = MemoryItem(
        relevance_score=0.9,
        importance=MemoryImportance.CRITICAL,
        reinforcement_score=1.0,
        content="High relevance critical item",
    )
    item2 = MemoryItem(
        relevance_score=0.5,
        importance=MemoryImportance.LOW,
        reinforcement_score=0.5,
        content="Low relevance item",
    )

    ranked = memory_ranking_engine.rank_memories([item1, item2])
    assert ranked[0].final_score > ranked[1].final_score


@pytest.mark.anyio
async def test_memory_engine_retrieval_and_package():
    workspace_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    
    pkg = await memory_engine.retrieve_memories(
        workspace_id=workspace_id,
        query="What is our strategy for Acme Corp?",
        intent=ContextIntent.COMPANY_DEEP_DIVE,
    )

    assert isinstance(pkg, MemoryPackage)
    assert len(pkg.memories) > 0
    assert pkg.overall_confidence_score > 0.0
    assert "HISTORICAL ENTERPRISE MEMORY PACKAGE" in prompt_builder.build_system_prompt(memory_package=pkg)
