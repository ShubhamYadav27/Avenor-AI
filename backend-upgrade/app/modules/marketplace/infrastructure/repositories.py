from typing import List, Optional, Dict
from app.modules.marketplace.domain.models import MarketplaceApp, AppInstallation, AppCategory
from app.modules.marketplace.domain.ports import AppRepository, InstallationRepository

class InMemoryAppRepository(AppRepository):
    """
    In-Memory implementation of AppRepository for testing and rapid development.
    In production, this is swapped via Dependency Injection with SQLAlchemyAppRepository.
    """
    def __init__(self):
        self._apps: Dict[str, MarketplaceApp] = {}
        
    async def save(self, app: MarketplaceApp) -> None:
        self._apps[app.id] = app
        
    async def get_by_id(self, app_id: str) -> Optional[MarketplaceApp]:
        return self._apps.get(app_id)
        
    async def list_active_apps(self, category: Optional[AppCategory] = None) -> List[MarketplaceApp]:
        apps = [app for app in self._apps.values() if app.is_active]
        if category:
            apps = [app for app in apps if app.category == category]
        return apps


class InMemoryInstallationRepository(InstallationRepository):
    """
    In-Memory implementation of InstallationRepository.
    """
    def __init__(self):
        self._installations: Dict[str, AppInstallation] = {}
        
    async def save(self, installation: AppInstallation) -> None:
        self._installations[installation.id] = installation
        
    async def get_by_id(self, installation_id: str) -> Optional[AppInstallation]:
        return self._installations.get(installation_id)
        
    async def get_by_app_and_workspace(self, app_id: str, workspace_id: str) -> Optional[AppInstallation]:
        for inst in self._installations.values():
            if inst.app_id == app_id and inst.workspace_id == workspace_id:
                return inst
        return None
        
    async def list_by_workspace(self, workspace_id: str) -> List[AppInstallation]:
        return [inst for inst in self._installations.values() if inst.workspace_id == workspace_id]
