import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.shastriya_pramana import (
    default_shastriya_pramana_engine,
    SHASTRIYA_SHLOKAS,
    PUSHKARA_NAVAMSHA_MATRIX,
    PUSHKARA_BHAGA_MAP,
)

@pytest.fixture
def sample_chart():
    b = BirthData(
        name="परीक्षार्थी जातक",
        birth_date=date(1995, 5, 15),
        birth_time=time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b)

def test_pushkara_status_evaluation():
    # Aries (Agnitattva rashi = 1)
    # Pushkara navamsha in fire signs: 7th (20° to 23°20' = Libra navamsha) & 9th (26°40' to 30° = Sag navamsha)
    res_non = default_shastriya_pramana_engine.evaluate_pushkara_status(1, 10.0)
    assert res_non["is_pushkara_navamsha"] is False
    assert res_non["is_pushkara_bhaga"] is False

    # Degree 21.0 in Aries is in 7th navamsha (Libra) -> Pushkara Navamsha!
    res_push = default_shastriya_pramana_engine.evaluate_pushkara_status(1, 21.0)
    assert res_push["is_pushkara_navamsha"] is True
    assert res_push["navamsha_lord"] == "Venus"

    # Degree 21.0 in Aries is also Pushkara Bhaga (exact 21°)
    assert res_push["is_pushkara_bhaga"] is True

def test_daily_muhurta_windows():
    test_d = date(2026, 10, 15)  # Thursday
    muh = default_shastriya_pramana_engine.calculate_daily_muhurta_windows(
        test_d, sunrise_time=time(6, 0), sunset_time=time(18, 0)
    )
    assert "rahu_kaal" in muh
    assert "abhijit" in muh
    assert "brahma_muhurta" in muh
    assert "shastriya_shloka" in muh["rahu_kaal"]
    assert "shastriya_shloka" in muh["abhijit"]

def test_kakshya_calculation():
    # 0° to 3°45' is Saturn kakshya
    k1 = default_shastriya_pramana_engine.evaluate_kakshya_position(2.5)
    assert k1["kakshya_number"] == 1
    assert k1["kakshya_lord_en"] == "Saturn"

    # 4.0° is Jupiter kakshya (3°45' to 7°30')
    k2 = default_shastriya_pramana_engine.evaluate_kakshya_position(4.0)
    assert k2["kakshya_number"] == 2
    assert k2["kakshya_lord_en"] == "Jupiter"

def test_conditional_dasha_audit(sample_chart):
    cond = default_shastriya_pramana_engine.evaluate_conditional_dasha_eligibility(sample_chart)
    assert "ashtottari" in cond
    assert "shodashottari" in cond
    assert "dwisaptati" in cond
    assert "shashtihayani" in cond
    assert "shastriya_shloka" in cond

def test_chart_pushkara_and_vargottama_audit(sample_chart):
    p_audit = default_shastriya_pramana_engine.audit_chart_pushkara(sample_chart)
    assert "planets" in p_audit
    assert "total_pushkara_count" in p_audit

    v_audit = default_shastriya_pramana_engine.audit_vargottama(sample_chart)
    assert "vargottama_planets" in v_audit
    assert "count" in v_audit

def test_badhaka_maraka_audit(sample_chart):
    bm = default_shastriya_pramana_engine.audit_badhaka_maraka(sample_chart)
    assert "lagna_type" in bm
    assert "badhaka_house" in bm
    assert "badhakesh" in bm
    assert "maraka_primary" in bm
    assert "maraka_secondary" in bm
    assert "shastriya_shloka" in bm
    assert bm["maraka_primary"]["house"] == 2
    assert bm["maraka_secondary"]["house"] == 7

def test_shastriya_shlokas_structure():
    required_keys = [
        "pushkara_navamsha",
        "pushkara_bhaga",
        "vargottama",
        "abhijit_muhurta",
        "rahu_kaal",
        "kakshya_system",
        "conditional_dashas",
        "badhaka_maraka",
        "shadbala_pramana",
        "ishta_kashta_pramana",
        "bhavabala_pramana",
        "jaimini_sutras",
        "double_transit",
        "shodashvarga_vaisheshikamsa"
    ]
    for k in required_keys:

        assert k in SHASTRIYA_SHLOKAS
        item = SHASTRIYA_SHLOKAS[k]
        assert "grantha" in item
        assert "shloka" in item
        assert "anuvad_hi" in item
        assert "rule" in item

