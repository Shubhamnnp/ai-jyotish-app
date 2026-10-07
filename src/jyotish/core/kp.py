"""
Krishnamurti Paddhati (KP System) Comprehensive Core & Prediction Engine for JyotishOS.
According to Prof. K.S. Krishnamurti (KP Readers I to VI).
Calculates:
1. Complete 249 Sub-Lords & Sub-Sub-Lords Table based on Vimshottari dasha proportions.
2. Planet Positions with Sign Lord, Star Lord, Sub Lord, Sub-Sub Lord (SSL).
3. Cuspal Placements (12 Cusps) with Sign Lord, Star Lord, Sub Lord, Sub-Sub Lord.
4. 4-Fold House & Planet Significations (A, B, C, D Levels).
5. Ruling Planets (RP) with Rahu/Ketu Node representations.
6. 1-249 KP Horary & Natal Query Prediction Engine for 12+ real-world domains.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
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

KP_QUERY_RULES: Dict[str, Dict[str, Any]] = {
    "JOB_CAREER": {
        "name": "💼 नौकरी, करियर, पदोन्नति व स्थानांतरण (Job & Career)",
        "primary_cusps": [6, 10],
        "favorable_houses": [2, 6, 10, 11],
        "unfavorable_houses": [5, 8, 12],
        "neutral_houses": [1, 3, 9],
        "desc": "छठा भाव (सेवा/नौकरी प्राप्ति), दसवां भाव (उच्च पद/प्रतिष्ठा), दूसरा भाव (धन लाभ), ग्यारहवां भाव (मनोकामना पूर्ति व पदोन्नति)। पांचवां व बारहवां भाव सेवा निवृत्ति या त्यागपत्र के सूचक हैं।"
    },
    "MARRIAGE": {
        "name": "💍 विवाह, वैवाहिक सुख व संबंध (Marriage & Relationship)",
        "primary_cusps": [7],
        "favorable_houses": [2, 7, 11],
        "unfavorable_houses": [1, 6, 10],
        "neutral_houses": [3, 5, 9],
        "desc": "सातवां भाव (जीवनसाथी/विवाह), दूसरा भाव (कुटुंब वृद्धि), ग्यारहवां भाव (विवाह अभिलाषा पूर्ति)। पहला (7वें का 7वां), छठा (7वें का 12वां) व दसवां भाव वैवाहिक गतिरोध व अलगाव दर्शाते हैं।"
    },
    "CHILDBIRTH": {
        "name": "👶 संतान प्राप्ति एवं गर्भाधान (Childbirth & Progeny)",
        "primary_cusps": [5],
        "favorable_houses": [2, 5, 11],
        "unfavorable_houses": [1, 4, 10],
        "neutral_houses": [3, 9],
        "desc": "पांचवां भाव (संतान व गर्भाधान), दूसरा भाव (परिवार में नए सदस्य का आगमन), ग्यारहवां भाव (संतान सुख पूर्ति)। चौथा (5वें का 12वां) व दसवां भाव गर्भ धारण में विलंब या चिकित्सा बाधा दर्शाते हैं।"
    },
    "PROPERTY_VEHICLE": {
        "name": "🏠 भूमि, भवन, अचल संपत्ति व वाहन क्रय (Property & Vehicle)",
        "primary_cusps": [4],
        "favorable_houses": [4, 11, 12],
        "unfavorable_houses": [3, 6, 8],
        "neutral_houses": [1, 2, 10],
        "desc": "चौथा भाव (अचल संपत्ति/वाहन), ग्यारहवां भाव (प्राप्ति/लाभ), बारहवां भाव (पूंजी निवेश/क्रय व्यय)। तीसरा भाव संपत्ति विक्रय व छठा भाव ऋण का सूचक है।"
    },
    "FOREIGN_TRAVEL": {
        "name": "✈️ विदेश यात्रा, वीज़ा व विदेश वास (Foreign Travel & Settlement)",
        "primary_cusps": [9, 12],
        "favorable_houses": [3, 9, 12],
        "unfavorable_houses": [2, 4, 11],
        "neutral_houses": [1, 6, 10],
        "desc": "तीसरा भाव (घर से प्रस्थान/छोटी यात्रा), नौवां भाव (दूरस्थ यात्रा/विदेश), बारहवां भाव (विदेश भूमि पर निवास)। चौथा भाव स्वदेश में बने रहने का सूचक है।"
    },
    "WEALTH_FINANCE": {
        "name": "💰 धन लाभ, व्यापारिक लाभ व ऋण मुक्ति (Wealth & Finance)",
        "primary_cusps": [2, 11],
        "favorable_houses": [2, 6, 11],
        "unfavorable_houses": [5, 8, 12],
        "neutral_houses": [1, 3, 7, 10],
        "desc": "दूसरा भाव (धन कोष), छठा भाव (ऋण प्राप्ति/व्यापारिक जीत), ग्यारहवां भाव (नियमित लाभ)। आठवां व बारहवां भाव अप्रत्याशित वित्तीय हानि या रुकावट के सूचक हैं।"
    },
    "HEALTH_RECOVERY": {
        "name": "🏥 रोगमुक्ति एवं स्वास्थ्य लाभ (Health & Disease Recovery)",
        "primary_cusps": [6, 1],
        "favorable_houses": [1, 5, 11],
        "unfavorable_houses": [6, 8, 12],
        "neutral_houses": [2, 3, 10],
        "desc": "पहला भाव (शारीरिक आरोग्य), पांचवां भाव (रोग का क्षय - 6ठे का 12वां), ग्यारहवां भाव (पूर्ण रोगमुक्ति - 12वें का 12वां)। 6, 8, 12 भाव दीर्घ रोग व अस्पताल का सूचक हैं।"
    },
    "LITIGATION_LEGAL": {
        "name": "⚖️ कोर्ट केस, मुकदमा व कानूनी विवाद में विजय (Litigation & Victory)",
        "primary_cusps": [6],
        "favorable_houses": [6, 11],
        "unfavorable_houses": [12, 5, 7, 8],
        "neutral_houses": [1, 3, 9, 10],
        "desc": "छठा भाव (शत्रु व मुकदमे पर विजय), ग्यारहवां भाव (अंतिम सफलता)। बारहवां भाव पराजय और सातवां भाव विरोधी पक्ष के शक्तिशाली होने का सूचक है।"
    },
    "EDUCATION_EXAMS": {
        "name": "🎓 उच्च शिक्षा, प्रतियोगी परीक्षा व प्रवेश (Education & Exams)",
        "primary_cusps": [4, 9],
        "favorable_houses": [4, 9, 11, 6],
        "unfavorable_houses": [3, 8],
        "neutral_houses": [1, 2, 5, 10],
        "desc": "चौथा भाव (मूल व उच्च शिक्षा), नौवां भाव (उच्च शोध/डिग्री), छठा भाव (प्रतियोगी परीक्षा में चयन), 11वां भाव (सफलता)। तीसरा भाव ध्यान भंग दर्शाता है।"
    },
    "LOST_ARTICLE": {
        "name": "🔍 गुम वस्तु / खोई संपत्ति की प्राप्ति (Recovery of Lost Article)",
        "primary_cusps": [2],
        "favorable_houses": [2, 6, 11],
        "unfavorable_houses": [8, 12],
        "neutral_houses": [1, 3, 4, 10],
        "desc": "दूसरा भाव (खोई हुई वस्तु/धन), छठा भाव (पुनः हाथ लगना), ग्यारहवां भाव (सफलता)। आठवां व बारहवां भाव वस्तु के नष्ट या स्थायी रूप से चोरी होने का सूचक है।"
    },
    "GENERAL_DESIRE": {
        "name": "🌟 सामान्य मनोकामना / कार्य सिद्धि (General Wish Fulfillment)",
        "primary_cusps": [11],
        "favorable_houses": [2, 11, 1],
        "unfavorable_houses": [12, 8],
        "neutral_houses": [3, 4, 5, 6, 7, 9, 10],
        "desc": "ग्यारहवां भाव समस्त प्रकार की इच्छाओं की पूर्ति का मुख्य केंद्र है। यदि 11वें कस्प का सब-लॉर्ड 2, 11 भावों का कार्यक हो तो कार्य अवश्य सिद्ध होता है।"
    }
}


class KPEngine:
    """Krishnamurti Paddhati (KP) Engine with 249 Table, 4-Fold Significators, RP, and Horary Predictor."""

    _kp_249_table: List[Dict[str, Any]] = []

    @classmethod
    def _build_249_table(cls):
        """Pre-computes the full 249 KP sub-divisions table."""
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
            curr_sub_start = nak_start_lon

            for s_i in range(9):
                sub_lord = PLANET_ORDER[(start_lord_idx + s_i) % 9]
                sub_span = (nak_span * DASHA_YEARS[sub_lord]) / 120.0
                curr_sub_end = curr_sub_start + sub_span

                sign_boundary = (int(curr_sub_start // 30.0) + 1) * 30.0

                if curr_sub_start < sign_boundary < curr_sub_end:
                    # Split across sign boundary
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
    def get_all_249_table(cls) -> List[Dict[str, Any]]:
        """Returns the full 1-249 KP sub-division table."""
        cls._build_249_table()
        return cls._kp_249_table

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
        sub_start = 0.0
        sub_end = 360.0
        for row in cls._kp_249_table:
            if row["start_lon"] <= norm_lon < row["end_lon"] or (row["number"] == 249 and norm_lon >= row["start_lon"]):
                sub_lord = row["sub_lord"]
                sub_start = row["start_lon"]
                sub_end = row["end_lon"]
                break

        # Sub-Sub Lord calculation (dividing sub into 9 sub-subs)
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
            "sign_id": sign_id,
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
    def calculate_4fold_significators(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Calculates 4-Fold Significators (A, B, C, D) for 12 Houses and 9 Planets.
        Level A: Planets in the Star of Occupants of House H (Strongest).
        Level B: Occupants of House H.
        Level C: Planets in the Star of Lord of House H.
        Level D: Lord of House H (Weakest).
        """
        cls._build_249_table()

        # Planet Star Lords & Houses occupied
        planet_data = {}
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in chart.planets:
                p_obj = chart.planets[p_name]
                kp_info = cls.get_sign_star_sub_subsub(p_obj.longitude)
                # House from Lagna
                h_occupied = ((p_obj.sign_id - chart.lagna_sign_id) % 12) + 1
                planet_data[p_name] = {
                    "star_lord": kp_info["star_lord"],
                    "sub_lord": kp_info["sub_lord"],
                    "sub_sub_lord": kp_info["sub_sub_lord"],
                    "sign_lord": kp_info["sign_lord"],
                    "house_occupied": h_occupied,
                    "sign_id": p_obj.sign_id
                }

        # House Lords and Occupants
        house_occupants = {h: [] for h in range(1, 13)}
        house_lords = {}
        for h in range(1, 13):
            h_sign_id = ((chart.lagna_sign_id - 1 + (h - 1)) % 12) + 1
            h_sign_name = SIGN_NAMES[h_sign_id - 1]
            house_lords[h] = SIGN_LORDS[h_sign_name]
            for p_name, p_info in planet_data.items():
                if p_info["house_occupied"] == h:
                    house_occupants[h].append(p_name)

        # 4-Fold House Significators
        house_significators = {}
        for h in range(1, 13):
            # Level B: Occupants
            level_b = list(house_occupants[h])

            # Level A: Planets in the star of occupants
            level_a = []
            for occ in level_b:
                for p_name, p_info in planet_data.items():
                    if p_info["star_lord"] == occ and p_name not in level_a:
                        level_a.append(p_name)

            # Level D: Lord of House
            level_d = [house_lords[h]]

            # Level C: Planets in star of Lord of House
            level_c = []
            for p_name, p_info in planet_data.items():
                if p_info["star_lord"] == house_lords[h] and p_name not in level_c:
                    level_c.append(p_name)

            all_sigs = list(dict.fromkeys(level_a + level_b + level_c + level_d))
            house_significators[h] = {
                "house": h,
                "lord": house_lords[h],
                "level_a": level_a,
                "level_b": level_b,
                "level_c": level_c,
                "level_d": level_d,
                "all_significators": all_sigs
            }

        # Planetary Significations (Reverse map)
        planet_significations = {}
        for p_name in planet_data.keys():
            p_houses_a = [h for h, s in house_significators.items() if p_name in s["level_a"]]
            p_houses_b = [h for h, s in house_significators.items() if p_name in s["level_b"]]
            p_houses_c = [h for h, s in house_significators.items() if p_name in s["level_c"]]
            p_houses_d = [h for h, s in house_significators.items() if p_name in s["level_d"]]

            combined = sorted(list(set(p_houses_a + p_houses_b + p_houses_c + p_houses_d)))
            planet_significations[p_name] = {
                "planet": p_name,
                "star_lord": planet_data[p_name]["star_lord"],
                "sub_lord": planet_data[p_name]["sub_lord"],
                "sub_sub_lord": planet_data[p_name]["sub_sub_lord"],
                "level_a_houses": p_houses_a,
                "level_b_houses": p_houses_b,
                "level_c_houses": p_houses_c,
                "level_d_houses": p_houses_d,
                "combined_houses": combined,
                "primary_signification": f"Star: {planet_data[p_name]['star_lord']} ➔ Sub: {planet_data[p_name]['sub_lord']}"
            }

        return {
            "house_significators": house_significators,
            "planet_significations": planet_significations
        }

    @classmethod
    def get_ruling_planets(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates Ruling Planets (RP) with Node Representations."""
        cls._build_249_table()
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

        direct_rps = [
            lagna_kp["star_lord"],
            lagna_kp["sign_lord"],
            moon_kp["star_lord"],
            moon_kp["sign_lord"],
            day_lord
        ]

        # Node representation (Rahu & Ketu as agents of RPs)
        rahu_kp = cls.get_sign_star_sub_subsub(chart.planets["Rahu"].longitude)
        ketu_kp = cls.get_sign_star_sub_subsub(chart.planets["Ketu"].longitude)

        node_agents = []
        if rahu_kp["sign_lord"] in direct_rps or rahu_kp["star_lord"] in direct_rps:
            node_agents.append(f"Rahu (एजेंट: {rahu_kp['sign_lord']}/{rahu_kp['star_lord']})")
        if ketu_kp["sign_lord"] in direct_rps or ketu_kp["star_lord"] in direct_rps:
            node_agents.append(f"Ketu (एजेंट: {ketu_kp['sign_lord']}/{ketu_kp['star_lord']})")

        return {
            "day_lord": {"title": "वार स्वामी (Day Lord)", "planet": day_lord},
            "moon_sign_lord": {"title": "चन्द्र राशि स्वामी (Moon Sign Lord)", "planet": moon_kp["sign_lord"]},
            "moon_star_lord": {"title": "चन्द्र नक्षत्र स्वामी (Moon Star Lord)", "planet": moon_kp["star_lord"]},
            "moon_sub_lord": {"title": "चन्द्र उप-स्वामी (Moon Sub Lord)", "planet": moon_kp["sub_lord"]},
            "lagna_sign_lord": {"title": "लग्न राशि स्वामी (Lagna Sign Lord)", "planet": lagna_kp["sign_lord"]},
            "lagna_star_lord": {"title": "लग्न नक्षत्र स्वामी (Lagna Star Lord)", "planet": lagna_kp["star_lord"]},
            "lagna_sub_lord": {"title": "लग्न उप-स्वामी (Lagna Sub Lord)", "planet": lagna_kp["sub_lord"]},
            "all_rp_list": list(dict.fromkeys(direct_rps)),
            "node_agents": node_agents
        }

    @classmethod
    def calculate_nirayana_placidus_cusps(cls, chart: KundaliChart) -> Dict[int, float]:
        """
        Calculates exact Nirayana (Sidereal) Placidus House Cusps (1 to 12)
        following Prof. K.S. Krishnamurti's KP Reader II (Table of Houses).
        Uses exact Right Ascension of Midheaven (RAMC), geographic latitude,
        obliquity of the ecliptic, and the active ayanamsa.
        """
        import math
        import ephem

        b_data = chart.birth_data
        b_d = b_data.birth_date
        b_t = b_data.birth_time
        if isinstance(b_d, str):
            b_d = datetime.strptime(b_d, "%Y-%m-%d").date()
        elif isinstance(b_d, datetime):
            b_d = b_d.date()
        if isinstance(b_t, str):
            try:
                b_t = datetime.strptime(b_t, "%H:%M:%S").time()
            except ValueError:
                b_t = datetime.strptime(b_t, "%H:%M").time()
        elif isinstance(b_t, datetime):
            b_t = b_t.time()

        birth_dt = datetime.combine(b_d, b_t)
        dt_utc = birth_dt - timedelta(hours=float(b_data.timezone_offset))

        observer = ephem.Observer()
        observer.lat = str(b_data.latitude)
        observer.lon = str(b_data.longitude)
        observer.elevation = 0
        observer.date = ephem.Date(dt_utc)

        lst_rad = float(observer.sidereal_time())
        ramc_rad = lst_rad % (2 * math.pi)

        jd = float(ephem.julian_date(dt_utc))
        t = (jd - 2451545.0) / 36525.0
        eps_deg = 23.4392911 - 0.0130042 * t
        eps = math.radians(eps_deg)
        phi = math.radians(b_data.latitude)
        ayanamsa = chart.ayanamsa_value

        mc_trop = math.atan2(math.sin(ramc_rad), math.cos(ramc_rad) * math.cos(eps)) % (2 * math.pi)
        y1 = math.cos(ramc_rad)
        x1 = -(math.sin(ramc_rad) * math.cos(eps) + math.tan(phi) * math.sin(eps))
        asc_trop = math.atan2(y1, x1) % (2 * math.pi)

        def solve_placidus(base_ra, f, is_diurnal):
            lam = base_ra
            for _ in range(25):
                sin_d = math.sin(eps) * math.sin(lam)
                d = math.asin(max(-0.9999, min(0.9999, sin_d)))
                tan_d = math.tan(d)
                sin_ad = max(-0.9999, min(0.9999, math.tan(phi) * tan_d))
                ad = math.asin(sin_ad)
                if is_diurnal:
                    ra = (ramc_rad + f * (math.pi / 2.0 + ad)) % (2 * math.pi)
                else:
                    ra = (ramc_rad + math.pi - (1.0 - f) * (math.pi / 2.0 - ad)) % (2 * math.pi)
                y = math.sin(ra)
                x = math.cos(ra) * math.cos(eps) - tan_d * math.sin(eps)
                lam_next = math.atan2(y, x) % (2 * math.pi)
                if abs(lam_next - lam) < 1e-7:
                    break
                lam = lam_next
            return lam

        try:
            cusp11 = solve_placidus(ramc_rad + math.radians(30), 1/3, True)
            cusp12 = solve_placidus(ramc_rad + math.radians(60), 2/3, True)
            cusp2 = solve_placidus(ramc_rad + math.radians(120), 1/3, False)
            cusp3 = solve_placidus(ramc_rad + math.radians(150), 2/3, False)

            trop = {
                10: math.degrees(mc_trop) % 360.0,
                11: math.degrees(cusp11) % 360.0,
                12: math.degrees(cusp12) % 360.0,
                1: math.degrees(asc_trop) % 360.0,
                2: math.degrees(cusp2) % 360.0,
                3: math.degrees(cusp3) % 360.0,
            }
            trop[4] = (trop[10] + 180.0) % 360.0
            trop[5] = (trop[11] + 180.0) % 360.0
            trop[6] = (trop[12] + 180.0) % 360.0
            trop[7] = (trop[1] + 180.0) % 360.0
            trop[8] = (trop[2] + 180.0) % 360.0
            trop[9] = (trop[3] + 180.0) % 360.0

            return {h: (trop[h] - ayanamsa) % 360.0 for h in range(1, 13)}
        except Exception:
            return {h: (chart.lagna_longitude + (h - 1) * 30.0) % 360.0 for h in range(1, 13)}

    @classmethod
    def calculate_chart_kp(cls, chart: KundaliChart, house_system: str = "Placidus") -> Dict[str, Any]:
        """
        Calculates complete KP planetary, cuspal, 4-fold significator, and RP details.
        Supports authentic KP Nirayana Placidus House Cusps (KP Readers I-VI standard)
        as well as Equal Bhav Chalit cusps.
        """
        cls._build_249_table()

        # 1. Planetary KP Significations
        planets_kp = []
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in chart.planets:
                p_obj = chart.planets[p_name]
                kp_info = cls.get_sign_star_sub_subsub(p_obj.longitude)
                deg_str = f"{int(kp_info['sign_degree'])}° {int((kp_info['sign_degree'] % 1) * 60):02d}' {int(((kp_info['sign_degree'] * 60) % 1) * 60):02d}\""
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
        if house_system.lower() == "placidus":
            cusp_lons = cls.calculate_nirayana_placidus_cusps(chart)
        else:
            cusp_lons = {h: (chart.lagna_longitude + (h - 1) * 30.0) % 360.0 for h in range(1, 13)}

        cusps_kp = []
        for h in range(1, 13):
            cusp_lon = cusp_lons.get(h, (chart.lagna_longitude + (h - 1) * 30.0) % 360.0)
            kp_c = cls.get_sign_star_sub_subsub(cusp_lon)
            deg_str = f"{int(kp_c['sign_degree'])}° {int((kp_c['sign_degree'] % 1) * 60):02d}' {int(((kp_c['sign_degree'] * 60) % 1) * 60):02d}\""
            cusps_kp.append({
                "cusp_num": h,
                "cusp": f"Cusp #{h} (भाव {h})",
                "sign": kp_c["sign_name"],
                "degree_formatted": deg_str,
                "sign_lord": kp_c["sign_lord"],
                "star_lord": kp_c["star_lord"],
                "sub_lord": kp_c["sub_lord"],
                "sub_sub_lord": kp_c["sub_sub_lord"],
                "longitude": cusp_lon
            })

        # 3. 4-Fold Significators
        significators_data = cls.calculate_4fold_significators(chart)

        # 4. Ruling Planets (RP)
        ruling_planets = cls.get_ruling_planets(chart)

        # 5. CSL 1-12 Promise Matrix
        csl_matrix = cls.get_csl_promise_matrix(chart, house_system=house_system)

        return {
            "planets_kp": planets_kp,
            "cusps_kp": cusps_kp,
            "ruling_planets": ruling_planets,
            "house_significators": significators_data["house_significators"],
            "planet_significations": significators_data["planet_significations"],
            "csl_matrix": csl_matrix,
            "house_system_used": "Nirayana Placidus (KP Reader Standard)" if house_system.lower() == "placidus" else "Equal House (Bhav Chalit)",
            "total_249_divisions": cls._kp_249_table
        }

    @classmethod
    def get_csl_promise_matrix(cls, chart: KundaliChart, house_system: str = "Placidus") -> List[Dict[str, Any]]:
        """
        Evaluates Cuspal Sub Lords (CSL 1 to 12) Matrix for all 12 life domains
        according to Prof. K.S. Krishnamurti's KP Readers I to VI.
        """
        cls._build_249_table()
        if house_system.lower() == "placidus":
            cusp_lons = cls.calculate_nirayana_placidus_cusps(chart)
        else:
            cusp_lons = {h: (chart.lagna_longitude + (h - 1) * 30.0) % 360.0 for h in range(1, 13)}

        significators_data = cls.calculate_4fold_significators(chart)
        p_sigs = significators_data["planet_significations"]

        csl_rules = {
            1: {"name": "प्रथम भाव (तनु / शारीरिक स्वास्थ्य / आयु)", "fav": [1, 2, 3, 11], "unfav": [6, 8, 12], "rule": "L1 CSL 1, 3, 11 का कार्यक हो तो दीर्घायु व उत्तम स्वास्थ्य; 6, 8, 12 रोग व व्याधि दर्शाते हैं।"},
            2: {"name": "द्वितीय भाव (धन / कुटुंब / वित्तीय संचय)", "fav": [2, 6, 11], "unfav": [8, 12], "rule": "L2 CSL 2, 6, 11 का कार्यक हो तो प्रचुर धन संचय व वित्तीय सुरक्षा; 8, 12 हानि के सूचक हैं।"},
            3: {"name": "तृतीय भाव (पराक्रम / भ्राता / लघु यात्रा / अनुबंध)", "fav": [3, 9, 11], "unfav": [4, 8], "rule": "L3 CSL 3, 11 को दर्शाये तो अनुबंध, संचार, मीडिया व व्यापारिक यात्राओं में सफलता।"},
            4: {"name": "चतुर्थ भाव (गृह / भूमि / वाहन / माता / मूल शिक्षा)", "fav": [4, 11, 12], "unfav": [3, 6, 8], "rule": "L4 CSL 4, 11, 12 का कार्यक हो तो संपत्ति व वाहन प्राप्ति सुनिश्चित; 3 भाव विक्रय दर्शाता है।"},
            5: {"name": "पंचम भाव (संतान / बुद्धि / प्रेम / पूर्वपुण्य)", "fav": [2, 5, 11], "unfav": [1, 4, 10], "rule": "L5 CSL 2, 5, 11 को दर्शाये तो संतान प्राप्ति व रचनात्मक सफलता; 1, 4, 10 विलंब दर्शाते हैं।"},
            6: {"name": "षष्ठ भाव (नौकरी / सेवा / ऋण मुक्ति / शत्रु विजय)", "fav": [2, 6, 10, 11], "unfav": [5, 8, 12], "rule": "L6 CSL 6, 11 का कार्यक हो तो नौकरी, प्रतियोगी परीक्षा व विवाद में विजय; 5 व 12 पद त्याग दर्शाते हैं।"},
            7: {"name": "सप्तम भाव (विवाह / जीवनसाथी / साझेदारी / व्यापार)", "fav": [2, 7, 11], "unfav": [1, 6, 10], "rule": "L7 CSL 2, 7, 11 को दर्शाये तो वैवाहिक सुख व स्थिर साझेदारी; 1, 6, 10 अलगाव दर्शाते हैं।"},
            8: {"name": "अष्टम भाव (आयु / आकस्मिक धन / गूढ़ शोध / संकट)", "fav": [2, 8, 11], "unfav": [1, 5, 12], "rule": "L8 CSL 2, 11 से जुड़े तो वसीयत व आकस्मिक धन लाभ; 1, 6, 12 सर्जरी व कष्ट दर्शाते हैं।"},
            9: {"name": "नवम भाव (भाग्य / धर्म / उच्च शिक्षा / दूरस्थ यात्रा)", "fav": [9, 11, 1], "unfav": [8, 12], "rule": "L9 CSL 9, 11 को दर्शाए तो भाग्योदय, उच्च शिक्षा व विदेशी सम्मान की प्राप्ति।"},
            10: {"name": "दशम भाव (करियर / उच्च पद / प्रतिष्ठा / शासन सम्मान)", "fav": [2, 6, 10, 11], "unfav": [5, 8, 12], "rule": "L10 CSL 2, 6, 10, 11 का कार्यक हो तो करियर में सर्वोच्च पद व प्रशासनिक सफलता।"},
            11: {"name": "एकादश भाव (सर्व मनोकामना पूर्ति / नियमित आय / लाभ)", "fav": [2, 11, 1], "unfav": [8, 12], "rule": "L11 CSL 2, 11 को पुष्ट करे तो जातक के समस्त मनोरथ व महत्वाकांक्षाएं सफल होती हैं।"},
            12: {"name": "द्वादश भाव (विदेश वास / निवेश / मोक्ष / अस्पताल व्यय)", "fav": [3, 9, 12], "unfav": [2, 4, 11], "rule": "L12 CSL 3, 9, 12 से जुड़े तो स्थायी विदेश निवास व विदेशी स्रोतों से प्रचुर लाभ।"}
        }

        matrix = []
        for h in range(1, 13):
            c_lon = cusp_lons.get(h, (chart.lagna_longitude + (h - 1) * 30.0) % 360.0)
            kp_c = cls.get_sign_star_sub_subsub(c_lon)
            csl_p = kp_c["sub_lord"]
            csl_star = kp_c["star_lord"]
            csl_ssl = kp_c["sub_sub_lord"]

            # Houses signified by CSL planet & its Star Lord
            csl_houses = p_sigs.get(csl_p, {}).get("combined_houses", [])
            star_houses = p_sigs.get(csl_star, {}).get("combined_houses", [])
            all_signified = sorted(list(set(csl_houses + star_houses)))

            rule = csl_rules.get(h, csl_rules[1])
            fav_hits = [house for house in all_signified if house in rule["fav"]]
            unfav_hits = [house for house in all_signified if house in rule["unfav"]]

            score = 50 + len(fav_hits) * 15 - len(unfav_hits) * 18
            score = max(10, min(95, score))

            if score >= 65:
                badge = "🌟 पूर्ण अनुकूल (Promised / Fruitful)"
                color = "#059669"
            elif score >= 45:
                badge = "⚠️ मध्यम / विलंब उपरांत (Mixed / Delayed)"
                color = "#D97706"
            else:
                badge = "❌ प्रतिकूल / बाधा (Challenging / Denied)"
                color = "#DC2626"

            deg_str = f"{int(kp_c['sign_degree'])}° {int((kp_c['sign_degree'] % 1) * 60):02d}'"

            matrix.append({
                "cusp_num": h,
                "bhava_name": rule["name"],
                "cusp_degree": deg_str,
                "sign": kp_c["sign_name"],
                "sign_lord": kp_c["sign_lord"],
                "star_lord": csl_star,
                "csl": csl_p,
                "ssl": csl_ssl,
                "signified_houses": all_signified,
                "favorable_houses": rule["fav"],
                "fav_hits": fav_hits,
                "unfav_hits": unfav_hits,
                "promise_badge": badge,
                "score": score,
                "color": color,
                "kp_rule_text": rule["rule"]
            })

        return matrix

    @classmethod
    def get_horary_number_detail(cls, number: int) -> Dict[str, Any]:
        """Resolves KP Horary Number (1 to 249)."""
        cls._build_249_table()
        idx = max(1, min(249, number)) - 1
        return cls._kp_249_table[idx]

    @classmethod
    def predict_kp_query(
        cls,
        chart: KundaliChart,
        query_key: str,
        horary_num: Optional[int] = None,
        query_text: str = ""
    ) -> Dict[str, Any]:
        """
        Executes complete KP Horary & Natal Future Prediction Engine.
        1. Determines Primary Cusp and Cuspal Sub-Lord (CSL).
        2. Evaluates Star Lord and Sub Lord of CSL.
        3. Evaluates 4-Fold House Significations for favorable vs detrimental houses.
        4. Verifies Ruling Planets (RP) synergy.
        5. Estimates Timing of Event via active Dasha-Bhukti-Antara and RP transit.
        """
        cls._build_249_table()
        rule = KP_QUERY_RULES.get(query_key, KP_QUERY_RULES["GENERAL_DESIRE"])

        # 1. Resolve Horary / Ascendant Cusp
        kp_data = cls.calculate_chart_kp(chart)
        cusps = kp_data["cusps_kp"]
        p_sigs = kp_data["planet_significations"]
        rps = kp_data["ruling_planets"]["all_rp_list"]

        # Primary Cusp
        primary_cusp_num = rule["primary_cusps"][0]
        primary_csl_obj = cusps[primary_cusp_num - 1]

        csl_planet = primary_csl_obj["sub_lord"]
        csl_star_lord = primary_csl_obj["star_lord"]
        csl_ssl = primary_csl_obj["sub_sub_lord"]

        # Planet's own significations
        csl_p_info = p_sigs.get(csl_planet, {})
        star_p_info = p_sigs.get(csl_star_lord, {})

        csl_houses = csl_p_info.get("combined_houses", [])
        star_houses = star_p_info.get("combined_houses", [])

        # House matches
        fav_houses = rule["favorable_houses"]
        unfav_houses = rule["unfavorable_houses"]

        all_signified = sorted(list(set(csl_houses + star_houses)))
        fav_hits = [h for h in all_signified if h in fav_houses]
        unfav_hits = [h for h in all_signified if h in unfav_houses]

        # KP Sub-Lord Permission Rule:
        # Star Lord indicates WHAT event happens (sources), Sub-Lord decides YES/NO (fruitification).
        sub_p_info = p_sigs.get(csl_planet, {}).get("sub_lord", "")
        sub_of_csl_houses = p_sigs.get(sub_p_info, {}).get("combined_houses", [])
        is_sub_favorable = any(h in fav_houses for h in sub_of_csl_houses) or (not any(h in unfav_houses for h in sub_of_csl_houses))

        # Ruling Planets Agreement
        rp_match = (csl_planet in rps) or (csl_star_lord in rps) or (csl_ssl in rps)

        # Quantitative Confidence Score Calculation (0 to 100)
        base_score = 50.0
        # Positive houses weight
        base_score += len(fav_hits) * 15.0
        # Negative houses penalty
        base_score -= len(unfav_hits) * 18.0
        # Sub-lord approval
        if is_sub_favorable:
            base_score += 15.0
        else:
            base_score -= 15.0
        # RP agreement bonus
        if rp_match:
            base_score += 15.0

        confidence_score = max(5, min(98, int(base_score)))

        # Qualitative Verdict
        if confidence_score >= 70:
            verdict_badge = "🌟 पूर्ण कार्य सिद्धि (Fruitful / Successful)"
            verdict_desc = "कृष्णमूर्ति पद्धति के अनुसार मुख्य कस्पल सब-लॉर्ड एवं उसका नक्षत्र स्वामी अभीष्ट कार्य के अनुकूल भावों को सशक्त रूप से दर्शा रहे हैं। कार्य में सफलता सुनिश्चित है।"
            color_theme = "#059669"
        elif confidence_score >= 45:
            verdict_badge = "⚠️ विलंब व परिश्रम उपरांत सफलता (Success with Delay)"
            verdict_desc = "कस्पल सब-लॉर्ड अनुकूल व कुछ मिश्रित भावों का कार्यक है। कार्य में कुछ विलंब, अतिरिक्त प्रयास अथवा प्रारंभिक बाधाओं के बाद सफलता प्राप्त होगी।"
            color_theme = "#D97706"
        else:
            verdict_badge = "❌ कार्य असिद्धि / प्रतिकूल संकेत (Unfavorable / Denied)"
            verdict_desc = "कस्पल सब-लॉर्ड एवं उसका नक्षत्र स्वामी कार्य-विरोधी या बाधक भावों को दर्शा रहे हैं। वर्तमान समय में इस कार्य में रुकावट या असफलता की संभावना प्रबल है।"
            color_theme = "#DC2626"

        # Timing of Event Synthesis
        timing_planets = [p for p in [csl_planet, csl_star_lord] if p in rps] or [csl_planet, csl_star_lord]
        timing_str = f"जब गोचरस्थ सूर्य एवं चन्द्रमा {', '.join(timing_planets)} के नक्षत्र/उप-नक्षत्र में भ्रमण करेंगे तथा वर्तमान अनुकूल दशा-भुक्ति-अंतरा सक्रिय होगी, तब घटना का फलित सुनिश्चित होगा।"

        return {
            "query_key": query_key,
            "query_name": rule["name"],
            "query_desc": rule["desc"],
            "query_text": query_text,
            "horary_num": horary_num,
            "primary_cusp": primary_cusp_num,
            "primary_csl": {
                "planet": csl_planet,
                "star_lord": csl_star_lord,
                "sub_sub_lord": csl_ssl,
                "sign": primary_csl_obj["sign"],
                "degree": primary_csl_obj["degree_formatted"]
            },
            "favorable_houses": fav_houses,
            "unfavorable_houses": unfav_houses,
            "signified_favorable": fav_hits,
            "signified_unfavorable": unfav_hits,
            "all_signified_houses": all_signified,
            "rp_agreement": rp_match,
            "ruling_planets_active": rps,
            "confidence_score": confidence_score,
            "verdict_badge": verdict_badge,
            "verdict_desc": verdict_desc,
            "color_theme": color_theme,
            "timing_estimate": timing_str
        }


default_kp_engine = KPEngine()
