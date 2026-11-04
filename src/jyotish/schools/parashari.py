"""
Parashari Astrological School Engine.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8 & P4-T9).

Governs classical Parashari Jyotish:
- Sources: Brihat Parashara Hora Shastra (BPHS), Phaladeepika, Saravali, Brihat Jataka
- Core factors: Bhava, Bhava Lords, Kendra/Trikona relations, Shadbala, Classical Yogas, Vimshottari Dasha
- Internal Precedence: Vishesha overrides Samanya, Neechabhanga, Kemadruma Bhanga, Viparita Raja Yoga.
"""

from typing import Dict, List, Any, Optional
from ..core.models import KundaliChart
from ..core.constants import KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES, SIGN_LORDS
from ..core.yoga import ClassicalYogaDoshaEngine, default_yoga_dosha_engine
default_yoga_engine = default_yoga_dosha_engine
from ..core.shadbala import default_shadbala_engine
from .base import BaseSchoolEngine, SchoolResult, Finding, PrecedenceRecord, PrecedencePrinciple
from .conflict import ShastriyaPrecedenceEngine


class ParashariEngine(BaseSchoolEngine):
    """Classical Parashari astrological system engine."""

    @property
    def school_key(self) -> str:
        return "parashari"

    @property
    def school_name(self) -> str:
        return "Parashari Jyotish (पाराशरी ज्योतिष)"

    @property
    def canonical_texts(self) -> List[str]:
        return [
            "Brihat Parashara Hora Shastra (BPHS)",
            "Phaladeepika (Mantreswara)",
            "Saravali (Kalyana Varma)",
            "Brihat Jataka (Varahamihira)"
        ]

    def evaluate(self, chart: KundaliChart, domain: str = "general", **kwargs) -> SchoolResult:
        """
        Evaluates the chart strictly within Parashari principles.
        Resolves conflicts using classical precedence and records bhangas.
        """
        supported_findings: List[Finding] = []
        cautionary_findings: List[Finding] = []
        cancellations: List[str] = []
        conflicts_resolved: List[PrecedenceRecord] = []

        # 1. Evaluate pure classical yogas & doshas from core.yoga
        yoga_results = default_yoga_engine.evaluate_all(chart)
        shadbala_summary = default_shadbala_engine.calculate(chart)

        # 2. Check Neechabhanga Precedence for debilitated planets
        for p_name, pos in chart.planets.items():
            if pos.dignity == "debilitated":
                prec = ShastriyaPrecedenceEngine.resolve_neechabhanga_precedence(chart, p_name)
                if prec:
                    conflicts_resolved.append(prec)
                    cancellations.append(f"{p_name} नीचभंग राजयोग (Neechabhanga Active)")
                    supported_findings.append(Finding(
                        finding_id=f"PAR-NB-{p_name.upper()}",
                        rule_ids=[prec.dominant_rule_id],
                        title_en=f"{p_name} Neechabhanga Raja Yoga",
                        title_hi=f"{p_name} नीचभंग राजयोग",
                        claim_en=f"{p_name}'s debility is cancelled by dispositor in Kendra, producing Raja Yoga.",
                        claim_hi=f"{p_name} का नीचत्व केंद्र स्थित स्वामी के प्रभाव से भंग होकर राजयोगकारी बनता है।",
                        domain=domain,
                        polarity="+",
                        strength_score=1.2,
                        strength_reason=["Dispositor in Kendra", "BPHS Ch. 41 Neechabhanga rule"],
                        precedence_applied=prec
                    ))
                else:
                    cautionary_findings.append(Finding(
                        finding_id=f"PAR-DEB-{p_name.upper()}",
                        rule_ids=[f"GEN-DEBILITY-{p_name.upper()}"],
                        title_en=f"{p_name} Debilitated (Neecha)",
                        title_hi=f"{p_name} नीचस्थ",
                        claim_en=f"{p_name} is in its depression sign {pos.sign_name} without primary cancellation.",
                        claim_hi=f"{p_name} अपनी नीच राशि {pos.sign_name} में स्थित है।",
                        domain=domain,
                        polarity="-",
                        strength_score=0.8
                    ))

        # 3. Check Kemadruma Precedence
        kem_prec = ShastriyaPrecedenceEngine.resolve_kemadruma_precedence(chart)
        if kem_prec:
            conflicts_resolved.append(kem_prec)
            cancellations.append("केमद्रुम भंग (Kemadruma Bhanga Active)")
            supported_findings.append(Finding(
                finding_id="PAR-KEMADRUMA-BHANGA",
                rule_ids=[kem_prec.dominant_rule_id],
                title_en="Kemadruma Bhanga (Dosha Nullified)",
                title_hi="केमद्रुम भंग राजयोग",
                claim_en="Solitary Moon condition is cancelled by benefics/Moon occupying Kendra.",
                claim_hi="केंद्र में शुभ ग्रहों अथवा चंद्रमा की स्थिति से केमद्रुम दोष का परिहार होता है।",
                domain=domain,
                polarity="+",
                strength_score=1.1,
                precedence_applied=kem_prec
            ))

        # 4. Check Viparita Raja Yogas
        viparita_precs = ShastriyaPrecedenceEngine.resolve_viparita_precedence(chart)
        for vp in viparita_precs:
            conflicts_resolved.append(vp)
            cancellations.append(f"विपरीत राजयोग: {vp.dominant_rule_id}")
            supported_findings.append(Finding(
                finding_id=vp.dominant_rule_id,
                rule_ids=[vp.dominant_rule_id],
                title_en="Viparita Raja Yoga Active",
                title_hi="विपरीत राजयोग",
                claim_en=vp.explanation_en,
                claim_hi=vp.explanation_hi,
                domain=domain,
                polarity="+",
                strength_score=1.15,
                precedence_applied=vp
            ))

        # 5. Integrate Classical Yogas (PMR, Gajakesari, Dhana Yogas)
        for y in yoga_results.yogas:
            if not y.is_active:
                continue
            y_name = y.name_en
            finding = Finding(
                finding_id=f"PAR-YOGA-{y_name.replace(' ', '-').upper()}",
                rule_ids=[y.shloka_reference or "BPHS"],
                title_en=y_name,
                title_hi=y.name_hi,
                claim_en=y.description_en,
                claim_hi=y.description_hi,
                domain=domain,
                polarity="+",
                strength_score=y.strength_score / 100.0 if y.strength_score > 10 else y.strength_score,
                strength_reason=[f"Verified classical definition from {y.shloka_reference or 'BPHS'}"]
            )
            supported_findings.append(finding)

        # Integrate Doshas
        for d in yoga_results.doshas:
            if not d.is_present:
                continue
            if d.is_cancelled:
                cancellations.append(f"{d.name_hi} परिहार ({d.name_en} Cancelled)")
                continue
            cautionary_findings.append(Finding(
                finding_id=f"PAR-DOSHA-{d.dosha_id.upper()}",
                rule_ids=[d.shloka_reference or "BPHS"],
                title_en=d.name_en,
                title_hi=d.name_hi,
                claim_en=d.description_en,
                claim_hi=d.description_hi,
                domain=domain,
                polarity="-",
                strength_score=0.8,
                caveats=[d.remedy_summary] if d.remedy_summary else []
            ))

        # 6. Bhava Lords Strength Synthesis
        lagna_sign = chart.houses[0].sign_name
        lagna_lord = SIGN_LORDS.get(lagna_sign, "")
        lagna_lord_pos = chart.planets.get(lagna_lord)
        if lagna_lord_pos:
            lord_house = lagna_lord_pos.house_from_lagna
            supported_findings.append(Finding(
                finding_id=f"PAR-LAGNESHA-H{lord_house}",
                rule_ids=[f"BPHS-24-LORD1-H{lord_house}"],
                title_en=f"Lagna Lord {lagna_lord} in House {lord_house}",
                title_hi=f"लग्नेश {lagna_lord} {lord_house} भाव में",
                claim_en=f"Ascendant lord {lagna_lord} occupies House {lord_house} ({lagna_lord_pos.sign_name}).",
                claim_hi=f"लग्न भाव का स्वामी {lagna_lord} भाव {lord_house} में {lagna_lord_pos.sign_name} राशि में स्थित है।",
                domain=domain,
                polarity="+" if lord_house in set(KENDRA_HOUSES).union(TRIKONA_HOUSES) else "neutral",
                strength_score=1.0,
                strength_reason=[f"Dignity: {lagna_lord_pos.dignity}"]
            ))

        summary_en = (
            f"Parashari evaluation identified {len(supported_findings)} auspicious alignments and "
            f"{len(cautionary_findings)} cautionary factors. {len(cancellations)} classical cancellations applied."
        )
        summary_hi = (
            f"पाराशरी विश्लेषण में {len(supported_findings)} शुभ योग एवं {len(cautionary_findings)} सतर्कता कारक प्राप्त हुए। "
            f"{len(cancellations)} शास्त्रीय परिहार (भंग) सक्रिय पाए गए।"
        )

        return SchoolResult(
            school_key=self.school_key,
            school_name=self.school_name,
            canonical_texts=self.canonical_texts,
            domain=domain,
            supported_findings=supported_findings,
            cautionary_findings=cautionary_findings,
            active_cancellations=cancellations,
            conflicts_resolved=conflicts_resolved,
            summary_en=summary_en,
            summary_hi=summary_hi,
            system_metrics={
                "total_classical_yogas": len(yoga_results.yogas),
                "total_doshas": len(yoga_results.doshas),
                "cancellations_count": len(cancellations),
                "shadbala_summary": {p: r.strength_ratio for p, r in shadbala_summary.planets.items()} if hasattr(shadbala_summary, "planets") else {}
            }
        )
