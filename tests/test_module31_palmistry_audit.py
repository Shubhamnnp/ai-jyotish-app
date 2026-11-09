import pytest
from unittest.mock import MagicMock
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.core.palmistry import (
    HastarekhaEngine,
    PalmInputProfile
)
from src.jyotish.ui.modules.palmistry_view import render_palmistry_view


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1
    chart.lagna_degree = 15.5

    class PlanetMock:
        def __init__(self, name, sign_name, degree=15.0, nak_name="Ashwini", nak_pada=1, is_retrograde=False):
            self.name = name
            self.sign_name = sign_name
            self.degree = degree
            self.sign_degree = degree
            self.nakshatra_name = nak_name
            self.nakshatra = nak_name
            self.nakshatra_pada = nak_pada
            self.pada = nak_pada
            self.is_retrograde = is_retrograde

    chart.planets = {
        "Sun": PlanetMock("Sun", "Aries", 10.25, nak_name="Ashwini", nak_pada=4),
        "Moon": PlanetMock("Moon", "Cancer", 20.5, nak_name="Ashlesha", nak_pada=2),
        "Mars": PlanetMock("Mars", "Capricorn", 28.0, nak_name="Dhanishta", nak_pada=2),
        "Mercury": PlanetMock("Mercury", "Virgo", 15.0, nak_name="Hasta", nak_pada=2),
        "Jupiter": PlanetMock("Jupiter", "Sagittarius", 12.0, nak_name="Moola", nak_pada=4),
        "Venus": PlanetMock("Venus", "Libra", 18.0, nak_name="Swati", nak_pada=4),
        "Saturn": PlanetMock("Saturn", "Aquarius", 5.0, nak_name="Dhanishta", nak_pada=4)
    }
    return chart


def test_shastriya_pramana_samudrika():
    """Verify classical Samudrika Shastra shloka in SHASTRIYA_SHLOKAS."""
    assert "samudrika_shastra_lakshana" in SHASTRIYA_SHLOKAS
    pramana = SHASTRIYA_SHLOKAS["samudrika_shastra_lakshana"]
    assert "आयुरेखा यदा दीर्घा" in pramana["shloka_sanskrit"]
    assert "गरुड़ पुराण" in pramana["grantha"]
    assert "सामुद्रिक" in pramana["grantha"]
    assert "हस्त रेखाएं" in pramana["anuvad_hi"]


def test_hastarekha_engine_analyze_palm(mock_chart):
    """Verify palm analysis and chart cross-referencing with degree, ansh, kala, pada."""
    profile = PalmInputProfile()
    report = HastarekhaEngine.analyze_palm(profile, chart=mock_chart)

    assert report.vitality_score > 0
    assert report.career_score > 0
    assert report.intellect_score > 0
    assert report.relationship_score > 0
    assert report.spiritual_score > 0
    assert report.overall_samudrika_grade != ""

    # Kundali correlations
    assert len(report.kundali_palm_correlations) >= 4
    for corr in report.kundali_palm_correlations:
        assert "domain" in corr
        assert "status" in corr
        assert "explanation" in corr
        # Must contain precise degrees / nakshatras
        assert any(term in corr["explanation"] for term in ["Aries", "Cancer", "Sagittarius", "Aquarius", "नक्षत्र", "पद", "°"])


def test_render_palmistry_view_no_unpack_crash(mock_chart, monkeypatch):
    """Verify render_palmistry_view unpacks 7 tabs cleanly."""
    mock_tabs = [MagicMock() for _ in range(7)]
    monkeypatch.setattr("streamlit.tabs", lambda t: mock_tabs)
    monkeypatch.setattr("streamlit.columns", lambda n, *args, **kwargs: [MagicMock() for _ in range(len(n) if isinstance(n, (list, tuple)) else n)])
    monkeypatch.setattr("streamlit.subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.caption", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.write", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.info", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.success", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.warning", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.dataframe", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.radio", lambda *args, **kwargs: "✋ दायां हाथ (Right)")
    monkeypatch.setattr("streamlit.selectbox", lambda *args, **kwargs: "Square (व्यावहारिक)")
    monkeypatch.setattr("streamlit.slider", lambda *args, **kwargs: 3)
    monkeypatch.setattr("streamlit.checkbox", lambda *args, **kwargs: True)
    monkeypatch.setattr("streamlit.camera_input", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.file_uploader", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.button", lambda *args, **kwargs: False)
    monkeypatch.setattr("streamlit.metric", lambda *args, **kwargs: None)
    monkeypatch.setattr("streamlit.expander", lambda *args, **kwargs: MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))

    # Call with default tabs=None
    render_palmistry_view(mock_chart, tabs=None)
    assert len(mock_tabs) == 7


def test_app_tabs_registry_module31():
    """Verify MODULE_TABS_REGISTRY[31] in app.py has 7 synchronized tabs."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'31:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[31] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 7
    assert tabs == [
        "✋ १. विज़ुअल हस्त-नक्शा (Palm Map)",
        "📜 २. समग्र शास्त्रीय फलादेश (Predictions)",
        "🪐 ३. नवग्रह पर्वत एवं बल (Mounts)",
        "📏 ४. रेखाएं एवं आयु काल-विभाजन (Age Dating)",
        "⚜️ ५. विशिष्ट दिव्य चिन्ह व योग (Yogas)",
        "🔗 ६. कुण्डली-हस्तरेखा समन्वय (Synthesis)",
        "🪔 ७. दोष निवारण एवं वैदिक उपाय (Remedies)"
    ]
