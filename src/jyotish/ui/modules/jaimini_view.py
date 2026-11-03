import streamlit as st
import pandas as pd
import importlib
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.core.ayurdaya import default_ayurdaya_engine

def render_jaimini_view(chart, tabs=None):
    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark

    if tabs is None:
        tabs = [
            '🔱 कारकांश व स्वांश',
            '👑 ७ चर कारक',
            '🌟 विशेष लग्न व योग',
            '🏰 १२ आरूढ़ पद',
            '🛡️ अर्गला व बाधा',
            '⏳ चर व त्रिकोण दशा',
            '⚔️ आयुर्दाय ( Longevity )'
        ]
    st.subheader("🔱 जैमिनी ज्योतिष, विशेष लग्न, आरूढ़ पद एवं अप्रकाशित उपग्रह (Jaimini Master Suite)")
    st.write("महर्षि जैमिनी उपदेश सूत्र एवं बृहत्पाराशर होराशास्त्र (BPHS) आधारित १० समर्पित प्रभाग: कारकांश, ७ चर कारक, विशेष लग्न, १२ आरूढ़ पद, राशि दृष्टि, अर्गला, ग्रह आरूढ़, आयुर्दाय, अप्रकाशित उपग्रह एवं शास्त्रीय सूत्र।")

    def _clean_html(s: str) -> str:
        return "".join(line.strip() for line in s.splitlines() if line.strip())

    try:
        import importlib
        import src.jyotish.services.jaimini_suite as js_mod
        importlib.reload(js_mod)
        j_res = js_mod.default_jaimini_suite_service.analyze_jaimini_suite(chart)
    except Exception as _e_js:
        j_res = {}

    try:
        import src.jyotish.core.jaimini as jm_mod
        importlib.reload(jm_mod)
        rashi_drishti_data = jm_mod.JaiminiCalculator.calculate_rashi_drishti(chart)
        argala_data = jm_mod.JaiminiCalculator.calculate_argala(chart)
        graha_arudha_data = jm_mod.JaiminiCalculator.calculate_graha_arudhas(chart)
    except Exception:
        rashi_drishti_data = {}
        argala_data = {}
        graha_arudha_data = {}

    try:
        jaimini_ayur = default_ayurdaya_engine.calculate_jaimini_longevity(chart)
        pindayu_res = default_ayurdaya_engine.calculate_pindayu(chart)
    except Exception:
        jaimini_ayur = {}
        pindayu_res = {}

    karakas_7 = j_res.get("karakas_7") or getattr(chart.jaimini, "karakas_7", {})
    sl_details = getattr(chart.jaimini, "special_lagnas_detail", {})
    ar_details = j_res.get("arudha_details") or getattr(chart.jaimini, "arudha_details", {})

    # SVG Chart: Chara Karaka Degrees Spectrum
    def _render_chara_karaka_svg(chart_obj, k7_dict: dict, is_dark: bool = False) -> str:
        bg = "#111827" if is_dark else "#FFFFFF"
        card_bdr = "#374151" if is_dark else "#E2E8F0"
        txt_col = "#F9FAFB" if is_dark else "#1E293B"
        sub_col = "#9CA3AF" if is_dark else "#64748B"
        bar_bg = "#374151" if is_dark else "#F1F5F9"

        karaka_meta = {
            "AK": ("आत्मकारक (AK)", "आत्मा, स्वभाव, मोक्ष", "#8B5CF6"),
            "AmK": ("अमात्यकारक (AmK)", "कर्म, आजीविका, मेधा", "#3B82F6"),
            "BK": ("भ्रातृकारक (BK)", "पराक्रम, गुरु, भ्राता", "#06B6D4"),
            "MK": ("मातृकारक (MK)", "माता, गृह, संपत्ति, सुख", "#10B981"),
            "PK": ("पुत्रकारक (PK)", "संतान, बुद्धि, मंत्र", "#F59E0B"),
            "GK": ("ज्ञातिकारक (GK)", "शत्रु, ऋण, रोग, विवाद", "#EF4444"),
            "DK": ("दाराकारक (DK)", "जीवनसाथी, काम, साझेदारी", "#EC4899")
        }

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 290" width="100%" style="background:{bg};border:1.5px solid {card_bdr};border-radius:12px;font-family:system-ui,-apple-system,sans-serif;">',
            f'<text x="24" y="26" fill="{txt_col}" font-size="13" font-weight="700">👑 जैमिनी ७ चर कारक भोगांश स्पेक्ट्रम (Chara Karaka Degrees Spectrum)</text>',
            f'<text x="540" y="26" fill="{sub_col}" font-size="11" font-weight="600">अंश सीमा: ०° से ३०° (घटते क्रम में)</text>'
        ]

        y = 52
        for k_code, (k_name, k_sig, col) in karaka_meta.items():
            p_name = k7_dict.get(k_code, "")
            p_obj = chart_obj.planets.get(p_name)
            deg = getattr(p_obj, "sign_degree", 15.0) if p_obj else 15.0
            deg_str = f"{deg:.2f}°"
            bar_w = int((deg / 30.0) * 410)

            svg.append(f'<text x="24" y="{y+13}" fill="{txt_col}" font-size="11" font-weight="700">{k_name}</text>')
            svg.append(f'<text x="180" y="{y+13}" fill="{col}" font-size="11" font-weight="bold">{p_name}</text>')
            svg.append(f'<rect x="250" y="{y+2}" width="410" height="15" rx="3" fill="{bar_bg}" opacity="0.6" />')
            svg.append(f'<rect x="250" y="{y+2}" width="{bar_w}" height="15" rx="3" fill="{col}" />')
            svg.append(f'<text x="670" y="{y+13}" fill="{col}" font-size="11" font-weight="bold">{deg_str}</text>')
            y += 33

        svg.append('</svg>')
        return "".join(svg)

    # 10 Dedicated Tabs for Jaimini Suite
    jtab1, jtab2, jtab3, jtab4, jtab5, jtab6, jtab7, jtab8, jtab9, jtab10 = st.tabs(tabs)

    # =========================================================================
    # TAB 1: कारकांश व स्वांश चक्र (Karakamsha & Swamsha Suite)
    # =========================================================================
    with jtab1:
        st.markdown("#### 🔱 जैमिनी कारकांश, स्वांश एवं मोक्ष वेध (Karakamsha & Swamsha Suite)")
        st.caption("महर्षि जैमिनी उपदेश सूत्र अनुसार नवमांश चक्र में आत्मकारक की स्थिति (कारकांश लग्न), स्वांश फल, इष्ट देवता एवं मोक्ष योग।")

        c_jk1, c_jk2, c_jk3, c_jk4 = st.columns(4)
        c_jk1.metric("आत्मकारक (AK)", f"{j_res.get('atmakaraka', 'Moon')}", "आत्मा का मूल स्वरूप")
        c_jk2.metric("कारकांश राशि (D9)", f"{j_res.get('karakamsha_sign', '-')}", f"Sign #{j_res.get('karakamsha_sign_id', 1)}")

        ishta_info = j_res.get("ishta_devata", {})
        c_jk3.metric("इष्ट देवता (Ishta)", f"{ishta_info.get('deity', 'श्री विष्णु')}", f"अवतार: {ishta_info.get('avatar', '-')}")

        dharma_info = j_res.get("dharma_devata", {})
        c_jk4.metric("धर्म देवता (Dharma)", f"{dharma_info.get('deity', 'श्री शिव')}", f"ग्रह: {dharma_info.get('planet', '-')}")

        st.markdown("---")
        st.markdown("##### 🏛️ कारकांश लग्न (D9) से द्वादश भावों में ग्रहीय स्थिति (Houses from Karakamsha)")

        h_kl = j_res.get("houses_from_kl", {})
        h_cols1 = st.columns(6)
        for h_num in range(1, 7):
            with h_cols1[h_num - 1]:
                pls = h_kl.get(h_num, [])
                pl_str = ", ".join(pls) if pls else "—"
                st.markdown(_clean_html(f"""
                <div style="background:#F8FAFC;border:1px solid #CBD5E1;border-radius:8px;padding:8px;text-align:center;margin-bottom:8px;">
                    <div style="font-weight:700;color:#1E3A8A;font-size:11px;">भाव {h_num}</div>
                    <div style="font-weight:700;color:#0F172A;font-size:12px;margin-top:2px;">{pl_str}</div>
                </div>
                """), unsafe_allow_html=True)

        h_cols2 = st.columns(6)
        for h_num in range(7, 13):
            with h_cols2[h_num - 7]:
                pls = h_kl.get(h_num, [])
                pl_str = ", ".join(pls) if pls else "—"
                bg_col = "#DCFCE7" if (h_num == 12 and "Ketu" in pls) else "#F8FAFC"
                bdr_col = "#86EFAC" if (h_num == 12 and "Ketu" in pls) else "#CBD5E1"
                st.markdown(_clean_html(f"""
                <div style="background:{bg_col};border:1px solid {bdr_col};border-radius:8px;padding:8px;text-align:center;margin-bottom:8px;">
                    <div style="font-weight:700;color:#1E3A8A;font-size:11px;">भाव {h_num}</div>
                    <div style="font-weight:700;color:#0F172A;font-size:12px;margin-top:2px;">{pl_str}</div>
                </div>
                """), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📜 स्वांश फल एवं जैमिनी योग (Swamsha Classical Yogas)")
        sw_yogas = j_res.get("swamsha_yogas", [])
        if sw_yogas:
            for yg in sw_yogas:
                st.markdown(_clean_html(f"""
                <div style="background:#FFFBEB;border-left:4px solid #F59E0B;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;">
                    <div style="font-weight:700;color:#B45309;font-size:13px;">{yg.get('title', '')} — <small style="color:#78350F;">{yg.get('sutra', '')}</small></div>
                    <div style="margin-top:4px;color:#1E293B;font-size:12px;">{yg.get('desc', '')}</div>
                </div>
                """), unsafe_allow_html=True)
        else:
            st.info("कारकांश में सामान्य ग्रह स्थिति है। आत्मकारक का ध्यान एवं इष्ट साधना कल्याणकारी है।")

        st.markdown("---")
        c_al1, c_al2 = st.columns(2)
        with c_al1:
            st.info(f"**🌟 आरूढ़ लग्न (AL) व जन्म लग्न संबंध:** {j_res.get('al_jl_harmony', 'उत्तम समन्वय')}")
        with c_al2:
            st.info(f"**💍 उपपद लग्न (UL) दांपत्य वेध:** {j_res.get('ul_summary', 'सामान्य अनुकूल')}")

    # =========================================================================
    # TAB 2: जैमिनी ७ चर कारक (7 Chara Karakas Scheme)
    # =========================================================================
    with jtab2:
        st.markdown("#### 👑 जैमिनी ७ चर कारक व्यवस्था (7 Chara Karakas Scheme)")
        st.caption("अंशों के आधार पर सर्वोच्च से निम्नतम क्रम में ७ चर कारक: आत्मकारक से दाराकारक तक।")

        # Top 3 Karaka cards
        ck1, ck2, ck3 = st.columns(3)
        ak_p = karakas_7.get("AK", "")
        ak_deg = getattr(chart.planets.get(ak_p), "sign_degree", 0.0) if ak_p else 0.0
        amk_p = karakas_7.get("AmK", "")
        amk_deg = getattr(chart.planets.get(amk_p), "sign_degree", 0.0) if amk_p else 0.0
        dk_p = karakas_7.get("DK", "")
        dk_deg = getattr(chart.planets.get(dk_p), "sign_degree", 0.0) if dk_p else 0.0

        ck1.metric("👑 आत्मकारक (AK - Soul)", f"{ak_p}", f"{ak_deg:.2f}° (सर्वोच्च अंश)")
        ck2.metric("💼 अमात्यकारक (AmK - Career)", f"{amk_p}", f"{amk_deg:.2f}° (द्वितीय अंश)")
        ck3.metric("💍 दाराकारक (DK - Spouse)", f"{dk_p}", f"{dk_deg:.2f}° (न्यूनतम अंश)")

        st.markdown("---")
        st.markdown("##### 📊 चर कारक भोगांश स्पेक्ट्रम आलेख")
        svg_ck_code = _render_chara_karaka_svg(chart, karakas_7, is_dark=is_night_mode or is_astrallis_mode)
        st.markdown(svg_ck_code, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📋 ७ चर कारक महा-तालिका (Master Chara Karaka Table)")

        karaka_definitions = {
            "AK": ("आत्मकारक (Atmakaraka)", "आत्मा का स्वभाव, प्रारब्ध कर्म, जीवन का मूल उद्देश्य एवं मोक्ष मार्ग"),
            "AmK": ("अमात्यकारक (Amatyakaraka)", "कर्मक्षेत्र, आजीविका, सामाजिक दायित्व, वित्त एवं बौद्धिक परामर्श"),
            "BK": ("भ्रातृकारक (Bhatrukaraka)", "पराक्रम, छोटे भाई-बहन, गुरु, मार्गदर्शक एवं साहसिक उपक्रम"),
            "MK": ("मातृकारक (Matrukaraka)", "माता, गृह, भूमि, अचल संपत्ति, वाहन, सुख एवं आंतरिक संतोष"),
            "PK": ("पुत्रकारक (Putrakaraka)", "संतान, बुद्धि, मंत्र सिद्धि, रचनात्मकता, पूर्वपुण्य एवं शिष्य"),
            "GK": ("ज्ञातिकारक (Gnatikaraka)", "शत्रु, रोग, ऋण, कोर्ट-कचहरी, पारिवारिक मतभेद एवं रुकावटें"),
            "DK": ("दाराकारक (Darakaraka)", "जीवनसाथी, दांपत्य सुख, व्यापारिक साझेदार, काम एवं भोग")
        }

        ck_table_rows = []
        for k_code, (k_full, k_duty) in karaka_definitions.items():
            p_name = karakas_7.get(k_code, "—")
            p_obj = chart.planets.get(p_name)
            p_sign = getattr(p_obj, "sign_name", "—") if p_obj else "—"
            p_deg = f"{getattr(p_obj, 'sign_degree', 0.0):.2f}°" if p_obj else "—"
            p_nak = f"{getattr(p_obj, 'nakshatra_name', '—')} ({getattr(p_obj, 'nakshatra_pada', 1)})" if p_obj else "—"
            p_house = f"भाव {getattr(p_obj, 'house_from_lagna', 1)}" if p_obj else "—"

            ck_table_rows.append({
                "कारक कोड": k_code,
                "कारक नाम": k_full,
                "ग्रह (Planet)": p_name,
                "अंश (Degree)": p_deg,
                "राशि (Sign)": p_sign,
                "भाव (House)": p_house,
                "नक्षत्र (Nakshatra)": p_nak,
                "शास्त्रीय दायित्व एवं फल": k_duty
            })

        st.dataframe(pd.DataFrame(ck_table_rows), use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 3: विशेष लग्न एवं राजयोग (Special Lagnas Suite)
    # =========================================================================
    with jtab3:
        st.markdown("#### 🌟 विशेष लग्न विश्लेषण एवं राजयोग (Special Lagnas Suite)")
        st.caption("बृहत्पाराशर होराशास्त्र एवं जैमिनी सूत्रों अनुसार धन, सत्ता, समृद्धि, प्राण एवं वर्णदा लग्न।")

        if sl_details:
            sl1, sl2, sl3, sl4 = st.columns(4)
            hl = sl_details.get("HL", {})
            gl = sl_details.get("GL", {})
            sl = sl_details.get("SL", {})
            il = sl_details.get("IL", {})

            sl1.metric("👑 होरा लग्न (HL - Wealth)", f"{hl.get('sign', '-')}", f"{hl.get('degree', 0):.2f}°")
            sl2.metric("⚡ घटी लग्न (GL - Power)", f"{gl.get('sign', '-')}", f"{gl.get('degree', 0):.2f}°")
            sl3.metric("🌸 श्री लग्न (SL - Prosperity)", f"{sl.get('sign', '-')}", f"{sl.get('degree', 0):.2f}°")
            sl4.metric("💰 इन्दु लग्न (IL - Dhana)", f"{il.get('sign', '-')}", f"Lord: {il.get('lord', '-')}")

            st.markdown("---")
            st.markdown("##### 📋 विशेष लग्न विस्तृत सारणी")

            sl_rows = []
            for k_code, k_info in sl_details.items():
                sl_rows.append({
                    "लग्न कोड": k_code,
                    "विशेष लग्न नाम": k_info.get("name_hi", k_code),
                    "राशि (Sign)": k_info.get("sign", ""),
                    "अंश (Degree)": f"{k_info.get('degree', 0):.2f}°" if k_info.get("degree", 0) > 0 else "—",
                    "राशि स्वामी": k_info.get("lord", ""),
                    "शास्त्रीय प्रयोजन एवं फल": k_info.get("purpose_hi", "")
                })
            st.dataframe(pd.DataFrame(sl_rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### 👑 जैमिनी राजयोग एवं धनयोग समन्वय (Jaimini Raja Yoga Analysis)")
            st.markdown(_clean_html("""
            <div style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:10px;padding:14px;margin-bottom:12px;">
                <div style="font-weight:700;color:#166534;font-size:14px;">१. महाराज योग सूत्र (JL, HL & GL Alignment)</div>
                <div style="font-size:12.5px;color:#1E293B;margin-top:6px;line-height:1.5;">
                    यदि जन्म लग्न (JL), होरा लग्न (HL) एवं घटी लग्न (GL) तीनों पर किसी एक ही शुभ ग्रह की दृष्टि हो, अथवा इनके स्वामी परस्पर केंद्र/त्रिकोण में स्थित हों, तो जातक को समाज में सर्वोच्च सत्ता, प्रतिष्ठा एवं अपार संपत्ति की प्राप्ति होती है।
                </div>
            </div>
            <div style="background:#EFF6FF;border:1.5px solid #93C5FD;border-radius:10px;padding:14px;">
                <div style="font-weight:700;color:#1E40AF;font-size:14px;">२. इन्दु लग्न धन समृद्धि सिद्धांत (Indu Lagna Wealth Reservoir)</div>
                <div style="font-size:12.5px;color:#1E293B;margin-top:6px;line-height:1.5;">
                    इन्दु लग्न में यदि उच्च, स्वराशि अथवा शुभ ग्रह स्थित हों, तो जातक कोट्यधिपति (अत्यधिक धनवान) बनता है। यदि क्रूर ग्रह हों किंतु मित्र राशि में हों, तो मध्यम धन लाभ होता है।
                </div>
            </div>
            """), unsafe_allow_html=True)

    # =========================================================================
    # TAB 4: सम्पूर्ण १२ आरूढ़ पद (All 12 Arudha Padas)
    # =========================================================================
    with jtab4:
        st.markdown("#### 🏰 सम्पूर्ण द्वादश आरूढ़ पद (All 12 Arudha Padas Matrix)")
        st.caption("भावेश की दूरी अनुसार शास्त्रीय अपवादों (1st Lord in 1st/7th -> 10th/4th) सहित संपूर्ण १२ आरूढ़ पद।")

        if ar_details:
            ak_col1, ak_col2, ak_col3, ak_col4 = st.columns(4)
            al_v = ar_details.get("AL", {})
            ul_v = ar_details.get("A12", ar_details.get("UL", {}))
            a10_v = ar_details.get("A10", {})
            a2_v = ar_details.get("A2", {})

            ak_col1.metric("🌟 आरूढ़ लग्न (AL)", f"{al_v.get('pada_sign_name', '-')}", f"भाव {al_v.get('pada_house_from_lagna', 1)}")
            ak_col2.metric("💍 उपपद लग्न (UL)", f"{ul_v.get('pada_sign_name', '-')}", f"भाव {ul_v.get('pada_house_from_lagna', 12)}")
            ak_col3.metric("👑 राज्य पद (A10)", f"{a10_v.get('pada_sign_name', '-')}", f"भाव {a10_v.get('pada_house_from_lagna', 10)}")
            ak_col4.metric("💰 कोष पद (A2)", f"{a2_v.get('pada_sign_name', '-')}", f"भाव {a2_v.get('pada_house_from_lagna', 2)}")

            st.markdown("---")
            st.markdown("##### 📋 १२ आरूढ़ पद विस्तृत विवरण तालिका")

            ar_table_rows = []
            for a_code, a_val in ar_details.items():
                ar_table_rows.append({
                    "पद (Pada)": a_code,
                    "मूल भाव": f"भाव {a_val.get('house_num', '')} ({a_val.get('house_sign', '')})",
                    "भावेश": f"{a_val.get('lord_name', '')} ({a_val.get('lord_sign', '')})",
                    "दूरी": f"{a_val.get('distance', 0)} भाव",
                    "शास्त्रीय अपवाद": a_val.get("exception", "सामान्य"),
                    "आरूढ़ राशि": a_val.get("pada_sign_name", ""),
                    "लग्न से भाव": f"भाव {a_val.get('pada_house_from_lagna', '')}",
                    "कारकत्व एवं फल": a_val.get("signification_hi", "")
                })

            st.dataframe(pd.DataFrame(ar_table_rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            col_arp1, col_arp2 = st.columns(2)
            with col_arp1:
                st.markdown(_clean_html(f"""
                <div style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:10px;padding:14px;">
                    <b style="color:#166534;font-size:13px;">🌟 आरूढ़ लग्न (AL - Public Image): {al_v.get('pada_sign_name', '')}</b>
                    <div style="font-size:12px;color:#1E293B;margin-top:4px;line-height:1.5;">
                        संसार जातक को किस रूप में देखता है। यह सामाजिक प्रतिष्ठा, बाह्य प्रभाव एवं भौतिक उपलब्धियों का वास्तविक आईना है।
                    </div>
                </div>
                """), unsafe_allow_html=True)
            with col_arp2:
                st.markdown(_clean_html(f"""
                <div style="background:#FFF1F2;border:1.5px solid #FECDD3;border-radius:10px;padding:14px;">
                    <b style="color:#9F1239;font-size:13px;">💍 उपपद लग्न (UL / A12 - Spouse): {ul_v.get('pada_sign_name', '')}</b>
                    <div style="font-size:12px;color:#1E293B;margin-top:4px;line-height:1.5;">
                        दांपत्य जीवन, जीवनसाथी का परिवार, वैवाहिक सुख एवं स्थिरता। उपपद लग्न पर शुभ ग्रहों की दृष्टि स्थायी विवाह कराती है।
                    </div>
                </div>
                """), unsafe_allow_html=True)

    # =========================================================================
    # TAB 5: जैमिनी राशि दृष्टि (Rashi Drishti Aspect Grid)
    # =========================================================================
    with jtab5:
        st.markdown("#### 📡 जैमिनी राशि दृष्टि (Jaimini Rashi Drishti & Aspects)")
        st.info("📌 **मौलिक राशि दृष्टि नियम:** चर राशियाँ ➔ स्थिर राशियों को देखती हैं (निकटवर्ती छोड़कर) | स्थिर राशियाँ ➔ चर राशियों को देखती हैं (निकटवर्ती छोड़कर) | द्विस्वभाव राशियाँ ➔ अन्य द्विस्वभाव राशियों को देखती हैं।")

        if rashi_drishti_data:
            rd_rows = []
            for k, v in rashi_drishti_data.items():
                s_obj = next((s for s in chart.houses if s.sign_name == k), None)
                occ_str = ", ".join(s_obj.occupants) if (s_obj and s_obj.occupants) else "—"
                d_str = ", ".join(v) if v else "—"

                rd_rows.append({
                    "राशि (Sign)": k,
                    "राशि में स्थित ग्रह": occ_str,
                    "दृष्टि प्राप्त राशियाँ (Aspects)": d_str,
                    "दृष्टियों की कुल संख्या": f"{len(v)} राशियाँ"
                })

            st.dataframe(pd.DataFrame(rd_rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            col_rd_exp1, col_rd_exp2 = st.columns(2)
            with col_rd_exp1:
                st.markdown("""
                **चर राशियों की दृष्टि (मेष, कर्क, तुला, मकर):**
                - मेष ➔ सिंह, वृश्चिक, कुंभ को देखता है (निकटवर्ती वृषभ को छोड़कर)।
                - कर्क ➔ वृश्चिक, कुंभ, वृषभ को देखता है (निकटवर्ती सिंह को छोड़कर)।
                - तुला ➔ कुंभ, वृषभ, सिंह को देखता है (निकटवर्ती वृश्चिक को छोड़कर)।
                - मकर ➔ वृषभ, सिंह, वृश्चिक को देखता है (निकटवर्ती कुंभ को छोड़कर)।
                """)
            with col_rd_exp2:
                st.markdown("""
                **द्विस्वभाव राशियों की दृष्टि (मिथुन, कन्या, धनु, मीन):**
                - प्रत्येक द्विस्वभाव राशि अन्य तीनों द्विस्वभाव राशियों को पूर्ण दृष्टि से देखती है।
                - मिथुन ➔ कन्या, धनु, मीन को देखता है।
                - कन्या ➔ धनु, मीन, मिथुन को देखती है।
                - धनु ➔ मीन, मिथुन, कन्या को देखता है।
                - मीन ➔ मिथुन, कन्या, धनु को देखता है।
                """)

    # =========================================================================
    # TAB 6: अर्गला एवं विरोधार्गला (Argala Intervention Matrix)
    # =========================================================================
    with jtab6:
        st.markdown("#### 🔗 अर्गला एवं विरोधार्गला (Argala & Virodhargala Suite)")
        st.info("📌 **अर्गला सम्बंध:** द्वितीय भाव (धन अर्गला ⟷ १२वां विरोधी) | चतुर्थ भाव (सुख अर्गला ⟷ १०वां विरोधी) | एकादश भाव (लाभ अर्गला ⟷ ३रा विरोधी) | पंचम भाव (पुत्र अर्गला ⟷ ९वां विरोधी)।")

        if argala_data:
            arg_rows = []
            for k, v in argala_data.items():
                dhana = v.get("dhana_argala", {})
                sukha = v.get("sukha_argala", {})
                labha = v.get("labha_argala", {})

                dh_str = f"ग्रह: {', '.join(dhana.get('planets', [])) or '—'} | विरोध: {', '.join(dhana.get('virodha', [])) or '—'} ({'✅ प्रभावी' if dhana.get('effective') else 'निष्प्रभावी'})"
                su_str = f"ग्रह: {', '.join(sukha.get('planets', [])) or '—'} | विरोध: {', '.join(sukha.get('virodha', [])) or '—'} ({'✅ प्रभावी' if sukha.get('effective') else 'निष्प्रभावी'})"
                la_str = f"ग्रह: {', '.join(labha.get('planets', [])) or '—'} | विरोध: {', '.join(labha.get('virodha', [])) or '—'} ({'✅ प्रभावी' if labha.get('effective') else 'निष्प्रभावी'})"

                arg_rows.append({
                    "भाव": f"भाव {v.get('bhava', k)} ({v.get('sign', '')})",
                    "द्वितीय अर्गला (Dhana)": dh_str,
                    "चतुर्थ अर्गला (Sukha)": su_str,
                    "एकादश अर्गला (Labha)": la_str,
                    "सक्रिय अर्गलाएँ": f"{v.get('total_argalas', 0)} / 3"
                })

            st.dataframe(pd.DataFrame(arg_rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("""
            **शास्त्रीय अर्गला सिद्धांत (BPHS Ch. 31):**
            - **अर्गला (Intervention):** किसी भाव या ग्रह पर अनुकूल या प्रतिकूल हस्तक्षेप जो उसके फल को नियंत्रित करता है।
            - **विरोधार्गला (Obstruction):** यदि विरोधी भाव में अर्गला कारक ग्रह से अधिक या समान बलवान ग्रह हों, तो अर्गला का प्रभाव निष्प्रभावी हो जाता है।
            - **शुभार्गला vs पापार्गला:** शुभ ग्रहों की अर्गला जीवन में स्वतः गति एवं सहज लाभ देती है, जबकि पाप ग्रहों की अर्गला दबाव व संघर्ष उत्पन्न करती है।
            """)

    # =========================================================================
    # TAB 7: ग्रह आरूढ़ पद (Graha Arudhas)
    # =========================================================================
    with jtab7:
        st.markdown("#### 🌍 ग्रह आरूढ़ पद (Graha Arudha Padas)")
        st.caption("प्रत्येक ग्रह की राशि के स्वामी से उतनी ही दूरी आगे गिनने पर ग्रह आरूढ़ ज्ञात होता है — ग्रह के बाह्य सांसारिक प्रभाव का प्रकटन।")

        if graha_arudha_data:
            ga_rows = []
            for k, v in graha_arudha_data.items():
                ar_sid = v.get("arudha_sign_id", 1)
                h_from_l = ((ar_sid - chart.lagna_sign_id) % 12) + 1

                ga_rows.append({
                    "ग्रह (Planet)": k,
                    "ग्रह राशि": v.get("planet_sign", "—"),
                    "राशि स्वामी": f"{v.get('planet_lord', '—')} ({v.get('lord_sign', '—')})",
                    "आरूढ़ राशि (Pada)": v.get("arudha_sign", "—"),
                    "लग्न से भाव": f"भाव {h_from_l}",
                    "शास्त्रीय प्रभाव एवं प्रकटन": v.get("meaning_hi", "—")
                })

            st.dataframe(pd.DataFrame(ga_rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.info("💡 **महत्व:** भाव आरूढ़ जहाँ भौतिक घटनाओं व परिस्थितियों का आईना है, वहीं ग्रह आरूढ़ व्यक्ति के आंतरिक ग्रह बल का समाज में किस रूप में प्रकटन हो रहा है, उसका सटीक विश्लेषण प्रस्तुत करता है।")

    # =========================================================================
    # TAB 8: आयुर्दाय एवं दीर्घायु (Jaimini Longevity Engine)
    # =========================================================================
    with jtab8:
        st.markdown("#### ⏳ शास्त्रीय आयुर्दाय एवं दीर्घायु गणना (Jaimini Longevity Engine)")
        st.caption("महर्षि जैमिनी त्रिसूत्रीय आयु निर्णय (Three-Pair Method), कक्षा वृद्धि/ह्रास एवं पारम्परिक पिण्डायु गणना।")

        col_ay1, col_ay2 = st.columns(2)
        with col_ay1:
            st.markdown(_clean_html(f"""
            <div style="background:#FFFFFF;border:1.5px solid #10B981;border-radius:10px;padding:16px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <b style="font-size:15px;color:#065F46;">🔱 जैमिनी आयु वर्ग निर्णय</b>
                    <span style="background:#ECFDF5;color:#065F46;border:1.5px solid #10B981;border-radius:8px;padding:3px 10px;font-weight:800;font-size:12px;">
                        {jaimini_ayur.get('final_span', 'दीर्घायु')}
                    </span>
                </div>
                <div style="font-size:13px;color:#1E293B;line-height:1.6;margin-bottom:10px;">
                    • <b>अनुमानित आयु सीमा (Base Span):</b> <b style="font-size:15px;color:#0F766E;">{jaimini_ayur.get('estimated_years', 75)} वर्ष</b><br/>
                    • <b>युग्म १ (लग्नेश व अष्टमेश):</b> {jaimini_ayur.get('pair1', {}).get('result', '-')}<br/>
                    • <b>युग्म २ (लग्न व चन्द्र):</b> {jaimini_ayur.get('pair2', {}).get('result', '-')}<br/>
                    • <b>युग्म ३ (लग्न व होरा लग्न):</b> {jaimini_ayur.get('pair3', {}).get('result', '-')}
                </div>
                <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:6px;padding:6px 10px;font-size:11.5px;color:#166534;">
                    🌟 <b>कक्षा वृद्धि/ह्रास:</b> {', '.join(jaimini_ayur.get('modifiers', ['सामान्य']))}
                </div>
            </div>
            """), unsafe_allow_html=True)

        with col_ay2:
            st.markdown(_clean_html(f"""
            <div style="background:#FFFFFF;border:1.5px solid #2563EB;border-radius:10px;padding:16px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <b style="font-size:15px;color:#1E40AF;">⚖️ पारम्परिक पिण्डायु गणना (Pindayu)</b>
                    <span style="background:#EFF6FF;color:#1E40AF;border:1.5px solid #3B82F6;border-radius:8px;padding:3px 10px;font-weight:800;font-size:12px;">
                        शुद्ध पिण्डायु: {pindayu_res.get('net_pindayu_years', 72)} वर्ष
                    </span>
                </div>
                <div style="font-size:12px;color:#1E293B;line-height:1.5;margin-bottom:8px;">
                    उच्च-नीच अंशों एवं चक्रार्ध/शत्रुक्षेत्र हरण उपरांत प्राप्त शुद्ध आयु योगदान:
                </div>
            </div>
            """), unsafe_allow_html=True)

            p_pinda = pindayu_res.get("planet_contributions", {})
            p_pinda_list = [{"ग्रह (Planet)": p, "आयु योगदान (Years)": f"{y:.1f} वर्ष"} for p, y in p_pinda.items()]
            st.dataframe(pd.DataFrame(p_pinda_list), use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 9: अप्रकाशित उपग्रह (Invisible Upagrahas)
    # =========================================================================
    with jtab9:
        st.markdown("#### 👻 अप्रकाशित उपग्रह (Invisible Upagrahas & Gulika/Mandi)")
        st.caption("सूर्य, चन्द्र एवं शनि के आधार पर खगोलीय रूप से निर्धारित अप्रकाशित उपग्रह स्थिति एवं उनका शास्त्रीय प्रभाव।")

        if getattr(chart, "upagrahas", None):
            u = chart.upagrahas
            u_data = [
                {"उपग्रह (Upagraha)": "गुलिक (Gulika)", "राशि": u.gulika_sign_name, "भोगांश": f"{u.gulika_longitude:.2f}°", "प्रकृति": "शनि पुत्र / दारुण", "शास्त्रीय प्रभाव": "कष्ट, विघ्न, विषमय परिस्थितियां"},
                {"उपग्रह (Upagraha)": "मान्दि (Mandi)", "राशि": u.mandi_sign_name, "भोगांश": f"{u.mandi_longitude:.2f}°", "प्रकृति": "शनि अंश / मारक", "शास्त्रीय प्रभाव": "शारीरिक पीड़ा, रोग, आघात"},
                {"उपग्रह (Upagraha)": "धूम (Dhuma)", "राशि": "Calculated", "भोगांश": f"{u.dhuma_longitude:.2f}°", "प्रकृति": "सूर्य उपग्रह / संताप", "शास्त्रीय प्रभाव": "अग्नि भय, ताप, नेत्र कष्ट"},
                {"उपग्रह (Upagraha)": "व्यतीपात (Vyatipata)", "राशि": "Calculated", "भोगांश": f"{u.vyatipata_longitude:.2f}°", "प्रकृति": "सूर्य उपग्रह / विघ्न", "शास्त्रीय प्रभाव": "आकस्मिक हानि, पतन, भ्रम"},
                {"उपग्रह (Upagraha)": "परिवेष (Parivesha)", "राशि": "Calculated", "भोगांश": f"{u.parivesha_longitude:.2f}°", "प्रकृति": "चन्द्र उपग्रह / भय", "शास्त्रीय प्रभाव": "मानसिक चिंता, जल भय, अशांति"},
                {"उपग्रह (Upagraha)": "इन्द्रचाप (Indrachapa)", "राशि": "Calculated", "भोगांश": f"{u.indrachapa_longitude:.2f}°", "प्रकृति": "शुक्र उपग्रह / क्षय", "शास्त्रीय प्रभाव": "संसाधनों का क्षय, मिथ्या व्यय"},
                {"उपग्रह (Upagraha)": "उपकेतु (Upaketu)", "राशि": "Calculated", "भोगांश": f"{u.upaketu_longitude:.2f}°", "प्रकृति": "केतु उपग्रह / अनिष्ट", "शास्त्रीय प्रभाव": "विस्फोट, अचानक अवरोध, चोट"}
            ]
            st.dataframe(pd.DataFrame(u_data), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("""
            **गुलिक एवं मान्दि का विशेष शास्त्रीय विधान (Phaladeepika Ch. 25):**
            - गुलिक जिस भाव में बैठता है, उस भाव के फलों में बाधा एवं संघर्ष उत्पन्न करता है (तृतीय, षष्ठ व एकादश भाव को छोड़कर, जहाँ यह शत्रुओं का नाश करता है)।
            - गुलिक पर गुरु की शुभ दृष्टि होने से उसका विषमय दोष अत्यंत क्षीण हो जाता है।
            """)

    # =========================================================================
    # TAB 10: जैमिनी उपदेश सूत्र एवं प्रमाण
    # =========================================================================
    with jtab10:
        st.markdown("#### 📜 महर्षि जैमिनी उपदेश सूत्र एवं शास्त्रीय प्रमाण संदर्भ")
        st.caption("महर्षि जैमिनी विरचित प्रामाणिक उपदेश सूत्रों के मूल संस्कृत सूत्र, हिंदी अनुवाद एवं व्यावहारिक फलकथन सिद्धांत:")

        jm_shl = SHASTRIYA_SHLOKAS.get("jaimini_sutras", {})
        if jm_shl:
            jm_lines = "<br/>".join(jm_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(139, 92, 246, 0.08); border-left: 4px solid #8B5CF6; padding: 14px 18px; border-radius: 8px; margin-bottom: 16px;">
    <div style="font-weight: 700; color: #6D28D9; font-size: 13.5px; margin-bottom: 4px;">📖 {jm_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {jm_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {jm_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {jm_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("""
        ### १. राशि दृष्टि सूत्र (Upadesha Sutra 1.1.2-3)
        > **अभिपश्यन्ति रिक्षाणि॥ न स्वाभिमुखं तत्रस्थम्॥**
        - **अर्थ:** समस्त राशियाँ दृष्टि डालती हैं, परंतु अपने सम्मुख स्थित निकटवर्ती राशि को छोड़कर अन्य को देखती हैं।
        - **व्यावहारिक नियम:** चर राशियाँ (१, ४, ७, १०) निकटवर्ती स्थिर को छोड़कर अन्य तीन स्थिर राशियों को देखती हैं। स्थिर राशियाँ (२, ५, ८, ११) निकटवर्ती चर को छोड़कर अन्य चर राशियों को देखती हैं। द्विस्वभाव राशियाँ (३, ६, ९, १२) अन्य सभी द्विस्वभाव राशियों को परस्पर देखती हैं।

        ---

        ### २. अर्गला एवं विरोधार्गला सूत्र (Upadesha Sutra 1.1.4-6)
        > **दारादिभ्यश्चार्गला॥ न निहन्त्री॥ रिपुकेवला॥**
        - **अर्थ:** द्वितीय, चतुर्थ एवं एकादश भाव शुभ या अशुभ ग्रहों द्वारा 'अर्गला' (हस्तक्षेप/ताला) डालते हैं।
        - **विरोधार्गला नियम:** द्वादश भाव द्वितीय की, दशम भाव चतुर्थ की, तथा तृतीय भाव एकादश की अर्गला को अवरुद्ध करता है। यदि विरोधी भाव में अधिक बलवान ग्रह हों, तो अर्गला निष्प्रभावी हो जाती है।

        ---

        ### ३. आत्मकारक एवं कारकांश सूत्र (Upadesha Sutra 1.1.11, 1.2.1)
        > **अथात्मकारकः॥ सांशोऽधिककलः॥ तत्र कारकांशः॥**
        - **अर्थ:** जो ग्रह कुण्डली में सर्वाधिक अंशों (०° से ३०° के मध्य) पर स्थित होता है, वह आत्मकारक (AK) कहलाता है। आत्मकारक ग्रह नवमांश कुण्डली (D9) में जिस राशि में स्थित होता है, वही 'कारकांश लग्न' कहलाता है। कारकांश से जातक के प्रारब्ध, साधना एवं जीवन-ध्येय की सिद्धि परखी जाती है।

        ---

        ### ४. मोक्ष एवं इष्टदेवता सूत्र (Upadesha Sutra 1.2.69-72)
        > **केतौ कैवल्यम्॥ क्रियावान्॥**
        - **अर्थ:** कारकांश लग्न से १२वें भाव में यदि केतु स्थित हो अथवा उसकी दृष्टि हो, तो जातक को कैवल्य (मोक्ष) की प्राप्ति होती है।
        - यदि १२वें भाव पर गुरु या शुक्र की दृष्टि हो, तो जातक सात्विक मोक्ष मार्ग प्राप्त करता है।
        - कारकांश से १२वें भाव में स्थित ग्रह अथवा उसके स्वामी के आधार पर जातक के वास्तविक **इष्ट देवता** (जैसे सूर्य = शिव/राम, चन्द्र = गौरी/कृष्ण, मंगल = कार्तिकेय/हनुमान, बुध = विष्णु/नारायण, गुरु = शिव/दत्तात्रेय, शुक्र = लक्ष्मी/दुर्गा, शनि = कालभैरव/शास्ता) का प्रामाणिक निर्धारण होता है।

        ---

        ### ५. उपपद लग्न एवं दांपत्य सूत्र (Upadesha Sutra 1.3.1-4)
        > **उपपदं पदं पितुश्च॥**
        - **अर्थ:** द्वादश भाव के आरूढ़ को 'उपपद लग्न' (UL) कहा जाता है। उपपद पर शुभ ग्रहों की दृष्टि, उच्च ग्रह अथवा अपने स्वामी की उपस्थिति स्थायी, समृद्ध एवं सुखी दांपत्य जीवन प्रदान करती है। उपपद से द्वितीय भाव दांपत्य के स्थायित्व की कुंजी है।
        """)





    # =============================================================
    # TAB 10: DASHA SYSTEMS

