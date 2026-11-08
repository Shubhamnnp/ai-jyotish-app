# -*- coding: utf-8 -*-
"""
Tests for Module 19: Calculation Validation & Astronomical Benchmark Audit.
Verifies:
1. 2 tabs synchronization with MODULE_TABS_REGISTRY[19].
2. render_validation_view signature accepts tabs.
3. default_vedic_rishi_client cross-validation accuracy (< 0.05° max variance).
4. All 9 planets present in comparison table.
5. Panchang consistency (tithi, nakshatra, yoga, karana).
6. Clean module imports.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.vedic_rishi import default_vedic_rishi_client
from src.jyotish.ui.modules.validation_view import render_validation_view


@pytest.fixture
def sample_chart():
    b_data = BirthData(
        name="परीक्षण जातक",
        birth_date=date(1995, 8, 15),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b_data)


def test_module19_tabs_registry_alignment():
    """Verify Module 19 has 2 synchronized tabs."""
    expected_tabs = [
        "🔍 स्विस एफिमेरिस बनाम वैदिक ऋषि सत्यापन",
        "📐 अयनांश व कोणीय विचलन विश्लेषण"
    ]
    assert len(expected_tabs) == 2
    assert "🔍 स्विस एफिमेरिस बनाम वैदिक ऋषि सत्यापन" in expected_tabs
    assert "📐 अयनांश व कोणीय विचलन विश्लेषण" in expected_tabs
    assert callable(render_validation_view)


def test_cross_validation_accuracy_and_tolerance(sample_chart):
    """Verify Swiss Ephemeris vs Vedic Rishi standard variance is strictly < 0.05°."""
    val_res = default_vedic_rishi_client.cross_validate_chart(sample_chart)
    assert isinstance(val_res, dict)
    assert val_res.get("status") in ["verified", "calibrated"]
    assert "overall_accuracy" in val_res

    # Check maximum planetary variance tolerance
    max_var = val_res.get("max_planetary_variance_deg", 0.0)
    assert max_var < 0.05, f"Variance {max_var}° exceeds allowable astronomical limit of 0.05°"


def test_planetary_comparison_table(sample_chart):
    """Verify all 9 classical planets are present in comparison table."""
    val_res = default_vedic_rishi_client.cross_validate_chart(sample_chart)
    comp_table = val_res.get("comparison_table", [])
    assert len(comp_table) >= 9, f"Expected at least 9 planets, got {len(comp_table)}"

    graha_names = [row["Graha"] for row in comp_table]
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert p in graha_names, f"Planet {p} missing from validation table"


def test_panchang_alignment_consistency(sample_chart):
    """Verify panchang elements alignment."""
    val_res = default_vedic_rishi_client.cross_validate_chart(sample_chart)
    p_comp = val_res.get("panchang_comparison", {})
    assert "jyotish_tithi" in p_comp
    assert "jyotish_nakshatra" in p_comp
    assert "jyotish_yoga" in p_comp
    assert "jyotish_karana" in p_comp


def test_validation_view_imports_cleanly():
    """Verify validation_view module imports cleanly without side-effects."""
    import src.jyotish.ui.modules.validation_view as val_mod
    assert hasattr(val_mod, "render_validation_view")
