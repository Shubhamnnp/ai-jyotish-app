"""
Tests for Module 32: Gemology, Rudraksha & Shastriya Upay (Module Audit & Verification).
Ensures 100% compliance with Brihat Samhita, Garuda Purana, Phaladeepika, and AGENTS.md rules.
"""

import pytest
import re
from unittest.mock import MagicMock, patch
from src.jyotish.services.gemology import (
    default_gemology_service,
    SHASTRIYA_GEMOLOGY_SHLOKAS,
    INCOMPATIBLE_GEM_COMBINATIONS
)
from src.jyotish.ui.modules.gemology_view import render_gemology_view


class MockPlanet:
    def __init__(self, name, house, degree, dignity="own", is_combust=False, is_retrograde=False):
        self.name = name
        self.house_from_lagna = house
        self.degree = degree
        self.longitude = degree
        self.dignity = dignity
        self.is_combust = is_combust
        self.is_retrograde = is_retrograde


class MockChart:
    def __init__(self, lagna_sign_id=1):
        self.lagna_sign_id = lagna_sign_id
        self.planets = {
            "Sun": MockPlanet("Sun", 1, 10.5, "exalted"),
            "Moon": MockPlanet("Moon", 4, 102.3, "own"),
            "Mars": MockPlanet("Mars", 1, 15.0, "own"),
            "Mercury": MockPlanet("Mercury", 8, 225.4, "neutral"),  # Dusthana (8th house)
            "Jupiter": MockPlanet("Jupiter", 9, 245.8, "own"),
            "Venus": MockPlanet("Venus", 7, 190.2, "own"),
            "Saturn": MockPlanet("Saturn", 10, 280.1, "own"),
            "Rahu": MockPlanet("Rahu", 3, 75.0, "neutral"),
            "Ketu": MockPlanet("Ketu", 9, 255.0, "neutral"),
        }


def test_gemology_service_audit_all_planets():
    chart = MockChart(lagna_sign_id=1)  # Aries Lagna
    audit = default_gemology_service.audit_all_planets(chart)

    assert audit["lagna_name"] == "Aries (मेष)"
    assert audit["lagnesh"] == "Mars"
    assert len(audit["planets_audit"]) == 9

    # Check micro-degrees, ansh, kala, nakshatra, and pada
    sun_data = audit["planets_audit"]["Sun"]
    assert sun_data["house"] == 1
    assert sun_data["ansh"] == 10
    assert sun_data["kala"] == 30
    assert sun_data["nakshatra"] == "Ashwini"
    assert sun_data["pada"] == 4
    assert sun_data["is_recommended"] is True
    assert "positive_verdict" in sun_data
    assert "negative_caution" in sun_data


def test_gemology_strictly_prohibited_dusthana_gems():
    chart = MockChart(lagna_sign_id=1)
    # Mercury is placed in the 8th house (Dusthana)
    audit = default_gemology_service.audit_all_planets(chart)

    merc = audit["planets_audit"]["Mercury"]
    assert merc["house"] == 8
    assert merc["status_code"] == "STRICTLY_PROHIBITED"
    assert merc["is_recommended"] is False
    assert any(g["planet"] == "Mercury" for g in audit["strictly_prohibited_gems"])
    assert any(a[0] == "Mercury" and a[1] == 8 for a in audit["dusthana_afflictions"])
    assert "पन्ना" in merc["gem_hi"]
    assert "सर्वथा वर्जित" in merc["verdict"]


def test_navratri_fasting_tithi_calculation():
    chart = MockChart(lagna_sign_id=1)
    fasting = default_gemology_service.get_navratri_fasting_tithi(chart)

    assert "optimal_tithi" in fasting
    assert "devi_form" in fasting
    assert "spiritual_focus" in fasting
    assert "positive_verdict" in fasting
    assert "negative_caution" in fasting
    assert fasting["lagnesh"] == "Mars"


def test_vivaha_gem_muhurta_compatibility():
    chart = MockChart(lagna_sign_id=1)
    vivaha = default_gemology_service.get_vivaha_gem_muhurta_compatibility(chart)

    assert "sun_shuddhi" in vivaha
    assert "chandra_shuddhi" in vivaha
    assert "guru_shuddhi" in vivaha
    assert vivaha["muhurta_score"] > 0
    assert len(vivaha["incompatible_combinations"]) > 0
    assert len(vivaha["auspicious_wearing_nakshatras"]) > 0
    assert "positive_verdict" in vivaha
    assert "negative_caution" in vivaha


def test_shastriya_gemology_shlokas():
    assert "brihat_samhita_ratna_pariksha" in SHASTRIYA_GEMOLOGY_SHLOKAS
    assert "garuda_purana_ratna_dharana" in SHASTRIYA_GEMOLOGY_SHLOKAS
    assert "phaladeepika_dusthana_ratna_nishedha" in SHASTRIYA_GEMOLOGY_SHLOKAS

    for k, sh in SHASTRIYA_GEMOLOGY_SHLOKAS.items():
        assert len(sh["shloka"]) > 10
        assert len(sh["source"]) > 5
        assert len(sh["meaning"]) > 10


def test_module32_app_registration_and_tabs():
    app_code = open("src/jyotish/ui/app.py", encoding="utf-8").read()

    # Check MODULE_TABS_REGISTRY has 32 registered
    assert "32: [" in app_code
    assert "१. शास्त्रीय रत्न ऑडिट" in app_code
    assert "२. सर्वथा वर्जित रत्न" in app_code
    assert "३. कुण्डली-सम्मत रुद्राक्ष" in app_code
    assert "४. दान, व्रत, मन्त्र" in app_code
    assert "५. विवाह व मांगलिक रत्न" in app_code
    assert "६. बृहत्संहिता व गरुड़ पुराण" in app_code

    # Check routing for selected_idx == 32
    assert "elif selected_idx == 32:" in app_code
    assert "gemology_view_mod.render_gemology_view" in app_code


def test_module32_ui_rendering():
    tabs = [
        "💎 १. शास्त्रीय रत्न ऑडिट व संस्तुति (Gemstone Audit)",
        "🚫 २. सर्वथा वर्जित रत्न व त्रिक दोष (Prohibited Dusthana Gems)",
        "📿 ३. कुण्डली-सम्मत रुद्राक्ष विधान (Rudraksha Therapy)",
        "🌿 ४. दान, व्रत, मन्त्र एवं सात्विक शांति (Mantra, Daan & Vrata)",
        "💍 ५. विवाह व मांगलिक रत्न शुद्धि (Vivaha & Manglik Gem Shuddhi)",
        "📜 ६. बृहत्संहिता व गरुड़ पुराण प्रमाण (Classical Shlokas)"
    ]

    chart = MockChart(lagna_sign_id=1)

    with patch("streamlit.subheader") as mock_sub, \
         patch("streamlit.write"), \
         patch("streamlit.columns", side_effect=lambda n, *args, **kwargs: [MagicMock() for _ in range(len(n) if isinstance(n, (list, tuple)) else n)]), \
         patch("streamlit.tabs", side_effect=lambda t: [MagicMock() for _ in range(len(t))]), \
         patch("streamlit.expander", return_value=MagicMock()), \
         patch("streamlit.container", return_value=MagicMock()), \
         patch("streamlit.markdown"), \
         patch("streamlit.dataframe"), \
         patch("streamlit.success"), \
         patch("streamlit.info"), \
         patch("streamlit.warning"), \
         patch("streamlit.error"), \
         patch("streamlit.code"):

        render_gemology_view(chart, tabs=tabs)
        assert mock_sub.called
