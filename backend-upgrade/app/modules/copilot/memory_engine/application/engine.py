"""
Enterprise Memory Engine (Phase 5.5.4 Architecture)
Coordinating layer integrating Planner -> Retrieval -> Governance -> Validation -> Ranking -> PackageBuilder.
Launches background async extraction & consolidation for low user-facing latency.
"""
import asyncio
import time
from typing import List, Optional
import uuid

from app.modules.copilot.domain.context import ContextIntent
from app.modules.copilot.domain.interfaces import IMemoryEngine
from app.modules.copilot.domain.memory_entities import MemoryConsolidationResult, MemoryItem, MemoryMetrics, MemoryPackage
from app.modules.copilot.memory_engine.application.builders.package_builder import memory_package_builder
from app.modules.copilot.memory_engine.application.extractors.extraction_engine import memory_extraction_engine
from app.modules.copilot.memory_engine.application.governance.governance_engine import memory_governance_engine
from app.modules.copilot.memory_engine.application.planners.memory_planner import memory_planner
from app.modules.copilot.memory_engine.application.rankers.ranking_engine import memory_ranking_engine
from app.modules.copilot.memory_engine.application.validation.validation_engine import memory_validation_engine
from app.modules.copilot.memory_engine.infrastructure.adapters.in_memory_adapter import in_memory_adapter


class MemoryEngine(IMemoryEngine):
    def __init__(self, adapter=None):
        self.adapter = adapter or in_memory_adapter

    async def retrieve_memories(
        self,
        workspace_id: uuid.UUID,
        query: str,
        intent: ContextIntent,
        thread_id: Optional[uuid.UUID] = None,
    ) -> MemoryPackage:
        start_time = time.perf_counter()
        metrics = MemoryMetrics()

        # 1. Memory Retrieval Planning
        plan = memory_planner.create_retrieval_plan(workspace_id, query, intent)
        target_cats = [c.value for c in plan.target_categories]

        # 2. Retrieval from Adapter
        t0 = time.perf_counter()
        raw_memories = await self.adapter.query_memories(
            workspace_id=workspace_id,
            categories=target_cats,
            limit=plan.max_items * 2,
        )
        metrics.retrieval_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        metrics.memories_queried_count = len(raw_memories)

        # 3. Governance Enforcement (PII Scrubbing, Expiration & Workspace Isolation)
        governed_memories = memory_governance_engine.enforce_governance(workspace_id, raw_memories)

        # 4. Multi-Factor Ranking (Relevance, Freshness, Importance, Feedback)
        t1 = time.perf_counter()
        ranked_memories = memory_ranking_engine.rank_memories(governed_memories)
        metrics.ranking_latency_ms = round((time.perf_counter() - t1) * 1000.0, 2)

        # Select top N memories within token budget
        selected_memories = ranked_memories[: plan.max_items]
        metrics.memories_retrieved_count = len(selected_memories)

        # 5. Build Memory Package
        pkg = memory_package_builder.build_package(
            workspace_id=workspace_id,
            intent=intent,
            memories=selected_memories,
            metrics=metrics,
            thread_id=thread_id,
        )

        # 6. Trigger Background Async Memory Extraction & Consolidation
        asyncio.create_task(self._async_extract_and_consolidate(workspace_id, query, thread_id))

        return pkg

    async def consolidate_and_persist(
        self,
        workspace_id: uuid.UUID,
        raw_items: List[MemoryItem],
    ) -> MemoryConsolidationResult:
        t0 = time.perf_counter()
        
        # 1. Fetch existing memories for deduplication
        existing = await self.adapter.query_memories(workspace_id=workspace_id, limit=200)
        
        # 2. Validation & Deduplication
        valid_items, dupes, conflicts = memory_validation_engine.validate_and_deduplicate(raw_items, existing)

        # 3. Save valid new memories
        for item in valid_items:
            await self.adapter.save_memory(item)

        duration = round((time.perf_counter() - t0) * 1000.0, 2)
        return MemoryConsolidationResult(
            consolidated_count=len(valid_items),
            superseded_count=conflicts,
            new_memories_created=len(valid_items),
            duration_ms=duration,
        )

    async def _async_extract_and_consolidate(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        thread_id: Optional[uuid.UUID] = None,
    ) -> None:
        try:
            extracted = memory_extraction_engine.extract_memories_from_query(workspace_id, user_query, thread_id)
            if extracted:
                await self.consolidate_and_persist(workspace_id, extracted)
        except Exception:
            pass  # Background tasks must never throw to caller


memory_engine = MemoryEngine()
