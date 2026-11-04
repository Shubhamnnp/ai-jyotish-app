"""
Domain Analysis Package for JyotishOS (Phase 5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.2).

Exports:
- DomainAnalyzer, default_domain_analyzer
- DomainSignificators, BhavaAnalysisFactor, KarakaAnalysisFactor, DomainAnalysisResult
"""

from .analyzer import (
    DomainAnalyzer,
    default_domain_analyzer,
    DomainSignificators,
    BhavaAnalysisFactor,
    KarakaAnalysisFactor,
    DomainAnalysisResult
)

__all__ = [
    "DomainAnalyzer",
    "default_domain_analyzer",
    "DomainSignificators",
    "BhavaAnalysisFactor",
    "KarakaAnalysisFactor",
    "DomainAnalysisResult"
]
