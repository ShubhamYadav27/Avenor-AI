from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
import uuid
import re

class AppCategory(str, Enum):
    CRM = "CRM"
    SALES = "Sales"
    MARKETING = "Marketing"
    REVENUE_INTELLIGENCE = "Revenue Intelligence"
    FORECASTING = "Forecasting"
    AI = "AI"
    AUTOMATION = "Automation"
    DASHBOARDS = "Dashboards"
    AGENTS = "Agents"
    PROMPTS = "Prompts"
    WORKFLOWS = "Workflows"
    SECURITY = "Security"

class AppType(str, Enum):
    OFFICIAL = "Official"
    PARTNER = "Partner"
    PRIVATE = "Private"
    BETA = "Beta"

class InstallStatus(str, Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    PENDING_PERMISSION = "Pending Permission"
    CONFIGURED = "Configured"
    ACTIVATED = "Activated"
    SUSPENDED = "Suspended"
    DISABLED = "Disabled"
    DEPRECATED = "Deprecated"
    ARCHIVED = "Archived"
    UNINSTALLED = "Uninstalled"

class AppPermission(str, Enum):
    READ_COMPANIES = "read:companies"
    WRITE_COMPANIES = "write:companies"
    READ_CONTACTS = "read:contacts"
    READ_OPPORTUNITIES = "read:opportunities"
    READ_SIGNALS = "read:signals"
    EXECUTE_AI = "execute:ai"
    EXECUTE_WORKFLOW = "execute:workflow"
    MANAGE_DASHBOARD = "manage:dashboard"
    MANAGE_BILLING = "manage:billing"

@dataclass
class SemanticVersion:
    major: int
    minor: int
    patch: int
    
    @classmethod
    def parse(cls, version_str: str) -> 'SemanticVersion':
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str)
        if not match:
            raise ValueError(f"Invalid semantic version: {version_str}")
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
        
    def satisfies(self, constraint: str) -> bool:
        # Simplified semver satisfaction (e.g. ">=1.0.0")
        if constraint.startswith(">="):
            target = SemanticVersion.parse(constraint[2:])
            if self.major > target.major: return True
            if self.major == target.major and self.minor > target.minor: return True
            if self.major == target.major and self.minor == target.minor and self.patch >= target.patch: return True
            return False
        return str(self) == constraint

@dataclass
class AppDependency:
    app_id: str
    version_constraint: str
    is_optional: bool = False

@dataclass
class PublisherProfile:
    id: str
    name: str
    is_verified: bool
    is_official: bool
    website: str
    support_email: str

@dataclass
class AppCapability:
    type: str
    metadata: Dict[str, Any]

@dataclass
class MarketplaceApp:
    id: str
    name: str
    description: str
    publisher_id: str
    category: AppCategory
    app_type: AppType
    version: str
    required_permissions: List[AppPermission]
    capabilities: List[AppCapability]
    dependencies: List[AppDependency]
    published_at: datetime
    is_active: bool = True
    checksum: str = ""

@dataclass
class AppInstallation:
    id: str
    app_id: str
    workspace_id: str
    installed_by: str
    status: InstallStatus
    granted_permissions: List[AppPermission]
    configuration: Dict[str, Any]
    installed_at: datetime
    updated_at: datetime
    current_version: str
    
    def can_execute(self, permission: AppPermission) -> bool:
        return self.status == InstallStatus.ACTIVATED and permission in self.granted_permissions

    @classmethod
    def create(cls, app_id: str, workspace_id: str, installed_by: str, granted_permissions: List[AppPermission], version: str, config: Dict[str, Any] = None):
        return cls(
            id=str(uuid.uuid4()),
            app_id=app_id,
            workspace_id=workspace_id,
            installed_by=installed_by,
            status=InstallStatus.PENDING_PERMISSION,
            granted_permissions=granted_permissions,
            configuration=config or {},
            installed_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            current_version=version
        )
