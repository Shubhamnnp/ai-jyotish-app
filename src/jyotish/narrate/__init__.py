"""
Grounded Shastriya Narrator Package (Phase 5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T5 & P5-T6).

Exports:
- build_narrator_prompt
- CitationGroundingValidator, default_citation_validator, ValidationResult, ProvenanceSentence
- GroundedNarrator, default_grounded_narrator, GroundedNarrativeResponse
"""

from .prompt import build_narrator_prompt
from .validator import (
    CitationGroundingValidator,
    default_citation_validator,
    ValidationResult,
    ProvenanceSentence
)
from .engine import (
    GroundedNarrator,
    default_grounded_narrator,
    GroundedNarrativeResponse
)

__all__ = [
    "build_narrator_prompt",
    "CitationGroundingValidator",
    "default_citation_validator",
    "ValidationResult",
    "ProvenanceSentence",
    "GroundedNarrator",
    "default_grounded_narrator",
    "GroundedNarrativeResponse"
]
