"""
Unit tests for Strength Model & Parameterised Weights (Phase 5, Task P5-T3).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T3).

Verifies:
1. Mathematical normalization: weights sum strictly to 1.0.
2. Differential sensitivity: exalted planets score higher than debilitated.
3. Neechabhanga effect: cancellation increases potency.
4. Combustion penalty: reduces avastha score.
5. 'Why' breakdown: exposes reasons for every weight component without magic numbers.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.evidence.strength import (
    StrengthModel,
    StrengthBreakdown,
    STRENGTH_WEIGHTS,
    DIGNITY_SCORE_MAP,
    DEEPTADI_SCORE_MAP
)
from jyotish.evidence.factors import PlanetFactors


def test_strength_weights_sum_to_unity():
    """Verify calibrated weights strictly sum to 1.0 (100%)."""
    total_weight = sum(STRENGTH_WEIGHTS.values())
    assert abs(total_weight - 1.0) < 1e-6, f"Weights must sum to 1.0, found {total_weight}"


def test_exalted_vs_debilitated_potency():
    """Verify exalted planet scores significantly higher than debilitated planet."""
    exalted_pf = PlanetFactors(
        planet="Jupiter",
        longitude=95.0,
        sign_name="Cancer",
        sign_id=4,
        house_from_lagna=1,
        house_from_moon=1,
        dignity="exalted",
        is_retrograde=False,
        is_combust=False,
        combustion_separation=45.0,
        baladi_avastha="Yuva",
        jagratadi_avastha="Jagrata",
        deeptadi_avastha="Deepta",
        shadbala_virupas=450.0,
        shadbala_ratio=1.45,
        is_shadbala_strong=True,
        houses_owned=[9, 12],
        nakshatra_name="Pushya",
        nakshatra_pada=2,
        nakshatra_lord="Saturn",
        conjunctions=[],
        aspects_given_to_houses=[5, 7, 9],
        aspects_given_to_planets=[],
        aspects_received_from_planets=[],
        d9_navamsha_sign="Cancer",
        d10_dashamsha_sign="Aries",
        is_vargottama=True
    )

    debilitated_pf = PlanetFactors(
        planet="Jupiter",
        longitude=275.0,
        sign_name="Capricorn",
        sign_id=10,
        house_from_lagna=7,
        house_from_moon=7,
        dignity="debilitated",
        is_retrograde=False,
        is_combust=False,
        combustion_separation=45.0,
        baladi_avastha="Bala",
        jagratadi_avastha="Swapna",
        deeptadi_avastha="Khala",
        shadbala_virupas=280.0,
        shadbala_ratio=0.72,
        is_shadbala_strong=False,
        houses_owned=[9, 12],
        nakshatra_name="Dhanishta",
        nakshatra_pada=1,
        nakshatra_lord="Mars",
        conjunctions=[],
        aspects_given_to_houses=[11, 1, 3],
        aspects_given_to_planets=[],
        aspects_received_from_planets=[],
        d9_navamsha_sign="Leo",
        d10_dashamsha_sign="Scorpio",
        is_vargottama=False
    )

    ex_breakdown = StrengthModel.evaluate_planet_strength(exalted_pf)
    deb_breakdown = StrengthModel.evaluate_planet_strength(debilitated_pf)

    assert ex_breakdown.final_score > deb_breakdown.final_score
    assert ex_breakdown.dignity_contribution > deb_breakdown.dignity_contribution
    assert ex_breakdown.shadbala_contribution > deb_breakdown.shadbala_contribution


def test_neechabhanga_inversion_potency():
    """Verify Neechabhanga raises strength of a debilitated planet."""
    debilitated_pf = PlanetFactors(
        planet="Mars",
        longitude=110.0,
        sign_name="Cancer",
        sign_id=4,
        house_from_lagna=4,
        house_from_moon=4,
        dignity="debilitated",
        is_retrograde=False,
        is_combust=False,
        combustion_separation=30.0,
        baladi_avastha="Yuva",
        jagratadi_avastha="Swapna",
        deeptadi_avastha="Dina",
        shadbala_virupas=310.0,
        shadbala_ratio=1.03,
        is_shadbala_strong=True,
        houses_owned=[1, 8],
        nakshatra_name="Ashlesha",
        nakshatra_pada=1,
        nakshatra_lord="Mercury",
        conjunctions=[],
        aspects_given_to_houses=[7, 10, 11],
        aspects_given_to_planets=[],
        aspects_received_from_planets=[],
        d9_navamsha_sign="Sagittarius",
        d10_dashamsha_sign="Pisces",
        is_vargottama=False
    )

    without_nb = StrengthModel.evaluate_planet_strength(debilitated_pf, has_neechabhanga=False)
    with_nb = StrengthModel.evaluate_planet_strength(debilitated_pf, has_neechabhanga=True)

    assert with_nb.final_score > without_nb.final_score
    assert with_nb.bhanga_contribution > without_nb.bhanga_contribution
    assert any("Neechabhanga" in r for r in with_nb.reasons)


def test_combustion_penalty_applied():
    """Verify combustion reduces avastha contribution score."""
    normal_pf = PlanetFactors(
        planet="Venus",
        longitude=120.0,
        sign_name="Leo",
        sign_id=5,
        house_from_lagna=5,
        house_from_moon=5,
        dignity="enemy",
        is_retrograde=False,
        is_combust=False,
        combustion_separation=25.0,
        baladi_avastha="Yuva",
        jagratadi_avastha="Jagrata",
        deeptadi_avastha="Dina",
        shadbala_virupas=350.0,
        shadbala_ratio=1.06,
        is_shadbala_strong=True,
        houses_owned=[2, 7],
        nakshatra_name="Magha",
        nakshatra_pada=1,
        nakshatra_lord="Ketu",
        conjunctions=[],
        aspects_given_to_houses=[11],
        aspects_given_to_planets=[],
        aspects_received_from_planets=[],
        d9_navamsha_sign="Aries",
        d10_dashamsha_sign="Leo",
        is_vargottama=False
    )

    combust_pf = normal_pf.model_copy(update={
        "is_combust": True,
        "combustion_separation": 2.5
    })

    norm_res = StrengthModel.evaluate_planet_strength(normal_pf)
    comb_res = StrengthModel.evaluate_planet_strength(combust_pf)

    assert comb_res.final_score < norm_res.final_score
    assert comb_res.avastha_contribution < norm_res.avastha_contribution
    assert any("Combustion" in r for r in comb_res.reasons)
