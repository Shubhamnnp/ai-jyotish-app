import pytest
from unittest.mock import MagicMock
from src.jyotish.core.lifestyle import RelationshipEngine
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.modules.relationships_view import render_relationships_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1  # Aries (Mesha, Lagnesha Mars)

    class PlanetMock:
        def __init__(self, sign_id, house_from_lagna, dignity="neutral", is_retrograde=False):
            self.sign_id = sign_id
            self.house_from_lagna = house_from_lagna
            self.dignity = dignity
            self.is_retrograde = is_retrograde

    chart.planets = {
        "Sun": PlanetMock(1, 1, "exalted"),       # Sun exalted in 1st house (Karaka for Father)
        "Moon": PlanetMock(2, 2, "exalted"),      # Moon exalted in 2nd house (Karaka for Mother)
        "Mars": PlanetMock(6, 6, "own"),          # Mars in 6th house (Shatruhanta Yoga!)
        "Mercury": PlanetMock(7, 7, "friendly"),  # Mercury in 7th house
        "Jupiter": PlanetMock(9, 9, "own"),       # Jupiter in 9th house (Karaka for Children/Mentors)
        "Venus": PlanetMock(7, 7, "own"),         # Venus in 7th house Libra (Karaka for Spouse)
        "Saturn": PlanetMock(11, 11, "own"),      # Saturn in 11th house (Friends & Benefactors)
        "Rahu": PlanetMock(6, 6, "neutral"),      # Rahu in 6th house
        "Ketu": PlanetMock(12, 12, "neutral")
    }
    return chart


def test_relationships_engine_chart_analysis(mock_chart):
    res = RelationshipEngine.analyze(mock_chart)

    # 1. Basic properties
    assert res["lagnesh"] == "Mars"
    assert "relations" in res
    relations = res["relations"]

    # 2. Spouse (7th house)
    assert "spouse" in relations
    sp = relations["spouse"]
    assert sp["lord"] == "Venus"
    assert "तुला" in sp["sign_name"]
    assert "Venus" in sp["occupants"]
    assert len(sp["positive_points"]) > 0
    assert len(sp["caution_points"]) > 0

    # 3. Enemies (6th house) - Shatruhanta Yoga with Mars/Rahu in 6th
    assert "enemies" in relations
    en = relations["enemies"]
    assert "शत्रुहंता" in en["status"]
    assert any("अंतिम विजय" in pt for pt in en["positive_points"])

    # 4. Friends (11th house)
    assert "friends" in relations
    fr = relations["friends"]
    assert fr["lord"] == "Saturn"
    assert len(fr["positive_points"]) > 0

    # 5. Family (father 9th, mother 4th, siblings 3rd, children 5th)
    for fam_key in ["father", "mother", "siblings", "children"]:
        assert fam_key in relations
        item = relations[fam_key]
        assert "lord" in item
        assert "status" in item
        assert len(item["positive_points"]) > 0


def test_shastriya_pramana_relationships_shloka():
    assert "bphs_kalatra_sambandha" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["bphs_kalatra_sambandha"]
    assert "बृहत्पाराशर होराशास्त्र" in pramana["grantha"]
    assert "सप्तमेशे बलोपेते" in pramana["shloka_sanskrit"]
    assert "दांपत्य" in pramana["hindi_translation"] or "कलत्र" in pramana["hindi_translation"]


def test_render_relationships_view_no_unpack_crash(mock_chart, monkeypatch):
    """Ensure render_relationships_view does not crash when tabs=None."""
    mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr("streamlit.tabs", lambda t: mock_tabs)
    monkeypatch.setattr("streamlit.columns", lambda n: [MagicMock() for _ in range(n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.info", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.warning", lambda *args, **kwargs: None)

    # Call with default tabs=None
    render_relationships_view(mock_chart, tabs=None)
    assert len(mock_tabs) == 4


def test_app_tabs_registry_module24():
    """Verify MODULE_TABS_REGISTRY[24] has 4 synchronized tabs in app.py."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'24:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[24] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 4
    assert tabs == [
        "👫 जीवनसाथी व दांपत्य",
        "👨‍👩‍👦 परिवार व स्वजन",
        "🌟 मित्र व सहायक",
        "⚔️ शत्रु व विरोधी"
    ]
