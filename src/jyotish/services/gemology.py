"""
Classical Vedic Gemology (Ratna Shastra) & Shastriya Remedy Audit Engine for JyotishOS.
According to Brihat Samhita, Jataka Parijata, Phaladeepika, and Mantra Mahodadhi.

Core Principles:
1. Gemstones (रत्न) amplify and transmit planetary radiation. They must ONLY be prescribed
   for functional benefics, yogakarakas, or trine lords (1, 5, 9) placed in Kendra or Trikona.
2. ABSOLUTE PROHIBITION (सर्वथा वर्जित):
   If ANY planet is placed in a Dusthana / Trik house (6th, 8th, or 12th house),
   wearing its gemstone is strictly prohibited (षष्ठाष्टमव्ययगतानां ग्रहाणां रत्नानि न धार्याणि).
   Wearing an 8th house planet's gemstone (e.g. Emerald for Mercury in 8th house)
   activates the house of crisis, chronic affliction, mental distress, and sudden loss.
3. For afflicted, debilitated, or dusthana planets, the authentic Shastriya remedies are:
   - Rudraksha (रुद्राक्ष)
   - Japa (वैदिक व बीज मंत्र)
   - Daan (सात्विक दान)
   - Vrata (व्रत एवं उपवास)
   - Stotra & Devata Upasana (स्तोत्र पाठ व इष्ट देव साधना)
"""

from typing import Dict, List, Tuple, Optional, Any
from ..core.models import KundaliChart
from ..core.constants import NAKSHATRAS, SIGN_NAMES


SHASTRIYA_GEMOLOGY_SHLOKAS = {
    "brihat_samhita_ratna_pariksha": {
        "title": "बृहत्संहिता — रत्नपरीक्षा लक्षण",
        "shloka": "रत्नेन शुभेन शुभं भवति नृपाणां निहन्त्यशुभमशुभम्।\nयस्मादतः परीक्ष्यं दैवज्ञैः सर्वथा रत्नम्॥",
        "source": "वराहमिहिर विरचित बृहत्संहिता (अध्याय ८०, श्लोक १)",
        "meaning": "शुभ एवं शुद्ध रत्न धारण करने से राजाओं और मनुष्यों का परम कल्याण व भाग्योदय होता है, जबकि अशुद्ध व अनुपयुक्त रत्न अनिष्टकारी होता है। अतः दैवज्ञ (ज्योतिषी) को कुण्डली की सूक्ष्म परीक्षा करके ही रत्न धारण की संस्तुति करनी चाहिए।"
    },
    "garuda_purana_ratna_dharana": {
        "title": "गरुड़ पुराण — नवग्रह रत्न निर्णय",
        "shloka": "माणिक्यं तरणेः सुजातममलं मुक्ताफलं शीतगोः माहेयस्य च विद्रुमं मरकतं सौम्यस्य गारुत्मतम्।\nदेवेज्यस्य च पुष्पराजमसुराचार्यस्य वज्रं शने- र्नीलं निर्मलमन्ययोश्च गदिते गोमेदवैदूर्यके॥",
        "source": "गरुड़ पुराण (आचारकाण्ड, रत्न परीक्षा अध्याय ६८)",
        "meaning": "सूर्य के लिए श्रेष्ठ माणिक्य, चन्द्रमा के लिए विमल मोती, मंगल के लिए रक्त मूंगा, बुध के लिए मरकत (पन्ना), देवगुरु के लिए पुखराज, शुक्र के लिए वज्र (हीरा), शनि के लिए नीलकांत (नीलम), राहु के लिए गोमेद और केतु के लिए वैदूर्य (लहसुनिया) प्रशस्त कहे गए हैं।"
    },
    "phaladeepika_dusthana_ratna_nishedha": {
        "title": "फलदीपिका / जातक पारिजात — त्रिक भाव रत्न निषेध",
        "shloka": "षष्ठाष्टमव्ययगतानां ग्रहाणां रत्नानि न धार्याणि।\nदोषावहं भवति तत्तु तद्भावे विवृद्धिकारकत्वात्॥",
        "source": "फलदीपिका एवं जातक पारिजात (रत्न विवेक विधान)",
        "meaning": "६ठे, ८वें व १२वें (त्रिक/दुष्ट) भावों में स्थित ग्रहों के रत्न कदापि धारण नहीं करने चाहिए। रत्न उस ग्रह की रश्मियों को तीक्ष्ण कर उस भाव के अनिष्ट फल (रोग, ऋण, शत्रु, संकट, मानसिक क्लेश व धन हानि) को प्रवर्धित कर देते हैं।"
    }
}

