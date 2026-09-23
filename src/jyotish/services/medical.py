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
                "affliction_score": affliction_score,
                "status_badge": status_badge,
                "status_color": status_color,
                "potential_issues": item["potential_issues"],
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

        panchakarma = "नस्य एवं शिरोधरा" if "वात" in dominant_dosha else ("विरेचन एवं शीतल लेप" if "पित्त" in dominant_dosha else "वमन एवं उद्वर्तन")

        return {
            "organ_zones": organ_results,
            "high_risk_organs": high_risk_organs,
            "tridosha": {
                "vata_pct": vata_pct,
                "pitta_pct": pitta_pct,
                "kapha_pct": kapha_pct,
                "dominant": dominant_dosha
            },
            "ayurvedic_remedies": herbal_remedies,
            "panchakarma": panchakarma,
            "vitality_score": max(25, 100 - (len(high_risk_organs) * 15))
        }


default_medical_service = MedicalAstrologyService()
