"""
Prashna Kundali (Horary Astrology) Engine for JyotishOS.
Generates query-time charts calculated at the exact moment and location of the query,
following Prashna Marga, Tajika Neelakanthi, and Kerala astrological principles.
Provides 23 query categories, sub-questions, 12-house role maps with icons, and Tajika Yogas.
"""

from datetime import datetime, date, time
from typing import Dict, Any, List, Optional
from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..core.constants import KENDRA_HOUSES, TRIKONA_HOUSES, SIGN_LORDS


PRASHNA_CATEGORIES = [
    {"Id": 1, "Name": "Health", "Name_Hi": "स्वास्थ्य एवं रोग मुक्ति", "house": 1, "karyesh_default": "Sun", "icon": "🩺"},
    {"Id": 2, "Name": "Marriage", "Name_Hi": "विवाह एवं वैवाहिक जीवन", "house": 7, "karyesh_default": "Venus", "icon": "💍"},
    {"Id": 3, "Name": "Relationship", "Name_Hi": "प्रेम सम्बंध एवं सामंजस्य", "house": 7, "karyesh_default": "Venus", "icon": "❤️"},
    {"Id": 4, "Name": "Child", "Name_Hi": "संतान प्राप्ति एवं सुख", "house": 5, "karyesh_default": "Jupiter", "icon": "👶"},
    {"Id": 5, "Name": "Wealth", "Name_Hi": "धन लाभ एवं बैंक बैलेंस", "house": 2, "karyesh_default": "Jupiter", "icon": "💰"},
    {"Id": 6, "Name": "Career", "Name_Hi": "करियर, पद एवं प्रतिष्ठा", "house": 10, "karyesh_default": "Saturn", "icon": "👔"},
    {"Id": 7, "Name": "Job", "Name_Hi": "नई नौकरी एवं पदोन्नति", "house": 6, "karyesh_default": "Saturn", "icon": "💼"},
    {"Id": 8, "Name": "Business", "Name_Hi": "व्यापार, साझेदारी एवं विस्तार", "house": 7, "karyesh_default": "Mercury", "icon": "🏢"},
    {"Id": 9, "Name": "Property", "Name_Hi": "भूमि, भवन एवं अचल संपत्ति", "house": 4, "karyesh_default": "Mars", "icon": "🏠"},
    {"Id": 10, "Name": "Investment", "Name_Hi": "शेयर बाज़ार, निवेश एवं मुनाफा", "house": 11, "karyesh_default": "Jupiter", "icon": "📈"},
    {"Id": 11, "Name": "Litigation / Court", "Name_Hi": "न्यायालय, मुक़दमा एवं विवाद विजय", "house": 6, "karyesh_default": "Mars", "icon": "⚖️"},
    {"Id": 12, "Name": "Foreign Travel", "Name_Hi": "विदेश यात्रा, वीज़ा एवं परदेस वास", "house": 9, "karyesh_default": "Jupiter", "icon": "✈️"},
    {"Id": 13, "Name": "Education / Exam", "Name_Hi": "उच्च शिक्षा, परीक्षा एवं प्रतियोगिता", "house": 5, "karyesh_default": "Mercury", "icon": "🎓"},
    {"Id": 14, "Name": "Lost Item", "Name_Hi": "खोई वस्तु की प्राप्ति", "house": 2, "karyesh_default": "Moon", "icon": "🔍"},
    {"Id": 15, "Name": "Purchase Vehicle", "Name_Hi": "नया वाहन क्रय एवं सुख", "house": 4, "karyesh_default": "Venus", "icon": "🚗"},
    {"Id": 16, "Name": "Partnership", "Name_Hi": "व्यावसायिक साझेदारी एवं अनुबंध", "house": 7, "karyesh_default": "Mercury", "icon": "🤝"},
    {"Id": 17, "Name": "Debt / Loan", "Name_Hi": "ऋण मुक्ति एवं कर्ज़ निवारण", "house": 6, "karyesh_default": "Mars", "icon": "💳"},
    {"Id": 18, "Name": "Relocation / Transfer", "Name_Hi": "तबादला, स्थान परिवर्तन एवं प्रवास", "house": 3, "karyesh_default": "Moon", "icon": "🔄"},
    {"Id": 19, "Name": "Surgery / Diagnosis", "Name_Hi": "शल्य चिकित्सा (सर्जरी) एवं रोग निदान", "house": 8, "karyesh_default": "Mars", "icon": "🏥"},
    {"Id": 20, "Name": "Spiritual Initiation", "Name_Hi": "आध्यात्मिक साधना, दीक्षा एवं गुरु कृपा", "house": 9, "karyesh_default": "Jupiter", "icon": "🕉️"},
    {"Id": 21, "Name": "Construction / Vastu", "Name_Hi": "गृह निर्माण, नवीनीकरण एवं वास्तु", "house": 4, "karyesh_default": "Mars", "icon": "🏗️"},
    {"Id": 22, "Name": "Friends / Enemies", "Name_Hi": "मित्र सहयोग अथवा गुप्त शत्रु", "house": 11, "karyesh_default": "Mercury", "icon": "👥"},
    {"Id": 23, "Name": "General Prashna", "Name_Hi": "सामान्य एवं तात्कालिक प्रश्न", "house": 1, "karyesh_default": "Moon", "icon": "🔮"}
]

