"""
Evidence Architecture Package for JyotishOS (Phase 5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5).

Exports:
- FactorExtractor, default_factor_extractor
- PlanetFactors, HouseFactors, ChartFactors
- StrengthModel, StrengthBreakdown, STRENGTH_WEIGHTS
- EvidencePack, EvidenceFinding, FindingTiming, EvidencePackBuilder, default_evidence_pack_builder
"""

from .factors import (
    FactorExtractor,
    default_factor_extractor,
    PlanetFactors,
    HouseFactors,
    ChartFactors
)
from .strength import (
    StrengthModel,
    StrengthBreakdown,
    STRENGTH_WEIGHTS,
    DIGNITY_SCORE_MAP,
    DEEPTADI_SCORE_MAP
)
from .pack import (
    EvidencePack,
    EvidenceFinding,
    FindingTiming,
    EvidencePackBuilder,
    default_evidence_pack_builder
)

__all__ = [
    "FactorExtractor",
    "default_factor_extractor",
    "PlanetFactors",
    "HouseFactors",
    "ChartFactors",
    "StrengthModel",
    "StrengthBreakdown",
    "STRENGTH_WEIGHTS",
    "DIGNITY_SCORE_MAP",
    "DEEPTADI_SCORE_MAP",
    "EvidencePack",
    "EvidenceFinding",
    "FindingTiming",
    "EvidencePackBuilder",
    "default_evidence_pack_builder"
]
