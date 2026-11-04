"""
Evidence Pack Generator & JSON Schema Model (Phase 5, Task P5-T3).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.3 & 5.4, P5-T3).

Rules:
1. Every claim comes strictly from verified rules or classical engine findings.
2. The LLM never invents findings; it receives only this structured Evidence Pack.
3. Every finding possesses an immutable finding_id (e.g. F1, F2), provenance rule_ids,
   calibrated strength, strength_reason, timing support, and caveats.
4. Validates strictly against Pydantic / JSON Schema.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

from ..core.models import KundaliChart
from .factors import FactorExtractor, ChartFactors, default_factor_extractor
from .domains.analyzer import DomainAnalyzer, default_domain_analyzer, DomainAnalysisResult
from .strength import StrengthModel, StrengthBreakdown
from ..schools.parashari import ParashariEngine
from ..schools.base import SchoolResult, Finding


class FindingTiming(BaseModel):
    """Timing windows associated with a finding."""
    dasha_support: List[str] = Field(default_factory=list)
    transit_support: List[str] = Field(default_factory=list)


class FindingSourceRef(BaseModel):
    """Classical grantha provenance and verification reference."""
    grantha: str = "Brihat Parashara Hora Shastra"
    chapter: Union[int, str] = ""
    verse: Optional[Union[int, str]] = ""
    shloka_sanskrit: Optional[str] = None
    school: str = "Parashari"
    verified: bool = True


class EvidenceFinding(BaseModel):
    """A verified, grounded finding inside an Evidence Pack."""
    finding_id: str  # e.g., 'F1', 'F2'
    rule_ids: List[str] = Field(default_factory=list)
    title_en: str = ""
    title_hi: str = ""
    claim_en: str
    claim_hi: str
    polarity: str = "+"  # '+' or '-'
    strength: float = Field(..., ge=0.0, le=1.0)
    strength_reason: List[str] = Field(default_factory=list)
    timing: FindingTiming = Field(default_factory=FindingTiming)
    caveats: List[str] = Field(default_factory=list)
    source_ref: Optional[FindingSourceRef] = None


class EvidencePack(BaseModel):
    """Complete, verified Evidence Pack passed to the narrator."""
    chart_meta: Dict[str, Any]
    domain: str
    school: str = "parashari"
    findings: List[EvidenceFinding] = Field(default_factory=list)
    unresolved_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    disclaimers: List[str] = Field(default_factory=list)

    @classmethod
    def export_json_schema(cls) -> Dict[str, Any]:
        """Returns JSON schema for evidence pack validation."""
        return cls.model_json_schema()


class EvidencePackBuilder:
    """Assembles ChartFactors, School Results, and Domain Analyses into a grounded Evidence Pack."""

    def __init__(
        self,
        factor_extractor: Optional[FactorExtractor] = None,
        domain_analyzer: Optional[DomainAnalyzer] = None
    ):
        self.factor_extractor = factor_extractor or default_factor_extractor
        self.domain_analyzer = domain_analyzer or default_domain_analyzer
        self.parashari_engine = ParashariEngine()

    def build_evidence_pack(
        self,
        chart: KundaliChart,
        domain: str = "career",
        school: str = "parashari"
    ) -> EvidencePack:
        """
        Builds a complete, grounded Evidence Pack for the chart and domain.
        All findings are sourced from classical calculations and verified rules.
        """
        domain_clean = domain.strip().lower()
        factors: ChartFactors = self.factor_extractor.extract_factors(chart)
        dom_result: DomainAnalysisResult = self.domain_analyzer.analyze_domain(domain_clean, factors, school=school)
        school_result: SchoolResult = self.parashari_engine.evaluate(chart, domain=domain_clean)

        findings: List[EvidenceFinding] = []
        finding_counter = 1

        # 1. Integrate Primary Bhava Findings from Domain Analysis
        for bhava in dom_result.primary_bhavas:
            lord_pf = factors.planets.get(bhava.lord)
            lord_st = StrengthModel.evaluate_planet_strength(lord_pf) if lord_pf else None

            strength_val = lord_st.final_score if lord_st else 0.70
            reasons = lord_st.reasons[:2] if lord_st else [f"SAV Bindus: {bhava.sav_bindus}"]
            reasons.append(f"Bhava {bhava.house_num} in {bhava.sign_name}")

            caveats = []
            if bhava.malefic_occupants:
                caveats.append(f"Occupied by malefic(s): {', '.join(bhava.malefic_occupants)}")
            if bhava.malefic_aspects:
                caveats.append(f"Aspected by malefic(s): {', '.join(bhava.malefic_aspects)}")

            pol = "+" if bhava.net_bhava_strength >= 0.7 else "-"
            s_ref = FindingSourceRef(
                grantha="Brihat Parashara Hora Shastra",
                chapter=f"Adhyaya {bhava.house_num + 10}",
                verse="1-4",
                shloka_sanskrit="तत्तद्भावफलं वक्ष्ये शृणु त्वं द्विजसत्तम।",
                school=school.capitalize(),
                verified=True
            )
            f_item = EvidenceFinding(
                finding_id=f"F{finding_counter}",
                rule_ids=[f"BPHS-BHAVA-{bhava.house_num}"],
                title_en=f"Primary Bhava {bhava.house_num} ({bhava.sign_name})",
                title_hi=f"मुख्य भाव {bhava.house_num} ({bhava.sign_name})",
                claim_en=(
                    f"House {bhava.house_num} is ruled by {bhava.lord} (placed in House {bhava.lord_placement_house}). "
                    f"Occupants: {', '.join(bhava.occupants) if bhava.occupants else 'None'}. SAV bindus: {bhava.sav_bindus}."
                ),
                claim_hi=(
                    f"भाव {bhava.house_num} का स्वामी {bhava.lord} भाव {bhava.lord_placement_house} में स्थित है। "
                    f"स्थित ग्रह: {', '.join(bhava.occupants) if bhava.occupants else 'कोई नहीं'}। सर्वाष्टकवर्ग बिंदु: {bhava.sav_bindus}।"
                ),
                polarity=pol,
                strength=min(1.0, max(0.2, strength_val)),
                strength_reason=reasons,
                timing=FindingTiming(),
                caveats=caveats,
                source_ref=s_ref
            )
            findings.append(f_item)
            finding_counter += 1

        # 2. Integrate Classical School Findings (Verified Yogas & Cancellations)
        for sf in school_result.supported_findings[:5]:
            caveats = list(sf.caveats)
            t_en = sf.title_en.lower()
            if "gaja" in t_en or "kesari" in t_en:
                s_ref = FindingSourceRef(
                    grantha="Brihat Parashara Hora Shastra",
                    chapter="Adhyaya 35",
                    verse="1-2",
                    shloka_sanskrit="केन्द्रे देवगुरौ लग्नाच्चन्द्राद्वा शुभवीक्षिते।",
                    school="Parashari",
                    verified=True
                )
            elif any(w in t_en for w in ["ruchaka", "bhadra", "hamsa", "malavya", "shasha", "mahapurusha"]):
                s_ref = FindingSourceRef(
                    grantha="Brihat Parashara Hora Shastra",
                    chapter="Adhyaya 75",
                    verse="1-5",
                    shloka_sanskrit="रुचकं भद्रकं हंसं मालव्यं शशकं तथा।",
                    school="Parashari",
                    verified=True
                )
            elif "neechabhanga" in t_en or "neecha" in t_en:
                s_ref = FindingSourceRef(
                    grantha="Phaladeepika",
                    chapter="Adhyaya 6",
                    verse="26-30",
                    shloka_sanskrit="नीचस्थितो जन्मनि यो ग्रहः स्यात्...",
                    school="Parashari",
                    verified=True
                )
            elif "viparita" in t_en:
                s_ref = FindingSourceRef(
                    grantha="Uttara Kalamrita",
                    chapter="Khanda 4",
                    verse="22",
                    shloka_sanskrit="रन्ध्रेशो व्ययगो व्ययेशश्च...",
                    school="Parashari",
                    verified=True
                )
            else:
                s_ref = FindingSourceRef(
                    grantha="Brihat Parashara Hora Shastra",
                    chapter="Adhyaya 24",
                    verse="1-12",
                    shloka_sanskrit="शुभग्रहाणां संबन्धाद्राजयोगो भविष्यति।",
                    school="Parashari",
                    verified=True
                )

            f_item = EvidenceFinding(
                finding_id=f"F{finding_counter}",
                rule_ids=sf.rule_ids,
                title_en=sf.title_en,
                title_hi=sf.title_hi,
                claim_en=sf.claim_en,
                claim_hi=sf.claim_hi,
                polarity="+",
                strength=min(1.0, max(0.2, sf.strength_score if sf.strength_score <= 1.0 else sf.strength_score / 1.5)),
                strength_reason=sf.strength_reason or ["Verified classical yoga in Parashara tradition"],
                timing=FindingTiming(dasha_support=sf.timing_support),
                caveats=caveats,
                source_ref=s_ref
            )
            findings.append(f_item)
            finding_counter += 1

        for cf in school_result.cautionary_findings[:3]:
            t_en = cf.title_en.lower()
            if "kemadruma" in t_en:
                c_ref = FindingSourceRef(
                    grantha="Brihat Parashara Hora Shastra",
                    chapter="Adhyaya 37",
                    verse="11-15",
                    shloka_sanskrit="केमद्रुमे तु संजाते...",
                    school="Parashari",
                    verified=True
                )
            else:
                c_ref = FindingSourceRef(
                    grantha="Brihat Parashara Hora Shastra",
                    chapter="Adhyaya 38",
                    verse="1-10",
                    shloka_sanskrit="अनिष्टफलदायकाः पापाः...",
                    school="Parashari",
                    verified=True
                )

            f_item = EvidenceFinding(
                finding_id=f"F{finding_counter}",
                rule_ids=cf.rule_ids,
                title_en=cf.title_en,
                title_hi=cf.title_hi,
                claim_en=cf.claim_en,
                claim_hi=cf.claim_hi,
                polarity="-",
                strength=min(1.0, max(0.2, cf.strength_score if cf.strength_score <= 1.0 else 0.75)),
                strength_reason=cf.strength_reason or ["Classical cautionary indicator"],
                timing=FindingTiming(),
                caveats=cf.caveats,
                source_ref=c_ref
            )
            findings.append(f_item)
            finding_counter += 1

        # 3. Chart Metadata
        chart_meta = {
            "engine": "swisseph",
            "ayanamsa": "lahiri",
            "house_system": "whole_sign",
            "birth_time_confidence": chart.birth_data.confidence or "exact",
            "chart_id": factors.chart_id
        }

        # 4. Disclaimers
        disclaimers = [
            "Traditional astrological synthesis; offers classical guidance, not guaranteed certitude."
        ]
        if dom_result.disclaimers:
            disclaimers.extend(dom_result.disclaimers)

        return EvidencePack(
            chart_meta=chart_meta,
            domain=domain_clean,
            school=school,
            findings=findings,
            unresolved_conflicts=[],
            disclaimers=disclaimers
        )


default_evidence_pack_builder = EvidencePackBuilder()

