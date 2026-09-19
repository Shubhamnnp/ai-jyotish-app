"""
Classical Shastriya Astrological Knowledge Base for JyotishOS.
Indexes foundational Vedic astrology scriptures (BPHS, Saravali, Phaladeepika, Jaimini, Tajika, Prashna Marga)
for evidence retrieval and grounded AI generation with Gemini.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ShastraPassage(BaseModel):
    id: str
    grantha: str
    author: str
    chapter: str
    theme: str
    shloka_sanskrit: Optional[str] = None
    translation_hi: str
    translation_en: str
    principles: List[str]


CLASSICAL_SHASTRA_CHUNKS: List[Dict[str, Any]] = [
    {
        "id": "BPHS_LAGNA_01",
        "grantha": "Brihat Parashara Hora Shastra",
        "author": "Maharishi Parashara",
        "chapter": "Adhyaya 11 - Bhavaphaladhikara",
        "theme": "personality_and_vitality",
        "shloka_sanskrit": "लग्नेशे केन्द्रकोणस्थे शुभग्रहयुतेक्षिते। जातकः कीर्तिमान् भोगी दीर्घायुः सुभगो भवेत्॥",
        "translation_hi": "यदि लग्नेश केन्द्र अथवा त्रिकोण भाव में शुभ ग्रहों से युक्त या दृष्ट हो, तो जातक कीर्तिमान, भोगी, दीर्घायु और भाग्यशाली होता है।",
        "translation_en": "When the Ascendant Lord occupies a Kendra or Trikona aspected or conjoined by benefics, the native gains enduring fame, vitality, and fortune.",
        "principles": ["Lagna Lord in Kendra or Trikona fortifies vitality and whole chart strength.", "Benefic aspect multiplies auspiciousness."]
    },
    {
        "id": "BPHS_10TH_CAREER_01",
        "grantha": "Brihat Parashara Hora Shastra",
        "author": "Maharishi Parashara",
        "chapter": "Adhyaya 20 - Karmabhavaphala",
        "theme": "career_and_profession",
        "shloka_sanskrit": "दशमेशे बलोपेते राजयोगसमन्विते। कीर्तिं मानं च राज्यं च लभते नात्र संशयः॥",
        "translation_hi": "जब दशम भाव का स्वामी बली होकर राजयोग से युक्त हो, तो जातक को उच्च पद, मान-सम्मान और आजीविका में उत्कृष्ट सफलता प्राप्त होती है।",
        "translation_en": "A powerful 10th house lord aligned with Raja Yogas brings high authority, social honour, and professional pre-eminence.",
        "principles": ["10th lord strength directly governs public reputation and status.", "Connection with 9th lord forms Dharma-Karmadhipati Raja Yoga."]
    },
    {
        "id": "SARAVALI_GAJAKESARI_01",
        "grantha": "Saravali",
        "author": "Kalyanavarma",
        "chapter": "Adhyaya 31 - Raja Yoga",
        "theme": "wisdom_and_prosperity",
        "shloka_sanskrit": "केन्द्रे देवगुरौ शशाङ्कसहिते तद्दृष्टिसंप्रापिते। गजकेसरीति विख्यातो मन्त्री वा नृपतिर्भवेत्॥",
        "translation_hi": "चन्द्रमा से केन्द्र में बृहस्पति के होने अथवा परस्पर शुभ दृष्टि होने से गजकेसरी योग बनता है; जातक तेजस्वी, विद्वान और यशस्वी होता है।",
        "translation_en": "When Jupiter is in an angle from Moon or mutually conjoined without debility, Gajakesari Yoga is formed, endowing supreme intellect and righteous wealth.",
        "principles": ["Jupiter-Moon Kendra relationship creates lasting intellectual authority.", "Debilitation or combustion mitigates base strength."]
    },
    {
        "id": "PHALADEEPIKA_DASHA_01",
        "grantha": "Phaladeepika",
        "author": "Mantreshwara",
        "chapter": "Adhyaya 19 - Dasha Phala Nirupana",
        "theme": "vimshottari_dasha",
        "shloka_sanskrit": "दशाधिपो यद्भावेशः शुभे वा यदि वाऽशुभे। तत्तद्भावफलं दत्ते स्वपाके कालसंयुतः॥",
        "translation_hi": "दशा स्वामी जिस भाव का स्वामी होता है और जहां स्थित होता है, अपनी महादशा व अन्तर्दशा में उसी भाव के शुभाशुभ फल प्रदान करता है।",
        "translation_en": "The operating dasha lord bestows the fruits of the houses it owns and occupies, modified by the sub-period lord's natural rapport.",
        "principles": ["Operating Mahadasha activates natal house significations.", "Antardasha fine-tunes precise manifestation windows."]
    },
    {
        "id": "JAIMINI_ATMAKARAKA_01",
        "grantha": "Jaimini Upadesha Sutras",
        "author": "Maharishi Jaimini",
        "chapter": "Adhyaya 1 - Pada 1",
        "theme": "soul_indicator",
        "shloka_sanskrit": "अंशाधिकः कारकोऽन्त्यांशतः आत्मकारकः॥",
        "translation_hi": "राशियों में जिस ग्रह के भोग्यांश (डिग्री) सबसे अधिक होते हैं, वही जातक का आत्मकारक (आत्मा का प्रतीक) ग्रह बनता है।",
        "translation_en": "The planet with the highest longitude in degrees within its respective sign is designated as the Atmakaraka, king of the horoscope.",
        "principles": ["Atmakaraka dictates the soul's primary karmic evolution.", "Navamsha position of AK constitutes Karakamsha Lagna."]
    },
    {
        "id": "TAJIKA_ITHASALA_01",
        "grantha": "Tajika Neelakanthi",
        "author": "Neelakantha Daivajna",
        "chapter": "Samjna Tantra - Ithasala Yoga",
        "theme": "annual_and_prashna",
        "shloka_sanskrit": "शीघ्रगः पृष्ठगो मन्दश्चाग्रे स्याद्दीप्तभागतः। इत्थशालं समाख्यातं कार्यसिद्धिप्रदं नृणाम्॥",
        "translation_hi": "जब तीव्रगामी ग्रह कम डिग्री पर और मन्दगामी ग्रह अधिक डिग्री पर दीप्तांश की सीमा में दृष्टि संबंध बनाते हैं, तब इत्थशाल योग सिद्ध होता है जो कार्यसिद्धि देता है।",
        "translation_en": "When a faster planet with lower degrees aspects a slower planet within orb (deepthamsa), Ithasala yoga forms, confirming the completion of the desired matter.",
        "principles": ["Ithasala is the fundamental positive aspect in Varshaphal and Prashna.", "Separating aspects (Ishrafa) indicate completion or missed opportunity."]
    },
    {
        "id": "PRASHNA_MARGA_KARYA_01",
        "grantha": "Prashna Marga",
        "author": "Panakkattu Namboodiri",
        "chapter": "Adhyaya 5 - Prashna Lagna Vivada",
        "theme": "horary_prashna",
        "shloka_sanskrit": "आरूढलग्नोदययोः सामरस्ये च चन्द्रमः। प्रश्नकार्यं समाप्नोति निर्विघ्नं दैवयोगतः॥",
        "translation_hi": "आरूढ़ लग्न, उदित लग्न और चन्द्रमा यदि परस्पर शुभ भावों में हों, तो पूछे गए प्रश्न का कार्य निर्विघ्न संपन्न होता है।",
        "translation_en": "When the Udaya Lagna, Arudha Lagna, and Moon are benefic and harmoniously placed, the queried endeavor succeeds without impediment.",
        "principles": ["Query moment ascendant mirrors immediate cosmic intent.", "Moon's application defines immediate outcome velocity."]
    }
]


class ShastriyaKnowledgeBase:
    """Searchable Repository of classical Jyotish Granthas."""

    def __init__(self):
        self.passages: List[ShastraPassage] = [
            ShastraPassage(
                id=c["id"],
                grantha=c["grantha"],
                author=c["author"],
                chapter=c["chapter"],
                theme=c["theme"],
                shloka_sanskrit=c.get("shloka_sanskrit"),
                translation_hi=c["translation_hi"],
                translation_en=c["translation_en"],
                principles=c["principles"]
            )
            for c in CLASSICAL_SHASTRA_CHUNKS
        ]

    def search(self, query: str, theme: Optional[str] = None, limit: int = 3) -> List[ShastraPassage]:
        """Searches classical shastra passages by keywords and theme."""
        q_lower = query.lower()
        scored: List[tuple] = []

        for p in self.passages:
            score = 0
            if theme and theme.lower() in p.theme.lower():
                score += 3
            if q_lower in p.grantha.lower():
                score += 2
            if q_lower in p.chapter.lower() or q_lower in p.theme.lower():
                score += 2
            for principle in p.principles:
                if any(w in principle.lower() for w in q_lower.split()):
                    score += 1
            if q_lower in p.translation_hi or q_lower in p.translation_en:
                score += 2
            scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]


# Singleton Knowledge Base instance
default_knowledge_base = ShastriyaKnowledgeBase()

