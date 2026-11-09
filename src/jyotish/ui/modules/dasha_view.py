import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
import importlib
import streamlit.components.v1 as components

from src.jyotish.services.shastriya_pramana import default_shastriya_pramana_engine

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def render_dasha_view(chart, tz_offset=5.5, tabs=None):
    if tabs is None or len(tabs) < 14:
        tabs = [
            "📊 १२०-वर्ष गेंट चार्ट",
            "⏳ जीवन टाइमलाइन",
            "🌟 विंशोत्तरी (५ स्तर)",
            "🌸 योगिनी दशा (३६ वर्ष)",
            "🔱 जैमिनी चर दशा",
            "🔄 कालचक्र दशा",
            "⚔️ शूल दशा (मारक)",
            "🕉️ अष्टोत्तरी दशा",
            "🪐 नारायण दशा",
            "⏳ द्विसप्ततिसम दशा",
            "🔷 स्थिर दशा",
            "👁️ दृग दशा",
            "🎯 बहु-दशा संगम",
            "📜 शास्त्रीय प्रमाण व उपाय"
        ]
    st.subheader("⏱️ दशा प्रणालियाँ एवं एकीकृत जीवन टाइमलाइन (Dasha Systems & Predictive Life Timeline)")
    st.write("विंशोत्तरी (५-स्तर), योगिनी, जैमिनी चर, कालचक्र, शूल, अष्टोत्तरी, नारायण, द्विसप्ततिसम, स्थिर, दृग एवं बहु-दशा सहमति विश्लेषण।")

    c_dt1, c_dt2 = st.columns([2, 4])
    with c_dt1:
        live_dasha_now = get_live_local_now(tz_offset)
        dasha_target_date = st.date_input(
            "🎯 लक्षित दिनांक पर दशा देखें (Target Date for All Dashas):",
            value=live_dasha_now.date(),
            min_value=date(1900, 1, 1),
            max_value=date(2100, 12, 31),
            format="DD/MM/YYYY",
            key="dasha_main_target_date_picker"
        )
    with c_dt2:
        st.caption(f"🗓️ वर्तमान में **{dasha_target_date.strftime('%d-%b-%Y')}** के लिए समस्त १४ दशा प्रणालियों एवं सूक्ष्म दशाओं का तात्कालिक मूल्यांकन प्रदर्शित है।")

    birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
    moon_lon = chart.planets["Moon"].longitude
    target_dt = datetime.combine(dasha_target_date, live_dasha_now.time().replace(microsecond=0))

    import importlib
    import src.jyotish.services.dasha_timeline as dt_mod
    import src.jyotish.services.timeline as tl_mod
    import src.jyotish.dasha.vimshottari as vim_mod
    import src.jyotish.dasha.yogini as yog_mod
    import src.jyotish.dasha.chara as chara_mod
    import src.jyotish.dasha.kcd as kcd_mod
    import src.jyotish.dasha.shoola as shoola_mod
    import src.jyotish.dasha.ashtottari as ashto_mod
    import src.jyotish.dasha.narayana as narayana_mod
    import src.jyotish.dasha.sama_dashas as sama_mod
    import src.jyotish.dasha.sthira_drig as sthira_mod

    d_engine = vim_mod.default_dasha_engine
    y_engine = yog_mod.default_yogini_engine
    c_engine = chara_mod.default_chara_engine
    kcd_engine = getattr(kcd_mod, "default_kcd_engine", None) or getattr(kcd_mod, "KaalachakraDashaEngine")()
    shoola_engine = getattr(shoola_mod, "default_shoola_engine", None) or getattr(shoola_mod, "ShoolaDashaEngine")()
    ashto_engine = ashto_mod.default_ashtottari_engine
    narayana_engine = narayana_mod.default_narayana_engine
    dwisaptati_engine = sama_mod.default_dwisaptati_engine
    sthira_engine = sthira_mod.default_sthira_engine
    drig_engine = sthira_mod.default_drigdasha_engine

    # Classical Shastriya Shloka Card
    bphs_dasha_shloka = {
        "title": "बृहत्पाराशर होराशास्त्रम् एवं सारावली — दशा फल एवं काल निर्णय",
        "source": "महर्षि पराशर विरचित BPHS (अध्याय ३५ - दशाध्याय) एवं सारावली (अध्याय ४०)",
        "shloka": "दशासु सर्वजन्तूनां शुभाशुभफलोद्भवः।\nग्रहाणां बलदोषेण जायते कालसंयुतः॥\nविंशोत्तरी दशा मुख्या नक्षत्राणां बलेन च।\nयोगिन्याद्यास्तथैवान्या फलपाके विशिष्यते॥",
        "meaning": "समस्त प्राणियों के जीवन में शुभाशुभ फलों की अभिव्यक्ति ग्रहों की दशाओं में उनके बल, निर्बलता, सूक्ष्म देशांतर व काल-संयोग से होती है। कलिकाल में नक्षत्र-बल से परिकलित १२०-वर्षीय विंशोत्तरी दशा सर्वप्रमुख है तथा योगिनी, चर आदि दशाएं सूक्ष्म फलपाक को प्रकट करती हैं।"
    }
    with st.expander(f"📜 शास्त्रीय प्रमाण — {bphs_dasha_shloka['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {bphs_dasha_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{bphs_dasha_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {bphs_dasha_shloka['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Active Native Micro-Planetary Longitudes & Active Dasha Lords Console
    lagna_sname = getattr(chart, "lagna_sign_name", "Aries")
    l_deg = getattr(chart, "lagna_degree", 0.0)
    l_ansh = int(l_deg)
    l_kala = int(round((l_deg - l_ansh) * 60.0))
    if l_kala >= 60:
        l_kala = 0
        l_ansh += 1
    l_dms = f"{l_ansh}° {l_kala:02d}'"

    moon = chart.planets.get("Moon")
    if moon:
        m_deg = getattr(moon, "sign_degree", 0.0)
        m_ansh = int(m_deg)
        m_kala = int(round((m_deg - m_ansh) * 60.0))
        if m_kala >= 60:
            m_kala = 0
            m_ansh += 1
        m_dms = f"{m_ansh}° {m_kala:02d}'"
        m_nak = getattr(moon, "nakshatra_name", getattr(moon, "nakshatra", "—"))
        m_pada = getattr(moon, "nakshatra_pada", getattr(moon, "pada", 1))
        moon_str = f"{moon.sign_name} {m_dms} [{m_nak}-P{m_pada}]"
    else:
        moon_str = "—"

    # Active Vimshottari at target date
    try:
        active_vim = d_engine.get_active_dasha_at(birth_dt, moon_lon, dasha_target_date)
        md_lord = active_vim.mahadasha.lord if (active_vim and active_vim.mahadasha) else "—"
        ad_lord = active_vim.antardasha.lord if (active_vim and active_vim.antardasha) else "—"
        pd_lord = active_vim.pratyantardasha.lord if (active_vim and active_vim.pratyantardasha) else "—"
    except Exception:
        md_lord, ad_lord, pd_lord = "—", "—", "—"

    # Micro coords of MD lord
    md_p_obj = chart.planets.get(md_lord)
    if md_p_obj:
        md_deg = getattr(md_p_obj, "sign_degree", 0.0)
        md_ansh = int(md_deg)
        md_kala = int(round((md_deg - md_ansh) * 60.0))
        if md_kala >= 60:
            md_kala = 0
            md_ansh += 1
        md_dms = f"{md_p_obj.sign_name} {md_ansh}° {md_kala:02d}' [{getattr(md_p_obj, 'nakshatra_name', getattr(md_p_obj, 'nakshatra', '—'))}-P{getattr(md_p_obj, 'nakshatra_pada', getattr(md_p_obj, 'pada', 1))}]"
        is_shubh_md = md_lord in ["Jupiter", "Venus", "Mercury", "Moon"]
        md_swabhav = "नैसर्गिक शुभ" if is_shubh_md else "नैसर्गिक क्रूर"
    else:
        md_dms = ""
        md_swabhav = "—"

    c_da1, c_da2, c_da3, c_da4 = st.columns(4)
    c_da1.metric("लग्न एवं चन्द्र", f"{lagna_sname} {l_dms}", f"🌙 {moon_str}")
    c_da2.metric("🌟 सक्रिय महादशा (MD)", f"{md_lord} ({md_swabhav})", f"{md_dms}")
    c_da3.metric("🎯 अंतर्दशा (AD) व प्रत्यंतर", f"{ad_lord} ➔ {pd_lord}", f"लक्षित: {dasha_target_date.strftime('%d-%b-%Y')}")
    c_da4.metric("📊 एकीकृत दशा चक्र", "१४ दशा प्रणालियाँ", "पाराशर, जैमिनी व योगिनी")

    tab_d1, tab_d2, tab_d3, tab_d4, tab_d5, tab_d6, tab_d7, tab_d8, tab_d9, tab_d10, tab_d11, tab_d12, tab_d13, tab_d14 = st.tabs(tabs)

    # =========================================================================
    # TAB 1: 120-YEAR VISUAL GANTT TIMELINE
    # =========================================================================
    with tab_d1:
        st.markdown("### 📊 विंशोत्तरी बहु-स्तरीय दृश्य दशा टाइमलाइन (120-Year Gantt Timeline)")
        st.caption("पाराशर-स्तरीय १२०-वर्षीय आनुपातिक महादशा, अंतर्दशा एवं प्रत्यन्तर्दशा गेंट चार्ट — '📍 आज' स्थिति एवं काल-खंड प्रगति:")

        try:
            c_gt1, c_gt2 = st.columns([2, 2])
            m_list = dt_mod.default_dasha_timeline_service.engine.generate_timeline(chart)
            m_options = ["वर्तमान सक्रिय महादशा (Auto)"] + [
                f"{m['lord']} महादशा ({m['start_date'].strftime('%Y')} - {m['end_date'].strftime('%Y')})"
                for m in m_list
            ]
            with c_gt1:
                sel_m_str = st.selectbox("🔍 विस्तारित महादशा चुनें (Expand Mahadasha):", m_options, index=0, key="sel_gantt_m_14tab")
            with c_gt2:
                cur_th = st.session_state.get("app_theme_mode", "day")
                st.caption(f"🎨 वर्तमान दृश्य थीम: **{cur_th.upper()}** | लक्षित दिनांक: **{dasha_target_date.strftime('%d-%b-%Y')}**")

            sel_idx = None
            if sel_m_str != "वर्तमान सक्रिय महादशा (Auto)":
                sel_idx = m_options.index(sel_m_str) - 1

            gantt_html = dt_mod.default_dasha_timeline_service.render_gantt_html(
                chart,
                target_date=dasha_target_date,
                selected_maha_idx=sel_idx,
                theme_mode=cur_th
            )
            components.html(gantt_html, height=580, scrolling=True)
        except Exception as _e_gantt:
            st.error(f"गेंट टाइमलाइन निर्माण में त्रुटि: {_e_gantt}")

    # =========================================================================
    # TAB 2: UNIFIED 0-100 YEAR PREDICTIVE LIFE TIMELINE
    # =========================================================================
    with tab_d2:
        st.markdown("### ⏳ ० से १०० वर्ष सम्पूर्ण एकीकृत जीवन टाइमलाइन व घटना संभावना")
        st.caption("विंशोत्तरी, जैमिनी चर, योगिनी दशा, वर्षफल मुन्था एवं गोचर गुरु-शनि का संश्लेषित संयुक्त विश्लेषण:")

        try:
            tl_service = tl_mod.default_timeline_service
            tl_bundle = tl_service.calculate_life_timeline(chart, 0, 100)
            records = tl_bundle["records"]
            event_win = tl_bundle["event_windows"]
            curr_age = tl_bundle["current_age"]

            col_ag1, col_ag2 = st.columns([3, 1])
            with col_ag1:
                sel_age = st.slider("🎯 जातक की आयु का चयन करें (Select Age):", min_value=0, max_value=100, value=min(100, curr_age), key="tl_slider_sel_age_14tab")
            with col_ag2:
                st.metric("चुनी गई आयु / वर्ष", f"{sel_age} वर्ष", f"{tl_bundle['birth_year'] + sel_age} ईस्वी")

            sel_rec = next((r for r in records if r["age"] == sel_age), records[0])

            curr_tag_color = '#DCFCE7' if sel_rec['is_current'] else '#EFF6FF'
            curr_text_color = '#166534' if sel_rec['is_current'] else '#1E40AF'
            curr_tag_text = '🔴 वर्तमान प्रभावी वर्ष (Current)' if sel_rec['is_current'] else f"वर्ष {sel_rec['year']}"
            muntha_color = '#16A34A' if 'Fav' in sel_rec['muntha_status'] else '#DC2626'
            sade_color = '#DC2626' if sel_rec['sade_sati'] != 'नहीं' else '#16A34A'

            st.markdown(f"""<div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:12px; padding:16px; margin-bottom:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #E2E8F0; padding-bottom:8px; margin-bottom:12px;">
    <b style="font-size:16px; color:#0F172A;">🗓️ आयु {sel_rec['age']} वर्ष (वर्ष {sel_rec['year']}) की संयुक्त खगोलीय व दशा स्थिति</b>
    <span style="background:{curr_tag_color}; color:{curr_text_color}; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:800;">{curr_tag_text}</span>
    </div>
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:12px;">
    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
    <span style="font-size:11px; color:#64748B; font-weight:700;">🌟 विंशोत्तरी दशा</span><br/>
    <b style="font-size:14px; color:#0F172A;">{sel_rec['dasha_code']}</b><br/>
    <small style="color:#2563EB;">प्रत्यंतर: {sel_rec['vimshottari_pd']}</small>
    </div>
    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
    <span style="font-size:11px; color:#64748B; font-weight:700;">🔱 जैमिनी चर दशा</span><br/>
    <b style="font-size:14px; color:#7C3AED;">{sel_rec['chara_sign']} राशि</b><br/>
    <small style="color:#6B7280;">राशि आधारित काल</small>
    </div>
    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
    <span style="font-size:11px; color:#64748B; font-weight:700;">🌸 योगिनी दशा</span><br/>
    <b style="font-size:14px; color:#DB2777;">{sel_rec['yogini']}</b><br/>
    <small style="color:#6B7280;">३६ वर्षीय चक्र</small>
    </div>
    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
    <span style="font-size:11px; color:#64748B; font-weight:700;">📅 वर्षफल मुन्था</span><br/>
    <b style="font-size:14px; color:#D97706;">भाव {sel_rec['muntha_house']} ({sel_rec['muntha_sign']})</b><br/>
    <small style="color:{muntha_color}; font-weight:700;">{sel_rec['muntha_status']}</small>
    </div>
    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
    <span style="font-size:11px; color:#64748B; font-weight:700;">🪐 शनि / साढ़ेसाती स्थिति</span><br/>
    <b style="font-size:14px; color:{sade_color};">{sel_rec['sade_sati']}</b><br/>
    <small style="color:#6B7280;">चन्द्र से प्रभाव</small>
    </div>
    </div>
    </div>""", unsafe_allow_html=True)

            st.markdown("#### 🎯 इस वर्ष जीवन घटनाओं की संभावना मीटर (Probability Meters 0-100%):")
            col_ev1, col_ev2 = st.columns(2)
            with col_ev1:
                st.markdown(f"💼 **करियर एवं पदोन्नति अनुकूलता:** {sel_rec['career_score']}%")
                st.progress(sel_rec['career_score'] / 100.0)
                st.markdown(f"💍 **विवाह एवं दांपत्य अनुकूलता:** {sel_rec['marriage_score']}%")
                st.progress(sel_rec['marriage_score'] / 100.0)
                st.markdown(f"💰 **धन लाभ एवं संपत्ति क्रय:** {sel_rec['wealth_score']}%")
                st.progress(sel_rec['wealth_score'] / 100.0)
            with col_ev2:
                st.markdown(f"✈️ **विदेश गमन / स्थानांतरण:** {sel_rec['travel_score']}%")
                st.progress(sel_rec['travel_score'] / 100.0)
                st.markdown(f"🛡️ **स्वास्थ्य सतर्कता सूचकांक:** {sel_rec['health_caution_score']}%")
                st.progress(sel_rec['health_caution_score'] / 100.0)

            with st.expander("🌟 जातक के जीवन के प्रमुख अनुकूल समय-खिड़कियां (Life Event Windows Highlights)", expanded=True):
                col_w1, col_w2, col_w3 = st.columns(3)
                with col_w1:
                    st.markdown("**💼 शीर्ष करियर उत्थान वर्ष:**")
                    c_items = [f"• वर्ष {w['year']} (आयु {w['age']} वर्ष, दशा: {w['dasha']}) — {w['score']}%" for w in event_win["career"][:5]]
                    st.markdown("\n".join(c_items) if c_items else "—")
                with col_w2:
                    st.markdown("**💍 प्रबल विवाह योग वर्ष:**")
                    m_items = [f"• वर्ष {w['year']} (आयु {w['age']} वर्ष, दशा: {w['dasha']}) — {w['score']}%" for w in event_win["marriage"][:5]]
                    st.markdown("\n".join(m_items) if m_items else "—")
                with col_w3:
                    st.markdown("**💰 भारी धन लाभ / संपत्ति वर्ष:**")
                    w_items = [f"• वर्ष {w['year']} (आयु {w['age']} वर्ष, दशा: {w['dasha']}) — {w['score']}%" for w in event_win["wealth"][:5]]
                    st.markdown("\n".join(w_items) if w_items else "—")

            with st.expander("📜 ० से १०० वर्ष सम्पूर्ण जीवन डेटा तालिका (Full Table)", expanded=False):
                tbl_rows = []
                for r in records:
                    tbl_rows.append({
                        "आयु": f"{r['age']} वर्ष",
                        "ईस्वी वर्ष": r["year"],
                        "विंशोत्तरी दशा": r["dasha_code"],
                        "चर दशा": r["chara_sign"],
                        "योगिनी": r["yogini"],
                        "मुन्था भाव": f"भाव {r['muntha_house']}",
                        "मुन्था स्थिति": r["muntha_status"],
                        "साढ़ेसाती": r["sade_sati"],
                        "करियर %": f"{r['career_score']}%",
                        "विवाह %": f"{r['marriage_score']}%",
                        "धन %": f"{r['wealth_score']}%",
                        "स्वास्थ्य जोखिम": f"{r['health_caution_score']}%"
                    })
                st.dataframe(pd.DataFrame(tbl_rows), use_container_width=True, hide_index=True)
        except Exception as _e_tl:
            st.error(f"टाइमलाइन गणना त्रुटि: {str(_e_tl)[:300]}")

    # =========================================================================
    # TAB 3: VIMSHOTTARI 5-LEVEL HIERARCHY
    # =========================================================================
    with tab_d3:
        h5 = d_engine.get_5level_hierarchy(birth_dt, moon_lon, target_dt)
        act_m = h5["mahadasha"]
        act_a = h5["antardasha"]
        act_pr = h5["pratyantardasha"]
        act_s = h5["sookshmadasha"]
        act_p = h5["pranadasha"]

        st.markdown(f"#### 🔴 सक्रिय 5-स्तरीय विंशोत्तरी दशा ({dasha_target_date.strftime('%d-%b-%Y')})")
        p_icons = {
            "Sun": "☀️ सूर्य (Sun)", "Moon": "🌙 चन्द्र (Moon)", "Mars": "⚔️ मंगल (Mars)",
            "Mercury": "☿️ बुध (Mercury)", "Jupiter": "🪐 गुरु (Jupiter)", "Venus": "💎 शुक्र (Venus)",
            "Saturn": "⚖️ शनि (Saturn)", "Rahu": "🐉 राहु (Rahu)", "Ketu": "☄️ केतु (Ketu)"
        }

        b_str = (
            f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
            f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय 5-स्तरीय दशा पदानुक्रम (Active Dasha Hierarchy):</div>"
            f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
            f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>👑 {p_icons.get(act_m['lord'], act_m['lord'])}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>🪐 {p_icons.get(act_a['lord'], act_a['lord'])}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ {p_icons.get(act_pr['lord'], act_pr['lord'])}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>🔍 {p_icons.get(act_s['lord'], act_s['lord'])}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#F1F5F9; border:1.5px solid #64748B; color:#0F172A; padding:5px 12px; border-radius:8px;'>🧬 {p_icons.get(act_p['lord'], act_p['lord'])}</span>"
            f"</div>"
            f"</div>"
        )
        st.markdown(b_str, unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">👑 महादशा (L1)</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_m['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{act_m['start_date'].strftime('%d-%b-%y')} ~ {act_m['end_date'].strftime('%d-%b-%y')}</div>
    </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">🪐 अंतर्दशा (L2)</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{act_a['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{act_a['start_date'].strftime('%d-%b-%y')} ~ {act_a['end_date'].strftime('%d-%b-%y')}</div>
    </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ प्रत्यंतर्दशा (L3)</div>
    <div style="font-size:18px; font-weight:900; color:#78350F;">{act_pr['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{act_pr['start_date'].strftime('%d-%b-%y')} ~ {act_pr['end_date'].strftime('%d-%b-%y')}</div>
    </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#BE185D; font-weight:800;">🔍 सूक्ष्मदशा (L4)</div>
    <div style="font-size:18px; font-weight:900; color:#831843;">{act_s['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{act_s['start_date'].strftime('%d-%b')} ~ {act_s['end_date'].strftime('%d-%b')} ({act_s.get('duration_days', 0)}d)</div>
    </div>""", unsafe_allow_html=True)
        with c5:
            st.markdown(f"""<div style="background:#F3F4F6; border: 2px solid #64748B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#334155; font-weight:800;">🧬 प्राणदशा (L5)</div>
    <div style="font-size:18px; font-weight:900; color:#0F172A;">{act_p['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{act_p['start_date'].strftime('%d-%b %H:%M')} ~ {act_p['end_date'].strftime('%d-%b %H:%M')}</div>
    </div>""", unsafe_allow_html=True)

        a_total_sec = (act_a["end_date"] - act_a["start_date"]).total_seconds()
        a_elapsed_sec = max(0.0, min(a_total_sec, (target_dt - act_a["start_date"]).total_seconds()))
        a_pct = (a_elapsed_sec / max(1.0, a_total_sec))
        st.write("")
        st.markdown(f"**🪐 सक्रिय अंतर्दशा ({act_m['lord']}-{act_a['lord']}) प्रगति: {int(a_pct * 100)}% संपन्न**")
        st.progress(a_pct)

        def _get_lord_micro_info(p_name):
            p_obj = chart.planets.get(p_name)
            if not p_obj:
                return "—", "—", "—"
            deg_val = getattr(p_obj, "sign_degree", 0.0)
            ansh = int(deg_val)
            kala = int(round((deg_val - ansh) * 60.0))
            if kala >= 60:
                kala = 0
                ansh += 1
            dms_str = f"{p_obj.sign_name} {ansh}° {kala:02d}'"
            nak_str = getattr(p_obj, "nakshatra_name", getattr(p_obj, "nakshatra", "—"))
            pada_str = getattr(p_obj, "nakshatra_pada", getattr(p_obj, "pada", 1))
            is_shubh = p_name in ["Jupiter", "Venus", "Mercury", "Moon"]
            swabhav_str = "नैसर्गिक शुभ" if is_shubh else "नैसर्गिक क्रूर"
            return dms_str, f"{nak_str} (चरण {pada_str})", swabhav_str

        st.markdown("##### 🪐 सक्रिय ५-स्तरीय दशा स्वामियों के सूक्ष्म देशांतर व स्वभाव (Active Dasha Lords Micro Dossier)")
        h5_rows = []
        for lvl_name, item in [
            ("महादशा (L1)", act_m),
            ("अंतर्दशा (L2)", act_a),
            ("प्रत्यंतर्दशा (L3)", act_pr),
            ("सूक्ष्मदशा (L4)", act_s),
            ("प्राणदशा (L5)", act_p)
        ]:
            l_name = item['lord']
            dms_s, nak_s, swa_s = _get_lord_micro_info(l_name)
            h5_rows.append({
                "दशा स्तर": lvl_name,
                "स्वामी ग्रह": l_name,
                "नैसर्गिक स्वभाव": swa_s,
                "राशि व अंश-कला (DMS)": dms_s,
                "नक्षत्र एवं चरण": nak_s,
                "अवधि प्रारंभ": item['start_date'].strftime('%d-%b-%Y'),
                "अवधि समाप्ति": item['end_date'].strftime('%d-%b-%Y')
            })
        st.dataframe(pd.DataFrame(h5_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 🌳 विंशोत्तरी दशा बहु-स्तरीय विस्तृत अन्वेषक (5-Level Interactive Explorer)")

        tab_v1, tab_v2, tab_v3, tab_v4, tab_v5, tab_v_all = st.tabs([
            "👑 स्तर 1: महादशा (Mahadasha)",
            "🪐 स्तर 2: अंतर्दशा (Antardasha)",
            "⚡ स्तर 3: प्रत्यंतर्दशा (Pratyantardasha)",
            "🔍 स्तर 4: सूक्ष्मदशा (Sookshmadasha)",
            "🧬 स्तर 5: प्राणदशा (Pranadasha)",
            "📜 सम्पूर्ण 120-वर्षीय कालक्रम (All Mahadashas)"
        ])

        v_mahadashas = d_engine.generate_mahadasha_sequence(birth_dt, moon_lon, num_cycles=2)
        maha_options = [f"{m['lord']} ({m['start_date'].strftime('%d-%b-%Y')} से {m['end_date'].strftime('%d-%b-%Y')})" for m in v_mahadashas]
        default_maha_idx = next((i for i, m in enumerate(v_mahadashas) if m['lord'] == act_m['lord'] and m['start_date'] <= target_dt <= m['end_date']), 0)

        with tab_v1:
            st.markdown("##### 👑 समस्त 9 महादशाएँ (120 Years Vimshottari Cycle)")
            m_rows = []
            for m in v_mahadashas:
                is_active = (m["start_date"] <= target_dt <= m["end_date"])
                m_rows.append({
                    "महादशा स्वामी (Lord)": f"👑 {m['lord']}" + (" (⭐ वर्तमान सक्रिय)" if is_active else ""),
                    "आरंभ दिनांक (Start)": m["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक (End)": m["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (Years)": f"{m['duration_years']:.2f} वर्ष",
                    "प्रकार": "जन्म शेष (Birth Balance)" if m.get("is_partial") else "पूर्ण महादशा",
                    "सक्रियता": "✅ सक्रिय" if is_active else "—"
                })
            st.dataframe(pd.DataFrame(m_rows), use_container_width=True, hide_index=True)

        with tab_v2:
            st.markdown("##### 🪐 महादशा अंतर्गत समस्त 9 अंतर्दशाएं (Antardashas / Bhuktis)")
            sel_maha_idx = st.selectbox("महादशा चुनें (Select Mahadasha)", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_maha_for_antar_14tab")
            sel_m_obj = v_mahadashas[sel_maha_idx]
            antars = d_engine.generate_antardashas(
                sel_m_obj["lord"], sel_m_obj["start_date"], sel_m_obj["end_date"], is_partial=sel_m_obj.get("is_partial", False)
            )
            a_rows = []
            for a in antars:
                is_a_active = (a["start_date"] <= target_dt <= a["end_date"])
                a_rows.append({
                    "महादशा / अंतर्दशा": f"{sel_m_obj['lord']} — {a['lord']}" + (" (⭐ सक्रिय)" if is_a_active else ""),
                    "अंतर्दशा स्वामी (Lord)": a["lord"],
                    "आरंभ दिनांक (Start)": a["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक (End)": a["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (Years)": f"{a['duration_years']:.2f} वर्ष",
                    "अवधि (माह / दिन)": f"{int(a['duration_years']*12)} माह {int((a['duration_years']*12 % 1)*30)} दिन",
                    "सक्रियता": "✅ सक्रिय" if is_a_active else "—"
                })
            st.dataframe(pd.DataFrame(a_rows), use_container_width=True, hide_index=True)

        with tab_v3:
            st.markdown("##### ⚡ अंतर्दशा अंतर्गत समस्त 9 प्रत्यंतर्दशाएं (Pratyantardashas)")
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                sel_m_prat_idx = st.selectbox("महादशा चुनें", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_m_for_prat_14tab")
            sel_m_for_p = v_mahadashas[sel_m_prat_idx]
            antars_for_p = d_engine.generate_antardashas(sel_m_for_p["lord"], sel_m_for_p["start_date"], sel_m_for_p["end_date"], is_partial=sel_m_for_p.get("is_partial", False))
            antar_p_options = [f"{a['lord']} ({a['start_date'].strftime('%d-%b-%Y')} से {a['end_date'].strftime('%d-%b-%Y')})" for a in antars_for_p]
            default_a_idx = next((i for i, a in enumerate(antars_for_p) if a['lord'] == act_a['lord'] and a['start_date'] <= target_dt <= a['end_date']), 0)
            with col_sel2:
                sel_a_prat_idx = st.selectbox("अंतर्दशा चुनें", range(len(antar_p_options)), format_func=lambda i: antar_p_options[i], index=default_a_idx, key="sel_a_for_prat_14tab")
            sel_a_for_p = antars_for_p[sel_a_prat_idx]
            pratyantars = d_engine.generate_pratyantardashas(
                sel_m_for_p["lord"], sel_a_for_p["lord"], sel_a_for_p["start_date"], sel_a_for_p["end_date"]
            )
            pr_rows = []
            for pr in pratyantars:
                is_pr_act = (pr["start_date"] <= target_dt <= pr["end_date"])
                dur_days = (pr["end_date"] - pr["start_date"]).total_seconds() / 86400.0
                pr_rows.append({
                    "दशा क्रम": f"{sel_m_for_p['lord']} / {sel_a_for_p['lord']} / {pr['lord']}" + (" (⭐ सक्रिय)" if is_pr_act else ""),
                    "प्रत्यंतर्दशा स्वामी": pr["lord"],
                    "आरंभ दिनांक": pr["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक": pr["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (दिन)": f"{dur_days:.1f} दिन",
                    "सक्रियता": "✅ सक्रिय" if is_pr_act else "—"
                })
            st.dataframe(pd.DataFrame(pr_rows), use_container_width=True, hide_index=True)

        with tab_v4:
            st.markdown("##### 🔍 प्रत्यंतर्दशा अंतर्गत समस्त 9 सूक्ष्मदशाएं (Sookshmadashas - Level 4)")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                sel_m_s_idx = st.selectbox("महादशा", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_m_for_sookshma_14tab")
            sel_m_s = v_mahadashas[sel_m_s_idx]
            antars_s = d_engine.generate_antardashas(sel_m_s["lord"], sel_m_s["start_date"], sel_m_s["end_date"], is_partial=sel_m_s.get("is_partial", False))
            with col_s2:
                sel_a_s_idx = st.selectbox("अंतर्दशा", range(len(antars_s)), format_func=lambda i: f"{antars_s[i]['lord']} ({antars_s[i]['start_date'].strftime('%d-%b-%y')})", index=min(default_a_idx, len(antars_s)-1), key="sel_a_for_sookshma_14tab")
            sel_a_s = antars_s[sel_a_s_idx]
            prats_s = d_engine.generate_pratyantardashas(sel_m_s["lord"], sel_a_s["lord"], sel_a_s["start_date"], sel_a_s["end_date"])
            default_pr_idx = next((i for i, p in enumerate(prats_s) if p['lord'] == act_pr['lord'] and p['start_date'] <= target_dt <= p['end_date']), 0)
            with col_s3:
                sel_pr_s_idx = st.selectbox("प्रत्यंतर्दशा", range(len(prats_s)), format_func=lambda i: f"{prats_s[i]['lord']} ({prats_s[i]['start_date'].strftime('%d-%b-%y')})", index=min(default_pr_idx, len(prats_s)-1), key="sel_pr_for_sookshma_14tab")
            sel_pr_s = prats_s[sel_pr_s_idx]
            sookshmas = d_engine.generate_sookshmadashas(sel_m_s["lord"], sel_a_s["lord"], sel_pr_s["lord"], sel_pr_s["start_date"], sel_pr_s["end_date"])
            s_rows = []
            for s in sookshmas:
                is_s_act = (s["start_date"] <= target_dt <= s["end_date"])
                s_rows.append({
                    "4-स्तरीय दशा": f"{sel_m_s['lord']}/{sel_a_s['lord']}/{sel_pr_s['lord']}/{s['lord']}" + (" (⭐ सक्रिय)" if is_s_act else ""),
                    "सूक्ष्मदशा स्वामी": s["lord"],
                    "आरंभ समय": s["start_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "समाप्ति समय": s["end_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "अवधि": f"{s['duration_days']} दिन",
                    "सक्रियता": "✅ सक्रिय" if is_s_act else "—"
                })
            st.dataframe(pd.DataFrame(s_rows), use_container_width=True, hide_index=True)

        with tab_v5:
            st.markdown("##### 🧬 सूक्ष्मदशा अंतर्गत समस्त 9 प्राणदशाएं (Pranadashas - Level 5 / Hourly Precision)")
            c_p1, c_p2, c_p3, c_p4 = st.columns(4)
            with c_p1:
                sel_m_p_idx = st.selectbox("महादशा (Maha)", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_m_for_prana_14tab")
            sel_m_p = v_mahadashas[sel_m_p_idx]
            antars_p = d_engine.generate_antardashas(sel_m_p["lord"], sel_m_p["start_date"], sel_m_p["end_date"], is_partial=sel_m_p.get("is_partial", False))
            with c_p2:
                sel_a_p_idx = st.selectbox("अंतर्दशा (Antar)", range(len(antars_p)), format_func=lambda i: f"{antars_p[i]['lord']}", index=min(default_a_idx, len(antars_p)-1), key="sel_a_for_prana_14tab")
            sel_a_p = antars_p[sel_a_p_idx]
            prats_p = d_engine.generate_pratyantardashas(sel_m_p["lord"], sel_a_p["lord"], sel_a_p["start_date"], sel_a_p["end_date"])
            with c_p3:
                sel_pr_p_idx = st.selectbox("प्रत्यंतर्दशा (Prat)", range(len(prats_p)), format_func=lambda i: f"{prats_p[i]['lord']}", index=min(default_pr_idx, len(prats_p)-1), key="sel_pr_for_prana_14tab")
            sel_pr_p = prats_p[sel_pr_p_idx]
            sookshmas_p = d_engine.generate_sookshmadashas(sel_m_p["lord"], sel_a_p["lord"], sel_pr_p["lord"], sel_pr_p["start_date"], sel_pr_p["end_date"])
            default_s_idx = next((i for i, s in enumerate(sookshmas_p) if s['lord'] == act_s['lord'] and s['start_date'] <= target_dt <= s['end_date']), 0)
            with c_p4:
                sel_s_p_idx = st.selectbox("सूक्ष्मदशा (Sookshma)", range(len(sookshmas_p)), format_func=lambda i: f"{sookshmas_p[i]['lord']}", index=min(default_s_idx, len(sookshmas_p)-1), key="sel_s_for_prana_14tab")
            sel_s_p = sookshmas_p[sel_s_p_idx]
            pranas = d_engine.generate_pranadashas(sel_m_p["lord"], sel_a_p["lord"], sel_pr_p["lord"], sel_s_p["lord"], sel_s_p["start_date"], sel_s_p["end_date"])
            p_rows = []
            for prn in pranas:
                is_p_act = (prn["start_date"] <= target_dt <= prn["end_date"])
                p_rows.append({
                    "5-स्तरीय प्राणदशा": f"{sel_m_p['lord']}/{sel_a_p['lord']}/{sel_pr_p['lord']}/{sel_s_p['lord']}/{prn['lord']}" + (" (⭐ सक्रिय)" if is_p_act else ""),
                    "प्राणदशा स्वामी": prn["lord"],
                    "आरंभ समय": prn["start_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "समाप्ति समय": prn["end_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "अवधि (घंटे)": f"{prn['duration_hours']} घंटे",
                    "सक्रियता": "✅ सक्रिय" if is_p_act else "—"
                })
            st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)

        with tab_v_all:
            st.markdown("##### 📜 संपूर्ण 120-वर्षीय जीवन कालक्रम तालिका")
            full_rows = []
            for m in v_mahadashas:
                m_antars = d_engine.generate_antardashas(m["lord"], m["start_date"], m["end_date"], is_partial=m.get("is_partial", False))
                for a in m_antars:
                    is_active = (a["start_date"] <= target_dt <= a["end_date"])
                    full_rows.append({
                        "महादशा (L1)": m["lord"],
                        "अंतर्दशा (L2)": a["lord"],
                        "आरंभ दिनांक": a["start_date"].strftime("%d-%b-%Y"),
                        "समाप्ति दिनांक": a["end_date"].strftime("%d-%b-%Y"),
                        "अवधि (वर्ष)": f"{a['duration_years']:.2f}",
                        "सक्रियता": "⭐ वर्तमान सक्रिय" if is_active else ""
                    })
            st.dataframe(pd.DataFrame(full_rows), use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 4: YOGINI DASHA (36 YEARS - 3 LEVELS)
    # =========================================================================
    with tab_d4:
        st.markdown(f"#### 🌸 योगिनी दशा (36-Year Classical Cycle — Major, Antar & Pratyantar)")
        st.caption("अष्ट योगिनियों (मंगला, पिंगला, धन्या, भ्रामरी, भद्रिका, उल्का, सिद्धा, संकटा) का सूक्ष्म ३-स्तरीय काल-प्रभाव:")
        try:
            yog_dashas = y_engine.generate_timeline(chart)
            act_yog = next((y for y in yog_dashas if y["start_date"] <= target_dt <= y["end_date"]), yog_dashas[0])
            y_antars_for_act = y_engine.generate_antardashas(
                act_yog.get("yogini_name", act_yog.get("yogini")), act_yog["start_date"], act_yog["end_date"]
            )
            act_ya = next((a for a in y_antars_for_act if a["start_date"] <= target_dt <= a["end_date"]), y_antars_for_act[0])
            y_prats_for_act = y_engine.generate_pratyantardashas(
                act_yog.get("yogini_name", act_yog.get("yogini")), act_ya["yogini"], act_ya["start_date"], act_ya["end_date"]
            )
            act_ypr = next((p for p in y_prats_for_act if p["start_date"] <= target_dt <= p["end_date"]), y_prats_for_act[0])

            b_str_yog = (
                f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
                f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय 3-स्तरीय योगिनी दशा पदानुक्रम (Active Yogini Dasha Hierarchy):</div>"
                f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
                f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🌸 मुख्य योगिनी: {act_yog.get('yogini_name', act_yog.get('yogini'))} ({act_yog.get('lord')})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>💫 योगिनी अंतर्दशा: {act_ya['yogini']} ({act_ya['lord']})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ योगिनी प्रत्यंतर: {act_ypr['yogini']} ({act_ypr['lord']})</span>"
                f"</div>"
                f"</div>"
            )
            st.markdown(b_str_yog, unsafe_allow_html=True)

            y_col1, y_col2, y_col3 = st.columns(3)
            with y_col1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🌸 मुख्य योगिनी (Major)</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_yog.get('yogini_name', act_yog.get('yogini'))} ({act_yog.get('lord')})</div>
    <div style="font-size:10.5px; color:#475569;">{act_yog['start_date'].strftime('%d-%b-%y')} ~ {act_yog['end_date'].strftime('%d-%b-%y')} ({act_yog['duration_years']} वर्ष)</div>
    </div>""", unsafe_allow_html=True)
            with y_col2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">💫 अंतर्दशा (Sub-Period)</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{act_ya['yogini']} ({act_ya['lord']})</div>
    <div style="font-size:10.5px; color:#475569;">{act_ya['start_date'].strftime('%d-%b-%y')} ~ {act_ya['end_date'].strftime('%d-%b-%y')}</div>
    </div>""", unsafe_allow_html=True)
            with y_col3:
                st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ प्रत्यंतर्दशा (Pratyantar)</div>
    <div style="font-size:18px; font-weight:900; color:#78350F;">{act_ypr['yogini']} ({act_ypr['lord']})</div>
    <div style="font-size:10.5px; color:#475569;">{act_ypr['start_date'].strftime('%d-%b-%y')} ~ {act_ypr['end_date'].strftime('%d-%b-%y')}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            tab_y1, tab_y2, tab_y3 = st.tabs([
                "🌸 मुख्य योगिनी दशा (Major Periods)",
                "💫 योगिनी अंतर्दशा (Antardashas)",
                "⚡ योगिनी प्रत्यंतर्दशा (Pratyantardashas)"
            ])
            with tab_y1:
                st.markdown("##### 🌸 मुख्य योगिनी दशा चक्र (36 वर्ष)")
                st.dataframe(pd.DataFrame([{
                    "योगिनी (Yogini)": y.get("yogini_name") or y.get("yogini", "Yogini"),
                    "स्वामी ग्रह (Lord)": y.get("lord", ""),
                    "आरंभ दिनांक (Start)": y["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक (End)": y["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (वर्ष)": f"{y['duration_years']} वर्ष",
                    "स्थिति": "जन्म शेष (Birth Balance)" if y.get("is_partial") else "पूर्ण दशा",
                    "सक्रियता": "⭐ वर्तमान सक्रिय" if (y["start_date"] <= target_dt <= y["end_date"]) else ""
                } for y in yog_dashas]), use_container_width=True, hide_index=True)

            with tab_y2:
                st.markdown("##### 💫 योगिनी अंतर्दशा (8 Sub-periods per Yogini)")
                y_options = [f"{y.get('yogini_name', y.get('yogini'))} ({y['start_date'].strftime('%d-%b-%Y')} ~ {y['end_date'].strftime('%d-%b-%Y')})" for y in yog_dashas]
                default_y_idx = next((i for i, y in enumerate(yog_dashas) if y["start_date"] <= target_dt <= y["end_date"]), 0)
                sel_y_idx = st.selectbox("मुख्य योगिनी चुनें", range(len(y_options)), format_func=lambda i: y_options[i], index=default_y_idx, key="sel_yogini_for_antar_14tab")
                sel_y_obj = yog_dashas[sel_y_idx]
                y_antars = y_engine.generate_antardashas(
                    sel_y_obj.get("yogini_name", sel_y_obj.get("yogini")), sel_y_obj["start_date"], sel_y_obj["end_date"]
                )
                st.dataframe(pd.DataFrame([{
                    "योगिनी / अंतर्दशा": f"{sel_y_obj.get('yogini_name', sel_y_obj.get('yogini'))} — {ya['yogini']}",
                    "अंतर्दशा स्वामी": ya["lord"],
                    "आरंभ दिनांक": ya["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक": ya["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (माह / दिन)": f"{ya['duration_months']} माह ({ya['duration_days']} दिन)",
                    "सक्रियता": "⭐ सक्रिय" if (ya["start_date"] <= target_dt <= ya["end_date"]) else ""
                } for ya in y_antars]), use_container_width=True, hide_index=True)

            with tab_y3:
                st.markdown("##### ⚡ योगिनी प्रत्यंतर्दशा (Pratyantardashas)")
                col_y_p1, col_y_p2 = st.columns(2)
                with col_y_p1:
                    sel_y_m_idx = st.selectbox("मुख्य योगिनी", range(len(y_options)), format_func=lambda i: y_options[i], index=default_y_idx, key="sel_y_m_for_prat_14tab")
                sel_y_m_p = yog_dashas[sel_y_m_idx]
                y_antars_p = y_engine.generate_antardashas(sel_y_m_p.get("yogini_name", sel_y_m_p.get("yogini")), sel_y_m_p["start_date"], sel_y_m_p["end_date"])
                with col_y_p2:
                    sel_y_a_idx = st.selectbox("अंतर्दशा योगिनी", range(len(y_antars_p)), format_func=lambda i: f"{y_antars_p[i]['yogini']} ({y_antars_p[i]['start_date'].strftime('%d-%b-%y')})", key="sel_y_a_for_prat_14tab")
                sel_y_a_p = y_antars_p[sel_y_a_idx]
                y_prats = y_engine.generate_pratyantardashas(
                    sel_y_m_p.get("yogini_name", sel_y_m_p.get("yogini")), sel_y_a_p["yogini"], sel_y_a_p["start_date"], sel_y_a_p["end_date"]
                )
                st.dataframe(pd.DataFrame([{
                    "3-स्तरीय योगिनी": f"{sel_y_m_p.get('yogini_name', sel_y_m_p.get('yogini'))} / {sel_y_a_p['yogini']} / {yp['yogini']}",
                    "प्रत्यंतर स्वामी": yp["lord"],
                    "आरंभ समय": yp["start_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "समाप्ति समय": yp["end_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "अवधि (दिन)": f"{yp['duration_days']} दिन",
                    "सक्रियता": "⭐ सक्रिय" if (yp["start_date"] <= target_dt <= yp["end_date"]) else ""
                } for yp in y_prats]), use_container_width=True, hide_index=True)
        except Exception as _e_yog:
            st.error(f"योगिनी दशा गणना में त्रुटि: {_e_yog}")

    # =========================================================================
    # TAB 5: JAIMINI CHARA DASHA (RASHI BASED)
    # =========================================================================
    with tab_d5:
        st.markdown("#### 🔱 जैमिनी चर दशा (Jaimini Rashi Chara Dasha — Major & Antar)")
        st.caption("महर्षि जैमिनी प्रतिपादित राशि-आधारित चर दशा — कारक ग्रहों व राशि दृष्टियों का संयुक्त फल:")
        try:
            chara_dashas = c_engine.generate_timeline(chart)
            act_chara = next((c for c in chara_dashas if c["start_date"] <= target_dt <= c["end_date"]), chara_dashas[0])
            c_antars_for_act = c_engine.generate_antardashas(act_chara["sign_id"], act_chara["start_date"], act_chara["end_date"])
            act_ca = next((a for a in c_antars_for_act if a["start_date"] <= target_dt <= a["end_date"]), c_antars_for_act[0])
            c_prats_for_act = c_engine.generate_pratyantardashas(act_ca["sign_id"], act_ca["start_date"], act_ca["end_date"])
            act_cpr = next((p for p in c_prats_for_act if p["start_date"] <= target_dt <= p["end_date"]), c_prats_for_act[0])

            b_str_chara = (
                f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
                f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय 3-स्तरीय जैमिनी चर दशा पदानुक्रम (Active Jaimini Chara Dasha Hierarchy):</div>"
                f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
                f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🔱 चर महादशा: {act_chara['sign_name']} (#{act_chara['sign_id']})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>💫 चर अंतर्दशा: {act_ca['sign_name']} (स्वामी: {act_ca['lord']})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ चर प्रत्यंतर: {act_cpr['sign_name']} (स्वामी: {act_cpr['lord']})</span>"
                f"</div>"
                f"</div>"
            )
            st.markdown(b_str_chara, unsafe_allow_html=True)

            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🔱 सक्रिय चर महादशा</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_chara['sign_name']} (#{act_chara['sign_id']})</div>
    <div style="font-size:10.5px; color:#475569;">{act_chara['start_date'].strftime('%d-%b-%y')} ~ {act_chara['end_date'].strftime('%d-%b-%y')} ({act_chara['duration_years']} वर्ष)</div>
    </div>""", unsafe_allow_html=True)
            with c_col2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">💫 चर अंतर्दशा</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{act_ca['sign_name']} (स्वामी: {act_ca['lord']})</div>
    <div style="font-size:10.5px; color:#475569;">{act_ca['start_date'].strftime('%d-%b-%y')} ~ {act_ca['end_date'].strftime('%d-%b-%y')}</div>
    </div>""", unsafe_allow_html=True)
            with c_col3:
                st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ चर प्रत्यंतर्दशा</div>
    <div style="font-size:18px; font-weight:900; color:#78350F;">{act_cpr['sign_name']} (स्वामी: {act_cpr['lord']})</div>
    <div style="font-size:10.5px; color:#475569;">{act_cpr['start_date'].strftime('%d-%b-%y')} ~ {act_cpr['end_date'].strftime('%d-%b-%y')}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            tab_c1, tab_c2, tab_c3 = st.tabs([
                "🔱 चर महादशा (12 Signs)",
                "💫 चर अंतर्दशा (12 Sub-Signs per Sign)",
                "⚡ चर प्रत्यंतर्दशा (Pratyantardasha)"
            ])
            with tab_c1:
                st.markdown("##### 🔱 12 राशियों का चर महादशा कालक्रम")
                st.dataframe(pd.DataFrame([{
                    "राशि (Sign)": f"{c['sign_name']} (#{c['sign_id']})",
                    "आरंभ दिनांक (Start)": c["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक (End)": c["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (वर्ष)": f"{c['duration_years']} वर्ष",
                    "सक्रियता": "⭐ वर्तमान सक्रिय" if (c["start_date"] <= target_dt <= c["end_date"]) else ""
                } for c in chara_dashas]), use_container_width=True, hide_index=True)

            with tab_c2:
                st.markdown("##### 💫 चर अंतर्दशा (12 Sub-signs under Selected Rashi)")
                c_options = [f"{c['sign_name']} ({c['start_date'].strftime('%d-%b-%Y')} ~ {c['end_date'].strftime('%d-%b-%Y')})" for c in chara_dashas]
                default_c_idx = next((i for i, c in enumerate(chara_dashas) if c["start_date"] <= target_dt <= c["end_date"]), 0)
                sel_c_idx = st.selectbox("चर दशा राशि चुनें", range(len(c_options)), format_func=lambda i: c_options[i], index=default_c_idx, key="sel_chara_for_antar_14tab")
                sel_c_obj = chara_dashas[sel_c_idx]
                c_antars = c_engine.generate_antardashas(sel_c_obj["sign_id"], sel_c_obj["start_date"], sel_c_obj["end_date"])
                st.dataframe(pd.DataFrame([{
                    "चर महादशा / अंतर्दशा": f"{sel_c_obj['sign_name']} — {ca['sign_name']}",
                    "राशि स्वामी (Lord)": ca["lord"],
                    "आरंभ दिनांक": ca["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक": ca["end_date"].strftime("%d-%b-%Y"),
                    "अवधि": f"{ca['duration_months']} माह ({ca['duration_days']} दिन)",
                    "सक्रियता": "⭐ सक्रिय" if (ca["start_date"] <= target_dt <= ca["end_date"]) else ""
                } for ca in c_antars]), use_container_width=True, hide_index=True)

            with tab_c3:
                st.markdown("##### ⚡ चर प्रत्यंतर्दशा (12 Sub-divisions per Antardasha)")
                col_c_p1, col_c_p2 = st.columns(2)
                with col_c_p1:
                    sel_c_m_idx = st.selectbox("महादशा राशि", range(len(c_options)), format_func=lambda i: c_options[i], index=default_c_idx, key="sel_c_m_for_prat_14tab")
                sel_c_m_p = chara_dashas[sel_c_m_idx]
                c_antars_p = c_engine.generate_antardashas(sel_c_m_p["sign_id"], sel_c_m_p["start_date"], sel_c_m_p["end_date"])
                with col_c_p2:
                    sel_c_a_idx = st.selectbox("अंतर्दशा राशि", range(len(c_antars_p)), format_func=lambda i: f"{c_antars_p[i]['sign_name']} ({c_antars_p[i]['start_date'].strftime('%d-%b-%y')})", key="sel_c_a_for_prat_14tab")
                sel_c_a_p = c_antars_p[sel_c_a_idx]
                c_prats = c_engine.generate_pratyantardashas(sel_c_a_p["sign_id"], sel_c_a_p["start_date"], sel_c_a_p["end_date"])
                st.dataframe(pd.DataFrame([{
                    "3-स्तरीय चर दशा": f"{sel_c_m_p['sign_name']} / {sel_c_a_p['sign_name']} / {cp['sign_name']}",
                    "राशि स्वामी": cp["lord"],
                    "आरंभ दिनांक": cp["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक": cp["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (दिन)": f"{cp['duration_days']} दिन",
                    "सक्रियता": "⭐ सक्रिय" if (cp["start_date"] <= target_dt <= cp["end_date"]) else ""
                } for cp in c_prats]), use_container_width=True, hide_index=True)
        except Exception as _e_chara:
            st.error(f"चर दशा गणना में त्रुटि: {_e_chara}")

    # =========================================================================
    # TAB 6: KAALACHAKRA DASHA (DEHA & JIVA)
    # =========================================================================
    with tab_d6:
        st.markdown("#### 🔄 कालचक्र महादशा (Kaalachakra Dasha — BPHS)")
        st.caption("बृहत्पाराशर होरा शास्त्र अध्याय ४६ — देह व जीव राशियां, चक्र-गति (मण्डूक, मर्कटी, सिंहावलोकन) एवं आयुर्दाय प्रभाव:")
        try:
            kcd_res = kcd_engine.calculate(chart)
            act_kcd = None
            for item in kcd_res["timeline"]:
                try:
                    s_dt = datetime.strptime(item["start_date"], "%d-%b-%Y")
                    e_dt = datetime.strptime(item["end_date"], "%d-%b-%Y")
                    if s_dt <= target_dt <= e_dt:
                        act_kcd = item
                        break
                except Exception:
                    pass
            if not act_kcd and kcd_res["timeline"]:
                act_kcd = kcd_res["timeline"][0]

            b_str_kcd = (
                f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
                f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय कालचक्र दशा स्थिति (Active Kaalachakra Dasha Overview):</div>"
                f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
                f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🔄 सक्रिय राशि: {act_kcd['rashi']} ({act_kcd.get('role', '') or 'दशा'})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>👤 देह राशि: {kcd_res['deha_rashi']}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>❤️ जीव राशि: {kcd_res['jeeva_rashi']}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>🌀 गति: {act_kcd['gati'].split('/')[0]}</span>"
                f"</div>"
                f"</div>"
            )
            st.markdown(b_str_kcd, unsafe_allow_html=True)

            _gati_str = act_kcd.get('gati', '')
            if any(w in _gati_str for w in ["मंडूक", "मर्कटी", "सिंहावलोकन", "Jump", "Frog", "Monkey", "Lion"]):
                st.warning(f"""🚨 **कालचक्र विशेष छलांग (KCD Gati Alert — {_gati_str}):**
    वर्तमान कालचक्र महादशा में **{_gati_str}** सक्रिय है। 
    बृहत्पाराशर होरा शास्त्र (BPHS) अनुसार यह काल जातक के जीवन में आकस्मिक युगांतरकारी मोड़ लाता है — कार्यक्षेत्र में बड़ा परिवर्तन, पदोन्नति/स्थान परिवर्तन अथवा स्वास्थ्य व मानसिक स्थिति में तीव्र उतार-चढ़ाव। 
    विशेष सावधानी व महामृत्युंजय अनुष्ठान प्रशस्त रहेगा।""", icon="⚠️")

            col_kc1, col_kc2, col_kc3, col_kc4 = st.columns(4)
            with col_kc1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🔄 सक्रिय कालचक्र राशि</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_kcd['rashi']}</div>
    <div style="font-size:10.5px; color:#475569;">{act_kcd['start_date']} ~ {act_kcd['end_date']}</div>
    </div>""", unsafe_allow_html=True)
            with col_kc2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">👤 देह राशि (Deha Rashi)</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{kcd_res['deha_rashi']}</div>
    <div style="font-size:10.5px; color:#475569;">शारीरिक सुख व स्वास्थ्य</div>
    </div>""", unsafe_allow_html=True)
            with col_kc3:
                st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#B45309; font-weight:800;">❤️ जीव राशि (Jeeva Rashi)</div>
    <div style="font-size:18px; font-weight:900; color:#78350F;">{kcd_res['jeeva_rashi']}</div>
    <div style="font-size:10.5px; color:#475569;">मानसिक एवं आत्मिक शांति</div>
    </div>""", unsafe_allow_html=True)
            with col_kc4:
                st.markdown(f"""<div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#BE185D; font-weight:800;">✨ चक्र वर्ग एवं नक्षत्र</div>
    <div style="font-size:18px; font-weight:900; color:#831843;">{kcd_res['nakshatra']} (पद {kcd_res['pada']})</div>
    <div style="font-size:10.5px; color:#475569;">{kcd_res['group_type']}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            st.dataframe(pd.DataFrame(kcd_res["timeline"]), use_container_width=True)
            st.info("💡 **कालचक्र गति फल:** 'मण्डूक गति' (Frog Jump) अथवा 'सिंहावलोकन' (Lion's Gaze) की दशा में जीवन में अचानक बड़े परिवर्तन, स्थान परिवर्तन अथवा अप्रत्याशित उत्थान/पतन घटित होता है। देह राशि शारीरिक सुख-स्वास्थ्य और जीव राशि मानसिक व आत्मिक शांति का नियंत्रण करती है।")
        except Exception as _e_kcd:
            st.error(f"कालचक्र दशा गणना में त्रुटि: {_e_kcd}")

    # =========================================================================
    # TAB 7: SHOOLA DASHA (AYURDAYA & MARAKA)
    # =========================================================================
    with tab_d7:
        st.markdown("#### 🔱 शूल महादशा (Shoola Dasha — Ayurdaya & Maraka Timing)")
        st.caption("महर्षि जैमिनी प्रतिपादित शूल दशा — त्रिशूल राशियां, रुद्र स्थान, गंभीर स्वास्थ्य संकट व मारक समय निर्धारण:")
        try:
            shoola_res = shoola_engine.calculate(chart)
            act_shoola = None
            for item in shoola_res["timeline"]:
                try:
                    s_dt = datetime.strptime(item["start_date"], "%d-%b-%Y")
                    e_dt = datetime.strptime(item["end_date"], "%d-%b-%Y")
                    if s_dt <= target_dt <= e_dt:
                        act_shoola = item
                        break
                except Exception:
                    pass
            if not act_shoola and shoola_res["timeline"]:
                act_shoola = shoola_res["timeline"][0]

            b_str_shoola = (
                f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
                f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय शूल दशा एवं आयुर्दाय स्थिति (Active Shoola Dasha & Ayurdaya Status):</div>"
                f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
                f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🔱 सक्रिय शूल राशि: {act_shoola['sign']} ({act_shoola['duration_years']} वर्ष)</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>🎯 आरंभिक बीज राशि: {shoola_res['start_sign']}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ त्रिशूल राशियाँ: {', '.join(shoola_res['trishoola_signs'])}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>🛡️ जोखिम स्तर: {act_shoola['risk_level'].split('/')[0]}</span>"
                f"</div>"
                f"</div>"
            )
            st.markdown(b_str_shoola, unsafe_allow_html=True)

            col_sh1, col_sh2, col_sh3, col_sh4 = st.columns(4)
            with col_sh1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🔱 सक्रिय शूल दशा राशि</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_shoola['sign']}</div>
    <div style="font-size:10.5px; color:#475569;">{act_shoola['start_date']} ~ {act_shoola['end_date']}</div>
    </div>""", unsafe_allow_html=True)
            with col_sh2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">🎯 आरंभिक बीज राशि</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{shoola_res['start_sign']}</div>
    <div style="font-size:10.5px; color:#475569;">{shoola_res['direction']}</div>
    </div>""", unsafe_allow_html=True)
            with col_sh3:
                st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ त्रिशूल राशियाँ (Trishoola)</div>
    <div style="font-size:16px; font-weight:900; color:#78350F;">{', '.join(shoola_res['trishoola_signs'])}</div>
    <div style="font-size:10.5px; color:#475569;">रुद्रांश त्रिकोण राशियाँ</div>
    </div>""", unsafe_allow_html=True)
            with col_sh4:
                st.markdown(f"""<div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#BE185D; font-weight:800;">🛡️ वर्तमान जोखिम स्थिति</div>
    <div style="font-size:16px; font-weight:900; color:#831843;">{act_shoola['risk_level'].split('/')[0]}</div>
    <div style="font-size:10.5px; color:#475569;">ग्रह स्थिति: {act_shoola['occupants']}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            st.dataframe(pd.DataFrame(shoola_res["timeline"]), use_container_width=True)
            st.warning("⚠️ **शूल दशा शास्त्रीय उपयोग:** शूल दशा जातक के जीवन में स्वास्थ्य संकट, शल्यक्रिया (Surgery), दुर्घटना एवं मारक काल के सूक्ष्म परीक्षण हेतु उपयोग की जाती है। जब दशा त्रिशूल राशि में हो और उस पर क्रूर ग्रहों का प्रभाव हो, तो वह काल विशेष रूप से संवेदनशील होता है।")
        except Exception as _e_shoola:
            st.error(f"शूल दशा गणना में त्रुटि: {_e_shoola}")

    # =========================================================================
    # TAB 8: ASHTOTTARI DASHA (108 YEARS - 8 PLANETS)
    # =========================================================================
    with tab_d8:
        st.markdown("### 🕉️ अष्टोत्तरी दशा (Ashtottari Dasha — 108 वर्ष)")
        st.caption("बृहत्पाराशर होरा शास्त्र अनुसार १०८ वर्षीय नक्षत्र दशा — ८ ग्रह चक्र (राहु सहित, केतु रहित):")
        try:
            active_a = ashto_engine.get_active_dasha_at(chart, dasha_target_date)
            ca1, ca2, ca3 = st.columns(3)
            with ca1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">👑 अष्टोत्तरी महादशा</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{active_a['mahadasha']['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_a['mahadasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_a['mahadasha']['end_date'].strftime('%d-%b-%Y')}</div>
    </div>""", unsafe_allow_html=True)
            with ca2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">🪐 अंतर्दशा (Antar)</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{active_a['antardasha']['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_a['antardasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_a['antardasha']['end_date'].strftime('%d-%b-%Y')}</div>
    </div>""", unsafe_allow_html=True)
            with ca3:
                st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ प्रत्यंतर्दशा (Pratyantar)</div>
    <div style="font-size:18px; font-weight:900; color:#78350F;">{active_a['pratyantardasha']['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_a['pratyantardasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_a['pratyantardasha']['end_date'].strftime('%d-%b-%Y')}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            st.success(f"🌟 **सक्रिय दशा सूत्र:** {active_a['summary']}")

            with st.expander("📜 सम्पूर्ण १०८-वर्षीय अष्टोत्तरी कालक्रम", expanded=True):
                tl_a = ashto_engine.generate_timeline(chart)
                tl_a_rows = [{
                    "महादशा": md["lord"],
                    "प्रारम्भ": md["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति": md["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (वर्ष)": f"{md['duration_years']:.2f}",
                    "स्थिति": "⭐ वर्तमान सक्रिय" if md["start_date"] <= target_dt <= md["end_date"] else "—"
                } for md in tl_a[:16]]
                st.dataframe(pd.DataFrame(tl_a_rows), use_container_width=True, hide_index=True)

            with st.expander("🪐 सक्रिय महादशा के अंतर्गत अंतर्दशाएँ", expanded=True):
                ads = ashto_engine.generate_antardashas(active_a["mahadasha"]["lord"], active_a["mahadasha"]["start_date"], active_a["mahadasha"]["end_date"], active_a["mahadasha"].get("is_partial", False))
                ad_rows = [{
                    "अंतर्दशा स्वामी": ad["lord"],
                    "प्रारम्भ": ad["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति": ad["end_date"].strftime("%d-%b-%Y"),
                    "अवधि": f"{ad['duration_years']:.3f} वर्ष",
                    "स्थिति": "⭐ वर्तमान सक्रिय" if ad["start_date"] <= target_dt <= ad["end_date"] else "—"
                } for ad in ads]
                st.dataframe(pd.DataFrame(ad_rows), use_container_width=True, hide_index=True)

            st.info("📜 **अष्टोत्तरी दशा शास्त्रीय नियम:** BPHS अनुसार यदि जन्म कृष्ण पक्ष में दिन का हो अथवा शुक्ल पक्ष में रात्रि का हो, अथवा लग्न से केन्द्र/त्रिकोण में राहु स्थित हो, तो विंशोत्तरी के स्थान पर अष्टोत्तरी दशा विशेष सटीक फल देती है।")
        except Exception as e_a:
            st.error(f"अष्टोत्तरी दशा त्रुटि: {str(e_a)[:300]}")

    # =========================================================================
    # TAB 9: NARAYANA RASHI DASHA (JAIMINI)
    # =========================================================================
    with tab_d9:
        st.markdown("### 🪐 नारायण दशा (Narayana Rashi Dasha — Jaimini)")
        st.caption("महर्षि जैमिनी का सर्वश्रेष्ठ सार्वभौमिक राशि दशा फलित — आरंभ स्थान, पदक्रम एवं फल निर्धारण:")
        try:
            active_n = narayana_engine.get_active_dasha_at(chart, dasha_target_date)
            cn1, cn2 = st.columns(2)
            with cn1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🪐 नारायण महादशा (राशि)</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{active_n['mahadasha']['sign_name']}</div>
    <div style="font-size:10.5px; color:#475569;">अवधि: {active_n['mahadasha']['duration_years']} वर्ष ({active_n['mahadasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_n['mahadasha']['end_date'].strftime('%d-%b-%Y')})</div>
    </div>""", unsafe_allow_html=True)
            with cn2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">💫 अंतर्दशा (राशि)</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{active_n['antardasha']['sign_name']}</div>
    <div style="font-size:10.5px; color:#475569;">प्रारम्भ: {active_n['antardasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_n['antardasha']['end_date'].strftime('%d-%b-%Y')}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            st.success(f"🌟 **सक्रिय नारायण दशा:** {active_n['summary']}")

            with st.expander("📜 नारायण दशा सम्पूर्ण कालक्रम (12 राशियां)", expanded=True):
                tl_n = narayana_engine.generate_timeline(chart)
                tl_n_rows = [{
                    "राशि": md["sign_name"],
                    "स्वामी": md["lord"],
                    "प्रारम्भ": md["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति": md["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (वर्ष)": md["duration_years"],
                    "स्थिति": "⭐ वर्तमान सक्रिय" if md["start_date"] <= target_dt <= md["end_date"] else "—"
                } for md in tl_n]
                st.dataframe(pd.DataFrame(tl_n_rows), use_container_width=True, hide_index=True)

            st.info("💡 **जैमिनी सिद्धांत:** नारायण दशा में लग्न और सप्तम भाव में जो अधिक बली हो, वहां से दशा का आरंभ होता है। विषम राशियों से प्रत्यक्ष क्रम एवं सम राशियों से व्युत्क्रम (Apasavya) गणना की जाती है।")
        except Exception as e_n:
            st.error(f"नारायण दशा त्रुटि: {str(e_n)[:300]}")

    # =========================================================================
    # TAB 10: DWISAPTATI SAMA DASHA (72 YEARS)
    # =========================================================================
    with tab_d10:
        st.markdown("### ⏳ द्विसप्ततिसम दशा (Dwisaptati Sama Dasha — 72 वर्ष)")
        st.caption("पाराशर विशेष सम दशा — ७२ वर्ष, ८ ग्रह, प्रत्येक ग्रह की ९-९ वर्ष की सम-अवधि:")
        try:
            active_dw = dwisaptati_engine.get_active_dasha_at(chart, dasha_target_date)
            cdw1, cdw2 = st.columns(2)
            with cdw1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">⏳ महादशा स्वामी</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{active_dw['mahadasha']['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_dw['mahadasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_dw['mahadasha']['end_date'].strftime('%d-%b-%Y')}</div>
    </div>""", unsafe_allow_html=True)
            with cdw2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">🪐 अंतर्दशा स्वामी</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{active_dw['antardasha']['lord']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_dw['antardasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_dw['antardasha']['end_date'].strftime('%d-%b-%Y')}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            st.success(f"🌟 **सक्रिय द्विसप्ततिसम दशा:** {active_dw['summary']}")

            with st.expander("📜 द्विसप्ततिसम सम्पूर्ण कालक्रम", expanded=True):
                tl_dw = dwisaptati_engine.generate_timeline(chart)
                tl_dw_rows = [{
                    "महादशा": md["lord"],
                    "प्रारम्भ": md["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति": md["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (वर्ष)": f"{md['duration_years']:.2f}",
                    "स्थिति": "⭐ वर्तमान सक्रिय" if md["start_date"] <= target_dt <= md["end_date"] else "—"
                } for md in tl_dw[:16]]
                st.dataframe(pd.DataFrame(tl_dw_rows), use_container_width=True, hide_index=True)

            st.info("📜 **शास्त्रीय पात्रता नियम (BPHS Ch. 46):** 'मदे शे लग्नेशे मदे वा...' — यदि सप्तमेश लग्न में बैठा हो अथवा लग्नेश सप्तम भाव में स्थित हो, तब जातक की कुण्डली में द्विसप्ततिसम दशा साक्षात् फलित होती है।")
        except Exception as e_dw:
            st.error(f"द्विसप्ततिसम दशा त्रुटि: {str(e_dw)[:300]}")

    # =========================================================================
    # TAB 11: STHIRA DASHA (FIXED LONGEVITY)
    # =========================================================================
    with tab_d11:
        st.markdown("### 🔷 स्थिर दशा (Sthira Dasha — Jaimini Fixed)")
        st.caption("महर्षि जैमिनी प्रतिपादित स्थिर दशा — चर=७ वर्ष, स्थिर=८ वर्ष, द्विस्वभाव=९ वर्ष (ब्रह्मा ग्रह व आयु निर्धारण):")
        try:
            active_st = sthira_engine.get_active_dasha_at(chart, dasha_target_date)
            cst1, cst2 = st.columns(2)
            with cst1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🔷 स्थिर महादशा (राशि)</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{active_st['mahadasha']['sign_name']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_st['mahadasha']['type']} — {active_st['mahadasha']['duration_years']} वर्ष</div>
    </div>""", unsafe_allow_html=True)
            with cst2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">💫 अंतर्दशा (राशि)</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{active_st['antardasha']['sign_name']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_st['antardasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_st['antardasha']['end_date'].strftime('%d-%b-%Y')}</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            st.success(f"🌟 **सक्रिय स्थिर दशा:** {active_st['summary']}")

            with st.expander("📜 स्थिर दशा सम्पूर्ण कालक्रम (12 राशियां)", expanded=True):
                tl_st = sthira_engine.generate_timeline(chart)
                tl_st_rows = [{
                    "राशि": md["sign_name"],
                    "प्रकार": md["type"],
                    "प्रारम्भ": md["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति": md["end_date"].strftime("%d-%b-%Y"),
                    "वर्ष": md["duration_years"],
                    "स्थिति": "⭐ वर्तमान सक्रिय" if md["start_date"] <= target_dt <= md["end_date"] else "—"
                } for md in tl_st]
                st.dataframe(pd.DataFrame(tl_st_rows), use_container_width=True, hide_index=True)

            st.info("💡 **स्थिर दशा सिद्धांत:** स्थिर दशा में प्रत्येक राशि का काल पूर्व-निश्चित होता है (चर=७, स्थिर=८, द्विस्वभाव=९ वर्ष)। यह दशा ब्रह्म, महेश्वर एवं मारक राशि के प्रभाव से आयु व संकट का विश्लेषण करती है।")
        except Exception as e_st:
            st.error(f"स्थिर दशा त्रुटि: {str(e_st)[:300]}")

    # =========================================================================
    # TAB 12: DRIG DASHA (SPIRITUAL VISION)
    # =========================================================================
    with tab_d12:
        st.markdown("### 👁️ दृग दशा (Drig Dasha — Jaimini Spiritual Vision & Aspects)")
        st.caption("महर्षि जैमिनी की दृष्टि-आधारित आध्यात्मिक दशा — नवम भाव (धर्म/साधना) से आरंभ होकर दृष्टि क्रम अनुसार काल निर्धारण:")
        try:
            active_drig = drig_engine.get_active_dasha_at(chart, dasha_target_date)
            cd1, cd2 = st.columns(2)
            with cd1:
                st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">👁️ सक्रिय दृग महादशा (राशि)</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{active_drig['mahadasha']['sign_name']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_drig['mahadasha']['type']} ({active_drig['mahadasha']['duration_years']} वर्ष)</div>
    </div>""", unsafe_allow_html=True)
            with cd2:
                st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">🗓️ दशा कालखंड विस्तार</div>
    <div style="font-size:16px; font-weight:900; color:#064E3B;">{active_drig['mahadasha']['start_date'].strftime('%d-%b-%Y')} ~ {active_drig['mahadasha']['end_date'].strftime('%d-%b-%Y')}</div>
    <div style="font-size:10.5px; color:#475569;">आध्यात्मिक चिंतन व अंतर्ज्ञान का काल</div>
    </div>""", unsafe_allow_html=True)

            st.write("")
            st.success(f"👁️ **शास्त्रीय फलादेश:** वर्तमान में **{active_drig['mahadasha']['sign_name']}** राशि की दृग दशा प्रभावी है। यह काल आध्यात्मिक उन्नति, गुरु कृपा, तीर्थाटन, मंत्र सिद्धि एवं जीवन दर्शन को परिपक्व करने का सर्वोत्तम समय है।")

            with st.expander("📜 दृग दशा सम्पूर्ण समय-चक्र (Timeline)", expanded=True):
                tl_drig = drig_engine.generate_timeline(chart)
                tl_drig_rows = [{
                    "राशि (Sign)": md["sign_name"],
                    "प्रकृति (Type)": md["type"],
                    "आरंभ तिथि": md["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति तिथि": md["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (वर्ष)": md["duration_years"],
                    "स्थिति": "⭐ वर्तमान सक्रिय" if md["start_date"] <= target_dt <= md["end_date"] else "—"
                } for md in tl_drig]
                st.dataframe(pd.DataFrame(tl_drig_rows), use_container_width=True, hide_index=True)

            st.info("📜 **जैमिनी उपदेश सूत्र:** दृग दशा जातक के अंतःकरण के विकास, आंतरिक नेत्र के जागरण एवं ईश्वरीय साक्षात्कार की दिशा का बोध कराती है।")
        except Exception as e_dr:
            st.error(f"दृग दशा गणना त्रुटि: {str(e_dr)[:300]}")

    # =========================================================================
    # TAB 13: MULTI-DASHA CONVERGENCE MATRIX
    # =========================================================================
    with tab_d13:
        st.markdown("### 🎯 बहु-दशा सहमति एवं घटना संगम (Multi-Dasha Convergence Matrix)")
        st.caption(f"दिनांक **{dasha_target_date.strftime('%d-%b-%Y')}** पर विंशोत्तरी, योगिनी, चर, कालचक्र, शूल व नारायण दशाओं का संश्लेषित सहमति स्कोर:")

        try:
            # Active factors summary
            v_act_str = f"{act_m['lord']}-{act_a['lord']}-{act_pr['lord']}"
            y_act_str = f"{act_yog.get('yogini_name', act_yog.get('yogini'))} ({act_ya['yogini']})"
            c_act_str = f"{act_chara['sign_name']} ({act_ca['sign_name']})"
            k_act_str = f"{act_kcd['rashi']} (देह:{kcd_res['deha_rashi']}, जीव:{kcd_res['jeeva_rashi']})"
            s_act_str = f"{act_shoola['sign']} (जोखिम: {act_shoola['risk_level'].split('/')[0]})"

            # Domain Convergence Scoring
            # Assess lord placements in D1
            benefic_lords = {"Jupiter", "Venus", "Mercury", "Moon"}
            active_planets = [act_m['lord'], act_a['lord'], act_ya.get('lord', ''), act_ca.get('lord', '')]

            career_support = 0
            wealth_support = 0
            rel_support = 0
            health_alert = 0
            spirit_support = 0

            # Score by active planetary archetypes
            for p in active_planets:
                if p in ["Sun", "Mars", "Jupiter", "Saturn"]:
                    career_support += 22
                if p in ["Jupiter", "Venus", "Mercury", "Moon"]:
                    wealth_support += 24
                if p in ["Venus", "Jupiter", "Moon"]:
                    rel_support += 26
                if p in ["Saturn", "Rahu", "Mars", "Ketu"]:
                    health_alert += 20
                if p in ["Jupiter", "Ketu", "Sun", "Saturn"]:
                    spirit_support += 25

            # Factor in KCD and Shoola
            if "High" in act_shoola.get("risk_level", "") or "Moderate" in act_shoola.get("risk_level", ""):
                health_alert = min(95, health_alert + 25)
            if any(w in _gati_str for w in ["मंडूक", "मर्कटी", "सिंहावलोकन", "Jump"]):
                career_support = min(95, career_support + 15)

            c_score = min(95, max(30, career_support))
            w_score = min(95, max(35, wealth_support))
            r_score = min(95, max(25, rel_support))
            h_score = min(90, max(15, health_alert))
            s_score = min(95, max(30, spirit_support))

            # 4-Lane Parallel Multi-Dasha Gantt Timeline (Vimshottari, Yogini, Chara, KCD)
            try:
                parallel_html = dt_mod.default_dasha_timeline_service.render_multi_dasha_parallel_timeline_html(
                    chart, target_date=dasha_target_date, theme_mode=cur_th
                )
                components.html(parallel_html, height=450, scrolling=True)
            except Exception as _e_par:
                st.caption(f"समानांतर टाइमलाइन निर्माण: {_e_par}")

            # HUD Matrix Table
            matrix_data = [
                {"दशा प्रणाली": "🌟 विंशोत्तरी (५-स्तर)", "सक्रिय काल": v_act_str, "मुख्य स्वामी": act_m['lord'], "प्रभाव क्षेत्र": "जीवन की आधारभूत दिशा व कार्यकलाप"},
                {"दशा प्रणाली": "🌸 योगिनी (३-स्तर)", "सक्रिय काल": y_act_str, "मुख्य स्वामी": act_yog.get('lord', ''), "प्रभाव क्षेत्र": "तात्कालिक मनोदशा, संबंध व स्वास्थ्य"},
                {"दशा प्रणाली": "🔱 जैमिनी चर दशा", "सक्रिय काल": c_act_str, "मुख्य स्वामी": act_ca.get('lord', ''), "प्रभाव क्षेत्र": "कारक ग्रहों की सक्रियता व पदोन्नति"},
                {"दशा प्रणाली": "🔄 कालचक्र दशा", "सक्रिय काल": k_act_str, "मुख्य स्वामी": act_kcd.get('rashi', ''), "प्रभाव क्षेत्र": "देह-जीव संतुलन व आकस्मिक गति परिवर्तन"},
                {"दशा प्रणाली": "⚔️ शूल दशा", "सक्रिय काल": s_act_str, "मुख्य स्वामी": act_shoola.get('sign', ''), "प्रभाव क्षेत्र": "आयुर्दाय सतर्कता, शल्यक्रिया व मारक परीक्षण"}
            ]
            st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

            st.markdown("#### 🎯 बहु-दशा संगमित जीवन-आयाम संभावना सूचकांक (Convergence Gauge):")
            cg1, cg2 = st.columns(2)
            with cg1:
                st.markdown(f"💼 **करियर व प्रतिष्ठा संगमन अनुकूलता:** **{c_score}%**")
                st.progress(c_score / 100.0)
                st.markdown(f"💰 **धन वृद्धि व भौतिक समृद्धि सहमति:** **{w_score}%**")
                st.progress(w_score / 100.0)
                st.markdown(f"💍 **संबंध, विवाह व पारिवारिक सौहार्द:** **{r_score}%**")
                st.progress(r_score / 100.0)
            with cg2:
                st.markdown(f"🛡️ **स्वास्थ्य संवेदनशीलता / जोखिम सूचकांक:** **{h_score}%**")
                st.progress(h_score / 100.0)
                st.markdown(f"🕉️ **आध्यात्मिक प्रगति, ध्यान व विद्या:** **{s_score}%**")
                st.progress(s_score / 100.0)

            st.write("")
            consensus_level = "उच्च संगमन (High Consensus)" if c_score >= 70 or w_score >= 70 else "मध्यम संगमन (Moderate Consensus)"
            st.success(f"⚖️ **शास्त्रीय संगम निष्कर्ष:** तात्कालिक दशाओं में **{consensus_level}** परिलक्षित हो रहा है। जब विंशोत्तरी और जैमिनी चर दोनों एक साथ किसी भाव को सक्रिय करते हैं, तो उस कालखंड में घटना का घटित होना निश्चितप्राय माना जाता है।")
        except Exception as _e_conv:
            st.error(f"बहु-दशा संगम विश्लेषण में त्रुटि: {_e_conv}")

    # =========================================================================
    # TAB 14: BPHS CLASSICAL RULES & REMEDIES
    # =========================================================================
    with tab_d14:
        st.markdown("### 📜 दशा शास्त्रीय नियम, प्रमाण एवं वैदिक उपाय (Classical Rules & Remedial Suite)")
        st.caption("बृहत्पाराशर होरा शास्त्र एवं जैमिनी उपदेश सूत्रों के प्रामाणिक संदर्भ तथा सक्रिय दशा स्वामियों के शास्त्रीय अनुष्ठान:")

        with st.expander("📖 बृहत्पाराशर होरा शास्त्र (BPHS) मूल दशा सिद्धांत एवं प्रमाण", expanded=True):
            st.markdown("""**१. विंशोत्तरी दशा की सार्वभौमिकता (BPHS Ch. 38):**
    > *दशा विंशोत्तरी ज्ञेया सर्वत्रेव कलौ युगे। आयुषः परिमाणं तु शतं विंशतिवत्सरम्॥*
    > *कलियुग में मानव की परम आयु १२० वर्ष मानकर विंशोत्तरी दशा को सर्वश्रेष्ठ व सार्वभौमिक स्वीकार किया गया है।*

    **२. दशा सन्धि एवं छिद्र दशा सावधानी (Dasha Sandhi Caution):**
    > *दशामध्ये दशान्ते च महाकष्टं प्रजायते। विशेषतः क्रूरदशासन्धौ मृत्युतुल्यं फलम्॥*
    > जब एक महादशा समाप्त होकर दूसरी महादशा आरंभ होती है (विशेषकर राहु-गुरु, शनि-बुध, केतु-शुक्र संक्रमण), तो उस ६ माह से १ वर्ष के कालखंड को 'दशा संधि' अथवा 'छिद्र दशा' कहा जाता है। इसमें नवीन व्यापार, भारी निवेश अथवा जोखिमपूर्ण कार्यों में अत्यधिक संयम रखना चाहिए।

    **३. कालचक्र दशा का रहस्य (BPHS Ch. 46):**
    > *देहजीवसमायुक्ता कालचक्रदशा परा। देहं च पीडिते व्याधिर्जीवे तु मरणं ध्रुवम्॥*
    > जब क्रूर ग्रह देह राशि पर गोचर या दृष्टि डालते हैं, तो शरीर रोगग्रस्त होता है; और जब जीव राशि पर आक्रांत होते हैं, तो मानसिक व प्राण संकट उत्पन्न होता है।

    **४. अष्टोत्तरी दशा की पात्रता नियम (BPHS Ch. 46):**
    > *कृष्णे दिवा जन्म यस्य शुक्ले निशि भवेद् यदि। राहुश्च केन्द्रगो वापि तदाष्टोत्तरी शुभा॥*
    > कृष्ण पक्ष का दिन में जन्म हो अथवा शुक्ल पक्ष की रात्रि में जन्म हो, अथवा लग्नेश से केन्द्र/त्रिकोण में राहु बली हो, तब अष्टोत्तरी दशा का प्रत्यक्ष फल घटित होता है।""")

        with st.expander("🛡️ सक्रिय दशा स्वामियों हेतु वैदिक शास्त्रीय उपाय (Active Dasha Remedies)", expanded=True):
            m_lord = act_m.get('lord', 'Sun')
            a_lord = act_a.get('lord', 'Moon')

            remedy_catalog = {
                "Sun": {"mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", "gayatri": "ॐ आदित्याय विद्महे मार्तण्डाय धीमहि तन्नः सूर्यः प्रचोदयात्", "gem": "माणिक्य (Ruby) / ताम्र / लाल चंदन", "daan": "गेहूं, गुड़, ताम्र पात्र, लाल वस्त्र", "deity": "भगवान सूर्य नारायण / आदित्य हृदय स्तोत्र"},
                "Moon": {"mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्राय नमः", "gayatri": "ॐ क्षीरपुत्राय विद्महे अमृतत्त्वाय धीमहि तन्नश्चन्द्रः प्रचोदयात्", "gem": "मोती (Pearl) / चांदी / चंद्रकांत मणि", "daan": "चावल, श्वेत वस्त्र, दूध, शंख, चांदी", "deity": "भगवान शिव / शिव पंचाक्षर स्तोत्र"},
                "Mars": {"mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः", "gayatri": "ॐ अंगारकाय विद्महे शक्तिहस्ताय धीमहि तन्नो भौमः प्रचोदयात्", "gem": "मूंगा (Red Coral) / तांबा", "daan": "लाल मसूर, गुड़, लाल वस्त्र, कस्तूरी", "deity": "भगवान हनुमान जी / सुंदरकाण्ड"},
                "Mercury": {"mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः", "gayatri": "ॐ सौम्यरूपाय विद्महे वाणेशाय धीमहि तन्नो सौम्यः प्रचोदयात्", "gem": "पन्ना (Emerald) / कांसा / ओनेक्स", "daan": "हरी मूंग, हरा वस्त्र, कांस्य पात्र, फल", "deity": "भगवान गणेश जी / अथर्वशीर्ष"},
                "Jupiter": {"mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः", "gayatri": "ॐ अंगिरसाय विद्महे दिव्यदेहाय धीमहि तन्नो जीवः प्रचोदयात्", "gem": "पुखराज (Yellow Sapphire) / स्वर्ण / हल्दी", "daan": "चने की दाल, हल्दी, पीला वस्त्र, स्वर्ण, धार्मिक पुस्तकें", "deity": "भगवान दक्षिणामूर्ति / गुरु पादुका स्तोत्र"},
                "Venus": {"mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः", "gayatri": "ॐ भृगुजाय विद्महे दिव्यदेहाय धीमहि तन्नः शुक्रः प्रचोदयात्", "gem": "हीरा (Diamond) / ओपल / जरकन / श्वेत रेशम", "daan": "मिश्री, श्वेत वस्त्र, सुगंध, चावल, घी", "deity": "माता महालक्ष्मी / श्री सूक्त"},
                "Saturn": {"mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः", "gayatri": "ॐ काकध्वजाय विद्महे खड्गहस्ताय धीमहि तन्नो मन्दः प्रचोदयात्", "gem": "नीलम (Blue Sapphire) / जामुनिया / लौह / तिल तैल", "daan": "काले उड़द, तिल, सरसों का तेल, लौह पात्र, काला कंबल", "deity": "भगवान शनिदेव / दशरथ कृत शनि स्तोत्र"},
                "Rahu": {"mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः", "gayatri": "ॐ शिरोरूपाय विद्महे अमृतेशाय धीमहि तन्नो राहुः प्रचोदयात्", "gem": "गोमेद (Hessonite Garnet) / रांगा / सीसा", "daan": "सप्तधान्य, नारियल, काला-नीला वस्त्र, गोमेद", "deity": "माता दुर्गा / दुर्गा सप्तशती / भैरव कवच"},
                "Ketu": {"mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः", "gayatri": "ॐ गदाहस्ताय विद्महे अमृतेशाय धीमहि तन्नः केतुः प्रचोदयात्", "gem": "लहसुनिया (Cat's Eye) / पंचधातु", "daan": "तिल, कंबल, छाता, दोरंगा वस्त्र, लहसुनिया", "deity": "भगवान गणेश / कुलगुरु / महामृत्युंजय"}
            }

            m_rem = remedy_catalog.get(m_lord, remedy_catalog["Sun"])
            a_rem = remedy_catalog.get(a_lord, remedy_catalog["Moon"])

            cr1, cr2 = st.columns(2)
            with cr1:
                st.markdown(f"##### 👑 महादशा स्वामी ({m_lord}) शास्त्रीय अनुष्ठान")
                st.markdown(f"- 📿 **वैदिक बीज मंत्र:** `{m_rem['mantra']}` (१०८ जप)")
                st.markdown(f"- 🕉️ **गायत्री मंत्र:** `{m_rem['gayatri']}`")
                st.markdown(f"- 💎 **धारण रत्न / उपधातु:** {m_rem['gem']}")
                st.markdown(f"- 🎁 **प्रशस्त दान सामग्री:** {m_rem['daan']}")
                st.markdown(f"- 🛕 **आराध्य देव / स्तोत्र:** {m_rem['deity']}")

            with cr2:
                st.markdown(f"##### 🪐 अंतर्दशा स्वामी ({a_lord}) शास्त्रीय अनुष्ठान")
                st.markdown(f"- 📿 **वैदिक बीज मंत्र:** `{a_rem['mantra']}` (१०८ जप)")
                st.markdown(f"- 🕉️ **गायत्री मंत्र:** `{a_rem['gayatri']}`")
                st.markdown(f"- 💎 **धारण रत्न / उपधातु:** {a_rem['gem']}")
                st.markdown(f"- 🎁 **प्रशस्त दान सामग्री:** {a_rem['daan']}")
                st.markdown(f"- 🛕 **आराध्य देव / स्तोत्र:** {a_rem['deity']}")

        with st.expander("📜 सशर्त दशा पात्रता ऑडिट (Conditional Dasha Eligibility Audit — BPHS Ch. 46)", expanded=True):
            st.markdown("#### ⚖️ बृहत्पाराशर होरा शास्त्र अध्याय ४६ अनुसार विशेष दशाओं की पात्रता विश्लेषण:")
            try:
                cond_audit = default_shastriya_pramana_engine.evaluate_conditional_dasha_eligibility(chart)
                c_ashto = cond_audit["ashtottari"]
                c_shoda = cond_audit["shodashottari"]
                c_dwisa = cond_audit["dwisaptati"]
                c_shashti = cond_audit["shashtihayani"]

                cd_col1, cd_col2 = st.columns(2)
                with cd_col1:
                    badge_ashto = "🟢 **अधिकार प्राप्त (Eligible)**" if c_ashto["is_eligible"] else "⚪ सामान्य विंशोत्तरी लागू"
                    st.info(f"**{c_ashto['name']}**\n- **स्थिति:** {badge_ashto}\n- **शास्त्रीय तर्क:** {c_ashto['reason_hi']}")
                    badge_dwisa = "🟢 **अधिकार प्राप्त (Eligible)**" if c_dwisa["is_eligible"] else "⚪ सामान्य विंशोत्तरी लागू"
                    st.info(f"**{c_dwisa['name']}**\n- **स्थिति:** {badge_dwisa}\n- **शास्त्रीय तर्क:** {c_dwisa['reason_hi']}")
                with cd_col2:
                    badge_shoda = "🟢 **अधिकार प्राप्त (Eligible)**" if c_shoda["is_eligible"] else "⚪ सामान्य विंशोत्तरी लागू"
                    st.info(f"**{c_shoda['name']}**\n- **स्थिति:** {badge_shoda}\n- **शास्त्रीय तर्क:** {c_shoda['reason_hi']}")
                    badge_shashti = "🟢 **अधिकार प्राप्त (Eligible)**" if c_shashti["is_eligible"] else "⚪ सामान्य विंशोत्तरी लागू"
                    st.info(f"**{c_shashti['name']}**\n- **स्थिति:** {badge_shashti}\n- **शास्त्रीय तर्क:** {c_shashti['reason_hi']}")

                shl = cond_audit["shastriya_shloka"]
                shl_lines = "<br/>".join(shl['shloka'].splitlines())
                st.markdown(f"""
    <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 6px; margin-top: 10px;">
    <div style="font-weight: 700; color: #B45309; font-size: 13px; margin-bottom: 4px;">📖 {shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #1E293B;">
        {shl_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12px; color: #475569; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11px; color: #6B7280;">
        <b>शास्त्रीय नियम:</b> {shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)
            except Exception as _e_cond:
                st.caption(f"सशर्त दशा विश्लेषण: {_e_cond}")



