import logging
from uuid import UUID
from typing import List, Tuple

from app.modules.enterprise_intelligence.application.engines.signal_intelligence_engine import SignalIntelligenceEngine

logger = logging.getLogger(__name__)

class SignalProcessingWorker:
    """
    Background worker for processing unified signal streams (Phase 7, Engine 11).
    """
    def __init__(self, engine: SignalIntelligenceEngine):
        self.engine = engine

    async def batch_process_signals(self, tenant_id: UUID, companies: List[Tuple[UUID, str]]) -> None:
        """
        Processes pending signals for a batch of companies.
        """
        logger.info(f"Starting batch signal processing for {len(companies)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for company_id, domain in companies:
            try:
                await self.engine.process_signals(tenant_id, company_id, domain)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to process signals for {domain}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Batch signal processing complete. Success: {success_count}, Failed: {failure_count}")
