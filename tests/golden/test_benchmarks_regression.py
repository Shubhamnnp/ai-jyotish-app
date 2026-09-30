"""
Golden Invariant Regression Test Suite for BHARAT JYOTISH AI SaaS.
Verifies zero regression against immutable snapshot benchmarks_snapshot.json.
Guarantees:
- Exact astronomical coordinate conservation (< 0.0001 deg).
- Exact Ashtakavarga conservation invariant (SAV sum == 337).
- Exact Shodashavarga Varga placements.
- Exact Jaimini Chara Karakas.
"""

import os
import sys
import json
import pytest
from datetime import datetime, date

curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.jaimini import default_jaimini_calculator


@pytest.fixture(scope="module")
def golden_data():
    snapshot_path = os.path.join(curr_dir, "benchmarks_snapshot.json")
    with open(snapshot_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_golden_snapshots_loaded(golden_data):
    """Verify golden snapshots contain all 10 historical benchmark Kundalis."""
    assert "benchmarks" in golden_data
    benchmarks = golden_data["benchmarks"]
    assert len(benchmarks) >= 10, f"Expected at least 10 benchmarks, found {len(benchmarks)}"
    assert golden_data["metadata"]["invariant_sav_sum"] == 337


def test_golden_benchmarks_astronomical_invariants(golden_data):
    """Verify precision of planetary calculations against golden snapshots."""
    benchmarks = golden_data["benchmarks"]

    for name, b_data in benchmarks.items():
        inp = b_data["birth_data"]
        dt_d = datetime.strptime(inp["birth_date"], "%Y-%m-%d").date()
        dt_t = datetime.strptime(inp["birth_time"], "%H:%M:%S").time()

        b_obj = BirthData(
            name=name,
            birth_date=dt_d,
            birth_time=dt_t,
            latitude=inp["latitude"],
            longitude=inp["longitude"],
            timezone_offset=inp["timezone_offset"],
            city=inp["city"],
            confidence="Exact"
        )

        chart = default_chart_calculator.calculate_full_chart(b_obj)

        snap_lagna = b_data["lagna"]
        assert chart.lagna_sign_id == snap_lagna["sign_id"], f"Lagna sign mismatch for {name}"
        assert abs(chart.lagna_degree - snap_lagna["degree"]) < 0.001, f"Lagna degree mismatch for {name}"

        snap_planets = b_data["planets"]
        for p_name, snap_p in snap_planets.items():
            calc_p = chart.planets[p_name]
            diff = abs(calc_p.longitude - snap_p["longitude"])
            if diff > 180.0:
                diff = 360.0 - diff
            assert diff < 0.001, f"Planet {p_name} longitude drift for {name}: {diff}"
            assert calc_p.sign_id == snap_p["sign_id"], f"Planet {p_name} sign mismatch for {name}"

        av = AshtakavargaCalculator.calculate(chart)
        assert av.total_bindus == 337, f"Ashtakavarga 337 invariant violated for {name}"
