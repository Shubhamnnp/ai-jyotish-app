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
from ..core.constants import KENDRA_HOUSES, TRIKONA_HOUSES


PRASHNA_CATEGORIES = [
    {"Id": 19, "Name": "Health", "house": 1, "karyesh_default": "Sun", "icon": "🩺"},
    {"Id": 20, "Name": "Marriage", "house": 7, "karyesh_default": "Venus", "icon": "💍"},
    {"Id": 3, "Name": "Relationship", "house": 7, "karyesh_default": "Venus", "icon": "❤️"},
    {"Id": 4, "Name": "Child", "house": 5, "karyesh_default": "Jupiter", "icon": "👶"},
    {"Id": 5, "Name": "Wealth", "house": 2, "karyesh_default": "Jupiter", "icon": "💰"},
    {"Id": 6, "Name": "Career", "house": 10, "karyesh_default": "Saturn", "icon": "👔"},
    {"Id": 27, "Name": "Job", "house": 6, "karyesh_default": "Saturn", "icon": "💼"},
    {"Id": 28, "Name": "Business", "house": 7, "karyesh_default": "Mercury", "icon": "🏢"},
    {"Id": 29, "Name": "Property", "house": 4, "karyesh_default": "Mars", "icon": "🏠"},
    {"Id": 30, "Name": "Investment", "house": 11, "karyesh_default": "Jupiter", "icon": "📈"},
    {"Id": 31, "Name": "Litigation / Court", "house": 6, "karyesh_default": "Mars", "icon": "⚖️"},
    {"Id": 32, "Name": "Foreign Travel", "house": 9, "karyesh_default": "Jupiter", "icon": "✈️"},
    {"Id": 33, "Name": "Education / Exam", "house": 5, "karyesh_default": "Mercury", "icon": "🎓"},
    {"Id": 34, "Name": "Lost Item", "house": 2, "karyesh_default": "Moon", "icon": "🔍"},
    {"Id": 35, "Name": "Purchase Vehicle", "house": 4, "karyesh_default": "Venus", "icon": "🚗"},
    {"Id": 36, "Name": "General Prashna", "house": 1, "karyesh_default": "Moon", "icon": "🔮"}
]

