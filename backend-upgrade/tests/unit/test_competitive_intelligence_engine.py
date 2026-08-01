import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.competitive_intelligence import CompetitiveIntelligence, Competitor
from app.modules.enterprise_intelligence.application.engines.competitive_intelligence_engine import CompetitiveIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_competitive_high_risk():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "comptest.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = CompetitiveIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    
    comp1 = Competitor(name="LegacyCRM", domain="legacycrm.com", is_direct=True, market_position="leader")
    comp2 = Competitor(name="LegacySales", domain="legacysales.com", is_direct=True, market_position="leader")
    comp3 = Competitor(name="NicheTool", domain="nichetool.com", is_direct=True, market_position="niche")
    mock_external.competitors = [comp1, comp2, comp3]
    
    mock_provider.fetch_competitive_data.return_value = mock_external
    
    engine = CompetitiveIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_competitive(tenant_id, company_id, domain)
    
    assert result.company_domain == domain
    assert result.enrichment_status == "enriched"
    assert len(result.competitors) == 3
    
    # 3 direct competitors * 0.1 = 0.3
    # 2 leaders * 0.2 = 0.4
    # Total = 0.7 risk
    assert result.competitive_risk_score == pytest.approx(0.7)
    
    assert any("Displace LegacyCRM" in op for op in result.displacement_opportunities)
    assert any("lacks advanced AI" in gap for gap in result.feature_gaps)
    assert "Block NicheTool" in "".join(result.displacement_opportunities)

@pytest.mark.asyncio
async def test_get_or_enrich_competitive_no_data():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "comptest-empty.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    mock_external = CompetitiveIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    mock_provider.fetch_competitive_data.return_value = mock_external
    
    engine = CompetitiveIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_competitive(tenant_id, company_id, domain)
    
    assert len(result.competitors) == 0
    assert result.competitive_risk_score == 0.1
    assert "No major competitors detected" in result.ai_summary
