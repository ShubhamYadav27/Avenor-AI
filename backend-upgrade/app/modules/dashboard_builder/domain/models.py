from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class WidgetType(str, Enum):
    KPI = "kpi"
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    AI_SUMMARY = "ai_summary"
    DATA_TABLE = "data_table"

@dataclass
class WidgetLayout:
    """Grid spatial coordinates (React-Grid-Layout style)."""
    x: int
    y: int
    w: int
    h: int

@dataclass
class DataSource:
    """Defines the API boundary the widget consumes data from."""
    endpoint: str # e.g., '/api/v1/analytics/revenue'
    metrics: List[str] # e.g., ['arr', 'mrr']
    dimensions: List[str] # e.g., ['month', 'region']

@dataclass
class Widget:
    """A granular visualization block."""
    id: str
    type: WidgetType
    title: str
    layout: WidgetLayout
    data_source: DataSource
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Dashboard:
    """An overarching analytics view."""
    id: str
    workspace_id: str
    name: str
    description: str = ""
    widgets: List[Widget] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
@dataclass
class ChartSchema:
    """Standardized output schema consumed by the frontend charting library."""
    labels: List[str]
    datasets: List[Dict[str, Any]]
