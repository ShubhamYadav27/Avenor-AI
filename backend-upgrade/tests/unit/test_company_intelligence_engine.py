import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.company_intelligence import CompanyIntelligence
from app.modules.enterprise_intelligence.application.engines.company_intelligence_engine import CompanyIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_company_new_enrichment():
    tenant_id = uuid4()
    domain = "test-ai.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_domain.return_value = None  # No existing data
    
    # Mock save to just return the passed object
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = CompanyIntelligence(tenant_id=tenant_id, company_domain=domain)
    mock_external.financials.estimated_revenue = 5000000
    mock_provider.fetch_company_data.return_value = mock_external
    
    engine = CompanyIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_company(tenant_id, domain)
    
    assert result.company_domain == domain
    assert result.enrichment_status == "enriched"
    assert result.financials.estimated_revenue == 5000000
    assert result.buying_intent_score == 0.85 # As per mock AI logic > 1M
    assert "growing entity" in result.ai_summary

@pytest.mark.asyncio
async def test_get_or_enrich_company_existing_stale():
    tenant_id = uuid4()
    domain = "test-ai.com"
    
    # Test would simulate existing record older than 30 days...
    pass
