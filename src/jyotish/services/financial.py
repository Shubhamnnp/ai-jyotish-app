"""
Financial and Commodity Astrology Service for JyotishOS.
Implements classical Sarvatobhadra market transits for commodities (Gold, Silver, Crude Oil, Copper, Grains, Equities/Nifty)
and personal natal wealth/trading suitability analysis according to Brihat Samhita and Parashari Dhana Yogas.
"""

from typing import Dict, List, Any, Optional
from ..core.constants import SIGN_NAMES, SIGN_LORDS, NAKSHATRAS, GRAHAS
from ..core.models import KundaliChart


COMMODITY_MAPPINGS = {
    "Gold (स्वर्ण)": {
        "rulers": ["Sun", "Jupiter"],
        "element": "Agni",
        "nakshatras": ["Krittika", "Pushya", "Vishakha", "Uttara Phalguni"],
        "icon": "🪙",
        "description": "सूर्य एवं देवगुरु बृहस्पति द्वारा शासित। तेज एवं समृद्धि का प्रतीक।"
    },
    "Silver (चांदी)": {
        "rulers": ["Moon", "Venus"],
        "element": "Jala",
        "nakshatras": ["Rohini", "Hasta", "Shravana", "Punarvasu"],
        "icon": "🥈",
        "description": "चन्द्र एवं शुक्र द्वारा शासित। सौम्यता एवं तरलता का सूचक।"
    },
    "Crude Oil (कच्चा तेल व ऊर्जा)": {
        "rulers": ["Saturn", "Rahu"],
        "element": "Vayu / Tamas",
        "nakshatras": ["Ardra", "Swati", "Shatabhisha", "Purva Bhadrapada"],
        "icon": "🛢️",
        "description": "शनि एवं राहु द्वारा शासित। भूगर्भ, ईंधन एवं औद्योगिक ऊर्जा।"
    },
    "Copper & Metals (तांबा व औद्योगिक धातु)": {
        "rulers": ["Mars"],
        "element": "Agni",
        "nakshatras": ["Mrigashira", "Chitra", "Dhanishta"],
        "icon": "⛏️",
        "description": "मंगल द्वारा शासित। विद्युत चालकता, रक्षा उपकरण एवं निर्माण।"
    },
    "Equities & Nifty (शेयर बाज़ार व सूचकांक)": {
        "rulers": ["Mercury", "Jupiter"],
        "element": "Prithvi / Vayu",
        "nakshatras": ["Ashlesha", "Jyeshtha", "Revati", "Pushya"],
        "icon": "📊",
        "description": "बुध (व्यापार व गणित) एवं गुरु (विस्तार) द्वारा नियंत्रित वित्तीय सूचकांक।"
    },
    "Grains & Agri (खाद्यान्न व कृषि उपज)": {
        "rulers": ["Jupiter", "Moon"],
        "element": "Prithvi / Jala",
        "nakshatras": ["Magha", "Purva Phalguni", "Anuradha", "Uttara Ashadha"],
        "icon": "🌾",
        "description": "गुरु एवं चन्द्र द्वारा शासित। जन-पोषण, अन्न एवं कृषि उत्पाद।"
    }
}


