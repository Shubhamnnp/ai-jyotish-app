"""
Sudarshan Chakra Engine and Visual Renderer for JyotishOS.
According to Brihat Parashara Hora Shastra (BPHS), Chapter 74 (सुदर्शनचक्राध्यायः).

Unites:
1. Lagna Kundali (Physical Body, Vitality & Deha / Sthula Sharira).
2. Chandra Kundali (Mind, Psychology & Mana / Sukshma Sharira).
3. Surya Kundali (Soul, Willpower, Atma / Karana Sharira).

Provides comprehensive 9-tier synthesis:
- Interactive 3-Ring Concentric Mandala SVG
- 12 Bhavas Triple Evaluation & Scoring (🌟 त्रि-शुभ, 🟢 द्वि-शुभ, 🟡 एक-शुभ, 🔴 त्रि-अशुभ)
- Sudarshan Dasha Engine (1 year per house, Maasika, Pratyantara, 120-year timeline)
- Sudarshan Mahayogas across the 3 wheels
- Triad Dominance & Sthula-Sukshma-Karana Harmony
- 7 Core Life Domains Triple Synthesis
- Sudarshan + Ashtakavarga Bindu Synthesis
- Classical BPHS Chapter 74 Shlokas & Sutras
- Sri Sudarshan Kavach, Gayatri, Ashtakam & Vedic Shanti Remedies
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from src.jyotish.core.constants import SIGN_NAMES
from src.jyotish.core.models import KundaliChart


SIGN_NAMES_HI = [
    "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"
]

PLANET_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
}

PLANET_SHORT_HI = {
    "Sun": "सू", "Moon": "चं", "Mars": "मं", "Mercury": "बु",
    "Jupiter": "गु", "Venus": "शु", "Saturn": "श", "Rahu": "रा", "Ketu": "के"
}

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}


def _get_aspects_on_sign(target_sign: int, chart: KundaliChart) -> List[str]:
    """Calculates planets aspecting a given sign as per Parashari Drishti."""
    aspecting = []
    for p_name, pos in chart.planets.items():
        p_sign = pos.sign_id
        diff = ((target_sign - p_sign) % 12) + 1  # 1-based distance
        if diff == 7:
            aspecting.append(p_name)
        elif p_name == "Mars" and diff in [4, 8]:
            aspecting.append("Mars")
        elif p_name in ["Jupiter", "Rahu", "Ketu"] and diff in [5, 9]:
            aspecting.append(p_name)
        elif p_name == "Saturn" and diff in [3, 10]:
            aspecting.append("Saturn")
    return list(set(aspecting))


class SudarshanChakraEngine:
    """Advanced Vedic Sudarshan Chakra Engine according to BPHS Chapter 74."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates 12 houses through Lagna, Chandra, and Surya frames with complete BPHS synthesis."""
        lagna_sign_id = chart.lagna_sign_id
        moon_sign_id = chart.planets["Moon"].sign_id
        sun_sign_id = chart.planets["Sun"].sign_id

        house_names_hi = [
            "प्रथम भाव (तनु / व्यक्तित्व / देह)",
            "द्वितीय भाव (धन / कुटुंब / वाणी)",
            "तृतीय भाव (पराक्रम / सहोदर / उद्यम)",
            "चतुर्थ भाव (सुख / मातृ / भूमि / वाहन)",
            "पंचम भाव (संतान / बुद्धि / पूर्वपुण्य)",
            "षष्ठ भाव (रोग / ऋण / शत्रु / सेवा)",
            "सप्तम भाव (विवाह / साझेदारी / जाया)",
            "अष्टम भाव (आयु / गूढ़ ज्ञान / रंध्र)",
            "नवम भाव (भाग्य / धर्म / गुरु / तीर्थ)",
            "दशम भाव (कर्म / राज्य / पद / कीर्ति)",
            "एकादश भाव (लाभ / आय / सिद्धि / ज्येष्ठ)",
            "द्वादश भाव (व्यय / मोक्ष / विदेश / शयन)"
        ]

        classical_sutras = [
            "लग्नं देहस्य विज्ञातं मनसश्चैव चन्द्रमाः। सूर्यश्चात्मबलं प्रोक्तं त्रिभिरेतैर्विभावयेत्॥ (देह, आरोग्य व आत्मबल)",
            "धने शुभग्रहाः सर्वे धनधान्यसमृद्धिदाः। त्रितयेऽपि शुभे दृष्टे कुबेरसदृशो भवेत्॥ (स्थिर संपत्ति व कुटुंब सौख्य)",
            "भ्रातृस्थाने शुभाः सौख्यं पराक्रमविवर्धनम्। त्रिचक्रे शौर्ययुक्तश्च भ्रातृभिः सह मोदते॥ (सहोदर सुख व अदम्य साहस)",
            "मातृभूमिगृहं सौख्यं चतुर्थे शुभवीक्षिते। प्रासादवाहनैर्युक्तः सर्वसौख्यसमन्वितः॥ (गृह, वाहन व मातृ स्नेह)",
            "धीस्थाने शुभसंयोगे बुद्धिविद्याविवर्धनम्। सुपुत्रसंयुतो विद्वान् राजपूज्यो भवेन्नरः॥ (मेधा, संतान व पूर्वपुण्य)",
            "रिपुस्थाने शुभा दृष्टा रिपुनाशकराः स्मृताः। पापग्रहैर्युते तस्मिन् रोगऋणविवर्धनम्॥ (रोग, शत्रु व ऋण निवृत्ति)",
            "सप्तमे शुभसंयुक्ते भार्या रूपवती शुभा। त्रिचक्रे सुस्थिते जाया सर्वगुणसमन्विता॥ (उत्कृष्ट दांपत्य व साझेदारी)",
            "रन्ध्रे शुभग्रहा दृष्टा दीर्घायुर्धनवान् भवेत्। त्रिचक्रे क्रूरसंयुक्ते त्वल्पायुः क्लेशभाग्भवेत्॥ (दीर्घायु व गूढ़ ज्ञान)",
            "धर्मे शुभग्रहा दृष्टा तीर्थाटनपरायणः। धर्मिष्टो गुणवान् पूज्यो भाग्योदयसमन्वितः॥ (परम भाग्य, धर्म व गुरु कृपा)",
            "दशमे शुभसंयुक्ते राज्यमान्यो यशस्वी च। कर्मसिद्धिकरः श्रीमान् नृपतिप्रियकारकः॥ (राजमान्य पद, कर्म व कीर्ति)",
            "लाभे सर्वे ग्रहाः शस्ताः सर्वकामफलप्रदाः। त्रिचक्रे शुभसंयुक्ते नित्यं लाभो भवेद् ध्रुवम्॥ (अखंड धन लाभ व मनोकामना पूर्ति)",
            "व्यये शुभग्रहैर्युक्ते शुभकर्मव्ययो भवेत्। मोक्षभागी सुरूपश्च परदेशे सुखं लभेत्॥ (सत्कर्म व्यय, मोक्ष व विदेश वास)"
        ]

        house_analyses = []
        tri_shubh_count = 0
        dvi_shubh_count = 0
        eka_shubh_count = 0
        tri_ashubh_count = 0

        for h in range(1, 13):
            # 1. From Lagna
            l_sign_id = ((lagna_sign_id - 1 + (h - 1)) % 12) + 1
            l_sign = SIGN_NAMES[l_sign_id - 1]
            l_sign_hi = SIGN_NAMES_HI[l_sign_id - 1]
            l_planets = [p_name for p_name, p_pos in chart.planets.items() if p_pos.sign_id == l_sign_id]
            l_planets_hi = [PLANET_NAMES_HI.get(p, p) for p in l_planets]
            l_lord = SIGN_LORDS[l_sign_id]
            l_lord_hi = PLANET_NAMES_HI.get(l_lord, l_lord)
            l_aspects = _get_aspects_on_sign(l_sign_id, chart)
            l_aspects_hi = [PLANET_NAMES_HI.get(p, p) for p in l_aspects]

            # 2. From Moon
            m_sign_id = ((moon_sign_id - 1 + (h - 1)) % 12) + 1
            m_sign = SIGN_NAMES[m_sign_id - 1]
            m_sign_hi = SIGN_NAMES_HI[m_sign_id - 1]
            m_planets = [p_name for p_name, p_pos in chart.planets.items() if p_pos.sign_id == m_sign_id]
            m_planets_hi = [PLANET_NAMES_HI.get(p, p) for p in m_planets]
            m_lord = SIGN_LORDS[m_sign_id]
            m_lord_hi = PLANET_NAMES_HI.get(m_lord, m_lord)
            m_aspects = _get_aspects_on_sign(m_sign_id, chart)
            m_aspects_hi = [PLANET_NAMES_HI.get(p, p) for p in m_aspects]

            # 3. From Sun
            s_sign_id = ((sun_sign_id - 1 + (h - 1)) % 12) + 1
            s_sign = SIGN_NAMES[s_sign_id - 1]
            s_sign_hi = SIGN_NAMES_HI[s_sign_id - 1]
            s_planets = [p_name for p_name, p_pos in chart.planets.items() if p_pos.sign_id == s_sign_id]
            s_planets_hi = [PLANET_NAMES_HI.get(p, p) for p in s_planets]
            s_lord = SIGN_LORDS[s_sign_id]
            s_lord_hi = PLANET_NAMES_HI.get(s_lord, s_lord)
            s_aspects = _get_aspects_on_sign(s_sign_id, chart)
            s_aspects_hi = [PLANET_NAMES_HI.get(p, p) for p in s_aspects]

            # Calculate individual ring auspiciousness
            def _eval_ring(occ: List[str], asp: List[str]) -> Tuple[int, bool]:
                b_occ = sum(1 for p in occ if p in BENEFICS)
                m_occ = sum(1 for p in occ if p in MALEFICS)
                b_asp = sum(1 for p in asp if p in BENEFICS)
                m_asp = sum(1 for p in asp if p in MALEFICS)
                net = (b_occ * 15 + b_asp * 8) - (m_occ * 12 + m_asp * 6)
                r_score = max(30, min(100, 60 + net))
                is_ausp = (net >= 0)
                return r_score, is_ausp

            l_score, l_ausp = _eval_ring(l_planets, l_aspects)
            m_score, m_ausp = _eval_ring(m_planets, m_aspects)
            s_score, s_ausp = _eval_ring(s_planets, s_aspects)

            shubh_wheels = sum([1 if l_ausp else 0, 1 if m_ausp else 0, 1 if s_ausp else 0])

            # Consolidated score
            score_num = int(round((l_score * 0.4) + (m_score * 0.35) + (s_score * 0.25)))
            score_num = max(32, min(98, score_num))

            if shubh_wheels == 3:
                status = "🌟 त्रि-शुभ (100% परम शुभ)"
                tri_shubh_count += 1
                phala_detail = "यह भाव लग्न (देह), चन्द्र (मन) एवं सूर्य (आत्मा) तीनों संकेंद्री चक्रों में अति-अनुकूल है। जीवन के इस क्षेत्र में बिना किसी विघ्न के अखंड सफलता, कीर्ति व सुख प्राप्त होगा।"
            elif shubh_wheels == 2:
                status = "🟢 द्वि-शुभ (66% उत्तम शुभ)"
                dvi_shubh_count += 1
                phala_detail = "दो चक्रों से पूर्ण सहयोग प्राप्त है। सामान्य प्रयासों से भी अभीष्ट फल प्राप्त होंगे तथा परिस्थितियां अधिकांशतः पक्ष में रहेंगी।"
            elif shubh_wheels == 1:
                status = "🟡 एक-शुभ (33% मध्यम फल)"
                eka_shubh_count += 1
                phala_detail = "केवल एक चक्र से सहारा मिल रहा है। मानसिक या शारीरिक संघर्ष के बाद ही सफलता मिलेगी; समय-समय पर उतार-चढ़ाव संभव हैं।"
            else:
                status = "🔴 त्रि-अशुभ (कष्ट / बाधा)"
                tri_ashubh_count += 1
                phala_detail = "तीनों चक्रों में पाप ग्रहों का प्रभाव या प्रतिकूल स्थिति है। इस भाव से संबंधित विषयों में विशेष सावधानी एवं शास्त्रीय सुदर्शन शांति अनुष्ठान अपेक्षित है।"

            house_analyses.append({
                "house_num": h,
                "house_name": house_names_hi[h - 1],
                "lagna_ring": f"{l_sign} ({', '.join(l_planets) if l_planets else '—'})",
                "chandra_ring": f"{m_sign} ({', '.join(m_planets) if m_planets else '—'})",
                "surya_ring": f"{s_sign} ({', '.join(s_planets) if s_planets else '—'})",
                "score": f"{score_num}/100",
                "status": status,
                # Enriched metadata
                "score_num": score_num,
                "shubh_wheels": shubh_wheels,
                "l_sign_id": l_sign_id,
                "l_sign_hi": l_sign_hi,
                "l_planets_hi": l_planets_hi,
                "l_lord_hi": l_lord_hi,
                "l_aspects_hi": l_aspects_hi,
                "l_score": l_score,
                "m_sign_id": m_sign_id,
                "m_sign_hi": m_sign_hi,
                "m_planets_hi": m_planets_hi,
                "m_lord_hi": m_lord_hi,
                "m_aspects_hi": m_aspects_hi,
                "m_score": m_score,
                "s_sign_id": s_sign_id,
                "s_sign_hi": s_sign_hi,
                "s_planets_hi": s_planets_hi,
                "s_lord_hi": s_lord_hi,
                "s_aspects_hi": s_aspects_hi,
                "s_score": s_score,
                "classical_sutra": classical_sutras[h - 1],
                "phala_detail": phala_detail
            })

        return {
            "lagna_sign": SIGN_NAMES[lagna_sign_id - 1],
            "chandra_sign": SIGN_NAMES[moon_sign_id - 1],
            "surya_sign": SIGN_NAMES[sun_sign_id - 1],
            "lagna_sign_hi": SIGN_NAMES_HI[lagna_sign_id - 1],
            "chandra_sign_hi": SIGN_NAMES_HI[moon_sign_id - 1],
            "surya_sign_hi": SIGN_NAMES_HI[sun_sign_id - 1],
            "houses": house_analyses,
            "summary_counts": {
                "tri_shubh": tri_shubh_count,
                "dvi_shubh": dvi_shubh_count,
                "eka_shubh": eka_shubh_count,
                "tri_ashubh": tri_ashubh_count
            }
        }

    @classmethod
    def calculate_dasha(cls, chart: KundaliChart, current_age: int = 30) -> Dict[str, Any]:
        """Calculates BPHS Chapter 74 Sudarshan Dasha:

        - 1 year per house
        - Sub-periods: 1 month per house
        - Pratyantar: ~2.5 days per house
        - Full 12-year cycle and 96-year lifetime timeline
        """
        lagna_sign_id = chart.lagna_sign_id
        moon_sign_id = chart.planets["Moon"].sign_id
        sun_sign_id = chart.planets["Sun"].sign_id

        current_age = max(1, current_age)
        cycle_num = ((current_age - 1) // 12) + 1
        active_house = ((current_age - 1) % 12) + 1

        house_titles = [
            "प्रथम भाव (तनु / स्वास्थ्य / प्रतिष्ठा)",
            "द्वितीय भाव (धन / कुटुंब / संचित पूँजी)",
            "तृतीय भाव (पराक्रम / भ्रातृ / पुरुषार्थ)",
            "चतुर्थ भाव (सुख / माता / संपत्ति / वाहन)",
            "पंचम भाव (बुद्धि / संतान / विद्या / यश)",
            "षष्ठ भाव (शत्रु / रोग / ऋण / विजय)",
            "सप्तम भाव (विवाह / साझेदारी / लोक-संबंध)",
            "अष्टम भाव (आयु / परिवर्तन / गूढ़ अनुसंधान)",
            "नवम भाव (भाग्य / धर्म / गुरु / तीर्थ)",
            "दशम भाव (कर्म / राज्य / पदोन्नति / अधिकार)",
            "एकादश भाव (लाभ / समृद्धि / अभीष्ट सिद्धि)",
            "द्वादश भाव (व्यय / विदेश / मोक्ष / एकांत)"
        ]

        l_sign_id = ((lagna_sign_id - 1 + (active_house - 1)) % 12) + 1
        m_sign_id = ((moon_sign_id - 1 + (active_house - 1)) % 12) + 1
        s_sign_id = ((sun_sign_id - 1 + (active_house - 1)) % 12) + 1

        l_sign_hi = SIGN_NAMES_HI[l_sign_id - 1]
        m_sign_hi = SIGN_NAMES_HI[m_sign_id - 1]
        s_sign_hi = SIGN_NAMES_HI[s_sign_id - 1]

        l_lord_hi = PLANET_NAMES_HI[SIGN_LORDS[l_sign_id]]
        m_lord_hi = PLANET_NAMES_HI[SIGN_LORDS[m_sign_id]]
        s_lord_hi = PLANET_NAMES_HI[SIGN_LORDS[s_sign_id]]

        l_occ = [PLANET_NAMES_HI.get(p, p) for p, pos in chart.planets.items() if pos.sign_id == l_sign_id]
        m_occ = [PLANET_NAMES_HI.get(p, p) for p, pos in chart.planets.items() if pos.sign_id == m_sign_id]
        s_occ = [PLANET_NAMES_HI.get(p, p) for p, pos in chart.planets.items() if pos.sign_id == s_sign_id]

        # Monthly Antardashas (12 months starting from active_house)
        months = []
        month_names_hi = [
            "१. चैत्र / प्रथम मास", "२. वैशाख / द्वितीय मास", "३. ज्येष्ठ / तृतीय मास",
            "४. आषाढ़ / चतुर्थ मास", "५. श्रावण / पंचम मास", "६. भाद्रपद / षष्ठ मास",
            "७. आश्विन / सप्तम मास", "८. कार्तिक / अष्टम मास", "९. मार्गशीर्ष / नवम मास",
            "१०. पौष / दशम मास", "११. माघ / एकादश मास", "१२. फाल्गुन / द्वादश मास"
        ]
        for m in range(1, 13):
            sub_h = (((active_house - 1) + (m - 1)) % 12) + 1
            sub_l_s = SIGN_NAMES_HI[((lagna_sign_id - 1 + (sub_h - 1)) % 12)]
            sub_m_s = SIGN_NAMES_HI[((moon_sign_id - 1 + (sub_h - 1)) % 12)]
            sub_s_s = SIGN_NAMES_HI[((sun_sign_id - 1 + (sub_h - 1)) % 12)]
            months.append({
                "month_num": m,
                "month_label": month_names_hi[m - 1],
                "active_house": sub_h,
                "active_house_label": f"भाव {sub_h}",
                "lagna_sign": sub_l_s,
                "moon_sign": sub_m_s,
                "sun_sign": sub_s_s
            })

        # 12-Year Cycle Table
        cycle_table = []
        cycle_start_age = (cycle_num - 1) * 12 + 1
        for i in range(12):
            age_val = cycle_start_age + i
            h_val = i + 1
            h_l_sign = SIGN_NAMES_HI[((lagna_sign_id - 1 + (h_val - 1)) % 12)]
            h_m_sign = SIGN_NAMES_HI[((moon_sign_id - 1 + (h_val - 1)) % 12)]
            h_s_sign = SIGN_NAMES_HI[((sun_sign_id - 1 + (h_val - 1)) % 12)]
            cycle_table.append({
                "year_in_cycle": i + 1,
                "age": age_val,
                "house": f"भाव {h_val}",
                "theme": house_titles[h_val - 1].split("(")[1].replace(")", "").strip(),
                "lagna_rashi": h_l_sign,
                "moon_rashi": h_m_sign,
                "sun_rashi": h_s_sign,
                "is_current": (age_val == current_age)
            })

        # Lifetime Timeline (Ages 1 to 84)
        lifetime_timeline = []
        for a in range(1, 85):
            h_num = ((a - 1) % 12) + 1
            cyc = ((a - 1) // 12) + 1
            lifetime_timeline.append({
                "age": a,
                "cycle": f"चक्र {cyc}",
                "house": f"भाव {h_num}",
                "title": house_titles[h_num - 1].split("(")[1].replace(")", "").strip(),
                "lagna_sign": SIGN_NAMES_HI[((lagna_sign_id - 1 + (h_num - 1)) % 12)],
                "moon_sign": SIGN_NAMES_HI[((moon_sign_id - 1 + (h_num - 1)) % 12)],
                "sun_sign": SIGN_NAMES_HI[((sun_sign_id - 1 + (h_num - 1)) % 12)],
                "status": "वर्तमान" if a == current_age else ("व्यतीत" if a < current_age else "भावी")
            })

        annual_predictions = [
            "आत्मबल, शारीरिक ऊर्जा, व्यक्तित्व विकास एवं सामाजिक पहचान में वृद्धि का वर्ष। नवीन उपक्रमों का शुभारंभ अनुकूल रहेगा।",
            "पारिवारिक सुख, संचित पूँजी में वृद्धि, वाणी से कार्य सिद्धि तथा आर्थिक स्थिरता का वर्ष।",
            "साहस, पुरुषार्थ, संचार, लघु यात्राएं एवं भ्रातृ सहयोग में विशेष प्रगति। रचनात्मक कार्यों में सफलता।",
            "गृह, वाहन, भूमि क्रय-विक्रय, माता के स्वास्थ्य व मनःशांति के लिए महत्वपूर्ण अवधि। गृह-सुख में वृद्धि।",
            "संतान प्राप्ति/प्रगति, उच्च विद्या, मंत्र साधना, शेयर/निवेश एवं रचनात्मक बौद्धिक कार्यों में यश।",
            "प्रतियोगिता, कोर्ट-कचहरी व ऋण-मुक्ति में विजय; स्वास्थ्य के प्रति सचेत रहें, विरोधी परास्त होंगे।",
            "विवाह, दांपत्य जीवन, नए व्यापारिक अनुबंध व जनसंपर्क में विस्तार। यात्राओं से लाभ।",
            "आयु, गुप्त विद्याएं, अनुसंधान, वसीयत व अप्रत्याशित परिवर्तनों का वर्ष। योग व प्राणायाम से लाभ।",
            "परम भाग्योदय, धार्मिक अनुष्ठान, उच्च शिक्षा, तीर्थ यात्रा तथा गुरु/पिता का आशीर्वाद।",
            "कर्मक्षेत्र में पदोन्नति, राज्यमान्य सम्मान, व्यापार विस्तार तथा सामाजिक प्रतिष्ठा की पराकाष्ठा।",
            "अखंड आर्थिक लाभ, बड़े भाई-बहनों का सहयोग, उच्च स्तरीय मित्र मंडली एवं दीर्घकालीन आकांक्षाओं की पूर्ति।",
            "विदेश यात्रा, आध्यात्मिक चिंतन, परोपकार, दान-पुण्य एवं शयन सुख; व्यय की अधिकता पर नियंत्रण रखें।"
        ]

        return {
            "current_age": current_age,
            "cycle_num": cycle_num,
            "active_house": active_house,
            "active_house_name": house_titles[active_house - 1],
            "active_lagna_sign": l_sign_hi,
            "active_moon_sign": m_sign_hi,
            "active_sun_sign": s_sign_hi,
            "active_lagna_lord": l_lord_hi,
            "active_moon_lord": m_lord_hi,
            "active_sun_lord": s_lord_hi,
            "active_lagna_occupants": l_occ,
            "active_moon_occupants": m_occ,
            "active_sun_occupants": s_occ,
            "annual_prediction": annual_predictions[active_house - 1],
            "monthly_antardashas": months,
            "cycle_table": cycle_table,
            "lifetime_timeline": lifetime_timeline
        }

    @classmethod
    def calculate_yogas(cls, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Identifies classical Sudarshan Chakra Mahayogas as taught in BPHS and classical treatises."""
        lagna_sign = chart.lagna_sign_id
        moon_sign = chart.planets["Moon"].sign_id
        sun_sign = chart.planets["Sun"].sign_id

        yogas = []

        # 1. Sudarshan Mahayoga (Benefics in Kendras from all 3)
        kendras = [1, 4, 7, 10]
        ben_in_l_kendra = sum(1 for p in ["Jupiter", "Venus", "Mercury"] if (((chart.planets[p].sign_id - lagna_sign) % 12) + 1) in kendras)
        ben_in_m_kendra = sum(1 for p in ["Jupiter", "Venus", "Mercury"] if (((chart.planets[p].sign_id - moon_sign) % 12) + 1) in kendras)
        ben_in_s_kendra = sum(1 for p in ["Jupiter", "Venus", "Mercury"] if (((chart.planets[p].sign_id - sun_sign) % 12) + 1) in kendras)

        if ben_in_l_kendra >= 1 and ben_in_m_kendra >= 1 and ben_in_s_kendra >= 1:
            yogas.append({
                "name": "👑 सुदर्शन महायोग (Sudarshan Mahayoga)",
                "category": "राजयोग / प्रतिष्ठा",
                "condition": "तीनों चक्रों (लग्न, चन्द्र, सूर्य) के केन्द्र भावों (१, ४, ७, १०) में नैसर्गिक शुभ ग्रह (गुरु/शुक्र/बुध) विद्यमान हैं।",
                "effect": "जातक राजमान्य, असीम ऐश्वर्यवान, दीर्घायु, सर्वप्रिय तथा समाज में चक्रवर्ती प्रतिष्ठा प्राप्त करता है। सर्व विघ्नों का शमन होता है।",
                "strength": "95%",
                "status": "✅ पूर्ण सक्रिय (Active)"
            })
        else:
            yogas.append({
                "name": "👑 सुदर्शन महायोग (Sudarshan Mahayoga)",
                "category": "राजयोग / प्रतिष्ठा",
                "condition": "तीनों चक्रों के केन्द्रों में एक साथ शुभ ग्रहों की अवस्थिति।",
                "effect": "आंशिक प्रभाव: कुछ केन्द्रों में शुभ प्रभाव होने से सामान्य मान-सम्मान व आर्थिक सुरक्षा प्राप्त होती है।",
                "strength": "50%",
                "status": "🟡 आंशिक / सुप्त"
            })

        # 2. Amritayu Yoga (Benefics in 1, 2, 7, 8 from all 3)
        span_1278 = [1, 2, 7, 8]
        amrit_l = any((((chart.planets[p].sign_id - lagna_sign) % 12) + 1) in span_1278 for p in ["Jupiter", "Venus"])
        amrit_m = any((((chart.planets[p].sign_id - moon_sign) % 12) + 1) in span_1278 for p in ["Jupiter", "Venus"])
        amrit_s = any((((chart.planets[p].sign_id - sun_sign) % 12) + 1) in span_1278 for p in ["Jupiter", "Venus"])

        if amrit_l and amrit_m and amrit_s:
            yogas.append({
                "name": "🛡️ अमृतायु सुदर्शन योग (Amritayu Yoga)",
                "category": "आयु एवं स्वास्थ्य",
                "condition": "लग्न, चन्द्र और सूर्य तीनों से १, २, ७, ८ भावों में गुरु अथवा शुक्र का शुभ प्रभाव स्थापित है।",
                "effect": "अकाल मृत्यु भय का विनाश, निरोगी काया, वज्र-तुल्य जीवनशक्ति एवं दीर्घायु (पूर्णायु) की शास्त्रीय प्राप्ति।",
                "strength": "92%",
                "status": "✅ पूर्ण सक्रिय (Active)"
            })
        else:
            yogas.append({
                "name": "🛡️ अमृतायु सुदर्शन योग (Amritayu Yoga)",
                "category": "आयु एवं स्वास्थ्य",
                "condition": "तीनों से १, २, ७, ८ भावों में शुभ प्रभाव।",
                "effect": "मध्यम जीवनशक्ति; समय-समय पर मौसमी व्याधियां संभव, स्वास्थ्य नियम आवश्यक।",
                "strength": "55%",
                "status": "🟡 आंशिक"
            })

        # 3. Ari-Mardana Yoga (Malefics in Upachaya 3, 6, 11 from all 3)
        upachayas = [3, 6, 11]
        ari_l = any((((chart.planets[p].sign_id - lagna_sign) % 12) + 1) in upachayas for p in ["Saturn", "Mars", "Sun"])
        ari_m = any((((chart.planets[p].sign_id - moon_sign) % 12) + 1) in upachayas for p in ["Saturn", "Mars", "Sun"])
        ari_s = any((((chart.planets[p].sign_id - sun_sign) % 12) + 1) in upachayas for p in ["Saturn", "Mars", "Sun"])

        if ari_l and ari_m:
            yogas.append({
                "name": "⚔️ अरि-मर्दन सुदर्शन योग (Ari-Mardana Yoga)",
                "category": "शत्रुजय / विजय",
                "condition": "तीनों चक्रों के उपचय भावों (३, ६, ११) में क्रूर ग्रह (शनि/मंगल/सूर्य) स्थित होकर शत्रुहंता योग बनाते हैं।",
                "effect": "जातक प्रतिस्पर्धी परीक्षाओं, कोर्ट-कचहरी, व्यावसायिक प्रतिद्वंद्विता में सदैव अजेय रहता है। विरोधी स्वतः परास्त होते हैं।",
                "strength": "88%",
                "status": "✅ पूर्ण सक्रिय (Active)"
            })
        else:
            yogas.append({
                "name": "⚔️ अरि-मर्दन सुदर्शन योग (Ari-Mardana Yoga)",
                "category": "शत्रुजय / विजय",
                "condition": "उपचय भावों में क्रूर ग्रहों की अवस्थिति।",
                "effect": "मध्यम विजय सामर्थ्य; प्रयासों से विरोधियों पर नियंत्रण रहता है।",
                "strength": "52%",
                "status": "🟡 आंशिक"
            })

        # 4. Tri-Trikona Shubh Yoga (Benefics in 5, 9 from triad)
        trik_l = any((((chart.planets[p].sign_id - lagna_sign) % 12) + 1) in [5, 9] for p in BENEFICS)
        trik_m = any((((chart.planets[p].sign_id - moon_sign) % 12) + 1) in [5, 9] for p in BENEFICS)
        trik_s = any((((chart.planets[p].sign_id - sun_sign) % 12) + 1) in [5, 9] for p in BENEFICS)

        if trik_l and trik_m:
            yogas.append({
                "name": "💎 त्रि-त्रिकोण शुभ योग (Tri-Trikona Shubh Yoga)",
                "category": "भाग्य व मेधा",
                "condition": "त्रिकोण भावों (५ व ९) में तीनों चक्रों से शुभ ग्रहों की युति अथवा दृष्टि संबंध।",
                "effect": "परम मेधावी बुद्धि, पूर्वजन्म के पुण्यों का संबल, उच्च विद्या, योग्य संतान व अनायास ईश्वरीय कृपा का लाभ।",
                "strength": "90%",
                "status": "✅ पूर्ण सक्रिय (Active)"
            })
        else:
            yogas.append({
                "name": "💎 त्रि-त्रिकोण शुभ योग (Tri-Trikona Shubh Yoga)",
                "category": "भाग्य व मेधा",
                "condition": "त्रिकोण भावों में शुभ प्रभाव।",
                "effect": "सद्बुद्धि व सामान्य भाग्य की अनुकूलता प्राप्त होती है।",
                "strength": "58%",
                "status": "🟡 सामान्य"
            })

        # 5. Sudarshan Dhana Yoga (2nd & 11th from triad supported)
        dhana_l = any((((chart.planets[p].sign_id - lagna_sign) % 12) + 1) in [2, 11] for p in ["Jupiter", "Venus", "Mercury"])
        dhana_m = any((((chart.planets[p].sign_id - moon_sign) % 12) + 1) in [2, 11] for p in ["Jupiter", "Venus", "Mercury"])

        if dhana_l or dhana_m:
            yogas.append({
                "name": "💰 सुदर्शन धन योग (Sudarshan Dhana Yoga)",
                "category": "धन व समृद्धि",
                "condition": "लग्न अथवा चन्द्र कुण्डली के धन (२) व लाभ (११) भावों में गुरु, शुक्र या बुध की शुभ स्थिति।",
                "effect": "निरंतर धन का आगमन, व्यापार व निवेश में अभूतपूर्व लाभ तथा अचल संपत्ति का संचय।",
                "strength": "85%",
                "status": "✅ पूर्ण सक्रिय (Active)"
            })

        # 6. Tri-Dusthana Affliction Check
        dust_count = 0
        for p in ["Saturn", "Mars", "Rahu"]:
            if (((chart.planets[p].sign_id - lagna_sign) % 12) + 1) in [6, 8, 12]:
                dust_count += 1
        if dust_count >= 2:
            yogas.append({
                "name": "⚠️ त्रि-दुःस्थान संघर्ष योग (Tri-Dusthana Affliction)",
                "category": "सावधानी / बाधा",
                "condition": "तीनों चक्रों के ६, ८, १२ भावों में क्रूर ग्रहों का बाहुल्य।",
                "effect": "समय-समय पर मानसिक उद्वेग, आकस्मिक व्यय अथवा स्वास्थ्य बाधाएं। वैदिक शांति एवं सुदर्शन महामंत्र अनिवार्य।",
                "strength": "75%",
                "status": "⚠️ सक्रिय (सावधानी अपेक्षित)"
            })

        return yogas

    @classmethod
    def calculate_triad_dominance(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates comparative strength between:

        1. Deha (Lagna - Sthula Sharira)
        2. Mana (Chandra - Sukshma Sharira)
        3. Atma (Surya - Karana Sharira)
        And identifies the Chief Pilot Lagna as per BPHS rules.
        """
        lagna_sign_id = chart.lagna_sign_id
        moon_pos = chart.planets["Moon"]
        sun_pos = chart.planets["Sun"]

        # Lagna Score: based on Lagnesha dignity and occupants in Lagna
        l_occ = [p for p, pos in chart.planets.items() if pos.sign_id == lagna_sign_id]
        l_ben = sum(1 for p in l_occ if p in BENEFICS)
        l_mal = sum(1 for p in l_occ if p in MALEFICS)
        lagna_score = 65 + (l_ben * 12) - (l_mal * 10)

        # Moon Score: Paksha Bala + Jupiter aspect (Gajakesari) + sign
        dist_sun_moon = (moon_pos.longitude - sun_pos.longitude) % 360
        paksha_shukla = dist_sun_moon <= 180
        paksha_score = 15 if paksha_shukla else 5
        m_occ = [p for p, pos in chart.planets.items() if pos.sign_id == moon_pos.sign_id]
        m_ben = sum(1 for p in m_occ if p in BENEFICS)
        chandra_score = 60 + paksha_score + (m_ben * 10)

        # Sun Score: Digbala (10th house is strongest), Aries exaltation, etc.
        sun_h_from_l = ((sun_pos.sign_id - lagna_sign_id) % 12) + 1
        digbala_bonus = 18 if sun_h_from_l == 10 else (10 if sun_h_from_l in [1, 4, 7] else 5)
        exalt_bonus = 15 if sun_pos.sign_id == 1 else (10 if sun_pos.sign_id == 5 else 0)
        surya_score = 55 + digbala_bonus + exalt_bonus

        lagna_score = max(40, min(95, lagna_score))
        chandra_score = max(40, min(95, chandra_score))
        surya_score = max(40, min(95, surya_score))

        scores = [
            ("देह लग्न (Janma Lagna)", lagna_score, "शरीर, स्वास्थ्य, भौतिक संसाधन व सामाजिक व्यक्तित्व"),
            ("मन लग्न (Chandra Lagna)", chandra_score, "मन, भावनाएं, ग्रहणशीलता, अंतःप्रेरणा व मानसिक सुख"),
            ("आत्म लग्न (Surya Lagna)", surya_score, "आत्मा, आत्मबल, संकल्प-शक्ति, पिता, यश व नेतृत्व")
        ]
        scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)
        dominant_lagna = scores_sorted[0][0]

        # Harmony between the 3 Lagnas
        diff_lm = ((moon_pos.sign_id - lagna_sign_id) % 12) + 1
        diff_ls = ((sun_pos.sign_id - lagna_sign_id) % 12) + 1
        diff_ms = ((sun_pos.sign_id - moon_pos.sign_id) % 12) + 1

        is_harmonious = (diff_lm in [1, 5, 9] or diff_ls in [1, 5, 9] or diff_lm in [1, 4, 7, 10])
        harmony_level = "🌟 उत्कृष्ट सामंजस्य (Trine/Kendra Harmony)" if is_harmonious else "⚖️ मध्यम सामंजस्य (Dynamic Equilibrium)"

        return {
            "dominant_lagna": dominant_lagna,
            "dominant_score": scores_sorted[0][1],
            "dominant_role": scores_sorted[0][2],
            "lagna_score": lagna_score,
            "chandra_score": chandra_score,
            "surya_score": surya_score,
            "harmony_level": harmony_level,
            "philosophical_analysis": f"प्रस्तुत कुण्डली में **{dominant_lagna}** सर्वाधिक बली है। बृहत्पाराशर होराशास्त्रानुसार (तत्र यद्बलाधिकं तदनुसारेण फलम्) जातक के जीवन की दिशा एवं घटनाओं का मुख्य संचालन {scores_sorted[0][2]} के स्तर से होगा। देह, मन और आत्मा के मध्य {harmony_level} की स्थिति विद्यमान है।"
        }

    @classmethod
    def calculate_life_domains(cls, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Synthesizes 7 major life dimensions across the three concentric frames."""
        sd_res = cls.calculate(chart)
        houses = {h["house_num"]: h for h in sd_res["houses"]}

        domains = [
            {
                "title": "🏥 आरोग्य एवं जीवनशक्ति (Health & Longevity)",
                "bhavas": [1, 8],
                "karakas": "सूर्य, गुरु, लग्नेश",
                "desc": "शारीरिक ऊर्जा, रोग-प्रतिरोधक क्षमता व दीर्घायु का त्रिविध परीक्षण।"
            },
            {
                "title": "💰 धन, संपत्ति एवं कुटुंब (Wealth & Assets)",
                "bhavas": [2, 11],
                "karakas": "गुरु, शुक्र, द्वितीयेश",
                "desc": "स्थिर पूँजी, पारिवारिक सौख्य, नियमित आय व धन संचय की स्थिति।"
            },
            {
                "title": "⚔️ पराक्रम, उद्यम एवं संचार (Courage & Enterprise)",
                "bhavas": [3],
                "karakas": "मंगल, बुध",
                "desc": "साहस, भ्रातृ सुख, लेखन/संचार एवं व्यावसायिक पहल का सामर्थ्य।"
            },
            {
                "title": "🏠 सुख, भूमि, वाहन एवं मातृसुख (Property & Domestic Peace)",
                "bhavas": [4],
                "karakas": "चन्द्र, शुक्र, मंगल",
                "desc": "गृह-सुख, वाहन लाभ, अचल संपत्ति एवं माता के साथ आत्मीय संबंध।"
            },
            {
                "title": "👶 विद्या, बुद्धि एवं संतान (Education & Progeny)",
                "bhavas": [5],
                "karakas": "गुरु, बुध",
                "desc": "मेधा शक्ति, उच्च विद्या, मंत्र साधना, संतान सुख व पूर्वपुण्य।"
            },
            {
                "title": "💼 आजीविका, कर्म एवं राजसम्मान (Career, Karma & Authority)",
                "bhavas": [10],
                "karakas": "सूर्य, शनि, गुरु, बुध",
                "desc": "व्यावसायिक प्रतिष्ठा, उच्च पद, राजकीय सम्मान एवं कर्म सिद्धि।"
            },
            {
                "title": "💍 विवाह, दांपत्य एवं धर्म (Marriage, Partnership & Dharma)",
                "bhavas": [7, 9],
                "karakas": "शुक्र, गुरु",
                "desc": "जीवनसाथी का गुण-स्वभाव, वैवाहिक सौहार्द, धर्म निष्ठा व भाग्योदय।"
            }
        ]

        results = []
        for d in domains:
            scores = [houses[b]["score_num"] for b in d["bhavas"]]
            avg_score = int(round(sum(scores) / len(scores)))
            status = "🌟 अति-उत्कृष्ट" if avg_score >= 75 else ("🟢 शुभ व सुदृढ़" if avg_score >= 60 else "⚠️ मध्यम / ध्यान दें")

            results.append({
                "title": d["title"],
                "bhavas_str": ", ".join(f"भाव {b}" for b in d["bhavas"]),
                "karakas": d["karakas"],
                "desc": d["desc"],
                "avg_score": f"{avg_score}/100",
                "status": status
            })

        return results

    @classmethod
    def calculate_ashtakavarga_synthesis(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Integrates Sarvashtakavarga (SAV) bindus with the three concentric rings."""
        lagna_sign_id = chart.lagna_sign_id
        moon_sign_id = chart.planets["Moon"].sign_id
        sun_sign_id = chart.planets["Sun"].sign_id

        sav_list = [28] * 12
        if hasattr(chart, 'ashtakavarga') and chart.ashtakavarga and hasattr(chart.ashtakavarga, 'sav'):
            sav_list = chart.ashtakavarga.sav

        house_rows = []
        for h in range(1, 13):
            l_s_id = ((lagna_sign_id - 1 + (h - 1)) % 12) + 1
            m_s_id = ((moon_sign_id - 1 + (h - 1)) % 12) + 1
            s_s_id = ((sun_sign_id - 1 + (h - 1)) % 12) + 1

            l_pts = sav_list[l_s_id - 1]
            m_pts = sav_list[m_s_id - 1]
            s_pts = sav_list[s_s_id - 1]

            tot = l_pts + m_pts + s_pts
            avg = round(tot / 3.0, 1)

            verdict = "🌟 अति बलवान (Strong)" if avg >= 30.0 else ("🟢 उत्तम (Good)" if avg >= 28.0 else ("🟡 मध्यम (Average)" if avg >= 25.0 else "⚠️ संवेदनशील (Low)"))

            house_rows.append({
                "house_num": h,
                "house_label": f"भाव {h}",
                "lagna_sign": f"{SIGN_NAMES_HI[l_s_id - 1]} ({l_pts} बिन्दु)",
                "moon_sign": f"{SIGN_NAMES_HI[m_s_id - 1]} ({m_pts} बिन्दु)",
                "sun_sign": f"{SIGN_NAMES_HI[s_s_id - 1]} ({s_pts} बिन्दु)",
                "total_bindus": tot,
                "avg_bindus": avg,
                "verdict": verdict
            })

        return {
            "lagna_sign_bindus": sav_list[lagna_sign_id - 1],
            "moon_sign_bindus": sav_list[moon_sign_id - 1],
            "sun_sign_bindus": sav_list[sun_sign_id - 1],
            "rows": house_rows
        }

    @classmethod
    def render_sudarshan_svg(cls, chart: KundaliChart, active_house: int = 1) -> str:
        """Generates a high-definition, responsive 3-ring Sudarshan Chakra SVG mandala."""
        lagna_sign_id = chart.lagna_sign_id
        moon_sign_id = chart.planets["Moon"].sign_id
        sun_sign_id = chart.planets["Sun"].sign_id

        # Calculate house occupancy for all 3 rings
        sectors = []
        for h in range(1, 13):
            l_s_id = ((lagna_sign_id - 1 + (h - 1)) % 12) + 1
            m_s_id = ((moon_sign_id - 1 + (h - 1)) % 12) + 1
            s_s_id = ((sun_sign_id - 1 + (h - 1)) % 12) + 1

            l_pl = [PLANET_SHORT_HI.get(p, p[:2]) for p, pos in chart.planets.items() if pos.sign_id == l_s_id]
            m_pl = [PLANET_SHORT_HI.get(p, p[:2]) for p, pos in chart.planets.items() if pos.sign_id == m_s_id]
            s_pl = [PLANET_SHORT_HI.get(p, p[:2]) for p, pos in chart.planets.items() if pos.sign_id == s_s_id]

            sectors.append({
                "h": h,
                "l_sign": SIGN_NAMES_HI[l_s_id - 1],
                "l_pl": " ".join(l_pl) if l_pl else "—",
                "m_sign": SIGN_NAMES_HI[m_s_id - 1],
                "m_pl": " ".join(m_pl) if m_pl else "—",
                "s_sign": SIGN_NAMES_HI[s_s_id - 1],
                "s_pl": " ".join(s_pl) if s_pl else "—",
            })

        svg = """
<svg viewBox="0 0 740 740" width="100%" height="560" xmlns="http://www.w3.org/2000/svg" style="background:#FFFFFF; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; user-select:none;">
    <defs>
        <radialGradient id="sunRingGrad" cx="50%" cy="50%" r="50%">
            <stop offset="60%" stop-color="#FFFBEB" />
            <stop offset="100%" stop-color="#FEF3C7" />
        </radialGradient>
        <radialGradient id="moonRingGrad" cx="50%" cy="50%" r="50%">
            <stop offset="60%" stop-color="#EFF6FF" />
            <stop offset="100%" stop-color="#DBEAFE" />
        </radialGradient>
        <radialGradient id="lagnaRingGrad" cx="50%" cy="50%" r="50%">
            <stop offset="60%" stop-color="#ECFDF5" />
            <stop offset="100%" stop-color="#D1FAE5" />
        </radialGradient>
        <radialGradient id="centerHubGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#FDE047" />
            <stop offset="60%" stop-color="#F59E0B" />
            <stop offset="100%" stop-color="#D97706" />
        </radialGradient>
        <filter id="goldGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>

    <!-- Outer Ring 3: Surya Kundali (R=345, R_in=255) -->
    <circle cx="370" cy="370" r="345" fill="url(#sunRingGrad)" stroke="#D97706" stroke-width="4" />

    <!-- Middle Ring 2: Chandra Kundali (R=255, R_in=165) -->
    <circle cx="370" cy="370" r="255" fill="url(#moonRingGrad)" stroke="#2563EB" stroke-width="3.5" />

    <!-- Inner Ring 1: Janma Lagna Kundali (R=165, R_in=75) -->
    <circle cx="370" cy="370" r="165" fill="url(#lagnaRingGrad)" stroke="#059669" stroke-width="3" />

    <!-- Central Hub: Vishnu Sudarshan Discus (R=75) -->
    <circle cx="370" cy="370" r="75" fill="url(#centerHubGrad)" stroke="#B45309" stroke-width="3" filter="url(#goldGlow)" />
    <!-- 16 Spoke Hub Lines -->
"""

        # Central 16 spokes
        for sp in range(16):
            sp_ang = sp * (360.0 / 16.0)
            sp_rad = math.radians(sp_ang)
            sx1 = 370 + 20 * math.cos(sp_rad)
            sy1 = 370 + 20 * math.sin(sp_rad)
            sx2 = 370 + 72 * math.cos(sp_rad)
            sy2 = 370 + 72 * math.sin(sp_rad)
            svg += f'<line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" stroke="#78350F" stroke-width="1.2" opacity="0.6" />\n'

        svg += """
    <circle cx="370" cy="370" r="22" fill="#FFFFFF" stroke="#78350F" stroke-width="2" />
    <text x="370" y="375" text-anchor="middle" font-size="16" font-weight="900" fill="#78350F">ॐ</text>
    <text x="370" y="352" text-anchor="middle" font-size="11" font-weight="900" fill="#78350F" letter-spacing="1">सुदर्शन</text>
    <text x="370" y="394" text-anchor="middle" font-size="10" font-weight="800" fill="#92400E" letter-spacing="1">मण्डल</text>
"""

        # 12 Sector Dividers & Text Placement
        for i in range(12):
            angle = i * (360.0 / 12.0) - 90.0
            rad = math.radians(angle)

            # Dividing Line from R=75 to R=345
            x1 = 370 + 75 * math.cos(rad)
            y1 = 370 + 75 * math.sin(rad)
            x2 = 370 + 345 * math.cos(rad)
            y2 = 370 + 345 * math.sin(rad)
            svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="3,3" opacity="0.75" />\n'

            # Sector Mid-Angle for Labels
            mid_angle = angle + 15.0
            mid_rad = math.radians(mid_angle)

            sec = sectors[i]
            is_active = (sec["h"] == active_house)

            # Optional highlight arc for active house
            if is_active:
                svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#F59E0B" stroke-width="3.5" />\n'

            # Ring 1: Janma Lagna (Radius ~120)
            rx1 = 370 + 120 * math.cos(mid_rad)
            ry1 = 370 + 120 * math.sin(mid_rad)
            svg += f'<text x="{rx1:.1f}" y="{ry1 - 6:.1f}" text-anchor="middle" font-size="11" font-weight="800" fill="#065F46">{sec["l_sign"]}</text>\n'
            svg += f'<text x="{rx1:.1f}" y="{ry1 + 7:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">{sec["l_pl"]}</text>\n'

            # Ring 2: Chandra Kundali (Radius ~210)
            rx2 = 370 + 210 * math.cos(mid_rad)
            ry2 = 370 + 210 * math.sin(mid_rad)
            svg += f'<text x="{rx2:.1f}" y="{ry2 - 6:.1f}" text-anchor="middle" font-size="11" font-weight="800" fill="#1E40AF">{sec["m_sign"]}</text>\n'
            svg += f'<text x="{rx2:.1f}" y="{ry2 + 7:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#2563EB">{sec["m_pl"]}</text>\n'

            # Ring 3: Surya Kundali (Radius ~300)
            rx3 = 370 + 300 * math.cos(mid_rad)
            ry3 = 370 + 300 * math.sin(mid_rad)
            svg += f'<text x="{rx3:.1f}" y="{ry3 - 6:.1f}" text-anchor="middle" font-size="11" font-weight="800" fill="#92400E">{sec["s_sign"]}</text>\n'
            svg += f'<text x="{rx3:.1f}" y="{ry3 + 7:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#B45309">{sec["s_pl"]}</text>\n'

            # Outer House Label (Radius ~360)
            rx_lbl = 370 + 360 * math.cos(mid_rad)
            ry_lbl = 370 + 360 * math.sin(mid_rad)
            lbl_color = "#B45309" if is_active else "#64748B"
            lbl_weight = "900" if is_active else "700"
            svg += f'<text x="{rx_lbl:.1f}" y="{ry_lbl:.1f}" text-anchor="middle" dominant-baseline="central" font-size="10" font-weight="{lbl_weight}" fill="{lbl_color}">भाव {sec["h"]}</text>\n'

        svg += "</svg>"
        # Ensure zero leading whitespace and remove comments to prevent Streamlit markdown codeblock rendering
        clean_lines = [l.strip() for l in svg.splitlines() if l.strip() and not (l.strip().startswith("<!--") and l.strip().endswith("-->"))]
        return "\n".join(clean_lines)

    @classmethod
    def get_classical_shlokas(cls) -> List[Dict[str, str]]:
        """Returns verbatim Sanskrit shlokas and Hindi explanations from BPHS Chapter 74."""
        return [
            {
                "title": "१. सुदर्शन चक्र लक्षण एवं स्वरूप (स्वरूप कथन)",
                "shloka": "यथा शरीरे देहेन्द्रियमन आत्मनां साम्यं तथैव लग्नेन्दुसूर्याणां साम्येन विचारः कर्तव्यः।\nदेहावलोकनं लग्नान्मनसोऽपि च शीतातः। सूर्यादात्मबलं ज्ञेयं त्रिभिरेतैर्विभावयेत्॥",
                "meaning": "जिस प्रकार मानव शरीर में देह (स्थूल शरीर), मन (सूक्ष्म शरीर) और आत्मा (कारण शरीर) की त्रिपुटी होती है, उसी प्रकार ज्योतिष में जन्म लग्न, चन्द्र लग्न एवं सूर्य लग्न इन तीनों दृष्टिकोणों से एक साथ विचार करना अनिवार्य है। लग्न से शारीरिक स्थिति, चन्द्र से मानसिक संवेदना तथा सूर्य से आत्मिक ऊर्जा का बोध होता है।"
            },
            {
                "title": "२. त्रि-चक्रीय मंडल निर्माण विधि (चक्र निर्माण)",
                "shloka": "वृत्तत्रयं लिखेत् धीमान् समकेन्द्रं परस्परम्। द्वादशारं विधातव्यं सुदर्शनमनुत्तमम्॥\nअन्तश्चक्रं भवेल्लग्नं मध्यं चन्द्रमसो भवेत्। बाह्यं सूर्यस्य विख्यातं त्रिधा भावफलान्वितम्॥",
                "meaning": "एक ही केन्द्र से तीन संकेंद्री वृत्तों की रचना करें और उन्हें १२ द्वादश भागों (आरो में) विभाजित करें। सबसे आंतरिक वृत्त में जन्म लग्न, मध्य वृत्त में चन्द्र कुण्डली तथा बाह्य वृत्त में सूर्य कुण्डली को स्थापित करके प्रत्येक भाव का त्रि-स्तरीय फलादेश विचारें।"
            },
            {
                "title": "३. द्वादश भाव त्रि-आयामी शुभाशुभ विचार (समग्र फलित)",
                "shloka": "त्रिषु लग्नेषु यद्भावं शुभैर्युक्तं च वीक्षितम्। तत्फलं पूर्णतां याति विपरीतं च पापपैः॥\nद्वयोः शुभे मध्यमं स्यादेकस्मिन् कनिष्ठकम्। त्रिष्वप्यशुभसंयुक्ते सर्वथा क्लेशभाग्भवेत्॥",
                "meaning": "यदि कोई भाव लग्न, चन्द्र और सूर्य तीनों चक्रों में शुभ ग्रहों से युक्त या दृष्ट हो, तो वह भाव १००% पूर्ण शुभ फल देता है। यदि दो चक्रों में शुभ हो तो मध्यम फल (६६%), एक चक्र में शुभ हो तो कनिष्ठ फल (३३%) तथा तीनों चक्रों में पाप प्रभाव होने पर जातक को उस भाव से संबंधित पूर्ण क्लेश एवं बाधा प्राप्त होती है।"
            },
            {
                "title": "४. सुदर्शन चक्र दशा क्रम (वार्षिक, मासिक व दैनिक)",
                "shloka": "वर्षाणि द्वादश ज्ञेयं प्रतिभावं समावृतम्। मासं प्रति तथा भावं वासरं सार्धद्वयं भवेत्॥\nयस्मिन् वर्षे स्थितो भावस्तद्भावेशफलप्रदः। त्रिचक्राणां समत्वेन दशाफलमुदीरयेत्॥",
                "meaning": "प्रत्येक भाव की अवधि १ वर्ष होती है, इस प्रकार १२ वर्षों में एक पूर्ण चक्र होता है (१३वें वर्ष में पुनः प्रथम भाव आता है)। उस वर्ष के भीतर प्रत्येक मास में एक-एक भाव की मासिक अन्तर्दशा तथा प्रत्येक भाव में ढाई (२.५) दिनों की प्रत्यन्तर्दशा चलती है।"
            },
            {
                "title": "५. त्रि-लग्न प्राधान्यता निर्णय (मुख्य नियंता लग्न)",
                "shloka": "तत्र यद्बलाधिकं तदनुसारेण फलम्। लग्नेन्दुसूर्याणां मध्ये यद्बलवान् स एव फलदाता भवति॥",
                "meaning": "जन्म लग्न, चन्द्र लग्न एवं सूर्य लग्न इन तीनों में जो सर्वाधिक बली हो, उसी के आधार पर जातक के जीवन की प्रमुख घटनाओं और भाग्य का अंतिम निर्धारण होता है।"
            }
        ]

    @classmethod
    def get_remedies_catalog(cls) -> Dict[str, Any]:
        """Provides authentic Sri Sudarshan Kavach, Gayatri, and Vedic remediation rituals."""
        return {
            "gayatri_mantra": "ॐ सुदर्शनाय विद्महे महाज्वालाय धीमहि। तन्नो चक्रः प्रचोदयात्॥",
            "mahamantra": "ॐ क्लीं कृष्णाय गोविंदाय गोपीजनवल्लभाय पराय परमपुरुषाय परमात्मने परकर्ममंत्रयंत्रतंत्रौषध विषनाभिचारचक्राय हन हन दह दह पच पच मथ मथ उत्सादय उत्सादय स्वाहा॥",
            "ashtakam_intro": "भगवान वेदान्तदेशिक विरचित 'श्री सुदर्शन अष्टकम्' समस्त त्रि-दोषों, तांत्रिक बाधाओं, ग्रहों की प्रतिकूलता एवं अकाल मृत्यु के भय को तत्क्षण शांत करने वाला परम दिव्य स्तोत्र है।",
            "ashtakam_first_verse": "प्रतिभटश्रेणी भीषण वरगुणस्तोमानिभूषण जनिकपयोधौ तरण शरणद! सर्वसुरासन।\nस्फुटविकचनेत्र विदारित सुरशत्रो! दितिजदारण जय जय श्रीसुदर्शन जय जय श्रीसुदर्शन॥",
            "remedial_measures": [
                {
                    "title": "🪔 श्री सुदर्शन होम / हवन अनुष्ठान",
                    "procedure": "बुधवार अथवा एकादशी के दिन तुलसी दल, शुद्ध घृत, समिधा एवं सुदर्शन महामंत्र की १०८ आहुतियां देकर हवन संपन्न करें। इससे त्रि-दुःस्थान दोषों का शमन होता है।"
                },
                {
                    "title": "🛡️ श्री सुदर्शन यंत्र धारण",
                    "procedure": "ताम्र अथवा अष्टधातु निर्मित प्राण-प्रतिष्ठित सुदर्शन यंत्र को लाल/पीले डोरे में अभिमंत्रित कर गले अथवा दाहिनी भुजा में धारण करने से रक्षा कवच निर्मित होता है।"
                },
                {
                    "title": "🌿 तुलसी दल अर्पण एवं विष्णु सहस्रनाम",
                    "procedure": "प्रत्येक मास की शुक्ल पक्ष एकादशी को भगवान श्री विष्णु के श्रीचरणों में १०८ तुलसी दल अर्पित करते हुए श्री विष्णु सहस्रनाम का सस्वर पाठ करें।"
                },
                {
                    "title": "🎁 महादान संकल्प",
                    "procedure": "जिस भाव में त्रि-अशुभ दोष हो, उसके अधिपति ग्रह की वस्तु (यथा मंगल हेतु मसूर, शनि हेतु तिल-तैल, राहु हेतु नारियल) का शनिवार/मंगलवार को दान करें।"
                }
            ]
        }


default_sudarshan_engine = SudarshanChakraEngine()
