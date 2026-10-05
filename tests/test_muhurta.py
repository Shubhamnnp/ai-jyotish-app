"""
Unit tests for the upgraded Vedic Muhurta Engine and Classical Prohibitions.
Validates:
1. Pitru Paksha prohibition for Griha Pravesh and Vivaha.
2. Chaturmas & Devashayana detection.
3. Bhadra (Vishti Karana) detection and Loka residence.
4. Multi-day range scanner strictly filtering prohibited dates.
"""

from datetime import date
import pytest
from src.jyotish.services.muhurta import default_muhurta_engine, default_muhurta_scanner


def test_pitru_paksha_detection():
    # 2026-10-05: Sun in Virgo, Krishna Dashami (Pitru Paksha)
    p_info = default_muhurta_engine.get_daily_panchang_and_doshas(date(2026, 10, 5))
    assert p_info["is_pitru_paksha"] is True
    assert p_info["is_chaturmas"] is True
    assert p_info["sun_sign_id"] == 6
    assert p_info["tithi_idx"] >= 16

    # Griha Pravesh on 2026-10-05 must be strictly prohibited (score <= 10)
    res_gp = default_muhurta_engine.evaluate_activity_suitability(date(2026, 10, 5), "griha_pravesh")
    assert res_gp["suitability_score"] <= 10
    assert "वर्जित" in res_gp["verdict"]
    assert len(res_gp["fatal_violations"]) >= 1
    assert any("पितृपक्ष" in f for f in res_gp["fatal_violations"])

    # Vivaha on 2026-10-05 must also be strictly prohibited
    res_viv = default_muhurta_engine.evaluate_activity_suitability(date(2026, 10, 5), "vivaha")
    assert res_viv["suitability_score"] <= 10
    assert "वर्जित" in res_viv["verdict"]


def test_bhadra_and_loka_detection():
    # 2026-10-05 12:00: Karana 50 (Vishti Karana) with Moon in Cancer -> Martya Loka
    p_info = default_muhurta_engine.get_daily_panchang_and_doshas(date(2026, 10, 5))
    assert p_info["is_bhadra"] is True
    assert "मृत्युलोक" in p_info["bhadra_loka"]
    assert p_info["bhadra_is_fatal"] is True


def test_range_scanner_rejects_pitru_paksha():
    # Scanning from 2026-10-05 for 60 days should not return any Pitru Paksha dates among top auspicious dates
    results = default_muhurta_scanner.scan_range(
        activity_type="griha_pravesh",
        start_date=date(2026, 10, 5),
        end_date=date(2026, 12, 10),
        top_n=5
    )
    assert len(results) > 0
    for r in results:
        # All top dates must be after Pitru Paksha / Devutthani Ekadashi
        assert r["score"] >= 80
        assert r["raw_date"] >= date(2026, 11, 1)
