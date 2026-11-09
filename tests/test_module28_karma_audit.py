import pytest
from unittest.mock import MagicMock
from src.jyotish.core.karmaphala import KarmaphalaEngine
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.modules.karma_view import render_karma_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1  # Aries (Mesha, Lagnesha Mars)
    chart.lagna_degree = 15.0
    chart.atmakaraka = "Sun"

    class PlanetMock:
        def __init__(self, sign_id, house_from_lagna, degree=15.0, dignity="neutral", is_combust=False, is_retrograde=False, sign_name="Aries"):
            self.sign_id = sign_id
            self.house_from_lagna = house_from_lagna
            self.degree = degree
            self.dignity = dignity
            self.is_combust = is_combust
            self.is_retrograde = is_retrograde
            self.sign_name = sign_name

    chart.planets = {
        "Sun": PlanetMock(1, 1, dignity="exalted", sign_name="Aries"),
        "Moon": PlanetMock(4, 4, dignity="own", sign_name="Cancer"),
        "Mars": PlanetMock(10, 10, dignity="exalted", sign_name="Capricorn"),
        "Mercury": PlanetMock(6, 6, dignity="exalted", sign_name="Virgo"),
        "Jupiter": PlanetMock(9, 9, dignity="own", sign_name="Sagittarius"),
        "Venus": PlanetMock(7, 7, dignity="own", sign_name="Libra"),
        "Saturn": PlanetMock(11, 11, dignity="own", sign_name="Aquarius"),
        "Rahu": PlanetMock(3, 3, dignity="neutral", sign_name="Gemini"),
        "Ketu": PlanetMock(9, 9, dignity="neutral", sign_name="Sagittarius")
    }

    class HouseMock:
        def __init__(self, house_num, sign_id, sign_name, lord, occupants=None):
            self.house_num = house_num
            self.sign_id = sign_id
            self.sign_name = sign_name
            self.lord = lord
            self.occupants = occupants or []
            self.aspecting_planets = []

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
    return chart


def test_karmaphala_engine_analysis(mock_chart):
    res = KarmaphalaEngine.analyze(mock_chart)

    # 1. Career (Business vs Job)
    assert "career" in res
    car = res["career"]
    assert "business_score" in car
    assert "job_score" in car
    assert "recommendation_hi" in car
    assert len(car["sectors"]) > 0

    # 2. Education & Intellect
    assert "education" in res
    edu = res["education"]
    assert "education_score" in edu

    # 3. Morals & Integrity
    assert "morals" in res
    mor = res["morals"]
    assert "morality_score" in mor
    assert "integrity_level" in mor

    # 4. Vices & Addictions
    assert "vices" in res
    vic = res["vices"]
    assert "addiction_score" in vic
    assert "risk_level" in vic

    # 5. Inheritance & Inner Peace
    assert "inheritance" in res
    assert "peace" in res

    # 6. Past Life Karma & Atmakaraka
    assert "karma" in res
    krm = res["karma"]
    assert "purva_punya_score" in krm
    assert "atmakaraka" in krm
    assert "active_debts" in krm


def test_shastriya_pramana_karma_vipaka_shloka():
    assert "phaladeepika_karma_vipaka" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["phaladeepika_karma_vipaka"]
    assert "फलदीपिका" in pramana["grantha"]
    assert "यदुपचितमन्यजन्मनि" in pramana["shloka_sanskrit"]
    assert "कर्म" in pramana["anuvad_hi"]


def test_render_karma_view_no_unpack_crash(mock_chart, monkeypatch):
    """Ensure render_karma_view unpacks 6 tabs cleanly with default tabs=None."""
    mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr("streamlit.tabs", lambda t: mock_tabs)
    monkeypatch.setattr("streamlit.columns", lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, (list, tuple)) else n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.caption", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.info", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.success", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.warning", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.progress", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.expander", lambda *args, **kwargs: MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))

    # Call with default tabs=None
    render_karma_view(mock_chart, tabs=None)
    assert len(mock_tabs) == 6


def test_app_tabs_registry_module28():
    """Verify MODULE_TABS_REGISTRY[28] in app.py has 6 synchronized tabs."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'28:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[28] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 6
    assert tabs == [
        "💼 नौकरी बनाम व्यापार",
        "🎓 शिक्षा व मेधा",
        "⚖️ आचरण व प्रवृत्तियां",
        "🚫 व्यसन व प्रलोभन",
        "🏛️ पैतृक संपत्ति व सुख",
        "🕉️ पूर्वजन्म प्रारब्ध व ऋण"
    ]
