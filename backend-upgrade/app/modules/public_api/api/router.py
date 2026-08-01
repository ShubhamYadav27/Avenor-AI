from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from typing import Optional
import uuid

from app.modules.public_api.domain.models import ApiKey, ApiError
from app.modules.public_api.application.services import KeyManager, RateLimiter, ErrorMapper

router = APIRouter(prefix="/v1", tags=["Public API v1"])

# Global singletons for demonstration
_key_manager = KeyManager()
_rate_limiter = RateLimiter()

def get_key_manager() -> KeyManager:
    return _key_manager

def get_rate_limiter() -> RateLimiter:
    return _rate_limiter

async def require_api_key(
    request: Request,
    authorization: Optional[str] = Header(None),
    key_manager: KeyManager = Depends(get_key_manager),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> ApiKey:
    """Dependency to validate API Key and enforce Rate Limits."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    try:
        if not authorization or not authorization.startswith("Bearer "):
            # We map this through ErrorMapper manually for HTTP 401
            raise ValueError("Missing or invalid Authorization header. Expected 'Bearer <key>'")
        
        raw_token = authorization.split(" ")[1]
        api_key = key_manager.validate_key(raw_token)
        
        # Enforce rate limits
        rate_limiter.enforce(api_key)
        
        return api_key
    except Exception as e:
        # Use our canonical error mapper
        mapped_error = ErrorMapper.map_exception(e, request_id)
        if isinstance(e, ValueError) and "Missing or invalid" in str(e):
             mapped_error = ApiError(status=401, code="unauthorized", message=str(e), request_id=request_id)
             
        raise ReturnEarlyException(mapped_error)

class ReturnEarlyException(Exception):
    def __init__(self, api_error: ApiError):
        self.api_error = api_error

# In a real FastAPI app, you'd register this handler globally on the App object.
# We simulate it here by wrapping endpoints (or just letting the test client catch it via standard FastAPI exception handlers)
# For the sake of this mock API, we'll assume a global handler transforms ReturnEarlyException to JSONResponse.

# --- Example Public Endpoints ---

@router.get("/companies")
async def list_companies(api_key: ApiKey = Depends(require_api_key)):
    """
    Public API Endpoint to list companies.
    Requires 'read:companies' scope.
    """
    if not api_key.has_scope("read:companies"):
        err = ErrorMapper.map_exception(
            Exception("Insufficient scope. Requires 'read:companies'"), 
            request_id="req_foo"
        )
        err.status = 403
        err.code = "forbidden_scope"
        raise ReturnEarlyException(err)
        
    return {
        "object": "list",
        "data": [
            {"id": "comp_1", "name": "Acme Corp", "domain": "acme.com"},
            {"id": "comp_2", "name": "GlobalTech", "domain": "global.tech"}
        ],
        "has_more": False
    }

@router.get("/me")
async def get_current_token_info(api_key: ApiKey = Depends(require_api_key)):
    """Returns information about the current authenticated workspace and scopes."""
    return {
        "workspace_id": api_key.workspace_id,
        "key_name": api_key.name,
        "scopes": api_key.scopes,
        "tier": api_key.quota.tier
    }
