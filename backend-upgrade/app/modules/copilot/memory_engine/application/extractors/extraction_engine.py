"""
Memory Extraction Engine (Phase 5.5.4)
Extracts key business facts, user preferences, and target account signals from conversation history.
"""
from typing import List, Optional
import uuid

from app.modules.copilot.domain.memory_entities import MemoryItem
from app.modules.copilot.domain.memory_value_objects import MemoryCategory, MemoryImportance, MemoryTier


class MemoryExtractionEngine:
    def extract_memories_from_query(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        thread_id: Optional[uuid.UUID] = None,
    ) -> List[MemoryItem]:
        extracted: List[MemoryItem] = []
        query_lower = user_query.lower()

        # Rule-based extraction heuristics for B2B sales intents
        if "acme" in query_lower or "target account" in query_lower or "customer" in query_lower:
            extracted.append(
                MemoryItem(
                    workspace_id=workspace_id,
                    category=MemoryCategory.COMPANY,
                    tier=MemoryTier.LONG_TERM,
                    content=f"User requested intelligence regarding query: '{user_query}'",
                    confidence_score=0.90,
                    importance=MemoryImportance.HIGH,
                    source_type="user_query",
                    entity_type="thread",
                    entity_id=str(thread_id) if thread_id else None,
                )
            )

        if "prefer" in query_lower or "always" in query_lower or "strategy" in query_lower:
            extracted.append(
                MemoryItem(
                    workspace_id=workspace_id,
                    category=MemoryCategory.USER,
                    tier=MemoryTier.LONG_TERM,
                    content=f"User sales preference note: '{user_query}'",
                    confidence_score=0.85,
                    importance=MemoryImportance.NORMAL,
                    source_type="user_query",
                )
            )

        return extracted


memory_extraction_engine = MemoryExtractionEngine()
