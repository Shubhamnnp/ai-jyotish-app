"""
Ashtakavarga Calculation Engine for JyotishOS.
Implements Parashari Bhinna Ashtakavarga (BAV) and Sarva Ashtakavarga (SAV).
Ensures exact classical conservation of 337 total bindus.
"""

from typing import Dict, List
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

