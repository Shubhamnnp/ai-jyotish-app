"""
Ashtakavarga Calculation Engine for JyotishOS.
Implements Parashari Bhinna Ashtakavarga (BAV) and Sarva Ashtakavarga (SAV).
Ensures exact classical conservation of 337 total bindus.
"""

from typing import Dict, List, Any, Optional, Tuple
from .constants import ASHTAKAVARGA_RULES
from .models import AshtakavargaResult, KundaliChart


class AshtakavargaCalculator:
    """Calculates classical 8-contributor Bhinna & Sarva Ashtakavarga."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> AshtakavargaResult:
        """
        Calculates BAV for 7 planets across 12 signs (indices 0..11 for Aries..Pisces),
        and SAV (summed across 7 planets).
        """
        contributors = {
            "Sun": chart.planets["Sun"].sign_id,
            "Moon": chart.planets["Moon"].sign_id,
            "Mars": chart.planets["Mars"].sign_id,
            "Mercury": chart.planets["Mercury"].sign_id,
            "Jupiter": chart.planets["Jupiter"].sign_id,
            "Venus": chart.planets["Venus"].sign_id,
            "Saturn": chart.planets["Saturn"].sign_id,
            "Lagna": chart.lagna_sign_id,
        }

        # Initialize BAV: {planet_name: [0]*12}
        bav: Dict[str, List[int]] = {
            p: [0] * 12 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        }

        # Calculate bindus for each planet
        for p_name, contributor_rules in ASHTAKAVARGA_RULES.items():
            for contrib_name, houses in contributor_rules.items():
                ref_sign = contributors[contrib_name]  # 1 to 12
                for h in houses:
                    # Target sign = (ref_sign - 1 + h - 1) % 12
                    target_sign_idx = (ref_sign - 1 + (h - 1)) % 12
                    bav[p_name][target_sign_idx] += 1

        # Calculate SAV: sum of all 7 planets per sign
        sav = [0] * 12
        for s_idx in range(12):
            sav[s_idx] = sum(bav[p][s_idx] for p in bav.keys())

        total = sum(sav)

        # Calculate Shodhana (Trikona & Ekadhipatya reductions + Pinda)
        shodhana = cls.calculate_shodhana(bav, chart)

        return AshtakavargaResult(
            bav=bav,
            sav=sav,
            total_bindus=total,
            shodhana=shodhana
        )

    @classmethod
    def calculate_shodhana(cls, bav: Dict[str, List[int]], chart: KundaliChart):
        """
        Implements Trikona Shodhana and Ekadhipatya Shodhana on BAV.
        Computes Rashi Pinda, Graha Pinda, and Yoga Pinda.
        """
        from .models import ShodhanaResult

        trikona_groups = [
            [0, 4, 8],    # Aries, Leo, Sagittarius (Agni/Fire)
            [1, 5, 9],    # Taurus, Virgo, Capricorn (Prithvi/Earth)
            [2, 6, 10],   # Gemini, Libra, Aquarius (Vayu/Air)
            [3, 7, 11],   # Cancer, Scorpio, Pisces (Jala/Water)
        ]

        dual_signs = [
            (0, 7),   # Mars: Aries & Scorpio
            (2, 5),   # Mercury: Gemini & Virgo
            (8, 11),  # Jupiter: Sagittarius & Pisces
            (1, 6),   # Venus: Taurus & Libra
            (9, 10),  # Saturn: Capricorn & Aquarius
        ]

        # Multipliers for Rashi Pinda (Aries to Pisces)
        rashi_multipliers = [7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12]

        # Multipliers for Graha Pinda
        graha_multipliers = {
            "Sun": 5, "Moon": 5, "Mars": 8, "Mercury": 5,
            "Jupiter": 10, "Venus": 7, "Saturn": 5
        }

        # Track which planets occupy which sign index (0-11)
        occupied_signs: Dict[int, List[str]] = {i: [] for i in range(12)}
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if p_name in chart.planets:
                s_idx = chart.planets[p_name].sign_id - 1
                occupied_signs[s_idx].append(p_name)

        trikona_res: Dict[str, List[int]] = {}
        ekadhipatya_res: Dict[str, List[int]] = {}
        rashi_pindas: Dict[str, int] = {}
        graha_pindas: Dict[str, int] = {}
        yoga_pindas: Dict[str, int] = {}

        for p_name, raw_bindus in bav.items():
            # 1. Trikona Shodhana
            t_bindus = list(raw_bindus)
            for group in trikona_groups:
                min_val = min(t_bindus[idx] for idx in group)
                for idx in group:
                    t_bindus[idx] = max(0, t_bindus[idx] - min_val)
            trikona_res[p_name] = t_bindus

            # 2. Ekadhipatya Shodhana
            e_bindus = list(t_bindus)
            for s1, s2 in dual_signs:
                b1, b2 = e_bindus[s1], e_bindus[s2]
                has_p1 = len(occupied_signs[s1]) > 0
                has_p2 = len(occupied_signs[s2]) > 0

                if b1 == 0 and b2 == 0:
                    continue
                elif has_p1 and has_p2:
                    # Both occupied by planets -> no reduction
                    continue
                elif not has_p1 and not has_p2:
                    # Neither occupied -> equal bindus or reduced to smaller
                    if b1 == b2:
                        e_bindus[s1] = 0
                        e_bindus[s2] = 0
                    elif b1 < b2:
                        e_bindus[s2] = b1
                    else:
                        e_bindus[s1] = b2
                elif has_p1 and not has_p2:
                    # s1 occupied, s2 unoccupied -> s2 is reduced
                    if b2 > b1:
                        e_bindus[s2] = b1
                    elif b2 == b1:
                        e_bindus[s2] = 0
                    else:
                        e_bindus[s2] = 0
                elif not has_p1 and has_p2:
                    # s2 occupied, s1 unoccupied
                    if b1 > b2:
                        e_bindus[s1] = b2
                    elif b1 == b2:
                        e_bindus[s1] = 0
                    else:
                        e_bindus[s1] = 0

            ekadhipatya_res[p_name] = e_bindus

            # 3. Rashi Pinda
            r_pinda = sum(e_bindus[i] * rashi_multipliers[i] for i in range(12))
            rashi_pindas[p_name] = r_pinda

            # 4. Graha Pinda
            g_pinda = 0
            for i in range(12):
                if occupied_signs[i]:
                    for occ in occupied_signs[i]:
                        g_pinda += e_bindus[i] * graha_multipliers.get(occ, 5)
            graha_pindas[p_name] = g_pinda

            # 5. Yoga Pinda
            yoga_pindas[p_name] = r_pinda + g_pinda

        return ShodhanaResult(
            trikona_reduced_bav=trikona_res,
            ekadhipatya_reduced_bav=ekadhipatya_res,
            rashi_pinda=rashi_pindas,
            graha_pinda=graha_pindas,
            yoga_pinda=yoga_pindas
        )

    @classmethod
    def get_transit_bindus(cls, ashtakavarga: AshtakavargaResult, planet_name: str, transit_sign_id: int) -> int:
        """
        Returns the BAV bindu count for a transit planet in a specific sign (1-12).
        For Saturn transit, for example, 4+ bindus is considered supportive in classical Jyotish.
        """
        if planet_name not in ashtakavarga.bav:
            return 0
        sign_idx = (transit_sign_id - 1) % 12
        return ashtakavarga.bav[planet_name][sign_idx]

    @classmethod
    def get_sav_bindus(cls, ashtakavarga: AshtakavargaResult, sign_id: int) -> int:
        """Returns the SAV total bindu count for a specific sign (1-12). Average is 28."""
        sign_idx = (sign_id - 1) % 12
        return ashtakavarga.sav[sign_idx]

    @classmethod
    def calculate_bhrigu_bindu(cls, chart: "KundaliChart") -> Dict:
        """
        Calculates Bhrigu Bindu — the midpoint between Rahu and Moon.
        This sensitive point triggers important events when planets transit over it.
        Transit of Jupiter, Saturn, or Rahu/Ketu over Bhrigu Bindu = major life event.
        """
        from .constants import SIGN_NAMES
        rahu_lon = chart.planets["Rahu"].longitude
        moon_lon = chart.planets["Moon"].longitude

        # Midpoint calculation (handle 0/360 wraparound)
        diff = (moon_lon - rahu_lon) % 360.0
        if diff > 180.0:
            bhrigu_bindu_lon = (rahu_lon + diff / 2.0) % 360.0
        else:
            bhrigu_bindu_lon = (rahu_lon + diff / 2.0) % 360.0

        sign_id = int(bhrigu_bindu_lon // 30.0) + 1
        if sign_id > 12:
            sign_id = 12
        sign_name = SIGN_NAMES[sign_id - 1]
        degree_in_sign = bhrigu_bindu_lon % 30.0

        # Nakshatra determination
        nak_span = 360.0 / 27.0
        nak_idx = int(bhrigu_bindu_lon / nak_span) % 27
        NAKSHATRA_NAMES = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
            "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]

        return {
            "longitude": round(bhrigu_bindu_lon, 4),
            "sign_id": sign_id,
            "sign_name": sign_name,
            "degree_in_sign": round(degree_in_sign, 4),
            "nakshatra": NAKSHATRA_NAMES[nak_idx],
            "rahu_longitude": round(rahu_lon, 4),
            "moon_longitude": round(moon_lon, 4),
            "description_hi": (
                f"भृगु बिन्दु: {sign_name} {round(degree_in_sign, 2)}° ({NAKSHATRA_NAMES[nak_idx]} नक्षत्र) — "
                f"जब कोई ग्रह इस स्थान पर गोचर करे, तो जीवन में महत्वपूर्ण घटनाएँ होती हैं। "
                f"विशेषतः गुरु, शनि, राहु/केतु का गोचर अत्यन्त प्रभावशाली होता है।"
            ),
        }

    @classmethod
    def calculate_prastara(cls, chart: "KundaliChart", ashtakavarga: AshtakavargaResult) -> Dict:
        """
        Calculates Prastara Ashtakvarga — the full 8×12 contributor grid for each planet.
        Shows exactly WHICH contributor (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna)
        gives a bindu in each sign for each planet.
        This is the detailed foundation of Ashtakvarga from which BAV is derived.
        """
        from .constants import ASHTAKAVARGA_RULES, SIGN_NAMES

        contributors = {
            "Sun": chart.planets["Sun"].sign_id,
            "Moon": chart.planets["Moon"].sign_id,
            "Mars": chart.planets["Mars"].sign_id,
            "Mercury": chart.planets["Mercury"].sign_id,
            "Jupiter": chart.planets["Jupiter"].sign_id,
            "Venus": chart.planets["Venus"].sign_id,
            "Saturn": chart.planets["Saturn"].sign_id,
            "Lagna": chart.lagna_sign_id,
        }

        prastara = {}
        for p_name, contributor_rules in ASHTAKAVARGA_RULES.items():
            planet_prastara = {}
            for contrib_name, houses in contributor_rules.items():
                ref_sign = contributors[contrib_name]
                contrib_bindus = [0] * 12
                for h in houses:
                    target_sign_idx = (ref_sign - 1 + (h - 1)) % 12
                    contrib_bindus[target_sign_idx] = 1
                planet_prastara[contrib_name] = contrib_bindus

            # Build a grid: rows=contributors, cols=signs
            grid_rows = []
            for contrib_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]:
                row = {"contributor": contrib_name, "bindus": planet_prastara.get(contrib_name, [0]*12)}
                grid_rows.append(row)

            prastara[p_name] = {
                "grid": grid_rows,
                "bav_total": ashtakavarga.bav.get(p_name, [0]*12),
                "sign_names": SIGN_NAMES,
            }

        return prastara

    KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]

    @classmethod
    def calculate_kakshya_transit(
        cls,
        natal_chart: KundaliChart,
        transit_chart: KundaliChart
    ) -> List[Dict[str, Any]]:
        """
        Calculates the classical Kakshya (3°45' subdivision) transit status
        for each transiting planet according to Parashari Ashtakavarga.
        """
        contributors = {
            "Sun": natal_chart.planets["Sun"].sign_id,
            "Moon": natal_chart.planets["Moon"].sign_id,
            "Mars": natal_chart.planets["Mars"].sign_id,
            "Mercury": natal_chart.planets["Mercury"].sign_id,
            "Jupiter": natal_chart.planets["Jupiter"].sign_id,
            "Venus": natal_chart.planets["Venus"].sign_id,
            "Saturn": natal_chart.planets["Saturn"].sign_id,
            "Lagna": natal_chart.lagna_sign_id,
        }

        kakshya_results = []
        planets_to_track = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Rahu", "Ketu"]

        for p_name in planets_to_track:
            if p_name not in transit_chart.planets:
                continue
            tp = transit_chart.planets[p_name]
            sign_idx = tp.sign_id - 1
            deg_in_sign = tp.sign_degree
            kakshya_idx = min(7, max(0, int(deg_in_sign // 3.75)))
            kakshya_lord = cls.KAKSHYA_LORDS[kakshya_idx]

            k_start = kakshya_idx * 3.75
            k_end = (kakshya_idx + 1) * 3.75

            # For Rahu/Ketu, use Saturn's/Mars's BAV rules
            target_bav_planet = p_name if p_name in ASHTAKAVARGA_RULES else ("Saturn" if p_name == "Rahu" else "Mars")

            # Check if kakshya_lord contributed a bindu to target_bav_planet in this sign
            contrib_rules = ASHTAKAVARGA_RULES.get(target_bav_planet, {}).get(kakshya_lord, [])
            ref_sign = contributors[kakshya_lord]
            house_offset = ((tp.sign_id - ref_sign) % 12) + 1

            has_bindu = house_offset in contrib_rules
            bindu_status = 1 if has_bindu else 0

            sav_bindus = natal_chart.ashtakavarga.sav[sign_idx] if (natal_chart.ashtakavarga and natal_chart.ashtakavarga.sav) else 28

            if has_bindu:
                status_label = "शुभ फलदायी (Auspicious / Unobstructed)"
                badge = "success"
                desc = f"{p_name} वर्तमान में {kakshya_lord} के कक्ष्य ({k_start:.1f}° - {k_end:.1f}°) में १ बिन्दु युक्त है। कार्य सिद्धि व अनुकूलता प्राप्त होगी।"
            else:
                status_label = "अवरुद्ध / संघर्ष (Obstructed / Rekha)"
                badge = "warning"
                desc = f"{p_name} वर्तमान में {kakshya_lord} के कक्ष्य ({k_start:.1f}° - {k_end:.1f}°) में ० बिन्दु (रेखा) में है। तात्कालिक रुकावटें संभव हैं।"

            kakshya_results.append({
                "planet": p_name,
                "transit_sign": tp.sign_name,
                "transit_degree": round(deg_in_sign, 2),
                "kakshya_index": kakshya_idx + 1,
                "kakshya_lord": kakshya_lord,
                "kakshya_span": f"{k_start:.2f}° - {k_end:.2f}°",
                "bindu": bindu_status,
                "is_favorable": has_bindu,
                "sav_bindus": sav_bindus,
                "status_label": status_label,
                "badge": badge,
                "description_hi": desc
            })

        return kakshya_results

