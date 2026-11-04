"""
Evidence Architecture Package for JyotishOS (Phase 5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5).

Exports:
- FactorExtractor, default_factor_extractor
- PlanetFactors, HouseFactors, ChartFactors
"""

from .factors import (
    FactorExtractor,
    default_factor_extractor,
    PlanetFactors,
    HouseFactors,
    ChartFactors
)

__all__ = [
    "FactorExtractor",
    "default_factor_extractor",
    "PlanetFactors",
    "HouseFactors",
    "ChartFactors"
]
