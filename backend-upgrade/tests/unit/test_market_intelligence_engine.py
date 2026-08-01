import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.market_intelligence import MarketIntelligence, MarketTrend
from app.modules.enterprise_intelligence.application.engines.market_intelligence_engine import MarketIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_market_bullish():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "markettest.com"
    industry = "SaaS"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = MarketIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain, industry=industry)
    
    trend1 = MarketTrend(name="AI Adoption", impact="positive", description="Massive shift to AI")
    trend2 = MarketTrend(name="Cloud Growth", impact="positive", description="Cloud spending up")
    trend3 = MarketTrend(name="Budget Cuts", impact="negative", description="Some budgets tightening")
    mock_external.market_trends = [trend1, trend2, trend3]
    mock_external.regulatory_changes = []
    
    mock_provider.fetch_market_data.return_value = mock_external
    
    engine = MarketIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_market(tenant_id, company_id, domain, industry)
    
    assert result.company_domain == domain
    assert result.industry == "SaaS"
    assert result.enrichment_status == "enriched"
    assert len(result.market_trends) == 3
    
    # Positive ratio = 2/3 = 0.66. Opp score = min(1.0, 0.66 + 0.1) = 0.76
    assert result.opportunity_score == pytest.approx(0.766, rel=1e-2)
    # Negative ratio = 1/3 = 0.33. Risk score = 0.33
    assert result.market_risk_score == pytest.approx(0.333, rel=1e-2)
    
    assert result.market_sentiment == "bullish"
    assert "Upsell existing accounts" in result.expansion_opportunities
    assert "Aggressively target" in result.strategic_market_recommendations

@pytest.mark.asyncio
async def test_get_or_enrich_market_bearish():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "markettest-bear.com"
    industry = "Real Estate"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    mock_external = MarketIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain, industry=industry)
    
    trend1 = MarketTrend(name="Interest Rates", impact="negative", description="Rates up")
    trend2 = MarketTrend(name="Housing Slump", impact="negative", description="Sales down")
    mock_external.market_trends = [trend1, trend2]
    mock_external.regulatory_changes = ["New zoning laws"]
    
    mock_provider.fetch_market_data.return_value = mock_external
    
    engine = MarketIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_market(tenant_id, company_id, domain, industry)
    
    # 2/2 negative = 1.0 + 0.2 reg penalty = 1.2 -> capped at 1.0
    assert result.market_risk_score == 1.0
    assert result.market_sentiment == "bearish"
    assert "Exercise caution" in result.strategic_market_recommendations
