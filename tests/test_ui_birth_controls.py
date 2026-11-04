"""
Unit tests for Modernized Birth Input Controls & Astrological Selectors (Phase 6, Task P6-T1).
Reference: docs/IMPLEMENTATION_PRD.md (Section 3.6 & 5.5, P6-T1).

Verifies:
1. Birth confidence options metadata (exact, approx_15m, approx_1h, unknown).
2. Calculation metadata catalogues (Ayanamsa, House System, Nodes, Schools) with sane defaults and tooltips.
3. Historical timezone anomaly detection:
   - British India War Time (1942-1945) flagged with UTC+6.5 recommendation.
   - Pre-1906 Local Mean Time (LMT) flagged.
   - Modern standard dates (e.g. 1995) return normal without anomaly.
4. Geocoding search ambiguity evaluation generates resolution prompts when multiple homonyms exist.
"""

import sys
import os
import pytest
from datetime import date
from types import SimpleNamespace

from jyotish.ui.components.birth_form import (
    BIRTH_CONFIDENCE_LEVELS,
    AYANAMSA_CATALOGUE,
    HOUSE_SYSTEM_CATALOGUE,
    NODE_TYPE_CATALOGUE,
    ASTRO_SCHOOLS_CATALOGUE,
    get_historical_tz_note,
    evaluate_geo_ambiguity
)


def test_birth_confidence_levels():
    """Verify birth confidence catalogue structure and options."""
    assert len(BIRTH_CONFIDENCE_LEVELS) == 4
    ids = [c["id"] for c in BIRTH_CONFIDENCE_LEVELS]
    assert "exact" in ids
    assert "approx_15m" in ids
    assert "approx_1h" in ids
    assert "unknown" in ids
    for c in BIRTH_CONFIDENCE_LEVELS:
        assert len(c["label"]) > 0
        assert len(c["description"]) > 0
        assert len(c["short_name"]) > 0


def test_calculation_catalogues_sane_defaults_and_tooltips():
    """Verify catalogues have defaults and descriptive tooltips."""
    # Ayanamsa
    assert "Lahiri" in AYANAMSA_CATALOGUE
    assert AYANAMSA_CATALOGUE["Lahiri"]["is_default"] is True
    assert len(AYANAMSA_CATALOGUE["Lahiri"]["tooltip"]) > 10

    # House Systems
    assert "Whole Sign" in HOUSE_SYSTEM_CATALOGUE
    assert HOUSE_SYSTEM_CATALOGUE["Whole Sign"]["is_default"] is True
    assert len(HOUSE_SYSTEM_CATALOGUE["Whole Sign"]["tooltip"]) > 10

    # Node Types
    assert "mean" in NODE_TYPE_CATALOGUE
    assert NODE_TYPE_CATALOGUE["mean"]["is_default"] is True
    assert "true" in NODE_TYPE_CATALOGUE

    # Astrological Schools
    assert "parashari" in ASTRO_SCHOOLS_CATALOGUE
    assert ASTRO_SCHOOLS_CATALOGUE["parashari"]["is_default"] is True
    assert "jaimini" in ASTRO_SCHOOLS_CATALOGUE
    assert "kp" in ASTRO_SCHOOLS_CATALOGUE
    assert "tajika" in ASTRO_SCHOOLS_CATALOGUE
    assert "lalkitab" in ASTRO_SCHOOLS_CATALOGUE


def test_historical_timezone_india_war_time():
    """Verify India War Time (1942-1945) anomaly detection."""
    # During India War Time (e.g. 1943)
    res_war = get_historical_tz_note(date(1943, 6, 15), timezone_offset=5.5, country_hint="IN")
    assert res_war["has_anomaly"] is True
    assert res_war["suggested_offset"] == 6.5
    assert any("India War Time" in n or "युद्ध-समय" in n for n in res_war["notes"])

    # Normal modern date (e.g. 1995)
    res_modern = get_historical_tz_note(date(1995, 5, 15), timezone_offset=5.5, country_hint="IN")
    assert res_modern["has_anomaly"] is False
    assert res_modern["suggested_offset"] == 5.5
    assert len(res_modern["notes"]) == 0


def test_historical_timezone_pre_1906_lmt():
    """Verify Pre-1906 Local Mean Time anomaly detection."""
    res_pre = get_historical_tz_note(date(1893, 9, 11), timezone_offset=5.89, country_hint="IN")
    assert res_pre["has_anomaly"] is True
    assert any("LMT" in n or "स्थानीय मध्यम समय" in n for n in res_pre["notes"])


def test_foreign_dst_notice():
    """Verify that non-IST offsets include foreign timezone/DST notice."""
    res_ny = get_historical_tz_note(date(2000, 7, 4), timezone_offset=-4.0, country_hint="US")
    assert len(res_ny["notes"]) > 0
    assert any("DST" in n for n in res_ny["notes"])


def test_geocoding_ambiguity_evaluator():
    """Verify detection of ambiguous homonyms in search results."""
    # Empty results
    res_empty = evaluate_geo_ambiguity([], "Nowhere")
    assert res_empty["is_ambiguous"] is False

    # Single distinct result
    loc1 = SimpleNamespace(city="Nanpara", formatted_name="Nanpara, UP, India")
    res_single = evaluate_geo_ambiguity([loc1], "Nanpara")
    assert res_single["is_ambiguous"] is False
    assert res_single["prompt"] is None

    # Multiple homonym results (e.g. Hyderabad, India vs Hyderabad, Pakistan)
    loc2a = SimpleNamespace(city="Hyderabad", formatted_name="Hyderabad, Telangana, India")
    loc2b = SimpleNamespace(city="Hyderabad", formatted_name="Hyderabad, Sindh, Pakistan")
    res_amb = evaluate_geo_ambiguity([loc2a, loc2b], "Hyderabad")
    assert res_amb["is_ambiguous"] is True
    assert res_amb["prompt"] is not None
    assert "एक से अधिक नगर" in res_amb["prompt"]
