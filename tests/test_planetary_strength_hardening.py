"""
Unit test suite for Phase 5: Planetary Strength & Supporting Calculations Hardening.
Tests:
1. 6-fold Shadbala breakdown & virupa thresholds for 7 classical planets.
2. Sthana Bala & Kaala Bala granular components.
3. Detailed BPHS Bhava Bala (Adhipati, Dig, Drishti) for all 12 houses.
4. Classical Planetary Avasthas: Baladi, Jagratadi, and 9 Deeptadi states.
5. Ashtakavarga exact 337 total bindu conservation invariant & planetary totals.
6. Shodhana reductions (Trikona, Ekadhipatya) and Pindas (Rashi, Graha, Yoga).
7. Upagrahas mathematical invariants (Aprakasha Grahas).
"""

import pytest
import math
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.shadbala import default_shadbala_calculator, REQUIRED_VIRUPAS
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.upagraha import default_upagraha_calculator


@pytest.fixture
def native_chart():
    bdata = BirthData(
        name="Shadbala Benchmark Native",
        birth_date=date(1992, 5, 10),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_full_chart(bdata)


def test_shadbala_six_fold_breakdown_and_thresholds(native_chart):
    """Verify all 6 components of Shadbala exist, are positive, and meet BPHS requirements."""
    sb = default_shadbala_calculator.calculate(native_chart)
    seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    assert len(sb.planets) == 7
    for p_name in seven_planets:
        res = sb.planets[p_name]
        # 6 core balas
        assert res.sthana_bala >= 0.0
        assert 0.0 <= res.dik_bala <= 60.0
        assert res.kaala_bala >= 0.0
        assert 30.0 <= res.cheshta_bala <= 60.0
        assert res.naisargika_bala > 0.0
        assert 0.0 <= res.drik_bala <= 60.0
        
        # Totals and ratios
        assert res.total_virupas > 0.0
        assert math.isclose(res.total_rupas, round(res.total_virupas / 60.0, 2), abs_tol=0.02)
        assert res.required_virupas == REQUIRED_VIRUPAS[p_name]
        assert math.isclose(res.strength_ratio, round(res.total_virupas / res.required_virupas, 2), abs_tol=0.02)
        assert res.is_strong == (res.strength_ratio >= 1.0)
        
        # Ishta / Kashta phala
        assert 0.0 <= res.ishta_phala <= 60.0
        assert 0.0 <= res.kashta_phala <= 60.0


def test_shadbala_granular_subcomponents(native_chart):
    """Verify detailed subcomponents for Sthana and Kaala Bala."""
    sb = default_shadbala_calculator.calculate(native_chart)
    for p_name, res in sb.planets.items():
        assert 0.0 <= res.uchha_bala <= 60.0
        assert res.kendradi_bala in (15.0, 30.0, 60.0)
        assert res.ojayugma_bala in (0.0, 15.0)
        assert 10.0 <= res.nathonnatha_bala <= 60.0
        assert res.paksha_bala in (20.0, 45.0)


def test_bhava_bala_three_fold_breakdown(native_chart):
    """Verify authentic BPHS Bhava Bala and its 3 components for all 12 houses."""
    sb = default_shadbala_calculator.calculate(native_chart)
    assert len(sb.bhava_bala) == 12
    assert sb.bhava_bala_components is not None
    assert len(sb.bhava_bala_components) == 12
    
    for h in range(1, 13):
        comp = sb.bhava_bala_components[h]
        assert "adhipati_bala" in comp
        assert "dig_bala" in comp
        assert "drishti_bala" in comp
        assert "total_virupas" in comp
        assert comp["adhipati_bala"] > 0.0
        assert 20.0 <= comp["dig_bala"] <= 60.0
        assert 0.0 <= comp["drishti_bala"] <= 60.0
        expected_total = round(comp["adhipati_bala"] + comp["dig_bala"] + comp["drishti_bala"], 2)
        assert math.isclose(comp["total_virupas"], expected_total, abs_tol=0.01)
        assert sb.bhava_bala[h] == comp["total_virupas"]


def test_classical_planetary_avasthas(native_chart):
    """Verify Baladi, Jagratadi, and Deeptadi states."""
    sb = default_shadbala_calculator.calculate(native_chart)
    valid_baladi = ["Bala (Infant)", "Kumara (Youth)", "Yuva (Adult/Full)", "Vriddha (Aged)", "Mrita (Dead)"]
    valid_jagratadi = ["Jagrat (Awake - 100% Phala)", "Swapna (Dreaming - 50% Phala)", "Sushupti (Sleeping - Minimal Phala)"]
    
    for p_name, res in sb.planets.items():
        assert res.baladi_avastha in valid_baladi
        assert res.jagratadi_avastha in valid_jagratadi
        assert len(res.deeptadi_avastha) > 0


def test_ashtakavarga_conservation_337_and_bav_totals(native_chart):
    """Verify exact 337 total SAV bindus and individual planetary BAV invariant totals."""
    av = AshtakavargaCalculator.calculate(native_chart)
    
    # Invariant BAV totals according to classical Parashari shlokas:
    expected_bav_totals = {
        "Sun": 48,
        "Moon": 49,
        "Mars": 39,
        "Mercury": 54,
        "Jupiter": 56,
        "Venus": 52,
        "Saturn": 39
    }
    
    for p_name, exp_total in expected_bav_totals.items():
        p_bindus = av.bav[p_name]
        assert len(p_bindus) == 12
        assert sum(p_bindus) == exp_total, f"{p_name} BAV total {sum(p_bindus)} != {exp_total}"
        
    # SAV total must equal 337 exactly
    assert len(av.sav) == 12
    assert sum(av.sav) == 337
    assert av.total_bindus == 337


def test_ashtakavarga_shodhana_and_pindas(native_chart):
    """Verify Trikona & Ekadhipatya Shodhana and Yoga Pinda conservation."""
    av = AshtakavargaCalculator.calculate(native_chart)
    shodhana = av.shodhana
    assert shodhana is not None
    
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        # Trikona reduced bindus must be <= raw BAV bindus
        raw = av.bav[p_name]
        tri = shodhana.trikona_reduced_bav[p_name]
        eka = shodhana.ekadhipatya_reduced_bav[p_name]
        for i in range(12):
            assert tri[i] <= raw[i]
            assert eka[i] <= tri[i]
            
        # Pindas
        r_pinda = shodhana.rashi_pinda[p_name]
        g_pinda = shodhana.graha_pinda[p_name]
        y_pinda = shodhana.yoga_pinda[p_name]
        assert r_pinda >= 0
        assert g_pinda >= 0
        assert y_pinda == (r_pinda + g_pinda)


def test_upagrahas_aprakasha_mathematical_invariants(native_chart):
    """Verify the classical Upaketu + 30° == Sun invariant for Aprakasha Grahas."""
    up = default_upagraha_calculator.calculate(native_chart)
    sun_lon = native_chart.planets["Sun"].longitude
    
    # Invariant: Upaketu + 30° == Sun (modulo 360°)
    derived_sun = (up.upaketu_longitude + 30.0) % 360.0
    diff = abs(derived_sun - sun_lon)
    if diff > 180.0:
        diff = abs(diff - 360.0)
    assert diff < 0.05, f"Aprakasha invariant violated: diff={diff}°"

