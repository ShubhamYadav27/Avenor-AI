import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.industry_intelligence import IndustryIntelligence, IndustryKPI
from app.modules.enterprise_intelligence.application.engines.industry_intelligence_engine import IndustryIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_industry_hightech():
    tenant_id = uuid4()
    industry_name = "FinTech"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_industry.return_value = None
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = IndustryIntelligence(tenant_id=tenant_id, industry_name=industry_name)
    
    mock_external.lifecycle_stage = "mature"
    mock_external.regulatory_environment = "high"
    kpi = IndustryKPI(name="Average Margin", benchmark_value="60%", description="Gross margin benchmark")
    mock_external.kpis = [kpi]
    
    mock_provider.fetch_industry_data.return_value = mock_external
    
    engine = IndustryIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_industry(tenant_id, industry_name)
    
    assert result.industry_name == industry_name
    assert result.enrichment_status == "enriched"
    assert len(result.kpis) == 1
    
    # AI logic assertions
    assert result.industry_maturity_score == 0.9 # mature
    assert result.digital_transformation_score == 0.9 # FinTech is high tech
    assert result.opportunity_score == 0.8
    assert result.risk_score == 0.8 # high regulatory
    
    # Readiness = (0.8 * 0.5) + (0.9 * 0.3) - (0.8 * 0.2) = 0.40 + 0.27 - 0.16 = 0.51
    assert result.readiness_score == pytest.approx(0.51)
    
    assert "Consensus-based" in result.buying_patterns
    assert "Moderate/Low readiness" in result.strategic_recommendations

@pytest.mark.asyncio
async def test_get_or_enrich_industry_legacy():
    tenant_id = uuid4()
    industry_name = "Manufacturing"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_industry.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    mock_external = IndustryIntelligence(tenant_id=tenant_id, industry_name=industry_name)
    mock_external.lifecycle_stage = "declining"
    mock_external.regulatory_environment = "medium"
    
    mock_provider.fetch_industry_data.return_value = mock_external
    
    engine = IndustryIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_industry(tenant_id, industry_name)
    
    assert result.industry_maturity_score == 1.0 # declining
    assert result.digital_transformation_score == 0.4 # Legacy
    assert result.opportunity_score == 0.9 # High opp for digitization
    assert result.risk_score == 0.4 # Medium reg
    
    # Readiness = (0.9 * 0.5) + (0.4 * 0.3) - (0.4 * 0.2) = 0.45 + 0.12 - 0.08 = 0.49
    assert result.readiness_score == pytest.approx(0.49)
    assert "Relationship-driven" in result.buying_patterns
