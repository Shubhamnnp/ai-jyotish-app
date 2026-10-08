"""
Executive UI View for Vedic Jyotish Panchang module.
Provides a comprehensive, world-class Shastriya Panchang interface exceeding Drik Panchang standards.
12 Complete Shastriya Tabs:
1. Pancha-Anga (5 Core Pillars): Tithi, Nakshatra, Yoga, Karana, Vara with exact ending times, degrees, padas & deities.
2. Festivals & Vrat Engine: Ekadashis with Parana timings, Pradosha, Shivaratri, Chaturthis, Purnima/Amavasya.
3. Paksha & Pitru Paksha Deep Engine: Strict prohibitions (क्या-क्या नहीं कर सकते), Prescribed deeds, Kutupa/Rohina/Aparahna kaal.
4. 24-Hour Rising Lagna Table: Start-End moments of all 12 Lagnas, Nature (चर/स्थिर/द्विस्वभाव), Elements, Muhurta suitability.
5. Auspicious & Inauspicious Muhurtas: Abhijit, Brahma, Vijaya, Godhuli, Amrit Kaal, Rahu Kaal, Yamaghanta, Gulika, Durmuhurta, Varjyam.
6. Choghadiya, Horas & 60-Ghati Vedic Clock: 8 Day + 8 Night Choghadiyas, 24 Planetary Horas, Ishtakala clock.
7. Bhadra, Panchaka & Gandamoola: Bhadra Vasa (Swarga/Patala/Bhuloka), Mukha (5 ghatis), Puchha (3 ghatis), Panchaka doshas, Gandamoola shanti.
8. Chandra Balam, Tara Balam & Auspicious Yogas: 12 Moon Sign Chandra Balam, 27 Nakshatra Navatara matrix, 28 Anandadi yogas.
9. Planetary Transit Matrix & Cabinet: Real-time planet degrees, retro/combustion, 60 Samvatsaras & Planetary Cabinet.
10. Vedic Sankalpa Mantra Generator: Dynamic Sanskrit text with Yajamana name, Gotra, Intent selection & ritual guide.
11. Monthly Calendar Grid View: 7-day responsive interactive calendar grid with tithis, festivals, and one-click inspection.
12. AI Panchang Sarathi & Action Suitability: Conversational AI advisor for specific muhurta queries + 12-deed suitability scorecard.
"""

import streamlit as st
import importlib
import calendar
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List

import src.jyotish.services.panchang as panchang_svc_module
importlib.reload(panchang_svc_module)
from src.jyotish.services.panchang import VedicPanchangService


POPULAR_CITIES = {
    "नई दिल्ली (New Delhi)": {"lat": 28.6139, "lon": 77.2090, "tz": 5.5},
    "वाराणसी (Varanasi / Kashi)": {"lat": 25.3176, "lon": 82.9739, "tz": 5.5},
    "उज्जैन (Ujjain - महाकाल)": {"lat": 23.1765, "lon": 75.7885, "tz": 5.5},
    "हरिद्वार (Haridwar)": {"lat": 29.9457, "lon": 78.1642, "tz": 5.5},
    "अयोध्या (Ayodhya)": {"lat": 26.7922, "lon": 82.1998, "tz": 5.5},
    "मथुरा (Mathura)": {"lat": 27.4924, "lon": 77.6737, "tz": 5.5},
    "मुंबई (Mumbai)": {"lat": 19.0760, "lon": 72.8777, "tz": 5.5},
    "कोलकाता (Kolkata)": {"lat": 22.5726, "lon": 88.3639, "tz": 5.5},
    "चेन्नई (Chennai)": {"lat": 13.0827, "lon": 80.2707, "tz": 5.5},
    "बेंगलुरु (Bengaluru)": {"lat": 12.9716, "lon": 77.5946, "tz": 5.5},
    "जयपुर (Jaipur)": {"lat": 26.9124, "lon": 75.7873, "tz": 5.5},
    "अहमदाबाद (Ahmedabad)": {"lat": 23.0225, "lon": 72.5714, "tz": 5.5},
    "लखनऊ (Lucknow)": {"lat": 26.8467, "lon": 80.9462, "tz": 5.5},
    "पटना (Patna)": {"lat": 25.5941, "lon": 85.1376, "tz": 5.5},
}


def ask_ai_panchang_advisor(query: str, p_data: Dict[str, Any]) -> str:
    """Provides high-intelligence, Shastriya astrological answers for panchang questions."""
    m = p_data.get("meta", {})
    pil = p_data.get("five_pillars", {})
    t = pil.get("tithi", {})
    v = pil.get("vara", {})
    nak = pil.get("nakshatra", {})
    yg = pil.get("yoga", {})
    kc = pil.get("karana", {}).get("current", {})
    pak = p_data.get("paksha_engine", {})
    pitru = pak.get("pitru_paksha", {})
    bhadra = p_data.get("bhadra", {})
    muh = p_data.get("muhurtas", {})

    api_key = os.getenv("GEMINI_API_KEY") or st.session_state.get("gemini_api_key")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            prompt = f"""You are 'दैवज्ञ पञ्चाङ्ग सारथी' (Daivajna Panchang AI Advisor), an authority on Vedic Panchang, Muhurta Chintamani, and Brihat Samhita.
User asked: "{query}"

TODAY'S ACCURATE CELESTIAL COORDINATES:
- Date & City: {m.get('date_str')} at {m.get('city')}
- Tithi: {t.get('name')} ({t.get('paksha')}), Ends: {t.get('end_time_str')}
- Vara: {v.get('name_hi')} (Lord: {v.get('lord')})
- Nakshatra: {nak.get('name')} (Pada {nak.get('pada')}, Lord: {nak.get('lord')}), Ends: {nak.get('end_time_str')}
- Yoga: {yg.get('name')} ({yg.get('nature')})
- Karana: {kc.get('name')} ({kc.get('type')})
- Primary Festival/Vrat: {m.get('primary_festival')}
- Pitru Paksha Active: {pitru.get('is_active', False)} (Shradh: {pitru.get('shradh_name', 'None')})
- Bhadra Active: {bhadra.get('is_present', False)} (Fatal on Earth: {bhadra.get('is_fatal_on_earth', False)})
- Rahu Kaal: {muh.get('ashubh_windows', [{}])[0].get('time', 'N/A') if muh.get('ashubh_windows') else 'N/A'}
- Abhijit Muhurta: {next((x.get('time', 'N/A') for x in muh.get('shubh_windows', []) if 'अभिजित' in x.get('title', '') or 'अभिजित' in x.get('name', '')), 'आज अनुपस्थित')}
- Day Verdict: {m.get('day_verdict')}

Respond directly in respectful, clear Hindi (4-6 bullet points) with exact Shastriya reasoning, whether the activity is recommended or prohibited today, and what specific auspicious window or remedy to use."""
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2)
            )
            if resp and resp.text:
                return resp.text
        except Exception:
            pass

    # Expert Shastriya Rule-Based Intelligence
    q_low = query.lower()
    is_pitru = pitru.get("is_active", False)
    is_bhadra = bhadra.get("is_fatal_on_earth", False)
    abhijit = next((x.get('time', 'N/A') for x in muh.get('shubh_windows', []) if 'अभिजित' in x.get('title', '') or 'अभिजित' in x.get('name', '')), 'आज अभिजित मुहूर्त नहीं है')

    if any(k in q_low for k in ["वाहन", "गाड़ी", "car", "vehicle", "bike", "vahan"]):
        if is_pitru:
            return "🚫 **वाहन क्रय विचार:** वर्तमान में **पितृपक्ष (महालय श्राद्ध)** सक्रिय है। शास्त्रों अनुसार इस अवधि में नवीन वाहन अथवा विलासिता सामग्री का प्रथम उपभोग त्याज्य माना गया है। यदि अति-आवश्यक हो, तो केवल अग्रिम बुकिंग (बुकिंग टोकन) कर सकते हैं, परन्तु वाहन की डिलीवरी व प्रथम पूजन सर्वपितृ अमावस्या के बाद शारदीय नवरात्रि में करना सर्वोत्तम रहेगा।"
        elif is_bhadra:
            return f"⚠️ **वाहन क्रय विचार:** आज भद्रा का प्रभाव है। भद्रा समाप्ति के उपरान्त अथवा आज के **अभिजित मुहूर्त ({abhijit})** अथवा शुभ/अमृत चौघड़िया में वाहन क्रय करना अनुकूल रहेगा।"
        else:
            return f"🟢 **वाहन क्रय विचार:** आज का दिन वाहन क्रय हेतु अनुकूल है। विशेषकर **अभिजित मुहूर्त ({abhijit})** अथवा दिन के लाभ/अमृत चौघड़िया में वाहन लेना शुभ फलदायी रहेगा। राहुकाल से बचें।"

    elif any(k in q_low for k in ["गृह प्रवेश", "गृहप्रवेश", "house", "griha", "home"]):
        if is_pitru:
            return "🚫 **गृह प्रवेश निर्णय:** **पितृपक्ष में नूतन गृह प्रवेश सर्वथा वर्जित है।** निर्णय सिन्धु व मुहूर्त चिन्तामणि के अनुसार पितृपक्ष में किया गया गृह प्रवेश गृह क्लेश, अशांति व पितृ दोष का कारण बनता है। कृपया देवोत्थान एकादशी के बाद शुभ मुहूर्त में ही गृह प्रवेश करें।"
        else:
            return f"⚠️ **गृह प्रवेश निर्णय:** गृह प्रवेश हेतु स्थिर लग्न (वृषभ, सिंह, कुम्भ) एवं रिक्ता तिथि रहित शुद्ध काल अपेक्षित होता है। आज {t.get('name')} तिथि है। राहुकाल व भद्रा त्यागकर शुभ चौघड़िया में विद्वान ज्योतिषी से शुद्ध लग्न शोधन कराकर ही प्रवेश करें।"

    elif any(k in q_low for k in ["व्यापार", "दुकान", "business", "vyapar", "shop", "office", "start"]):
        if is_pitru:
            return "🚫 **नवीन व्यापार आरम्भ:** पितृपक्ष काल में नए व्यापार, प्रतिष्ठान अथवा दुकान का उद्घाटन करना शास्त्रसम्मत नहीं है। नए आरम्भ हेतु नवरात्रि अथवा दीपावली का काल सर्वोत्तम रहेगा।"
        else:
            return f"🟢 **व्यापार आरम्भ:** आज व्यापार आरम्भ अथवा अनुबंध हेतु **अभिजित मुहूर्त ({abhijit})** अथवा लाभ व अमृत चौघड़िया सर्वश्रेष्ठ है।"

    elif any(k in q_low for k in ["श्राद्ध", "तर्पण", "पिण्डदान", "pitru", "tarpan", "shradh"]):
        return f"🌟 **श्राद्ध व तर्पण विधान:** आज के श्राद्ध का मुख्य काल **कुतुप मुहूर्त ({pitru.get('kutupa_time', '11:45 AM - 12:32 PM')})** एवं **रौहिण मुहूर्त ({pitru.get('rohina_time', '12:32 PM - 01:19 PM')})** है। तर्पण व पिण्डदान **अपराह्न काल ({pitru.get('aparahna_time', '01:19 PM - 03:40 PM')})** में संपन्न करें। पंचबलि कर्म (गौ, श्वान, काक, देवादि, पिपीलिका) अवश्य करें।"

    else:
        return (
            f"📖 **आज का समग्र शास्त्रीय परामर्श:**\n\n"
            f"- **आज का दिवस निर्णय:** {m.get('day_verdict')}\n"
            f"- **सर्वश्रेष्ठ शुभ काल:** अभिजित मुहूर्त ({abhijit})\n"
            f"- **सावधानी / त्याज्य काल:** राहुकाल एवं दिशा शूल ({p_data.get('nivas_shoola', {}).get('disha_shoola', {}).get('direction', 'पूर्व')} दिशा) में यात्रा से बचें।\n"
            f"- **अनुकूलता:** सात्विक कर्म, इष्ट आराधना व दान-पुण्य हेतु दिन मंगलकारी है।"
        )


