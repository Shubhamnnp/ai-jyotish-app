"""
Golden Invariant Snapshot Generator for BHARAT JYOTISH AI SaaS.
Calculates and serializes the exact mathematical baseline state for all 10
historical benchmark Kundalis. These snapshots serve as immutable Golden Invariants
to guarantee Zero Regression across all future migrations and upgrades.
"""

import os
import sys
import json
from datetime import datetime, date, time

# Ensure project root is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.varga import VargaCalculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.shadbala import default_shadbala_calculator
from src.jyotish.core.jaimini import default_jaimini_calculator
from src.jyotish.dasha.vimshottari import default_dasha_engine
from src.jyotish.services.folder_manager import default_folder_manager


def generate_snapshots():
    folders = default_folder_manager.list_folders()
    demo_folder = next(f for f in folders if f["id"] == 100)
    charts = demo_folder["charts"]

    golden_db = {
        "metadata": {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "ephemeris_engine": "PyEphem 4.2.1",
            "ayanamsa": "Lahiri (Chitra Paksha)",
            "benchmark_count": len(charts),
            "invariant_sav_sum": 337
        },
        "benchmarks": {}
    }

    print(f"Generating Golden Invariants for {len(charts)} benchmark Kundalis...")

    for c_entry in charts:
        bd = c_entry["birth_data"]
        dt_d = datetime.strptime(bd["birth_date"], "%Y-%m-%d").date()
        dt_t = datetime.strptime(bd["birth_time"], "%H:%M:%S").time()

        b_obj = BirthData(
            name=bd["name"],
            birth_date=dt_d,
            birth_time=dt_t,
            latitude=bd["latitude"],
            longitude=bd["longitude"],
            timezone_offset=bd["timezone_offset"],
            city=bd["city"],
            confidence="Exact"
        )

        # 1. Full Natal Chart
        chart = default_chart_calculator.calculate_full_chart(b_obj)
        vargas = VargaCalculator.calculate_all_vargas(chart)
        ashtakavarga = AshtakavargaCalculator.calculate(chart)
        shadbala = default_shadbala_calculator.calculate(chart)
        jaimini = default_jaimini_calculator.calculate(chart)

        # Verify SAV invariant
        assert ashtakavarga.total_bindus == 337, f"SAV invariant violated for {b_obj.name}: {ashtakavarga.total_bindus}"

        # 2. Dasha at Birth & Target Date 2027-01-01
        full_dt = datetime.combine(dt_d, dt_t)
        moon_lon = chart.planets["Moon"].longitude
        dasha_birth = default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, dt_d)
        dasha_2027 = default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, date(2027, 1, 1))

        # 3. Structure snapshot data
        planets_dict = {}
        for p_name, pos in chart.planets.items():
            planets_dict[p_name] = {
                "longitude": round(pos.longitude, 6),
                "sign_id": pos.sign_id,
                "sign_name": pos.sign_name,
                "sign_degree": round(pos.sign_degree, 6),
                "house": pos.house_from_lagna,
                "speed": round(pos.speed, 6),
                "is_retrograde": pos.is_retrograde,
                "is_combust": pos.is_combust,
                "nakshatra_name": pos.nakshatra_name,
                "nakshatra_pada": pos.nakshatra_pada,
                "nakshatra_lord": pos.nakshatra_lord,
                "dignity": pos.dignity
            }

        vargas_dict = {}
        for v_code, v_chart in vargas.items():
            vargas_dict[v_code] = {
                "lagna_sign_id": v_chart.lagna_sign_id,
                "lagna_sign_name": v_chart.lagna_sign_name,
                "planets": {
                    pn: {
                        "sign_id": ppos.sign_id,
                        "sign_name": ppos.sign_name,
                        "dignity": ppos.dignity
                    }
                    for pn, ppos in v_chart.planets.items()
                }
            }

        shadbala_dict = {
            "total_rupas": {p: round(v, 4) for p, v in shadbala["total_rupas"].items()},
            "is_strong": shadbala["is_strong"]
        }

        ashtakavarga_dict = {
            "total_bindus": ashtakavarga.total_bindus,
            "sav_points": ashtakavarga.sarvashtakavarga,
            "bav_totals": ashtakavarga.bhavashtakavarga_totals
        }

        jaimini_dict = {
            "chara_karakas": jaimini["chara_karakas"],
            "karakamsha_sign": jaimini["karakamsha_sign"],
            "arudha_lagna": jaimini["arudha_lagna"],
            "upapada_lagna": jaimini["upapada_lagna"]
        }

        panchang_dict = {
            "tithi_name": chart.panchang.tithi_name,
            "vara_name": chart.panchang.vara_name,
            "nakshatra_name": chart.panchang.nakshatra_name,
            "yoga_name": chart.panchang.yoga_name,
            "karana_name": chart.panchang.karana_name
        }

        golden_db["benchmarks"][b_obj.name] = {
            "birth_data": {
                "birth_date": bd["birth_date"],
                "birth_time": bd["birth_time"],
                "latitude": bd["latitude"],
                "longitude": bd["longitude"],
                "timezone_offset": bd["timezone_offset"],
                "city": bd["city"]
            },
            "lagna": {
                "sign_id": chart.lagna_sign_id,
                "sign_name": chart.lagna_sign_name,
                "degree": round(chart.lagna_degree, 6),
                "longitude": round(chart.lagna_longitude, 6)
            },
            "planets": planets_dict,
            "vargas": vargas_dict,
            "ashtakavarga": ashtakavarga_dict,
            "shadbala": shadbala_dict,
            "jaimini": jaimini_dict,
            "panchang": panchang_dict,
            "dasha_birth": {
                "mahadasha": dasha_birth.mahadasha.lord,
                "antardasha": dasha_birth.antardasha.lord,
                "pratyantardasha": dasha_birth.pratyantardasha.lord
            },
            "dasha_2027": {
                "mahadasha": dasha_2027.mahadasha.lord,
                "antardasha": dasha_2027.antardasha.lord,
                "pratyantardasha": dasha_2027.pratyantardasha.lord
            }
        }
        print(f"  ✓ {b_obj.name}: Lagna {chart.lagna_sign_name}, Moon in {chart.planets['Moon'].sign_name}, SAV={ashtakavarga.total_bindus}")

    out_file = os.path.join(curr_dir, "benchmarks_snapshot.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(golden_db, f, ensure_ascii=False, indent=2)

    print(f"\nSuccessfully generated and saved {out_file} (Size: {os.path.getsize(out_file):,} bytes)!")


if __name__ == "__main__":
    generate_snapshots()
