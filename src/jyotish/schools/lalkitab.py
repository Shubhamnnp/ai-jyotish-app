"""
Lal Kitab Astrological School Engine.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8).

Governs classical Lal Kitab principles:
- Sources: Lal Kitab (1952 Gutka / Tarjuma by Pt. Roop Chand Joshi)
- Core factors: Kalapurusha Fixed Houses (Khana 1 to 12), Dharmi Teva, Andha Teva,
  Sleeping Houses (Soya Ghar), Sleeping Planets, 9 Karmic Debts (Rina), Authentic Upayas
- Operates in complete isolation from Parashari bhava lords and KP sub-lords.
"""

from typing import Dict, List, Any
from ..core.models import KundaliChart
from ..core.lalkitab import default_lalkitab_engine, LalKitabResult
from .base import BaseSchoolEngine, SchoolResult, Finding


class LalKitabEngine(BaseSchoolEngine):
    """Lal Kitab (1952 Gutka) astrological engine."""

    @property
    def school_key(self) -> str:
        return "lal_kitab"

    @property
    def school_name(self) -> str:
        return "Lal Kitab (लाल किताब - 1952)"

    @property
    def canonical_texts(self) -> List[str]:
        return [
            "Lal Kitab (1952 Tarjuma by Pt. Roop Chand Joshi)",
            "Lal Kitab Farmans & Ilm-e-Samudrik"
        ]

    def evaluate(self, chart: KundaliChart, domain: str = "general", **kwargs) -> SchoolResult:
        """Evaluates chart using pure Lal Kitab principles in strict isolation."""
        supported_findings: List[Finding] = []
        cautionary_findings: List[Finding] = []

        lk_res: LalKitabResult = default_lalkitab_engine.calculate(chart)

        # 1. Teva Type
        if lk_res.dharmi_teva:
            t_type = "Dharmi Teva"
            supported_findings.append(Finding(
                finding_id="LK-TEVA-DHARMI",
                rule_ids=["LAL-KITAB-1952-DHARMI-TEVA"],
                title_en="Dharmi Teva (Protected Kundali)",
                title_hi="धर्मी तेवा (दैवीय रक्षा कवच)",
                claim_en="Chart qualifies as Dharmi Teva due to auspicious planetary shields, providing protection from unexpected calamities.",
                claim_hi="कुंडली धर्मी तेवा की श्रेणी में आती है, जो आकस्मिक संकटों से अदृश्य ईश्वरीय रक्षा प्रदान करती है।",
                domain="general",
                polarity="+",
                strength_score=1.3,
                strength_reason=["Dharmi Teva Active"]
            ))
        elif lk_res.andha_teva:
            t_type = "Andha Teva"
            cautionary_findings.append(Finding(
                finding_id="LK-TEVA-ANDHA",
                rule_ids=["LAL-KITAB-1952-ANDHA-TEVA"],
                title_en="Andha Teva (Blind Horoscope)",
                title_hi="अंधा तेवा (दृष्टिहीन कुंडली)",
                claim_en="Planets in mutual conflict create Andha Teva condition requiring Lal Kitab precautions.",
                claim_hi="ग्रहों की परस्पर स्थिति से अंधा तेवा की स्थिति बनती है, जिसमें लाल किताब के विशिष्ट उपाय आवश्यक हैं।",
                domain="general",
                polarity="-",
                strength_score=0.8
            ))
        elif lk_res.ratandh_teva:
            t_type = "Ratandh Teva"
            cautionary_findings.append(Finding(
                finding_id="LK-TEVA-RATANDH",
                rule_ids=["LAL-KITAB-1952-RATANDH-TEVA"],
                title_en="Ratandh Teva (Night Blindness)",
                title_hi="रतौंधी तेवा",
                claim_en="Ratandh Teva active; decisions after sunset or night require discernment.",
                claim_hi="रतौंधी तेवा सक्रिय; रात्रि अथवा सूर्यास्त के बाद के निर्णयों में सतर्कता आवश्यक।",
                domain="general",
                polarity="-",
                strength_score=0.85
            ))
        else:
            t_type = "Normal"

        # 2. Sleeping Houses & Planets
        if lk_res.sleeping_houses:
            sh_str = ", ".join([f"Khana {h}" for h in lk_res.sleeping_houses[:3]])
            cautionary_findings.append(Finding(
                finding_id="LK-SLEEPING-HOUSES",
                rule_ids=["LAL-KITAB-SOYA-GHAR"],
                title_en=f"Sleeping Houses: {sh_str}",
                title_hi=f"सोए हुए घर: {sh_str}",
                claim_en=f"Houses {sh_str} are unoccupied (Soya Hua Ghar) until awakened by transit or related planetary trigger.",
                claim_hi=f"घर {sh_str} सोए हुए हैं, जब तक गोचर अथवा संबंधित ग्रह के प्रभाव से जाग्रत न हों।",
                domain="general",
                polarity="neutral",
                strength_score=1.0
            ))

        # 3. Karmic Debts (नौ ऋण)
        for d in lk_res.active_debts:
            d_name = d.get("debt_name", "Karmic Debt")
            cautionary_findings.append(Finding(
                finding_id=f"LK-RINA-{d_name.replace(' ', '-').upper()}",
                rule_ids=["LAL-KITAB-NAU-RINA"],
                title_en=f"Lal Kitab Rina: {d_name}",
                title_hi=f"लाल किताब ऋण: {d.get('debt_name_hi', d_name)}",
                claim_en=d.get("indication_en", f"{d_name} indicated."),
                claim_hi=d.get("indication_hi", f"{d_name} सक्रिय।"),
                domain="karma",
                polarity="-",
                strength_score=0.85,
                caveats=[d.get("remedy_en", "Classical Lal Kitab precaution recommended")]
            ))

        summary_en = (
            f"Lal Kitab evaluation: Teva={t_type}. {len(lk_res.active_debts)} karmic debts detected. "
            f"{len(lk_res.sleeping_houses)} sleeping houses, {len(lk_res.sleeping_planets)} sleeping planets."
        )
        summary_hi = (
            f"लाल किताब विश्लेषण: तेवा प्रकार={t_type}। {len(lk_res.active_debts)} शास्त्रीय ऋण संकेतित। "
            f"{len(lk_res.sleeping_houses)} सोए हुए घर, {len(lk_res.sleeping_planets)} सोए हुए ग्रह।"
        )

        return SchoolResult(
            school_key=self.school_key,
            school_name=self.school_name,
            canonical_texts=self.canonical_texts,
            domain=domain,
            supported_findings=supported_findings,
            cautionary_findings=cautionary_findings,
            active_cancellations=[],
            conflicts_resolved=[],
            summary_en=summary_en,
            summary_hi=summary_hi,
            system_metrics={
                "teva_type": t_type,
                "sleeping_houses_count": len(lk_res.sleeping_houses),
                "sleeping_planets_count": len(lk_res.sleeping_planets),
                "karmic_debts_count": len(lk_res.active_debts)
            }
        )
