import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import importlib
import src.jyotish.ui.sudarshan as sudarshan
from src.jyotish.ui.sudarshan import default_sudarshan_engine

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def render_sudarshan_chakra_view(chart, birth_profile, tz_offset=5.5, tabs=None):
    if tabs is None:
        tabs = [
            '☸️ त्रि-स्तरीय सुदर्शन चक्र',
            '🏰 १२ भाव त्रिकोणीय दृष्टि',
            '🪐 सुदर्शन दशा व चक्र वर्ष',
            '📊 संयुक्त शुभ-अशुभ स्कोर'
        ]
    st.subheader("☸️ सुदर्शन चक्र (Sudarshan Chakra - 3-Ring Concentric Mandala)")
    st.write("बृहत्पाराशर होराशास्त्र (BPHS), अध्याय ७४ अनुसार लग्न (स्थूल देह), चन्द्र (सूक्ष्म मन) एवं सूर्य (कारण आत्मा) तीनों संकेंद्री चक्रों का एक साथ सर्वांगीण त्रिविध विश्लेषण।")

    # Native basic info for age calculation
    from datetime import datetime, date
    import importlib
    from src.jyotish.ui import sudarshan
    if not hasattr(default_sudarshan_engine, "calculate_triad_dominance") or not hasattr(default_sudarshan_engine, "calculate_dasha"):
        importlib.reload(sudarshan)
    engine_sd = getattr(sudarshan, "default_sudarshan_engine", default_sudarshan_engine)

    # Shastric naming dictionaries & fallbacks
    SIGN_NAMES_HI = getattr(sudarshan, "SIGN_NAMES_HI", [
        "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
        "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"
    ])
    PLANET_NAMES_HI = getattr(sudarshan, "PLANET_NAMES_HI", {
        "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
        "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
    })
    SIGN_LORDS = getattr(sudarshan, "SIGN_LORDS", {
        1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
        7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
    })

    native_birth_year = birth_profile.birth_date.year
    curr_year = get_live_local_now(tz_offset).year
    default_calc_age = max(1, curr_year - native_birth_year)

    # Master calculation from engine
    sd_full_res = engine_sd.calculate(chart)
    sd_triad_dom = engine_sd.calculate_triad_dominance(chart)
    sd_counts = sd_full_res.get("summary_counts", {})

    # Top Hero KPI Banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #1E3A8A 0%, #1E40AF 50%, #047857 100%); border-radius:12px; padding:18px 24px; color:#FFFFFF; margin-bottom:16px; box-shadow:0 4px 14px rgba(30,58,138,0.18);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
            <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; opacity:0.85;">श्री विष्णु सुदर्शन चक्र मण्डल • त्रि-शरीर मीमांसा</div>
            <div style="font-size:22px; font-weight:900; margin-top:4px;">☸️ मुख्य नियंता लग्न: {sd_triad_dom['dominant_lagna']} ({sd_triad_dom['dominant_score']}%)</div>
            <div style="font-size:13px; opacity:0.92; margin-top:4px;">{sd_triad_dom['harmony_level']} | जातक आयु: {default_calc_age} वर्ष</div>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:18px; font-weight:900;">{sd_counts.get('tri_shubh', 0)}</div>
                <div style="font-size:11px; font-weight:700;">🌟 त्रि-शुभ भाव</div>
            </div>
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:18px; font-weight:900;">{sd_counts.get('dvi_shubh', 0)}</div>
                <div style="font-size:11px; font-weight:700;">🟢 द्वि-शुभ भाव</div>
            </div>
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:18px; font-weight:900;">{sd_counts.get('eka_shubh', 0)}</div>
                <div style="font-size:11px; font-weight:700;">🟡 एक-शुभ भाव</div>
            </div>
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:18px; font-weight:900;">{sd_counts.get('tri_ashubh', 0)}</div>
                <div style="font-size:11px; font-weight:700;">🔴 त्रि-अशुभ भाव</div>
            </div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    tab_sd1, tab_sd2, tab_sd3, tab_sd4, tab_sd5, tab_sd6, tab_sd7, tab_sd8, tab_sd9 = st.tabs(tabs)

    # -------------------------------------------------------------------------
    # TAB 1: VISUAL SVG MANDALA
    # -------------------------------------------------------------------------
    with tab_sd1:
        st.markdown("### ☸️ त्रि-चक्रीय सुदर्शन मण्डल (Visual Concentric Mandala)")
        col_ctrl1, col_ctrl2 = st.columns([1.5, 2.5])
        with col_ctrl1:
            sel_vis_house = st.selectbox(
                "विशेष भाव चक्र पर आलोकित (Highlight) करें:",
                options=list(range(1, 13)),
                index=0,
                format_func=lambda x: f"भाव {x}: {sd_full_res['houses'][x-1]['house_name'].split('(')[1].replace(')', '')}"
            )
        with col_ctrl2:
            st.caption("🟢 **आंतरिक वृत्त (Inner Ring):** जन्म लग्न (स्थूल देह) | 🔵 **मध्य वृत्त (Middle Ring):** चन्द्र कुण्डली (सूक्ष्म मन) | 🟡 **बाह्य वृत्त (Outer Ring):** सूर्य कुण्डली (कारण आत्मा)")

        col_svg1, col_svg2 = st.columns([1.3, 1.7])
        with col_svg1:
            svg_code = engine_sd.render_sudarshan_svg(chart, active_house=sel_vis_house)
            clean_svg = "\n".join(l.strip() for l in svg_code.splitlines() if l.strip() and not (l.strip().startswith("<!--") and l.strip().endswith("-->")))
            st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin:0 auto;">{clean_svg}</div>', unsafe_allow_html=True)

        with col_svg2:
            st.markdown("#### 🌟 त्रि-लग्न आधार स्तम्भ (Tripod of Life)")
            c_l1, c_l2, c_l3 = st.columns(3)
            with c_l1:
                st.markdown(f"""
    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:12px; height:100%;">
    <div style="font-size:12px; font-weight:800; color:#065F46;">🟢 देह लग्न (Lagna)</div>
    <div style="font-size:18px; font-weight:900; color:#047857; margin:4px 0;">{sd_full_res['lagna_sign_hi']}</div>
    <div style="font-size:11px; color:#065F46;"><b>अधिपति:</b> {PLANET_NAMES_HI.get(SIGN_LORDS[chart.lagna_sign_id], '')}</div>
    <div style="font-size:11px; color:#065F46; margin-top:4px;"><b>बल स्कोर:</b> {sd_triad_dom['lagna_score']}/100</div>
    <div style="font-size:10px; color:#047857; margin-top:4px; line-height:1.3;">स्थूल शरीर, भौतिक स्वास्थ्य व बाह्य क्रियाकलाप</div>
    </div>
    """, unsafe_allow_html=True)
            with c_l2:
                moon_sign_id_curr = chart.planets["Moon"].sign_id
                st.markdown(f"""
    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:12px; height:100%;">
    <div style="font-size:12px; font-weight:800; color:#1E40AF;">🔵 मन लग्न (Moon)</div>
    <div style="font-size:18px; font-weight:900; color:#1D4ED8; margin:4px 0;">{sd_full_res['chandra_sign_hi']}</div>
    <div style="font-size:11px; color:#1E40AF;"><b>अधिपति:</b> {PLANET_NAMES_HI.get(SIGN_LORDS[moon_sign_id_curr], '')}</div>
    <div style="font-size:11px; color:#1E40AF; margin-top:4px;"><b>बल स्कोर:</b> {sd_triad_dom['chandra_score']}/100</div>
    <div style="font-size:10px; color:#1E40AF; margin-top:4px; line-height:1.3;">सूक्ष्म मन, भावनाएं, ग्रहणशीलता व सुख-दुःख</div>
    </div>
    """, unsafe_allow_html=True)
            with c_l3:
                sun_sign_id_curr = chart.planets["Sun"].sign_id
                st.markdown(f"""
    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:12px; height:100%;">
    <div style="font-size:12px; font-weight:800; color:#92400E;">🟡 आत्म लग्न (Sun)</div>
    <div style="font-size:18px; font-weight:900; color:#B45309; margin:4px 0;">{sd_full_res['surya_sign_hi']}</div>
    <div style="font-size:11px; color:#92400E;"><b>अधिपति:</b> {PLANET_NAMES_HI.get(SIGN_LORDS[sun_sign_id_curr], '')}</div>
    <div style="font-size:11px; color:#92400E; margin-top:4px;"><b>बल स्कोर:</b> {sd_triad_dom['surya_score']}/100</div>
    <div style="font-size:10px; color:#92400E; margin-top:4px; line-height:1.3;">कारण आत्मा, प्राण-शक्ति, प्रतिष्ठा व दैवीय कृपा</div>
    </div>
    """, unsafe_allow_html=True)

            sel_h_data = sd_full_res["houses"][sel_vis_house - 1]
            st.markdown(f"""
    <div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:10px; padding:14px; margin-top:14px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:15px; font-weight:900; color:#0F172A;">🎯 चयनित: {sel_h_data['house_name']}</span>
        <span style="font-size:13px; font-weight:800; color:#047857;">{sel_h_data['status']} ({sel_h_data['score']})</span>
    </div>
    <div style="font-size:12px; color:#334155; margin-top:8px; line-height:1.5;">
        <b>लग्न से:</b> {sel_h_data['l_sign_hi']} (भावेश: {sel_h_data['l_lord_hi']}, स्थित: {', '.join(sel_h_data['l_planets_hi']) if sel_h_data['l_planets_hi'] else 'कोई नहीं'})<br/>
        <b>चन्द्र से:</b> {sel_h_data['m_sign_hi']} (भावेश: {sel_h_data['m_lord_hi']}, स्थित: {', '.join(sel_h_data['m_planets_hi']) if sel_h_data['m_planets_hi'] else 'कोई नहीं'})<br/>
        <b>सूर्य से:</b> {sel_h_data['s_sign_hi']} (भावेश: {sel_h_data['s_lord_hi']}, स्थित: {', '.join(sel_h_data['s_planets_hi']) if sel_h_data['s_planets_hi'] else 'कोई नहीं'})
    </div>
    <div style="font-size:12px; background:#EFF6FF; border-left:3px solid #3B82F6; padding:8px; margin-top:8px; color:#1E3A8A; font-style:italic;">
        {sel_h_data['classical_sutra']}
    </div>
    <div style="font-size:12px; color:#0F172A; margin-top:6px;">
        {sel_h_data['phala_detail']}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: 12 HOUSES TRIPLE EVALUATION
    # -------------------------------------------------------------------------
    with tab_sd2:
        st.markdown("### 📊 द्वादश भावों का त्रि-स्तरीय समग्र मूल्यांकन (12 Bhavas Triple Evaluation)")
        st.write("प्रत्येक भाव का लग्न (शरीर), चन्द्र (मन) एवं सूर्य (आत्मा) तीनों दृष्टिकोणों से एक साथ संकेंद्री मूल्यांकन:")

        # Summary Table
        tbl_data = []
        for h in sd_full_res["houses"]:
            tbl_data.append({
                "भाव": h["house_num"],
                "भाव विवरण": h["house_name"].split("(")[0].strip(),
                "लग्न चक्र (Lagna)": f"{h['l_sign_hi']} | {', '.join(h['l_planets_hi']) if h['l_planets_hi'] else '—'}",
                "चन्द्र चक्र (Moon)": f"{h['m_sign_hi']} | {', '.join(h['m_planets_hi']) if h['m_planets_hi'] else '—'}",
                "सूर्य चक्र (Sun)": f"{h['s_sign_hi']} | {', '.join(h['s_planets_hi']) if h['s_planets_hi'] else '—'}",
                "समग्र स्कोर": h["score"],
                "शास्त्रीय कोटि": h["status"]
            })
        st.dataframe(pd.DataFrame(tbl_data), use_container_width=True, hide_index=True)

        st.markdown("#### 🔍 द्वादश भाव विस्तृत व्याख्या (Deep Bhava Breakdown)")
        for h in sd_full_res["houses"]:
            with st.expander(f"{h['house_name']} — {h['status']} ({h['score']})"):
                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    st.markdown(f"""
    <div style="background:#ECFDF5; border:1px solid #10B981; border-radius:8px; padding:10px;">
    <b>🟢 लग्न दृष्टि (Physical Plane):</b><br/>
    • राशि: <b>{h['l_sign_hi']}</b><br/>
    • भावेश: <b>{h['l_lord_hi']}</b><br/>
    • स्थित ग्रह: <b>{', '.join(h['l_planets_hi']) if h['l_planets_hi'] else 'रिक्त'}</b><br/>
    • दृष्टियां: {', '.join(h['l_aspects_hi']) if h['l_aspects_hi'] else 'कोई नहीं'}<br/>
    • स्तर: {h['l_score']}/100
    </div>
    """, unsafe_allow_html=True)
                with col_h2:
                    st.markdown(f"""
    <div style="background:#EFF6FF; border:1px solid #3B82F6; border-radius:8px; padding:10px;">
    <b>🔵 चन्द्र दृष्टि (Emotional Plane):</b><br/>
    • राशि: <b>{h['m_sign_hi']}</b><br/>
    • भावेश: <b>{h['m_lord_hi']}</b><br/>
    • स्थित ग्रह: <b>{', '.join(h['m_planets_hi']) if h['m_planets_hi'] else 'रिक्त'}</b><br/>
    • दृष्टियां: {', '.join(h['m_aspects_hi']) if h['m_aspects_hi'] else 'कोई नहीं'}<br/>
    • स्तर: {h['m_score']}/100
    </div>
    """, unsafe_allow_html=True)
                with col_h3:
                    st.markdown(f"""
    <div style="background:#FFFBEB; border:1px solid #F59E0B; border-radius:8px; padding:10px;">
    <b>🟡 सूर्य दृष्टि (Soul/Causal Plane):</b><br/>
    • राशि: <b>{h['s_sign_hi']}</b><br/>
    • भावेश: <b>{h['s_lord_hi']}</b><br/>
    • स्थित ग्रह: <b>{', '.join(h['s_planets_hi']) if h['s_planets_hi'] else 'रिक्त'}</b><br/>
    • दृष्टियां: {', '.join(h['s_aspects_hi']) if h['s_aspects_hi'] else 'कोई नहीं'}<br/>
    • स्तर: {h['s_score']}/100
    </div>
    """, unsafe_allow_html=True)
                st.markdown(f"**📜 शास्त्रीय सूत्र:** *{h['classical_sutra']}*")
                st.write(f"**💡 फलादेश विवरण:** {h['phala_detail']}")

    # -------------------------------------------------------------------------
    # TAB 3: SUDARSHAN DASHA
    # -------------------------------------------------------------------------
    with tab_sd3:
        st.markdown("### ⏳ सुदर्शन चक्र दशा प्रणाली (BPHS Chapter 74 Sudarshan Dasha)")
        st.write("पाराशरी सुदर्शन दशा में प्रत्येक भाव की अवधि १ वर्ष होती है (१ वर्ष = १ भाव)। प्रत्येक वर्ष में १२ मासिक अन्तर्दशाएं तथा प्रत्येक मास में २.५ दिनों की प्रत्यन्तर्दशा चलती है।")

        col_d1, col_d2 = st.columns([1.5, 2.5])
        with col_d1:
            sel_dasha_age = st.number_input(
                "जातक की आयु चयन करें (Target Age in Years):",
                min_value=1,
                max_value=108,
                value=default_calc_age,
                step=1
            )
        with col_d2:
            st.write("")
            st.caption(f"📍 जन्म वर्ष: **{native_birth_year}** | लक्षित आयु: **{sel_dasha_age} वर्ष** (वर्ष: **{native_birth_year + sel_dasha_age}**)")

        dasha_info = engine_sd.calculate_dasha(chart, int(sel_dasha_age))

        st.markdown(f"""
    <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:16px; margin:14px 0; box-shadow:0 2px 8px rgba(34,197,94,0.1);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div>
            <span style="font-size:12px; font-weight:800; color:#15803D; text-transform:uppercase;">वर्तमान सक्रिय वर्ष दशा (Active Sudarshan Dasha)</span>
            <div style="font-size:20px; font-weight:900; color:#14532D; margin-top:2px;">{dasha_info['active_house_name']} (चक्र {dasha_info['cycle_num']})</div>
        </div>
        <div style="background:#FFFFFF; border:1px solid #86EFAC; border-radius:8px; padding:6px 14px; font-size:13px; font-weight:800; color:#166534;">
            आयु: {dasha_info['current_age']} वर्ष
        </div>
    </div>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-top:12px;">
        <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #DCFCE7;">
            <div style="font-size:11px; color:#15803D;">🟢 लग्न राशि व भावेश:</div>
            <div style="font-size:14px; font-weight:800; color:#166534;">{dasha_info['active_lagna_sign']} ({dasha_info['active_lagna_lord']})</div>
            <div style="font-size:11px; color:#4B5563;">स्थित: {', '.join(dasha_info['active_lagna_occupants']) if dasha_info['active_lagna_occupants'] else '—'}</div>
        </div>
        <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #DCFCE7;">
            <div style="font-size:11px; color:#15803D;">🔵 चन्द्र राशि व भावेश:</div>
            <div style="font-size:14px; font-weight:800; color:#166534;">{dasha_info['active_moon_sign']} ({dasha_info['active_moon_lord']})</div>
            <div style="font-size:11px; color:#4B5563;">स्थित: {', '.join(dasha_info['active_moon_occupants']) if dasha_info['active_moon_occupants'] else '—'}</div>
        </div>
        <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #DCFCE7;">
            <div style="font-size:11px; color:#15803D;">🟡 सूर्य राशि व भावेश:</div>
            <div style="font-size:14px; font-weight:800; color:#166534;">{dasha_info['active_sun_sign']} ({dasha_info['active_sun_lord']})</div>
            <div style="font-size:11px; color:#4B5563;">स्थित: {', '.join(dasha_info['active_sun_occupants']) if dasha_info['active_sun_occupants'] else '—'}</div>
        </div>
    </div>
    <div style="font-size:13px; color:#14532D; margin-top:12px; background:#DCFCE7; padding:10px; border-radius:6px;">
        <b>🎯 वार्षिक फलादेश:</b> {dasha_info['annual_prediction']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        col_dsub1, col_dsub2 = st.columns([1.5, 1.5])
        with col_dsub1:
            st.markdown(f"#### 🗓️ १२ मासिक अन्तर्दशाएं (माह १ से १२ - आयु {sel_dasha_age} वर्ष)")
            m_tbl = []
            for m in dasha_info["monthly_antardashas"]:
                m_tbl.append({
                    "मास": m["month_label"],
                    "सक्रिय भाव": m["active_house_label"],
                    "लग्न राशि": m["lagna_sign"],
                    "चन्द्र राशि": m["moon_sign"],
                    "सूर्य राशि": m["sun_sign"]
                })
            st.dataframe(pd.DataFrame(m_tbl), use_container_width=True, hide_index=True)

        with col_dsub2:
            st.markdown(f"#### 🔄 १२-वर्षीय दशा चक्र (चक्र {dasha_info['cycle_num']})")
            cyc_tbl = []
            for c in dasha_info["cycle_table"]:
                cyc_tbl.append({
                    "वर्ष": c["year_in_cycle"],
                    "आयु": f"{c['age']} वर्ष {'👉' if c['is_current'] else ''}",
                    "सक्रिय भाव": c["house"],
                    "मुख्य विषय": c["theme"],
                    "लग्न राशि": c["lagna_rashi"],
                    "चन्द्र राशि": c["moon_rashi"]
                })
            st.dataframe(pd.DataFrame(cyc_tbl), use_container_width=True, hide_index=True)

        with st.expander("📜 ८४-वर्षीय जीवन कालक्रम तालिका (84-Year Lifetime Sudarshan Timeline)"):
            st.dataframe(pd.DataFrame(dasha_info["lifetime_timeline"]), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 4: PLANETARY ALIGNMENTS & MAHAYOGAS
    # -------------------------------------------------------------------------
    with tab_sd4:
        st.markdown("### 🪐 नवग्रह त्रि-लग्न संरेखण व सुदर्शन महायोग (Yogas & Planetary Alignments)")
        st.write("बृहत्पाराशर होराशास्त्रानुसार जब कोई ग्रह अथवा शुभ-योग तीनों संकेंद्री चक्रों (लग्न, चन्द्र, सूर्य) में एक साथ निर्मित होता है, तो उसका प्रभाव अखंड एवं अकाट्य होता है:")

        yogas_list = engine_sd.calculate_yogas(chart)
        for yg in yogas_list:
            bg_c = "#EFF6FF" if "राजयोग" in yg["category"] else ("#ECFDF5" if "आयु" in yg["category"] else ("#FEF3C7" if "शत्रु" in yg["category"] else "#FFF1F2"))
            bd_c = "#3B82F6" if "राजयोग" in yg["category"] else ("#10B981" if "आयु" in yg["category"] else ("#F59E0B" if "शत्रु" in yg["category"] else "#F43F5E"))
            st.markdown(f"""
    <div style="background:{bg_c}; border:1.5px solid {bd_c}; border-radius:10px; padding:14px; margin-bottom:12px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:16px; font-weight:900; color:#0F172A;">{yg['name']}</span>
        <span style="font-size:13px; font-weight:800; background:#FFFFFF; border:1px solid {bd_c}; padding:3px 10px; border-radius:6px;">{yg['status']}</span>
    </div>
    <div style="font-size:12px; color:#475569; margin-top:6px;"><b>शास्त्रीय स्थिति:</b> {yg['condition']}</div>
    <div style="font-size:13px; color:#0F172A; margin-top:6px; line-height:1.4;"><b>प्रभाव:</b> {yg['effect']}</div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("#### 🌟 नवग्रह त्रि-चक्रीय अवस्थिति सारणी (Planets across 3 Wheels)")
        pl_rows = []
        l_s_id = chart.lagna_sign_id
        m_s_id = chart.planets["Moon"].sign_id
        s_s_id = chart.planets["Sun"].sign_id

        for p_name, pos in chart.planets.items():
            p_hi = PLANET_NAMES_HI.get(p_name, p_name)
            h_from_l = ((pos.sign_id - l_s_id) % 12) + 1
            h_from_m = ((pos.sign_id - m_s_id) % 12) + 1
            h_from_s = ((pos.sign_id - s_s_id) % 12) + 1
            r_hi = SIGN_NAMES_HI[pos.sign_id - 1]

            pl_rows.append({
                "ग्रह (Graha)": p_hi,
                "वर्तमान राशि": f"{r_hi} ({pos.sign_degree:.1f}°)",
                "लग्न से भाव": f"भाव {h_from_l}",
                "चन्द्र से भाव": f"भाव {h_from_m}",
                "सूर्य से भाव": f"भाव {h_from_s}",
                "अवस्था / गति": "वक्री (R)" if pos.is_retrograde else "मार्गी (D)"
            })
        st.dataframe(pd.DataFrame(pl_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 5: 7 CORE LIFE DOMAINS
    # -------------------------------------------------------------------------
    with tab_sd5:
        st.markdown("### 🔍 प्रमुख जीवन क्षेत्र त्रि-आयामी फलित (7 Core Life Domains Synthesis)")
        st.write("जीवन के ७ प्रमुख आयामों का लग्न (देह), चन्द्र (मन) एवं सूर्य (आत्मा) तीनों दृष्टिकोणों से समन्वित विश्लेषण:")

        domains_list = engine_sd.calculate_life_domains(chart)
        c_dom1, c_dom2 = st.columns(2)
        for idx, d in enumerate(domains_list):
            target_col = c_dom1 if (idx % 2 == 0) else c_dom2
            with target_col:
                st.markdown(f"""
    <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; padding:14px; margin-bottom:12px; box-shadow:0 2px 6px rgba(0,0,0,0.04);">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:15px; font-weight:900; color:#1E293B;">{d['title']}</span>
        <span style="font-size:12px; font-weight:800; background:#F1F5F9; border:1px solid #CBD5E1; padding:3px 8px; border-radius:6px;">{d['status']}</span>
    </div>
    <div style="font-size:12px; color:#475569; margin-top:6px;">
        <b>संबद्ध भाव:</b> {d['bhavas_str']} | <b>कारक ग्रह:</b> {d['karakas']}
    </div>
    <div style="font-size:13px; color:#0F172A; margin-top:6px; line-height:1.4;">
        {d['desc']}
    </div>
    <div style="margin-top:8px; font-size:12px; font-weight:800; color:#2563EB;">
        त्रि-स्तरीय संयुक्त सामर्थ्य: {d['avg_score']}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 6: SUDARSHAN + ASHTAKAVARGA SYNTHESIS
    # -------------------------------------------------------------------------
    with tab_sd6:
        st.markdown("### 📈 सुदर्शन-अष्टकवर्ग बिन्दु समन्वय (Sudarshan + Ashtakavarga Synthesis)")
        st.write("सर्वाष्टकवर्ग (SAV) के बिन्दुओं का लग्न, चन्द्र और सूर्य तीनों चक्रों में सामंजस्य:")

        av_res = engine_sd.calculate_ashtakavarga_synthesis(chart)

        c_av1, c_av2, c_av3 = st.columns(3)
        c_av1.metric("लग्न राशि SAV बिन्दु", f"{av_res['lagna_sign_bindus']} बिन्दु", "देह सामर्थ्य")
        c_av2.metric("चन्द्र राशि SAV बिन्दु", f"{av_res['moon_sign_bindus']} बिन्दु", "मनोबल")
        c_av3.metric("सूर्य राशि SAV बिन्दु", f"{av_res['sun_sign_bindus']} बिन्दु", "आत्मबल")

        st.markdown("#### 📊 द्वादश भावों का त्रि-चक्रीय अष्टकवर्ग बिन्दु योग")
        st.dataframe(pd.DataFrame(av_res["rows"]), use_container_width=True, hide_index=True)

        chart_df = pd.DataFrame([{"भाव": r["house_label"], "औसत बिन्दु": r["avg_bindus"]} for r in av_res["rows"]]).set_index("भाव")
        st.bar_chart(chart_df)
        st.caption("💡 मानक सामर्थ्य: २८+ बिन्दु = उच्च बली भाव, २५-२८ बिन्दु = मध्यम, २५ से कम = संवेद्य भाव।")

    # -------------------------------------------------------------------------
    # TAB 7: TRIAD DOMINANCE & HARMONY
    # -------------------------------------------------------------------------
    with tab_sd7:
        st.markdown("### ⚖️ त्रि-लग्न प्राधान्यता व त्रि-शरीर मीमांसा (Lagna, Moon, Sun Supremacy)")
        st.write("बृहत्पाराशर होराशास्त्रानुसार (तत्र यद्बलाधिकं तदनुसारेण फलम्) जातक के जीवन का मुख्य चालक कौन है:")

        col_dom1, col_dom2 = st.columns([1.5, 1.5])
        with col_dom1:
            st.markdown(f"""
    <div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:10px; padding:16px;">
    <h4 style="margin:0 0 10px 0; color:#0F172A;">👑 मुख्य नियंता लग्न का निर्णय</h4>
    <div style="font-size:18px; font-weight:900; color:#1E40AF;">{sd_triad_dom['dominant_lagna']}</div>
    <div style="font-size:13px; color:#475569; margin-top:4px;">स्कोर: <b>{sd_triad_dom['dominant_score']}/100</b> ({sd_triad_dom['dominant_role']})</div>
    <hr style="margin:12px 0; border:0; border-top:1px solid #E2E8F0;"/>
    <div style="font-size:13px; color:#1E293B; line-height:1.5;">
        {sd_triad_dom['philosophical_analysis']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        with col_dom2:
            st.markdown("""
    <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; padding:16px;">
    <h4 style="margin:0 0 10px 0; color:#0F172A;">🧘 त्रि-शरीर सामंजस्य मीमांसा</h4>
    <ul style="font-size:13px; color:#334155; line-height:1.6; padding-left:18px; margin:0;">
        <li><b>स्थूल शरीर (Deha - Lagna):</b> बाह्य शारीरिक स्वास्थ्य, रूप-रंग, ऊर्जा व संसार में कर्म का प्रत्यक्ष माध्यम।</li>
        <li><b>सूक्ष्म शरीर (Mana - Moon):</b> अंतःकरण, मानसिक एकाग्रता, भावनाएं, सुख-दुःख की अनुभूति व इच्छाशक्ति।</li>
        <li><b>कारण शरीर (Atma - Sun):</b> शुद्ध चेतना, आत्मिक संकल्प, प्रारब्ध का मूल स्रोत व ईश्वरीय अंश।</li>
    </ul>
    <div style="font-size:12px; background:#EFF6FF; border-radius:6px; padding:10px; margin-top:12px; color:#1E40AF;">
        जब तीनों चक्रों में सामंजस्य होता है, तो व्यक्ति जो सोचता है (मन), वही संकल्प लेता है (आत्मा) और वही कर्म करता है (देह)—यह जीवन में पूर्ण सिद्धि का मार्ग है।
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 8: CLASSICAL SHLOKAS & PRINCIPLES
    # -------------------------------------------------------------------------
    with tab_sd8:
        st.markdown("### 📜 बृहत्पाराशर होराशास्त्र अध्याय ७४ शास्त्रीय प्रमाण (BPHS Shlokas)")
        st.write("महर्षि पाराशर द्वारा सुदर्शन चक्राध्याय (अध्याय ७४) में वर्णित प्रामाणिक श्लोक, अन्वय एवं भावार्थ:")

        shlokas_data = engine_sd.get_classical_shlokas()
        for item in shlokas_data:
            st.markdown(f"""
    <div style="background:#FFFDF7; border:1.5px solid #F59E0B; border-radius:10px; padding:16px; margin-bottom:14px; box-shadow:0 2px 6px rgba(245,158,11,0.06);">
    <div style="font-size:16px; font-weight:900; color:#92400E; margin-bottom:8px;">{item['title']}</div>
    <div style="background:#FEF3C7; border-left:4px solid #D97706; padding:10px 14px; border-radius:4px; font-family:'Sanskrit Text',serif; font-size:14px; color:#78350F; font-weight:700; line-height:1.6; white-space:pre-line;">
    {item['shloka']}
    </div>
    <div style="font-size:13px; color:#1E293B; margin-top:10px; line-height:1.5;">
        <b>सरल भावार्थ:</b> {item['meaning']}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 9: REMEDIES & KAVACH
    # -------------------------------------------------------------------------
    with tab_sd9:
        st.markdown("### 🪔 श्री सुदर्शन कवच, महामंत्र एवं वैदिक शांति (Sudarshan Remedies)")
        st.write("सुदर्शन चक्र के तीनों चक्रों में विद्यमान दोषों के निवारण हेतु शास्त्रोक्त दिव्य मंत्र, कवच एवं अनुष्ठान:")

        rem_data = engine_sd.get_remedies_catalog()

        st.markdown(f"""
    <div style="background:linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); border:2px solid #F59E0B; border-radius:12px; padding:18px; margin-bottom:16px;">
    <div style="font-size:17px; font-weight:900; color:#92400E;">🕉️ श्री सुदर्शन महामंत्र (अमोघ रक्षा कवच)</div>
    <div style="font-size:13px; color:#78350F; margin-top:4px;">सर्वविघ्न, तांत्रिक बाधा, त्रि-दुःस्थान दोष एवं शत्रु-बाधा विनाशक:</div>
    <div style="background:#FFFFFF; border:1px solid #FCD34D; border-radius:8px; padding:12px; margin:10px 0; font-size:15px; font-weight:800; color:#B45309; text-align:center; line-height:1.6;">
        {rem_data['mahamantra']}
    </div>
    <div style="font-size:12px; color:#92400E;"><b>जप विधि:</b> तुलसी की माला से नित्य १०८ बार अथवा बुधवार/एकादशी को संकल्पपूर्वक जप करें।</div>
    </div>
    """, unsafe_allow_html=True)

        col_rk1, col_rk2 = st.columns(2)
        with col_rk1:
            st.markdown(f"""
    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:15px; font-weight:900; color:#1E40AF;">🔆 श्री सुदर्शन गायत्री मंत्र</div>
    <div style="background:#FFFFFF; border:1px solid #BFDBFE; border-radius:6px; padding:10px; margin:8px 0; font-size:14px; font-weight:800; color:#1D4ED8; text-align:center;">
        {rem_data['gayatri_mantra']}
    </div>
    <div style="font-size:12px; color:#1E3A8A; line-height:1.4;">
        प्रतिदिन प्रातःकाल सूर्योदय के समय पूर्वाभिमुख होकर ११ या २१ बार जप करने से आत्मबल, मेधा शक्ति और दैवीय सुरक्षा चक्र जागृत होता है।
    </div>
    </div>
    """, unsafe_allow_html=True)

        with col_rk2:
            st.markdown(f"""
    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:15px; font-weight:900; color:#065F46;">📜 श्री सुदर्शन अष्टकम् (वेदान्तदेशिक विरचितम्)</div>
    <div style="font-size:12px; color:#065F46; margin-top:4px;">{rem_data['ashtakam_intro']}</div>
    <div style="background:#FFFFFF; border:1px solid #A7F3D0; border-radius:6px; padding:8px; margin:8px 0; font-size:12px; font-weight:700; color:#047857; line-height:1.5; white-space:pre-line;">
    {rem_data['ashtakam_first_verse']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("#### 🛡️ विशिष्ट वैदिक शांति अनुष्ठान")
        col_m1, col_m2 = st.columns(2)
        for i, m in enumerate(rem_data["remedial_measures"]):
            c_target = col_m1 if (i % 2 == 0) else col_m2
            with c_target:
                st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:12px; margin-bottom:10px;">
    <div style="font-size:14px; font-weight:800; color:#0F172A;">{m['title']}</div>
    <div style="font-size:12px; color:#334155; margin-top:4px; line-height:1.4;">{m['procedure']}</div>
    </div>
    """, unsafe_allow_html=True)


    # =============================================================
    # TAB 15: VARSHAPHAL (TAJIKA ANNUAL SOLAR RETURN)

