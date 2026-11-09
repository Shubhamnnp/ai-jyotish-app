import pytest
from unittest.mock import MagicMock
from src.jyotish.core.lifestyle import HealthEngine
from src.jyotish.services.medical import MedicalAstrologyService
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.modules.health_disease_view import render_health_disease_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1  # Aries (Mesha, Lagnesha Mars)
    chart.lagna_degree = 15.0

    class PlanetMock:
        def __init__(self, sign_id, house_from_lagna, dignity="neutral", is_retrograde=False, is_combust=False, nakshatra_name="Ashwini", nakshatra_pada=1):
            self.sign_id = sign_id
            self.house_from_lagna = house_from_lagna
            self.dignity = dignity
            self.is_retrograde = is_retrograde
            self.is_combust = is_combust
            self.nakshatra_name = nakshatra_name
            self.nakshatra_pada = nakshatra_pada
            self.degree = 15.0
            self.speed = 1.0

    chart.planets = {
        "Sun": PlanetMock(1, 1, "exalted", nakshatra_name="Ashwini"),
        "Moon": PlanetMock(2, 2, "exalted", nakshatra_name="Rohini"),
        "Mars": PlanetMock(1, 1, "own", nakshatra_name="Ashwini"),
        "Mercury": PlanetMock(6, 6, "exalted", nakshatra_name="Hasta"),  # 6th house (Roga)
        "Jupiter": PlanetMock(9, 9, "own", nakshatra_name="Moola"),
        "Venus": PlanetMock(12, 12, "exalted", nakshatra_name="Revati"), # 12th house (Vyaya)
        "Saturn": PlanetMock(11, 11, "own", nakshatra_name="Shatabhisha"),
        "Rahu": PlanetMock(8, 8, "neutral", nakshatra_name="Jyeshtha"),  # 8th house (Randhra)
        "Ketu": PlanetMock(2, 2, "neutral", nakshatra_name="Rohini")
    }
    chart.birth_data = MagicMock()
    chart.birth_data.name = "परीक्षण जातक"
    return chart


def test_health_engine_dynamic_analysis(mock_chart):
    res = HealthEngine.analyze(mock_chart)

    # 1. Vitality Assessment
    assert "vitality_score" in res
    assert 40 <= res["vitality_score"] <= 98
    assert "vitality_status" in res

    # 2. Lagnesha & Moon Nakshatra
    assert res["lagnesh"] == "Mars"
    assert res["moon_nakshatra"] == "Rohini"

    # 3. Bhavas: 6th, 8th & 12th
    assert res["h6_lord"] == "Mercury"
    assert "Mercury" in res["h6_occupants"]
    assert "Rahu" in res["h8_occupants"]
    assert "Venus" in res["h12_occupants"]

    # 4. Positive and Negative indicators
    assert len(res["positive_health_traits"]) > 0
    assert len(res["vulnerable_areas"]) > 0
    assert len(res["future_risks"]) > 0
    assert "general_health_advice" in res


def test_shastriya_pramana_medical_shloka():
    assert "medical_kalapurusha_anatomy" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["medical_kalapurusha_anatomy"]
    assert "बृहत्पाराशर" in pramana["grantha"]
    assert "शीर्षाननं च हृदयं" in pramana["shloka_sanskrit"]
    assert "कालपुरुष" in pramana["anuvad_hi"] or "कालपुरुष" in pramana["hindi_translation"]


def test_medical_astrology_service_health_profile(mock_chart):
    profile = MedicalAstrologyService.analyze_health_profile(mock_chart)
    assert "tridosha" in profile
    assert "vata_percent" in profile["tridosha"] or "vata_pct" in profile["tridosha"]
    assert "organ_zones" in profile
    assert "rudraksha_therapy" in profile
    assert len(profile["organ_zones"]) == 12


def test_render_health_disease_view_no_unpack_crash(mock_chart, monkeypatch):
    """Ensure render_health_disease_view unpacks 5 tabs cleanly with default tabs=None."""
    mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr("streamlit.tabs", lambda t: mock_tabs)
    monkeypatch.setattr("streamlit.columns", lambda n: [MagicMock() for _ in range(n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.info", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.caption", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.progress", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.dataframe", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.success", lambda *args, **kwargs: None)

    # Call with default tabs=None
    render_health_disease_view(mock_chart, tabs=None)
    assert len(mock_tabs) == 5


def test_app_tabs_registry_module25():
    """Verify MODULE_TABS_REGISTRY[25] in app.py has 5 tabs."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'25:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[25] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 5
    assert tabs == [
        "🩺 देह वेध आरेख (Anatomy)",
        "💪 आरोग्य बल व स्थिति",
        "⚠️ संभावित रोग जोखिम",
        "📋 ग्रह-अंग चिकित्सा सारणी",
        "🌿 निवारक उपाय व दिनचर्या"
    ]
