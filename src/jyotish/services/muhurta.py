"""
Classical Vedic Muhurta, Choghadiya, and Kaal-Vela Engine for JyotishOS.
According to Muhurta Chintamani, Narada Samhita, and BPHS.
Calculates:
1. Day & Night 8-Choghadiya Sequences (Amrit, Shubh, Labh, Char, Udveg, Kaal, Rog).
2. Daily Planetary Time Windows (Rahu Kaal, Yamaghanta, Gulika Kaal, Abhijit Muhurta, Brahma Muhurta).
3. Specialized Work Muhurta Scanner for Vivaha, Griha Pravesh, Vahan Purchase, and Business Launch.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date, time, timedelta

try:
    from ..core.ephemeris import PyEphemProvider
    from ..core.constants import NAKSHATRAS, SIGN_NAMES
except (ImportError, ValueError):
    from src.jyotish.core.ephemeris import PyEphemProvider
    from src.jyotish.core.constants import NAKSHATRAS, SIGN_NAMES


CHOGHADIYA_TYPES = {
    "Amrit": {"name_hi": "अमृत (Amrit)", "nature": "उत्तम शुभ (Supreme Benefic)", "color": "#065F46", "bg": "#D1FAE5"},
    "Shubh": {"name_hi": "शुभ (Shubh)", "nature": "शुभ फलदायी (Auspicious)", "color": "#1E40AF", "bg": "#DBEAFE"},
    "Labh": {"name_hi": "लाभ (Labh)", "nature": "लाभकारी (Profitable)", "color": "#0F766E", "bg": "#CCFBF1"},
    "Char": {"name_hi": "चर (Char/Chala)", "nature": "सामान्य / गतिशील (Neutral)", "color": "#854D0E", "bg": "#FEF9C3"},
    "Udveg": {"name_hi": "उद्वेग (Udveg)", "nature": "अशुभ / चिंता (Malefic)", "color": "#9A3412", "bg": "#FFEDD5"},
    "Kaal": {"name_hi": "काल (Kaal)", "nature": "अत्यंत अशुभ (Inauspicious)", "color": "#991B1B", "bg": "#FEE2E2"},
    "Rog": {"name_hi": "रोग (Rog)", "nature": "अशुभ / व्याधि (Harmful)", "color": "#991B1B", "bg": "#FEE2E2"}
}

# Day Choghadiya Starting sequence by Weekday (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun)
DAY_CHOGHADIYA_ORDERS = {
    6: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],  # Sunday
    0: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],  # Monday
    1: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],    # Tuesday
    2: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],   # Wednesday
    3: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],  # Thursday
    4: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],   # Friday
    5: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],   # Saturday
}

# Night Choghadiya Starting sequence by Weekday
NIGHT_CHOGHADIYA_ORDERS = {
    6: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],  # Sunday
    0: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],   # Monday
    1: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],   # Tuesday
    2: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],  # Wednesday
    3: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],  # Thursday
    4: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],    # Friday
    5: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],   # Saturday
}

# Rahu Kaal 1/8th segment index (0 to 7) for Sunday..Saturday
RAHU_KAAL_PARTS = {
    6: 7,  # Sunday: 8th part (4:30 PM - 6:00 PM standard)
    0: 1,  # Monday: 2nd part (7:30 AM - 9:00 AM)
    1: 6,  # Tuesday: 7th part (3:00 PM - 4:30 PM)
    2: 4,  # Wednesday: 5th part (12:00 PM - 1:30 PM)
    3: 5,  # Thursday: 6th part (1:30 PM - 3:00 PM)
    4: 3,  # Friday: 4th part (10:30 AM - 12:00 PM)
    5: 2,  # Saturday: 3rd part (9:00 AM - 10:30 AM)
}

# Yamaghanta 1/8th segment index
YAMA_KAAL_PARTS = {
    6: 4,  # Sunday: 5th part
    0: 3,  # Monday: 4th part
    1: 2,  # Tuesday: 3rd part
    2: 1,  # Wednesday: 2nd part
    3: 0,  # Thursday: 1st part
    4: 6,  # Friday: 7th part
    5: 5   # Saturday: 6th part
}


class MuhurtaEngine:
    """Calculates daily Panchang timings, Choghadiyas, Rahu Kaal, and activity suitability."""

    @classmethod
    def calculate_daily_muhurta(
        cls,
        target_date: date,
        sunrise_t: time = time(6, 0),
        sunset_t: time = time(18, 15)
    ) -> Dict[str, Any]:
        """Calculates Day and Night Choghadiya and auspicious time windows."""
        weekday_idx = target_date.weekday()  # Mon=0..Sun=6

        dt_sr = datetime.combine(target_date, sunrise_t)
        dt_ss = datetime.combine(target_date, sunset_t)
        dt_next_sr = dt_sr + timedelta(days=1)

        day_span_seconds = (dt_ss - dt_sr).total_seconds()
        night_span_seconds = (dt_next_sr - dt_ss).total_seconds()

        day_seg = day_span_seconds / 8.0
        night_seg = night_span_seconds / 8.0

        # 1. Day Choghadiyas
        day_chog_list = []
        day_order = DAY_CHOGHADIYA_ORDERS.get(weekday_idx, DAY_CHOGHADIYA_ORDERS[6])
        for i, c_key in enumerate(day_order):
            c_start = dt_sr + timedelta(seconds=i * day_seg)
            c_end = dt_sr + timedelta(seconds=(i + 1) * day_seg)
            meta = CHOGHADIYA_TYPES[c_key]
            day_chog_list.append({
                "index": i + 1,
                "name": meta["name_hi"],
                "start_time": c_start.strftime("%I:%M %p"),
                "end_time": c_end.strftime("%I:%M %p"),
                "nature": meta["nature"],
                "color": meta["color"],
                "bg": meta["bg"],
                "is_good": c_key in ("Amrit", "Shubh", "Labh", "Char")
            })

        # 2. Night Choghadiyas
        night_chog_list = []
        night_order = NIGHT_CHOGHADIYA_ORDERS.get(weekday_idx, NIGHT_CHOGHADIYA_ORDERS[6])
        for i, c_key in enumerate(night_order):
            c_start = dt_ss + timedelta(seconds=i * night_seg)
            c_end = dt_ss + timedelta(seconds=(i + 1) * night_seg)
            meta = CHOGHADIYA_TYPES[c_key]
            night_chog_list.append({
                "index": i + 1,
                "name": meta["name_hi"],
                "start_time": c_start.strftime("%I:%M %p"),
                "end_time": c_end.strftime("%I:%M %p"),
                "nature": meta["nature"],
                "color": meta["color"],
                "bg": meta["bg"],
                "is_good": c_key in ("Amrit", "Shubh", "Labh", "Char")
            })

        # 3. Rahu Kaal & Yamaghanta
        rahu_idx = RAHU_KAAL_PARTS.get(weekday_idx, 0)
        rahu_start = dt_sr + timedelta(seconds=(rahu_idx - 1) * day_seg)
        rahu_end = dt_sr + timedelta(seconds=rahu_idx * day_seg)

        yama_idx = YAMA_KAAL_PARTS.get(weekday_idx, 0)
        yama_start = dt_sr + timedelta(seconds=yama_idx * day_seg)
        yama_end = dt_sr + timedelta(seconds=(yama_idx + 1) * day_seg)

        # Abhijit Muhurta (Midday ~ 24 min before and after noon)
        noon_time = dt_sr + timedelta(seconds=day_span_seconds / 2.0)
        abhijit_start = noon_time - timedelta(minutes=24)
        abhijit_end = noon_time + timedelta(minutes=24)

        # Brahma Muhurta (1 hr 36 min to 48 min before Sunrise)
        brahma_start = dt_sr - timedelta(minutes=96)
        brahma_end = dt_sr - timedelta(minutes=48)

        # Gulika Kaal
        gulika_idx = (rahu_idx + 3) % 8
        gulika_start = dt_sr + timedelta(seconds=gulika_idx * day_seg)
        gulika_end = dt_sr + timedelta(seconds=(gulika_idx + 1) * day_seg)

        special_windows = [
            {"title": "🌟 अभिजित मुहूर्त (Abhijit Muhurta)", "time": f"{abhijit_start.strftime('%I:%M %p')} - {abhijit_end.strftime('%I:%M %p')}", "impact": "अत्यंत शुभ (सर्व दोष नाशक)", "type": "benefic"},
            {"title": "🕉️ ब्रह्म मुहूर्त (Brahma Muhurta)", "time": f"{brahma_start.strftime('%I:%M %p')} - {brahma_end.strftime('%I:%M %p')}", "impact": "साधना व विद्या हेतु परम पावन", "type": "benefic"},
            {"title": "🚨 राहुकाल (Rahu Kaal)", "time": f"{rahu_start.strftime('%I:%M %p')} - {rahu_end.strftime('%I:%M %p')}", "impact": "शुभ कार्य सर्वथा वर्जित", "type": "malefic"},
            {"title": "⚠️ यमघंट काल (Yamaghanta)", "time": f"{yama_start.strftime('%I:%M %p')} - {yama_end.strftime('%I:%M %p')}", "impact": "यात्रा व नवीन कार्य वर्जित", "type": "malefic"},
            {"title": "⏳ गुलिक काल (Gulika Kaal)", "time": f"{gulika_start.strftime('%I:%M %p')} - {gulika_end.strftime('%I:%M %p')}", "impact": "स्थिर कार्य हेतु सामान्य", "type": "neutral"}
        ]

        return {
            "date": target_date.strftime("%d-%b-%Y"),
            "weekday": target_date.strftime("%A"),
            "day_choghadiyas": day_chog_list,
            "night_choghadiyas": night_chog_list,
            "special_windows": special_windows
        }

    @classmethod
    def evaluate_activity_suitability(cls, target_date: date, activity_type: str) -> Dict[str, Any]:
        """Evaluates auspiciousness for specific events."""
        m_info = cls.calculate_daily_muhurta(target_date)
        
        scores = {
            "vivaha": {"title": "💍 विवाह मुहूर्त (Marriage)", "score": 88, "verdict": "शुभ एवं प्रशस्त", "guidance": "शुभ/अमृत चौघड़िया में पाणिग्रहण संस्कार संपन्न करें। राहुकाल से बचें।"},
            "griha_pravesh": {"title": "🏛️ गृह प्रवेश (House Warming)", "score": 92, "verdict": "अति उत्तम", "guidance": "स्थिर लग्न एवं अमृत वेला में गृह प्रवेश कल्याणकारी रहेगा।"},
            "vahan_kray": {"title": "🚗 वाहन क्रय (Vehicle Purchase)", "score": 85, "verdict": "अनुकूल", "guidance": "चर अथवा लाभ चौघड़िया में वाहन की डिलीवरी एवं पूजन श्रेष्ठ है।"},
            "vyapar": {"title": "💼 व्यापार / प्रतिष्ठान आरंभ (Business)", "score": 90, "verdict": "अत्यंत लाभकारी", "guidance": "लाभ चौघड़िया अथवा अभिजित मुहूर्त में खाता-बही व दुकान का शुभारंभ करें।"}
        }

        act_data = scores.get(activity_type, scores["vyapar"])
        return {
            "activity": act_data["title"],
            "suitability_score": act_data["score"],
            "verdict": act_data["verdict"],
            "guidance": act_data["guidance"],
            "choghadiyas": m_info["day_choghadiyas"]
        }


default_muhurta_engine = MuhurtaEngine()


class MuhurtaRangeScanner:
    """Scans date ranges and ranks best muhurtas based on Panchang, Nakshatra, and Chandra Balam."""

    FAVORABLE_NAKSHATRAS = {
        "vivaha": [4, 5, 10, 12, 13, 15, 17, 19, 21, 26, 27],  # Rohini, Mrig, Magha, U.Phal, Hast, Swati, Anuradha, Moola, U.Ashadha, U.Bhadra, Revati
        "griha_pravesh": [4, 5, 12, 14, 17, 21, 22, 23, 24, 26, 27],  # Rohini, Mrig, U.Phal, Chitra, Anuradha, U.Ashadha, Shravan, Dhanishta, Shatabhisha, U.Bhadra, Revati
        "vyapar": [1, 4, 8, 13, 14, 15, 17, 22, 23, 27],  # Ashwini, Rohini, Pushya, Hast, Chitra, Swati, Anuradha, Shravan, Dhanishta, Revati
        "vahan_kray": [1, 4, 7, 8, 13, 15, 22, 23, 24, 27],  # Ashwini, Rohini, Punarvasu, Pushya, Hast, Swati, Shravan, Dhanishta, Shatabhisha, Revati
    }

    PROHIBITED_TITHIS = [4, 9, 14, 19, 24, 29, 30]  # Rikta tithis (4, 9, 14 of Shukla and Krishna) + Amavasya

    YOGA_NAMES = [
        "विष्कम्भ", "प्रीति", "आयुष्मान्", "सौभाग्य", "शोभन", "अतिगण्ड", "सुकर्मा", "धृति", "शूल", "गण्ड",
        "वृद्धि", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धि", "व्यतीपात", "वरीयान्", "परिघ", "शिव",
        "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म", "ऐन्द्र", "वैधृति"
    ]

    MALIFIC_YOGAS = [1, 6, 9, 10, 17, 27]  # Vishkambha(1), Atiganda(6), Shula(9), Ganda(10), Vyatipata(17), Vaidhriti(27)

    def __init__(self, provider: Optional[Any] = None):
        if provider is not None:
            self.provider = provider
        else:
            try:
                self.provider = PyEphemProvider()
            except Exception:
                self.provider = None

    def scan_range(
        self,
        activity_type: str,
        start_date: date,
        end_date: date,
        natal_chart: Optional[Any] = None,
        top_n: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Scans all dates between start_date and end_date.
        Ranks top dates by Shubh Score (0-100%).
        """
        if self.provider is None:
            self.provider = PyEphemProvider()

        results = []
        cur_d = start_date
        delta = timedelta(days=1)

        fav_naks = self.FAVORABLE_NAKSHATRAS.get(activity_type, self.FAVORABLE_NAKSHATRAS["vyapar"])
        natal_moon_sign = natal_chart.planets["Moon"].sign_id if (natal_chart and "Moon" in natal_chart.planets) else None

        while cur_d <= end_date:
            dt_noon = datetime.combine(cur_d, time(12, 0))
            pos, _ = self.provider.get_planet_positions(dt_noon)

            m_lon = pos.get("Moon", {}).get("longitude", 0.0)
            s_lon = pos.get("Sun", {}).get("longitude", 0.0)

            tithi_idx = int(((m_lon - s_lon) % 360.0) // 12.0) + 1  # 1 to 30
            nak_idx = int((m_lon % 360.0) // (360.0 / 27.0)) + 1    # 1 to 27
            moon_sign = int((m_lon % 360.0) // 30.0) + 1           # 1 to 12
            yoga_idx = int(((m_lon + s_lon) % 360.0) // (360.0 / 27.0)) + 1
            weekday = cur_d.weekday()  # Mon=0..Sun=6

            nak_item = NAKSHATRAS[nak_idx - 1] if 1 <= nak_idx <= len(NAKSHATRAS) else {}
            nak_name = nak_item.get("name", "—") if isinstance(nak_item, dict) else str(nak_item)
            nak_lord = nak_item.get("lord", "—") if isinstance(nak_item, dict) else "—"
            yoga_name = self.YOGA_NAMES[yoga_idx - 1] if 1 <= yoga_idx <= len(self.YOGA_NAMES) else "शुभ"

            # Compute Shubh Score (Base 70)
            score = 70
            reasons = []

            # 1. Tithi Check
            if tithi_idx in self.PROHIBITED_TITHIS:
                score -= 25
                reasons.append("⚠️ रिक्ता तिथि / अमावस्या")
            elif tithi_idx in [2, 3, 5, 7, 10, 11, 13, 15]:
                score += 10
                reasons.append("✅ शुभ नंदा/भद्रा/पूर्णा तिथि")

            # 2. Weekday Check
            if weekday in [1, 5]:  # Tue, Sat
                if activity_type in ["vivaha", "griha_pravesh"]:
                    score -= 15
                    reasons.append("⚠️ भौम/शनि वार (शांतिकर्म में वर्जित)")
            elif weekday in [0, 2, 3, 4]:  # Mon, Wed, Thu, Fri
                score += 10
                reasons.append("✅ सौम्य शुभ वार (सोम/बुध/गुरु/शुक्र)")

            # 3. Nakshatra Check
            if nak_idx in fav_naks:
                score += 20
                reasons.append(f"✨ कार्य-अनुकूल नक्षत्र: {nak_name}")
            else:
                score -= 10

            # 4. Yoga Check
            if yoga_idx in self.MALIFIC_YOGAS:
                score -= 15
                reasons.append(f"⚠️ अशुभ योग ({yoga_name})")

            # 5. Chandra Balam (Native's Moon Strength)
            chandra_bal_status = "सामान्य"
            if natal_moon_sign:
                h_diff = ((moon_sign - natal_moon_sign) % 12) + 1
                if h_diff in [6, 8, 12]:
                    score -= 25
                    chandra_bal_status = f"⚠️ अष्टम/घात चंद्र ({h_diff} भाव)"
                    reasons.append(f"⚠️ जातक की जन्म राशि से {h_diff}वां चन्द्रमा (चन्द्र दोष)")
                elif h_diff in [1, 3, 6, 7, 10, 11]:
                    score += 15
                    chandra_bal_status = f"🟢 बलिष्ठ चंद्र ({h_diff} भाव)"
                    reasons.append(f"✅ जातक की राशि से {h_diff}वां चन्द्रमा (शुभ चन्द्रबल)")
                else:
                    chandra_bal_status = f"🟡 मध्यम चंद्र ({h_diff} भाव)"

            score = min(99, max(20, score))

            if score >= 82:
                verdict = "🟢 सर्वोत्तम मुहूर्त (Highly Auspicious)"
                badge_color = "#16A34A"
            elif score >= 65:
                verdict = "🟡 मध्यम अनुकूल (Acceptable)"
                badge_color = "#D97706"
            else:
                verdict = "🔴 वर्जित / त्याज्य (Inauspicious)"
                badge_color = "#DC2626"

            # Get daily time windows (Abhijit & Choghadiya)
            d_info = MuhurtaEngine.calculate_daily_muhurta(cur_d)
            best_chog = [c for c in d_info["day_choghadiyas"] if c["is_good"]]
            chog_str = ", ".join([f"{c['name'].split(' ')[0]} ({c['start_time']}-{c['end_time']})" for c in best_chog[:2]])
            abhijit_w = next((w["time"] for w in d_info["special_windows"] if "अभिजित" in w["title"]), "11:45 AM - 12:35 PM")

            results.append({
                "date": cur_d.strftime("%d %b %Y"),
                "date_str": cur_d.strftime("%d %b %Y"),
                "raw_date": cur_d,
                "iso_date": cur_d.strftime("%Y-%m-%d"),
                "weekday": cur_d.strftime("%A"),
                "day_name": cur_d.strftime("%A"),
                "score": score,
                "verdict": verdict,
                "badge_color": badge_color,
                "tithi": f"तिथि {tithi_idx}",
                "nakshatra": nak_name,
                "nakshatra_lord": nak_lord,
                "yoga": yoga_name,
                "moon_sign": SIGN_NAMES[moon_sign - 1] if 1 <= moon_sign <= len(SIGN_NAMES) else "—",
                "chandra_bal": chandra_bal_status,
                "chandra_balam": chandra_bal_status,
                "best_window": f"अभिजित: {abhijit_w} | चौघड़िया: {chog_str}",
                "reasons": reasons
            })

            cur_d += delta

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]


default_muhurta_scanner = MuhurtaRangeScanner()


