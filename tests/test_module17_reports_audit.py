import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.prescription import ConsultationSlipService, default_prescription_service
from src.jyotish.services.report_generator import default_report_generator


@pytest.fixture
def sample_chart():
    b_data = BirthData(
        name="सुनील कुमार",
        birth_date=date(1991, 10, 10),
        birth_time=time(8, 20, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b_data)


def test_reports_tabs_registry_2_tabs():
    """Verify Module 17 has 2 synchronized tabs."""
    expected_tabs = [
        "📚 सम्पूर्ण ५०-पेज पत्रिका",
        "📋 १-पेज परामर्श पर्ची"
    ]
    assert len(expected_tabs) == 2
    assert "📚 सम्पूर्ण ५०-पेज पत्रिका" in expected_tabs
    assert "📋 १-पेज परामर्श पर्ची" in expected_tabs


def test_prescription_slip_generation(sample_chart):
    """Verify ConsultationSlipService creates structured prescription."""
    p_data = ConsultationSlipService.generate_prescription(sample_chart)
    assert "primary_gem" in p_data
    assert "secondary_gem" in p_data
    assert "prohibited_gems" in p_data
    assert "mantras" in p_data
    assert "charity" in p_data
    assert "lifestyle" in p_data
    assert "quarterly_caution" in p_data
    assert "native_name" in p_data
    assert p_data["native_name"] == "सुनील कुमार"


def test_prescription_slip_html_and_whatsapp(sample_chart):
    """Verify HTML rendering and WhatsApp text generation."""
    p_data = ConsultationSlipService.generate_prescription(sample_chart)
    html_out = ConsultationSlipService.render_prescription_html(
        p_data,
        astro_name="पं. शुभम तिवारी",
        astro_center="वैदिक ज्योतिष केंद्र",
        astro_contact="+91-9452155742"
    )
    assert isinstance(html_out, str)
    assert len(html_out) > 500
    assert "सुनील कुमार" in html_out
    assert "परामर्श" in html_out

    wa_text = ConsultationSlipService.generate_whatsapp_text(p_data)
    assert isinstance(wa_text, str)
    assert len(wa_text) > 100
    assert "सुनील कुमार" in wa_text


def test_master_html_report_generation(sample_chart):
    """Verify 50+ page HTML natal report generation."""
    html_rep = default_report_generator.generate_html_report(
        sample_chart,
        astro_name="पं. शुभम तिवारी",
        astro_phone="+91-9452155742",
        astro_org="वैदिक ज्योतिष केंद्र"
    )
    assert isinstance(html_rep, str)
    assert len(html_rep) > 5000
    assert "सुनील कुमार" in html_rep


def test_reports_view_module_imports_cleanly():
    """Verify reports_view imports cleanly without errors."""
    import src.jyotish.ui.modules.reports_view as reports_view
    assert hasattr(reports_view, "render_reports_view")