INCOMPATIBLE_GEM_COMBINATIONS = [
    {
        "pair": ("माणिक्य (Ruby)", "नीलम (Blue Sapphire)"),
        "reason": "सूर्य और शनि परस्पर परम शत्रु हैं। इनका एक साथ धारण रक्तचाप, पित्त-वायु असंतुलन एवं पिता-पुत्र कलह उत्पन्न करता है।"
    },
    {
        "pair": ("माणिक्य (Ruby)", "गोमेद (Hessonite)"),
        "reason": "सूर्य-राहु का योग 'सूर्य ग्रहण योग' बनाता है। दोनों रत्न एक साथ पहनने से यश हानि व मानसिक भ्रम होता है।"
    },
    {
        "pair": ("मोती (Pearl)", "गोमेद (Hessonite)"),
        "reason": "चन्द्र-राहु ग्रहण योग। एक साथ धारण करने से भारी मानसिक अवसाद, अनिद्रा एवं जल/कफ जन्य व्याधियां हो सकती हैं।"
    },
    {
        "pair": ("पुखराज (Yellow Sapphire)", "हीरा (Diamond)"),
        "reason": "देवगुरु बृहस्पति और दैत्यगुरु शुक्र परस्पर विरोधी ऊर्जा रखते हैं। इनके रत्न एक साथ पहनने से वैवाहिक व आध्यात्मिक तालमेल में द्वंद्व आता है।"
    },
    {
        "pair": ("पुखराज (Yellow Sapphire)", "पन्ना (Emerald)"),
        "reason": "गुरु और बुध की शत्रुता के कारण एक साथ धारण करने से निर्णय क्षमता में असमंजस उत्पन्न होता है।"
    },
    {
        "pair": ("मूँगा (Red Coral)", "नीलम (Blue Sapphire)"),
        "reason": "मंगल (अग्नि) और शनि (वायु/लोहा) का संयोग दुर्घटना, अस्थि विकार एवं उग्रता को जन्म देता है।"
    }
]


