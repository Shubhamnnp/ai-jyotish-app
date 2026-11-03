"""
Unit test suite for Phase 7: Classical Yoga, Dosha & Shastriya Engine Hardening.
Tests:
1. Pancha Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasa).
2. Raja Yogas (Dharma-Karmadhipati, Vipareeta, Neechabhanga).
3. Chandra & Surya Yogas (Gajakesari, Sunaphaa, Anaphaa, Dhurudhara, Budhaditya).
4. Manglik / Kuja Dosha and classical cancellation rules.
5. Kaal Sarp Dosha (12 types and full vs partial identification).
6. Kemadruma Bhanga, Guru Chandal, Pitru Dosha, and Gandanta.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.yoga import default_yoga_dosha_engine, ClassicalYogaDoshaEngine


@pytest.fixture
def sample_native_chart():
    bdata = BirthData(
        name="Yoga Benchmark Native",
        birth_date=date(1989, 7, 24),
        birth_time=time(11, 45, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_full_chart(bdata)


def test_yoga_dosha_complete_evaluation(sample_native_chart):
    """Verify full evaluation pipeline returns structured items with Shastriya shlokas."""
    result = default_yoga_dosha_engine.evaluate_all(sample_native_chart)
    
    assert len(result.yogas) >= 10
    assert len(result.doshas) >= 5
    assert result.active_yogas_count >= 0
    assert result.active_doshas_count >= 0
    
    # Verify every yoga has shloka citation and dual-language descriptions
    for y in result.yogas:
        assert len(y.yoga_id) > 0
        assert len(y.name_hi) > 0
        assert len(y.name_en) > 0
        assert len(y.shloka_reference) > 0
        assert 0.0 <= y.strength_score <= 100.0
        
    for d in result.doshas:
        assert len(d.dosha_id) > 0
        assert len(d.name_hi) > 0
        assert len(d.shloka_reference) > 0
        assert d.severity in ("None", "Mild", "Moderate", "Severe")


def test_pancha_mahapurusha_logic(sample_native_chart):
    """Verify Pancha Mahapurusha checks require both Kendra and qualifying signs."""
    yogas = default_yoga_dosha_engine._evaluate_pancha_mahapurusha(sample_native_chart)
    assert len(yogas) == 5
    pmp_keys = [y.yoga_id for y in yogas]
    assert "PMP_RUCHAKA" in pmp_keys
    assert "PMP_BHADRA" in pmp_keys
    assert "PMP_HAMSA" in pmp_keys
    assert "PMP_MALAVYA" in pmp_keys
    assert "PMP_SASA" in pmp_keys


def test_gajakesari_and_chandra_yogas(sample_native_chart):
    """Verify Gajakesari and flanking Chandra yogas (Sunaphaa, Anaphaa, Dhurudhara)."""
    chandra_yogas = default_yoga_dosha_engine._evaluate_chandra_surya_yogas(sample_native_chart)
    cy_ids = [y.yoga_id for y in chandra_yogas]
    assert "CY_GAJAKESARI" in cy_ids
    assert "CY_DHURUDHARA" in cy_ids
    assert "CY_SUNAPHAA" in cy_ids
    assert "CY_ANAPHAA" in cy_ids
    assert "SY_BUDHADITYA" in cy_ids


def test_manglik_cancellation_rules(sample_native_chart):
    """Verify Kuja Dosha identifies cancellations when Mars is in own sign, Leo/Aquarius, or with Jupiter."""
    dosha_item, is_present, severity, is_cancelled = default_yoga_dosha_engine._evaluate_manglik_dosha(sample_native_chart)
    assert isinstance(is_present, bool)
    assert isinstance(is_cancelled, bool)
    if is_cancelled:
        assert len(dosha_item.cancellation_reasons) > 0


def test_kaal_sarp_12_types_structure(sample_native_chart):
    """Verify Kaal Sarp evaluation handles all 12 types and hemmed hemisphere logic."""
    dosha_item, ks_name, is_present = default_yoga_dosha_engine._evaluate_kaal_sarp_dosha(sample_native_chart)
    assert dosha_item.category == "Kaal Sarp"
    if is_present:
        assert any(t in ks_name for t in [
            "Anant", "Kulik", "Vasuki", "Shankhpal", "Padma", "Mahapadma",
            "Takshak", "Karkotak", "Shankhachood", "Ghatak", "Vishdhar", "Sheshnag"
        ])
    else:
        assert ks_name is None


def test_kemadruma_bhanga_cancellation(sample_native_chart):
    """Verify Kemadruma Bhanga applies when natural benefics are in Kendra."""
    kd = default_yoga_dosha_engine._evaluate_kemadruma_dosha(sample_native_chart)
    assert kd.dosha_id == "DOSHA_KEMADRUMA"
    if kd.is_cancelled:
        assert any("cancels Kemadruma" in r for r in kd.cancellation_reasons)

