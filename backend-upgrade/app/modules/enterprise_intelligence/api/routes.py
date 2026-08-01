from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.api.dependencies.auth import get_current_user
from app.modules.enterprise_intelligence.application.engines.company_intelligence_engine import CompanyIntelligenceEngine
from app.modules.enterprise_intelligence.domain.company_intelligence import CompanyIntelligence

# Note: In a real app, dependencies would inject the concrete Repository and Provider.
# For now, we mock the dependency resolution.
async def get_company_intelligence_engine() -> CompanyIntelligenceEngine:
    # Dummy mock for DI
    class MockRepo:
        async def get_by_domain(self, tenant, domain): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_company_data(self, domain): 
            return CompanyIntelligence(tenant_id=UUID("00000000-0000-0000-0000-000000000000"), company_domain=domain)
            
    return CompanyIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

router = APIRouter(prefix="/intelligence/companies", tags=["Enterprise Intelligence - Company"])

class CompanyIntelligenceResponse(BaseModel):
    data: CompanyIntelligence

@router.get("/{domain}", response_model=CompanyIntelligenceResponse)
async def get_company_intelligence(
    domain: str,
    force_refresh: bool = Query(False, description="Force a re-enrichment of the company data"),
    current_user = Depends(get_current_user),
    engine: CompanyIntelligenceEngine = Depends(get_company_intelligence_engine)
):
    """
    Retrieve deep intelligence for a specific company domain.
    Aggregates CRM, Public, and Licensed Provider data via Layer 4 AI.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_company(tenant_id=tenant_id, domain=domain, force_refresh=force_refresh)
        return CompanyIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve company intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.contact_intelligence_engine import ContactIntelligenceEngine
from app.modules.enterprise_intelligence.domain.contact_intelligence import ContactIntelligence

async def get_contact_intelligence_engine() -> ContactIntelligenceEngine:
    class MockRepo:
        async def get_by_email(self, tenant, email): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_contact_data(self, email): 
            return ContactIntelligence(tenant_id=UUID("00000000-0000-0000-0000-000000000000"))
            
    return ContactIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class ContactIntelligenceResponse(BaseModel):
    data: ContactIntelligence

@router.get("/contacts/{email}", response_model=ContactIntelligenceResponse)
async def get_contact_intelligence(
    email: str,
    force_refresh: bool = Query(False, description="Force a re-enrichment of the contact data"),
    current_user = Depends(get_current_user),
    engine: ContactIntelligenceEngine = Depends(get_contact_intelligence_engine)
):
    """
    Retrieve deep intelligence for a specific contact email.
    Aggregates CRM, Public, and Licensed Provider data via Layer 4 AI.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_contact(tenant_id=tenant_id, email=email, force_refresh=force_refresh)
        return ContactIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve contact intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.technology_intelligence_engine import TechnologyIntelligenceEngine
from app.modules.enterprise_intelligence.domain.technology_intelligence import TechnologyIntelligence

async def get_technology_intelligence_engine() -> TechnologyIntelligenceEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_technology_data(self, domain): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return TechnologyIntelligence(tenant_id=dummy_uuid, company_id=dummy_uuid, company_domain=domain)
            
    return TechnologyIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class TechnologyIntelligenceResponse(BaseModel):
    data: TechnologyIntelligence

