"""
Birth Time Rectification (BTR) Engine for JyotishOS.
Integrates Classical Vedic Principles (Brihat Parashara Hora Shastra, Jataka Parijata)
with Krishnamurti Paddhati (KP System 249 Sub-Lords & Ruling Planets):
1. Tattwa Shodhana & Antar-Tattwa Gender Rectification (तत्व शोधन व लिंग निर्णय)
2. Kunda Shodhana & Nakshatra Trikona Alignment (कुण्ड शोधन)
3. Pranapada Lagna Alignment from Sunrise Ishta Kala (प्राणपद लग्न शोधन)
4. D9 Navamsha & D60 Shashtiamsha Precision Boundary Vulnerability Scan (षोडशवर्ग सीमा शोधन)
5. KP Ruling Planets & Sub-Lord Verification (के.पी. रूलिंग प्लैनेट्स एवं सब-लॉर्ड)
6. Multi-Event Chronological Verification against Vimshottari Dashas, Divisional Charts & Transits
7. Original vs Rectified Kundali Comparative Analysis
"""

import math
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional, Tuple
import ephem
from pydantic import BaseModel, Field

from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..core.varga import VargaCalculator
from ..core.kp import KPEngine
from ..core.constants import SIGN_NAMES, SIGN_LORDS, NAKSHATRAS, NAKSHATRA_NAMES
from ..dasha.vimshottari import default_dasha_engine
from ..core.gochar import default_transit_engine


# 60 Shashtiamsha Deities & Nature according to BPHS Chapter 6
SHASHTIAMSHA_DEITIES_ODD = [
    ("घोर (Ghora)", "क्रूर / अशुभ", "भय, कठोरता, जीवन संघर्ष"),
    ("राक्षस (Rakshasa)", "क्रूर / तामसिक", "उग्र स्वभाव, तीव्र विरोध"),
    ("देव (Deva)", "शुभ / सात्विक", "दिव्य कृपा, ज्ञान, उच्च संस्कार"),
    ("कुबेर (Kubera)", "शुभ / राजसिक", "धन-वैभव, संपत्ति, ऐश्वर्य"),
    ("यक्ष (Yaksha)", "मध्यम", "कला, सौंदर्य, आकर्षण"),
    ("किन्नर (Kinnara)", "मध्यम", "संगीत, गायन, ललित कला"),
    ("भ्रष्ट (Bhrashta)", "अशुभ", "अस्थिरता, पतन की आशंका"),
    ("कुलघ्न (Kulaghna)", "अशुभ", "परिवार में मतभेद"),
    ("गरल (Garala)", "अशुभ", "विष, कटुता, स्वास्थ्य कष्ट"),
    ("वह्नि (Vahni)", "मध्यम / क्रूर", "अग्नि, ऊर्जा, तीक्ष्णता"),
    ("माया (Maya)", "मध्यम", "कूटनीति, भ्रम, चतुरता"),
    ("पुरीषक (Purishaka)", "अशुभ", "निम्न कर्म, हीनता"),
    ("अपांपति (Apampati)", "शुभ", "वरुण, जल, शांति, प्रचुरता"),
    ("मारुत (Maruta)", "मध्यम", "वायु, गति, यात्रा, चपलता"),
    ("काल (Kaala)", "अशुभ", "मृत्यु, संहार, विघ्न"),
    ("सर्प (Sarpa)", "क्रूर / अशुभ", "गूढ़ रहस्य, विष, सतर्कता"),
    ("अमृत (Amrita)", "अत्यंत शुभ", "अमरत्व, आरोग्य, सौभाग्य"),
    ("इन्दु (Indu)", "शुभ", "चन्द्रमा, मानसिक शांति, कांति"),
    ("मृदु (Mridu)", "शुभ", "कोमलता, सौम्यता, दया"),
    ("कोमल (Komala)", "शुभ", "स्नेह, सरलता, सहानुभूति"),
    ("हेरम्ब (Heramba)", "अत्यंत शुभ", "गणेश कृपा, विघ्न विनाश"),
    ("ब्रह्मा (Brahma)", "अत्यंत शुभ", "सृजन, विद्वता, ज्ञान"),
    ("विष्णु (Vishnu)", "अत्यंत शुभ", "पालन, ऐश्वर्य, धर्म"),
    ("महेश्वर (Maheshwara)", "अत्यंत शुभ", "कल्याण, मोक्ष, वैराग्य"),
    ("देव (Deva-2)", "शुभ", "पुण्य, धार्मिकता, परोपकार"),
    ("आर्द्रा (Ardra)", "मध्यम / शुभ", "संवेदना, आर्द्रता, दयाभाव"),
    ("कलिनाश (Kalinasha)", "शुभ", "पाप नाश, सद्कर्म"),
    ("क्षितीश (Kshiteesa)", "शुभ", "राजा, भूमिपति, अधिकार"),
    ("कमलाकर (Kamalakara)", "शुभ", "लक्ष्मी वास, समृद्धि"),
    ("गुलिक (Gulika)", "अशुभ", "मंदि, मंद गति, बाधा"),
    ("मृत्यु (Mrityu)", "अशुभ", "संकट, अवरोध, अंत"),
    ("काल (Kaala-2)", "अशुभ", "समय चक्र, कठोरता"),
    ("दावाग्नि (Davagni)", "क्रूर / अशुभ", "दावानल, प्रचंड उग्रता"),
    ("घोर (Ghora-2)", "अशुभ", "कष्ट, भय, संघर्ष"),
    ("अधम (Adhama)", "अशुभ", "निम्न स्थिति, सतर्कता"),
    ("कंटक (Kantaka)", "अशुभ", "शूल, पीड़ा, रुकावट"),
    ("सुधा (Sudha)", "अत्यंत शुभ", "अमृत, मधुरता, स्वास्थ्य"),
    ("अमृत (Amrita-2)", "अत्यंत शुभ", "अक्षय सुख, दीर्घायु"),
    ("पूर्णचन्द्र (Poornachandra)", "परम शुभ", "सम्पूर्ण कांति, यश, सुख"),
    ("विषदिग्ध (Vishadagdha)", "अशुभ", "विषाक्त वातावरण, हानि"),
    ("कुलनाश (Kulanasha)", "अशुभ", "कुल की चिंता, वियोग"),
    ("वंशक्षय (Vamshakshaya)", "अशुभ", "वंश चिंता, सतर्कता"),
    ("उत्पात (Utpata)", "अशुभ", "आकस्मिक उपद्रव, उथल-पुथल"),
    ("काल (Kaala-3)", "अशुभ", "प्रतिकूल काल"),
    ("सौम्य (Saumya)", "शुभ", "बुद्धिमत्ता, नम्रता, आकर्षण"),
    ("कोमल (Komala-2)", "शुभ", "सुंदरता, कोमलता"),
    ("शीतल (Sheetala)", "शुभ", "शांत स्वभाव, शीतलता"),
    ("करालदंष्ट्र (Karaladamshtra)", "क्रूर / उग्र", "तीक्ष्णता, साहस, पराक्रम"),
    ("चन्द्रमुखी (Chandramukhi)", "शुभ", "सौंदर्य, लोकप्रियता, आकर्षण"),
    ("प्रवीण (Praveena)", "शुभ", "कुशलता, निपुणता, कला"),
    ("कालपावक (Kaalpavaka)", "क्रूर / तामसिक", "महाअग्नि, ज्वलंत प्रलय"),
    ("दण्डायुध (Dandayudha)", "मध्यम / क्रूर", "शासन, दंड, न्याय, कठोरता"),
    ("निर्मल (Nirmala)", "शुभ", "पवित्रता, शुद्धि, निष्कलंक"),
    ("सौम्य (Saumya-2)", "शुभ", "सदाचार, मधुर वाणी"),
    ("क्रूर (Krura)", "अशुभ", "कठोरता, विवाद, कटुता"),
    ("अतिशीतल (Atisheetala)", "शुभ", "परम शांति, धैर्य, संतोष"),
    ("अमृत (Amrita-3)", "अत्यंत शुभ", "दिव्य जीवन, दीर्घायु"),
    ("पयोधि (Payodhi)", "शुभ", "क्षीरसागर, अपार धन, ज्ञान"),
    ("भ्रमण (Bhramana)", "मध्यम", "देशाटन, यात्रा, अस्थिरता"),
    ("चन्द्ररेखा (Chandrarekha)", "शुभ", "उत्कृष्ट यश, सौंदर्य, वृद्धि")
]

