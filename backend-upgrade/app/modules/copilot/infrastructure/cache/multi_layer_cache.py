"""
Multi-Layer Cache Adapter (Phase 5.5.6)
High-performance L1 in-memory + L2 cache adapter for Context, Memory, and Tool Outputs.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import uuid


class MultiLayerCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        # Key -> (data, expires_at)
        self._l1_cache: Dict[str, tuple[Any, datetime]] = {}

    def get(self, cache_key: str) -> Optional[Any]:
        if cache_key not in self._l1_cache:
            return None

        data, expires_at = self._l1_cache[cache_key]
        if datetime.now(timezone.utc) > expires_at:
            del self._l1_cache[cache_key]
            return None

        return data

    def set(self, cache_key: str, data: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds or self.default_ttl
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        self._l1_cache[cache_key] = (data, expires_at)

    def invalidate(self, cache_key: str) -> None:
        self._l1_cache.pop(cache_key, None)

    def clear_workspace(self, workspace_id: uuid.UUID) -> int:
        prefix = f"ws:{str(workspace_id)}"
        keys_to_del = [k for k in self._l1_cache.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            del self._l1_cache[k]
        return len(keys_to_del)


multi_layer_cache = MultiLayerCache()
