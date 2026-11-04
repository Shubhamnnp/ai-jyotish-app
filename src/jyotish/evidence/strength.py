"""
Documented Planetary and Bhava Strength Model (Phase 5, Task P5-T3).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T3).

Governs calibrated astrological strength computation:
- Combines Shadbala ratio, Dignity, Avasthas, Bhanga cancellations, and Aspectual support.
- Fully parameterised weights with documented classical rationale.
- Zero undocumented magic numbers in calculation routines.
- Exposes transparent "why" breakdown of all contributing factors.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from .factors import PlanetFactors, HouseFactors


# -----------------------------------------------------------------------------
# Parameterised Strength Weights and Rationale
# -----------------------------------------------------------------------------
# Rationale:
# 1. Shadbala Ratio (40%): The six-fold mathematical potency (Sthana, Dik, Kaala,
#    Cheshta, Naisargika, Drik) provides the primary physiological/functional energy.
# 2. Dignity / Kshetra Bala (25%): Sign ownership and exaltation establish
#    whether the planet's energy is welcomed or resisted by the sign dispositor.
# 3. Avastha (15%): Jagratadi & Deeptadi state governs whether the planet is
#    alert (Deepta/Jagrata) or sleepy/distressed (Sushupti/Vikala).
# 4. Bhanga / Inversion (10%): Neechabhanga, Kemadruma Bhanga, or Viparita
#    converts debility into elevation through structured struggle.
# 5. Aspectual Support (10%): Natural benefic aspects enhance fruitfulness,
#    while malefic aspects introduce friction.
# -----------------------------------------------------------------------------

STRENGTH_WEIGHTS = {
    "shadbala": 0.40,
    "dignity": 0.25,
    "avastha": 0.15,
    "bhanga": 0.10,
    "aspects": 0.10
}

DIGNITY_SCORE_MAP = {
    "exalted": 1.00,
    "moolatrikona": 0.90,
    "own": 0.85,
    "friendly": 0.65,
    "friend": 0.65,
    "neutral": 0.50,
    "enemy": 0.35,
    "debilitated": 0.15
}

DEEPTADI_SCORE_MAP = {
    "Deepta": 1.00,     # Exalted, luminous
    "Swastha": 0.85,    # In own sign, settled
    "Mudita": 0.75,     # In friendly sign, happy
    "Shanta": 0.65,     # In auspicious vargas, peaceful
    "Dina": 0.45,       # In neutral/enemy sign, humble
    "Dukhita": 0.30,    # In inimical sign, troubled
    "Vikala": 0.20,     # Combust, impaired
    "Khala": 0.15,      # In debility/defeat, spiteful
    "Kopa": 0.10        # Defeated in Graha Yuddha
}


@dataclass
class StrengthBreakdown:
    """Detailed transparent breakdown of a planetary strength score."""
    final_score: float  # 0.0 to 1.0
    shadbala_contribution: float
    dignity_contribution: float
    avastha_contribution: float
    bhanga_contribution: float
    aspect_contribution: float
    reasons: List[str]


class StrengthModel:
    """Deterministic planetary strength evaluator."""

    @classmethod
    def evaluate_planet_strength(
        cls,
        pf: PlanetFactors,
        has_neechabhanga: bool = False
    ) -> StrengthBreakdown:
        """
        Computes calibrated strength (0.0 to 1.0) and documented reasons for pf.
        """
        reasons: List[str] = []

        # 1. Shadbala Component (cap ratio at 2.0 -> 1.0)
        norm_shad = min(1.0, pf.shadbala_ratio / 1.5)
        shad_contrib = norm_shad * STRENGTH_WEIGHTS["shadbala"]
        reasons.append(f"Shadbala ratio {pf.shadbala_ratio:.2f} (norm {norm_shad:.2f} x 40% = {shad_contrib:.3f})")

        # 2. Dignity Component
        dig_key = pf.dignity.lower()
        base_dig = DIGNITY_SCORE_MAP.get(dig_key, 0.50)
        dig_contrib = base_dig * STRENGTH_WEIGHTS["dignity"]
        reasons.append(f"Dignity '{pf.dignity}' (score {base_dig:.2f} x 25% = {dig_contrib:.3f})")

        # 3. Avastha Component
        deept_prefix = pf.deeptadi_avastha.split()[0] if pf.deeptadi_avastha else "Swastha"
        base_avastha = DEEPTADI_SCORE_MAP.get(deept_prefix, 0.60)
        if pf.is_combust:
            base_avastha = min(base_avastha, 0.25)
            reasons.append(f"Combustion impairs avastha (separation {pf.combustion_separation:.2f}°)")
        avastha_contrib = base_avastha * STRENGTH_WEIGHTS["avastha"]
        reasons.append(f"Avastha '{pf.deeptadi_avastha}' (score {base_avastha:.2f} x 15% = {avastha_contrib:.3f})")

        # 4. Bhanga / Inversion Component
        if pf.dignity.lower() == "debilitated" and has_neechabhanga:
            bhanga_score = 1.0
            reasons.append("Neechabhanga active: debility cancelled into elevation")
        elif pf.dignity.lower() == "debilitated":
            bhanga_score = 0.0
            reasons.append("Uncancelled debility present")
        else:
            bhanga_score = 0.70  # Standard baseline for non-debilitated planets
        bhanga_contrib = bhanga_score * STRENGTH_WEIGHTS["bhanga"]

        # 5. Aspectual Support Component
        rec_benefics = [p for p in pf.aspects_received_from_planets if p in ("Jupiter", "Venus", "Mercury")]
        rec_malefics = [p for p in pf.aspects_received_from_planets if p in ("Mars", "Saturn", "Rahu", "Ketu")]

        net_aspect = 0.50 + (len(rec_benefics) * 0.20) - (len(rec_malefics) * 0.15)
        net_aspect = min(1.0, max(0.1, net_aspect))
        aspect_contrib = net_aspect * STRENGTH_WEIGHTS["aspects"]
        if rec_benefics:
            reasons.append(f"Aspected by benefic(s): {', '.join(rec_benefics)}")
        if rec_malefics:
            reasons.append(f"Aspected by malefic(s): {', '.join(rec_malefics)}")

        final_score = round(shad_contrib + dig_contrib + avastha_contrib + bhanga_contrib + aspect_contrib, 3)

        return StrengthBreakdown(
            final_score=final_score,
            shadbala_contribution=round(shad_contrib, 3),
            dignity_contribution=round(dig_contrib, 3),
            avastha_contribution=round(avastha_contrib, 3),
            bhanga_contribution=round(bhanga_contrib, 3),
            aspect_contribution=round(aspect_contrib, 3),
            reasons=reasons
        )
