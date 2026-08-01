import time
import secrets
import hashlib
from typing import Dict, Tuple, Optional
from datetime import datetime

from app.modules.public_api.domain.models import ApiKey, ApiQuota, KeyStatus, RateLimitTier, ApiError
from app.modules.public_api.domain.exceptions import UnauthorizedAccessError, RateLimitExceededError, InvalidScopeError

def hash_secret(secret: str) -> str:
    """Mock hashing. In production, use argon2 or bcrypt."""
    return hashlib.sha256(secret.encode()).hexdigest()

class KeyManager:
    """Mints, Validates, and Revokes API Keys."""
    
    def __init__(self):
        # In-memory storage for demonstration. Will be an injected Repository.
        self._keys: Dict[str, ApiKey] = {}

    def mint_key(self, workspace_id: str, name: str, scopes: list[str], tier: RateLimitTier = RateLimitTier.PRO) -> Tuple[ApiKey, str]:
        """Creates a new API Key and returns the raw secret ONCE."""
        raw_secret = f"av_live_{secrets.token_urlsafe(32)}"
        hashed = hash_secret(raw_secret)
        
        key = ApiKey(
            id=f"key_{secrets.token_hex(8)}",
            workspace_id=workspace_id,
            name=name,
            prefix=raw_secret[:12],
            hashed_secret=hashed,
            scopes=scopes,
            status=KeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=None,
            last_used_at=None,
            quota=ApiQuota.default_for_tier(tier)
        )
        self._keys[key.id] = key
        # In memory simulation, we map hashed secret to the key for easy lookup in auth
        return key, raw_secret

    def validate_key(self, raw_secret: str) -> ApiKey:
        """Validates an incoming secret against the database."""
        hashed = hash_secret(raw_secret)
        # Search for key with this hash
        for key in self._keys.values():
            if key.hashed_secret == hashed:
                if not key.is_valid():
                    raise UnauthorizedAccessError("API Key is revoked or expired.")
                key.last_used_at = datetime.utcnow()
                return key
        raise UnauthorizedAccessError("Invalid API Key.")


class RateLimiter:
    """
    In-memory Token Bucket / Fixed Window mock implementation.
    In an enterprise deployment, this is backed by Redis via Lua scripts.
    """
    def __init__(self):
        # Maps workspace_id -> (timestamp, count)
        self._window: Dict[str, Tuple[float, int]] = {}

    def enforce(self, key: ApiKey):
        now = time.time()
        workspace_id = key.workspace_id
        
        if workspace_id not in self._window:
            self._window[workspace_id] = (now, 1)
            return

        window_start, count = self._window[workspace_id]
        
        # 1 second window
        if now - window_start < 1.0:
            if count >= key.quota.requests_per_second:
                raise RateLimitExceededError("Rate limit exceeded. Try again later.")
            self._window[workspace_id] = (window_start, count + 1)
        else:
            self._window[workspace_id] = (now, 1)


class ErrorMapper:
    """Maps internal system exceptions to canonical ApiErrors."""
    
    @staticmethod
    def map_exception(e: Exception, request_id: str) -> ApiError:
        if isinstance(e, UnauthorizedAccessError):
            return ApiError(status=401, code="unauthorized", message=str(e), request_id=request_id)
        if isinstance(e, RateLimitExceededError):
            return ApiError(status=429, code="rate_limit_exceeded", message=str(e), request_id=request_id)
        if isinstance(e, InvalidScopeError):
            return ApiError(status=403, code="forbidden_scope", message=str(e), request_id=request_id)
            
        # Default internal error mask to prevent stack trace leaks
        return ApiError(
            status=500, 
            code="internal_error", 
            message="An internal system error occurred.", 
            request_id=request_id
        )