# Deeptamsha (Orb of influence in degrees for Tajika aspects)
TAJIKA_DEEPTAMSHA = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mars": 8.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0,
    "Rahu": 5.0,
    "Ketu": 5.0
}

# Average daily planetary motion (degrees/day)
PLANET_DAILY_MOTION = {
    "Moon": 13.176,
    "Mercury": 1.383,
    "Venus": 1.200,
    "Sun": 0.985,
    "Mars": 0.524,
    "Jupiter": 0.083,
    "Saturn": 0.033,
    "Rahu": -0.053,
    "Ketu": -0.053
}

PRASHNA_HOUSE_ROLES: Dict[str, Dict[int, Dict[str, Any]]] = {
    "Health": {
        1: {"text": "रोगी / प्रश्नकर्ता (Querent / Patient)", "icon": "🫵", "important": True},
        4: {"text": "चिकित्सा / औषधि (Treatment & Medicine)", "icon": "💉", "important": True},
        6: {"text": "रोग / लक्षण (Disease & Infection)", "icon": "🦠", "important": True},
        8: {"text": "जटिलता / कष्ट (Severity & Complications)", "icon": "⚠️", "important": True},
        11: {"text": "रोग मुक्ति / स्वास्थ्य लाभ (Recovery & Health)", "icon": "✨", "important": True}
    },
    "Marriage": {
        1: {"text": "वर/वधू (Querent)", "icon": "🫵", "important": True},
        2: {"text": "कुटुम्ब / परिवार (Family Acceptance)", "icon": "👨‍👩‍👧", "important": True},
        4: {"text": "घरेलू सुख / सामंजस्य (Domestic Bliss)", "icon": "🕊️", "important": True},
        7: {"text": "प्रस्तावित जीवनसाथी (Proposed Partner)", "icon": "💍", "important": True},
        11: {"text": "विवाह सम्पादन / फलसिद्धि (Marriage Vows & Fulfillment)", "icon": "🎉", "important": True}
    },
    "Relationship": {
        1: {"text": "प्रश्नकर्ता (Querent)", "icon": "🫵", "important": True},
        5: {"text": "प्रेम भावना / अनुराग (Love & Romance)", "icon": "💖", "important": True},
        7: {"text": "प्रेमी / प्रेमिका (Partner)", "icon": "❤️", "important": True},
        11: {"text": "स्थायित्व एवं स्वीकृति (Commitment & Joy)", "icon": "🌟", "important": True}
    },
    "Child": {
        1: {"text": "माता / पिता (Parents)", "icon": "🫵", "important": True},
        2: {"text": "कुल वृद्धि (Family Growth)", "icon": "👨‍👩‍👧", "important": True},
        5: {"text": "गर्भधारण एवं संतान सुख (Conception & Progeny)", "icon": "👶", "important": True},
        9: {"text": "पूर्वजन्म पुण्य / भाग्योदय (Purva Punya & Grace)", "icon": "🕉️", "important": True},
        11: {"text": "संतान प्राप्ति फल (Childbirth Fulfillment)", "icon": "🎉", "important": True}
    },
    "Job": {
        1: {"text": "अभ्यर्थी / प्रश्नकर्ता (Candidate / Querent)", "icon": "🫵", "important": True},
        6: {"text": "दैनिक सेवा / साक्षात्कार (Interview & Service)", "icon": "📋", "important": True},
        10: {"text": "उच्चाधिकारी / पद (Boss & Appointment)", "icon": "💼", "important": True},
        11: {"text": "वेतन / नियुक्ति पत्र (Offer Letter & Gains)", "icon": "💵", "important": True}
    },
    "Career": {
        1: {"text": "प्रश्नकर्ता की पहल (Querent's Action)", "icon": "🫵", "important": True},
        7: {"text": "ग्राहक / सहकर्मी (Clients & Associates)", "icon": "🤝", "important": False},
        10: {"text": "कार्यक्षेत्र में प्रतिष्ठा (Career Stature & Promotion)", "icon": "👔", "important": True},
        11: {"text": "उच्च लाभ एवं लक्ष्य प्राप्ति (High Profits & Growth)", "icon": "🚀", "important": True}
    },
    "Business": {
        1: {"text": "व्यवसायी / उद्यमी (Business Owner)", "icon": "🫵", "important": True},
        2: {"text": "पूंजी / तरलता (Liquid Capital)", "icon": "💰", "important": True},
        7: {"text": "साझेदार / ग्राहक बाज़ार (Partners & Market)", "icon": "🏢", "important": True},
        10: {"text": "व्यापार विस्तार (Enterprise Success)", "icon": "📈", "important": True},
        11: {"text": "शुद्ध लाभ एवं मुनाफा (Net Profits & Return)", "icon": "💎", "important": True}
    },
    "Property": {
        1: {"text": "क्रेता / विक्रेता (Buyer / Seller)", "icon": "🫵", "important": True},
        4: {"text": "भूमि / मकान / संपत्ति (Land & Building)", "icon": "🏠", "important": True},
        7: {"text": "दूसरा पक्ष / ब्रोकर (Other Party / Dealer)", "icon": "🤝", "important": True},
        11: {"text": "सौदा पक्का होना व लाभ (Deal Closure & Profit)", "icon": "🔑", "important": True}
    },
    "Wealth": {
        1: {"text": "प्रश्नकर्ता (Querent)", "icon": "🫵", "important": True},
        2: {"text": "संचित धन / बैंक खाता (Bank Balance & Assets)", "icon": "🏦", "important": True},
        9: {"text": "ईश्वरीय कृपा व भाग्य (Divine Fortune & Luck)", "icon": "🍀", "important": True},
        11: {"text": "आकस्मिक धन प्राप्ति (Direct Financial Gain)", "icon": "💰", "important": True}
    },
    "Investment": {
        1: {"text": "निवेशक (Investor)", "icon": "🫵", "important": True},
        5: {"text": "सट्टा / शेयर बाजार निर्णय (Speculation & Market Intellect)", "icon": "📊", "important": True},
        9: {"text": "भाग्य एवं दीर्घावधि लाभ (Long-term Fortune)", "icon": "🍀", "important": True},
        11: {"text": "उच्च रिटर्न / मुनाफा (High ROI & Dividend)", "icon": "📈", "important": True}
    },
    "Litigation / Court": {
        1: {"text": "वादी / प्रश्नकर्ता (Plaintiff / Querent)", "icon": "🫵", "important": True},
        6: {"text": "शत्रु पक्ष एवं मुक़दमा (Opposition & Case)", "icon": "⚖️", "important": True},
        7: {"text": "विरोधी दल (Opponent / Defendant)", "icon": "⚔️", "important": True},
        10: {"text": "न्यायाधीश / फैसला (Judge & Final Verdict)", "icon": "🏛️", "important": True},
        11: {"text": "विजय एवं न्याय प्राप्ति (Victory & Favorable Order)", "icon": "🏆", "important": True}
    },
    "Foreign Travel": {
        1: {"text": "यात्री / प्रश्नकर्ता (Traveler)", "icon": "🫵", "important": True},
        3: {"text": "दस्तावेज़ / वीज़ा आवेदन (Visa Application & Journey)", "icon": "📄", "important": True},
        9: {"text": "सुदूर यात्रा एवं उच्च उद्देश्य (Long Distance & Fortune)", "icon": "✈️", "important": True},
        12: {"text": "विदेश भूमि प्रवास (Foreign Land Stay)", "icon": "🌐", "important": True}
    },
    "Education / Exam": {
        1: {"text": "परीक्षार्थी (Student / Candidate)", "icon": "🫵", "important": True},
        4: {"text": "मूल विद्या एवं शिक्षण संस्थान (School / College)", "icon": "🏫", "important": True},
        5: {"text": "मेधा शक्ति एवं परीक्षा परिणाम (Intellect & Result)", "icon": "🎓", "important": True},
        9: {"text": "उच्च डिग्री एवं गुरु मार्गदर्शन (Degree & Mentor)", "icon": "📜", "important": True},
        11: {"text": "मेरिट सूची व सफलता (Merit Rank & Success)", "icon": "🥇", "important": True}
    },
    "Lost Item": {
        1: {"text": "स्वामी (Owner of Item)", "icon": "🫵", "important": True},
        2: {"text": "खोई वस्तु एवं धन (Lost Property / Asset)", "icon": "🔍", "important": True},
        4: {"text": "घर के भीतर का स्थान (Within Home / Place)", "icon": "🏠", "important": True},
        7: {"text": "चोर अथवा जिसने वस्तु पाई (Finder / Thief)", "icon": "👤", "important": True},
        11: {"text": "वस्तु की पुनः प्राप्ति (Recovery of Item)", "icon": "🎉", "important": True}
    },
    "Purchase Vehicle": {
        1: {"text": "क्रेता (Buyer)", "icon": "🫵", "important": True},
        4: {"text": "वाहन सुख एवं मॉडल (Vehicle Comfort & Make)", "icon": "🚗", "important": True},
        11: {"text": "क्रय सम्पादन एवं शुभ यात्रा (Purchase Completion)", "icon": "🔑", "important": True}
    }
}


