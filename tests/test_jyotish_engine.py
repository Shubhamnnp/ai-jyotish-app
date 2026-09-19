"""
Unit and Integration Test Suite for JyotishOS.
Tests:
1. Astronomical calculations and Lahiri ayanamsa.
2. Ashtakavarga SAV invariant (Sum == 337).
3. Vimshottari 120-year Dasha hierarchy lookup.
4. Divisional Charts (D1, D9, D10).
5. 32-Rules execution & Gajakesari/Mangal Dosha triggers.
6. Ghatna Query (Event Window Analysis) end-to-end.
7. Prashna Kundali horary analysis.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

from datetime import date, time, datetime

from src.jyotish.core.models import BirthData, GhatnaQueryInput
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.varga import VargaCalculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.dasha.vimshottari import default_dasha_engine
from src.jyotish.services.event_query import default_event_query_service
from src.jyotish.services.prashna import default_prashna_service
from src.jyotish.rules.engine import default_rules_engine


def get_sample_birth_data() -> BirthData:
    """Standard benchmark profile: 15-May-1980, 10:30 AM IST, New Delhi."""
    return BirthData(
        name="Benchmark Jataka",
        birth_date=date(1980, 5, 15),
        birth_time=time(10, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi",
        confidence="Exact"
    )


def test_chart_calculation():
    """Verify planetary positions, houses, and Panchang generation."""
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_chart(profile)

    assert chart is not None
    assert 1 <= chart.lagna_sign_id <= 12
    assert 0.0 <= chart.lagna_degree < 30.0
    assert len(chart.planets) == 9
    assert len(chart.houses) == 12

    # Check Sun position in Taurus in mid-May
    sun = chart.planets["Sun"]
    assert sun.sign_name in ("Taurus", "Aries")  # Depending on exact sidereal boundary
    assert 0.0 <= sun.longitude < 360.0

    # Check Moon and Nakshatra
    moon = chart.planets["Moon"]
    assert moon.nakshatra_name != ""
    assert 1 <= moon.nakshatra_pada <= 4

    # Check Atmakaraka exists
    assert chart.atmakaraka in chart.planets


def test_ashtakavarga_conservation_337():
    """Verify that Sarva Ashtakavarga (SAV) totals exactly 337 bindus across all 12 signs."""
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_chart(profile)
    ashtak = AshtakavargaCalculator.calculate(chart)

    assert ashtak is not None
    assert len(ashtak.sav) == 12
    total_sav = sum(ashtak.sav)
    assert total_sav == 337, f"Expected exactly 337 SAV bindus, got {total_sav}"


def test_divisional_charts_varga():
    """Verify D1, D2, D9, D10 calculation."""
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_chart(profile)
    vargas = VargaCalculator.calculate_all_vargas(chart)

    assert "D1" in vargas
    assert "D9" in vargas
    assert "D10" in vargas

    # D9 Navamsha sign check
    d9 = vargas["D9"]
    assert 1 <= d9.lagna_sign_id <= 12
    assert len(d9.planets) == 9


def test_vimshottari_dasha_hierarchy():
    """Verify point-in-time Vimshottari dasha hierarchy for a specific date."""
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_chart(profile)
    birth_dt = datetime.combine(profile.birth_date, profile.birth_time)
    moon_lon = chart.planets["Moon"].longitude

    # Test query for future date 2027-04-12
    target = date(2027, 4, 12)
    active_dasha = default_dasha_engine.get_active_dasha_at(birth_dt, moon_lon, target)

    assert active_dasha is not None
    assert active_dasha.mahadasha.lord != ""
    assert active_dasha.antardasha.lord != ""
    assert active_dasha.pratyantardasha.lord != ""
    assert active_dasha.mahadasha.start_date <= datetime.combine(target, datetime.min.time()) <= active_dasha.mahadasha.end_date


def test_rules_library_loaded():
    """Verify that all 32 classical starter rules are loaded from JSON."""
    rules = default_rules_engine.rules
    assert len(rules) == 32, f"Expected 32 rules, found {len(rules)}"
    assert "BPHS_GAJAKESARI_001" in default_rules_engine.rules_by_id
    assert "GOCHARA_SHANI_SADE_SATI" in default_rules_engine.rules_by_id
    assert "BHAV_10TH_DASAMESH_STRENGTH" in default_rules_engine.rules_by_id
    assert "TAJIKA_PRASHNA_ITHASALA" in default_rules_engine.rules_by_id
    assert "BHAV_CHANDRA_LAGNA_LORD" in default_rules_engine.rules_by_id
    assert "GOCHARA_DOUBLE_TRANSIT_10TH" in default_rules_engine.rules_by_id


def test_ashtakavarga_shodhana():
    """Verify Trikona and Ekadhipatya Shodhana and Shodhita Pinda."""
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_full_chart(profile)
    sh = chart.ashtakavarga.shodhana
    assert sh is not None
    assert "Sun" in sh.trikona_reduced_bav
    assert "Sun" in sh.ekadhipatya_reduced_bav
    assert sh.yoga_pinda["Sun"] > 0


def test_shadbala_and_avasthas():
    """Verify 6-fold Shadbala, Virupas, and Planetary Avasthas."""
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_full_chart(profile)
    sb = chart.shadbala
    assert sb is not None
    assert len(sb.planets) == 7
    sun_sb = sb.planets["Sun"]
    assert sun_sb.total_virupas > 0
    assert sun_sb.baladi_avastha != ""
    assert sun_sb.deeptadi_avastha != ""


def test_jaimini_and_upagrahas():
    """Verify 7/8 Chara Karakas, Arudhas, and Upagrahas."""
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_full_chart(profile)
    j = chart.jaimini
    assert j is not None
    assert "AK" in j.karakas_7
    assert "AL" in j.arudha_pada_names
    assert "UL" in j.arudha_pada_names
    assert j.karakamsha_sign_name != ""

    u = chart.upagrahas
    assert u is not None
    assert u.gulika_sign_name != ""
    assert u.mandi_sign_name != ""


def test_secondary_dashas():
    """Verify Yogini Dasha and Jaimini Chara Dasha."""
    from src.jyotish.dasha.yogini import default_yogini_engine
    from src.jyotish.dasha.chara import default_chara_engine

    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_full_chart(profile)
    birth_dt = datetime.combine(profile.birth_date, profile.birth_time)
    moon_lon = chart.planets["Moon"].longitude

    yog = default_yogini_engine.get_active_yogini_at(birth_dt, moon_lon, date(2027, 4, 12))
    assert yog["yogini"] != ""

    chara = default_chara_engine.get_active_chara_dasha_at(chart, date(2027, 4, 12))
    assert chara["sign_name"] != ""


def test_varshaphal_annual_chart():
    """Verify Tajika Solar Return, Muntha, and Varshesha."""
    from src.jyotish.services.varshaphal import default_varshaphal_service
    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_full_chart(profile)

    vp = default_varshaphal_service.calculate_varshaphal(chart, 2027)
    assert vp["muntha_sign"] != ""
    assert vp["varshesha"] != ""
    assert len(vp["sahams"]) >= 4


def test_birth_time_rectification():
    """Verify BTR candidate ranking."""
    from src.jyotish.services.btr import default_btr_service, LifeEvent
    profile = get_sample_birth_data()
    events = [LifeEvent(event_date=date(2005, 6, 1), event_category="career", description="Promotion")]
    cands = default_btr_service.rectify_birth_time(profile, events, window_minutes=10, step_minutes=2)
    assert len(cands) > 0
    assert cands[0].fit_score >= 0.0


def test_kundali_milan_36_gunas():
    """Verify 36-Guna Ashtakoota and Manglik matching."""
    from src.jyotish.services.milan import default_milan_service
    b1 = get_sample_birth_data()
    b2 = BirthData(name="Partner", birth_date=date(1982, 9, 21), birth_time=time(8, 0), latitude=28.61, longitude=77.20)

    m = default_milan_service.match_charts(b1, b2)
    assert 0.0 <= m.total_score <= 36.0
    assert m.verdict != ""


def test_geocoding_and_vedic_rishi():
    """Verify Geocoding API and Vedic Rishi validation client."""
    from src.jyotish.services.geocoding import default_geocoding_service
    from src.jyotish.services.vedic_rishi import default_vedic_rishi_client

    locs = default_geocoding_service.search("Varanasi")
    assert len(locs) > 0
    assert locs[0].city in ("Varanasi", "Kashi")

    profile = get_sample_birth_data()
    chart = default_chart_calculator.calculate_full_chart(profile)
    val = default_vedic_rishi_client.cross_validate_chart(chart)
    assert val["status"] == "verified"


def test_ghatna_query_pipeline():
    """Test the Core MVP feature: Ghatna Query for 12-04-2027."""
    profile = get_sample_birth_data()
    query_input = GhatnaQueryInput(
        birth_data=profile,
        target_date=date(2027, 4, 12),
        theme="career"
    )

    result = default_event_query_service.execute_query(query_input)

    assert result is not None
    assert 0.0 <= result.composite_score <= 1.0
    assert result.confidence_band != ""
    assert len(result.all_evaluated_rules) > 0
    assert result.narrative_hi != ""
    assert result.narrative_en != ""
    assert "वैधानिक" in result.disclaimer


def test_prashna_horary():
    """Test query-time Horary chart generation and analysis."""
    res = default_prashna_service.generate_prashna_chart(
        query_text="Kya mujhe videsh yatra ka avsar milega?",
        query_category="travel"
    )

    assert res is not None
    assert "karyesh" in res
    assert "verdict" in res
    assert 0.0 <= res["verdict_score"] <= 1.0


if __name__ == "__main__":
    test_chart_calculation()
    test_ashtakavarga_conservation_337()
    test_divisional_charts_varga()
    test_vimshottari_dasha_hierarchy()
    test_rules_library_loaded()
    test_ashtakavarga_shodhana()
    test_shadbala_and_avasthas()
    test_jaimini_and_upagrahas()
    test_secondary_dashas()
    test_varshaphal_annual_chart()
    test_birth_time_rectification()
    test_kundali_milan_36_gunas()
    test_geocoding_and_vedic_rishi()
    test_ghatna_query_pipeline()
    test_prashna_horary()
    print("ALL TESTS PASSED SUCCESSFULLY!")

