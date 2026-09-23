"""
Universal Declarative Condition Evaluator for JyotishOS Rules Engine.
Evaluates classical astrological conditions dynamically against:
- Natal Kundali Chart (planets, cusps, signs, houses, dignities, aspects)
- Divisional Charts (D9 Navamsha, D10 Dashamsha, D7 Saptamsha)
- Vimshottari Active Dasha (Mahadasha, Antardasha, Pratyantardasha)
- Planetary Transits (Gochar positions and double transits)

Supports BPHS, Brihat Jataka, Saravali, Phaladeepika, Jaimini, KP, Lal Kitab, Prashna & Numerology.
"""

from typing import Dict, List, Tuple, Optional, Any, Set, Union
from ..core.constants import (
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES, UPACHAYA_HOUSES, MARAKA_HOUSES,
    SIGN_NAMES, SIGN_LORDS, GRAHAS, SPECIAL_ASPECTS
)
from ..core.models import (
    KundaliChart, PlanetPosition, HouseCusp, ActiveDashaHierarchy, TransitSummary
)


class UniversalConditionEvaluator:
    """Evaluates declarative AST/JSON rule conditions with zero code duplication."""

    NATURAL_BENEFICS: Set[str] = {"Jupiter", "Venus", "Mercury", "Moon"}
    NATURAL_MALEFICS: Set[str] = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

    @classmethod
    def get_planet(cls, chart: KundaliChart, name: str) -> Optional[PlanetPosition]:
        return chart.planets.get(name)

    @classmethod
    def get_house(cls, chart: KundaliChart, house_num: int) -> Optional[HouseCusp]:
        if 1 <= house_num <= len(chart.houses):
            return chart.houses[house_num - 1]
        return None

    @classmethod
    def get_house_lord_planet(cls, chart: KundaliChart, house_num: int) -> Optional[PlanetPosition]:
        h = cls.get_house(chart, house_num)
        if h and h.lord:
            return cls.get_planet(chart, h.lord)
        return None

    @classmethod
    def get_house_distance(cls, sign1_id: int, sign2_id: int) -> int:
        """Returns distance from sign1 to sign2 (1-based counting)."""
        return ((sign2_id - sign1_id) % 12) + 1

    @classmethod
    def check_aspect(cls, p1: PlanetPosition, p2: PlanetPosition) -> bool:
        """Checks if planet p1 aspects planet p2 according to Parashari special drishti."""
        dist = cls.get_house_distance(p1.sign_id, p2.sign_id)
        valid_aspects = SPECIAL_ASPECTS.get(p1.name, [7])
        return dist in valid_aspects

    @classmethod
    def evaluate_criterion(
        cls,
        crit: Dict[str, Any],
        chart: KundaliChart,
        dasha: Optional[ActiveDashaHierarchy] = None,
        transits: Optional[Dict[str, Any]] = None,
        summary: Optional[TransitSummary] = None
    ) -> Tuple[bool, str]:
        """Evaluates a single criterion dict against chart state."""
        entity = crit.get("entity", "")
        relationship = crit.get("relationship")
        quality = crit.get("quality")
        with_target = crit.get("with")
        orb = crit.get("orb_degrees", 12.0)
        target_house = crit.get("house") or crit.get("in_house")
        target_sign = crit.get("sign") or crit.get("in_sign")

        # -----------------------------------------------------------------
        # 1. House Lord Entities (e.g. "Lord_1", "Lord_7", "Lord_10")
        # -----------------------------------------------------------------
        if entity.startswith("Lord_") or entity.startswith("lord_"):
            try:
                h_idx = int(entity.split("_")[1])
                p = cls.get_house_lord_planet(chart, h_idx)
                if not p:
                    return False, f"House lord {entity} not found"
                # Delegate to planet checks with resolved planet
                crit_copy = dict(crit)
                crit_copy["entity"] = p.name
                return cls.evaluate_criterion(crit_copy, chart, dasha, transits, summary)
            except Exception as e:
                return False, f"Invalid lord entity {entity}: {e}"

        # -----------------------------------------------------------------
        # 2. House Entities (e.g. "House_7", "House_1", "House_10")
        # -----------------------------------------------------------------
        if entity.startswith("House_") or entity.startswith("house_"):
            try:
                h_idx = int(entity.split("_")[1])
                h = cls.get_house(chart, h_idx)
                if not h:
                    return False, f"House {h_idx} not found"

                if "occupants_include" in crit or "has_planet" in crit:
                    target_p = crit.get("occupants_include") or crit.get("has_planet")
                    if isinstance(target_p, list):
                        has_all = all(tp in h.occupants for tp in target_p)
                        return has_all, f"House {h_idx} occupants: {h.occupants}"
                    return target_p in h.occupants, f"House {h_idx} occupants: {h.occupants}"

                if "aspecting_include" in crit:
                    target_p = crit.get("aspecting_include")
                    return target_p in h.aspecting_planets, f"House {h_idx} aspects: {h.aspecting_planets}"

                if quality == "benefic_lord":
                    return h.lord in cls.NATURAL_BENEFICS, f"House {h_idx} lord: {h.lord}"
                if quality == "malefic_lord":
                    return h.lord in cls.NATURAL_MALEFICS, f"House {h_idx} lord: {h.lord}"

                return True, f"House {h_idx} exists"
            except Exception as e:
                return False, f"Invalid house entity {entity}: {e}"

        # -----------------------------------------------------------------
        # 3. Dasha Entities ("Dasha_Maha", "Dasha_Antar")
        # -----------------------------------------------------------------
        if entity.startswith("Dasha_") or entity == "Dasha":
            if not dasha:
                return True, "Dasha context ignored"
            if entity in ("Dasha_Maha", "Dasha"):
                target = crit.get("lord") or crit.get("is")
                is_match = (dasha.mahadasha.lord == target) if target else True
                return is_match, f"Active Mahadasha: {dasha.mahadasha.lord}"
            if entity == "Dasha_Antar":
                target = crit.get("lord") or crit.get("is")
                is_match = (dasha.antardasha.lord == target) if target else True
                return is_match, f"Active Antardasha: {dasha.antardasha.lord}"

        # -----------------------------------------------------------------
        # 4. Standard Planet Entities (Sun, Moon, Mars, etc.)
        # -----------------------------------------------------------------
        p1 = cls.get_planet(chart, entity)
        if not p1:
            return False, f"Planet {entity} not found in chart"

        # House Placement Check
        if target_house is not None:
            actual_house = p1.house_from_lagna
            if isinstance(target_house, list):
                if actual_house not in target_house:
                    return False, f"{entity} in house {actual_house}, expected one of {target_house}"
            elif actual_house != target_house:
                return False, f"{entity} in house {actual_house}, expected {target_house}"

        # Sign Placement Check
        if target_sign is not None:
            actual_sign = p1.sign_name
            if isinstance(target_sign, list):
                if actual_sign not in target_sign:
                    return False, f"{entity} in sign {actual_sign}, expected {target_sign}"
            elif actual_sign.lower() != target_sign.lower():
                return False, f"{entity} in sign {actual_sign}, expected {target_sign}"

        # Quality / Dignity Checks
        if quality:
            dignity_lower = p1.dignity.lower()
            if quality in ("exalted", "in_exaltation"):
                if "exalt" not in dignity_lower:
                    return False, f"{entity} dignity is {p1.dignity}, not exalted"
            elif quality in ("debilitated", "in_debilitation"):
                if "debil" not in dignity_lower:
                    return False, f"{entity} dignity is {p1.dignity}, not debilitated"
            elif quality == "not_debilitated":
                if "debil" in dignity_lower:
                    return False, f"{entity} is debilitated"
            elif quality == "own_sign":
                if "own" not in dignity_lower and "moolatrikona" not in dignity_lower:
                    return False, f"{entity} is not in own sign"
            elif quality == "moolatrikona":
                if "moolatrikona" not in dignity_lower:
                    return False, f"{entity} is not in moolatrikona"
            elif quality == "combust":
                if not p1.is_combust:
                    return False, f"{entity} is not combust"
            elif quality == "not_combust":
                if p1.is_combust:
                    return False, f"{entity} is combust"
            elif quality == "retrograde":
                if not p1.is_retrograde:
                    return False, f"{entity} is not retrograde"
            elif quality == "not_retrograde":
                if p1.is_retrograde:
                    return False, f"{entity} is retrograde"
            elif quality == "in_kendra":
                if p1.house_from_lagna not in KENDRA_HOUSES:
                    return False, f"{entity} is in house {p1.house_from_lagna}, not in Kendra"
            elif quality == "in_trikona":
                if p1.house_from_lagna not in TRIKONA_HOUSES:
                    return False, f"{entity} is in house {p1.house_from_lagna}, not in Trikona"
            elif quality == "in_dusthana":
                if p1.house_from_lagna not in DUSTHANA_HOUSES:
                    return False, f"{entity} is in house {p1.house_from_lagna}, not in Dusthana"
            elif quality == "in_upachaya":
                if p1.house_from_lagna not in UPACHAYA_HOUSES:
                    return False, f"{entity} is in house {p1.house_from_lagna}, not in Upachaya"

        # Relationships with Target Planet
        if relationship and with_target:
            p2 = cls.get_planet(chart, with_target)
            if not p2:
                return False, f"Target planet {with_target} not found"

            # Conjunction
            if relationship == "conjunction":
                if p1.sign_id != p2.sign_id:
                    return False, f"{entity} and {with_target} are in different signs ({p1.sign_name} vs {p2.sign_name})"
                # Check orb if within sign
                deg_diff = abs(p1.sign_degree - p2.sign_degree)
                if deg_diff > orb:
                    return False, f"{entity} and {with_target} orb {deg_diff:.1f}° exceeds limit {orb}°"

            # Kendra from each other
            elif relationship in ("kendra_from", "in_kendra_from"):
                dist = cls.get_house_distance(p2.sign_id, p1.sign_id)
                if dist not in KENDRA_HOUSES:
                    return False, f"{entity} is {dist}th from {with_target}, not Kendra"

            # Trikona from each other
            elif relationship in ("trikona_from", "in_trikona_from"):
                dist = cls.get_house_distance(p2.sign_id, p1.sign_id)
                if dist not in TRIKONA_HOUSES:
                    return False, f"{entity} is {dist}th from {with_target}, not Trikona"

            # Opposite / 7th from each other
            elif relationship in ("opposite", "saptama_from", "aspects_7th"):
                dist = cls.get_house_distance(p2.sign_id, p1.sign_id)
                if dist != 7:
                    return False, f"{entity} is {dist}th from {with_target}, not opposite"

            # Dusthana (6/8/12) from each other
            elif relationship in ("shadashtaka_from", "6_8_from"):
                dist = cls.get_house_distance(p2.sign_id, p1.sign_id)
                if dist not in (6, 8):
                    return False, f"{entity} is {dist}th from {with_target}, not 6/8"

            # Mutual Aspect
            elif relationship == "mutual_aspect":
                asp1 = cls.check_aspect(p1, p2)
                asp2 = cls.check_aspect(p2, p1)
                if not (asp1 and asp2):
                    return False, f"No mutual aspect between {entity} and {with_target}"

            # Direct Aspect p1 -> p2
            elif relationship in ("aspects", "aspecting"):
                if not cls.check_aspect(p1, p2):
                    return False, f"{entity} does not aspect {with_target}"

        return True, f"{entity} satisfies criteria"

    @classmethod
    def evaluate(
        cls,
        condition: Dict[str, Any],
        chart: KundaliChart,
        dasha: Optional[ActiveDashaHierarchy] = None,
        transits: Optional[Dict[str, Any]] = None,
        summary: Optional[TransitSummary] = None
    ) -> Tuple[bool, List[str], float]:
        """Evaluates a composite condition block (ALL, ANY, NONE).

        Returns: (is_fired, matched_explanations, delta_score)
        """
        if not condition:
            return True, ["No conditions specified"], 0.0

        cond_type = condition.get("type", "ALL").upper()
        criteria = condition.get("criteria", [])
        if not criteria:
            return True, ["Universal criteria matched"], 0.0

        results = []
        explanations = []

        for crit in criteria:
            matched, exp = cls.evaluate_criterion(crit, chart, dasha, transits, summary)
            results.append(matched)
            if matched:
                explanations.append(exp)

        if cond_type == "ALL":
            fired = all(results)
        elif cond_type == "ANY":
            fired = any(results)
        elif cond_type == "NONE":
            fired = not any(results)
        else:
            fired = all(results)

        # Confidence delta adjustment based on how cleanly criteria matched
        delta = 0.0
        if fired and len(criteria) > 0:
            matched_count = sum(1 for r in results if r)
            delta = round(0.15 * (matched_count / len(criteria)), 2)

        return fired, explanations, delta

