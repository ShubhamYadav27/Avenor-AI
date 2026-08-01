import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.hiring_intelligence import HiringIntelligence, JobPosting
from app.modules.enterprise_intelligence.application.engines.hiring_intelligence_engine import HiringIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_hiring_accelerating():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "hiretest.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = HiringIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    
    # 30 open roles to trigger "accelerating" (momentum > 0.7 since 30/25 = 1.2 which is > 0.7)
    now = datetime.now(timezone.utc)
    mock_external.open_roles = [
        JobPosting(title="Software Engineer", department="Engineering", location="Remote", date_posted=now)
        for _ in range(15)
    ] + [
        JobPosting(title="Account Executive", department="Sales", location="NY", date_posted=now)
        for _ in range(15)
    ]
    mock_provider.fetch_hiring_data.return_value = mock_external
    
    engine = HiringIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_hiring(tenant_id, company_id, domain)
    
    assert result.company_domain == domain
    assert result.enrichment_status == "enriched"
    assert result.total_open_roles == 30
    assert result.department_counts["Engineering"] == 15
    assert result.department_counts["Sales"] == 15
    
    assert result.hiring_velocity == "accelerating"
    assert result.buying_window_impact == "high"
    
    assert any("technical scale-up" in x for x in result.technology_adoption_indicators)
    assert any("GTM expansion" in x for x in result.revenue_expansion_indicators)

@pytest.mark.asyncio
async def test_get_or_enrich_hiring_frozen():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "hiretest-frozen.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    mock_external = HiringIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    mock_external.open_roles = []
    mock_provider.fetch_hiring_data.return_value = mock_external
    
    engine = HiringIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_hiring(tenant_id, company_id, domain)
    
    assert result.total_open_roles == 0
    assert result.hiring_velocity == "frozen"
    assert result.buying_window_impact == "low"
    assert "No active hiring detected" in result.ai_summary
