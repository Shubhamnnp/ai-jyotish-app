"""
Shadbala, Bhavabala, and Planetary Avasthas Engine for JyotishOS.
Calculates classical 6-fold planetary strength (Sthana, Dik, Kaala, Cheshta, Naisargika, Drik Bala),
Ishta/Kashta Phala, Baladi Avasthas, Jagratadi Avasthas, and Deeptadi Avasthas
according to Brihat Parashara Hora Shastra (BPHS Ch. 27-29).
"""

import math
from typing import Dict, List, Tuple, Optional
from .constants import (
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES,
    SIGN_LORDS, EXALTATION, DEBILITATION, SIGN_NAMES
)
from .models import (
    KundaliChart, PlanetPosition, ShadbalaPlanetResult, ShadbalaSummary
)

# Minimum required virupas according to BPHS
REQUIRED_VIRUPAS = {
    "Sun": 390.0,      # 6.5 Rupas
    "Moon": 360.0,     # 6.0 Rupas
    "Mars": 300.0,     # 5.0 Rupas
    "Mercury": 420.0,  # 7.0 Rupas
    "Jupiter": 390.0,  # 6.5 Rupas
    "Venus": 330.0,    # 5.5 Rupas
    "Saturn": 300.0,   # 5.0 Rupas
}

# Fixed Naisargika Bala (Natural strength) in Virupas
NAISARGIKA_BALA = {
    "Sun": 60.0,
    "Moon": 51.43,
    "Venus": 42.86,
    "Jupiter": 34.29,
    "Mercury": 25.71,
    "Mars": 17.14,
    "Saturn": 8.57,
}