@router.get("/companies/{company_id}/technology", response_model=TechnologyIntelligenceResponse)
async def get_technology_intelligence(
    company_id: UUID,
    domain: str = Query(..., description="The domain of the company to query tech data for"),
    force_refresh: bool = Query(False, description="Force a re-enrichment of the technology data"),
    current_user = Depends(get_current_user),
    engine: TechnologyIntelligenceEngine = Depends(get_technology_intelligence_engine)
):
    """
    Retrieve deep technology landscape intelligence for a company.
    Aggregates Cloud, CRM, Framework, and AI stacks.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_technology(
            tenant_id=tenant_id, 
            company_id=company_id, 
            company_domain=domain,
            force_refresh=force_refresh
        )
        return TechnologyIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve technology intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.buying_committee_engine import BuyingCommitteeEngine
from app.modules.enterprise_intelligence.domain.buying_committee import BuyingCommitteeIntelligence

async def get_buying_committee_engine() -> BuyingCommitteeEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_committee_data(self, company_id): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return BuyingCommitteeIntelligence(tenant_id=dummy_uuid, company_id=company_id)
            
    return BuyingCommitteeEngine(repository=MockRepo(), provider=MockProvider())

class BuyingCommitteeResponse(BaseModel):
    data: BuyingCommitteeIntelligence

@router.get("/companies/{company_id}/committee", response_model=BuyingCommitteeResponse)
async def get_buying_committee_intelligence(
    company_id: UUID,
    force_refresh: bool = Query(False, description="Force a re-enrichment of the buying committee data"),
    current_user = Depends(get_current_user),
    engine: BuyingCommitteeEngine = Depends(get_buying_committee_engine)
):
    """
    Retrieve buying committee intelligence for a company.
    Aggregates contact roles, influence, missing stakeholders, and AI risks.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_committee(
            tenant_id=tenant_id, 
            company_id=company_id,
            force_refresh=force_refresh
        )
        return BuyingCommitteeResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve buying committee intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.funding_intelligence_engine import FundingIntelligenceEngine
from app.modules.enterprise_intelligence.domain.funding_intelligence import FundingIntelligence

async def get_funding_intelligence_engine() -> FundingIntelligenceEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_funding_data(self, domain): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return FundingIntelligence(tenant_id=dummy_uuid, company_id=dummy_uuid, company_domain=domain)
            
    return FundingIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class FundingIntelligenceResponse(BaseModel):
    data: FundingIntelligence

@router.get("/companies/{company_id}/funding", response_model=FundingIntelligenceResponse)
async def get_funding_intelligence(
    company_id: UUID,
    domain: str = Query(..., description="The domain of the company to query funding data for"),
    force_refresh: bool = Query(False, description="Force a re-enrichment of the funding data"),
    current_user = Depends(get_current_user),
    engine: FundingIntelligenceEngine = Depends(get_funding_intelligence_engine)
):
    """
    Retrieve funding intelligence for a company.
    Aggregates funding rounds, investors, growth trend, and buying windows.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_funding(
            tenant_id=tenant_id, 
            company_id=company_id, 
            company_domain=domain,
            force_refresh=force_refresh
        )
        return FundingIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve funding intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.hiring_intelligence_engine import HiringIntelligenceEngine
from app.modules.enterprise_intelligence.domain.hiring_intelligence import HiringIntelligence

async def get_hiring_intelligence_engine() -> HiringIntelligenceEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_hiring_data(self, domain): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return HiringIntelligence(tenant_id=dummy_uuid, company_id=dummy_uuid, company_domain=domain)
            
    return HiringIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class HiringIntelligenceResponse(BaseModel):
    data: HiringIntelligence

@router.get("/companies/{company_id}/hiring", response_model=HiringIntelligenceResponse)
async def get_hiring_intelligence(
    company_id: UUID,
    domain: str = Query(..., description="The domain of the company to query hiring data for"),
    force_refresh: bool = Query(False, description="Force a re-enrichment of the hiring data"),
    current_user = Depends(get_current_user),
    engine: HiringIntelligenceEngine = Depends(get_hiring_intelligence_engine)
):
    """
    Retrieve hiring intelligence for a company.
    Aggregates job postings, department growth, and hiring velocity.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_hiring(
            tenant_id=tenant_id, 
            company_id=company_id, 
            company_domain=domain,
            force_refresh=force_refresh
        )
        return HiringIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve hiring intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.executive_intelligence_engine import ExecutiveIntelligenceEngine
from app.modules.enterprise_intelligence.domain.executive_intelligence import ExecutiveIntelligence

async def get_executive_intelligence_engine() -> ExecutiveIntelligenceEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_executive_data(self, company_id): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return ExecutiveIntelligence(tenant_id=dummy_uuid, company_id=company_id, company_domain="mock.com")
            
    return ExecutiveIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class ExecutiveIntelligenceResponse(BaseModel):
    data: ExecutiveIntelligence

