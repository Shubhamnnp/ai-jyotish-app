import pytest
from unittest.mock import MagicMock
from src.jyotish.core.ishta_devata import IshtaDevataEngine
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.modules.pooja_view import render_pooja_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1  # Aries (Mesha, Lagnesha Mars)
    chart.lagna_sign_name = "Aries"
    chart.lagna_degree = 12.0
    chart.atmakaraka = "Sun"
    chart.jaimini = None
    chart.vargas = {}

    class PlanetMock:
        def __init__(self, sign_id, house_from_lagna, degree=15.0, speed=1.0, dignity="neutral", sign_name="मेष"):
            self.sign_id = sign_id
            self.house_from_lagna = house_from_lagna
            self.degree = degree
            self.speed = speed
            self.dignity = dignity
            self.sign_name = sign_name

    chart.planets = {
        "Sun": PlanetMock(1, 1, degree=28.5),     # Sun at 28.5 deg -> Atmakaraka!
        "Moon": PlanetMock(2, 2, degree=14.0),
        "Mars": PlanetMock(1, 1, degree=20.0),    # Lagnesha Mars
        "Mercury": PlanetMock(6, 6, degree=10.0),
        "Jupiter": PlanetMock(9, 9, degree=25.0),
        "Venus": PlanetMock(12, 12, degree=18.0),
        "Saturn": PlanetMock(11, 11, degree=8.0),
        "Rahu": PlanetMock(8, 8, degree=5.0),
        "Ketu": PlanetMock(2, 2, degree=5.0)
    }
    return chart


def test_ishta_devata_engine_analysis(mock_chart):
    res = IshtaDevataEngine.analyze(mock_chart)

    # 1. Atmakaraka & Ishta Devata
    assert res["atmakaraka"] == "Sun"
    assert "karakamsha_sign" in res
    assert "ishta_deity" in res
    assert "ishta_mantra" in res
    assert "ishta_beej" in res

    # 2. Deities
    assert "palana_deity" in res
    assert "dharma_deity" in res
    assert "mantra_deity" in res
    assert "kula_deity" in res

    # 3. Navratri Guidelines & Optimal Fasting Tithi
    assert "navratri" in res
    nv = res["navratri"]
    assert "optimal_fasting_tithi" in nv
    assert "optimal_fasting_tithi_reason" in nv
    assert len(nv["nine_days"]) == 9
    assert ("तृतीया" in nv["optimal_fasting_tithi"] or "प्रतिपदा" in nv["optimal_fasting_tithi"] or "अष्टमी" in nv["optimal_fasting_tithi"])


def test_shastriya_pramana_ishta_shloka():
    assert "jaimini_ishta_moksha" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["jaimini_ishta_moksha"]
    assert "जैमिनी" in pramana["grantha"]
    assert "कारकांश" in pramana["shloka_sanskrit"]
    assert "मोक्ष" in pramana["anuvad_hi"] or "इष्ट" in pramana["anuvad_hi"]


def test_render_pooja_view_no_unpack_crash(mock_chart, monkeypatch):
    """Ensure render_pooja_view unpacks 5 tabs cleanly with default tabs=None."""
    mock_tabs = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    monkeypatch.setattr("streamlit.tabs", lambda t: mock_tabs)
    monkeypatch.setattr("streamlit.columns", lambda n: [MagicMock() for _ in range(n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.caption", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.code", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.expander", lambda *args, **kwargs: MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))

    # Call with default tabs=None
    render_pooja_view(mock_chart, tabs=None)
    assert len(mock_tabs) == 5


def test_app_tabs_registry_module27():
    """Verify MODULE_TABS_REGISTRY[27] in app.py has 5 synchronized tabs."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'27:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[27] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 5
    assert tabs == [
        "🕉️ इष्टदेवता व मोक्ष",
        "📿 कुलदेवता व मन्त्र साधना",
        "🪔 नित्य पूजा विधान",
        "📅 व्रत व उपवास नियम",
        "🚩 नवरात्रि ९ दिवसीय विधान"
    ]
