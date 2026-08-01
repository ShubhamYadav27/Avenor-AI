from typing import Protocol, List, Optional
from app.modules.marketplace.domain.models import MarketplaceApp, AppInstallation, AppCategory

class AppRepository(Protocol):
    """Port for interacting with the Global Marketplace App Catalog."""
    
    async def save(self, app: MarketplaceApp) -> None:
        ...
        
    async def get_by_id(self, app_id: str) -> Optional[MarketplaceApp]:
        ...
        
    async def list_active_apps(self, category: Optional[AppCategory] = None) -> List[MarketplaceApp]:
        ...

class InstallationRepository(Protocol):
    """Port for interacting with Workspace-specific App Installations."""
    
    async def save(self, installation: AppInstallation) -> None:
        ...
        
    async def get_by_id(self, installation_id: str) -> Optional[AppInstallation]:
        ...
        
    async def get_by_app_and_workspace(self, app_id: str, workspace_id: str) -> Optional[AppInstallation]:
        ...
        
    async def list_by_workspace(self, workspace_id: str) -> List[AppInstallation]:
        ...
