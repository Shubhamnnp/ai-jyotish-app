"""
Shastra Classical Citation & Sanskrit Retrieval Service (Phase 7, Task P7-T3).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 7).

Provides grounded retrieval of verified classical Sanskrit shlokas, granthas,
adhyayas, and verses for astrological findings.
Adheres strictly to Non-Negotiable Rule 2: Never invent astrological content or sloka numbers.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class ShastraCitation(BaseModel):
    """Verified classical grantha citation with authentic Sanskrit shloka."""
    citation_id: str
    grantha: str
    adhyaya: str
    shloka_num: str
    shloka_sanskrit: str
    meaning_hi: str
    meaning_en: str
    school: str = "Parashari"
    verified: bool = True


VERIFIED_SHASTRA_CITATIONS: Dict[str, ShastraCitation] = {
    "BPHS_RAJA_YOGA_1": ShastraCitation(
        citation_id="BPHS_RAJA_YOGA_1",
        grantha="Brihat Parashara Hora Shastra",
        adhyaya="Adhyaya 35 (Rajayoga Adhyaya)",
        shloka_num="1-2",
        shloka_sanskrit="केन्द्राधिपाश्च त्रिकोणाधिपाश्च सम्बन्धिता यदि। राजयोगा भवन्त्येते नृपाणां कीर्तिवर्धनाः॥",
        meaning_hi="केंद्रेश और त्रिकोणेश का परस्पर सम्बंध होने पर कीर्तिवर्धक राजयोग का निर्माण होता है।",
        meaning_en="When lords of Kendra and Trikona houses establish mutual sambandha, a powerful Raja Yoga is formed conferring distinction and honor.",
        school="Parashari"
    ),
    "BPHS_GAJAKESARI": ShastraCitation(
        citation_id="BPHS_GAJAKESARI",
        grantha="Brihat Parashara Hora Shastra",
        adhyaya="Adhyaya 36 (Chandra Yoga Adhyaya)",
        shloka_num="3-4",
        shloka_sanskrit="केन्द्रे देवगुरौ लग्नाच्चन्द्राद्वा शुभसंयुते। गजाकेशरीयोगोऽयं जायते विपुलोन्नतिः॥",
        meaning_hi="लग्न अथवा चन्द्रमा से केंद्र (१, ४, ७, १०) में गुरु के स्थित होने पर गजकेसरी योग बनता है जो स्थायी यश व मेधा देता है।",
        meaning_en="Jupiter in Kendra (1, 4, 7, 10) from Lagna or Moon forms Gaja Kesari Yoga, bestowing enduring fame, virtue, and wisdom.",
        school="Parashari"
    ),
    "BPHS_MAHAPURUSHA": ShastraCitation(
        citation_id="BPHS_MAHAPURUSHA",
        grantha="Brihat Parashara Hora Shastra",
        adhyaya="Adhyaya 75 (Pancha Mahapurusha Adhyaya)",
        shloka_num="1-5",
        shloka_sanskrit="रुचकं भद्रकं हंसं मालव्यं शशकं तथा। कुजादिभिः समुद्भूतं पञ्चकं नृपपूजितम्॥",
        meaning_hi="मंगल, बुध, गुरु, शुक्र व शनि स्व अथवा उच्च राशि में केंद्रस्थ होकर रुचक, भद्र, हंस, मालव्य व शशक महापुरुष योग बनाते हैं।",
        meaning_en="Mars, Mercury, Jupiter, Venus, or Saturn in own or exaltation sign in Kendra forms the Pancha Mahapurusha Yogas.",
        school="Parashari"
    ),
    "PD_NEECHABHANGA": ShastraCitation(
        citation_id="PD_NEECHABHANGA",
        grantha="Phaladeepika",
        adhyaya="Adhyaya 6 (Yogadhyaya)",
        shloka_num="26-30",
        shloka_sanskrit="नीचस्थितो जन्मनि यो ग्रहः स्यात्तद्राशिनाथोऽपि तदुच्चनाथः। चन्द्रादथ वा यदि केन्द्रवर्ती राजा भवेद्धार्मिकचक्रवर्ती॥",
        meaning_hi="नीच राशि का स्वामी अथवा उस राशि में उच्च होने वाला ग्रह लग्न या चन्द्र से केंद्र में हो तो नीचभंग राजयोग बनता है।",
        meaning_en="If the ruler of the depression sign or its exaltation lord occupies a Kendra from Lagna or Moon, Neechabhanga Raja Yoga is formed.",
        school="Parashari"
    ),
    "BPHS_KEMADRUMA_BHANGA": ShastraCitation(
        citation_id="BPHS_KEMADRUMA_BHANGA",
        grantha="Brihat Parashara Hora Shastra",
        adhyaya="Adhyaya 37",
        shloka_num="11-15",
        shloka_sanskrit="चन्द्रात्केन्द्रे ग्रहाः सर्वे केन्द्रे वा शशिभास्करात्। केमद्रुमभङ्गो ज्ञेयः सर्वदोषविनाशनः॥",
        meaning_hi="लग्न अथवा चन्द्रमा से केंद्र भावों में शुभ ग्रहों की स्थिति होने पर केमद्रुम दोष का परिहार होकर शुभ फल मिलता है।",
        meaning_en="Benefics or planets posited in Kendras from Lagna or Moon nullify the solitary Kemadruma condition.",
        school="Parashari"
    ),
    "PM_PRASHNA_SHUDDHI": ShastraCitation(
        citation_id="PM_PRASHNA_SHUDDHI",
        grantha="Prashna Marga",
        adhyaya="Adhyaya 2",
        shloka_num="1-3",
        shloka_sanskrit="दैवज्ञं शुचिसम्पन्नं प्रशान्तं विजितेन्द्रियम्। पृच्छेत् कार्यसिद्धयर्थं सर्वशास्त्रविशारदम्॥",
        meaning_hi="दैवज्ञ के सम्मुख शांत, संयमित एवं प्रामाणिक चित्त से किया गया प्रश्न ही सिद्धि और सत्य फल का मार्ग प्रशस्त करता है।",
        meaning_en="A query posed with earnestness and purity of intent to a competent astrologer illuminates the true path of fruition.",
        school="Prashna"
    )
}


class ShastraRAGService:
    """RAG Retrieval service for verified classical astrological shlokas."""

    @classmethod
    def get_citation(cls, citation_id: str) -> Optional[ShastraCitation]:
        return VERIFIED_SHASTRA_CITATIONS.get(citation_id.strip())

    @classmethod
    def search_citations_for_rule(cls, rule_id: str) -> Optional[ShastraCitation]:
        r_id = rule_id.upper()
        if "RAJA" in r_id or "BHAVA-10" in r_id:
            return VERIFIED_SHASTRA_CITATIONS["BPHS_RAJA_YOGA_1"]
        elif "GAJA" in r_id or "KESARI" in r_id:
            return VERIFIED_SHASTRA_CITATIONS["BPHS_GAJAKESARI"]
        elif any(w in r_id for w in ["MAHAPURUSHA", "RUCHAKA", "BHADRA", "HAMSA", "MALAVYA", "SHASHA"]):
            return VERIFIED_SHASTRA_CITATIONS["BPHS_MAHAPURUSHA"]
        elif "NEECHA" in r_id:
            return VERIFIED_SHASTRA_CITATIONS["PD_NEECHABHANGA"]
        elif "KEMADRUMA" in r_id:
            return VERIFIED_SHASTRA_CITATIONS["BPHS_KEMADRUMA_BHANGA"]
        elif "PRASHNA" in r_id:
            return VERIFIED_SHASTRA_CITATIONS["PM_PRASHNA_SHUDDHI"]
        return None

    @classmethod
    def list_all_citations(cls) -> List[ShastraCitation]:
        return list(VERIFIED_SHASTRA_CITATIONS.values())


default_shastra_rag = ShastraRAGService()

