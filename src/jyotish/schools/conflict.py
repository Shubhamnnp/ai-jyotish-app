"""
Shastriya Conflict Precedence & Resolution Engine.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T9).

Governs internal conflict resolution within an astrological school:
1. Vishesha (Specific) overrides Samanya (General).
2. Bhanga (Cancellation) overrides Dosha/Debility.
3. Viparita Raja Yoga overrides Dusthana affliction.
4. Shadbala Strength Dominance when opposing planetary forces contest a bhava.
"""

from typing import Dict, List, Optional, Tuple
from ..core.models import KundaliChart, PlanetPosition
from ..core.constants import KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES, SIGN_LORDS
from .base import PrecedenceRecord, PrecedencePrinciple, Finding


class ShastriyaPrecedenceEngine:
    """Evaluates and resolves astrological rule conflicts using classical precedence."""

    @staticmethod
    def resolve_neechabhanga_precedence(
        chart: KundaliChart,
        planet_name: str
    ) -> Optional[PrecedenceRecord]:
        """
        If a planet is debilitated but possesses Neechabhanga, the cancellation
        overrides the simple debility rule under classical Vishesha precedence.
        """
        pos = chart.planets.get(planet_name)
        if not pos or pos.dignity != "debilitated":
            return None

        # Check Neechabhanga condition: dispositor in Kendra from Lagna or Moon
        sign_lord = SIGN_LORDS.get(pos.sign_name)
        lord_p = chart.planets.get(sign_lord)
        if lord_p and (lord_p.house_from_lagna in KENDRA_HOUSES or lord_p.house_from_moon in KENDRA_HOUSES):
            return PrecedenceRecord(
                dominant_rule_id=f"BPHS-NEECHABHANGA-{planet_name.upper()}",
                overridden_rule_id=f"GEN-DEBILITY-{planet_name.upper()}",
                principle=PrecedencePrinciple.BHANGA_CANCELLATION,
                explanation_en=(
                    f"{planet_name} is debilitated in {pos.sign_name}, but its dispositor {sign_lord} "
                    f"is placed in Kendra (H{lord_p.house_from_lagna} from Lagna / H{lord_p.house_from_moon} from Moon), "
                    f"activating Neechabhanga Raja Yoga. The debility is cancelled and converts into eventual elevation."
                ),
                explanation_hi=(
                    f"{planet_name} {pos.sign_name} राशि में नीचस्थ है, परंतु इसका राशि स्वामी {sign_lord} "
                    f"केंद्र में स्थित होने से नीचभंग राजयोग सक्रिय होता है। नीच फल निष्प्रभावी होकर उत्थानकारी बनता है।"
                )
            )
        return None

    @staticmethod
    def resolve_kemadruma_precedence(chart: KundaliChart) -> Optional[PrecedenceRecord]:
        """
        Kemadruma Bhanga (Cancellation):
        When evaluating Moon dosha, if Moon or benefics (Jupiter, Venus, Mercury)
        occupy Kendra (1, 4, 7, 10) from Lagna or Moon, Kemadruma Bhanga applies
        and cancels the solitary Moon affliction.
        """
        moon = chart.planets.get("Moon")
        if not moon:
            return None

        # Check Kendra cancellation
        kendra_benefics = [
            p for p in ("Jupiter", "Venus", "Mercury")
            if (chart.planets.get(p) and (
                chart.planets[p].house_from_lagna in KENDRA_HOUSES or
                chart.planets[p].house_from_moon in KENDRA_HOUSES
            ))
        ]
        moon_in_kendra = moon.house_from_lagna in KENDRA_HOUSES

        if kendra_benefics or moon_in_kendra:
            reasons = []
            if moon_in_kendra:
                reasons.append("चन्द्रमा स्वयं केंद्र में स्थित है (Moon in Kendra)")
            if kendra_benefics:
                reasons.append(f"शुभ ग्रह केंद्र में स्थित हैं ({', '.join(kendra_benefics)})")

            return PrecedenceRecord(
                dominant_rule_id="BPHS-KEMADRUMA-BHANGA",
                overridden_rule_id="GEN-KEMADRUMA-DOSHA",
                principle=PrecedencePrinciple.BHANGA_CANCELLATION,
                explanation_en=(
                    f"Kemadruma Bhanga applies: {'; '.join(reasons)}. "
                    f"Classical Kemadruma dosha is cancelled by Kendra planetary placements."
                ),
                explanation_hi=(
                    f"{'; '.join(reasons)} होने से शास्त्रीय केमद्रुम भंग राजयोग लागू होता है।"
                )
            )
        return None

    @staticmethod
    def resolve_viparita_precedence(chart: KundaliChart) -> List[PrecedenceRecord]:
        """
        If a trik/dusthana lord (6, 8, 12) is in another dusthana house
        and unafflicted by benefic kendra/trikona lords, Viparita Raja Yoga overrides the dusthana affliction.
        """
        records: List[PrecedenceRecord] = []
        DUSTHANAS = {6, 8, 12}

        for lord_house in [6, 8, 12]:
            lord_sign = chart.houses[lord_house - 1].sign_name
            planet_name = SIGN_LORDS.get(lord_sign)
            if not planet_name:
                continue

            pos = chart.planets.get(planet_name)
            if not pos:
                continue

            target_house = pos.house_from_lagna
            if target_house in DUSTHANAS and target_house != lord_house:
                yoga_name = "Harsha" if lord_house == 6 else ("Sarala" if lord_house == 8 else "Vimala")
                records.append(
                    PrecedenceRecord(
                        dominant_rule_id=f"BPHS-VIPARITA-{yoga_name.upper()}",
                        overridden_rule_id=f"GEN-DUSTHANA-AFFLICTION-H{lord_house}",
                        principle=PrecedencePrinciple.VIPARITA_OVERRIDE,
                        explanation_en=(
                            f"{lord_house}th lord {planet_name} placed in {target_house}th house forms "
                            f"{yoga_name} Viparita Raja Yoga (BPHS/Uttarakalamrita). The evil of dusthana lordship "
                            f"is inverted into unexpected elevation and victory over obstacles."
                        ),
                        explanation_hi=(
                            f"{lord_house} भाव का स्वामी {planet_name} {target_house} भाव में स्थित होकर "
                            f"{yoga_name} विपरीत राजयोग बनाता है। त्रिक भाव का दोष भंग होकर संघर्षों पर विजय दिलाता है।"
                        )
                    )
                )
        return records

    @staticmethod
    def resolve_shadbala_precedence(
        p1_name: str,
        p1_ratio: float,
        p2_name: str,
        p2_ratio: float,
        house_num: int
    ) -> PrecedenceRecord:
        """
        When two planets exert opposing influences on house_num,
        the planet with higher Shadbala ratio commands dominant authority.
        """
        if p1_ratio >= p2_ratio:
            dominant, dominant_ratio = p1_name, p1_ratio
            subordinate, sub_ratio = p2_name, p2_ratio
        else:
            dominant, dominant_ratio = p2_name, p2_ratio
            subordinate, sub_ratio = p1_name, p1_ratio

        return PrecedenceRecord(
            dominant_rule_id=f"SHADBALA-DOMINANCE-{dominant.upper()}-H{house_num}",
            overridden_rule_id=f"SHADBALA-SUBORDINATE-{subordinate.upper()}-H{house_num}",
            principle=PrecedencePrinciple.SHADBALA_DOMINANCE,
            explanation_en=(
                f"{dominant} (Shadbala ratio {dominant_ratio:.2f}) possesses higher potency than "
                f"{subordinate} (Shadbala ratio {sub_ratio:.2f}) over House {house_num}. "
                f"Its classical indications take shastriya precedence."
            ),
            explanation_hi=(
                f"{dominant} का षड्बल अनुपात ({dominant_ratio:.2f}) {subordinate} ({sub_ratio:.2f}) "
                f"से अधिक होने के कारण भाव {house_num} पर इसका शास्त्रीय प्रभाव प्रभावी रहेगा।"
            )
        )
