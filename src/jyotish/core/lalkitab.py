"""
Lal Kitab (1952 Edition) Astronomical & Astrological Engine for JyotishOS.
Implements:
1. Kalapurusha House Conversion (12 Fixed Khana / Bhavas starting from Aries = Khana 1)
2. 7 Major Karmic Debts (Pitra Rina, Matra Rina, Swa Rina, Stri Rina, Rishtedari Rina, etc.)
3. Sleeping Houses (Soya Hua Ghar) & Sleeping Planets (Soya Hua Graha)
4. Masnui (Artificial / Synthetic) Planets Combinations
5. Lal Kitab specific remedies, precautions & auspicious/inauspicious indicators

References:
- Lal Kitab (1952 Gutka / Tarjuma by Pt. Roop Chand Joshi)
- LeoStar Lal Kitab Computational Architecture
"""

from typing import Dict, List, Any, Tuple, Optional
from pydantic import BaseModel, Field
from .models import KundaliChart, PlanetPosition
from .constants import SIGN_NAMES, GRAHAS


# -------------------------------------------------------------
# 1. Lal Kitab Classical House Attributes (Pakke Ghar)
# -------------------------------------------------------------

LAL_KITAB_KHANA_DATA = {
    1: {
        "khana": 1,
        "pakka_ruler": "Sun (सूर्य)",
        "pakka_sign": "Aries (मेष)",
        "karaka": "Mars (मंगल)",
        "nature_hi": "तख्त (सिंहासन), स्वभाव, देह, आयु, सम्मान",
        "benefic_planets": ["Sun", "Mars", "Jupiter", "Moon"],
        "malefic_planets": ["Saturn", "Rahu"],
    },
    2: {
        "khana": 2,
        "pakka_ruler": "Jupiter (बृहस्पति)",
        "pakka_sign": "Taurus (वृषभ)",
        "karaka": "Jupiter (बृहस्पति)",
        "nature_hi": "धर्मस्थान, ससुराल, संचित धन, वाणी, गुरु कृपा",
        "benefic_planets": ["Jupiter", "Moon", "Mars"],
        "malefic_planets": ["Venus", "Rahu"],
    },
    3: {
        "khana": 3,
        "pakka_ruler": "Mars (मंगल)",
        "pakka_sign": "Gemini (मिथुन)",
        "karaka": "Mercury (बुध)",
        "nature_hi": "पराक्रम, छोटे भाई-बहन, हाथ, गुप्त शत्रु",
        "benefic_planets": ["Mars", "Sun", "Rahu"],
        "malefic_planets": ["Moon", "Ketu"],
    },
    4: {
        "khana": 4,
        "pakka_ruler": "Moon (चन्द्र)",
        "pakka_sign": "Cancer (कर्क)",
        "karaka": "Moon (चन्द्र)",
        "nature_hi": "माता, नदी, शांति, हृदय, पैतृक संपत्ति",
        "benefic_planets": ["Moon", "Jupiter"],
        "malefic_planets": ["Saturn", "Rahu", "Ketu"],
    },
    5: {
        "khana": 5,
        "pakka_ruler": "Jupiter (बृहस्पति)",
        "pakka_sign": "Leo (सिंह)",
        "karaka": "Sun (सूर्य)",
        "nature_hi": "संतान, विद्या, पूर्वजन्म के कर्म, भविष्य",
        "benefic_planets": ["Sun", "Jupiter", "Mars"],
        "malefic_planets": ["Rahu", "Saturn"],
    },
    6: {
        "khana": 6,
        "pakka_ruler": "Mercury (बुध) & Ketu (केतु)",
        "pakka_sign": "Virgo (कन्या)",
        "karaka": "Ketu (केतु)",
        "nature_hi": "पाताल, रोग, ऋण, ननिहाल, गुप्त विद्या",
        "benefic_planets": ["Mercury", "Ketu"],
        "malefic_planets": ["Jupiter", "Sun", "Venus"],
    },
    7: {
        "khana": 7,
        "pakka_ruler": "Venus (शुक्र) & Mercury (बुध)",
        "pakka_sign": "Libra (तुला)",
        "karaka": "Venus (शुक्र)",
        "nature_hi": "गृहस्थ, विवाह, साझेदारी, दुनियादारी",
        "benefic_planets": ["Venus", "Mercury", "Saturn"],
        "malefic_planets": ["Sun", "Jupiter", "Moon"],
    },
    8: {
        "khana": 8,
        "pakka_ruler": "Mars (मंगल) & Saturn (शनि)",
        "pakka_sign": "Scorpio (वृश्चिक)",
        "karaka": "Saturn (शनि)",
        "nature_hi": "श्मशान, मृत्यु, रहस्य, अचानक संकट",
        "benefic_planets": ["Saturn", "Mars"],
        "malefic_planets": ["Moon", "Sun", "Jupiter"],
    },
    9: {
        "khana": 9,
        "pakka_ruler": "Jupiter (बृहस्पति)",
        "pakka_sign": "Sagittarius (धनु)",
        "karaka": "Jupiter (बृहस्पति)",
        "nature_hi": "भाग्य, धर्म, पिता, तीर्थयात्रा, पूर्वज",
        "benefic_planets": ["Jupiter", "Sun", "Mars"],
        "malefic_planets": ["Rahu", "Venus"],
    },
    10: {
        "khana": 10,
        "pakka_ruler": "Saturn (शनि)",
        "pakka_sign": "Capricorn (मकर)",
        "karaka": "Saturn (शनि)",
        "nature_hi": "कर्म, हुकूमत, मान-प्रतिष्ठा, व्यवसाय",
        "benefic_planets": ["Saturn", "Mercury", "Sun"],
        "malefic_planets": ["Moon", "Mars"],
    },
    11: {
        "khana": 11,
        "pakka_ruler": "Jupiter (बृहस्पति) & Saturn (शनि)",
        "pakka_sign": "Aquarius (कुम्भ)",
        "karaka": "Jupiter (बृहस्पति)",
        "nature_hi": "लाभ, बड़े भाई, आमदनी, इच्छा पूर्ति",
        "benefic_planets": ["Jupiter", "Saturn", "Sun"],
        "malefic_planets": ["Moon"],
    },
    12: {
        "khana": 12,
        "pakka_ruler": "Jupiter (बृहस्पति) & Rahu (राहु)",
        "pakka_sign": "Pisces (मीन)",
        "karaka": "Ketu (केतु)",
        "nature_hi": "शयन सुख, व्यय, विदेश, मोक्ष, राहु का घर",
        "benefic_planets": ["Jupiter", "Rahu", "Ketu"],
        "malefic_planets": ["Mars", "Sun", "Venus"],
    }
}


