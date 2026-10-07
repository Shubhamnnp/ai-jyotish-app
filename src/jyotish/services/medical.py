"""
Medical Astrology and Kalapurusha Anatomy Service for JyotishOS.
Maps 12 houses and signs to the anatomical organs of the Kalapurusha,
evaluates organ vulnerability, computes Ayurvedic Tridosha balance (Vata/Pitta/Kapha),
and generates classical therapeutic herbal, gemstone, and panchakarma remedies.
"""

from typing import Dict, List, Any, Optional
from ..core.constants import SIGN_NAMES, SIGN_LORDS, GRAHAS
from ..core.models import KundaliChart


KALAPURUSHA_ORAGANS = [
    {
        "house": 1,
        "sign": "Aries",
        "organ_hi": "सिर, मस्तिष्क एवं कपाल (Head & Brain)",
        "organ_en": "Head, Brain, Scalp",
        "potential_issues": "सिरदर्द, माइग्रेन, उच्च रक्तचाप, मानसिक तनाव, अनिद्रा।",
        "zone_key": "head"
    },
    {
        "house": 2,
        "sign": "Taurus",
        "organ_hi": "मुख, नेत्र, दांत, वाणी व कंठ (Face, Eyes, Throat)",
        "organ_en": "Face, Eyes, Throat, Teeth",
        "potential_issues": "दृष्टि दोष, दांतों के रोग, टॉन्सिल, थायरॉयड, वाणी विकार।",
        "zone_key": "face"
    },
    {
        "house": 3,
        "sign": "Gemini",
        "organ_hi": "कंधे, भुजाएं, श्वसन नली व कान (Shoulders & Respiratory)",
        "organ_en": "Shoulders, Arms, Lungs Upper, Ears",
        "potential_issues": "कंधों में जकड़न, श्वसन एलर्जी, फेफड़ों में संक्रमण, स्नायु दुर्बलता।",
        "zone_key": "arms"
    },
    {
        "house": 4,
        "sign": "Cancer",
        "organ_hi": "हृदय, वक्षस्थल एवं फेफड़े (Heart & Chest)",
        "organ_en": "Heart, Chest, Lungs Lower",
        "potential_issues": "हृदय धड़कन, रक्तचाप, सीने में जकड़न, कफ संचय, भावनात्मक उद्वेग।",
        "zone_key": "chest"
    },
    {
        "house": 5,
        "sign": "Leo",
        "organ_hi": "आमाशय, यकृत, पित्ताशय व ऊपरी रीढ़ (Stomach & Liver)",
        "organ_en": "Stomach, Liver, Upper Spine",
        "potential_issues": "अम्लपित्त (Acidity), लिवर संवेदनशीलता, अपच, स्पॉन्डिलाइटिस।",
        "zone_key": "stomach"
    },
    {
        "house": 6,
        "sign": "Virgo",
        "organ_hi": "आंतें, गुर्दे एवं पाचन प्रणाली (Intestines & Digestion)",
        "organ_en": "Intestines, Digestion, Appendix",
        "potential_issues": "कब्ज, कोलाइटिस, मधुमेह (Diabetes), रोग प्रतिरोधक क्षमता में कमी।",
        "zone_key": "abdomen"
    },
    {
        "house": 7,
        "sign": "Libra",
        "organ_hi": "कमर, गर्भाशय व गुर्दे (Lower Abdomen & Kidneys)",
        "organ_en": "Pelvis, Kidneys, Reproductive Organs",
        "potential_issues": "किडनी स्टोन, यूरिनरी ट्रैक्ट, कमर दर्द, हार्मोनल असंतुलन।",
        "zone_key": "pelvis"
    },
    {
        "house": 8,
        "sign": "Scorpio",
        "organ_hi": "गुदा, जननांग एवं मलाशय (Excretory & Secret Organs)",
        "organ_en": "Excretory, Colon, Anus",
        "potential_issues": "बवासीर (Piles), फिस्टुला, गुप्त रोग, क्रोनिक विषाक्तता।",
        "zone_key": "genitals"
    },
    {
        "house": 9,
        "sign": "Sagittarius",
        "organ_hi": "जांघें, कूल्हे एवं धमनियां (Thighs & Arteries)",
        "organ_en": "Thighs, Hips, Femoral Arteries",
        "potential_issues": "साइटिका (Sciatica), कूल्हों में दर्द, धमनियों में अवरोध, मोटापा।",
        "zone_key": "thighs"
    },
    {
        "house": 10,
        "sign": "Capricorn",
        "organ_hi": "घुटने, अस्थियां एवं जोड़ (Knees, Bones & Joints)",
        "organ_en": "Knees, Joints, Bones",
        "potential_issues": "गठिया (Arthritis), घुटनों का घिसाव, कैल्शियम की कमी, त्वचा रोग।",
        "zone_key": "knees"
    },
    {
        "house": 11,
        "sign": "Aquarius",
        "organ_hi": "पिंडलियां, टखने व रक्त संचार (Calves & Circulation)",
        "organ_en": "Calves, Shins, Circulatory System",
        "potential_issues": "वेरिकोज वेन्स (Varicose veins), ऐंठन, रक्त संचार में बाधा, पैर दर्द।",
        "zone_key": "calves"
    },
    {
        "house": 12,
        "sign": "Pisces",
        "organ_hi": "पैर के तलवे, बाईं आँख व लिम्फैटिक (Feet & Immune Lymph)",
        "organ_en": "Feet, Toes, Lymphatic, Left Eye",
        "potential_issues": "तलवों में जलन, अनिद्रा, फंगल इन्फेक्शन, लिम्फैटिक सूजन।",
        "zone_key": "feet"
    }
]


