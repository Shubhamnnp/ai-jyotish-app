import pytest
from unittest.mock import MagicMock
from src.jyotish.core.lifestyle import BodyAnatomyEngine
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.modules.body_anatomy_view import render_body_anatomy_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1  # Aries (Mesha, Fire)

    class PlanetMock:
        def __init__(self, sign_id, house_from_lagna, dignity="neutral", is_retrograde=False, nakshatra_name="Ashwini", nakshatra_pada=1):
            self.sign_id = sign_id
            self.house_from_lagna = house_from_lagna
            self.dignity = dignity
            self.is_retrograde = is_retrograde
            self.nakshatra_name = nakshatra_name
            self.nakshatra_pada = nakshatra_pada

    chart.planets = {
        "Sun": PlanetMock(1, 1, "exalted"),       # Sun in 1st house (Head mark)
        "Moon": PlanetMock(2, 2, "exalted"),      # Moon in 2nd house (Throat/Face)
        "Mars": PlanetMock(1, 1, "own"),          # Mars in 1st house (Face scar/mark)
        "Mercury": PlanetMock(6, 6, "exalted"),
        "Jupiter": PlanetMock(9, 9, "own"),
        "Venus": PlanetMock(12, 12, "exalted"),
        "Saturn": PlanetMock(11, 11, "own"),
        "Rahu": PlanetMock(8, 8, "neutral"),      # Rahu in 8th house (Pelvic/thigh mark)
        "Ketu": PlanetMock(2, 2, "neutral")
    }
    return chart


def test_body_anatomy_engine_analysis(mock_chart):
    res = BodyAnatomyEngine.analyze(mock_chart)

    # 1. Lagna & Physique
    assert res["lagna_sign"] == "Aries"
    assert "मेष" in res["lagna_sign_hi"]
    assert res["lagna_element"] == "Fire"
    assert res["lagnesh_name"] == "Mars"
    assert "frame" in res["physique"]
    assert "complexion" in res["physique"]
    assert "facial" in res["physique"]
    assert "constitution" in res["physique"]

    # 2. 12 Kalapurusha Limbs
    assert len(res["limbs_status"]) == 12
    for limb in res["limbs_status"]:
        assert "limb_hi" in limb
        assert "house_from_lagna" in limb
        assert "status" in limb
        assert "notes" in limb

    # 3. Congenital Marks (Mars/Sun in 1st house, Rahu in 8th house)
    assert len(res["congenital_marks"]) > 0
    assert any("मस्तक" in m or "चेहरे" in m for m in res["congenital_marks"])

    # 4. Asana Guidance & Core Advice
    assert "शीतलीकरण" in res["asana_guidance"] or "अग्नि" in res["asana_guidance"]
    assert "core_advice" in res


def test_shastriya_pramana_sharirika_shloka():
    assert "brihat_samhita_sharirika_lakshana" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["brihat_samhita_sharirika_lakshana"]
    assert "बृहत्संहिता" in pramana["grantha"]
    assert "लग्नेशे बलसंयुक्ते" in pramana["shloka_sanskrit"]
    assert "पुष्ट" in pramana["anuvad_hi"] or "शरीर" in pramana["anuvad_hi"]


def test_render_body_anatomy_view_no_unpack_crash(mock_chart, monkeypatch):
    """Ensure render_body_anatomy_view unpacks 4 tabs cleanly with default tabs=None."""
    mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr("streamlit.tabs", lambda t: mock_tabs)
    monkeypatch.setattr("streamlit.columns", lambda n: [MagicMock() for _ in range(n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.caption", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.dataframe", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.success", lambda *args, **kwargs: None)

    # Call with default tabs=None
    render_body_anatomy_view(mock_chart, tabs=None)
    assert len(mock_tabs) == 4


def test_app_tabs_registry_module26():
    """Verify MODULE_TABS_REGISTRY[26] in app.py has 4 synchronized tabs."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'26:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[26] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 4
    assert tabs == [
        "🏃 कद-काठी व रंग-रूप",
        "🦴 १२ कालपुरुष अंग",
        "🎯 तिल, मस्से व चिन्ह",
        "🔮 सुरक्षा व आसन परामर्श"
    ]
