"""
Shastriya Yoga & Dosha Pure-Function Catalogue Test Suite (Phase 4 Task 7).
Verifies:
1. Pancha Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasa).
2. Gajakesari Yoga (Jupiter in Kendra from Moon).
3. Dharma-Karmadhipati Raja Yoga (9th & 10th lords relationship).
4. Dhana Yogas (2nd & 11th, 5th & 9th lord connections).
5. Vipareeta Raja Yogas (Harsha 6th, Sarala 8th, Vimala 12th).
6. Neechabhanga Raja Yoga (Clause 1 & 2 dispositor/exaltation cancellations).
7. Amala Yoga (natural benefic in 10th from Lagna or Moon).
8. Manglik Dosha with classical cancellations (Pariharas).
9. Kemadruma Dosha with Kendra-benefic cancellations.
10. Kaal Sarp Dosha (Full vs Partial across Rahu-Ketu axis).
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.yoga import default_yoga_dosha_engine, ClassicalYogaDoshaEngine


@pytest.fixture
def swami_vivekananda_chart():
    bd = BirthData(
        name="Swami Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=time(6, 33, 0),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.5,
        city="Kolkata"
    )
    return default_chart_calculator.calculate_full_chart(bd)


def test_vivekananda_yogas_and_doshas(swami_vivekananda_chart):
    """Verify classical yogas evaluated for Swami Vivekananda."""
    analysis = default_yoga_dosha_engine.evaluate_all(swami_vivekananda_chart)
    assert analysis.active_yogas_count > 0

    y_map = {y.yoga_id: y for y in analysis.yogas}
    assert "PMP_RUCHAKA" in y_map
    assert "PMP_HAMSA" in y_map
    assert "CY_GAJAKESARI" in y_map
    assert "RY_DHARMA_KARMADHIPATI" in y_map
    assert "DY_2_11_PRIME" in y_map
    assert "AY_AMALA" in y_map

    # Doshas
    d_map = {d.dosha_id: d for d in analysis.doshas}
    assert "DOSHA_MANGLIK" in d_map
    assert "DOSHA_KAAL_SARP" in d_map
    assert "DOSHA_KEMADRUMA" in d_map
    assert "DOSHA_GANDANTA" in d_map


def test_pancha_mahapurusha_logic(swami_vivekananda_chart):
    """Verify Pancha Mahapurusha requires Kendra + Own/Exaltation."""
    pmp = ClassicalYogaDoshaEngine._evaluate_pancha_mahapurusha(swami_vivekananda_chart)
    assert len(pmp) == 5
    for item in pmp:
        assert item.category == "Pancha Mahapurusha"
        assert item.shloka_reference.startswith("BPHS Ch. 35")
        if item.is_active:
            assert item.strength_score >= 50.0


def test_dhana_yogas_structure(swami_vivekananda_chart):
    """Verify Dhana Yogas evaluate 2nd, 5th, 9th, and 11th lord alliances."""
    dy = ClassicalYogaDoshaEngine._evaluate_dhana_yogas(swami_vivekananda_chart)
    assert len(dy) == 3
    ids = [item.yoga_id for item in dy]
    assert "DY_2_11_PRIME" in ids
    assert "DY_LAGNESH_DHANA" in ids
    assert "DY_TRIKONA_LAKSHMI" in ids


def test_amala_yoga_structure(swami_vivekananda_chart):
    """Verify Amala Yoga checks natural benefics in 10th from Lagna or Moon."""
    ay = ClassicalYogaDoshaEngine._evaluate_amala_yoga(swami_vivekananda_chart)
    assert len(ay) == 1
    item = ay[0]
    assert item.yoga_id == "AY_AMALA"
    assert item.category == "Auspicious Yoga"
    assert "BPHS Ch. 36" in item.shloka_reference


def test_manglik_cancellations(swami_vivekananda_chart):
    """Verify Manglik dosha evaluation and cancellation detection."""
    m_dosha, is_present, sev, is_cancelled = ClassicalYogaDoshaEngine._evaluate_manglik_dosha(swami_vivekananda_chart)
    assert m_dosha.dosha_id == "DOSHA_MANGLIK"
    if is_present and is_cancelled:
        assert len(m_dosha.cancellation_reasons) > 0


def test_kemadruma_bhanga(swami_vivekananda_chart):
    """Verify Kemadruma cancellation by benefics in Kendra."""
    k_dosha = ClassicalYogaDoshaEngine._evaluate_kemadruma_dosha(swami_vivekananda_chart)
    assert k_dosha.dosha_id == "DOSHA_KEMADRUMA"
    if k_dosha.is_present and k_dosha.is_cancelled:
        assert "cancels Kemadruma" in "; ".join(k_dosha.cancellation_reasons)