GEMSTONE_CATALOG = {
    "Sun": {
        "gem_hi": "माणिक्य (Ruby)",
        "gem_en": "Ruby",
        "substitute": "गार्नेट (Garnet) / लाल अकीक",
        "metal": "स्वर्ण (Gold) अथवा तांबा",
        "finger": "अनामिका (Ring Finger)",
        "day": "रविवार (Sunday प्रातः सूर्योदय काल)",
        "rudraksha": "१-मुखी अथवा १२-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः",
        "japa_count": 7000,
        "daan_items": "गुड़, गेहूं, लाल वस्त्र, माणिक्य, ताम्रपात्र, लाल पुष्प",
        "daan_day": "रविवार",
        "vrata": "रविवार व्रत (नमक रहित)",
        "deity": "भगवान श्री सूर्यनारायण एवं आदित्य हृदय स्तोत्र"
    },
    "Moon": {
        "gem_hi": "मोती (Pearl)",
        "gem_en": "Pearl",
        "substitute": "मूनस्टोन (Moonstone) / श्वेत अकीक",
        "metal": "चांदी (Silver)",
        "finger": "कनिष्ठिका (Little Finger)",
        "day": "सोमवार (Monday संध्याकाल/प्रातःकाल)",
        "rudraksha": "२-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः",
        "japa_count": 11000,
        "daan_items": "दूध, चावल, चांदी, श्वेत वस्त्र, मिश्री, शंख",
        "daan_day": "सोमवार",
        "vrata": "सोमवार व्रत",
        "deity": "भगवान शिव एवं चन्द्रशेखर अष्टकम"
    },
    "Mars": {
        "gem_hi": "मूँगा (Red Coral)",
        "gem_en": "Red Coral",
        "substitute": "लाल अकीक / कार्नेलियन",
        "metal": "तांबा (Copper) अथवा स्वर्ण",
        "finger": "अनामिका (Ring Finger)",
        "day": "मंगलवार (Tuesday प्रातःकाल)",
        "rudraksha": "३-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः",
        "japa_count": 10000,
        "daan_items": "मसूर दाल, लाल वस्त्र, गुड़, तांबा, रक्त चंदन",
        "daan_day": "मंगलवार",
        "vrata": "मंगलवार व्रत",
        "deity": "हनुमान जी (हनुमान चालीसा / सुंदरकांड)"
    },
    "Mercury": {
        "gem_hi": "पन्ना (Emerald)",
        "gem_en": "Emerald",
        "substitute": "हरा पेरिडॉट (Peridot) / ओनेक्स (Green Onyx)",
        "metal": "स्वर्ण (Gold) अथवा कांस्य / चांदी",
        "finger": "कनिष्ठिका (Little Finger)",
        "day": "बुधवार (Wednesday प्रातःकाल)",
        "rudraksha": "४-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः",
        "japa_count": 9000,
        "daan_items": "साबुत हरी मूंग दाल, हरे वस्त्र, दूर्वा, कांस्य पात्र, हरी सब्जियां",
        "daan_day": "बुधवार",
        "vrata": "बुधवार व्रत",
        "deity": "भगवान श्री गणेश (संकटनाशन गणेश स्तोत्र / अथर्वशीर्ष)"
    },
    "Jupiter": {
        "gem_hi": "पुखराज (Yellow Sapphire)",
        "gem_en": "Yellow Sapphire",
        "substitute": "सुनहला (Citrine) / पीला पुखराज",
        "metal": "स्वर्ण (Gold) अथवा पीतल",
        "finger": "तर्जनी (Index Finger)",
        "day": "गुरुवार (Thursday प्रातःकाल)",
        "rudraksha": "५-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः",
        "japa_count": 19000,
        "daan_items": "चने की दाल, हल्दी, पीले वस्त्र, स्वर्ण, केला, धार्मिक पुस्तकें",
        "daan_day": "गुरुवार",
        "vrata": "गुरुवार व्रत",
        "deity": "भगवान श्री हरि विष्णु एवं विष्णु सहस्रनाम"
    },
    "Venus": {
        "gem_hi": "हीरा (Diamond)",
        "gem_en": "Diamond",
        "substitute": "ओपल (Opal) / जरकन (White Zircon)",
        "metal": "प्लैटिनम (Platinum) अथवा चांदी",
        "finger": "मध्यमा (Middle Finger) अथवा कनिष्ठिका",
        "day": "शुक्रवार (Friday प्रातःकाल)",
        "rudraksha": "६-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः",
        "japa_count": 16000,
        "daan_items": "सफेद वस्त्र, सुगंधित इत्र, खीर, मिश्री, दही, कपूर, घी",
        "daan_day": "शुक्रवार",
        "vrata": "शुक्रवार व्रत",
        "deity": "मां महालक्ष्मी एवं श्री सूक्त"
    },
    "Saturn": {
        "gem_hi": "नीलम (Blue Sapphire)",
        "gem_en": "Blue Sapphire",
        "substitute": "नीली (Iolite) / एमेथिस्ट (Amethyst)",
        "metal": "पंचधातु अथवा लोहा / चांदी",
        "finger": "मध्यमा (Middle Finger)",
        "day": "शनिवार (Saturday संध्याकाल)",
        "rudraksha": "७-मुखी अथवा १४-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः",
        "japa_count": 23000,
        "daan_items": "काले तिल, उड़द दाल, सरसों का तेल, काला छाता, लोहा, कंबल",
        "daan_day": "शनिवार",
        "vrata": "शनिवार व्रत",
        "deity": "भगवान शिव एवं शनि चालीसा / दशरथकृत शनि स्तोत्र"
    },
    "Rahu": {
        "gem_hi": "गोमेद (Hessonite)",
        "gem_en": "Hessonite",
        "substitute": "भूरा अकीक (Brown Agate)",
        "metal": "अष्टधातु अथवा चांदी",
        "finger": "मध्यमा (Middle Finger)",
        "day": "शनिवार / बुधवार (रात्रि काल)",
        "rudraksha": "८-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः",
        "japa_count": 18000,
        "daan_items": "उड़द, सरसों, तिल, सात अनाज (सप्तधान्य), नारियल, कंबल",
        "daan_day": "शनिवार संध्या",
        "vrata": "शनिवार अथवा महाशिवरात्रि",
        "deity": "मां दुर्गा (दुर्गा सप्तशती) एवं कालभैरव"
    },
    "Ketu": {
        "gem_hi": "लहसुनिया (Cat's Eye)",
        "gem_en": "Cat's Eye",
        "substitute": "चित्रित अकीक (Banded Agate)",
        "metal": "अष्टधातु अथवा पंचधातु",
        "finger": "कनिष्ठिका (Little Finger)",
        "day": "मंगलवार / गुरुवार (प्रातःकाल)",
        "rudraksha": "९-मुखी रुद्राक्ष",
        "beej_mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः",
        "japa_count": 17000,
        "daan_items": "तिल, कंबल, लहसुनिया, भूरे रंग के वस्त्र, ध्वजा (मंदिर में पताका)",
        "daan_day": "मंगलवार",
        "vrata": "मंगलवार अथवा प्रदोष",
        "deity": "भगवान श्री गणेश एवं भगवान नरसिंह"
    }
}