class MedicalAstrologyService:
    """Calculates organ afflictions and Tridosha Ayurvedic health parameters."""

    @classmethod
    def analyze_health_profile(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Analyzes 12 organ zones for vulnerability (0-100 score),
        calculates Tridosha balance (Vata/Pitta/Kapha), and provides Ayurvedic remedies.
        """
        planets = chart.planets
        lagna_sign_id = chart.lagna_sign_id

        def get_h_lord(h_num: int) -> str:
            s_id = ((lagna_sign_id - 1 + (h_num - 1)) % 12) + 1
            return SIGN_LORDS[SIGN_NAMES[s_id - 1]]

        l6 = get_h_lord(6)
        l8 = get_h_lord(8)
        l12 = get_h_lord(12)

        malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]

        organ_results = []
        high_risk_organs = []

        for item in KALAPURUSHA_ORAGANS:
            h_num = item["house"]
            # Base vulnerability score
            affliction_score = 15
            reasons = []

            # Check occupants in this house
            house_occupants = []
            for p_name, pos in planets.items():
                if pos.house_from_lagna == h_num:
                    house_occupants.append(p_name)
                    if p_name in malefics:
                        affliction_score += 25
                        reasons.append(f"क्रूर ग्रह {p_name} की स्थिति")
                    if p_name in [l6, l8, l12]:
                        affliction_score += 20
                        reasons.append(f"त्रिकेश ({p_name}) की स्थिति")
                    if p_name in benefics:
                        affliction_score -= 15
                        reasons.append(f"शुभ ग्रह {p_name} की सुरक्षा")

            # Check house lord's dignity and placement
            h_lord = get_h_lord(h_num)
            lord_pos = planets[h_lord]
            if lord_pos.house_from_lagna in [6, 8, 12]:
                affliction_score += 15
                reasons.append(f"भावेश ({h_lord}) का त्रिक भाव में होना")
            if lord_pos.dignity in ["debilitated"]:
                affliction_score += 20
                reasons.append(f"भावेश ({h_lord}) का नीच राशि में होना")
            elif lord_pos.dignity in ["exalted", "own", "moolatrikona"]:
                affliction_score -= 15
                reasons.append(f"भावेश ({h_lord}) का स्व/उच्च राशि में बलवान होना")

            # Aspect checks from Saturn / Mars
            sat_house = planets["Saturn"].house_from_lagna
            mars_house = planets["Mars"].house_from_lagna
            # Saturn aspects 3rd, 7th, 10th
            sat_aspects = [(sat_house + 2) % 12 + 1, (sat_house + 6) % 12 + 1, (sat_house + 9) % 12 + 1]
            if h_num in sat_aspects:
                affliction_score += 12
                reasons.append("शनि की विशेष दृष्टि")
            # Mars aspects 4th, 7th, 8th
            mars_aspects = [(mars_house + 3) % 12 + 1, (mars_house + 6) % 12 + 1, (mars_house + 7) % 12 + 1]
            if h_num in mars_aspects:
                affliction_score += 12
                reasons.append("मंगल की विशेष दृष्टि")

            affliction_score = min(98, max(8, affliction_score))

            if affliction_score >= 60:
                status_badge = "🔴 पीड़ित / विशेष ध्यान योग्य (High Alert)"
                status_color = "#DC2626"
                high_risk_organs.append(item["organ_hi"])
            elif affliction_score >= 35:
                status_badge = "🟡 सामान्य संवेदनशील (Moderate Sensitivity)"
                status_color = "#D97706"
            else:
                status_badge = "🟢 बलिष्ठ एवं स्वस्थ (Robust & Healthy)"
                status_color = "#16A34A"

            organ_results.append({
                "house": h_num,
                "zone_key": item["zone_key"],
                "organ_hi": item["organ_hi"],
                "organ_en": item["organ_en"],
                "organs": item["organ_hi"],
                "organ": item["organ_hi"],
                "affliction_score": affliction_score,
                "status": status_badge,
                "status_badge": status_badge,
                "status_color": status_color,
                "lord": h_lord,
                "occupants": house_occupants,
                "aspects": [r for r in reasons if "दृष्टि" in r],
                "potential_issues": item["potential_issues"],
                "issues": item["potential_issues"],
                "reasons": reasons if reasons else ["कोई प्रतिकूल योग नहीं, सामान्य संरक्षण।"]
            })

        # -------------------------------------------------------------
        # 2. Ayurvedic Tridosha Calculation (Vata / Pitta / Kapha)
        # -------------------------------------------------------------
        # Elements by sign:
        # Fire (Pitta): Aries(1), Leo(5), Sag(9)
        # Earth (Kapha): Taurus(2), Virgo(6), Cap(10)
        # Air (Vata): Gemini(3), Libra(7), Aqu(11)
        # Water (Kapha): Cancer(4), Scorpio(8), Pisces(12)
        vata_pts = 0
        pitta_pts = 0
        kapha_pts = 0

        # Planetary dosha assignments (Sushruta & Parashara)
        dosha_by_planet = {
            "Sun": "pitta",
            "Moon": "kapha",
            "Mars": "pitta",
            "Mercury": "vata",
            "Jupiter": "kapha",
            "Venus": "kapha",
            "Saturn": "vata",
            "Rahu": "vata",
            "Ketu": "pitta"
        }

        for p_name, pos in planets.items():
            # Planet natural dosha
            p_dosha = dosha_by_planet.get(p_name, "vata")
            if p_dosha == "vata":
                vata_pts += 12
            elif p_dosha == "pitta":
                pitta_pts += 12
            else:
                kapha_pts += 12

            # Sign element
            s_id = pos.sign_id
            if s_id in [1, 5, 9]:
                pitta_pts += 10
            elif s_id in [3, 7, 11]:
                vata_pts += 10
            elif s_id in [2, 6, 10]:
                kapha_pts += 8
                vata_pts += 2
            elif s_id in [4, 8, 12]:
                kapha_pts += 10

        tot_dosha = vata_pts + pitta_pts + kapha_pts
        vata_pct = round((vata_pts / tot_dosha) * 100)
        pitta_pct = round((pitta_pts / tot_dosha) * 100)
        kapha_pct = 100 - vata_pct - pitta_pct

        # Determine dominant constitution
        sorted_doshas = sorted([("वात (Vata)", vata_pct), ("पित्त (Pitta)", pitta_pct), ("कफ (Kapha)", kapha_pct)], key=lambda x: x[1], reverse=True)
        dominant_dosha = f"{sorted_doshas[0][0]} प्रधान ({sorted_doshas[0][1]}%) + {sorted_doshas[1][0]} ({sorted_doshas[1][1]}%)"

        # Ayurvedic Guidelines
        herbal_remedies = []
        if sorted_doshas[0][0].startswith("वात"):
            herbal_remedies.append("🌿 **वात संतुलन:** अश्वगंधा, बला, तिल का तेल मालिश (अभ्यंग), गर्म एवं स्निग्ध आहार, रात्रि में गर्म दूध व जायफल।")
        elif sorted_doshas[0][0].startswith("पित्त"):
            herbal_remedies.append("🌿 **पित्त संतुलन:** गिलोय (अमृता), आंवला, शतावरी, चंदन लेप, शीतल पेय, गुलाब जल, तीखे व खट्टे पदार्थों का त्याग।")
        else:
            herbal_remedies.append("🌿 **कफ संतुलन:** त्रिकटु (सोंठ, पिप्पली, कालीमिर्च), त्रिफला, तुलसी क्वाथ, शहद, हल्का व सुपाच्य भोजन, नित्य प्राणायाम।")

        # Classical Panchakarma Recommendations based on Dominant Dosha
        panchakarma = []
        if sorted_doshas[0][0].startswith("वात"):
            panchakarma = [
                "बस्ति कर्म (Basti Karma - Medicated Enema) — वात का परम उपचार",
                "स्नेहन एवं स्वेदन (Snehana & Swedana - Warm Herbal Oil Massage & Steam)",
                "शिरोधारा (Shirodhara) — मानसिक शांति एवं तंत्रिका तंत्र का विश्राम"
            ]
        elif sorted_doshas[0][0].startswith("पित्त"):
            panchakarma = [
                "विरेचन कर्म (Virechana Karma - Therapeutic Purgation) — पित्त एवं रक्त शोधन",
                "तिक्त घृत पान (Medicated Bitter Ghee) — पित्त व यकृत विषहरण",
                "शीतल क्षीरधारा / तक्रधारा — शरीर एवं मस्तिष्क का शीतलीकरण"
            ]
        else:
            panchakarma = [
                "वमन कर्म (Vamana Karma - Therapeutic Emesis) — कफ एवं आमाशय शोधन",
                "नस्य कर्म (Nasya Karma) — ऊर्ध्व जत्रुगत (कंठ, सिर व श्वास) शुद्धि",
                "उद्वर्तन (Udvartana - Herbal Powder Scrub) — मेद व कफ निवारण"
            ]

        # Determine suitable Rudrakshas
        rudraksha_remedies = cls.get_rudraksha_recommendations(chart, high_risk_organs)

        return {
            "organ_zones": organ_results,
            "high_risk_organs": high_risk_organs,
            "tridosha": {
                "vata_pct": vata_pct,
                "vata_percent": vata_pct,
                "pitta_pct": pitta_pct,
                "pitta_percent": pitta_pct,
                "kapha_pct": kapha_pct,
                "kapha_percent": kapha_pct,
                "dominant": dominant_dosha,
                "dominant_dosha": dominant_dosha,
                "recommendation": herbal_remedies[0] if herbal_remedies else "सात्विक आहार व नियमित दिनचर्या रखें।"
            },
            "ayurvedic_remedies": herbal_remedies,
            "panchakarma": panchakarma,
            "vitality_score": max(25, 100 - (len(high_risk_organs) * 15)),
            "rudraksha_therapy": rudraksha_remedies
        }

    # -------------------------------------------------------------
    # 3. Classical Rudraksha Health & Anatomical Therapy Mapping
    # -------------------------------------------------------------
    RUDRAKSHA_HEALTH_MAPPING = {
        1: {
            "name": "१ मुखी रुद्राक्ष (Ek Mukhi)",
            "lord": "Sun (सूर्य)",
            "deity": "शिव / सूर्य",
            "organs": "हृदय, मस्तिष्क, रीढ़ की हड्डी, दांया नेत्र",
            "dosha": "पित्त संतुलन (Pitta)",
            "clinical_benefits": "उच्च रक्तचाप (Hypertension), माइग्रेन, नेत्र रोग, हृदय दुर्बलता एवं मानसिक तनाव में रामबाण। आत्मबल व ओज की वृद्धि।",
            "wearing_rule": "लाल डोरे अथवा स्वर्ण में गले में धारण करें, 'ॐ ह्रीं नमः' का जप।"
        },
        2: {
            "name": "२ मुखी रुद्राक्ष (Do Mukhi)",
            "lord": "Moon (चन्द्र)",
            "deity": "अर्घनारीश्वर / गौरी-शंकर",
            "organs": "बांया नेत्र, मस्तिष्क, फेफड़े, गुर्दे, शारीरिक तरल (Lymph)",
            "dosha": "कफ-वात संतुलन (Kapha-Vata)",
            "clinical_benefits": "मानसिक अवसाद (Depression), अनिद्रा, भय, हिस्टीरिया, हार्मोन्स असंतुलन, खांसी-जुकाम एवं गुर्दे के विकारों में शांति।",
            "wearing_rule": "सफेद धागे या चांदी में सोमवार को 'ॐ नमः' जप कर धारण करें।"
        },
        3: {
            "name": "३ मुखी रुद्राक्ष (Teen Mukhi)",
            "lord": "Mars (मंगल)",
            "deity": "अग्नि देव",
            "organs": "आमाशय, यकृत, पित्ताशय, रक्त मज्जा, मांसपेशियां",
            "dosha": "पित्त संतुलन (Digestive Agni)",
            "clinical_benefits": "जठराग्नि मंदता (Indigestion), लिवर विकार, पीलिया, रक्तल्पता (Anemia), संक्रामक बुखार एवं त्वचा छालों में अत्यंत प्रभावी।",
            "wearing_rule": "लाल धागे में मंगलवार को 'ॐ क्लीं नमः' का जप कर धारण करें।"
        },
        4: {
            "name": "४ मुखी रुद्राक्ष (Char Mukhi)",
            "lord": "Mercury (बुध)",
            "deity": "ब्रह्मा / सरस्वती",
            "organs": "थायरॉयड, कंठ, स्वरतंतु, श्वसन नली, तंत्रिका तंत्र",
            "dosha": "वात संतुलन (Vata)",
            "clinical_benefits": "हकलाना, स्मृति दुर्बलता, श्वास नली की सूजन, थायरॉयड विकार, पक्षाघात (Paralysis) एवं न्यूरोपैथी में चमत्कारिक लाभ।",
            "wearing_rule": "हरे धागे अथवा पीले डोरे में बुधवार को 'ॐ ह्रीं नमः' जप कर पहनें।"
        },
        5: {
            "name": "५ मुखी रुद्राक्ष (Panch Mukhi)",
            "lord": "Jupiter (बृहस्पति)",
            "deity": "कालाग्नि रुद्र",
            "organs": "हृदय, कान, यकृत, अग्न्याशय (Pancreas), मोटापा",
            "dosha": "कफ-वात सामंजस्य",
            "clinical_benefits": "रक्तचाप नियंत्रण (BP Normalizer), मधुमेह (Diabetes), मोटापा, कोलेस्ट्रॉल, कर्ण रोग एवं दीर्घायु आरोग्य रक्षा।",
            "wearing_rule": "पीले डोरे या पंचधातु में नित्य धारण योग्य, 'ॐ ह्रीं नमः' जप।"
        },
        6: {
            "name": "६ मुखी रुद्राक्ष (Chheh Mukhi)",
            "lord": "Venus (शुक्र)",
            "deity": "भगवान कार्तिकेय",
            "organs": "जननेंद्रियां, गर्भाशय, मूत्र मार्ग, कंठ, त्वचा",
            "dosha": "कफ संतुलन",
            "clinical_benefits": "हार्मोनल असंतुलन, बांझपन, पथरी, मूत्राशय संक्रमण, मधुमेह जनित दुर्बलता एवं पौरुष शक्ति वृद्धि।",
            "wearing_rule": "सफेद या लाल डोरे में शुक्रवार को 'ॐ ह्रीं हुं नमः' जप कर पहनें।"
        },
        7: {
            "name": "७ मुखी रुद्राक्ष (Saat Mukhi)",
            "lord": "Saturn (शनि)",
            "deity": "महालक्ष्मी / सप्तर्षि",
            "organs": "अस्थियां, घुटने, जोड़, रीढ़ का निचला भाग, स्नायु",
            "dosha": "वात दोष शामक",
            "clinical_benefits": "गठिया (Arthritis), साइटिका, कमर व जोड़ों का पुराना दर्द, स्पांडिलाइटिस, पक्षाघात एवं दीर्घकालिक असाध्य व्याधियां।",
            "wearing_rule": "काले या नीले डोरे में शनिवार को 'ॐ हुं नमः' जप कर धारण करें।"
        },
        8: {
            "name": "८ मुखी रुद्राक्ष (Aath Mukhi)",
            "lord": "Rahu (राहु)",
            "deity": "श्री गणेश / अष्ट वसु",
            "organs": "प्रोस्टेट, मलाशय, श्वास तंत्र, त्वचा एलर्जी",
            "dosha": "वात-कफ विकार",
            "clinical_benefits": "असाध्य त्वचा रोग, गुप्त व्याधियां, हाइड्रोसील, मानसिक भ्रम, अकस्मात आघात एवं शल्य क्रिया (Surgery) से सुरक्षा।",
            "wearing_rule": "काले डोरे में बुधवार या शनिवार को 'ॐ हुं नमः' जप कर पहनें।"
        },
        9: {
            "name": "९ मुखी रुद्राक्ष (Nau Mukhi)",
            "lord": "Ketu (केतु)",
            "deity": "माँ नवदुर्गा",
            "organs": "मस्तिष्क, तंत्रिका तंत्र, त्वचा, प्रतिरोधी क्षमता",
            "dosha": "त्रिदोष शामक",
            "clinical_benefits": "अज्ञात भय, मिर्गी, चक्कर आना (Vertigo), अनिद्रा, कुष्ठ व फोड़े-फुंसी, संक्रामक रोगों से संपूर्ण रोग-प्रतिरोधक सुरक्षा।",
            "wearing_rule": "लाल डोरे में मंगलवार को 'ॐ ह्रीं हुं नमः' जप कर धारण करें।"
        },
        10: {
            "name": "१० मुखी रुद्राक्ष (Dus Mukhi)",
            "lord": "All Planets (नवग्रह शामक)",
            "deity": "भगवान विष्णु (दशावतार)",
            "organs": "समग्र देह, अंतःस्रावी ग्रंथियां, अनिद्रा",
            "dosha": "त्रिदोष नाशक",
            "clinical_benefits": "वात रोग, गंभीर अनिद्रा, पैनिक अटैक, अस्थमा, मानसिक व्याकुलता व तांत्रिक-नकारात्मक ऊर्जा का तत्काल शमन।",
            "wearing_rule": "पीले धागे में गुरुवार को 'ॐ ह्रीं नमः' जप कर पहनें।"
        },
        11: {
            "name": "११ मुखी रुद्राक्ष (Gyarah Mukhi)",
            "lord": "Indra / Mars (एकादश रुद्र)",
            "deity": "श्री हनुमान जी",
            "organs": "फेफड़े, श्वसन तंत्र, नसों का जाल, थायरॉयड",
            "dosha": "वात-कफ नाशक",
            "clinical_benefits": "दमा (Asthma), ब्रोंकाइटिस, फेफड़ों की कमजोरी, नसों का सिकुड़ना, शरीर में ऊर्जा व प्राण-शक्ति की अद्भुत वृद्धि।",
            "wearing_rule": "लाल डोरे में मंगलवार को 'ॐ श्रीं नमः' जप कर धारण करें।"
        },
        12: {
            "name": "१२ मुखी रुद्राक्ष (Barah Mukhi)",
            "lord": "Sun (द्वादश आदित्य)",
            "deity": "सूर्य नारायण",
            "organs": "हृदय, रक्त, आंखें, आंतें, अस्थि मज्जा",
            "dosha": "अग्नि-पित्त नियामक",
            "clinical_benefits": "हृदय रोग (Cardiovascular), हड्डियों का क्षरण, रिकेट्स, पेट के अल्सर, कम दृष्टि एवं सामान्य दुर्बलता का संपूर्ण निवारक।",
            "wearing_rule": "लाल डोरे या तांबे में रविवार को 'ॐ क्रौं क्षौं ग्लौं नमः' जप कर पहनें।"
        },
        14: {
            "name": "१४ मुखी रुद्राक्ष (Chaudah Mukhi - देवमणि)",
            "lord": "Saturn / Mars (शिव-हनुमान)",
            "deity": "महाकाल रुद्र",
            "organs": "आज्ञा चक्र, तंत्रिका तंत्र, मेरुदंड, हृदय",
            "dosha": "समस्त वात-पित्त-कफ संतुलन",
            "clinical_benefits": "लकवा, मिर्गी, असाध्य रीढ़ के रोग, अचानक दुर्घटना से पूर्ण जीवन रक्षा, परा-ऊर्जा विकार एवं चिरकालिक व्याधियों का शमन।",
            "wearing_rule": "सोमवार या मंगलवार को माथे या छाती पर 'ॐ नमः' जप कर धारण करें।"
        }
    }

    @classmethod
    def get_rudraksha_recommendations(cls, chart: KundaliChart, high_risk_organs: List[str]) -> List[Dict[str, Any]]:
        """Selects optimal therapeutic Rudrakshas based on chart's 6th/8th house lords

        and afflicted organ zones.
        """
        lagna_sign_id = chart.lagna_sign_id
        l6_sign_id = ((lagna_sign_id - 1 + 5) % 12) + 1
        l6_lord = SIGN_LORDS[SIGN_NAMES[l6_sign_id - 1]]
        l8_sign_id = ((lagna_sign_id - 1 + 7) % 12) + 1
        l8_lord = SIGN_LORDS[SIGN_NAMES[l8_sign_id - 1]]

        # Map lord to Mukhi
        lord_to_mukhi = {
            "Sun": 1, "Moon": 2, "Mars": 3, "Mercury": 4,
            "Jupiter": 5, "Venus": 6, "Saturn": 7, "Rahu": 8, "Ketu": 9
        }

        recommended_mukhis = [5]  # 5-Mukhi is universally protective in Ayurveda
        if l6_lord in lord_to_mukhi and lord_to_mukhi[l6_lord] not in recommended_mukhis:
            recommended_mukhis.append(lord_to_mukhi[l6_lord])
        if l8_lord in lord_to_mukhi and lord_to_mukhi[l8_lord] not in recommended_mukhis:
            recommended_mukhis.append(lord_to_mukhi[l8_lord])

        # If bone / nerve risk, add 7-Mukhi
        if any("अस्थि" in org or "घुटने" in org or "जोड़" in org for org in high_risk_organs):
            if 7 not in recommended_mukhis:
                recommended_mukhis.append(7)
        # If heart / brain risk, add 1-Mukhi or 12-Mukhi
        if any("हृदय" in org or "सिर" in org or "मस्तिष्क" in org for org in high_risk_organs):
            if 1 not in recommended_mukhis:
                recommended_mukhis.append(1)

        result = []
        for m in recommended_mukhis[:4]:
            if m in cls.RUDRAKSHA_HEALTH_MAPPING:
                info = cls.RUDRAKSHA_HEALTH_MAPPING[m]
                result.append({
                    "mukhi": m,
                    "title": info["name"],
                    "lord": info["lord"],
                    "deity": info["deity"],
                    "organs": info["organs"],
                    "dosha": info["dosha"],
                    "benefits": info["clinical_benefits"],
                    "rule": info["wearing_rule"]
                })
        return result

    # -------------------------------------------------------------
    # 4. Disease Susceptibility Timing Forecast
    # -------------------------------------------------------------
    @classmethod
    def forecast_disease_susceptibility_periods(cls, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Forecasts classical disease susceptibility periods based on 6th lord (Rogesh),

        8th lord (Randhresh), 12th lord (Vyayesh), Marakas (2nd/7th lords),
        Badhaka lord, and malefic transit/dasha activations.
        """
        lagna_s_id = chart.lagna_sign_id
        lagna_name = SIGN_NAMES[lagna_s_id - 1]

        def get_lord(h: int) -> str:
            s_id = ((lagna_s_id - 1 + (h - 1)) % 12) + 1
            return SIGN_LORDS[SIGN_NAMES[s_id - 1]]

        l2 = get_lord(2)
        l6 = get_lord(6)
        l7 = get_lord(7)
        l8 = get_lord(8)
        l12 = get_lord(12)

        # Badhaka sign: For Movable (1,4,7,10) -> 11th; Fixed (2,5,8,11) -> 9th; Dual (3,6,9,12) -> 7th
        if lagna_s_id in (1, 4, 7, 10):
            badhaka_h = 11
        elif lagna_s_id in (2, 5, 8, 11):
            badhaka_h = 9
        else:
            badhaka_h = 7
        badhaka_lord = get_lord(badhaka_h)

        planets = chart.planets

        forecasts = []

        # 1. Rogesh (6th lord) Period
        l6_pos = planets.get(l6)
        l6_house = l6_pos.house_from_lagna if l6_pos else 6
        forecasts.append({
            "trigger_planet": l6,
            "period_type": f"षष्ठेश ({l6}) की महादशा / अंतर्दशा काल",
            "shastriya_role": "रोग नियामक (Rogesh) — तीव्र व्याधि उत्पत्ति काल",
            "vulnerability_level": "🔴 उच्च संवेदनशीलता (High Vulnerability)",
            "level_badge": "high",
            "vulnerable_organs": "आंतें, पाचन संस्थान, उदर एवं रोग-प्रतिरोधक क्षमता (Immunity)",
            "ayurvedic_dosha": "पित्त-वात असंतुलन",
            "clinical_warning": f"इस अवधि में {l6} के रोग कारकत्व सक्रिय होते हैं। पाचन विकार, संक्रामक ज्वर अथवा आकस्मिक रोग उभर सकते हैं।",
            "preventive_protocol": f"{l6} ग्रह के बीज मंत्र का नित्य जप, सात्विक सुपाच्य आहार एवं महामृत्युंजय पाठ।"
        })

        # 2. Randhresh (8th lord) Period
        l8_pos = planets.get(l8)
        forecasts.append({
            "trigger_planet": l8,
            "period_type": f"अष्टमेश ({l8}) की अंतर्दशा / प्रत्यंतर काल",
            "shastriya_role": "रन्ध्रेश (Randhresh) — जीर्ण व्याधि, शल्यक्रिया (Surgery) व विषाक्तता",
            "vulnerability_level": "🔴 विशेष सावधानी (Critical Alert)",
            "level_badge": "critical",
            "vulnerable_organs": "गुदा, जननांग, अस्थि मज्जा, मूत्राशय एवं मलाशय",
            "ayurvedic_dosha": "वात-कफ जीर्ण प्रकोप",
            "clinical_warning": "जीर्ण (Chronic) रोगों का उभार, रक्त विकार, गुप्त अंग विकार अथवा शल्यक्रिया (ऑपरेशन) की संभावना।",
            "preventive_protocol": "रुद्राभिषेक, रक्तदान, पीपल में जल तथा नियमित चिकित्सा परीक्षण।"
        })

        # 3. Vyayesh (12th lord) Period
        forecasts.append({
            "trigger_planet": l12,
            "period_type": f"द्वादशेश ({l12}) की अंतर्दशा काल",
            "shastriya_role": "व्ययेश (Vyayesh) — चिकित्सा व्यय, अनिद्रा व अस्पताल प्रवास (Hospitalization)",
            "vulnerability_level": "🟡 मध्यम संवेदनशीलता (Moderate Caution)",
            "level_badge": "moderate",
            "vulnerable_organs": "पैर के तलवे, बांया नेत्र, लिम्फैटिक तंत्र एवं स्नायु",
            "ayurvedic_dosha": "वात दोष व मानसिक तनाव",
            "clinical_warning": "अनिद्रा, अत्यधिक थकावट, पैरों में दर्द, नेत्र विकार एवं अनावश्यक दवाओं का अधिक व्यय।",
            "preventive_protocol": "पाद-अभ्यंग (पैरों की तेल मालिश), ध्यान, जल का समुचित सेवन व अस्पताल/वृद्धाश्रम में सेवा।"
        })

        # 4. Maraka Activation (2nd & 7th lords)
        forecasts.append({
            "trigger_planet": f"{l2} / {l7}",
            "period_type": f"मारक ग्रह ({l2} व {l7}) की संयुक्त दशा",
            "shastriya_role": "द्वितीयाधिपति व सप्तमाधिपति (Maraka Lords) — जीवनी शक्ति क्षय",
            "vulnerability_level": "🟡 सतर्कता आवश्यक (Caution Required)",
            "level_badge": "moderate",
            "vulnerable_organs": "मुख, कंठ, कमर, गुर्दे एवं पेल्विक क्षेत्र",
            "ayurvedic_dosha": "त्रिदोष क्षोभ",
            "clinical_warning": "शरीर में प्राण-शक्ति (Vitality) में कमी, मौसमी संक्रमण एवं शारीरिक थकावट।",
            "preventive_protocol": "विष्णु सहस्रनाम पाठ, एकादशी व्रत एवं सात्विक जीवनचर्या।"
        })

        # 5. Shani Sade-Sati & Rahu Transit
        forecasts.append({
            "trigger_planet": "Saturn / Rahu",
            "period_type": "शनि साढ़ेसाती, ढैया अथवा राहु का ६/८/१२वें भाव से गोचर",
            "shastriya_role": "कालपुरुष क्रूर गोचर वेध — दीर्घकालिक संवेदनशीलता",
            "vulnerability_level": "🔴 उच्च सतर्कता (High Caution)",
            "level_badge": "high",
            "vulnerable_organs": "जोड़, घुटने, स्नायु, त्वचा, एलर्जी एवं मानसिक अवसाद",
            "ayurvedic_dosha": "प्रबल वात प्रकोप",
            "clinical_warning": "वात विकार, जोड़ों का दर्द, अज्ञात भय, एलर्जी एवं गलत औषधि सेवन से बचने की विशेष आवश्यकता।",
            "preventive_protocol": "शनिवार को तिल के तेल का दान, ७-मुखी रुद्राक्ष धारण व नित्य प्राणायाम।"
        })

        return forecasts


default_medical_service = MedicalAstrologyService()

