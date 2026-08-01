from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.modules.marketplace.domain.models import AppCategory, MarketplaceApp, AppInstallation
from app.modules.marketplace.domain.exceptions import AppNotFoundError, InstallationNotFoundError
from app.modules.marketplace.application.services import AppRegistryService, InstallationManager, PermissionEngine
from app.modules.marketplace.infrastructure.repositories import InMemoryAppRepository, InMemoryInstallationRepository

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# Dependency Injection setup (Simplified for API routes)
_app_repo = InMemoryAppRepository()
_install_repo = InMemoryInstallationRepository()
_permission_engine = PermissionEngine()
_registry_service = AppRegistryService(_app_repo)
_install_manager = InstallationManager(_registry_service, _install_repo, _permission_engine)

def get_registry_service() -> AppRegistryService:
    return _registry_service

def get_installation_manager() -> InstallationManager:
    return _install_manager

# --- Request/Response Models ---

class AppResponse(BaseModel):
    id: str
    name: str
    description: str
    publisher_id: str
    category: str
    app_type: str
    version: str

class InstallRequest(BaseModel):
    app_id: str
    workspace_id: str
    installed_by: str

class ConfigureRequest(BaseModel):
    config: dict

# --- Routes ---

@router.get("/apps", response_model=List[AppResponse])
async def browse_apps(
    category: Optional[AppCategory] = None,
    registry: AppRegistryService = Depends(get_registry_service)
):
    apps = await registry.browse_apps(category)
    return [
        AppResponse(
            id=app.id, name=app.name, description=app.description, 
            publisher_id=app.publisher_id, category=app.category, 
            app_type=app.app_type, version=app.version
        ) for app in apps
    ]

@router.get("/apps/{app_id}", response_model=AppResponse)
async def get_app_details(
    app_id: str,
    registry: AppRegistryService = Depends(get_registry_service)
):
    try:
        app = await registry.get_app(app_id)
        return AppResponse(
            id=app.id, name=app.name, description=app.description, 
            publisher_id=app.publisher_id, category=app.category, 
            app_type=app.app_type, version=app.version
        )
    except AppNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/installations")
async def install_app(
    req: InstallRequest,
    manager: InstallationManager = Depends(get_installation_manager)
):
    try:
        # Pass dummy version '1.0.0' for now, or resolve via registry in real usage
        installation = await manager.initiate_installation(req.app_id, req.workspace_id, req.installed_by)
        return {"installation_id": installation.id, "status": installation.status}
    except AppNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/installations/{installation_id}/configure")
async def configure_app(
    installation_id: str,
    req: ConfigureRequest,
    manager: InstallationManager = Depends(get_installation_manager)
):
    try:
        installation = await manager.configure_and_activate(installation_id, req.config)
        return {"installation_id": installation.id, "status": installation.status}
    except InstallationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workspaces/{workspace_id}/installations")
async def list_workspace_installations(
    workspace_id: str,
    manager: InstallationManager = Depends(get_installation_manager)
):
    installations = await manager.get_workspace_installations(workspace_id)
    return [{"id": i.id, "app_id": i.app_id, "status": i.status} for i in installations]
