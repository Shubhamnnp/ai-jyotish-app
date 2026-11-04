"""
Unit Tests for Shadbala and Bhava Bala Hardening (Phase 3 Task P3-T3).
Verifies:
1. Six-fold Shadbala calculation (Sthana, Dik, Kaala, Cheshta, Naisargika, Drik Bala) for 7 classical planets.
2. Minimum required Virupas hard gates per BPHS.
3. Rupa conversion: total_rupas = total_virupas / 60.
4. Cheshta Bala dynamic speed derivation (Retrograde == 60.0 Virupas).
5. Detailed Bhava Bala (Adhipati, Dig, Drishti) for all 12 houses.
6. Ishta Phala and Kashta Phala bounds (0 to 60).
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator
from src.jyotish.core.shadbala import ShadbalaCalculator, REQUIRED_VIRUPAS, NAISARGIKA_BALA


def test_shadbala_sixfold_and_minimum_virupas():
    """Verify BPHS minimum virupas and sixfold components for all 7 grahas."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Shadbala Native",
        birth_date=date(1980, 5, 10),
        birth_time=time(12, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    shad = ShadbalaCalculator.calculate(chart)

    expected_min = {
        "Sun": 390.0,
        "Moon": 360.0,
        "Mars": 300.0,
        "Mercury": 420.0,
        "Jupiter": 390.0,
        "Venus": 330.0,
        "Saturn": 300.0,
    }

    assert REQUIRED_VIRUPAS == expected_min

    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        res = shad.planets[p_name]

        # Component existence & positivity
        assert res.sthana_bala >= 0.0
        assert res.dik_bala >= 0.0
        assert res.kaala_bala >= 0.0
        assert res.cheshta_bala >= 0.0
        assert res.naisargika_bala == NAISARGIKA_BALA[p_name]
        assert res.drik_bala >= 0.0

        # Invariant: Total Virupas sum of 6 components
        comp_sum = round(res.sthana_bala + res.dik_bala + res.kaala_bala + res.cheshta_bala + res.naisargika_bala + res.drik_bala, 2)
        assert abs(res.total_virupas - comp_sum) <= 0.05

        # Rupa conversion: Virupas / 60
        assert abs(res.total_rupas - (res.total_virupas / 60.0)) < 0.05

        # Required virupas match BPHS
        assert res.required_virupas == expected_min[p_name]

        # Ishta / Kashta bounds
        assert 0.0 <= res.ishta_phala <= 60.0
        assert 0.0 <= res.kashta_phala <= 60.0

        # Avasthas
        assert any(k in res.baladi_avastha for k in ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"])
        assert any(k in res.jagratadi_avastha for k in ["Jagrat", "Swapna", "Sushupti"])
        assert any(k in res.deeptadi_avastha for k in ["Deepta", "Deena", "Kopa", "Swastha", "Mudita", "Khala", "Shanta", "Shakta", "Peedita"])


def test_cheshta_bala_retrograde_and_speed():
    """Verify Retrograde planets receive 60.0 Virupas for Cheshta Bala."""
    calc = ChartCalculator()
    # Date where Saturn is retrograde
    b_data = BirthData(
        name="Retrograde Native",
        birth_date=date(2023, 8, 15),
        birth_time=time(10, 0),
        latitude=19.0760,
        longitude=72.8777,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    shad = ShadbalaCalculator.calculate(chart)

    for p_name, p_pos in chart.planets.items():
        if p_name in shad.planets and p_pos.is_retrograde:
            assert shad.planets[p_name].cheshta_bala == 60.0


def test_detailed_bhava_bala():
    """Verify detailed Bhava Bala calculation for all 12 houses."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Bhava Bala Native",
        birth_date=date(1992, 3, 25),
        birth_time=time(7, 45),
        latitude=22.5726,
        longitude=88.3639,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    shad = ShadbalaCalculator.calculate(chart)

    assert len(shad.bhava_bala) == 12
    assert shad.bhava_bala_components is not None
    assert len(shad.bhava_bala_components) == 12

    for h in range(1, 13):
        comp = shad.bhava_bala_components[h]
        assert "adhipati_bala" in comp
        assert "dig_bala" in comp
        assert "drishti_bala" in comp
        assert "total_virupas" in comp
        assert comp["total_virupas"] == shad.bhava_bala[h]
