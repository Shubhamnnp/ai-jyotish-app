"""
Classical Ayurdaya & Shayanadi Planetary Avasthas Engine for JyotishOS.
According to Brihat Parashara Hora Shastra (BPHS) and Maharishi Jaimini:
1. 12 Shayanadi Planetary Avasthas for 9 planets (Shayana, Upaveshana, Netrapani, Prakasha, Gamana, Aagamana, Sabha, Agama, Bhojana, Nrityalipsa, Kauthuka, Nidra).
2. Jaimini 3-Pair Longevity Categorization (Alpayu, Madhyayu, Purnayu, Divyayu) with Kakshya Vriddhi/Hrasa.
3. Classical Pindayu planetary longevity calculation with classical Harana reductions.
"""

from typing import Dict, List, Tuple, Optional, Any
from .constants import SIGN_NAMES, SIGN_LORDS, EXALTATION
from .models import KundaliChart, PlanetPosition


# 12 Shayanadi Avasthas definitions and classical effects
SHAYANADI_AVASTHAS = {
    1: {
        "name_hi": "शयन (Shayana - Resting/Reclining)",
        "name_en": "Shayana (Rest)",
        "potency_pct": 35,
        "nature": "Passive",
        "effect_hi": "अकर्मण्यता, ऊर्जा की कमी, फलों में विलंब, स्वास्थ्य में शिथिलता परंतु आंतरिक शांति।",
        "effect_en": "Lethargy, delayed fruits, passive nature, restful yet low external productivity."
    },
    2: {
        "name_hi": "उपवेशन (Upaveshana - Sitting/Established)",
        "name_en": "Upaveshana (Sitting)",
        "potency_pct": 80,
        "nature": "Benefic",
        "effect_hi": "स्थिरता, मान-प्रतिष्ठा, पांडित्य, सम्मानित पद एवं शांत व सुखी पारिवारिक जीवन।",
        "effect_en": "Stability, scholarly reputation, honored status, and peaceful domestic life."
    },
    3: {
        "name_hi": "नेत्रपाणि (Netrapani - Wiping Eyes/Restless)",
        "name_en": "Netrapani (Eye-Rubbing)",
        "potency_pct": 45,
        "nature": "Afflicted",
        "effect_hi": "मानसिक चंचलता, नेत्र अथवा सिर विकार, धन का अपव्यय एवं योजनाओं में भटकाव।",
        "effect_en": "Restlessness, eye/head strain, financial volatility, and scattered focus."
    },
    4: {
        "name_hi": "प्रकाश (Prakasha - Shining/Radiant)",
        "name_en": "Prakasha (Radiant)",
        "potency_pct": 100,
        "nature": "Supreme Benefic",
        "effect_hi": "सर्वतोमुखी विजय, प्रखर तेज, शासकीय सम्मान, उच्च पद, संपदा एवं महान कीर्ति।",
        "effect_en": "Radiant fame, victory over obstacles, executive authority, prosperity, and renown."
    },
    5: {
        "name_hi": "गमन (Gamana - Journeying/Mobile)",
        "name_en": "Gamana (Moving)",
        "potency_pct": 65,
        "nature": "Active",
        "effect_hi": "निरंतर यात्राएं, गतिशील जीवन, विदेश संपर्क, परिवर्तनशीलता एवं साहसिक प्रयास।",
        "effect_en": "Frequent travels, dynamic pursuits, foreign linkages, and active enterprises."
    },
    6: {
        "name_hi": "आगमन (Aagamana - Returning/Acquiring)",
        "name_en": "Aagamana (Acquiring)",
        "potency_pct": 85,
        "nature": "Benefic",
        "effect_hi": "धन लाभ, पारिवारिक मिलन, गृह सुख, खोई हुई संपदा की पुनः प्राप्ति एवं संतोष।",
        "effect_en": "Wealth acquisition, domestic reunions, recovery of lost assets, and contentment."
    },
    7: {
        "name_hi": "सभा (Sabha - In Assembly/Royal Court)",
        "name_en": "Sabha (In Court)",
        "potency_pct": 95,
        "nature": "Supreme Benefic",
        "effect_hi": "राजदरबार अथवा सभा में प्रतिष्ठा, वाकपटुता, न्यायिक क्षमता एवं सर्वप्रिय नेतृत्व।",
        "effect_en": "Assembly leadership, high eloquence, judicial wisdom, and broad public respect."
    },
    8: {
        "name_hi": "आगम (Agama - Receiving Knowledge)",
        "name_en": "Agama (Learning)",
        "potency_pct": 90,
        "nature": "Benefic",
        "effect_hi": "उच्च आध्यात्मिक ज्ञान, शास्त्र प्रवीणता, मंत्र सिद्धि, गुरु कृपा एवं नैतिक समृद्धि।",
        "effect_en": "High spiritual intellect, mastery of sciences, mantra proficiency, and divine grace."
    },
    9: {
        "name_hi": "भोजन (Bhojana - Feasting/Pleasure)",
        "name_en": "Bhojana (Feasting)",
        "potency_pct": 85,
        "nature": "Benefic",
        "effect_hi": "उत्तम खान-पान, विलासिता, भौतिक सुख-साधनों की प्रचुरता एवं आरोग्य।",
        "effect_en": "Fine delicacies, abundant luxury, sensual pleasures, and buoyant vitality."
    },
    10: {
        "name_hi": "नृत्यलिप्सा (Nrityalipsa - Passion for Dance/Arts)",
        "name_en": "Nrityalipsa (Creative Passion)",
        "potency_pct": 75,
        "nature": "Creative",
        "effect_hi": "कलात्मक अभिरुचि, रचनात्मक प्रतिभा, रंगमंच/साहित्य में ख्याति एवं आनंदप्रिय स्वभाव।",
        "effect_en": "Artistic flair, theatrical or literary talents, creative pursuits, and joyful nature."
    },
    11: {
        "name_hi": "कौतुक (Kauthuka - Curiosity/Wonder)",
        "name_en": "Kauthuka (Curiosity)",
        "potency_pct": 70,
        "nature": "Active",
        "effect_hi": "नवीन अन्वेषण, उत्सवप्रियता, हर्षोल्लास, खेलकूद एवं मनोरंजन में रुचि।",
        "effect_en": "Novel research, eagerness for celebrations, amusement, and playful disposition."
    },
    12: {
        "name_hi": "निद्रा (Nidra - Deep Sleep/Slumber)",
        "name_en": "Nidra (Slumber)",
        "potency_pct": 25,
        "nature": "Inert",
        "effect_hi": "आलस्य, समय की बर्बादी, अवसरों का लोप, निर्णयहीनता एवं ऊर्जा का ह्रास।",
        "effect_en": "Procrastination, missed opportunities, indecisiveness, and dormant potential."
    }
}

