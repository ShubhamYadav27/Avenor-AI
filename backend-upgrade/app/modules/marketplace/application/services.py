from typing import List, Optional, Dict, Any
from datetime import datetime

from app.modules.marketplace.domain.models import MarketplaceApp, AppInstallation, AppCategory, InstallStatus, AppPermission
from app.modules.marketplace.domain.ports import AppRepository, InstallationRepository
from app.modules.marketplace.domain.exceptions import AppNotFoundError, InstallationNotFoundError, PermissionDeniedError, InvalidAppConfigurationError

class PermissionEngine:
    """Validates requested capabilities against the Workspace/Tenant rules."""
    
    def validate_permissions(self, requested: List[AppPermission], workspace_id: str) -> List[AppPermission]:
        """
        In a real scenario, this checks the tenant's license tier and user's RBAC scope.
        For now, we grant all requested permissions.
        """
        return requested

class AppRegistryService:
    """Manages the global Marketplace Catalog."""
    
    def __init__(self, app_repo: AppRepository):
        self.app_repo = app_repo
        
    async def get_app(self, app_id: str) -> MarketplaceApp:
        app = await self.app_repo.get_by_id(app_id)
        if not app:
            raise AppNotFoundError(f"App {app_id} not found in marketplace catalog.")
        return app
        
    async def browse_apps(self, category: Optional[AppCategory] = None) -> List[MarketplaceApp]:
        return await self.app_repo.list_active_apps(category)
        
    async def publish_app(self, app: MarketplaceApp) -> MarketplaceApp:
        # In real life, validates metadata, sandbox tests, etc.
        await self.app_repo.save(app)
        return app

class InstallationManager:
    """Orchestrates the App Installation Lifecycle into a Workspace."""
    
    def __init__(self, app_registry: AppRegistryService, install_repo: InstallationRepository, permission_engine: PermissionEngine):
        self.app_registry = app_registry
        self.install_repo = install_repo
        self.permission_engine = permission_engine
        
    async def initiate_installation(self, app_id: str, workspace_id: str, installed_by: str) -> AppInstallation:
        """Starts the installation flow."""
        # 1. Verify App exists
        app = await self.app_registry.get_app(app_id)
        
        # 2. Check if already installed
        existing = await self.install_repo.get_by_app_and_workspace(app_id, workspace_id)
        if existing:
            return existing
            
        # 3. Request permissions
        granted_permissions = self.permission_engine.validate_permissions(app.required_permissions, workspace_id)
        
        # 4. Create pending installation
        installation = AppInstallation.create(
            app_id=app_id,
            workspace_id=workspace_id,
            installed_by=installed_by,
            granted_permissions=granted_permissions,
            version=app.version,
            config={}
        )
        
        await self.install_repo.save(installation)
        return installation
        
    async def configure_and_activate(self, installation_id: str, config: Dict[str, Any]) -> AppInstallation:
        """Completes the installation by applying configuration and activating."""
        installation = await self.install_repo.get_by_id(installation_id)
        if not installation:
            raise InstallationNotFoundError(f"Installation {installation_id} not found.")
            
        installation.configuration = config
        installation.status = InstallStatus.ACTIVATED
        installation.updated_at = datetime.utcnow()
        
        await self.install_repo.save(installation)
        return installation
        
    async def get_workspace_installations(self, workspace_id: str) -> List[AppInstallation]:
        return await self.install_repo.list_by_workspace(workspace_id)