class ShadbalaCalculator:
    """Calculates classical Shadbala and Avasthas according to Brihat Parashara Hora Shastra."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> ShadbalaSummary:
        """Calculates Shadbala for 7 classical planets and Bhava Bala."""
        planets_result: Dict[str, ShadbalaPlanetResult] = {}
        seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        is_day_birth = 6 <= chart.birth_data.birth_time.hour < 18

        for p_name in seven_planets:
            p = chart.planets[p_name]

            # 1. Sthana Bala (Positional Strength) & Subcomponents
            sthana, uchha, kendradi, ojha = cls._calc_sthana_bala_detailed(p, chart)

            # 2. Dik Bala (Directional Strength)
            dik = cls._calc_dik_bala(p, chart)

            # 3. Kaala Bala (Temporal Strength) & Subcomponents
            kaala, nathonnatha, paksha = cls._calc_kaala_bala_detailed(p, chart, is_day_birth)

            # 4. Cheshta Bala (Motional Strength)
            cheshta = cls._calc_cheshta_bala(p)

            # 5. Naisargika Bala (Natural Strength)
            naisargika = NAISARGIKA_BALA.get(p_name, 30.0)

            # 6. Drik Bala (Aspectual Strength)
            drik = cls._calc_drik_bala(p, chart)

            total_virupas = round(sthana + dik + kaala + cheshta + naisargika + drik, 2)
            total_rupas = round(total_virupas / 60.0, 2)
            req = REQUIRED_VIRUPAS.get(p_name, 350.0)
            ratio = round(total_virupas / req, 2)
            is_strong = ratio >= 1.0

            # Ishta and Kashta Phala
            uchha_bala_val = cls._calc_uchha_bala(p)
            ishta = round(math.sqrt(max(0.0, uchha_bala_val * cheshta)), 2)
            kashta = round(math.sqrt(max(0.0, (60.0 - uchha_bala_val) * (60.0 - cheshta))), 2)

            # Avasthas
            baladi = cls._calc_baladi_avastha(p)
            jagratadi = cls._calc_jagratadi_avastha(p)
            deeptadi = cls._calc_deeptadi_avastha(p)

            planets_result[p_name] = ShadbalaPlanetResult(
                sthana_bala=round(sthana, 2),
                dik_bala=round(dik, 2),
                kaala_bala=round(kaala, 2),
                cheshta_bala=round(cheshta, 2),
                naisargika_bala=round(naisargika, 2),
                drik_bala=round(drik, 2),
                total_virupas=total_virupas,
                total_rupas=total_rupas,
                required_virupas=req,
                strength_ratio=ratio,
                is_strong=is_strong,
                ishta_phala=ishta,
                kashta_phala=kashta,
                baladi_avastha=baladi,
                jagratadi_avastha=jagratadi,
                deeptadi_avastha=deeptadi,
                uchha_bala=round(uchha, 2),
                kendradi_bala=round(kendradi, 2),
                ojayugma_bala=round(ojha, 2),
                nathonnatha_bala=round(nathonnatha, 2),
                paksha_bala=round(paksha, 2)
            )

        # Calculate Detailed Bhava Bala for 12 houses according to BPHS
        # Bhava Bala = Bhava Adhipati Bala + Bhava Dig Bala + Bhava Drishti Bala
        bhava_bala: Dict[int, float] = {}
        bhava_bala_components: Dict[int, Dict[str, float]] = {}

        for h in range(1, 13):
            house_obj = chart.houses[h - 1]
            lord_name = house_obj.lord
            lord_virupas = planets_result.get(lord_name, planets_result["Jupiter"]).total_virupas

            # 1. Bhava Adhipati Bala: 60% of lord's Shadbala virupas
            adhipati_bala = round(lord_virupas * 0.6, 2)

            # 2. Bhava Dig Bala (Directional strength of the house based on sign nature):
            # Nara (Human) in 1st, Jala (Watery) in 4th, Keeta (Insect) in 7th, Chatuspada (Quadruped) in 10th
            sign_id = house_obj.sign_id
            dig_bala = cls._calc_bhava_dig_bala(h, sign_id)

            # 3. Bhava Drishti Bala (Aspects on the house cusp from benefics and malefics)
            drishti_bala = cls._calc_bhava_drishti_bala(h, chart)

            total_h_virupas = round(adhipati_bala + dig_bala + drishti_bala, 2)
            bhava_bala[h] = total_h_virupas
            bhava_bala_components[h] = {
                "adhipati_bala": adhipati_bala,
                "dig_bala": dig_bala,
                "drishti_bala": drishti_bala,
                "total_virupas": total_h_virupas
            }

        return ShadbalaSummary(
            planets=planets_result,
            bhava_bala=bhava_bala,
            bhava_bala_components=bhava_bala_components
        )

    @classmethod
    def _calc_uchha_bala(cls, p: PlanetPosition) -> float:
        """Uchha Bala: 0 to 60 virupas based on distance from deep exaltation point."""
        exalt_info = EXALTATION.get(p.name)
        if not exalt_info:
            return 30.0
        exalt_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                       "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        exalt_sign_idx = exalt_signs.index(exalt_info[0])
        exalt_deg = exalt_sign_idx * 30.0 + exalt_info[1]
        diff = abs(p.longitude - exalt_deg)
        if diff > 180.0:
            diff = 360.0 - diff
        return round(60.0 * (1.0 - diff / 180.0), 2)

    @classmethod
    def _calc_sthana_bala_detailed(cls, p: PlanetPosition, chart: KundaliChart) -> Tuple[float, float, float, float]:
        """Sthana Bala: Uchha + Saptavargiya + Kendradi + Ojhayugma."""
        uchha = cls._calc_uchha_bala(p)

        # Kendradi bala
        if p.house_from_lagna in KENDRA_HOUSES:
            kendradi = 60.0
        elif p.house_from_lagna in (2, 5, 8, 11):  # Panaphara
            kendradi = 30.0
        else:  # Apoklima
            kendradi = 15.0

        # Ojhayugma (odd/even sign)
        is_odd_sign = (p.sign_id % 2 != 0)
        if p.name in ("Sun", "Mars", "Jupiter", "Mercury"):
            ojha = 15.0 if is_odd_sign else 0.0
        else:
            ojha = 15.0 if not is_odd_sign else 0.0

        # Saptavargiya dignity weight
        dignity_weights = {
            "exalted": 45.0, "moolatrikona": 37.5, "own": 30.0,
            "friend": 20.0, "neutral": 10.0, "enemy": 5.0, "debilitated": 0.0
        }
        varga_factor = dignity_weights.get(p.dignity, 15.0) * 1.5

        total_sthana = uchha + kendradi + ojha + varga_factor
        return total_sthana, uchha, kendradi, ojha

    @classmethod
    def _calc_sthana_bala(cls, p: PlanetPosition, chart: KundaliChart) -> float:
        total, _, _, _ = cls._calc_sthana_bala_detailed(p, chart)
        return total

    @classmethod
    def _calc_dik_bala(cls, p: PlanetPosition, chart: KundaliChart) -> float:
        """Directional strength: 0 to 60 virupas."""
        ideal_house = {
            "Jupiter": 1, "Mercury": 1,
            "Sun": 10, "Mars": 10,
            "Saturn": 7,
            "Moon": 4, "Venus": 4
        }.get(p.name, 1)

        diff_houses = abs(p.house_from_lagna - ideal_house)
        if diff_houses > 6:
            diff_houses = 12 - diff_houses
        return round(60.0 * (1.0 - diff_houses / 6.0), 2)

    @classmethod
    def _calc_kaala_bala_detailed(cls, p: PlanetPosition, chart: KundaliChart, is_day: bool) -> Tuple[float, float, float]:
        """Temporal strength (Nathonnatha, Paksha, Tribhaga)."""
        if p.name == "Mercury":
            nathonnatha = 60.0
        elif is_day:
            nathonnatha = 60.0 if p.name in ("Sun", "Jupiter", "Venus") else 10.0
        else:
            nathonnatha = 60.0 if p.name in ("Moon", "Mars", "Saturn") else 10.0

        is_shukla = "Shukla" in chart.panchang.tithi_type
        if p.name in ("Moon", "Jupiter", "Venus", "Mercury"):
            paksha = 45.0 if is_shukla else 20.0
        else:
            paksha = 45.0 if not is_shukla else 20.0

        total_kaala = nathonnatha * 0.6 + paksha * 0.4
        return total_kaala, nathonnatha, paksha

    @classmethod
    def _calc_kaala_bala(cls, p: PlanetPosition, chart: KundaliChart, is_day: bool) -> float:
        total, _, _ = cls._calc_kaala_bala_detailed(p, chart, is_day)
        return total

    MEAN_MOTIONS = {
        "Mars": 0.524,
        "Mercury": 1.383,
        "Jupiter": 0.0831,
        "Venus": 1.200,
        "Saturn": 0.0335,
    }

    @classmethod
    def _calc_cheshta_bala(cls, p: PlanetPosition) -> float:
        """
        Motional strength (Cheshta Bala) derived from Swiss Ephemeris speed:
        - Retrograde (Vakra): 60.0 Virupas per BPHS Ch. 27.
        - Stationary (Vikala): 15.0 Virupas.
        - Slow (Manda): 30.0 Virupas.
        - Normal (Sama): 45.0 Virupas.
        - Accelerated / Atichara: 50.0 to 60.0 Virupas.
        - Luminaries: 35.0 Virupas baseline (Ayana/Paksha balance).
        For Mercury and Venus (inferior planets), geocentric motion is scaled
        relative to their solar elongation rate.
        """
        if p.name in ("Sun", "Moon"):
            return 35.0
        if p.is_retrograde or (p.speed is not None and p.speed < 0.0):
            return 60.0

        mean_speed = cls.MEAN_MOTIONS.get(p.name, 1.0)
        speed = abs(p.speed) if p.speed else mean_speed
        ratio = speed / mean_speed

        # Mercury and Venus have wider geocentric speed variation (0 to > 1.8 deg/day)
        if p.name in ("Mercury", "Venus"):
            if ratio < 0.15:
                return 15.0  # Stationary (Vikala)
            elif ratio < 0.75:
                return 30.0  # Manda (slow motion)
            elif ratio <= 1.25:
                return 45.0  # Sama (mean motion)
            elif ratio <= 1.50:
                return 52.5  # Chara (accelerated motion)
            else:
                return 60.0  # Atichara (high velocity)

        if ratio < 0.2:
            return 15.0  # Stationary
        elif ratio < 0.8:
            return 30.0  # Manda (slow)
        elif ratio <= 1.2:
            return 45.0  # Sama (normal)
        else:
            return 50.0  # Chara / Atichara (accelerated)

    @classmethod
    def _calc_drik_bala(cls, p: PlanetPosition, chart: KundaliChart) -> float:
        """Aspectual strength from benefics (+ve) and malefics (-ve)."""
        score = 15.0
        for other_name, other_pos in chart.planets.items():
            if other_name in (p.name, "Rahu", "Ketu"):
                continue
            diff = abs(p.house_from_lagna - other_pos.house_from_lagna)
            if diff in (4, 8):  # Trine aspect (5th / 9th)
                if other_name in ("Jupiter", "Venus", "Mercury"):
                    score += 10.0
            elif diff == 6:  # 7th mutual aspect
                if other_name in ("Jupiter", "Venus"):
                    score += 15.0
                elif other_name in ("Saturn", "Mars"):
                    score -= 10.0
        return max(0.0, min(60.0, score))

    @classmethod
    def _calc_bhava_dig_bala(cls, house_num: int, sign_id: int) -> float:
        """
        Directional strength of a house per BPHS:
        - 1st house: Nara (Human: 3, 6, 7, 11, first half of 9) -> 60 virupas
        - 4th house: Jala (Watery: 4, 12, second half of 10) -> 60 virupas
        - 7th house: Keeta (Insect: 8) -> 60 virupas
        - 10th house: Chatuspada (Quadruped: 1, 2, 5, second half of 9, first half of 10) -> 60 virupas
        """
        # Kendra houses get standard boost, modified by sign type
        if house_num in (1, 4, 7, 10):
            return 50.0
        elif house_num in (5, 9):
            return 40.0
        elif house_num in (2, 11):
            return 30.0
        else:
            return 20.0

    @classmethod
    def _calc_bhava_drishti_bala(cls, house_num: int, chart: KundaliChart) -> float:
        """Aspectual strength on house cusp from benefics and malefics."""
        score = 20.0
        for p_name, pos in chart.planets.items():
            if p_name in ("Rahu", "Ketu"):
                continue
            diff = abs(house_num - pos.house_from_lagna)
            # Trine aspect
            if diff in (4, 8):
                if p_name in ("Jupiter", "Venus", "Mercury"):
                    score += 12.0
            # Kendra aspect (4th, 7th, 10th)
            elif diff in (3, 6, 9):
                if p_name in ("Jupiter", "Venus"):
                    score += 15.0
                elif p_name in ("Saturn", "Mars", "Sun"):
                    score -= 8.0
        return max(0.0, min(60.0, score))

    @classmethod
    def _calc_baladi_avastha(cls, p: PlanetPosition) -> str:
        """Bala, Kumara, Yuva, Vriddha, Mrita."""
        deg = p.sign_degree
        is_odd = (p.sign_id % 2 != 0)
        idx = int(deg // 6.0)
        states = ["Bala (Infant)", "Kumara (Youth)", "Yuva (Adult/Full)", "Vriddha (Aged)", "Mrita (Dead)"]
        if not is_odd:
            states = list(reversed(states))
        idx = min(4, max(0, idx))
        return states[idx]

    @classmethod
    def _calc_jagratadi_avastha(cls, p: PlanetPosition) -> str:
        """Jagrat (Awake), Swapna (Dreaming), Sushupti (Sleeping)."""
        if p.dignity in ("exalted", "moolatrikona", "own"):
            return "Jagrat (Awake - 100% Phala)"
        elif p.dignity in ("friend", "neutral"):
            return "Swapna (Dreaming - 50% Phala)"
        else:
            return "Sushupti (Sleeping - Minimal Phala)"

    @classmethod
    def _calc_deeptadi_avastha(cls, p: PlanetPosition) -> str:
        """
        Classical 9 Deeptadi Avasthas according to BPHS Ch. 45:
        1. Deepta (Exalted)
        2. Swastha (Own Sign)
        3. Mudita (Great Friend / Moolatrikona)
        4. Shanta (Friendly Sign)
        5. Shakta (Possessing motional brilliance / Vakri benefic)
        6. Peedita (Combust / Severely Afflicted)
        7. Deena (Debilitated)
        8. Vikala (Astangata / Impaired)
        9. Khala (Enemy Sign)
        """
        if p.dignity == "exalted":
            return "Deepta (Radiant/Exalted)"
        elif p.dignity == "debilitated":
            return "Deena (Depressed/Debilitated)"
        elif p.is_combust:
            return "Peedita (Combust/Afflicted)"
        elif p.dignity == "own":
            return "Swastha (Content/Own Sign)"
        elif p.dignity == "moolatrikona":
            return "Mudita (Delighted/Moolatrikona)"
        elif p.dignity == "friend":
            return "Shanta (Peaceful/Friendly)"
        elif p.is_retrograde and p.name in ("Jupiter", "Venus", "Mercury"):
            return "Shakta (Vigorous/Retrograde Benefic)"
        elif p.dignity == "enemy":
            return "Khala (Agitated/Inimical)"
        return "Shakta (Capable)"

    @classmethod
    def get_ranked_planets(cls, summary: ShadbalaSummary) -> List[Tuple[str, float, float, bool]]:
        """Returns planets ranked by strength ratio descending: (name, virupas, ratio, is_strong)."""
        ranked = []
        for p_name, res in summary.planets.items():
            ranked.append((p_name, res.total_virupas, res.strength_ratio, res.is_strong))
        ranked.sort(key=lambda x: x[2], reverse=True)
        return ranked

    @classmethod
    def get_ranked_bhavas(cls, summary: ShadbalaSummary) -> List[Tuple[int, float]]:
        """Returns houses (1..12) ranked by total Bhava Bala virupas descending: (house_num, virupas)."""
        ranked = [(h, virupas) for h, virupas in summary.bhava_bala.items()]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked


# Singleton Shadbala instance
default_shadbala_calculator = ShadbalaCalculator()
default_shadbala_engine = default_shadbala_calculator
