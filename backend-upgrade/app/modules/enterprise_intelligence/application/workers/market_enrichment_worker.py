import logging
from uuid import UUID
from typing import List, Tuple

from app.modules.enterprise_intelligence.application.engines.market_intelligence_engine import MarketIntelligenceEngine

logger = logging.getLogger(__name__)

class MarketEnrichmentWorker:
    """
    Background worker for processing bulk market enrichment (Phase 7, Engine 9).
    """
    def __init__(self, engine: MarketIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_market(self, tenant_id: UUID, companies: List[Tuple[UUID, str, str]]) -> None:
        """
        Processes a batch of companies (id, domain, industry tuples) for market enrichment.
        """
        logger.info(f"Starting bulk market enrichment for {len(companies)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for company_id, domain, industry in companies:
            try:
                await self.engine.get_or_enrich_market(tenant_id, company_id, domain, industry, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich market data for {domain} ({industry}): {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk market enrichment complete. Success: {success_count}, Failed: {failure_count}")
