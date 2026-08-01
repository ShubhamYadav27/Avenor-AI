import logging
from uuid import UUID
from typing import List

from app.modules.enterprise_intelligence.application.engines.buying_committee_engine import BuyingCommitteeEngine

logger = logging.getLogger(__name__)

class BuyingCommitteeWorker:
    """
    Background worker for processing bulk buying committee enrichment (Phase 7, Engine 4).
    """
    def __init__(self, engine: BuyingCommitteeEngine):
        self.engine = engine

    async def bulk_enrich_committees(self, tenant_id: UUID, company_ids: List[UUID]) -> None:
        """
        Processes a batch of companies for buying committee enrichment.
        """
        logger.info(f"Starting bulk buying committee enrichment for {len(company_ids)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for company_id in company_ids:
            try:
                await self.engine.get_or_enrich_committee(tenant_id, company_id, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich committee for company {company_id}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk committee enrichment complete. Success: {success_count}, Failed: {failure_count}")