PRASHNA_HOUSE_ROLES = {
    "Health": {
        1: {"text": "Doctor / Physician", "icon": "🩺", "important": True},
        4: {"text": "Treatment / Medicine", "icon": "💉", "important": True},
        6: {"text": "Disease / Symptom", "icon": "🦠", "important": True},
        8: {"text": "Complications / Severity", "icon": "⚠️", "important": True},
        11: {"text": "Recovery / Vitality", "icon": "✨", "important": True}
    },
    "Marriage": {
        1: {"text": "Client / Querent", "icon": "🫵", "important": True},
        2: {"text": "Family / Kutumba", "icon": "👨‍👩‍👧", "important": True},
        4: {"text": "Harmony / Patch Up", "icon": "🕊️", "important": True},
        7: {"text": "Proposed Partner / Match", "icon": "💍", "important": True},
        11: {"text": "Fulfillment / Marriage Vows", "icon": "🎉", "important": True}
    },
    "Job": {
        1: {"text": "Client / Candidate", "icon": "🫵", "important": True},
        6: {"text": "Daily Work / Service", "icon": "📋", "important": True},
        10: {"text": "New Job / Boss / Authority", "icon": "💼", "important": True},
        11: {"text": "Salary / Gains / Offer Letter", "icon": "💵", "important": True}
    },
    "Career": {
        1: {"text": "Querent's Initiative", "icon": "🫵", "important": True},
        7: {"text": "Partners / Clients", "icon": "🤝", "important": False},
        10: {"text": "Career Growth / Status", "icon": "👔", "important": True},
        11: {"text": "Profits / Promotion", "icon": "🚀", "important": True}
    },
    "Property": {
        1: {"text": "Buyer / Seller", "icon": "🫵", "important": True},
        4: {"text": "Land / Building / House", "icon": "🏠", "important": True},
        7: {"text": "Other Party / Dealer", "icon": "🤝", "important": True},
        11: {"text": "Deal Finalization / Profit", "icon": "🔑", "important": True}
    },
    "Wealth": {
        1: {"text": "Querent", "icon": "🫵", "important": True},
        2: {"text": "Accumulated Wealth / Bank Balance", "icon": "🏦", "important": True},
        9: {"text": "Bhagya / Divine Luck", "icon": "🍀", "important": True},
        11: {"text": "Direct Financial Inflow", "icon": "💰", "important": True}
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
        query_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates Prashna Chart at the query moment.
        Evaluates Lagna, Lagnesha, Karyesha, Moon, Tajika Ithasala, and house roles.
        """
        cat_str = query_category or category_name
        now = query_dt or datetime.now()
        birth_data = BirthData(
            name=f"Prashna: {cat_str}",
            birth_date=now.date(),
            birth_time=now.time(),
            latitude=latitude,
            longitude=longitude,
            timezone_offset=timezone_offset,
            confidence="Exact"
        )

        chart = self.calculator.calculate_chart(birth_data)

        # Match category
        cat_meta = next((c for c in PRASHNA_CATEGORIES if c["Name"].lower() == cat_str.lower()), PRASHNA_CATEGORIES[5])
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

        # Tajika Deeptamsha (orbs of influence: Sun 15, Moon 12, Mars 8, Mer 7, Jup 9, Ven 7, Sat 9)
        # Check for Ithasala yoga (applying benefic aspect 1st, 3rd, 5th, 9th, 11th or Kendra)
        is_ithasala = False
        faster_planet_speeds = {"Moon": 13.2, "Mercury": 1.2, "Venus": 1.0, "Sun": 0.98, "Mars": 0.5, "Jupiter": 0.08, "Saturn": 0.03}
        speed_lagnesh = faster_planet_speeds.get(lagnesh_name, 1.0)
        speed_karyesh = faster_planet_speeds.get(karyesh_name, 1.0)

        # Angular aspect check (conjunction ~0°, sextile ~60°, trine ~120°, opposition ~180°)
        in_aspect = any(abs(diff_deg - angle) < 10.0 for angle in [0, 60, 90, 120, 180])
        if in_aspect:
            if speed_lagnesh > speed_karyesh and lagnesh_planet.longitude < karyesh_planet.longitude:
                is_ithasala = True
            elif speed_karyesh > speed_lagnesh and karyesh_planet.longitude < lagnesh_planet.longitude:
                is_ithasala = True

        # Moon condition
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

        if verdict_score >= 0.70:
            verdict = "सकारात्मक / शीघ्र सिद्धि (Favorable / Swift Success)"
            timing = "1 से 3 सप्ताह के भीतर (Within 1-3 weeks)"
        elif verdict_score <= 0.45:
            verdict = "विलंब / बाधाएं (Delays & Obstacles Indicated)"
            timing = "विलंब संभव / उपाय आवश्यक (Delayed, Remedies Advised)"
        else:
            verdict = "मध्यम / प्रयास से सिद्धि (Mixed / Success through Effort)"
            timing = "2 से 3 माह के भीतर (Within 2-3 months)"

        # 12 Houses role mapping with icons
        cat_roles = PRASHNA_HOUSE_ROLES.get(category_name, PRASHNA_HOUSE_ROLES.get("Career", {}))
        house_roles = []
        for h in range(1, 13):
            role_meta = cat_roles.get(h, {"text": f"House {h}", "icon": "📍", "important": False})
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

        return {
            "query_text": query_text,
            "category": category_name,
            "query_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "prashna_lagna": f"{chart.lagna_sign_name} ({chart.lagna_degree:.2f}°)",
            "lagnesh": f"{lagnesh_name} in {house_lagnesh}th house ({lagnesh_planet.sign_name})",
            "karya_bhava": f"{karya_house_num}th House",
            "karyesh": f"{karyesh_name} in {house_karyesh}th house ({karyesh_planet.sign_name})",
            "tajika_yoga": "इत्थशाल योग (Ithasala Yoga - Strong Application)" if is_ithasala else "सामान्य दृष्टि (Standard Aspect)",
            "moon_placement": f"Moon in {moon.sign_name} ({moon.house_from_lagna}th house)",
            "verdict": verdict,
            "timing": timing,
            "verdict_score": round(verdict_score, 2),
            "house_roles": house_roles,
            "explanation_hi": (
                f"प्रश्न समय पर लग्न '{chart.lagna_sign_name}' उदित है। "
                f"कार्य भाव {karya_house_num} के स्वामी '{karyesh_name}' की स्थिति {house_karyesh} भाव में है। "
                f"लग्नेश और कार्येश का सम्बंध: {verdict}। संभावित समय: {timing}।"
            )
        }


default_prashna_service = PrashnaService()
