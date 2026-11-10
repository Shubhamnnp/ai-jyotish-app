import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import importlib
import src.jyotish.services.varshaphal as varshaphal
from src.jyotish.services.varshaphal import default_varshaphal_service
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.sudarshan import SIGN_NAMES_HI, PLANET_NAMES_HI
from src.jyotish.ui.chart_renderer import ChartRenderer

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def render_chart_svg_default(c_obj, chart_title, varga_code="D1"):
    chart_style = st.session_state.get("chart_style", "North Indian")
    if "South" in chart_style:
        return ChartRenderer.render_south_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    elif "East" in chart_style:
        return ChartRenderer.render_east_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    return ChartRenderer.render_north_indian_svg(c_obj, title=chart_title, varga_code=varga_code)

def render_varshaphal_view(chart, birth_profile, tz_offset=5.5, render_chart_svg_fn=None, tabs=None):
    if render_chart_svg_fn is None:
        render_chart_svg_fn = render_chart_svg_default
    render_chart_svg = render_chart_svg_fn
    
    if tabs is None or len(tabs) < 10:
        tabs = [
            "🌟 वर्ष कुण्डली (D1)",
            "🎯 मुन्था विचार",
            "👑 वर्षेश चयन",
            "⚖️ पंचवर्गीय व हर्ष बल",
            "⚡ १६ ताजिक योग",
            "💫 ३६ ताजिक सहम",
            "⏳ मुद्धा व योगिनी दशा",
            "📊 १२ भाव वर्षफल",
            "🗓️ मासफल (१२ मास)",
            "🪔 वर्षेश शांति उपाय"
        ]
    st.subheader("📅 वर्षफल / ताजिक वार्षिक चक्र (Tajika Annual Solar Return)")
    st.write("ताजिक नीलकण्ठी एवं हायन रत्न अनुसार वार्षिक सौर वापसी कुण्डली, मुन्था विचार, पंचाधिकारी वर्षेश निर्णय, पंचवर्गीय व हर्ष बल, १६ ताजिक योग, २८ सहम एवं १-वर्षीय मुद्धा दशा चक्र।")

    # Classical Shastriya Shloka Card
    tajika_neelakanthi_shloka = {
        "title": "ताजिक नीलकण्ठी — वर्ष लग्न, मुन्था एवं वर्षेश निर्णय",
        "source": "नीलकण्ठ दैवज्ञ विरचित 'ताजिक नीलकण्ठी' (वर्षतंत्र)",
        "shloka": "सूर्यस्य संक्रमणकाले यल्लग्नं समुदेति तत्।\nवर्षलग्नमिति ख्यातं ताजिके शास्त्रसंमतम्॥\nपञ्चाधिकारिसम्पन्नो वर्षेशो यत्र संस्थितः।\nमुन्था च शुभसंयुक्ता तद्वर्षं शुभदायकम्॥",
        "meaning": "जब सूर्य ठीक अपने जन्मकालीन स्पष्ट भोग (अंश व कला) पर पुनः आता है, उस सौर क्रांति वेला उदित होने वाला लग्न 'वर्ष लग्न' कहलाता है। पंचाधिकारियों (मुन्थाधिपति, जन्म लग्नेश, वर्ष लग्नेश, त्रिराशीश, दिन/रात्रि पति) में सर्वाधिक बलवान् ग्रह 'वर्षेश' निर्धारित होता है। वर्षेश एवं मुन्था की शुभ स्थिति वर्ष को सर्वतोमुखी ऐश्वर्य, पदोन्नति व कार्यसिद्धि प्रदान करती है।"
    }
    with st.expander(f"📜 शास्त्रीय प्रमाण — {tajika_neelakanthi_shloka['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {tajika_neelakanthi_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{tajika_neelakanthi_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {tajika_neelakanthi_shloka['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    from src.jyotish.services import varshaphal
    service_vp = getattr(varshaphal, "default_varshaphal_service", default_varshaphal_service)

    col_vy1, col_vy2 = st.columns([1.5, 2.5])
    with col_vy1:
        v_year = st.number_input("वर्ष चयन करें (Target Year)", value=get_live_local_now(tz_offset).year, min_value=1900, max_value=2100, step=1)
    with col_vy2:
        st.write("")
        st.caption(f"📍 जातक: **{birth_profile.name}** | जन्म वर्ष: **{birth_profile.birth_date.year}** (पूर्ण वर्ष आयु: **{max(0, int(v_year) - birth_profile.birth_date.year)}** वर्ष)")

    vp_res = service_vp.calculate_varshaphal(chart, int(v_year))

    # Top Hero KPI Banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #0D9488 100%); border-radius:12px; padding:18px 24px; color:#FFFFFF; margin-bottom:16px; box-shadow:0 4px 14px rgba(37,99,235,0.18);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
            <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; opacity:0.85;">ताजिक नीलकण्ठी वार्षिक चक्र • सौर क्रांति वेला</div>
            <div style="font-size:22px; font-weight:900; margin-top:4px;">☀️ सौर वापसी: {vp_res['solar_return_datetime']}</div>
            <div style="font-size:13px; opacity:0.92; margin-top:4px;">वर्ष लग्न: {vp_res['varsha_lagna_hi']} ({vp_res['varsha_lagna_degree']}°) | वर्षेश: {vp_res['varshesha_hi']} ({vp_res['varshesha']})</div>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:16px; font-weight:900;">{vp_res['muntha_sign_hi']}</div>
                <div style="font-size:11px; font-weight:700;">🎯 मुन्था ({vp_res['muntha_house']} भाव)</div>
            </div>
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:16px; font-weight:900;">👑 {vp_res['varshesha_hi']}</div>
                <div style="font-size:11px; font-weight:700;">वर्षेश अधिपति</div>
            </div>
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:16px; font-weight:900;">{vp_res['annual_score']}/100</div>
                <div style="font-size:11px; font-weight:700;">समग्र वार्षिक स्कोर</div>
            </div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Active Native Micro-Planetary Longitudes & Live Varshaphal Console
    nl_deg = getattr(chart, "lagna_degree", 0.0)
    nl_ansh = int(nl_deg)
    nl_kala = int(round((nl_deg - nl_ansh) * 60.0))
    if nl_kala >= 60:
        nl_kala = 0
        nl_ansh += 1
    nl_dms = f"{nl_ansh}° {nl_kala:02d}'"

    vl_deg = float(vp_res.get("varsha_lagna_degree", 0.0))
    vl_ansh = int(vl_deg)
    vl_kala = int(round((vl_deg - vl_ansh) * 60.0))
    if vl_kala >= 60:
        vl_kala = 0
        vl_ansh += 1
    vl_dms = f"{vl_ansh}° {vl_kala:02d}'"

    sun_natal = chart.planets.get("Sun")
    if sun_natal:
        sn_deg = getattr(sun_natal, "sign_degree", 0.0)
        sn_ansh = int(sn_deg)
        sn_kala = int(round((sn_deg - sn_ansh) * 60.0))
        if sn_kala >= 60:
            sn_kala = 0
            sn_ansh += 1
        sn_dms = f"{sn_ansh}° {sn_kala:02d}'"
        sn_nak = getattr(sun_natal, "nakshatra_name", getattr(sun_natal, "nakshatra", "—"))
        sn_pada = getattr(sun_natal, "nakshatra_pada", getattr(sun_natal, "pada", 1))
        sun_str = f"{sun_natal.sign_name} {sn_dms} [{sn_nak}-P{sn_pada}]"
    else:
        sn_dms = "—"
        sun_str = "—"

    c_vp1, c_vp2, c_vp3, c_vp4 = st.columns(4)
    c_vp1.metric("जन्म लग्न बनाम वर्ष लग्न", f"{vp_res['varsha_lagna_hi']} ({vl_dms})", f"जन्म: {SIGN_NAMES_HI[chart.lagna_sign_id - 1]} ({nl_dms})")
    c_vp2.metric("सौर क्रांति वेला (सूर्य भोग)", f"{sn_dms}", f"☀️ {sun_str.split(' ')[-1]}")
    c_vp3.metric("वर्षेश एवं मुन्था स्थिति", f"👑 {vp_res['varshesha_hi']}", f"मुन्था: भाव #{vp_res['muntha_house']} ({vp_res['muntha_sign_hi']})")
    c_vp4.metric("वार्षिक स्कोर व काल बलि", f"{vp_res['annual_score']}/100", f"{'दिवा बलि सूर्य' if vp_res['is_day_return'] else 'रात्रि बलि चन्द्र'}")

    tab_vp1, tab_vp2, tab_vp3, tab_vp4, tab_vp5, tab_vp6, tab_vp7, tab_vp8, tab_vp9, tab_vp10 = st.tabs(tabs)

    # -------------------------------------------------------------------------
    # TAB 1: VARSHA D1 CHART
    # -------------------------------------------------------------------------
    with tab_vp1:
        col_vch1, col_vch2 = st.columns([1.2, 1.8])
        with col_vch1:
            st.markdown("#### 🌟 वार्षिक कुण्डली (Varsha D1 Chart)")
            varsha_svg = render_chart_svg(vp_res["varsha_chart"], f"वर्ष कुण्डली {v_year} (D1)")
            clean_varsha_svg = "\n".join(l.strip() for l in varsha_svg.splitlines() if l.strip() and not (l.strip().startswith("<!--") and l.strip().endswith("-->")))
            st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin:0 auto;">{clean_varsha_svg}</div>', unsafe_allow_html=True)
            st.caption(f"☀️ सौर क्रांति वेला: **{vp_res['solar_return_datetime']}** | **{'दिवा सौर वापसी (Day Return)' if vp_res['is_day_return'] else 'रात्रि सौर वापसी (Night Return)'}**")

        with col_vch2:
            st.markdown("#### 🪐 वर्ष कुण्डली ग्रह स्पष्ट स्थिति (Planetary Positions)")
            v_planets_data = []
            for p_k, p_pos in vp_res["varsha_chart"].planets.items():
                p_hi = PLANET_NAMES_HI.get(p_k, p_k)
                r_hi = SIGN_NAMES_HI[p_pos.sign_id - 1]
                p_deg = getattr(p_pos, "sign_degree", 0.0)
                p_ansh = int(p_deg)
                p_kala = int(round((p_deg - p_ansh) * 60.0))
                if p_kala >= 60:
                    p_kala = 0
                    p_ansh += 1
                p_dms = f"{p_ansh}° {p_kala:02d}'"
                p_nak = getattr(p_pos, "nakshatra_name", getattr(p_pos, "nakshatra", "—"))
                p_pada = getattr(p_pos, "nakshatra_pada", getattr(p_pos, "pada", "—"))
                swabhav_str = "नैसर्गिक शुभ" if p_k in ["Jupiter", "Venus", "Mercury", "Moon"] else "नैसर्गिक क्रूर"

                v_planets_data.append({
                    "ग्रह (Graha)": p_hi,
                    "नैसर्गिक स्वभाव": swabhav_str,
                    "राशि (Sign)": f"{r_hi} ({p_pos.sign_name})",
                    "अंश-कला (DMS)": p_dms,
                    "नक्षत्र एवं चरण": f"{p_nak} (चरण {p_pada})",
                    "भाव (House)": f"{p_pos.house_from_lagna} भाव",
                    "गरिमा (Dignity)": p_pos.dignity.capitalize(),
                    "गति (Motion)": "⚡ वक्री (R)" if p_pos.is_retrograde else "मार्गी"
                })
            st.dataframe(pd.DataFrame(v_planets_data), use_container_width=True, hide_index=True)

            st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px; margin-top:12px;">
    <div style="font-size:14px; font-weight:800; color:#0F172A;">⚖️ जन्म लग्न बनाम वर्ष लग्न संबंध</div>
    <div style="font-size:12px; color:#334155; margin-top:6px; line-height:1.5;">
        • <b>जन्म लग्न:</b> {SIGN_NAMES_HI[chart.lagna_sign_id - 1]} ({chart.lagna_sign_name}) | <b>वर्ष लग्न:</b> {vp_res['varsha_lagna_hi']} ({vp_res['varsha_lagna']})<br/>
        • <b>वर्ष लग्नेश:</b> {vp_res['varsha_lagna_lord_hi']} ({vp_res['varsha_lagna_lord']})<br/>
        • <b>वार्षिक काल-अधिपति:</b> {'दिवा बलि सूर्य' if vp_res['is_day_return'] else 'रात्रि बलि चन्द्रमा'}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: MUNTHA PROGRESSION
    # -------------------------------------------------------------------------
    with tab_vp2:
        st.markdown("### 🎯 मुन्था विचार एवं वार्षिक प्रभाव (Muntha Progression)")
        st.write("ताजिक ज्योतिष में मुन्था को 'वार्षिक लग्न' की भांति सर्वाधिक प्रभावी माना गया है। मुन्था प्रति वर्ष १ राशि (३० अंश) आगे बढ़ती है।")

        mun_shl = SHASTRIYA_SHLOKAS.get("tajika_muntha_varshesha", {})
        if mun_shl:
            mun_lines = "<br/>".join(mun_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(37, 99, 235, 0.08); border-left: 4px solid #2563EB; padding: 14px 18px; border-radius: 8px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #1D4ED8; font-size: 13.5px; margin-bottom: 4px;">📖 {mun_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {mun_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {mun_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {mun_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("मुन्था राशि", f"{vp_res['muntha_sign_hi']}", f"वर्ष कुण्डली में {vp_res['muntha_house']} भाव")
        c_m2.metric("मुन्था पति (Lord)", f"👑 {vp_res['muntha_lord_hi']}", "मुन्था राशि अधिपति")
        c_m3.metric("जन्म कुण्डली में भाव", f"{vp_res['muntha_house_natal']} भाव", "मूल जन्म लग्न से स्थिति")

        m_bg = "#ECFDF5" if vp_res['muntha_house'] in (1, 2, 3, 5, 9, 10, 11) else ("#FFFBEB" if vp_res['muntha_house'] in (4, 6, 7) else "#FFF1F2")
        m_bd = "#10B981" if vp_res['muntha_house'] in (1, 2, 3, 5, 9, 10, 11) else ("#F59E0B" if vp_res['muntha_house'] in (4, 6, 7) else "#F43F5E")
        st.markdown(f"""
    <div style="background:{m_bg}; border:1.5px solid {m_bd}; border-radius:10px; padding:18px; margin:14px 0;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:16px; font-weight:900; color:#0F172A;">{vp_res['muntha_fruit_title']} ({vp_res['muntha_sign_hi']} राशि)</span>
        <span style="font-size:13px; font-weight:800; background:#FFFFFF; border:1px solid {m_bd}; padding:3px 10px; border-radius:6px;">{vp_res['muntha_verdict']}</span>
    </div>
    <div style="font-size:13px; color:#1E293B; margin-top:10px; line-height:1.6;">
        📜 <b>ताजिक नीलकण्ठी प्रमाण:</b> {vp_res['muntha_fruit_desc']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("""
    #### 📜 मुन्था फलित के शास्त्रीय नियम:
    * **शुभ भाव (१, २, ३, ५, ९, १०, ११):** मुन्था इन भावों में स्थित होने पर वर्ष भर राज्य कृपा, धन लाभ, आरोग्यता, पदोन्नति एवं सुख-समृद्धि प्रदान करती है।
    * **मध्यम भाव (४, ७):** चतुर्थ भाव में गृह-चिंता एवं माता के स्वास्थ्य पर ध्यान देना होता है; सप्तम में दांपत्य व साझेदारी में सतर्कता अपेक्षित है।
    * **अनिष्ट भाव (६, ८, १२):** इन भावों में मुन्था 'रोग, शत्रु, ऋण, मानसिक उद्वेग या व्यय' की वृद्धि करती है। इसके लिए ताजिक शांति विधान अनिवार्य है।
    """)

    # -------------------------------------------------------------------------
    # TAB 3: PANCHADHIKARI VARSHESHA
    # -------------------------------------------------------------------------
    with tab_vp3:
        st.markdown("### 👑 पंचाधिकारी वर्षेश चयन सारणी (5 Panchadhikari Candidates)")
        st.write("ताजिक नीलकण्ठी अनुसार वर्ष के 'राजा' (वर्षेश) का चुनाव इन ५ दावेदार ग्रहों के बल, स्थिति और वर्ष लग्न पर दृष्टि के आधार पर किया जाता है:")

        st.dataframe(pd.DataFrame(vp_res["varshesha_candidates_scored"]), use_container_width=True, hide_index=True)

        st.markdown(f"""
    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:16px; margin-top:14px;">
    <div style="font-size:17px; font-weight:900; color:#1E40AF;">🏆 वर्ष {v_year} के वर्षेश: {vp_res['varshesha_hi']} ({vp_res['varshesha']})</div>
    <div style="font-size:13px; color:#1E293B; margin-top:6px; line-height:1.5;">
        पंचाधिकारी नियमों के अनुसार सर्वाधिक गरिमा, भाव स्थिति एवं वर्ष लग्न पर शुभ प्रभाव के कारण <b>{vp_res['varshesha_hi']}</b> इस वर्ष के सर्वोच्च शासक (Lord of the Year) घोषित किए गए हैं। वर्ष के मुख्य परिणाम इस ग्रह की स्थिति से नियंत्रित होंगे।
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 4: PANCHAVARGIYA & HARSHA BALA
    # -------------------------------------------------------------------------
    with tab_vp4:
        st.markdown("### ⚖️ पंचवर्गीय बल एवं हर्ष बल (Panchavargiya & Harsha Bala)")
        st.write("ताजिक ज्योतिष में ग्रहों के सामर्थ्य और शुभ फल देने की क्षमता का आकलन पंचवर्गीय बल (०-२० विश्वा) एवं हर्ष बल (०-२० बिंदु) से किया जाता है:")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("#### 📊 पंचवर्गीय बल (Panchavargiya Bala - 20 Vishopakas)")
            pv_tbl = []
            for r in vp_res.get("panchavargiya_bala", []):
                pv_tbl.append({
                    "ग्रह": r["planet_hi"],
                    "क्षेत्र (30)": r["kshetra"],
                    "उच्च (20)": r["uccha"],
                    "हद्द (15)": r["hadda"],
                    "द्रेष्काण (10)": r["drekkana"],
                    "नवांश (5)": r["navamsha"],
                    "विश्वा (20)": f"{r['vishopaka']} / 20",
                    "स्थिति": r["status"]
                })
            st.dataframe(pd.DataFrame(pv_tbl), use_container_width=True, hide_index=True)

        with col_b2:
            st.markdown("#### 🌸 हर्ष बल (Harsha Bala - 20 Points of Joy)")
            hb_tbl = []
            for r in vp_res.get("harsha_bala", []):
                hb_tbl.append({
                    "ग्रह": r["planet_hi"],
                    "स्थान (5)": r["sthana"],
                    "स्वक्षेत्र (5)": r["swakshetra"],
                    "राशि (5)": r["rashi"],
                    "काल (5)": r["kala"],
                    "कुल बिंदु": f"{r['total']} / 20",
                    "हर्ष स्तर": r["status"]
                })
            st.dataframe(pd.DataFrame(hb_tbl), use_container_width=True, hide_index=True)

        st.caption("💡 **हर्ष बल नियम:** स्थान (निर्धारित भाव), स्वक्षेत्र/उच्च, स्त्री/पुरुष राशि एवं दिन/रात्रि काल में बलिष्ठता। २० में से १५+ अंक पूर्ण हर्ष को दर्शाते हैं।")

    # -------------------------------------------------------------------------
    # TAB 5: 16 TAJIKA YOGAS
    # -------------------------------------------------------------------------
    with tab_vp5:
        st.markdown("### ⚡ १६ ताजिक योग एवं दृष्टि चक्र (16 Tajika Yogas)")
        st.write("ताजिक ज्योतिष में ग्रहों के दीप्तांश (Orbs) एवं गति के आधार पर निर्मित होने वाले १६ शास्त्रीय योग:")

        yogas_tbl = []
        for yg in vp_res.get("all_tajika_yogas", []):
            yogas_tbl.append({
                "योग नाम": yg["name"],
                "संबद्ध ग्रह": yg["pair"],
                "विषय": yg["label"],
                "प्रकृति": yg["nature"],
                "दीप्तांश": yg["orb"],
                "फलित विवरण": yg["effect"]
            })
        st.dataframe(pd.DataFrame(yogas_tbl), use_container_width=True, hide_index=True)

        st.markdown("""
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px; margin-top:14px;">
    <div style="font-size:14px; font-weight:800; color:#0F172A;">👁️ ताजिक दृष्टि नियम (Aspect Rules):</div>
    <div style="font-size:12px; color:#334155; margin-top:6px; line-height:1.6;">
        • <b>प्रत्यक्ष मित्र दृष्टि (५, ९ भाव):</b> पूर्ण सहयोग, सौहार्द एवं निर्बाध कार्य सिद्धि।<br/>
        • <b>गुप्त मित्र दृष्टि (३, ११ भाव):</b> परोक्ष सहयोग, अप्रत्यक्ष लाभ एवं सामंजस्य।<br/>
        • <b>प्रत्यक्ष शत्रु दृष्टि (१, ४, ७, १० भाव):</b> खुला संघर्ष, प्रतिस्पर्धा व कड़े प्रयास।<br/>
        • <b>तटस्थ / उदासीन (२, ६, ८, १२ भाव):</b> कोई प्रत्यक्ष ताजिक दृष्टि संबंध नहीं।
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 6: 36 TAJIKA SAHAMS
    # -------------------------------------------------------------------------
    with tab_vp6:
        st.markdown("### 💫 ताजिक सहम मण्डल (Canonical Tajika Sahams)")
        st.write("सहम वर्ष कुण्डली में विभिन्न जीवन क्षेत्रों (धन, कर्म, विवाह, विद्या, यश) के अत्यंत संवेदनशील गणितीय बिंदु हैं:")

        c_sh1, c_sh2 = st.columns([1.5, 2.5])
        with c_sh1:
            sel_saham_cat = st.selectbox(
                "सहम श्रेणी फ़िल्टर करें:",
                options=["सभी सहम (All Sahams)", "शुभ व ऐश्वर्य", "धन व लाभ", "कर्म व व्यवसाय", "विद्या व बुद्धि", "संबंध व दांपत्य", "स्वास्थ्य व आयु", "सावधानी / बाधा"]
            )
        with c_sh2:
            st.write("")
            st.caption("📍 दिन की सौर वापसी में सूर्य-चन्द्र एवं रात्रि में चन्द्र-सूर्य सूत्रों का स्वतः संशोधन किया गया है।")

        all_sahams = vp_res.get("sahams", [])
        if sel_saham_cat != "सभी सहम (All Sahams)":
            filtered_sahams = [s for s in all_sahams if s.get("category") == sel_saham_cat]
        else:
            filtered_sahams = all_sahams

        st.dataframe(pd.DataFrame(filtered_sahams), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 7: ANNUAL DASHAS (MUDDA & YOGINI)
    # -------------------------------------------------------------------------
    with tab_vp7:
        st.markdown("### ⏳ वार्षिक दशा प्रणालियाँ (Mudda Vimshottari & Yogini Dashas)")
        st.write("सौर वर्ष (३६५.२५ दिन) के सूक्ष्म काल-विभाजन हेतु मुद्धा विंशोत्तरी एवं मुद्धा योगिनी दशा चक्र:")

        mud_shl = SHASTRIYA_SHLOKAS.get("mudda_dasha_pramana", {})
        if mud_shl:
            mud_lines = "<br/>".join(mud_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(147, 51, 234, 0.08); border-left: 4px solid #9333EA; padding: 14px 18px; border-radius: 8px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #7E22CE; font-size: 13.5px; margin-bottom: 4px;">📖 {mud_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {mud_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {mud_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {mud_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        c_md1, c_md2 = st.columns(2)
        with c_md1:
            st.markdown("#### 🗓️ १-वर्षीय मुद्धा विंशोत्तरी दशा (Mudda Vimshottari)")
            m_v_tbl = []
            for r in vp_res.get("mudda_dasha_full", []):
                m_v_tbl.append({
                    "दशेश ग्रह": r.get("lord_hi", r["lord"]),
                    "आरंभ": r["start_date"],
                    "समाप्ति": r["end_date"],
                    "अवधि (दिन)": f"{r['duration_days']} दिन",
                    "स्थिति": r.get("status", "—")
                })
            st.dataframe(pd.DataFrame(m_v_tbl), use_container_width=True, hide_index=True)

        with c_md2:
            st.markdown("#### 🌸 १-वर्षीय मुद्धा योगिनी दशा (Mudda Yogini)")
            m_y_tbl = []
            for r in vp_res.get("mudda_yogini_dasha", []):
                m_y_tbl.append({
                    "योगिनी": r["yogini"],
                    "आरंभ": r["start_date"],
                    "समाप्ति": r["end_date"],
                    "अवधि (दिन)": f"{r['duration_days']} दिन",
                    "स्थिति": r["status"]
                })
            st.dataframe(pd.DataFrame(m_y_tbl), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 8: 12 BHAVAS ANNUAL FORECAST
    # -------------------------------------------------------------------------
    with tab_vp8:
        st.markdown("### 📊 द्वादश भाव वार्षिक फलित (12 Bhavas Annual Forecast)")
        st.write("वर्ष कुण्डली के द्वादश भावों का भावेश, स्थित ग्रह, मुन्था एवं वर्षेश की दृष्टि से समन्वित वार्षिक फल:")

        bh_tbl = []
        for b in vp_res.get("bhavas_forecast", []):
            bh_tbl.append({
                "भाव": b["house_num"],
                "भाव विवरण": b["house_name"].split("(")[0].strip(),
                "राशि": f"{b['sign_hi']} ({b['lord_hi']})",
                "स्थित ग्रह": b["occupants_str"],
                "मुन्था स्थिति": "🎯 मुन्था स्थित" if b["is_muntha"] else "—",
                "वर्षेश स्थिति": "👑 वर्षेश स्थित" if b["is_varshesha_here"] else "—",
                "स्कोर": f"{b['score']}/100",
                "कोटि": b["status"]
            })
        st.dataframe(pd.DataFrame(bh_tbl), use_container_width=True, hide_index=True)

        st.markdown("#### 🔍 भाव-वार वार्षिक परामर्श:")
        for b in vp_res.get("bhavas_forecast", []):
            with st.expander(f"{b['house_name']} — {b['status']} ({b['score']}/100)"):
                st.write(f"• **राशि व भावेश:** {b['sign_hi']} (स्वामी: {b['lord_hi']})")
                st.write(f"• **स्थित ग्रह:** {b['occupants_str']}")
                if b["is_muntha"]:
                    st.info(f"🎯 **मुन्था इस भाव में स्थित है:** {vp_res['muntha_fruit_desc']}")
                if b["is_varshesha_here"]:
                    st.success(f"👑 **वर्षेश {vp_res['varshesha_hi']} इस भाव में स्थित हैं:** इस भाव से संबंधित कार्यों में अभूतपूर्व प्रगति होगी।")

    # -------------------------------------------------------------------------
    # TAB 9: 12 MONTHLY SOLAR PROGRESSIONS (MAASAPHALA)
    # -------------------------------------------------------------------------
    with tab_vp9:
        st.markdown("### 🗓️ १२ मास प्रवेश व मासिक कालचक्र (Maasa Pravesha)")
        st.write("सौर वर्ष के १२ महीनों में सूर्य की ३०-अंश क्रांति पर आधारित मासिक कालचक्र एवं मुन्था की मासिक गति (२.५° प्रति माह):")

        st.dataframe(pd.DataFrame(vp_res.get("maasa_pravesha_timeline", [])), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 10: REMEDIES & SHANTI
    # -------------------------------------------------------------------------
    with tab_vp10:
        st.markdown("### 🪔 वर्षेश शांति, मुन्था दोष परिहार व ताजिक उपाय (Annual Remedies)")
        st.write("वर्ष भर अनिष्ट ग्रहों के शमन, वर्षेश की कृपा प्राप्ति एवं मुन्था दोष निवारण हेतु शास्त्रोक्त उपाय:")

        rem = vp_res.get("remedies", {})

        st.markdown(f"""
    <div style="background:linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); border:2px solid #F59E0B; border-radius:12px; padding:18px; margin-bottom:16px;">
    <div style="font-size:17px; font-weight:900; color:#92400E;">👑 वर्षेश {rem.get('varshesha_hi', '')} की कृपा हेतु महामंत्र</div>
    <div style="background:#FFFFFF; border:1px solid #FCD34D; border-radius:8px; padding:12px; margin:10px 0; font-size:16px; font-weight:800; color:#B45309; text-align:center;">
        {rem.get('varshesha_mantra', '')}
    </div>
    <div style="font-size:12px; color:#92400E; line-height:1.5;">
        • <b>यंत्र / रत्न:</b> {rem.get('varshesha_ratna', '')}<br/>
        • <b>वार्षिक दान सामग्री:</b> {rem.get('varshesha_dana', '')}<br/>
        • <b>जप निर्देश:</b> प्रतिदिन प्रातः अथवा वर्षेश के वार को १०८ बार जप करें।
    </div>
    </div>
    """, unsafe_allow_html=True)

        col_vr1, col_vr2 = st.columns(2)
        with col_vr1:
            st.markdown(f"""
    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:15px; font-weight:900; color:#1E40AF;">🎯 मुन्था दोष शांति विधान</div>
    <div style="font-size:13px; color:#1E3A8A; margin-top:8px; line-height:1.5;">
        {rem.get('muntha_parihara', '')}
    </div>
    </div>
    """, unsafe_allow_html=True)

        with col_vr2:
            st.markdown(f"""
    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:15px; font-weight:900; color:#065F46;">☀️ आदित्य हृदय स्तोत्र पाठ</div>
    <div style="font-size:13px; color:#065F46; margin-top:8px; line-height:1.5;">
        {rem.get('aditya_hridaya', '')}
    </div>
    </div>
    """, unsafe_allow_html=True)


    # =============================================================
    # TAB 13: BIRTH TIME RECTIFICATION (BTR) - ADVANCED SUITE
    # =============================================================

