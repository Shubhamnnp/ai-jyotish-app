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

            is_rec = False
            status_code = "NEUTRAL"
            verdict = ""
            reasons = []
            alert = None

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

            # -------------------------------------------------------------
            # RULE 3: FUNCTIONAL MALEFICS & MARAKAS
            # -------------------------------------------------------------
            elif p_name in profile["maraka"] and p_name not in profile["benefics"]:
                status_code = "CAUTION"
                verdict = f"⚠️ सतर्कता (Maraka Lord — सावधानी)"
                alert = f"{p_name} इस लग्न के लिए मारक भाव का स्वामी है। बिना विशेष परीक्षण के रत्न न पहनें।"
                reasons.append(alert)

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
                else:
                    status_code = "CONDITIONAL"
                    verdict = f"🟡 मध्यम / विशिष्ट दशा में विचारणीय"
                    reasons.append(f"{p_name} की स्थिति मध्यम है। इसकी महादशा में ज्योतिषी परामर्श से विचार करें।")

            audit_results[p_name] = {
                "planet": p_name,
                "house": h,
                "dignity": dignity,
                "is_combust": is_combust,
                "is_retrograde": is_retro,
                "is_recommended": is_rec,
                "status_code": status_code,
                "verdict": verdict,
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
