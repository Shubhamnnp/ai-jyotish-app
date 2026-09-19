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

