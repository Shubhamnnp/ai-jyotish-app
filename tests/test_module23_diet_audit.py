import pytest
from unittest.mock import MagicMock
from src.jyotish.core.lifestyle import DietEngine
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.modules.ayurvedic_diet_view import render_ayurvedic_diet_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1  # Aries (Mesha, Fire, Pitta)

    class PlanetMock:
        def __init__(self, sign_id, house_from_lagna, nakshatra_name="Ashwini", nakshatra_pada=1):
            self.sign_id = sign_id
            self.house_from_lagna = house_from_lagna
            self.nakshatra_name = nakshatra_name
            self.nakshatra_pada = nakshatra_pada

    chart.planets = {
        "Sun": PlanetMock(1, 1, "Ashwini", 1),
        "Moon": PlanetMock(2, 2, "Rohini", 2),  # Moon in 2nd house Rohini (Kapha)
        "Mars": PlanetMock(1, 1, "Ashwini", 1), # Lagnesha Mars
        "Mercury": PlanetMock(1, 1, "Ashwini", 2),
        "Jupiter": PlanetMock(9, 9, "Moola", 1),
        "Venus": PlanetMock(12, 12, "Revati", 4),
        "Saturn": PlanetMock(11, 11, "Shatabhisha", 1),
        "Rahu": PlanetMock(2, 2, "Rohini", 1),  # Rahu in 2nd house
        "Ketu": PlanetMock(8, 8, "Jyeshtha", 3)
    }
    return chart


def test_diet_engine_dynamic_chart_analysis(mock_chart):
    res = DietEngine.analyze(mock_chart)

    # 1. Primary Dosha & Lagna
    assert res["primary_dosha"] == "Pitta (पित्त)"
    assert res["lagna_element"] == "Fire"
    assert "लग्नेश Mars" in res["lagnesh_summary"]

    # 2. Moon & Nakshatra Dosha
    assert res["moon_nakshatra"] == "Rohini"
    assert res["moon_pada"] == 2
    assert "Kapha" in res["nakshatra_dosha"]

    # 3. Sun Jatharagni
    assert "प्रदीप्त" in res["sun_jatharagni"] or "तीक्ष्ण" in res["sun_jatharagni"]
    assert res["sun_status_note"] is not None

    # 4. 2nd House Food Psychology (Rahu in 2nd house)
    assert res["h2_lord"] == "Venus"
    assert "Rahu" in res["h2_occupants"]
    assert any("राहु द्वितीय भाव में" in n for n in res["eating_habits"])

    # 5. Food lists
    assert len(res["favorable_foods"]) > 0
    assert len(res["unfavorable_foods"]) > 0
    assert "fasting_remedy" in res


def test_shastriya_pramana_diet_shloka():
    assert "ayurveda_diet_tridosha" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["ayurveda_diet_tridosha"]
    assert "अष्टांगहृदयम्" in pramana["grantha"]
    assert "वातः पित्तं कफश्चेति" in pramana["shloka_sanskrit"]
    assert "त्रिदोष" in pramana["anuvad_hi"] or "दोष" in pramana["anuvad_hi"]


def test_render_ayurvedic_diet_view_no_unpack_crash(mock_chart, monkeypatch):
    """Ensure render_ayurvedic_diet_view does not crash with default tabs=None."""
    mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr("streamlit.tabs", lambda t: mock_tabs)
    monkeypatch.setattr("streamlit.columns", lambda n: [MagicMock() for _ in range(n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.info", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.caption", lambda *args, **kwargs: None)

    # Call with tabs=None
    render_ayurvedic_diet_view(mock_chart, tabs=None)
    assert len(mock_tabs) == 4


def test_app_tabs_registry_sync():
    """Verify MODULE_TABS_REGISTRY[23] in app.py has 4 tabs matching view."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'23:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[23] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 4
    assert tabs == [
        "🌿 त्रिदोष शारीरिक प्रकृति",
        "✅ अनुकूल आहार व रस",
        "❌ वर्जित आहार व परहेज",
        "⏰ भोजन नियम व उपवास"
    ]
