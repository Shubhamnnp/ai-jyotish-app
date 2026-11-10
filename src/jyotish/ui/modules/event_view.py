import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
import importlib

from src.jyotish.core.models import GhatnaQueryInput
from src.jyotish.events.past_verification import default_past_event_engine, PastEventVerificationInput, AstrologicalEvidenceStatus
from src.jyotish.services.event_query import default_event_query_service
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def render_event_view(chart, birth_profile, tz_offset=5.5, tabs=None):
    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark

    if tabs is None:
        tabs = [
            '🔮 भविष्य घटना पूर्वानुमान',
            '🔍 भूतकाल घटना सत्यापन'
        ]
    st.subheader("🎯 घटना विश्लेषण एवं काल सत्यापन (Event Analysis & Verification)")

    # Classical Shastriya Shloka Card
    phaladeepika_event_shloka = {
        "title": "फलदीपिका एवं जातक पारिजात — दशा-गोचर काल विधान",
        "source": "मन्त्रेश्वर विरचित फलदीपिका (अध्याय २०) एवं जातक पारिजात",
        "shloka": "यद्भावे यत्फलं प्रोक्तं तत्तत्समये समुपस्थिते।\nदशानाथानुसारेण गोचरेण विचारयेत्॥\nगुरुणा शनिना युक्ते दृष्टे वा भावसंस्थिते।\nतदा फलस्य संसिद्धिः प्रोक्ता दैवज्ञसम्मतैः॥",
        "meaning": "कुण्डली में जिस भाव का जो फल शास्त्रों में कहा गया है, वह तभी घटित होता है जब दशानाथ अनुकूल हो तथा गोचर में देवगुरु बृहस्पति एवं मन्द शनि का शुभ दृष्टि/युति संबंध बने। दशा और गोचर के त्रिबल संयोग से ही काल-निर्णय प्रामाणिक होता है।"
    }
    with st.expander(f"📜 शास्त्रीय प्रमाण — {phaladeepika_event_shloka['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {phaladeepika_event_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{phaladeepika_event_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {phaladeepika_event_shloka['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Active Native Micro-Planetary Longitudes & DMS Console
    lagna_sname = getattr(chart, "lagna_sign_name", "Aries")
    moon = chart.planets.get("Moon")
    jup = chart.planets.get("Jupiter")
    sat = chart.planets.get("Saturn")
    
    with st.expander("🪐 सक्रिय जातक खगोलीय स्थिति एवं मुख्य ग्रह निर्देशांक (Native Key Planets HUD)", expanded=False):
        c_ev1, c_ev2, c_ev3, c_ev4 = st.columns(4)
        c_ev1.metric("लग्न एवं राशि", f"{lagna_sname}", f"चन्द्र: {moon.sign_name if moon else '—'}")
        c_ev2.metric("आत्मकारक ग्रह", f"{getattr(chart, 'atmakaraka', '—')}", "मूल स्वभाव")
        if jup:
            _j_sdeg = getattr(jup, 'sign_degree', 0.0)
            _j_ansh = int(_j_sdeg)
            _j_kala = int(round((_j_sdeg - _j_ansh) * 60.0))
            if _j_kala >= 60: _j_kala = 0; _j_ansh += 1
            _j_nak = getattr(jup, 'nakshatra_name', '')[:4]
            _j_pad = getattr(jup, 'nakshatra_pada', 1)
            c_ev3.metric("गुरु स्थिति", f"{jup.sign_name} ({_j_ansh}° {_j_kala:02d}')", f"{jup.house_from_lagna} भाव | {_j_nak}-P{_j_pad}")
        if sat:
            _s_sdeg = getattr(sat, 'sign_degree', 0.0)
            _s_ansh = int(_s_sdeg)
            _s_kala = int(round((_s_sdeg - _s_ansh) * 60.0))
            if _s_kala >= 60: _s_kala = 0; _s_ansh += 1
            _s_nak = getattr(sat, 'nakshatra_name', '')[:4]
            _s_pad = getattr(sat, 'nakshatra_pada', 1)
            c_ev4.metric("शनि स्थिति", f"{sat.sign_name} ({_s_ansh}° {_s_kala:02d}')", f"{sat.house_from_lagna} भाव | {_s_nak}-P{_s_pad}")

    tab_future_event, tab_past_event = st.tabs(tabs)

    with tab_future_event:
        with st.expander("⚙️ भविष्य घटना पूर्वानुमान पैरामीटर्स एवं विषय चयन (Event Forecast Query Controls)", expanded=True):
            st.write("अपनी कुण्डली के लिए किसी भी भविष्य की तिथि अथवा समयावधि का ३-स्तरीय शास्त्रीय ट्रिगर (दशा, गुरु-शनि दोहरा गोचर, अष्टकवर्ग) एवं ३२-शास्त्रीय नियमों द्वारा वैज्ञानिक विश्लेषण प्राप्त करें।")

            scan_mode = st.radio(
                "विश्लेषण प्रारूप चयन करें (Analysis Mode):",
                ["📈 १२-२४ माह सम्भावना क्षितिज (12-24 Month Horizon Scanner)", "🎯 एकल तिथि गहन वेध (Single Date Deep Dive)"],
                horizontal=True,
                key="ghatna_scan_mode_rad"
            )

            col_q1, col_q2, col_q3 = st.columns([2, 2, 2])
            theme = col_q1.selectbox(
                "विश्लेषण विषय (Event Theme)",
                ["career", "marriage", "wealth", "children", "property", "travel", "health", "spirituality", "all"],
                format_func=lambda x: {
                    "career": "💼 आजीविका / नौकरी / पदोन्नति (Career)",
                    "marriage": "💍 विवाह / संबंध (Marriage)",
                    "wealth": "💰 धन / संचित वैभव (Wealth)",
                    "children": "👶 संतान प्राप्ति / विद्या (Children)",
                    "property": "🏠 भूमि / भवन / वाहन क्रय (Property)",
                    "travel": "✈️ विदेश गमन / दूरस्थ यात्रा (Travel)",
                    "health": "🌿 स्वास्थ्य एवं जीवनी शक्ति (Health)",
                    "spirituality": "🕉️ आध्यात्म एवं साधना (Spirituality)",
                    "all": "🌐 समग्र जीवन चक्र (All Themes)"
                }.get(x, x),
                key="ghatna_theme_sel"
            )

            if "12-24" in scan_mode:
                with col_q2:
                    start_range_date = st.date_input("प्रारंभ तिथि (Start Date)", value=get_live_local_now(tz_offset).date(), format="DD/MM/YYYY", key="ghatna_start_d")
                with col_q3:
                    months_horizon = st.selectbox("अवधि क्षितिज (Horizon)", [12, 18, 24], index=0, format_func=lambda x: f"{x} माह ({x//12} वर्ष)", key="ghatna_horizon_m")
            else:
                with col_q2:
                    target_event_date = st.date_input("लक्षित तिथि (Target Date)", value=date(2027, 4, 12), format="DD/MM/YYYY", key="ghatna_single_d")
                with col_q3:
                    st.write("")
                    st.caption("📍 लक्षित तिथि का ३२-शास्त्रीय नियमों व ३-स्तरीय ट्रिगर द्वारा वेध")

        if "12-24" in scan_mode:
            scan_res = default_event_query_service.scan_event_range(chart, theme, start_range_date, months_horizon)

            # Top Hero Peak Banner
            p_rec = scan_res["peak_record"]
            p_month = scan_res["peak_month"]
            p_score = scan_res["peak_score"]
            st.markdown(f"""
    <div style="background:linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #0D9488 100%); border-radius:12px; padding:18px 24px; color:#FFFFFF; margin:16px 0; box-shadow:0 4px 14px rgba(37,99,235,0.2);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
            <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; opacity:0.85;">३-स्तरीय शास्त्रीय ट्रिगर क्षितिज • {scan_res['theme_name_hi']}</div>
            <div style="font-size:22px; font-weight:900; margin-top:4px;">🌟 सर्वोच्च सम्भावना काल: {p_month} ({p_score}% सम्भावना)</div>
            <div style="font-size:13px; opacity:0.92; margin-top:4px; font-style:italic;">"{scan_res['shastra_quote']}"</div>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:18px; font-weight:900;">{p_score}%</div>
                <div style="font-size:11px; font-weight:700;">शिखर स्कोर</div>
            </div>
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:18px; font-weight:900;">{len(scan_res['golden_months'])} माह</div>
                <div style="font-size:11px; font-weight:700;">स्वर्ण अवसर</div>
            </div>
            <div style="background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.3); border-radius:8px; padding:6px 14px; text-align:center;">
                <div style="font-size:18px; font-weight:900;">{scan_res['average_score']}%</div>
                <div style="font-size:11px; font-weight:700;">औसत सम्भावना</div>
            </div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

            st.markdown("#### 📊 माह-दर-माह सम्भावना एवं ३-स्तरीय शास्त्रीय ट्रिगर्स:")
            st.caption("प्रत्येक माह की सम्भावना (०-१००%) = दशा संरेखण (४०) + शनि-गुरु दोहरा गोचर (३५) + अष्टकवर्ग बल (२५):")

            dt_shl = SHASTRIYA_SHLOKAS.get("double_transit", {})
            if dt_shl:
                dt_lines = "<br/>".join(dt_shl['shloka'].splitlines())
                st.markdown(f"""
    <div style="background: rgba(37, 99, 235, 0.08); border-left: 4px solid #2563EB; padding: 14px 18px; border-radius: 8px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #1D4ED8; font-size: 13.5px; margin-bottom: 4px;">📖 {dt_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {dt_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {dt_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {dt_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

            # Grid of Monthly Records
            m_cols = st.columns(3)
            for idx, r in enumerate(scan_res["monthly_records"]):
                c_idx = idx % 3
                with m_cols[c_idx]:
                    card_bg = "#ECFDF5" if r["score"] >= 75 else ("#EFF6FF" if r["score"] >= 60 else ("#FFFBEB" if r["score"] >= 45 else "#FEF2F2"))
                    border_c = "#10B981" if r["score"] >= 75 else ("#3B82F6" if r["score"] >= 60 else ("#F59E0B" if r["score"] >= 45 else "#EF4444"))
                    st.markdown(f"""
    <div style="background:{card_bg}; border:1.5px solid {border_c}; border-radius:10px; padding:14px; margin-bottom:12px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:16px; font-weight:900; color:#0F172A;">📅 {r['month_label']}</span>
        <span style="font-size:14px; font-weight:900; color:{border_c}; background:#FFFFFF; border:1px solid {border_c}; padding:2px 8px; border-radius:6px;">{r['score']}%</span>
    </div>
    <div style="font-size:12px; font-weight:700; color:#334155; margin-top:6px;">{r['status_hi']}</div>
    <div style="font-size:11px; color:#475569; margin-top:4px;">
        • <b>सक्रिय दशा:</b> {r['active_dasha']}<br/>
        • <b>प्रत्यन्तर स्वामी:</b> {r.get('eval_detail', {}).get('tier1', {}).get('pratyantardasha', '')} | <b>दोहरा गोचर:</b> {'✅ सक्रिय' if r['double_transit'] else '⚪ आंशिक/तटस्थ'}<br/>
        • <b>ट्रिगर अंक:</b> दशा {r['tier1_score']}/40 | गोचर {r['tier2_score']}/35 | अष्टक {r['tier3_score']}/25
    </div>
    <div style="font-size:11px; color:#065F46; margin-top:6px; font-style:italic; line-height:1.4;">
        💡 {r['guidance_hi']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        else:
            # Single Date Deep Dive Execution
            query_input = GhatnaQueryInput(
                birth_data=birth_profile,
                target_date=target_event_date,
                theme=theme
            )
            result = default_event_query_service.execute_query(query_input, precomputed_chart=chart)
            tier_res = default_event_query_service.evaluate_3tier_triggers(chart, theme, target_event_date)

            st.markdown("---")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("लक्षित तिथि", result.target_date.strftime("%d-%b-%Y"))
            m_col2.metric("३-स्तरीय सम्भावना", f"{tier_res['composite_probability']}%", tier_res['status_hi'].split(' ')[1])
            m_col3.metric("विश्वास स्तर", result.confidence_band.split(" ")[0])
            m_col4.metric("सक्रिय विंशोत्तरी दशा", result.active_dasha.formatted_summary)

            st.info(f"📊 **पद्धति सहमति अनुपात (Consensus):** {result.consensus_ratio} | 👑 **प्रधान भाव:** {tier_res['prime_house']}वां भाव (स्वामी: {tier_res['prime_lord']})")

            # 3-Tier Trigger Detailed Cards
            st.markdown("#### ⚡ ३-स्तरीय शास्त्रीय ट्रिगर विस्तृत विश्लेषण (3-Tier Trigger Details)")
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                st.markdown(f"""
    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px; min-height:170px;">
    <div style="font-size:14px; font-weight:800; color:#1E40AF;">१. दशा संरेखण ({tier_res['tier1']['score']}/{tier_res['tier1']['max']} अंक)</div>
    <div style="font-size:12px; color:#1E3A8A; margin-top:6px;">
        • <b>दशा:</b> {tier_res['tier1']['active_dasha']}<br/>
        {'<br/>• '.join(tier_res['tier1']['reasons'])}
    </div>
    </div>
    """, unsafe_allow_html=True)
            with t_col2:
                st.markdown(f"""
    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:14px; min-height:170px;">
    <div style="font-size:14px; font-weight:800; color:#065F46;">२. गुरु-शनि दोहरा गोचर ({tier_res['tier2']['score']}/{tier_res['tier2']['max']} अंक)</div>
    <div style="font-size:12px; color:#064E3B; margin-top:6px;">
        • <b>शनि भाव:</b> {tier_res['tier2']['saturn_house']}वां | <b>गुरु भाव:</b> {tier_res['tier2']['jupiter_house']}वां<br/>
        {'<br/>• '.join(tier_res['tier2']['reasons'])}
    </div>
    </div>
    """, unsafe_allow_html=True)
            with t_col3:
                st.markdown(f"""
    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px; min-height:170px;">
    <div style="font-size:14px; font-weight:800; color:#92400E;">३. अष्टकवर्ग संपुष्टि ({tier_res['tier3']['score']}/{tier_res['tier3']['max']} अंक)</div>
    <div style="font-size:12px; color:#78350F; margin-top:6px;">
        • <b>गुरु BAV:</b> {tier_res['tier3']['jupiter_bav']} | <b>शनि BAV:</b> {tier_res['tier3']['saturn_bav']}<br/>
        • <b>प्रधान भाव SAV:</b> {tier_res['tier3']['prime_sav']} बिन्दु<br/>
        {'<br/>• '.join(tier_res['tier3']['reasons'])}
    </div>
    </div>
    """, unsafe_allow_html=True)

            col_res1, col_res2 = st.columns([3, 2])
            with col_res1:
                st.markdown("### 📖 शास्त्रीय साक्ष्य सार (Classical Narrative)")
                st.markdown(result.narrative_hi)
                with st.expander("English Summary"):
                    st.markdown(result.narrative_en)

            with col_res2:
                st.markdown("### 🪐 गोचर व सूक्ष्म स्थिति (Transit & Micro-Coordinates)")
                t = result.transit_summary
                st.markdown(f"- **शनि गोचर:** चंद्र से {t.saturn_house_from_moon}वां | लग्न से {t.saturn_house_from_lagna}वां भाव")
                st.markdown(f"- **गुरु गोचर:** चंद्र से {t.jupiter_house_from_moon}वां | लग्न से {t.jupiter_house_from_lagna}वां भाव")
                st.markdown(f"- **साढ़े साती:** {'✅ सक्रिय - ' + (t.sade_sati_phase or '') if t.is_sade_sati else '❌ निष्क्रिय'}")
                st.markdown(f"- **ढैय्या:** {'✅ सक्रिय - ' + (t.dhaiya_type or '') if t.is_dhaiya else '❌ निष्क्रिय'}")

                st.markdown("---")
                st.markdown("##### ⏳ सक्रिय दशानाथ सूक्ष्म स्थिति:")
                _d_lord = getattr(result, 'dasha_lord', 'Jupiter')
                _po = chart.planets.get(_d_lord)
                if _po:
                    _d_sdeg = getattr(_po, 'sign_degree', 0.0)
                    _d_ansh = int(_d_sdeg)
                    _d_kala = int(round((_d_sdeg - _d_ansh) * 60.0))
                    if _d_kala >= 60: _d_kala = 0; _d_ansh += 1
                    _d_nak = getattr(_po, 'nakshatra_name', '')
                    _d_pad = getattr(_po, 'nakshatra_pada', 1)
                    st.markdown(f"- **{_d_lord}:** `{_po.sign_name} ({_d_ansh}° {_d_kala:02d}')` | `{_po.house_from_lagna} भाव` | `{_d_nak} (पद {_d_pad})`")

            st.markdown("### 🔍 सक्रिय शास्त्रीय नियम एवं साक्ष्य (Fired Rules Evidence)")
            if result.top_positive_signals:
                st.markdown("##### 🟢 अनुकूल शास्त्रीय योग:")
                for r in result.top_positive_signals:
                    st.markdown(f"""
                    <div class="rule-card">
                        <b>{r.rule_name_hi}</b> ({r.rule_name_en})<br/>
                        <small style="color:#F59E0B;">स्रोत: {r.source_text} | अध्याय: {r.source_chapter} | पद्धति: {r.school}</small><br/>
                        <span>{r.explanation_hi}</span><br/>
                        <small style="color:#6EE7B7;">सिग्नल शक्ति: {r.signal_score:.2f} | पुष्टि: {'हाँ' if r.varga_confirmed else 'सामान्य'}</small>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_past_event:
        with st.expander("⚙️ भूतपूर्व घटना विवरण एवं ६-स्तंभ सत्यापन पैरामीटर्स (Past Event Verification Controls)", expanded=True):
            st.write("विगत जीवन की किसी भी ऐतिहासिक घटना (उदा: विवाह, प्रथम नौकरी, पदोन्नति, मकान क्रय, संतान जन्म, विदेश यात्रा आदि) का **६ शास्त्रीय स्तंभों** द्वारा वैज्ञानिक एवं शास्त्र-सम्मत सत्यापन प्राप्त करें।")

            col_p1, col_p2, col_p3 = st.columns([2, 2, 2])
            default_past_date = date(2021, 5, 20)
            past_target_date = col_p1.date_input("भूतपूर्व घटना तिथि (Past Event Date)", value=default_past_date, format="DD/MM/YYYY", key="pe_target_date_inp")
            past_theme = col_p2.selectbox(
                "घटना का विषय (Event Theme)",
                ["marriage", "career", "wealth", "education", "children", "property", "travel", "health", "spirituality"],
                format_func=lambda x: {
                    "marriage": "💍 विवाह / संबंध (Marriage)",
                    "career": "💼 आजीविका / नौकरी / पदोन्नति (Career)",
                    "wealth": "💰 धन / संचित वैभव (Wealth)",
                    "education": "🎓 उच्च शिक्षा / उपाधि (Education)",
                    "children": "👶 संतान प्राप्ति (Children)",
                    "property": "🏠 भूमि / भवन / वाहन क्रय (Property)",
                    "travel": "✈️ विदेश गमन / दूरस्थ यात्रा (Travel)",
                    "health": "🌿 स्वास्थ्य संकट / रोग (Health)",
                    "spirituality": "🕉️ दीक्षा / साधना / आध्यात्म (Spirituality)"
                }.get(x, x),
                key="pe_theme_sel"
            )
            past_desc = col_p3.text_input("घटना विवरण (Event Description)", value="विवाह संपन्न हुआ", key="pe_desc_inp")

            run_past_verify = st.button("🔍 ६-स्तंभ शास्त्रीय सत्यापन करें (Verify Across 6 Classical Pillars)", type="primary", use_container_width=True, key="pe_verify_btn")

        if run_past_verify or st.session_state.get("pe_last_verified", False):
            st.session_state["pe_last_verified"] = True
            try:
                from src.jyotish.events.past_verification import default_past_event_engine, PastEventVerificationInput
                from src.jyotish.rules.conflict_graph import AstrologicalEvidenceStatus

                pe_inp = PastEventVerificationInput(
                    birth_data=birth_profile,
                    event_theme=past_theme,
                    query_text=past_desc,
                    target_date=past_target_date
                )
                ver_res = default_past_event_engine.verify_past_event(pe_inp, precomputed_chart=chart)

                st.markdown("---")

                # Verdict Status Header Card
                st_val = ver_res.status
                if st_val in (AstrologicalEvidenceStatus.STRONGLY_SUPPORTED, AstrologicalEvidenceStatus.SUPPORTED):
                    card_bg = "#064E3B" if (is_astrallis_mode or is_night_mode) else "#ECFDF5"
                    card_border = "#10B981"
                    card_text = "#6EE7B7" if (is_astrallis_mode or is_night_mode) else "#065F46"
                    card_title = f"✅ शास्त्र-सम्मत सत्यापन: {st_val.value.upper()}"
                    card_desc = "इस ऐतिहासिक तिथि पर जन्म कुण्डली, विंशोत्तरी दशा, ऐतिहासिक गोचर एवं षोडशवर्ग चक्रों में घटना के पूर्ण शास्त्रीय योग उपस्थित पाए गए।"
                elif st_val in (AstrologicalEvidenceStatus.MODERATELY_SUPPORTED, AstrologicalEvidenceStatus.WEAKLY_SUPPORTED):
                    card_bg = "#78350F" if (is_astrallis_mode or is_night_mode) else "#FFFBEB"
                    card_border = "#F59E0B"
                    card_text = "#FCD34D" if (is_astrallis_mode or is_night_mode) else "#92400E"
                    card_title = f"⚠️ आंशिक शास्त्रीय समर्थन: {st_val.value.upper()}"
                    card_desc = "इस तिथि पर कुछ मुख्य शास्त्रीय स्तंभ (जैसे दशा या गोचर) अनुकूल रहे, जबकि कुछ स्तंभ तटस्थ अथवा सूक्ष्म स्तर पर सक्रिय थे।"
                elif st_val in (AstrologicalEvidenceStatus.INCONCLUSIVE, AstrologicalEvidenceStatus.CONFLICTING):
                    card_bg = "#1E293B" if (is_astrallis_mode or is_night_mode) else "#F1F5F9"
                    card_border = "#64748B"
                    card_text = "#CBD5E1" if (is_astrallis_mode or is_night_mode) else "#334155"
                    card_title = f"ℹ️ अनिर्णायक/विरोधाभासी साक्ष्य: {st_val.value.upper()}"
                    card_desc = "शास्त्रीय गणनाओं में इस तिथि पर घटना के स्पष्ट और निर्णायक योगों की पर्याप्त पुष्टि नहीं हो सकी।"
                else:
                    card_bg = "#7F1D1D" if (is_astrallis_mode or is_night_mode) else "#FEF2F2"
                    card_border = "#EF4444"
                    card_text = "#FCA5A5" if (is_astrallis_mode or is_night_mode) else "#991B1B"
                    card_title = f"❌ शास्त्रीय समर्थन का अभाव: {st_val.value.upper()}"
                    card_desc = "इस तिथि पर संबंधित भाव एवं भावेश के प्रतिकूल योग तथा दशा-गोचर की अनुपस्थिति पाई गई।"

                st.markdown(f"""
                <div style="background:{card_bg}; border:2px solid {card_border}; border-radius:10px; padding:16px; margin-bottom:16px;">
                    <div style="font-size:18px; font-weight:900; color:{card_text}; margin-bottom:4px;">{card_title}</div>
                    <div style="font-size:13.5px; color:{card_text}; font-weight:600;">{card_desc}</div>
                </div>
                """, unsafe_allow_html=True)

                # Metrics Row
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                m_c1.metric("लक्षित भूतपूर्व तिथि", ver_res.target_date.strftime("%d-%b-%Y"))
                m_c2.metric("शास्त्रीय विश्वास स्तर", f"{ver_res.confidence_score*100:.1f}%")
                m_c3.metric("सत्यापन स्थिति (Status)", ver_res.status.value.upper())
                m_c4.metric("सक्रिय विंशोत्तरी दशा", ver_res.pillar_4_dasha_evidence.get("summary", "—"))

                st.markdown("### 🏛️ ६ शास्त्रीय स्तंभों का विस्तृत साक्ष्य (The 6 Classical Pillars Evidence)")

                p_row1_c1, p_row1_c2, p_row1_c3 = st.columns(3)
                p_row2_c1, p_row2_c2, p_row2_c3 = st.columns(3)

                # Pillar 1: D1 Natal Potential
                p1 = ver_res.pillar_1_d1_evidence
                with p_row1_c1:
                    st.markdown(f"""
                    <div style="border:1.5px solid #3B82F6; border-radius:8px; padding:12px; height:100%; background:rgba(59,130,246,0.06);">
                        <b style="color:#2563EB; font-size:14px;">१. जन्म लग्न विभव (Natal D1)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>प्राथमिक भाव:</b> {p1.get('house')}वां भाव<br/>
                            • <b>भावेश:</b> {p1.get('lord')}<br/>
                            • <b>भावेश स्थिति:</b> {p1.get('lord_house')}वां भाव ({p1.get('lord_dignity', 'neutral')})<br/>
                            • <b>लग्न विभव स्कोर:</b> <b>{p1.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 2: Prashna Overlay
                p2 = ver_res.pillar_2_prashna_evidence or {}
                with p_row1_c2:
                    p2_fav = "✅ अनुकूल" if p2.get("prashna_favorable") else "ℹ️ सामान्य"
                    st.markdown(f"""
                    <div style="border:1.5px solid #8B5CF6; border-radius:8px; padding:12px; height:100%; background:rgba(139,92,246,0.06);">
                        <b style="color:#7C3AED; font-size:14px;">२. प्रश्न लग्न कुण्डली (Horary Overlay)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>प्रश्न लग्न:</b> {p2.get('prashna_lagna', 'उपलब्ध नहीं')}<br/>
                            • <b>कार्याध्यक्ष स्थिति:</b> {p2_fav}<br/>
                            • <b>प्रश्न कुण्डली समय:</b> वर्तमान जिज्ञासा क्षण<br/>
                            • <b>प्रश्न बल स्कोर:</b> <b>{p2.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 3: Varga Confirmation
                p3 = ver_res.pillar_3_varga_evidence
                with p_row1_c3:
                    p3_conf = "✅ वर्ग पुष्टि" if p3.get("confirmed") else "⚠️ सामान्य स्थिति"
                    st.markdown(f"""
                    <div style="border:1.5px solid #10B981; border-radius:8px; padding:12px; height:100%; background:rgba(16,185,129,0.06);">
                        <b style="color:#059669; font-size:14px;">३. वर्ग कुण्डली पुष्टि (Divisional Varga)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>संबद्ध वर्ग चक्र:</b> {p3.get('varga', 'D9')}<br/>
                            • <b>वर्ग भावेश:</b> {p3.get('varga_lord')} ({p3.get('varga_dignity', 'neutral')})<br/>
                            • <b>वर्ग स्थिति:</b> {p3.get('varga_house')}वां भाव ({p3_conf})<br/>
                            • <b>वर्ग पुष्टि स्कोर:</b> <b>{p3.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 4: Operating Vimshottari Dasha
                p4 = ver_res.pillar_4_dasha_evidence
                with p_row2_c1:
                    p4_fav = "✅ पूर्ण फलित योग" if p4.get("dasha_favorable") else "ℹ️ तटस्थ/सामान्य दशा"
                    st.markdown(f"""
                    <div style="border:1.5px solid #F59E0B; border-radius:8px; padding:12px; height:100%; background:rgba(245,158,11,0.06);">
                        <b style="color:#D97706; font-size:14px;">४. सक्रिय दशा विन्यास (Operating Dasha)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>महादशा:</b> {p4.get('mahadasha')} | <b>अंतर्दशा:</b> {p4.get('antardasha')}<br/>
                            • <b>प्रत्यंतर्दशा:</b> {p4.get('pratyantardasha', '—')}<br/>
                            • <b>दशा अनुकूलता:</b> {p4_fav}<br/>
                            • <b>दशा सक्रियता स्कोर:</b> <b>{p4.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 5: Historical Double Transit
                p5 = ver_res.pillar_5_transit_evidence
                with p_row2_c2:
                    p5_sat = "✅ अनुकूल" if p5.get("saturn_favorable") else "सामान्य"
                    p5_jup = "✅ शुभ/दृष्टि" if p5.get("jupiter_favorable") else "सामान्य"
                    st.markdown(f"""
                    <div style="border:1.5px solid #06B6D4; border-radius:8px; padding:12px; height:100%; background:rgba(6,182,212,0.06);">
                        <b style="color:#0891B2; font-size:14px;">५. ऐतिहासिक गोचर (Double Transit)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>शनि गोचर भाव:</b> {p5.get('saturn_transit_house')}वां भाव ({p5_sat})<br/>
                            • <b>गुरु गोचर भाव:</b> {p5.get('jupiter_transit_house')}वां भाव ({p5_jup})<br/>
                            • <b>द्वि-गोचर चक्र सक्रियता:</b> {p5.get('transit_score', 0.5)*100:.0f}%<br/>
                            • <b>गोचर संरेखण स्कोर:</b> <b>{p5.get('transit_score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 6: Classical Shastriya Rules Consensus
                p6 = ver_res.pillar_6_rules_evidence
                with p_row2_c3:
                    st.markdown(f"""
                    <div style="border:1.5px solid #EC4899; border-radius:8px; padding:12px; height:100%; background:rgba(236,72,153,0.06);">
                        <b style="color:#DB2777; font-size:14px;">६. शास्त्रीय नियम बैंक (Classical Rules Bank)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>सक्रिय नियम (Fired Rules):</b> {p6.get('rules_fired_count', 0)} नियम<br/>
                            • <b>अनुकूल शास्त्रीय साक्ष्य:</b> {p6.get('rules_favorable_count', 0)} योग<br/>
                            • <b>ज्ञानकोष स्रोत:</b> BPHS, फलदीपिका, सारावली<br/>
                            • <b>शास्त्रीय सहमति स्कोर:</b> <b>{p6.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                # Shastriya Narrative
                st.markdown("### 📖 शास्त्रीय साक्ष्य सार (Classical Verification Narrative)")
                st.markdown(ver_res.ai_explanation_hi)

                with st.expander("Classical English Synthesis"):
                    st.markdown(ver_res.ai_explanation_en)

                # Master Directive Rule 5 Disclaimer
                st.info(f"⚖️ **शास्त्रीय प्रमाण नीति (Master Directive Rule 5):** {ver_res.disclaimer_hi}")

            except Exception as pe_err:
                st.error(f"सत्यापन गणना में त्रुटि: {str(pe_err)}")

    # =============================================================
    # TAB 2: JANM KUNDALI & SHODASHAVARGA

