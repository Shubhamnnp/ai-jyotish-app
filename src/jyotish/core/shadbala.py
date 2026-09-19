"""
Shadbala, Bhavabala, and Planetary Avasthas Engine for JyotishOS.
Calculates classical 6-fold planetary strength (Sthana, Dik, Kaala, Cheshta, Naisargika, Drik Bala),
Ishta/Kashta Phala, Baladi Avasthas, Jagratadi Avasthas, and Deeptadi Avasthas
according to Brihat Parashara Hora Shastra (BPHS Ch. 27-29).
"""

import math
from typing import Dict, List, Tuple
from .constants import (
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES,
    SIGN_LORDS, EXALTATION, DEBILITATION
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
    """Calculates classical Shadbala and Avasthas."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> ShadbalaSummary:
        """Calculates Shadbala for 7 classical planets and Bhava Bala."""
        planets_result: Dict[str, ShadbalaPlanetResult] = {}
        seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        is_day_birth = 6 <= chart.birth_data.birth_time.hour < 18

        for p_name in seven_planets:
            p = chart.planets[p_name]

            # 1. Sthana Bala (Positional Strength)
            sthana = cls._calc_sthana_bala(p, chart)

            # 2. Dik Bala (Directional Strength)
            dik = cls._calc_dik_bala(p, chart)

            # 3. Kaala Bala (Temporal Strength)
            kaala = cls._calc_kaala_bala(p, chart, is_day_birth)

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
            uchha_bala = cls._calc_uchha_bala(p)
            ishta = round(math.sqrt(max(0.0, uchha_bala * cheshta)), 2)
            kashta = round(math.sqrt(max(0.0, (60.0 - uchha_bala) * (60.0 - cheshta))), 2)

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
                deeptadi_avastha=deeptadi
            )

        # Calculate Bhava Bala for 12 houses
        bhava_bala: Dict[int, float] = {}
        for h in range(1, 13):
            lord_name = chart.houses[h - 1].lord
            lord_virupas = planets_result.get(lord_name, planets_result["Jupiter"]).total_virupas
            # Kendra bonus + occupant support
            kendra_bonus = 60.0 if h in KENDRA_HOUSES else (30.0 if h in TRIKONA_HOUSES else 15.0)
            occupant_count = len(chart.houses[h - 1].occupants)
            bhava_bala[h] = round(lord_virupas * 0.7 + kendra_bonus + occupant_count * 15.0, 2)

        return ShadbalaSummary(
            planets=planets_result,
            bhava_bala=bhava_bala
        )

    @classmethod
    def _calc_uchha_bala(cls, p: PlanetPosition) -> float:
        """Uchha Bala: 0 to 60 virupas based on distance from deep exaltation point."""
        exalt_info = EXALTATION.get(p.name)
        if not exalt_info:
            return 30.0
        exalt_sign_idx = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"].index(exalt_info[0])
        exalt_deg = exalt_sign_idx * 30.0 + exalt_info[1]
        diff = abs(p.longitude - exalt_deg)
        if diff > 180.0:
            diff = 360.0 - diff
        return round(60.0 * (1.0 - diff / 180.0), 2)

    @classmethod
    def _calc_sthana_bala(cls, p: PlanetPosition, chart: KundaliChart) -> float:
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
        # Sun, Mars, Jupiter, Mercury prefer odd; Moon, Venus prefer even
        if p.name in ("Sun", "Mars", "Jupiter", "Mercury"):
            ojha = 15.0 if is_odd_sign else 0.0
        else:
            ojha = 15.0 if not is_odd_sign else 0.0

        # Dignity weight
        dignity_weights = {
            "exalted": 45.0, "moolatrikona": 37.5, "own": 30.0,
            "friend": 20.0, "neutral": 10.0, "enemy": 5.0, "debilitated": 0.0
        }
        varga_factor = dignity_weights.get(p.dignity, 15.0) * 1.5

        return uchha + kendradi + ojha + varga_factor

    @classmethod
    def _calc_dik_bala(cls, p: PlanetPosition, chart: KundaliChart) -> float:
        """Directional strength: 0 to 60 virupas."""
        # Ideal house
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
    def _calc_kaala_bala(cls, p: PlanetPosition, chart: KundaliChart, is_day: bool) -> float:
        """Temporal strength (Nathonnatha, Paksha, Tribhaga)."""
        # Day vs Night planets
        # Sun, Jupiter, Venus are strong by day; Moon, Mars, Saturn by night; Mercury always
        if p.name == "Mercury":
            nathonnatha = 60.0
        elif is_day:
            nathonnatha = 60.0 if p.name in ("Sun", "Jupiter", "Venus") else 10.0
        else:
            nathonnatha = 60.0 if p.name in ("Moon", "Mars", "Saturn") else 10.0

        # Paksha bala (based on tithi / moon brightness)
        is_shukla = "Shukla" in chart.panchang.tithi_type
        if p.name in ("Moon", "Jupiter", "Venus", "Mercury"):
            paksha = 45.0 if is_shukla else 20.0
        else:
            paksha = 45.0 if not is_shukla else 20.0

        return nathonnatha * 0.6 + paksha * 0.4

    @classmethod
    def _calc_cheshta_bala(cls, p: PlanetPosition) -> float:
        """Motional strength: Retrograde = 60, Direct = 30-45."""
        if p.name in ("Sun", "Moon"):
            return 35.0  # Luminaries do not retrograde
        if p.is_retrograde:
            return 60.0
        # Check speed
        if abs(p.speed) > 1.0:
            return 45.0
        return 30.0

    @classmethod
    def _calc_drik_bala(cls, p: PlanetPosition, chart: KundaliChart) -> float:
        """Aspectual strength from benefics (+ve) and malefics (-ve)."""
        score = 15.0
        for other_name, other_pos in chart.planets.items():
            if other_name in (p.name, "Rahu", "Ketu"):
                continue
            diff = abs(p.house_from_lagna - other_pos.house_from_lagna)
            if diff in (4, 8):  # Trine aspect
                if other_name in ("Jupiter", "Venus", "Mercury"):
                    score += 10.0
            elif diff == 6:  # 7th mutual aspect
                if other_name in ("Jupiter", "Venus"):
                    score += 15.0
                elif other_name in ("Saturn", "Mars"):
                    score -= 10.0
        return max(0.0, min(60.0, score))

    @classmethod
    def _calc_baladi_avastha(cls, p: PlanetPosition) -> str:
        """Bala, Kumara, Yuva, Vriddha, Mrita."""
        deg = p.sign_degree
        is_odd = (p.sign_id % 2 != 0)
        idx = int(deg // 6.0)  # 0 to 4
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
        """Deepta, Mudita, Shanta, Shakta, Peedita, Deena, Khala."""
        if p.dignity == "exalted":
            return "Deepta (Radiant/Exalted)"
        elif p.is_combust:
            return "Peedita (Combust/Afflicted)"
        elif p.dignity == "own":
            return "Swastha (Content/Own Sign)"
        elif p.dignity == "moolatrikona":
            return "Mudita (Delighted)"
        elif p.dignity == "friend":
            return "Shanta (Peaceful)"
        elif p.dignity == "debilitated":
            return "Deena (Depressed/Debilitated)"
        elif p.dignity == "enemy":
            return "Khala (Agitated)"
        return "Shakta (Capable)"


# Singleton Shadbala instance
default_shadbala_calculator = ShadbalaCalculator()

