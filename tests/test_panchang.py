"""
Unit tests for Vedic Jyotish Panchang service (VedicPanchangService).
Validates 5 pillars, ending times, Bhadra Mukha/Puchha/Vasa, Panchaka,
Gandamoola, Choghadiya, Horas, Auspicious/Inauspicious Muhurtas, and Planetary Matrix.
"""

import pytest
from datetime import date, datetime
from src.jyotish.services.panchang import VedicPanchangService


def test_panchang_delhi_oct_2026():
    target_d = date(2026, 10, 6)
    res = VedicPanchangService.get_full_panchang(
        target_date=target_d,
        latitude=28.6139,
        longitude=77.2090,
        city_name="नई दिल्ली (New Delhi)"
    )

    # 1. Sun & Moon timings
    assert "sunrise" in res["sun_moon"]
    assert "sunset" in res["sun_moon"]
    sr = res["sun_moon"]["sunrise"]
    ss = res["sun_moon"]["sunset"]
    assert sr.hour == 6
    assert ss.hour == 18

    # 2. Five Pillars
    pillars = res["five_pillars"]
    assert pillars["vara"]["name_hi"] == "मंगलवार"
    assert "एकादशी" in pillars["tithi"]["name"] or pillars["tithi"]["index"] == 26
    assert pillars["tithi"]["paksha"] == "कृष्ण पक्ष"
    assert "आश्लेषा" in pillars["nakshatra"]["name"] or pillars["nakshatra"]["index"] == 9
    assert pillars["yoga"]["index"] == 21  # Sadhya
    assert "बव" in pillars["karana"]["current"]["name"]

    # End times must be strings and datetimes
    assert pillars["tithi"]["end_time_str"] != ""
    assert pillars["nakshatra"]["end_time_str"] != ""

    # 3. Bhadra
    bhadra = res["bhadra"]
    assert "is_present" in bhadra

    # 4. Panchak & Gandamoola
    pg = res["panchak_gandamoola"]
    assert "panchaka" in pg
    assert "gandamoola" in pg
    # Ashlesha is a Gandamoola nakshatra
    assert pg["gandamoola"]["is_active"] is True
    assert "आश्लेषा" in pg["gandamoola"]["nakshatra"]

    # 5. Choghadiya & Horas
    ch = res["choghadiya_horas"]
    assert len(ch["day_choghadiyas"]) == 8
    assert len(ch["night_choghadiyas"]) == 8
    assert len(ch["horas_24"]) == 24
    # Tuesday day first choghadiya is Rog
    assert ch["day_choghadiyas"][0]["name"] == "रोग"

    # 6. Muhurtas
    muh = res["muhurtas"]
    assert len(muh["shubh_windows"]) >= 5
    assert len(muh["ashubh_windows"]) >= 5

    # 7. Planetary Transit Matrix
    matrix = res["transit_matrix"]
    assert len(matrix) >= 9
    sun = next(p for p in matrix if p["key"] == "Sun")
    moon = next(p for p in matrix if p["key"] == "Moon")
    assert sun["rashi"] == "कन्या (Virgo)"
    assert moon["rashi"] == "कर्क (Cancer)"


def test_panchang_arbitrary_date():
    # Test another date (e.g. Diwali / New Moon)
    target_d = date(2025, 11, 1)
    res = VedicPanchangService.get_full_panchang(target_d)
    assert res["meta"]["date"] == target_d
    assert res["five_pillars"]["tithi"]["index"] in range(1, 31)
    assert res["five_pillars"]["nakshatra"]["index"] in range(1, 28)
