from typing import List, Set, Dict
from app.modules.marketplace.domain.models import MarketplaceApp, AppDependency, SemanticVersion
from app.modules.marketplace.domain.exceptions import AppNotFoundError, CircularDependencyError, IncompatibleVersionError
from app.modules.marketplace.domain.ports import AppRepository

class DependencyResolver:
    """
    Enterprise Dependency Graph Resolver.
    Validates version constraints and detects circular dependencies.
    """
    
    def __init__(self, app_repo: AppRepository):
        self.app_repo = app_repo

    async def resolve_dependencies(self, root_app_id: str) -> List[MarketplaceApp]:
        """Returns a flattened, topologically sorted list of required apps for installation."""
        resolved: List[MarketplaceApp] = []
        visited: Set[str] = set()
        visiting: Set[str] = set()

        async def _dfs(app_id: str):
            if app_id in visiting:
                raise CircularDependencyError(f"Circular dependency detected involving {app_id}")
            if app_id in visited:
                return

            visiting.add(app_id)
            
            app = await self.app_repo.get_by_id(app_id)
            if not app:
                raise AppNotFoundError(f"Dependency {app_id} not found in catalog.")

            for dep in app.dependencies:
                dep_app = await self.app_repo.get_by_id(dep.app_id)
                if not dep_app:
                    if not dep.is_optional:
                        raise AppNotFoundError(f"Required dependency {dep.app_id} for {app_id} not found.")
                    continue
                
                # Check version compatibility
                installed_version = SemanticVersion.parse(dep_app.version)
                if not installed_version.satisfies(dep.version_constraint):
                    raise IncompatibleVersionError(
                        f"Dependency {dep.app_id} requires {dep.version_constraint}, but {dep_app.version} is available."
                    )
                
                await _dfs(dep.app_id)

            visiting.remove(app_id)
            visited.add(app_id)
            resolved.append(app)

        await _dfs(root_app_id)
        
        # The first item is the deepest dependency, the last is the root.
        # We return everything EXCEPT the root app itself as the "dependencies to install".
        return [app for app in resolved if app.id != root_app_id]


class UpdateManager:
    """
    Handles Version Upgrades, Rollbacks, and Update Notifications.
    """
    
    def __init__(self, app_repo: AppRepository):
        self.app_repo = app_repo
        
    async def check_for_updates(self, current_app_id: str, current_version: str) -> bool:
        """Determines if a newer version of the app exists in the catalog."""
        app = await self.app_repo.get_by_id(current_app_id)
        if not app:
            return False
            
        catalog_ver = SemanticVersion.parse(app.version)
        local_ver = SemanticVersion.parse(current_version)
        
        # Simple check: If catalog major/minor is higher, an update is available.
        if catalog_ver.major > local_ver.major:
            return True
        if catalog_ver.major == local_ver.major and catalog_ver.minor > local_ver.minor:
            return True
        if catalog_ver.major == local_ver.major and catalog_ver.minor == local_ver.minor and catalog_ver.patch > local_ver.patch:
            return True
            
        return False
