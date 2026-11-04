"""
Tolerance Enforcement Test Suite for 100-Chart Oracle (Phase 2 Task P2-T2).
Enforces hard mathematical gates against the authoritative Swiss Ephemeris oracle:
1. Graha longitudes: <= 0.001 deg (3.6 arcsec in Moshier mode, < 1 arcsec with .se1).
2. Lagna longitude: <= 1 arcmin (0.0167 deg).
3. Bhava cusps: <= 1 arcmin (0.0167 deg).
4. Vimshottari dasha balance at birth: <= 0.0001 year (< 1 hour).
5. Ashtakavarga: 0 error (exact integer parity, SAV sum invariant == 337).
6. Jaimini 7 Chara Karakas: exact ordering match without inversion.
"""

import os
import sys
import json
import pytest
from datetime import datetime, date, time

# Ensure project root in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator
from src.jyotish.core.ephemeris import SwissEphemerisProvider
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.jaimini import default_jaimini_calculator
from src.jyotish.dasha.vimshottari import default_dasha_engine


@pytest.fixture(scope="module")
def oracle_data():
    json_path = os.path.join(curr_dir, "oracle_100_benchmarks.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_oracle_dataset_integrity(oracle_data):
    """Verify oracle dataset loaded with all 100 benchmarks across 4 categories."""
    assert "benchmarks" in oracle_data
    benchmarks = oracle_data["benchmarks"]
    assert len(benchmarks) == 100

    categories = set(b["category"] for b in benchmarks.values())
    assert categories == {"historical", "modern", "edge_dates", "polar_latitudes"}


@pytest.mark.golden
def test_all_100_oracle_tolerances(oracle_data):
    """
    Evaluates all 100 benchmark charts against hard mathematical tolerance gates.
    Collects and asserts discrepancies across Grahas, Lagna, Cusps, Dashas, Ashtakavarga, and Jaimini.
    """
    benchmarks = oracle_data["benchmarks"]
    calc = ChartCalculator(SwissEphemerisProvider())

    max_planet_err = 0.0
    max_lagna_err = 0.0
    max_cusp_err = 0.0
    max_dasha_err = 0.0

    for case_id, b_entry in benchmarks.items():
        inp = b_entry["input"]
        dt_d = datetime.strptime(inp["birth_date"], "%Y-%m-%d").date()
        dt_t = datetime.strptime(inp["birth_time"], "%H:%M:%S").time()

        b_obj = BirthData(
            name=inp["name"],
            birth_date=dt_d,
            birth_time=dt_t,
            latitude=inp["latitude"],
            longitude=inp["longitude"],
            timezone=inp["timezone"],
            city=inp["city"],
            fold=inp.get("fold"),
            house_system=inp["house_system"],
            birth_time_confidence="exact"
        )

        chart = calc.calculate_full_chart(b_obj, house_system=inp["house_system"])

        # 1. Check Lagna Tolerance (<= 1 arcmin = 0.016667 deg)
        exp_lagna = b_entry["lagna"]
        lagna_diff = abs(chart.lagna_longitude - exp_lagna["longitude"])
        if lagna_diff > 180.0:
            lagna_diff = 360.0 - lagna_diff
        max_lagna_err = max(max_lagna_err, lagna_diff)
        assert lagna_diff < 0.0167, f"{case_id}: Lagna error {lagna_diff:.6f}° exceeds 1 arcmin"
        assert chart.lagna_sign_id == exp_lagna["sign_id"], f"{case_id}: Lagna sign mismatch"

        # 2. Check Planetary Tolerances (<= 0.001 deg)
        exp_planets = b_entry["planets"]
        for p_name, exp_p in exp_planets.items():
            calc_p = chart.planets[p_name]
            p_diff = abs(calc_p.longitude - exp_p["longitude"])
            if p_diff > 180.0:
                p_diff = 360.0 - p_diff
            max_planet_err = max(max_planet_err, p_diff)
            assert p_diff < 0.001, f"{case_id} {p_name}: Planet longitude error {p_diff:.6f}° exceeds 0.001°"
            assert calc_p.sign_id == exp_p["sign_id"], f"{case_id} {p_name}: Sign ID mismatch"
            assert calc_p.is_retrograde == exp_p["is_retrograde"], f"{case_id} {p_name}: Retrograde state mismatch"
            assert calc_p.is_combust == exp_p["is_combust"], f"{case_id} {p_name}: Combustion state mismatch"

        # 3. Check House Cusps (<= 1 arcmin = 0.016667 deg)
        exp_houses = b_entry["houses"]
        for h_idx, exp_h in enumerate(exp_houses):
            calc_h = chart.houses[h_idx]
            c_diff = abs(calc_h.cusp_longitude - exp_h["cusp_longitude"])
            if c_diff > 180.0:
                c_diff = 360.0 - c_diff
            max_cusp_err = max(max_cusp_err, c_diff)
            assert c_diff < 0.0167, f"{case_id} House {h_idx+1}: Cusp error {c_diff:.6f}° exceeds 1 arcmin"

        # 4. Check Ashtakavarga (0 error, exact SAV sum == 337)
        av = AshtakavargaCalculator.calculate(chart)
        assert av.total_bindus == 337, f"{case_id}: SAV sum {av.total_bindus} != 337"
        assert av.sav == b_entry["ashtakavarga"]["sav_signs"], f"{case_id}: SAV sign array mismatch"

        # 5. Check Jaimini Chara Karakas (0 ordering error)
        jaimini = default_jaimini_calculator.calculate(chart)
        assert jaimini.karakas_7 == b_entry["jaimini"]["chara_karakas_7"], f"{case_id}: Jaimini Chara Karakas ordering mismatch"
        assert jaimini.karakamsha_sign_name == b_entry["jaimini"]["karakamsha_sign_name"], f"{case_id}: Karakamsha mismatch"

        # 6. Check Vimshottari Dasha Balance (<= 0.0001 years = 0.88 hours)
        moon_lon = chart.planets["Moon"].longitude
        b_lord, _, b_years = default_dasha_engine.calculate_birth_balance(moon_lon)
        exp_dasha = b_entry["dasha_balance"]
        assert b_lord == exp_dasha["lord"], f"{case_id}: Dasha balance lord mismatch ({b_lord} != {exp_dasha['lord']})"
        d_diff = abs(b_years - exp_dasha["balance_years"])
        max_dasha_err = max(max_dasha_err, d_diff)
        assert d_diff < 0.0001, f"{case_id}: Dasha balance diff {d_diff:.6f} years exceeds 0.0001 years"

    print("\n--- 100-Chart Oracle Tolerances Verified ---")
    print(f"Max Planet Discrepancy: {max_planet_err * 3600.0:.3f} arcsec ({max_planet_err:.6f}°)")
    print(f"Max Lagna Discrepancy:  {max_lagna_err * 60.0:.3f} arcmin ({max_lagna_err:.6f}°)")
    print(f"Max Cusp Discrepancy:   {max_cusp_err * 60.0:.3f} arcmin ({max_cusp_err:.6f}°)")
    print(f"Max Dasha Discrepancy:  {max_dasha_err * 8766.0:.2f} hours ({max_dasha_err:.7f} years)")
    print(f"Ashtakavarga Invariant: SAV == 337 (100/100 verified)")
    print(f"Jaimini 7 Karakas:      0 ordering inversions (100/100 verified)")
