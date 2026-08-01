import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.dashboard_builder.api.router import router, _mock_dashboard, _mock_widget_1, _mock_widget_2
from app.modules.dashboard_builder.domain.models import Dashboard, Widget, WidgetLayout, DataSource, WidgetType
from app.modules.dashboard_builder.application.services import LayoutEngine, WidgetEngine, DashboardEngine

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_layout_engine_valid():
    assert LayoutEngine.validate_no_overlap([_mock_widget_1, _mock_widget_2]) is True

def test_layout_engine_invalid_overlap():
    # Create an overlapping widget
    w_overlap = Widget(
        id="w3", type=WidgetType.KPI, title="Overlap", 
        layout=WidgetLayout(x=2, y=0, w=4, h=2), # Overlaps with w1 (x0->x4) and w2 (x4->x12)
        data_source=DataSource(endpoint="", metrics=[], dimensions=[])
    )
    assert LayoutEngine.validate_no_overlap([_mock_widget_1, w_overlap]) is False

def test_widget_engine_data_transformation():
    # Test transformation for BAR_CHART
    chart_data = WidgetEngine.fetch_and_transform(_mock_widget_2)
    assert chart_data.labels == ["NA", "EMEA", "APAC"]
    assert len(chart_data.datasets) == 1
    assert chart_data.datasets[0]["label"] == "Revenue"
    assert chart_data.datasets[0]["data"] == [100000, 75000, 50000]

def test_dashboard_api_async_widget_data():
    # The dashboard wrapper only returns the layout bounds
    res_dash = client.get("/v1/dashboards/dash_cro")
    assert res_dash.status_code == 200
    assert len(res_dash.json()["widgets"]) == 2
    
    # The client must fetch the heavy data asynchronously per widget
    res_widget = client.get("/v1/dashboards/dash_cro/widgets/w2/data")
    assert res_widget.status_code == 200
    data = res_widget.json()
    assert data["labels"] == ["NA", "EMEA", "APAC"]
    assert data["datasets"][0]["data"] == [100000, 75000, 50000]
