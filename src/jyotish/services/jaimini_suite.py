"""
Comprehensive Jaimini Astrological Suite for JyotishOS (Jagannatha Hora Grade).
Computes:
1. Karakamsha Chart (D9 Navamsha & D1 Rashi views with Karakamsha as Lagna).
2. Ishta Devata, Dharma Devata, and Palana Devata according to Jaimini Upadesha Sutras.
3. Swamsha Shastriya Yogas (Moksha, Authorship, State honor, Astrology expertise).
4. 12 Arudha Padas (AL, A2-A11, UL) with house occupants, AL-Janma Lagna alignment, and worldly status synthesis.
"""

from typing import Dict, List, Any, Optional, Tuple
try:
    from ..core.models import KundaliChart
    from ..core.constants import SIGN_NAMES, SIGN_LORDS
    from ..core.jaimini import JaiminiCalculator, ARUDHA_SIGNIFICATIONS
except (ImportError, ValueError):
    from src.jyotish.core.models import KundaliChart
    from src.jyotish.core.constants import SIGN_NAMES, SIGN_LORDS
    from src.jyotish.core.jaimini import JaiminiCalculator, ARUDHA_SIGNIFICATIONS


DEITY_MAP = {
    "Sun": {"deity": "भगवान शिव / सूर्य नारायण", "avatar": "राम", "mantra": "ॐ घृणि सूर्याय नमः"},
    "Moon": {"deity": "माता पार्वती / गौरी", "avatar": "कृष्ण", "mantra": "ॐ सों सोमाय नमः"},
    "Mars": {"deity": "भगवान कार्तिकेय / हनुमान जी", "avatar": "नृसिंह", "mantra": "ॐ अं अंगारकाय नमः"},
    "Mercury": {"deity": "भगवान विष्णु / नारायण", "avatar": "बुद्ध", "mantra": "ॐ बुं बुधाय नमः"},
    "Jupiter": {"deity": "भगवान शिव / साम्ब सदाशिव / दत्तात्रेय", "avatar": "वामन", "mantra": "ॐ बृं बृहस्पतये नमः"},
    "Venus": {"deity": "माता महालक्ष्मी / अन्नपूर्णा", "avatar": "परशुराम", "mantra": "ॐ शुं शुक्राय नमः"},
    "Saturn": {"deity": "भगवान भैरव / कूर्म / यमराज", "avatar": "कूर्म", "mantra": "ॐ शं शनैश्चराय नमः"},
    "Rahu": {"deity": "माता दुर्गा / चण्डी", "avatar": "वराह", "mantra": "ॐ रां राहवे नमः"},
    "Ketu": {"deity": "भगवान गणेश / मत्स्य", "avatar": "मत्स्य", "mantra": "ॐ कें केतवे नमः"},
}


