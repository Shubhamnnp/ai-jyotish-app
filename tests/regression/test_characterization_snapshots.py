"""
Characterization Snapshot Regression Harness (Phase U0, Task U0-T3).

Rules & Requirements:
1. Characterization test (NOT oracle): Captures existing system behaviour to detect any regression.
2. Two tiers:
   - Quick: 3 diverse profiles executed in 'make verify' (sub-second runtime).
   - Full: All 15 profiles decorated with @pytest.mark.slow (pre-merge gate).
3. Non-deterministic fields excluded (no timestamps, UUIDs, cache hashes).
4. Float tolerances applied (1e-4 degrees on planetary longitudes, 0.01 on rupas/years).
5. Strict engine mode guard: If engine_mode differs from snapshot ("SwissEph (precise)"),
   fails immediately with a clear error without silent cross-engine comparison.
"""

import json
import os
import pytest
from datetime import date, time

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.dasha.vimshottari import default_dasha_engine

SNAPSHOT_FILE = os.path.join(
    os.path.dirname(__file__), "snapshots", "characterization_15_profiles.json"
)

with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
    _SNAPSHOT_DATA = json.load(f)

METADATA = _SNAPSHOT_DATA["metadata"]
ALL_PROFILES = _SNAPSHOT_DATA["profiles"]
QUICK_PROFILES = [p for p in ALL_PROFILES if p.get("tier") == "quick"]


def get_current_engine_mode() -> str:
    prov = default_chart_calculator.provider
    is_deg = getattr(prov, "is_degraded", False)
    if callable(is_deg):
        is_deg = is_deg()
    has_swe = getattr(prov, "_has_swisseph", False)
    return "SwissEph (precise)" if has_swe and not is_deg else "PyEphem (degraded)"


def _execute_and_verify(profile_entry: dict):
    # 1. Strict Engine Mode Verification
    current_mode = get_current_engine_mode()
    expected_mode = METADATA["engine_mode"]
    if current_mode != expected_mode:
        pytest.fail(
            f"CHARACTERIZATION ENGINE MISMATCH: Snapshot was captured using '{expected_mode}', "
            f"but active runtime engine is '{current_mode}'. Refusing to compare across differing engines!"
        )

    # 2. Re-execute live calculation (Real compute, NOT static comparison)
    p_info = profile_entry["profile"]
    b_d = date.fromisoformat(p_info["birth_date"])
    t_parts = [int(x) for x in p_info["birth_time"].split(":")]
    b_t = time(t_parts[0], t_parts[1], t_parts[2])

    bdata = BirthData(
        name=p_info["name"],
        birth_date=b_d,
        birth_time=b_t,
        latitude=p_info["latitude"],
        longitude=p_info["longitude"],
        timezone=p_info["timezone"],
        timezone_offset=p_info["timezone_offset"]
    )

    chart = default_chart_calculator.calculate_full_chart(
        bdata, ayanamsa_name="Lahiri", house_system="Whole Sign", use_cache=False
    )
    expected = profile_entry["expected"]

    # 3. Assert Lagna (within 1e-4 degrees)
    assert chart.lagna_sign_id == expected["lagna_sign_id"]
    assert chart.lagna_sign_name == expected["lagna_sign_name"]
    assert chart.lagna_longitude == pytest.approx(expected["lagna_longitude"], abs=1e-4)

    # 4. Assert Planets (Longitudes & Retrograde motion)
    for pname, exp_p in expected["planets"].items():
        actual_p = chart.planets[pname]
        assert actual_p.sign_id == exp_p["sign_id"], f"{pname} sign mismatch in {profile_entry['id']}"
        assert actual_p.is_retrograde == exp_p["is_retrograde"], f"{pname} retrograde mismatch in {profile_entry['id']}"
        assert actual_p.longitude == pytest.approx(exp_p["longitude"], abs=1e-4), (
            f"{pname} longitude drifted > 1e-4 deg in {profile_entry['id']}"
        )

    # 5. Assert House Cusps
    for h_idx, exp_cusp in enumerate(expected["house_cusps"]):
        assert chart.houses[h_idx].cusp_longitude == pytest.approx(exp_cusp, abs=1e-4)

    # 6. Assert Divisional Chart Signs (D9 Navamsha & D60 Shashtiamsha)
    for pname, exp_sign in expected["d9_signs"].items():
        assert chart.vargas["D9"].planets[pname].sign_id == exp_sign
    for pname, exp_sign in expected["d60_signs"].items():
        assert chart.vargas["D60"].planets[pname].sign_id == exp_sign

    # 7. Assert Ashtakavarga (SAV points and invariant sum = 337)
    assert chart.ashtakavarga.sav == expected["sav"]
    assert chart.ashtakavarga.total_bindus == expected["sav_total"]
    assert sum(chart.ashtakavarga.sav) == 337

    # 8. Assert 6-Fold Shadbala Rupas (within 0.01 Rupas)
    for pname, exp_rupas in expected["shadbala_rupas"].items():
        actual_rupas = chart.shadbala.planets[pname].total_rupas
        assert actual_rupas == pytest.approx(exp_rupas, abs=0.01), (
            f"Shadbala rupas for {pname} drifted > 0.01 in {profile_entry['id']}"
        )

    # 9. Assert Jaimini 7 Chara Karakas & Arudha Padas
    assert chart.jaimini.karakas_7 == expected["chara_karakas"]
    assert chart.jaimini.arudha_padas == expected["arudha_padas"]

    # 10. Assert Upagrahas (Mandi & Gulika longitudes within 1e-4 degrees)
    assert chart.upagrahas.mandi_longitude == pytest.approx(expected["upagrahas"]["mandi_longitude"], abs=1e-4)
    assert chart.upagrahas.gulika_longitude == pytest.approx(expected["upagrahas"]["gulika_longitude"], abs=1e-4)

    # 11. Assert Vimshottari Birth Dasha Balance
    bal = default_dasha_engine.calculate_birth_balance(chart.planets["Moon"].longitude)
    assert bal[0] == expected["vimshottari_balance"]["lord"]
    assert bal[2] == pytest.approx(expected["vimshottari_balance"]["remaining_years"], abs=0.01)


# --- Tier 1: Quick Regression (Included in make verify, 3 charts, sub-second) ---
@pytest.mark.parametrize("profile_entry", QUICK_PROFILES, ids=[p["id"] for p in QUICK_PROFILES])
def test_characterization_quick(profile_entry):
    """Tier 1 Characterization: Evaluates 3 diverse charts in real-time within fast CI gate."""
    _execute_and_verify(profile_entry)


# --- Tier 2: Full Regression (Pre-merge gate, all 15 diverse astronomical profiles) ---
@pytest.mark.slow
@pytest.mark.parametrize("profile_entry", ALL_PROFILES, ids=[p["id"] for p in ALL_PROFILES])
def test_characterization_full(profile_entry):
    """Tier 2 Characterization: Evaluates all 15 diverse astronomical profiles across full spectrum."""
    _execute_and_verify(profile_entry)
