import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.executive_intelligence import ExecutiveIntelligence, ExecutiveProfile
from app.modules.enterprise_intelligence.application.engines.executive_intelligence_engine import ExecutiveIntelligenceEngine

@pytest.mark.asyncio
async def test_get_or_enrich_executives_high_influence():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "exectest.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = ExecutiveIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    
    exec1 = ExecutiveProfile(contact_id=uuid4(), title="CEO", role_classification="CEO", decision_authority="high", influence_score=0.9, strategic_priorities=["Revenue Growth", "AI Adoption"])
    exec2 = ExecutiveProfile(contact_id=uuid4(), title="CFO", role_classification="CFO", decision_authority="high", influence_score=0.85, strategic_priorities=["Cost Control"])
    mock_external.executives = [exec1, exec2]
    mock_external.recent_leadership_changes = ["New CFO appointed 2 months ago"]
    
    mock_provider.fetch_executive_data.return_value = mock_external
    
    engine = ExecutiveIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_executives(tenant_id, company_id, domain)
    
    assert result.company_domain == domain
    assert result.enrichment_status == "enriched"
    assert len(result.executives) == 2
    
    # High influence: 2/2 high authority execs + 0.2 base bonus = 1.2 capped at 1.0
    assert result.executive_buying_influence_score == pytest.approx(1.0)
    assert len(result.overall_strategic_priorities) == 3
    assert "Cost Control" in result.overall_strategic_priorities
    
    # Leadership changes trigger moderate risk
    assert "Moderate Risk" in result.executive_risk_analysis
    assert "New executives" in result.strategic_opportunity_detection

@pytest.mark.asyncio
async def test_get_or_enrich_executives_no_data():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "exectest-empty.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    mock_external = ExecutiveIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    mock_provider.fetch_executive_data.return_value = mock_external
    
    engine = ExecutiveIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_executives(tenant_id, company_id, domain)
    
    assert len(result.executives) == 0
    assert result.executive_buying_influence_score == 0.0
    assert "High Risk" in result.executive_risk_analysis