@router.get("/companies/{company_id}/executives", response_model=ExecutiveIntelligenceResponse)
async def get_executive_intelligence(
    company_id: UUID,
    domain: str = Query(..., description="The domain of the company to query executive data for"),
    force_refresh: bool = Query(False, description="Force a re-enrichment of the executive data"),
    current_user = Depends(get_current_user),
    engine: ExecutiveIntelligenceEngine = Depends(get_executive_intelligence_engine)
):
    """
    Retrieve executive intelligence for a company.
    Aggregates executive profiles, influence scores, and strategic priorities.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_executives(
            tenant_id=tenant_id, 
            company_id=company_id, 
            company_domain=domain,
            force_refresh=force_refresh
        )
        return ExecutiveIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve executive intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.competitive_intelligence_engine import CompetitiveIntelligenceEngine
from app.modules.enterprise_intelligence.domain.competitive_intelligence import CompetitiveIntelligence

async def get_competitive_intelligence_engine() -> CompetitiveIntelligenceEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_competitive_data(self, domain): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return CompetitiveIntelligence(tenant_id=dummy_uuid, company_id=dummy_uuid, company_domain=domain)
            
    return CompetitiveIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class CompetitiveIntelligenceResponse(BaseModel):
    data: CompetitiveIntelligence

@router.get("/companies/{company_id}/competitors", response_model=CompetitiveIntelligenceResponse)
async def get_competitive_intelligence(
    company_id: UUID,
    domain: str = Query(..., description="The domain of the company to query competitive data for"),
    force_refresh: bool = Query(False, description="Force a re-enrichment of the competitive data"),
    current_user = Depends(get_current_user),
    engine: CompetitiveIntelligenceEngine = Depends(get_competitive_intelligence_engine)
):
    """
    Retrieve competitive intelligence for a company.
    Aggregates competitors, market positions, risk scores, and displacement opportunities.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_competitive(
            tenant_id=tenant_id, 
            company_id=company_id, 
            company_domain=domain,
            force_refresh=force_refresh
        )
        return CompetitiveIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve competitive intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.market_intelligence_engine import MarketIntelligenceEngine
from app.modules.enterprise_intelligence.domain.market_intelligence import MarketIntelligence

async def get_market_intelligence_engine() -> MarketIntelligenceEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_market_data(self, industry): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return MarketIntelligence(tenant_id=dummy_uuid, company_id=dummy_uuid, company_domain="mock.com", industry=industry)
            
    return MarketIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class MarketIntelligenceResponse(BaseModel):
    data: MarketIntelligence

@router.get("/companies/{company_id}/market", response_model=MarketIntelligenceResponse)
async def get_market_intelligence(
    company_id: UUID,
    domain: str = Query(..., description="The domain of the company"),
    industry: str = Query(..., description="The industry of the company to query market data for"),
    force_refresh: bool = Query(False, description="Force a re-enrichment of the market data"),
    current_user = Depends(get_current_user),
    engine: MarketIntelligenceEngine = Depends(get_market_intelligence_engine)
):
    """
    Retrieve market intelligence for a company based on its industry.
    Aggregates macro trends, sentiment, and risk/opportunity scores.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_market(
            tenant_id=tenant_id, 
            company_id=company_id, 
            company_domain=domain,
            industry=industry,
            force_refresh=force_refresh
        )
        return MarketIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve market intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.industry_intelligence_engine import IndustryIntelligenceEngine
from app.modules.enterprise_intelligence.domain.industry_intelligence import IndustryIntelligence

async def get_industry_intelligence_engine() -> IndustryIntelligenceEngine:
    class MockRepo:
        async def get_by_industry(self, tenant, industry_name): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_industry_data(self, industry_name): 
            # Dummy UUID for the mocked dependency
            dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")
            return IndustryIntelligence(tenant_id=dummy_uuid, industry_name=industry_name)
            
    return IndustryIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class IndustryIntelligenceResponse(BaseModel):
    data: IndustryIntelligence

@router.get("/industries/{industry_name}", response_model=IndustryIntelligenceResponse)
async def get_industry_intelligence(
    industry_name: str,
    force_refresh: bool = Query(False, description="Force a re-enrichment of the industry data"),
    current_user = Depends(get_current_user),
    engine: IndustryIntelligenceEngine = Depends(get_industry_intelligence_engine)
):
    """
    Retrieve deep industry intelligence based on the industry name (e.g. SaaS, Manufacturing).
    Aggregates maturity, digital transformation, and readiness scores.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.get_or_enrich_industry(
            tenant_id=tenant_id, 
            industry_name=industry_name,
            force_refresh=force_refresh
        )
        return IndustryIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve industry intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.signal_intelligence_engine import SignalIntelligenceEngine
