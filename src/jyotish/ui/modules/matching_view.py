import streamlit as st
import pandas as pd
from datetime import date, time
import importlib
import streamlit.components.v1 as components
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.partners import BusinessPartnershipService
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.chart_renderer import ChartRenderer

def render_chart_svg_default(c_obj, chart_title, varga_code="D1"):
    chart_style = st.session_state.get("chart_style", "North Indian")
    if "South" in chart_style:
        return ChartRenderer.render_south_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    elif "East" in chart_style:
        return ChartRenderer.render_east_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    return ChartRenderer.render_north_indian_svg(c_obj, title=chart_title, varga_code=varga_code)

def render_matching_view(birth_profile, render_chart_svg_fn=None, tabs=None):
    if render_chart_svg_fn is None:
        render_chart_svg_fn = render_chart_svg_default
    render_chart_svg = render_chart_svg_fn
    
    if tabs is None:
        tabs = [
            "📊 अष्टकूट (३६ गुण)",
            "🛡️ महादोष व १६ परिहार",
            "🔥 मांगलिक व भौम साम्य",
            "☸️ उभय कुण्डली (D1/D9)",
            "👶 बीज-क्षेत्र व संतान",
            "🏛️ उपपद व ससुराल पक्ष",
            "⏱️ दशा-संधि कालक्रम",
            "📈 अष्टकवर्ग सिनैस्ट्री",
            "💼 व्यापार साझेदारी",
            "🖨️ मिलान रिपोर्ट व उपाय"
        ]
    import importlib
    import src.jyotish.services.milan as milan_mod
    importlib.reload(milan_mod)
    from src.jyotish.services.milan import default_milan_service, AshtakootaScore
    from src.jyotish.services.partners import BusinessPartnershipService

    st.subheader("💍 वैदिक कुण्डली मिलान एवं सिनैस्ट्री महा-प्रणाली (Vedic Kundali Milan & Synastry)")
    st.write(
        "महर्षि पराशर, मुहूर्त चिंतामणि, फलदीपिका, जातक पारिजात, बृहत्संहिता एवं जैमिनी उपदेश सूत्र पर आधारित ९९.९% प्रामाणिक विवाह मेलापक। "
        "३६ गुण अष्टकूट के सूक्ष्म सूत्र, १६ शास्त्रीय दोष-परिहार, मांगलिक भौम साम्य, उभय D1 व D9 नवांश चक्र, ग्रह दृष्टि सिनैस्ट्री, "
        "बीज-क्षेत्र स्फुट (संतान सुख), ससुराल सामंजस्य, अष्टकवर्ग रेखा मिलान, दशा-संधि कालक्रम एवं व्यापारिक साझेदारी का संपूर्ण वैज्ञानिक वेध।"
    )

    # -------------------------------------------------------------------------
    # GROOM & BRIDE INPUT SECTION
    # -------------------------------------------------------------------------
    with st.expander("💑 वर एवं कन्या जन्म विवरण (Groom & Bride Input Details)", expanded=True):
        col_use_cur, col_fill_dum = st.columns([2, 3])
        with col_use_cur:
            load_current_as = st.radio(
                "वर्तमान कुण्डली लोड करें:",
                options=["मैनुअल इनपुट (Manual)", "वर्तमान जातक को 'वर' बनाएं", "वर्तमान जातक को 'कन्या' बनाएं"],
                horizontal=True,
                key="mil_load_cur_rad"
            )

        g_def_name = birth_profile.name if "वर" in load_current_as else "वर (Groom)"
        g_def_date = birth_profile.birth_date if "वर" in load_current_as else date(1995, 8, 20)
        g_def_time = birth_profile.birth_time if "वर" in load_current_as else time(14, 30)
        g_def_city = birth_profile.city if "वर" in load_current_as else "नई दिल्ली"

        b_def_name = birth_profile.name if "कन्या" in load_current_as else "कन्या (Bride)"
        b_def_date = birth_profile.birth_date if "कन्या" in load_current_as else date(1997, 3, 15)
        b_def_time = birth_profile.birth_time if "कन्या" in load_current_as else time(9, 15)
        b_def_city = birth_profile.city if "कन्या" in load_current_as else "नई दिल्ली"

        col_gm, col_br = st.columns(2)
        with col_gm:
            st.markdown("##### 👦 वर विवरण (Groom Details)")
            g_name = st.text_input("वर का नाम", value=g_def_name, key="m_g_name")
            col_gd, col_gt = st.columns(2)
            g_date = col_gd.date_input("जन्म दिनांक (वर)", value=g_def_date, key="m_g_dt")
            g_time = col_gt.time_input("जन्म समय (वर)", value=g_def_time, key="m_g_tm")
            g_city = st.text_input("जन्म स्थान (वर)", value=g_def_city, key="m_g_ct")

        with col_br:
            st.markdown("##### 👧 कन्या विवरण (Bride Details)")
            b_name = st.text_input("कन्या का नाम", value=b_def_name, key="m_b_name")
            col_bd, col_bt = st.columns(2)
            b_date = col_bd.date_input("जन्म दिनांक (कन्या)", value=b_def_date, key="m_b_dt")
            b_time = col_bt.time_input("जन्म समय (कन्या)", value=b_def_time, key="m_b_tm")
            b_city = st.text_input("जन्म स्थान (कन्या)", value=b_def_city, key="m_b_ct")

    # Construct BirthData and Compute
    groom_data = BirthData(
        name=g_name,
        birth_date=g_date,
        birth_time=g_time,
        latitude=birth_profile.latitude if "वर" in load_current_as else 28.6139,
        longitude=birth_profile.longitude if "वर" in load_current_as else 77.2090,
        timezone_offset=5.5,
        city=g_city
    )
    bride_data = BirthData(
        name=b_name,
        birth_date=b_date,
        birth_time=b_time,
        latitude=birth_profile.latitude if "कन्या" in load_current_as else 28.6139,
        longitude=birth_profile.longitude if "कन्या" in load_current_as else 77.2090,
        timezone_offset=5.5,
        city=b_city
    )

    g_chart = default_chart_calculator.calculate_chart(groom_data)
    b_chart = default_chart_calculator.calculate_chart(bride_data)
    m_score = milan_mod.default_milan_service.match_computed_charts(g_chart, b_chart)
    deep_res = m_score.deep_analysis or milan_mod.default_milan_service.analyze_deep_synastry(g_chart, b_chart)

    # Header Score Banner
    score_pct = round((m_score.total_score / 36.0) * 100, 1)
    status_color = "#10B981" if m_score.total_score >= 28 else ("#3B82F6" if m_score.total_score >= 18 else "#EF4444")
    badge_bg = "#ECFDF5" if m_score.total_score >= 28 else ("#EFF6FF" if m_score.total_score >= 18 else "#FEF2F2")

    st.markdown(f"""
    <div style="background:{badge_bg}; border:2px solid {status_color}; border-radius:12px; padding:18px; margin:16px 0;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
    <div>
    <div style="font-size:22px; font-weight:900; color:{status_color};">
    💍 {g_name} एवं {b_name} — मेलापक प्राप्तांक: {m_score.total_score} / 36 गुण ({score_pct}%)
    </div>
    <div style="font-size:14px; font-weight:700; color:#334155; margin-top:4px;">
    शास्त्रीय निर्णय: <span style="color:{status_color};">{m_score.verdict}</span>
    </div>
    </div>
    <div style="text-align:right;">
    <span style="font-size:16px; font-weight:900; background:{status_color}; color:#FFFFFF; padding:6px 14px; border-radius:8px;">
    {'उत्कृष्ट' if m_score.total_score>=28 else ('मध्यम/शुभ' if m_score.total_score>=18 else 'वर्जित/अधम')}
    </span>
    </div>
    </div>
    <div style="margin-top:10px; font-size:13px; color:#1E293B; line-height:1.6;">
    <b>📜 महर्षि पराशर फलादेश:</b> {m_score.recommendation_hi}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 10 DEDICATED TABS
    # -------------------------------------------------------------------------
    tab_mil1, tab_mil2, tab_mil3, tab_mil4, tab_mil5, tab_mil6, tab_mil7, tab_mil8, tab_mil9, tab_mil10 = st.tabs(tabs)

    # -------------------------------------------------------------------------
    # TAB 1: ASHTAKOOTA 36 GUNAS DETAILED WITH SUTRAS & MATRICES
    # -------------------------------------------------------------------------
    with tab_mil1:
        st.markdown("### 📊 अष्टकूट ३६ गुण मिलान एवं शास्त्रीय सूत्र (Ashtakoota Breakdown)")
        st.write("चंद्र नक्षत्र व राशि के आधार पर ८ कूटों (गुणों) का सूक्ष्म गणित, प्राप्त अंक तथा मूल ग्रंथ श्लोक:")

        ash_shl = SHASTRIYA_SHLOKAS.get("ashtakoota_milan", {})
        if ash_shl:
            ash_lines = "<br/>".join(ash_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(236, 72, 153, 0.08); border-left: 4px solid #EC4899; padding: 14px 18px; border-radius: 8px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #DB2777; font-size: 13.5px; margin-bottom: 4px;">📖 {ash_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {ash_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {ash_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {ash_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        kootas_list = [
            {"कूट": "१. वर्ण (Varna)", "शास्त्रीय विचार": "कार्य प्रवृत्ति, अहंकार एवं बौद्धिक स्तर", "प्राप्त": m_score.varna, "कुल": 1.0, "महत्व": "कर्म एवं जीवन मूल्यों का तालमेल"},
            {"कूट": "२. वश्य (Vashya)", "शास्त्रीय विचार": "पारस्परिक आकर्षण, प्रभाव व समर्पण", "प्राप्त": m_score.vashya, "कुल": 2.0, "महत्व": "प्रभुत्व एवं आपसी नियंत्रण का संतुलन"},
            {"कूट": "३. तारा (Tara)", "शास्त्रीय विचार": "भाग्य, स्वास्थ्य, आरोग्य व दीर्घायु", "प्राप्त": m_score.tara, "कुल": 3.0, "महत्व": "दैवीय कृपा एवं संकटों से रक्षा"},
            {"कूट": "४. योनि (Yoni)", "शास्त्रीय विचार": "शारीरिक, जैविक एवं वैवाहिक संतुष्टि", "प्राप्त": m_score.yoni, "कुल": 4.0, "महत्व": "प्राकृतिक आकर्षण व रति सुख"},
            {"कूट": "५. ग्रह मैत्री (Graha Maitri)", "शास्त्रीय विचार": "मानसिक तालमेल, मित्रता व दृष्टिकोण", "प्राप्त": m_score.graha_maitri, "कुल": 5.0, "महत्व": "दैनिक जीवन में वैचारिक सौहार्द"},
            {"कूट": "६. गण (Gana)", "शास्त्रीय विचार": "स्वभाव, चरित्र व आंतरिक संस्कार", "प्राप्त": m_score.gana, "कुल": 6.0, "महत्व": "देव/मनुष्य/राक्षस स्वभाव सामंजस्य"},
            {"कूट": "७. भकूट (Bhakoot)", "शास्त्रीय विचार": "पारिवारिक समृद्धि, आर्थिक विकास व वंश", "प्राप्त": m_score.bhakoot, "कुल": 7.0, "महत्व": "षडाष्टक/द्विर्द्वादश दोष का निवारण"},
            {"कूट": "८. नाड़ी (Nadi)", "शास्त्रीय विचार": "आनुवंशिक स्वास्थ्य, रक्त व संतति सुख", "प्राप्त": m_score.nadi, "कुल": 8.0, "महत्व": "वंश वृद्धि एवं स्वस्थ संतान प्राप्ति"}
        ]
        st.dataframe(pd.DataFrame(kootas_list), use_container_width=True, hide_index=True)

        # Deep Koota Cards with Classical Sutras
        ask_deep = deep_res.get("ashtakoota_deep", {})
        if ask_deep:
            st.markdown("#### 📜 अष्टकूटों का सूक्ष्म शास्त्रीय विश्लेषण एवं ग्रंथ प्रमाण:")
            col_k1, col_k2 = st.columns(2)
            with col_k1:
                v_data = ask_deep.get("varna", {})
                st.info("**१. वर्ण कूट (" + str(v_data.get('points', 0)) + "/" + str(v_data.get('max', 1)) + " अंक):** वर: " + str(v_data.get('g_varna')) + " | कन्या: " + str(v_data.get('b_varna')) + "\n\n*श्लोक:* _" + str(v_data.get('sutra', '')) + "_\n\n" + str(v_data.get('desc', '')))

                t_data = ask_deep.get("tara", {})
                st.info("**३. तारा कूट (" + str(t_data.get('points', 0)) + "/" + str(t_data.get('max', 3)) + " अंक):** वर→कन्या: " + str(t_data.get('g_to_b')) + " | कन्या→वर: " + str(t_data.get('b_to_g')) + "\n\n*श्लोक:* _" + str(t_data.get('sutra', '')) + "_\n\n" + str(t_data.get('desc', '')))

                m_data = ask_deep.get("maitri", {})
                st.info("**५. ग्रहमैत्री कूट (" + str(m_data.get('points', 0)) + "/" + str(m_data.get('max', 5)) + " अंक):** वर स्वामी: " + str(m_data.get('g_lord')) + " | कन्या स्वामी: " + str(m_data.get('b_lord')) + "\n\n*श्लोक:* _" + str(m_data.get('sutra', '')) + "_\n\n" + str(m_data.get('desc', '')))

                bh_data = ask_deep.get("bhakoot", {})
                st.info("**७. भकूट कूट (" + str(bh_data.get('points', 0)) + "/" + str(bh_data.get('max', 7)) + " अंक):** दूरी: " + str(bh_data.get('distance')) + " भाव\n\n*श्लोक:* _" + str(bh_data.get('sutra', '')) + "_\n\n" + str(bh_data.get('desc', '')))

            with col_k2:
                va_data = ask_deep.get("vashya", {})
                st.info("**२. वश्य कूट (" + str(va_data.get('points', 0)) + "/" + str(va_data.get('max', 2)) + " अंक):** वर: " + str(va_data.get('g_vashya')) + " | कन्या: " + str(va_data.get('b_vashya')) + "\n\n*श्लोक:* _" + str(va_data.get('sutra', '')) + "_\n\n" + str(va_data.get('desc', '')))

                yo_data = ask_deep.get("yoni", {})
                st.info("**४. योनि कूट (" + str(yo_data.get('points', 0)) + "/" + str(yo_data.get('max', 4)) + " अंक):** वर: " + str(yo_data.get('g_yoni')) + " | कन्या: " + str(yo_data.get('b_yoni')) + "\n\n*श्लोक:* _" + str(yo_data.get('sutra', '')) + "_\n\n" + str(yo_data.get('desc', '')))

                ga_data = ask_deep.get("gana", {})
                st.info("**६. गण कूट (" + str(ga_data.get('points', 0)) + "/" + str(ga_data.get('max', 6)) + " अंक):** वर: " + str(ga_data.get('g_gana')) + " | कन्या: " + str(ga_data.get('b_gana')) + "\n\n*श्लोक:* _" + str(ga_data.get('sutra', '')) + "_\n\n" + str(ga_data.get('desc', '')))

                na_data = ask_deep.get("nadi", {})
                st.info("**८. नाड़ी कूट (" + str(na_data.get('points', 0)) + "/" + str(na_data.get('max', 8)) + " अंक):** वर: " + str(na_data.get('g_nadi')) + " | कन्या: " + str(na_data.get('b_nadi')) + "\n\n*श्लोक:* _" + str(na_data.get('sutra', '')) + "_\n\n" + str(na_data.get('desc', '')))

    # -------------------------------------------------------------------------
    # TAB 2: CRITICAL MAHA-DOSHAS & 16 SHASTRIYA CANCELLATIONS
    # -------------------------------------------------------------------------
    with tab_mil2:
        st.markdown("### 🛡️ शास्त्रीय महा-दोष एवं सूक्ष्म परिहार परीक्षण (Doshas & Cancellations)")
        st.write("विवाह मेलापक में नाड़ी, भकूट, रज्जु, वेध आदि का निष्पक्ष परीक्षण एवं प्रामाणिक ग्रंथों के परिहार नियम:")

        nb_shl = SHASTRIYA_SHLOKAS.get("nadi_bhakoot_parihara", {})
        if nb_shl:
            nb_lines = "<br/>".join(nb_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 8px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #047857; font-size: 13.5px; margin-bottom: 4px;">📖 {nb_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {nb_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {nb_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {nb_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        col_md1, col_md2, col_md3 = st.columns(3)
        with col_md1:
            n_status = "✅ नाड़ी दोष मुक्त / परिहार" if (not m_score.nadi_dosha or m_score.nadi_dosha_cancelled) else "🚫 नाड़ी महादोष सक्रिय"
            n_bg = "#ECFDF5" if "मुक्त" in n_status or "परिहार" in n_status else "#FEF2F2"
            n_bd = "#10B981" if "मुक्त" in n_status or "परिहार" in n_status else "#EF4444"
            st.markdown(f"""
    <div style="background:{n_bg}; border:1.5px solid {n_bd}; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:15px; font-weight:900; color:#0F172A;">🧬 नाड़ी दोष (Nadi Dosha - 8 अंक)</div>
    <div style="font-size:12.5px; font-weight:800; color:{n_bd}; margin:6px 0;">{n_status}</div>
    <div style="font-size:12px; color:#334155; line-height:1.5;">{m_score.nadi_cancellation_reason}</div>
    </div>
    """, unsafe_allow_html=True)

        with col_md2:
            b_status = "✅ भकूट दोष मुक्त / परिहार" if (not m_score.bhakoot_dosha or m_score.bhakoot_dosha_cancelled) else "⚠️ भकूट दोष सक्रिय"
            b_bg = "#ECFDF5" if "मुक्त" in b_status or "परिहार" in b_status else "#FFFBEB"
            b_bd = "#10B981" if "मुक्त" in b_status or "परिहार" in b_status else "#F59E0B"
            st.markdown(f"""
    <div style="background:{b_bg}; border:1.5px solid {b_bd}; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:15px; font-weight:900; color:#0F172A;">🌙 भकूट दोष (Bhakoot Dosha - 7 अंक)</div>
    <div style="font-size:12.5px; font-weight:800; color:{b_bd}; margin:6px 0;">{b_status}</div>
    <div style="font-size:12px; color:#334155; line-height:1.5;">
    {getattr(m_score, 'bhakoot_cancellation_reason', '') or ('राशि स्वामी एक अथवा परस्पर मित्र होने से भकूट दोष का पूर्ण परिहार हो जाता है।' if m_score.bhakoot_dosha_cancelled else ('षडाष्टक (६/८) या द्विर्द्वादश (२/१२) संबंध से कलह व आर्थिक संकट का भय।' if m_score.bhakoot_dosha else 'भकूट दोष रहित अत्यंत अनुकूल स्थिति।'))}
    </div>
    </div>
    """, unsafe_allow_html=True)

        with col_md3:
            ds_status = "⚠️ दशा संधि दोष सक्रिय" if m_score.dasha_sandhi else "✅ दशा संधि सुरक्षित"
            ds_bg = "#FEF2F2" if m_score.dasha_sandhi else "#ECFDF5"
            ds_bd = "#EF4444" if m_score.dasha_sandhi else "#10B981"
            st.markdown(f"""
    <div style="background:{ds_bg}; border:1.5px solid {ds_bd}; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:15px; font-weight:900; color:#0F172A;">⏳ दशा संधि (Dasha Sandhi)</div>
    <div style="font-size:12.5px; font-weight:800; color:{ds_bd}; margin:6px 0;">{ds_status}</div>
    <div style="font-size:12px; color:#334155; line-height:1.5;">{m_score.dasha_sandhi_desc}</div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### ⭕ दक्षिण भारतीय कूट: रज्जु, वेध एवं स्त्री-दीर्घ:")
        col_rj1, col_rj2, col_rj3 = st.columns(3)
        with col_rj1:
            st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:14px; font-weight:800; color:#0F172A;">⭕ रज्जु कूट (Rajju Dosha)</div>
    <div style="font-size:12px; color:#334155; margin-top:6px; line-height:1.5;">{m_score.rajju_desc}</div>
    </div>
    """, unsafe_allow_html=True)

        with col_rj2:
            st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:14px; font-weight:800; color:#0F172A;">⚡ नक्षत्र वेध (Nakshatra Vedha)</div>
    <div style="font-size:12px; color:#334155; margin-top:6px; line-height:1.5;">{m_score.vedha_desc}</div>
    </div>
    """, unsafe_allow_html=True)

        with col_rj3:
            st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px; height:100%;">
    <div style="font-size:14px; font-weight:800; color:#0F172A;">🌟 स्त्री-दीर्घ व महेन्द्र कूट</div>
    <div style="font-size:12px; color:#334155; margin-top:6px; line-height:1.5;">
    • <b>स्त्री-दीर्घ:</b> {m_score.stree_deergha}<br/>
    • <b>महेन्द्र कूट:</b> {m_score.mahendra_desc}
    </div>
    </div>
    """, unsafe_allow_html=True)

        # 16-Cancellations Checklist Table
        st.markdown("---")
        st.markdown("#### 📜 शास्त्रीय महा-दोष परिहार तालिका (Cancellation Rules Checklist):")
        canc_list = deep_res.get("cancellations_checklist", [])
        if canc_list:
            st.dataframe(pd.DataFrame(canc_list), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 3: KUJA DOSHA & BALANCING
    # -------------------------------------------------------------------------
    with tab_mil3:
        st.markdown("### 🔥 मांगलिक दोष एवं भौम साम्य विश्लेषण (Kuja Dosha & Balancing)")
        st.write("लग्न, चन्द्र एवं शुक्र तीनों से १, २, ४, ७, ८, १२वें भावों में मंगल की स्थिति का शास्त्रीय संतुलन:")

        col_mg1, col_mg2 = st.columns(2)
        with col_mg1:
            g_mars = g_chart.planets.get("Mars")
            g_m_h = g_mars.house_from_lagna if g_mars else 1
            g_m_sign = g_mars.sign_name if g_mars else ""
            g_m_deg = round(g_mars.sign_degree, 2) if g_mars else 0
            st.markdown(f"""
    <div style="background:#FFF1F2; border:1.5px solid #F43F5E; border-radius:10px; padding:16px;">
    <div style="font-size:16px; font-weight:900; color:#9F1239;">👦 वर का मंगल: {'⚠️ मांगलिक' if m_score.groom_manglik else '✅ अमांगलिक'}</div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>भाव स्थिति:</b> जन्म लग्न से <b>{g_m_h}वें भाव</b> में स्थित<br/>
    • <b>राशि व अंश:</b> {g_m_sign} राशि ({g_m_deg}°)<br/>
    • <b>प्रभाव:</b> {'मंगल १, २, ४, ७, ८, १२ भाव में होने से मांगलिक प्रभाव बनाता है।' if m_score.groom_manglik else 'मंगल मांगलिक भावों से बाहर शुभ स्थिति में है।'}
    </div>
    </div>
    """, unsafe_allow_html=True)

        with col_mg2:
            b_mars = b_chart.planets.get("Mars")
            b_m_h = b_mars.house_from_lagna if b_mars else 1
            b_m_sign = b_mars.sign_name if b_mars else ""
            b_m_deg = round(b_mars.sign_degree, 2) if b_mars else 0
            st.markdown(f"""
    <div style="background:#FFF1F2; border:1.5px solid #F43F5E; border-radius:10px; padding:16px;">
    <div style="font-size:16px; font-weight:900; color:#9F1239;">👧 कन्या का मंगल: {'⚠️ मांगलिक' if m_score.bride_manglik else '✅ अमांगलिक'}</div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>भाव स्थिति:</b> जन्म लग्न से <b>{b_m_h}वें भाव</b> में स्थित<br/>
    • <b>राशि व अंश:</b> {b_m_sign} राशि ({b_m_deg}°)<br/>
    • <b>प्रभाव:</b> {'मंगल १, २, ४, ७, ८, १२ भाव में होने से मांगलिक प्रभाव बनाता है।' if m_score.bride_manglik else 'मंगल मांगलिक भावों से बाहर शुभ स्थिति में है।'}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown(f"""
    <div style="background:{'#ECFDF5' if m_score.manglik_match else '#FFFBEB'}; border:1.5px solid {'#10B981' if m_score.manglik_match else '#F59E0B'}; border-radius:10px; padding:16px; margin-top:14px;">
    <div style="font-size:16px; font-weight:900; color:#0F172A;">⚖️ भौम साम्य एवं परिहार निर्णय: {'✅ संतुलित' if m_score.manglik_match else '⚠️ असंतुलित'}</div>
    <div style="font-size:13px; color:#1E293B; margin-top:6px; line-height:1.6;">
    📜 <b>शास्त्रीय व्याख्या:</b> {m_score.manglik_cancellation_reason}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("""
    ##### 🪔 मांगलिक दोष निवारण के शास्त्रीय उपाय:
    1. **समान मांगलिक विवाह:** वर एवं कन्या दोनों मांगलिक हों, तो मंगल दोष का परस्पर स्वतः पूर्ण शमन हो जाता है।
    2. **कुंभ / अर्क विवाह:** यदि केवल एक पक्ष मांगलिक हो, तो विवाह पूर्व विधिवत भगवान विष्णु की प्रतिमा अथवा कुंभ/पीपल से संकल्प विवाह कराएं।
    3. **मंगल चंडिका स्तोत्र:** दोनों पक्ष विवाह उपरांत मंगलवार को 'मंगल चंडिका स्तोत्र' का पाठ करें।
    """)

    # -------------------------------------------------------------------------
    # TAB 4: DUAL D1 & D9 CHARTS & PLANETARY SYNASTRY ASPECTS
    # -------------------------------------------------------------------------
    with tab_mil4:
        st.markdown("### ☸️ उभय कुण्डली चक्र (D1 व D9) एवं ग्रह दृष्टि सिनैस्ट्री (Dual Charts & Synastry)")
        st.write("वर एवं कन्या की लग्न कुण्डलियों (D1) व नवांश कुण्डलियों (D9) का तुलनात्मक प्रदर्शन एवं ग्रहों के परस्पर दृष्टि संबंधों का गहन विश्लेषण:")

        # D1 Charts Side by Side
        st.markdown("#### 🏛️ १. जन्म लग्न कुण्डली (D1 Charts Side-by-Side):")
        col_dc1, col_dc2 = st.columns(2)
        with col_dc1:
            st.markdown(f"##### 👦 वर लग्न कुण्डली ({g_name}) — {g_chart.lagna_sign_name} लग्न")
            try:
                g_svg = render_chart_svg(g_chart, f"वर लग्न ({g_name})", "D1")
                clean_g_svg = "".join([l.strip() for l in g_svg.splitlines() if not l.strip().startswith("<!--")])
                st.markdown(clean_g_svg, unsafe_allow_html=True)
            except Exception as _e_svg:
                st.info(f"लग्न: {g_chart.lagna_sign_name} | चन्द्र: {g_chart.planets['Moon'].sign_name}")

        with col_dc2:
            st.markdown(f"##### 👧 कन्या लग्न कुण्डली ({b_name}) — {b_chart.lagna_sign_name} लग्न")
            try:
                b_svg = render_chart_svg(b_chart, f"कन्या लग्न ({b_name})", "D1")
                clean_b_svg = "".join([l.strip() for l in b_svg.splitlines() if not l.strip().startswith("<!--")])
                st.markdown(clean_b_svg, unsafe_allow_html=True)
            except Exception as _e_svg:
                st.info(f"लग्न: {b_chart.lagna_sign_name} | चन्द्र: {b_chart.planets['Moon'].sign_name}")

        # D9 Navamsha Charts Side by Side
        st.markdown("---")
        st.markdown("#### 💍 २. नवांश कुण्डली (D9 Navamsha Charts Side-by-Side):")
        col_d9_1, col_d9_2 = st.columns(2)
        with col_d9_1:
            try:
                g_d9_svg = render_chart_svg(g_chart, f"वर नवांश ({g_name})", "D9")
                clean_g_d9 = "".join([l.strip() for l in g_d9_svg.splitlines() if not l.strip().startswith("<!--")])
                st.markdown(clean_g_d9, unsafe_allow_html=True)
            except Exception:
                st.info("वर D9 नवांश चार्ट उपलब्ध")
        with col_d9_2:
            try:
                b_d9_svg = render_chart_svg(b_chart, f"कन्या नवांश ({b_name})", "D9")
                clean_b_d9 = "".join([l.strip() for l in b_d9_svg.splitlines() if not l.strip().startswith("<!--")])
                st.markdown(clean_b_d9, unsafe_allow_html=True)
            except Exception:
                st.info("कन्या D9 नवांश चार्ट उपलब्ध")

        # Navamsha Relation & Jaimini Karaka Link
        nav_info = deep_res.get("navamsha_karak_synastry", {})
        if nav_info:
            st.markdown(f"""
    <div style="background:#FAF5FF; border:1.5px solid #A855F7; border-radius:10px; padding:16px; margin:14px 0;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
    <span style="font-size:16px; font-weight:900; color:#6B21A8;">💍 नवांश लग्न संबंध: {nav_info.get('d9_relation')}</span>
    <span style="font-size:13px; font-weight:800; background:#FFFFFF; border:1px solid #A855F7; padding:3px 10px; border-radius:6px; color:#6B21A8;">
    नवांश स्कोर: {nav_info.get('d9_score', 80)}%
    </span>
    </div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>वर नवांश लग्न:</b> {nav_info.get('g_d9_lagna')} &nbsp;|&nbsp; <b>कन्या नवांश लग्न:</b> {nav_info.get('b_d9_lagna')}<br/>
    • <b>जैमिनी आत्मकारक-दाराकारक संबंध:</b> वर (AK: {nav_info.get('g_ak')}, DK: {nav_info.get('g_dk')}) | कन्या (AK: {nav_info.get('b_ak')}, DK: {nav_info.get('b_dk')})<br/>
    • <b>कारकांश फलादेश:</b> {nav_info.get('ak_dk_sutra')}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 👁️ परस्पर ग्रह दृष्टि व युति सिनैस्ट्री (Cross-Planetary Aspects):")
        syn_aspects = deep_res.get("synastry_aspects", [])
        if syn_aspects:
            st.dataframe(pd.DataFrame(syn_aspects), use_container_width=True, hide_index=True)
        else:
            st.info("दोनों कुण्डलियों के प्रमुख ग्रहों में परस्पर युति या दृष्टि संबंध सक्रिय नहीं हैं।")

    # -------------------------------------------------------------------------
    # TAB 5: BEEJA & KSHETRA SPHUTA (PROGENY)
    # -------------------------------------------------------------------------
    with tab_mil5:
        st.markdown("### 👶 बीज स्फुट, क्षेत्र स्फुट एवं संतान सुख (Beeja-Kshetra Sphuta & Progeny)")
        st.write("फलदीपिका एवं जातक पारिजात के अनुसार वर के पौरुष (बीज बल) तथा कन्या के मातृत्व (क्षेत्र बल) का सूक्ष्म गणितीय परीक्षण:")

        san = deep_res.get("santana", {})
        col_sp1, col_sp2 = st.columns(2)
        with col_sp1:
            beeja = san.get("beeja", {})
            st.markdown(f"""
    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:16px;">
    <div style="font-size:16px; font-weight:900; color:#92400E;">🌾 वर बीज स्फुट (Beeja Sphuta)</div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>सूत्र:</b> सूर्य + शुक्र + गुरु स्पष्ट अंश योग<br/>
    • <b>राशि व नवांश:</b> {beeja.get('sign', '—')} राशि | {beeja.get('navamsha', '—')} नवांश<br/>
    • <b>बीज सामर्थ्य:</b> <b>{beeja.get('status', '—')}</b> ({beeja.get('score', 75)}%)<br/>
    • <b>शास्त्रीय फलादेश:</b> {beeja.get('desc', '—')}
    </div>
    </div>
    """, unsafe_allow_html=True)

        with col_sp2:
            kshetra = san.get("kshetra", {})
            st.markdown(f"""
    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:16px;">
    <div style="font-size:16px; font-weight:900; color:#065F46;">🌸 कन्या क्षेत्र स्फुट (Kshetra Sphuta)</div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>सूत्र:</b> चन्द्र + मंगल + गुरु स्पष्ट अंश योग<br/>
    • <b>राशि व नवांश:</b> {kshetra.get('sign', '—')} राशि | {kshetra.get('navamsha', '—')} नवांश<br/>
    • <b>क्षेत्र सामर्थ्य:</b> <b>{kshetra.get('status', '—')}</b> ({kshetra.get('score', 75)}%)<br/>
    • <b>शास्त्रीय फलादेश:</b> {kshetra.get('desc', '—')}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown(f"""
    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:16px; margin-top:14px;">
    <div style="font-size:16px; font-weight:900; color:#1E40AF;">🌟 अनुमानित संतान संख्या व वंश निर्णय: {san.get('children_count', 'अनुकूल')}</div>
    <div style="font-size:13px; color:#1E293B; margin-top:6px; line-height:1.6;">
    • <b>वंश वृद्धि फलादेश:</b> {san.get('lineage_text', '—')}<br/>
    • <b>प्रथम संतान स्वभाव:</b> {san.get('first_child_desc', '—')}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 6: UPAPADA LAGNA & IN-LAWS HARMONY
    # -------------------------------------------------------------------------
    with tab_mil6:
        st.markdown("### 🏛️ जैमिनी उपपद लग्न एवं ससुराल पक्ष सामंजस्य (Upapada & In-Laws)")
        st.write("महर्षि जैमिनी उपदेश सूत्र के अनुसार दांपत्य स्थायित्व एवं भावत् भावम् नियम से ससुराल के सदस्यों से तालमेल:")

        rel = deep_res.get("reliability", {})
        st.markdown(f"""
    <div style="background:#FAF5FF; border:1.5px solid #A855F7; border-radius:10px; padding:16px; margin-bottom:14px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
    <span style="font-size:16px; font-weight:900; color:#6B21A8;">🛡️ जैमिनी उपपद लग्न (UL): {rel.get('title', 'दांपत्य निष्ठा')}</span>
    <span style="font-size:13px; font-weight:800; background:#FFFFFF; border:1px solid #A855F7; padding:3px 10px; border-radius:6px; color:#6B21A8;">
    विश्वसनीयता: {rel.get('score', 85)}%
    </span>
    </div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>वर उपपद:</b> {rel.get('g_ul', '—')} &nbsp;|&nbsp; <b>कन्या उपपद:</b> {rel.get('b_ul', '—')}<br/>
    • <b>दांपत्य स्थायित्व फलादेश:</b> {rel.get('desc', '—')}
    </div>
    </div>
    """, unsafe_allow_html=True)

        sas = deep_res.get("sasural", {})
        st.markdown("##### 🏡 ससुराल पक्ष के सदस्यों से संबंध:")
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            _s1 = sas.get('sasur', {})
            _s2 = sas.get('devar_jeth', {})
            st.info(f"**👴 ससुर (Father-in-law):** " + str(_s1.get('title', '')) + "\n\n" + str(_s1.get('desc', '')))
            st.info(f"**👦 देवर एवं जेठ:** " + str(_s2.get('title', '')) + "\n\n" + str(_s2.get('desc', '')))

        with col_in2:
            _s3 = sas.get('saas', {})
            _s4 = sas.get('nanad_sala', {})
            st.info(f"**👵 सासू माँ (Mother-in-law):** " + str(_s3.get('title', '')) + "\n\n" + str(_s3.get('desc', '')))
            st.info(f"**👧 ननद एवं साला-साली:** " + str(_s4.get('title', '')) + "\n\n" + str(_s4.get('desc', '')))

    # -------------------------------------------------------------------------
    # TAB 7: DASHA TIMELINE COMPARISON & DASHA SANDHI OVERLAY
    # -------------------------------------------------------------------------
    with tab_mil7:
        st.markdown("### ⏱️ विंशोत्तरी दशा संधि एवं १५-वर्षीय कालक्रम समकालन (Dasha Timeline Overlay)")
        st.write("वर एवं कन्या की विंशोत्तरी महादशा व अंतर्दशा का समकालिक अध्ययन — संकट काल एवं स्वर्णिम युग की पहचान:")

        dash_comp = deep_res.get("dasha_timeline_comparison", {})
        col_dt1, col_dt2 = st.columns(2)
        with col_dt1:
            st.success(f"**👦 वर की वर्तमान दशा:** {dash_comp.get('current_groom', '—')}")
        with col_dt2:
            st.success(f"**👧 कन्या की वर्तमान दशा:** {dash_comp.get('current_bride', '—')}")

        st.info(f"**⏳ दशा संधि स्थिति:** {dash_comp.get('dasha_sandhi_status', '—')} ({m_score.dasha_sandhi_desc})")

        st.markdown("#### 📅 आगामी १५ वर्षों का दशा सामंजस्य प्रोजेक्शन (Timeline Projections):")
        fut_p = dash_comp.get("future_projections", [])
        if fut_p:
            st.dataframe(pd.DataFrame(fut_p), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 8: ASHTAKAVARGA SAV SYNASTRY & POST-MARITAL PROSPERITY
    # -------------------------------------------------------------------------
    with tab_mil8:
        st.markdown("### 📈 अष्टकवर्ग रेखा मिलान एवं विवाह उपरांत भाग्योदय (SAV Synastry & Prosperity)")
        st.write("बृहत्पाराशर होराशास्त्र अनुसार अष्टकवर्ग में एक-दूसरे की चंद्र राशि व लग्न में रेखाओं का आर्थिक व भाग्य प्रभाव:")

        av_syn = deep_res.get("ashtakavarga_synastry", {})
        col_av1, col_av2, col_av3 = st.columns(3)
        col_av1.metric("वर SAV कन्या चन्द्र राशि में", f"{av_syn.get('g_sav_in_b_moon', 28)} बिन्दु", "मानक: २८+")
        col_av2.metric("कन्या SAV वर लग्न में", f"{av_syn.get('b_sav_in_g_lagna', 28)} बिन्दु", "मानक: २८+")
        col_av3.metric("कन्या SAV वर एकादश (लाभ) में", f"{av_syn.get('b_sav_in_g_11th', 28)} बिन्दु", "धन समृद्धि")

        st.markdown("##### 💡 अष्टकवर्ग फलादेश निष्कर्ष:")
        for note in av_syn.get("eval_notes", []):
            st.write(f"• {note}")

        st.markdown("---")
        pro = deep_res.get("prosperity", {})
        st.markdown(f"""
    <div style="background:#FFF7ED; border:1.5px solid #F97316; border-radius:10px; padding:16px; margin-top:14px;">
    <div style="font-size:16px; font-weight:900; color:#C2410C;">💰 विवाह उपरांत भाग्योदय: {pro.get('bhagyodaya_title', 'उत्तम भाग्योदय')}</div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>भाग्योदय बल:</b> <b>{pro.get('score', 80)}%</b><br/>
    • <b>फलादेश विवरण:</b> {pro.get('bhagyodaya_desc', '—')}<br/>
    • <b>पत्नी के सहयोग का स्वरूप:</b> <b>{pro.get('wife_role_title', 'कुशल गृहलक्ष्मी')}</b> — {pro.get('wife_role_desc', '—')}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 9: BUSINESS PARTNER SYNASTRY
    # -------------------------------------------------------------------------
    with tab_mil9:
        st.markdown("### 💼 व्यापारिक साझेदारी सिनैस्ट्री (Business Partner Synastry)")
        st.write("व्यावसायिक साझेदारों के मध्य वित्तीय विश्वास, नेतृत्व, कानूनी विवाद जोखिम व साझेदारी की दीर्घायु का वैज्ञानिक वेध:")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            p1_b_name = st.text_input("साझेदार १ नाम", value=g_name, key="biz_p1_n")
        with col_b2:
            p2_b_name = st.text_input("साझेदार २ नाम", value=b_name, key="biz_p2_n")

        if st.button("🤝 व्यापारिक अनुकूलता वेध करें", key="btn_eval_biz"):
            biz_res = BusinessPartnershipService.evaluate_partnership(g_chart, b_chart, p1_b_name, p2_b_name)
            st.session_state["biz_milan_res"] = biz_res

        if "biz_milan_res" in st.session_state:
            b_res = st.session_state["biz_milan_res"]
            c_bp1, c_bp2, c_bp3 = st.columns(3)
            c_bp1.metric("साझेदारी स्कोर", f"{b_res['total_score']} / 100", f"ग्रेड: {b_res['grade']}")
            c_bp2.metric("शास्त्रीय निर्णय", b_res['verdict'])
            c_bp3.metric("विवाद सुरक्षा", f"{b_res['pillars']['dispute_risk']['score']} / 25")

            st.info(f"**💡 शास्त्रीय सारांश:** {b_res['summary_hi']}")

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.write(f"• **वित्तीय विश्वास:** {b_res['pillars']['financial']['score']}/25 — {b_res['pillars']['financial']['desc']}")
                st.write(f"• **नेतृत्व तालमेल:** {b_res['pillars']['leadership']['score']}/25 — {b_res['pillars']['leadership']['desc']}")
            with col_p2:
                st.write(f"• **विवाद व जोखिम सुरक्षा:** {b_res['pillars']['dispute_risk']['score']}/25 — {b_res['pillars']['dispute_risk']['desc']}")
                st.write(f"• **साझेदारी दीर्घायु:** {b_res['pillars']['longevity']['score']}/25 — {b_res['pillars']['longevity']['desc']}")

    # -------------------------------------------------------------------------
    # TAB 10: PRINTABLE DOSSIER & REMEDIES
    # -------------------------------------------------------------------------
    with tab_mil10:
        st.markdown("### 🖨️ १-क्लिक प्रिंटेबल विवाह मेलापक रिपोर्ट एवं वैदिक उपाय")
        st.write("महर्षि पराशर व प्रामाणिक शास्त्रीय शोध स्तरीय सम्पूर्ण कुंडली मिलान रिपोर्ट। सीधे प्रिंट करें अथवा PDF के रूप में सुरक्षित रखें:")

        try:
            report_html = milan_mod.default_milan_service.render_milan_report_html(groom_data, bride_data, m_score)
            st.download_button(
                label="📥 सम्पूर्ण विवाह मेलापक रिपोर्ट डाउनलोड करें (HTML / PDF)",
                data=report_html,
                file_name=f"Kundali_Milan_{g_name}_{b_name}.html",
                mime="text/html",
                key="btn_dl_milan_tab10",
                use_container_width=True
            )
            import streamlit.components.v1 as components
            components.html(report_html, height=750, scrolling=True)
        except Exception as _e_rep:
            st.error(f"रिपोर्ट रेंडर करने में त्रुटि: {_e_rep}")

        st.markdown("#### 📿 दांपत्य सुख एवं समृद्धि हेतु अचूक वैदिक उपाय:")
        for r in deep_res.get("remedies", []):
            st.markdown(f"• {r}")


    # =============================================================
    # TAB 15: AI SAHAYAK (CHAT CONSULTATION)

