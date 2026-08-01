import pytest
from datetime import datetime
from app.modules.marketplace.domain.models import MarketplaceApp, AppCategory, AppType, AppDependency
from app.modules.marketplace.domain.exceptions import CircularDependencyError, IncompatibleVersionError
from app.modules.marketplace.infrastructure.repositories import InMemoryAppRepository
from app.modules.marketplace.application.enterprise_services import DependencyResolver, UpdateManager

@pytest.fixture
def app_repo():
    return InMemoryAppRepository()

@pytest.fixture
def resolver(app_repo):
    return DependencyResolver(app_repo)

@pytest.fixture
def updater(app_repo):
    return UpdateManager(app_repo)

def create_mock_app(app_id: str, version: str, deps=None):
    return MarketplaceApp(
        id=app_id,
        name=f"App {app_id}",
        description="",
        publisher_id="pub-1",
        category=AppCategory.CRM,
        app_type=AppType.OFFICIAL,
        version=version,
        required_permissions=[],
        capabilities=[],
        dependencies=deps or [],
        published_at=datetime.utcnow()
    )

@pytest.mark.asyncio
async def test_successful_dependency_resolution(app_repo, resolver):
    # App A -> App B -> App C
    app_c = create_mock_app("C", "1.0.0")
    app_b = create_mock_app("B", "2.1.0", deps=[AppDependency(app_id="C", version_constraint=">=1.0.0")])
    app_a = create_mock_app("A", "3.0.0", deps=[AppDependency(app_id="B", version_constraint=">=2.0.0")])
    
    await app_repo.save(app_c)
    await app_repo.save(app_b)
    await app_repo.save(app_a)
    
    resolved = await resolver.resolve_dependencies("A")
    assert len(resolved) == 2
    # Topological sort ensures deepest comes first
    assert resolved[0].id == "C"
    assert resolved[1].id == "B"

@pytest.mark.asyncio
async def test_circular_dependency_detection(app_repo, resolver):
    # App X -> App Y -> App X
    app_y = create_mock_app("Y", "1.0.0", deps=[AppDependency(app_id="X", version_constraint=">=1.0.0")])
    app_x = create_mock_app("X", "1.0.0", deps=[AppDependency(app_id="Y", version_constraint=">=1.0.0")])
    
    await app_repo.save(app_y)
    await app_repo.save(app_x)
    
    with pytest.raises(CircularDependencyError):
        await resolver.resolve_dependencies("X")

@pytest.mark.asyncio
async def test_incompatible_version_detection(app_repo, resolver):
    # App A requires B >= 2.0.0, but catalog only has B 1.5.0
    app_b = create_mock_app("B", "1.5.0")
    app_a = create_mock_app("A", "1.0.0", deps=[AppDependency(app_id="B", version_constraint=">=2.0.0")])
    
    await app_repo.save(app_b)
    await app_repo.save(app_a)
    
    with pytest.raises(IncompatibleVersionError):
        await resolver.resolve_dependencies("A")

@pytest.mark.asyncio
async def test_update_manager_detects_updates(app_repo, updater):
    # Catalog has version 2.5.0
    app = create_mock_app("SFDC", "2.5.0")
    await app_repo.save(app)
    
    # Local install is 2.4.0 (Update available)
    assert await updater.check_for_updates("SFDC", "2.4.0") == True
    
    # Local install is 3.0.0 (Ahead of catalog?)
    assert await updater.check_for_updates("SFDC", "3.0.0") == False
    
    # Local install is 2.5.0 (Up to date)
    assert await updater.check_for_updates("SFDC", "2.5.0") == False
