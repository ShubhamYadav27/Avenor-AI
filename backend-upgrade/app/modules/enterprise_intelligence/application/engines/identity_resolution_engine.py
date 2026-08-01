import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.identity_resolution import CanonicalEntity, CompanyIdentity, ContactIdentity, MergeCandidate
from app.modules.enterprise_intelligence.domain.repositories import IdentityResolutionRepository, IdentityProvider

logger = logging.getLogger(__name__)

class IdentityResolutionEngine:
    """
    Core Application Service for the Identity Resolution Engine (Phase 7, Engine 12).
    Acts as the canonical identity layer for the entire AVENOR-AI platform.
    Eliminates duplicates, merges entities, and normalizes domains/emails.
    """
    def __init__(
        self,
        repository: IdentityResolutionRepository,
        provider: IdentityProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def resolve_company(
        self, 
        tenant_id: UUID, 
        domain: str, 
        name: str
    ) -> CompanyIdentity:
        """
        Resolves a canonical company identity given a domain and name.
        """
        normalized_domain = domain.lower().strip().replace("www.", "")
        existing = await self.repository.get_by_primary_identifier(tenant_id, "company", normalized_domain)
        
        if existing and isinstance(existing, CompanyIdentity):
            return await self._apply_proprietary_ai(existing)
            
        logger.info(f"Creating new canonical company identity for {normalized_domain}")
        new_identity = CompanyIdentity(
            tenant_id=tenant_id,
            primary_identifier=normalized_domain,
            canonical_name=name,
            domains=[normalized_domain]
        )
        return await self.repository.save(await self._apply_proprietary_ai(new_identity))
        
    async def resolve_contact(
        self, 
        tenant_id: UUID, 
        email: str, 
        name: str,
        company_domain: Optional[str] = None
    ) -> ContactIdentity:
        """
        Resolves a canonical contact identity given an email and name.
        """
        normalized_email = email.lower().strip()
        existing = await self.repository.get_by_primary_identifier(tenant_id, "contact", normalized_email)
        
        if existing and isinstance(existing, ContactIdentity):
            return await self._apply_proprietary_ai(existing)
            
        logger.info(f"Creating new canonical contact identity for {normalized_email}")
        new_identity = ContactIdentity(
            tenant_id=tenant_id,
            primary_identifier=normalized_email,
            canonical_name=name,
            emails=[normalized_email]
        )
        
        # Link to company if domain is provided
        if company_domain:
            company = await self.resolve_company(tenant_id, company_domain, company_domain.split('.')[0])
            new_identity.company_id = company.id
            
        return await self.repository.save(await self._apply_proprietary_ai(new_identity))

    async def find_merge_candidates(self, tenant_id: UUID, entity_type: str) -> List[CanonicalEntity]:
        """
        Finds entities of the specified type that have high-confidence merge candidates.
        """
        duplicates = await self.repository.find_duplicates(tenant_id, entity_type)
        results = []
        for dup in duplicates:
            # Re-run AI to ensure merge candidates are fresh
            processed = await self._apply_proprietary_ai(dup)
            if processed.merge_candidates:
                results.append(processed)
        return results

    async def _apply_proprietary_ai(self, identity: CanonicalEntity) -> CanonicalEntity:
        """
        Layer 4: Avenor's Proprietary AI models for Entity Matching and Duplicate Detection.
        Simulates fuzzy matching, alias detection, and generating merge candidates.
        """
        # In a real system, this would query an embedded vector store or ML model
        # to find highly similar entities (e.g. "Acme Corp" vs "Acme Corporation").
        
        if identity.entity_type == "company":
            # Mock fuzzy matching logic
            if "inc" in identity.canonical_name.lower() or "corp" in identity.canonical_name.lower():
                identity.resolution_confidence = 0.95
                identity.ai_generated_explanation = "High confidence canonical match. Standardized legal suffixes removed during comparison."
                
                # Mock a merge candidate discovery
                if len(identity.merge_candidates) == 0:
                    mock_dup_id = UUID("11111111-1111-1111-1111-111111111111")
                    if identity.id != mock_dup_id:
                        identity.merge_candidates.append(MergeCandidate(
                            target_id=mock_dup_id,
                            confidence_score=0.88,
                            reason="High fuzzy match on canonical name (Acme Corp vs Acme Corporation)."
                        ))
            else:
                identity.resolution_confidence = 0.80
                identity.ai_generated_explanation = "Standard entity resolution."
                
        elif identity.entity_type == "contact":
            if "+" in identity.primary_identifier: # e.g. john+sales@acme.com
                identity.resolution_confidence = 0.99
                identity.ai_generated_explanation = "Identified and normalized sub-addressing alias."
            else:
                identity.resolution_confidence = 0.90
                identity.ai_generated_explanation = "Standard contact resolution."
                
        return identity
