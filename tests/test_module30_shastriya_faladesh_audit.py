import pytest
from unittest.mock import MagicMock
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.services.shastriya_faladesh import (
    default_shastriya_faladesh_engine,
    LIFE_DIMENSIONS_50,
    PLANET_NAMES_HI
)
from src.jyotish.ui.shastriya_faladesh_view import render_shastriya_faladesh_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1
    chart.lagna_sign_name = "Aries"
    chart.lagna_degree = 15.5
    chart.atmakaraka = "Sun"

    class PlanetMock:
        def __init__(self, name, sign_id, sign_name, sign_degree, house_from_lagna, house_from_moon=1, dignity="own", is_combust=False, is_retrograde=False, nak_name="Ashwini", nak_pada=1, nak_lord="Ketu"):
            self.name = name
            self.sign_id = sign_id
            self.sign_name = sign_name
            self.sign_degree = sign_degree
            self.degree = sign_degree
            self.house_from_lagna = house_from_lagna
            self.house_from_moon = house_from_moon
            self.dignity = dignity
            self.is_combust = is_combust
            self.is_retrograde = is_retrograde
            self.nakshatra_name = nak_name
            self.nakshatra = nak_name
            self.nakshatra_pada = nak_pada
            self.pada = nak_pada
            self.nakshatra_lord = nak_lord

    chart.planets = {
        "Sun": PlanetMock("Sun", 1, "Aries", 10.25, 1, 10, dignity="exalted", nak_name="Ashwini", nak_pada=4, nak_lord="Ketu"),
        "Moon": PlanetMock("Moon", 4, "Cancer", 20.5, 4, 1, dignity="own", nak_name="Ashlesha", nak_pada=2, nak_lord="Mercury"),
        "Mars": PlanetMock("Mars", 10, "Capricorn", 28.0, 10, 7, dignity="exalted", nak_name="Dhanishta", nak_pada=2, nak_lord="Mars"),
        "Mercury": PlanetMock("Mercury", 6, "Virgo", 15.0, 6, 3, dignity="exalted", nak_name="Hasta", nak_pada=2, nak_lord="Moon"),
        "Jupiter": PlanetMock("Jupiter", 9, "Sagittarius", 12.0, 9, 6, dignity="own", nak_name="Moola", nak_pada=4, nak_lord="Ketu"),
        "Venus": PlanetMock("Venus", 7, "Libra", 18.0, 7, 4, dignity="own", nak_name="Swati", nak_pada=4, nak_lord="Rahu"),
        "Saturn": PlanetMock("Saturn", 11, "Aquarius", 5.0, 11, 8, dignity="own", nak_name="Dhanishta", nak_pada=4, nak_lord="Mars"),
        "Rahu": PlanetMock("Rahu", 3, "Gemini", 14.0, 3, 12, dignity="neutral", nak_name="Ardra", nak_pada=3, nak_lord="Rahu"),
        "Ketu": PlanetMock("Ketu", 9, "Sagittarius", 14.0, 9, 6, dignity="neutral", nak_name="Purvashadha", nak_pada=1, nak_lord="Venus")
    }

    class HouseMock:
        def __init__(self, house_num, sign_id, sign_name, lord, occupants=None):
            self.house_number = house_num
            self.sign_id = sign_id
            self.sign_name = sign_name
            self.lord = lord
            self.cusp_longitude = (sign_id - 1) * 30.0 + 15.0
            self.occupants = occupants or []

    signs = [
        ("Aries", "Mars"), ("Taurus", "Venus"), ("Gemini", "Mercury"),
        ("Cancer", "Moon"), ("Leo", "Sun"), ("Virgo", "Mercury"),
        ("Libra", "Venus"), ("Scorpio", "Mars"), ("Sagittarius", "Jupiter"),
        ("Capricorn", "Saturn"), ("Aquarius", "Saturn"), ("Pisces", "Jupiter")
    ]
    chart.houses = [
        HouseMock(i + 1, i + 1, signs[i][0], signs[i][1], [p for p, obj in chart.planets.items() if obj.house_from_lagna == i + 1])
        for i in range(12)
    ]

    chart.ashtakavarga = MagicMock()
    chart.ashtakavarga.sav = [30, 28, 32, 29, 31, 26, 33, 27, 34, 30, 36, 25]

    chart.shadbala = MagicMock()
    chart.shadbala.bhava_bala = {i + 1: 300.0 + i * 15.0 for i in range(12)}
    chart.shadbala.planets = {
        p: MagicMock(total_virupas=400.0, strength_ratio=1.2, total_rupas=6.67)
        for p in chart.planets
    }

    return chart


