"""
Jaimini Astrological School Engine.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8).

Governs Jaimini Sutram principles:
- Sources: Upadesha Sutras of Maharishi Jaimini
- Core factors: 7/8 Chara Karakas (Atmakaraka, Amatyakaraka, etc.), Arudha Padas,
  Rashi Drishti (sign aspects), Karakamsha, Chara Dasha
- Strictly isolated from Parashari planetary aspects or KP sub-lords.
"""

from typing import Dict, List, Any
from ..core.models import KundaliChart
from ..core.jaimini import default_jaimini_engine
from .base import BaseSchoolEngine, SchoolResult, Finding


class JaiminiEngine(BaseSchoolEngine):
    """Jaimini Upadesha Sutras astrological system engine."""

    @property
    def school_key(self) -> str:
        return "jaimini"

    @property
    def school_name(self) -> str:
        return "Jaimini Sutram (जैमिनी सूत्रम्)"

    @property
    def canonical_texts(self) -> List[str]:
        return [
            "Jaimini Upadesha Sutras (Maharishi Jaimini)",
            "Jyotisha Phala Ratnamala (Krishna Mishra)"
        ]

    def evaluate(self, chart: KundaliChart, domain: str = "general", **kwargs) -> SchoolResult:
        """Evaluates chart using pure Jaimini principles in total isolation."""
        supported_findings: List[Finding] = []
        cautionary_findings: List[Finding] = []

        # 1. Chara Karakas & Arudhas from core calculator
        j_res = default_jaimini_engine.calculate(chart)
        ak_planet = j_res.karakas_7.get("AK") or j_res.karakas_8.get("AK")
        amk_planet = j_res.karakas_7.get("AmK") or j_res.karakas_8.get("AmK")

        if ak_planet:
            ak_pos = chart.planets.get(ak_planet)
            sign_deg = ak_pos.sign_degree if ak_pos else 0.0
            sign_name = ak_pos.sign_name if ak_pos else ""
            supported_findings.append(Finding(
                finding_id=f"JAI-AK-{ak_planet.upper()}",
                rule_ids=["JAIMINI-SUTRA-1-1-11"],
                title_en=f"Atmakaraka: {ak_planet}",
                title_hi=f"आत्मकारक: {ak_planet}",
                claim_en=f"{ak_planet} is the Atmakaraka at {sign_deg:.2f}° in {sign_name}, indicating the soul's primary trajectory.",
                claim_hi=f"{ak_planet} {sign_deg:.2f}° पर {sign_name} राशि में आत्मकारक है, जो आत्मा की मुख्य दिशा दर्शाता है।",
                domain="spirituality" if domain == "general" else domain,
                polarity="+",
                strength_score=1.2,
                strength_reason=[f"Highest sign degree ({sign_deg:.2f}°)"]
            ))

        if amk_planet:
            amk_pos = chart.planets.get(amk_planet)
            sign_deg = amk_pos.sign_degree if amk_pos else 0.0
            sign_name = amk_pos.sign_name if amk_pos else ""
            supported_findings.append(Finding(
                finding_id=f"JAI-AMK-{amk_planet.upper()}",
                rule_ids=["JAIMINI-SUTRA-1-1-12"],
                title_en=f"Amatyakaraka: {amk_planet}",
                title_hi=f"अमात्यकारक: {amk_planet}",
                claim_en=f"{amk_planet} is Amatyakaraka, guiding intellect, career, and achievement.",
                claim_hi=f"{amk_planet} अमात्यकारक है, जो बुद्धि, कर्मक्षेत्र और सफलता का संचालन करता है।",
                domain="career" if domain == "general" else domain,
                polarity="+",
                strength_score=1.1,
                strength_reason=[f"Second highest degree ({sign_deg:.2f}°)"]
            ))

        # Check AK & AmK mutual relation (Jaimini Raja Yoga)
        if ak_planet and amk_planet:
            ak_pos = chart.planets.get(ak_planet)
            amk_pos = chart.planets.get(amk_planet)
            if ak_pos and amk_pos and ak_pos.sign_name == amk_pos.sign_name:
                supported_findings.append(Finding(
                    finding_id="JAI-RY-AK-AMK-CONJUNCT",
                    rule_ids=["JAIMINI-SUTRA-1-1-35"],
                    title_en="Jaimini Raja Yoga (AK & AmK Conjunction)",
                    title_hi="जैमिनी राजयोग (आत्मकारक व अमात्यकारक युति)",
                    claim_en=f"Conjunction of Atmakaraka ({ak_planet}) and Amatyakaraka ({amk_planet}) in {ak_pos.sign_name} forms powerful Jaimini Raja Yoga.",
                    claim_hi=f"आत्मकारक ({ak_planet}) और अमात्यकारक ({amk_planet}) की {ak_pos.sign_name} में युति श्रेष्ठ जैमिनी राजयोग बनाती है।",
                    domain="career",
                    polarity="+",
                    strength_score=1.3,
                    strength_reason=["AK-AmK Conjunction"]
                ))

        # 2. Arudha Padas
        al_house = j_res.arudha_padas.get("AL")
        al_sign = j_res.arudha_pada_names.get("AL", "")
        if al_house:
            supported_findings.append(Finding(
                finding_id="JAI-ARUDHA-LAGNA",
                rule_ids=["JAIMINI-SUTRA-1-1-29"],
                title_en=f"Arudha Lagna (AL) in {al_sign}",
                title_hi=f"आरूढ़ लग्न (AL) {al_sign} में",
                claim_en=f"Arudha Lagna falls in House {al_house} ({al_sign}), governing worldly image and reputation.",
                claim_hi=f"आरूढ़ लग्न भाव {al_house} ({al_sign}) में पड़ता है, जो लौकिक छवि का प्रतिनिधित्व करता है।",
                domain="personality",
                polarity="+"
            ))

        ul_house = j_res.arudha_padas.get("UL")
        ul_sign = j_res.arudha_pada_names.get("UL", "")
        if ul_house:
            finding_pol = "+" if ul_house not in (6, 8, 12) else "-"
            target_list = supported_findings if finding_pol == "+" else cautionary_findings
            target_list.append(Finding(
                finding_id="JAI-UPAPADA-LAGNA",
                rule_ids=["JAIMINI-SUTRA-1-4-1"],
                title_en=f"Upapada Lagna (UL) in {ul_sign}",
                title_hi=f"उपपद लग्न (UL) {ul_sign} में",
                claim_en=f"Upapada Lagna occupies House {ul_house} ({ul_sign}), determining marital harmony and partnership longevity.",
                claim_hi=f"उपपद लग्न भाव {ul_house} ({ul_sign}) में है, जो वैवाहिक संबंध व जीवनसाथी का कारक है।",
                domain="marriage",
                polarity=finding_pol
            ))

        summary_en = (
            f"Jaimini analysis identified {len(supported_findings)} key significations and "
            f"{len(cautionary_findings)} challenges. AK={ak_planet or 'N/A'}, AmK={amk_planet or 'N/A'}."
        )
        summary_hi = (
            f"जैमिनी विश्लेषण में {len(supported_findings)} मुख्य शुभ कारक एवं {len(cautionary_findings)} सतर्कता बिंदु प्राप्त हुए। "
            f"आत्मकारक: {ak_planet or 'N/A'}, अमात्यकारक: {amk_planet or 'N/A'}।"
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
                "atmakaraka": ak_planet,
                "amatyakaraka": amk_planet,
                "karakamsha": j_res.karakamsha_sign_name,
                "arudha_lagna_house": al_house,
                "upapada_lagna_house": ul_house
            }
        )
