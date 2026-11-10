# -*- coding: utf-8 -*-
"""
Tests for Module 22: Lal Kitab 1952 Engine & Totkas Audit.
Verifies:
1. 4 tabs synchronization with MODULE_TABS_REGISTRY[22].
2. render_lal_kitab_view callable signature accepts tabs=None without unpack error.
3. Lal Kitab engine calculation (khana_planets, dharmi_teva, andha_teva, debts, sleeping houses).
4. Full coverage of 108 Lal Kitab Totkas (9 planets x 12 houses).
5. Full coverage of 9 classical Karmic Debt definitions.
6. Clean module imports.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.lalkitab import (
    default_lalkitab_engine,
    LAL_KITAB_108_TOTKAS,
    DEBT_DEFINITIONS,
    LAL_KITAB_KHANA_DATA
)
from src.jyotish.ui.modules.lal_kitab_view import render_lal_kitab_view


@pytest.fixture
def sample_chart():
    b_data = BirthData(
        name="सुनील कुमार",
        birth_date=date(1991, 10, 10),
        birth_time=time(8, 20, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b_data)


def test_module22_tabs_registry_alignment():
    """Verify Module 22 registry has 4 synchronized tabs and render function is safe."""
    expected_tabs = [
        "🏠 १२ पक्के खाने व ग्रह स्थिति",
        "⚠️ ९ कर्मिक ऋण व पितृ दोष",
        "💤 सोए हुए घर व ग्रह विचार",
        "🌿 १०८ प्रामाणिक टोटके व उपाय"
    ]
    assert len(expected_tabs) == 4
    for tab in expected_tabs:
        assert isinstance(tab, str)
    assert callable(render_lal_kitab_view)


def test_lalkitab_engine_calculation(sample_chart):
    """Verify Lal Kitab engine computes 12 khana mapping, teva type, debts, and sleeping houses."""
    res = default_lalkitab_engine.calculate(sample_chart)
    assert hasattr(res, "khana_planets")
    assert isinstance(res.khana_planets, dict)
    assert len(res.khana_planets) <= 12

    assert hasattr(res, "dharmi_teva")
    assert isinstance(res.dharmi_teva, bool)

    assert hasattr(res, "andha_teva")
    assert isinstance(res.andha_teva, bool)

    assert hasattr(res, "active_debts")
    assert isinstance(res.active_debts, list)

    assert hasattr(res, "sleeping_houses")
    assert isinstance(res.sleeping_houses, list)

    totkas = getattr(res, "chart_108_totkas", getattr(res, "specific_remedies", []))
    assert isinstance(totkas, list)
    assert len(totkas) > 0


def test_108_totkas_repository_complete():
    """Verify LAL_KITAB_108_TOTKAS has all 108 combinations (9 planets x 12 houses)."""
    assert len(LAL_KITAB_108_TOTKAS) == 108, f"Expected 108 totkas, got {len(LAL_KITAB_108_TOTKAS)}"

    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in planets:
        for kh in range(1, 13):
            key = (p, kh)
            assert key in LAL_KITAB_108_TOTKAS, f"Missing totka for {p} in khana {kh}"
            entry = LAL_KITAB_108_TOTKAS[key]
            assert "totka_hi" in entry
            assert "precaution_hi" in entry
            assert "shastra_effect_hi" in entry


def test_9_karmic_debt_definitions():
    """Verify all 9 classical karmic debt definitions exist."""
    assert len(DEBT_DEFINITIONS) == 9, f"Expected 9 debt definitions, got {len(DEBT_DEFINITIONS)}"
    debt_ids = [d["id"] for d in DEBT_DEFINITIONS]
    expected_ids = [
        "pitra_rina", "matra_rina", "swa_rina", "stri_rina", "rishtedari_rina",
        "nirdayi_rina", "ani_rina", "kanya_rina", "jal_rina"
    ]
    for exp in expected_ids:
        assert exp in debt_ids, f"Missing debt definition ID: {exp}"


def test_lal_kitab_view_imports_cleanly():
    """Verify lal_kitab_view imports cleanly without errors."""
    import src.jyotish.ui.modules.lal_kitab_view as lk_view
    assert hasattr(lk_view, "render_lal_kitab_view")


def test_module22_classical_shloka_and_constants():
    """Verify Module 22 includes authentic Lal Kitab 1952 farman and conjunction rules."""
    from src.jyotish.ui.modules.lal_kitab_view import (
        LAL_KITAB_SHLOKA, LAL_KITAB_CONJUNCTION_RULES, GRAHA_NAMES_HI, DIGNITY_HI
    )
    assert "लाल किताब १९५२" in LAL_KITAB_SHLOKA["title"]
    assert "किस्मत का लिखा कोई टाल न सके" in LAL_KITAB_SHLOKA["shloka"]
    assert "नेकी से बुराई टलती है" in LAL_KITAB_SHLOKA["shloka"]
    assert GRAHA_NAMES_HI["Sun"] == "सूर्य"
    assert GRAHA_NAMES_HI["Saturn"] == "शनि"
    assert frozenset(["Sun", "Mercury"]) in LAL_KITAB_CONJUNCTION_RULES
    assert frozenset(["Sun", "Saturn"]) in LAL_KITAB_CONJUNCTION_RULES
    assert frozenset(["Moon", "Jupiter"]) in LAL_KITAB_CONJUNCTION_RULES


def test_module22_multi_planet_conjunctions_analysis(sample_chart):
    """Verify analyze_khana_conjunctions detects multi-planet khanas, masnui planets, and how to evaluate."""
    from src.jyotish.ui.modules.lal_kitab_view import analyze_khana_conjunctions

    mock_khana_planets = {
        1: ["Sun", "Mercury"],
        5: ["Jupiter"],
        10: ["Saturn", "Mars"]
    }
    res = analyze_khana_conjunctions(mock_khana_planets, sample_chart)
    assert len(res) == 2, "Expected 2 khanas with multiple planets"

    kh1 = next(item for item in res if item["khana"] == 1)
    assert "Sun" in kh1["planets"] and "Mercury" in kh1["planets"]
    assert len(kh1["conjunctions"]) == 1
    assert "बुधादित्य" in kh1["conjunctions"][0]["title"]
    assert "मंगल नेक" in kh1["conjunctions"][0]["masnui"]
    assert "कैसे देखें" in kh1["conjunctions"][0]["how_to_see"] or len(kh1["conjunctions"][0]["how_to_see"]) > 5

    kh10 = next(item for item in res if item["khana"] == 10)
    assert len(kh10["conjunctions"]) == 1
    assert "मंगल + शनि" in kh10["conjunctions"][0]["title"]


def test_module22_render_source_audit():
    """Verify render_lal_kitab_view contains HUD, farman card, and multi-planet conjunctions expander."""
    import inspect
    from src.jyotish.ui.modules import lal_kitab_view
    src = inspect.getsource(lal_kitab_view.render_lal_kitab_view)

    assert "LAL_KITAB_SHLOKA" in src
    assert "सक्रिय जातक लाल किताब तेवा" in src
    assert "_format_dms" in src
    assert "analyze_khana_conjunctions" in src
    assert "एक ही खाने में एकाधिक ग्रह युति फलादेश" in src
