import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.cross_customer_intelligence.domain.models import (
    ConsentStatus, AnonymousSignal, SignalType, SignalBucket, Pattern, CollectiveInsight
)

class ConsentRequiredError(Exception):
    pass

class ConsentManager:
    """Manages explicit opt-in/opt-out for collective intelligence."""
    
    # In-memory mock DB for consent
    _consent_db: Dict[str, ConsentStatus] = {}
    
    @classmethod
    def set_consent(cls, org_id: str, is_opted_in: bool, user_id: str) -> ConsentStatus:
        status = ConsentStatus(
            organization_id=org_id,
            is_opted_in=is_opted_in,
            audit_user_id=user_id
        )
        cls._consent_db[org_id] = status
        return status
        
    @classmethod
    def get_consent(cls, org_id: str) -> bool:
        """Returns True only if explicitly opted in."""
        status = cls._consent_db.get(org_id)
        return status.is_opted_in if status else False

class PrivacyGuard:
    """Strict anonymization boundary. Prevents PII from entering the intelligence cloud."""
    
    @staticmethod
    def anonymize_signal(org_id: str, cohort_name: str, signal_type: SignalType, raw_value: float) -> AnonymousSignal:
        """
        Takes raw data, verifies consent, strips org_id, and buckets the raw value.
        """
        if not ConsentManager.get_consent(org_id):
            raise ConsentRequiredError(f"Privacy Block: Organization {org_id} has not explicitly opted into Collective Intelligence.")
            
        # Bucket logic (simplified for mockup)
        bucket = SignalBucket.STABLE
        if raw_value > 10.0:
            bucket = SignalBucket.HIGH_GROWTH
        elif raw_value < -10.0:
            bucket = SignalBucket.DECLINING
            
        # Hard override for boolean-like signals
        if signal_type == SignalType.BUYING_WINDOW:
            bucket = SignalBucket.ACTIVE if raw_value > 0 else SignalBucket.INACTIVE
            
        return AnonymousSignal(
            id=f"anon_{uuid.uuid4().hex[:8]}",
            anonymized_cohort_id=cohort_name, # Preserves industry context without identity
            signal_type=signal_type,
            bucketed_value=bucket
        )

class PatternDiscoveryEngine:
    """Discovers correlations between anonymous events."""
    
    @staticmethod
    def discover_patterns(signals: List[AnonymousSignal]) -> List[Pattern]:
        """
        Mock implementation: Scans signals to find pairs.
        In reality, this would be a massive MapReduce or Spark job finding statistical correlations over time windows.
        """
        patterns = []
        
        # Hardcoded mockup of a discovered pattern for demonstration
        # If we see High Engineering Hiring, we often see Active Buying Windows.
        patterns.append(
            Pattern(
                id=f"pat_{uuid.uuid4().hex[:8]}",
                trigger_signal=SignalType.ENGINEERING_HIRING,
                trigger_value=SignalBucket.HIGH_GROWTH,
                outcome_signal=SignalType.BUYING_WINDOW,
                outcome_value=SignalBucket.ACTIVE,
                confidence_score=0.82,
                occurrence_count=14500 # Discovered across 14,500 anonymous orgs
            )
        )
        
        return patterns

class InsightEngine:
    """Translates raw mathematical patterns into executive intelligence."""
    
    @staticmethod
    def generate_insight(pattern: Pattern) -> CollectiveInsight:
        trigger_str = pattern.trigger_signal.value.replace("_", " ")
        outcome_str = pattern.outcome_signal.value.replace("_", " ")
        
        message = (
            f"Organizations experiencing {pattern.trigger_value.value} {trigger_str} "
            f"are highly likely to show {pattern.outcome_value.value} {outcome_str}. "
            f"(Confidence: {pattern.confidence_score*100:.0f}%, based on {pattern.occurrence_count:,} anonymous observations)"
        )
        
        return CollectiveInsight(
            id=f"ins_{uuid.uuid4().hex[:8]}",
            pattern_id=pattern.id,
            message=message.capitalize(),
            confidence_score=pattern.confidence_score
        )
