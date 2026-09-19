"""
Chakras Engine for JyotishOS:
1. Sarvatobhadra Chakra (9x9 Vedha Matrix with 28 Nakshatras, 12 Signs, Vowels, Tithis, and Sensitive Points).
2. Kota Chakra (4-Zone Durga Fortress with Stambha, Madhya, Prakaara, Bahya, Kota Swami, and Kota Pala).
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from .constants import SIGN_NAMES, NAKSHATRA_NAMES
from .models import KundaliChart, PlanetPosition


# 28 Nakshatras list including Abhijit (Abhijit is placed between Uttara Ashadha and Shravana)
NAKSHATRAS_28 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha",
    "Uttara Ashadha", "Abhijit", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadra",
    "Uttara Bhadra", "Revati"
]

BENEFIC_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFIC_PLANETS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


class SarvatobhadraEngine:
    """Calculates 9x9 Sarvatobhadra Chakra layout, Vedhas, and sensitive points."""

    # 9x9 Grid layout definition
    # Coordinates (r, c) from (0,0) to (8,8)
    GRID_LAYOUT = [
        # Row 0 (Top / East outer edge)
        [("vowel", "अ"), ("nak", "Krittika"), ("nak", "Rohini"), ("nak", "Mrigashira"), ("vowel", "आ"), ("nak", "Ardra"), ("nak", "Punarvasu"), ("nak", "Pushya"), ("vowel", "इ")],
        # Row 1
        [("nak", "Bharani"), ("rashi", "Taurus"), ("rashi", "Gemini"), ("tithi", "Nanda"), ("dir", "East"), ("tithi", "Bhadra"), ("rashi", "Cancer"), ("rashi", "Leo"), ("nak", "Ashlesha")],
        # Row 2
        [("nak", "Ashwini"), ("rashi", "Aries"), ("cons", "Ka"), ("cons", "Cha"), ("vowel", "ई"), ("cons", "Ta"), ("cons", "Tha"), ("rashi", "Virgo"), ("nak", "Magha")],
        # Row 3
        [("nak", "Revati"), ("tithi", "Poorna"), ("cons", "Ha"), ("swara", "A"), ("day", "Sun/Mars"), ("swara", "B"), ("cons", "Da"), ("tithi", "Jaya"), ("nak", "Purva Phalguni")],
        # Row 4 (Center Row)
        [("vowel", "ऋ"), ("dir", "North"), ("vowel", "उ"), ("day", "Merc"), ("center", "ब्रह्म"), ("day", "Jup"), ("vowel", "ऊ"), ("dir", "South"), ("vowel", "ऌ")],
        # Row 5
        [("nak", "Uttara Bhadra"), ("tithi", "Jaya"), ("cons", "Sa"), ("swara", "C"), ("day", "Moon/Ven"), ("swara", "D"), ("cons", "Pa"), ("tithi", "Poorna"), ("nak", "Uttara Phalguni")],
        # Row 6
        [("nak", "Purva Bhadra"), ("rashi", "Pisces"), ("cons", "Sha"), ("cons", "Ya"), ("vowel", "ए"), ("cons", "Na"), ("cons", "Ma"), ("rashi", "Libra"), ("nak", "Hasta")],
        # Row 7
        [("nak", "Shatabhisha"), ("rashi", "Aquarius"), ("rashi", "Capricorn"), ("tithi", "Rikta"), ("dir", "West"), ("tithi", "Rikta"), ("rashi", "Sagittarius"), ("rashi", "Scorpio"), ("nak", "Chitra")],
        # Row 8 (Bottom / West outer edge)
        [("vowel", "ऐ"), ("nak", "Dhanishta"), ("nak", "Shravana"), ("nak", "Abhijit"), ("vowel", "ओ"), ("nak", "Uttara Ashadha"), ("nak", "Purva Ashadha"), ("nak", "Moola"), ("vowel", "औ")]
    ]

    # Special sensitive nakshatra offsets from Janma Nakshatra (1-based index in 28-nakshatra system)
    SENSITIVE_POINTS_MAP = {
        1: ("Janma Nakshatra", "जन्म नक्षत्र", "शारीरिक स्वास्थ्य, मूल प्रकृति एवं मानसिक स्थिति।"),
        2: ("Sampat", "सम्पत् नक्षत्र", "धन-धान्य, वित्तीय लाभ एवं पारिवारिक समृद्धि।"),
        3: ("Vipat", "विपत् नक्षत्र", "बाधाएं, अचानक रुकावटें एवं वित्तीय संकट।"),
        4: ("Kshema", "क्षेम नक्षत्र", "सुरक्षा, आरोग्य, कल्याण एवं मानसिक शांति।"),
        5: ("Pratyak", "प्रत्यक् नक्षत्र", "शत्रुता, असफलता एवं प्रयासों में अवरोध।"),
        6: ("Sadhaka", "साधक नक्षत्र", "मनोकामना पूर्ति, लक्ष्य सिद्धि एवं सफलता।"),
        7: ("Vadha / Naidhana", "वध / नैधन नक्षत्र", "अत्यंत संकट, स्वास्थ्य आघात एवं भारी नुकसान।"),
        8: ("Mitra", "मित्र नक्षत्र", "सौहार्दपूर्ण संबंध, सहयोग एवं शुभ अवसर।"),
        9: ("Parama Mitra", "परम मित्र नक्षत्र", "परम मित्र, महाभाग्य एवं दुर्लभ सहयोग।"),
        10: ("Karma Nakshatra", "कर्म नक्षत्र", "कार्यक्षेत्र, व्यवसाय, आजीविका एवं सामाजिक प्रतिष्ठा।"),
        16: ("Sanghatika", "सांघातिक नक्षत्र", "साझेदारी, पारिवारिक रिश्ते एवं आकस्मिक आघात।"),
        18: ("Samudayika", "सामुदायिक नक्षत्र", "सामूहिक संबंध, जनसंपर्क एवं समाज में प्रभाव।"),
        19: ("Aadhana", "आधान नक्षत्र", "मूल बीज, गर्भाधान, मानसिक आधार एवं आंतरिक शक्ति।"),
        23: ("Vainashika", "वैनाशिक नक्षत्र", "गंभीर क्षति, विनाशकारी प्रवृत्तियां एवं विनाश से रक्षा।"),
        26: ("Jati Nakshatra", "जाति नक्षत्र", "कुल, वंश, समुदाय एवं सामाजिक स्तर।"),
        27: ("Desha Nakshatra", "देश नक्षत्र", "निवास स्थान, राष्ट्र, यात्रा एवं स्थानान्तरण।"),
        28: ("Abhisheka", "अभिषेक नक्षत्र", "राज्याभिषेक, सर्वोच्च पद-प्रतिष्ठा एवं कीर्ति।")
    }

    @classmethod
    def get_28_nakshatra_index(cls, nak_name_27: str, sign_deg: float = 0.0) -> int:
        """Converts 27-Nakshatra name to 28-Nakshatra index (0 to 27)."""
        if nak_name_27 == "Uttara Ashadha" and sign_deg >= 6.666:
            # Last 3 padas of Uttara Ashadha partially overlap with Abhijit
            return NAKSHATRAS_28.index("Abhijit")
        if nak_name_27 in NAKSHATRAS_28:
            return NAKSHATRAS_28.index(nak_name_27)
        return 0

    @classmethod
    def calculate(cls, natal_chart: KundaliChart, transit_chart: Optional[KundaliChart] = None) -> Dict[str, Any]:
        """Calculates Sarvatobhadra Chakra Vedha analysis."""
        natal_moon = natal_chart.planets["Moon"]
        natal_nak_27 = natal_chart.panchang.nakshatra_name
        janma_idx_28 = cls.get_28_nakshatra_index(natal_nak_27, natal_moon.sign_degree)

        # 1. Map sensitive nakshatras for the native
        sensitive_points = []
        for offset, (code, hi_name, desc) in cls.SENSITIVE_POINTS_MAP.items():
            target_idx = (janma_idx_28 + (offset - 1)) % 28
            nak_name = NAKSHATRAS_28[target_idx]
            sensitive_points.append({
                "offset": offset,
                "code": code,
                "hi_name": hi_name,
                "nakshatra": nak_name,
                "desc": desc
            })

        # 2. Determine transit planet positions on the 28-nakshatra wheel
        active_chart = transit_chart if transit_chart else natal_chart
        transit_placements = []
        vedhas = []

        for p_name, p_obj in active_chart.planets.items():
            # Get 28 nakshatra
            nak_idx_28 = cls.get_28_nakshatra_index(p_obj.nakshatra_name, p_obj.sign_degree)
            nak_28_name = NAKSHATRAS_28[nak_idx_28]
            is_benefic = p_name in BENEFIC_PLANETS

            # Check Vedha to native's sensitive nakshatras
            for sp in sensitive_points:
                # Sammukha (opposite index in 28 cycle ~ 14 nakshatras away)
                dist = abs(nak_idx_28 - NAKSHATRAS_28.index(sp["nakshatra"]))
                vedha_type = None
                if dist == 0:
                    vedha_type = "प्रत्यक्ष युति (Conjunction / Exact)"
                elif dist == 14:
                    vedha_type = "सम्मुख वेध (Front / Sammukha Vedha)"
                elif dist in (7, 21):
                    vedha_type = "वाम/दक्षिण वेध (Diagonal / Cross Vedha)"

                if vedha_type:
                    impact = "शुभ प्रभाव (Benefic Protection)" if is_benefic else "अशुभ वेध (Malefic Affliction)"
                    vedhas.append({
                        "planet": p_name,
                        "planet_nak": nak_28_name,
                        "target_point": sp["hi_name"],
                        "target_nak": sp["nakshatra"],
                        "vedha_type": vedha_type,
                        "impact": impact,
                        "is_benefic": is_benefic
                    })

            transit_placements.append({
                "planet": p_name,
                "nakshatra": nak_28_name,
                "sign": p_obj.sign_name,
                "degree": round(p_obj.sign_degree, 2),
                "speed": "वक्र (R)" if p_obj.is_retrograde else "मार्गी (D)"
            })

        return {
            "janma_nakshatra_28": NAKSHATRAS_28[janma_idx_28],
            "sensitive_points": sensitive_points,
            "transit_placements": transit_placements,
            "vedhas": vedhas,
            "grid_layout": cls.GRID_LAYOUT
        }


class KotaChakraEngine:
    """Calculates Kota Chakra (Durga Fortress) 4-zone allocation and defense analysis."""

    @classmethod
    def calculate(cls, natal_chart: KundaliChart, transit_chart: Optional[KundaliChart] = None) -> Dict[str, Any]:
        """Computes Kota Chakra 4-zone fortress analysis."""
        natal_moon = natal_chart.planets["Moon"]
        janma_idx = SarvatobhadraEngine.get_28_nakshatra_index(natal_chart.panchang.nakshatra_name, natal_moon.sign_degree)

        # Zone partitions from Janma Nakshatra (28 nakshatras)
        # 1. Stambha (Central Pillar): 4 nakshatras (Janma, +7, +14, +21)
        stambha_indices = [(janma_idx + i) % 28 for i in [0, 7, 14, 21]]
        # 2. Madhya (Inner Court): 4 nakshatras
        madhya_indices = [(janma_idx + i) % 28 for i in [1, 8, 15, 22]]
        # 3. Prakaara (Fort Walls / Ramparts): 8 nakshatras
        prakaara_indices = [(janma_idx + i) % 28 for i in [2, 6, 9, 13, 16, 20, 23, 27]]
        # 4. Bahya (Outer Ground / Gates): 12 nakshatras
        bahya_indices = [(janma_idx + i) % 28 for i in [3, 4, 5, 10, 11, 12, 17, 18, 19, 24, 25, 26]]

        zones_map = {
            "Stambha (स्तम्भ - गर्भगृह)": [NAKSHATRAS_28[i] for i in stambha_indices],
            "Madhya (मध्य - अन्तःपुर)": [NAKSHATRAS_28[i] for i in madhya_indices],
            "Prakaara (प्राकार - परकोटा/दीवार)": [NAKSHATRAS_28[i] for i in prakaara_indices],
            "Bahya (बाह्य - दुर्ग के बाहर)": [NAKSHATRAS_28[i] for i in bahya_indices],
        }

        # Kota Swami (Lord of Moon sign) and Kota Pala (Lord of 8th / Guardian)
        moon_sign = natal_moon.sign_name
        from .constants import SIGN_LORDS
        kota_swami = SIGN_LORDS.get(moon_sign, "Moon")
        # Kota Pala is typically Mercury/Mars or Lord of Janma Nakshatra
        kota_pala = natal_moon.nakshatra_lord

        # Map current transit planets into Kota zones
        active_chart = transit_chart if transit_chart else natal_chart
        planet_allocations = []
        stambha_malefics = []
        stambha_benefics = []

        for p_name, p_obj in active_chart.planets.items():
            p_nak_28_idx = SarvatobhadraEngine.get_28_nakshatra_index(p_obj.nakshatra_name, p_obj.sign_degree)
            p_nak_name = NAKSHATRAS_28[p_nak_28_idx]

            zone_name = "Bahya (बाह्य)"
            if p_nak_28_idx in stambha_indices:
                zone_name = "Stambha (स्तम्भ - केंद्र)"
                if p_name in MALEFIC_PLANETS:
                    stambha_malefics.append(p_name)
                else:
                    stambha_benefics.append(p_name)
            elif p_nak_28_idx in madhya_indices:
                zone_name = "Madhya (मध्य)"
            elif p_nak_28_idx in prakaara_indices:
                zone_name = "Prakaara (प्राकार)"

            # Movement (Ingress vs Egress)
            motion = "प्रवेश (Pravesha / Entering)" if not p_obj.is_retrograde else "निर्गम (Nirgamana / Exiting)"

            planet_allocations.append({
                "planet": p_name,
                "nakshatra": p_nak_name,
                "zone": zone_name,
                "motion": motion,
                "nature": "Benefic" if p_name in BENEFIC_PLANETS else "Malefic"
            })

        # Evaluate Defense / Siege Score
        if len(stambha_malefics) >= 2:
            status = "🚨 दुर्ग संकट (Severe Siege / High Vulnerability)"
            summary = f"अशुभ ग्रह ({', '.join(stambha_malefics)}) स्तम्भ (केंद्रीय गर्भगृह) में स्थित हैं। स्वास्थ्य व प्रतिष्ठा की रक्षा आवश्यक है।"
        elif len(stambha_benefics) >= 1:
            status = "🛡️ पूर्ण रक्षित (Strong Defense / Protected)"
            summary = f"शुभ ग्रह ({', '.join(stambha_benefics)}) स्तम्भ में स्थित होकर दुर्ग को अभेद्य सुरक्षा प्रदान कर रहे हैं।"
        else:
            status = "⚖️ सामान्य स्थिति (Balanced / Moderate Defense)"
            summary = "दुर्ग का वातावरण संतुलित है। कोटा स्वामी एवं कोटा पाल की अनुकूलता रक्षा कर रही है।"

        return {
            "kota_swami": kota_swami,
            "kota_pala": kota_pala,
            "zones_map": zones_map,
            "planet_allocations": planet_allocations,
            "defense_status": status,
            "defense_summary": summary,
            "stambha_malefics": stambha_malefics,
            "stambha_benefics": stambha_benefics
        }


# Singletons
default_sarvatobhadra_engine = SarvatobhadraEngine()
default_kota_chakra_engine = KotaChakraEngine()

