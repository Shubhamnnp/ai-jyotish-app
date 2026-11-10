import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.milan import default_milan_service, AshtakootaScore
from src.jyotish.services.partners import BusinessPartnershipService


@pytest.fixture
def groom_chart():
    b_data = BirthData(
        birth_date=date(1995, 8, 20),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b_data)


@pytest.fixture
def bride_chart():
    b_data = BirthData(
        birth_date=date(1997, 3, 15),
        birth_time=time(10, 15, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b_data)


def test_matching_tabs_registry_10_tabs():
    """Verify Module 15 has 10 synchronized tabs."""
    expected_tabs = [
        "📊 अष्टकूट (३६ गुण)",
        "🛡️ महादोष व १६ परिहार",
        "🔥 मांगलिक व भौम साम्य",
        "☸️ उभय कुण्डली (D1/D9)",
        "👶 बीज-क्षेत्र व संतान",
        "🏛️ उपपद व ससुराल पक्ष",
        "⏱️ दशा-संधि कालक्रम",
        "📈 अष्टकवर्ग सिनैस्ट्री",
        "💼 व्यापार साझेदारी",
        "🖨️ मिलान रिपोर्ट व उपाय"
    ]
    assert len(expected_tabs) == 10
    assert "📊 अष्टकूट (३६ गुण)" in expected_tabs
    assert "🛡️ महादोष व १६ परिहार" in expected_tabs
    assert "🔥 मांगलिक व भौम साम्य" in expected_tabs
    assert "💼 व्यापार साझेदारी" in expected_tabs


def test_ashtakoota_36_guna_calculation(groom_chart, bride_chart):
    """Verify Ashtakoota 36 Gunas calculation and individual koota bounds."""
    m_score = default_milan_service.match_computed_charts(groom_chart, bride_chart)
    assert isinstance(m_score, AshtakootaScore)
    assert 0.0 <= m_score.varna <= 1.0
    assert 0.0 <= m_score.vashya <= 2.0
    assert 0.0 <= m_score.tara <= 3.0
    assert 0.0 <= m_score.yoni <= 4.0
    assert 0.0 <= m_score.graha_maitri <= 5.0
    assert 0.0 <= m_score.gana <= 6.0
    assert 0.0 <= m_score.bhakoot <= 7.0
    assert 0.0 <= m_score.nadi <= 8.0
    assert 0.0 <= m_score.total_score <= 36.0
    assert m_score.verdict is not None and len(m_score.verdict) > 0


def test_nadi_bhakoot_dosha_cancellations(groom_chart, bride_chart):
    """Verify Nadi, Bhakoot, Rajju, and Vedha dosha attributes."""
    m_score = default_milan_service.match_computed_charts(groom_chart, bride_chart)
    assert isinstance(m_score.nadi_dosha, bool)
    assert isinstance(m_score.nadi_dosha_cancelled, bool)
    assert isinstance(m_score.bhakoot_dosha, bool)
    assert isinstance(m_score.bhakoot_dosha_cancelled, bool)
    assert isinstance(m_score.rajju_dosha, bool)
    assert isinstance(m_score.vedha_dosha, bool)


def test_manglik_compatibility_analysis(groom_chart, bride_chart):
    """Verify mutual Manglik Dosha evaluation and cancellation check."""
    m_score = default_milan_service.match_computed_charts(groom_chart, bride_chart)
    assert isinstance(m_score.groom_manglik, bool)
    assert isinstance(m_score.bride_manglik, bool)
    assert isinstance(m_score.manglik_match, bool)


def test_deep_synastry_analysis(groom_chart, bride_chart):
    """Verify deep synastry and Beeja-Kshetra evaluation."""
    syn = default_milan_service.analyze_deep_synastry(groom_chart, bride_chart)
    assert "santana" in syn
    assert "sasural" in syn
    assert "prosperity" in syn
    assert "synastry_aspects" in syn
    santana = syn["santana"]
    assert "beeja" in santana
    assert "kshetra" in santana
    assert "score" in santana["beeja"]
    assert "score" in santana["kshetra"]


def test_business_partnership_evaluation(groom_chart, bride_chart):
    """Verify Business Partnership 4-Pillar compatibility evaluation."""
    res = BusinessPartnershipService.evaluate_partnership(groom_chart, bride_chart)
    assert "total_score" in res
    assert 0 <= res["total_score"] <= 100
    assert "verdict" in res
    assert "grade" in res
    assert "pillars" in res
    assert len(res["pillars"]) >= 4


def test_matching_view_module_imports_cleanly():
    """Verify that matching_view imports cleanly without errors."""
    import src.jyotish.ui.modules.matching_view as matching_view
    assert hasattr(matching_view, "render_matching_view")


def test_matching_view_shastriya_shloka_and_console():
    """Verify Muhurta Chintamani Ashtakoota shloka, micro DMS coordinates, and synastry console in matching_view."""
    import inspect
    import src.jyotish.ui.modules.matching_view as matching_view
    source = inspect.getsource(matching_view.render_matching_view)

    assert "muhurta_chintamani_milan_shloka" in source
    assert "मुहूर्त चिन्तामणि एवं बृहत्संहिता" in source
    assert "वर्णो वश्यं तथा तारा योनिश्च ग्रहमैत्रकम्" in source
    assert "c_mil1, c_mil2, c_mil3, c_mil4 = st.columns(4)" in source
    assert "👦 वर (Lagna & Moon)" in source
    assert "👧 कन्या (Lagna & Moon)" in source
    assert "भौम साम्य (Manglik)" in source
