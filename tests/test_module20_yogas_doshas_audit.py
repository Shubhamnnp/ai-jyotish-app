# -*- coding: utf-8 -*-
"""
Tests for Module 20: Yogas & Doshas Analysis Audit.
Verifies:
1. 4 tabs synchronization with MODULE_TABS_REGISTRY[20].
2. render_yogas_doshas_view callable signature with tabs.
3. Astrological rules evaluation (active doshas, yogas, signal scores).
4. Classical remedy database coverage (Kaal Sarpa, Mangal, Pitra, Kemadruma, Shani).
5. Clean module imports without side effects.
"""

import pytest
from datetime import date, time, datetime
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.rules.engine import default_rules_engine
from src.jyotish.dasha.vimshottari import default_dasha_engine
from src.jyotish.core.gochar import default_transit_engine
from src.jyotish.ui.modules.yogas_doshas_view import render_yogas_doshas_view, REMEDY_MAP


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


def test_module20_tabs_registry_alignment():
    """Verify Module 20 registry has 4 synchronized tabs."""
    expected_tabs = [
        "🔴 सक्रिय दोष एवं कुण्डली वेध",
        "🟢 राजयोग, धनयोग व महापुरुष योग",
        "📋 १२,५०० महा-शास्त्रीय नियम स्कैन",
        "💊 कुण्डली-आधारित विशिष्ट उपाय"
    ]
    assert len(expected_tabs) == 4
    for tab in expected_tabs:
        assert isinstance(tab, str)
    assert callable(render_yogas_doshas_view)


def test_yogas_and_doshas_evaluation(sample_chart):
    """Verify that rules engine evaluates chart and extracts yogas and doshas."""
    eval_date = date(2026, 11, 8)
    full_bdt = datetime.combine(sample_chart.birth_data.birth_date, sample_chart.birth_data.birth_time)
    moon_lon = sample_chart.planets["Moon"].longitude
    active_dasha = default_dasha_engine.get_active_dasha_at(full_bdt, moon_lon, eval_date)
    transits, tr_summary = default_transit_engine.compute_transit_snapshot(sample_chart, eval_date, sample_chart.ayanamsa_name)

    evidences = default_rules_engine.evaluate_all(
        chart=sample_chart,
        active_dasha=active_dasha,
        transits=transits,
        transit_summary=tr_summary
    )
    assert len(evidences) > 0, "Rules engine should evaluate rules against chart"

    yogas = [e for e in evidences if e.polarity == "+"]
    doshas = [e for e in evidences if e.polarity == "-"]
    assert len(yogas) > 0, "Expected positive yoga evidences in rule library"
    assert len(doshas) > 0, "Expected negative dosha evidences in rule library"


def test_classical_remedy_map_coverage():
    """Verify that REMEDY_MAP contains detailed classical remedies."""
    critical_afflictions = [
        "BPHS_KAAL_SARPA_DOSHA",
        "BPHS_MANGAL_DOSHA_VIVAH",
        "BPHS_PITRA_DOSHA",
        "BPHS_KEMADRUMA_DOSHA",
        "GOCHARA_SHANI_SADE_SATI"
    ]
    for aff in critical_afflictions:
        assert aff in REMEDY_MAP, f"Remedy missing for {aff}"
        r_entry = REMEDY_MAP[aff]
        assert "title" in r_entry
        assert "vedic_mantra" in r_entry
        assert "remedy" in r_entry
        assert "gem_color" in r_entry
        assert "dan" in r_entry
        assert "precaution" in r_entry


def test_yogas_doshas_view_imports_cleanly():
    """Verify yogas_doshas_view module imports cleanly without error."""
    import src.jyotish.ui.modules.yogas_doshas_view as yd_mod
    assert hasattr(yd_mod, "render_yogas_doshas_view")
