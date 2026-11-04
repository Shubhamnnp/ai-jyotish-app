"""
Factor Extractor for JyotishOS (Phase 5, Task P5-T1).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.1).

Computes typed, verified astrological facts per planet and per house:
- Sign, house, dignity, avastha (Baladi, Jagratadi, Deeptadi)
- Combustion status and angular separation from Sun
- Retrogression status and speed
- Shadbala virupas, ratio (relative to classical minimum threshold), and rank
- Classical Parashari Aspects given and received (houses and planets)
- Conjunctions (co-occupants in the same house)
- House lordships (e.g. Sagittarius Lagna -> Sun owns 9th, Jupiter owns 1st & 4th)
- Nakshatra name, pada, and nakshatra lord
- Varga positions (D1, D9 Navamsha, D10 Dashamsha) & Vargottama detection
- Ashtakavarga Bhinna (BAV) bindus for occupied sign & Sarvashtakavarga (SAV) per house
- Jaimini Chara Karakas (AK, AmK, BK, MK, PK, GK, DK) and Naisargika Karakatwa
- House classifications: Kendra, Trikona, Dusthana, Upachaya, and Arudha Padas resident

Strict Rule:
This module is a pure mathematical function of the chart. It outputs structured, typed facts
and does not generate speculative or ungrounded textual claims.
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field

from ..core.models import KundaliChart, PlanetPosition
from ..core.constants import (
    SIGN_NAMES,
    SIGN_LORDS,
    NAKSHATRAS,
    NAKSHATRA_NAMES,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    DUSTHANA_HOUSES,
    UPACHAYA_HOUSES,
)
from ..core.shadbala import default_shadbala_calculator
from ..core.varga import VargaCalculator
from ..core.ashtakavarga import AshtakavargaCalculator
from ..core.jaimini import default_jaimini_calculator
from ..core.combustion import CombustionCalculator


NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

NAISARGIKA_KARAKATWAS: Dict[str, List[str]] = {
    "Sun": ["Soul (Atma)", "Father (Pitri)", "Authority & Kingdom", "Vitality", "Ego & Fame"],
    "Moon": ["Mind (Manas)", "Mother (Matri)", "Emotions", "Peace & Nourishment", "Memory"],
    "Mars": ["Courage & Valour", "Younger Siblings (Bhratri)", "Physical Vigor", "Property & Land", "Command"],
    "Mercury": ["Intellect (Buddhi)", "Speech (Vak)", "Commerce & Finance", "Analytical Logic", "Education"],
    "Jupiter": ["Wisdom (Guru)", "Children (Putra)", "Wealth & Dharma", "Guru & Spirituality", "Divine Grace"],
    "Venus": ["Spouse (Kalatra)", "Vehicles & Luxuries", "Arts & Aesthetics", "Material Prosperity", "Sensory Joy"],
    "Saturn": ["Longevity (Ayush)", "Labor & Discipline", "Perseverance", "Sorrow & Humility", "Karmic Reckoning"],
    "Rahu": ["Worldly Ambition", "Foreign Endeavors", "Unorthodox Innovation", "Illusion (Maya)", "Technical Research"],
    "Ketu": ["Spiritual Liberation (Moksha)", "Occult Insight", "Detachment (Vairagya)", "Asceticism", "Karmic Culmination"]
}

PARASHARI_SPECIAL_ASPECTS: Dict[str, List[int]] = {
    "Mars": [4, 7, 8],
    "Jupiter": [5, 7, 9],
    "Saturn": [3, 7, 10],
    "Rahu": [5, 7, 9],
    "Ketu": [5, 7, 9]
}


class PlanetFactors(BaseModel):
    """Typed astrological factors for a single planet."""
    planet: str
    longitude: float
    sign_name: str
    sign_id: int  # 1..12
    house_from_lagna: int  # 1..12
    house_from_moon: int  # 1..12
    dignity: str  # 'exalted', 'own', 'moolatrikona', 'friendly', 'neutral', 'enemy', 'debilitated'
    is_retrograde: bool
    is_combust: bool
    combustion_separation: float
    baladi_avastha: str
    jagratadi_avastha: str
    deeptadi_avastha: str
    shadbala_virupas: float
    shadbala_ratio: float
    is_shadbala_strong: bool
    houses_owned: List[int]
    nakshatra_name: str
    nakshatra_pada: int
    nakshatra_lord: str
    conjunctions: List[str]
    aspects_given_to_houses: List[int]
    aspects_given_to_planets: List[str]
    aspects_received_from_planets: List[str]
    d9_navamsha_sign: str
    d10_dashamsha_sign: str
    is_vargottama: bool
    chara_karaka: Optional[str] = None
    naisargika_karakatwas: List[str] = Field(default_factory=list)
    bav_bindus: int = 0


class HouseFactors(BaseModel):
    """Typed astrological factors for a single house / bhava."""
    house_num: int  # 1..12
    sign_name: str
    sign_id: int  # 1..12
    lord: str
    lord_placement_house: int
    lord_dignity: str
    lord_shadbala_ratio: float
    occupants: List[str]
    benefic_occupants: List[str]
    malefic_occupants: List[str]
    aspecting_planets: List[str]
    benefic_aspects: List[str]
    malefic_aspects: List[str]
    sav_bindus: int
    is_kendra: bool
    is_trikona: bool
    is_dusthana: bool
    is_upachaya: bool
    arudha_padas_resident: List[str] = Field(default_factory=list)


class ChartFactors(BaseModel):
    """Unified collection of typed astrological factors for the entire chart."""
    chart_id: str
    lagna_sign: str
    lagna_degree: float
    lagna_lord: str
    moon_sign: str
    moon_nakshatra: str
    sun_sign: str
    planets: Dict[str, PlanetFactors]
    houses: Dict[int, HouseFactors]
    atmakaraka: Optional[str] = None
    amatyakaraka: Optional[str] = None
    vargottama_planets: List[str] = Field(default_factory=list)
    combust_planets: List[str] = Field(default_factory=list)
    retrograde_planets: List[str] = Field(default_factory=list)
    exalted_planets: List[str] = Field(default_factory=list)
    debilitated_planets: List[str] = Field(default_factory=list)


class FactorExtractor:
    """Pure-function factor extractor computing typed facts across all astrological dimensions."""

    @classmethod
    def extract_factors(cls, chart: KundaliChart) -> ChartFactors:
        """
        Extracts typed factors for all planets and houses in the chart.
        Pure function: identical chart input always yields identical typed factors.
        """
        # 1. Ephemeris & Fundamental Calculations
        shadbala_summary = default_shadbala_calculator.calculate(chart)
        ashtakavarga = AshtakavargaCalculator.calculate(chart)
        jaimini = default_jaimini_calculator.calculate(chart)
        vargottama_list = VargaCalculator.get_vargottama_planets(chart)
        d9_chart = VargaCalculator.calculate_d9(chart)
        d10_chart = VargaCalculator.calculate_d10(chart)

        sun_obj = chart.planets.get("Sun")
        sun_lon = sun_obj.longitude if sun_obj else 0.0

        # Precompute House Ownerships per planet
        planet_ownerships: Dict[str, List[int]] = {p: [] for p in chart.planets.keys()}
        for h_idx in range(12):
            h_num = h_idx + 1
            h_sign = chart.houses[h_idx].sign_name
            h_lord = SIGN_LORDS.get(h_sign)
            if h_lord and h_lord in planet_ownerships:
                planet_ownerships[h_lord].append(h_num)

        # Precompute House Occupants
        house_occupants: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        for p_name, pos in chart.planets.items():
            house_occupants[pos.house_from_lagna].append(p_name)

        # Precompute Aspects Given by Planets to Houses
        aspects_given_to_houses: Dict[str, List[int]] = {}
        for p_name, pos in chart.planets.items():
            from_h = pos.house_from_lagna
            relative_aspects = PARASHARI_SPECIAL_ASPECTS.get(p_name, [7])
            target_houses: List[int] = []
            for rel in relative_aspects:
                target_h = ((from_h + rel - 2) % 12) + 1
                target_houses.append(target_h)
            aspects_given_to_houses[p_name] = sorted(list(set(target_houses)))

        # Precompute Aspects Received by Planets
        aspects_given_to_planets: Dict[str, List[str]] = {p: [] for p in chart.planets.keys()}
        aspects_received_by_planets: Dict[str, List[str]] = {p: [] for p in chart.planets.keys()}

        for p_src, target_houses in aspects_given_to_houses.items():
            for target_h in target_houses:
                occupants = house_occupants.get(target_h, [])
                for p_dest in occupants:
                    if p_dest != p_src:
                        aspects_given_to_planets[p_src].append(p_dest)
                        aspects_received_by_planets[p_dest].append(p_src)

        # Precompute Arudha Padas resident per house
        arudhas_in_house: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        for ap_key, ap_h in jaimini.arudha_padas.items():
            if 1 <= ap_h <= 12:
                arudhas_in_house[ap_h].append(ap_key)

        # 2. Extract Factors per Planet
        planet_factors_map: Dict[str, PlanetFactors] = {}
        combust_list: List[str] = []
        retrograde_list: List[str] = []
        exalted_list: List[str] = []
        debilitated_list: List[str] = []

        # Invert chara karakas for quick lookup
        chara_karaka_lookup: Dict[str, str] = {}
        for k_name, p_val in jaimini.karakas_7.items():
            chara_karaka_lookup[p_val] = k_name

        for p_name, pos in chart.planets.items():
            # Combustion
            comb_detail = CombustionCalculator.get_combustion_detail(
                planet_name=p_name,
                planet_lon=pos.longitude,
                sun_lon=sun_lon,
                is_retrograde=pos.is_retrograde
            )
            is_comb = comb_detail["is_combust"]
            if is_comb:
                combust_list.append(p_name)

            if pos.is_retrograde:
                retrograde_list.append(p_name)
            if pos.dignity == "exalted":
                exalted_list.append(p_name)
            elif pos.dignity == "debilitated":
                debilitated_list.append(p_name)

            # Shadbala
            p_shad = shadbala_summary.planets.get(p_name)
            shad_virupas = p_shad.total_virupas if p_shad else 0.0
            shad_ratio = p_shad.strength_ratio if p_shad else 1.0
            is_strong = p_shad.is_strong if p_shad else True
            baladi = p_shad.baladi_avastha if p_shad else "Yuva"
            jagratadi = p_shad.jagratadi_avastha if p_shad else "Jagrata"
            deeptadi = p_shad.deeptadi_avastha if p_shad else "Swastha"

            # Varga placements
            d9_pos = d9_chart.planets.get(p_name)
            d10_pos = d10_chart.planets.get(p_name)
            d9_sign = d9_pos.sign_name if d9_pos else pos.sign_name
            d10_sign = d10_pos.sign_name if d10_pos else pos.sign_name

            # Ashtakavarga BAV bindus for occupied sign
            bav_counts = ashtakavarga.bav.get(p_name, [0] * 12)
            sign_idx = pos.sign_id - 1
            p_bav = bav_counts[sign_idx] if 0 <= sign_idx < len(bav_counts) else 0

            # Conjunctions (other planets in same house)
            conjs = [other for other in house_occupants[pos.house_from_lagna] if other != p_name]

            p_factor = PlanetFactors(
                planet=p_name,
                longitude=round(pos.longitude, 4),
                sign_name=pos.sign_name,
                sign_id=pos.sign_id,
                house_from_lagna=pos.house_from_lagna,
                house_from_moon=pos.house_from_moon,
                dignity=pos.dignity,
                is_retrograde=pos.is_retrograde,
                is_combust=is_comb,
                combustion_separation=comb_detail["separation_degrees"],
                baladi_avastha=baladi,
                jagratadi_avastha=jagratadi,
                deeptadi_avastha=deeptadi,
                shadbala_virupas=round(shad_virupas, 2),
                shadbala_ratio=round(shad_ratio, 3),
                is_shadbala_strong=is_strong,
                houses_owned=planet_ownerships.get(p_name, []),
                nakshatra_name=pos.nakshatra_name,
                nakshatra_pada=pos.nakshatra_pada,
                nakshatra_lord=pos.nakshatra_lord,
                conjunctions=conjs,
                aspects_given_to_houses=aspects_given_to_houses.get(p_name, []),
                aspects_given_to_planets=aspects_given_to_planets.get(p_name, []),
                aspects_received_from_planets=aspects_received_by_planets.get(p_name, []),
                d9_navamsha_sign=d9_sign,
                d10_dashamsha_sign=d10_sign,
                is_vargottama=(p_name in vargottama_list),
                chara_karaka=chara_karaka_lookup.get(p_name),
                naisargika_karakatwas=NAISARGIKA_KARAKATWAS.get(p_name, []),
                bav_bindus=p_bav
            )
            planet_factors_map[p_name] = p_factor

        # 3. Extract Factors per House
        house_factors_map: Dict[int, HouseFactors] = {}
        for h_idx in range(12):
            h_num = h_idx + 1
            h_sign = chart.houses[h_idx].sign_name
            h_sign_id = (chart.lagna_sign_id + h_idx - 1) % 12 + 1
            h_lord = SIGN_LORDS.get(h_sign, "")

            lord_p = planet_factors_map.get(h_lord)
            lord_h = lord_p.house_from_lagna if lord_p else 1
            lord_dig = lord_p.dignity if lord_p else "neutral"
            lord_shad = lord_p.shadbala_ratio if lord_p else 1.0

            occupants = house_occupants.get(h_num, [])
            ben_occ = [p for p in occupants if p in NATURAL_BENEFICS]
            mal_occ = [p for p in occupants if p in NATURAL_MALEFICS]

            # Aspecting planets
            aspecting = [
                p_src for p_src, tgts in aspects_given_to_houses.items()
                if h_num in tgts
            ]
            ben_asp = [p for p in aspecting if p in NATURAL_BENEFICS]
            mal_asp = [p for p in aspecting if p in NATURAL_MALEFICS]

            # SAV bindus
            sav_bindus = ashtakavarga.sav[h_sign_id - 1] if 0 <= h_sign_id - 1 < len(ashtakavarga.sav) else 28

            h_factor = HouseFactors(
                house_num=h_num,
                sign_name=h_sign,
                sign_id=h_sign_id,
                lord=h_lord,
                lord_placement_house=lord_h,
                lord_dignity=lord_dig,
                lord_shadbala_ratio=lord_shad,
                occupants=occupants,
                benefic_occupants=ben_occ,
                malefic_occupants=mal_occ,
                aspecting_planets=aspecting,
                benefic_aspects=ben_asp,
                malefic_aspects=mal_asp,
                sav_bindus=sav_bindus,
                is_kendra=(h_num in KENDRA_HOUSES),
                is_trikona=(h_num in TRIKONA_HOUSES),
                is_dusthana=(h_num in DUSTHANA_HOUSES),
                is_upachaya=(h_num in UPACHAYA_HOUSES),
                arudha_padas_resident=arudhas_in_house.get(h_num, [])
            )
            house_factors_map[h_num] = h_factor

        # 4. Chart Master Factors
        moon_obj = chart.planets.get("Moon")
        lagna_sign_name = chart.houses[0].sign_name
        lagna_lord_name = SIGN_LORDS.get(lagna_sign_name, "")

        return ChartFactors(
            chart_id=f"{chart.birth_data.name}_{chart.birth_data.birth_date}",
            lagna_sign=lagna_sign_name,
            lagna_degree=round(chart.lagna_longitude % 30.0, 4),
            lagna_lord=lagna_lord_name,
            moon_sign=moon_obj.sign_name if moon_obj else "",
            moon_nakshatra=moon_obj.nakshatra_name if moon_obj else "",
            sun_sign=sun_obj.sign_name if sun_obj else "",
            planets=planet_factors_map,
            houses=house_factors_map,
            atmakaraka=jaimini.karakas_7.get("AK"),
            amatyakaraka=jaimini.karakas_7.get("AmK"),
            vargottama_planets=vargottama_list,
            combust_planets=combust_list,
            retrograde_planets=retrograde_list,
            exalted_planets=exalted_list,
            debilitated_planets=debilitated_list
        )


default_factor_extractor = FactorExtractor()
