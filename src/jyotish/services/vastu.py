"""
Vastu-Jyotish Directional Mandala and Remedial Architecture Engine for JyotishOS.

Correlates planetary positions, strengths, and afflictions from the natal Kundali
with the 8 cardinal directions and Brahmasthan of residential/commercial spaces.
Provides bilingual (English/Hindi) diagnostic reports, architectural zones, and shastriya remedies.
"""

from typing import Dict, Any, List, Optional
from ..core.models import KundaliChart, PlanetPosition
from ..core.constants import SIGN_LORDS


VASTU_DIRECTIONS = {
    "East": {
        "hindi": "पूर्व (Purva)",
        "lord": "Sun",
        "deity": "Indra / Surya",
        "element": "Agni / Light",
        "ideal_uses": ["Main Entrance", "Balcony", "Puja / Meditation", "Living Room Windows"],
        "avoid": ["Heavy Storage", "Toilets", "Septic Tank", "High Walls"],
        "chakra_organ": "Vitality, Eye Sight, Heart, Head, Father",
        "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः ॥",
        "remedy_en": "Keep eastern wall low and clear of heavy furniture. Place Surya Yantra or brass sun emblem on eastern wall. Use red/gold accents.",
        "remedy_hi": "पूर्व दिशा को स्वच्छ, खुला और हल्का रखें। भारी सामान न रखें। पूर्व की दीवार पर तांबे का सूर्य यंत्र या पीतल का सूर्य स्थापित करें।"
    },
    "South-East": {
        "hindi": "आग्नेय (Agneya)",
        "lord": "Venus",
        "deity": "Agni Dev",
        "element": "Fire (Agni)",
        "ideal_uses": ["Kitchen", "Cooktop", "Electrical Meter / Panels", "Inverter / Generator", "Boiler"],
        "avoid": ["Water Boring", "Underground Tank", "Master Bedroom", "Main Gate"],
        "chakra_organ": "Hormones, Reproductive System, Luxury, Cash Flow, Marital Bliss",
        "mantra": "ॐ शुं शुक्राय नमः ॥",
        "remedy_en": "Keep burner facing East. Avoid water element in this zone. Paint in cream, off-white or light pink.",
        "remedy_hi": "रसोईघर और विद्युत उपकरण आग्नेय कोण में रखें। इस दिशा में पानी का बोरिंग या भूमिगत टंकी कभी न बनाएं। क्रीम या हल्का गुलाबी रंग प्रयोग करें।"
    },
    "South": {
        "hindi": "दक्षिण (Dakshina)",
        "lord": "Mars",
        "deity": "Yama",
        "element": "Tejas / Earth",
        "ideal_uses": ["Bedroom", "Heavy Storage", "Staircase", "Overhead Storage"],
        "avoid": ["Main Entrance (unless 3rd/4th Pada)", "Underground Water", "Large Mirrors"],
        "chakra_organ": "Blood, Bone Marrow, Muscular Strength, Courage, Siblings",
        "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः ॥",
        "remedy_en": "Keep southern boundary wall higher and heavier than northern. Plant Neem or Ashoka trees along southern perimeter.",
        "remedy_hi": "दक्षिण की दीवारें उत्तर से ऊँची और भारी रखें। मुख्य द्वार के दोष पर मंगल यंत्र और तांबे की पट्टी स्थापित करें।"
    },
    "South-West": {
        "hindi": "नैऋत्य (Nairutya)",
        "lord": "Rahu",
        "deity": "Nirriti / Pitrus",
        "element": "Prithvi (Earth)",
        "ideal_uses": ["Master Bedroom", "Heavy Wardrobe / Safe", "Staircase", "Highest Elevation"],
        "avoid": ["Main Entrance", "Water Tank", "Borewell", "Toilet", "Balcony / Slope"],
        "chakra_organ": "Stability, Lifespan, Nervous Balance, Ancestral Blessings",
        "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः ॥",
        "remedy_en": "Keep South-West corner completely solid with no cuts or extensions. Place heavy furniture and brass elephants. Install lead helix/pyramids for defects.",
        "remedy_hi": "नैऋत्य कोण को घर का सबसे भारी और ऊँचा कोना बनाएं। यहाँ बोरिंग, गड्ढा या शौचालय कभी न बनाएं। दोष निवारण हेतु राहु यंत्र एवं लेड पिरामिड लगाएं।"
    },
    "West": {
        "hindi": "पश्चिम (Pashchima)",
        "lord": "Saturn",
        "deity": "Varuna",
        "element": "Vayu / Water",
        "ideal_uses": ["Dining Room", "Study Room", "Overhead Water Tank", "Servant / Staff Quarters"],
        "avoid": ["Main Entrance facing NW", "Kitchen", "Open Low Ground"],
        "chakra_organ": "Bones, Joints, Discipline, Long-term Gains, Longevity",
        "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः ॥",
        "remedy_en": "Plant Shami tree (खेजड़ी या शमी) on a Saturday or Shani Hora. Place overhead water tank on western zone.",
        "remedy_hi": "पश्चिम दिशा में शमी का वृक्ष शनिवार या शनि होरा में लगाएं। लोहे का शनि यंत्र अथवा नीले क्रिस्टल स्थापित करें।"
    },
    "North-West": {
        "hindi": "वायव्य (Vayavya)",
        "lord": "Moon",
        "deity": "Vayu Dev",
        "element": "Air (Vayu)",
        "ideal_uses": ["Guest Room", "Finished Goods Stock", "Unmarried Daughters' Bedroom", "Garage / Parking"],
        "avoid": ["Master Bedroom", "Heavy Concrete Clutter", "Kitchen Fireplace"],
        "chakra_organ": "Mind, Mental Peace, Fluids, Mother's Health, Travel, Relationships",
        "mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः ॥",
        "remedy_en": "Ensure proper cross-ventilation and white/silver decor. Place Chandra Yantra or a running water fountain.",
        "remedy_hi": "वायव्य दिशा में हवा का आवागमन सुगम रखें। श्वेत रंग, चांदी का स्वास्तिक या बहते पानी का फव्वारा लगाएं।"
    },
    "North": {
        "hindi": "उत्तर (Uttara)",
        "lord": "Mercury",
        "deity": "Kubera / Vishnu",
        "element": "Jala / Wealth",
        "ideal_uses": ["Cash Locker / Safe", "Accounts / Study Room", "Lawn / Open Veranda", "Green Plants"],
        "avoid": ["Toilets", "Staircase", "Heavy Storage / Clutter", "High Solid Walls"],
        "chakra_organ": "Intellect, Communication, Financial Growth, Nervous System, Trade",
        "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः ॥",
        "remedy_en": "Plant Panasa (Jackfruit) or Tulsi. Keep northern zone light and green. Install Kubera Yantra or Budha Yantra.",
        "remedy_hi": "उत्तर दिशा कुबेर का स्थान है। यहाँ तिजोरी या कैश बॉक्स उत्तर दिशा की ओर खुलता हुआ रखें। तुलसी का पौधा और बुध यंत्र लगाएं।"
    },
    "North-East": {
        "hindi": "ईशान (Ishanya)",
        "lord": "Jupiter",
        "deity": "Shiva / Ishana",
        "element": "Jala / Ether (Water)",
        "ideal_uses": ["Mandir / Puja Room", "Meditation Space", "Underground Clean Water Tank / Borewell", "Study"],
        "avoid": ["Toilet / Septic Tank", "Kitchen / Fire", "Heavy Storage", "Staircase", "Overhead Tank"],
        "chakra_organ": "Spiritual Wisdom, Progeny, Family Harmony, Higher Knowledge",
        "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः ॥",
        "remedy_en": "Absolute sacred cleanliness. Keep lowest elevation of the entire plot. Place brass Guru Yantra and keep Ganga Jal.",
        "remedy_hi": "ईशान कोण भगवान शिव और बृहस्पति का पावन स्थान है। यहाँ पूजा घर या भूमिगत जल स्रोत रखें। यहाँ शौचालय या भारी सीढ़ी महादोष उत्पन्न करती है।"
    },
    "Center": {
        "hindi": "ब्रह्मस्थान (Brahmasthan)",
        "lord": "All",
        "deity": "Lord Brahma",
        "element": "Akasha (Ether / Space)",
        "ideal_uses": ["Courtyard / Open Space", "Light Central Hall", "Natural Skylight"],
        "avoid": ["Pillars", "Heavy Beams", "Toilets", "Kitchen", "Underground Pit / Tank"],
        "chakra_organ": "Universal Cosmic Energy, Life Balance",
        "mantra": "ॐ नमो भगवते वासुदेवाय ॥",
        "remedy_en": "Keep the center of the building completely open, clean, and unweighted. Allow natural daylight if possible.",
        "remedy_hi": "घर के मध्य भाग को ब्रह्मस्थान कहते हैं। इसे पूर्णतः खुला, प्रकाशयुक्त और भारमुक्त रखें।"
    }
}


