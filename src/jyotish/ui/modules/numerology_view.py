import streamlit as st
from datetime import date
import importlib

def render_numerology_view(birth_profile, tabs=None):
    if tabs is None:
        tabs = [
            '🧭 लो-शू ग्रिड व तल',
            '🔢 मूलांक व भाग्यांक विश्लेषण',
            '✍️ नाम सुधार व अनुकूलता',
            '💎 क्रिस्टल व अंक उपाय'
        ]
    st.subheader("🔢 अंकशास्त्र एवं लो-शू ग्रिड (Vedic & Lo-Shu Numerology)")
    st.write("कील्डियन नामांक, मूलांक, भाग्यांक, कुआ नंबर, ३×३ लो-शू ग्रिड (८ तल), मिसिंग नंबर एवं क्रिस्टल/धातु आधारित शास्त्रीय उपाय।")

    import importlib
    import src.jyotish.core.numerology as num_mod
    importlib.reload(num_mod)

    b_date = birth_profile.birth_date
    num_res = num_mod.default_numerology_engine.calculate(
        birth_date=b_date,
        full_name=birth_profile.name,
        gender=st.session_state.get("birth_gender", "male")
    )

    # 4-Pillar Numerology HUD
    c_n1, c_n2, c_n3, c_n4 = st.columns(4)
    c_n1.metric("मूलांक (Driver / Root)", f"🔢 {num_res.mulank}", num_res.driver_info["planet"].split()[0])
    c_n2.metric("भाग्यांक (Destiny / Conductor)", f"🌟 {num_res.bhagyank}", num_res.conductor_info["planet"].split()[0])
    c_n3.metric("कुआ नंबर (Kua / Feng Shui)", f"🧭 {num_res.kua_number}", "दिशात्मक ऊर्जा")
    c_n4.metric("कील्डियन नामांक (Name No.)", f"✍️ {num_res.chaldean_namank}", f"पाइथागोरस: {num_res.pythagorean_namank}")

    tab_num1, tab_num2, tab_num3, tab_num4 = st.tabs(tabs)

    with tab_num1:
        st.markdown("### 📊 ३×३ लो-शू ग्रिड (Magic Square of 15)")
        st.caption("जन्म दिनांक के अंकों एवं मूलांक-भाग्यांक से निर्मित दिव्य लो-शू चक्र:")

        g = num_res.lo_shu_grid
        col_g1, col_g2 = st.columns([1.2, 1.8])

        with col_g1:
            # 3x3 Lo-Shu Box HTML
            def fmt_cell(n):
                cnt = g.get(n, 0)
                if cnt == 0:
                    return f"<span style='color:#CBD5E1;font-size:22px;'>—</span><br/><small style='color:#94A3B8;'>{n}</small>"
                return f"<span style='color:#1E40AF;font-size:24px;font-weight:900;'>{str(n)*cnt}</span>"

            grid_html = f"""
            <table style="width:100%; border-collapse:collapse; text-align:center; font-family:sans-serif; background:#F8FAFC; border:2px solid #3B82F6; border-radius:12px; overflow:hidden;">
                <tr style="height:90px; border-bottom:2px solid #93C5FD;">
                    <td style="width:33.3%; border-right:2px solid #93C5FD; background:#EFF6FF;">{fmt_cell(4)}</td>
                    <td style="width:33.3%; border-right:2px solid #93C5FD; background:#EFF6FF;">{fmt_cell(9)}</td>
                    <td style="width:33.3%; background:#EFF6FF;">{fmt_cell(2)}</td>
                </tr>
                <tr style="height:90px; border-bottom:2px solid #93C5FD;">
                    <td style="border-right:2px solid #93C5FD; background:#EFF6FF;">{fmt_cell(3)}</td>
                    <td style="border-right:2px solid #93C5FD; background:#FEF3C7; border:2px solid #F59E0B;">{fmt_cell(5)}</td>
                    <td style="background:#EFF6FF;">{fmt_cell(7)}</td>
                </tr>
                <tr style="height:90px;">
                    <td style="border-right:2px solid #93C5FD; background:#EFF6FF;">{fmt_cell(8)}</td>
                    <td style="border-right:2px solid #93C5FD; background:#EFF6FF;">{fmt_cell(1)}</td>
                    <td style="background:#EFF6FF;">{fmt_cell(6)}</td>
                </tr>
            </table>
            """
            st.markdown(grid_html, unsafe_allow_html=True)
            st.caption("📌 ग्रिड में उपस्थित अंक जातक की आंतरिक शक्तियों को दर्शाते हैं।")

        with col_g2:
            st.markdown("#### 🌟 सक्रिय योग / तल (Active Planes)")
            if num_res.completed_planes:
                for p in num_res.completed_planes:
                    st.markdown(f"""
                    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:8px; padding:10px; margin-bottom:8px;">
                        <b style="color:#065F46; font-size:15px;">✅ {p['name']} (100% पूर्ण)</b><br/>
                        <small style="color:#1F2937;">{p['significance_hi']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("वर्तमान ग्रिड में कोई 100% पूर्ण तल नहीं है। आंशिक तलों की स्थिति नीचे देखें:")

            with st.expander("⚪ अन्य आंशिक / अपूर्ण तल (Incomplete Planes)"):
                for p in num_res.incomplete_planes:
                    st.markdown(f"• **{p['name']}** — शक्ति: **{p['strength_pct']}%** ({p['significance_hi'][:60]}...)")

    with tab_num2:
        st.markdown("### 🪐 मूलांक एवं भाग्यांक व्यक्तित्व विश्लेषण")
        col_dr1, col_dr2 = st.columns(2)
        with col_dr1:
            d = num_res.driver_info
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px;">
                <h4 style="color:#B45309; margin-top:0;">👑 मूलांक: {num_res.mulank} (स्वामी: {d['planet']})</h4>
                <p><b>तत्व:</b> {d['element']} | <b>दिशा:</b> {d['direction']}</p>
                <p><b>स्वभाव एवं गुण:</b> {d['nature_hi']}</p>
                <p><b>मुख्य रत्न:</b> {d['gemstone']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_dr2:
            c = num_res.conductor_info
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px;">
                <h4 style="color:#1E40AF; margin-top:0;">🌟 भाग्यांक: {num_res.bhagyank} (स्वामी: {c['planet']})</h4>
                <p><b>तत्व:</b> {c['element']} | <b>दिशा:</b> {c['direction']}</p>
                <p><b>जीवन लक्ष्य व कर्म:</b> {c['nature_hi']}</p>
                <p><b>मुख्य रत्न:</b> {c['gemstone']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.info(f"⏳ **पर्सनल ईयर (Personal Year {date.today().year}):** इस वर्ष का व्यक्तिगत अंक **{num_res.personal_year}** है। यह वर्ष नए संकल्पों एवं योजनाओं के क्रियान्वयन हेतु अत्यंत महत्वपूर्ण रहेगा।")

    with tab_num3:
        st.markdown("### 🧩 मिसिंग नंबर (Missing Numbers) एवं अचूक उपाय")
        st.caption("लो-शू ग्रिड में जो अंक अनुपस्थित हैं, उनके जीवन पर पड़ने वाले प्रभाव व सटीक निवारण:")

        if num_res.remedies_for_missing:
            for rem in num_res.remedies_for_missing:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:12px; margin-bottom:10px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                    <b style="color:#DC2626; font-size:15px;">⚠️ अनुपस्थित अंक {rem['number']} ({rem['planet']})</b>
                    <p style="margin:4px 0; color:#475569;"><b>प्रभाव:</b> {rem['lacking_hi']}</p>
                    <p style="margin:4px 0; color:#047857;"><b>🌿 अचूक उपाय:</b> {rem['remedy_hi']}</p>
                    <small style="color:#2563EB;"><b>धारण योग्य वस्तु:</b> {rem['item']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 अद्भुत! आपके लो-शू ग्रिड में लगभग सभी महत्वपूर्ण अंक संतुलित हैं।")

    with tab_num4:
        st.markdown("### 💎 लकी फैक्टर्स, नेम ट्यूनिंग एवं वाहन/मोबाइल नंबर अनुकूलता")
        st.caption("कील्डियन अंकशास्त्र, मूलांक-भाग्यांक मैत्री एवं ध्वनि तरंगों के आधार पर जीवन में सर्वतोमुखी सफलता के सूत्र:")

        ls = num_res.lucky_summary
        col_lf1, col_lf2 = st.columns(2)
        with col_lf1:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#0F172A;">✨ अनुकूल लकी फैक्टर्स:</b>
                <p style="margin:4px 0;">• <b>शुभ दिन:</b> {', '.join(ls['lucky_days'])}</p>
                <p style="margin:4px 0;">• <b>अनुकूल रंग:</b> {', '.join(ls['lucky_colors'])}</p>
                <p style="margin:4px 0;">• <b>शुभ अंक (Friendly):</b> <span style="color:#16A34A; font-weight:800;">{', '.join(str(n) for n in ls['lucky_numbers'])}</span></p>
            </div>
            """, unsafe_allow_html=True)
        with col_lf2:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#0F172A;">⚠️ वर्जित एवं रत्न:</b>
                <p style="margin:4px 0;">• <b>शत्रु / प्रतिकूल अंक:</b> <span style="color:#DC2626; font-weight:800;">{', '.join(str(n) for n in ls['unfavorable_numbers']) or 'कोई नहीं'}</span></p>
                <p style="margin:4px 0;">• <b>शुभ रत्न:</b> {', '.join(ls['lucky_gemstones'])}</p>
                <p style="margin:4px 0;">• <b>मूलांक स्वामी:</b> {ls['mulank_lord']} | <b>भाग्यांक:</b> {ls['bhagyank_lord']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        # 1. Name Spelling Tuning Engine
        st.markdown("#### ✍️ कील्डियन नेम ट्यूनिंग एवं स्पेलिंग सुधार इंजन (Chaldean Name Correction):")
        tuning_res = num_mod.default_numerology_engine.suggest_name_tuning(
            full_name=birth_profile.name,
            mulank=num_res.mulank,
            bhagyank=num_res.bhagyank
        )

        c_tun1, c_tun2 = st.columns([1.2, 2.8])
        with c_tun1:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px; text-align:center;">
                <span style="font-size:13px; color:#B45309; font-weight:600;">वर्तमान नाम कंपन (Current Vibration)</span>
                <div style="font-size:26px; font-weight:900; color:#78350F; margin:6px 0;">{tuning_res['original_compound']} ➔ {tuning_res['original_single']}</div>
                <div style="font-size:12px; font-weight:700; color:#1E40AF;">{tuning_res['harmony_status']}</div>
                <hr style="margin:8px 0; border:0; border-top:1px dashed #FCD34D;"/>
                <small style="color:#475569;"><b>अर्थ:</b> {tuning_res['original_meaning']}</small>
            </div>
            """, unsafe_allow_html=True)

        with c_tun2:
            st.markdown("**🌟 अनुशंसित वैकल्पिक स्पेलिंग (Optimized Royal Spelling Options):**")
            if tuning_res["suggestions"]:
                sugg_rows = []
                for s in tuning_res["suggestions"]:
                    sugg_rows.append({
                        "प्रस्तावित नाम": s["suggested_name"],
                        "संयुक्त अंक": s["compound_number"],
                        "एकल अंक": f"{s['single_number']} ({'👑 राजयोग' if s['is_royal'] else 'शुभ'})",
                        "ग्रह स्वामी": s["planetary_lord"].split()[0],
                        "शास्त्रीय प्रभाव": s["significance"]
                    })
                st.dataframe(pd.DataFrame(sugg_rows), use_container_width=True, hide_index=True)
                st.caption("💡 हस्ताक्षर अथवा सोशल मीडिया/बिजनेस कार्ड में इस स्पेलिंग का प्रयोग करने से अनुकूल कंपन आकर्षित होते हैं।")
            else:
                st.success("✨ आपके वर्तमान नाम की स्पेलिंग पहले से ही मूलांक व भाग्यांक के अनुकूलतम शुभ कंपन पर स्थित है। किसी बदलाव की आवश्यकता नहीं है।")

        st.markdown("---")
        # 2. Vehicle & Mobile Number Compatibility Tester
        st.markdown("#### 🚗 📱 मोबाइल नंबर एवं वाहन नंबर अनुकूलता परीक्षक (Vehicle & Mobile Harmonizer):")
        test_num_input = st.text_input("परीक्षण हेतु मोबाइल नंबर या वाहन प्लेट अंक दर्ज करें:", value="9810123456", key="num_compat_input")
        if test_num_input:
            compat_eval = num_mod.default_numerology_engine.check_vehicle_mobile_compatibility(
                number_str=test_num_input,
                mulank=num_res.mulank,
                bhagyank=num_res.bhagyank
            )
            col_cmp1, col_cmp2 = st.columns([1.2, 2.8])
            with col_cmp1:
                st.markdown(f"""
                <div style="background:#F0FDF4 if compat_eval['is_lucky'] else #FEF2F2; border:1.5px solid #86EFAC if compat_eval['is_lucky'] else #FCA5A5; border-radius:10px; padding:14px; text-align:center;">
                    <span style="font-size:13px; color:#475569;">कुल योग (Compound ➔ Single)</span>
                    <div style="font-size:26px; font-weight:900; color:#1E293B; margin:4px 0;">{compat_eval['compound_sum']} ➔ {compat_eval['single_digit']}</div>
                    <small style="color:#2563EB;">स्वामी: {compat_eval['lord']}</small>
                </div>
                """, unsafe_allow_html=True)
            with col_cmp2:
                st.markdown(f"**रेटिंग:** {compat_eval['rating']}")
                st.info(compat_eval["advice"])


    # =============================================================
    # MODULE 23: लाल किताब 1952 तेवा एवं उपाय (LAL KITAB 1952)
    # =============================================================