class FinancialAstrologyService:
    """Analyzes planetary vedha on financial markets and personal trading suitability."""

    @classmethod
    def analyze_commodity_market_trends(cls, transit_chart: KundaliChart) -> List[Dict[str, Any]]:
        """
        Calculates bull/bear/volatility scores for major commodities and equities
        based on active transits of natural benefics vs malefics over sensitive nakshatras.
        """
        t_planets = transit_chart.planets
        results = []

        # Find nakshatras occupied by transit planets
        transit_nak_map = {}
        for p_name, pos in t_planets.items():
            nak_name = pos.nakshatra_name
            if nak_name not in transit_nak_map:
                transit_nak_map[nak_name] = []
            transit_nak_map[nak_name].append(p_name)

        malefics = ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]

        for item_name, info in COMMODITY_MAPPINGS.items():
            score = 50  # 50 = neutral baseline
            reasons = []

            # Check transit in commodity's sensitive nakshatras
            for s_nak in info["nakshatras"]:
                if s_nak in transit_nak_map:
                    occ = transit_nak_map[s_nak]
                    for p in occ:
                        if p in malefics:
                            score += 15  # Malefics drive supply shortage / price inflation (तेजी)
                            reasons.append(f"क्रूर ग्रह {p} का संवेदनशील नक्षत्र '{s_nak}' में गोचर (तेजी व उछाल दबाव)।")
                        else:
                            score -= 8   # Benefics stabilize or ease prices (स्थिरता/सुस्ती)
                            reasons.append(f"सौम्य ग्रह {p} का संवेदनशील नक्षत्र '{s_nak}' में गोचर (संतुलित आपूर्ति)।")

            # Check rulers' status in transit
            for ruler in info["rulers"]:
                if ruler in t_planets:
                    r_pos = t_planets[ruler]
                    if r_pos.is_retrograde:
                        score += 8
                        reasons.append(f"अधिष्ठाता ग्रह {ruler} का वक्री होना (बाज़ार में अप्रत्याशित उतार-चढ़ाव)।")
                    if r_pos.dignity in ["exalted", "own", "moolatrikona"]:
                        score += 10
                        reasons.append(f"अधिष्ठाता ग्रह {ruler} का बलवान (उच्च/स्वराशि) होना (मजबूत मांग व गति)।")
                    elif r_pos.dignity in ["debilitated"]:
                        score -= 10
                        reasons.append(f"अधिष्ठाता ग्रह {ruler} का नीचस्थ होना (गिरावट या मंदी दबाव)।")

            score = min(98, max(12, score))

            if score >= 70:
                trend_status = "🔥 प्रबल तेजी (Strong Bullish)"
                badge_color = "#16A34A"
            elif score >= 55:
                trend_status = "📈 हल्की तेजी (Moderate Upward)"
                badge_color = "#2563EB"
            elif score <= 35:
                trend_status = "📉 मंदी का रुख (Bearish / Downward)"
                badge_color = "#DC2626"
            elif score <= 45:
                trend_status = "⚖️ सुस्त व संभलकर (Consolidation)"
                badge_color = "#D97706"
            else:
                trend_status = "↔️ सामान्य दायरा (Range-Bound / Neutral)"
                badge_color = "#475569"

            results.append({
                "commodity": item_name,
                "icon": info["icon"],
                "score": score,
                "trend": trend_status,
                "badge_color": badge_color,
                "description": info["description"],
                "sensitive_nakshatras": ", ".join(info["nakshatras"]),
                "reasons": reasons if reasons else ["गोचर में कोई तात्कालिक वेध नहीं, सामान्य व्यापार दायरा।"]
            })

        return results

    @classmethod
    def evaluate_personal_wealth_and_trading(cls, natal_chart: KundaliChart) -> Dict[str, Any]:
        """
        Evaluates natal chart for stock market, intraday trading, long-term wealth,
        real estate, and speculative windfall luck.
        """
        planets = natal_chart.planets
        lagna_sign_id = natal_chart.lagna_sign_id

        def get_h_lord(h_num: int) -> str:
            s_id = ((lagna_sign_id - 1 + (h_num - 1)) % 12) + 1
            return SIGN_LORDS[SIGN_NAMES[s_id - 1]]

        l1 = get_h_lord(1)
        l2 = get_h_lord(2)   # Dhana
        l5 = get_h_lord(5)   # Speculation
        l8 = get_h_lord(8)   # Sudden gains
        l9 = get_h_lord(9)   # Fortune
        l11 = get_h_lord(11) # Labha
        l4 = get_h_lord(4)   # Property/Real Estate

        # 1. Day Trading / Intraday / Speculation (Houses 5, 8, Mercury, Mars)
        day_trading_score = 35
        # 5th lord in Kendra/Trikona
        if planets[l5].house_from_lagna in [1, 4, 5, 7, 9, 10, 11]:
            day_trading_score += 20
        # Mercury (Calculation/Speed) dignity
        if planets["Mercury"].dignity in ["exalted", "own", "moolatrikona", "friend"]:
            day_trading_score += 15
        # Mars (Risk taking & courage) strong
        if planets["Mars"].dignity in ["exalted", "own", "moolatrikona"]:
            day_trading_score += 15
        # Rahu in 3, 6, 10, 11 (Street smart / Speculative boldness)
        if planets["Rahu"].house_from_lagna in [3, 6, 10, 11]:
            day_trading_score += 15
        # Malefic in 5th without benefic aspect reduces trading discipline
        if planets["Saturn"].house_from_lagna == 5 or planets["Ketu"].house_from_lagna == 5:
            day_trading_score -= 15
        day_trading_score = min(96, max(15, day_trading_score))

        # 2. Long-term Investing / Value Assets (Houses 2, 9, 11, Jupiter, Saturn)
        long_term_score = 40
        if planets[l2].house_from_lagna in [1, 2, 4, 5, 9, 10, 11]:
            long_term_score += 20
        if planets[l11].house_from_lagna in [1, 2, 5, 9, 11]:
            long_term_score += 20
        if planets["Jupiter"].dignity in ["exalted", "own", "moolatrikona", "friend"]:
            long_term_score += 15
        if planets["Saturn"].house_from_lagna in [3, 6, 10, 11] or planets["Saturn"].dignity in ["exalted", "own"]:
            long_term_score += 10
        long_term_score = min(98, max(20, long_term_score))

        # 3. Real Estate & Land Wealth (Houses 4, Mars, Saturn)
        property_score = 35
        if planets[l4].house_from_lagna in [1, 4, 5, 9, 10, 11]:
            property_score += 25
        if planets["Mars"].dignity in ["exalted", "own", "moolatrikona", "friend"]:
            property_score += 20
        if planets["Saturn"].dignity in ["exalted", "own", "friend"]:
            property_score += 15
        property_score = min(96, max(20, property_score))

        # 4. Gold & Sovereign Assets (Houses 2, Sun, Jupiter)
        gold_score = 35
        if planets["Sun"].dignity in ["exalted", "own", "moolatrikona", "friend"]:
            gold_score += 25
        if planets["Jupiter"].dignity in ["exalted", "own", "friend"]:
            gold_score += 25
        if planets[l2].dignity in ["exalted", "own"]:
            gold_score += 15
        gold_score = min(98, max(20, gold_score))

        # Strategic advice
        advice = []
        if day_trading_score >= 70:
            advice.append("✅ **डे ट्रेडिंग / इंट्राडे:** आपकी बुद्धि तीव्र व निर्णय क्षमता गणनात्मक है। तकनीकी विश्लेषण पर आधारित अल्पकालिक ट्रेडिंग फलदायी रहेगी।")
        else:
            advice.append("⚠️ **इंट्राडे ट्रेडिंग में संयम रखें:** ५वें/८वें भाव का स्वभाव दीर्घकालिक संपत्ति निर्माण हेतु अधिक अनुकूल है। सट्टा प्रवृत्ति से बचें।")

        if long_term_score >= 70:
            advice.append("🌟 **दीर्घकालिक निवेश (Mutual Funds / Equities):** २रे व ११वें भाव का उत्तम बल दर्शाता है कि धैर्यपूर्वक किया गया संचय विशाल धन योग बनाएगा।")

        if property_score >= 65:
            advice.append("🏛️ **भूमि व अचल संपत्ति:** चतुर्थेश व मंगल की स्थिति भूमि, भवन एवं रियल एस्टेट में सुरक्षित व निरंतर मूल्य-वृद्धि का संकेत देती है।")

        if gold_score >= 65:
            advice.append("🪙 **स्वर्ण एवं सॉवरेन बॉन्ड:** सूर्य-गुरु की कृपा से सोने में निवेश संकट काल में सर्वोत्तम सुरक्षा एवं लक्ष्मी कृपा प्रदान करेगा।")

        return {
            "day_trading_score": day_trading_score,
            "long_term_score": long_term_score,
            "property_score": property_score,
            "gold_score": gold_score,
            "dhana_lords": {
                "2nd_lord_dhana": l2,
                "5th_lord_speculation": l5,
                "8th_lord_windfall": l8,
                "9th_lord_fortune": l9,
                "11th_lord_gains": l11,
            },
            "strategic_advice": advice
        }


default_financial_service = FinancialAstrologyService()
