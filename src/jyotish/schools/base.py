"""
Base School Architecture & Isolated School Output Contracts.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8 & P4-T9).

Rules:
1. Each school (Parashari, Jaimini, KP, Lal Kitab, Tajika) operates in strict isolation.
2. Cross-school mixing or synthetic score averaging is strictly prohibited.
3. Every finding preserves provenance, polarity, shastriya precedence, and caveats.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from ..core.models import KundaliChart


class PrecedencePrinciple(str):
    VISHESHA_OVERRIDES_SAMANYA = "vishesha_overrides_samanya"
    BHANGA_CANCELLATION = "bhanga_cancellation"
    VIPARITA_OVERRIDE = "viparita_override"
    SHADBALA_DOMINANCE = "shadbala_dominance"
    HIGHER_AUTHORITY = "higher_authority"


class PrecedenceRecord(BaseModel):
    """Records the resolution of a classical conflict according to shastriya precedence."""
    dominant_rule_id: str
    overridden_rule_id: str
    principle: str
    explanation_en: str
    explanation_hi: str


class Finding(BaseModel):
    """A verified, structured finding from a single astrological school."""
    finding_id: str
    rule_ids: List[str] = Field(default_factory=list)
    title_en: str
    title_hi: str
    claim_en: str
    claim_hi: str
    domain: str  # e.g., 'career', 'wealth', 'marriage', 'health', 'spirituality'
    polarity: str = "+"  # '+' for auspicious, '-' for cautionary/challenging, 'neutral'
    strength_score: float = 1.0  # computed from dignity / shadbala, not hardcoded
    strength_reason: List[str] = Field(default_factory=list)
    timing_support: List[str] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)
    precedence_applied: Optional[PrecedenceRecord] = None


class SchoolResult(BaseModel):
    """The isolated output of a single astrological school."""
    school_key: str
    school_name: str
    canonical_texts: List[str]
    domain: str = "general"
    supported_findings: List[Finding] = Field(default_factory=list)
    cautionary_findings: List[Finding] = Field(default_factory=list)
    active_cancellations: List[str] = Field(default_factory=list)
    conflicts_resolved: List[PrecedenceRecord] = Field(default_factory=list)
    summary_en: str = ""
    summary_hi: str = ""
    system_metrics: Dict[str, Any] = Field(default_factory=dict)


class BaseSchoolEngine(ABC):
    """Abstract base class for an isolated astrological school engine."""

    @property
    @abstractmethod
    def school_key(self) -> str:
        """Unique identifier (e.g. 'parashari', 'jaimini', 'kp', 'lal_kitab', 'tajika')."""
        pass

    @property
    @abstractmethod
    def school_name(self) -> str:
        """Human-readable name."""
        pass

    @property
    @abstractmethod
    def canonical_texts(self) -> List[str]:
        """Recognized classical texts for this school."""
        pass

    @abstractmethod
    def evaluate(self, chart: KundaliChart, domain: str = "general", **kwargs) -> SchoolResult:
        """
        Evaluates the chart strictly within this school's principles.
        Never references or blends with data/rules from another school.
        """
        pass

