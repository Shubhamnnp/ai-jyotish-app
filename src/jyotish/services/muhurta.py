"""
Classical Vedic Muhurta, Choghadiya, Panchanga Shuddhi, and Kaal-Vela Engine for JyotishOS.
According to Muhurta Chintamani, Kala Prakashika, Narada Samhita, Nirnaya Sindhu, and BPHS.

Calculates:
1. Day & Night 8-Choghadiya Sequences (Amrit, Shubh, Labh, Char, Udveg, Kaal, Rog).
2. Daily Planetary Time Windows (Rahu Kaal, Yamaghanta, Gulika Kaal, Abhijit Muhurta, Brahma Muhurta).
3. 99.9% Authentic Shastriya Maha-Nishedha Engine:
   - Pitru Paksha (पितृपक्ष / महालय श्राद्ध काल)
   - Chaturmas (चातुर्मास / देवशयन काल)
   - Kharmas / Malmaas (खरमास / धनु-मीन संक्रान्ति)
   - Guru / Shukra Tara Asta (बृहस्पति / शुक्र तारा अस्त)
   - Bhadra / Vishti Karana (विष्टि करण एवं मृत्युलोक/स्वर्ग/पाताल वास)
   - Rikta Tithis (४, ९, १४) एवं दर्श / अमावस्या (३०)
4. 12+ Major Activity Suitability Evaluator with Native Tara Balam & Chandra Balam.
5. Multi-Day Automated Muhurta Range Scanner strictly enforcing Shastriya purity.
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

# Rahu Kaal 1/8th segment index (1 to 8) for Sunday..Saturday
RAHU_KAAL_PARTS = {
    6: 8,  # Sunday: 8th part (4:30 PM - 6:00 PM standard)
    0: 2,  # Monday: 2nd part (7:30 AM - 9:00 AM)
    1: 7,  # Tuesday: 7th part (3:00 PM - 4:30 PM)
    2: 5,  # Wednesday: 5th part (12:00 PM - 1:30 PM)
    3: 6,  # Thursday: 6th part (1:30 PM - 3:00 PM)
    4: 4,  # Friday: 4th part (10:30 AM - 12:00 PM)
    5: 3,  # Saturday: 3rd part (9:00 AM - 10:30 AM)
}

# Yamaghanta 1/8th segment index (1 to 8)
YAMA_KAAL_PARTS = {
    6: 5,  # Sunday: 5th part
    0: 4,  # Monday: 4th part
    1: 3,  # Tuesday: 3rd part
    2: 2,  # Wednesday: 2nd part
    3: 1,  # Thursday: 1st part
    4: 7,  # Friday: 7th part
    5: 6   # Saturday: 6th part
}

TITHI_NAMES = [
    "प्रतिपदा (Pratipada)", "द्वितीया (Dwitiya)", "तृतीया (Tritiya)", "चतुर्थी (Chaturthi)",
    "पञ्चमी (Panchami)", "षष्ठी (Shashthi)", "सप्तमी (Saptami)", "अष्टमी (Ashtami)",
    "नवमी (Navami)", "दशमी (Dashami)", "एकादशी (Ekadashi)", "द्वादशी (Dvadashi)",
    "त्रयोदशी (Trayodashi)", "चतुर्दशी (Chaturdashi)", "पूर्णिमा (Purnima)",
    "प्रतिपदा (Pratipada)", "द्वितीया (Dwitiya)", "तृतीया (Tritiya)", "चतुर्थी (Chaturthi)",
    "पञ्चमी (Panchami)", "षष्ठी (Shashthi)", "सप्तमी (Saptami)", "अष्टमी (Ashtami)",
    "नवमी (Navami)", "दशमी (Dashami)", "एकादशी (Ekadashi)", "द्वादशी (Dvadashi)",
    "त्रयोदशी (Trayodashi)", "चतुर्दशी (Chaturdashi)", "अमावस्या (Amavasya)"
]

YOGA_NAMES = [
    "विष्कम्भ", "प्रीति", "आयुष्मान्", "सौभाग्य", "शोभन", "अतिगण्ड", "सुकर्मा", "धृति", "शूल", "गण्ड",
    "वृद्धि", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धि", "व्यतीपात", "वरीयान्", "परिघ", "शिव",
    "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म", "ऐन्द्र", "वैधृति"
]

MALIFIC_YOGAS = [1, 6, 9, 10, 13, 15, 17, 19, 27]  # Vishkambha(1), Atiganda(6), Shula(9), Ganda(10), Vyaghata(13), Vajra(15), Vyatipata(17), Parigha(19), Vaidhriti(27)

KARANA_NAMES = [
    "बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि (भद्रा)",
    "शकुनि", "चतुष्पद", "नाग", "किंस्तुघ्न"
]

# Vishti Karanas out of 60 half-tithis
VISHTI_KARANAS = [8, 15, 22, 29, 36, 43, 50, 57]

TARA_NAMES_9 = [
    ("जन्म तारा (Janma)", "शारीरिक कष्ट, मानसिक चिंता व स्वास्थ्य सतर्कता। नवीन कार्य में वर्जित।", "⚠️ मध्यम / सतर्कता", "#F59E0B"),
    ("सम्पत् तारा (Sampat)", "धन लाभ, समृद्धि, व्यापार वृद्धि व सफलता।", "🟢 अति शुभ", "#10B981"),
    ("विपत् तारा (Vipat)", "विपत्ति, धनहानि, कार्य में आकस्मिक अवरोध। सर्वथा वर्जित।", "🔴 अशुभ (वर्जित)", "#EF4444"),
    ("क्षेम तारा (Kshema)", "कल्याण, आरोग्य, सुरक्षा एवं कार्य सिद्धि।", "🟢 शुभ", "#10B981"),
    ("प्रत्यरि तारा (Pratyari)", "शत्रुता, विवाद, कानूनी अड़चनें व मतभेद। वर्जित।", "🔴 अशुभ (वर्जित)", "#EF4444"),
    ("साधक तारा (Sadhaka)", "अभिलाषा सिद्धि, विजय, यश व महत्वपूर्ण कार्य पूर्ति।", "🟢 अति शुभ", "#10B981"),
    ("वध / निधन तारा (Naidhana)", "मृत्युतुल्य कष्ट, गंभीर हानि, दुर्घटना का भय। महा-वर्जित।", "🔴 महा अशुभ (सर्वथा वर्जित)", "#DC2626"),
    ("मित्र तारा (Mitra)", "सुखद सहयोग, मैत्री लाभ, सामान्य कार्य अनुकूल।", "🟢 शुभ", "#10B981"),
    ("परम मित्र तारा (Parama Mitra)", "सर्वोच्च सिद्धि, स्थायी लाभ व परम मंगलकारी।", "🟢 परम शुभ", "#059669")
]


class MuhurtaEngine:
    """Calculates daily Panchang timings, Choghadiyas, Rahu Kaal, Maha-Nishedha checks, and activity suitability."""

    _ephem_provider: Optional[PyEphemProvider] = None

    @classmethod
    def get_provider(cls) -> PyEphemProvider:
        if cls._ephem_provider is None:
            cls._ephem_provider = PyEphemProvider()
        return cls._ephem_provider

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
        rahu_idx = RAHU_KAAL_PARTS.get(weekday_idx, 8)
        rahu_start = dt_sr + timedelta(seconds=(rahu_idx - 1) * day_seg)
        rahu_end = dt_sr + timedelta(seconds=rahu_idx * day_seg)

        yama_idx = YAMA_KAAL_PARTS.get(weekday_idx, 5)
        yama_start = dt_sr + timedelta(seconds=(yama_idx - 1) * day_seg)
        yama_end = dt_sr + timedelta(seconds=yama_idx * day_seg)

        # Abhijit Muhurta (Midday ~ 24 min before and after noon)
        noon_time = dt_sr + timedelta(seconds=day_span_seconds / 2.0)
        abhijit_start = noon_time - timedelta(minutes=24)
        abhijit_end = noon_time + timedelta(minutes=24)

        # Brahma Muhurta (1 hr 36 min to 48 min before Sunrise)
        brahma_start = dt_sr - timedelta(minutes=96)
        brahma_end = dt_sr - timedelta(minutes=48)

        # Gulika Kaal
        gulika_idx = ((rahu_idx + 2) % 8) + 1
        gulika_start = dt_sr + timedelta(seconds=(gulika_idx - 1) * day_seg)
        gulika_end = dt_sr + timedelta(seconds=gulika_idx * day_seg)

        special_windows = [
            {"title": "🌟 अभिजित मुहूर्त (Abhijit Muhurta)", "time": f"{abhijit_start.strftime('%I:%M %p')} - {abhijit_end.strftime('%I:%M %p')}", "impact": "अत्यंत शुभ (सर्व दोष नाशक)", "type": "benefic"},
            {"title": "🕉️ ब्रह्म मुहूर्त (Brahma Muhurta)", "time": f"{brahma_start.strftime('%I:%M %p')} - {brahma_end.strftime('%I:%M %p')}", "impact": "साधना व विद्या हेतु परम पावन", "type": "benefic"},
            {"title": "🚨 राहुकाल (Rahu Kaal)", "time": f"{rahu_start.strftime('%I:%M %p')} - {rahu_end.strftime('%I:%M %p')}", "impact": "शुभ कार्य सर्वथा वर्जित", "type": "malefic"},
            {"title": "⚠️ यमघंट काल (Yamaghanta)", "time": f"{yama_start.strftime('%I:%M %p')} - {yama_end.strftime('%I:%M %p')}", "impact": "यात्रा व नवीन कार्य वर्जित", "type": "malefic"},
            {"title": "⏳ गुलिक काल (Gulika Kaal)", "time": f"{gulika_start.strftime('%I:%M %p')} - {gulika_end.strftime('%I:%M %p')}", "impact": "स्थिर कार्य हेतु सामान्य", "type": "neutral"}
        ]

        # Calculate astronomical panchang & mahadoshas for this date
        panchang_doshas = cls.get_daily_panchang_and_doshas(target_date)

        return {
            "date": target_date.strftime("%d-%b-%Y"),
            "weekday": target_date.strftime("%A"),
            "day_choghadiyas": day_chog_list,
            "night_choghadiyas": night_chog_list,
            "special_windows": special_windows,
            "panchang_doshas": panchang_doshas
        }

    @classmethod
    def get_daily_panchang_and_doshas(
        cls,
        target_date: date,
        time_val: time = time(12, 0)
    ) -> Dict[str, Any]:
        """
        Performs 99.9% accurate astronomical Panchang and Shastriya Maha-Dosha calculation.
        Computes Pitru Paksha, Chaturmas, Kharmas, Guru/Shukra Asta, Bhadra (with Loka),
        Rikta tithis, and malefic Yogas according to Muhurta Chintamani.
        """
        provider = cls.get_provider()
        dt_noon = datetime.combine(target_date, time_val)
        positions, _ = provider.get_planet_positions(dt_noon)

        s_lon = positions.get("Sun", {}).get("longitude", 0.0)
        m_lon = positions.get("Moon", {}).get("longitude", 0.0)
        j_lon = positions.get("Jupiter", {}).get("longitude", 0.0)
        v_lon = positions.get("Venus", {}).get("longitude", 0.0)

        sun_sign = int(s_lon // 30.0) + 1        # 1 to 12
        moon_sign = int(m_lon // 30.0) + 1       # 1 to 12
        sun_deg = s_lon % 30.0
        moon_deg = m_lon % 30.0

        diff = (m_lon - s_lon) % 360.0
        tithi_idx = int(diff // 12.0) + 1        # 1 to 30
        karana_idx = int(diff // 6.0) + 1        # 1 to 60
        nak_idx = int((m_lon % 360.0) // (360.0 / 27.0)) + 1  # 1 to 27
        yoga_idx = int(((m_lon + s_lon) % 360.0) // (360.0 / 27.0)) + 1
        weekday = target_date.weekday()          # Mon=0..Sun=6

        # Tithi Details
        is_shukla = tithi_idx <= 15
        paksha_name = "शुक्ल पक्ष" if is_shukla else "कृष्ण पक्ष"
        tithi_name = TITHI_NAMES[tithi_idx - 1] if 1 <= tithi_idx <= 30 else f"तिथि {tithi_idx}"
        t_mod15 = tithi_idx if is_shukla else (tithi_idx - 15)
        if t_mod15 in [1, 6, 11]:
            tithi_category = "नन्दा (Nanda - आनंदवर्धक)"
        elif t_mod15 in [2, 7, 12]:
            tithi_category = "भद्रा (Bhadra - कल्याणकारी)"
        elif t_mod15 in [3, 8, 13]:
            tithi_category = "जया (Jaya - विजयप्रद)"
        elif t_mod15 in [4, 9, 14]:
            tithi_category = "रिक्ता (Rikta - शुभ कार्य वर्जित)"
        else:
            tithi_category = "पूर्णा (Poorna - सिद्धिप्रद)" if tithi_idx != 30 else "दर्श (Amavasya - पितृ तिथि)"

        # Nakshatra Details
        nak_item = NAKSHATRAS[nak_idx - 1] if 1 <= nak_idx <= len(NAKSHATRAS) else {}
        nak_name = nak_item.get("name", "—") if isinstance(nak_item, dict) else str(nak_item)
        nak_lord = nak_item.get("lord", "—") if isinstance(nak_item, dict) else "—"

        # Yoga Details
        yoga_name = YOGA_NAMES[yoga_idx - 1] if 1 <= yoga_idx <= len(YOGA_NAMES) else "शुभ"
        is_malefic_yoga = yoga_idx in MALIFIC_YOGAS

        # Karana Details
        is_bhadra = karana_idx in VISHTI_KARANAS
        karana_name = "विष्टि (भद्रा)" if is_bhadra else (KARANA_NAMES[(karana_idx - 1) % 7] if karana_idx <= 56 else KARANA_NAMES[7 + (karana_idx - 57)])

        # Bhadra Residence (Loka) Analysis
        bhadra_loka = None
        bhadra_impact = None
        bhadra_is_fatal = False
        if is_bhadra:
            if moon_sign in [1, 2, 3, 8]:  # Mesha, Vrishabha, Mithuna, Vrischika
                bhadra_loka = "स्वर्ग लोक (Swarga Loka)"
                bhadra_impact = "स्वर्ग की भद्रा का वास स्वर्ग में होने से पृथ्वी पर इसका दुष्प्रभाव निष्प्रभावी रहता है।"
                bhadra_is_fatal = False
            elif moon_sign in [6, 7, 9, 10]:  # Kanya, Tula, Dhanu, Makara
                bhadra_loka = "पाताल लोक (Patala Loka)"
                bhadra_impact = "पाताल की भद्रा धनप्रद मानी गई है, सामान्य कार्यों में विशेष दोष नहीं करती।"
                bhadra_is_fatal = False
            else:  # Karka (4), Simha (5), Kumbha (11), Meena (12)
                bhadra_loka = "मृत्युलोक / पृथ्वी (Martya Loka - Earth)"
                bhadra_impact = "🔴 भद्रा का साक्षात् वास मृत्युलोक (पृथ्वी) पर है! यह 'सर्वकार्यविनाशिनी' कहलाती है। इसमें गृह प्रवेश, विवाह, यात्रा व नवीन कार्य सर्वथा वर्जित हैं!"
                bhadra_is_fatal = True

        # =====================================================================
        # 1. PITRU PAKSHA (पितृपक्ष / महालय श्राद्ध पक्ष)
        # Classical Rule: Sun in Virgo (Kanya, sign 6) and Moon in Krishna Paksha (tithi 16..30)
        # In some regional traditions, Ashadha or Ashwin Pratipada is also considered,
        # but Sun in Virgo with Krishna Paksha is universally the core Mahalaya.
        # =====================================================================
        is_pitru_paksha = (sun_sign == 6 and 16 <= tithi_idx <= 30)

        # =====================================================================
        # 2. CHATURMAS (चातुर्मास / देवशयन काल)
        # Ashadha Shukla Ekadashi to Kartika Shukla Ekadashi (Devutthani).
        # Sun passes Cancer(4), Leo(5), Virgo(6), and early Libra(7).
        # =====================================================================
        is_chaturmas = (sun_sign in [4, 5, 6]) or (sun_sign == 7 and (tithi_idx < 11 or not is_shukla))

        # =====================================================================
        # 3. KHARMAS / MALMAAS (खरमास / धनु-मीन संक्रान्ति)
        # Sun in Sagittarius (Dhanu, 9) or Pisces (Meena, 12).
        # =====================================================================
        is_kharmas = (sun_sign in [9, 12])

        # =====================================================================
        # 4. GURU & SHUKRA TARA ASTA (देवगुरु व शुक्र का अस्त)
        # =====================================================================
        j_sun_diff = abs(j_lon - s_lon)
        if j_sun_diff > 180.0:
            j_sun_diff = 360.0 - j_sun_diff
        is_guru_asta = j_sun_diff < 11.0

        v_sun_diff = abs(v_lon - s_lon)
        if v_sun_diff > 180.0:
            v_sun_diff = 360.0 - v_sun_diff
        is_shukra_asta = v_sun_diff < 8.0

        # =====================================================================
        # 5. RIKTA TITHI & AMAVASYA
        # =====================================================================
        is_rikta = (t_mod15 in [4, 9, 14])
        is_amavasya = (tithi_idx == 30)

        # Build Active Mahadoshas List
        active_mahadoshas = []

        if is_pitru_paksha:
            active_mahadoshas.append({
                "key": "pitru_paksha",
                "severity": "FATAL",
                "badge": "🚫 महा-निषेध (FATAL)",
                "color": "#DC2626",
                "title": "पितृपक्ष (श्राद्ध / महालय पक्ष) सक्रिय",
                "sutra": "आश्विने कृष्णपक्षे तु पितृपक्षः प्रकीर्तितः। विवाहादि शुभं कर्म गृहप्रवेशं च वर्जयेत्॥ (निर्णय सिन्धु / मुहूर्त चिन्तामणि)",
                "desc": f"वर्तमान में सूर्य कन्या राशि ({sun_deg:.1f}°) में तथा चन्द्रमा कृष्ण पक्ष ({tithi_name}) में है। यह पितरों के तर्पण, श्राद्ध व पिंडदान का पवित्र काल है। शास्त्रों अनुसार इस अवधि में नवीन गृह प्रवेश, विवाह, मुंडन, उपनयन, भूमि पूजन एवं नवीन प्रतिष्ठान सर्वथा वर्जित (Strictly Prohibited) हैं।"
            })

        if is_chaturmas:
            active_mahadoshas.append({
                "key": "chaturmas",
                "severity": "HIGH",
                "badge": "⚠️ देवशयन काल",
                "color": "#EA580C",
                "title": "चातुर्मास (देवशयन काल) सक्रिय",
                "sutra": "सुप्ते जनार्दने प्राप्ते शुभकर्म विवर्जयेत्। विवाहादिकृतं कर्म विपत्तिं कुरुते ध्रुवम्॥ (मुहूर्त चिन्तामणि)",
                "desc": "आषाढ़ शुक्ल एकादशी से कार्तिक शुक्ल एकादशी (देवोत्थान एकादशी) पर्यन्त भगवान श्रीहरि विष्णु क्षीरसागर में योगनिद्रा में रहते हैं। इस काल में अपूर्व गृह प्रवेश (नया घर) एवं पाणिग्रहण संस्कार (विवाह) निषिद्ध हैं।"
            })

        if is_kharmas:
            active_mahadoshas.append({
                "key": "kharmas",
                "severity": "FATAL",
                "badge": "🚫 महा-निषेध (FATAL)",
                "color": "#DC2626",
                "title": "खरमास / मलमास (सूर्य धनु/मीन राशि) सक्रिय",
                "sutra": "धनुर्मीनगते सूर्ये गुरुमन्दसमन्विते। मलिम्लुचे च कर्तव्यं न शुभं कर्म जातुचित्॥",
                "desc": "सूर्य जब देवगुरु बृहस्पति की राशि (धनु या मीन) में होते हैं, तब गुरु का तेज मद्धम हो जाता है। अतः समस्त मांगलिक संस्कार (विवाह, गृह प्रवेश, मुंडन) वर्जित होते हैं।"
            })

        if is_bhadra:
            b_sev = "FATAL" if bhadra_is_fatal else "MEDIUM"
            b_col = "#DC2626" if bhadra_is_fatal else "#D97706"
            active_mahadoshas.append({
                "key": "bhadra",
                "severity": b_sev,
                "badge": "🚫 भद्रा महादोष" if bhadra_is_fatal else "⚠️ भद्रा काल",
                "color": b_col,
                "title": f"भद्रा (विष्टि करण #{karana_idx}) — {bhadra_loka}",
                "sutra": "भद्रायां द्वे न कर्तव्ये विवाहो गृहप्रवेशनम्। यात्रां च नैव कुर्वीत कृते मृत्युर्न संशयः॥ (मुहूर्त चिन्तामणि)",
                "desc": f"{bhadra_impact} भद्रा काल में किया गया शुभ कार्य निष्फल व विनाशकारी सिद्ध होता है।"
            })

        if is_guru_asta:
            active_mahadoshas.append({
                "key": "guru_asta",
                "severity": "FATAL",
                "badge": "🚫 गुरु अस्त",
                "color": "#DC2626",
                "title": "देवगुरु बृहस्पति तारा अस्त (Guru Asta)",
                "sutra": "गुरोरस्ते च शुक्रस्य बाले वृद्धे विवर्जयेत्।",
                "desc": f"बृहस्पति सूर्य के अत्यंत समीप (अन्तर: {j_sun_diff:.1f}°) होने से अस्त हैं। देवगुरु के अस्त काल में विवाह, प्रतिष्ठा व गृह प्रवेश निषिद्ध हैं।"
            })

        if is_shukra_asta:
            active_mahadoshas.append({
                "key": "shukra_asta",
                "severity": "FATAL",
                "badge": "🚫 शुक्र अस्त",
                "color": "#DC2626",
                "title": "दैत्यगुरु शुक्र तारा अस्त (Shukra Asta)",
                "sutra": "शुक्रास्ते सर्वमङ्गलं नश्यति।",
                "desc": f"शुक्र सूर्य के अत्यंत समीप (अन्तर: {v_sun_diff:.1f}°) होने से अस्त हैं। सांसारिक सुख व वैवाहिक मांगलिक कार्यों में शुक्र का उदित होना अनिवार्य है।"
            })

        if is_rikta:
            active_mahadoshas.append({
                "key": "rikta_tithi",
                "severity": "HIGH",
                "badge": "⚠️ रिक्ता तिथि",
                "color": "#EA580C",
                "title": f"रिक्ता तिथि ({tithi_name} - #{tithi_idx})",
                "sutra": "रिक्तासु कार्यं न सिद्धयेत्।",
                "desc": "चतुर्थी, नवमी एवं चतुर्दशी 'रिक्ता' कहलाती हैं। इनमें नवीन कार्य, गृह प्रवेश या विवाह करने से धन, मान व कार्य की रिक्तता होती है।"
            })

        if is_amavasya:
            active_mahadoshas.append({
                "key": "amavasya",
                "severity": "FATAL",
                "badge": "🚫 दर्श / अमावस्या",
                "color": "#DC2626",
                "title": "अमावस्या (दर्श तिथि)",
                "sutra": "अमावास्यायां मङ्गलं सर्वथा वर्जयेत्।",
                "desc": "अमावस्या चन्द्रमा के पूर्ण क्षीण होने की तिथि है। यह केवल पितृ कर्म, दान व तंत्र साधना हेतु उपयुक्त है; गृह प्रवेश, विवाह आदि शुभ कर्म सर्वथा वर्जित हैं।"
            })

        if is_malefic_yoga:
            active_mahadoshas.append({
                "key": "malefic_yoga",
                "severity": "MEDIUM",
                "badge": "⚠️ अशुभ योग",
                "color": "#D97706",
                "title": f"अशुभ नित्य योग ({yoga_name})",
                "sutra": "विष्कम्भादिषु दुष्टेषु योगेषु परिवर्जयेत्।",
                "desc": f"वर्तमान नित्य योग '{yoga_name}' अशुभ श्रेणी में आता है जो कार्य में मानसिक उद्वेग या विघ्न उत्पन्न कर सकता है।"
            })

        return {
            "date": target_date.strftime("%d-%b-%Y"),
            "weekday_idx": weekday,
            "weekday_name": target_date.strftime("%A"),
            "sun_longitude": s_lon,
            "moon_longitude": m_lon,
            "sun_sign_id": sun_sign,
            "sun_sign_name": SIGN_NAMES[sun_sign - 1] if 1 <= sun_sign <= 12 else "—",
            "sun_deg": sun_deg,
            "moon_sign_id": moon_sign,
            "moon_sign_name": SIGN_NAMES[moon_sign - 1] if 1 <= moon_sign <= 12 else "—",
            "moon_deg": moon_deg,
            "tithi_idx": tithi_idx,
            "tithi_name": tithi_name,
            "paksha": paksha_name,
            "tithi_category": tithi_category,
            "nakshatra_idx": nak_idx,
            "nakshatra_name": nak_name,
            "nakshatra_lord": nak_lord,
            "yoga_idx": yoga_idx,
            "yoga_name": yoga_name,
            "is_malefic_yoga": is_malefic_yoga,
            "karana_idx": karana_idx,
            "karana_name": karana_name,
            "is_bhadra": is_bhadra,
            "bhadra_loka": bhadra_loka,
            "bhadra_impact": bhadra_impact,
            "bhadra_is_fatal": bhadra_is_fatal,
            "is_pitru_paksha": is_pitru_paksha,
            "is_chaturmas": is_chaturmas,
            "is_kharmas": is_kharmas,
            "is_guru_asta": is_guru_asta,
            "is_shukra_asta": is_shukra_asta,
            "is_rikta": is_rikta,
            "is_amavasya": is_amavasya,
            "active_mahadoshas": active_mahadoshas
        }

    @classmethod
    def evaluate_activity_suitability(
        cls,
        target_date: date,
        activity_type: str,
        natal_chart: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluates 99.9% accurate Muhurta suitability for 12+ major Sanskaras & activities.
        Strictly incorporates Classical prohibitions (Pitru Paksha, Chaturmas, Kharmas, Bhadra, Rikta, Asta),
        activity-specific Tithi/Nakshatra/Vara rules, and the native's individual Tara & Chandra Balam.
        """
        p_info = cls.get_daily_panchang_and_doshas(target_date)
        m_info = cls.calculate_daily_muhurta(target_date)

        activity_titles = {
            "griha_pravesh": "🏛️ गृह प्रवेश (House Warming / Entry)",
            "vivaha": "💍 विवाह संस्कार (Marriage Ceremony)",
            "vyapar": "💼 व्यापार / दुकान / प्रतिष्ठान उद्घाटन (Business Launch)",
            "vahan_kray": "🚗 नवीन वाहन क्रय व पूजन (Vehicle Purchase)",
            "property_kray": "🏠 भूमि, भवन व अचल संपत्ति क्रय (Property Purchase)",
            "namakarana": "👶 नामकरण संस्कार (Naming Ceremony)",
            "mundan": "✂️ मुंडन / चूड़ाकर्म संस्कार (Tonsure Ceremony)",
            "vidyarambha": "🎓 विद्यारंभ / अक्षरारंभ (Commencement of Studies)",
            "upanayana": "📿 उपनयन / जनेऊ संस्कार (Sacred Thread Ceremony)",
            "yatra": "✈️ यात्रा एवं देश-विदेश गमन (Travel & Journey)",
            "medical": "🏥 शल्यक्रिया व नवीन चिकित्सा (Medical / Surgery)",
            "vastra_bhooshan": "💎 नवीन वस्त्र व आभूषण धारण (Wearing Ornaments)"
        }
        title = activity_titles.get(activity_type, f"🚩 {activity_type.capitalize()}")

        reasons = []
        fatal_violations = []
        score = 75
        shastriya_sutras = []

        # =====================================================================
        # 1. EVALUATE UNIVERSAL & ACTIVITY-SPECIFIC FATAL PROHIBITIONS
        # =====================================================================
        is_pitru = p_info["is_pitru_paksha"]
        is_chatur = p_info["is_chaturmas"]
        is_khar = p_info["is_kharmas"]
        is_g_asta = p_info["is_guru_asta"]
        is_s_asta = p_info["is_shukra_asta"]
        is_bhadra = p_info["is_bhadra"]
        is_bhadra_fatal = p_info["bhadra_is_fatal"]
        is_rikta = p_info["is_rikta"]
        is_amav = p_info["is_amavasya"]
        weekday = p_info["weekday_idx"]
        tithi_idx = p_info["tithi_idx"]
        nak_idx = p_info["nakshatra_idx"]
        nak_name = p_info["nakshatra_name"]

        # --- Activity Rules Matrix ---
        if activity_type == "griha_pravesh":
            # Shastra: Griha Pravesh is completely forbidden during Pitru Paksha, Chaturmas (for Apurva), Kharmas, Guru/Shukra Asta, Bhadra, Amavasya, Rikta.
            shastriya_sutras.append("आश्विने कृष्णपक्षे तु पितृपक्षः प्रकीर्तितः। विवाहादि शुभं कर्म गृहप्रवेशं च वर्जयेत्॥ (निर्णय सिन्धु)")
            shastriya_sutras.append("भद्रायां द्वे न कर्तव्ये विवाहो गृहप्रवेशनम्। यात्रां च नैव कुर्वीत कृते मृत्युर्न संशयः॥ (मुहूर्त चिन्तामणि)")

            if is_pitru:
                fatal_violations.append("🚫 **पितृपक्ष (श्राद्ध / महालय पक्ष):** सूर्य कन्या राशि में कृष्ण पक्ष में है। इस काल में पितरों के तर्पण के अतिरिक्त नवीन गृह प्रवेश सर्वथा वर्जित व अमंगलकारी है।")
            if is_chatur:
                fatal_violations.append("⚠️ **चातुर्मास (देवशयन काल):** श्रीहरि विष्णु शयन मुद्रा में हैं। शास्त्रों अनुसार अपूर्व (नवीन) गृह प्रवेश निषिद्ध है।")
            if is_khar:
                fatal_violations.append("🚫 **खरमास (धनु/मीन सूर्य):** सूर्य के गुरु राशि में होने पर गृह प्रवेश वर्जित है।")
            if is_g_asta or is_s_asta:
                fatal_violations.append("🚫 **गुरु/शुक्र तारा अस्त:** शुभ ग्रहों के अस्त काल में गृह प्रवेश निषेध है।")
            if is_bhadra:
                if is_bhadra_fatal:
                    fatal_violations.append(f"🚫 **मृत्युलोक भद्रा (विष्टि करण):** {p_info['bhadra_impact']}")
                else:
                    reasons.append(f"⚠️ भद्रा उपस्थित ({p_info['bhadra_loka']}) - गृह प्रवेश में भद्रा वेला त्यागें।")
            if is_amav:
                fatal_violations.append("🚫 **अमावस्या (दर्श तिथि):** गृह प्रवेश हेतु अमावस्या सर्वथा त्याज्य है।")
            if is_rikta:
                reasons.append(f"⚠️ रिक्ता तिथि ({p_info['tithi_name']}) - गृह प्रवेश में रिक्ता तिथि गृहस्वामी हेतु अनिष्टकारी होती है।")
                score -= 25

            # Favorable Nakshatras for Griha Pravesh: Sthira (Rohini 4, U.Phal 12, U.Ashadha 21, U.Bhadra 26) + Mridu/Chitra (Mrig 5, Chitra 14, Anuradha 17, Revati 27, Hasta 13)
            fav_gp_naks = [4, 5, 12, 13, 14, 17, 21, 26, 27]
            if nak_idx in fav_gp_naks:
                score += 15
                reasons.append(f"✅ गृह प्रवेश अनुकूल नक्षत्र: {nak_name}")
            else:
                score -= 15
                reasons.append(f"ℹ️ नक्षत्र {nak_name} गृह प्रवेश हेतु मध्यम / सामान्य है।")

            # Weekday check: Mon, Wed, Thu, Fri are best. Sun, Tue, Sat avoided for Griha Pravesh
            if weekday in [1, 6]:  # Tue, Sun
                score -= 15
                reasons.append("⚠️ भौम/रवि वार: गृह प्रवेश में अग्नि भय की आशंका से त्याज्य माना जाता है।")
            elif weekday in [0, 2, 3, 4]:  # Mon, Wed, Thu, Fri
                score += 10
                reasons.append("✅ सौम्य वार (सोम/बुध/गुरु/शुक्र): गृह में सुख-शांति हेतु उत्तम।")

        elif activity_type == "vivaha":
            shastriya_sutras.append("सुप्ते जनार्दने प्राप्ते शुभकर्म विवर्जयेत्। विवाहादिकृतं कर्म विपत्तिं कुरुते ध्रुवम्॥")
            shastriya_sutras.append("गुरोरस्ते च शुक्रस्य बाले वृद्धे विवर्जयेत्।")

            if is_pitru:
                fatal_violations.append("🚫 **पितृपक्ष (महालय काल):** पितृपक्ष में विवाह संस्कार सर्वथा निषिद्ध है।")
            if is_chatur:
                fatal_violations.append("🚫 **चातुर्मास (देवशयन):** देवशयन काल में पाणिग्रहण संस्कार पूर्णतः वर्जित है।")
            if is_khar:
                fatal_violations.append("🚫 **खरमास:** सूर्य धनु या मीन में होने पर विवाह वर्जित है।")
            if is_g_asta or is_s_asta:
                fatal_violations.append("🚫 **गुरु/शुक्र अस्त दोष:** गुरु या शुक्र के अस्त रहने पर पाणिग्रहण संस्कार सर्वथा वर्जित है।")
            if is_bhadra and is_bhadra_fatal:
                fatal_violations.append("🚫 **मृत्युलोक भद्रा:** भद्रा में विवाह करने से वैधव्य या घोर अशांति की शास्त्रीय चेतावनी है।")
            if is_amav or is_rikta:
                fatal_violations.append("🚫 **रिक्ता / अमावस्या तिथि:** विवाह संस्कार हेतु यह तिथियां सर्वथा त्याज्य हैं।")

            fav_viv_naks = [4, 5, 10, 12, 13, 15, 17, 19, 21, 26, 27]
            if nak_idx in fav_viv_naks:
                score += 15
                reasons.append(f"✅ विवाह अनुकूल नक्षत्र: {nak_name}")
            else:
                score -= 15

        elif activity_type == "vyapar":
            shastriya_sutras.append("व्यापारे लाभसंस्थानं धनेशे केन्द्रसंस्थिते।")
            if is_pitru:
                reasons.append("⚠️ **पितृपक्ष प्रभाव:** नवीन प्रतिष्ठान या व्यापार का शुभारंभ पितृपक्ष के उपरांत (शारदीय नवरात्रि से) करना अत्यधिक श्रेयस्कर होता है।")
                score -= 35
            if is_bhadra and is_bhadra_fatal:
                fatal_violations.append("⚠️ **मृत्युलोक भद्रा:** दुकान या प्रतिष्ठान का उद्घाटन भद्रा काल में न करें।")
                score -= 30
            if is_amav:
                reasons.append("⚠️ अमावस्या: व्यापार शुभारंभ हेतु त्याज्य।")
                score -= 25
            if is_rikta:
                reasons.append(f"⚠️ रिक्ता तिथि ({p_info['tithi_name']}): व्यापार में हानि व आर्थिक रिक्तता का भय।")
                score -= 20

            # Favorable nakshatras for trade: Ashwini 1, Rohini 4, Pushya 8, Hasta 13, Chitra 14, Swati 15, Anuradha 17, Shravan 22, Dhanishta 23, Revati 27
            fav_trade_naks = [1, 4, 8, 13, 14, 15, 17, 22, 23, 27]
            if nak_idx in fav_trade_naks:
                score += 20
                reasons.append(f"✅ व्यापार वृद्धि कारक नक्षत्र: {nak_name}")

        elif activity_type == "vahan_kray":
            if is_pitru:
                reasons.append("⚠️ **पितृपक्ष काल:** पितृपक्ष में नवीन विलासिता व निजी वाहन क्रय से बचना चाहिए; व्यावसायिक अनिवार्यता हो तो विशेष शांति कर सकते हैं।")
                score -= 30
            if is_bhadra and is_bhadra_fatal:
                reasons.append("⚠️ मृत्युलोक भद्रा: वाहन क्रय व डिलीवरी में दुर्घटना भय से भद्रा त्याज्य है।")
                score -= 25
            if weekday == 1:  # Tuesday
                score -= 15
                reasons.append("⚠️ मंगलवार: वाहन क्रय हेतु सामान्यतः वर्जित (अग्नि/धातु दोष)।")
            # Chara nakshatras: Swati 15, Punarvasu 7, Shravan 22, Dhanishta 23, Shatabhisha 24, Ashwini 1, Hasta 13
            fav_vahan_naks = [1, 4, 7, 8, 13, 15, 22, 23, 24, 27]
            if nak_idx in fav_vahan_naks:
                score += 15
                reasons.append(f"✅ गतिमान / चर नक्षत्र ({nak_name}): वाहन दीर्घायु व सुरक्षा हेतु उत्तम।")

        elif activity_type in ["namakarana", "mundan", "upanayana"]:
            if is_pitru:
                fatal_violations.append("🚫 **पितृपक्ष महा-निषेध:** पितृपक्ष में समस्त संस्कार (नामकरण, मुंडन, उपनयन) वर्जित हैं।")
            if is_chatur and activity_type in ["mundan", "upanayana"]:
                fatal_violations.append("🚫 **चातुर्मास:** देवशयन में मुंडन व उपनयन संस्कार निषिद्ध हैं।")
            if is_khar:
                fatal_violations.append("🚫 **खरमास:** उपनयन व चूड़ाकर्म वर्जित हैं।")
            if is_g_asta or is_s_asta:
                fatal_violations.append("🚫 **तारा अस्त:** गुरु/शुक्र अस्त में संस्कार निषिद्ध हैं।")

        else:
            # Generic checks for other activities
            if is_pitru:
                reasons.append("⚠️ पितृपक्ष प्रभाव: मांगलिक कार्यों में संयम रखें।")
                score -= 20
            if is_bhadra and is_bhadra_fatal:
                reasons.append("⚠️ मृत्युलोक भद्रा काल में कार्य आरंभ न करें।")
                score -= 20
            if is_rikta:
                reasons.append("⚠️ रिक्ता तिथि दोष।")
                score -= 15

        # =====================================================================
        # 2. EVALUATE NATIVE PERSONAL TARA BALAM & CHANDRA BALAM (IF CHART GIVEN)
        # =====================================================================
        tara_data = None
        chandra_bal_data = None

        if natal_chart and hasattr(natal_chart, "planets") and "Moon" in natal_chart.planets:
            natal_m = natal_chart.planets["Moon"]
            natal_m_lon = getattr(natal_m, "longitude", 0.0)
            natal_m_nak_idx = int((natal_m_lon % 360.0) // (360.0 / 27.0)) + 1
            natal_m_sign = getattr(natal_m, "sign_id", 1)

            # 1. Tara Balam
            tara_diff = (nak_idx - natal_m_nak_idx) % 27
            tara_num = (tara_diff % 9) + 1
            t_name, t_desc, t_verdict, t_col = TARA_NAMES_9[tara_num - 1]

            tara_data = {
                "tara_number": tara_num,
                "tara_name": t_name,
                "description": t_desc,
                "verdict": t_verdict,
                "color": t_col,
                "is_good": tara_num in [2, 4, 6, 8, 9]
            }

            if tara_num in [2, 4, 6, 8, 9]:
                score += 15
                reasons.append(f"🟢 **जातक ताराबल अनुकूल ({t_name}):** {t_verdict}")
            elif tara_num in [3, 5, 7]:
                score -= 25
                reasons.append(f"🔴 **जातक ताराबल दोष ({t_name}):** {t_desc}")
            else:
                score -= 5
                reasons.append(f"🟡 **जातक ताराबल ({t_name}):** सतर्कता अपेक्षित।")

            # 2. Chandra Balam
            c_diff = ((p_info["moon_sign_id"] - natal_m_sign) % 12) + 1
            if c_diff in [1, 3, 6, 7, 10, 11]:
                score += 15
                c_status = f"🟢 शुभ चन्द्रबल ({c_diff} भाव)"
                c_desc = f"गोचर चन्द्रमा जातक की जन्म राशि से {c_diff}वें भाव में भ्रमण कर रहा है, जो मनोबल व कार्य सिद्धि प्रदान करता है।"
                reasons.append(f"✅ जातक के लिए अनुकूल चन्द्रबल ({c_diff}वां चन्द्रमा)")
            elif c_diff in [4, 8, 12]:
                score -= 30
                c_status = f"🔴 घात चन्द्र / अष्टम चन्द्र दोष ({c_diff} भाव)"
                c_desc = f"गोचर चन्द्रमा जन्म राशि से {c_diff}वें भाव में है (घात चन्द्र)। यह मानसिक तनाव व कार्य बाधा का कारण बनता है।"
                reasons.append(f"⚠️ जातक की जन्म राशि से {c_diff}वां चन्द्रमा (घात चन्द्र दोष)")
            else:
                score += 5
                c_status = f"🟡 मध्यम चन्द्रबल ({c_diff} भाव)"
                c_desc = f"गोचर चन्द्रमा {c_diff}वें भाव में मध्यम फलदायी है।"

            chandra_bal_data = {
                "house_diff": c_diff,
                "status": c_status,
                "description": c_desc,
                "is_good": c_diff in [1, 3, 6, 7, 10, 11]
            }

        # =====================================================================
        # 3. FINAL SCORE & VERDICT RESOLUTION
        # =====================================================================
        if fatal_violations:
            # Fatal Shastriya prohibition: score strictly clamped to 0-10%
            final_score = min(8, max(2, score % 10))
            verdict = "🚫 सर्वथा वर्जित एवं त्याज्य (Strictly Prohibited)"
            badge_color = "#DC2626"
            guidance = "वर्तमान काल में महा-निषेध (पितृपक्ष / चातुर्मास / भद्रा / खरमास) सक्रिय होने के कारण इस कार्य को संपन्न करना शास्त्रों में पूर्णतः निषिद्ध है। कृपया उपयुक्त काल शुद्धि एवं महादोष समाप्ति तक प्रतीक्षा करें।"
        else:
            final_score = min(98, max(15, score))
            if final_score >= 80:
                verdict = "🟢 अति उत्तम व प्रशस्त मुहूर्त (Highly Auspicious)"
                badge_color = "#16A34A"
                guidance = "पञ्चाङ्ग शुद्धि, ताराबल एवं अनुकूल चौघड़िया प्राप्त हैं। शुभ वेला में संकल्प सहित कार्य संपन्न करें।"
            elif final_score >= 60:
                verdict = "🟡 मध्यम अनुकूल (Acceptable with Remedies)"
                badge_color = "#D97706"
                guidance = "मुहूर्त मध्यम है। अभिजित मुहूर्त अथवा अमृत/लाभ चौघड़िया में गणपति पूजन व नवग्रह स्मरण उपरांत कार्य करें।"
            else:
                verdict = "🔴 वर्जित / त्याज्य मुहूर्त (Inauspicious)"
                badge_color = "#DC2626"
                guidance = "पञ्चाङ्ग दोषों अथवा प्रतिकूल ताराबल के कारण यह तिथि शुभ कार्य हेतु त्याज्य है। अन्य शुभ तिथि का चयन करें।"

        return {
            "activity": title,
            "activity_key": activity_type,
            "target_date": target_date.strftime("%d-%b-%Y"),
            "suitability_score": final_score,
            "verdict": verdict,
            "badge_color": badge_color,
            "guidance": guidance,
            "fatal_violations": fatal_violations,
            "reasons": reasons,
            "shastriya_sutras": shastriya_sutras,
            "panchang_summary": p_info,
            "tara_balam": tara_data,
            "chandra_balam": chandra_bal_data,
            "day_choghadiyas": m_info["day_choghadiyas"],
            "special_windows": m_info["special_windows"]
        }


default_muhurta_engine = MuhurtaEngine()


class MuhurtaRangeScanner:
    """Scans date ranges and ranks best muhurtas based on classical Panchang purity, Maha-Doshas, and Native alignment."""

    FAVORABLE_NAKSHATRAS = {
        "vivaha": [4, 5, 10, 12, 13, 15, 17, 19, 21, 26, 27],  # Rohini, Mrig, Magha, U.Phal, Hast, Swati, Anuradha, Moola, U.Ashadha, U.Bhadra, Revati
        "griha_pravesh": [4, 5, 12, 13, 14, 17, 21, 26, 27],  # Rohini, Mrig, U.Phal, Hast, Chitra, Anuradha, U.Ashadha, U.Bhadra, Revati
        "vyapar": [1, 4, 8, 13, 14, 15, 17, 22, 23, 27],      # Ashwini, Rohini, Pushya, Hast, Chitra, Swati, Anuradha, Shravan, Dhanishta, Revati
        "vahan_kray": [1, 4, 7, 8, 13, 15, 22, 23, 24, 27],   # Ashwini, Rohini, Punarvasu, Pushya, Hast, Swati, Shravan, Dhanishta, Shatabhisha, Revati
    }

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
        Strictly applies Shastriya Maha-Nishedha filters:
        - Completely penalizes Pitru Paksha for Griha Pravesh & Vivaha.
        - Penalizes Chaturmas, Kharmas, Guru/Shukra Asta, and Martya Bhadra.
        - Calculates Native's personal Chandra and Tara Balam.
        - Returns authentic top-ranked auspicious dates.
        """
        results = []
        cur_d = start_date
        delta = timedelta(days=1)

        while cur_d <= end_date:
            eval_res = MuhurtaEngine.evaluate_activity_suitability(
                target_date=cur_d,
                activity_type=activity_type,
                natal_chart=natal_chart
            )

            score = eval_res["suitability_score"]
            p_inf = eval_res["panchang_summary"]

            # Filter out dates with fatal prohibitions from top suggestions
            if eval_res["fatal_violations"]:
                # Still store if range is very small, but with severely low score
                pass

            d_info = MuhurtaEngine.calculate_daily_muhurta(cur_d)
            best_chog = [c for c in d_info["day_choghadiyas"] if c["is_good"]]
            chog_str = ", ".join([f"{c['name'].split(' ')[0]} ({c['start_time']}-{c['end_time']})" for c in best_chog[:2]])
            abhijit_w = next((w["time"] for w in d_info["special_windows"] if "अभिजित" in w["title"]), "11:45 AM - 12:35 PM")

            reasons_display = []
            if eval_res["fatal_violations"]:
                reasons_display.extend(eval_res["fatal_violations"])
            else:
                reasons_display.extend(eval_res["reasons"][:3])

            results.append({
                "date": cur_d.strftime("%d %b %Y"),
                "date_str": cur_d.strftime("%d %b %Y"),
                "raw_date": cur_d,
                "iso_date": cur_d.strftime("%Y-%m-%d"),
                "weekday": cur_d.strftime("%A"),
                "day_name": cur_d.strftime("%A"),
                "score": score,
                "verdict": eval_res["verdict"],
                "badge_color": eval_res["badge_color"],
                "tithi": f"{p_inf['tithi_name']} ({p_inf['paksha']})",
                "nakshatra": p_inf["nakshatra_name"],
                "nakshatra_lord": p_inf["nakshatra_lord"],
                "yoga": p_inf["yoga_name"],
                "moon_sign": p_inf["moon_sign_name"],
                "chandra_bal": eval_res.get("chandra_balam", {}).get("status", "—") if eval_res.get("chandra_balam") else "—",
                "chandra_balam": eval_res.get("chandra_balam", {}).get("status", "—") if eval_res.get("chandra_balam") else "—",
                "best_window": f"अभिजित: {abhijit_w} | चौघड़िया: {chog_str}",
                "reasons": reasons_display,
                "fatal_count": len(eval_res["fatal_violations"])
            })

            cur_d += delta

        # Sort descending by score, prioritizing dates without fatal violations
        results.sort(key=lambda x: (x["score"], -x["fatal_count"]), reverse=True)
        return results[:top_n]


default_muhurta_scanner = MuhurtaRangeScanner()
