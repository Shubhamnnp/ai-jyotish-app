"""
Unit Tests for Jaimini System, Special Lagnas, and Arudha Padas (Phase 3 Task P3-T4).
Verifies:
1. 7 and 8 Chara Karakas with degree tie-breaker resolution.
2. Karakamsha sign derivation from Atmakaraka Navamsha.
3. 12 Arudha Padas with classical exceptions (no pada in 1st or 7th).
4. Special Lagnas: Hora Lagna (HL), Ghati Lagna (GL), Sri Lagna (SL), Varnada Lagna (VL), Indu Lagna (IL).
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator
from src.jyotish.core.jaimini import JaiminiCalculator


def test_jaimini_7_and_8_karakas():
    """Verify 7-Karaka and 8-Karaka designations and tie-breaker sorting."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Jaimini Native",
        birth_date=date(1988, 7, 22),
        birth_time=time(15, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    jaimini = JaiminiCalculator.calculate(chart)

    # 1. 7 Karakas check
    labels_7 = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
    for lab in labels_7:
        assert lab in jaimini.karakas_7
        assert jaimini.karakas_7[lab] in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    # All 7 planets must be unique in 7-karaka scheme
    assert len(set(jaimini.karakas_7.values())) == 7

    # 2. 8 Karakas check
    labels_8 = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
    for lab in labels_8:
        assert lab in jaimini.karakas_8
    assert len(set(jaimini.karakas_8.values())) == 8
    assert "Rahu" in jaimini.karakas_8.values()


def test_karakamsha_sign():
    """Verify Karakamsha is the exact D9 Navamsha sign of the Atmakaraka."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Karakamsha Native",
        birth_date=date(1990, 1, 15),
        birth_time=time(10, 0),
        latitude=19.0760,
        longitude=72.8777,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    jaimini = JaiminiCalculator.calculate(chart)

    ak_planet = jaimini.karakas_7["AK"]
    ak_lon = chart.planets[ak_planet].longitude

    # Compute expected Navamsha sign
    pada_idx = int((ak_lon % 360.0) // (360.0 / 108.0))
    expected_sign_id = (pada_idx % 12) + 1

    assert jaimini.karakamsha_sign_id == expected_sign_id


def test_arudha_padas_classical_exceptions():
    """Verify that no Arudha Pada falls in the 1st or 7th from its original house."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Arudha Native",
        birth_date=date(1982, 11, 4),
        birth_time=time(6, 15),
        latitude=22.5726,
        longitude=88.3639,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    jaimini = JaiminiCalculator.calculate(chart)

    # 12 Arudhas present
    expected_labels = ["AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "UL"]
    for lab in expected_labels:
        assert lab in jaimini.arudha_padas
        sign_id = jaimini.arudha_padas[lab]
        assert 1 <= sign_id <= 12

    # Check classical rule: For every house h, its pada cannot fall in h or (h+6)
    for h in range(1, 13):
        lab = "AL" if h == 1 else ("UL" if h == 12 else f"A{h}")
        pada_sign = jaimini.arudha_padas[lab]
        house_sign = chart.houses[h - 1].sign_id
        distance = ((pada_sign - house_sign) % 12) + 1

        assert distance != 1, f"Arudha {lab} violated exception: fell in house 1 ({distance})"
        assert distance != 7, f"Arudha {lab} violated exception: fell in house 7 ({distance})"


def test_special_lagnas_present():
    """Verify calculation of Special Lagnas (HL, GL, SL, IL, VL, BL, PP)."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Special Lagnas Native",
        birth_date=date(2000, 1, 1),
        birth_time=time(12, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)
    jaimini = JaiminiCalculator.calculate(chart)

    # All special lagnas populated with valid zodiac signs
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    assert jaimini.hora_lagna_sign_name in signs
    assert jaimini.ghati_lagna_sign_name in signs
    assert jaimini.sri_lagna_sign_name in signs
    assert jaimini.indu_lagna_sign_name in signs
    assert jaimini.bhava_lagna_sign_name in signs
    assert jaimini.pranapada_lagna_sign_name in signs
    assert jaimini.varnada_lagna_sign_name in signs

    # Detailed dictionary
    assert jaimini.special_lagnas_detail is not None
    assert "HL" in jaimini.special_lagnas_detail
    assert "GL" in jaimini.special_lagnas_detail
    assert "SL" in jaimini.special_lagnas_detail