class PrashnaService:
    """Computes horary charts, Tajika Sambandha, and house role breakdowns."""

    def __init__(self):
        self.calculator = default_chart_calculator

    def get_categories(self) -> List[Dict[str, Any]]:
        return PRASHNA_CATEGORIES

    def generate_prashna_chart(
        self,
        query_text: str,
        category_name: str = "Career",
        latitude: float = 28.6139,
        longitude: float = 77.2090,
        timezone_offset: float = 5.5,
        query_dt: Optional[datetime] = None,
        query_category: Optional[str] = None,
        questioner_name: str = "Prashna Querent",
        horary_number: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculates Prashna Chart at the query moment.
        Evaluates Lagna, Lagnesha, Karyesha, Moon, Tajika Ithasala/Esharpha, and house roles.
        """
        cat_str = query_category or category_name
        now = query_dt or datetime.now()
        
        # Build BirthData representing the exact query moment
        birth_data = BirthData(
            name=f"{questioner_name} ({cat_str})",
            birth_date=now.date(),
            birth_time=now.time(),
            latitude=latitude,
            longitude=longitude,
            timezone_offset=timezone_offset,
            confidence="Exact"
        )

        chart = self.calculator.calculate_full_chart(birth_data)

        # Match category metadata
        cat_meta = next(
            (c for c in PRASHNA_CATEGORIES if c["Name"].lower() == cat_str.lower() or c["Name_Hi"] == cat_str),
            PRASHNA_CATEGORIES[5]
        )
        karya_house_num = cat_meta["house"]
        karyesh_name = chart.houses[karya_house_num - 1].lord
        karyesh_planet = chart.planets[karyesh_name]

        lagnesh_name = chart.houses[0].lord
        lagnesh_planet = chart.planets[lagnesh_name]

        is_same = (lagnesh_name == karyesh_name)
        house_karyesh = karyesh_planet.house_from_lagna
        house_lagnesh = lagnesh_planet.house_from_lagna

        # Tajika aspect: distance between lagnesha and karyesha
        diff_deg = abs(lagnesh_planet.longitude - karyesh_planet.longitude) % 360.0
        if diff_deg > 180:
            diff_deg = 360.0 - diff_deg

        # Calculate average deeptamsha orb
        orb_lagnesh = TAJIKA_DEEPTAMSHA.get(lagnesh_name, 8.0)
        orb_karyesh = TAJIKA_DEEPTAMSHA.get(karyesh_name, 8.0)
        max_orb = (orb_lagnesh + orb_karyesh) / 2.0

        # Speeds (motion in degrees/day)
        speed_lagnesh = PLANET_DAILY_MOTION.get(lagnesh_name, 1.0)
        speed_karyesh = PLANET_DAILY_MOTION.get(karyesh_name, 1.0)

        # Tajika aspects: 1st (Conjunction 0°), 3rd/11th (Friendly 60°), 5th/9th (Trine 120°), 4th/10th (Square 90°), 7th (Direct 180°)
        aspect_angles = [0.0, 60.0, 90.0, 120.0, 180.0]
        closest_aspect = None
        min_aspect_diff = 999.0
        for ang in aspect_angles:
            cur_diff = abs(diff_deg - ang)
            if cur_diff < min_aspect_diff:
                min_aspect_diff = cur_diff
                closest_aspect = ang

        in_aspect = (min_aspect_diff <= max_orb)

        is_ithasala = False
        is_esharpha = False
        tajika_yoga_name = "सामान्य दृष्टि (Neutral Sambandha)"

        if in_aspect:
            # Faster planet is applying to slower planet
            if speed_lagnesh > speed_karyesh:
                if lagnesh_planet.sign_degree < karyesh_planet.sign_degree:
                    is_ithasala = True
                    tajika_yoga_name = "🌟 प्रत्यक्ष इत्थशाल योग (Pratyaksha Ithasala - Highly Favorable)"
                else:
                    is_esharpha = True
                    tajika_yoga_name = "⚠️ ईशराफ / मुसरिफ़ योग (Esharpha - Separating / Past Event)"
            elif speed_karyesh > speed_lagnesh:
                if karyesh_planet.sign_degree < lagnesh_planet.sign_degree:
                    is_ithasala = True
                    tajika_yoga_name = "🌟 प्रत्यक्ष इत्थशाल योग (Pratyaksha Ithasala - Highly Favorable)"
                else:
                    is_esharpha = True
                    tajika_yoga_name = "⚠️ ईशराफ / मुसरिफ़ योग (Esharpha - Separating / Past Event)"
            else:
                tajika_yoga_name = "🤝 दृष्टि सम्बंध (Aspect In Orb)"
        elif is_same:
            is_ithasala = True
            tajika_yoga_name = "👑 एकाधिपत्य योग (Same Lord for Lagna & Karya - Natural Success)"

        # Moon condition check
        moon = chart.planets["Moon"]
        moon_favorable = moon.house_from_lagna not in [6, 8, 12]

        is_promising = (
            is_same or
            is_ithasala or
            (house_karyesh in [1, 2, 4, 5, 7, 9, 10, 11] and house_lagnesh in [1, 2, 4, 5, 7, 9, 10, 11])
        )

        verdict_score = 0.50
        if is_promising:
            verdict_score += 0.25
        if is_ithasala:
            verdict_score += 0.15
        if moon_favorable:
            verdict_score += 0.10
        if is_esharpha:
            verdict_score -= 0.15

        verdict_score = max(0.10, min(0.98, verdict_score))

        if verdict_score >= 0.70:
            verdict = "सकारात्मक / शीघ्र कार्य सिद्धि (Favorable / Swift Success)"
            timing = "1 से 3 सप्ताह के भीतर (Within 1-3 weeks)"
            verdict_badge = "✅ शुभ एवं फलदायक"
        elif verdict_score <= 0.45:
            verdict = "विलंब / बाधाएं एवं चुनौतियां (Delays & Obstacles Indicated)"
            timing = "विलंब संभव / शास्त्रीय उपाय आवश्यक (Delayed, Remedies Advised)"
            verdict_badge = "⚠️ विलंबकारी"
        else:
            verdict = "मध्यम / प्रयास एवं धैर्य से सिद्धि (Mixed / Success through Effort)"
            timing = "1 से 3 माह के भीतर (Within 1-3 months)"
            verdict_badge = "⚖️ मध्यम फल"

        # 12 Houses role mapping with icons & descriptions
        cat_roles = PRASHNA_HOUSE_ROLES.get(cat_str, PRASHNA_HOUSE_ROLES.get(cat_meta["Name"], {}))
        house_roles = []
        for h in range(1, 13):
            role_meta = cat_roles.get(h, {
                "text": f"{h}वां भाव (House {h})",
                "icon": "📍",
                "important": (h in [1, karya_house_num, 11])
            })
            h_sign_name = chart.houses[h - 1].sign_name
            occupants = [p for p, pos in chart.planets.items() if pos.house_from_lagna == h]
            house_roles.append({
                "house": h,
                "sign": h_sign_name,
                "lord": chart.houses[h - 1].lord,
                "text": role_meta["text"],
                "icon": role_meta["icon"],
                "is_important": role_meta["important"],
                "occupants": occupants
            })

        # Planetary positions detail list for UI table
        graha_table_data = []
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            p_obj = chart.planets.get(p_name)
            if not p_obj:
                continue
            h_lord = SIGN_LORDS.get(p_obj.sign_name, "-")
            h_num = p_obj.house_from_lagna
            graha_table_data.append({
                "graha": p_name,
                "sign": p_obj.sign_name,
                "lord": h_lord,
                "degree": f"{p_obj.sign_degree:.2f}°",
                "house": f"{h_num} भाव",
                "nakshatra": f"{p_obj.nakshatra_name} ({p_obj.nakshatra_pada})",
                "motion": "वक्री (R)" if p_obj.is_retrograde else "मार्गी (D)",
                "is_retrograde": p_obj.is_retrograde
            })

        return {
            "chart": chart,
            "questioner_name": questioner_name,
            "query_text": query_text,
            "category": cat_meta["Name"],
            "category_hi": cat_meta["Name_Hi"],
            "category_icon": cat_meta["icon"],
            "query_time": now.strftime("%d %b %Y, %I:%M %p"),
            "prashna_lagna": f"{chart.lagna_sign_name} ({chart.lagna_degree:.2f}°)",
            "prashna_lagna_sign": chart.lagna_sign_name,
            "prashna_lagna_deg": f"{chart.lagna_degree:.2f}°",
            "lagnesh": f"{lagnesh_name} ({lagnesh_planet.sign_name}, {house_lagnesh} भाव)",
            "lagnesh_name": lagnesh_name,
            "lagnesh_house": house_lagnesh,
            "karya_bhava": f"{karya_house_num}वां भाव ({chart.houses[karya_house_num - 1].sign_name})",
            "karya_house_num": karya_house_num,
            "karyesh": f"{karyesh_name} ({karyesh_planet.sign_name}, {house_karyesh} भाव)",
            "karyesh_name": karyesh_name,
            "karyesh_house": house_karyesh,
            "tajika_yoga": tajika_yoga_name,
            "is_ithasala": is_ithasala,
            "is_esharpha": is_esharpha,
            "moon_placement": f"चन्द्र देव: {moon.sign_name} ({moon.sign_degree:.2f}°) — {moon.house_from_lagna}वां भाव",
            "verdict": verdict,
            "verdict_badge": verdict_badge,
            "timing": timing,
            "verdict_score": round(verdict_score, 2),
            "house_roles": house_roles,
            "graha_table": graha_table_data,
            "explanation_hi": (
                f"प्रश्न समय पर लग्न '{chart.lagna_sign_name}' उदित है जिसके स्वामी '{lagnesh_name}' {house_lagnesh}वें भाव में स्थित हैं। "
                f"प्रश्न से सम्बंधित कार्य भाव {karya_house_num} के स्वामी '{karyesh_name}' की स्थिति {house_karyesh}वें भाव में है। "
                f"लग्नेश एवं कार्येश के मध्य {tajika_yoga_name} बना हुआ है। "
                f"चंद्र देव {moon.house_from_lagna}वें भाव में {moon.sign_name} राशि में विराजमान हैं। "
                f"शास्त्रीय फल: {verdict}। कार्य सिद्धि का संभावित काल: {timing}।"
            )
        }


default_prashna_service = PrashnaService()