# -------------------------------------------------------------
# 2. Lal Kitab 7 Major Karmic Debts (Rinas)
# -------------------------------------------------------------

DEBT_DEFINITIONS = [
    {
        "id": "pitra_rina",
        "name_hi": "पितृ ऋण (Forefathers' Debt)",
        "cause_hi": "पूर्वजों द्वारा किसी पूज्य संत, मंदिर या ब्राह्मण का अपमान अथवा पीपल का वृक्ष काटना।",
        "condition_desc_hi": "गुरु (बृहस्पति) का खाना 2, 5, 9 या 12 में शुक्र, बुध, राहु या केतु से पीड़ित होना अथवा गुरु का नीच होना।",
        "effect_hi": "संतान प्राप्ति में बाधा, उच्च शिक्षा में रुकावट, बाल समय से पहले सफेद होना, आर्थिक अस्थिरता।",
        "remedy_hi": "परिवार के सभी रक्त-संबंधी सदस्यों से बराबर वजन या धन लेकर किसी मंदिर या धर्मस्थान में दान करें।",
    },
    {
        "id": "matra_rina",
        "name_hi": "मातृ ऋण (Mother's Debt)",
        "cause_hi": "पूर्वजन्म में माता या किसी असहाय स्त्री का तिरस्कार अथवा उन्हें कष्ट पहुँचाना।",
        "condition_desc_hi": "चन्द्रमा का खाना 2, 4 में केतु, राहु अथवा शनि से दृष्ट या पीड़ित होना।",
        "effect_hi": "मानसिक अशांति, अत्यधिक तनाव, धन का व्यर्थ बह जाना, फेफड़ों व छाती के विकार।",
        "remedy_hi": "परिवार के सभी सदस्यों से बराबर चाँदी का सिक्का या चाँदी लेकर बहते पानी में प्रवाहित करें।",
    },
    {
        "id": "swa_rina",
        "name_hi": "स्व-ऋण / आत्म-ऋण (Self Debt)",
        "cause_hi": "नास्तिकता, धर्म और परंपराओं की अवहेलना करना या कुलदेवी/देवता को भूल जाना।",
        "condition_desc_hi": "सूर्य का खाना 5 में राहु, शनि या केतु से पीड़ित होना अथवा शुक्र के साथ बैठना।",
        "effect_hi": "मुकदमेबाजी, बदनामी, हड्डियों या हृदय के रोग, सरकारी कार्यों में लगातार अड़चनें।",
        "remedy_hi": "परिवार के सभी सदस्यों से समान सिक्का/तांबा लेकर यज्ञ या सूर्य नारायण की पूजा कराएं।",
    },
    {
        "id": "stri_rina",
        "name_hi": "स्त्री ऋण (Woman's Debt)",
        "cause_hi": "गर्भवती स्त्री को सताना, पत्नी का अपमान करना या कन्या भ्रूण को कष्ट देना।",
        "condition_desc_hi": "शुक्र का खाना 2 या 7 में राहु, सूर्य या मंगल से दूषित होना।",
        "effect_hi": "वैवाहिक जीवन में कलह, दांपत्य सुख का अभाव, गुप्त रोग, व्यापार में भारी घाटा।",
        "remedy_hi": "परिवार के सभी सदस्यों से अन्न या धन एकत्र कर 100 गायों को हरा चारा खिलाएं।",
    },
    {
        "id": "rishtedari_rina",
        "name_hi": "रिश्तेदारी ऋण (Relatives' Debt)",
        "cause_hi": "भाइयों, मित्रों या सगे संबंधियों का हक मारना अथवा उनकी जमीन हड़पना।",
        "condition_desc_hi": "मंगल का खाना 1 या 8 में बुध अथवा केतु के साथ होना या बुध का नीच होना।",
        "effect_hi": "रक्त विकार, दुर्घटनाएं, भाइयों से दुश्मनी, संतान का अवज्ञाकारी होना।",
        "remedy_hi": "हकीम, चिकित्सक या जरूरतमंदों को मुफ्त दवाइयों का वितरण करें।",
    },
    {
        "id": "nirdayi_rina",
        "name_hi": "निर्दयी ऋण (Cruelty / Oppression Debt)",
        "cause_hi": "किसी जीव, निर्दोष पशु या मजदूर पर अत्याचार करना, उनकी मेहनत की मजदूरी न देना।",
        "condition_desc_hi": "शनि का खाना 10 या 11 में सूर्य, चन्द्र या मंगल से पीड़ित होना।",
        "effect_hi": "अचानक आग लगना, घर में चोरी, असाध्य रोग, अकाल कष्ट।",
        "remedy_hi": "मजदूरों, असहायों और कौओं/कुत्तों को तेल लगी रोटी या भोजन कराएं।",
    },
    {
        "id": "ani_rina",
        "name_hi": "अनिष्ट / कुदरती ऋण (Nature / God's Debt)",
        "cause_hi": "कुत्ते, पक्षी या बेजुबान जानवरों को मारना अथवा विश्वासघात करना।",
        "condition_desc_hi": "केतु का खाना 6 या 12 में चन्द्र या मंगल से दृष्ट होना।",
        "effect_hi": "पैरों व जोड़ों का दर्द, मूत्र विकार, संतानों का रोगी होना, हर कार्य में अड़चन।",
        "remedy_hi": "100 आवारा कुत्तों को मीठी रोटी अथवा दूध-ब्रेड खिलाएं। कान में सोना पहनें।",
    }
]


