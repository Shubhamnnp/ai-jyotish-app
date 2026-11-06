"""
Tests for BRAMHAHORA UI Web Interface components, assets, and API integrations.
Ensures zero breakage of mathematical engines, canonical charts, and rules.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from src.jyotish.api.main import app

client = TestClient(app)

WEB_DIR = Path(__file__).resolve().parent.parent / "src" / "jyotish" / "ui" / "web"


def test_web_static_index_html_exists_and_serves():
    index_file = WEB_DIR / "index.html"
    assert index_file.exists(), "index.html must exist in web directory"
    content = index_file.read_text(encoding="utf-8")
    
    # Check BRAMHAHORA branding
    assert "BRAMHAHORA" in content
    
    # Check top action buttons
    assert "btnHdrJanmaPanchang" in content
    assert "btnHdrTodayPanchang" in content
    assert "btn-cta-prashna" in content
    assert "NEW PRASHNA KUNDLI" in content
    assert "savedKundliModal" in content
    assert "formGender" in content
    assert "formSaveKundli" in content
    assert "toolbelt-slide-btn" in content
    
    # Check all 3 chart styles (North, South, East)
    assert "btnNorthChart" in content
    assert "btnSouthChart" in content
    assert "btnEastChart" in content
    
    # Check all 16 Shodashavarga pills
    for varga in ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]:
        assert f'data-varga="{varga}"' in content
        
    # Check analytical sub-views
    assert "panelTablePlanets" in content
    assert "panelTableHouses" in content
    assert "panelTableSummary" in content
    assert "panelGrahaBalaGraph" in content
    assert "grahaBalaGraphBox" in content


def test_web_chart_js_has_east_indian_renderer():
    chart_js = WEB_DIR / "chart.js"
    assert chart_js.exists()
    content = chart_js.read_text(encoding="utf-8")
    assert "renderNorthIndian" in content
    assert "renderSouthIndian" in content
    assert "renderEastIndian" in content
    assert "#6B1D2F" in content  # Dark maroon stroke


def test_web_app_js_has_bramhahora_methods():
    app_js = WEB_DIR / "app.js"
    assert app_js.exists()
    content = app_js.read_text(encoding="utf-8")
    assert "slideToolbelt" in content
    assert "saveCurrentKundli" in content
    assert "openSavedKundliModal" in content
    assert "renderAnalyticalSubViews" in content
    assert "setAnalyticalSubView" in content
    assert "renderHousesTable" in content
    assert "renderD1SummaryPanchang" in content
    assert "renderGrahaBalaGraph" in content
    assert "openJanmaPanchangModal" in content
    assert "openTodayPanchangModal" in content
    assert "createInstantPrashnaKundli" in content


def test_api_panchang_endpoint_for_bramhahora():
    payload = {
        "date": "1994-05-16",
        "time": "17:00:00",
        "latitude": 27.8643,
        "longitude": 81.5033,
        "timezone_offset": 5.5
    }
    response = client.post("/api/panchang/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "tithi" in data or "weekday" in data or "date" in data


def test_api_chart_endpoint_nanpara_integrity():
    payload = {
        "name": "Shubham Kumar",
        "birth_date": "1994-05-16",
        "birth_time": "17:00:00",
        "latitude": 27.8643,
        "longitude": 81.5033,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/calculate?ayanamsa=Lahiri", json=payload)
    assert response.status_code == 200
    chart = response.json()
    assert chart["lagna_sign_id"] == 7  # Libra
    assert "planets" in chart
    assert "Sun" in chart["planets"]
    assert "Moon" in chart["planets"]
    assert chart["planets"]["Mars"]["sign_id"] == 1  # Aries in 7th
    assert chart["planets"]["Moon"]["sign_id"] == 4  # Cancer in 10th