from app.modules.enterprise_intelligence.domain.signal_intelligence import SignalIntelligence, NormalizedSignal

async def get_signal_intelligence_engine() -> SignalIntelligenceEngine:
    class MockRepo:
        async def get_by_company_id(self, tenant, company_id): return None
        async def save(self, data): return data
    class MockProvider:
        async def fetch_signals(self, domain): return []
            
    return SignalIntelligenceEngine(repository=MockRepo(), provider=MockProvider())

class SignalIntelligenceResponse(BaseModel):
    data: SignalIntelligence

@router.get("/companies/{company_id}/signals", response_model=SignalIntelligenceResponse)
async def get_signal_intelligence(
    company_id: UUID,
    domain: str = Query(..., description="The domain of the company"),
    current_user = Depends(get_current_user),
    engine: SignalIntelligenceEngine = Depends(get_signal_intelligence_engine)
):
    """
    Retrieve unified signal intelligence for a company.
    Aggregates, correlates, and scores all active and historical signals.
    """
    try:
        tenant_id = current_user.tenant_id
        intelligence = await engine.process_signals(
            tenant_id=tenant_id, 
            company_id=company_id,
            company_domain=domain
        )
        return SignalIntelligenceResponse(data=intelligence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve signal intelligence: {str(e)}")

from app.modules.enterprise_intelligence.application.engines.identity_resolution_engine import IdentityResolutionEngine
from app.modules.enterprise_intelligence.domain.identity_resolution import CanonicalEntity, CompanyIdentity

async def get_identity_resolution_engine() -> IdentityResolutionEngine:
    class MockRepo:
        async def get_by_primary_identifier(self, tenant, entity_type, identifier): return None
        async def get_by_id(self, tenant, entity_id): return None
        async def save(self, data): return data
        async def find_duplicates(self, tenant, entity_type): return []
    class MockProvider:
        async def verify_identity(self, entity_type, identifier): return {}
            
    return IdentityResolutionEngine(repository=MockRepo(), provider=MockProvider())

class CanonicalCompanyResponse(BaseModel):
    data: CompanyIdentity

@router.get("/identity/company/resolve", response_model=CanonicalCompanyResponse)
async def resolve_company_identity(
    domain: str = Query(..., description="The domain to resolve"),
    name: str = Query(..., description="The company name to resolve"),
    current_user = Depends(get_current_user),
    engine: IdentityResolutionEngine = Depends(get_identity_resolution_engine)
):
    """
    Resolve a canonical company identity given a domain and name.
    """
    try:
        tenant_id = current_user.tenant_id
        identity = await engine.resolve_company(
            tenant_id=tenant_id, 
            domain=domain,
            name=name
        )
        return CanonicalCompanyResponse(data=identity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve company identity: {str(e)}")

class MergeCandidatesResponse(BaseModel):
    data: list[CanonicalEntity]

@router.get("/identity/duplicates", response_model=MergeCandidatesResponse)
async def get_duplicate_identities(
    entity_type: str = Query(..., description="The entity type to check for duplicates (e.g. company, contact)"),
    current_user = Depends(get_current_user),
    engine: IdentityResolutionEngine = Depends(get_identity_resolution_engine)
):
    """
    Retrieve entities that have high-confidence AI merge suggestions.
    """
    try:
        tenant_id = current_user.tenant_id
        candidates = await engine.find_merge_candidates(tenant_id, entity_type)
        return MergeCandidatesResponse(data=candidates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve merge candidates: {str(e)}")
