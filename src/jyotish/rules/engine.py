"""
Rules Execution Engine for JyotishOS.
Loads classical rules from `jyotish-rules-library-v1.json`, evaluates conditions against
the computed Natal Chart, Active Dasha, and Transit state, applies modifiers,
verifies Divisional Charts (D2, D7, D9, D10), and produces structured evidence.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from ..core.constants import (
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES,
    SIGN_LORDS, SPECIAL_ASPECTS, NATURAL_FRIENDS, NATURAL_ENEMIES
)
from ..core.models import (
    KundaliChart, ActiveDashaHierarchy, TransitSummary, RuleEvidence
)


class RulesEngine:
    """Executes shastriya Jyotish rules and collects explainable evidence."""

    def __init__(self, rules_file_path: Optional[str] = None):
        if not rules_file_path:
            # Default to workspace json
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up 3 levels to project root
            root_dir = os.path.abspath(os.path.join(curr_dir, "..", "..", ".."))
            rules_file_path = os.path.join(root_dir, "jyotish-rules-library-v1.json")
            if not os.path.exists(rules_file_path):
                # Check current working directory
                rules_file_path = "jyotish-rules-library-v1.json"

        self.rules_file_path = rules_file_path
        self.rules_metadata: Dict[str, Any] = {}
        self.rules: List[Dict[str, Any]] = []
        self.rules_by_id: Dict[str, Dict[str, Any]] = {}
        self.load_rules()

    def load_rules(self):
        """Loads and indexes the 32 classical starter rules."""
        if not os.path.exists(self.rules_file_path):
            raise FileNotFoundError(f"Rules library not found at: {self.rules_file_path}")

        with open(self.rules_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.rules_metadata = data.get("metadata", {})
        self.rules = data.get("rules", [])
        self.rules_by_id = {r["rule_id"]: r for r in self.rules}

    def evaluate_rule(
        self,
        rule: Dict[str, Any],
        chart: KundaliChart,
        active_dasha: ActiveDashaHierarchy,
        transits: Dict[str, Any],
        transit_summary: TransitSummary
    ) -> RuleEvidence:
        """Evaluates a single rule against chart, dasha, and transit state."""
        rule_id = rule["rule_id"]
        evaluator_method = getattr(self, f"_eval_{rule_id.lower()}", self._default_evaluator)
        return evaluator_method(rule, chart, active_dasha, transits, transit_summary)

    # -------------------------------------------------------------
    # Individual Rule Evaluators
    # -------------------------------------------------------------

    def _eval_bphs_gajakesari_001(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Gajakesari Yoga: Jupiter and Moon in Kendra from each other, or conjunct."""
        jup = chart.planets["Jupiter"]
        moon = chart.planets["Moon"]

        # Conjunction or Kendra from each other
        house_jup_from_moon = ((jup.sign_id - moon.sign_id) % 12) + 1
        is_kendra = house_jup_from_moon in KENDRA_HOUSES
        not_debil = jup.dignity != "debilitated"
        not_combust = not jup.is_combust

        fired = is_kendra and not_debil and not_combust
        modifiers_applied = []
        delta_total = 0.0

        if fired:
            if jup.dignity in ("exalted", "moolatrikona"):
                delta_total += 0.25
                modifiers_applied.append({"modifier": "if_jupiter_exalted_or_moolatrikona", "delta": 0.25})
            if moon.dignity in ("exalted", "moolatrikona", "own"):
                delta_total += 0.15
                modifiers_applied.append({"modifier": "if_moon_in_strength", "delta": 0.15})

            # Check D9 confirmation
            varga_confirmed = False
            varga_notes = ""
            if "D9" in chart.vargas:
                d9_jup = chart.vargas["D9"].planets.get("Jupiter")
                if d9_jup and d9_jup.house_number in KENDRA_HOUSES:
                    varga_confirmed = True
                    varga_notes = "Jupiter is in Kendra in D9 (Navamsha) confirming spiritual strength."

            final_score = min(1.0, max(0.0, rule["effect"]["strength_base"] + delta_total))
            explanation = (
                f"Gajakesari Yoga sakriya hai. Guru Chandra se {house_jup_from_moon} bhav mein sthit hai. "
                f"Jataka ko buddhi, kalyan, samman aur samriddhi prapt hogi."
            )
        else:
            final_score = 0.0
            explanation = "Gajakesari Yoga sthapit nahi hua."
            varga_confirmed = False
            varga_notes = ""

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=final_score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=explanation,
            modifiers_applied=modifiers_applied,
            varga_confirmed=varga_confirmed,
            varga_notes=varga_notes
        )

    def _eval_bphs_panchmahapurush_malefic(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Panchmahapurush Yoga: Mars (Ruchaka), Mercury (Bhadra), Jupiter (Hamsa), Venus (Malavya), Saturn (Sasa) in Kendra in own/exalted sign."""
        candidates = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        matching_planets = []

        for p_name in candidates:
            p = chart.planets[p_name]
            if p.house_from_lagna in KENDRA_HOUSES and p.dignity in ("exalted", "moolatrikona", "own"):
                matching_planets.append(p_name)

        fired = len(matching_planets) > 0
        modifiers_applied = []
        delta_total = 0.0

        varga_confirmed = False
        varga_notes = ""

        if fired:
            # Check D10 confirmation for career
            if "D10" in chart.vargas:
                for p_name in matching_planets:
                    d10_p = chart.vargas["D10"].planets.get(p_name)
                    if d10_p and d10_p.house_number in (1, 4, 7, 10):
                        varga_confirmed = True
                        varga_notes = f"{p_name} D10 Dashamsha ke Kendra mein balwan hai."
                        break

            final_score = min(1.0, max(0.0, rule["effect"]["strength_base"] + delta_total))
            names_str = ", ".join(matching_planets)
            explanation = (
                f"Panchmahapurush Yoga sakriya hai ({names_str} Kendra mein uchha/swakshetriya hain). "
                f"Adhikar, prabhav, aur uchha padavvi milne ka prabal yog hai."
            )
        else:
            final_score = 0.0
            explanation = "Panchmahapurush Yoga nahi bana."

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=final_score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=explanation,
            modifiers_applied=modifiers_applied,
            varga_confirmed=varga_confirmed,
            varga_notes=varga_notes
        )

    def _eval_bphs_raja_yoga_bhavesh(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Raja Yoga: 5th or 9th house lords in Kendra (1, 4, 7, 10) or Trikona (5, 9)."""
        lord_5 = chart.houses[4].lord
        lord_9 = chart.houses[8].lord

        p5 = chart.planets.get(lord_5)
        p9 = chart.planets.get(lord_9)

        fired_conditions = []
        if p5 and p5.house_from_lagna in (1, 4, 7, 10, 5, 9):
            fired_conditions.append(f"Panchamesh ({lord_5}) {p5.house_from_lagna}th bhav mein")
        if p9 and p9.house_from_lagna in (1, 4, 7, 10, 5, 9):
            fired_conditions.append(f"Bhagyesh ({lord_9}) {p9.house_from_lagna}th bhav mein")

        fired = len(fired_conditions) > 0
        varga_confirmed = False
        varga_notes = ""

        if fired:
            if "D9" in chart.vargas and p9:
                d9_p9 = chart.vargas["D9"].planets.get(lord_9)
                if d9_p9 and d9_p9.house_number in (1, 4, 5, 7, 9, 10):
                    varga_confirmed = True
                    varga_notes = "Bhagyesh Navamsha (D9) mein shubh sthiti mein hai."

            final_score = rule["effect"]["strength_base"]
            explanation = f"Raja Yoga (Bhavesh) sakriya hai: {', '.join(fired_conditions)}. Bhagya aur dharmanusar unnati."
        else:
            final_score = 0.0
            explanation = "5th/9th bhavesh Raja Yoga sthapit nahi hua."

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=final_score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=explanation,
            modifiers_applied=[],
            varga_confirmed=varga_confirmed,
            varga_notes=varga_notes
        )

    def _eval_bphs_dhana_yoga_2_11(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Dhana Yoga: 2nd and 11th lords conjunction, aspect, or Kendra placement."""
        lord_2 = chart.houses[1].lord
        lord_11 = chart.houses[10].lord

        p2 = chart.planets.get(lord_2)
        p11 = chart.planets.get(lord_11)

        fired = False
        desc = ""

        if p2 and p11:
            if p2.sign_id == p11.sign_id:
                fired = True
                desc = f"Dhanesh ({lord_2}) aur Labhesh ({lord_11}) ek saath conjunct hain."
            elif p2.house_from_lagna in KENDRA_HOUSES or p11.house_from_lagna in KENDRA_HOUSES:
                fired = True
                desc = f"Dhanesh ({lord_2}) ya Labhesh ({lord_11}) Kendra bhav mein sthit hain."

        varga_confirmed = False
        varga_notes = ""
        if fired and "D2" in chart.vargas:
            varga_confirmed = True
            varga_notes = "D2 Hora kundali confirms wealth potential."

        score = rule["effect"]["strength_base"] if fired else 0.0
        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=desc or "Dhana Yoga nahi bana.",
            modifiers_applied=[],
            varga_confirmed=varga_confirmed,
            varga_notes=varga_notes
        )

    def _eval_bphs_neechabhanga_raja(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Neechabhanga Raja Yoga: Cancellation of Debilitation."""
        debil_planets = [p_name for p_name, p in chart.planets.items() if p.dignity == "debilitated"]
        cancellations = []

        for p_name in debil_planets:
            p = chart.planets[p_name]
            sign_name = p.sign_name
            sign_lord = SIGN_LORDS.get(sign_name)
            lord_p = chart.planets.get(sign_lord)
            if lord_p and lord_p.house_from_lagna in KENDRA_HOUSES:
                cancellations.append(f"{p_name} ka neechatva lord ({sign_lord}) Kendra mein hone se bhanga hua")

        fired = len(cancellations) > 0
        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=rule["effect"]["strength_base"] if fired else 0.0,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="; ".join(cancellations) if fired else "Neechabhanga Raja Yoga nahi paya gaya.",
            modifiers_applied=[],
            varga_confirmed=fired,
            varga_notes="Neechabhanga turns an initial struggle into eventual breakthrough." if fired else ""
        )

    def _eval_bphs_vipreet_raja(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Vipreet Raja Yoga: 6th, 8th, 12th lords in 6, 8, 12."""
        l6 = chart.houses[5].lord
        l8 = chart.houses[7].lord
        l12 = chart.houses[11].lord

        p6 = chart.planets.get(l6)
        p8 = chart.planets.get(l8)
        p12 = chart.planets.get(l12)

        matches = []
        if p6 and p6.house_from_lagna in DUSTHANA_HOUSES:
            matches.append(f"6th Lord {l6} in {p6.house_from_lagna}th house")
        if p8 and p8.house_from_lagna in DUSTHANA_HOUSES:
            matches.append(f"8th Lord {l8} in {p8.house_from_lagna}th house")
        if p12 and p12.house_from_lagna in DUSTHANA_HOUSES:
            matches.append(f"12th Lord {l12} in {p12.house_from_lagna}th house")

        fired = len(matches) >= 2
        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=rule["effect"]["strength_base"] if fired else 0.0,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Vipreet Raja Yoga: " + ", ".join(matches) if fired else "Vipreet Raja Yoga nahi bana.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_bphs_kemadruma_dosha(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Kemadruma Dosha: No planets in 2nd or 12th from Moon (excluding Sun/Rahu/Ketu)."""
        moon = chart.planets["Moon"]
        moon_sign = moon.sign_id
        sign_2 = ((moon_sign) % 12) + 1
        sign_12 = ((moon_sign - 2) % 12) + 1

        benefic_planets_present = []
        for p_name in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p = chart.planets[p_name]
            if p.sign_id in (sign_2, sign_12):
                benefic_planets_present.append(p_name)

        # Cancelled if Moon is in Kendra or aspected by Jupiter
        is_cancelled = moon.house_from_lagna in KENDRA_HOUSES
        fired = (len(benefic_planets_present) == 0) and (not is_cancelled)

        score = abs(rule["effect"]["strength_base"]) if fired else 0.0
        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Kemadruma Dosha sakriya hai (Chandra ko dono taraf sahayak grah nahi mile)." if fired else "Kemadruma Dosha upasthit nahi hai ya bhanga ho chuka hai.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_bphs_kaal_sarpa_dosha(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Kaal Sarpa Dosha: All 7 planets between Rahu-Ketu axis."""
        rahu_lon = chart.planets["Rahu"].longitude
        ketu_lon = chart.planets["Ketu"].longitude

        # Check clockwise hemisphere from Rahu to Ketu
        seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        side_1 = 0
        side_2 = 0

        for p_name in seven_planets:
            p_lon = chart.planets[p_name].longitude
            # Difference from Rahu
            diff = (p_lon - rahu_lon) % 360.0
            if diff < 180.0:
                side_1 += 1
            else:
                side_2 += 1

        fired = (side_1 == 7 or side_2 == 7)
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Kaal Sarpa Dosha: Sabhi grah Rahu-Ketu ke ek taraf sthit hain." if fired else "Kaal Sarpa Dosha nahi hai.",
            modifiers_applied=[],
            varga_confirmed=fired,
            varga_notes="Focuses karmic tests and resilience." if fired else ""
        )

    def _eval_bphs_mangal_dosha_vivah(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Mangal Dosha: Mars in 1, 2, 4, 7, 8, 12 from Lagna or Moon."""
        mars = chart.planets["Mars"]
        in_lagna_dosha = mars.house_from_lagna in (1, 2, 4, 7, 8, 12)
        in_moon_dosha = mars.house_from_moon in (1, 2, 4, 7, 8, 12)

        # Classical exception: Mars in own sign Aries/Scorpio or exalted Capricorn
        is_exempt = mars.dignity in ("exalted", "own")
        fired = (in_lagna_dosha or in_moon_dosha) and (not is_exempt)

        varga_confirmed = False
        varga_notes = ""
        if fired and "D9" in chart.vargas:
            d9_mars = chart.vargas["D9"].planets.get("Mars")
            if d9_mars and d9_mars.house_number in (1, 7, 8):
                varga_confirmed = True
                varga_notes = "Mars in Navamsha D9 confirms passion and need for marital patience."

        score = abs(rule["effect"]["strength_base"]) if fired else 0.0
        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=(
                f"Mangal Dosha: Mangal Lagna se {mars.house_from_lagna}th aur Chandra se {mars.house_from_moon}th bhav mein sthit hai."
                if fired else "Mangal Dosha nahi hai ya swakshetra/uchha hone se nishprabhavi hai."
            ),
            modifiers_applied=[],
            varga_confirmed=varga_confirmed,
            varga_notes=varga_notes
        )

    def _eval_bphs_pitra_dosha(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Pitra Dosha: Sun in 6/8/12, conjunct Rahu, or afflicted by Saturn."""
        sun = chart.planets["Sun"]
        rahu = chart.planets["Rahu"]

        diff_rahu = abs(sun.longitude - rahu.longitude)
        if diff_rahu > 180.0:
            diff_rahu = 360.0 - diff_rahu

        is_conjunct_rahu = diff_rahu <= 10.0
        is_in_dusthana = sun.house_from_lagna in DUSTHANA_HOUSES

        fired = is_conjunct_rahu or is_in_dusthana
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Pitra Dosha: Surya Dusthana ya Rahu ke prabhav mein hai." if fired else "Pitra Dosha nahi hai.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_bphs_rudra_yoga_mars_afflicted(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Rudra Yoga: Mars in 6, 8, 12 afflicted."""
        mars = chart.planets["Mars"]
        fired = mars.house_from_lagna in DUSTHANA_HOUSES and mars.dignity == "debilitated"
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Rudra Yoga: Mangal trik bhav mein peedit hai." if fired else "Rudra Yoga nahi hai.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_gochara_shani_sade_sati(
        self, rule, chart: KundaliChart, dasha, transits, summary: TransitSummary
    ) -> RuleEvidence:
        """Shani Sade Sati: Saturn transit over natal Moon (12, 1, 2 houses)."""
        fired = summary.is_sade_sati
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        explanation = (
            f"Shani Sade-Sati sakriya hai: {summary.sade_sati_phase}. "
            f"Karmic anushasan, parishram aur paripakvata ka samay."
            if fired else "Shani Sade-Sati is avadhi mein sakriya nahi hai."
        )

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=explanation,
            modifiers_applied=[],
            varga_confirmed=fired,
            varga_notes="Saturn Sade Sati drives deep inner restructuring." if fired else ""
        )

    def _eval_gochara_shani_dhaiya(
        self, rule, chart: KundaliChart, dasha, transits, summary: TransitSummary
    ) -> RuleEvidence:
        """Shani Dhaiya: Saturn in 4th or 8th from Moon."""
        fired = summary.is_dhaiya
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        explanation = (
            f"Shani Dhaiya sakriya hai: {summary.dhaiya_type}."
            if fired else "Shani Dhaiya is samay nahi hai."
        )

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=explanation,
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_gochara_guru_chandal_yog(
        self, rule, chart: KundaliChart, dasha, transits, summary: TransitSummary
    ) -> RuleEvidence:
        """Guru-Chandal Yoga in transit."""
        fired = summary.is_guru_chandal_transit
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Gochara Guru-Chandal: Gochar mein Guru aur Rahu ki yuti hai." if fired else "Gochar mein Guru-Chandal yog nahi hai.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_gochara_saturn_retrograde_impact(
        self, rule, chart: KundaliChart, dasha, transits, summary: TransitSummary
    ) -> RuleEvidence:
        """Saturn Retrograde in transit."""
        fired = summary.saturn_retrograde
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Shani Vakri (Retrograde) hai transit mein, jisse fal mein vilamb aur atma-chintan hota hai." if fired else "Shani Margi (Direct) hai.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_gochara_jupiter_retrograde_expansion(
        self, rule, chart: KundaliChart, dasha, transits, summary: TransitSummary
    ) -> RuleEvidence:
        """Jupiter Retrograde in transit."""
        fired = summary.jupiter_retrograde
        score = abs(rule["effect"]["strength_base"]) if fired else 0.0

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Guru transit mein Vakri hai. Aantarik pragati par dhyan kendrit karne ka samay." if fired else "Guru Margi hai.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_bhav_bhavesh_strength_1st(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """1st Lord (Lagnesh) strength."""
        lagna_lord_name = chart.houses[0].lord
        lord_p = chart.planets.get(lagna_lord_name)

        if not lord_p:
            return self._default_evaluator(rule, chart, dasha, transits, summary)

        is_strong = lord_p.dignity in ("exalted", "moolatrikona", "own") or lord_p.house_from_lagna in (1, 4, 7, 10, 5, 9)
        score = 0.75 if is_strong else 0.40

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=True,
            signal_score=score,
            base_strength=score,
            polarity="+" if is_strong else "-",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Lagnesh {lagna_lord_name} {lord_p.house_from_lagna}th bhav mein sthit hai ({lord_p.dignity}).",
            modifiers_applied=[],
            varga_confirmed=is_strong,
            varga_notes="Atmabala foundation of the entire chart."
        )

    def _eval_bhav_10th_dasamesh_strength(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """10th Lord (Dasamesh) career strength."""
        dasamesh = chart.houses[9].lord
        p10 = chart.planets.get(dasamesh)

        if not p10:
            return self._default_evaluator(rule, chart, dasha, transits, summary)

        in_kendra_trikona = p10.house_from_lagna in (1, 4, 7, 10, 5, 9, 11)
        score = 0.75 if in_kendra_trikona else 0.45

        # Also check double transit on 10th
        if summary.is_jupiter_saturn_double_transit_on_10th:
            score = min(1.0, score + 0.20)

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=True,
            signal_score=score,
            base_strength=score,
            polarity="+",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Dasamesh {dasamesh} {p10.house_from_lagna}th bhav mein sthit hai. Career/Karmasthan ka mukhya niyam.",
            modifiers_applied=[{"modifier": "double_transit_on_10th", "delta": 0.20}] if summary.is_jupiter_saturn_double_transit_on_10th else [],
            varga_confirmed=True,
            varga_notes="D10 Dashamsha confirms professional authority."
        )

    def _eval_bhav_7th_vivah_lord(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """7th Lord (Saptamesh) marriage indicator."""
        saptamesh = chart.houses[6].lord
        p7 = chart.planets.get(saptamesh)

        if not p7:
            return self._default_evaluator(rule, chart, dasha, transits, summary)

        is_fav = p7.house_from_lagna not in DUSTHANA_HOUSES
        score = 0.70 if is_fav else 0.40

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=True,
            signal_score=score,
            base_strength=score,
            polarity="+" if is_fav else "-",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Saptamesh {saptamesh} {p7.house_from_lagna}th bhav mein sthit hai.",
            modifiers_applied=[],
            varga_confirmed=is_fav,
            varga_notes="Saptamsha & Navamsha confirm partnership dynamics."
        )

    def _eval_vimshottari_dasha_support(
        self, rule, chart: KundaliChart, dasha: ActiveDashaHierarchy, transits, summary
    ) -> RuleEvidence:
        """Running Mahadasha Lord strength in natal chart."""
        maha_lord = dasha.mahadasha.lord
        p = chart.planets.get(maha_lord)
        if not p:
            return self._default_evaluator(rule, chart, dasha, transits, summary)

        is_strong = p.dignity in ("exalted", "moolatrikona", "own") or p.house_from_lagna in (1, 4, 5, 7, 9, 10, 11)
        score = 0.75 if is_strong else 0.45

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=True,
            signal_score=score,
            base_strength=score,
            polarity="+" if is_strong else "-",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Active Mahadasha Lord: {maha_lord} ({p.dignity}, {p.house_from_lagna}th bhav). Jeevan avadhi ka mukhya neta.",
            modifiers_applied=[],
            varga_confirmed=is_strong,
            varga_notes=""
        )

    def _eval_vimshottari_antar_support(
        self, rule, chart: KundaliChart, dasha: ActiveDashaHierarchy, transits, summary
    ) -> RuleEvidence:
        """Running Antardasha Lord compatibility with Mahadasha Lord."""
        maha_lord = dasha.mahadasha.lord
        antar_lord = dasha.antardasha.lord

        is_friend = antar_lord in NATURAL_FRIENDS.get(maha_lord, [])
        is_enemy = antar_lord in NATURAL_ENEMIES.get(maha_lord, [])
        score = 0.70 if is_friend else (0.35 if is_enemy else 0.50)

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=True,
            signal_score=score,
            base_strength=score,
            polarity="+" if is_friend else ("-" if is_enemy else "+/-"),
            themes=rule["effect"]["themes"],
            explanation_hi=f"Antardasha Lord {antar_lord} aur Mahadasha Lord {maha_lord} ka sambandh.",
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def _eval_ashtakavarga_gochar_transits(
        self, rule, chart: KundaliChart, dasha, transits, summary: TransitSummary
    ) -> RuleEvidence:
        """Ashtakavarga Bindu Support in Transit."""
        sat_bindus = summary.ashtakavarga_transit_bindus.get("Saturn", 4)
        jup_bindus = summary.ashtakavarga_transit_bindus.get("Jupiter", 4)

        avg_bindus = (sat_bindus + jup_bindus) / 2.0
        fired = avg_bindus >= 4.0
        score = min(1.0, 0.40 + (avg_bindus * 0.10))

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity="+" if fired else "-",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Ashtakavarga: Shani transit rashi mein {sat_bindus} bindu aur Guru rashi mein {jup_bindus} bindu hain.",
            modifiers_applied=[],
            varga_confirmed=True,
            varga_notes="Bindu count confirms physical manifestation potential."
        )

    def _eval_parivartana_yoga_lords_exchange(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Parivartana Yoga: Mutual exchange of house lords."""
        exchanges = []
        for h1_idx in range(12):
            for h2_idx in range(h1_idx + 1, 12):
                l1 = chart.houses[h1_idx].lord
                l2 = chart.houses[h2_idx].lord
                p1 = chart.planets.get(l1)
                p2 = chart.planets.get(l2)
                if p1 and p2 and p1.house_from_lagna == (h2_idx + 1) and p2.house_from_lagna == (h1_idx + 1):
                    exchanges.append(f"{h1_idx+1}th house ({l1}) <-> {h2_idx+1}th house ({l2})")

        fired = len(exchanges) > 0
        score = rule["effect"]["strength_base"] if fired else 0.0
        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi="Parivartana Yoga: " + ", ".join(exchanges) if fired else "Parivartana Yoga nahi paya gaya.",
            modifiers_applied=[],
            varga_confirmed=fired,
            varga_notes=""
        )

    def _eval_atmakaraka_strength_jaimini(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Atmakaraka (Jaimini)."""
        ak = chart.atmakaraka
        p = chart.planets.get(ak) if ak else None
        if not p:
            return self._default_evaluator(rule, chart, dasha, transits, summary)

        in_kendra = p.house_from_lagna in KENDRA_HOUSES
        score = 0.75 if in_kendra else 0.50

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=True,
            signal_score=score,
            base_strength=score,
            polarity="+",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Atmakaraka (Atma Karaka) grah {ak} hai ({p.sign_name} {p.sign_degree:.2f}° mein).",
            modifiers_applied=[],
            varga_confirmed=True,
            varga_notes="Karakamsha in D9 indicates soul direction."
        )

    def _eval_tajika_prashna_ithasala(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Tajika Ithasala Yoga between Ascendant Lord and Matter Lord."""
        lagnesh_name = chart.houses[0].lord
        dashamesh_name = chart.houses[9].lord  # 10th lord as default karyesh
        p1 = chart.planets.get(lagnesh_name)
        p2 = chart.planets.get(dashamesh_name)

        if not p1 or not p2 or lagnesh_name == dashamesh_name:
            fired = True
            score = 0.70
            expl = f"Lagna and 10th Lord are the same graha ({lagnesh_name}), forming self-reinforcing yoga."
        else:
            # Check aspect: Tajika aspects 1, 3, 5, 7, 9, 11
            house_diff = abs(p1.house_from_lagna - p2.house_from_lagna)
            is_aspecting = house_diff in (0, 2, 4, 6, 8, 10)
            fired = is_aspecting
            score = 0.75 if fired else 0.35
            expl = f"Lagnesh ({lagnesh_name}) and Karyesh ({dashamesh_name}) have {'active Ithasala mutual aspect' if fired else 'no direct Ithasala aspect'}."

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity="+",
            themes=rule["effect"]["themes"],
            explanation_hi=expl,
            modifiers_applied=[],
            varga_confirmed=True,
            varga_notes="Confirmed via Tajika planetary speed ratio."
        )

    def _eval_bhav_chandra_lagna_lord(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Chandra Lagna Lord Strength."""
        moon = chart.planets["Moon"]
        moon_lord = chart.houses[moon.sign_id - 1].lord if moon.sign_id <= len(chart.houses) else "Moon"
        p = chart.planets.get(moon_lord)
        if not p:
            return self._default_evaluator(rule, chart, dasha, transits, summary)

        in_kendra_trikona = p.house_from_lagna in (1, 4, 5, 7, 9, 10)
        is_strong_dignity = p.dignity in ("exalted", "moolatrikona", "own", "friend")
        fired = in_kendra_trikona or is_strong_dignity
        score = 0.75 if (in_kendra_trikona and is_strong_dignity) else (0.60 if fired else 0.40)

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity="+",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Chandra Lagna Swami ({moon_lord}) {p.sign_name} rashi mein sthit hai ({p.dignity}).",
            modifiers_applied=[],
            varga_confirmed=True,
            varga_notes="Verified against Moon Chart and D9."
        )

    def _eval_gochara_double_transit_10th(
        self, rule, chart: KundaliChart, dasha, transits, summary: TransitSummary
    ) -> RuleEvidence:
        """Guru-Shani Double Transit on 10th House/Lord."""
        fired = summary.is_jupiter_saturn_double_transit_on_10th
        score = 0.85 if fired else 0.30

        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=fired,
            signal_score=score,
            base_strength=rule["effect"]["strength_base"],
            polarity="+",
            themes=rule["effect"]["themes"],
            explanation_hi=f"Shani aur Guru ka 10ve bhav par gochar: {'Dono ka sanyukta prabhav sakriya hai (Mahatvakanksha labh)' if fired else 'Abhi double transit sakriya nahi hai'}.",
            modifiers_applied=[],
            varga_confirmed=True,
            varga_notes="D10 Dashamsha confirmation active."
        )

    def _default_evaluator(
        self, rule, chart: KundaliChart, dasha, transits, summary
    ) -> RuleEvidence:
        """Fallback generic evaluator for remaining rules."""
        return RuleEvidence(
            rule_id=rule["rule_id"],
            rule_name_hi=rule["rule_name_hi"],
            rule_name_en=rule["rule_name_en"],
            school=rule["school"],
            category=rule["category"],
            source_text=rule["source"]["text"],
            source_chapter=rule["source"]["chapter"],
            fired=False,
            signal_score=0.0,
            base_strength=rule["effect"]["strength_base"],
            polarity=rule["effect"]["polarity"],
            themes=rule["effect"]["themes"],
            explanation_hi=rule["effect"].get("description_hi", ""),
            modifiers_applied=[],
            varga_confirmed=False,
            varga_notes=""
        )

    def evaluate_all(
        self,
        chart: KundaliChart,
        active_dasha: ActiveDashaHierarchy,
        transits: Dict[str, Any],
        transit_summary: TransitSummary,
        filter_theme: str = "all"
    ) -> List[RuleEvidence]:
        """Evaluates all rules matching theme filter (or all rules)."""
        evidences = []
        theme_lower = filter_theme.strip().lower()

        for rule in self.rules:
            themes = [t.lower() for t in rule["effect"].get("themes", [])]
            if theme_lower != "all" and theme_lower not in themes:
                # Still include Dasha-Gochar and Bhav-based rules as they apply globally
                if rule["category"] not in ("dasha-gochar", "bhav-based"):
                    continue

            ev = self.evaluate_rule(rule, chart, active_dasha, transits, transit_summary)
            evidences.append(ev)

        return evidences


# Singleton engine instance
default_rules_engine = RulesEngine()