class JaiminiSuiteService:
    """Advanced Jaimini Karakamsha and Arudha Analysis Service."""

    @classmethod
    def analyze_jaimini_suite(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Runs comprehensive Jaimini analysis on chart.
        """
        res = JaiminiCalculator.calculate(chart)
        kl_sign_id = res.karakamsha_sign_id  # 1..12
        kl_sign_name = res.karakamsha_sign_name
        ak_planet = res.karakas_7["AK"]

        # -------------------------------------------------------------
        # 1. Karakamsha Chart in Navamsha (D9)
        # -------------------------------------------------------------
        d9_planets = {}
        for p_name, p_data in chart.planets.items():
            d9_s_id = JaiminiCalculator._get_navamsha_sign(p_data.longitude)
            # House from Karakamsha Lagna
            h_from_kl = ((d9_s_id - kl_sign_id) % 12) + 1
            d9_planets[p_name] = {
                "navamsha_sign_id": d9_s_id,
                "navamsha_sign": SIGN_NAMES[d9_s_id - 1],
                "house_from_karakamsha": h_from_kl,
                "is_ak": (p_name == ak_planet)
            }

        # Group planets by house from Karakamsha
        houses_from_kl = {h: [] for h in range(1, 13)}
        for p_name, p_info in d9_planets.items():
            houses_from_kl[p_info["house_from_karakamsha"]].append(p_name)

        # -------------------------------------------------------------
        # 2. Ishta Devata & Moksha Determination (12th from Karakamsha in D9)
        # -------------------------------------------------------------
        h12_planets = houses_from_kl[12]
        h9_planets = houses_from_kl[9]
        h6_planets = houses_from_kl[6]

        is_moksha_yoga = "Ketu" in h12_planets
        
        # Primary Ishta planet
        if h12_planets:
            ishta_planet = h12_planets[0]
        else:
            # 12th lord from Karakamsha
            s12_id = ((kl_sign_id - 1 + 11) % 12) + 1
            ishta_planet = SIGN_LORDS[SIGN_NAMES[s12_id - 1]]

        ishta_info = DEITY_MAP.get(ishta_planet, DEITY_MAP["Jupiter"])

        # Dharma Devata (9th from Karakamsha)
        dharma_planet = h9_planets[0] if h9_planets else SIGN_LORDS[SIGN_NAMES[((kl_sign_id - 1 + 8) % 12)]]
        dharma_info = DEITY_MAP.get(dharma_planet, DEITY_MAP["Sun"])

        # Palana Devata (6th from Amatyakaraka in D9 - protector in worldly life)
        amk_planet = res.karakas_7.get("AmK", "Sun")
        amk_d9_s = d9_planets.get(amk_planet, {}).get("navamsha_sign_id", 1)
        palana_s_id = ((amk_d9_s - 1 + 5) % 12) + 1
        palana_planet = SIGN_LORDS[SIGN_NAMES[palana_s_id - 1]]
        palana_info = DEITY_MAP.get(palana_planet, DEITY_MAP["Moon"])

        # -------------------------------------------------------------
        # 3. Classical Swamsha Yogas from Jaimini Upadesha Sutras
        # -------------------------------------------------------------
        yogas = []
        if is_moksha_yoga:
            yogas.append({
                "title": "🕊️ कैवल्य / मोक्ष योग (Moksha Yoga)",
                "sutra": "जैमिनी सूत्र १.२.६९: क्रियायाम् केतौ कैवल्यम्",
                "desc": "कारकांश से द्वादश भाव में केतु की स्थिति आध्यात्मिक मुक्ति, वासना-क्षय एवं मोक्ष का शास्त्रीय प्रमाण है।",
                "type": "Auspicious Spiritual"
            })
        
        # 1st / 5th house planets
        if "Sun" in houses_from_kl[1] or "Venus" in houses_from_kl[1]:
            yogas.append({
                "title": "👑 राजयोग / शासन सेवा (Government / Authority)",
                "sutra": "रविशुक्राभ्यां राजकार्यम्",
                "desc": "कारकांश में सूर्य अथवा शुक्र की स्थिति जातक को प्रशासनिक प्रतिष्ठा, सरकारी सम्मान व सामाजिक प्रभुत्व देती है।",
                "type": "Power"
            })

        if "Mercury" in houses_from_kl[1] or "Mercury" in houses_from_kl[5]:
            yogas.append({
                "title": "📚 प्रखर बुद्धि व शिल्पकार योग (Art & Business Intelligence)",
                "sutra": "बुधेन शिल्पी वाणिज्यो वा",
                "desc": "कारकांश या पंचम में बुध होने से जातक प्रखर वक्ता, कुशल व्यापारी, लेखक अथवा निपुण शिल्पकार बनता है।",
                "type": "Intellect"
            })

        if "Jupiter" in houses_from_kl[1] or "Jupiter" in houses_from_kl[5]:
            yogas.append({
                "title": "🕉️ सर्वशास्त्र वेत्ता / ज्योतिषी योग (Vedic Scholar & Astrologer)",
                "sutra": "गुरुणा सर्वविद् धार्मिकश्च",
                "desc": "कारकांश अथवा पंचम में गुरु सर्वशास्त्र ज्ञान, वेदांत, ज्योतिष एवं आध्यात्मिक उपदेशक बनाता है।",
                "type": "Wisdom"
            })

        if "Mars" in houses_from_kl[1] or "Mars" in houses_from_kl[3]:
            yogas.append({
                "title": "⚔️ धातु-अग्नि-शस्त्र पराक्रम योग (Technical / Armed Courage)",
                "sutra": "भौमेन कुविन्दो लोहकारी वा",
                "desc": "कारकांश में मंगल जातक को साहसी, तकनीकी विशेषज्ञ, शल्य चिकित्सक अथवा रक्षा/सुरक्षा क्षेत्र में यश दिलाता है।",
                "type": "Courage"
            })

        if "Moon" in houses_from_kl[1] or "Moon" in houses_from_kl[4]:
            yogas.append({
                "title": "🌊 सुख व काव्य प्रतिभा योग (Creative & Material Comforts)",
                "sutra": "चंद्रेण सौख्यं काव्यादिकम्",
                "desc": "कारकांश अथवा चतुर्थ में चन्द्रमा जातक को संवेदनशील, काव्यात्मक, संगीत प्रेमी एवं सुखी जीवन प्रदान करता है।",
                "type": "Creative"
            })

        # -------------------------------------------------------------
        # 4. Arudha Lagna (AL) vs Janma Lagna Synthesis
        # -------------------------------------------------------------
        jl_sign_id = chart.lagna_sign_id
        al_sign_name = res.arudha_pada_names.get("AL", "Aries")
        al_sign_id = SIGN_NAMES.index(al_sign_name) + 1 if al_sign_name in SIGN_NAMES else 1

        al_dist = ((al_sign_id - jl_sign_id) % 12) + 1
        if al_dist in [1, 4, 7, 10]:
            al_jl_harmony = "🟢 केंद्र संबंध (Auspicious): वास्तविक व्यक्तित्व और सामाजिक छवि में पूर्ण सामंजस्य व उच्च सम्मान।"
        elif al_dist in [5, 9]:
            al_jl_harmony = "🟢 त्रिकोण संबंध (Highly Fortunate): पूर्वपुण्य व भाग्य का सतत सहयोग, धर्मपरायण प्रतिष्ठा।"
        elif al_dist in [6, 8, 12]:
            al_jl_harmony = "🟡 षडाष्टक / द्विर्द्वादश (Complex Image): वास्तविक क्षमता और सामाजिक छवि में अंतर, गुप्त संघर्ष।"
        else:
            al_jl_harmony = "🔵 उपचय संबंध (Growth with Effort): कर्म और परिश्रम द्वारा निरंतर मान-सम्मान में वृद्धि।"

        # -------------------------------------------------------------
        # 5. Upapada Lagna (UL) Marital Harmony Assessment
        # -------------------------------------------------------------
        ul_sign_name = res.arudha_pada_names.get("UL", "Taurus")
        ul_sign_id = SIGN_NAMES.index(ul_sign_name) + 1 if ul_sign_name in SIGN_NAMES else 2
        ul_dist_from_al = ((ul_sign_id - al_sign_id) % 12) + 1

        if ul_dist_from_al in [6, 8, 12]:
            ul_summary = f"⚠️ AL से UL {ul_dist_from_al}वें भाव में है (षडाष्टक/व्यय): वैवाहिक जीवन में धैर्य, समझदारी व उपाय आवश्यक।"
        else:
            ul_summary = f"✅ AL से UL {ul_dist_from_al}वें भाव में अनुकूल है: दांपत्य व सामाजिक प्रतिष्ठा में उत्तम समन्वय।"

        return {
            "result_obj": res,
            "karakas_7": res.karakas_7,
            "atmakaraka": ak_planet,
            "amatyakaraka": amk_planet,
            "karakamsha_sign": kl_sign_name,
            "karakamsha_sign_id": kl_sign_id,
            "d9_planets": d9_planets,
            "houses_from_kl": houses_from_kl,
            "ishta_devata": {
                "planet": ishta_planet,
                "deity": ishta_info["deity"],
                "avatar": ishta_info["avatar"],
                "mantra": ishta_info["mantra"],
                "moksha_yoga": is_moksha_yoga
            },
            "dharma_devata": {
                "planet": dharma_planet,
                "deity": dharma_info["deity"],
                "mantra": dharma_info["mantra"]
            },
            "palana_devata": {
                "planet": palana_planet,
                "deity": palana_info["deity"],
                "mantra": palana_info["mantra"]
            },
            "swamsha_yogas": yogas,
            "arudha_padas": res.arudha_pada_names,
            "arudha_details": res.arudha_details,
            "special_lagnas": res.special_lagnas_detail,
            "al_jl_harmony": al_jl_harmony,
            "ul_summary": ul_summary
        }


# Singleton instance
default_jaimini_suite_service = JaiminiSuiteService()
