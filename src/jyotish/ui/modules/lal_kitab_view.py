import streamlit as st
import pandas as pd
import importlib

def render_lal_kitab_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            '📖 खाना विश्लेषण व पक्का घर',
            '⛓️ कर्मिक ऋण (Rinas) व दोष',
            '🌿 कुण्डली टोटके एवं उपाय'
        ]
    st.subheader("📕 लाल किताब 1952 तेवा एवं शास्त्रीय उपाय (Lal Kitab 1952 Engine)")
    st.write("कालपुरुष पक्के घर (खाना नं. १ से १२), ९ प्रकार के कर्मिक ऋण (Pitra, Matra, Swa, Stri, Rishtedari, Nirdayi, Kudrati, Kanya, Jal Rina), सोया हुआ घर/ग्रह, धर्मी व अंधा तेवा एवं १०८ प्रामाणिक अचूक टोटके।")

    import importlib
    import src.jyotish.core.lalkitab as lk_mod
    importlib.reload(lk_mod)

    lk_res = lk_mod.default_lalkitab_engine.calculate(chart)

    # Top Status Banner
    c_lk1, c_lk2, c_lk3, c_lk4 = st.columns(4)
    c_lk1.metric("कुण्डली प्रकार", "धर्मी तेवा (Blessed) 🛡️" if lk_res.dharmi_teva else "सामान्य तेवा", "ईश्वरीय सुरक्षा")
    c_lk2.metric("अंधा तेवा (Eye Status)", "⚠️ अंधा तेवा" if lk_res.andha_teva else ("🌙 रात का अंधा (Ratandh)" if getattr(lk_res, "ratandh_teva", False) else "✅ नेत्रवान (सक्रिय)"), "दृष्टि सामर्थ्य")
    c_lk3.metric("सक्रिय कर्मिक ऋण", f"{len(lk_res.active_debts)} / 9 ऋण", "पूर्वजन्म संस्कार")
    c_lk4.metric("सोए हुए घर (Sleeping)", f"{len(lk_res.sleeping_houses)} / 12", "जाग्रत करने योग्य")

    tab_lk1, tab_lk2, tab_lk3, tab_lk4 = st.tabs(tabs)

    with tab_lk1:
        st.markdown("### 🏠 लाल किताब अनुसार १२ खानों में ग्रह स्थिति")
        st.caption("लाल किताब में राशि नहीं, बल्कि खाना (House 1 to 12) सर्वोपरि होता है:")

        khana_table = []
        for kh in range(1, 13):
            kh_info = lk_mod.LAL_KITAB_KHANA_DATA[kh]
            pls = lk_res.khana_planets.get(kh, [])
            khana_table.append({
                "खाना नं.": f"खाना {kh}",
                "पक्का स्वामी": kh_info["pakka_ruler"],
                "कारक": kh_info["karaka"],
                "स्थित ग्रह": ", ".join(pls) if pls else "⚪ रिक्त (सोया घर)",
                "महत्व / क्षेत्र": kh_info["nature_hi"]
            })
        st.dataframe(pd.DataFrame(khana_table), use_container_width=True, hide_index=True)

    with tab_lk2:
        st.markdown("### ⚠️ लाल किताब के ९ शास्त्रीय कर्मिक ऋण (9 Karmic Debts)")
        st.caption("पूर्वजन्म अथवा पूर्वजों द्वारा किए गए कृत्यों के कारण उत्पन्न ९ शास्त्रीय ऋण:")

        if lk_res.active_debts:
            for d in lk_res.active_debts:
                st.markdown(f"""
                <div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:14px; margin-bottom:12px;">
                    <b style="color:#991B1B; font-size:16px;">⚠️ {d['name_hi']}</b>
                    <p style="margin:5px 0;"><b>कारण:</b> {d['cause_hi']}</p>
                    <p style="margin:5px 0;"><b>जीवन पर प्रभाव:</b> {d['effect_hi']}</p>
                    <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #FCA5A5; margin-top:6px;">
                        <b style="color:#047857;">🌿 लाल किताब निवारण उपाय:</b> {d['remedy_hi']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 अत्यंत शुभ! आपकी कुण्डली लाल किताब के समस्त ९ कर्मिक ऋणों (पितृ, मातृ, स्व, स्त्री, रिश्तेदारी, निर्दयी, कुदरती, कन्या व जल ऋण) से पूर्णतः मुक्त है!")

        with st.expander("📖 लाल किताब के सभी ९ कर्मिक ऋणों की प्रामाणिक सूची एवं लक्षण", expanded=False):
            for all_d in lk_mod.DEBT_DEFINITIONS:
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px; margin-bottom:8px;">
                    <b>{all_d['name_hi']}</b>: {all_d['condition_desc_hi']}<br/>
                    <small style="color:#059669;"><b>उपाय:</b> {all_d['remedy_hi']}</small>
                </div>
                """, unsafe_allow_html=True)

    with tab_lk3:
        st.markdown("### 💤 सोए हुए घर एवं ग्रह विचार")
        col_sl1, col_sl2 = st.columns(2)
        with col_sl1:
            st.markdown("#### 🏠 सोए हुए घर (Sleeping Houses)")
            st.write("जिन घरों में कोई ग्रह नहीं होता, वे सोए हुए माने जाते हैं। उनके पक्के स्वामियों की सेवा से वे जाग्रत होते हैं:")
            st.info(", ".join(f"खाना {h}" for h in lk_res.sleeping_houses) if lk_res.sleeping_houses else "कोई घर सोया हुआ नहीं है।")

        with col_sl2:
            st.markdown("#### 🪐 सोए हुए ग्रह (Sleeping Planets)")
            st.write("जो ग्रह अपने कारक घर से संपर्क नहीं बना पाते:")
            st.warning(", ".join(lk_res.sleeping_planets) if lk_res.sleeping_planets else "सभी ग्रह सक्रिय हैं।")

    with tab_lk4:
        st.markdown("### 🌿 लाल किताब के अनुभूत अचूक टोटके एवं सावधानियां")

        # 1. Native Chart 9 Planets Specific Totkas
        st.markdown("#### 🎯 आपकी कुण्डली के ९ ग्रहों के अचूक टोटके:")
        st.caption("आपके जन्म लग्न के अनुसार प्रत्येक ग्रह के वर्तमान खाने के प्रामाणिक उपाय व सावधानियां:")

        if lk_res.chart_108_totkas:
            t_grid_cols = st.columns(3)
            for idx, c_t in enumerate(lk_res.chart_108_totkas):
                col_i = idx % 3
                with t_grid_cols[col_i]:
                    st.markdown(f"""
    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px; margin-bottom:12px; min-height:220px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:15px; font-weight:900; color:#B45309;">{c_t['planet_hi']} (खाना नं. {c_t['khana']})</span>
        <span style="font-size:11px; background:#FEF3C7; color:#92400E; padding:2px 6px; border-radius:4px; font-weight:700;">लाल किताब 1952</span>
    </div>
    <div style="font-size:12px; color:#1E293B; margin-top:8px; line-height:1.5;">
        <b>🌿 अचूक टोटका:</b> {c_t['totka_hi']}
    </div>
    <div style="font-size:11px; color:#991B1B; margin-top:6px; line-height:1.4;">
        <b>⚠️ विशेष सावधानी:</b> {c_t['precaution_hi']}
    </div>
    <div style="font-size:11px; color:#065F46; margin-top:6px; font-style:italic;">
        ✨ {c_t['shastra_effect_hi']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("---")
        # 2. Comprehensive 108 Totkas Explorer
        st.markdown("#### 📚 सम्पूर्ण १०८ लाल किताब टोटके पुस्तकालय (108 Totkas Explorer)")
        st.caption("लाल किताब (१९५२ संस्करण) के सभी ९ ग्रहों एवं १२ खानों के १०८ प्रामाणिक उपाय खोजें:")

        col_ex_p, col_ex_kh = st.columns([1.5, 1.5])
        with col_ex_p:
            sel_pl = st.selectbox(
                "ग्रह चुनें (Select Planet):",
                ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"],
                format_func=lambda x: {"Sun": "☀️ सूर्य (Sun)", "Moon": "🌙 चन्द्र (Moon)", "Mars": "⚔️ मंगल (Mars)", "Mercury": "☿️ बुध (Mercury)", "Jupiter": "🪐 गुरु (Jupiter)", "Venus": "💎 शुक्र (Venus)", "Saturn": "⚖️ शनि (Saturn)", "Rahu": "🌪️ राहु (Rahu)", "Ketu": "🚩 केतु (Ketu)"}.get(x, x),
                key="lk_explorer_planet"
            )
        with col_ex_kh:
            sel_kh = st.selectbox(
                "खाना चुनें (Select Khana 1-12):",
                list(range(1, 13)),
                format_func=lambda x: f"खाना नं. {x} ({lk_mod.LAL_KITAB_KHANA_DATA[x]['pakka_sign']})",
                key="lk_explorer_khana"
            )

        exp_data = lk_mod.LAL_KITAB_108_TOTKAS.get((sel_pl, sel_kh), None)
        if exp_data:
            st.markdown(f"""
    <div style="background:#F0FDF4; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin:10px 0;">
    <div style="font-size:16px; font-weight:900; color:#065F46;">
        📜 {sel_pl} खाना नं. {sel_kh} का प्रामाणिक लाल किताब उपाय
    </div>
    <div style="font-size:14px; color:#0F172A; margin-top:10px; line-height:1.6;">
        <b>🌿 अचूक टोटका:</b> {exp_data['totka_hi']}
    </div>
    <div style="font-size:13px; color:#991B1B; margin-top:8px;">
        <b>⚠️ जीवन रक्षा सावधानी:</b> {exp_data['precaution_hi']}
    </div>
    <div style="font-size:12px; color:#047857; margin-top:8px; font-style:italic;">
        <b>फल प्रभाव:</b> {exp_data['shastra_effect_hi']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("""
        #### 📜 लाल किताब के १० शाश्वत नियम:
        1. किसी भी उपाय को सूर्योदय के पश्चात और सूर्यास्त से पहले करें।
        2. एक समय में एक ही उपाय करें, कम से कम ४० से ४३ दिन तक नियम न टूटे।
        3. मुफ्त में कोई वस्तु या ताबीज न लें, न ही बिना दक्षिणा के ज्योतिषीय उपाय करें।
        4. घर के मंदिर में भारी घंटियां या ऊंची मूर्तियां न रखें।
        5. मांस, मदिरा एवं पराई स्त्री के संग से सदा दूर रहें।
        """)

