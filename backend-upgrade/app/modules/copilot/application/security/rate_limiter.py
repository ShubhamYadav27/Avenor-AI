"""
Token Rate Limiter (Phase 5.5.6)
Sliding-window rate limiter enforcing per-workspace request and token quotas.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
import uuid


class TokenRateLimiter:
    def __init__(self, max_requests_per_minute: int = 60, max_tokens_per_minute: int = 100000):
        self.max_requests = max_requests_per_minute
        self.max_tokens = max_tokens_per_minute
        # workspace_id -> list of (timestamp, token_count)
        self._windows: Dict[str, List[Tuple[datetime, int]]] = {}

    def check_rate_limit(self, workspace_id: uuid.UUID, estimated_tokens: int = 1000) -> bool:
        ws_key = str(workspace_id)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)

        if ws_key not in self._windows:
            self._windows[ws_key] = []

        # Evict entries older than 1 minute
        self._windows[ws_key] = [e for e in self._windows[ws_key] if e[0] > cutoff]

        recent_requests = len(self._windows[ws_key])
        recent_tokens = sum(e[1] for e in self._windows[ws_key])

        if recent_requests >= self.max_requests or (recent_tokens + estimated_tokens) > self.max_tokens:
            return False

        self._windows[ws_key].append((now, estimated_tokens))
        return True


token_rate_limiter = TokenRateLimiter()