class VastuJyotishEngine:
    """Engine mapping natal chart strengths and afflictions to architectural Vastu layout."""

    def __init__(self, chart: KundaliChart):
        self.chart = chart

    def evaluate_vastu_zones(self) -> List[Dict[str, Any]]:
        """
        Evaluates each direction based on the native's chart:
        - Planetary status (Exalted, Own, Friendly, Enemy, Debilitated, Combust)
        - Dusthana placement (6th, 8th, 12th)
        - Vastu zone harmony score (0 to 100)
        - Specific architectural defects to inspect and remedies
        """
        results = []

        for direction, meta in VASTU_DIRECTIONS.items():
            lord_name = meta["lord"]
            if lord_name == "All":
                results.append({
                    "direction": direction,
                    "hindi": meta["hindi"],
                    "lord": "Cosmic (Brahma)",
                    "element": meta["element"],
                    "status": "Neutral",
                    "score": 85,
                    "defect_risk": "Low",
                    "meta": meta
                })
                continue

            pos: Optional[PlanetPosition] = self.chart.planets.get(lord_name)
            if not pos:
                continue

            # Determine planetary dignity
            status = pos.dignity.capitalize()
            score = 70.0

            if status in ["Exalted", "Own", "Moolatrikona"]:
                score += 20.0
            elif status in ["Debilitated"]:
                score -= 30.0
            elif status in ["Enemy", "Great_enemy"]:
                score -= 15.0

            # Dusthana check
            if pos.house_from_lagna in [6, 8, 12]:
                score -= 15.0
            elif pos.house_from_lagna in [1, 4, 5, 9, 10]:
                score += 10.0

            # Combustion check
            if pos.is_combust:
                score -= 15.0

            score = max(20.0, min(100.0, score))

            defect_risk = "High Risk" if score < 50 else "Moderate Risk" if score < 75 else "Harmonious"

            results.append({
                "direction": direction,
                "hindi": meta["hindi"],
                "lord": lord_name,
                "planet_symbol": pos.name[:2],
                "sign_name": pos.sign_name,
                "house": pos.house_from_lagna,
                "element": meta["element"],
                "status": status,
                "is_combust": pos.is_combust,
                "score": int(score),
                "defect_risk": defect_risk,
                "meta": meta
            })

        return results

