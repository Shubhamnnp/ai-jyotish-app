"""
Krishnamurti Paddhati (KP System) Core Engine for JyotishOS.
Calculates:
1. Complete 249 Sub-Lords Table based on Vimshottari dasha proportions.
2. Planet Positions with Sign Lord, Star Lord, Sub Lord, Sub-Sub Lord.
3. Cuspal Placements (12 Cusps) with Sign Lord, Star Lord, Sub Lord, Sub-Sub Lord.
4. Ruling Planets (RP) at birth or query moment.
5. 1-249 KP Horary Number Resolver.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from .constants import SIGN_NAMES, SIGN_LORDS, NAKSHATRAS, NAKSHATRA_NAMES, VIMSHOTTARI_DASHAS
from .models import KundaliChart, PlanetPosition


# Planetary Vimshottari years
DASHA_YEARS = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0
}

PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


class KPEngine:
    """KP Astrology calculations: 249 sub divisions, cuspal sub-lords, ruling planets."""

    _kp_249_table: List[Dict[str, Any]] = []

    @classmethod
    def _build_249_table(cls):
        """Pre-computes the 249 KP sub divisions table."""
        if cls._kp_249_table:
            return

        table = []
        num = 1
        nak_span = 360.0 / 27.0  # 13.33333333 deg

        for nak_idx in range(27):
            nak_name = NAKSHATRA_NAMES[nak_idx]
            star_lord = NAKSHATRAS[nak_idx]["lord"]
            start_lord_idx = PLANET_ORDER.index(star_lord)

            nak_start_lon = nak_idx * nak_span

            # Sub divisions in this nakshatra
            curr_sub_start = nak_start_lon

            for s_i in range(9):
                sub_lord = PLANET_ORDER[(start_lord_idx + s_i) % 9]
                sub_span = (nak_span * DASHA_YEARS[sub_lord]) / 120.0
                curr_sub_end = curr_sub_start + sub_span

                # Check if this sub crosses a sign boundary (multiple of 30 deg)
                sign_boundary = (int(curr_sub_start // 30.0) + 1) * 30.0

                if curr_sub_start < sign_boundary < curr_sub_end:
                    # Split into two entries
                    # Part 1
                    s_id1 = int(curr_sub_start // 30.0) + 1
                    table.append({
                        "number": num,
                        "sign_id": s_id1,
                        "sign_name": SIGN_NAMES[s_id1 - 1],
                        "sign_lord": SIGN_LORDS[SIGN_NAMES[s_id1 - 1]],
                        "nakshatra": nak_name,
                        "star_lord": star_lord,
                        "sub_lord": sub_lord,
                        "start_deg": curr_sub_start % 30.0,
                        "end_deg": 30.0,
                        "start_lon": curr_sub_start,
                        "end_lon": sign_boundary
                    })
                    num += 1

                    # Part 2
                    s_id2 = int(sign_boundary // 30.0) + 1
                    table.append({
                        "number": num,
                        "sign_id": s_id2,
                        "sign_name": SIGN_NAMES[s_id2 - 1],
                        "sign_lord": SIGN_LORDS[SIGN_NAMES[s_id2 - 1]],
                        "nakshatra": nak_name,
                        "star_lord": star_lord,
                        "sub_lord": sub_lord,
                        "start_deg": 0.0,
                        "end_deg": curr_sub_end % 30.0,
                        "start_lon": sign_boundary,
                        "end_lon": curr_sub_end
                    })
                    num += 1
                else:
                    s_id = int(curr_sub_start // 30.0) + 1
                    table.append({
                        "number": num,
                        "sign_id": s_id,
                        "sign_name": SIGN_NAMES[s_id - 1],
                        "sign_lord": SIGN_LORDS[SIGN_NAMES[s_id - 1]],
                        "nakshatra": nak_name,
                        "star_lord": star_lord,
                        "sub_lord": sub_lord,
                        "start_deg": curr_sub_start % 30.0,
                        "end_deg": curr_sub_end % 30.0 if curr_sub_end % 30.0 != 0 else 30.0,
                        "start_lon": curr_sub_start,
                        "end_lon": curr_sub_end
                    })
                    num += 1

                curr_sub_start = curr_sub_end

        cls._kp_249_table = table

    @classmethod
    def get_sign_star_sub_subsub(cls, lon: float) -> Dict[str, Any]:
        """Given longitude (0-360), returns Sign, Sign Lord, Star, Star Lord, Sub Lord, Sub-Sub Lord."""
        cls._build_249_table()
        norm_lon = lon % 360.0

        sign_id = int(norm_lon // 30.0) + 1
        sign_name = SIGN_NAMES[sign_id - 1]
        sign_lord = SIGN_LORDS[sign_name]

        nak_span = 360.0 / 27.0
        nak_idx = int(norm_lon // nak_span)
        nak_name = NAKSHATRA_NAMES[nak_idx]
        star_lord = NAKSHATRAS[nak_idx]["lord"]

        # Find Sub Lord from 249 table
        sub_lord = "Ketu"
        for row in cls._kp_249_table:
            if row["start_lon"] <= norm_lon < row["end_lon"] or (row["number"] == 249 and norm_lon >= row["start_lon"]):
                sub_lord = row["sub_lord"]
                break

        # Sub-Sub Lord calculation (dividing sub into 9 sub-subs)
        sub_start = 0.0
        sub_end = 360.0
        for row in cls._kp_249_table:
            if row["start_lon"] <= norm_lon < row["end_lon"] or (row["number"] == 249 and norm_lon >= row["start_lon"]):
                sub_start = row["start_lon"]
                sub_end = row["end_lon"]
                break

        sub_total_span = max(0.0001, sub_end - sub_start)
        fraction_in_sub = (norm_lon - sub_start) / sub_total_span

        sub_lord_idx = PLANET_ORDER.index(sub_lord)
        sub_sub_lord = "Ketu"
        cum_frac = 0.0
        for ss_i in range(9):
            p_ss = PLANET_ORDER[(sub_lord_idx + ss_i) % 9]
            weight = DASHA_YEARS[p_ss] / 120.0
            cum_frac += weight
            if fraction_in_sub <= cum_frac:
                sub_sub_lord = p_ss
                break

        return {
            "sign_name": sign_name,
            "sign_lord": sign_lord,
            "sign_degree": norm_lon % 30.0,
            "nakshatra": nak_name,
            "star_lord": star_lord,
            "sub_lord": sub_lord,
            "sub_sub_lord": sub_sub_lord,
            "longitude": norm_lon
        }

    @classmethod
    def calculate_chart_kp(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates complete KP planetary and cuspal details."""
        cls._build_249_table()

        # 1. Planetary KP Significations
        planets_kp = []
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in chart.planets:
                p_obj = chart.planets[p_name]
                kp_info = cls.get_sign_star_sub_subsub(p_obj.longitude)
                deg_str = f"{int(kp_info['sign_degree'])}° {int((kp_info['sign_degree'] % 1) * 60)}' {int(((kp_info['sign_degree'] * 60) % 1) * 60)}\""
                planets_kp.append({
                    "planet": p_name,
                    "sign": kp_info["sign_name"],
                    "degree_formatted": deg_str,
                    "sign_lord": kp_info["sign_lord"],
                    "star_lord": kp_info["star_lord"],
                    "sub_lord": kp_info["sub_lord"],
                    "sub_sub_lord": kp_info["sub_sub_lord"],
                    "motion": "वक्री (R)" if p_obj.is_retrograde else "मार्गी (D)"
                })

        # 2. Cuspal KP Details (12 Houses)
        cusps_kp = []
        for h in range(1, 13):
            # House cusp longitude
            cusp_lon = (chart.lagna_longitude + (h - 1) * 30.0) % 360.0
            kp_c = cls.get_sign_star_sub_subsub(cusp_lon)
            deg_str = f"{int(kp_c['sign_degree'])}° {int((kp_c['sign_degree'] % 1) * 60)}' {int(((kp_c['sign_degree'] * 60) % 1) * 60)}\""
            cusps_kp.append({
                "cusp": f"Cusp #{h} (भाव {h})",
                "sign": kp_c["sign_name"],
                "degree_formatted": deg_str,
                "sign_lord": kp_c["sign_lord"],
                "star_lord": kp_c["star_lord"],
                "sub_lord": kp_c["sub_lord"],
                "sub_sub_lord": kp_c["sub_sub_lord"]
            })

        # 3. Ruling Planets (RP)
        moon_kp = cls.get_sign_star_sub_subsub(chart.planets["Moon"].longitude)
        lagna_kp = cls.get_sign_star_sub_subsub(chart.lagna_longitude)
        vara_name = chart.panchang.vara_name
        vara_lords = {
            "Sunday": "Sun", "Monday": "Moon", "Tuesday": "Mars",
            "Wednesday": "Mercury", "Thursday": "Jupiter", "Friday": "Venus", "Saturday": "Saturn",
            "रविवार": "Sun", "सोमवार": "Moon", "मंगलवार": "Mars",
            "बुधवार": "Mercury", "गुरुवार": "Jupiter", "शुक्रवार": "Venus", "शनिवार": "Saturn"
        }
        day_lord = vara_lords.get(vara_name, "Sun")

        ruling_planets = {
            "day_lord": {"title": "वार स्वामी (Day Lord)", "planet": day_lord},
            "moon_sign_lord": {"title": "चन्द्र राशि स्वामी (Moon Sign Lord)", "planet": moon_kp["sign_lord"]},
            "moon_star_lord": {"title": "चन्द्र नक्षत्र स्वामी (Moon Star Lord)", "planet": moon_kp["star_lord"]},
            "lagna_sign_lord": {"title": "लग्न राशि स्वामी (Lagna Sign Lord)", "planet": lagna_kp["sign_lord"]},
            "lagna_star_lord": {"title": "लग्न नक्षत्र स्वामी (Lagna Star Lord)", "planet": lagna_kp["star_lord"]}
        }

        return {
            "planets_kp": planets_kp,
            "cusps_kp": cusps_kp,
            "ruling_planets": ruling_planets,
            "total_249_divisions": cls._kp_249_table
        }

    @classmethod
    def get_horary_number_detail(cls, number: int) -> Dict[str, Any]:
        """Resolves KP Horary Number (1 to 249)."""
        cls._build_249_table()
        idx = max(1, min(249, number)) - 1
        return cls._kp_249_table[idx]


default_kp_engine = KPEngine()

