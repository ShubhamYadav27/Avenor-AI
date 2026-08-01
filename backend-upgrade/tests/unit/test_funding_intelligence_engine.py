import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.funding_intelligence import FundingIntelligence, FundingRound, Investor
from app.modules.enterprise_intelligence.application.engines.funding_intelligence_engine import FundingIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_funding_recent_round():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "fundtest.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = FundingIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    mock_external.total_funding = 50_000_000
    
    recent_date = datetime.now(timezone.utc) - timedelta(days=30)
    round_a = FundingRound(round_type="Series B", amount_raised=45_000_000, date_announced=recent_date)
    mock_external.funding_rounds = [round_a]
    mock_external.last_funding_date = recent_date
    mock_provider.fetch_funding_data.return_value = mock_external
    
    engine = FundingIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_funding(tenant_id, company_id, domain)
    
    assert result.company_domain == domain
    assert result.enrichment_status == "enriched"
    assert result.capital_growth_trend == "accelerating"
    
    # Recent funding (under 180 days) triggers high buying window
    assert result.buying_window_impact == "high"
    assert result.hiring_probability == 0.90
    assert "Series B" in result.ai_summary

@pytest.mark.asyncio
async def test_get_or_enrich_funding_no_rounds():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "fundtest-no-rounds.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    mock_external = FundingIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    mock_provider.fetch_funding_data.return_value = mock_external
    
    engine = FundingIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_funding(tenant_id, company_id, domain)
    
    assert result.buying_window_impact == "low"
    assert "Organic growth" in result.ai_summary