def render_vedic_panchang_view(chart: Any, birth_profile: Any, is_dark: bool = False):
    """Renders the master Vedic Jyotish Panchang module with 12 rich interactive tabs."""

    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFFDF5 0%, #FEF3C7 50%, #FFFBEB 100%);
                border: 2px solid #F59E0B; padding: 22px 26px; border-radius: 14px;
                margin-bottom: 20px; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.12);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="flex: 1; min-width: 280px;">
                <h2 style="margin:0; font-size:26px; color:#78350F !important; font-weight:800; letter-spacing:0.5px; line-height:1.3;">
                    📅 वैदिक ज्योतिषीय पञ्चाङ्ग (Vedic Jyotish Panchang)
                </h2>
                <p style="margin:6px 0 0 0; color:#92400E !important; font-size:14px; font-weight:500; line-height:1.5;">
                    सूर्य सिद्धान्त, दृक्-गणित, निर्णय सिन्धु एवं मुहूर्त चिन्तामणि पर आधारित १००% प्रामाणिक दैनिक पञ्चाङ्ग, २४-घण्टे लग्न सारणी एवं सङ्कल्प मन्त्र
                </p>
            </div>
            <div style="text-align:right;">
                <span style="background:#FEF2F2; border:1.5px solid #DC2626; color:#991B1B !important;
                             padding:7px 18px; border-radius:24px; font-size:15px; font-weight:800; letter-spacing:0.5px;
                             display:inline-block; box-shadow:0 2px 6px rgba(220, 38, 38, 0.12);">
                    🕉️ ॥ श्री गणेशाय नमः ॥
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TOP CONTROLS: Date, Location & Preset Quick Select
    # -------------------------------------------------------------
    col_c1, col_c2, col_c3, col_c4 = st.columns([1.5, 1.8, 1.2, 1.5])

    today_dt = date.today()

    with col_c1:
        selected_date = st.date_input(
            "📅 पञ्चाङ्ग दिनांक (Select Date)",
            value=today_dt,
            key="panchang_selected_date"
        )

    with col_c2:
        city_names = list(POPULAR_CITIES.keys())
        default_city_idx = 0
        if hasattr(birth_profile, "city") and birth_profile.city:
            for idx, c_name in enumerate(city_names):
                if birth_profile.city.lower() in c_name.lower():
                    default_city_idx = idx
                    break

        selected_city_name = st.selectbox(
            "📍 प्रमुख धार्मिक / प्रशासनिक नगर",
            city_names,
            index=default_city_idx,
            key="panchang_selected_city"
        )

    city_info = POPULAR_CITIES[selected_city_name]
    lat_val = city_info["lat"]
    lon_val = city_info["lon"]
    tz_val = city_info["tz"]

    with col_c3:
        quick_action = st.selectbox(
            "⚡ त्वरित चयन",
            ["आज (Today)", "कल (Tomorrow)", "कुण्डली जन्म तिथि", "एकादशी / अमावस्या"],
            key="panchang_quick_jump"
        )
        if quick_action == "कल (Tomorrow)" and selected_date != today_dt + timedelta(days=1):
            selected_date = today_dt + timedelta(days=1)
        elif quick_action == "कुण्डली जन्म तिथि" and hasattr(birth_profile, "date_of_birth"):
            selected_date = birth_profile.date_of_birth

    with col_c4:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                    border-radius:10px; padding:10px 14px; text-align:center; margin-top:4px;">
            <span style="font-size:12px; color:{'#9CA3AF' if is_dark else '#64748B'};">भौगोलिक स्थिति</span>
            <div style="font-size:14px; font-weight:700; color:{'#F9FAFB' if is_dark else '#0F172A'};">
                {lat_val:.2f}° N, {lon_val:.2f}° E
            </div>
            <small style="color:#2563EB; font-weight:600;">IST (UTC +{tz_val})</small>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # CALCULATE PANCHANG DATA
    # -------------------------------------------------------------
    with st.spinner("ज्योतिषीय पञ्चाङ्ग गणना एवं शास्त्रीय शोधन प्रगति पर है..."):
        panchang_data = VedicPanchangService.get_full_panchang(
            target_date=selected_date,
            latitude=lat_val,
            longitude=lon_val,
            city_name=selected_city_name,
            tz_offset_hours=tz_val
        )

    meta = panchang_data["meta"]
    sun_moon = panchang_data["sun_moon"]
    pillars = panchang_data["five_pillars"]
    bhadra = panchang_data["bhadra"]
    pg = panchang_data["panchak_gandamoola"]
    chog = panchang_data["choghadiya_horas"]
    muh = panchang_data["muhurtas"]
    yogas = panchang_data["yogas"]
    nivas = panchang_data["nivas_shoola"]
    balam = panchang_data["balam"]
    samvat = panchang_data["samvatsar"]
    transit = panchang_data["transit_matrix"]
    paksha_eng = panchang_data.get("paksha_engine") or {}
    pitru = paksha_eng.get("pitru_paksha", {})
    lagna_table = panchang_data.get("lagna_table", [])
    festivals_vrat = panchang_data.get("festivals_and_vrat", {})
    sankalpa_mantra = panchang_data.get("sankalpa_mantra", {})
    gowri = panchang_data.get("gowri_panchangam", {})
    baana = panchang_data.get("baana_dosha", {})

    # -------------------------------------------------------------
    # HERO BANNER: Day, Sunrise/Sunset, Samvat & Day Quality
    # -------------------------------------------------------------
    sr_str = sun_moon["sunrise"].strftime("%I:%M %p")
    ss_str = sun_moon["sunset"].strftime("%I:%M %p")
    mr_str = sun_moon["moonrise"].strftime("%I:%M %p") if sun_moon["moonrise"] else "—"
    ms_str = sun_moon["moonset"].strftime("%I:%M %p") if sun_moon["moonset"] else "—"

    col_h1, col_h2, col_h3, col_h4 = st.columns([1.6, 1.4, 1.4, 1.6])

    with col_h1:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#EFF6FF'}; border:1px solid {'#374151' if is_dark else '#BFDBFE'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:13px; color:#1E40AF; font-weight:600;">{meta['date_hi']}</div>
            <div style="font-size:24px; font-weight:800; color:#1D4ED8; margin:4px 0;">{pillars['vara']['name_hi']}</div>
            <span style="font-size:12px; color:#3B82F6;">वार स्वामी: <b>{pillars['vara']['lord']}</b></span>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#FEF3C7'}; border:1px solid {'#374151' if is_dark else '#FDE68A'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:12px; color:#92400E; font-weight:600;">☀️ सौर गणना</div>
            <div style="font-size:15px; font-weight:700; color:#B45309; margin:4px 0;">
                सूर्योदय: {sr_str}<br/>सूर्यास्त: {ss_str}
            </div>
            <span style="font-size:11.5px; color:#78350F;">दिनमान: {sun_moon['dinamana_ghatis']} घटी</span>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#F0FDFA'}; border:1px solid {'#374151' if is_dark else '#CCFBF1'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:12px; color:#0F766E; font-weight:600;">🌙 चान्द्र गणना</div>
            <div style="font-size:15px; font-weight:700; color:#0D9488; margin:4px 0;">
                चन्द्रोदय: {mr_str}<br/>चन्द्रास्त: {ms_str}
            </div>
            <span style="font-size:11.5px; color:#115E59;">रात्रिमान: {sun_moon['ratrimana_ghatis']} घटी</span>
        </div>
        """, unsafe_allow_html=True)

    with col_h4:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#FAF5FF'}; border:1px solid {'#374151' if is_dark else '#DDD6FE'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:12px; color:#6D28D9; font-weight:600;">🕉️ संवत्सर व अयन</div>
            <div style="font-size:14px; font-weight:700; color:#5B21B6; margin:4px 0;">
                विक्रम संवत {samvat['vikram_samvat']} | शक {samvat['shaka_samvat']}<br/>
                {samvat['ayana']}
            </div>
            <span style="font-size:12px; color:#7C3AED; font-weight:700;">{samvat['ritu']} ({samvat['solar_month']})</span>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # PRIMARY FESTIVAL BADGE (If present)
    # -------------------------------------------------------------
    prim_fest = meta.get("primary_festival")
    if prim_fest and "सामान्य दिवस" not in prim_fest:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #FFFBEB 0%, #FEF3C7 100%); border:1.5px solid #F59E0B;
                    border-radius:10px; padding:10px 18px; margin:14px 0; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:22px;">🚩</span>
                <div>
                    <b style="color:#B45309; font-size:16px;">आज का मुख्य पर्व / महा-व्रत:</b>
                    <span style="color:#92400E; font-size:16px; font-weight:800; margin-left:6px;">{prim_fest}</span>
                </div>
            </div>
            <div>
                <span style="background:#F59E0B; color:#FFFFFF; padding:4px 12px; border-radius:14px; font-size:12px; font-weight:700;">
                    पर्व व व्रत काल
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # PITRU PAKSHA GRAND ALERT BANNER (If Active)
    # -------------------------------------------------------------
    if pitru.get("is_active"):
        st.markdown(f"""
        <div style="background:#FEF2F2; border:2px solid #DC2626; border-radius:12px; padding:16px 20px; margin:16px 0;
                    box-shadow:0 4px 12px rgba(220, 38, 38, 0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <h3 style="margin:0; color:#991B1B; font-size:20px; font-weight:800;">
                        🪔 {pitru['shradh_name']} — पितृपक्ष (महालय श्राद्ध काल) सक्रिय!
                    </h3>
                    <div style="margin-top:4px; color:#7F1D1D; font-size:13.5px;">
                        {pitru['verdict_desc']}
                    </div>
                </div>
                <div style="margin-top:4px;">
                    <span style="background:#DC2626; color:#FFFFFF; padding:5px 14px; border-radius:20px; font-weight:700; font-size:12.5px;">
                        🚫 समस्त मांगलिक कार्य सर्वथा वर्जित
                    </span>
                </div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:10px; margin-top:12px;">
                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                    <b style="color:#991B1B; font-size:13px;">☀️ कुतुप मुहूर्त (श्राद्ध का मुख्य काल):</b>
                    <div style="color:#0F172A; font-weight:700; font-size:14px;">{pitru['kutupa_time']}</div>
                </div>
                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                    <b style="color:#991B1B; font-size:13px;">☀️ रौहिण मुहूर्त:</b>
                    <div style="color:#0F172A; font-weight:700; font-size:14px;">{pitru['rohina_time']}</div>
                </div>
                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                    <b style="color:#991B1B; font-size:13px;">🌊 अपराह्न काल (पिण्डदान व तर्पण):</b>
                    <div style="color:#0F172A; font-weight:700; font-size:14px;">{pitru['aparahna_time']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # General Status Alert Bar
    verdict_badge = meta["day_verdict"]
    verdict_col = meta["day_verdict_color"]
    st.markdown(f"""
    <div style="background:{verdict_col}15; border-left:5px solid {verdict_col}; border-radius:8px;
                padding:12px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <b style="color:{verdict_col}; font-size:15px;">🌟 आज का समग्र शास्त्रीय निर्णय: {verdict_badge}</b>
            <span style="color:{'#E5E7EB' if is_dark else '#374151'}; font-size:13.5px; margin-left:10px;">
                | भद्रा: <b>{bhadra['badge']}</b> | पञ्चक: <b>{pg['panchaka']['name']}</b> | गण्डमूल: <b>{pg['gandamoola']['badge']}</b>
            </span>
        </div>
        <div>
            <span style="font-size:12.5px; color:#2563EB; font-weight:700;">वैदिक इष्टकाल: {nivas['vedic_clock']['ishta_str']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Expandable Digital Panchang Patri (WhatsApp / Print Share)
    with st.expander("🖨️ दैनिक डिजिटल पञ्चाङ्ग पत्रक (WhatsApp / Print Shareable Card)"):
        st.markdown(f"""
        <div style="background:#FFFFFF; border:2px solid #B45309; border-radius:12px; padding:20px; font-family:sans-serif; max-width:680px; margin:auto; box-shadow:0 4px 14px rgba(0,0,0,0.08);">
            <div style="text-align:center; border-bottom:2px dashed #D97706; padding-bottom:12px; margin-bottom:12px;">
                <h3 style="margin:0; color:#92400E; font-size:22px;">🕉️ श्री गणेशाय नमः | दैनिक पञ्चाङ्ग पत्रक 🕉️</h3>
                <div style="color:#B45309; font-size:14px; font-weight:700; margin-top:4px;">
                    {meta['city']} | {meta['date_hi']} ({pillars['vara']['name_hi']})
                </div>
                <small style="color:#78350F;">विक्रम संवत {samvat['vikram_samvat']} | शक संवत {samvat['shaka_samvat']} | {samvat['ayana']} | {samvat['ritu']}</small>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:13.5px; line-height:1.7; color:#1E293B;">
                <div>• <b>तिथि:</b> {pillars['tithi']['name']} ({pillars['tithi']['paksha']}) पर्यन्त {pillars['tithi']['end_time_str']}</div>
                <div>• <b>नक्षत्र:</b> {pillars['nakshatra']['name']} (चरण {pillars['nakshatra']['pada']}) पर्यन्त {pillars['nakshatra']['end_time_str']}</div>
                <div>• <b>योग:</b> {pillars['yoga']['name']} पर्यन्त {pillars['yoga']['end_time_str']}</div>
                <div>• <b>करण:</b> {pillars['karana']['current']['name']} पर्यन्त {pillars['karana']['current']['end_time_str']}</div>
                <div>• <b>सूर्योदय / सूर्यास्त:</b> {sr_str} / {ss_str}</div>
                <div>• <b>चन्द्रोदय / चन्द्रास्त:</b> {mr_str} / {ms_str}</div>
                <div>• <b>राहुकाल (त्याज्य):</b> <span style="color:#DC2626; font-weight:700;">{muh.get('ashubh_windows', [{}])[0].get('time', '—') if muh.get('ashubh_windows') else '—'}</span></div>
                <div>• <b>अभिजित मुहूर्त (शुभ):</b> <span style="color:#059669; font-weight:700;">{next((x.get('time', '—') for x in muh.get('shubh_windows', []) if 'अभिजित' in x.get('title', '') or 'अभिजित' in x.get('name', '')), '—')}</span></div>
                <div>• <b>दिशा शूल:</b> {nivas.get('disha_shoola', {}).get('direction', '—')} (उपाय: {nivas.get('disha_shoola', {}).get('parihar', '—')})</div>
                <div>• <b>चन्द्र राशि:</b> {transit[1].get('rashi', 'कर्क') if len(transit) > 1 else 'कर्क'}</div>
            </div>
            {f'<div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:6px; padding:8px 12px; margin-top:12px; font-size:13px; color:#991B1B;"><b>🪔 विशेष:</b> {prim_fest}</div>' if prim_fest else '<div style="margin-top:4px;"></div>'}
            <div style="text-align:center; border-top:1px solid #E2E8F0; padding-top:8px; margin-top:12px; font-size:11.5px; color:#64748B;">
                ज्योतिषीय पञ्चाङ्ग साफ्टवेयर द्वारा प्रमाणित | सर्वमंगलं भवतु
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 12 COMPREHENSIVE TABS
    # -------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "🌟 पञ्चाङ्ग के ५ स्तम्भ",
        "🚩 पर्व, व्रत व एकादशी पारणा",
        "🪔 पक्ष व पितृपक्ष (श्राद्ध)",
        "🏛️ २४-घंटे लग्न सारणी",
        "⏰ शुभ व अशुभ मुहूर्त",
        "☀️ चौघड़िया, होरा व वैदिक घड़ी",
        "🛡️ भद्रा, पञ्चक व गण्डमूल",
        "⚖️ चन्द्रबलम, ताराबलम व शुभ योग",
        "🪐 ग्रह गोचर व मंत्रिमंडल",
        "📜 दैनिक वैदिक सङ्कल्प मन्त्र",
        "📅 मासिक पञ्चाङ्ग कैलेंडर",
        "🤖 AI पञ्चाङ्ग सारथी व कर्म शुद्धि"
    ])

    # =============================================================
    # TAB 1: पञ्चाङ्ग के पाँच स्तम्भ (5 Pillars)
    # =============================================================
    with tab1:
        st.markdown("### 🌟 पञ्चाङ्ग के पाँचों स्तम्भ (Pancha-Anga 5 Core Pillars)")
        st.caption("तिथि, नक्षत्र, योग, करण एवं वार की विशुद्ध खगोलीय व शास्त्रीय गणना समाप्ति काल, अंशात्मक मान एवं स्वामी सहित:")

        col_p1, col_p2, col_p3 = st.columns(3)

        # 1. TITHI CARD
        t = pillars["tithi"]
        with col_p1:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#3B82F6' if not is_dark else '#1E40AF'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#1D4ED8; font-weight:700; font-size:13px;">स्तम्भ १: तिथि</span>
                    <span style="background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        {t['category']}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0 4px 0;">
                    {t['name']} ({t['paksha']})
                </div>
                <div style="color:#DC2626; font-size:14px; font-weight:700; margin-bottom:8px;">
                    ⏳ {t['end_time_str']}
                </div>
                <div style="margin:8px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B;">
                        <span>तिथि भोग ({t['degree_in_tithi']}° / 12°)</span>
                        <span>{t['progress_pct']}% व्यतीत</span>
                    </div>
                    <div style="background:#E2E8F0; border-radius:4px; height:6px; overflow:hidden;">
                        <div style="background:#2563EB; width:{t['progress_pct']}%; height:100%;"></div>
                    </div>
                </div>
                <div style="font-size:12.5px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:10px;">
                    • <b>अधिष्ठाता देवता:</b> {t.get('deity', '—')}<br/>
                    • <b>तिथि संज्ञा:</b> {t.get('category', '—')} ({'रिक्ता तिथि - शुभ कार्य वर्जित' if 'रिक्ता' in t.get('category', '') else 'शुभ फलप्रद'})<br/>
                    • <b>चन्द्र-सूर्य अन्तर:</b> {t.get('degree', 0.0):.2f}°<br/>
                    • <b>आगामी तिथि:</b> {t.get('next_name', '—')} ({t.get('next_paksha', '')})
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. NAKSHATRA CARD
        nak = pillars["nakshatra"]
        with col_p2:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#10B981' if not is_dark else '#065F46'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#047857; font-weight:700; font-size:13px;">स्तम्भ २: नक्षत्र</span>
                    <span style="background:#D1FAE5; color:#065F46; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        चरण {nak['pada']}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0 4px 0;">
                    {nak['name']}
                </div>
                <div style="color:#DC2626; font-size:14px; font-weight:700; margin-bottom:8px;">
                    ⏳ {nak['end_time_str']}
                </div>
                <div style="margin:8px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B;">
                        <span>नक्षत्र भोग ({nak['degree_in_nak']}° / 13°20')</span>
                        <span>{nak['progress_pct']}% व्यतीत</span>
                    </div>
                    <div style="background:#E2E8F0; border-radius:4px; height:6px; overflow:hidden;">
                        <div style="background:#059669; width:{nak['progress_pct']}%; height:100%;"></div>
                    </div>
                </div>
                <div style="font-size:12.5px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:10px;">
                    • <b>नक्षत्र स्वामी:</b> {nak['lord']}<br/>
                    • <b>अधिष्ठाता देवता:</b> {nak['deity']}<br/>
                    • <b>गण / योनि:</b> {nak['gana']} गण | {nak['yoni']} योनि<br/>
                    • <b>नाड़ी / वर्ण:</b> {nak['nadi']} नाड़ी | {nak['varna']}<br/>
                    • <b>आगामी नक्षत्र:</b> {nak['next_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 3. YOGA CARD
        yg = pillars["yoga"]
        yg_bg = "#D1FAE5" if yg["is_good"] else "#FEE2E2"
        yg_col = "#065F46" if yg["is_good"] else "#991B1B"
        with col_p3:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#F59E0B' if not is_dark else '#B45309'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#B45309; font-weight:700; font-size:13px;">स्तम्भ ३: योग</span>
                    <span style="background:{yg_bg}; color:{yg_col}; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        {yg['nature']}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0 4px 0;">
                    {yg['name']} ({yg['name_en']})
                </div>
                <div style="color:#DC2626; font-size:14px; font-weight:700; margin-bottom:8px;">
                    ⏳ {yg['end_time_str']}
                </div>
                <div style="margin:8px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B;">
                        <span>योग भोग ({yg['degree']}°)</span>
                        <span>{yg['progress_pct']}% व्यतीत</span>
                    </div>
                    <div style="background:#E2E8F0; border-radius:4px; height:6px; overflow:hidden;">
                        <div style="background:#D97706; width:{yg['progress_pct']}%; height:100%;"></div>
                    </div>
                </div>
                <div style="font-size:12.5px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:10px;">
                    • <b>योग अधिष्ठाता:</b> {yg['deity']}<br/>
                    • <b>प्रकृति:</b> {'शुभ फलदायी' if yg['is_good'] else 'सावधानी अपेक्षित (वर्जित)'}<br/>
                    • <b>सूर्य + चन्द्र योग:</b> {yg['degree']}°<br/>
                    • <b>आगामी योग:</b> {yg['next_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        col_k1, col_k2 = st.columns(2)

        # 4. KARANA CARD
        kc = pillars["karana"]["current"]
        kn = pillars["karana"]["next"]
        with col_k1:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#8B5CF6' if not is_dark else '#6D28D9'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#7C3AED; font-weight:700; font-size:13px;">स्तम्भ ४: करण (अर्ध-तिथि)</span>
                    <span style="background:#EDE9FE; color:#5B21B6; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        {kc['type']} करण
                    </span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:8px;">
                    <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'};">
                        वर्तमान: {kc['name']}
                    </div>
                    <div style="color:#DC2626; font-size:14px; font-weight:700;">
                        ⏳ {kc['end_time_str']}
                    </div>
                </div>
                <div style="font-size:13px; color:{'#D1D5DB' if is_dark else '#475569'}; margin:6px 0;">
                    • <b>अधिष्ठाता देवता:</b> {kc['deity']} | प्रगति: {kc['progress_pct']}%
                </div>
                <div style="background:#F1F5F9; border-radius:6px; padding:8px 12px; margin-top:8px; display:flex; justify-content:space-between;">
                    <span style="font-size:12.5px; color:#334155;"><b>परवर्ती करण:</b> {kn['name']} ({kn['type']})</span>
                    <span style="font-size:12.5px; color:#DC2626; font-weight:700;">{kn['end_time_str']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 5. VARA CARD
        vr = pillars["vara"]
        with col_k2:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#EC4899' if not is_dark else '#BE185D'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#DB2777; font-weight:700; font-size:13px;">स्तम्भ ५: वार (दिवस)</span>
                    <span style="background:#FCE7F3; color:#9D174D; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        सप्ताह दिवस #{vr['weekday_idx'] + 1}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin-top:8px;">
                    {vr['name_hi']} (Day Lord: {vr['lord']})
                </div>
                <div style="font-size:13px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:8px;">
                    • <b>प्रथम होरा अधिपति:</b> {vr['lord']} (सूर्योदय से प्रथम १ घण्टा)<br/>
                    • <b>दैनिक दिनमान:</b> {sun_moon['dinamana_str']}<br/>
                    • <b>दैनिक रात्रिमान:</b> {sun_moon['ratrimana_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Five Pillars Summary Table
        st.markdown("#### 📋 पञ्चाङ्ग के पाँचों अंगों का सम्पूर्ण शास्त्रीय विवरण")
        pillars_table = [
            {"अंग": "१. तिथि", "मान": f"{t['name']} ({t['paksha']})", "समाप्ति काल": t['end_time_str'], "संज्ञा / स्वामी": f"{t['category']} / {t['deity']}", "शुभता": "मांगलिक" if "रिक्ता" not in t['category'] else "रिक्ता (सावधानी)"},
            {"अंग": "२. नक्षत्र", "मान": f"{nak['name']} (चरण {nak['pada']})", "समाप्ति काल": nak['end_time_str'], "संज्ञा / स्वामी": f"{nak['lord']} / {nak['deity']}", "शुभता": "गण्डमूल" if pg['gandamoola']['is_active'] else "शुभ"},
            {"अंग": "३. योग", "मान": f"{yg['name']} ({yg['name_en']})", "समाप्ति काल": yg['end_time_str'], "संज्ञा / स्वामी": f"{yg['nature']} / {yg['deity']}", "शुभता": "शुभ" if yg['is_good'] else "अशुभ"},
            {"अंग": "४. करण", "मान": f"{kc['name']} ({kc['type']})", "समाप्ति काल": kc['end_time_str'], "संज्ञा / स्वामी": kc['deity'], "शुभता": "भद्रा" if "विष्टि" in kc['name'] else "सामान्य"},
            {"अंग": "५. वार", "मान": vr['name_hi'], "समाप्ति काल": "अहोरात्र (सूर्योदय पर्यन्त)", "संज्ञा / स्वामी": vr['lord'], "शुभता": "अनुकूल"}
        ]
        st.table(pillars_table)

    # =============================================================
    # TAB 2: पर्व, व्रत एवं एकादशी पारणा (Festivals & Vrat Engine)
    # =============================================================
    with tab2:
        st.markdown("### 🚩 व्रत, पर्व एवं एकादशी पारणा शोध")
        st.caption("दृक्-पञ्चाङ्ग प्रमाणित प्रमुख सनातन व्रत, त्यौहार, महा-पर्व एवं एकादशी पारणा का सूक्ष्म समय:")

        vr_list = festivals_vrat.get("vrats", [])
        ek_parana = festivals_vrat.get("ekadashi_parana")

        if vr_list:
            st.markdown("#### 🌟 आज सक्रिय व्रत एवं त्यौहार (Active Vrats & Festivals)")
            for v_item in vr_list:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#FFFBEB'}; border:1.5px solid #F59E0B;
                            border-radius:12px; padding:16px 20px; margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#B45309; font-size:18px;">🚩 {v_item['name']}</b>
                        <span style="background:#FDE68A; color:#78350F; padding:4px 12px; border-radius:14px; font-weight:700; font-size:12px;">
                            {v_item['badge']}
                        </span>
                    </div>
                    <div style="color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13.5px; margin-top:6px; line-height:1.6;">
                        • <b>व्रत स्वरूप:</b> {v_item['type']}<br/>
                        • <b>आध्यात्मिक महत्व:</b> {v_item['significance']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("आज कोई प्रमुख विशिष्ट महा-व्रत अथवा पर्व नहीं है। नित्य सात्विक कर्म व ईष्ट आराधना शुभ फलदायी है।")

        # Ekadashi Parana Card (If Active)
        if ek_parana and ek_parana.get("is_applicable"):
            st.markdown("#### 🍲 एकादशी व्रत पारणा मुहूर्त (Ekadashi Parana Timings)")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:2px solid #16A34A;
                        border-radius:12px; padding:18px 20px; margin:14px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#166534; font-size:18px;">✨ {ek_parana['ekadashi_name']}</b>
                    <span style="background:#DCFCE7; color:#14532D; padding:4px 12px; border-radius:14px; font-weight:700; font-size:12.5px;">
                        पारणा काल शुभ
                    </span>
                </div>
                <div style="font-size:20px; font-weight:800; color:#15803D; margin:10px 0 6px 0;">
                    ⏱️ पारणा समय: {ek_parana['parana_window_str']}
                </div>
                <div style="font-size:13.5px; color:{'#D1D5DB' if is_dark else '#334155'}; line-height:1.6;">
                    <b>शास्त्रीय पारणा विधि:</b> {ek_parana['rule']}<br/>
                    • <i>हरिवासर विचार:</i> धर्मसिन्धु अनुसार द्वादशी के प्रथम चतुर्थांश (हरिवासर) में पारणा निषिद्ध है। उक्त समय पूर्णतः हरिवासर समाप्त्योपरान्त प्रशस्त है।
                </div>
            </div>
            """, unsafe_allow_html=True)

        # City-Specific Puja Muhurta Card (If Active for Diwali, Karwa Chauth, Shivratri, etc.)
        puja_muh = festivals_vrat.get("puja_muhurta")
        if puja_muh:
            st.markdown(f"#### 🪔 {puja_muh['festival']} — सूक्ष्म पूजन मुहूर्त")
            prad_txt = f"<br/>• <b>प्रदोष काल:</b> {puja_muh['pradosh_kaal']}" if puja_muh.get('pradosh_kaal') else ""
            nish_txt = f"<br/>• <b>निशीथ काल:</b> {puja_muh['nishita_kaal']}" if puja_muh.get('nishita_kaal') else ""
            moon_txt = f"<br/>• <b>{puja_muh['moonrise_time']}</b>" if puja_muh.get('moonrise_time') else ""
            lagna_txt = f"<br/>• <b>शुभ लग्न:</b> {puja_muh['lagna_auspicious']}" if puja_muh.get('lagna_auspicious') else ""
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFF7ED'}; border:2px solid #F97316;
                        border-radius:12px; padding:20px; margin:14px 0; box-shadow:0 4px 14px rgba(249,115,22,0.15);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#C2410C; font-size:19px;">{puja_muh['badge']}</b>
                    <span style="background:#FFEDD5; color:#9A3412; padding:5px 14px; border-radius:16px; font-weight:800; font-size:13px;">
                        अवधि: {puja_muh.get('duration', 'प्रशस्त')}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:#EA580C; margin:12px 0 8px 0;">
                    ⏱️ श्रेष्ठ पूजा समय: {puja_muh['muhurta_window']}
                </div>
                <div style="font-size:14px; color:{'#E5E7EB' if is_dark else '#334155'}; line-height:1.7;">
                    {prad_txt}{nish_txt}{moon_txt}{lagna_txt}<br/>
                    • <b>शास्त्रीय विधान व पूजा विधि:</b> {puja_muh['vidhi']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🗓️ आगामी प्रमुख व्रत एवं पर्व तालिका")
        fest_sched = [
            {"पर्व / व्रत": "इन्दिरा एकादशी", "मास व पक्ष": "आश्विन कृष्ण पक्ष", "महत्व": "पितरों के उद्धार व मोक्ष हेतु परम पावन"},
            {"पर्व / व्रत": "सर्वपितृ अमावस्या", "मास व पक्ष": "आश्विन कृष्ण अमावस्या", "महत्व": "समस्त ज्ञात-अज्ञात पितरों का महा-विसर्जन"},
            {"पर्व / व्रत": "शारदीय नवरात्रि (घटस्थापना)", "मास व पक्ष": "आश्विन शुक्ल प्रतिपदा", "महत्व": "माँ भगवती दुर्गा के ९ स्वरूपों की उपासना"},
            {"पर्व / व्रत": "विजयादशमी (दशहरा)", "मास व पक्ष": "आश्विन शुक्ल दशमी", "महत्व": "अधर्म पर धर्म की विजय, अपराजिता पूजन"},
            {"पर्व / व्रत": "करवा चौथ", "मास व पक्ष": "कार्तिक कृष्ण चतुर्थी", "महत्व": "अखण्ड सौभाग्य व पति दीर्घायु हेतु निर्जला व्रत"},
            {"पर्व / व्रत": "धनतेरस व दीपावली", "मास व पक्ष": "कार्तिक कृष्ण त्रयोदशी-अमावस्या", "महत्व": "धन्वन्तरि जयंती व महालक्ष्मी पूजनोत्सव"},
            {"पर्व / व्रत": "देवउठनी एकादशी", "मास व पक्ष": "कार्तिक शुक्ल एकादशी", "महत्व": "भगवान विष्णु का देवोत्थान व मांगलिक कार्य आरम्भ"}
        ]
        st.table(fest_sched)

    # =============================================================
    # TAB 3: पक्ष, पितृपक्ष (श्राद्ध) एवं महा-काल शोध
    # =============================================================
    with tab3:
        st.markdown("### 🪔 पक्ष, पितृपक्ष (श्राद्ध) एवं महा-काल शोध")
        st.caption("शुक्ल/कृष्ण पक्ष के चन्द्र-बल गुणधर्म, पितृपक्ष (महालय) निषेध व विधान, चातुर्मास एवं खरमास का प्रामाणिक शास्त्रीय फलादेश:")

        # 1. PAKSHA & MOON STRENGTH
        st.markdown("#### 🌓 १. पक्ष एवं चन्द्रमा का प्राकृतिक बल (Chandra Bala in Paksha)")
        cur_paksha = paksha_eng.get('paksha_name') or pillars['tithi']['paksha']
        cb_val = paksha_eng.get('chandra_bala') or ("सर्वोच्च / पूर्ण चन्द्र बल" if "शुक्ल" in cur_paksha else "क्षीण चन्द्र बल (संयम काल)")
        cb_col = paksha_eng.get('chandra_bala_color') or ("#059669" if "शुक्ल" in cur_paksha else "#D97706")
        cb_desc = paksha_eng.get('chandra_bala_desc') or (
            "शुक्ल प्रतिपदा से पूर्णिमा तक चन्द्रमा वृद्धिशील व शुभ बली होता है। इस काल में किए गए नूतन आरम्भ व मांगलिक कार्य समृद्धिकारक सिद्ध होते हैं।"
            if "शुक्ल" in cur_paksha else
            "कृष्ण षष्ठी से अमावस्या पर्यन्त चन्द्रमा क्षीण व हीन बली माना जाता है। यह काल आत्म-चिन्तन, साधना, पितृ-तर्पण एवं संयम हेतु श्रेष्ठ है।"
        )
        col_pk1, col_pk2 = st.columns([1.5, 2.5])
        with col_pk1:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#EFF6FF'}; border:1.5px solid #3B82F6;
                        border-radius:12px; padding:18px; text-align:center;">
                <span style="font-size:13px; color:#1E40AF; font-weight:600;">वर्तमान सक्रिय पक्ष</span>
                <div style="font-size:26px; font-weight:800; color:#1D4ED8; margin:6px 0;">
                    {cur_paksha}
                </div>
                <span style="background:{cb_col}20; color:{cb_col};
                             padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;">
                    {cb_val}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col_pk2:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                        border-left:4px solid #3B82F6; border-radius:10px; padding:16px;">
                <b style="color:#1E3A8A; font-size:15px;">📖 शास्त्रीय पक्ष-बल नियम:</b>
                <div style="margin-top:6px; color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13.5px; line-height:1.6;">
                    {cb_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 2. PITRU PAKSHA DEEP ENGINE
        st.markdown("#### 🪔 २. पितृपक्ष (महालय श्राद्ध काल) गहन शास्त्रीय अनुसंधान")
        if pitru.get("is_active"):
            st.markdown(f"""
            <div style="background:#FFF5F5; border:2px solid #DC2626; border-radius:12px; padding:20px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <b style="color:#991B1B; font-size:18px;">🚫 {pitru['shradh_name']} सक्रिय</b>
                    <span style="background:#DC2626; color:#FFFFFF; padding:4px 12px; border-radius:14px; font-weight:700; font-size:12px;">
                        {pitru['badge']}
                    </span>
                </div>
                <div style="color:#7F1D1D; font-size:13.5px; margin:8px 0; line-height:1.6;">
                    <b>शास्त्रीय प्रमाण:</b> <i>"{pitru['sutra']}"</i><br/>
                    {pitru['verdict_desc']}
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; margin-top:10px;">
                    <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                        <b style="color:#991B1B;">☀️ कुतुप मुहूर्त (श्राद्ध का मुख्य काल):</b><br/>
                        <span style="font-size:15px; font-weight:700; color:#0F172A;">{pitru['kutupa_time']}</span>
                    </div>
                    <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                        <b style="color:#991B1B;">☀️ रौहिण मुहूर्त:</b><br/>
                        <span style="font-size:15px; font-weight:700; color:#0F172A;">{pitru['rohina_time']}</span>
                    </div>
                    <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                        <b style="color:#991B1B;">🌊 अपराह्न काल (तर्पण/पिण्डदान):</b><br/>
                        <span style="font-size:15px; font-weight:700; color:#0F172A;">{pitru['aparahna_time']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_pt1, col_pt2 = st.columns(2)

            with col_pt1:
                st.markdown("""
                <div style="background:#FEF2F2; border:1.5px solid #DC2626; border-radius:10px; padding:16px; height:100%;">
                    <b style="color:#991B1B; font-size:16px;">🚫 क्या-क्या सर्वथा वर्जित है (Strict Prohibitions):</b>
                    <div style="color:#7F1D1D; font-size:12.5px; margin:4px 0 10px 0;">शास्त्रों अनुसार इस अवधि में भौतिक मांगलिक उत्सव अनिष्टकारी होते हैं:</div>
                    <ul style="color:#991B1B; font-size:13px; line-height:1.7; padding-left:18px; margin:0;">
                        <li><b>नूतन गृह प्रवेश व भूमि पूजन:</b> नया घर खरीदना, गृह प्रवेश या नींव पूजन पूर्णतः निषिद्ध।</li>
                        <li><b>विवाह, सगाई व रोका:</b> पाणिग्रहण संस्कार व वैवाहिक उत्सव महा-वर्जित।</li>
                        <li><b>मुंडन व उपनयन संस्कार:</b> कोई भी मांगलिक संस्कार सम्पन्न नहीं किया जाता।</li>
                        <li><b>नया व्यापार/प्रतिष्ठान उद्घाटन:</b> नए व्यवसाय या दुकान का आरम्भ न करें।</li>
                        <li><b>नवीन वाहन एवं स्वर्ण क्रय:</b> विलासिता सामग्री व नवीन आभूषणों का प्रथम उपयोग वर्जित।</li>
                        <li><b>तामसिक भोजन व व्यसन:</b> प्याज, लहसुन, मांस, मदिरा महा-पाप माना गया है।</li>
                        <li><b>बाल, दाढ़ी व नाखून काटना:</b> श्राद्ध कर्ता हेतु क्षौर कर्म निषिद्ध है।</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col_pt2:
                st.markdown("""
                <div style="background:#F0FDF4; border:1.5px solid #16A34A; border-radius:10px; padding:16px; height:100%;">
                    <b style="color:#166534; font-size:16px;">🟢 क्या-क्या करने का विधान है (Prescribed Rituals):</b>
                    <div style="color:#15803D; font-size:12.5px; margin:4px 0 10px 0;">इस पावन काल में पितृ सेवा से वंश वृद्धि, आरोग्य व शांति प्राप्त होती है:</div>
                    <ul style="color:#14532D; font-size:13px; line-height:1.7; padding-left:18px; margin:0;">
                        <li><b>पितृ तर्पण:</b> काले तिल, जौ, कुशा व गंगाजल से पितरों को जलांजलि अर्पण।</li>
                        <li><b>पिण्डदान एवं श्राद्ध कर्म:</b> कुतुप व रौहिण मुहूर्त में विधिपूर्वक श्राद्ध कर्म।</li>
                        <li><b>पंचबलि कर्म:</b> गौ (गाय), श्वान (कुत्ता), काक (कौआ), देवादि एवं चींटियों को ग्रास देना।</li>
                        <li><b>ब्राह्मण भोजन व दक्षिणा:</b> सात्विक खीर-पूरी से योग्य ब्राह्मणों को तृप्त करना।</li>
                        <li><b>श्रीमद्भगवद्गीता पाठ:</b> विशेषकर अध्याय ७, ११ एवं गरुड़ पुराण का श्रवण।</li>
                        <li><b>अन्न व वस्त्र दान:</b> जरूरतमंदों को अन्न, छाता, पादुका (जूते) एवं दीपदान।</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            pitru_badge = pitru.get('badge') or '🟢 पितृपक्ष निष्क्रिय (Normal Period)'
            pitru_desc = pitru.get('desc') or 'वर्तमान में पितृपक्ष सक्रिय नहीं है। सामान्य मांगलिक कार्यों पर पितृपक्ष का कोई प्रतिबंध नहीं है।'
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:1px solid #BBF7D0;
                        border-radius:10px; padding:16px;">
                <b style="color:#166534; font-size:15px;">{pitru_badge}</b>
                <div style="margin-top:6px; color:#15803D; font-size:13.5px; line-height:1.5;">{pitru_desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 3. CHATURMAS & KHARMAS
        st.markdown("#### 🕉️ ३. चातुर्मास (देवशयन) एवं खरमास (मलमास) स्थिति")
        col_ct1, col_ct2 = st.columns(2)

        with col_ct1:
            is_ch = paksha_eng.get("is_chaturmas", False)
            ch_bg = "#FFF7ED" if is_ch else "#F8FAFC"
            ch_bdr = "#F97316" if is_ch else "#E2E8F0"
            ch_col = "#C2410C" if is_ch else "#475569"
            ch_desc = paksha_eng.get('chaturmas_desc') or (
                "आषाढ़ शुक्ल एकादशी से कार्तिक शुक्ल एकादशी तक श्रीहरि विष्णु क्षीरसागर में योगनिद्रा में रहते हैं। अपूर्व गृह प्रवेश व विवाह संस्कार निषिद्ध माने गए हैं।"
                if is_ch else "वर्तमान में चातुर्मास सक्रिय नहीं है।"
            )
            st.markdown(f"""
            <div style="background:{ch_bg if not is_dark else '#1F2937'}; border:1.5px solid {ch_bdr};
                        border-radius:10px; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{ch_col}; font-size:15px;">चातुर्मास (देवशयन काल)</b>
                    <span style="background:{ch_col}20; color:{ch_col}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                        {'⚠️ सक्रिय' if is_ch else '🟢 निष्क्रिय'}
                    </span>
                </div>
                <div style="margin-top:6px; color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13px; line-height:1.5;">
                    {ch_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_ct2:
            is_kh = paksha_eng.get("is_kharmas", False)
            kh_bg = "#FEF2F2" if is_kh else "#F8FAFC"
            kh_bdr = "#DC2626" if is_kh else "#E2E8F0"
            kh_col = "#991B1B" if is_kh else "#475569"
            kh_desc = paksha_eng.get('kharmas_desc') or (
                "सूर्य जब देवगुरु बृहस्पति की राशि (धनु या मीन) में होते हैं, तब समस्त मांगलिक संस्कार वर्जित रहते हैं।"
                if is_kh else "वर्तमान में खरमास सक्रिय नहीं है।"
            )
            st.markdown(f"""
            <div style="background:{kh_bg if not is_dark else '#1F2937'}; border:1.5px solid {kh_bdr};
                        border-radius:10px; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{kh_col}; font-size:15px;">खरमास / मलमास (धनु-मीन सूर्य)</b>
                    <span style="background:{kh_col}20; color:{kh_col}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                        {'🚫 सक्रिय' if is_kh else '🟢 निष्क्रिय'}
                    </span>
                </div>
                <div style="margin-top:6px; color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13px; line-height:1.5;">
                    {kh_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================
    # TAB 4: दैनिक लग्न सारणी (24-Hour Lagna Timings)
    # =============================================================
    with tab4:
        st.markdown("### 🏛️ दैनिक २४-घंटे की लग्न सारणी (24-Hour Rising Lagna Table)")
        st.caption("सूर्योदय से अगले सूर्योदय तक मेष से मीन पर्यन्त द्वादश लग्नों का उदय-अस्त समय, स्वभाव एवं मुहूर्त उपयोगिता:")

        if lagna_table:
            # Filter options
            lag_filter = st.radio("लग्न प्रकार फ़िल्टर:", ["समस्त १२ लग्न (All)", "स्थिर लग्न (गृह प्रवेश / व्यापार)", "द्विस्वभाव लग्न (विद्या / शिल्प)", "चर लग्न (यात्रा / परिवर्तन)"], horizontal=True)

            filtered_lagnas = lagna_table
            if "स्थिर" in lag_filter:
                filtered_lagnas = [x for x in lagna_table if "स्थिर" in x["type"]]
            elif "द्विस्वभाव" in lag_filter:
                filtered_lagnas = [x for x in lagna_table if "द्विस्वभाव" in x["type"]]
            elif "चर" in lag_filter:
                filtered_lagnas = [x for x in lagna_table if "चर" in x["type"]]

            cols_l = st.columns(2)
            for idx, lg in enumerate(filtered_lagnas):
                with cols_l[idx % 2]:
                    type_color = "#059669" if "स्थिर" in lg["type"] else ("#2563EB" if "द्विस्वभाव" in lg["type"] else "#D97706")
                    is_active_box = lg.get("is_current", False)
                    box_border = "#DC2626" if is_active_box else ('#374151' if is_dark else '#E2E8F0')

                    active_badge = '<span style="background:#DC2626; color:#FFF; padding:3px 8px; border-radius:10px; font-size:10.5px; font-weight:700;">🔴 सक्रिय काल</span>' if is_active_box else ''
                    active_shadow = 'box-shadow:0 0 10px rgba(220,38,38,0.25);' if is_active_box else ''
                    bg_color = '#1F2937' if is_dark else '#FFFFFF'
                    text_title_color = '#FFFFFF' if is_dark else '#0F172A'
                    text_body_color = '#D1D5DB' if is_dark else '#475569'

                    card_html = (
                        f'<div style="background:{bg_color}; border:1.5px solid {box_border}; '
                        f'border-left:5px solid {type_color}; border-radius:10px; padding:14px; margin-bottom:12px; {active_shadow}">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                        f'<div>'
                        f'<b style="font-size:18px; color:{text_title_color};">{lg["name"]} लग्न ({lg["name_en"]})</b>'
                        f'<span style="background:{type_color}20; color:{type_color}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700; margin-left:6px;">{lg["type"]}</span>'
                        f'</div>'
                        f'<div>{active_badge}</div>'
                        f'</div>'
                        f'<div style="font-size:15px; font-weight:800; color:#1D4ED8; margin:6px 0;">'
                        f'⏱️ {lg["start_str"]} से {lg["end_str"]} <span style="font-size:12px; color:#64748B; font-weight:400;">({lg["duration_str"]} | {lg["duration_ghatis"]})</span>'
                        f'</div>'
                        f'<div style="font-size:12.5px; color:{text_body_color}; line-height:1.6;">'
                        f'• <b>लग्न स्वामी:</b> {lg["lord"]} | <b>तत्व:</b> {lg["element"]}<br/>'
                        f'• <b>मुहूर्त शुद्धि:</b> {lg["suitability"]}'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("लग्न सारणी की गणना प्रगति पर है...")

    # =============================================================
    # TAB 5: शुभ एवं अशुभ मुहूर्त (Timings)
    # =============================================================
    with tab5:
        st.markdown("### ⏰ शुभ एवं अशुभ काल / मुहूर्त (Auspicious & Inauspicious Timings)")
        st.caption("सूर्योदय व सूर्यास्त के शुद्ध दिनमान विभाजन पर आधारित यथार्थ वेला एवं त्याज्य काल चक्र:")

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown("#### 🟢 शुभ काल व मुहूर्त (Auspicious Windows)")
            for win in muh["shubh_windows"]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:1px solid {'#374151' if is_dark else '#BBF7D0'};
                            border-left:4px solid {win['color']}; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:{win['color']}; font-size:14.5px;">{win['title']}</b>
                        <span style="background:{win['color']}20; color:{win['color']}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                            {win['badge']}
                        </span>
                    </div>
                    <div style="font-size:16px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:4px 0;">
                        ⏱️ {win['time']}
                    </div>
                    <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{win['status']}</small>
                </div>
                """, unsafe_allow_html=True)

        with col_m2:
            st.markdown("#### 🔴 अशुभ एवं त्याज्य काल (Inauspicious Windows)")
            for win in muh["ashubh_windows"]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#FEF2F2'}; border:1px solid {'#374151' if is_dark else '#FECACA'};
                            border-left:4px solid {win['color']}; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:{win['color']}; font-size:14.5px;">{win['title']}</b>
                        <span style="background:{win['color']}20; color:{win['color']}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                            {win['badge']}
                        </span>
                    </div>
                    <div style="font-size:16px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:4px 0;">
                        ⚠️ {win['time']}
                    </div>
                    <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{win['status']}</small>
                </div>
                """, unsafe_allow_html=True)

    # =============================================================
    # TAB 6: चौघड़िया, होरा एवं वैदिक घड़ी
    # =============================================================
    with tab6:
        st.markdown("### ☀️ चौघड़िया, होरा एवं वैदिक घड़ी (Choghadiya, Horas & Vedic Time)")
        st.caption("दिन के ८ एवं रात्रि के ८ चौघड़िया, २४ ग्रह होराएं एवं ६० घटी वैदिक काल मापन:")

        c_tab1, c_tab2, c_tab3, c_tab4, c_tab5 = st.tabs([
            "☀️ दिन का चौघड़िया", "🌙 रात्रि का चौघड़िया",
            "🦚 दिन का गौरी पञ्चाङ्गम", "🌙 रात्रि का गौरी पञ्चाङ्गम",
            "🪐 २४ ग्रह होरा चक्र"
        ])

        with c_tab1:
            st.markdown("#### ☀️ दिन का चौघड़िया (Day Choghadiya: सूर्योदय से सूर्यास्त)")
            col_d1, col_d2 = st.columns(2)
            half = len(chog["day_choghadiyas"]) // 2
            with col_d1:
                for item in chog["day_choghadiyas"][:half]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with col_d2:
                for item in chog["day_choghadiyas"][half:]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        with c_tab2:
            st.markdown("#### 🌙 रात्रि का चौघड़िया (Night Choghadiya: सूर्यास्त से आगामी सूर्योदय)")
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                for item in chog["night_choghadiyas"][:half]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with col_n2:
                for item in chog["night_choghadiyas"][half:]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        with c_tab3:
            st.markdown("#### 🦚 दिन का गौरी पञ्चाङ्गम (Day Gowri Panchangam)")
            st.caption("पारम्परिक दक्षिण भारतीय ८ गौरी मुहूर्त (उत्ति, अमृत, रोग, लाभ, धन, विष, सुख, चोर):")
            col_gd1, col_gd2 = st.columns(2)
            d_gowri_list = gowri.get("day_gowri", [])
            g_half = len(d_gowri_list) // 2
            with col_gd1:
                for item in d_gowri_list[:g_half]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']}</b>
                            <span style="font-size:11.5px; color:{item['color']}; font-weight:700;">{item['nature']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with col_gd2:
                for item in d_gowri_list[g_half:]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']}</b>
                            <span style="font-size:11.5px; color:{item['color']}; font-weight:700;">{item['nature']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        with c_tab4:
            st.markdown("#### 🌙 रात्रि का गौरी पञ्चाङ्गम (Night Gowri Panchangam)")
            col_gn1, col_gn2 = st.columns(2)
            n_gowri_list = gowri.get("night_gowri", [])
            with col_gn1:
                for item in n_gowri_list[:g_half]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']}</b>
                            <span style="font-size:11.5px; color:{item['color']}; font-weight:700;">{item['nature']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with col_gn2:
                for item in n_gowri_list[g_half:]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']}</b>
                            <span style="font-size:11.5px; color:{item['color']}; font-weight:700;">{item['nature']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        with c_tab5:
            st.markdown("#### 🪐 २४ ग्रह होरा चक्र (24 Planetary Horas)")
            hora_cols = st.columns(2)
            with hora_cols[0]:
                st.markdown("##### ☀️ दिन की १२ होराएं")
                for h in chog["horas_24"][:12]:
                    st.markdown(f"""
                    <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                                border-left:3px solid #3B82F6; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <b>#{h['hora_num']} होरा: {h['planet']}</b> — <span style="color:#2563EB;">{h['start']} से {h['end']}</span><br/>
                        <small style="color:#64748B;">{h['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with hora_cols[1]:
                st.markdown("##### 🌙 रात्रि की १२ होराएं")
                for h in chog["horas_24"][12:]:
                    st.markdown(f"""
                    <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                                border-left:3px solid #8B5CF6; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <b>#{h['hora_num']} होरा: {h['planet']}</b> — <span style="color:#7C3AED;">{h['start']} से {h['end']}</span><br/>
                        <small style="color:#64748B;">{h['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

    # =============================================================
    # TAB 7: भद्रा, पञ्चक एवं गण्डमूल शोध
    # =============================================================
    with tab7:
        st.markdown("### 🛡️ भद्रा, पञ्चक एवं गण्डमूल शोध (Bhadra, Panchaka & Gandamoola Engine)")
        st.caption("मुहूर्त चिन्तामणि के अनुसार भद्रा वास, मुख-पुच्छ काल, पञ्चक के ५ प्रकार एवं गण्डमूल चरण फल:")

        # 1. BHADRA ENGINE
        st.markdown("#### 🚫 १. भद्रा विचार (Vishti Karana Deep Analysis)")
        if bhadra["is_present"]:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FEF2F2'}; border:1.5px solid {bhadra['color']};
                        border-radius:12px; padding:18px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{bhadra['color']}; font-size:18px;">⚠️ भद्रा सक्रिय — {bhadra['loka']}</b>
                    <span style="background:{bhadra['color']}20; color:{bhadra['color']}; padding:4px 12px; border-radius:14px; font-weight:700;">
                        {bhadra['badge']}
                    </span>
                </div>
                <div style="font-size:16px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0;">
                    ⏱️ भद्रा काल: {bhadra['full_time_str']} (कुल अवधि: {bhadra['duration_str']})
                </div>
                <div style="color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13.5px; margin:6px 0;">
                    <b>शास्त्रीय निर्णय:</b> {bhadra['verdict']}<br/>
                    <i>"{bhadra['sutra']}"</i>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:10px;">
                    <div style="background:rgba(220, 38, 38, 0.1); border:1px solid #DC2626; border-radius:8px; padding:10px;">
                        <b style="color:#DC2626;">💀 भद्रा मुख (सर्वथा वर्जित):</b><br/>
                        {bhadra['mukha_time']}
                    </div>
                    <div style="background:rgba(5, 150, 105, 0.1); border:1px solid #059669; border-radius:8px; padding:10px;">
                        <b style="color:#059669;">✨ भद्रा पुच्छ (कार्य सिद्धिप्रद):</b><br/>
                        {bhadra['puchha_time']}
                    </div>
                </div>
                <div style="margin-top:10px; font-size:12.5px; color:#DC2626;">
                    <b>वर्जित कर्म:</b> {', '.join(bhadra['prohibitions'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:1px solid #BBF7D0;
                        border-radius:12px; padding:16px; margin-bottom:16px;">
                <b style="color:#166534; font-size:16px;">{bhadra['badge']}</b>
                <div style="color:#15803D; margin-top:4px; font-size:13.5px;">{bhadra['status_hi']}</div>
            </div>
            """, unsafe_allow_html=True)

        col_pg1, col_pg2 = st.columns(2)

        # 2. PANCHAKA ENGINE
        p_info = pg["panchaka"]
        with col_pg1:
            st.markdown("#### ⚡ २. पञ्चक विचार (5 Panchaka Types)")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {p_info['color']};
                        border-radius:12px; padding:16px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{p_info['color']}; font-size:16px;">{p_info['name']}</b>
                    <span style="background:{p_info['color']}20; color:{p_info['color']}; padding:2px 8px; border-radius:12px; font-weight:700; font-size:11px;">
                        {p_info['badge']}
                    </span>
                </div>
                <div style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin:8px 0;">{p_info['desc']}</div>
                {'<div style="font-size:12px; color:#DC2626;"><b>विशेष निषेध:</b><br/>• ' + '<br/>• '.join(p_info.get('prohibitions', [])) + '</div>' if p_info['is_active'] else ''}
            </div>
            """, unsafe_allow_html=True)

        # 3. GANDAMOOLA ENGINE
        g_info = pg["gandamoola"]
        with col_pg2:
            st.markdown("#### 🌿 ३. गण्डमूल विचार (Gandamoola 6 Nakshatras)")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {g_info['color']};
                        border-radius:12px; padding:16px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{g_info['color']}; font-size:16px;">{g_info.get('nakshatra', 'गण्डमूल')} {f'(चरण {g_info.get("pada")})' if g_info['is_active'] else ''}</b>
                    <span style="background:{g_info['color']}20; color:{g_info['color']}; padding:2px 8px; border-radius:12px; font-weight:700; font-size:11px;">
                        {g_info['badge']}
                    </span>
                </div>
                <div style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin:8px 0;">{g_info['desc']}</div>
                {f'<div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:6px; padding:8px; font-size:12px; color:#92400E;"><b>शान्ति विधान:</b> {g_info.get("shanti_vidhi")}</div>' if g_info['is_active'] else ''}
            </div>
            """, unsafe_allow_html=True)

    # =============================================================
    # TAB 8: चन्द्रबलम, ताराबलम एवं आनन्दादि शुभ योग
    # =============================================================
    with tab8:
        st.markdown("### ⚖️ चन्द्रबलम, ताराबलम एवं आनन्दादि शुभ योग")
        st.caption("१२ राशियों का चन्द्रबल, २७ नक्षत्रों का ताराबल एवं २८ आनन्दादि महायोग:")

        # Special Yogas Banner
        sp_yogas = yogas["special_yogas"]
        if sp_yogas:
            st.markdown("#### 🌟 आज सक्रिय विशेष महायोग (Active Super Yogas)")
            for sy in sp_yogas:
                st.markdown(f"""
                <div style="background:#F0FDF4; border:1.5px solid #10B981; border-radius:10px; padding:12px 16px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#047857; font-size:15px;">{sy['title']}</b>
                        <span style="background:#D1FAE5; color:#065F46; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">{sy['badge']}</span>
                    </div>
                    <div style="color:#065F46; font-size:13px; margin-top:4px;">{sy['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

        # Anandadi 28 Yoga
        ay = yogas["anandadi_yoga"]
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                    border-left:4px solid {ay['color']}; border-radius:8px; padding:12px; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="color:{ay['color']}; font-size:15px;">✨ आनन्दादि २८ योग: {ay['name']} योग ({ay['nature']})</b>
                <span style="background:{ay['color']}20; color:{ay['color']}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">{ay['badge']}</span>
            </div>
            <div style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin-top:4px;">{ay['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

        col_b1, col_b2 = st.columns(2)

        # Chandrabalam
        with col_b1:
            st.markdown("#### 🌙 द्वादश राशि चन्द्रबलम् (Chandrabalam)")
            st.caption("आज चन्द्रमा किस-किस राशि के जातकों हेतु बली है:")
            c_grid = st.columns(3)
            for i, c_item in enumerate(balam["chandrabalam"]):
                with c_grid[i % 3]:
                    st.markdown(f"""
                    <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {c_item['color']};
                                border-radius:6px; padding:8px; margin-bottom:6px; text-align:center;">
                        <b style="font-size:12.5px; color:{'#FFFFFF' if is_dark else '#0F172A'};">{c_item['rashi']}</b><br/>
                        <span style="font-size:11px; color:{c_item['color']}; font-weight:700;">{c_item['score']}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # Tarabalam
        with col_b2:
            st.markdown("#### ⭐ नवतारा चक्र (Tarabalam for 27 Nakshatras)")
            st.caption("९ तारा प्रकार (जन्म, संपत, विपत, क्षेम, प्रत्यरि, साधक, वध, मित्र, अतिमित्र):")
            t_grid = st.columns(3)
            for j, t_item in enumerate(balam["tarabalam"][:12]):
                with t_grid[j % 3]:
                    st.markdown(f"""
                    <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {t_item['color']};
                                border-radius:6px; padding:8px; margin-bottom:6px; text-align:center;">
                        <b style="font-size:12px; color:{'#FFFFFF' if is_dark else '#0F172A'};">#{t_item.get('nak_idx', j + 1)} {t_item.get('nakshatra', '')}</b><br/>
                        <span style="font-size:10.5px; color:{t_item.get('color', '#3B82F6')}; font-weight:700;">{t_item.get('tara_name', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # 5 Baana Dosha Analysis Card
        if baana:
            st.markdown("---")
            b_col = baana.get("color", "#DC2626")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFBEB'}; border:1.5px solid {b_col};
                        border-left:5px solid {b_col}; border-radius:10px; padding:14px 18px; margin-top:14px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{b_col}; font-size:16px;">🏹 पञ्च बाण विचार: {baana['baana_name']}</b>
                    <span style="background:{b_col}20; color:{b_col}; padding:3px 10px; border-radius:12px; font-weight:700; font-size:12px;">
                        {'🚫 सर्वथा वर्जित' if baana['is_fatal'] else '⚠️ सावधानी आवश्यक'}
                    </span>
                </div>
                <div style="font-size:13.5px; color:{'#E5E7EB' if is_dark else '#334155'}; margin-top:6px; line-height:1.6;">
                    • <b>बाण प्रभाव:</b> {baana['nature']}<br/>
                    • <b>शास्त्रीय निषेध:</b> {baana['remedy']}<br/>
                    • <i>शास्त्र प्रमाण:</i> {baana['shastra_quote']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================
    # TAB 9: दैनिक ग्रह स्पष्ट एवं मंत्रिमंडल
    # =============================================================
    with tab9:
        st.markdown("### 🪐 दैनिक ग्रह स्पष्ट एवं आकाशीय मंत्रिमंडल")
        st.caption("सूर्योदय कालीन नवग्रह स्पष्ट भोग, नक्षत्र, पाद, गति, वक्री/अस्त स्थिति एवं संवत्सर मंत्रिमंडल:")

        col_g1, col_g2 = st.columns([2, 1.2])

        with col_g1:
            st.markdown("#### 🌟 नवग्रह स्पष्ट स्थिति (Planetary Transit Matrix)")
            st.table(transit)

        with col_g2:
            st.markdown("#### 👑 वर्ष का आकाशीय मंत्रिमंडल (Cabinet)")
            for post in samvat["cabinet"]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                            border-left:3px solid #6366F1; border-radius:6px; padding:10px 12px; margin-bottom:8px;">
                    <b style="color:#4338CA; font-size:13.5px;">{post['post']}</b>: <b>{post['graha']}</b><br/>
                    <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{post['effect']}</small>
                </div>
                """, unsafe_allow_html=True)

    # =============================================================
    # TAB 10: दैनिक वैदिक सङ्कल्प मन्त्र (Vedic Sankalpa Generator)
    # =============================================================
    with tab10:
        st.markdown("### 📜 दैनिक वैदिक सङ्कल्प मन्त्र जनरेटर (Dynamic Vedic Sankalpa)")
        st.caption("कर्मकाण्ड, नित्य पूजा, श्राद्ध, हवन, अभिषेक व व्यापार हेतु १००% शुद्ध देश-काल-संवत युक्त सङ्कल्प मन्त्र:")

        col_sk1, col_sk2, col_sk3 = st.columns(3)

        with col_sk1:
            default_y_name = getattr(birth_profile, "name", "शुभम") if hasattr(birth_profile, "name") and birth_profile.name else "अमुक"
            yaj_name = st.text_input("यजमान का नाम (Native Name)", value=default_y_name, key="sankalpa_y_name")

        with col_sk2:
            gotra_val = st.text_input("गोत्र (Gotra)", value="कश्यप", key="sankalpa_gotra")

        with col_sk3:
            intent_map = {
                "general": "दैनिक नित्य देव पूजन व जप",
                "pitru": "पितृ तर्पण, पिण्डदान व महालय श्राद्ध",
                "havan": "हवन एवं वैदिक यज्ञ कर्म",
                "shiva": "रुद्राभिषेक एवं शिव पूजन",
                "vyapar": "नूतन व्यापार व प्रतिष्ठान उद्घाटन",
                "satyanarayan": "सत्यनारायण व्रत कथा व पूजन"
            }
            def_intent = "pitru" if pitru.get("is_active") else "general"
            intent_key = st.selectbox(
                "सङ्कल्प का पावन प्रयोजन (Ritual Intent)",
                list(intent_map.keys()),
                index=list(intent_map.keys()).index(def_intent),
                format_func=lambda x: intent_map[x],
                key="sankalpa_intent_choice"
            )

        # Generate dynamically with user inputs
        dyn_sankalpa = VedicPanchangService.generate_vedic_sankalpa_mantra(
            target_date=selected_date,
            city_name=selected_city_name,
            samvatsar_data=samvat,
            five_pillars=pillars,
            paksha_engine=paksha_eng,
            transit_matrix=transit,
            yajamana_name=yaj_name,
            gotra_name=gotra_val,
            intent_type=intent_key
        )

        st.markdown(f"""
        <div style="background:#FFFBEB; border:2px solid #D97706; border-radius:12px; padding:20px; margin:16px 0; box-shadow:0 4px 12px rgba(217, 119, 6, 0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #FDE68A; padding-bottom:10px; margin-bottom:12px;">
                <b style="color:#92400E; font-size:18px;">🕉️ शास्त्रीय सङ्कल्प मन्त्र (संस्कृत पाठ)</b>
                <span style="background:#F59E0B; color:#FFFFFF; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;">
                    {dyn_sankalpa['intent_label']}
                </span>
            </div>
            <div style="color:#78350F; font-size:15.5px; line-height:1.9; font-family:'Georgia', serif; text-align:justify;">
                {dyn_sankalpa['sanskrit_mantra']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.code(dyn_sankalpa['sanskrit_mantra'], language="text")

        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                    border-radius:10px; padding:16px; margin-top:12px;">
            <b style="color:#2563EB; font-size:15px;">📖 सरल हिन्दी भावार्थ:</b>
            <div style="color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13.5px; line-height:1.6; margin-top:6px;">
                {dyn_sankalpa['hindi_meaning']}
            </div>
            <div style="background:#EFF6FF; border-radius:6px; padding:10px 14px; margin-top:12px; font-size:12.5px; color:#1E40AF;">
                <b>🙏 सङ्कल्प की कर्मकाण्डीय विधि:</b> दाहिने हाथ की हथेली में थोड़ा जल, गंध (चंदन), अक्षत (चावल), पुष्प एवं एक सिक्का (द्रव्य) लेकर उत्तराभिमुख होकर बैठें। उपरोक्त मन्त्र का उच्चारण करें अथवा विद्वान ब्राह्मण से वाचन कराएं, और सङ्कल्प पूर्ण होने पर जल को ताम्र पात्र अथवा भूमि पर छोड़ दें।
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =============================================================
    # TAB 11: मासिक पञ्चाङ्ग (Month Calendar & Vedic Monthly Patri)
    # =============================================================
    with tab11:
        st.markdown("### 📅 मासिक पञ्चाङ्ग (Vedic Monthly Calendar & Panchang Patri)")
        st.caption("सम्पूर्ण मास का दृक्-पञ्चाङ्ग प्रमाणित खगोलीय एवं शास्त्रीय विवरण — वर्ष सूची, मास सूची व पञ्चाङ्ग प्रकार के साथ:")

        # 1. Top Controls: Year list, Month list, Type of Calendar
        col_m_yr, col_m_mo, col_m_type = st.columns([1.1, 1.4, 1.9])
        with col_m_yr:
            year_list = list(range(1950, 2051))
            cur_y_idx = year_list.index(selected_date.year) if selected_date.year in year_list else year_list.index(2026)
            sel_cal_year = st.selectbox("📅 वर्ष चयन (Year List):", year_list, index=cur_y_idx, key="panchang_cal_year")

        with col_m_mo:
            months_hi = [
                "१. जनवरी (पौष / माघ)",
                "२. फ़रवरी (माघ / फाल्गुन)",
                "३. मार्च (फाल्गुन / चैत्र)",
                "४. अप्रैल (चैत्र / वैशाख)",
                "५. मई (वैशाख / ज्येष्ठ)",
                "६. जून (ज्येष्ठ / आषाढ़)",
                "७. जुलाई (आषाढ़ / श्रावण)",
                "८. अगस्त (श्रावण / भाद्रपद)",
                "९. सितंबर (भाद्रपद / आश्विन)",
                "१०. अक्टूबर (आश्विन / कार्तिक)",
                "११. नवंबर (कार्तिक / मार्गशीर्ष)",
                "१२. दिसंबर (मार्गशीर्ष / पौष)"
            ]
            sel_cal_month_idx = st.selectbox("🗓️ मास चयन (Month List):", range(1, 13), index=selected_date.month - 1, format_func=lambda x: months_hi[x-1], key="panchang_cal_month")

        with col_m_type:
            cal_type_dict = {
                "purnimanta": "पूर्णिमान्त पञ्चाङ्ग (North India — UP, बिहार, राजस्थान, MP)",
                "amanta": "अमान्त पञ्चाङ्ग (South & West — गुजरात, महाराष्ट्र, दक्षिण भारत)",
                "solar": "सौर संवत्सर (संक्रान्ति मास — बंगाली, तमिल, ओड़िया)",
                "standard": "मानक दृक्-पञ्चाङ्ग (Astronomical Drik System)"
            }
            sel_cal_type = st.selectbox(
                "🕉️ पञ्चाङ्ग प्रणाली (Type of Calendar):",
                list(cal_type_dict.keys()),
                format_func=lambda x: cal_type_dict[x],
                key="panchang_cal_type"
            )

        # 2. Retrieve Monthly Data & Transits
        monthly_data = VedicPanchangService.get_monthly_panchang_summary(
            year=int(sel_cal_year),
            month=int(sel_cal_month_idx),
            latitude=lat_val,
            longitude=lon_val,
            tz_offset_hours=tz_val,
            calendar_type=sel_cal_type
        )
        monthly_transits = VedicPanchangService.get_monthly_transits(
            year=int(sel_cal_year),
            month=int(sel_cal_month_idx)
        )

        # Monthly Overview Info Banner
        sample_first = monthly_data[0] if monthly_data else {}
        sample_mid = monthly_data[len(monthly_data)//2] if monthly_data else {}
        m_name_disp = sample_mid.get("masa_name", sample_first.get("masa_name", "मास"))
        sun_r_disp = sample_mid.get("sun_sign", "सूर्य")

        type_desc = {
            "purnimanta": "उत्तर भारतीय पूर्णिमान्त नियम: माह का अन्त पूर्णिमा पर होता है, कृष्ण पक्ष नवीन मास का प्रथम पक्ष होता है।",
            "amanta": "दक्षिण व पश्चिम भारतीय अमान्त नियम: माह का अन्त अमावस्या पर होता है, शुक्ल पक्ष से नया मास आरम्भ होता है।",
            "solar": "सौर पञ्चाङ्ग नियम: सूर्य की निरयण राशि संक्रान्ति के दिन से मास का शुभारम्भ होता है।",
            "standard": "मानक दृक्-पञ्चाङ्ग नियम: दृक्-गणित सिद्ध निरयण खगोलीय गणना पर आधारित।"
        }.get(sel_cal_type, "")

        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#FFFBEB'}; border:1.5px solid #F59E0B;
                    border-radius:10px; padding:12px 18px; margin:12px 0 16px 0; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <b style="color:#B45309; font-size:16px;">📖 {months_hi[sel_cal_month_idx-1]} {sel_cal_year} — {m_name_disp} ({cal_type_dict[sel_cal_type].split('(')[0].strip()})</b>
                <div style="color:{'#D1D5DB' if is_dark else '#78350F'}; font-size:12.5px; margin-top:2px;">
                    {type_desc} | सूर्य स्थिति: <b>{sun_r_disp} राशि</b> | कुल दिन: <b>{len(monthly_data)}</b>
                </div>
            </div>
            <div>
                <span style="background:#FDE68A; color:#78350F; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px;">
                    🪐 ग्रह गोचर: {len(monthly_transits)} | पर्व/व्रत: {len([x for x in monthly_data if x.get('festival')])}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Five Researched Sub-Tabs
        sub_c1, sub_c2, sub_c3, sub_c4, sub_c5 = st.tabs([
            "🗓️ मासिक कैलेंडर ग्रिड (Visual Grid)",
            "📋 सम्पूर्ण ३०-दिवसीय तालिका (Master Table)",
            "🚩 प्रमुख व्रत, पर्व एवं त्यौहार संकलन",
            "🪐 मासिक ग्रह गोचर व संक्रान्ति",
            "⚡ पञ्चक, भद्रा एवं शुभाशुभ काल चक्र"
        ])

        # ---------------------------------------------------------
        # SUB-TAB 1: मासिक विजुअल ग्रिड
        # ---------------------------------------------------------
        with sub_c1:
            st.markdown("#### 🗓️ मासिक पञ्चाङ्ग ग्रिड (Monthly Visual Grid)")
            weekdays_names = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
            hdr_cols = st.columns(7)
            for w_idx, w_name in enumerate(weekdays_names):
                with hdr_cols[w_idx]:
                    st.markdown(f"""
                    <div style="background:{'#374151' if is_dark else '#F1F5F9'}; color:{'#F3F4F6' if is_dark else '#334155'};
                                padding:8px; border-radius:6px; text-align:center; font-weight:700; font-size:12px; margin-bottom:8px;">
                        {w_name}
                    </div>
                    """, unsafe_allow_html=True)

            first_day_weekday = monthly_data[0]["weekday"] if monthly_data else 0
            grid_slots = [None] * first_day_weekday + monthly_data

            total_rows = (len(grid_slots) + 6) // 7
            for r in range(total_rows):
                row_cols = st.columns(7)
                for c in range(7):
                    idx = r * 7 + c
                    with row_cols[c]:
                        if idx < len(grid_slots) and grid_slots[idx] is not None:
                            day_obj = grid_slots[idx]
                            is_today = (day_obj["date"] == selected_date)
                            cell_bdr = "#2563EB" if is_today else ('#374151' if is_dark else '#E2E8F0')
                            cell_bg = "#EFF6FF" if is_today else ('#1F2937' if is_dark else '#FFFFFF')

                            # Badge tags
                            tags = []
                            if day_obj.get("is_ekadashi"):
                                tags.append(f'<span style="background:#FEF3C7; color:#B45309; padding:1px 4px; border-radius:4px; font-size:9.5px; font-weight:700;">{day_obj["festival"]}</span>')
                            elif day_obj.get("is_purnima"):
                                tags.append('<span style="background:#EDE9FE; color:#6D28D9; padding:1px 4px; border-radius:4px; font-size:9.5px; font-weight:700;">🌕 पूर्णिमा</span>')
                            elif day_obj.get("is_amavasya"):
                                tags.append('<span style="background:#FEE2E2; color:#991B1B; padding:1px 4px; border-radius:4px; font-size:9.5px; font-weight:700;">🌑 अमावस्या</span>')
                            elif day_obj.get("is_sankranti"):
                                tags.append(f'<span style="background:#FFEDD5; color:#C2410C; padding:1px 4px; border-radius:4px; font-size:9.5px; font-weight:700;">☀️ {day_obj["festival"]}</span>')
                            elif day_obj.get("festival"):
                                tags.append(f'<span style="background:#E0E7FF; color:#3730A3; padding:1px 4px; border-radius:4px; font-size:9.5px; font-weight:700;">{day_obj["festival"][:10]}</span>')

                            if day_obj.get("special_yoga") and day_obj.get("special_yoga") != "—":
                                tags.append(f'<span style="background:#DCFCE7; color:#15803D; padding:1px 4px; border-radius:4px; font-size:9px; font-weight:700;">✨ {day_obj["special_yoga"].split("/")[0].strip()}</span>')

                            if day_obj.get("is_panchak"):
                                tags.append('<span style="background:#F3E8FF; color:#7E22CE; padding:1px 3px; border-radius:3px; font-size:8.5px;">⚡पञ्चक</span>')

                            tags_block = f'<div style="margin-top:3px; display:flex; flex-direction:column; gap:2px;">{" ".join(tags)}</div>' if tags else '<div style="min-height:16px;"></div>'

                            cell_title_col = '#3B82F6' if is_today else ('#FFFFFF' if is_dark else '#0F172A')
                            cell_sub_col = '#93C5FD' if is_today else ('#D1D5DB' if is_dark else '#334155')

                            card_html = (
                                f'<div style="background:{cell_bg}; border:1.5px solid {cell_bdr}; border-radius:8px; '
                                f'padding:6px; min-height:102px; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
                                f'<div style="display:flex; justify-content:space-between; align-items:baseline;">'
                                f'<b style="font-size:14px; color:{cell_title_col};">{day_obj["day"]}</b>'
                                f'<span style="font-size:9.5px; color:#64748B;">{day_obj["paksha"][:1]} | {day_obj.get("moon_sign", "")[:2]}</span>'
                                f'</div>'
                                f'<div style="font-size:11px; font-weight:700; color:{cell_sub_col}; margin:2px 0;">{day_obj["tithi_name"]}</div>'
                                f'<div style="font-size:10px; color:#94A3B8;">{day_obj["nak_name"]}</div>'
                                f'{tags_block}'
                                f'</div>'
                            )
                            st.markdown(card_html, unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="min-height:102px; margin-bottom:8px;"></div>', unsafe_allow_html=True)

        # ---------------------------------------------------------
        # SUB-TAB 2: सम्पूर्ण मासिक तालिका (Master Table)
        # ---------------------------------------------------------
        with sub_c2:
            st.markdown("#### 📋 सम्पूर्ण मासिक पञ्चाङ्ग तालिका (30-Day Master Table)")
            table_rows = []
            for d in monthly_data:
                table_rows.append({
                    "तारीख": f"{d['day']:02d}-{sel_cal_month_idx:02d}-{sel_cal_year}",
                    "वार": d.get("weekday_full_hi", d.get("weekday_hi")),
                    "मास व पक्ष": f"{d.get('masa_name', '')} {d.get('paksha', '')}",
                    "तिथि": d.get("tithi_name"),
                    "नक्षत्र": d.get("nak_name"),
                    "चन्द्र राशि": d.get("moon_sign"),
                    "सूर्य राशि": d.get("sun_sign"),
                    "पर्व / त्यौहार": d.get("festival") or "—",
                    "विशेष योग": d.get("special_yoga") or "—",
                    "पञ्चक / भद्रा": ("⚡ पञ्चक" if d.get("is_panchak") else "") + (" 🛡️ भद्रा" if d.get("is_bhadra") else "") or "सामान्य"
                })
            st.table(table_rows)

        # ---------------------------------------------------------
        # SUB-TAB 3: प्रमुख व्रत, पर्व एवं त्यौहार संकलन
        # ---------------------------------------------------------
        with sub_c3:
            st.markdown("#### 🚩 इस माह के प्रमुख व्रत, पर्व एवं महा-त्यौहार (Festival Agenda)")
            fest_days = [d for d in monthly_data if d.get("festival") or d.get("is_ekadashi") or d.get("is_purnima") or d.get("is_amavasya") or d.get("is_pradosh")]
            if fest_days:
                cols_f = st.columns(2)
                for f_idx, fd in enumerate(fest_days):
                    with cols_f[f_idx % 2]:
                        badge_color = "#B45309" if fd.get("is_ekadashi") else ("#6D28D9" if fd.get("is_purnima") else ("#991B1B" if fd.get("is_amavasya") else "#2563EB"))
                        f_title = fd.get("festival") or (
                            "एकादशी व्रत" if fd.get("is_ekadashi") else (
                                "पूर्णिमा व्रत" if fd.get("is_purnima") else (
                                    "अमावस्या" if fd.get("is_amavasya") else (
                                        "प्रदोष व्रत" if fd.get("is_pradosh") else "पावन पर्व"
                                    )
                                )
                            )
                        )
                        st.markdown(f"""
                        <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                                    border-left:4px solid {badge_color}; border-radius:8px; padding:12px 14px; margin-bottom:10px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:{badge_color}; font-size:15px;">🚩 {f_title}</b>
                                <span style="background:{badge_color}20; color:{badge_color}; padding:2px 8px; border-radius:10px; font-weight:700; font-size:11px;">
                                    {fd['day']} {months_hi[sel_cal_month_idx-1].split('.')[1].split('(')[0].strip()}
                                </span>
                            </div>
                            <div style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:12.5px; margin-top:4px;">
                                • <b>वार:</b> {fd['weekday_full_hi']} | <b>तिथि:</b> {fd['tithi_name']} ({fd['paksha']})<br/>
                                • <b>नक्षत्र:</b> {fd['nak_name']} | <b>चन्द्र राशि:</b> {fd['moon_sign']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("इस माह में कोई विशिष्ट प्रमुख महापर्व नहीं है।")

        # ---------------------------------------------------------
        # SUB-TAB 4: मासिक ग्रह गोचर व संक्रान्ति
        # ---------------------------------------------------------
        with sub_c4:
            st.markdown("#### 🪐 इस माह के प्रमुख ग्रह गोचर व संक्रान्ति (Planetary Transits)")
            if monthly_transits:
                for tr in monthly_transits:
                    t_col = "#C2410C" if tr["planet"] == "Sun" else "#4338CA"
                    st.markdown(f"""
                    <div style="background:{'#1F2937' if is_dark else '#FFF7ED' if tr['planet'] == 'Sun' else '#EEF2FF'};
                                border:1.5px solid {t_col}; border-radius:10px; padding:14px 18px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{t_col}; font-size:16px;">{tr['badge']}: {tr['title']}</b>
                            <span style="background:{t_col}20; color:{t_col}; padding:3px 10px; border-radius:12px; font-weight:700; font-size:12px;">
                                दिनांक: {tr['day']} {months_hi[sel_cal_month_idx-1].split('.')[1].split('(')[0].strip()} {sel_cal_year}
                            </span>
                        </div>
                        <div style="color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13px; margin-top:6px;">
                            {tr['description']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"{months_hi[sel_cal_month_idx-1].split('.')[1].split('(')[0].strip()} {sel_cal_year} में मुख्य ग्रहों का कोई बड़ा राशि परिवर्तन निर्धारित नहीं है।")

        # ---------------------------------------------------------
        # SUB-TAB 5: पञ्चक, भद्रा एवं शुभाशुभ काल
        # ---------------------------------------------------------
        with sub_c5:
            st.markdown("#### ⚡ मासिक पञ्चक, भद्रा एवं शुभ योग काल चक्र (Inauspicious & Super Yoga Dates)")
            col_u1, col_u2 = st.columns(2)

            with col_u1:
                panchak_days = [d["day"] for d in monthly_data if d.get("is_panchak")]
                bhadra_days = [d["day"] for d in monthly_data if d.get("is_bhadra")]
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#FEF2F2'}; border:1px solid #FECACA; border-radius:10px; padding:16px;">
                    <b style="color:#991B1B; font-size:15px;">⚡ पञ्चक एवं भद्रा दिवस (सावधानी काल):</b>
                    <div style="font-size:13px; color:{'#D1D5DB' if is_dark else '#334155'}; margin-top:6px; line-height:1.7;">
                        • <b>पञ्चक तिथियां (चन्द्रमा कुम्भ/मीन):</b> {', '.join(str(x) for x in panchak_days) if panchak_days else 'इस माह पञ्चक नहीं'}<br/>
                        <small style="color:#DC2626;">(पञ्चक में दक्षिण दिशा यात्रा, तृण/काष्ठ संग्रह व छत डालना वर्जित)</small><br/>
                        • <b>भद्रा तिथियां (विष्टि करण):</b> {', '.join(str(x) for x in bhadra_days) if bhadra_days else 'इस माह भद्रा नहीं'}<br/>
                        <small style="color:#DC2626;">(भद्रा काल में मांगलिक उत्सव त्याज्य)</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_u2:
                shubh_yoga_days = [f"{d['day']} तारीख ({d.get('special_yoga')})" for d in monthly_data if d.get("special_yoga") and d.get("special_yoga") != "—"]
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:1px solid #BBF7D0; border-radius:10px; padding:16px;">
                    <b style="color:#166534; font-size:15px;">✨ सर्वार्थ सिद्धि व अमृत सिद्धि योग (महा-शुभ काल):</b>
                    <div style="font-size:13px; color:{'#D1D5DB' if is_dark else '#334155'}; margin-top:6px; line-height:1.7;">
                        • <b>सर्वश्रेष्ठ कार्य-सिद्धि दिवस:</b><br/>
                        {'<br/>• '.join(shubh_yoga_days) if shubh_yoga_days else 'इस माह कोई विशेष संयोग नहीं'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ---------------------------------------------------------
        # Quick Day Inspector (त्वरित दिन सूक्ष्म पञ्चाङ्ग)
        # ---------------------------------------------------------
        st.markdown("---")
        st.markdown("#### 🔍 किसी भी तारीख का त्वरित सूक्ष्म पञ्चाङ्ग परीक्षण (Day Inspector)")
        ins_col1, ins_col2 = st.columns([1.5, 3.5])
        with ins_col1:
            default_insp_day = min(selected_date.day, len(monthly_data)) if (selected_date.year == sel_cal_year and selected_date.month == sel_cal_month_idx) else 1
            insp_day = st.selectbox(
                "तारीख चुनें (Select Day):",
                range(1, len(monthly_data) + 1),
                index=default_insp_day - 1,
                format_func=lambda x: f"{x:02d} {months_hi[sel_cal_month_idx-1].split('.')[1].split('(')[0].strip()} ({monthly_data[x-1]['weekday_full_hi']})",
                key="panchang_inspect_day_choice"
            )
        with ins_col2:
            target_obj = monthly_data[insp_day - 1]
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                        border-left:4px solid #2563EB; border-radius:8px; padding:12px 16px;">
                <b style="color:#1D4ED8; font-size:15px;">📌 {target_obj['day']} {months_hi[sel_cal_month_idx-1].split('.')[1].split('(')[0].strip()} {sel_cal_year} ({target_obj['weekday_full_hi']})</b>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:13px; color:{'#D1D5DB' if is_dark else '#334155'}; margin-top:6px;">
                    <div>• <b>तिथि:</b> {target_obj['tithi_name']} ({target_obj['paksha']})</div>
                    <div>• <b>नक्षत्र:</b> {target_obj['nak_name']}</div>
                    <div>• <b>मास:</b> {target_obj.get('masa_name', '—')}</div>
                    <div>• <b>चन्द्र राशि:</b> {target_obj.get('moon_sign', '—')}</div>
                    <div>• <b>विशेष योग:</b> {target_obj.get('special_yoga', '—')}</div>
                    <div>• <b>पर्व/त्यौहार:</b> {target_obj.get('festival') or 'सामान्य नित्य कर्म'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================
    # TAB 12: AI पञ्चाङ्ग सारथी व दैनिक कर्म शुद्धि
    # =============================================================
    with tab12:
        st.markdown("### 🤖 AI पञ्चाङ्ग सारथी व कर्म शुद्धि (AI Advisor & Shuddhi)")
        st.caption("दैनिक कर्म शुद्धि स्कोरकार्ड, दिशा शूल, अग्नि/शिव वास एवं जेमिनी AI समर्थित पञ्चाङ्ग परामर्शदाता:")

        # 1. AI PANCHANG ADVISOR
        st.markdown("#### 🤖 १. दैवज्ञ AI पञ्चाङ्ग सारथी (Ask AI Muhurta Advisor)")
        st.markdown("""
        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:12px 16px; margin-bottom:14px;">
            <b style="color:#1E40AF; font-size:14px;">💡 AI पञ्चाङ्ग परामर्श:</b>
            <span style="color:#1E3A8A; font-size:13px;"> आज के दिन किसी भी कार्य (वाहन क्रय, व्यापार, यात्रा, गृह पूजन आदि) की शुभता व समय जानने हेतु नीचे त्वरित प्रश्न चुनें अथवा स्वयं टाइप करें:</span>
        </div>
        """, unsafe_allow_html=True)

        preset_qs = [
            "🚗 क्या आज नया वाहन खरीदना शुभ रहेगा?",
            "🏠 क्या आज गृह प्रवेश या नींव पूजन कर सकते हैं?",
            "📈 आज नया व्यापार या दुकान शुरू करने का सबसे श्रेष्ठ समय क्या है?",
            "🪔 आज पितृ तर्पण व दान का सर्वोत्तम मुहूर्त क्या है?",
            "✈️ आज किसी महत्वपूर्ण यात्रा पर जाना अनुकूल है या नहीं?"
        ]
        chosen_preset = st.selectbox("त्वरित शास्त्रीय प्रश्न चुनें:", ["-- अपना प्रश्न लिखें --"] + preset_qs, key="panchang_ai_preset")

        user_ai_q = st.text_input("अथवा अपना विशिष्ट प्रश्न लिखें:", value="" if chosen_preset == "-- अपना प्रश्न लिखें --" else chosen_preset, key="panchang_ai_custom_q")

        if st.button("🔮 AI पञ्चाङ्ग शास्त्रीय परामर्श प्राप्त करें", key="btn_ask_panchang_ai"):
            if user_ai_q.strip():
                with st.spinner("दैवज्ञ AI आज के पञ्चाङ्ग, मुहूर्त चिन्तामणि व ग्रह गोचर का शोधन कर रहा है..."):
                    ai_ans = ask_ai_panchang_advisor(user_ai_q, panchang_data)
                st.markdown(f"""
                <div style="background:#F0FDF4; border:1.5px solid #16A34A; border-radius:12px; padding:18px; margin:16px 0;">
                    <b style="color:#166534; font-size:16px;">🌟 दैवज्ञ AI पञ्चाङ्ग निर्णय:</b>
                    <div style="color:#14532D; font-size:14px; line-height:1.7; margin-top:8px;">
                        {ai_ans}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("कृपया कोई प्रश्न चुनें अथवा लिखें।")

        st.markdown("---")

        # 2. DISHA SHOOLA & CHANDRA VASA
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("#### 🧭 २. दिशा शूल एवं चन्द्र वास")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFBEB'}; border:1px solid {'#374151' if is_dark else '#FDE68A'};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:#92400E; font-size:15px;">🚨 आज का दिशा शूल: {nivas['disha_shoola']['direction']}</b>
                <div style="color:#78350F; font-size:13px; margin-top:4px;">
                    <b>निवारक उपाय (Parihar):</b> {nivas['disha_shoola']['parihar']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#EFF6FF'}; border:1px solid {'#374151' if is_dark else '#BFDBFE'};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:#1E40AF; font-size:15px;">🌙 चन्द्र वास: {nivas['chandra_vasa']['direction']}</b>
                <div style="color:#1E3A8A; font-size:13px; margin-top:4px;">
                    {nivas['chandra_vasa']['rule']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown("#### 🔥 ३. अग्नि वास एवं शिव वास विचार")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {nivas['agnivasa']['color']};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:{nivas['agnivasa']['color']}; font-size:15px;">🔥 अग्नि वास (हवन विचार): {nivas['agnivasa']['vasa']}</b>
                <div style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin-top:4px;">
                    {nivas['agnivasa']['verdict']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {nivas['shivavasa']['color']};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:{nivas['shivavasa']['color']}; font-size:15px;">🔱 शिव वास (रुद्राभिषेक विचार): {nivas['shivavasa']['vasa']}</b>
                <div style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin-top:4px;">
                    {nivas['shivavasa']['verdict']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 3. ACTION SUITABILITY SCORECARD
        is_pitru_active = pitru.get("is_active", False)

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h4 style="margin:0;">🎯 ४. दैनिक कर्म शुद्धि स्कोरकार्ड (Action Suitability Scorecard)</h4>
            {'<span style="background:#FEE2E2; color:#DC2626; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;">⚠️ पितृपक्ष निषेध नियम लागू</span>' if is_pitru_active else ''}
        </div>
        """, unsafe_allow_html=True)

        acts_cols = st.columns(4)
        acts_list = [
            ("🏠 गृह प्रवेश", "🚫 सर्वथा वर्जित (पितृपक्ष)" if is_pitru_active else ("वर्जित" if bhadra.get("is_fatal_on_earth") or "रिक्ता" in pillars["tithi"]["category"] else "शुभ"), "#DC2626" if (is_pitru_active or bhadra.get("is_fatal_on_earth")) else "#059669"),
            ("💍 विवाह संस्कार", "🚫 महा-निषेध (पितृपक्ष)" if is_pitru_active else ("वर्जित" if bhadra.get("is_fatal_on_earth") or not pillars["yoga"]["is_good"] else "शुभ"), "#DC2626" if (is_pitru_active or bhadra.get("is_fatal_on_earth")) else "#059669"),
            ("🚗 वाहन क्रय", "⚠️ त्याज्य (विलासिता वर्जित)" if is_pitru_active else "चर/लाभ चौघड़िया में शुभ", "#DC2626" if is_pitru_active else "#059669"),
            ("📈 नवीन व्यापार आरम्भ", "🚫 वर्जित (नवीन आरम्भ निषिद्ध)" if is_pitru_active else "लाभ/अमृत चौघड़िया में उत्तम", "#DC2626" if is_pitru_active else "#059669"),
            ("🌾 भूमि पूजन / नींव", "🚫 वर्जित (पितृपक्ष/पञ्चक)" if (is_pitru_active or pg["panchaka"]["is_active"]) else "शुभ", "#DC2626" if (is_pitru_active or pg["panchaka"]["is_active"]) else "#059669"),
            ("✈️ यात्रा आरम्भ", "दिशा शूल परिहार आवश्यक", "#D97706"),
            ("💰 स्वर्ण व आभूषण", "⚠️ नवीन उपभोग त्याज्य" if is_pitru_active else "शुभ चौघड़िया में क्रय", "#D97706" if is_pitru_active else "#059669"),
            ("🪔 तर्पण व पिण्डदान", "🌟 सर्वोत्तम (परम पितृ-तृप्ति)" if is_pitru_active else "अमावस्या/संक्रान्ति पर शुभ", "#059669"),
            ("🍲 पंचबलि व ब्राह्मण भोज", "🟢 परम कल्याणकारी (अक्षय पुण्य)" if is_pitru_active else "शुभ कर्म", "#059669"),
            ("📖 गीता पाठ (अध्याय ७ व ११)", "सर्वदोष नाशक व पितृ उद्धारक", "#059669"),
            ("🌿 दान-पुण्य व गौ सेवा", "अति उत्तम (अक्षय फल)", "#059669"),
            ("💊 औषधि सेवन", "शुभ", "#059669")
        ]
        for idx, (act_name, act_status, act_color) in enumerate(acts_list):
            with acts_cols[idx % 4]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                            border-left:3px solid {act_color}; border-radius:6px; padding:10px; margin-bottom:8px; text-align:center;">
                    <b style="font-size:13px; color:{'#FFFFFF' if is_dark else '#0F172A'};">{act_name}</b>
                    <div style="color:{act_color}; font-size:12px; font-weight:700; margin-top:2px;">{act_status}</div>
                </div>
                """, unsafe_allow_html=True)
