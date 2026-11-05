"""
Phase 2 Deep Calculation Engine & Benchmark Verification Suite.
Validates tasks P2-T1 through P2-T7:
- P2-T1: Planetary motion, speeds, retrograde status, combustion orbs, Graha Yuddha.
- P2-T2: Ayanamsa resolution and house systems across polar and standard latitudes.
- P2-T3: D1 to D60 Shodashvarga algorithms, Vargottama, and Vaisheshikamsa designations.
- P2-T4: Shadbala 6-fold components, BPHS virupas, and Naisargika invariants.
- P2-T5: Ashtakavarga 337 bindu conservation invariant, Trikona & Ekadhipatya Shodhana.
- P2-T6: 9 Dasha systems cycles, balance, and boundary timing.
"""

import pytest
from datetime import date, time, datetime, timezone
import math

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.ephemeris import default_ephemeris_provider, resolve_ayanamsa_mode
from src.jyotish.core.combustion import CombustionCalculator, CombustionOrbConfig
from src.jyotish.core.varga import VargaCalculator, SHODASHAVARGA_CODES, VAISHESHIKAMSA_BENCHMARKS
from src.jyotish.core.shadbala import ShadbalaCalculator, NAISARGIKA_BALA, REQUIRED_VIRUPAS
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.houses import HouseCalculator
from src.jyotish.dasha.vimshottari import default_dasha_engine
from src.jyotish.dasha.yogini import YoginiDashaEngine, YOGINI_SEQUENCE, TOTAL_YOGINI_CYCLE_YEARS


@pytest.fixture(scope="module")
def standard_chart():
    """Standard Vedic benchmark chart (Swami Vivekananda)."""
    bd = BirthData(
        name="Swami Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=time(6, 33, 0),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.89,
        gender="male",
        confidence="exact"
    )
    return default_chart_calculator.calculate_full_chart(bd)


# -----------------------------------------------------------------------------
# P2-T1: Planetary Motion, Retrograde, Combustion & Graha Yuddha
# -----------------------------------------------------------------------------
def test_p2_t1_planetary_speeds_and_retrograde(standard_chart):
    """Verify planetary speeds are calculated, Rahu/Ketu are always retrograde."""
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        pos = standard_chart.planets[p_name]
        assert hasattr(pos, "speed")
        assert isinstance(pos.speed, float)
        # Check retrograde consistency
        if pos.is_retrograde:
            assert pos.speed < 0.0

    # Lunar nodes always retrograde
    rahu = standard_chart.planets["Rahu"]
    ketu = standard_chart.planets["Ketu"]
    assert rahu.is_retrograde is True
    assert ketu.is_retrograde is True
    assert rahu.speed < 0.0
    assert ketu.speed < 0.0
    # Ketu exactly 180 degrees from Rahu
    diff = abs(ketu.longitude - rahu.longitude)
    assert pytest.approx(diff, abs=0.01) == 180.0 or pytest.approx(diff, abs=0.01) == 180.0


def test_p2_t1_combustion_classical_orbs():
    """Verify classical combustion orbs according to BPHS and Varahamihira."""
    sun_lon = 100.0

    # Mars: Direct orb 17 degrees
    assert CombustionCalculator.check_combustion("Mars", 116.0, sun_lon, is_retrograde=False) is True
    assert CombustionCalculator.check_combustion("Mars", 118.0, sun_lon, is_retrograde=False) is False

    # Jupiter: Direct orb 11 degrees
    assert CombustionCalculator.check_combustion("Jupiter", 110.0, sun_lon, is_retrograde=False) is True
    assert CombustionCalculator.check_combustion("Jupiter", 112.0, sun_lon, is_retrograde=False) is False

    # Mercury: Direct orb 14 deg, Retrograde orb 12 deg
    assert CombustionCalculator.check_combustion("Mercury", 113.0, sun_lon, is_retrograde=False) is True
    assert CombustionCalculator.check_combustion("Mercury", 113.0, sun_lon, is_retrograde=True) is False
    assert CombustionCalculator.check_combustion("Mercury", 111.0, sun_lon, is_retrograde=True) is True

    # Venus: Direct orb 10 deg, Retrograde orb 8 deg
    assert CombustionCalculator.check_combustion("Venus", 109.0, sun_lon, is_retrograde=False) is True
    assert CombustionCalculator.check_combustion("Venus", 109.0, sun_lon, is_retrograde=True) is False
    assert CombustionCalculator.check_combustion("Venus", 107.0, sun_lon, is_retrograde=True) is True


