from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from app.modules.administration.domain.models import User, Role, Policy, PolicyType, UserStatus
from app.modules.administration.application.services import RBACEngine, AuditEngine, PolicyEngine

router = APIRouter(prefix="/v1/admin", tags=["Enterprise Administration"])

# Pre-seed for demonstration
_roles_db = {
    "role_admin": Role(id="role_admin", name="Super Admin", permissions=["*"]),
    "role_sales": Role(id="role_sales", name="Sales Rep", permissions=["dashboard:read", "agent:execute"])
}

_users_db = {
    "u_1": User(id="u_1", email="ceo@avenor.ai", roles=["role_admin"]),
    "u_2": User(id="u_2", email="rep@avenor.ai", roles=["role_sales"])
}

_policies_db = [
    Policy(id="pol_1", type=PolicyType.IP_RESTRICTION, configuration={"allowed_ips": ["192.168.1.100"]})
]

@router.post("/evaluate")
async def evaluate_access(payload: Dict[str, Any]) -> dict:
    """Evaluate if a User has a specific permission."""
    user_id = payload.get("user_id")
    permission = payload.get("permission")
    
    user = _users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    has_access = RBACEngine.evaluate(user, _roles_db, permission)
    
    # Log the access attempt
    AuditEngine.log_event(
        actor_id=user_id,
        action="rbac.evaluation",
        resource_id=permission,
        details={"granted": has_access}
    )
    
    return {"granted": has_access}

@router.post("/login_attempt")
async def simulate_login(payload: Dict[str, Any]) -> dict:
    """Simulate a login attempt gated by Policy Engine (e.g. IP Restrictions)."""
    client_ip = payload.get("client_ip")
    
    # 1. Enforce Policies
    is_allowed = PolicyEngine.evaluate_request(_policies_db, {"client_ip": client_ip})
    
    # 2. Audit
    AuditEngine.log_event(
        actor_id="anonymous",
        action="security.login_attempt",
        resource_id="system",
        details={"client_ip": client_ip, "blocked_by_policy": not is_allowed}
    )
    
    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access blocked by Organization Security Policy")
        
    return {"status": "success"}

@router.get("/audit")
async def get_audit_logs() -> List[dict]:
    """Fetch the immutable ledger."""
    return [{"id": l.id, "timestamp": l.timestamp.isoformat(), "action": l.action, "actor": l.actor_id, "details": l.details} 
            for l in AuditEngine.get_logs()]
