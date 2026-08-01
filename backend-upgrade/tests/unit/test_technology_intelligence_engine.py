import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.technology_intelligence import TechnologyIntelligence, TechnologyItem
from app.modules.enterprise_intelligence.application.engines.technology_intelligence_engine import TechnologyIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_technology_new_enrichment():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "tech-test.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None  # No existing data
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = TechnologyIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    mock_external.stack.cloud_providers.append(TechnologyItem(name="AWS", category="Cloud Provider"))
    mock_external.stack.crm.append(TechnologyItem(name="Salesforce", category="CRM"))
    mock_provider.fetch_technology_data.return_value = mock_external
    
    engine = TechnologyIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_technology(tenant_id, company_id, domain)
    
    assert result.company_domain == domain
    assert result.enrichment_status == "enriched"
    assert len(result.stack.cloud_providers) == 1
    assert result.stack.cloud_providers[0].name == "AWS"
    
    # Cloud + CRM = 0.5 + 0.2 + 0.2 = 0.9 maturity score
    assert result.maturity_score == pytest.approx(0.9)
    assert result.fit_score == 0.85 # Has CRM
    assert "strong cloud infrastructure and CRM adoption" in result.ai_summary

@pytest.mark.asyncio
async def test_get_or_enrich_technology_existing_stale():
    pass
