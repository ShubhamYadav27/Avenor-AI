from typing import List, Dict, Any, Optional

from app.modules.dashboard_builder.domain.models import (
    Dashboard, Widget, WidgetLayout, WidgetType, ChartSchema
)

class LayoutEngine:
    """Validates and calculates responsive grid logic."""
    
    @staticmethod
    def validate_no_overlap(widgets: List[Widget]) -> bool:
        """Returns True if layout is valid, False if any widgets overlap."""
        for i, w1 in enumerate(widgets):
            for w2 in widgets[i+1:]:
                # Check for rectangle intersection
                r1, r2 = w1.layout, w2.layout
                if (r1.x < r2.x + r2.w and
                    r1.x + r1.w > r2.x and
                    r1.y < r2.y + r2.h and
                    r1.y + r1.h > r2.y):
                    return False
        return True

class WidgetEngine:
    """Transforms raw API payloads into Standardized Chart Schemas."""
    
    @staticmethod
    def fetch_and_transform(widget: Widget) -> ChartSchema:
        # Mocking the internal API fetch based on widget.data_source.endpoint
        # In production, this proxies a request to /api/v1/analytics or a Public API
        
        if widget.type == WidgetType.BAR_CHART:
            # Mock raw response
            raw_data = [
                {"region": "NA", "revenue": 100000},
                {"region": "EMEA", "revenue": 75000},
                {"region": "APAC", "revenue": 50000}
            ]
            # Transform to ChartSchema
            labels = [row["region"] for row in raw_data]
            values = [row["revenue"] for row in raw_data]
            return ChartSchema(
                labels=labels,
                datasets=[{"label": "Revenue", "data": values, "backgroundColor": "#4f46e5"}]
            )
            
        elif widget.type == WidgetType.KPI:
            return ChartSchema(
                labels=["Current"],
                datasets=[{"label": "Total ARR", "value": "$2.5M", "trend": "+12%"}]
            )
            
        return ChartSchema(labels=[], datasets=[])

class DashboardEngine:
    """Orchestrates overarching dashboard lifecycle."""
    
    def __init__(self):
        self._dashboards: Dict[str, Dashboard] = {}
        
    def save_dashboard(self, dashboard: Dashboard) -> None:
        if not LayoutEngine.validate_no_overlap(dashboard.widgets):
            raise ValueError("Dashboard layout invalid: Widget overlap detected.")
        self._dashboards[dashboard.id] = dashboard
        
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        return self._dashboards.get(dashboard_id)
