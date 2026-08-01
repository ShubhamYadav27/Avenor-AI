from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"

class PolicyType(str, Enum):
    IP_RESTRICTION = "ip_restriction"
    SESSION_TIMEOUT = "session_timeout"
    MFA_REQUIRED = "mfa_required"

@dataclass
class Organization:
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Workspace:
    id: str
    org_id: str
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Role:
    """RBAC Role defining a set of permissions."""
    id: str
    name: str # e.g., 'Super Admin', 'Sales Rep'
    permissions: List[str] # e.g., ['prompt:publish', 'agent:execute', '*']

@dataclass
class User:
    id: str
    email: str
    status: UserStatus = UserStatus.ACTIVE
    roles: List[str] = field(default_factory=list) # List of Role IDs
    workspaces: List[str] = field(default_factory=list) # List of Workspace IDs they can access

@dataclass
class AuditLog:
    """Immutable ledger record."""
    id: str
    timestamp: datetime
    actor_id: str
    action: str # e.g., 'prompt.published', 'user.suspended'
    resource_id: str
    details: Dict[str, Any]

@dataclass
class Policy:
    """Security rule applied to a workspace or organization."""
    id: str
    type: PolicyType
    configuration: Dict[str, Any] # e.g., {'allowed_ips': ['192.168.1.0/24']}
    is_active: bool = True

@dataclass
class FeatureFlag:
    key: str
    is_enabled: bool = False
    enabled_workspaces: List[str] = field(default_factory=list)
