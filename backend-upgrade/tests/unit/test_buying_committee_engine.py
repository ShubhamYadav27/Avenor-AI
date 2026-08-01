import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.buying_committee import BuyingCommitteeIntelligence, CommitteeMember
from app.modules.enterprise_intelligence.application.engines.buying_committee_engine import BuyingCommitteeEngine

@pytest.mark.asyncio
async def test_get_or_enrich_committee_new_enrichment():
    tenant_id = uuid4()
    company_id = uuid4()
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None  # No existing data
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_external = BuyingCommitteeIntelligence(tenant_id=tenant_id, company_id=company_id)
    
    member1 = CommitteeMember(contact_id=uuid4())
    member1.roles.is_champion = True
    
    member2 = CommitteeMember(contact_id=uuid4())
    member2.roles.is_legal = True
    
    mock_external.members = [member1, member2]
    mock_provider.fetch_committee_data.return_value = mock_external
    
    engine = BuyingCommitteeEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.get_or_enrich_committee(tenant_id, company_id)
    
    assert result.company_id == company_id
    assert result.enrichment_status == "enriched"
    assert len(result.members) == 2
    
    # completeness logic: champion (0.3) + legal (0.1) + base (0.3) = 0.7
    assert result.committee_completeness_score == pytest.approx(0.7)
    
    # Missing economic buyer should trigger high risk
    assert "Economic Buyer" in result.missing_stakeholders
    assert "High Risk" in result.buying_risk_analysis

@pytest.mark.asyncio
async def test_get_or_enrich_committee_existing_stale():
    pass
