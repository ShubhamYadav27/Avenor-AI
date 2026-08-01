import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.contact_intelligence import ContactIntelligence
from app.modules.enterprise_intelligence.application.engines.contact_intelligence_engine import ContactIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_contact_new_enrichment():
    tenant_id = uuid4()
    email = "test@ai.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None  # No existing data
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = ContactIntelligence(tenant_id=tenant_id)
    mock_external.profile.seniority = "VP"
    mock_external.communication.email = email
    mock_provider.fetch_contact_data.return_value = mock_external
    
    engine = ContactIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_contact(tenant_id, email)
    
    assert result.communication.email == email
    assert result.enrichment_status == "enriched"
    assert result.profile.seniority == "VP"
    assert result.influence_score == 0.95 # As per mock AI logic for VP
    assert "strong purchasing influence" in result.ai_summary

@pytest.mark.asyncio
async def test_get_or_enrich_contact_existing_stale():
    tenant_id = uuid4()
    email = "stale@ai.com"
    
    pass
