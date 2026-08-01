"""
Memory Governance Engine (Phase 5.5.4)
Enforces multi-tenant workspace isolation, PII scrubbing, and expiration check.
"""
from datetime import datetime, timezone
import re
from typing import List, Optional
import uuid

from app.modules.copilot.domain.memory_entities import MemoryGovernancePolicy, MemoryItem
from app.modules.copilot.domain.memory_value_objects import MemoryStatus


class MemoryGovernanceEngine:
    # Regex patterns for scrubbing sensitive PII (API keys, secrets, bearer tokens)
    SECRET_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
        re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
        re.compile(r"password\s*=\s*['\"]?[^\s'\"]+", re.IGNORECASE),
        re.compile(r"secret\s*=\s*['\"]?[^\s'\"]+", re.IGNORECASE),
    ]

    def enforce_governance(
        self,
        workspace_id: uuid.UUID,
        items: List[MemoryItem],
        policy: Optional[MemoryGovernancePolicy] = None,
    ) -> List[MemoryItem]:
        valid_items: List[MemoryItem] = []
        now = datetime.now(timezone.utc)

        for item in items:
            # 1. Multi-Tenant Workspace Isolation Check
            if item.workspace_id != workspace_id:
                continue

            # 2. Expiration Check
            if item.expires_at and item.expires_at <= now:
                item.status = MemoryStatus.EXPIRED
                continue

            if item.status in (MemoryStatus.EXPIRED, MemoryStatus.DELETED):
                continue

            # 3. Sensitive PII & Secret Scrubbing
            if policy is None or policy.scrub_pii:
                scrubbed_content = item.content
                for pattern in self.SECRET_PATTERNS:
                    scrubbed_content = pattern.sub("[REDACTED SECRET]", scrubbed_content)
                item.content = scrubbed_content

            valid_items.append(item)

        return valid_items


memory_governance_engine = MemoryGovernanceEngine()
