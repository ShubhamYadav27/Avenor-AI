from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.industry_benchmarking.domain.models import Cohort, CohortFilters, BenchmarkMetric
from app.modules.industry_benchmarking.application.services import PercentileEngine, InsightEngine, PrivacyViolationError

router = APIRouter(prefix="/v1/benchmarks", tags=["Industry Benchmarking"])

# Pre-seed for demonstration
_cohorts_db = {
    "cohort_saas_smb": Cohort(id="cohort_saas_smb", name="B2B SaaS (100-500 Employees)", filters=CohortFilters(industry="SaaS", employee_count_range="100-500"), member_count=1420),
    "cohort_finance_ent": Cohort(id="cohort_finance_ent", name="Financial Services (Enterprise)", filters=CohortFilters(industry="Finance", employee_count_range="5000+"), member_count=3) # Note: member_count=3, PrivacyGuard will block this
}

# In-memory "Data Warehouse" mocking the aggregated raw arrays
_benchmark_cache = {
    "cohort_saas_smb": {
        BenchmarkMetric.WIN_RATE: [12.0, 15.5, 18.0, 22.0, 24.5, 25.0, 31.0, 35.0, 42.0, 45.0], # 10 samples
        BenchmarkMetric.SALES_CYCLE_DAYS: [14.0, 21.0, 30.0, 45.0, 60.0, 75.0, 90.0, 120.0] # 8 samples
    },
    "cohort_finance_ent": {
        BenchmarkMetric.WIN_RATE: [10.0, 15.0, 20.0] # 3 samples (will trigger Privacy Error)
    }
}

@router.get("/cohorts/{cohort_id}/metrics/{metric}")
async def get_benchmark_distribution(cohort_id: str, metric: BenchmarkMetric) -> dict:
    """Fetch the anonymous percentile distribution for a specific cohort & metric."""
    cohort = _cohorts_db.get(cohort_id)
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
        
    raw_data = _benchmark_cache.get(cohort_id, {}).get(metric, [])
    
    try:
        dist = PercentileEngine.calculate_distribution(metric, cohort, raw_data)
        return {
            "metric": metric.value,
            "cohort": cohort.name,
            "sample_size": dist.sample_size,
            "distribution": {
                "p10": dist.p10,
                "p25": dist.p25,
                "median": dist.median,
                "p75": dist.p75,
                "p90": dist.p90,
                "average": dist.average
            }
        }
    except PrivacyViolationError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/cohorts/{cohort_id}/metrics/{metric}/insight")
async def generate_benchmark_insight(cohort_id: str, metric: BenchmarkMetric, payload: Dict[str, Any]) -> dict:
    """Compare my specific value against the cohort and generate an AI Insight."""
    user_value = payload.get("user_value")
    
    cohort = _cohorts_db.get(cohort_id)
    raw_data = _benchmark_cache.get(cohort_id, {}).get(metric, [])
    
    try:
        dist = PercentileEngine.calculate_distribution(metric, cohort, raw_data)
        insight = InsightEngine.generate_insight(metric, float(user_value), dist)
        
        return {
            "metric": metric.value,
            "severity": insight.severity.value,
            "message": insight.message,
            "user_value": user_value,
            "cohort_median": insight.cohort_median
        }
    except PrivacyViolationError as e:
        raise HTTPException(status_code=403, detail=str(e))
