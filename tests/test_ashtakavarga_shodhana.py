"""
Unit Tests for Ashtakavarga and Shodhana Reductions (Phase 3 Task P3-T2).
Verifies:
1. Strict SAV invariant: total bindus == 337 across all 12 rashis.
2. Trikona Shodhana reduction rules per BPHS Chapters 66–72.
3. Ekadhipatya Shodhana reduction rules for dual-owned rashis.
4. Pinda Sadhana: Rashi Pinda, Graha Pinda, and Yoga Pinda (Rashi + Graha).
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator


def test_ashtakavarga_337_invariant():
    """Verify that unreduced SAV sum is strictly 337 across diverse birth charts."""
    calc = ChartCalculator()
    dates = [
        (date(1950, 1, 15), time(12, 0), 28.6139, 77.2090),
        (date(1980, 8, 20), time(8, 30), 19.0760, 72.8777),
        (date(2000, 1, 1), time(0, 0), 51.5074, -0.1278),
        (date(2024, 6, 21), time(18, 45), -33.8688, 151.2093),
    ]

    for b_d, b_t, lat, lon in dates:
        b_data = BirthData(name="SAV Native", birth_date=b_d, birth_time=b_t, latitude=lat, longitude=lon)
        chart = calc.calculate_full_chart(b_data)
        av = AshtakavargaCalculator.calculate(chart)

        assert av.total_bindus == 337, f"Failed for {b_d}: SAV total was {av.total_bindus}"
        assert sum(av.sav) == 337
        assert len(av.sav) == 12


def test_trikona_and_ekadhipatya_shodhana():
    """Verify Trikona Shodhana and Ekadhipatya Shodhana reductions."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Shodhana Native",
        birth_date=date(1985, 11, 10),
        birth_time=time(14, 25),
        latitude=26.8467,
        longitude=80.9462,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    av = AshtakavargaCalculator.calculate(chart)

    shodhana = av.shodhana
    assert shodhana is not None

    trikona_groups = [
        [0, 4, 8],    # Aries, Leo, Sagittarius
        [1, 5, 9],    # Taurus, Virgo, Capricorn
        [2, 6, 10],   # Gemini, Libra, Aquarius
        [3, 7, 11],   # Cancer, Scorpio, Pisces
    ]

    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        raw_bav = av.bav[p_name]
        t_bav = shodhana.trikona_reduced_bav[p_name]
        e_bav = shodhana.ekadhipatya_reduced_bav[p_name]

        # 1. Trikona check: for each trikona group, at least one sign must be reduced to 0
        for group in trikona_groups:
            min_raw = min(raw_bav[idx] for idx in group)
            for idx in group:
                assert t_bav[idx] == raw_bav[idx] - min_raw
            assert min(t_bav[idx] for idx in group) == 0

        # 2. Ekadhipatya check: Ekadhipatya values can never exceed Trikona values
        for i in range(12):
            assert e_bav[i] <= t_bav[i]

        # 3. Pinda Sadhana check: Yoga Pinda = Rashi Pinda + Graha Pinda
        r_pinda = shodhana.rashi_pinda[p_name]
        g_pinda = shodhana.graha_pinda[p_name]
        y_pinda = shodhana.yoga_pinda[p_name]

        assert r_pinda >= 0
        assert g_pinda >= 0
        assert y_pinda == r_pinda + g_pinda, f"{p_name}: Yoga Pinda {y_pinda} != {r_pinda} + {g_pinda}"
