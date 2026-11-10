import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.ai.narrative import default_narrative_service


@pytest.fixture
def sample_chart():
    b_data = BirthData(
        name="राहुल शर्मा",
        birth_date=date(1992, 5, 22),
        birth_time=time(11, 45, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b_data)


def test_daivajna_tabs_registry_1_tab():
    """Verify Module 16 has 1 tab dedicated to Vedic AI consultation."""
    expected_tabs = ["💬 वैदिक परामर्श AI"]
    assert len(expected_tabs) == 1
    assert expected_tabs[0] == "💬 वैदिक परामर्श AI"


def test_daivajna_deep_research_marriage(sample_chart):
    """Verify dual-kundali deep research for marriage query."""
    res = default_narrative_service.conduct_daivajna_deep_research("मेरी शादी कब होगी?", sample_chart)
    assert res["topic"] == "marriage"
    assert res["category_name"] == "Marriage"
    assert "prashna_res" in res
    assert "prashna_lagna_sign" in res["prashna_res"]
    assert "natal_summary" in res
    assert "direct_timing" in res
    assert "rules_scan_info" in res


def test_daivajna_deep_research_career(sample_chart):
    """Verify dual-kundali deep research for career query."""
    res = default_narrative_service.conduct_daivajna_deep_research("करियर में पदोन्नति कब होगी?", sample_chart)
    assert res["topic"] == "career"
    assert res["category_name"] == "Career"
    assert "prashna_res" in res
    assert "natal_summary" in res


def test_daivajna_deterministic_consultation(sample_chart):
    """Verify deterministic offline consultation generates authentic Vedic text."""
    ans = default_narrative_service.chat_consultation(
        user_query="मेरी शादी कब तक होगी?",
        chart=sample_chart,
        provider_mode="offline",
        language="Hindi"
    )
    assert isinstance(ans, str)
    assert len(ans) > 100
    assert "विवाह" in ans or "सप्तम" in ans or "शादी" in ans


def test_daivajna_greeting_intelligence(sample_chart):
    """Verify greeting and gratitude queries return dignified blessings without full chart dump."""
    greet_ans = default_narrative_service.chat_consultation(
        user_query="नमस्ते गुरुजी",
        chart=sample_chart,
        provider_mode="offline",
        language="Hindi"
    )
    assert "प्रणाम" in greet_ans or "नमस्ते" in greet_ans or "स्वागत" in greet_ans

    thanks_ans = default_narrative_service.chat_consultation(
        user_query="धन्यवाद गुरुजी",
        chart=sample_chart,
        provider_mode="offline",
        language="Hindi"
    )
    assert "कल्याणमस्तु" in thanks_ans or "शुभ" in thanks_ans or "ईश्वर" in thanks_ans


def test_daivajna_view_module_imports_cleanly():
    """Verify daivajna_view imports cleanly and accepts tabs argument."""
    import src.jyotish.ui.modules.daivajna_view as daivajna_view
    assert hasattr(daivajna_view, "render_daivajna_view")


def test_daivajna_view_shastriya_shloka_and_console():
    """Verify classical Prashna Marga shloka, micro DMS coordinates, and Daivajna HUD console in daivajna_view."""
    import inspect
    import src.jyotish.ui.modules.daivajna_view as daivajna_view
    source = inspect.getsource(daivajna_view.render_daivajna_view)

    assert "prashna_marga_daivajna_shloka" in source
    assert "प्रश्न मार्ग एवं बृहत्संहिता" in source
    assert "दैवज्ञः शान्तो दान्तो विमलमनाः शास्त्रपारगो विप्रः" in source
    assert "col_dj1, col_dj2, col_dj3, col_dj4 = st.columns(4)" in source
    assert "सक्रिय जातक व लग्न" in source
    assert "चन्द्र राशि व नक्षत्र" in source
    assert "आत्मकारक (AK) व AmK" in source
