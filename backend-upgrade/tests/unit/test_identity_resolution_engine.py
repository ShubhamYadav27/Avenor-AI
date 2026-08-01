import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.identity_resolution import CompanyIdentity, ContactIdentity
from app.modules.enterprise_intelligence.application.engines.identity_resolution_engine import IdentityResolutionEngine

@pytest.mark.asyncio
async def test_resolve_company_new():
    tenant_id = uuid4()
    domain = "  WWW.AcmeCorp.com  "
    name = "Acme Corp"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_primary_identifier.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    
    engine = IdentityResolutionEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.resolve_company(tenant_id, domain, name)
    
    assert result.primary_identifier == "acmecorp.com"
    assert result.canonical_name == "Acme Corp"
    assert result.resolution_confidence == 0.95
    assert "inc" in name.lower() or "corp" in name.lower()
    assert len(result.merge_candidates) == 1
    assert result.merge_candidates[0].confidence_score == 0.88

@pytest.mark.asyncio
async def test_resolve_company_existing():
    tenant_id = uuid4()
    domain = "acmecorp.com"
    name = "Acme Corp"
    
    existing = CompanyIdentity(tenant_id=tenant_id, primary_identifier=domain, canonical_name=name)
    
    mock_repo = AsyncMock()
    mock_repo.get_by_primary_identifier.return_value = existing
    
    mock_provider = AsyncMock()
    
    engine = IdentityResolutionEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.resolve_company(tenant_id, domain, name)
    
    assert result.id == existing.id
    assert result.resolution_confidence == 0.95

@pytest.mark.asyncio
async def test_resolve_contact_alias():
    tenant_id = uuid4()
    email = "john+sales@acme.com"
    name = "John Doe"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_primary_identifier.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    
    engine = IdentityResolutionEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.resolve_contact(tenant_id, email, name)
    
    assert result.primary_identifier == "john+sales@acme.com"
    assert result.resolution_confidence == 0.99
    assert "sub-addressing" in result.ai_generated_explanation