def test_shastriya_pramana_bphs_shastriya_faladesh():
    """Verify classical BPHS shloka in SHASTRIYA_SHLOKAS."""
    assert "bphs_shastriya_faladesh_srishti" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["bphs_shastriya_faladesh_srishti"]
    assert "अथातः सर्वशास्त्रज्ञं" in pramana["shloka_sanskrit"]
    assert "बृहत्पाराशर होराशास्त्रम्" in pramana["grantha"]
    assert "शुभाशुभ फल" in pramana["grantha"]
    assert "पराशर" in pramana["anuvad_hi"]


def test_50_life_dimensions_presence_and_structure():
    """Verify exactly 50 dimensions of life are configured with proper schemas."""
    assert len(LIFE_DIMENSIONS_50) == 50
    for dim in LIFE_DIMENSIONS_50:
        assert "id" in dim
        assert "name_hi" in dim
        assert "category" in dim
        assert "desc" in dim
        assert "houses" in dim
        assert "karakas" in dim


def test_shastriya_faladesh_engine_synthesis(mock_chart):
    """Verify dimension synthesis produces full evidence and honest positives/negatives."""
    res = default_shastriya_faladesh_engine.synthesize_dimension(mock_chart, 1)

    assert "dimension" in res
    assert res["dimension"]["id"] == 1
    assert "positive_pct" in res
    assert "negative_pct" in res
    assert res["positive_pct"] + res["negative_pct"] == 100

    assert "houses_data" in res
    assert len(res["houses_data"]) > 0

    assert "planets_data" in res
    assert len(res["planets_data"]) > 0

    assert "positives" in res
    assert "negatives" in res
    assert "citations" in res
    assert "remedies" in res

    # 100 FAQs
    assert "faqs_100" in res
    assert len(res["faqs_100"]) == 100


def test_render_shastriya_faladesh_view_no_unpack_crash(mock_chart, monkeypatch):
    """Verify render_shastriya_faladesh_view unpacks 4 tabs without errors."""
    created_tabs = []
    def mock_tabs_fn(t):
        tabs = [MagicMock() for _ in range(len(t))]
        created_tabs.append(tabs)
        return tabs

    monkeypatch.setattr("streamlit.tabs", mock_tabs_fn)
    monkeypatch.setattr("streamlit.columns", lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, (list, tuple)) else n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.caption", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.info", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.success", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.warning", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.dataframe", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.table", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.selectbox", lambda *args, **kwargs: "1. आजीविका, करियर एवं व्यवसाय (Career & Profession)")
    monkeypatch.setattr("streamlit.text_input", lambda *args, **kwargs: "")
    monkeypatch.setattr("streamlit.expander", lambda *args, **kwargs: MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))

    # Call with default tabs=None
    render_shastriya_faladesh_view(mock_chart, tabs=None)
    assert len(created_tabs[0]) == 4


def test_app_tabs_registry_module30():
    """Verify MODULE_TABS_REGISTRY[30] in app.py has 4 synchronized tabs."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'30:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[30] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 4
    assert tabs == [
        "🌟 ५० जीवन आयाम",
        "❓ १०० प्रश्न-उत्तर (FAQs)",
        "🔬 सर्व-गणना संश्लेषण",
        "📜 ग्रन्थ प्रमाण व उपाय"
    ]
