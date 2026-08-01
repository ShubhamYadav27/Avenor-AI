"""
In-Memory Memory Adapter (Phase 5.5.4 Infrastructure)
Fast in-memory store for Enterprise Memory Engine with workspace scoping, category filtering, and TTL invalidation.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.interfaces import IMemoryAdapter
from app.modules.copilot.domain.memory_entities import MemoryItem
from app.modules.copilot.domain.memory_value_objects import MemoryCategory, MemoryImportance, MemoryStatus, MemoryTier


class InMemoryMemoryAdapter(IMemoryAdapter):
    def __init__(self):
        # Key: memory_id -> MemoryItem
        self._store: Dict[str, MemoryItem] = {}

    async def save_memory(self, item: MemoryItem) -> MemoryItem:
        self._store[item.id] = item
        return item

    async def get_memory_by_id(self, memory_id: str, workspace_id: uuid.UUID) -> Optional[MemoryItem]:
        item = self._store.get(memory_id)
        if item and item.workspace_id == workspace_id:
            return item
        return None

    async def query_memories(
        self,
        workspace_id: uuid.UUID,
        categories: Optional[List[str]] = None,
        entity_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[MemoryItem]:
        results: List[MemoryItem] = []
        now = datetime.now(timezone.utc)

        for item in self._store.values():
            if item.workspace_id != workspace_id:
                continue

            if item.status in (MemoryStatus.EXPIRED, MemoryStatus.DELETED):
                continue

            if item.expires_at and item.expires_at <= now:
                item.status = MemoryStatus.EXPIRED
                continue

            if categories and item.category.value not in categories:
                continue

            if entity_id and item.entity_id != entity_id:
                continue

            results.append(item)
            if len(results) >= limit:
                break

        return results

    async def update_memory(self, item: MemoryItem) -> MemoryItem:
        item.last_used_at = datetime.now(timezone.utc)
        self._store[item.id] = item
        return item

    @classmethod
    def create_default_adapter_with_seed(cls) -> "InMemoryMemoryAdapter":
        adapter = cls()
        # Seed baseline workspace memory items
        demo_ws_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        adapter._store["mem-seed-1"] = MemoryItem(
            id="mem-seed-1",
            workspace_id=demo_ws_id,
            category=MemoryCategory.WORKSPACE,
            tier=MemoryTier.LONG_TERM,
            content="Workspace strategy: Prioritize high-intent Tier 1 accounts with recent hiring triggers.",
            confidence_score=1.0,
            importance=MemoryImportance.CRITICAL,
            source_type="workspace_config",
        )
        adapter._store["mem-seed-2"] = MemoryItem(
            id="mem-seed-2",
            workspace_id=demo_ws_id,
            category=MemoryCategory.KNOWLEDGE,
            tier=MemoryTier.SEMANTIC,
            content="Avenor Playbook: Respond to objection on price by proving 10x ROI via buying signal velocity.",
            confidence_score=0.95,
            importance=MemoryImportance.HIGH,
            source_type="playbook",
        )
        return adapter


in_memory_adapter = InMemoryMemoryAdapter.create_default_adapter_with_seed()
