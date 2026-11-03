"""
Unit test suite for Phase 8: Multi-System Astrology Integration Hardening.
Tests:
1. Jaimini Astrology Engine (7 & 8 Chara Karakas, Karakamsha Lagna, Arudha Padas A1-A12, Special Lagnas).
2. Krishnamurti Paddhati (KP) Engine (249 Sub-Lord table, 4-fold significators, Ruling Planets).
3. Tajika & Varshaphala Engine (Muntha, Varsheshwara, Ithasala/Ishrafa, Classical Sahams).
4. Lal Kitab Engine (Pakka Ghar, 9 Karmic Debts, Dharmi/Andha Teva classification).
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.jaimini import default_jaimini_calculator
from src.jyotish.core.kp import default_kp_engine
from src.jyotish.core.tajika import default_tajika_engine
from src.jyotish.core.lalkitab import default_lalkitab_engine, LAL_KITAB_KHANA_DATA


@pytest.fixture
def multi_chart():
    bdata = BirthData(
        name="Multi-System Benchmark Native",
        birth_date=date(1988, 10, 20),
        birth_time=time(16, 20, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_full_chart(bdata)


def test_jaimini_chara_karakas_and_arudhas(multi_chart):
    """Verify 7/8 Chara Karakas, Karakamsha Lagna, and Arudha Padas."""
    j_res = default_jaimini_calculator.calculate(multi_chart)
    
    # 7-Karaka scheme
    assert len(j_res.karakas_7) == 7
    assert "AK" in j_res.karakas_7  # Atmakaraka
    assert "DK" in j_res.karakas_7  # Darakaraka
    assert j_res.karakas_7["AK"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    
    # 8-Karaka scheme (includes Pitrikaraka)
    assert len(j_res.karakas_8) == 8
    assert "PiK" in j_res.karakas_8
    
    # Karakamsha Lagna
    assert 1 <= j_res.karakamsha_sign_id <= 12
    assert len(j_res.karakamsha_sign_name) > 0
    
    # Arudha Padas AL and A2 to A11, UL
    assert len(j_res.arudha_padas) == 12
    assert "AL" in j_res.arudha_padas
    assert "UL" in j_res.arudha_padas
    for k, s_id in j_res.arudha_padas.items():
        assert 1 <= s_id <= 12


def test_kp_249_table_and_sub_lord_precision(multi_chart):
    """Verify complete 1-249 Sub-Lord table and 4-fold significators."""
    table_249 = default_kp_engine.get_all_249_table()
    assert 249 <= len(table_249) <= 250
    
    # Verify continuous degree coverage from 0° to 360°
    assert table_249[0]["start_lon"] == 0.0
    assert abs(table_249[-1]["end_lon"] - 360.0) < 0.01
    
    # Sub-lord resolution for arbitrary longitude
    coords = default_kp_engine.get_sign_star_sub_subsub(125.45)
    assert coords["sign_lord"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    assert coords["star_lord"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
    assert coords["sub_lord"] in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
    
    # 4-fold significators
    four_fold = default_kp_engine.calculate_4fold_significators(multi_chart)
    assert "house_significators" in four_fold
    assert "planet_significations" in four_fold
    
    # Ruling Planets
    rp = default_kp_engine.get_ruling_planets(multi_chart)
    assert "day_lord" in rp
    assert "moon_sign_lord" in rp
    assert "lagna_sign_lord" in rp


def test_tajika_varshaphala_and_sahams(multi_chart):
    """Verify Muntha, Varsheshwara, Ithasala Yogas, and Classical Sahams."""
    t_res = default_tajika_engine.calculate(multi_chart, target_year=2026)
    
    assert 1 <= t_res.muntha_sign_id <= 12
    assert 1 <= t_res.muntha_house_from_lagna <= 12
    assert len(t_res.varsheshwara) > 0
    assert len(t_res.varshesh_candidates) == 5
    
    # Classical Sahams
    assert len(t_res.sahams) == 5
    for saham_key in ["punya_saham", "vidya_saham", "yashas_saham", "vivaha_saham", "bhratri_saham"]:
        assert saham_key in t_res.sahams
        s_data = t_res.sahams[saham_key]
        assert 0.0 <= s_data["longitude"] < 360.0
        assert 1 <= s_data["sign_id"] <= 12
        assert 1 <= s_data["house_from_lagna"] <= 12


def test_lalkitab_pakka_ghar_and_rina_classification(multi_chart):
    """Verify Lal Kitab Kalapurusha houses, Rina evaluation, and Teva classification."""
    # 12 Classical Khanas Pakka Ghar mapping
    assert len(LAL_KITAB_KHANA_DATA) == 12
    assert LAL_KITAB_KHANA_DATA[1]["pakka_ruler"] == "Sun (सूर्य)"
    assert LAL_KITAB_KHANA_DATA[4]["pakka_ruler"] == "Moon (चन्द्र)"
    assert LAL_KITAB_KHANA_DATA[8]["pakka_ruler"] == "Mars (मंगल) & Saturn (शनि)"
    
    # Engine evaluation
    lk_res = default_lalkitab_engine.calculate(multi_chart)
    assert len(lk_res.khana_planets) == 12
    assert len(lk_res.planet_khanas) >= 7
    assert isinstance(lk_res.dharmi_teva, bool)
    assert isinstance(lk_res.andha_teva, bool)
    assert isinstance(lk_res.active_debts, list)
    assert len(lk_res.chart_108_totkas) >= 7