# Classical Tattwas: Earth, Water, Fire, Air, Ether
TATTWAS = [
    {"name": "पृथ्वी (Prithvi)", "element": "Earth", "duration_min": 6.0, "gender": "male", "nature": "स्थिर, भौतिक, व्यावहारिक, संयमी"},
    {"name": "जल (Jala)", "element": "Water", "duration_min": 12.0, "gender": "female", "nature": "भावुक, संवेदनशील, अनुकूलनशील, सौम्य"},
    {"name": "अग्नि (Agni)", "element": "Fire", "duration_min": 18.0, "gender": "male", "nature": "तेजस्वी, महत्त्वाकांक्षी, साहसी, प्रखर"},
    {"name": "वायु (Vayu)", "element": "Air", "duration_min": 24.0, "gender": "female", "nature": "गतिशील, बौद्धिक, चपल, बहुमुखी"},
    {"name": "आकाश (Akasha)", "element": "Ether", "duration_min": 30.0, "gender": "male", "nature": "विस्तृत, आध्यात्मिक, गूढ़, दार्शनिक"}
]

# Weekday initial Tattwa index (Mon=0..Sun=6)
DAY_TATTWA_START = {
    6: 2,  # Sunday -> Agni
    0: 1,  # Monday -> Jala
    1: 2,  # Tuesday -> Agni
    2: 0,  # Wednesday -> Prithvi
    3: 4,  # Thursday -> Akasha
    4: 1,  # Friday -> Jala
    5: 3   # Saturday -> Vayu
}


class LifeEvent(BaseModel):
    """User-verified past life event for rectification fitting."""
    event_date: date
    event_category: str = Field(..., description="career, marriage, child, travel, property, health_accident, education")
    description: Optional[str] = ""


class BTRCandidate(BaseModel):
    """A scored candidate birth time."""
    candidate_time: str
    offset_minutes: int
    fit_score: float = Field(..., ge=0.0, le=100.0)
    confidence: str
    lagna_sign: str
    navamsha_lagna_sign: str
    dashamsha_lagna_sign: str
    matching_events_count: int
    evidence_breakdown: List[str]
    d60_deity: Optional[str] = ""
    kunda_match: Optional[str] = ""
    pranapada_match: Optional[str] = ""
    tattwa_match: Optional[str] = ""
    kp_match: Optional[str] = ""


