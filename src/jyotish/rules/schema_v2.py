"""
Schema v2 (Modernized Shastriya Rule Schema) for JyotishOS.
Conforms to docs/IMPLEMENTATION_PRD.md Section 4.1.

Replaces unverified bulk-generated rules with provenance-rich,
mathematically verifiable, scholar-verified classical rules.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


class RuleSource(BaseModel):
    """Classical text provenance and citation."""
    model_config = ConfigDict(extra="ignore")

    text: str = Field(..., description="Name of the classical grantha, e.g. Brihat Parashara Hora Shastra")
    edition: Optional[str] = Field(None, description="Translator / Edition / Publication details")
    chapter: Union[int, str] = Field(..., description="Adhyaya / Chapter number or identifier")
    verse: Optional[Union[int, str]] = Field(None, description="Sloka / Sutra number")
    original_excerpt_sa: Optional[str] = Field(None, description="Short Sanskrit excerpt if public domain/permitted")
    paraphrase_hi: Optional[str] = Field(None, description="Original Hindi paraphrase/translation")
    paraphrase_en: Optional[str] = Field(None, description="Original English paraphrase/translation")
    author: Optional[str] = Field(None, description="Classical author, e.g. Maharishi Parashara, Varahamihira")


class ConditionCriterion(BaseModel):
    """Atomic astrological condition criterion."""
    model_config = ConfigDict(extra="allow")

    fact: Optional[str] = Field(None, description="Typed fact, e.g. lord_of_house, planet_in_house, aspect")
    entity: Optional[str] = Field(None, description="Graha, Bhava, or Lagna name")
    house: Optional[int] = Field(None, ge=1, le=12, description="House number 1-12")
    placed_in_house: Optional[int] = Field(None, ge=1, le=12, description="Target house number 1-12")
    sign: Optional[Union[str, int]] = Field(None, description="Zodiac sign name or 1-12 id")
    dignity: Optional[str] = Field(None, description="Required dignity (own, exalted, etc.)")
    values: Optional[List[Any]] = Field(None, description="Allowed values for the fact")


class RuleCondition(BaseModel):
    """Boolean composition of criteria."""
    model_config = ConfigDict(extra="ignore")

    type: Literal["ALL", "ANY", "NOT"] = Field("ALL", description="Logic operator")
    criteria: List[ConditionCriterion] = Field(default_factory=list, description="List of criteria")


class RuleModifiers(BaseModel):
    """Classical condition strength modifiers and bhanga cancellations."""
    model_config = ConfigDict(extra="ignore")

    strengthens_if: List[Dict[str, Any]] = Field(default_factory=list)
    weakens_if: List[Dict[str, Any]] = Field(default_factory=list)
    bhanga_refs: List[str] = Field(default_factory=list, description="IDs of cancellation/bhanga rules")


class RuleEffect(BaseModel):
    """Astrological indication/fruit (Phaladesh) of the rule."""
    model_config = ConfigDict(extra="ignore")

    domain: Optional[str] = Field("general", description="Life domain: personality, career, wealth, marriage, etc.")
    polarity: Literal["+", "-", "0", "~"] = Field("+", description="Auspicious (+), Inauspicious (-), Neutral (0), Mixed (~)")
    summary_hi: Optional[str] = Field(None, description="Concise Hindi claim")
    summary_en: Optional[str] = Field(None, description="Concise English claim")
    description_hi: Optional[str] = Field(None, description="Detailed Hindi description")
    description_en: Optional[str] = Field(None, description="Detailed English description")
    themes: Optional[List[str]] = Field(default_factory=list, description="Keywords/tags")


class RuleApplicability(BaseModel):
    """Operational constraints on when the rule should be applied."""
    model_config = ConfigDict(extra="ignore")

    dasha_required: bool = Field(False, description="Whether dasha activation is mandatory")
    varga: str = Field("D1", description="Divisional chart where condition must evaluate (e.g. D1, D9, D10)")
    min_shadbala_ratio: Optional[float] = Field(None, description="Minimum planetary strength ratio required")
    applicable_dashas: Optional[List[str]] = Field(default_factory=list)


class RuleVerification(BaseModel):
    """Academic and editorial provenance tracking."""
    model_config = ConfigDict(extra="ignore")

    status: Literal["draft", "machine_checked", "scholar_verified", "rejected"] = Field(
        "draft",
        description="Verification lifecycle status"
    )
    verified_by: Optional[str] = Field(None, description="Name/credential of the scholar/verifier")
    verified_on: Optional[Union[datetime, date, str]] = Field(None, description="Date/time of verification")
    notes: str = Field("", description="Editorial commentary, text variant notes")


class RuleV2(BaseModel):
    """Complete Shastriya Rule definition in Schema v2."""
    model_config = ConfigDict(extra="ignore")

    rule_id: str = Field(..., description="Unique canonical rule identifier (e.g. BPHS-24-LORD1-H1)")
    rule_name_hi: Optional[str] = Field(None, description="Human-readable Hindi title")
    rule_name_en: Optional[str] = Field(None, description="Human-readable English title")
    schema_version: Literal[2] = Field(2, description="Schema specification version (strictly 2)")
    school: str = Field(
        "parashari",
        description="Jyotish sampradaya: parashari, jaimini, kp, nadi, lalkitab, tajika, muhurta, prashna"
    )
    source: RuleSource = Field(..., description="Classical Grantha reference")
    condition: RuleCondition = Field(..., description="Evaluation logic and criteria")
    modifiers: RuleModifiers = Field(default_factory=RuleModifiers, description="Strengthening/weakening factors")
    effect: RuleEffect = Field(..., description="Phaladesh and polarity")
    applicability: RuleApplicability = Field(default_factory=RuleApplicability, description="Scope and varga")
    verification: RuleVerification = Field(default_factory=RuleVerification, description="Verification status")
    generated: bool = Field(
        False,
        description="Whether this rule was emitted by a bulk generator script rather than handwritten"
    )
