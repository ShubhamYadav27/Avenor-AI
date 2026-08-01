from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.dashboard_builder.domain.models import Dashboard, Widget, WidgetLayout, DataSource, WidgetType
from app.modules.dashboard_builder.application.services import DashboardEngine, WidgetEngine

router = APIRouter(prefix="/v1/dashboards", tags=["Enterprise Dashboard Builder"])

_engine = DashboardEngine()

# Pre-seed for demonstration
_mock_widget_1 = Widget(
    id="w1", type=WidgetType.KPI, title="Total ARR", 
    layout=WidgetLayout(x=0, y=0, w=4, h=2),
    data_source=DataSource(endpoint="/api/v1/metrics/arr", metrics=["arr"], dimensions=[])
)
_mock_widget_2 = Widget(
    id="w2", type=WidgetType.BAR_CHART, title="Revenue by Region", 
    layout=WidgetLayout(x=4, y=0, w=8, h=4),
    data_source=DataSource(endpoint="/api/v1/metrics/revenue", metrics=["revenue"], dimensions=["region"])
)
_mock_dashboard = Dashboard(
    id="dash_cro", workspace_id="ws_001", name="CRO Command Center", description="Executive view",
    widgets=[_mock_widget_1, _mock_widget_2]
)
_engine.save_dashboard(_mock_dashboard)

@router.get("/")
async def list_dashboards(workspace_id: str) -> List[dict]:
    """List all dashboards in the workspace."""
    return [{"id": d.id, "name": d.name, "widget_count": len(d.widgets)} 
            for d in _engine._dashboards.values() if d.workspace_id == workspace_id]

@router.get("/{dashboard_id}")
async def get_dashboard(dashboard_id: str) -> dict:
    """Get the layout schema for a dashboard. Does NOT fetch data."""
    dash = _engine.get_dashboard(dashboard_id)
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
        
    return {
        "id": dash.id,
        "name": dash.name,
        "widgets": [
            {"id": w.id, "type": w.type.value, "title": w.title, "layout": w.layout.__dict__}
            for w in dash.widgets
        ]
    }

@router.get("/{dashboard_id}/widgets/{widget_id}/data")
async def get_widget_data(dashboard_id: str, widget_id: str) -> dict:
    """Fetch the transformed data for a specific widget. Highly optimized async pattern."""
    dash = _engine.get_dashboard(dashboard_id)
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
        
    widget = next((w for w in dash.widgets if w.id == widget_id), None)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
        
    chart_data = WidgetEngine.fetch_and_transform(widget)
    
    return {
        "labels": chart_data.labels,
        "datasets": chart_data.datasets
    }
