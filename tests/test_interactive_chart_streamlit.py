import datetime
import pytest
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.ui.chart_renderer import ChartRenderer

@pytest.fixture
def sample_chart():
    bd = BirthData(
        name="Test Native",
        birth_date=datetime.date(1995, 5, 15),
        birth_time=datetime.time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_full_chart(bd)

def test_build_bhav_inspector_data_contains_12_houses(sample_chart):
    """Verify that build_bhav_inspector_data computes authentic data for all 12 houses."""
    bhav_data = ChartRenderer.build_bhav_inspector_data(sample_chart, varga_code="D1")
    assert isinstance(bhav_data, dict)
    assert len(bhav_data) == 12
    for h in range(1, 13):
        assert h in bhav_data
        h_info = bhav_data[h]
        assert "bhav_label" in h_info
        assert "sign_name" in h_info
        assert "lord_name" in h_info
        assert "occupants" in h_info
        assert "aspects" in h_info
        assert "karaka" in h_info
        assert "cusp_info" in h_info
        assert "significations" in h_info

def test_interactive_chart_html_has_clickable_polygons(sample_chart):
    """Verify that render_interactive_chart_html contains 12 clickable house polygons."""
    html_out = ChartRenderer.render_interactive_chart_html(sample_chart, varga_code="D1", initial_house=1)
    assert isinstance(html_out, str)
    # Check that all 12 house click targets exist in SVG
    for h in range(1, 13):
        assert f'data-h="{h}"' in html_out or f'data-house="{h}"' in html_out
    # Check that JS data dictionary is embedded
    assert "BHAV_DATA" in html_out or "bhavData" in html_out
    assert "selectHouse" in html_out
    # Check that Bhav Inspector container is present
    assert "bhav-inspector" in html_out or "inspector" in html_out
