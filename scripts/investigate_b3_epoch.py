"""
Investigation Script for PRD Finding B3 / Task P1-T4:
Measures sidereal longitude discrepancy between PyEphem and Swiss Ephemeris
across 20 sample dates between 1950 and 2050 for Sun, Moon, and Jupiter.
"""

import os
import sys
import datetime
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.jyotish.core.ephemeris import PyEphemProvider, SwissEphemerisProvider


def run_investigation() -> Dict[str, Any]:
    py_prov = PyEphemProvider()
    sw_prov = SwissEphemerisProvider()

    dates = [
        datetime.datetime(year, month, day, 12, 0, tzinfo=datetime.timezone.utc)
        for year, month, day in [
            (1950, 1, 15), (1955, 7, 20), (1960, 3, 10), (1965, 11, 5),
            (1970, 8, 25), (1975, 4, 14), (1980, 12, 30), (1985, 9, 18),
            (1990, 5, 2),  (1995, 2, 28), (2000, 1, 1),   (2005, 6, 21),
            (2010, 10, 10),(2015, 4, 1),  (2020, 8, 15),  (2025, 1, 1),
            (2030, 7, 4),  (2035, 12, 25),(2040, 5, 15),  (2045, 9, 30),
            (2050, 11, 11)
        ]
    ]

    records = []
    max_sun_err = 0.0
    max_moon_err = 0.0
    max_jup_err = 0.0

    print("=" * 80)
    print("B3 EPOCH ERROR INVESTIGATION: PyEphem vs Swiss Ephemeris (1950 - 2050 CE)")
    print("=" * 80)
    header = f"{'Date (UTC)':12} | {'Sun Err (deg)':14} | {'Moon Err (deg)':15} | {'Jupiter Err (deg)':17} | {'Verdict'}"
    print(header)
    print("-" * 80)

    for dt in dates:
        p_py, _ = py_prov.get_planet_positions(dt, ayanamsa_name="Lahiri")
        p_sw, _ = sw_prov.get_planet_positions(dt, ayanamsa_name="Lahiri")

        def diff_deg(d1: float, d2: float) -> float:
            d = abs(d1 - d2) % 360.0
            return 360.0 - d if d > 180.0 else d

        err_sun = diff_deg(p_py["Sun"]["longitude"], p_sw["Sun"]["longitude"])
        err_moon = diff_deg(p_py["Moon"]["longitude"], p_sw["Moon"]["longitude"])
        err_jup = diff_deg(p_py["Jupiter"]["longitude"], p_sw["Jupiter"]["longitude"])

        if err_sun > max_sun_err:
            max_sun_err = err_sun
        if err_moon > max_moon_err:
            max_moon_err = err_moon
        if err_jup > max_jup_err:
            max_jup_err = err_jup

        verdict = "EXCESSIVE (>0.02 deg)" if (err_sun > 0.02 or err_jup > 0.02 or err_moon > 0.05) else "Tolerable"

        row = {
            "date": dt.strftime("%Y-%m-%d"),
            "sun_error_deg": round(err_sun, 6),
            "moon_error_deg": round(err_moon, 6),
            "jupiter_error_deg": round(err_jup, 6),
            "verdict": verdict,
        }
        records.append(row)
        print(f"{row['date']:12} | {err_sun:14.6f} | {err_moon:15.6f} | {err_jup:17.6f} | {verdict}")

    print("-" * 80)
    print(f"Max Sun Error:     {max_sun_err:.6f} deg ({max_sun_err * 3600:.1f} arcsec)")
    print(f"Max Moon Error:    {max_moon_err:.6f} deg ({max_moon_err * 3600:.1f} arcsec)")
    print(f"Max Jupiter Error: {max_jup_err:.6f} deg ({max_jup_err * 3600:.1f} arcsec)")
    print("=" * 80)

    # Architectural declaration as per PRD P1-T4
    pyephem_supported = max_sun_err <= 0.02 and max_moon_err <= 0.05 and max_jup_err <= 0.02

    return {
        "records": records,
        "max_sun_error_deg": max_sun_err,
        "max_moon_error_deg": max_moon_err,
        "max_jupiter_error_deg": max_jup_err,
        "pyephem_supported": pyephem_supported,
    }


if __name__ == "__main__":
    res = run_investigation()
    if not res["pyephem_supported"]:
        print("\n[CONCLUSION]: Discrepancy > 0.02 deg found.")
        print("As required by PRD P1-T4, the PyEphem standalone path is formally declared UNSUPPORTED for professional Jyotish.")
        print("It is restricted strictly to emergency degraded fallback with explicit user warning.")