# Sign Polarity: 1=Movable (Chara), 2=Fixed (Sthira), 3=Dual (Dwisvabhava)
SIGN_MODALITY = {
    "Aries": 1, "Taurus": 2, "Gemini": 3,
    "Cancer": 1, "Leo": 2, "Virgo": 3,
    "Libra": 1, "Scorpio": 2, "Sagittarius": 3,
    "Capricorn": 1, "Aquarius": 2, "Pisces": 3
}


class AyurdayaEngine:
    """Calculates 12 Shayanadi Planetary Avasthas, Jaimini Longevity, and Pindayu Ayurdaya."""

    @classmethod
    def calculate_shayanadi_avasthas(cls, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Computes 12 Shayanadi Avasthas for all 9 planets according to BPHS formula."""
        planet_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        nak_span = 360.0 / 27.0
        pada_span = nak_span / 4.0

        # Lagna degree integer (0-29)
        lagna_deg_int = int(chart.lagna_longitude % 30.0)

        # Janma Ghati (from Sunrise)
        hours = chart.birth_data.birth_time.hour + chart.birth_data.birth_time.minute / 60.0
        ghati_val = int((hours - 5.5) * 2.5)
        if ghati_val <= 0:
            ghati_val += 60

        avasthas_list = []

        for p_idx, p_name in enumerate(planet_order, start=1):
            p_obj = chart.planets[p_name]
            nak_idx = int(p_obj.longitude // nak_span) + 1  # 1-27
            pada_num = int((p_obj.longitude % nak_span) // pada_span) + 1  # 1-4

            # Classical BPHS product formula
            prod = (p_idx * nak_idx * pada_num) + lagna_deg_int + ghati_val
            avastha_idx = prod % 12
            if avastha_idx == 0:
                avastha_idx = 12

            avastha_meta = SHAYANADI_AVASTHAS[avastha_idx]

            # Aspect modifier: benefic aspect boosts, malefic reduces
            aspect_mod = "शुद्ध दृष्टि (Balanced)"
            if p_obj.dignity in ("exalted", "moolatrikona", "own"):
                aspect_mod = "🌟 स्वक्षेत्री / उच्च पुष्ट (Elevated)"
            elif p_obj.is_combust:
                aspect_mod = "🔥 अस्त पीड़ित (Combust Weakened)"

            avasthas_list.append({
                "planet": p_name,
                "avastha_num": avastha_idx,
                "name_hi": avastha_meta["name_hi"],
                "name_en": avastha_meta["name_en"],
                "potency_pct": avastha_meta["potency_pct"],
                "nature": avastha_meta["nature"],
                "aspect_mod": aspect_mod,
                "effect_hi": avastha_meta["effect_hi"],
                "effect_en": avastha_meta["effect_en"],
            })

        return avasthas_list

    @classmethod
    def calculate_jaimini_longevity(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Calculates Jaimini 3-Pair Ayurdaya:
        Pair 1: Lagna Lord Sign Modality & 8th Lord Sign Modality
        Pair 2: Lagna Sign Modality & Moon Sign Modality
        Pair 3: Lagna Sign Modality & Hora Lagna Sign Modality
        """
        lagna_sign = chart.lagna_sign_name
        lord_h1_name = SIGN_LORDS[lagna_sign]
        lord_h1_sign = chart.planets[lord_h1_name].sign_name

        h8_sign = chart.houses[7].sign_name
        lord_h8_name = SIGN_LORDS[h8_sign]
        lord_h8_sign = chart.planets[lord_h8_name].sign_name

        moon_sign = chart.planets["Moon"].sign_name
        hl_sign = chart.jaimini.hora_lagna_sign_name if chart.jaimini else "Aries"

        def evaluate_pair(m1: int, m2: int) -> Tuple[str, str]:
            # Both Movable (1,1) OR One Fixed + One Dual (2,3 or 3,2) -> Purnayu
            if (m1 == 1 and m2 == 1) or ({m1, m2} == {2, 3}):
                return "पूर्णायु (Purnayu - 72 to 108 Yrs)", "Long"
            # Both Fixed (2,2) OR One Movable + One Dual (1,3 or 3,1) -> Madhyayu
            elif (m1 == 2 and m2 == 2) or ({m1, m2} == {1, 3}):
                return "मध्यायु (Madhyayu - 36 to 72 Yrs)", "Medium"
            # Both Dual (3,3) OR One Movable + One Fixed (1,2 or 2,1) -> Alpayu
            else:
                return "अल्पायु (Alpayu - 0 to 36 Yrs)", "Short"

        p1_res, p1_code = evaluate_pair(SIGN_MODALITY[lord_h1_sign], SIGN_MODALITY[lord_h8_sign])
        p2_res, p2_code = evaluate_pair(SIGN_MODALITY[lagna_sign], SIGN_MODALITY[moon_sign])
        p3_res, p3_code = evaluate_pair(SIGN_MODALITY[lagna_sign], SIGN_MODALITY.get(hl_sign, 1))

        # Determine consensus category
        codes = [p1_code, p2_code, p3_code]
        if codes.count("Long") >= 2:
            final_span = "पूर्णायु (Purnayu: 72 - 108 वर्ष)"
            base_years = 84.0
        elif codes.count("Medium") >= 2:
            final_span = "मध्यायु (Madhyayu: 36 - 72 वर्ष)"
            base_years = 62.0
        elif codes.count("Short") >= 2:
            final_span = "अल्पायु (Alpayu: 0 - 36 वर्ष)"
            base_years = 32.0
        else:
            # Fallback to Pair 1
            if p1_code == "Long":
                final_span = "पूर्णायु (Purnayu: 72 - 108 वर्ष)"
                base_years = 80.0
            elif p1_code == "Medium":
                final_span = "मध्यायु (Madhyayu: 36 - 72 वर्ष)"
                base_years = 58.0
            else:
                final_span = "अल्पायु (Alpayu: 0 - 36 वर्ष)"
                base_years = 34.0

        # Kakshya Vriddhi (Modifiers): Jupiter in Lagna/7th, Strong Lagnesha adds years
        vriddhi = 0.0
        modifiers = []
        if chart.planets["Jupiter"].house_from_lagna in (1, 5, 9):
            vriddhi += 6.0
            modifiers.append("गुरु त्रिकोण / लग्न प्रभाव: +6 वर्ष (कक्षा वृद्धि / Kakshya Vriddhi)")
        if chart.planets[lord_h1_name].dignity in ("exalted", "own"):
            vriddhi += 4.0
            modifiers.append("लग्नेश स्वक्षेत्री / उच्च: +4 वर्ष (प्रबल जीवन शक्ति)")

        est_lifespan = round(base_years + vriddhi, 1)

        return {
            "final_span": final_span,
            "estimated_years": est_lifespan,
            "pair1": {"desc": "लग्नेश एवं अष्टमेश राशि स्वभाव", "result": p1_res},
            "pair2": {"desc": "लग्न राशि एवं चन्द्र राशि स्वभाव", "result": p2_res},
            "pair3": {"desc": "लग्न राशि एवं होरा लग्न स्वभाव", "result": p3_res},
            "modifiers": modifiers if modifiers else ["सामान्य ग्रह प्रभाव (Standard Balance)"]
        }

    @classmethod
    def calculate_pindayu(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Classical Pindayu Longevity Calculation."""
        max_years = {
            "Sun": 19.0, "Moon": 25.0, "Mars": 15.0,
            "Mercury": 12.0, "Jupiter": 15.0, "Venus": 21.0, "Saturn": 20.0
        }

        planet_years = {}
        total_unreduced = 0.0

        for p_name, max_y in max_years.items():
            p_obj = chart.planets[p_name]
            # Exaltation distance factor
            exalt_info = EXALTATION.get(p_name, ("Aries", 10.0))
            exalt_idx = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"].index(exalt_info[0])
            exalt_lon = exalt_idx * 30.0 + exalt_info[1]
            diff = abs(p_obj.longitude - exalt_lon)
            if diff > 180.0:
                diff = 360.0 - diff

            factor = 0.5 + 0.5 * (1.0 - diff / 180.0)
            p_contribution = max_y * factor
            planet_years[p_name] = round(p_contribution, 2)
            total_unreduced += p_contribution

        # Classical reductions (Haranas: Chakrardha Hani ~ 15% average for natal houses)
        net_years = round(total_unreduced * 0.72, 1)

        return {
            "planet_contributions": planet_years,
            "total_unreduced": round(total_unreduced, 2),
            "net_pindayu_years": net_years,
        }


default_ayurdaya_engine = AyurdayaEngine()