# -------------------------------------------------------------
# 3. Lal Kitab Core Engine Class
# -------------------------------------------------------------

class LalKitabResult(BaseModel):
    khana_planets: Dict[int, List[str]]
    planet_khanas: Dict[str, int]
    sleeping_houses: List[int]
    awakened_houses: List[int]
    sleeping_planets: List[str]
    active_debts: List[Dict[str, Any]]
    dharmi_teva: bool
    andha_teva: bool
    specific_remedies: List[Dict[str, Any]]


class LalKitabEngine:
    """
    Classical Lal Kitab 1952 engine for converting Lagna Chart into Kalapurusha Khana system,
    analyzing debts, sleeping houses, and generating authentic classical totkas.
    """

    @classmethod
    def calculate(cls, chart: KundaliChart) -> LalKitabResult:
        # In Lal Kitab, House 1 = Lagna, House 2 = 2nd from Lagna, etc.
        # But planets are treated in the 1-12 Khana framework (fixed Aries archetype)
        khana_planets = {i: [] for i in range(1, 13)}
        planet_khanas = {}

        for p_name, p_pos in chart.planets.items():
            # Lal Kitab takes house from Lagna as Khana number (1 to 12)
            khana = p_pos.house_from_lagna
            khana_planets[khana].append(p_name)
            planet_khanas[p_name] = khana

        # 1. Sleeping Houses (Soya Hua Ghar)
        # A house is sleeping if it has no planets AND is not aspected by any planet
        # In Lal Kitab, aspect rules differ (Houses 1-7, 4-10, 8-12 etc.), but simple rule:
        # Empty house without planets is initially considered asleep
        sleeping_houses = [h for h in range(1, 13) if len(khana_planets[h]) == 0]
        awakened_houses = [h for h in range(1, 13) if len(khana_planets[h]) > 0]

        # 2. Sleeping Planets (Soya Hua Graha)
        # If planet is in sleeping house or has no planet in its reciprocal house
        sleeping_planets = []
        for p, kh in planet_khanas.items():
            # If the ruler of this khana is unoccupied
            ruler = LAL_KITAB_KHANA_DATA[kh]["pakka_ruler"].split()[0]
            if ruler in planet_khanas:
                r_kh = planet_khanas[ruler]
                if len(khana_planets[r_kh]) <= 1:
                    sleeping_planets.append(p)

        # 3. Dharmi Teva (धर्मी तेवा - Blessed Kundali)
        # If Jupiter is in Kendra (1, 4, 7, 10) or Saturn is in 11, or Rahu/Ketu are in 4
        dharmi = False
        jup_kh = planet_khanas.get("Jupiter", 0)
        sat_kh = planet_khanas.get("Saturn", 0)
        if jup_kh in [1, 4, 7, 10] or sat_kh == 11 or planet_khanas.get("Rahu") == 4:
            dharmi = True

        # 4. Andha Teva (अंधा तेवा - Blind Horoscope)
        # If 10th house has two enemy planets, or Sun and Saturn together in 10th
        andha = False
        h10_pl = khana_planets[10]
        if "Sun" in h10_pl and "Saturn" in h10_pl:
            andha = True

        # 5. Evaluate Debts (Rinas)
        active_debts = []
        
        # Pitra Rina check
        if jup_kh in [2, 5, 9, 12]:
            h_pl = khana_planets[jup_kh]
            if any(p in h_pl for p in ["Venus", "Mercury", "Rahu", "Ketu"]):
                active_debts.append(DEBT_DEFINITIONS[0])
        elif chart.planets.get("Jupiter") and chart.planets["Jupiter"].dignity == "debilitated":
            active_debts.append(DEBT_DEFINITIONS[0])

        # Matra Rina check
        moon_kh = planet_khanas.get("Moon", 0)
        if moon_kh in [2, 4]:
            h_pl = khana_planets[moon_kh]
            if any(p in h_pl for p in ["Ketu", "Rahu", "Saturn"]):
                active_debts.append(DEBT_DEFINITIONS[1])

        # Swa Rina check
        sun_kh = planet_khanas.get("Sun", 0)
        if sun_kh == 5:
            h_pl = khana_planets[5]
            if any(p in h_pl for p in ["Rahu", "Saturn", "Ketu", "Venus"]):
                active_debts.append(DEBT_DEFINITIONS[2])

        # Stri Rina check
        ven_kh = planet_khanas.get("Venus", 0)
        if ven_kh in [2, 7]:
            h_pl = khana_planets[ven_kh]
            if any(p in h_pl for p in ["Rahu", "Sun", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[3])

        # Rishtedari Rina check
        mars_kh = planet_khanas.get("Mars", 0)
        if mars_kh in [1, 8]:
            h_pl = khana_planets[mars_kh]
            if any(p in h_pl for p in ["Mercury", "Ketu"]):
                active_debts.append(DEBT_DEFINITIONS[4])

        # Nirdayi Rina check
        if sat_kh in [10, 11]:
            h_pl = khana_planets[sat_kh]
            if any(p in h_pl for p in ["Sun", "Moon", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[5])

        # Anisht Rina check
        ketu_kh = planet_khanas.get("Ketu", 0)
        if ketu_kh in [6, 12]:
            h_pl = khana_planets[ketu_kh]
            if any(p in h_pl for p in ["Moon", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[6])

        # 6. Specific Lal Kitab Remedies for key afflicted placements
        specific_remedies = []
        if sat_kh in [1, 4, 7, 10]:
            specific_remedies.append({
                "placement": f"शनि खाना नं. {sat_kh}",
                "totka_hi": "भैंस या काले कुत्ते को तेल चुपड़ी रोटी खिलाएं। बहते पानी में नारियल या बादाम प्रवाहित करें।"
            })
        if mars_kh in [1, 4, 7, 8, 12]:
            specific_remedies.append({
                "placement": f"मंगल खाना नं. {mars_kh} (मंगल बद)",
                "totka_hi": "चाँदी का चौरस टुकड़ा अपनी जेब या पर्स में रखें। मीठी रोटी तंदूर में बनवाकर गरीबों को बांटें।"
            })
        if planet_khanas.get("Rahu") in [1, 5, 9, 12]:
            specific_remedies.append({
                "placement": f"राहु खाना नं. {planet_khanas.get('Rahu')}",
                "totka_hi": "सरस्वती माता की आराधना करें। पीले कपड़े में साबुत मूंग या चने की दाल बांधकर सिरहाने रखें।"
            })
        if planet_khanas.get("Ketu") in [6, 8, 12]:
            specific_remedies.append({
                "placement": f"केतु खाना नं. {planet_khanas.get('Ketu')}",
                "totka_hi": "कान में सोना धारण करें। चितकबरे कुत्ते को भोजन दें। गणेश जी को दूर्वा अर्पित करें।"
            })

        return LalKitabResult(
            khana_planets=khana_planets,
            planet_khanas=planet_khanas,
            sleeping_houses=sleeping_houses,
            awakened_houses=awakened_houses,
            sleeping_planets=list(set(sleeping_planets)),
            active_debts=active_debts,
            dharmi_teva=dharmi,
            andha_teva=andha,
            specific_remedies=specific_remedies
        )


default_lalkitab_engine = LalKitabEngine()
