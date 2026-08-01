"""
Memory Validation Engine (Phase 5.5.4)
Validates memory items for schema correctness, duplicate detection, and conflict resolution.
"""
from typing import List, Tuple

from app.modules.copilot.domain.memory_entities import MemoryItem


class MemoryValidationEngine:
    def validate_and_deduplicate(
        self,
        new_items: List[MemoryItem],
        existing_items: List[MemoryItem],
    ) -> Tuple[List[MemoryItem], int, int]:
        existing_contents = {item.content.strip().lower(): item for item in existing_items}
        
        valid_items: List[MemoryItem] = []
        duplicate_count = 0
        conflict_count = 0

        for item in new_items:
            if not item.content or len(item.content.strip()) < 3:
                continue

            normalized = item.content.strip().lower()
            if normalized in existing_contents:
                duplicate_count += 1
                # Conflict resolution: If new item has higher confidence, update existing item
                existing = existing_contents[normalized]
                if item.confidence_score > existing.confidence_score:
                    conflict_count += 1
                    existing.confidence_score = item.confidence_score
                    existing.version += 1
                    existing.previous_version_id = item.id
            else:
                valid_items.append(item)

        return valid_items, duplicate_count, conflict_count


memory_validation_engine = MemoryValidationEngine()
