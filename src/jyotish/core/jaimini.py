"""
Jaimini System, Special Lagnas, and Arudha Padas Engine for JyotishOS.
Calculates:
1. 7 and 8 Chara Karakas (AK, AmK, BK, MK, PiK, PK, GK, DK).
2. Karakamsha (Navamsha sign of Atmakaraka).
3. Complete 12 Arudha Padas (AL, UL, A1-A12) with classical exceptions (1st -> 10th, 7th -> 4th).
4. Special Lagnas:
   - Hora Lagna (HL): Wealth, financial prosperity, and transactions.
   - Ghati Lagna (GL): Power, prestige, authority, and public status.
   - Sri Lagna (SL): Wealth, auspiciousness, and blessings of Mahalakshmi.
   - Indu Lagna: Financial standing, hidden wealth, and Dhana yogas.
   - Bhava Lagna (BL): Physical health, baseline aura, and vitality.
   - Pranapada Lagna (PP): Life breath, soul connection, and birth time accuracy.
   - Varnada Lagna (VL): Sustenance, career role, and societal position.
"""

from typing import Dict, List, Tuple, Optional, Any
from .constants import SIGN_NAMES, SIGN_LORDS
from .models import KundaliChart, JaiminiResult


# Indu Lagna Planetary Kalas (Rays / Bindus)
INDU_RAYS = {
    "Sun": 30,
    "Moon": 16,
    "Mars": 6,
    "Mercury": 8,
    "Jupiter": 10,
    "Venus": 12,
    "Saturn": 1,
}

ARUDHA_SIGNIFICATIONS = {
    "AL": {
        "hi": "प्रथम आरूढ़ / आरूढ़ लग्न (AL): सामाजिक छवि, मान-सम्मान, बाह्य व्यक्तित्व एवं प्रतिष्ठा।",
        "en": "Self-image, public perception, reputation, and worldly identity."
    },
    "A2": {
        "hi": "कोष पद (A2): संचित धन, चल-अचल संपत्ति, पारिवारिक संपदा एवं वाक् सिद्धि।",
        "en": "Accumulated wealth, financial assets, speech, and material sustenance."
    },
    "A3": {
        "hi": "भ्रातृ पद (A3): पराक्रम, साहस, अनुज सहोदर, कला-कौशल एवं संचार।",
        "en": "Courage, prowess, younger siblings, talents, and communication."
    },
    "A4": {
        "hi": "मातृ/सुख पद (A4): आंतरिक सुख, वाहन, भूमि-भवन, गृह वातावरण एवं माता का प्रभाव।",
        "en": "Inner contentment, vehicles, properties, mother, and domestic peace."
    },
    "A5": {
        "hi": "मंत्र/पुत्र पद (A5): बुद्धि, पूर्वपुण्य, संतान सुख, मंत्र साधना एवं परामर्श क्षमता।",
        "en": "Intelligence, progeny, speculative gains, mantras, and past-life merits."
    },
    "A6": {
        "hi": "रोग/शत्रु पद (A6): रोग, ऋण, शत्रु, प्रतिस्पर्धा, सेवा कार्य एवं संघर्ष क्षमता।",
        "en": "Enemies, litigations, debts, illnesses, service, and obstacles overcome."
    },
    "A7": {
        "hi": "दार पद (A7): जीवनसाथी का स्वरूप, व्यापारिक साझेदार, संबंध एवं वाणिज्य।",
        "en": "Spouse characteristics, business partners, sexual relations, and public relations."
    },
    "A8": {
        "hi": "मृत्यु पद (A8): आयु, अचानक परिवर्तन, गुप्त ज्ञान, संकट एवं पैतृक संपत्ति।",
        "en": "Longevity, sudden events, hidden research, transformations, and occult."
    },
    "A9": {
        "hi": "भाग्य पद (A9): भाग्य, धर्म, गुरु, तीर्थाटन, उच्च विद्या एवं ईश्वरीय कृपा।",
        "en": "Fortune, dharma, higher learning, father, pilgrimages, and divine grace."
    },
    "A10": {
        "hi": "राज्य पद (A10): कर्मक्षेत्र, पद-प्रतिष्ठा, प्रशासनिक अधिकार, यश एवं सफलता।",
        "en": "Career stature, administrative power, societal leadership, and profession."
    },
    "A11": {
        "hi": "लाभ पद (A11): सर्वतोमुखी लाभ, आय के स्रोत, बड़े भाई-बहन, मित्र एवं महत्वाकांक्षा।",
        "en": "Financial gains, friendships, older siblings, fulfillment of desires."
    },
    "UL": {
        "hi": "उपपद लग्न / व्यय पद (UL/A12): वैवाहिक संबंध की स्थिरता, जीवनसाथी का कुल, दान एवं मोक्ष।",
        "en": "Spouse family status, marital longevity, sacrifices, charities, and spiritual liberation."
    }
}


