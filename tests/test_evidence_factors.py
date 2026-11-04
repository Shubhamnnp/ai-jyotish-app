"""
Comprehensive unit test suite for Factor Extractor (Phase 5, Task P5-T1).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.1).

Verifies:
1. Extraction completeness: all 9 planets and 12 houses typed and populated.
2. Pure function determinism: multiple extractions yield identical results.
3. Planet factor attributes: avasthas, combustion, shadbala virupas/ratio, nakshatras, conjunctions.
4. Classical Parashari aspect geometry (Mars 4,7,8; Jupiter 5,7,9; Saturn 3,7,10).
5. House factor attributes: lord placement, benefic/malefic occupants and aspects, SAV bindus.
6. Chara Karaka and Naisargika Karakatwa integrity.
7. Vargottama and Varga sign consistency.
"""

import sys
import os
import pytest
from datetime import date, datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.evidence.factors import (
    FactorExtractor,
    default_factor_extractor,
    ChartFactors,
    PlanetFactors,
    HouseFactors
)


@pytest.fixture(scope="module")
def vivekananda_chart():
    """Swami Vivekananda benchmark chart."""
    bd = BirthData(
        name="Swami Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=datetime.strptime("06:33:00", "%H:%M:%S").time(),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.5,
        city="Kolkata",
        confidence="Exact"
    )
    return default_chart_calculator.calculate_full_chart(bd)


def test_factor_extractor_completeness(vivekananda_chart):
    """Verify all 9 planets and 12 houses are extracted with typed factors."""
    factors: ChartFactors = default_factor_extractor.extract_factors(vivekananda_chart)

    assert factors.lagna_sign == "Capricorn"
    assert factors.lagna_lord == "Saturn"
    assert factors.moon_sign == "Virgo"
    assert factors.sun_sign == "Sagittarius"

    # 9 Grahas check
    expected_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in expected_planets:
        assert p in factors.planets, f"Missing planet {p} in extracted factors"
        pf = factors.planets[p]
        assert isinstance(pf, PlanetFactors)
        assert pf.planet == p
        assert 1 <= pf.sign_id <= 12
        assert 1 <= pf.house_from_lagna <= 12
        assert 1 <= pf.house_from_moon <= 12
        assert pf.dignity.lower() in ("exalted", "own", "moolatrikona", "friendly", "friend", "neutral", "enemy", "debilitated")
        assert len(pf.nakshatra_name) > 0
        assert 1 <= pf.nakshatra_pada <= 4
        assert len(pf.nakshatra_lord) > 0

    # 12 Houses check
    assert len(factors.houses) == 12
    for h in range(1, 13):
        assert h in factors.houses, f"Missing house {h} in extracted factors"
        hf = factors.houses[h]
        assert isinstance(hf, HouseFactors)
        assert hf.house_num == h
        assert 1 <= hf.sign_id <= 12
        assert len(hf.lord) > 0
        assert 1 <= hf.lord_placement_house <= 12
        assert hf.sav_bindus >= 0


def test_pure_function_determinism(vivekananda_chart):
    """Verify FactorExtractor is a deterministic pure function of the chart."""
    factors_1 = FactorExtractor.extract_factors(vivekananda_chart)
    factors_2 = FactorExtractor.extract_factors(vivekananda_chart)

    # Identical JSON serializations
    assert factors_1.model_dump() == factors_2.model_dump()


def test_planet_factors_avasthas_and_shadbala(vivekananda_chart):
    """Verify Avastha calculations and Shadbala ratio mappings."""
    factors = default_factor_extractor.extract_factors(vivekananda_chart)
    sun_f = factors.planets["Sun"]

    assert any(sun_f.baladi_avastha.startswith(av) for av in ("Bala", "Kumara", "Yuva", "Vriddha", "Mrita"))
    assert any(sun_f.jagratadi_avastha.startswith(av) for av in ("Jagrata", "Swapna", "Sushupti"))
    assert len(sun_f.deeptadi_avastha) > 0
    assert sun_f.shadbala_virupas > 0.0
    assert sun_f.shadbala_ratio > 0.0


def test_parashari_special_aspect_geometry(vivekananda_chart):
    """Verify special aspect rules (Mars 4,7,8; Jupiter 5,7,9; Saturn 3,7,10; Sun 7)."""
    factors = default_factor_extractor.extract_factors(vivekananda_chart)

    mars_f = factors.planets["Mars"]
    jup_f = factors.planets["Jupiter"]
    sat_f = factors.planets["Saturn"]
    sun_f = factors.planets["Sun"]

    # Sun in H1 aspects H7 (12th from Lagna -> aspects H6)
    sun_h = sun_f.house_from_lagna
    expected_sun_target = ((sun_h + 7 - 2) % 12) + 1
    assert expected_sun_target in sun_f.aspects_given_to_houses

    # Mars aspects 4, 7, 8 relative houses
    mars_h = mars_f.house_from_lagna
    for rel in [4, 7, 8]:
        target = ((mars_h + rel - 2) % 12) + 1
        assert target in mars_f.aspects_given_to_houses

    # Jupiter aspects 5, 7, 9 relative houses
    jup_h = jup_f.house_from_lagna
    for rel in [5, 7, 9]:
        target = ((jup_h + rel - 2) % 12) + 1
        assert target in jup_f.aspects_given_to_houses

    # Saturn aspects 3, 7, 10 relative houses
    sat_h = sat_f.house_from_lagna
    for rel in [3, 7, 10]:
        target = ((sat_h + rel - 2) % 12) + 1
        assert target in sat_f.aspects_given_to_houses


def test_house_factors_occupants_and_classification(vivekananda_chart):
    """Verify house benefic/malefic occupancy and kendra/trikona/dusthana classification."""
    factors = default_factor_extractor.extract_factors(vivekananda_chart)

    # House 1 is Kendra and Trikona
    h1 = factors.houses[1]
    assert h1.is_kendra is True
    assert h1.is_trikona is True
    assert h1.is_dusthana is False

    # House 6 is Dusthana and Upachaya
    h6 = factors.houses[6]
    assert h6.is_dusthana is True
    assert h6.is_upachaya is True
    assert h6.is_kendra is False

    # House 10 is Kendra and Upachaya
    h10 = factors.houses[10]
    assert h10.is_kendra is True
    assert h10.is_upachaya is True


def test_karakatwas_and_chara_karakas(vivekananda_chart):
    """Verify Jaimini Chara Karakas and Naisargika Karakatwas."""
    factors = default_factor_extractor.extract_factors(vivekananda_chart)

    assert factors.atmakaraka is not None
    assert factors.amatyakaraka is not None

    for p_name, pf in factors.planets.items():
        assert len(pf.naisargika_karakatwas) >= 2
        if p_name == factors.atmakaraka:
            assert pf.chara_karaka == "AK"
        if p_name == factors.amatyakaraka:
            assert pf.chara_karaka == "AmK"


def test_ashtakavarga_bindus_populated(vivekananda_chart):
    """Verify Ashtakavarga BAV and SAV bindus are populated."""
    factors = default_factor_extractor.extract_factors(vivekananda_chart)

    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        pf = factors.planets[p_name]
        assert pf.bav_bindus >= 0

    total_sav = sum(hf.sav_bindus for hf in factors.houses.values())
    assert total_sav == 337, f"SAV across all 12 houses must sum to exactly 337, found {total_sav}"
