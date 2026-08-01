import math
import uuid
from typing import List, Dict, Any

from app.modules.industry_benchmarking.domain.models import (
    Cohort, BenchmarkMetric, PercentileDistribution, BenchmarkInsight, InsightSeverity
)

class PrivacyViolationError(Exception):
    pass

class PrivacyGuard:
    """The strict boundary preventing reverse engineering of anonymous metrics."""
    
    MIN_COHORT_SIZE = 5 # Absolute minimum number of companies required to form an anonymous cohort
    
    @classmethod
    def assert_safe_to_aggregate(cls, cohort: Cohort) -> None:
        if cohort.member_count < cls.MIN_COHORT_SIZE:
            raise PrivacyViolationError(
                f"Privacy Guard Block: Cohort '{cohort.name}' only has {cohort.member_count} members. "
                f"Minimum required is {cls.MIN_COHORT_SIZE} to ensure anonymity."
            )

class PercentileEngine:
    """Calculates statistical distributions from raw anonymous data arrays."""
    
    @staticmethod
    def calculate_distribution(metric: BenchmarkMetric, cohort: Cohort, raw_data: List[float]) -> PercentileDistribution:
        PrivacyGuard.assert_safe_to_aggregate(cohort)
        
        sorted_data = sorted(raw_data)
        n = len(sorted_data)
        
        def get_percentile(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_data[int(k)]
            d0 = sorted_data[int(f)] * (c - k)
            d1 = sorted_data[int(c)] * (k - f)
            return round(d0 + d1, 2)
            
        return PercentileDistribution(
            metric=metric,
            cohort_id=cohort.id,
            sample_size=n,
            p10=get_percentile(0.10),
            p25=get_percentile(0.25),
            median=get_percentile(0.50),
            p75=get_percentile(0.75),
            p90=get_percentile(0.90),
            average=round(sum(sorted_data) / n, 2)
        )

class InsightEngine:
    """Generates human-readable strategic insights based on mathematical positioning."""
    
    @staticmethod
    def generate_insight(metric: BenchmarkMetric, user_value: float, dist: PercentileDistribution) -> BenchmarkInsight:
        
        # Determine if "higher is better" (e.g. Win Rate) or "lower is better" (e.g. Sales Cycle)
        is_higher_better = metric != BenchmarkMetric.SALES_CYCLE_DAYS
        
        if is_higher_better:
            if user_value >= dist.p75:
                severity = InsightSeverity.POSITIVE
                msg = f"Excellent. Your {metric.value} is in the Top 25% of your peer group."
            elif user_value < dist.p25:
                severity = InsightSeverity.NEGATIVE
                msg = f"Action Required: Your {metric.value} is falling behind 75% of your peer group."
            else:
                severity = InsightSeverity.NEUTRAL
                msg = f"You are performing near the median of your peer group for {metric.value}."
        else:
            # Lower is better (Sales Cycle)
            if user_value <= dist.p25:
                severity = InsightSeverity.POSITIVE
                msg = f"Excellent. Your {metric.value} is shorter than 75% of your peer group."
            elif user_value > dist.p75:
                severity = InsightSeverity.NEGATIVE
                msg = f"Action Required: Your {metric.value} is significantly longer than the peer median."
            else:
                severity = InsightSeverity.NEUTRAL
                msg = f"You are performing near the median of your peer group for {metric.value}."
                
        return BenchmarkInsight(
            metric=metric,
            severity=severity,
            message=msg,
            user_value=user_value,
            cohort_median=dist.median
        )