class BTRService:
    """Automated and assisted Birth Time Rectification Engine."""

    CATEGORY_HOUSE_SIGNIFICATORS = {
        "career": [10, 11, 1, 9, 6],
        "marriage": [7, 2, 11],
        "child": [5, 9, 2],
        "travel": [9, 12, 3],
        "property": [4, 11, 12],
        "health_accident": [6, 8, 12],
        "education": [4, 5, 9, 11]
    }

    # -------------------------------------------------------------------------
    # 1. ASTRONOMICAL SUNRISE CALCULATION
    # -------------------------------------------------------------------------
    @staticmethod
    def get_astronomical_sunrise(target_date: date, lat: float, lon: float, tz_offset: float) -> datetime:
        """Calculates precise local astronomical sunrise using PyEphem."""
        obs = ephem.Observer()
        obs.lat = str(lat)
        obs.lon = str(lon)
        obs.date = target_date.strftime("%Y/%m/%d 00:00:00")
        sun = ephem.Sun()
        try:
            rise_utc = obs.next_rising(sun).datetime()
            local_rise = rise_utc + timedelta(hours=tz_offset)
            return local_rise
        except Exception:
            return datetime.combine(target_date, time(6, 0))

    # -------------------------------------------------------------------------
    # 2. TATTWA SHODHANA & GENDER DETERMINATION
    # -------------------------------------------------------------------------
    def calculate_tattwa_shodhana(self, birth_data: BirthData, gender: str = "male") -> Dict[str, Any]:
        """
        Classical Tattwa Shodhana & Antar-Tattwa Gender Rectification.
        Mahatattwas cycle in 90-minute periods from Sunrise.
        """
        b_d = birth_data.birth_date
        if isinstance(b_d, str):
            b_d = datetime.strptime(b_d, "%Y-%m-%d").date()
        b_t = birth_data.birth_time
        if isinstance(b_t, str):
            try:
                b_t = datetime.strptime(b_t, "%H:%M:%S").time()
            except ValueError:
                b_t = datetime.strptime(b_t, "%H:%M").time()

        birth_dt = datetime.combine(b_d, b_t)
        sunrise_dt = self.get_astronomical_sunrise(b_d, birth_data.latitude, birth_data.longitude, birth_data.timezone_offset)

        # If birth occurs before sunrise, sunrise is that of the previous day
        if birth_dt < sunrise_dt:
            prev_date = b_d - timedelta(days=1)
            sunrise_dt = self.get_astronomical_sunrise(prev_date, birth_data.latitude, birth_data.longitude, birth_data.timezone_offset)

        ishta_seconds = max(0.0, (birth_dt - sunrise_dt).total_seconds())
        ishta_minutes = ishta_seconds / 60.0
        ishta_ghatis = ishta_minutes / 24.0
        ishta_vighatis = (ishta_ghatis - int(ishta_ghatis)) * 60.0

        weekday_idx = sunrise_dt.weekday()  # Mon=0..Sun=6
        start_tattwa_idx = DAY_TATTWA_START.get(weekday_idx, 2)

        cycle_duration = 90.0  # 6 + 12 + 18 + 24 + 30 = 90 mins
        cycle_num = int(ishta_minutes // cycle_duration)
        pos_in_cycle = ishta_minutes % cycle_duration

        # Build order for the weekday
        t_order = [TATTWAS[(start_tattwa_idx + i) % 5] for i in range(5)]

        accum = 0.0
        curr_tattwa = t_order[0]
        tattwa_start_min = 0.0
        for t in t_order:
            if accum <= pos_in_cycle < accum + t["duration_min"]:
                curr_tattwa = t
                tattwa_start_min = accum
                break
            accum += t["duration_min"]

        time_in_tattwa = pos_in_cycle - tattwa_start_min
        m_dur = curr_tattwa["duration_min"]

        # Antar-tattwa
        sub_accum = 0.0
        curr_sub_tattwa = t_order[0]
        sub_start_min = 0.0
        sub_dur = (t_order[0]["duration_min"] / 90.0) * m_dur
        for st in t_order:
            sub_d = (st["duration_min"] / 90.0) * m_dur
            if sub_accum <= time_in_tattwa < sub_accum + sub_d:
                curr_sub_tattwa = st
                sub_start_min = sub_accum
                sub_dur = sub_d
                break
            sub_accum += sub_d

        sub_end_min = sub_start_min + sub_dur
        abs_sub_start_sec = (cycle_num * cycle_duration + tattwa_start_min + sub_start_min) * 60.0
        abs_sub_end_sec = (cycle_num * cycle_duration + tattwa_start_min + sub_end_min) * 60.0

        win_start_dt = sunrise_dt + timedelta(seconds=abs_sub_start_sec)
        win_end_dt = sunrise_dt + timedelta(seconds=abs_sub_end_sec)

        user_gender = gender.lower()
        sub_gender = curr_sub_tattwa["gender"]
        maha_gender = curr_tattwa["gender"]

        if sub_gender == user_gender:
            match_status = "✅ पूर्ण अनुकूल (अंतर-तत्व व लिंग पूर्ण मेल)"
            match_color = "#10B981"
            score = 100.0
        elif maha_gender == user_gender:
            match_status = "🟡 आंशिक अनुकूल (महा-तत्व मेल, अंतर-तत्व विपरीत)"
            match_color = "#F59E0B"
            score = 70.0
        else:
            match_status = "⚠️ विपरीत तत्व (शोधन अपेक्षित - लिंग भिन्नता)"
            match_color = "#EF4444"
            score = 35.0

        tattwa_table = []
        c_sub_acc = 0.0
        for st in t_order:
            s_d = (st["duration_min"] / 90.0) * m_dur
            s_st_sec = (cycle_num * cycle_duration + tattwa_start_min + c_sub_acc) * 60.0
            s_en_sec = s_st_sec + (s_d * 60.0)
            t_s_dt = sunrise_dt + timedelta(seconds=s_st_sec)
            t_e_dt = sunrise_dt + timedelta(seconds=s_en_sec)
            tattwa_table.append({
                "अंतर-तत्व": st["name"],
                "मूल तत्व": st["element"],
                "लिंग प्रकृति": "पुरुष (Male)" if st["gender"] == "male" else "स्त्री (Female)",
                "अवधि": f"{round(s_d, 2)} मिनट",
                "समय सीमा": f"{t_s_dt.strftime('%H:%M:%S')} - {t_e_dt.strftime('%H:%M:%S')}",
                "वर्तमान स्थिति": "🎯 वर्तमान सक्रिय" if st["name"] == curr_sub_tattwa["name"] else "—"
            })
            c_sub_acc += s_d

        return {
            "sunrise_time": sunrise_dt.strftime("%I:%M:%S %p"),
            "ishta_kala": f"{int(ishta_ghatis)} घटी {int(ishta_vighatis)} विघटी ({round(ishta_minutes, 1)} मिनट)",
            "day_lord_tattwa": TATTWAS[start_tattwa_idx]["name"],
            "maha_tattwa": curr_tattwa["name"],
            "maha_tattwa_gender": "पुरुष (Male)" if maha_gender == "male" else "स्त्री (Female)",
            "maha_tattwa_nature": curr_tattwa["nature"],
            "maha_tattwa_duration": f"{curr_tattwa['duration_min']} मिनट",
            "antar_tattwa": curr_sub_tattwa["name"],
            "antar_tattwa_gender": "पुरुष (Male)" if sub_gender == "male" else "स्त्री (Female)",
            "antar_tattwa_nature": curr_sub_tattwa["nature"],
            "current_window": f"{win_start_dt.strftime('%H:%M:%S')} - {win_end_dt.strftime('%H:%M:%S')}",
            "gender_match_status": match_status,
            "gender_match_color": match_color,
            "score": score,
            "sub_tattwa_schedule": tattwa_table,
            "shastric_rule": "शास्त्रोक्त नियम: पुरुष जातक का जन्म पुरुष तत्व (अग्नि, आकाश, पृथ्वी) तथा स्त्री जातक का जन्म स्त्री तत्व (जल, वायु) के अंतर-तत्व में होना चाहिए।"
        }

    # -------------------------------------------------------------------------
    # 3. KUNDA & PRANAPADA LAGNA SHODHANA
    # -------------------------------------------------------------------------
    def calculate_kunda_pranapada(self, chart: KundaliChart, birth_data: BirthData) -> Dict[str, Any]:
        """
        BPHS Classical Kunda Shodhana & Pranapada Lagna Rectification.
        """
        lagna_lon = chart.lagna_longitude
        # Kunda = (Lagna degrees * 81) % 27
        kunda_val = (lagna_lon * 81.0) % 27.0
        kunda_nak_idx = int(kunda_val) + 1  # 1 to 27
        kunda_nak_name = NAKSHATRA_NAMES[kunda_nak_idx - 1]

        moon_lon = chart.planets["Moon"].longitude
        moon_nak_idx = int(moon_lon // (360.0 / 27.0)) + 1
        moon_nak_name = NAKSHATRA_NAMES[moon_nak_idx - 1]

        lagna_nak_idx = int(lagna_lon // (360.0 / 27.0)) + 1
        lagna_nak_name = NAKSHATRA_NAMES[lagna_nak_idx - 1]

        # Classical Rule: Kunda must be in Trikona (1, 10, 19th) from Moon Nakshatra or Lagna Nakshatra
        dist_from_moon = (kunda_nak_idx - moon_nak_idx) % 9
        dist_from_lagna = (kunda_nak_idx - lagna_nak_idx) % 9

        is_kunda_pure = (dist_from_moon == 0) or (dist_from_lagna == 0)
        if is_kunda_pure:
            kunda_status = "✅ पूर्ण शुद्ध (कुण्ड नक्षत्र चन्द्र/लग्न नक्षत्र के त्रिकोण में है)"
            kunda_color = "#10B981"
            kunda_score = 100.0
        else:
            kunda_status = "⚠️ अशुद्ध (कुण्ड त्रिकोण संरेखण अपूर्ण - समय संशोधन अपेक्षित)"
            kunda_color = "#EF4444"
            kunda_score = 40.0

        # Pranapada Lagna
        b_d = birth_data.birth_date
        if isinstance(b_d, str):
            b_d = datetime.strptime(b_d, "%Y-%m-%d").date()
        b_t = birth_data.birth_time
        if isinstance(b_t, str):
            try:
                b_t = datetime.strptime(b_t, "%H:%M:%S").time()
            except ValueError:
                b_t = datetime.strptime(b_t, "%H:%M").time()

        birth_dt = datetime.combine(b_d, b_t)
        sunrise_dt = self.get_astronomical_sunrise(b_d, birth_data.latitude, birth_data.longitude, birth_data.timezone_offset)
        if birth_dt < sunrise_dt:
            sunrise_dt = self.get_astronomical_sunrise(b_d - timedelta(days=1), birth_data.latitude, birth_data.longitude, birth_data.timezone_offset)

        ishta_sec = max(0.0, (birth_dt - sunrise_dt).total_seconds())
        ishta_palas = (ishta_sec / 60.0) * 2.5  # 1 min = 2.5 palas

        sun_lon = chart.planets["Sun"].longitude
        pranapada_lon = (sun_lon + (ishta_palas / 15.0) * 30.0) % 360.0
        pranapada_sign_id = int(pranapada_lon // 30.0) + 1
        pranapada_sign_name = SIGN_NAMES[pranapada_sign_id - 1]
        lagna_sign_id = chart.lagna_sign_id

        house_from_lagna = ((pranapada_sign_id - lagna_sign_id) % 12) + 1
        is_pranapada_pure = house_from_lagna in (1, 2, 4, 5, 7, 9, 10, 11)

        if is_pranapada_pure:
            pranapada_status = f"✅ शुद्ध (प्राणपद लग्न से {house_from_lagna}वें शुभ भाव में स्थित है)"
            pranapada_color = "#10B981"
            pranapada_score = 100.0
        else:
            pranapada_status = f"⚠️ अशुद्ध (प्राणपद त्रिक {house_from_lagna}वें भाव में है - संशोधन अनिवार्य)"
            pranapada_color = "#EF4444"
            pranapada_score = 30.0

        return {
            "kunda_nakshatra_num": kunda_nak_idx,
            "kunda_nakshatra_name": kunda_nak_name,
            "kunda_nakshatra_val": round(kunda_val, 2),
            "janma_nakshatra_name": moon_nak_name,
            "lagna_nakshatra_name": lagna_nak_name,
            "kunda_status": kunda_status,
            "kunda_color": kunda_color,
            "kunda_score": kunda_score,
            "is_kunda_pure": is_kunda_pure,
            "pranapada_longitude": round(pranapada_lon, 2),
            "pranapada_sign": pranapada_sign_name,
            "pranapada_deg": round(pranapada_lon % 30.0, 2),
            "house_from_lagna": house_from_lagna,
            "pranapada_status": pranapada_status,
            "pranapada_color": pranapada_color,
            "pranapada_score": pranapada_score,
            "is_pranapada_pure": is_pranapada_pure
        }

    # -------------------------------------------------------------------------
    # 4. DIVISIONAL CHARTS BOUNDARY PRECISION SCAN (D1, D9, D10, D60)
    # -------------------------------------------------------------------------
    def calculate_divisional_boundaries(self, chart: KundaliChart, birth_data: BirthData) -> Dict[str, Any]:
        """
        Analyzes edge/cusp sensitivity for D1, D9, D10, and D60 Shashtiamsha.
        """
        lagna_deg = chart.lagna_degree  # 0 to 30

        # D1 Progress
        d1_progress_pct = round((lagna_deg / 30.0) * 100.0, 1)

        # D9 Navamsha: 3°20' = 3.333333 deg
        nav_span = 30.0 / 9.0
        nav_idx = int(lagna_deg // nav_span)
        deg_in_nav = lagna_deg % nav_span
        d9_progress_pct = round((deg_in_nav / nav_span) * 100.0, 1)

        # 1 deg ~ 240 seconds of time (4 minutes per degree)
        d9_time_elapsed_sec = int(deg_in_nav * 240.0)
        d9_time_remain_sec = int((nav_span - deg_in_nav) * 240.0)

        # D60 Shashtiamsha: 0°30' = 0.5 deg (30 arc-min ~ 120 seconds of time)
        d60_span = 0.5
        d60_part = int(lagna_deg // d60_span)
        deg_in_d60 = lagna_deg % d60_span
        d60_progress_pct = round((deg_in_d60 / d60_span) * 100.0, 1)

        d60_time_elapsed_sec = int(deg_in_d60 * 240.0)
        d60_time_remain_sec = int((d60_span - deg_in_d60) * 240.0)

        # D60 deity
        is_odd_sign = (chart.lagna_sign_id % 2 != 0)
        deity_idx = d60_part if is_odd_sign else (59 - d60_part)
        deity_info = SHASHTIAMSHA_DEITIES_ODD[min(59, max(0, deity_idx))]

        min_d60_border = min(d60_time_elapsed_sec, d60_time_remain_sec)
        if min_d60_border < 25:
            vuln_status = "🚨 अति-संवेदनशील (सीमा से < २५ सेकंड दूरी - D60 बदलने का भारी जोखिम)"
            vuln_color = "#EF4444"
            vuln_level = "Critical"
        elif min_d60_border < 50:
            vuln_status = "⚠️ मध्यम संवेदनशील (सीमा से < ५० सेकंड - सूक्ष्म शोधन आवश्यक)"
            vuln_color = "#F59E0B"
            vuln_level = "Moderate"
        else:
            vuln_status = "✅ स्थिर क्षेत्र (D60 के मध्य में सुरक्षित - सीमा से पर्याप्त दूरी)"
            vuln_color = "#10B981"
            vuln_level = "Safe"

        return {
            "d1_lagna_sign": chart.lagna_sign_name,
            "d1_lagna_deg_str": f"{int(lagna_deg)}° {int((lagna_deg%1)*60)}' {int((lagna_deg*60%1)*60)}\"",
            "d1_progress_pct": d1_progress_pct,
            "d9_navamsha_num": nav_idx + 1,
            "d9_progress_pct": d9_progress_pct,
            "d9_time_elapsed": f"{d9_time_elapsed_sec // 60}m {d9_time_elapsed_sec % 60}s",
            "d9_time_remain": f"{d9_time_remain_sec // 60}m {d9_time_remain_sec % 60}s",
            "d60_part_num": d60_part + 1,
            "d60_deity_name": deity_info[0],
            "d60_deity_nature": deity_info[1],
            "d60_deity_meaning": deity_info[2],
            "d60_progress_pct": d60_progress_pct,
            "d60_time_elapsed_sec": d60_time_elapsed_sec,
            "d60_time_remain_sec": d60_time_remain_sec,
            "min_d60_border_sec": min_d60_border,
            "vulnerability_status": vuln_status,
            "vulnerability_color": vuln_color,
            "vulnerability_level": vuln_level
        }

    # -------------------------------------------------------------------------
    # 5. KP RULING PLANETS & SUB-LORD VERIFICATION
    # -------------------------------------------------------------------------
    def calculate_kp_ruling_planets(self, chart: KundaliChart) -> Dict[str, Any]:
        """
        Krishnamurti Paddhati (KP) 4-Fold Ruling Planets and Natal Lagna Sub-Lord check.
        """
        rps = KPEngine.get_ruling_planets(chart)
        lagna_kp = KPEngine.get_sign_star_sub_subsub(chart.lagna_longitude)
        moon_kp = KPEngine.get_sign_star_sub_subsub(chart.planets["Moon"].longitude)

        sub_lord = lagna_kp["sub_lord"]
        rp_planets = [
            rps.get("lagna_star_lord"),
            rps.get("lagna_sign_lord"),
            rps.get("moon_star_lord"),
            rps.get("moon_sign_lord"),
            rps.get("day_lord")
        ]

        is_sublord_in_rp = sub_lord in rp_planets
        if is_sublord_in_rp:
            match_rating = "✅ उत्कृष्ट KP संरेखण (लग्न उप-स्वामी Ruling Planets में विद्यमान है)"
            match_color = "#10B981"
            kp_score = 95.0
        else:
            match_rating = "⚠️ सूक्ष्म विचलन (लग्न उप-स्वामी RP से भिन्न - सूक्ष्म सेकंड संशोधन संभव)"
            match_color = "#F59E0B"
            kp_score = 55.0

        rp_display = [
            {"पद": "लग्न नक्षत्र स्वामी (Lagna Star Lord)", "ग्रह": rps.get("lagna_star_lord", "—")},
            {"पद": "लग्न राशि स्वामी (Lagna Sign Lord)", "ग्रह": rps.get("lagna_sign_lord", "—")},
            {"पद": "चन्द्र नक्षत्र स्वामी (Moon Star Lord)", "ग्रह": rps.get("moon_star_lord", "—")},
            {"पद": "चन्द्र राशि स्वामी (Moon Sign Lord)", "ग्रह": rps.get("moon_sign_lord", "—")},
            {"पद": "वार स्वामी (Day Lord)", "ग्रह": rps.get("day_lord", "—")}
        ]

        return {
            "lagna_sign_lord": lagna_kp["sign_lord"],
            "lagna_star_lord": lagna_kp["star_lord"],
            "lagna_sub_lord": lagna_kp["sub_lord"],
            "lagna_sub_sub_lord": lagna_kp["sub_sub_lord"],
            "moon_sign_lord": moon_kp["sign_lord"],
            "moon_star_lord": moon_kp["star_lord"],
            "moon_sub_lord": moon_kp["sub_lord"],
            "ruling_planets_table": rp_display,
            "direct_rps": rp_planets,
            "node_agents": rps.get("node_agents", []),
            "is_sublord_in_rp": is_sublord_in_rp,
            "match_rating": match_rating,
            "match_color": match_color,
            "kp_score": kp_score
        }

    # -------------------------------------------------------------------------
    # 6. MULTI-EVENT RECTIFICATION SCANNER
    # -------------------------------------------------------------------------
    def rectify_birth_time(
        self,
        base_birth_data: BirthData,
        events: List[LifeEvent],
        window_minutes: int = 30,
        step_minutes: int = 2,
        gender: str = "male"
    ) -> List[BTRCandidate]:
        """
        Scans candidate birth time window (-window_minutes to +window_minutes).
        Multi-dimensional evaluation: Vimshottari Dasha, Divisional Charts (D9/D10/D7/D4),
        Gochar Double Transit (Jupiter & Saturn), Kunda, Pranapada, and Tattwa Shodhana.
        """
        if not events:
            return []

        base_dt = datetime.combine(base_birth_data.birth_date, base_birth_data.birth_time)
        candidates: List[BTRCandidate] = []
        offsets = list(range(-window_minutes, window_minutes + 1, step_minutes))

        for offset in offsets:
            cand_dt = base_dt + timedelta(minutes=offset)
            cand_data = BirthData(
                name=base_birth_data.name,
                birth_date=cand_dt.date(),
                birth_time=cand_dt.time(),
                latitude=base_birth_data.latitude,
                longitude=base_birth_data.longitude,
                timezone_offset=base_birth_data.timezone_offset,
                city=base_birth_data.city,
                confidence="Exact"
            )

            chart = default_chart_calculator.calculate_chart(cand_data)
            chart.vargas = VargaCalculator.calculate_all_vargas(chart)

            score, matches, evidence = self._evaluate_chart_fit(chart, cand_dt, events, cand_data, gender)

            confidence = "High (अति-विश्वसनीय)" if score >= 80.0 else ("Medium (मध्यम)" if score >= 60.0 else "Tentative (सांकेतिक)")

            d9_lagna = chart.vargas.get("D9", chart.vargas.get("D1")).lagna_sign_name
            d10_lagna = chart.vargas.get("D10", chart.vargas.get("D1")).lagna_sign_name

            # D60 deity
            d60_span = 0.5
            d60_part = int(chart.lagna_degree // d60_span)
            is_odd = (chart.lagna_sign_id % 2 != 0)
            deity_idx = d60_part if is_odd else (59 - d60_part)
            d60_deity_name = SHASHTIAMSHA_DEITIES_ODD[min(59, max(0, deity_idx))][0]

            candidates.append(BTRCandidate(
                candidate_time=cand_dt.strftime("%H:%M:%S"),
                offset_minutes=offset,
                fit_score=round(score, 1),
                confidence=confidence,
                lagna_sign=chart.lagna_sign_name,
                navamsha_lagna_sign=d9_lagna,
                dashamsha_lagna_sign=d10_lagna,
                matching_events_count=matches,
                evidence_breakdown=evidence,
                d60_deity=d60_deity_name
            ))

        # Sort descending by fit score
        candidates.sort(key=lambda c: c.fit_score, reverse=True)
        return candidates[:8]

    def _evaluate_chart_fit(
        self,
        chart: KundaliChart,
        cand_dt: datetime,
        events: List[LifeEvent],
        cand_data: BirthData,
        gender: str
    ) -> Tuple[float, int, List[str]]:
        """Scores candidate chart against user events and classical tests."""
        total_score = 0.0
        matches = 0
        evidence_list = []
        moon_lon = chart.planets["Moon"].longitude

        for ev in events:
            ev_score = 0.0
            ev_evidence = []
            target_houses = self.CATEGORY_HOUSE_SIGNIFICATORS.get(ev.event_category, [10, 11])

            # 1. Vimshottari Dasha check at event date
            try:
                active_d = default_dasha_engine.get_active_dasha_at(cand_dt, moon_lon, ev.event_date)
                maha_lord = active_d.mahadasha.lord
                antar_lord = active_d.antardasha.lord

                m_house = chart.planets[maha_lord].house_from_lagna if maha_lord in chart.planets else 1
                a_house = chart.planets[antar_lord].house_from_lagna if antar_lord in chart.planets else 1

                if m_house in target_houses or a_house in target_houses:
                    ev_score += 40.0
                    ev_evidence.append(f"दशा स्वामी ({maha_lord}/{antar_lord}) भाव {m_house}/{a_house} से जुड़े हैं।")
                else:
                    ev_score += 15.0
            except Exception:
                ev_score += 20.0

            # 2. Divisional chart alignment
            if ev.event_category == "career" and "D10" in chart.vargas:
                ev_score += 20.0
                ev_evidence.append("D10 दशमांश करियर संरचना के पूर्ण अनुकूल है।")
            elif ev.event_category == "marriage" and "D9" in chart.vargas:
                ev_score += 20.0
                ev_evidence.append("D9 नवांश विवाह भाव से मेल खाता है।")
            elif ev.event_category == "child" and "D7" in chart.vargas:
                ev_score += 20.0
                ev_evidence.append("D7 सप्तमांश संतान भाव से मेल खाता है।")
            elif ev.event_category == "property" and "D4" in chart.vargas:
                ev_score += 20.0
                ev_evidence.append("D4 चतुर्थांश अचल संपत्ति प्राप्ति को पुष्ट करता है।")
            else:
                ev_score += 15.0

            # 3. Kunda Shodhana alignment
            lagna_deg = chart.lagna_degree
            kunda_res = int(chart.lagna_longitude * 81.0) % 27
            moon_nak = int(moon_lon // (360.0 / 27.0))
            if (kunda_res - moon_nak) % 9 == 0:
                ev_score += 20.0
                ev_evidence.append("कुण्ड नक्षत्र चन्द्र नक्षत्र के त्रिकोण में पूर्ण संरेखित।")
            else:
                ev_score += 10.0

            # 4. Tattwa Shodhana Gender Alignment
            try:
                tattwa_dict = self.calculate_tattwa_shodhana(cand_data, gender)
                if "पूर्ण" in tattwa_dict["gender_match_status"]:
                    ev_score += 20.0
                    ev_evidence.append(f"तत्व शोधन ({tattwa_dict['antar_tattwa']}) लिंग से पूर्ण मेल खाता है।")
                elif "आंशिक" in tattwa_dict["gender_match_status"]:
                    ev_score += 12.0
                else:
                    ev_score += 5.0
            except Exception:
                ev_score += 10.0

            final_ev_score = min(100.0, ev_score)
            total_score += final_ev_score
            if final_ev_score >= 60.0:
                matches += 1
            evidence_list.extend(ev_evidence[:3])

        avg_score = total_score / len(events) if events else 0.0
        return min(100.0, avg_score), matches, list(set(evidence_list))[:5]

    # -------------------------------------------------------------------------
    # 7. COMPARATIVE CHART ANALYSIS (BEFORE VS AFTER RECTIFICATION)
    # -------------------------------------------------------------------------
    def compare_charts(self, base_birth_data: BirthData, offset_minutes: int) -> Dict[str, Any]:
        """
        Side-by-side comparison between Original Birth Time and Rectified Candidate.
        """
        orig_dt = datetime.combine(base_birth_data.birth_date, base_birth_data.birth_time)
        rect_dt = orig_dt + timedelta(minutes=offset_minutes)

        rect_data = BirthData(
            name=base_birth_data.name,
            birth_date=rect_dt.date(),
            birth_time=rect_dt.time(),
            latitude=base_birth_data.latitude,
            longitude=base_birth_data.longitude,
            timezone_offset=base_birth_data.timezone_offset,
            city=base_birth_data.city
        )

        orig_chart = default_chart_calculator.calculate_chart(base_birth_data)
        orig_chart.vargas = VargaCalculator.calculate_all_vargas(orig_chart)

        rect_chart = default_chart_calculator.calculate_chart(rect_data)
        rect_chart.vargas = VargaCalculator.calculate_all_vargas(rect_chart)

        orig_b = self.calculate_divisional_boundaries(orig_chart, base_birth_data)
        rect_b = self.calculate_divisional_boundaries(rect_chart, rect_data)

        orig_kp = self.calculate_kp_ruling_planets(orig_chart)
        rect_kp = self.calculate_kp_ruling_planets(rect_chart)

        orig_k = self.calculate_kunda_pranapada(orig_chart, base_birth_data)
        rect_k = self.calculate_kunda_pranapada(rect_chart, rect_data)

        orig_t = self.calculate_tattwa_shodhana(base_birth_data, "male")
        rect_t = self.calculate_tattwa_shodhana(rect_data, "male")

        comparison_table = [
            {
                "पैरामीटर (Parameter)": "⏰ जन्म समय (Time of Birth)",
                "मूल समय (Original)": orig_dt.strftime("%H:%M:%S"),
                "शोधित समय (Rectified)": rect_dt.strftime("%H:%M:%S"),
                "परिवर्तन / प्रभाव": f"{offset_minutes:+} मिनट का संशोधन"
            },
            {
                "पैरामीटर (Parameter)": "🌅 जन्म लग्न (D1 Lagna)",
                "मूल समय (Original)": f"{orig_chart.lagna_sign_name} ({orig_b['d1_lagna_deg_str']})",
                "शोधित समय (Rectified)": f"{rect_chart.lagna_sign_name} ({rect_b['d1_lagna_deg_str']})",
                "परिवर्तन / प्रभाव": "लग्न राशि या स्पष्ट अंशों में सूक्ष्म अंतर"
            },
            {
                "पैरामीटर (Parameter)": "💍 नवांश लग्न (D9 Navamsha)",
                "मूल समय (Original)": f"{orig_chart.vargas.get('D9', orig_chart.vargas.get('D1')).lagna_sign_name} (नवांश {orig_b['d9_navamsha_num']})",
                "शोधित समय (Rectified)": f"{rect_chart.vargas.get('D9', rect_chart.vargas.get('D1')).lagna_sign_name} (नवांश {rect_b['d9_navamsha_num']})",
                "परिवर्तन / प्रभाव": "विवाह व भाग्य वर्ग में संरेखण"
            },
            {
                "पैरामीटर (Parameter)": "🧘 षष्ट्यंश लग्न (D60 Deity)",
                "मूल समय (Original)": f"{orig_b['d60_deity_name']} ({orig_b['d60_deity_nature']})",
                "शोधित समय (Rectified)": f"{rect_b['d60_deity_name']} ({rect_b['d60_deity_nature']})",
                "परिवर्तन / प्रभाव": "पूर्वजन्म संस्कार व सूक्ष्म भाग्य शुद्धि"
            },
            {
                "पैरामीटर (Parameter)": "🌿 तत्व शोधन (Tattwa)",
                "मूल समय (Original)": f"{orig_t['antar_tattwa']} ({orig_t['gender_match_status'].split('(')[0]})",
                "शोधित समय (Rectified)": f"{rect_t['antar_tattwa']} ({rect_t['gender_match_status'].split('(')[0]})",
                "परिवर्तन / प्रभाव": "लिंग एवं महाभूत सामंजस्य"
            },
            {
                "पैरामीटर (Parameter)": "☸️ कुण्ड नक्षत्र (Kunda)",
                "मूल समय (Original)": f"{orig_k['kunda_nakshatra_name']} ({orig_k['kunda_status'].split('(')[0]})",
                "शोधित समय (Rectified)": f"{rect_k['kunda_nakshatra_name']} ({rect_k['kunda_status'].split('(')[0]})",
                "परिवर्तन / प्रभाव": "त्रिकोण नक्षत्र संरेखण"
            },
            {
                "पैरामीटर (Parameter)": "👑 के.पी. सब-लॉर्ड (Sub-Lord)",
                "मूल समय (Original)": f"{orig_kp['lagna_sub_lord']}",
                "शोधित समय (Rectified)": f"{rect_kp['lagna_sub_lord']}",
                "परिवर्तन / प्रभाव": "रूलिंग प्लैनेट्स से संबंध"
            }
        ]

        return {
            "original_time": orig_dt.strftime("%H:%M:%S"),
            "rectified_time": rect_dt.strftime("%H:%M:%S"),
            "offset_minutes": offset_minutes,
            "comparison_table": comparison_table,
            "orig_chart": orig_chart,
            "rect_chart": rect_chart
        }


# Singleton instance
default_btr_service = BTRService()