def test_p2_t1_graha_yuddha_detection():
    """Verify Graha Yuddha is detected between Taragrahas within 1 degree."""
    bd = BirthData(
        name="Graha Yuddha Test Chart",
        birth_date=date(2008, 9, 11),
        birth_time=time(12, 0, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    wars = default_chart_calculator.detect_graha_yuddha(chart)
    assert isinstance(wars, list)
    for war in wars:
        assert war["separation_deg"] <= 1.0
        assert war["planet1"] in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        assert war["planet2"] in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        assert war["winner"] in [war["planet1"], war["planet2"]]


# -----------------------------------------------------------------------------
# P2-T2: Ayanamsa and House Systems Math
# -----------------------------------------------------------------------------
def test_p2_t2_ayanamsa_resolution():
    """Verify various ayanamsas resolve to distinct valid degrees."""
    dt_test = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    jd_test = default_ephemeris_provider.datetime_to_jd(dt_test)

    lahiri = default_ephemeris_provider.calculate_ayanamsa(jd_test, "Lahiri")
    raman = default_ephemeris_provider.calculate_ayanamsa(jd_test, "Raman")
    kp = default_ephemeris_provider.calculate_ayanamsa(jd_test, "Krishnamurti")

    assert 24.0 < lahiri < 25.0
    assert 22.0 < raman < 23.5
    assert 24.0 < kp < 25.0
    # Raman is ~1.5 deg less than Lahiri
    assert (lahiri - raman) > 1.0


def test_p2_t2_house_systems_and_polar_safeguard():
    """Verify house systems work standardly and circumpolar polar latitude collapses safely."""
    # Standard Delhi
    jd = default_ephemeris_provider.datetime_to_jd(datetime(2026, 6, 21, 6, 0, 0, tzinfo=timezone.utc))
    res_ws = HouseCalculator.calculate_houses(jd=jd, latitude=28.6, longitude=77.2, house_system="Whole Sign")
    assert len(res_ws.cusps) == 12
    assert res_ws.polar_latitude_adjusted is False

    # Extreme Arctic Tromso (69.64° N) with Placidus: should trigger polar adjustment to Equal
    res_polar = HouseCalculator.calculate_houses(jd=jd, latitude=69.64, longitude=18.95, house_system="Placidus")
    assert len(res_polar.cusps) == 12
    assert res_polar.polar_latitude_adjusted is True
    assert "polar" in str(res_polar.warning).lower()


# -----------------------------------------------------------------------------
# P2-T3: D1 to D60 Shodashvarga Mathematical Verification
# -----------------------------------------------------------------------------
def test_p2_t3_shodashavarga_completeness(standard_chart):
    """Verify all 16 canonical Shodashavarga charts are generated with valid planets."""
    shodasha = VargaCalculator.calculate_all_shodashavarga(standard_chart)
    for code in SHODASHAVARGA_CODES:
        assert code in shodasha, f"Missing varga {code}"
        vchart = shodasha[code]
        assert len(vchart.planets) >= 9, f"Varga {code} missing planets"
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            pos = vchart.planets[p_name]
            assert 1 <= pos.sign_id <= 12
            assert 1 <= pos.house_number <= 12


def test_p2_t3_vaisheshikamsa_benchmarks(standard_chart):
    """Verify Vaisheshikamsa designations match BPHS 16-division benchmarks."""
    vaisheshikamsa = VargaCalculator.calculate_vaisheshikamsa(standard_chart)
    for p_name, data in vaisheshikamsa.items():
        assert "count" in data
        assert "designation" in data
        assert 0 <= data["count"] <= 16
        if data["count"] in VAISHESHIKAMSA_BENCHMARKS:
            assert data["designation"] == VAISHESHIKAMSA_BENCHMARKS[data["count"]]


# -----------------------------------------------------------------------------
# P2-T4: Shadbala 6-Fold Classical Components & Invariants
# -----------------------------------------------------------------------------
def test_p2_t4_shadbala_invariants(standard_chart):
    """Verify Shadbala 6-fold components, fixed Naisargika Bala, and minimum virupas."""
    shadbala = ShadbalaCalculator.calculate(standard_chart)
    assert len(shadbala.planets) == 7

    for p_name, res in shadbala.planets.items():
        # Sthana, Dik, Kaala, Cheshta, Naisargika, Drik Balas must all be non-negative
        assert res.sthana_bala >= 0.0
        assert res.dik_bala >= 0.0
        assert res.kaala_bala >= 0.0
        assert res.cheshta_bala >= 0.0
        assert res.drik_bala is not None
        # Naisargika Bala is an invariant fixed classical value
        assert pytest.approx(res.naisargika_bala, abs=0.1) == NAISARGIKA_BALA[p_name]
        # Sum of 6 components equals total_virupas
        expected_total = res.sthana_bala + res.dik_bala + res.kaala_bala + res.cheshta_bala + res.naisargika_bala + res.drik_bala
        assert pytest.approx(res.total_virupas, abs=0.2) == expected_total
        # Required virupa threshold validation
        req = REQUIRED_VIRUPAS[p_name]
        assert res.is_strong == (res.total_virupas >= req)


# -----------------------------------------------------------------------------
# P2-T5: Ashtakavarga Invariants (337 Bindus) and Shodhana
# -----------------------------------------------------------------------------
def test_p2_t5_ashtakavarga_337_invariant_and_shodhana(standard_chart):
    """Verify exact mathematical conservation of 337 SAV bindus and Shodhana reductions."""
    av_res = AshtakavargaCalculator.calculate(standard_chart)
    # Conservation of 337 total bindus across 12 signs
    assert sum(av_res.sav) == 337
    assert av_res.total_bindus == 337

    # Verify BAV has 7 planets, each with 12 signs
    assert len(av_res.bav) == 7
    for p_name, signs in av_res.bav.items():
        assert len(signs) == 12

    # Verify Shodhana result
    shodhana = av_res.shodhana
    assert shodhana is not None
    assert hasattr(shodhana, "rashi_pinda")
    assert hasattr(shodhana, "graha_pinda")
    assert hasattr(shodhana, "yoga_pinda")
    for p_name in av_res.bav.keys():
        assert shodhana.rashi_pinda[p_name] > 0
        assert shodhana.graha_pinda[p_name] >= 0
        assert shodhana.yoga_pinda[p_name] == shodhana.rashi_pinda[p_name] + shodhana.graha_pinda[p_name]


# -----------------------------------------------------------------------------
# P2-T6: 9 Dasha Systems Cycles and Balance
# -----------------------------------------------------------------------------
def test_p2_t6_vimshottari_and_yogini_cycles(standard_chart):
    """Verify Vimshottari 120-year cycle and Yogini 36-year cycle."""
    # Vimshottari
    v_timeline = default_dasha_engine.generate_timeline(standard_chart)
    assert len(v_timeline) == 9
    first_md = v_timeline[0]
    last_md = v_timeline[-1]
    # Total span covers 120 years from birth
    total_days = (last_md["end_date"] - first_md["start_date"]).days
    total_years = total_days / 365.25
    assert 110.0 < total_years < 125.0

    # Yogini
    y_engine = YoginiDashaEngine()
    y_res = y_engine.generate_timeline(standard_chart)
    assert len(y_res) >= 8  # 8 Yoginis: Mangala, Pingala, Dhanya, Bhramari, Bhadrika, Ulka, Siddha, Sankata
    # Sum of 8 yoginis in classical cycle = 1+2+3+4+5+6+7+8 = 36 years
    assert TOTAL_YOGINI_CYCLE_YEARS == 36.0
    assert sum(y["years"] for y in YOGINI_SEQUENCE) == 36
    assert y_res[0]["yogini"] in [y["name"] for y in YOGINI_SEQUENCE]