class JaiminiCalculator:
    """Calculates Jaimini astrological indicators according to Jaimini Upadesha Sutras and BPHS."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> JaiminiResult:
        """Complete Jaimini and Special Lagnas computation."""
        # 1. 7 and 8 Chara Karakas
        karakas_7, karakas_8 = cls._calculate_karakas(chart)

        # 2. Karakamsha (Navamsha sign of Atmakaraka)
        ak_name = karakas_7["AK"]
        ak_planet = chart.planets[ak_name]
        d9_sign_id = cls._get_navamsha_sign(ak_planet.longitude)
        d9_sign_name = SIGN_NAMES[d9_sign_id - 1]

        # 3. Arudha Padas (AL, UL, A1..A12) with classical exceptions and detailed breakdown
        arudha_padas, arudha_names, arudha_details = cls._calculate_arudha_padas(chart)

        # 4. Special Lagnas Calculations
        hl_sign, hl_deg, hl_lon = cls._calculate_hora_lagna(chart)
        gl_sign, gl_deg, gl_lon = cls._calculate_ghati_lagna(chart)
        sl_sign, sl_deg, sl_lon = cls._calculate_sri_lagna(chart)
        indu_sign = cls._calculate_indu_lagna(chart)
        bl_sign, bl_deg, bl_lon = cls._calculate_bhava_lagna(chart)
        pp_sign, pp_deg, pp_lon = cls._calculate_pranapada_lagna(chart)
        vl_sign = cls._calculate_varnada_lagna(chart, hl_sign)

        special_lagnas_detail = {
            "HL": {
                "name_hi": "होरा लग्न (Hora Lagna)",
                "sign": hl_sign,
                "degree": round(hl_deg, 2),
                "longitude": round(hl_lon, 2),
                "lord": SIGN_LORDS.get(hl_sign, ""),
                "purpose_hi": "धन संपदा, आर्थिक समृद्धि एवं वित्तीय लेन-देन का मुख्य संकेतक।",
                "purpose_en": "Primary indicator of financial prosperity, wealth flows, and asset valuation."
            },
            "GL": {
                "name_hi": "घटी लग्न (Ghati Lagna)",
                "sign": gl_sign,
                "degree": round(gl_deg, 2),
                "longitude": round(gl_lon, 2),
                "lord": SIGN_LORDS.get(gl_sign, ""),
                "purpose_hi": "सत्ता, पद, प्रतिष्ठा, शासकीय अधिकार एवं नेतृत्व क्षमता का संकेतक।",
                "purpose_en": "Authority, public fame, governmental power, and societal leadership."
            },
            "SL": {
                "name_hi": "श्री लग्न (Sree Lagna)",
                "sign": sl_sign,
                "degree": round(sl_deg, 2),
                "longitude": round(sl_lon, 2),
                "lord": SIGN_LORDS.get(sl_sign, ""),
                "purpose_hi": "महालक्ष्मी कृपा, सौभाग्य, विलासिता एवं स्थायी आर्थिक सुरक्षा।",
                "purpose_en": "Blessings of Goddess Lakshmi, auspicious fortunes, and sustained abundance."
            },
            "IL": {
                "name_hi": "इन्दु लग्न (Indu Lagna)",
                "sign": indu_sign,
                "degree": 0.0,
                "longitude": 0.0,
                "lord": SIGN_LORDS.get(indu_sign, ""),
                "purpose_hi": "विशेष धन योग, गुप्त धन, वित्तीय साम्राज्य एवं कोटिपतित्व।",
                "purpose_en": "Special wealth yogas, multi-millionaire potential, and financial fortitude."
            },
            "BL": {
                "name_hi": "भाव लग्न (Bhava Lagna)",
                "sign": bl_sign,
                "degree": round(bl_deg, 2),
                "longitude": round(bl_lon, 2),
                "lord": SIGN_LORDS.get(bl_sign, ""),
                "purpose_hi": "शारीरिक ओज, बाह्य प्रभाव, जीवन शक्ति एवं मूल आभा मंडल।",
                "purpose_en": "Physical aura, outer influence, vital baseline energy, and life force."
            },
            "PP": {
                "name_hi": "प्राणपद लग्न (Pranapada Lagna)",
                "sign": pp_sign,
                "degree": round(pp_deg, 2),
                "longitude": round(pp_lon, 2),
                "lord": SIGN_LORDS.get(pp_sign, ""),
                "purpose_hi": "प्राण वायु, जीवन शक्ति एवं जन्म समय शोधन (BTR) का सूक्ष्म संकेतक।",
                "purpose_en": "Breath of life, soul connection, and high-precision birth time rectification."
            },
            "VL": {
                "name_hi": "वर्णद लग्न (Varnada Lagna)",
                "sign": vl_sign,
                "degree": 0.0,
                "longitude": 0.0,
                "lord": SIGN_LORDS.get(vl_sign, ""),
                "purpose_hi": "आजीविका की प्रकृति, सामाजिक वर्ण (भूमिका) एवं आजीविका निर्वाह।",
                "purpose_en": "Socio-professional orientation, livelihood sustenance, and social standing."
            }
        }

        return JaiminiResult(
            karakas_7=karakas_7,
            karakas_8=karakas_8,
            karakamsha_sign_id=d9_sign_id,
            karakamsha_sign_name=d9_sign_name,
            arudha_padas=arudha_padas,
            arudha_pada_names=arudha_names,
            hora_lagna_sign_name=hl_sign,
            ghati_lagna_sign_name=gl_sign,
            sri_lagna_sign_name=sl_sign,
            indu_lagna_sign_name=indu_sign,
            bhava_lagna_sign_name=bl_sign,
            pranapada_lagna_sign_name=pp_sign,
            varnada_lagna_sign_name=vl_sign,
            special_lagnas_detail=special_lagnas_detail,
            arudha_details=arudha_details
        )

    @classmethod
    def _calculate_karakas(cls, chart: KundaliChart) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Computes 7-Karaka and 8-Karaka designations by descending degrees."""
        seven_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        sorted_7 = sorted(seven_names, key=lambda p: chart.planets[p].sign_degree, reverse=True)

        labels_7 = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        karakas_7 = {labels_7[i]: sorted_7[i] for i in range(7)}

        # 8-Karaka scheme includes Rahu (degree from end of sign since retrograde)
        rahu_deg = 30.0 - chart.planets["Rahu"].sign_degree  # inverted for retrograde
        deg_map = {p: chart.planets[p].sign_degree for p in seven_names}
        deg_map["Rahu"] = rahu_deg
        sorted_8 = sorted(deg_map.keys(), key=lambda p: deg_map[p], reverse=True)

        labels_8 = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
        karakas_8 = {labels_8[i]: sorted_8[i] for i in range(8)}

        return karakas_7, karakas_8

    @classmethod
    def _get_navamsha_sign(cls, lon: float) -> int:
        """Calculates D9 Navamsha sign ID (1-12)."""
        pada_idx = int((lon % 360.0) // (360.0 / 108.0))
        return (pada_idx % 12) + 1

    @classmethod
    def _calculate_arudha_padas(cls, chart: KundaliChart) -> Tuple[Dict[str, int], Dict[str, str], Dict[str, Dict[str, Any]]]:
        """
        Calculates Arudha Padas for all 12 houses with classical exception handling:
        If lord is in 1st house -> Pada is 10th from house.
        If lord is in 7th house -> Pada is 4th from house.
        """
        padas: Dict[str, int] = {}
        names: Dict[str, str] = {}
        details: Dict[str, Dict[str, Any]] = {}

        for h in range(1, 13):
            house_sign = chart.houses[h - 1].sign_id  # 1-12
            house_sign_name = SIGN_NAMES[house_sign - 1]
            lord_name = chart.houses[h - 1].lord
            lord_sign = chart.planets[lord_name].sign_id  # 1-12
            lord_sign_name = SIGN_NAMES[lord_sign - 1]

            # Distance from house to its lord (1 to 12)
            distance = ((lord_sign - house_sign) % 12) + 1

            exception_text = "सामान्य (Standard Rule)"
            if distance == 1:
                # Exception 1: Lord in same house -> Pada falls in 10th
                target_sign = ((house_sign - 1 + 9) % 12) + 1
                exception_text = "अपवाद १ (स्वामी स्वगृह में -> १०वां भाव)"
            elif distance == 7:
                # Exception 2: Lord in 7th from house -> Pada falls in 4th
                target_sign = ((house_sign - 1 + 3) % 12) + 1
                exception_text = "अपवाद २ (स्वामी ७वें भाव में -> ४था भाव)"
            else:
                # Standard rule: project distance steps ahead from lord
                target_sign = ((lord_sign - 1 + (distance - 1)) % 12) + 1

            label = "AL" if h == 1 else ("UL" if h == 12 else f"A{h}")
            pada_name = SIGN_NAMES[target_sign - 1]
            padas[label] = target_sign
            names[label] = pada_name

            # House placement from Lagna
            pada_house_from_lagna = ((target_sign - chart.lagna_sign_id) % 12) + 1

            sig = ARUDHA_SIGNIFICATIONS.get(label, {"hi": "", "en": ""})

            details[label] = {
                "label": label,
                "house_num": h,
                "house_sign": house_sign_name,
                "lord_name": lord_name,
                "lord_sign": lord_sign_name,
                "distance": distance,
                "exception": exception_text,
                "pada_sign_id": target_sign,
                "pada_sign_name": pada_name,
                "pada_house_from_lagna": pada_house_from_lagna,
                "signification_hi": sig["hi"],
                "signification_en": sig["en"]
            }

        return padas, names, details

    @classmethod
    def _calculate_hora_lagna(cls, chart: KundaliChart) -> Tuple[str, float, float]:
        """Hora Lagna: advances 1 sign (30 deg) per 2.5 ghatis (~1 hr) from Sun."""
        sun = chart.planets["Sun"]
        hours = chart.birth_data.birth_time.hour + chart.birth_data.birth_time.minute / 60.0 + chart.birth_data.birth_time.second / 3600.0
        # Total degrees advance: 30 degrees per hour from Sun's longitude
        hl_lon = (sun.longitude + (hours * 30.0)) % 360.0
        hl_sign_idx = int(hl_lon // 30.0)
        hl_deg = hl_lon % 30.0
        return SIGN_NAMES[hl_sign_idx], hl_deg, hl_lon

    @classmethod
    def _calculate_ghati_lagna(cls, chart: KundaliChart) -> Tuple[str, float, float]:
        """Ghati Lagna: advances 1 sign per ghati (24 minutes = 1.25 deg/min) from Lagna."""
        hours = chart.birth_data.birth_time.hour + chart.birth_data.birth_time.minute / 60.0 + chart.birth_data.birth_time.second / 3600.0
        ghatis = hours * 2.5
        gl_lon = (chart.lagna_longitude + (ghatis * 30.0)) % 360.0
        gl_sign_idx = int(gl_lon // 30.0)
        gl_deg = gl_lon % 30.0
        return SIGN_NAMES[gl_sign_idx], gl_deg, gl_lon

    @classmethod
    def _calculate_sri_lagna(cls, chart: KundaliChart) -> Tuple[str, float, float]:
        """Sri Lagna: Fortunes and Mahalakshmi blessings."""
        moon = chart.planets["Moon"]
        nak_span = 360.0 / 27.0
        frac = (moon.longitude % nak_span) / nak_span
        sl_lon = (chart.lagna_longitude + frac * 360.0) % 360.0
        sl_sign_idx = int(sl_lon // 30.0)
        sl_deg = sl_lon % 30.0
        return SIGN_NAMES[sl_sign_idx], sl_deg, sl_lon

    @classmethod
    def _calculate_indu_lagna(cls, chart: KundaliChart) -> str:
        """
        Indu Lagna: Sum of 9th lord rays from Lagna and Moon.
        Count remainder houses from Moon.
        """
        # 9th from Lagna
        h9_lagna_sign = chart.houses[8].sign_name
        lord_h9_lagna = SIGN_LORDS[h9_lagna_sign]
        rays1 = INDU_RAYS.get(lord_h9_lagna, 6)

        # 9th from Moon
        moon_sign_id = chart.planets["Moon"].sign_id
        sign9_moon_id = ((moon_sign_id - 1 + 8) % 12) + 1
        sign9_moon_name = SIGN_NAMES[sign9_moon_id - 1]
        lord_h9_moon = SIGN_LORDS[sign9_moon_name]
        rays2 = INDU_RAYS.get(lord_h9_moon, 6)

        total_rays = rays1 + rays2
        rem = total_rays % 12
        if rem == 0:
            rem = 12

        indu_sign_id = ((moon_sign_id - 1 + (rem - 1)) % 12) + 1
        return SIGN_NAMES[indu_sign_id - 1]

    @classmethod
    def _calculate_bhava_lagna(cls, chart: KundaliChart) -> Tuple[str, float, float]:
        """Bhava Lagna: advances 1 sign per 5 ghatis (2 hours = 15 deg/hr) from Sun/Sunrise."""
        sun = chart.planets["Sun"]
        hours = chart.birth_data.birth_time.hour + chart.birth_data.birth_time.minute / 60.0
        # 15 degrees per hour
        bl_lon = (sun.longitude + (hours * 15.0)) % 360.0
        bl_sign_idx = int(bl_lon // 30.0)
        bl_deg = bl_lon % 30.0
        return SIGN_NAMES[bl_sign_idx], bl_deg, bl_lon

    @classmethod
    def _calculate_pranapada_lagna(cls, chart: KundaliChart) -> Tuple[str, float, float]:
        """Pranapada Lagna: 1 sign per 1 vighati (24 seconds) from Sun."""
        sun = chart.planets["Sun"]
        # Total minutes from start of day
        total_mins = chart.birth_data.birth_time.hour * 60.0 + chart.birth_data.birth_time.minute + chart.birth_data.birth_time.second / 60.0
        vighatis = total_mins * 2.5 * 60.0 / 24.0
        pp_lon = (sun.longitude + (vighatis * 30.0)) % 360.0
        pp_sign_idx = int(pp_lon // 30.0)
        pp_deg = pp_lon % 30.0
        return SIGN_NAMES[pp_sign_idx], pp_deg, pp_lon

    @classmethod
    def _calculate_varnada_lagna(cls, chart: KundaliChart, hl_sign_name: str) -> str:
        """Varnada Lagna calculation based on Lagna and Hora Lagna odd/even polarity."""
        lagna_id = chart.lagna_sign_id
        hl_id = SIGN_NAMES.index(hl_sign_name) + 1

        is_lagna_odd = (lagna_id % 2 != 0)
        is_hl_odd = (hl_id % 2 != 0)

        # Count from Aries to Lagna if odd, or Pisces backward if even
        count_lagna = lagna_id if is_lagna_odd else (13 - lagna_id)
        count_hl = hl_id if is_hl_odd else (13 - hl_id)

        if is_lagna_odd:
            sum_val = (count_lagna + count_hl) % 12
            if sum_val == 0:
                sum_val = 12
            vl_id = sum_val
        else:
            diff_val = (count_lagna - count_hl) % 12
            if diff_val <= 0:
                diff_val += 12
            vl_id = (13 - diff_val) % 12
            if vl_id == 0:
                vl_id = 12

        return SIGN_NAMES[vl_id - 1]


# Singleton Jaimini Calculator
default_jaimini_calculator = JaiminiCalculator()