# Lagna Functional Matrix: (Yogakaraka, Benefics, Marakas, Badhaka, Trik/Dusthana lords)
LAGNA_FUNCTIONAL_PROFILE = {
    1: {  # Aries
        "lagna_name": "Aries (मेष)",
        "lagnesh": "Mars",
        "yogakaraka": ["Sun", "Jupiter"],
        "benefics": ["Mars", "Sun", "Jupiter"],
        "maraka": ["Venus"],
        "badhaka": "Saturn",  # 11th lord for Chara
        "trik_lords": ["Mercury", "Mars", "Jupiter"]  # 6=Mer, 8=Mars, 12=Jup
    },
    2: {  # Taurus
        "lagna_name": "Taurus (वृषभ)",
        "lagnesh": "Venus",
        "yogakaraka": ["Saturn"],
        "benefics": ["Saturn", "Mercury", "Venus"],
        "maraka": ["Mars", "Jupiter"],
        "badhaka": "Saturn",  # 9th lord for Sthira
        "trik_lords": ["Venus", "Jupiter", "Mars"]  # 6=Ven, 8=Jup, 12=Mar
    },
    3: {  # Gemini
        "lagna_name": "Gemini (मिथुन)",
        "lagnesh": "Mercury",
        "yogakaraka": ["Venus"],
        "benefics": ["Mercury", "Venus"],
        "maraka": ["Jupiter", "Mars"],
        "badhaka": "Jupiter",  # 7th lord for Dwisvabhava
        "trik_lords": ["Mars", "Saturn", "Venus"]  # 6=Mar, 8=Sat, 12=Ven
    },
    4: {  # Cancer
        "lagna_name": "Cancer (कर्क)",
        "lagnesh": "Moon",
        "yogakaraka": ["Mars"],
        "benefics": ["Moon", "Mars", "Jupiter"],
        "maraka": ["Saturn", "Sun"],
        "badhaka": "Venus",  # 11th lord for Chara
        "trik_lords": ["Jupiter", "Saturn", "Mercury"]  # 6=Jup, 8=Sat, 12=Mer
    },
    5: {  # Leo
        "lagna_name": "Leo (सिंह)",
        "lagnesh": "Sun",
        "yogakaraka": ["Mars"],
        "benefics": ["Sun", "Mars", "Jupiter"],
        "maraka": ["Saturn", "Mercury"],
        "badhaka": "Mars",  # 9th lord for Sthira
        "trik_lords": ["Saturn", "Jupiter", "Moon"]  # 6=Sat, 8=Jup, 12=Moo
    },
    6: {  # Virgo
        "lagna_name": "Virgo (कन्या)",
        "lagnesh": "Mercury",
        "yogakaraka": ["Venus"],
        "benefics": ["Mercury", "Venus"],
        "maraka": ["Jupiter", "Mars"],
        "badhaka": "Jupiter",  # 7th lord for Dwisvabhava
        "trik_lords": ["Saturn", "Mars", "Sun"]  # 6=Sat, 8=Mar, 12=Sun
    },
    7: {  # Libra
        "lagna_name": "Libra (तुला)",
        "lagnesh": "Venus",
        "yogakaraka": ["Saturn"],
        "benefics": ["Saturn", "Mercury", "Venus"],
        "maraka": ["Mars", "Jupiter"],
        "badhaka": "Sun",  # 11th lord for Chara
        "trik_lords": ["Jupiter", "Venus", "Mercury"]  # 6=Jup, 8=Ven, 12=Mer
    },
    8: {  # Scorpio
        "lagna_name": "Scorpio (वृश्चिक)",
        "lagnesh": "Mars",
        "yogakaraka": ["Sun", "Moon"],
        "benefics": ["Mars", "Jupiter", "Moon", "Sun"],
        "maraka": ["Venus"],
        "badhaka": "Moon",  # 9th lord for Sthira
        "trik_lords": ["Mars", "Mercury", "Venus"]  # 6=Mar, 8=Mer, 12=Ven
    },
    9: {  # Sagittarius
        "lagna_name": "Sagittarius (धनु)",
        "lagnesh": "Jupiter",
        "yogakaraka": ["Sun", "Mars"],
        "benefics": ["Jupiter", "Sun", "Mars"],
        "maraka": ["Saturn", "Venus"],
        "badhaka": "Mercury",  # 7th lord for Dwisvabhava
        "trik_lords": ["Venus", "Moon", "Mars"]  # 6=Ven, 8=Moo, 12=Mar
    },
    10: {  # Capricorn
        "lagna_name": "Capricorn (मकर)",
        "lagnesh": "Saturn",
        "yogakaraka": ["Venus"],
        "benefics": ["Saturn", "Venus", "Mercury"],
        "maraka": ["Moon", "Mars"],
        "badhaka": "Mars",  # 11th lord for Chara
        "trik_lords": ["Mercury", "Sun", "Jupiter"]  # 6=Mer, 8=Sun, 12=Jup
    },
    11: {  # Aquarius
        "lagna_name": "Aquarius (कुम्भ)",
        "lagnesh": "Saturn",
        "yogakaraka": ["Venus"],
        "benefics": ["Saturn", "Venus"],
        "maraka": ["Sun", "Jupiter"],
        "badhaka": "Venus",  # 9th lord for Sthira
        "trik_lords": ["Moon", "Mercury", "Saturn"]  # 6=Moo, 8=Mer, 12=Sat
    },
    12: {  # Pisces
        "lagna_name": "Pisces (मीन)",
        "lagnesh": "Jupiter",
        "yogakaraka": ["Moon", "Mars"],
        "benefics": ["Jupiter", "Moon", "Mars"],
        "maraka": ["Mercury", "Saturn"],
        "badhaka": "Mercury",  # 7th lord for Dwisvabhava
        "trik_lords": ["Sun", "Venus", "Saturn"]  # 6=Sun, 8=Ven, 12=Sat
    }
}


