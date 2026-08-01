"""
Evidence Normalizer (Phase 5.5.5)
Normalizes raw evidence text, calculates quality metrics, strips noise, and formats uniform evidence objects.
"""
from typing import List

from app.modules.copilot.domain.citation_entities import EvidenceItem
from app.modules.copilot.domain.citation_value_objects import EvidenceQuality


class EvidenceNormalizer:
    def normalize_items(self, items: List[EvidenceItem]) -> List[EvidenceItem]:
        normalized: List[EvidenceItem] = []
        for item in items:
            text = item.raw_content.strip()
            if not text or len(text) < 5:
                continue

            # Assign quality tier
            if item.confidence_score >= 0.95:
                quality = EvidenceQuality.VERIFIED
            elif item.confidence_score >= 0.80:
                quality = EvidenceQuality.HIGH_CONFIDENCE
            elif item.confidence_score >= 0.60:
                quality = EvidenceQuality.MEDIUM_CONFIDENCE
            else:
                quality = EvidenceQuality.UNVERIFIED

            item.quality = quality
            item.normalized_text = text
            normalized.append(item)

        return normalized


evidence_normalizer = EvidenceNormalizer()
