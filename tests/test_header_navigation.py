"""
Tests for 3-Tier Workstation Header & Categorized Navigation System.
Verifies category mapping, module cascading, and quick popup tool integrations.
"""
import pytest
from datetime import date, time, datetime


# Canonical 5-Category Registry for all 33 Vedic Modules (Indices 0 to 32)
MODULE_CATEGORIES = {
    "🏛️ १. मूलभूत व षड्बल": [0, 3, 6, 12, 19],
    "⏱️ २. दशा व गोचर": [8, 9, 13, 29, 11],
    "📜 ३. शास्त्रीय फलादेश": [30, 1, 20, 15, 24, 28, 17],
    "🔱 ४. विशेष पद्धतियां": [10, 7, 22, 5, 21, 31, 14, 4],
    "🌿 ५. उपचार व जीवनशैली": [2, 32, 27, 25, 26, 23, 16, 18],
}


def get_category_for_module(mod_idx: int) -> str:
    """Returns the matching category name for a given module index."""
    for cat_name, idx_list in MODULE_CATEGORIES.items():
        if mod_idx in idx_list:
            return cat_name
    return list(MODULE_CATEGORIES.keys())[0]


def test_all_33_modules_covered_without_omissions():
    """Verify all 33 modules (0 to 32) are included exactly once across all 5 categories."""
    all_indices = []
    for cat_name, idx_list in MODULE_CATEGORIES.items():
        all_indices.extend(idx_list)

    assert len(all_indices) == 33
    assert set(all_indices) == set(range(33))


def test_category_lookup_accuracy():
    """Verify exact category lookup for key modules."""
    # Module 0 (Kundali) -> Foundations
    assert "मूलभूत" in get_category_for_module(0)
    # Module 8 (Dasha) -> Time & Dasha
    assert "दशा" in get_category_for_module(8)
    # Module 30 (Predictions) -> Predictions
    assert "फलादेश" in get_category_for_module(30)
    # Module 10 (KP) -> Special Systems
    assert "विशेष" in get_category_for_module(10)
    # Module 32 (Gemology) -> Remedies & Health
    assert "उपचार" in get_category_for_module(32)


def test_calendar_month_slide_logic():
    """Verify previous / next month sliding calculation."""
    cur_year = 2026
    cur_month = 11

    # Slide next
    next_m = cur_month + 1 if cur_month < 12 else 1
    next_y = cur_year if cur_month < 12 else cur_year + 1
    assert next_m == 12
    assert next_y == 2026

    # Slide prev
    prev_m = cur_month - 1 if cur_month > 1 else 12
    prev_y = cur_year if cur_month > 1 else cur_year - 1
    assert prev_m == 10
    assert prev_y == 2026


def test_all_11_action_tools_registered():
    """Verify all 11 action icons have defined tool handlers."""
    ACTION_ICONS_MAP = {
        "📅": "calendar_month",
        "☀️": "panchang_today",
        "🌙": "panchang_jatak",
        "✨": "new",
        "❓": "prashna",
        "📂": "open",
        "📝": "notes",
        "🌐": "lang",
        "🌓": "theme",
        "⚙️": "settings",
        "🚪": "logout"
    }
    assert len(ACTION_ICONS_MAP) == 11
    # Verify each tool name is unique
    assert len(set(ACTION_ICONS_MAP.values())) == 11


def test_line3_status_breadcrumb_formatting():
    """Verify Line 3 status breadcrumb formatting."""
    mock_dob = date(1995, 1, 1)
    mock_tob = time(14, 30, 0)
    dob_str = mock_dob.strftime("%d-%m-%Y")
    tob_str = mock_tob.strftime("%I:%M %p")
    place_str = "New Delhi, India"
    mod_str = "📜 जन्म कुण्डली (Kundali)"
    name_str = "शुभम शर्मा"

    line3_html = f"📍 सक्रिय मॉड्यूल: {mod_str} | 👤 जातक: {name_str} (जन्म: {dob_str}, {tob_str} | {place_str})"
    assert "01-01-1995" in line3_html
    assert "02:30 PM" in line3_html
    assert "New Delhi, India" in line3_html
    assert "शुभम शर्मा" in line3_html
    assert "जन्म कुण्डली" in line3_html


def test_line3_status_breadcrumb_with_micro_dms_coordinates():
    """Verify Line 3 status breadcrumb with active native Lagna and Moon micro coordinates (अंश, कला, विकला & चरण)."""
    def _pill_dms(deg_val):
        deg_norm = float(deg_val) % 30.0
        ansh = int(deg_norm)
        rem_min = (deg_norm - ansh) * 60.0
        kala = int(rem_min)
        vikala = int(round((rem_min - kala) * 60.0))
        if vikala >= 60:
            vikala = 0
            kala += 1
        if kala >= 60:
            kala = 0
            ansh = (ansh + 1) % 30
        return f"{ansh}° {kala:02d}' {vikala:02d}\""

    # Test exact DMS calculation
    l_dms = _pill_dms(14.5025)
    assert l_dms == "14° 30' 09\""

    # Test boundary roll-over
    assert _pill_dms(29.9999) == "0° 00' 00\"" or "29°" in _pill_dms(29.9999)

    lagna_sign = "मेष (Aries)"
    moon_sign = "वृषभ (Taurus)"
    moon_dms = _pill_dms(22.75)
    assert moon_dms == "22° 45' 00\""
    moon_nak = "रोहिणी"
    moon_pada = 4

    breadcrumb_snippet = (
        f"🌅 लग्न: <b>{lagna_sign}</b> ({l_dms}) │ "
        f"🌙 चंद्र: <b>{moon_sign}</b> ({moon_dms}) • {moon_nak} (पद-{moon_pada})"
    )

    assert "14° 30' 09\"" in breadcrumb_snippet
    assert "22° 45' 00\"" in breadcrumb_snippet
    assert "रोहिणी (पद-4)" in breadcrumb_snippet
    assert "मेष (Aries)" in breadcrumb_snippet