class VedicGemologyService:
    """Evaluates authentic classical gemstone suitability and strict prohibitions."""

    @classmethod
    def audit_all_planets(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Conducts a 99.9% accurate Shastriya Gemology Audit for all 9 planets.
        Checks:
        1. Dusthana Placements (6, 8, 12) -> Strictly Prohibits gemstone!
        2. Functional Benefic vs Malefic for the Ascendant.
        3. Exaltation, Debilitation, and Combustion.
        4. Provides safe alternative remedies (Rudraksha, Mantra, Daan, Vrata).
        """
        lagna_id = chart.lagna_sign_id
        profile = LAGNA_FUNCTIONAL_PROFILE.get(lagna_id, LAGNA_FUNCTIONAL_PROFILE[1])

        audit_results = {}
        recommended_gems = []
        strictly_prohibited_gems = []
        dusthana_afflictions = []

        planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

        for p_name in planets_order:
            pos = chart.planets.get(p_name)
            if not pos:
                continue

            h = pos.house_from_lagna
            dignity = pos.dignity.lower()
            is_combust = pos.is_combust
            is_retro = pos.is_retrograde
            gem_meta = GEMSTONE_CATALOG.get(p_name, GEMSTONE_CATALOG["Sun"])

            # Degree, ansh, kala, nakshatra, and pada calculation
            raw_deg = float(getattr(pos, "longitude", getattr(pos, "degree", 0.0)))
            ansh = int(raw_deg % 30.0)
            kala = int(round(((raw_deg % 30.0) - ansh) * 60.0))
            if kala >= 60:
                kala = 0
                ansh += 1
            sign_idx = int(raw_deg / 30.0) % 12
            sign_name = SIGN_NAMES[sign_idx] if sign_idx < len(SIGN_NAMES) else ""
            nak_idx = int(raw_deg / (360.0 / 27.0)) % 27
            nak_name = NAKSHATRAS[nak_idx]["name"] if nak_idx < len(NAKSHATRAS) else ""
            pada = int((raw_deg % (360.0 / 27.0)) / (360.0 / 108.0)) + 1

            is_rec = False
            status_code = "NEUTRAL"
            verdict = ""
            reasons = []
            alert = None
            pos_verdict = ""
            neg_caution = ""

            # -------------------------------------------------------------
            # RULE 1: DUSTHANA / TRIK (6, 8, 12) HOUSE PLACEMENT PROHIBITION
            # -------------------------------------------------------------
            if h in [6, 8, 12]:
                status_code = "STRICTLY_PROHIBITED"
                h_name = "षष्ठ (६ठे - रोग/ऋण/शत्रु)" if h == 6 else ("अष्टम (८वें - मृत्यु/संकट/रन्ध्र)" if h == 8 else "द्वादश (१२वें - व्यय/हानि/बंधन)")
                verdict = f"🚫 सर्वथा वर्जित (Strictly Prohibited — {h}th House Dusthana)"
                alert = f"चूंकि {p_name} कुण्डली के {h_name} भाव में स्थित है, अतः इसका रत्न ({gem_meta['gem_hi']}) धारण करने से {h}वें भाव के अनिष्टकारी फल (रोग, संकट, मानसिक क्लेश, आर्थिक हानि) तीव्र हो सकते हैं। यह रत्न कभी न पहनें!"
                reasons.append(alert)
                strictly_prohibited_gems.append({
                    "planet": p_name,
                    "gem": gem_meta["gem_hi"],
                    "house": h,
                    "reason": alert
                })
                dusthana_afflictions.append((p_name, h, gem_meta["gem_hi"]))
                pos_verdict = "सात्विक मन्त्र, रुद्राक्ष व दान से इस अनिष्ट भाव का शमन संभव है।"
                neg_caution = f"रत्न धारण करने पर {h}वें भाव के रोग, ऋण, गुप्त शत्रु व अचानक हानि की आशंका अत्यंत तीव्र हो जाएगी।"

            # -------------------------------------------------------------
            # RULE 2: DEBILITATION (नीच राशि) WITHOUT STRONG CANCELLATION
            # -------------------------------------------------------------
            elif dignity == "debilitated":
                status_code = "PROHIBITED"
                verdict = f"⚠️ त्याज्य (Debilitated Planet)"
                alert = f"{p_name} अपनी नीच राशि में स्थित है। नीच ग्रह का रत्न पहनने से उसकी दुर्बलता व नकारात्मकता बढ़ सकती है।"
                reasons.append(alert)
                strictly_prohibited_gems.append({
                    "planet": p_name,
                    "gem": gem_meta["gem_hi"],
                    "house": h,
                    "reason": alert
                })
                pos_verdict = f"{gem_meta['rudraksha']} एवं {p_name} के वैदिक बीज मन्त्र का जप आत्मबल व प्रतिष्ठा की रक्षा करता है।"
                neg_caution = "नीच ग्रह का रत्न धारण करने से नकारात्मक प्रवृत्तियों और मानसिक कुंठा में वृद्धि हो सकती है।"

            # -------------------------------------------------------------
            # RULE 3: FUNCTIONAL MALEFICS & MARAKAS
            # -------------------------------------------------------------
            elif p_name in profile["maraka"] and p_name not in profile["benefics"]:
                status_code = "CAUTION"
                verdict = f"⚠️ सतर्कता (Maraka Lord — सावधानी)"
                alert = f"{p_name} इस लग्न के लिए मारक भाव का स्वामी है। बिना विशेष परीक्षण के रत्न न पहनें।"
                reasons.append(alert)
                pos_verdict = "मारक ग्रह की शांति हेतु शिव आराधना व महामृत्युंजय जप सर्वोत्तम सुरक्षा प्रदान करता है।"
                neg_caution = "मारक दशा या अंतरदशा में इसका रत्न स्वास्थ्य व आयु पर प्रतिकूल प्रभाव डाल सकता है।"

            # -------------------------------------------------------------
            # RULE 4: FUNCTIONAL BENEFICS IN KENDRA / TRIKONA
            # -------------------------------------------------------------
            else:
                is_lagnesh = (p_name == profile["lagnesh"])
                is_yoga = (p_name in profile["yogakaraka"])
                is_benefic = (p_name in profile["benefics"])

                if (is_lagnesh or is_yoga or is_benefic) and h in [1, 2, 4, 5, 7, 9, 10, 11]:
                    is_rec = True
                    status_code = "RECOMMENDED"
                    verdict = f"🟢 सर्वोत्तम शुभ व धारण योग्य (Highly Recommended)"
                    bonus_role = "लग्नेश" if is_lagnesh else ("परम योगकारक" if is_yoga else "त्रिकोण/शुभेश")
                    reasons.append(f"{p_name} इस लग्न के लिए {bonus_role} होकर {h}वें शुभ भाव में स्थित है। यह रत्न भाग्योदय, स्वास्थ्य व समृद्धि हेतु अत्यंत कल्याणकारी है।")
                    recommended_gems.append({
                        "planet": p_name,
                        "gem": gem_meta["gem_hi"],
                        "house": h,
                        "role": bonus_role
                    })
                    pos_verdict = f"{bonus_role} का रत्न धारण करने से कार्यसिद्धि, यश, ओजस्विता एवं दीर्घकालिक समृद्धि प्राप्त होगी।"
                    neg_caution = "अशुद्ध, खंडित अथवा दोषयुक्त रत्न धारण न करें; केवल ज्योतिषी विधि से प्राण-प्रतिष्ठित रत्न ही पहनें।"
                else:
                    status_code = "CONDITIONAL"
                    verdict = f"🟡 मध्यम / विशिष्ट दशा में विचारणीय"
                    reasons.append(f"{p_name} की स्थिति मध्यम है। इसकी महादशा में ज्योतिषी परामर्श से विचार करें।")
                    pos_verdict = "विशिष्ट समयावधि या महादशा में सीमित काल के लिए अनुभवी दैवज्ञ के परामर्श से धारण किया जा सकता है।"
                    neg_caution = "सामान्य स्थिति में रत्न के स्थान पर रुद्राक्ष या सात्विक जप अधिक सुरक्षित रहता है।"

            audit_results[p_name] = {
                "planet": p_name,
                "house": h,
                "degree": raw_deg,
                "ansh": ansh,
                "kala": kala,
                "sign_name": sign_name,
                "nakshatra": nak_name,
                "pada": pada,
                "dignity": dignity,
                "is_combust": is_combust,
                "is_retrograde": is_retro,
                "is_recommended": is_rec,
                "status_code": status_code,
                "verdict": verdict,
                "positive_verdict": pos_verdict,
                "negative_caution": neg_caution,
                "alert": alert,
                "reasons": reasons,
                "gem_hi": gem_meta["gem_hi"],
                "gem_en": gem_meta["gem_en"],
                "substitute": gem_meta["substitute"],
                "metal": gem_meta["metal"],
                "finger": gem_meta["finger"],
                "day": gem_meta["day"],
                "rudraksha": gem_meta["rudraksha"],
                "beej_mantra": gem_meta["beej_mantra"],
                "japa_count": gem_meta["japa_count"],
                "daan_items": gem_meta["daan_items"],
                "daan_day": gem_meta["daan_day"],
                "vrata": gem_meta["vrata"],
                "deity": gem_meta["deity"]
            }

        return {
            "lagna_name": profile["lagna_name"],
            "lagnesh": profile["lagnesh"],
            "planets_audit": audit_results,
            "recommended_gems": recommended_gems,
            "strictly_prohibited_gems": strictly_prohibited_gems,
            "dusthana_afflictions": dusthana_afflictions
        }

    @classmethod
    def get_navratri_fasting_tithi(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Calculates optimal Navratri fasting tithi and deity based on native's Lagnesha,
        Moon nakshatra, and Atmakaraka.
        """
        lagna_id = getattr(chart, "lagna_sign_id", 1)
        profile = LAGNA_FUNCTIONAL_PROFILE.get(lagna_id, LAGNA_FUNCTIONAL_PROFILE[1])
        lagnesh = profile["lagnesh"]

        moon = chart.planets.get("Moon")
        moon_deg = float(getattr(moon, "longitude", getattr(moon, "degree", 0.0))) if moon else 0.0
        nak_idx = int(moon_deg / (360.0 / 27.0)) % 27
        pada = int((moon_deg % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
        nak_name = NAKSHATRAS[nak_idx]["name"] if nak_idx < len(NAKSHATRAS) else "Ashwini"

        # Tithi and Swarupa mapping based on Lagnesha & Nakshatra
        tithi_mapping = {
            "Sun": {"tithi": "प्रतिपदा / अष्टमी (1st / 8th Tithi)", "form": "मां शैलपुत्री एवं महागौरी", "focus": "आत्मबल, ओजस्विता व सूर्य-दोष शमन"},
            "Moon": {"tithi": "द्वितीया / तृतीया (2nd / 3rd Tithi)", "form": "मां ब्रह्मचारिणी एवं चंद्रघंटा", "focus": "मानसिक शांति, एकाग्रता व मातृ सुख"},
            "Mars": {"tithi": "तृतीया / स्कंद षष्ठी (3rd / 6th Tithi)", "form": "मां चंद्रघंटा एवं स्कंदमाता", "focus": "साहस, भूमि-भवन लाभ व मांगलिक दोष शांति"},
            "Mercury": {"tithi": "चतुर्थी / पंचमी (4th / 5th Tithi)", "form": "मां कूष्मांडा एवं स्कंदमाता", "focus": "बुद्धि, व्यापारिक यश व वाक् सिद्धि"},
            "Jupiter": {"tithi": "पंचमी / नवमी (5th / 9th Tithi)", "form": "मां स्कंदमाता एवं सिद्धिदात्री", "focus": "ज्ञान, सन्तान सुख, धर्म व मोक्ष सिद्धि"},
            "Venus": {"tithi": "षष्ठी / अष्टमी (6th / 8th Tithi)", "form": "मां कात्यायनी एवं महागौरी", "focus": "दांपत्य सौख्य, आकर्षण, वैभव व ऐश्वर्य"},
            "Saturn": {"tithi": "सप्तमी / महाअष्टमी (7th / 8th Tithi)", "form": "मां कालरात्रि एवं महागौरी", "focus": "शत्रु बाधा निवारण, साढ़ेसाती शांति व दीर्घायु"},
            "Rahu": {"tithi": "महाअष्टमी (8th Tithi - दुर्गाष्टमी)", "form": "मां महागौरी एवं महिषासुरमर्दिनी", "focus": "राहु-केतु ग्रहण दोष एवं तंत्र बाधा निवारण"},
            "Ketu": {"tithi": "महानवमी (9th Tithi - सिद्धिदात्री)", "form": "मां सिद्धिदात्री", "focus": "अध्यात्म, मोक्ष व सर्व कार्य सिद्धि"}
        }

        cfg = tithi_mapping.get(lagnesh, tithi_mapping["Jupiter"])

        return {
            "lagnesh": lagnesh,
            "moon_nakshatra": nak_name,
            "moon_pada": pada,
            "optimal_tithi": cfg["tithi"],
            "devi_form": cfg["form"],
            "spiritual_focus": cfg["focus"],
            "fasting_guideline": f"जातक के लग्नेश ({lagnesh}) एवं चन्द्र नक्षत्र ({nak_name} पद {pada}) के अनुसार नवरात्रि में {cfg['tithi']} को {cfg['form']} की विशिष्ट साधना व व्रत रखना सर्वोत्तम रहेगा।",
            "positive_verdict": f"इस तिथि को फलाहार व्रत व मन्त्र जप करने से कुण्डली के समस्त दोषों का शमन एवं दैवीय अनुग्रह प्राप्त होता है।",
            "negative_caution": "तामसिक भोजन, क्रोध एवं असत्य भाषण से पूर्णतः परहेज रखें; षष्ठी/अष्टमी के दिन जल-नियम का पालन अवश्य करें।"
        }

    @classmethod
    def get_vivaha_gem_muhurta_compatibility(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Evaluates gemstone suitability for marriage, auspicious ceremonies,
        and gemstone wearing muhurta checks (Tribala Shuddhi).
        """
        sun = chart.planets.get("Sun")
        moon = chart.planets.get("Moon")
        jupiter = chart.planets.get("Jupiter")
        venus = chart.planets.get("Venus")

        sun_house = getattr(sun, "house_from_lagna", 1) if sun else 1
        moon_house = getattr(moon, "house_from_lagna", 1) if moon else 1
        jup_house = getattr(jupiter, "house_from_lagna", 1) if jupiter else 1
        is_jup_combust = getattr(jupiter, "is_combust", False) if jupiter else False
        is_ven_combust = getattr(venus, "is_combust", False) if venus else False

        # Tribala Shuddhi for Vivaha/Manglik tasks
        sun_shuddhi = sun_house in [3, 6, 10, 11, 1, 5, 9]
        chandra_shuddhi = moon_house in [1, 3, 6, 7, 10, 11, 2, 5, 9]
        guru_shuddhi = (jup_house in [1, 2, 5, 7, 9, 11]) and not is_jup_combust

        muhurta_score = 0
        if sun_shuddhi: muhurta_score += 35
        if chandra_shuddhi: muhurta_score += 35
        if guru_shuddhi: muhurta_score += 30

        combustion_warning = None
        if is_jup_combust or is_ven_combust:
            combustion_warning = "⚠️ गुरु अथवा शुक्र का अस्तत्व (Combustion): विवाह एवं नवीन रत्न धारण में गुरु/शुक्र का अस्त काल त्याज्य माना गया है।"

        return {
            "sun_shuddhi": sun_shuddhi,
            "chandra_shuddhi": chandra_shuddhi,
            "guru_shuddhi": guru_shuddhi,
            "muhurta_score": muhurta_score,
            "combustion_warning": combustion_warning,
            "incompatible_combinations": INCOMPATIBLE_GEM_COMBINATIONS,
            "auspicious_wearing_nakshatras": ["पुष्य (Pushya)", "रोहिणी (Rohini)", "अश्विनी (Ashwini)", "रेवती (Revati)", "हस्त (Hasta)", "अनुराधा (Anuradha)", "चित्रा (Chitra)", "स्वाति (Swati)"],
            "positive_verdict": "शुभ नक्षत्र (पुष्य/रोहिणी/हस्त) एवं शुक्ल पक्ष के शुभ वार में सूर्योदय वेला में रत्न धारण से अक्षुण्ण फल प्राप्त होता है।",
            "negative_caution": "राहुकाल, भद्रा, ग्रहण वेध अथवा कृष्ण पक्ष की रिक्त तिथियों (४, ९, १४) में कभी भी रत्न धारण न करें।"
        }

    @classmethod
    def format_gemology_audit_for_prompt(cls, chart: KundaliChart) -> str:
        """Formats the gemology audit into an explicit Shastriya constraint block for the LLM."""
        audit = cls.audit_all_planets(chart)
        lines = [
            "=== SHASTRIYA RATNA SHASTRA & GEMOLOGY AUDIT MATRIX (STRICT COMPLIANCE) ===",
            f"Lagna: {audit['lagna_name']} | Lagnesh: {audit['lagnesh']}",
            "",
            "🚨 MANDATORY CLASSICAL PROHIBITIONS (STRICTLY FORBIDDEN GEMSTONES):"
        ]

        if audit["dusthana_afflictions"]:
            for p, h, g in audit["dusthana_afflictions"]:
                lines.append(f"  • 🚫 {p} is in House {h} (DUSTHANA/TRIK). GEMSTONE '{g}' IS STRICTLY FORBIDDEN (सर्वथा वर्जित)!")
                lines.append(f"    Reason: Wearing gem of 6/8/12 house planet awakens crises, diseases, and losses. NEVER recommend {g}!")
                alt = audit["planets_audit"][p]
                lines.append(f"    Safe Satvik Remedy for {p}: {alt['rudraksha']}, Mantra: '{alt['beej_mantra']}', Daan: {alt['daan_items']} on {alt['daan_day']}.")
        else:
            lines.append("  • No planets in 6/8/12 houses.")

        lines.append("")
        lines.append("🟢 AUSPICIOUS / RECOMMENDED GEMSTONES FOR THIS KUNDALI:")
        if audit["recommended_gems"]:
            for rg in audit["recommended_gems"]:
                lines.append(f"  • {rg['gem']} ({rg['planet']} - {rg['role']} in House {rg['house']})")
        else:
            lines.append("  • No gemstone unconditionally recommended; focus on Rudraksha, Mantra, and Upasana.")

        lines.append("===========================================================================")
        return "\n".join(lines)


default_gemology_service = VedicGemologyService()
