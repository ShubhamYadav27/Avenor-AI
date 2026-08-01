import logging
from uuid import UUID
from typing import List, Tuple

from app.modules.enterprise_intelligence.application.engines.funding_intelligence_engine import FundingIntelligenceEngine

logger = logging.getLogger(__name__)

class FundingEnrichmentWorker:
    """
    Background worker for processing bulk funding enrichment (Phase 7, Engine 5).
    """
    def __init__(self, engine: FundingIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_funding(self, tenant_id: UUID, companies: List[Tuple[UUID, str]]) -> None:
        """
        Processes a batch of companies (id, domain tuples) for funding enrichment.
        """
        logger.info(f"Starting bulk funding enrichment for {len(companies)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for company_id, domain in companies:
            try:
                await self.engine.get_or_enrich_funding(tenant_id, company_id, domain, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich funding for {domain}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk funding enrichment complete. Success: {success_count}, Failed: {failure_count}")
