"""
Tajika Astrological School Engine (Varshaphala & Solar Return).
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8).

Governs classical Tajika principles:
- Sources: Tajika Neelakanthi (Neelakantha Daivajna)
- Core factors: Solar return (Varsha Pravesh), Muntha & Munthesha,
  Varsheshwara (5 Panchadhikaris), 16 Tajika Yogas (Ithasala, Ishrafa, etc.), Sahams
- Operates in strict isolation from natal Parashari dashas and Jaimini karakas.
"""

from typing import Dict, List, Any
from datetime import date
from ..core.models import KundaliChart
from ..core.tajika import default_tajika_engine, TajikaResult
from .base import BaseSchoolEngine, SchoolResult, Finding


class TajikaEngine(BaseSchoolEngine):
    """Tajika Varshaphala (Solar Return) engine."""

    @property
    def school_key(self) -> str:
        return "tajika"

    @property
    def school_name(self) -> str:
        return "Tajika Neelakanthi (ताजिक वर्षफल)"

    @property
    def canonical_texts(self) -> List[str]:
        return [
            "Tajika Neelakanthi (Neelakantha Daivajna)",
            "Prashna Tantra (Neelakantha)"
        ]

    def evaluate(self, chart: KundaliChart, domain: str = "general", target_year: int = 2026, **kwargs) -> SchoolResult:
        """Evaluates chart using pure Tajika Varshaphala principles."""
        supported_findings: List[Finding] = []
        cautionary_findings: List[Finding] = []

        taj_res: TajikaResult = default_tajika_engine.calculate(chart, target_year=target_year)
        muntha_h = taj_res.muntha_house_from_lagna
        muntha_sign = taj_res.muntha_sign_name
        is_muntha_auspicious = muntha_h in (1, 2, 3, 5, 9, 10, 11)

        # 1. Muntha
        if is_muntha_auspicious:
            supported_findings.append(Finding(
                finding_id=f"TAJ-MUNTHA-H{muntha_h}",
                rule_ids=["TAJIKA-NEELAKANTHI-MUNTHA"],
                title_en=f"Auspicious Muntha in House {muntha_h} ({muntha_sign})",
                title_hi=f"शुभ मुन्था {muntha_h} भाव ({muntha_sign}) में",
                claim_en=f"Muntha for year {target_year} resides in House {muntha_h}, conferring progression, health, and status.",
                claim_hi=f"वर्ष {target_year} के लिए मुन्था भाव {muntha_h} में शुभ स्थान पर स्थित होकर उन्नति और स्वास्थ्य वर्धक है।",
                domain=domain,
                polarity="+",
                strength_score=1.15,
                strength_reason=[f"Occupies House {muntha_h}"]
            ))
        else:
            cautionary_findings.append(Finding(
                finding_id=f"TAJ-MUNTHA-H{muntha_h}",
                rule_ids=["TAJIKA-NEELAKANTHI-MUNTHA-DUSTHANA"],
                title_en=f"Muntha in Dusthana House {muntha_h} ({muntha_sign})",
                title_hi=f"मुन्था त्रिक भाव {muntha_h} ({muntha_sign}) में",
                claim_en=f"Muntha occupies House {muntha_h} (4th, 6th, 7th, 8th or 12th), advising caution regarding stress and expenses.",
                claim_hi=f"मुन्था भाव {muntha_h} में होने से मानसिक तनाव व अनपेक्षित व्यय के प्रति सावधानी अपेक्षित है।",
                domain=domain,
                polarity="-",
                strength_score=0.85
            ))

        # 2. Varsheshwara (Lord of the Year)
        varshesh = taj_res.varsheshwara
        supported_findings.append(Finding(
            finding_id=f"TAJ-VARSHE-LORD-{varshesh.upper()}",
            rule_ids=["TAJIKA-PANCHADHIKARI-VARSHE"],
            title_en=f"Varsheshwara (Lord of the Year): {varshesh}",
            title_hi=f"वर्षेश (वर्ष का स्वामी): {varshesh}",
            claim_en=f"{varshesh} commands supreme lordship (Varsheshwara) for the annual cycle of {target_year}.",
            claim_hi=f"वर्ष चक्र {target_year} के लिए {varshesh} पंचाधिकारियों में सर्वाधिक बली होकर वर्षेश नियुक्त होता है।",
            domain=domain,
            polarity="+",
            strength_score=1.2,
            strength_reason=[taj_res.varshesh_reason_hi]
        ))

        # 3. Tajika Yogas
        for y in taj_res.tajika_yogas:
            y_name = y.get("yoga_name", "Tajika Yoga")
            status = y.get("status", "")
            is_pos = "इत्थशाल" in status or "Ithasala" in status or "Benefic" in status
            finding = Finding(
                finding_id=f"TAJ-YOGA-{y_name.replace(' ', '-').upper()}",
                rule_ids=["TAJIKA-NEELAKANTHI-16-YOGAS"],
                title_en=f"Tajika Yoga: {y_name}",
                title_hi=f"ताजिक योग: {y_name}",
                claim_en=f"{y_name} formed by {y.get('planets', '')}. Status: {status}",
                claim_hi=f"{y.get('planets', '')} द्वारा {y_name} योग। स्थिति: {status}",
                domain=domain,
                polarity="+" if is_pos else "neutral",
                strength_score=1.1 if is_pos else 0.95
            )
            if is_pos:
                supported_findings.append(finding)
            else:
                cautionary_findings.append(finding)

        summary_en = (
            f"Tajika Varshaphala evaluation for year {target_year}: Muntha in House {muntha_h} ({muntha_sign}), "
            f"Varsheshwara is {varshesh}. {len(supported_findings)} auspicious, {len(cautionary_findings)} cautionary."
        )
        summary_hi = (
            f"ताजिक वर्षफल विश्लेषण (वर्ष {target_year}): मुन्था भाव {muntha_h} ({muntha_sign}) में, "
            f"वर्षेश: {varshesh}। {len(supported_findings)} अनुकूल एवं {len(cautionary_findings)} सतर्कता सूचक।"
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
                "target_year": target_year,
                "completed_age": taj_res.completed_age,
                "muntha_house": muntha_h,
                "muntha_sign": muntha_sign,
                "varsheshwara": varshesh,
                "yogas_count": len(taj_res.tajika_yogas)
            }
        )
