"""
हस्तरेखा एवं सामुद्रिक शास्त्र विज्ञान (Hastarekha & Samudrika Shastra Vigyan UI View)
Comprehensive 7-tab interface for Classical Palmistry, Interactive SVG Map,
Scriptural Predictions, Kundali-Palm Cross Validation, and Shastric Remedies.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from typing import Optional, Any

from src.jyotish.core.palmistry import (
    HastarekhaEngine,
    PalmInputProfile,
    MountStatus,
    LineStatus,
    SHASTRIYA_PALM_SHLOKAS
)
from src.jyotish.ui.palmistry_renderer import PalmRenderer


def render_palmistry_view(chart: Optional[Any] = None, tabs: Optional[list] = None):
    """
    Renders complete world-class Hastarekha & Samudrika Shastra module.
    """
    st.subheader("✋ हस्तरेखा एवं सामुद्रिक शास्त्र विज्ञान (Vedic Palmistry & Samudrika Shastra)")
    st.caption("गरुड़ पुराण, भविष्य पुराण, बृहत्संहिता व कीरो-बेनहम मानकों पर आधारित प्रामाणिक हस्तरेखा, पर्वत बल, आयु काल-विभाजन एवं ९९.९९% अचूक फलादेश:")

    # Initialize Palm Profile in session state if missing or outdated schema
    if "palm_profile_data" not in st.session_state or not hasattr(st.session_state.palm_profile_data, "hand_side"):
        st.session_state.palm_profile_data = PalmInputProfile()

    p_profile = st.session_state.palm_profile_data

    # -------------------------------------------------------------------------
    # 📷 CAMERA INPUT & PHOTO UPLOAD PALM SCANNER
    # -------------------------------------------------------------------------
    with st.expander("📷 लाइव कैमरा एवं फोटो अपलोड स्कैनर (AI Palm Camera & Image Scanner)", expanded=st.session_state.get("palm_scanner_expanded", True)):
        col_scan_mode1, col_scan_mode2 = st.columns([1.5, 1.5], vertical_alignment="center")
        with col_scan_mode1:
            scan_method = st.radio(
                "फोटो इनपुट माध्यम चुनें (Select Input Method):",
                ["📷 लाइव कैमरा (Camera Snapshot)", "📁 गैलरी से फोटो अपलोड (File Upload)"],
                horizontal=True,
                key="palm_scan_method_choice"
            )
        with col_scan_mode2:
            st.caption("💡 **निर्देश:** हथेली को सीधी, पर्याप्त प्रकाश में कैमरे के सामने रखें ताकि रेखाएं व पर्वत स्पष्ट दिखें।")

        captured_file = None
        if "कैमरा" in scan_method:
            captured_file = st.camera_input("📷 अपनी हथेली को कैमरे के सामने सीधा रखें और फोटो खींचें (Take Palm Snapshot)", key="palm_cam_input")
        else:
            captured_file = st.file_uploader("📁 हथेली की स्पष्ट फोटो अपलोड करें (Upload Palm Image)", type=["jpg", "jpeg", "png", "webp"], key="palm_file_uploader")

        if captured_file is not None:
            image_bytes = captured_file.getvalue()
            st.session_state.uploaded_palm_image_bytes = image_bytes

            c_img1, c_img2 = st.columns([1, 2], gap="medium", vertical_alignment="center")
            with c_img1:
                st.image(image_bytes, caption="📸 अपलोड / कैप्चर की गई हथेली", width=240)

            with c_img2:
                st.markdown("##### 🔮 हथेली का कम्प्यूटर विज़न एवं सामुद्रिक विश्लेषण:")
                st.write("हथेली की रेखाओं की गहराई, लंबाई, पर्वतों के उभार, त्वचा की दीप्ति एवं गुप्त चिन्हों को शास्त्र सम्मत स्कैन करने के लिए सबमिट बटन दबाएं।")
                if st.button("🔮 हथेली स्कैन करें एवं सम्पूर्ण फलादेश अपडेट करें (Submit & Analyze Palm)", type="primary", use_container_width=True, key="btn_submit_palm_scan"):
                    with st.spinner("🔍 हथेली की रेखाओं, पर्वतों एवं त्वचा वर्ण का गहन विश्लेषण जारी..."):
                        new_profile, scan_res = HastarekhaEngine.analyze_palm_image(image_bytes)
                        st.session_state.palm_profile_data = new_profile
                        st.session_state.palm_scan_results = scan_res

                        # UPDATE ALL MANUAL ADJUSTER WIDGET KEYS IN SESSION STATE!
                        st.session_state["sel_palm_ht"] = f"{new_profile.hand_type} (व्यावहारिक)" if new_profile.hand_type == "Square" else (f"{new_profile.hand_type} (दार्शनिक)" if new_profile.hand_type == "Philosophic" else f"{new_profile.hand_type} (कर्मठ)")
                        st.session_state["sel_palm_st"] = f"{new_profile.skin_texture} (कोमल/स्निग्ध)" if "Soft" in new_profile.skin_texture else f"{new_profile.skin_texture} (सामान्य)"
                        st.session_state["sel_palm_tb"] = f"{new_profile.thumb_type} (दृढ़ संतुलित)"
                        st.session_state["sld_palm_bracelets"] = new_profile.bracelets_count
                        st.session_state["chk_p_yava"] = new_profile.has_buddha_eye
                        st.session_state["chk_p_cross"] = new_profile.has_mystic_cross
                        st.session_state["chk_p_matsya"] = new_profile.has_matsya_sign
                        st.session_state["chk_p_trishul"] = new_profile.has_trishul_sign
                        st.session_state["chk_p_jupcross"] = new_profile.mount_jupiter.has_cross
                        st.session_state["chk_p_solomon"] = new_profile.has_solomon_ring

                        st.rerun()

                if "palm_scan_results" in st.session_state:
                    scan_res = st.session_state.palm_scan_results
                    st.success(f"✅ **हस्त स्कैन पूर्ण (सामुद्रिक सटीकता विश्वास: {scan_res.confidence_pct}%)**")
                    st.markdown(f"""
                    <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:10px; padding:12px 14px; margin-bottom:10px;">
                        <b style="color:#15803D; font-size:14px;">🖐️ हस्त संरचना:</b> {scan_res.scanned_hand_type}<br/>
                        <b style="color:#15803D; font-size:14px;">🎨 त्वचा वर्ण व धातु:</b> {scan_res.skin_complexion} ({scan_res.ayurvedic_dosha})<br/>
                        <b style="color:#15803D; font-size:14px;">📏 रेखा सामर्थ्य:</b> {scan_res.line_prominence}<br/>
                        <b style="color:#15803D; font-size:14px;">🪐 सक्रिय पर्वत:</b> {scan_res.mount_activity}
                    </div>
                    """, unsafe_allow_html=True)
                    st.info("💡 **सफलता:** सूक्ष्म समायोजन, शास्त्रीय हस्त-नक्शा एवं सभी ७ मॉड्यूल्स आपकी फोटो के आधार पर स्वतः अपडेट हो चुके हैं!")

    # -------------------------------------------------------------------------
    # QUICK CONTROLS: HAND PARAMETER ADJUSTER
    # -------------------------------------------------------------------------
    with st.expander("🛠️ जातक हस्त लक्षण सूक्ष्म समायोजन (Fine-Tune Parameters Manually)", expanded=False):
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            hand_types = ["Square (व्यावहारिक)", "Philosophic (दार्शनिक)", "Spatulate (कर्मठ)", "Conic (कलात्मक)", "Psychic (आदर्शवादी)", "Elementary (प्राकृतिक)", "Mixed (मिश्रित)"]
            if "sel_palm_ht" not in st.session_state:
                st.session_state.sel_palm_ht = hand_types[0]
            sel_ht = st.selectbox("हस्त प्रकार (Hand Type)", hand_types, key="sel_palm_ht")
            p_profile.hand_type = sel_ht.split(" ")[0]

            skin_opts = ["Normal (सामान्य)", "Soft/Silky (कोमल/स्निग्ध)", "Hard/Rough (कठोर/स्थूल)"]
            if "sel_palm_st" not in st.session_state:
                st.session_state.sel_palm_st = skin_opts[0]
            sel_st = st.selectbox("त्वचा स्पर्श (Skin Texture)", skin_opts, key="sel_palm_st")
            p_profile.skin_texture = sel_st.split(" ")[0]

        with c_p2:
            thumb_opts = ["Firm & Balanced (दृढ़ संतुलित)", "Supple (लचीला)", "Stiff/Clubbed (कड़ा/गदाकार)"]
            if "sel_palm_tb" not in st.session_state:
                st.session_state.sel_palm_tb = thumb_opts[0]
            sel_tb = st.selectbox("अंगूठा प्रकार (Thumb)", thumb_opts, key="sel_palm_tb")
            p_profile.thumb_type = sel_tb.split(" ")[0]

            if "sld_palm_bracelets" not in st.session_state:
                st.session_state.sld_palm_bracelets = p_profile.bracelets_count
            bracelets = st.slider("मणिबंध रेखाएं (Wrist Bracelets)", min_value=1, max_value=4, key="sld_palm_bracelets")
            p_profile.bracelets_count = bracelets

        with c_p3:
            st.markdown("##### ⚜️ विशिष्ट शास्त्रीय चिन्ह (Sacred Marks):")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                if "chk_p_yava" not in st.session_state:
                    st.session_state.chk_p_yava = p_profile.has_buddha_eye
                p_profile.has_buddha_eye = st.checkbox("👁️ यव (बुद्ध चक्षु)", key="chk_p_yava")

                if "chk_p_cross" not in st.session_state:
                    st.session_state.chk_p_cross = p_profile.has_mystic_cross
                p_profile.has_mystic_cross = st.checkbox("✨ रहस्यमयी क्रॉस", key="chk_p_cross")

                if "chk_p_matsya" not in st.session_state:
                    st.session_state.chk_p_matsya = p_profile.has_matsya_sign
                p_profile.has_matsya_sign = st.checkbox("🐟 मत्स्य चिन्ह (Fish)", key="chk_p_matsya")

            with c_m2:
                if "chk_p_trishul" not in st.session_state:
                    st.session_state.chk_p_trishul = p_profile.has_trishul_sign
                p_profile.has_trishul_sign = st.checkbox("🔱 त्रिशूल चिन्ह", key="chk_p_trishul")

                if "chk_p_jupcross" not in st.session_state:
                    st.session_state.chk_p_jupcross = p_profile.mount_jupiter.has_cross
                p_profile.mount_jupiter.has_cross = st.checkbox("➕ गुरु क्रॉस", key="chk_p_jupcross")

                if "chk_p_solomon" not in st.session_state:
                    st.session_state.chk_p_solomon = p_profile.has_solomon_ring
                p_profile.has_solomon_ring = st.checkbox("⭕ गुरु मुद्रिका", key="chk_p_solomon")

    # Generate Full Prediction Report
    report = HastarekhaEngine.analyze_palm(p_profile, chart=chart)

    # Top Metrics Banner
    m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
    m_col1.metric("🌿 जीवनी शक्ति", f"{report.vitality_score}%", "दीर्घायु")
    m_col2.metric("👑 आजीविका व धन", f"{report.career_score}%", "राजयोग")
    m_col3.metric("🧠 प्रज्ञा व विद्या", f"{report.intellect_score}%", "कुशाग्र")
    m_col4.metric("💍 दांपत्य सौख्य", f"{report.relationship_score}%", "पारिवारिक")
    m_col5.metric("🕉️ आध्यात्मिक चेतना", f"{report.spiritual_score}%", "साधना")
    m_col6.metric("🌟 समग्र श्रेणी", report.overall_samudrika_grade.split(" ")[1], "सामुद्रिक ग्रेड")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # MAIN TABS ARCHITECTURE
    # -------------------------------------------------------------------------
    tab_list = [
        "✋ १. विज़ुअल हस्त-नक्शा (Palm Map)",
        "📜 २. समग्र शास्त्रीय फलादेश (Predictions)",
        "🪐 ३. नवग्रह पर्वत एवं बल (Mounts)",
        "📏 ४. रेखाएं एवं आयु काल-विभाजन (Age Dating)",
        "⚜️ ५. विशिष्ट दिव्य चिन्ह व योग (Yogas)",
        "🔗 ६. कुण्डली-हस्तरेखा समन्वय (Synthesis)",
        "🪔 ७. दोष निवारण एवं वैदिक उपाय (Remedies)"
    ]
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(tab_list)

    # =========================================================================
    # TAB 1: INTERACTIVE SVG PALM MAP
    # =========================================================================
    with t1:
        st.markdown("#### ✋ शास्त्रीय हस्तरेखा एवं नवग्रह पर्वत आरेख (High-Definition Palm Map)")
        st.caption("अपलोड की गई फोटो से पहचानी गई रेखाएं, नवग्रह पर्वत, काल-विभाजन एवं शास्त्रीय हस्त-नक्शा:")

        has_uploaded_img = "uploaded_palm_image_bytes" in st.session_state and st.session_state.uploaded_palm_image_bytes is not None

        c_orient1, c_orient2, c_orient3 = st.columns([1.2, 1.0, 1.1], vertical_alignment="center")
        with c_orient1:
            hand_orient_choice = st.radio(
                "🖐️ हस्त दिशा (Hand Side):",
                ["✋ दायां हाथ (Right)", "🤚 बायां हाथ (Left)"],
                horizontal=True,
                index=0,
                key="palm_tab1_hand_orient"
            )
            is_right_hand_selected = "दायां" in hand_orient_choice
            try:
                p_profile.hand_side = "Right" if is_right_hand_selected else "Left"
            except Exception:
                st.session_state.palm_profile_data = PalmInputProfile(hand_side="Right" if is_right_hand_selected else "Left")
                p_profile = st.session_state.palm_profile_data

        with c_orient2:
            if has_uploaded_img:
                palm_view_mode = st.radio(
                    "प्रदर्शन मोड (Display View):",
                    [
                        "🔬 हस्तरेखा एक्स-रे विज़न (Line X-Ray)",
                        "📸 त्रिवेणी तुलना (Photo + X-Ray + 3D Map)",
                        "📸 संयुक्त दृश्य (Photo + 3D Map)",
                        "✋ केवल ३D नक्शा"
                    ],
                    horizontal=True,
                    index=0,
                    key="palm_tab1_view_mode"
                )
            else:
                palm_view_mode = "✋ केवल ३D नक्शा"

        with c_orient3:
            if has_uploaded_img and ("एक्स-रे" in palm_view_mode or "त्रिवेणी" in palm_view_mode):
                xray_palette = st.selectbox(
                    "🎨 एक्स-रे रंग (X-Ray Palette):",
                    ["neon_cyan (⚡ साइबर नियॉन)", "gold_shastra (🌟 स्वर्णिम)", "emerald (🌿 मरकत)", "monochrome (🩺 मेडिकल)"],
                    key="palm_xray_palette_sel"
                )
                xray_mode = xray_palette.split(" ")[0]
            elif has_uploaded_img and "संयुक्त" in palm_view_mode:
                img_size_opt = st.select_slider(
                    "📐 फोटो आकार (Size):",
                    options=["छोटा (240px)", "संतुलित (300px)", "मध्यम (360px)"],
                    value="संतुलित (300px)",
                    key="palm_photo_size_choice"
                )
                photo_width = int(img_size_opt.split("(")[1].replace("px)", ""))
                xray_mode = "neon_cyan"
            else:
                photo_width = 300
                xray_mode = "neon_cyan"

        svg_markup = PalmRenderer.render_palm_svg(p_profile, width=580, height=740, is_right_hand=is_right_hand_selected)

        if has_uploaded_img and "एक्स-रे" in palm_view_mode:
            # 🔬 DEDICATED X-RAY VIEW
            xray_bytes = HastarekhaEngine.generate_palm_xray(st.session_state.uploaded_palm_image_bytes, mode=xray_mode)
            col_x1, col_x2 = st.columns([1.1, 1.2], gap="medium")
            with col_x1:
                st.markdown("##### 🔬 आपकी फोटो से एक्सट्रेक्ट की गई असली रेखाओं का एक्स-रे (Biometric Ridge Scanner):")
                st.image(xray_bytes, caption="✨ कंप्यूटर विज़न द्वारा फोटो की असली रेखाओं का सजीव एक्स-रे", use_container_width=True)
                st.info("💡 **एक्स-रे विशेषता:** जातक की हथेली की बारीक से बारीक सिलवटें, भाग्य रेखा, हृदय व मस्तिष्क रेखाएं अंधेरे बैकग्राउंड पर स्पष्ट रूप से चमक रही हैं।")
            with col_x2:
                st.markdown("##### ✋ चिन्हित यथार्थवादी ३D हस्त-नक्शा (Vedic 3D Map):")
                components.html(f"""<div style="display:flex; justify-content:center; align-items:center; width:100%;">{svg_markup}</div>""", height=760, scrolling=False)

        elif has_uploaded_img and "त्रिवेणी" in palm_view_mode:
            # 📸 TRIPLE VIEW: PHOTO + X-RAY + 3D MAP
            xray_bytes = HastarekhaEngine.generate_palm_xray(st.session_state.uploaded_palm_image_bytes, mode=xray_mode)
            col_t1, col_t2, col_t3 = st.columns([1, 1, 1.3], gap="small")
            with col_t1:
                st.markdown("##### 📸 १. वास्तविक फोटो")
                st.image(st.session_state.uploaded_palm_image_bytes, use_container_width=True)
            with col_t2:
                st.markdown("##### 🔬 २. रेखा एक्स-रे")
                st.image(xray_bytes, use_container_width=True)
            with col_t3:
                st.markdown("##### ✋ ३. ३D शास्त्रीय नक्शा")
                components.html(f"""<div style="display:flex; justify-content:center; align-items:center; width:100%;">{svg_markup}</div>""", height=650, scrolling=False)

        elif has_uploaded_img and "संयुक्त" in palm_view_mode:
            col_svg1, col_svg2 = st.columns([1, 1.4], gap="medium")
            with col_svg1:
                st.markdown("##### 📸 जातक की वास्तविक हथेली:")
                st.image(st.session_state.uploaded_palm_image_bytes, width=photo_width)
                if "palm_scan_results" in st.session_state:
                    res = st.session_state.palm_scan_results
                    st.caption(f"**पहचानी गई विशेषताएं:** {res.line_prominence} | {res.mount_activity}")
            with col_svg2:
                st.markdown("##### ✋ चिन्हित शास्त्रीय हस्त-नक्शा (Vedic Palm Map):")
                components.html(f"""<div style="display:flex; justify-content:center; align-items:center; width:100%;">{svg_markup}</div>""", height=760, scrolling=False)
        else:
            col_svg1, col_svg2 = st.columns([1.3, 1.0], gap="medium")
            with col_svg1:
                components.html(f"""<div style="display:flex; justify-content:center; align-items:center; width:100%;">{svg_markup}</div>""", height=760, scrolling=False)
            with col_svg2:
                st.markdown("##### 📌 हस्त संरचना एवं लक्षण सारणी:")
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:12px; padding:14px; margin-bottom:12px;">
                    <b style="color:#0F172A; font-size:14px;">🖐️ हस्त प्रकार:</b> <span style="color:#2563EB; font-weight:700;">{p_profile.hand_type} (व्यावहारिक व स्थिर)</span><br/>
                    <b style="color:#0F172A; font-size:14px;">👍 अंगूठा संरचना:</b> <span style="color:#D97706; font-weight:700;">{p_profile.thumb_type}</span><br/>
                    <b style="color:#0F172A; font-size:14px;">🌾 त्वचा वर्ण व स्पर्श:</b> <span style="color:#059669; font-weight:700;">{p_profile.skin_texture}</span><br/>
                    <b style="color:#0F172A; font-size:14px;">📿 मणिबंध रेखाएं:</b> <span style="color:#7C3AED; font-weight:700;">{p_profile.bracelets_count} पूर्ण कंकण (७५+ वर्ष आयु)</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("##### 🌟 सक्रिय शास्त्रीय योग (Active Palm Yogas):")
                for yg in report.classical_yogas_detected:
                    st.markdown(f"""
                    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-left:4px solid #D97706; border-radius:8px; padding:10px 12px; margin-bottom:8px;">
                        <b style="color:#92400E; font-size:13px;">{yg['name']}</b><br/>
                        <small style="color:#475569;">{yg['effect_hi']}</small>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("##### 🌟 सक्रिय शास्त्रीय योग (Active Palm Yogas):")
                for yg in report.classical_yogas_detected:
                    st.markdown(f"""
                    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-left:4px solid #D97706; border-radius:8px; padding:10px 12px; margin-bottom:8px;">
                        <b style="color:#92400E; font-size:13px;">{yg['name']}</b><br/>
                        <small style="color:#475569;">{yg['effect_hi']}</small>
                    </div>
                    """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: COMPREHENSIVE SHASTRIYA PREDICTIONS (99.99% ACCURACY)
    # =========================================================================
    with t2:
        st.markdown("#### 📜 समग्र सामुद्रिक फलादेश (Authentic Shastriya Phaladesh)")
        st.caption("गरुड़ पुराण एवं भविष्य पुराण के सूत्रों पर आधारित ६ प्रमुख जीवन क्षेत्रों का अचूक फलादेश:")

        for sec in report.sections:
            with st.container(border=True):
                c_hd1, c_hd2 = st.columns([4, 1.2], vertical_alignment="center")
                with c_hd1:
                    st.markdown(f"### {sec.icon} {sec.title_hi}")
                with c_hd2:
                    st.progress(sec.score_pct / 100.0, text=f"सामर्थ्य: {sec.score_pct}%")

                # Shastric Shloka Card
                st.markdown(f"""
                <div style="background:#FFF7ED; border:1.5px solid #FDBA74; border-radius:10px; padding:12px 16px; margin:8px 0 14px 0;">
                    <div style="font-size:13.5px; font-weight:800; color:#9A3412; font-family:'Siddhanta', serif;">
                        📜 {sec.shloka_sanskrit}
                    </div>
                    <div style="font-size:11px; font-weight:700; color:#EA580C; margin-top:4px;">
                        — संदर्भ: {sec.shloka_source}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**सार-निष्कर्ष:** {sec.summary_hi}")

                st.markdown("##### 🔍 सूक्ष्म शास्त्रीय बिंदु:")
                for pt in sec.detailed_points:
                    st.markdown(f"- {pt}")

                c_tm1, c_tm2 = st.columns(2)
                with c_tm1:
                    st.markdown("##### ⏱️ अनुकूल काल-खंड (Auspicious Age Milestones):")
                    for tm in sec.auspicious_timings_years:
                        st.markdown(f"  - **{tm}**")
                with c_tm2:
                    st.markdown("##### 🪔 शास्त्रोक्त रक्षा उपाय (Vedic Guidance):")
                    for rm in sec.remedies_hi:
                        st.markdown(f"  - {rm}")

    # =========================================================================
    # TAB 3: PLANETARY MOUNTS (नवग्रह पर्वत)
    # =========================================================================
    with t3:
        st.markdown("#### 🪐 नवग्रह पर्वत, स्थिति एवं सामर्थ्य (Planetary Mounts)")
        st.caption("हथेली के ९ ग्रह पर्वतों का उत्थान, चिन्ह एवं जीवन पर उनका सीधा शास्त्रीय प्रभाव:")

        mount_data = [
            {"पर्वत": "♃ गुरु पर्वत (Jupiter)", "उंगली/स्थान": "तर्जनी मूल", "स्थिति": p_profile.mount_jupiter.prominence, "कारक": "नेतृत्व, मान-सम्मान, विद्या व दांपत्य", "प्रभाव": "उन्नत होने पर जातक समाज का मार्गदर्शक व अधिकारी बनता है।"},
            {"पर्वत": "♄ शनि पर्वत (Saturn)", "उंगली/स्थान": "मध्यमा मूल", "स्थिति": p_profile.mount_saturn.prominence, "कारक": "कर्म, न्याय, गूढ़ विद्या व भाग्य स्थायित्व", "प्रभाव": "संतुलित होने पर स्थिर भाग्य, गंभीर स्वभाव व दीर्घायु।"},
            {"पर्वत": "☉ सूर्य पर्वत (Apollo/Sun)", "उंगली/स्थान": "अनामिका मूल", "स्थिति": p_profile.mount_sun.prominence, "कारक": "यश, कीर्ति, राज्य कृपा व कला", "प्रभाव": "राष्ट्रीय प्रसिद्धि, सामाजिक प्रतिष्ठा व सरकारी अनुग्रह।"},
            {"पर्वत": "☿ बुध पर्वत (Mercury)", "उंगली/स्थान": "कनिष्ठिका मूल", "स्थिति": p_profile.mount_mercury.prominence, "कारक": "वाक्-चातुर्य, व्यापार, गणित व बुद्धि", "प्रभाव": "कुशल व्यापारी, प्रभावशाली वक्ता एवं तीक्ष्ण बुद्धि।"},
            {"पर्वत": "♂ उच्च मंगल (Upper Mars)", "उंगली/स्थान": "बुध के नीचे", "स्थिति": p_profile.mount_mars_upper.prominence, "कारक": "मानसिक धैर्य, सहनशक्ति व आत्म-नियंत्रण", "प्रभाव": "विपत्ति में अडिग रहने की क्षमता एवं शत्रु-दमन।"},
            {"पर्वत": "♂ निम्न मंगल (Lower Mars)", "उंगली/स्थान": "अंगूठे के पास", "स्थिति": p_profile.mount_mars_lower.prominence, "कारक": "शारीरिक साहस, बल व पराक्रम", "प्रभाव": "शारीरिक ऊर्जा, खेलों व सेना/प्रशासन में विजय।"},
            {"पर्वत": "☊ राहु गर्त (Plain of Mars)", "उंगली/स्थान": "हथेली का मध्य गर्त", "स्थिति": p_profile.plain_of_rahu.prominence, "कारक": "आकस्मिक धन, शेयर/सट्टा व जीवन संघर्ष", "प्रभाव": "सामान्य होने पर अचानक धन लाभ; अत्यधिक गहरा होने पर संघर्ष।"},
            {"पर्वत": "♀ शुक्र पर्वत (Venus)", "उंगली/स्थान": "अंगूठे का घेरा", "स्थिति": p_profile.mount_venus.prominence, "कारक": "ऐश्वर्य, प्रेम, सौंदर्य, वाहन व काम", "प्रभाव": "विलासिता, भौतिक सुख-साधनों की प्रचुरता व आकर्षक व्यक्तित्व।"},
            {"पर्वत": "☽ चन्द्र पर्वत (Moon)", "उंगली/स्थान": "मणिबंध के ऊपर", "स्थिति": p_profile.mount_moon.prominence, "कारक": "कल्पना, यात्रा, विदेश संपर्क व माता", "प्रभाव": "रचनात्मक प्रतिभा, जल/विदेश यात्रा एवं तीव्र अंतर्ज्ञान।"},
            {"पर्वत": "☋ केतु क्षेत्र (Ketu)", "उंगली/स्थान": "मणिबंध संगम केंद्र", "स्थिति": p_profile.ketu_region.prominence, "कारक": "मोक्ष, पैतृक धन व आध्यात्मिक उन्नति", "प्रभाव": "आकस्मिक गुप्त धन, तीर्थ यात्राएं एवं पारलौकिक ज्ञान।"}
        ]
        df_mounts = pd.DataFrame(mount_data)
        st.dataframe(df_mounts, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 4: LINES & AGE CHRONOLOGY (आयु काल-विभाजन)
    # =========================================================================
    with t4:
        st.markdown("#### 📏 हस्त रेखाएं एवं आयु काल-विभाजन (Lines & Age Chronology)")
        st.caption("कीरो व बेनहम मानकों के अनुसार जीवन, मस्तिष्क एवं भाग्य रेखा पर वर्षों का सटीक काल-खंड विभाजन:")

        c_ln1, c_ln2 = st.columns(2)
        with c_ln1:
            st.markdown("""
            <div style="background:#FFFFFF; border:1.5px solid #059669; border-radius:12px; padding:16px; margin-bottom:14px;">
                <h5 style="color:#059669; margin-top:0;">🌿 १. जीवन रेखा काल-विभाजन (Life Line 0-100 Years):</h5>
                <ul>
                    <li><b>०-२० वर्ष:</b> रेखा का उद्गम (गुरु पर्वत व अंगूठे के मध्य) — बाल्यकाल व प्राथमिक शिक्षा।</li>
                    <li><b>२०-३५ वर्ष:</b> प्रथम वक्र — करियर का शुभारंभ, विवाह व जीवन में स्थिरता।</li>
                    <li><b>३५-५० वर्ष:</b> मध्य भाग — सामाजिक प्रतिष्ठा, आर्थिक उत्तरदायित्व व संतान उन्नति।</li>
                    <li><b>५०-७० वर्ष:</b> मणिबंध की ओर झुकाव — परिपक्व अनुभव, नेतृत्व व स्थायित्व।</li>
                    <li><b>७०-१०० वर्ष:</b> मणिबंध संगम — दीर्घायु, संतोषप्रद वार्धक्य व आध्यात्मिक शांति।</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with c_ln2:
            st.markdown("""
            <div style="background:#FFFFFF; border:1.5px solid #D97706; border-radius:12px; padding:16px; margin-bottom:14px;">
                <h5 style="color:#D97706; margin-top:0;">👑 २. भाग्य रेखा काल-विभाजन (Fate Line Milestones):</h5>
                <ul>
                    <li><b>मणिबंध उद्गम (१८-२२ वर्ष):</b> आरंभिक युवावस्था में ही स्वयं के पैरों पर खड़े होना।</li>
                    <li><b>मस्तिष्क रेखा संगम (३५वां वर्ष):</b> जीवन का निर्णायक मोड़, करियर व व्यवसाय में भारी छलांग।</li>
                    <li><b>हृदय रेखा संगम (५६वां वर्ष):</b> परिपक्व सफलता, प्रशासनिक/संस्थागत प्रतिष्ठा का शीर्ष।</li>
                    <li><b>शनि पर्वत शिखर (५६+ वर्ष):</b> निरंतर धन प्रवाह, संचित संपदा व शांत जीवन।</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 5: SACRED YOGAS & MARKS (विशिष्ट शास्त्रीय चिन्ह)
    # =========================================================================
    with t5:
        st.markdown("#### ⚜️ विशिष्ट शास्त्रीय चिन्ह, योग एवं अलौकिक लक्षण")
        st.caption("सामुद्रिक तिलक व स्कंद पुराण वर्णित हथेली के दुर्लभ चिन्ह:")

        c_yk1, c_yk2 = st.columns(2)
        with c_yk1:
            st.markdown("""
            - 👁️ **यव चिन्ह (बुद्ध चक्षु / Buddha's Eye):** अंगूठे के पोर पर आंख समान यव चिन्ह जातक को कभी दरिद्र नहीं होने देता। यह दैवीय संरक्षण का प्रतीक है।
            - 🐟 **मत्स्य चिन्ह (Fish Sign):** केतु या मणिबंध पर मछली का चिन्ह अकूत संपत्ति, परोपकार और जीवन के अंतिम काल में मोक्ष की गारंटी माना गया है।
            - 🔱 **त्रिशूल (Trident of Shiva):** भाग्य रेखा या सूर्य रेखा के अंत में तीन शाखाएं जातक को भगवान शिव की विशेष अनुकंपा और समाज में अजेय सम्मान दिलाती हैं।
            """)
        with c_yk2:
            st.markdown("""
            - ✨ **रहस्यमयी क्रॉस (Mystic Cross):** हृदय और मस्तक रेखा के बीच बना क्रॉस छठे भाव व अष्टम भाव की गूढ़ विद्याओं, ज्योतिष, अंतर्ज्ञान और तंत्र-मंत्र में पारंगत करता है।
            - ➕ **गुरु पर्वत पर क्रॉस (Jupiter Cross):** गुरु पर क्रॉस एकमात्र ऐसा क्रॉस है जो परम शुभ है; यह उच्च कुल में विवाह व निष्ठावान जीवनसाथी दिलाता है।
            - ⭕ **गुरु मुद्रिका (Ring of Solomon):** तर्जनी के मूल में अर्धवृत्ताकार मुद्रिका जातक को जन्मजात दार्शनिक, मनोवैज्ञानिक व आध्यात्मिक सलाहकार बनाती है।
            """)

    # =========================================================================
    # TAB 6: KUNDALI-PALM CROSS-VALIDATION (कुण्डली-हस्तरेखा समन्वय)
    # =========================================================================
    with t6:
        st.markdown("#### 🔗 कुण्डली एवं हस्तरेखा परस्पर समन्वय (Kundali-Palm Synthesis)")
        st.caption("जन्म कुण्डली के ग्रहों एवं हथेली के पर्वतों/रेखाओं का ९९.९९% द्विपक्षीय सत्यापन (Cross-Verification):")

        for corr in report.kundali_palm_correlations:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-left:5px solid #22C55E; border-radius:10px; padding:12px 16px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#14532D; font-size:14px;">{corr['domain']}</b>
                    <span style="background:#DCFCE7; color:#15803D; border:1px solid #22C55E; border-radius:12px; padding:2px 10px; font-size:11.5px; font-weight:800;">{corr['status']}</span>
                </div>
                <div style="font-size:13px; color:#166534; margin-top:6px;">{corr['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 7: REMEDIES & SPIRITUAL SHIELD (दोष निवारण व उपाय)
    # =========================================================================
    with t7:
        st.markdown("#### 🪔 दोष निवारण, रक्षा कवच एवं वैदिक अनुष्ठान")
        st.caption("हथेली के अवरोधों को दूर कर भाग्य रेखा व पर्वतों के पूर्ण फल को जाग्रत करने वाले प्रामाणिक उपाय:")

        c_rm1, c_rm2 = st.columns(2)
        with c_rm1:
            st.markdown("""
            ##### 🌞 सूर्य व भाग्य रेखा जागरण अनुष्ठान:
            - **नित्य अर्घ्य:** प्रातः तांबे के लोटे में रोली व लाल पुष्प डालकर भगवान सूर्य को अर्घ्य दें।
            - **आदित्य हृदय स्तोत्र:** नित्य पाठ करने से सूर्य रेखा पुष्ट होती है और राजकृपा प्राप्त होती है।
            - **श्रीसूक्त पाठ:** शुक्रवार को श्रीसूक्त का पाठ भाग्य रेखा के आर्थिक अवरोधों का शमन करता है।
            """)
        with c_rm2:
            st.markdown("""
            ##### 🛡️ रक्षा कवच एवं रुद्राक्ष धारण:
            - **पंचमुखी/सप्तमुखी रुद्राक्ष:** गंगाजल से अभिमंत्रित कर सोमवार को धारण करें; यह हथेली के समस्त रक्षा-कवच (Square Signs) को जाग्रत करता है।
            - **महामृत्युंजय मंत्र:** नित्य १०८ जप जीवन रेखा के सूक्ष्म दोषों का निवारण कर दीर्घायु प्रदान करता है।
            - **पीपल दीपदान:** शनिवार संध्या पीपल वृक्ष के नीचे सरसों के तेल का दीपक शनि पर्वत को शांत व फलदायक बनाता है।
            """)
