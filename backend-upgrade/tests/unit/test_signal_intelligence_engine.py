import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock

from app.modules.enterprise_intelligence.domain.signal_intelligence import SignalIntelligence, NormalizedSignal
from app.modules.enterprise_intelligence.application.engines.signal_intelligence_engine import SignalIntelligenceEngine

@pytest.mark.asyncio
async def test_process_signals_high_intent():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "signaltest.com"
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = None
    
    async def mock_save(intel):
        return intel
    mock_repo.save = mock_save
    
    mock_provider = AsyncMock()
    mock_provider.fetch_signals.return_value = []
    
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=5)
    
    # 2 buying signals, 1 growth
    s1 = NormalizedSignal(tenant_id=tenant_id, source_type="crm", signal_type="buying", signal_name="Pricing Page Visit", description="Visited pricing", expires_at=future, impact_score=0.9, confidence_score=0.9)
    s2 = NormalizedSignal(tenant_id=tenant_id, source_type="web", signal_type="buying", signal_name="Requested Demo", description="Inbound demo", expires_at=future, impact_score=1.0, confidence_score=1.0)
    s3 = NormalizedSignal(tenant_id=tenant_id, source_type="provider", signal_type="growth", signal_name="Series C Funding", description="Raised $50M", expires_at=future, impact_score=0.8, confidence_score=1.0)
    
    incoming = [s1, s2, s3]
    
    engine = SignalIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.process_signals(tenant_id, company_id, domain, incoming)
    
    assert result.company_domain == domain
    assert result.processing_status == "processed"
    assert len(result.active_signals) == 3
    
    # Buying score = (0.81 + 1.0)/2 + 0.2 = 0.905 + 0.2 = 1.105 -> capped at 1.0
    assert result.composite_buying_window_score == 1.0
    # Growth score = 0.8/1 + 0.1 = 0.9
    assert result.growth_indicator_score == pytest.approx(0.9)
    assert result.risk_indicator_score == 0.0 # No risk signals (returns 0 because sum is 0 and length is 0? wait calc logic says max(1, len)=1, sum=0 -> 0 + 0.0 = 0.0)
    
    assert result.strategic_prioritization_tier == 1
    assert "High priority account" in result.ai_generated_summary
    assert len(result.correlated_events) == 1

@pytest.mark.asyncio
async def test_process_signals_expired():
    tenant_id = uuid4()
    company_id = uuid4()
    domain = "expiretest.com"
    
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=5)
    
    existing_intel = SignalIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=domain)
    s1 = NormalizedSignal(tenant_id=tenant_id, source_type="crm", signal_type="buying", signal_name="Old", description="Old", expires_at=past, impact_score=0.9, confidence_score=0.9)
    existing_intel.active_signals = [s1]
    
    mock_repo = AsyncMock()
    mock_repo.get_by_company_id.return_value = existing_intel
    mock_repo.save = AsyncMock(side_effect=lambda x: x)
    
    mock_provider = AsyncMock()
    mock_provider.fetch_signals.return_value = []
    
    engine = SignalIntelligenceEngine(repository=mock_repo, provider=mock_provider)
    result = await engine.process_signals(tenant_id, company_id, domain)
    
    assert len(result.active_signals) == 0
    assert len(result.historical_signals) == 1
    assert result.composite_buying_window_score == 0.1
    assert result.strategic_prioritization_tier == 3
