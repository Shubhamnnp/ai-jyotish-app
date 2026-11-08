import streamlit as st
import pandas as pd
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.core.shadbala import default_shadbala_calculator

def render_shadbala_view(chart, tabs=None):
    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark

    if tabs is None:
        tabs = [
            '⚖️ षड्बल सारणी',
            '🔬 ६ बल विश्लेषण',
            '🏰 १२ भाव बल',
            '🎭 ग्रह अवस्था व इष्ट-कष्ट',
            '📐 दृष्टि चक्र (Aspectarium)',
            '📜 षड्बल प्रमाण'
        ]
    st.subheader("⚖️ षड्बल, भावबल एवं दृष्टि वेध चक्र (Comprehensive Shadbala & Aspectarium)")
    st.write("महर्षि पराशर विरचित बृहत्पाराशर होराशास्त्र (BPHS Ch. 27-29) आधारित षड्विध बल, द्वादश भाव बल, त्रिविध ग्रह अवस्थाएं, इष्ट-कष्ट फल एवं दृष्टि वेध मैट्रिक्स।")

    def _clean_html(s: str) -> str:
        return "".join(line.strip() for line in s.splitlines() if line.strip())

    if not getattr(chart, "shadbala", None):
        try:
            chart.shadbala = default_shadbala_calculator.calculate(chart)
        except Exception:
            pass

    sb_summary = getattr(chart, "shadbala", None)
    if not sb_summary:
        st.warning("⚠️ षड्बल गणना उपलब्ध नहीं है। कृपया जन्म विवरण पुनः सत्यापित करें।")
    else:
        sb_planets = sb_summary.planets
        sb_bhavas = sb_summary.bhava_bala
        seven_p = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        hi_planet_meta = {
            "Sun": ("☀️ सूर्य", "#F59E0B", "आत्मकारक, पिता, ओज"),
            "Moon": ("🌙 चन्द्र", "#38BDF8", "मनःकारक, माता, शांति"),
            "Mars": ("♂️ मंगल", "#EF4444", "पराक्रम, भूमि, साहस"),
            "Mercury": ("☿ बुध", "#10B981", "बुद्धि, व्यापार, वाणी"),
            "Jupiter": ("♃ गुरु", "#EAB308", "ज्ञान, वित्त, सन्तान"),
            "Venus": ("♀ शुक्र", "#EC4899", "सुख, वाहन, कला, दांपत्य"),
            "Saturn": ("♄ शनि", "#6366F1", "कर्म, अनुशासन, दीर्घायु")
        }

        # SVG Chart 1: Shadbala Rupa Ratio vs 1.0 Benchmark
        def _render_shadbala_ratio_svg(p_dict: dict, is_dark: bool = False) -> str:
            bg = "#111827" if is_dark else "#FFFFFF"
            card_bdr = "#374151" if is_dark else "#E2E8F0"
            txt_col = "#F9FAFB" if is_dark else "#1E293B"
            sub_col = "#9CA3AF" if is_dark else "#64748B"
            grid_col = "#374151" if is_dark else "#E2E8F0"

            chart_top = 55
            chart_bottom = 225
            h_span = chart_bottom - chart_top
            max_ratio = 2.0
            y_benchmark = chart_bottom - int((1.0 / max_ratio) * h_span)

            svg = [
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 295" width="100%" style="background:{bg};border:1.5px solid {card_bdr};border-radius:12px;font-family:system-ui,-apple-system,sans-serif;">',
                f'<text x="24" y="28" fill="{txt_col}" font-size="14" font-weight="700">⚖️ षड्बल रूपा सामर्थ्य अनुपात (Shadbala Strength Ratio vs 1.0 Benchmark)</text>',
                f'<text x="560" y="28" fill="{sub_col}" font-size="11" font-weight="600">न्यूनतम मानक: 1.00 (100% अपेक्षा)</text>'
            ]

            for r_val in [0.5, 1.0, 1.5, 2.0]:
                y_g = chart_bottom - int((r_val / max_ratio) * h_span)
                svg.append(f'<line x1="70" y1="{y_g}" x2="720" y2="{y_g}" stroke="{grid_col}" stroke-width="1" stroke-dasharray="3,3" />')
                svg.append(f'<text x="35" y="{y_g + 4}" fill="{sub_col}" font-size="10">{r_val:.1f}x</text>')

            # Benchmark Line
            svg.append(f'<line x1="70" y1="{y_benchmark}" x2="720" y2="{y_benchmark}" stroke="#EF4444" stroke-width="2" stroke-dasharray="5,3" />')
            svg.append(f'<text x="640" y="{y_benchmark - 6}" fill="#EF4444" font-size="10" font-weight="bold">मानक (1.0x)</text>')

            bar_w = 44
            start_x = 90
            step_x = 90

            for i, p in enumerate(seven_p):
                p_obj = p_dict.get(p)
                ratio = getattr(p_obj, "strength_ratio", 1.0) if p_obj else 1.0
                virupas = getattr(p_obj, "total_virupas", 350.0) if p_obj else 350.0
                name_hi, def_color, _ = hi_planet_meta.get(p, (p, "#3B82F6", ""))

                is_strong = ratio >= 1.0
                bar_col = def_color if is_strong else "#F87171"
                capped_ratio = min(max_ratio, max(0.1, ratio))
                bar_h = int((capped_ratio / max_ratio) * h_span)
                bar_y = chart_bottom - bar_h
                cur_x = start_x + (i * step_x)

                svg.append(f'<rect x="{cur_x}" y="{chart_top}" width="{bar_w}" height="{h_span}" fill="{grid_col}" opacity="0.15" rx="4" />')
                svg.append(f'<rect x="{cur_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="{bar_col}" rx="4" />')
                svg.append(f'<text x="{cur_x + bar_w//2}" y="{bar_y - 8}" fill="{bar_col}" font-size="11" font-weight="bold" text-anchor="middle">{ratio:.2f}x</text>')
                svg.append(f'<text x="{cur_x + bar_w//2}" y="{bar_y + 14}" fill="#FFFFFF" font-size="9" font-weight="bold" text-anchor="middle">{int(virupas)}V</text>')
                svg.append(f'<text x="{cur_x + bar_w//2}" y="{chart_bottom + 18}" fill="{txt_col}" font-size="11" font-weight="600" text-anchor="middle">{name_hi.split()[1]}</text>')

                badge_txt = "✅ बली" if is_strong else "⚠️ निर्बल"
                badge_col = "#10B981" if is_strong else "#EF4444"
                svg.append(f'<text x="{cur_x + bar_w//2}" y="{chart_bottom + 34}" fill="{badge_col}" font-size="10" font-weight="bold" text-anchor="middle">{badge_txt}</text>')

            svg.append('</svg>')
            return "".join(svg)

        # SVG Chart 2: Bhavabala 12 Houses
        def _render_bhavabala_svg(bhava_dict: dict, is_dark: bool = False) -> str:
            bg = "#111827" if is_dark else "#FFFFFF"
            card_bdr = "#374151" if is_dark else "#E2E8F0"
            txt_col = "#F9FAFB" if is_dark else "#1E293B"
            sub_col = "#9CA3AF" if is_dark else "#64748B"
            grid_col = "#374151" if is_dark else "#E2E8F0"

            vals = list(bhava_dict.values()) if bhava_dict else [400.0]
            max_v = max(vals)
            scale_max = max(650.0, max_v * 1.15)

            chart_top = 55
            chart_bottom = 225
            h_span = chart_bottom - chart_top

            svg = [
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 295" width="100%" style="background:{bg};border:1.5px solid {card_bdr};border-radius:12px;font-family:system-ui,-apple-system,sans-serif;">',
                f'<text x="24" y="28" fill="{txt_col}" font-size="14" font-weight="700">🏰 द्वादश भाव बल तुलना (12 Houses Potency - Virupas)</text>',
                f'<text x="510" y="28" fill="{sub_col}" font-size="11" font-weight="600">केंद्रादि बल + भावेश षड्बल + भावस्थ ग्रह</text>'
            ]

            # 400 Virupas Target line
            y_400 = chart_bottom - int((400.0 / scale_max) * h_span)
            svg.append(f'<line x1="40" y1="{y_400}" x2="735" y2="{y_400}" stroke="#9CA3AF" stroke-width="1" stroke-dasharray="3,3" />')
            svg.append(f'<text x="710" y="{y_400 - 5}" fill="{sub_col}" font-size="9">400V</text>')

            bar_w = 42
            start_x = 52
            step_x = 57

            house_meta = {
                1: ("केंद्र", "#0284C7"), 4: ("केंद्र", "#0284C7"), 7: ("केंद्र", "#0284C7"), 10: ("केंद्र", "#0284C7"),
                5: ("त्रिकोण", "#059669"), 9: ("त्रिकोण", "#059669"),
                3: ("उपचय", "#D97706"), 6: ("उपचय", "#D97706"), 11: ("उपचय", "#D97706"),
                2: ("धन/मार", "#8B5CF6"), 8: ("त्रिक", "#DC2626"), 12: ("त्रिक", "#DC2626")
            }

            for h in range(1, 13):
                val = bhava_dict.get(h, 300.0)
                h_tag, h_col = house_meta.get(h, ("भाव", "#3B82F6"))
                bar_h = int((val / scale_max) * h_span)
                bar_y = chart_bottom - bar_h
                cur_x = start_x + ((h - 1) * step_x)

                svg.append(f'<rect x="{cur_x}" y="{chart_top}" width="{bar_w}" height="{h_span}" fill="{grid_col}" opacity="0.12" rx="4" />')
                svg.append(f'<rect x="{cur_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="{h_col}" rx="4" />')
                svg.append(f'<text x="{cur_x + bar_w//2}" y="{bar_y - 6}" fill="{h_col}" font-size="10" font-weight="bold" text-anchor="middle">{int(val)}</text>')
                svg.append(f'<text x="{cur_x + bar_w//2}" y="{chart_bottom + 18}" fill="{txt_col}" font-size="11" font-weight="700" text-anchor="middle">H{h}</text>')
                svg.append(f'<text x="{cur_x + bar_w//2}" y="{chart_bottom + 32}" fill="{h_col}" font-size="9" font-weight="600" text-anchor="middle">{h_tag}</text>')

            svg.append('</svg>')
            return "".join(svg)

        # SVG Chart 3: Ishta vs Kashta Phala Balance
        def _render_ishta_kashta_svg(p_dict: dict, is_dark: bool = False) -> str:
            bg = "#111827" if is_dark else "#FFFFFF"
            card_bdr = "#374151" if is_dark else "#E2E8F0"
            txt_col = "#F9FAFB" if is_dark else "#1E293B"
            sub_col = "#9CA3AF" if is_dark else "#64748B"

            svg = [
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 270" width="100%" style="background:{bg};border:1.5px solid {card_bdr};border-radius:12px;font-family:system-ui,-apple-system,sans-serif;">',
                f'<text x="24" y="26" fill="{txt_col}" font-size="13" font-weight="700">🎭 इष्ट फल (शुभत्व) vs कष्ट फल (संघर्ष) संतुलन आलेख (0 से 60 विरूपा)</text>',
                f'<text x="540" y="26" fill="{sub_col}" font-size="11" font-weight="600">🟢 इष्ट फल | 🔴 कष्ट फल</text>'
            ]

            y = 52
            for p in seven_p:
                p_obj = p_dict.get(p)
                ishta = getattr(p_obj, "ishta_phala", 30.0) if p_obj else 30.0
                kashta = getattr(p_obj, "kashta_phala", 30.0) if p_obj else 30.0
                name_hi, col, _ = hi_planet_meta.get(p, (p, "#3B82F6", ""))

                total_ik = ishta + kashta
                ishta_pct = int((ishta / max(1.0, total_ik)) * 100)
                ishta_w = int((ishta / 60.0) * 230)
                kashta_w = int((kashta / 60.0) * 230)

                svg.append(f'<text x="24" y="{y+13}" fill="{txt_col}" font-size="11" font-weight="600">{name_hi}</text>')

                # Left bar: Ishta (Green)
                svg.append(f'<rect x="140" y="{y+2}" width="230" height="15" rx="3" fill="#334155" opacity="0.2" />')
                svg.append(f'<rect x="{370 - ishta_w}" y="{y+2}" width="{ishta_w}" height="15" rx="3" fill="#10B981" />')
                svg.append(f'<text x="135" y="{y+13}" fill="#10B981" font-size="10" font-weight="bold" text-anchor="end">{ishta:.1f}</text>')

                # Center Divider
                svg.append(f'<line x1="375" y1="{y}" x2="375" y2="{y+18}" stroke="#9CA3AF" stroke-width="1.5" />')

                # Right bar: Kashta (Red)
                svg.append(f'<rect x="380" y="{y+2}" width="230" height="15" rx="3" fill="#334155" opacity="0.2" />')
                svg.append(f'<rect x="380" y="{y+2}" width="{kashta_w}" height="15" rx="3" fill="#EF4444" />')
                svg.append(f'<text x="615" y="{y+13}" fill="#EF4444" font-size="10" font-weight="bold">{kashta:.1f}</text>')

                # Ratio percentage tag
                tag_col = "#10B981" if ishta >= kashta else "#EF4444"
                svg.append(f'<text x="690" y="{y+13}" fill="{tag_col}" font-size="11" font-weight="bold" text-anchor="middle">{ishta_pct}% शुभ</text>')

                y += 29

            svg.append('</svg>')
            return "".join(svg)

        # 6 Dedicated Shadbala Tabs
        sbtab1, sbtab2, sbtab3, sbtab4, sbtab5, sbtab6 = st.tabs(tabs)

        # =====================================================================
        # TAB 1: समग्र षड्बल सारणी एवं ग्रह सामर्थ्य
        # =====================================================================
        with sbtab1:
            st.markdown("#### ⚖️ समग्र षड्बल महा-सारणी एवं ग्रह सामर्थ्य क्रम")
            st.caption("७ ग्रहों का कुल विरूपा बल, रूपा मान, न्यूनतम BPHS अपेक्षा एवं सामर्थ्य अनुपात (Strength Ratio >= 1.00 = बलवान्)।")

            # Compute ranks and top metrics
            ranked_planets = sorted(seven_p, key=lambda p: getattr(sb_planets.get(p), "strength_ratio", 0.0), reverse=True)
            top_planet = ranked_planets[0]
            top_obj = sb_planets.get(top_planet)
            low_planet = ranked_planets[-1]
            low_obj = sb_planets.get(low_planet)

            strong_count = sum(1 for p in seven_p if getattr(sb_planets.get(p), "is_strong", False))
            avg_ratio = sum(getattr(sb_planets.get(p), "strength_ratio", 1.0) for p in seven_p) / 7.0

            k1, k2, k3, k4 = st.columns(4)
            top_hi = hi_planet_meta.get(top_planet, (top_planet, "", ""))[0]
            low_hi = hi_planet_meta.get(low_planet, (low_planet, "", ""))[0]

            k1.metric("🌟 सर्वाधिक बली ग्रह", f"{top_hi}", f"Ratio: {top_obj.strength_ratio:.2f}x ({int(top_obj.total_virupas)}V)")
            k2.metric("⚠️ न्यूनतम बली ग्रह", f"{low_hi}", f"Ratio: {low_obj.strength_ratio:.2f}x ({int(low_obj.total_virupas)}V)")
            k3.metric("👑 बलवान् ग्रह संख्या", f"{strong_count} / 7 ग्रह", "न्यूनतम मानक उत्तीर्ण")
            k4.metric("📊 औसत सामर्थ्य अनुपात", f"{avg_ratio:.2f}x", "समग्र कुण्डली बल")

            st.markdown("---")
            # SVG Ratio Chart
            st.markdown("##### 📊 षड्बल रूपा सामर्थ्य अनुपात आलेख (Shadbala Strength Ratio Chart)")
            svg_ratio_code = _render_shadbala_ratio_svg(sb_planets, is_dark=is_night_mode or is_astrallis_mode)
            st.markdown(svg_ratio_code, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 📋 षड्बल संपूर्ण घटक एवं सामर्थ्य महा-तालिका")

            sb_master_rows = []
            for rank_idx, p in enumerate(ranked_planets, start=1):
                p_obj = sb_planets.get(p)
                p_hi, _, _ = hi_planet_meta.get(p, (p, "", ""))
                is_str = p_obj.is_strong
                st_badge = "✅ बलवान्" if is_str else "⚠️ निर्बल"

                sb_master_rows.append({
                    "क्रम (Rank)": f"#{rank_idx}",
                    "ग्रह (Planet)": f"{p_hi} ({p})",
                    "स्थान बल": f"{p_obj.sthana_bala:.1f}",
                    "दिग्बल": f"{p_obj.dik_bala:.1f}",
                    "काल बल": f"{p_obj.kaala_bala:.1f}",
                    "चेष्टा बल": f"{p_obj.cheshta_bala:.1f}",
                    "नैसर्गिक बल": f"{p_obj.naisargika_bala:.1f}",
                    "दृग्बल": f"{p_obj.drik_bala:.1f}",
                    "कुल विरूपा": f"{p_obj.total_virupas:.1f}",
                    "रूपा (Rupas)": f"{p_obj.total_rupas:.2f}",
                    "अपेक्षित विरूपा": f"{p_obj.required_virupas:.0f}",
                    "सामर्थ्य अनुपात": f"{p_obj.strength_ratio:.2f}x",
                    "स्थिति (Status)": st_badge
                })

            st.dataframe(pd.DataFrame(sb_master_rows), use_container_width=True, hide_index=True)

        # =====================================================================
        # TAB 2: षड्विध बल गहन विश्लेषण
        # =====================================================================
        with sbtab2:
            st.markdown("#### 🔬 षड्विध बल गहन विश्लेषण (6-Fold Individual Bala Breakdown)")
            st.caption("महर्षि पराशर अनुसार षड्बल के ६ प्रमुख अंगों की विस्तृत शास्त्रीय गणना व विरूपा मान।")

            col_bf1, col_bf2 = st.columns(2)

            with col_bf1:
                st.markdown(_clean_html("""
                <div style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:10px;padding:14px;margin-bottom:12px;">
                    <div style="font-weight:700;color:#166534;font-size:14px;">1. स्थान बल (Sthana Bala - Positional Strength)</div>
                    <div style="font-size:12px;color:#1E293B;margin-top:6px;line-height:1.5;">
                        ग्रह की राशि, उच्च/नीच, सप्तवर्गज, ओझ-युग्म एवं केन्द्रादि स्थिति से प्राप्त बल।<br/>
                        • <b>उच्च बल:</b> परमोच्च अंश से दूरी अनुसार 0 से 60 विरूपा।<br/>
                        • <b>सप्तवर्गज बल:</b> मूलत्रिकोण, स्वराशि, मित्र राशि में स्थिति अनुसार वृद्धि।
                    </div>
                </div>
                """), unsafe_allow_html=True)

                st.markdown(_clean_html("""
                <div style="background:#EFF6FF;border:1.5px solid #93C5FD;border-radius:10px;padding:14px;margin-bottom:12px;">
                    <div style="font-weight:700;color:#1E40AF;font-size:14px;">2. दिग्बल (Dik Bala - Directional Strength)</div>
                    <div style="font-size:12px;color:#1E293B;margin-top:6px;line-height:1.5;">
                        दिशानुसार ग्रहों की विशिष्ट सामर्थ्य (60 विरूपा पूर्ण बल):<br/>
                        • <b>लग्न (पूर्व):</b> गुरु एवं बुध (ज्ञान व बुद्धि का उदय)<br/>
                        • <b>चतुर्थ (उत्तर):</b> चन्द्र एवं शुक्र (हृदय व सुख)<br/>
                        • <b>सप्तम (पश्चिम):</b> शनि (श्रम व कर्म का अस्ताचल)<br/>
                        • <b>दशम (दक्षिण):</b> सूर्य एवं मंगल (मध्याह्न तेज व पराक्रम)
                    </div>
                </div>
                """), unsafe_allow_html=True)

                st.markdown(_clean_html("""
                <div style="background:#FEF3C7;border:1.5px solid #FCD34D;border-radius:10px;padding:14px;">
                    <div style="font-weight:700;color:#92400E;font-size:14px;">3. काल बल (Kaala Bala - Temporal Strength)</div>
                    <div style="font-size:12px;color:#1E293B;margin-top:6px;line-height:1.5;">
                        समय, दिन-रात्रि, पक्ष एवं अयन से जनित शक्ति:<br/>
                        • <b>नतोन्नतांश बल:</b> दिवा जन्म में सूर्य, गुरु, शुक्र बली; रात्रि जन्म में चन्द्र, मंगल, शनि बली। बुध सर्वदा मध्यम बली।<br/>
                        • <b>पक्ष बल:</b> शुक्ल पक्ष में शुभ ग्रह बली, कृष्ण पक्ष में पाप ग्रह बली।
                    </div>
                </div>
                """), unsafe_allow_html=True)

            with col_bf2:
                st.markdown(_clean_html("""
                <div style="background:#FAF5FF;border:1.5px solid #D8B4FE;border-radius:10px;padding:14px;margin-bottom:12px;">
                    <div style="font-weight:700;color:#6B21A8;font-size:14px;">4. चेष्टा बल (Cheshta Bala - Motional Strength)</div>
                    <div style="font-size:12px;color:#1E293B;margin-top:6px;line-height:1.5;">
                        ग्रहों की गति (वक्री, मंद, तीव्र) से उत्पन्न चेष्टा सामर्थ्य:<br/>
                        • <b>वक्र गति (Retrograde):</b> पूर्ण 60 विरूपा चेष्टा बल।<br/>
                        • <b>अनुवक्र / मंद:</b> 30 से 45 विरूपा।<br/>
                        • सूर्य एवं चन्द्र का चेष्टा बल उनके अयन बल के समान होता है।
                    </div>
                </div>
                """), unsafe_allow_html=True)

                st.markdown(_clean_html("""
                <div style="background:#FFF1F2;border:1.5px solid #FECDD3;border-radius:10px;padding:14px;margin-bottom:12px;">
                    <div style="font-weight:700;color:#9F1239;font-size:14px;">5. नैसर्गिक बल (Naisargika Bala - Natural Strength)</div>
                    <div style="font-size:12px;color:#1E293B;margin-top:6px;line-height:1.5;">
                        सृष्टि के नियमानुसार ग्रहों की स्वाभाविक प्रकाशमय शक्ति (अपरिवर्तनीय):<br/>
                        सूर्य (60.00) > चन्द्र (51.43) > शुक्र (42.86) > गुरु (34.29) > बुध (25.71) > मंगल (17.14) > शनि (8.57)।
                    </div>
                </div>
                """), unsafe_allow_html=True)

                st.markdown(_clean_html("""
                <div style="background:#F1F5F9;border:1.5px solid #CBD5E1;border-radius:10px;padding:14px;">
                    <div style="font-weight:700;color:#334155;font-size:14px;">6. दृग्बल (Drik Bala - Aspectual Strength)</div>
                    <div style="font-size:12px;color:#1E293B;margin-top:6px;line-height:1.5;">
                        अन्य ग्रहों की शुभ व अशुभ दृष्टि से प्राप्त बल:<br/>
                        • शुभ ग्रहों (गुरु, शुक्र, शुभ बुध) की दृष्टि से विरूपा में वृद्धि होती है।<br/>
                        • पाप ग्रहों (शनि, मंगल, राहु) की क्रूर दृष्टि से विरूपा में ह्रास होता है।
                    </div>
                </div>
                """), unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 📊 ६-घटक बल तुलनात्मक तालिका (Virupas per Component)")

            comp_df_rows = []
            for p in seven_p:
                p_obj = sb_planets.get(p)
                p_hi, _, _ = hi_planet_meta.get(p, (p, "", ""))
                comp_df_rows.append({
                    "ग्रह": f"{p_hi} ({p})",
                    "स्थान बल": f"{p_obj.sthana_bala:.1f}",
                    "दिग्बल": f"{p_obj.dik_bala:.1f}",
                    "काल बल": f"{p_obj.kaala_bala:.1f}",
                    "चेष्टा बल": f"{p_obj.cheshta_bala:.1f}",
                    "नैसर्गिक बल": f"{p_obj.naisargika_bala:.1f}",
                    "दृग्बल": f"{p_obj.drik_bala:.1f}",
                    "कुल विरूपा": f"{p_obj.total_virupas:.1f}"
                })
            st.dataframe(pd.DataFrame(comp_df_rows), use_container_width=True, hide_index=True)

        # =====================================================================
        # TAB 3: द्वादश भाव बल तुलना
        # =====================================================================
        with sbtab3:
            st.markdown("#### 🏰 द्वादश भाव बल (12 Bhavabala & House Potency Suite)")
            st.caption("भावेश षड्बल (70%), केंद्रादि स्थिति बोनस एवं भावस्थ ग्रहों के आधार पर १२ भावों का सामर्थ्य निर्धारण।")

            # Find Top & Weak Houses
            sorted_bhavas = sorted(range(1, 13), key=lambda h: sb_bhavas.get(h, 0.0), reverse=True)
            best_h = sorted_bhavas[0]
            weak_h = sorted_bhavas[-1]

            hb1, hb2, hb3 = st.columns(3)
            hb1.metric("👑 सर्वाधिक बली भाव", f"भाव {best_h} ({chart.houses[best_h-1].sign_name})", f"{int(sb_bhavas.get(best_h, 0))} विरूपा")
            hb2.metric("⚠️ न्यूनतम बली भाव", f"भाव {weak_h} ({chart.houses[weak_h-1].sign_name})", f"{int(sb_bhavas.get(weak_h, 0))} विरूपा")
            hb3.metric("🎯 औसत भाव सामर्थ्य", f"{int(sum(sb_bhavas.values()) / 12)} विरूपा", "द्वादश भाव मानक: 400V")

            st.markdown("---")
            st.markdown("##### 📊 द्वादश भाव बल आलेख (12 Houses Potency Chart)")
            svg_bhava_code = _render_bhavabala_svg(sb_bhavas, is_dark=is_night_mode or is_astrallis_mode)
            st.markdown(svg_bhava_code, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 📋 द्वादश भाव विस्तृत बल एवं कारकत्व तालिका")

            bhava_rows = []
            house_significations = {
                1: ("तनु भाव", "शारीरिक स्वास्थ्य, व्यक्तित्व, ऊर्जा, आत्मविश्वास"),
                2: ("धन भाव", "संचित धन, कुटुंब, वाणी, प्राथमिक शिक्षा"),
                3: ("सहज भाव", "पराक्रम, छोटे भाई-बहन, संचार, साहस"),
                4: ("सुख भाव", "माता, गृह, भूमि, वाहन, मानसिक शांति"),
                5: ("पुत्र/बुद्धि", "संतान, मेधा, पूर्वपुण्य, उच्च शिक्षा, मंत्र"),
                6: ("रिपु/ऋण", "शत्रु विजय, रोग प्रतिरोधक क्षमता, नौकरी, सेवा"),
                7: ("जाया भाव", "दांपत्य जीवन, व्यापारिक साझेदार, जनसंपर्क"),
                8: ("आयु/रन्ध्र", "दीर्घायु, शोध, आकस्मिक लाभ, गुप्त ज्ञान"),
                9: ("धर्म/भाग्य", "भाग्य, तीर्थाटन, पिता, उच्च ज्ञान, गुरु कृपा"),
                10: ("कर्म भाव", "आजीविका, पद, प्रतिष्ठा, सामाजिक प्रभाव"),
                11: ("लाभ/आय", "आय, अभीष्ट सिद्धि, ज्येष्ठ भ्राता, मित्र"),
                12: ("व्यय भाव", "मोक्ष, विदेश वास, दान, शयन सुख, व्यय")
            }

            bhava_comps = getattr(sb_summary, "bhava_bala_components", {})
            for h in range(1, 13):
                h_obj = chart.houses[h - 1]
                h_lord = h_obj.lord
                lord_vir = getattr(sb_planets.get(h_lord), "total_virupas", 350.0) if sb_planets.get(h_lord) else 350.0
                total_b = sb_bhavas.get(h, 300.0)
                h_title, h_sig = house_significations.get(h, ("भाव", ""))

                h_comp = bhava_comps.get(h, {})
                adhipati_b = h_comp.get("adhipati_bala", round(lord_vir * 0.6, 1))
                dig_b = h_comp.get("dig_bala", 0.0)
                drishti_b = h_comp.get("drishti_bala", 0.0)

                if total_b >= 480:
                    status_lbl = "🌟 अति प्रबल"
                elif total_b >= 400:
                    status_lbl = "✅ प्रबल"
                elif total_b >= 330:
                    status_lbl = "⚖️ मध्यम"
                else:
                    status_lbl = "⚠️ अल्पबली"

                occ_str = ", ".join(h_obj.occupants) if h_obj.occupants else "—"

                bhava_rows.append({
                    "भाव": f"भाव {h} ({h_title})",
                    "राशि": h_obj.sign_name,
                    "भावेश": f"{h_lord} ({int(lord_vir)}V)",
                    "भावेश बल (60%)": f"{adhipati_b:.1f}",
                    "भाव दिग्बल": f"{dig_b:.1f}",
                    "भाव दृष्टि बल": f"{drishti_b:.1f}",
                    "कुल भाव बल": f"{int(total_b)} विरूपा",
                    "सामर्थ्य श्रेणी": status_lbl,
                    "भावस्थ ग्रह": occ_str,
                    "मुख्य जीवन क्षेत्र प्रभाव": h_sig
                })

            st.dataframe(pd.DataFrame(bhava_rows), use_container_width=True, hide_index=True)

        # =====================================================================
        # TAB 4: ग्रह अवस्थाएं एवं इष्ट-कष्ट फल
        # =====================================================================
        with sbtab4:
            st.markdown("#### 🎭 ग्रह अवस्थाएं एवं इष्ट-कष्ट फल (Planetary Avasthas & Ishta/Kashta Phala)")
            st.caption("महर्षि पराशर विरचित उच्च बल एवं चेष्टा बल आधारित इष्ट/कष्ट फल तथा बालादि, जाग्रतादि व दीप्तादि त्रिविध अवस्थाएं।")

            st.markdown("##### ⚖️ इष्ट फल (शुभत्व) vs कष्ट फल (संघर्ष) संतुलन आलेख")
            svg_ik_code = _render_ishta_kashta_svg(sb_planets, is_dark=is_night_mode or is_astrallis_mode)
            st.markdown(svg_ik_code, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 📋 ग्रह अवस्थाएं एवं शास्त्रीय फलदायिता तालिका")

            avastha_rows = []
            for p in seven_p:
                p_obj = sb_planets.get(p)
                p_hi, _, _ = hi_planet_meta.get(p, (p, "", ""))
                ishta_v = getattr(p_obj, "ishta_phala", 30.0)
                kashta_v = getattr(p_obj, "kashta_phala", 30.0)
                baladi_v = getattr(p_obj, "baladi_avastha", "युवा")
                jagratadi_v = getattr(p_obj, "jagratadi_avastha", "जाग्रत")
                deeptadi_v = getattr(p_obj, "deeptadi_avastha", "स्वस्थ")

                ik_ratio = int((ishta_v / max(1.0, ishta_v + kashta_v)) * 100)

                avastha_rows.append({
                    "ग्रह": f"{p_hi} ({p})",
                    "इष्ट फल (0-60)": f"{ishta_v:.1f}",
                    "कष्ट फल (0-60)": f"{kashta_v:.1f}",
                    "शुभ अनुपात": f"{ik_ratio}%",
                    "बालादि अवस्था": baladi_v,
                    "जाग्रतादि अवस्था": jagratadi_v,
                    "दीप्तादि अवस्था": deeptadi_v
                })

            st.dataframe(pd.DataFrame(avastha_rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            col_av1, col_av2, col_av3 = st.columns(3)
            with col_av1:
                st.markdown("""
                **१. बालादि अवस्था (उम्र अनुसार फल):**
                - **बाल (Infant):** १/४ (२५%) फल
                - **कुमार (Youth):** १/२ (५०%) फल
                - **युवा (Adult):** पूर्ण (१००%) फल
                - **वृद्ध (Old):** अल्प फल
                - **मृत (Dead):** शून्य या नगण्य फल
                """)
            with col_av2:
                st.markdown("""
                **२. जाग्रतादि अवस्था (चेतना स्थिति):**
                - **जाग्रत (Awake):** स्वराशि/उच्च ➔ पूर्ण चेतना व त्वरित फल
                - **स्वप्न (Dreaming):** मित्र/सम ➔ मध्यम व मिश्रित फल
                - **सुषुप्ति (Sleeping):** नीच/शत्रु ➔ निष्क्रिय व विलंबित फल
                """)
            with col_av3:
                st.markdown("""
                **३. दीप्तादि अवस्था (गरिमा):**
                - **दीप्त:** उच्च राशि में ➔ परमोच्च शुभ
                - **स्वस्थ:** स्वराशि में ➔ सुदृढ़ व अनुकूल
                - **मुदित:** मित्र राशि में ➔ प्रसन्न व सहयोगी
                - **दीन/विकल:** शत्रु/नीच/अस्त ➔ उपाय अपेक्षित
                """)

        # =====================================================================
        # TAB 5: दृष्टि वेध एवं कोणीय संबंध (Dynamic Aspectarium)
        # =====================================================================
        with sbtab5:
            st.markdown("#### 📐 डायनेमिक वैदिक एवं पाश्चात्य दृष्टि वेध चक्र (Dynamic Aspectarium & Orbs)")
            st.caption("Shri Jyoti Star एवं Parashara's Light ग्रेड 9x9 कोणीय अंतर मैट्रिक्स, पराशरीय विशेष दृष्टि (मंगल 4/8, गुरु 5/9, शनि 3/10) एवं पाश्चात्य प्रमुख कोणीय वेध (0°, 60°, 90°, 120°, 150°, 180°):")

            try:
                from src.jyotish.services.aspectarium import default_aspectarium_service
                asp_data = default_aspectarium_service.calculate_aspectarium(chart)
                asp_html = default_aspectarium_service.render_aspectarium_html(chart)

                c_as1, c_as2, c_as3 = st.columns(3)
                with c_as1:
                    st.metric("सक्रिय प्रमुख दृष्टियां (Western Aspects)", f"{asp_data['total_aspects_count']} संबंध", "युति, त्रिकोण, केंद्र, लाभ")
                with c_as2:
                    st.metric("वैदिक विशेष दृष्टियां (Vedic Drishtis)", f"{asp_data['total_drishti_count']} वेध", "मंगल, गुरु, शनि एवं सप्तम दृष्टि")
                with c_as3:
                    t_asp = min(asp_data["aspects"], key=lambda x: x["orb_abs"]) if asp_data["aspects"] else None
                    if t_asp:
                        st.metric("सर्वाधिक तीव्र वेध (Tightest Orb)", f"{t_asp['p1_hi']} {t_asp['symbol']} {t_asp['p2_hi']}", f"Orb: {t_asp['orb_str']} ({t_asp['motion_hi']})")
                    else:
                        st.metric("सर्वाधिक तीव्र वेध", "—", "—")

                st.markdown(asp_html.strip(), unsafe_allow_html=True)

                col_ad1, col_ad2 = st.columns(2)
                with col_ad1:
                    st.markdown("##### 🌟 पाश्चात्य एवं हार्मोनिक कोणीय संबंध (Major Aspects & Orbs)")
                    if asp_data["aspects"]:
                        asp_rows = []
                        for a in asp_data["aspects"]:
                            asp_rows.append({
                                "ग्रह १": f"{a['p1_hi']} ({a['planet1']})",
                                "दृष्टि प्रकार": f"{a['symbol']} {a['aspect_name']}",
                                "ग्रह २": f"{a['p2_hi']} ({a['planet2']})",
                                "वास्तविक कोण": f"{a['actual_angle']:.2f}°",
                                "ऑर्ब": f"{a['orb_str']}",
                                "गति": a["motion_hi"],
                                "प्रकृति": a["nature"]
                            })
                        st.dataframe(pd.DataFrame(asp_rows), use_container_width=True, hide_index=True)
                    else:
                        st.info("कोई प्रमुख कोणीय दृष्टि इस चार्ट में सक्रिय नहीं है।")

                with col_ad2:
                    st.markdown("##### 🔱 पराशरीय वैदिक विशेष दृष्टियां (Parashari Vedic Drishtis)")
                    if asp_data["vedic_drishtis"]:
                        vd_rows = []
                        for vd in asp_data["vedic_drishtis"]:
                            vd_rows.append({
                                "दृष्टि कर्ता ग्रह": f"{vd['drishti_kar']}",
                                "दृष्टि प्रकार": vd["drishti_type"],
                                "दृष्टि प्राप्त ग्रह": f"{vd['drishti_prapak']}",
                                "भाव अंतर": f"{vd['house_dist']} भाव दूरी",
                                "शास्त्रीय प्रभाव": vd["impact"]
                            })
                        st.dataframe(pd.DataFrame(vd_rows), use_container_width=True, hide_index=True)
                    else:
                        st.info("कोई वैदिक विशेष दृष्टि दर्ज नहीं हुई।")

            except Exception as _e_asp:
                st.error(f"Aspectarium गणना त्रुटि: {_e_asp}")

        # =====================================================================
        # TAB 6: षड्बल शास्त्रीय नियम एवं प्रमाण
        # =====================================================================
        with sbtab6:
            st.markdown("#### 📜 षड्बल, भावबल एवं इष्ट-कष्ट फल शास्त्रीय नियम एवं प्रमाण")
            st.caption("महर्षि पराशर विरचित बृहत्पाराशर होराशास्त्र (BPHS Ch. 27-29), सारावली एवं फलदीपिका के मूल संस्कृत श्लोक, हिंदी अनुवाद एवं गणितीय सूत्र:")

            # Shloka 1: Shadbala Pramana (BPHS Ch. 27)
            sb_shl = SHASTRIYA_SHLOKAS.get("shadbala_pramana", {})
            if sb_shl:
                sb_lines = "<br/>".join(sb_shl['shloka'].splitlines())
                st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.08); border-left: 4px solid #3B82F6; padding: 14px 18px; border-radius: 8px; margin-bottom: 15px;">
    <div style="font-weight: 700; color: #1D4ED8; font-size: 13.5px; margin-bottom: 4px;">📖 {sb_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {sb_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {sb_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {sb_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

            # Shloka 2: Ishta-Kashta Phala (BPHS Ch. 29 & Phaladeepika Ch. 4)
            ik_shl = SHASTRIYA_SHLOKAS.get("ishta_kashta_pramana", {})
            if ik_shl:
                ik_lines = "<br/>".join(ik_shl['shloka'].splitlines())
                st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 8px; margin-bottom: 15px;">
    <div style="font-weight: 700; color: #047857; font-size: 13.5px; margin-bottom: 4px;">📖 {ik_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {ik_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {ik_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>गणितीय सूत्र:</b> <code>इष्ट फल = √(उच्च बल × चेष्टा बल)</code> एवं <code>कष्ट फल = ६० - इष्ट फल</code>
    </div>
    </div>
    """, unsafe_allow_html=True)

            # Shloka 3: Bhavabala Pramana (BPHS Ch. 28)
            bb_shl = SHASTRIYA_SHLOKAS.get("bhavabala_pramana", {})
            if bb_shl:
                bb_lines = "<br/>".join(bb_shl['shloka'].splitlines())
                st.markdown(f"""
    <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 14px 18px; border-radius: 8px; margin-bottom: 15px;">
    <div style="font-weight: 700; color: #B45309; font-size: 13.5px; margin-bottom: 4px;">📖 {bb_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {bb_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {bb_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {bb_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

            st.markdown("""
            ### ⚖️ षड्बल न्यूनतम मानक एवं रूपा विधान (BPHS Ch. 27 Shloka 15-18)
            महर्षि पराशर के अनुसार किसी भी ग्रह को पूर्ण फल देने हेतु निम्नलिखित न्यूनतम विरूपा बल अनिवार्य है:
            - **बुध:** ४२० विरूपा (७.० रूप) — बुद्धि एवं व्यापार की जटिलताओं हेतु सर्वाधिक बल आवश्यक।
            - **सूर्य व गुरु:** ३९० विरूपा (६.५ रूप) — आत्मा, राज्य सत्ता, ज्ञान एवं ईश्वरीय कृपा के मुख्य आधार।
            - **चन्द्रमा:** ३६० विरूपा (६.० रूप) — मन, माता एवं जनसंपर्क का संतुलन।
            - **शुक्र:** ३३० विरूपा (५.५ रूप) — भोग, कला, वाहन एवं भौतिक समृद्धि।
            - **मंगल व शनि:** ३०० विरूपा (५.० रूप) — पुरुषार्थ, पराक्रम एवं कर्म का स्थायित्व।

            > *यदि किसी ग्रह का कुल विरूपा बल इस न्यूनतम मान से कम होता है, तो वह ग्रह अपनी महादशा अथवा अंतर्दशा में अभीष्ट फल देने में असमर्थ होकर संघर्ष उत्पन्न करता है।*

            ---

            ### 🧭 दिग्बल शास्त्रीय सूत्र (BPHS Ch. 27 Shloka 7-9)
            > **सूर्योदये दिने लग्ने गुरुबुधौ बलान्वितौ।**<br/>
            > **चतुर्थे चन्द्रशुक्रौ च पश्चिमे सूर्यपुत्रकः।**<br/>
            > **दशमे रविभौमौ च दिग्बलेनोत्तमाः स्मृताः॥**

            - **प्रथम भाव (लग्न - पूर्व):** गुरु एवं बुध को पूर्ण ६० विरूपा दिग्बल प्राप्त होता है।
            - **चतुर्थ भाव (पाताल - उत्तर):** चन्द्रमा एवं शुक्र उत्तर दिशा में पूर्ण दिग्बली होते हैं।
            - **सप्तम भाव (अस्त - पश्चिम):** शनि पश्चिम दिशा में सर्वोच्च दिग्बली होता है।
            - **दशम भाव (आकाश - दक्षिण):** सूर्य एवं मंगल मध्याह्न काल में दक्षिण दिशा में पूर्ण दिग्बली होते हैं।

            ---

            ### 🏰 भाव बल एवं कार्यसिद्धि का रहस्य (Saravali Ch. 39)
            - किसी भाव की सफलता केवल उसमें बैठे ग्रहों पर निर्भर नहीं करती, अपितु उस भाव के स्वामी (भावेश) के षड्बल और भाव की केंद्रादि स्थिति पर निर्भर करती है।
            - **४०० विरूपा से अधिक बल वाला भाव:** जीवन के उस आयाम में सहज सफलता, स्थिरता और संतोष प्रदान करता है।
            - **३३० विरूपा से कम बल वाला भाव:** उस क्षेत्र में अत्यधिक परिश्रम के उपरांत भी आंशिक सफलता या अवरोध का संकेत देता है, जिसके लिए विशिष्ट वैदिक उपचार अनुशंसित हैं।
            """)





    # =============================================================
    # TAB 9: JAIMINI & UPAGRAHAS & SPECIAL LAGNAS & AVASTHAS

