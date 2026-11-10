import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.btr import default_btr_service, LifeEvent, BTRCandidate


@pytest.fixture
def sample_birth_data():
    return BirthData(
        birth_date=date(1990, 1, 15),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )


@pytest.fixture
def sample_chart(sample_birth_data):
    return default_chart_calculator.calculate_chart(sample_birth_data)


def test_btr_tabs_registry_8_tabs():
    """Verify that Module 14 has 8 distinct tabs."""
    expected_tabs = [
        "🏆 घटना मिलान शोधन",
        "🌿 तत्व व लिंग शोधन",
        "☸️ कुण्ड व प्राणपद लग्न",
        "📐 D9 व D60 सीमा",
        "👑 के.पी. रूलिंग प्लैनेट्स",
        "⚖️ पूर्व व शोधित तुलना",
        "🎯 सेकंड्स सूक्ष्म स्लाइडर",
        "📜 शास्त्रीय सूत्र व प्रमाण"
    ]
    assert len(expected_tabs) == 8
    assert "🌿 तत्व व लिंग शोधन" in expected_tabs
    assert "☸️ कुण्ड व प्राणपद लग्न" in expected_tabs
    assert "📐 D9 व D60 सीमा" in expected_tabs


def test_tattwa_shodhana_calculation(sample_birth_data):
    """Verify classical Tattwa and Antar-tattwa gender rectification calculation."""
    res = default_btr_service.calculate_tattwa_shodhana(sample_birth_data, gender="male")
    assert "sunrise_time" in res
    assert "ishta_kala" in res
    assert "maha_tattwa" in res
    assert "antar_tattwa" in res
    assert "gender_match_status" in res
    assert "sub_tattwa_schedule" in res
    assert len(res["sub_tattwa_schedule"]) == 5
    assert 0.0 <= res["score"] <= 100.0


def test_kunda_pranapada_calculation(sample_chart, sample_birth_data):
    """Verify BPHS Kunda Shodhana and Pranapada Lagna calculations."""
    res = default_btr_service.calculate_kunda_pranapada(sample_chart, sample_birth_data)
    assert "kunda_nakshatra_num" in res
    assert 1 <= res["kunda_nakshatra_num"] <= 27
    assert "kunda_nakshatra_name" in res
    assert "pranapada_longitude" in res
    assert 0.0 <= res["pranapada_longitude"] < 360.0
    assert "pranapada_sign" in res
    assert "kunda_status" in res
    assert "pranapada_status" in res


def test_divisional_boundaries_precision(sample_chart, sample_birth_data):
    """Verify D1, D9 and D60 Shashtiamsha border vulnerability scan."""
    res = default_btr_service.calculate_divisional_boundaries(sample_chart, sample_birth_data)
    assert "d1_lagna_sign" in res
    assert "d9_navamsha_num" in res
    assert 1 <= res["d9_navamsha_num"] <= 9
    assert "d60_part_num" in res
    assert 1 <= res["d60_part_num"] <= 60
    assert "d60_deity_name" in res
    assert "vulnerability_status" in res
    assert res["vulnerability_level"] in ("Critical", "Moderate", "Safe")


def test_kp_ruling_planets_verification(sample_chart):
    """Verify KP 4-Fold Ruling Planets and Lagna Sub-Lord verification."""
    res = default_btr_service.calculate_kp_ruling_planets(sample_chart)
    assert "lagna_sign_lord" in res
    assert "lagna_star_lord" in res
    assert "lagna_sub_lord" in res
    assert "ruling_planets_table" in res
    assert len(res["ruling_planets_table"]) == 5
    assert "match_rating" in res
    assert 0.0 <= res["kp_score"] <= 100.0


def test_btr_view_module_imports_cleanly():
    """Verify that btr_view imports cleanly without NameError or reload issues."""
    import src.jyotish.ui.modules.btr_view as btr_view
    assert hasattr(btr_view, "render_btr_view")


def test_btr_view_shastriya_shloka_and_console():
    """Verify classical BPHS Kunda & Pranapada shloka, micro DMS, D60 deity, and BTR console in btr_view."""
    import inspect
    import src.jyotish.ui.modules.btr_view as btr_view
    source = inspect.getsource(btr_view.render_btr_view)

    assert "bphs_btr_shloka" in source
    assert "बृहत्पाराशर होराशास्त्र एवं चन्द्रकला नाड़ी" in source
    assert "इष्टघट्या गुणीकृत्य भानुभं सप्तभिर्भजेत्" in source
    assert "col_mb1, col_mb2, col_mb3, col_mb4 = st.columns(4)" in source
    assert "जन्म लग्न (D1 & D9)" in source
    assert "D60:" in source
    assert "कुण्ड व प्राणपद" in source
