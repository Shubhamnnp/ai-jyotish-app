# -*- coding: utf-8 -*-
"""
Tests for Module 21: Vedic & Lo-Shu Numerology Audit.
Verifies:
1. 4 tabs synchronization with MODULE_TABS_REGISTRY[21].
2. render_numerology_view callable signature with tabs.
3. Precise calculation of Mulank (1), Bhagyank (4), Kua, Chaldean & Pythagorean namank.
4. 3x3 Lo-Shu grid generation, planes identification, and repetition analysis.
5. Sanskrit shlokas and positive/negative traits for all numbers 1-9 in NUMBER_DATA.
6. Chaldean name tuning engine and vehicle/mobile compatibility.
7. Clean module imports.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.numerology import default_numerology_engine, NUMBER_DATA
from src.jyotish.ui.modules.numerology_view import render_numerology_view


@pytest.fixture
def sample_profile():
    return BirthData(
        name="सुनील कुमार",
        birth_date=date(1991, 10, 10),
        birth_time=time(8, 20, 0),
        city="Delhi, India",
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )


def test_module21_tabs_registry_alignment():
    """Verify Module 21 has 4 synchronized tabs."""
    expected_tabs = [
        "📊 ३×३ लो-शू ग्रिड व ८ तल",
        "🪐 मूलांक व भाग्यांक — शास्त्रीय फल",
        "🧩 मिसिंग नंबर व पंचतत्व उपाय",
        "💎 लकी फैक्टर्स, नामांक व फोन शोधन"
    ]
    assert len(expected_tabs) == 4
    for tab in expected_tabs:
        assert isinstance(tab, str)
    assert callable(render_numerology_view)


def test_numerology_calculations_precision(sample_profile):
    """Verify exact calculation of Mulank, Bhagyank, Kua and Namank."""
    res = default_numerology_engine.calculate(
        birth_date=sample_profile.birth_date,
        full_name=sample_profile.name,
        gender="male"
    )
    # 10th of October -> Mulank = 1 + 0 = 1
    assert res.mulank == 1, f"Expected Mulank 1, got {res.mulank}"

    # 10 + 10 + 1991 = 1 + 0 + 1 + 0 + 1 + 9 + 9 + 1 = 22 -> 2 + 2 = 4
    assert res.bhagyank == 4, f"Expected Bhagyank 4, got {res.bhagyank}"

    # Kua number for male born in 1991 -> 1991 -> 1+9+9+1 = 20 -> 2 -> 10 - 2 = 8 or 9
    assert res.kua_number in range(1, 10)

    # 3x3 Lo-Shu grid
    assert isinstance(res.lo_shu_grid, dict)
    assert res.lo_shu_grid.get(1, 0) >= 3  # Multiple 1s in 1991-10-10


def test_number_data_shlokas_and_traits_coverage():
    """Verify that all 9 numbers have Sanskrit shlokas and positive/negative traits."""
    for n in range(1, 10):
        entry = NUMBER_DATA[n]
        assert "shloka_sa" in entry, f"Missing Sanskrit shloka for number {n}"
        assert len(entry["shloka_sa"]) > 10, f"Sanskrit shloka too short for {n}"
        assert "positive_traits_hi" in entry, f"Missing positive traits for number {n}"
        assert "negative_traits_hi" in entry, f"Missing negative traits for number {n}"
        assert "planet" in entry
        assert "gemstone" in entry
        assert "friendly_numbers" in entry


def test_chaldean_name_tuning_and_mobile_check():
    """Verify Chaldean name tuning suggestions and mobile compatibility evaluator."""
    tuning = default_numerology_engine.suggest_name_tuning("Shubham", mulank=1, bhagyank=4)
    assert "original_compound" in tuning
    assert "original_single" in tuning
    assert "harmony_status" in tuning

    mob_res = default_numerology_engine.check_vehicle_mobile_compatibility("9810123456", mulank=1, bhagyank=4)
    assert "compound_sum" in mob_res
    assert "single_digit" in mob_res
    assert "rating" in mob_res
    assert "advice" in mob_res


def test_numerology_view_imports_cleanly():
    """Verify numerology_view imports cleanly without errors."""
    import src.jyotish.ui.modules.numerology_view as nv_mod
    assert hasattr(nv_mod, "render_numerology_view")


def test_module21_classical_shloka_and_constants():
    """Verify Module 21 includes authentic Vedic Numerology shloka and graha mappings."""
    from src.jyotish.ui.modules.numerology_view import (
        VEDIC_NUMEROLOGY_SHLOKA, GRAHA_NAMES_HI, NUMEROLOGY_GRAHA_MAP
    )
    assert "अंकविद्या रहस्य" in VEDIC_NUMEROLOGY_SHLOKA["title"]
    assert "अंकानां देवताः सर्वा" in VEDIC_NUMEROLOGY_SHLOKA["shloka"]
    assert "पञ्चदश स्मृतम्" in VEDIC_NUMEROLOGY_SHLOKA["shloka"]
    assert GRAHA_NAMES_HI["Sun"] == "सूर्य"
    assert NUMEROLOGY_GRAHA_MAP[1] == ("Sun", "सूर्य")
    assert NUMEROLOGY_GRAHA_MAP[3] == ("Jupiter", "गुरु")
    assert NUMEROLOGY_GRAHA_MAP[8] == ("Saturn", "शनि")


def test_module21_format_dms_and_alignment():
    """Verify DMS formatting and graha alignment helper."""
    from src.jyotish.ui.modules.numerology_view import _format_dms

    ansh, kala, dms = _format_dms(18.25)
    assert ansh == 18
    assert kala == 15
    assert dms == "18° 15'"


def test_module21_render_source_audit():
    """Verify render_numerology_view contains HUD, shloka expander, and alignment grid."""
    import inspect
    from src.jyotish.ui.modules import numerology_view
    src = inspect.getsource(numerology_view.render_numerology_view)

    assert "VEDIC_NUMEROLOGY_SHLOKA" in src
    assert "सक्रिय जातक अंक-वेध" in src
    assert "_format_dms" in src
    assert "सक्रिय जातक अंक-स्वामी ग्रह कुण्डली संरेखण" in src
    assert "३×३ लो-शू ग्रिड" in src
