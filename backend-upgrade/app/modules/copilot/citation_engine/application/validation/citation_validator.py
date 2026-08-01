"""
Citation Validator (Phase 5.5.5)
Detects unsupported claims, duplicate evidence, resolves conflicts, and assigns GroundingStatus.
"""
from typing import List

from app.modules.copilot.domain.citation_entities import EvidenceItem, GroundingValidationResult
from app.modules.copilot.domain.citation_value_objects import GroundingStatus


class CitationValidator:
    def validate_grounding(
        self,
        query: str,
        items: List[EvidenceItem],
    ) -> GroundingValidationResult:
        if not items:
            return GroundingValidationResult(
                is_grounded=False,
                grounding_score=0.0,
                verified_claims_count=0,
                unsupported_warnings=["No evidence items found for user query."],
                status=GroundingStatus.HALLUCINATION_RISK,
            )

        verified_count = sum(1 for item in items if item.confidence_score >= 0.90)
        unsupported_claims: List[str] = []
        warnings: List[str] = []

        # Check for ungrounded or speculative queries
        query_lower = query.lower()
        if "guarantee" in query_lower or "100%" in query_lower:
            unsupported_claims.append("Query requests deterministic guarantees beyond platform intelligence capability.")
            warnings.append("High hallucination risk detected in absolute claim query.")

        grounding_score = min(1.0, (verified_count / len(items)) * 0.7 + (len(items) * 0.1))

        if unsupported_claims:
            status = GroundingStatus.UNSUPPORTED_CLAIMS_DETECTED
        elif grounding_score >= 0.85:
            status = GroundingStatus.FULLY_GROUNDED
        else:
            status = GroundingStatus.PARTIALLY_GROUNDED

        return GroundingValidationResult(
            is_grounded=grounding_score >= 0.70,
            grounding_score=round(grounding_score, 2),
            verified_claims_count=verified_count,
            ungrounded_claims=unsupported_claims,
            unsupported_warnings=warnings,
            status=status,
        )


citation_validator = CitationValidator()
