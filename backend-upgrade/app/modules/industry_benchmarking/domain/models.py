from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class BenchmarkMetric(str, Enum):
    WIN_RATE = "win_rate"
    SALES_CYCLE_DAYS = "sales_cycle_days"
    REVENUE_GROWTH = "revenue_growth"
    PIPELINE_COVERAGE = "pipeline_coverage"

class InsightSeverity(str, Enum):
    POSITIVE = "positive" # e.g. Outperforming peer group
    NEUTRAL = "neutral"
    NEGATIVE = "negative" # e.g. Underperforming, action required

@dataclass
class CohortFilters:
    """Dimensions that define the anonymous peer group."""
    industry: Optional[str] = None
    employee_count_range: Optional[str] = None # e.g. "100-500"
    region: Optional[str] = None

@dataclass
class Cohort:
    """An anonymous peer group."""
    id: str
    name: str
    filters: CohortFilters
    member_count: int = 0

@dataclass
class PercentileDistribution:
    """Mathematical distribution of a metric across a cohort."""
    metric: BenchmarkMetric
    cohort_id: str
    sample_size: int
    p10: float
    p25: float
    median: float
    p75: float
    p90: float
    average: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BenchmarkInsight:
    """AI-generated insight based on user position in distribution."""
    metric: BenchmarkMetric
    severity: InsightSeverity
    message: str
    user_value: float
    cohort_median: float
