# -*- coding: utf-8 -*-
"""
Module 21: Vedic & Lo-Shu Numerology View.
Provides:
1. 3x3 Lo-Shu Grid (Magic Square of 15), 8 Planes analysis, and Number Frequency Repetitions.
2. Mulank (Driver) & Bhagyank (Conductor) classical Sanskrit shlokas, positive and shadow/negative phalas.
3. Missing Numbers with Five-Element (Panchatattva), Gemstone, Crystal and Metal remedies.
4. Lucky Factors, Chaldean Name Spelling Tuning, and Vehicle/Mobile Number Harmonizer.
"""

import streamlit as st
import pandas as pd
from datetime import date
from typing import List, Optional
import src.jyotish.core.numerology as num_mod
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS


def render_numerology_view(birth_profile, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "📊 ३×३ लो-शू ग्रिड व ८ तल",
            "🪐 मूलांक व भाग्यांक — शास्त्रीय फल",
            "🧩 मिसिंग नंबर व पंचतत्व उपाय",
            "💎 लकी फैक्टर्स, नामांक व फोन शोधन"
        ]

    st.subheader("🔢 अंकशास्त्र एवं लो-शू ग्रिड (Vedic & Lo-Shu Numerology)")
    st.caption("कील्डियन नामांक, मूलांक, भाग्यांक, कुआ नंबर, ३×३ लो-शू ग्रिड (८ तल), मिसिंग नंबर एवं शास्त्रीय रत्न/धातु/क्रिस्टल आधारित अचूक उपाय।")

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

    rendered_tabs = st.tabs(tabs)

    # -------------------------------------------------------------
    # TAB 1: ३×३ लो-शू ग्रिड व ८ तल
    # -------------------------------------------------------------
    with rendered_tabs[0]:
        st.markdown("### 📊 ३×३ लो-शू ग्रिड (Magic Square of 15) एवं ८ तल")
        loshu_pramana = SHASTRIYA_SHLOKAS.get("loshu_grid_planes", {})
        if loshu_pramana:
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:3px solid #D97706; padding:8px 12px; margin-bottom:12px; border-radius:6px; font-size:13px; color:#78350F;">
                <b>📜 लो-शू पञ्चदश यन्त्र प्रमाण:</b><br/>
                <i>{loshu_pramana.get('shloka_sanskrit', '').replace(chr(10), '<br/>')}</i><br/>
                <small style="color:#92400E;"><b>ग्रन्थ:</b> {loshu_pramana.get('grantha', '')}</small>
            </div>
            """, unsafe_allow_html=True)

        g = num_res.lo_shu_grid
        col_g1, col_g2 = st.columns([1.2, 1.8])

        with col_g1:
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
            st.caption("📌 ग्रिड में उपस्थित अंक जातक की आंतरिक शक्तियों व तलों को प्रकट करते हैं।")

        with col_g2:
            st.markdown("#### 🌟 सक्रिय योग / तल (Active Planes)")
            if num_res.completed_planes:
                for p in num_res.completed_planes:
                    st.markdown(f"""
                    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:8px; padding:10px; margin-bottom:8px;">
                        <b style="color:#065F46; font-size:15px;">✅ {p['name']} (100% पूर्ण)</b><br/>
                        <span style="color:#1F2937; font-size:13px;">{p['significance_hi']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("वर्तमान ग्रिड में कोई 100% पूर्ण तल नहीं है। आंशिक तलों की स्थिति नीचे देखें:")

            with st.expander("⚪ अन्य आंशिक / अपूर्ण तल (Incomplete Planes)"):
                for p in num_res.incomplete_planes:
                    st.markdown(f"• **{p['name']}** — शक्ति: **{p['strength_pct']}%** ({p['significance_hi'][:60]}...)")

        # Repetition Frequency Analysis
        st.markdown("---")
        st.markdown("#### 🔁 अंक पुनरावृत्ति फल (Number Frequency Analysis)")
        st.caption("ग्रिड में किसी अंक की अत्यधिक पुनरावृत्ति (३ या अधिक बार) ऊर्जा का असंतुलन कर सकती है:")

        rep_rows = []
        for n in range(1, 10):
            cnt = g.get(n, 0)
            if cnt > 0:
                p_name = num_mod.NUMBER_DATA[n]["planet"].split()[0]
                status_note = "संतुलित ऊर्जा (+)" if cnt <= 2 else "अति-ऊर्जा / सावधानी (-)"
                rep_rows.append({
                    "अंक (Number)": f"{n} ({p_name})",
                    "आवृत्ति (Count)": f"{cnt} बार",
                    "ऊर्जा संतुलन": status_note,
                    "शास्त्रीय प्रभाव": "सकारात्मक अभिव्यक्ति एवं स्वाभाविक तेज" if cnt <= 2 else f"अंक {n} की अति-पुनरावृत्ति से अहंकार अथवा हठधर्मिता की संभावना, सात्विक संतुलन अपेक्षित।"
                })
        if rep_rows:
            st.dataframe(pd.DataFrame(rep_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 2: मूलांक व भाग्यांक — शास्त्रीय फल
    # -------------------------------------------------------------
    with rendered_tabs[1]:
        st.markdown("### 🪐 मूलांक एवं भाग्यांक — प्रामाणिक शास्त्रीय श्लोक एवं द्विविध फल (Positive & Negative)")
        st.caption("वैदिक सांख्य शास्त्र अनुसार जातक के मूलांक (स्वभाव) एवं भाग्यांक (कर्म-पथ) का सकारात्मक शक्ति एवं छाया सावधानियों सहित यथार्थ विश्लेषण:")

        col_dr1, col_dr2 = st.columns(2)
        with col_dr1:
            d = num_res.driver_info
            shloka_1 = d.get("shloka_sa", "")
            pos_1 = d.get("positive_traits_hi", d["nature_hi"])
            neg_1 = d.get("negative_traits_hi", "अति-उत्साह से बचें।")
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:16px; margin-bottom:12px;">
                <h4 style="color:#B45309; margin-top:0;">👑 मूलांक: {num_res.mulank} (स्वामी: {d['planet']})</h4>
                <div style="background:#FEF3C7; border-left:3px solid #D97706; padding:6px 10px; margin:8px 0; font-size:12.5px; color:#78350F;">
                    <b>📜 मूल संस्कृत श्लोक:</b><br/>{shloka_1.replace(chr(10), '<br/>')}
                </div>
                <p style="margin:4px 0;"><b>तत्व:</b> {d['element']} | <b>दिशा:</b> {d['direction']}</p>
                <div style="margin:8px 0; padding:8px; background:#ECFDF5; border-radius:6px; border:1px solid #A7F3D0;">
                    <b style="color:#065F46;">🟢 सकारात्मक गुण (+):</b><br/>
                    <span style="font-size:13px; color:#064E3B;">{pos_1}</span>
                </div>
                <div style="margin:8px 0; padding:8px; background:#FEF2F2; border-radius:6px; border:1px solid #FECACA;">
                    <b style="color:#991B1B;">🔴 छाया लक्षण व सावधानी (-):</b><br/>
                    <span style="font-size:13px; color:#7F1D1D;">{neg_1}</span>
                </div>
                <p style="margin:4px 0; font-size:12.5px;"><b>मुख्य रत्न:</b> {d['gemstone']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_dr2:
            c = num_res.conductor_info
            shloka_2 = c.get("shloka_sa", "")
            pos_2 = c.get("positive_traits_hi", c["nature_hi"])
            neg_2 = c.get("negative_traits_hi", "अहंकार व लापरवाही से बचें।")
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:16px; margin-bottom:12px;">
                <h4 style="color:#1E40AF; margin-top:0;">🌟 भाग्यांक: {num_res.bhagyank} (स्वामी: {c['planet']})</h4>
                <div style="background:#DBEAFE; border-left:3px solid #2563EB; padding:6px 10px; margin:8px 0; font-size:12.5px; color:#1E3A8A;">
                    <b>📜 मूल संस्कृत श्लोक:</b><br/>{shloka_2.replace(chr(10), '<br/>')}
                </div>
                <p style="margin:4px 0;"><b>तत्व:</b> {c['element']} | <b>दिशा:</b> {c['direction']}</p>
                <div style="margin:8px 0; padding:8px; background:#ECFDF5; border-radius:6px; border:1px solid #A7F3D0;">
                    <b style="color:#065F46;">🟢 सकारात्मक कर्म-पथ (+):</b><br/>
                    <span style="font-size:13px; color:#064E3B;">{pos_2}</span>
                </div>
                <div style="margin:8px 0; padding:8px; background:#FEF2F2; border-radius:6px; border:1px solid #FECACA;">
                    <b style="color:#991B1B;">🔴 कर्म-पथ की बाधाएं व सावधानी (-):</b><br/>
                    <span style="font-size:13px; color:#7F1D1D;">{neg_2}</span>
                </div>
                <p style="margin:4px 0; font-size:12.5px;"><b>मुख्य रत्न:</b> {c['gemstone']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.info(f"⏳ **पर्सनल ईयर (Personal Year {date.today().year}):** इस वर्ष का व्यक्तिगत अंक **{num_res.personal_year}** है। यह वर्ष नए संकल्पों एवं योजनाओं के क्रियान्वयन हेतु अत्यंत महत्वपूर्ण रहेगा।")

    # -------------------------------------------------------------
    # TAB 3: मिसिंग नंबर व पंचतत्व उपाय
    # -------------------------------------------------------------
    with rendered_tabs[2]:
        st.markdown("### 🧩 मिसिंग नंबर (Missing Numbers) एवं पंचतत्वीय अचूक उपाय")
        st.caption("लो-शू ग्रिड में जो अंक अनुपस्थित हैं, उनके जीवन पर पड़ने वाले प्रभाव व सटीक निवारण:")

        if num_res.remedies_for_missing:
            for rem in num_res.remedies_for_missing:
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:14px; margin-bottom:10px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                    <b style="color:#DC2626; font-size:15px;">⚠️ अनुपस्थित अंक {rem['number']} ({rem['planet']})</b>
                    <p style="margin:4px 0; color:#475569;"><b>प्रभाव:</b> {rem['lacking_hi']}</p>
                    <p style="margin:4px 0; color:#047857;"><b>🌿 अचूक उपाय:</b> {rem['remedy_hi']}</p>
                    <small style="color:#2563EB;"><b>धारण योग्य वस्तु / क्रिस्टल:</b> {rem['item']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 अद्भुत! आपके लो-शू ग्रिड में लगभग सभी महत्वपूर्ण अंक संतुलित हैं।")

    # -------------------------------------------------------------
    # TAB 4: लकी फैक्टर्स, नामांक व फोन शोधन
    # -------------------------------------------------------------
    with rendered_tabs[3]:
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
                bg_col = "#F0FDF4" if compat_eval['is_lucky'] else "#FEF2F2"
                bd_col = "#86EFAC" if compat_eval['is_lucky'] else "#FCA5A5"
                st.markdown(f"""
                <div style="background:{bg_col}; border:1.5px solid {bd_col}; border-radius:10px; padding:14px; text-align:center;">
                    <span style="font-size:13px; color:#475569;">कुल योग (Compound ➔ Single)</span>
                    <div style="font-size:26px; font-weight:900; color:#1E293B; margin:4px 0;">{compat_eval['compound_sum']} ➔ {compat_eval['single_digit']}</div>
                    <small style="color:#2563EB;">स्वामी: {compat_eval['lord']}</small>
                </div>
                """, unsafe_allow_html=True)
            with col_cmp2:
                st.markdown(f"**रेटिंग:** {compat_eval['rating']}")
                st.info(compat_eval["advice"])
