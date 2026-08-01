import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.administration.domain.models import (
    User, Role, AuditLog, Policy, PolicyType, UserStatus
)

class RBACEngine:
    """Evaluates Fine-Grained Permissions."""
    
    @staticmethod
    def evaluate(user: User, roles_db: Dict[str, Role], required_permission: str) -> bool:
        if user.status != UserStatus.ACTIVE:
            return False
            
        for role_id in user.roles:
            role = roles_db.get(role_id)
            if not role:
                continue
                
            if "*" in role.permissions:
                return True # Super Admin
                
            if required_permission in role.permissions:
                return True
                
        return False

class PolicyEngine:
    """Enforces Security Rules (e.g. IP Restrictions)."""
    
    @staticmethod
    def evaluate_request(policies: List[Policy], request_context: Dict[str, Any]) -> bool:
        """Returns True if request is allowed by all policies, False if blocked."""
        for policy in policies:
            if not policy.is_active:
                continue
                
            if policy.type == PolicyType.IP_RESTRICTION:
                allowed_ips = policy.configuration.get("allowed_ips", [])
                client_ip = request_context.get("client_ip")
                if client_ip not in allowed_ips:
                    return False # Blocked
                    
        return True

class AuditEngine:
    """Immutable Ledger for Security Tracking."""
    
    _ledger: List[AuditLog] = []
    
    @classmethod
    def log_event(cls, actor_id: str, action: str, resource_id: str, details: Dict[str, Any] = None) -> AuditLog:
        log = AuditLog(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow(),
            actor_id=actor_id,
            action=action,
            resource_id=resource_id,
            details=details or {}
        )
        cls._ledger.append(log)
        return log
        
    @classmethod
    def get_logs(cls) -> List[AuditLog]:
        return cls._ledger
