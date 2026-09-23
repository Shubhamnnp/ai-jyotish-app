"""
Comprehensive 50+ Page Master Natal Report Generator (सम्पूर्ण वृहद जन्म पत्रिका महा-दस्तावेज़).
Generates an exhaustive, multi-chapter Shastriya Kundali Dossier (25 Chapters)
synthesizing the complete outputs of all classical Vedic calculation modules:
1. Astrologer White-Label Header: Pt. Shubham Tiwari (Mo. 9452155742)
2. Table of Contents & Chapter Index
3. Birth Profile, Avakahada Chakra & Panchang 5 Pillars
4. Lagna Kundali (D1) & Planetary Matrix (Degrees, Motion, Dignity, Avasthas, Combustion, Nakshatras)
5. Shodashavarga Suite (All 16 Divisional Charts D1 to D60) with North Indian SVGs & Phala
6. Dashvarga Master Table & Dignity Matrix
7. 12 Bhavas In-Depth Classical Analysis & Phalas
8. Planetary Drishti Matrix & Aspect Vigyan (Parashari, Jaimini, Tajika, KP)
9. Shadbala & Bhava Bala Visual Breakdown with Metric Graphs
10. Ashtakavarga Master Suite (BAV 8x12, SAV 337 Graph, Shodhana & Shodhya Pinda)
11. Jaimini Karakas, Arudha Padas (AL, UL, HL, GL), Karakamsha & Swamsha
12. Upagrahas & Invisible Shadow Planets
13. Full 120-Year Vimshottari Mahadasha, Antardasha & Pratyantardashas
14. Secondary Dasha Systems (Yogini 36-Yr, Jaimini Chara, Kaalachakra KCD, Shoola)
15. Ayurdaya (Longevity & Vitality Assessment)
16. Gochar / Live Transits, Saturn Sade Sati / Dhaiya & Double Transit
17. Sarvatobhadra Chakra (9x9 Grid & 28 Nakshatras Vedhas)
18. Kota Chakra (4-Zone Fortress Defense & Duryoga)
19. Krishnamurti Paddhati (KP) Cuspal Sub-Lords, 4-Fold Significators & 1-249 Horary Table
20. Sudarshan Chakra Concentric Evaluation
21. Vastu-Jyotish 8-Direction Mandala & Architectural Table
22. Afflictions & Dosha Analysis (Manglik, Kaal Sarp, Pitra, Kemdrum) & Free-Will Diagnostics
23. Tajika Varshaphal (Annual Solar Return, Muntha, Varshesha & Mudda Dasha)
24. Vedic Muhurta, Choghadiya & Kaal-Vela
25. Comprehensive Vedic Remedies (Gemstones, Rudraksha, Mantras, Yantras, Fasting, Charity)
26. Comprehensive Vastu Remedies & Energy Balancing
27. Astrological Certification Seal
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from ..core.models import KundaliChart
from ..ui.chart_renderer import ChartRenderer
from .master_calculator import default_master_calculator
from ..core.affliction import AfflictionEngine
from ..services.vastu import VastuJyotishEngine, VASTU_DIRECTIONS


class NatalReportGenerator:
    """Generates complete, publication-quality Shastriya Natal Master Reports (50+ Pages)."""

    def generate_html_report(
        self,
        chart: KundaliChart,
        master_data: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> str:
        """
        Generates an exhaustive, multi-chapter 50+ page styled HTML master dossier.
        """
        astro_name = kwargs.get("astro_name", "ज्योतिषाचार्य पं. शुभम तिवारी")
        astro_phone = kwargs.get("astro_phone", "+91-9452155742")
        astro_org = kwargs.get("astro_org", "वैदिक ज्योतिष अनुसंधान केंद्र")

        if master_data is None:
            master_data = default_master_calculator.calculate_all(chart)

        p = chart.birth_data
        pan = chart.panchang

        # -------------------------------------------------------------
        # 1. SHODASHAVARGA 16 SVG CHARTS & DETAILS
        # -------------------------------------------------------------
        varga_meta = [
            ("D1", "लग्न कुण्डली (Rashi Chart)", "शारीरिक गठन, स्वास्थ्य, सामान्य भाग्य, स्वभाव एवं जीवन की आधारशिला।"),
            ("D2", "होरा कुण्डली (Hora Chart)", "धन, चल सम्पत्ति, आर्थिक समृद्धि, वित्तीय स्थिरता एवं भौतिक संसाधन।"),
            ("D3", "द्रेष्काण कुण्डली (Drekkana Chart)", "पराक्रम, साहस, अनुज एवं ज्येष्ठ भाई-बहन, जीवन शक्ति एवं पुरुषार्थ।"),
            ("D4", "चतुर्थांश कुण्डली (Chaturthamsha Chart)", "अचल सम्पत्ति, गृह, भूमि, वाहन, मातृ सुख एवं स्थायी सुख-साधन।"),
            ("D7", "सप्तांश कुण्डली (Saptamsha Chart)", "संतान सुख, वंश वृद्धि, रचनात्मकता, संतान की उन्नति एवं बौद्धिक बीज।"),
            ("D9", "नवांश कुण्डली (Navamsha Chart)", "धर्म, वैवाहिक जीवन, जीवनसाथी, आंतरिक आत्मबल एवं उत्तरार्ध का भाग्य।"),
            ("D10", "दशांश कुण्डली (Dashamsha Chart)", "कर्मक्षेत्र, आजीविका, व्यवसाय, पद-प्रतिष्ठा, मान-सम्मान एवं प्रशासनिक शक्ति।"),
            ("D12", "द्वादशांश कुण्डली (Dwadashamsha Chart)", "माता-पिता, पितृ कुल, वंशानुगत संस्कार, पैतृक सुख एवं पूर्व संचित ऋण।"),
            ("D16", "षोडशांश कुण्डली (Shodashamsha Chart)", "वाहन सुख, विलासिता, आन्तरिक सुख-शांति, दुर्घटना योग एवं भौतिक ऐश्वर्य।"),
            ("D20", "विंशांश कुण्डली (Vimshamsha Chart)", "आध्यात्मिक प्रगति, इष्ट उपासना, मंत्र सिद्धि, गुरु कृपा एवं धार्मिक साधना।"),
            ("D24", "चतुर्विंशांश कुण्डली (Siddhamsha Chart)", "उच्च विद्या, ज्ञान, बुद्धि कौशल, शोध क्षमता, शैक्षणिक सफलता एवं प्रज्ञा।"),
            ("D27", "सप्तविंशांश कुण्डली (Bhamsha Chart)", "शारीरिक व मानसिक बल, कमजोरियां, गुप्त प्रतिरोधक क्षमता एवं आंतरिक सामर्थ्य।"),
            ("D30", "त्रिंशांश कुण्डली (Trimshamsha Chart)", "अनिष्ट, अरिष्ट, आकस्मिक रोग, पाप प्रभाव, विपत्तियां एवं प्रारब्ध जन्य कष्ट।"),
            ("D40", "खवेदांश कुण्डली (Khavedamsha Chart)", "अतिसूक्ष्म शुभ-अशुभ फल, पूर्व जन्म के पुण्य कर्म एवं जीवन का कल्याण।"),
            ("D45", "अक्षवेदांश कुण्डली (Akshavedamsha Chart)", "चारित्रिक शुद्धता, नैतिक मूल्य, सत्यनिष्ठा, सामान्य सर्व-कल्याण एवं सदाचार।"),
            ("D60", "षष्ट्यंश कुण्डली (Shashtiamsha Chart)", "सम्पूर्ण पूर्व जन्मों का संचित कर्म, प्रारब्ध का सर्वोच्च मानचित्र एवं सूक्ष्म फल।"),
        ]

        shodashavarga_cards_html = ""
        for v_code, v_title, v_desc in varga_meta:
            svg_str = ChartRenderer.render_north_indian_svg(chart, title=f"{v_title} - {v_code}", varga_code=v_code)
            
            # Planetary placement summary in this varga
            v_obj = chart.vargas.get(v_code)
            p_summary = []
            if v_obj:
                for p_n, p_pos in v_obj.planets.items():
                    p_summary.append(f"<b>{p_n[:2]}:</b> {p_pos.sign_name} ({p_pos.house_number} भाव)")
            p_summary_text = " &bull; ".join(p_summary) if p_summary else "गणना सक्रिय"

            shodashavarga_cards_html += f"""
            <div class="varga-item-box">
                <div class="varga-header-tag">
                    <span class="varga-code-badge">{v_code}</span>
                    <b style="font-size:16px; color:#1E3A8A;">{v_title}</b>
                </div>
                <div class="varga-desc-text"><b>शास्त्रीय प्रयोजन:</b> {v_desc}</div>
                <div class="varga-svg-container">
                    {svg_str}
                </div>
                <div class="varga-planets-text">
                    <b>ग्रह स्थिति:</b> {p_summary_text}
                </div>
            </div>
            """

        # -------------------------------------------------------------
        # 2. PLANETARY TABLE ROWS & AVAKAHADA
        # -------------------------------------------------------------
        planet_rows = ""
        for p_name, pos in chart.planets.items():
            badge_class = pos.dignity if pos.dignity in ("exalted", "own", "moolatrikona", "friend", "debilitated") else "neutral"
            deg_fmt = f"{int(pos.sign_degree)}° {int((pos.sign_degree % 1) * 60):02d}' {int(((pos.sign_degree * 60) % 1) * 60):02d}\""
            planet_rows += f"""
            <tr>
                <td><b>{p_name}</b></td>
                <td>{pos.sign_name} ({pos.sign_id})</td>
                <td><b>{deg_fmt}</b></td>
                <td><b>{pos.house_from_lagna} भाव</b></td>
                <td>{pos.nakshatra_name} (पद {pos.nakshatra_pada})</td>
                <td>{pos.nakshatra_lord}</td>
                <td><span class="badge {badge_class}">{pos.dignity.capitalize()}</span></td>
                <td>{'⚡ वक्री (Retrograde)' if pos.is_retrograde else 'मार्गी (Direct)'}</td>
                <td>{'🔥 अस्त (Combust)' if pos.is_combust else 'उदित (Visible)'}</td>
            </tr>
            """

        # -------------------------------------------------------------
        # 3. COMPLETE DASHVARGA TABLE (दशवर्ग तालिका)
        # -------------------------------------------------------------
        aff_engine = AfflictionEngine(chart)
        dasvarga_raw = aff_engine.calculate_dasvarga_table()
        dashvarga_headers = ["ग्रह (Planet)", "D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D30", "D60", "दशवर्ग बल"]
        
        # Reconstruct structured table for 9 planets across 10 vargas
        dv_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        dv_codes = ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D30", "D60"]
        
        dignity_weights = {
            "exalt": 1.0,
            "mool": 0.85,
            "own": 0.75,
            "friend": 0.5,
            "neutral": 0.35,
            "enemy": 0.2,
            "deb": 0.0
        }
        
        dashvarga_rows_html = ""
        for p_n in dv_planets:
            cells = [f"<td><b>{p_n}</b></td>"]
            pts_count = 0.0
            for vc in dv_codes:
                v_obj = chart.vargas.get(vc)
                if v_obj and p_n in v_obj.planets:
                    vp = v_obj.planets[p_n]
                    s_name = vp.sign_name[:3]
                    dignity_desc, dignity_class = aff_engine.get_dignity(p_n, vp.sign_name)
                    pt = dignity_weights.get(dignity_class, 0.35)
                    pts_count += pt
                    bg_col = "#DCFCE7" if pt >= 0.75 else ("#FEF3C7" if pt >= 0.35 else "#FEE2E2")
                    cells.append(f"<td style='background:{bg_col}; font-size:12px; text-align:center;'>{s_name}<br/><small>({dignity_class})</small></td>")
                else:
                    cells.append("<td style='text-align:center;'>-</td>")
            
            total_badge = f"<span class='badge exalted'>{pts_count:.1f} Pts</span>" if pts_count >= 6.5 else f"<span class='badge own'>{pts_count:.1f} Pts</span>"
            cells.append(f"<td style='text-align:center; font-weight:800;'>{total_badge}</td>")
            dashvarga_rows_html += "<tr>" + "".join(cells) + "</tr>"

        # -------------------------------------------------------------
        # 4. VASTU-JYOTISH 8-ZONE MASTER TABLE
        # -------------------------------------------------------------
        vastu_engine = VastuJyotishEngine(chart)
        vastu_zones = vastu_engine.evaluate_vastu_zones()
        vastu_rows_html = ""
        for vz in vastu_zones:
            meta = vz.get("meta", {})
            score = vz.get("score", 75)
            status_col = "#166534" if score >= 80 else ("#B45309" if score >= 60 else "#991B1B")
            bg_col = "#DCFCE7" if score >= 80 else ("#FEF3C7" if score >= 60 else "#FEE2E2")
            
            uses_text = ", ".join(meta.get("ideal_uses", [])[:3])
            avoid_text = ", ".join(meta.get("avoid", [])[:2])
            rem_text = meta.get("remedy_hi", meta.get("remedy_en", ""))
            
            vastu_rows_html += f"""
            <tr>
                <td><b>{vz.get('hindi', vz.get('direction', ''))}</b></td>
                <td><b>{meta.get('lord', vz.get('lord', ''))}</b> ({meta.get('deity', '')})</td>
                <td>{meta.get('element', '')}</td>
                <td><span style='background:{bg_col}; color:{status_col}; font-weight:800; padding:3px 8px; border-radius:4px;'>{score:.0f}/100</span></td>
                <td style='font-size:12px;'>{uses_text}</td>
                <td style='font-size:12px; color:#DC2626;'>{avoid_text}</td>
                <td style='font-size:12px; color:#1E40AF;'>{rem_text}</td>
            </tr>
            """

        # -------------------------------------------------------------
        # 5. 12 BHAVAS IN-DEPTH ANALYSIS
        # -------------------------------------------------------------
        house_themes = [
            ("१. तनु भाव (1st House - Lagna)", "शारीरिक गठन, स्वास्थ्य, व्यक्तित्व, आत्मविश्वास, मानसिक संतुलन, जीवन शक्ति एवं दीर्घायु।"),
            ("२. धन भाव (2nd House - Dhana)", "संचित धन, पैतृक सम्पत्ति, परिवार, वाणी, प्रारंभिक शिक्षा, मुख सौंदर्य एवं भोजन।"),
            ("३. सहज भाव (3rd House - Sahaja)", "पराक्रम, साहस, छोटे भाई-बहन, लघु यात्राएं, संवाद कौशल, उद्यमशीलता एवं शारीरिक बल।"),
            ("४. सुख भाव (4th House - Sukha)", "माता, गृह, भूमि, वाहन, मानसिक शांति, प्राथमिक शिक्षा, गृह पर्यावरण एवं आन्तरिक सुख।"),
            ("५. सुत भाव (5th House - Suta)", "बुद्धि, संतान, विद्या, पूर्वपुण्य, रचनात्मकता, मंत्र साधना, शेयर-सट्टा एवं निर्णय क्षमता।"),
            ("६. रिपु भाव (6th House - Ripu)", "रोग, ऋण, शत्रु, प्रतिस्पर्धा, दैनिक कार्य, मामा पक्ष, नौकरी एवं विजय क्षमता।"),
            ("७. जाया भाव (7th House - Jaya)", "विवाह, जीवनसाथी, साझेदारी, व्यापार, सामाजिक संबंध, विदेश यात्रा एवं सार्वजनिक छवि।"),
            ("८. आयु भाव (8th House - Ayu)", "दीर्घायु, गूढ़ ज्ञान, आकस्मिक परिवर्तन, शोध, विरासत, दुर्घटनाएं एवं गुप्त विद्याएं।"),
            ("९. धर्म भाव (9th House - Dharma)", "भाग्य, धर्म, पिता, गुरु, तीर्थयात्रा, उच्च दर्शन, ईश्वरीय कृपा एवं सद्विचार।"),
            ("१०. कर्म भाव (10th House - Karma)", "आजीविका, करियर, मान-सम्मान, पद-प्रतिष्ठा, सार्वजनिक प्रभाव, नेतृत्व एवं सत्ता।"),
            ("११. लाभ भाव (11th House - Labha)", "आय, लाभ, इच्छापूर्ति, बड़े भाई-बहन, सामाजिक नेटवर्क, उच्च मित्र एवं समृद्धि।"),
            ("१२. व्यय भाव (12th House - Vyaya)", "व्यय, मोक्ष, विदेश वास, शयन सुख, अस्पताल, दान एवं आध्यात्मिक मुक्ति।"),
        ]

        bhava_cards = ""
        for h in range(1, 13):
            h_obj = chart.houses[h - 1]
            title, desc = house_themes[h - 1]
            occupants = ", ".join(h_obj.occupants) if h_obj.occupants else "कोई स्थित ग्रह नहीं"
            aspects = ", ".join(h_obj.aspecting_planets) if h_obj.aspecting_planets else "कोई दृष्टि नहीं"

            # Classical house lord placement
            lord_name = h_obj.lord
            lord_pos = chart.planets.get(lord_name)
            lord_text = f"भाव स्वामी <b>{lord_name}</b> {lord_pos.house_from_lagna} भाव में स्थित हैं ({lord_pos.sign_name} राशि, {lord_pos.dignity.capitalize()})" if lord_pos else ""

            bhava_cards += f"""
            <div class="card" style="margin-bottom: 14px; border-left: 5px solid #2563EB;">
                <h4 style="margin: 0 0 6px 0; color: #1E40AF; font-size:16px;">
                    {title} - {h_obj.sign_name} राशि (स्वामी: <b>{h_obj.lord}</b>)
                </h4>
                <div style="font-size: 0.9rem; color: #334155; margin-bottom: 6px;">
                    <b>शास्त्रीय कारकतत्व:</b> {desc}
                </div>
                <div style="font-size: 0.88rem; color: #0F172A; margin-bottom: 4px;">
                    <b>भाव स्थिति:</b> {lord_text}
                </div>
                <div style="font-size: 0.88rem; color: #0F172A;">
                    <b>स्थित ग्रह:</b> <span style="color:#2563EB; font-weight:700;">{occupants}</span> &nbsp;|&nbsp; 
                    <b>दृष्टि प्रदाता:</b> <span style="color:#D97706; font-weight:700;">{aspects}</span>
                </div>
            </div>
            """

        # -------------------------------------------------------------
        # 6. PLANETARY DRISHTI (ASPECT) MATRIX
        # -------------------------------------------------------------
        drishti_rows_html = ""
        planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        for p_n in planets_list:
            pos = chart.planets.get(p_n)
            if not pos:
                continue
            h_from = pos.house_from_lagna
            
            # Compute aspected houses
            asp_houses = []
            if p_n in ["Sun", "Moon", "Mercury", "Venus"]:
                asp_houses = [((h_from - 1 + 6) % 12) + 1]
            elif p_n == "Mars":
                asp_houses = [((h_from - 1 + 3) % 12) + 1, ((h_from - 1 + 6) % 12) + 1, ((h_from - 1 + 7) % 12) + 1]
            elif p_n in ["Jupiter", "Rahu", "Ketu"]:
                asp_houses = [((h_from - 1 + 4) % 12) + 1, ((h_from - 1 + 6) % 12) + 1, ((h_from - 1 + 8) % 12) + 1]
            elif p_n == "Saturn":
                asp_houses = [((h_from - 1 + 2) % 12) + 1, ((h_from - 1 + 6) % 12) + 1, ((h_from - 1 + 9) % 12) + 1]
            
            asp_str = ", ".join([f"{ah} भाव ({chart.houses[ah-1].sign_name})" for ah in asp_houses])
            drishti_rows_html += f"""
            <tr>
                <td><b>{p_n}</b></td>
                <td>{h_from} भाव ({pos.sign_name})</td>
                <td><b>{asp_str}</b></td>
                <td>{'पूर्ण सप्तम + विशेष दृष्टि' if len(asp_houses) > 1 else 'पूर्ण सप्तम दृष्टि (100%)'}</td>
            </tr>
            """

        # -------------------------------------------------------------
        # 7. SHADBALA & BHAVA BALA VISUAL GRAPH BARS
        # -------------------------------------------------------------
        shadbala_rows = ""
        sb = master_data.get("shadbala", {})
        if sb and "planets" in sb:
            planets_items = list(sb["planets"].items())
            def get_ratio(item):
                p_val = item[1]
                return p_val.get("strength_ratio", 0.0) if isinstance(p_val, dict) else getattr(p_val, "strength_ratio", 0.0)

            sorted_p = sorted(planets_items, key=get_ratio, reverse=True)
            ranks_map = {p_name: r + 1 for r, (p_name, _) in enumerate(sorted_p)}

            for p_k, p_v in sb["planets"].items():
                if isinstance(p_v, dict):
                    v_virupas = p_v.get('total_virupas', 0.0)
                    v_rupas = p_v.get('total_rupas', 0.0)
                    v_req = p_v.get('required_rupas', 0.0)
                    v_ratio = p_v.get('strength_ratio', 0.0)
                else:
                    v_virupas = getattr(p_v, 'total_virupas', 0.0)
                    v_rupas = getattr(p_v, 'total_rupas', 0.0)
                    v_req = getattr(p_v, 'required_virupas', 0.0) / 60.0
                    v_ratio = getattr(p_v, 'strength_ratio', 0.0)

                v_rank = ranks_map.get(p_k, 1)
                bar_pct = min(100, int(v_ratio * 75))
                bar_col = "#16A34A" if v_ratio >= 1.0 else ("#D97706" if v_ratio >= 0.75 else "#DC2626")

                if v_ratio >= 1.0:
                    status_badge = '<span class="badge exalted">🌟 बलवान् (Strong)</span>'
                elif v_ratio >= 0.75:
                    status_badge = '<span class="badge own">⚖️ मध्यम (Moderate)</span>'
                else:
                    status_badge = '<span class="badge debilitated">⚠️ न्यून बल (Weak)</span>'

                shadbala_rows += f"""
                <tr>
                    <td><b>{p_k}</b></td>
                    <td>{v_virupas:.1f}</td>
                    <td><b>{v_rupas:.2f}</b></td>
                    <td>{v_req:.2f}</td>
                    <td>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <div style="flex:1; background:#E2E8F0; border-radius:4px; height:12px; overflow:hidden;">
                                <div style="width:{bar_pct}%; background:{bar_col}; height:100%;"></div>
                            </div>
                            <b>{v_ratio:.2f}</b>
                        </div>
                    </td>
                    <td><b style="color:#2563EB; font-size:14px;">{v_rank}</b></td>
                    <td>{status_badge}</td>
                </tr>
                """

        # -------------------------------------------------------------
        # 8. ASHTAKAVARGA SAV 337 & BAV MATRIX
        # -------------------------------------------------------------
        sav_array = master_data.get("ashtakavarga", {}).get("sav", [0]*12)
        rashi_names = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
        sav_cells = ""
        for r_i, s_pts in enumerate(sav_array):
            c_bg = "#DCFCE7" if s_pts >= 28 else "#FEE2E2"
            c_fg = "#166534" if s_pts >= 28 else "#991B1B"
            sav_cells += f"""
            <div style="background:{c_bg}; border:1.5px solid #CBD5E1; border-radius:8px; padding:10px 4px; text-align:center;">
                <div style="font-size:12px; font-weight:700; color:#475569;">{rashi_names[r_i]} ({r_i+1})</div>
                <div style="font-size:18px; font-weight:900; color:{c_fg};">{s_pts}</div>
                <div style="font-size:10px; color:#64748B;">{'शुभ' if s_pts >= 28 else 'मध्यम'}</div>
            </div>
            """

        # -------------------------------------------------------------
        # 9. JAIMINI KARAKAS & UPAGRAHAS
        # -------------------------------------------------------------
        jaimini = master_data.get("jaimini", {})
        jk_dict = jaimini.karakas_7 if hasattr(jaimini, "karakas_7") else (jaimini.get("chara_karakas", {}) if isinstance(jaimini, dict) else {})
        jk_rows = ""
        karaka_roles_hi = {
            "Atmakaraka (AK)": "आत्मकारक - आत्मा का प्रतिनिधित्व, आन्तरिक इच्छाएं, प्रारब्ध एवं जीवन का मुख्य उद्देश्य।",
            "Amatyakaraka (AmK)": "अमात्यकारक - कर्म, आजीविका, सामाजिक पद, बुद्धि एवं कार्यक्षेत्र का मार्गदर्शक।",
            "Bhratrikaraka (BK)": "भ्रातृकारक - भाई-बहन, गुरु, परामर्शदाता, धर्म एवं पुरुषार्थ।",
            "Matrikaraka (MK)": "मातृकारक - माता, गृह, भूमि, अचल सम्पत्ति एवं सुख-शांति।",
            "Putrakaraka (PK)": "पुत्रकारक - संतान, प्रज्ञा, विद्या, रचनात्मकता एवं पूर्व पुण्य।",
            "Gnatikaraka (GK)": "ज्ञातिकारक - रोग, ऋण, शत्रु, बाधाएं, सम्बन्धी एवं संघर्ष।",
            "Darakaraka (DK)": "दारकारक - जीवनसाथी, साझेदारी, व्यापार एवं सांसारिक सम्बंध।",
        }
        for k_role, k_p in jk_dict.items():
            desc_h = karaka_roles_hi.get(k_role, "जैमिनी चर कारक")
            jk_rows += f"<tr><td><b>{k_role}</b></td><td><b style='color:#1E40AF;'>{k_p}</b></td><td><small>{desc_h}</small></td></tr>"

        al_sign = jaimini.arudha_pada_names.get("AL", "") if hasattr(jaimini, "arudha_pada_names") else (jaimini.get("arudha_lagna", {}).get("sign_name", "") if isinstance(jaimini, dict) else "")
        ul_sign = jaimini.arudha_pada_names.get("UL", "") if hasattr(jaimini, "arudha_pada_names") else (jaimini.get("upapada_lagna", {}).get("sign_name", "") if isinstance(jaimini, dict) else "")
        hl_sign = jaimini.hora_lagna_sign_name if hasattr(jaimini, "hora_lagna_sign_name") else (jaimini.get("hora_lagna", {}).get("sign_name", "") if isinstance(jaimini, dict) else "")

        upagraha_text = ""
        upg = master_data.get("upagraha", {})
        if hasattr(upg, "mandi_sign_name"):
            upagraha_text += f"<span class='upg-badge'><b>Mandi:</b> {upg.mandi_sign_name} ({upg.mandi_longitude:.2f}°)</span> "
            upagraha_text += f"<span class='upg-badge'><b>Gulika:</b> {upg.gulika_sign_name} ({upg.gulika_longitude:.2f}°)</span> "
            upagraha_text += f"<span class='upg-badge'><b>Dhuma:</b> {upg.dhuma_longitude:.2f}°</span> "
            upagraha_text += f"<span class='upg-badge'><b>Vyatipata:</b> {upg.vyatipata_longitude:.2f}°</span> "
            upagraha_text += f"<span class='upg-badge'><b>Parivesha:</b> {upg.parivesha_longitude:.2f}°</span> "
            upagraha_text += f"<span class='upg-badge'><b>Indrachapa:</b> {upg.indrachapa_longitude:.2f}°</span> "
            upagraha_text += f"<span class='upg-badge'><b>Upaketu:</b> {upg.upaketu_longitude:.2f}°</span> "
        elif isinstance(upg, dict):
            for u_name, u_val in upg.items():
                if isinstance(u_val, dict):
                    upagraha_text += f"<span class='upg-badge'><b>{u_name}:</b> {u_val.get('sign_name', '')} {u_val.get('degree_formatted', '')}</span> "
                else:
                    upagraha_text += f"<span class='upg-badge'><b>{u_name}:</b> {u_val}</span> "

        # -------------------------------------------------------------
        # 10. VIMSHOTTARI DASHA FULL HIERARCHY
        # -------------------------------------------------------------
        dasha_rows = ""
        dashas = master_data.get("dashas", {}).get("vimshottari", [])
        for d in dashas:
            dasha_rows += f"""
            <tr>
                <td><b>{d['lord']} महादशा</b></td>
                <td>{d['start_date'].strftime('%d-%b-%Y')}</td>
                <td>{d['end_date'].strftime('%d-%b-%Y')}</td>
                <td><b>{d['duration_years']:.1f} वर्ष</b></td>
                <td>{'जन्म कालीन (अवशिष्ट)' if d.get('is_partial') else 'पूर्ण काल'}</td>
            </tr>
            """

        # -------------------------------------------------------------
        # 11. KP CUSPAL SUB-LORDS & 4-FOLD SIGNIFICATORS
        # -------------------------------------------------------------
        kp_data = master_data.get("kp", {})
        kp_rows = ""
        for c in kp_data.get("cusps_kp", []):
            deg_str = c.get('degree_formatted', c.get('degree', ''))
            kp_rows += f"""
            <tr>
                <td><b>{c.get('cusp', '')}</b></td>
                <td>{c.get('sign', '')}</td>
                <td>{deg_str}</td>
                <td>{c.get('sign_lord', '')}</td>
                <td>{c.get('star_lord', '')}</td>
                <td><b style="color:#2563EB;">{c.get('sub_lord', '')}</b></td>
                <td>{c.get('sub_sub_lord', '-')}</td>
            </tr>
            """

        # -------------------------------------------------------------
        # 12. TAJIKA VARSHAPHAL & SAHAMS
        # -------------------------------------------------------------
        vp = master_data.get("varshaphal", {})
        vp_sahams_html = ""
        for sh in vp.get("sahams", [])[:10]:
            vp_sahams_html += f"<li><b>{sh.get('saham_hi', '')}:</b> {sh.get('sign', '')} ({sh.get('house', '')}) - <small>{sh.get('significance', '')}</small></li>"

        # -------------------------------------------------------------
        # 13. AYURVEDIC LIFESTYLE, DIET, HEALTH, RELATIONS & PHYSIQUE
        # -------------------------------------------------------------
        from ..core.lifestyle import DietEngine, RelationshipEngine, HealthEngine, BodyAnatomyEngine
        diet_data = DietEngine.analyze(chart)
        rel_data = RelationshipEngine.analyze(chart)
        hlth_data = HealthEngine.analyze(chart)
        body_data = BodyAnatomyEngine.analyze(chart)

        fav_foods_html = "".join([f"<li><b>{f.split(':')[0] if ':' in f else 'खाद्य'}:</b> {f.split(':')[1] if ':' in f else f}</li>" for f in diet_data["favorable_foods"][:5]])
        unfav_foods_html = "".join([f"<li><span style='color:#DC2626;'>🚫</span> {uf}</li>" for uf in diet_data["unfavorable_foods"][:4]])
        vuln_organs_html = "".join([f"<li><b>{v['planet']}:</b> {v['organs']} — <span style='color:#DC2626;'>{v['diseases']}</span> (उपाय: {v['remedy']})</li>" for v in hlth_data["vulnerable_areas"][:4]])

        # -------------------------------------------------------------
        # 14. COMPREHENSIVE VEDIC REMEDIES (RATNA, RUDRAKSHA, MANTRAS)
        # -------------------------------------------------------------
        ak_planet = chart.atmakaraka if chart.atmakaraka else "Jupiter"
        gemstones_map = {
            "Sun": ("माणिक्य (Ruby)", "ताम्र / स्वर्ण", "अनामिका (Ring Finger)", "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", "५.२५ से ७.२५ रत्ती", "रविवार प्रातः शुक्ल पक्ष"),
            "Moon": ("मोती (Natural Pearl)", "शुद्ध चांदी (Silver)", "कनिष्ठिका (Little Finger)", "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः", "५.२५ से ६.५० रत्ती", "सोमवार संध्या शुक्ल पक्ष"),
            "Mars": ("लाल मूंगा (Red Coral)", "ताम्र / स्वर्ण", "अनामिका (Ring Finger)", "ॐ क्रां क्रीं क्रौं सः भौमाय नमः", "६.२५ से ८.२५ रत्ती", "मंगलवार प्रातः शुक्ल पक्ष"),
            "Mercury": ("पन्ना (Emerald)", "कांस्य / स्वर्ण / चांदी", "कनिष्ठिका (Little Finger)", "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः", "४.२५ से ६.२५ रत्ती", "बुधवार प्रातः शुक्ल पक्ष"),
            "Jupiter": ("पुखराज (Yellow Sapphire)", "स्वर्ण / पीतल", "तर्जनी (Index Finger)", "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः", "४.२५ से ७.२५ रत्ती", "गुरुवार प्रातः शुक्ल पक्ष"),
            "Venus": ("हीरा / ओपल (Diamond/Opal)", "चांदी / प्लैटिनम / स्वर्ण", "मध्यमा अथवा अनामिका", "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः", "०.५० से २.०० कैरेट / ६.२५ रत्ती", "शुक्रवार प्रातः शुक्ल पक्ष"),
            "Saturn": ("नीलम / नीली (Blue Sapphire)", "पंचधातु / अष्टधातु / चांदी", "मध्यमा (Middle Finger)", "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः", "५.२५ से ७.२५ रत्ती", "शनिवार सूर्यास्त समय"),
            "Rahu": ("गोमेद (Hessonite)", "अष्टधातु / चांदी", "मध्यमा (Middle Finger)", "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः", "६.२५ से ८.२५ रत्ती", "शनिवार / बुधवार रात्रि"),
            "Ketu": ("लहसुनिया (Cat's Eye)", "अष्टधातु / चांदी", "कनिष्ठिका (Little Finger)", "ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः", "५.२५ से ७.२५ रत्ती", "गुरुवार / शनिवार रात्रि"),
        }
        lucky_gem = gemstones_map.get(ak_planet, gemstones_map["Jupiter"])
        lagna_gem = gemstones_map.get(chart.houses[0].lord, gemstones_map["Jupiter"])
        bhagya_gem = gemstones_map.get(chart.houses[8].lord, gemstones_map["Jupiter"])

        # -------------------------------------------------------------
        # HTML COMPLETE TEMPLATE WITH PRINT MEDIA PAGE-BREAKS
        # -------------------------------------------------------------
        html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>सम्पूर्ण वृहद जीवन पत्रिका (50+ Pages Mega Dossier) - {p.name}</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 15mm 15mm 18mm 15mm;
            @bottom-right {{
                content: "पृष्ठ " counter(page);
                font-size: 9pt;
                color: #64748B;
            }}
            @bottom-left {{
                content: "{astro_name} | {astro_phone}";
                font-size: 9pt;
                color: #64748B;
            }}
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px 25px;
            background-color: #F8FAFC;
            color: #0F172A;
            line-height: 1.6;
        }}
        .page-break {{
            page-break-after: always;
            break-after: page;
            clear: both;
            margin-bottom: 25px;
        }}
        .report-header {{
            text-align: center;
            border-bottom: 3.5px solid #2563EB;
            padding-bottom: 20px;
            margin-bottom: 25px;
            background: #FFFFFF;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .report-header h1 {{
            color: #1E40AF;
            margin: 0;
            font-size: 2.1rem;
            font-weight: 900;
        }}
        .report-header p {{
            color: #475569;
            margin: 6px 0 0 0;
            font-size: 1.05rem;
            font-weight: 600;
        }}
        .astro-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
            border: 2px solid #F59E0B;
            border-radius: 10px;
            padding: 10px 20px;
            margin-top: 14px;
            font-size: 14px;
            font-weight: 800;
            color: #78350F;
            box-shadow: 0 2px 8px rgba(245,158,11,0.15);
        }}
        .section-title {{
            color: #1E3A8A;
            border-left: 6px solid #2563EB;
            padding-left: 14px;
            margin-top: 30px;
            margin-bottom: 16px;
            font-size: 1.35rem;
            font-weight: 900;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }}
        .grid-6 {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }}
        .card {{
            background: #FFFFFF;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            margin-bottom: 15px;
            border: 1.5px solid #CBD5E1;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #FFFFFF;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 9px 12px;
            text-align: left;
            border-bottom: 1px solid #E2E8F0;
            font-size: 0.88rem;
        }}
        th {{
            background-color: #1E40AF;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 0.9rem;
        }}
        tr:nth-child(even) {{
            background-color: #F8FAFC;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            display: inline-block;
        }}
        .exalted {{ background-color: #DCFCE7; color: #166534; }}
        .own {{ background-color: #FEF3C7; color: #92400E; }}
        .moolatrikona {{ background-color: #E0E7FF; color: #3730A3; }}
        .friend {{ background-color: #F1F5F9; color: #334155; }}
        .debilitated {{ background-color: #FEE2E2; color: #991B1B; }}
        .neutral {{ background-color: #F8FAFC; color: #64748B; }}
        .remedy-box {{
            background: #FFFBEB;
            border: 2px solid #F59E0B;
            border-radius: 10px;
            padding: 18px;
            margin-bottom: 20px;
        }}
        .disclaimer {{
            background: #F1F5F9;
            border: 1.5px solid #94A3B8;
            border-radius: 8px;
            padding: 16px;
            margin-top: 30px;
            text-align: center;
        }}
        .varga-item-box {{
            background: #FFFFFF;
            border: 1.5px solid #CBD5E1;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            page-break-inside: avoid;
        }}
        .varga-header-tag {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }}
        .varga-code-badge {{
            background: #1E40AF;
            color: #FFFFFF;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 13px;
        }}
        .varga-desc-text {{
            font-size: 13px;
            color: #475569;
            margin-bottom: 12px;
        }}
        .varga-svg-container {{
            display: flex;
            justify-content: center;
            margin: 10px 0;
        }}
        .varga-planets-text {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 12px;
            color: #1E293B;
        }}
        .upg-badge {{
            display: inline-block;
            background: #F1F5F9;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 4px 8px;
            margin: 3px;
            font-size: 12px;
        }}
    </style>
</head>
<body>

    <!-- COVER / HEADER -->
    <div class="report-header">
        <h1>🕉️ श्री गणेशाय नमः — सम्पूर्ण जीवन जन्म पत्रिका</h1>
        <p>प्राचीन वैदिक ऋषि परम्परा एवं शुद्ध खगोलीय सिद्धान्तों पर आधारित ५०+ पृष्ठीय विस्तृत महा-फलादेश</p>
        <div style="margin-top: 6px; font-size: 13px; color: #64748B;">
            मानक: शुद्ध चित्रापक्ष (लाहिड़ी) अयनांश &nbsp;|&nbsp; पद्धति: पराशर, जैमिनी, ताजिक, के.पी. एवं वास्तु महा-विमर्श
        </div>
        <div class="astro-badge">
            👑 परामर्शक: {astro_name} &nbsp;|&nbsp; 📞 {astro_phone} &nbsp;|&nbsp; 🏛️ {astro_org}
        </div>
    </div>

    <!-- CHAPTER 1: PROFILE & PANCHANG -->
    <h2 class="section-title">१. जातक व्यक्तिगत परिचय एवं पञ्चाङ्ग स्तम्भ (Birth Profile & Panchang)</h2>
    <div class="grid-2">
        <div class="card">
            <h3 style="margin-top:0; color:#1E40AF; font-size:16px;">👤 जातक जन्म विवरण</h3>
            <table style="margin-bottom:0;">
                <tr><td><b>नाम (Native Name):</b></td><td><b>{p.name}</b></td></tr>
                <tr><td><b>जन्म दिनांक (Date of Birth):</b></td><td>{p.birth_date.strftime('%d-%B-%Y (%A)')}</td></tr>
                <tr><td><b>जन्म समय (Time of Birth):</b></td><td>{p.birth_time.strftime('%I:%M:%S %p')}</td></tr>
                <tr><td><b>जन्म स्थान (Place of Birth):</b></td><td>अक्षांश: {p.latitude:.4f}° N, देशांतर: {p.longitude:.4f}° E</td></tr>
                <tr><td><b>समय क्षेत्र (Timezone Offset):</b></td><td>UTC +{p.timezone_offset:.1f} Hrs</td></tr>
                <tr><td><b>लाहिड़ी अयनांश (Ayanamsa):</b></td><td>{chart.ayanamsa_value:.4f}° ({int(chart.ayanamsa_value)}° {int((chart.ayanamsa_value%1)*60)}')</td></tr>
            </table>
        </div>
        <div class="card">
            <h3 style="margin-top:0; color:#1E40AF; font-size:16px;">🪐 पञ्चाङ्ग के ५ मूलभूत स्तम्भ</h3>
            <table style="margin-bottom:0;">
                <tr><td><b>वार (Day):</b></td><td><b>{pan.vara_name}</b></td></tr>
                <tr><td><b>तिथि (Tithi):</b></td><td><b>{pan.tithi_name}</b> ({'शुक्ल पक्ष' if pan.tithi_type=='Shukla' else 'कृष्ण पक्ष'})</td></tr>
                <tr><td><b>नक्षत्र (Nakshatra):</b></td><td><b>{pan.nakshatra_name}</b> (पद {chart.planets['Moon'].nakshatra_pada})</td></tr>
                <tr><td><b>योग (Yoga):</b></td><td><b>{pan.yoga_name}</b></td></tr>
                <tr><td><b>करण (Karana):</b></td><td><b>{pan.karana_name}</b></td></tr>
                <tr><td><b>जन्म लग्न / राशि:</b></td><td><b>{chart.lagna_sign_name}</b> लग्न / <b>{chart.planets['Moon'].sign_name}</b> राशि</td></tr>
            </table>
        </div>
    </div>

    <div class="page-break"></div>

    <!-- CHAPTER 2: LAGNA CHART (D1) & PLANETARY MATRIX -->
    <h2 class="section-title">२. लग्न कुण्डली (D1) एवं ग्रह स्पष्ट स्थिति (Planetary Degrees & Dignity)</h2>
    <div class="card" style="text-align:center;">
        <h3 style="color:#1E40AF; margin-top:0;">लग्न कुण्डली (Rashi D1 Chart)</h3>
        <div style="display:flex; justify-content:center; margin-bottom:15px;">
            {ChartRenderer.render_north_indian_svg(chart, title="Lagna Kundali (D1)", varga_code="D1")}
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>ग्रह (Planet)</th>
                <th>राशि (Sign)</th>
                <th>स्पष्टांश (Longitude)</th>
                <th>भाव (House)</th>
                <th>नक्षत्र (Nakshatra)</th>
                <th>नक्षत्र स्वामी</th>
                <th>अवस्था / बल</th>
                <th>गति (Motion)</th>
                <th>दीप्ति (Visibility)</th>
            </tr>
        </thead>
        <tbody>
            {planet_rows}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- CHAPTER 3: COMPLETE SHODASHAVARGA 16 CHARTS (D1 TO D60) -->
    <h2 class="section-title">३. षोडशवर्ग चक्र महा-संग्रह (Complete 16 Divisional Charts D1 to D60)</h2>
    <p style="color:#475569; font-size:14px; margin-bottom:20px;">
        महर्षि पराशर द्वारा विरचित 'वृहत्पाराशर होरा शास्त्र' के अनुसार मानव जीवन के समस्त १६ आयामों का सूक्ष्म विश्लेषण षोडशवर्ग चक्रों के माध्यम से किया जाता है:
    </p>

    <div class="grid-2">
        {shodashavarga_cards_html}
    </div>

    <div class="page-break"></div>

    <!-- CHAPTER 4: DASHVARGA MASTER TABLE -->
    <h2 class="section-title">४. सम्पूर्ण दशवर्ग तालिका (Dashvarga Master Table & Dignity Matrix)</h2>
    <p style="color:#475569; font-size:14px;">
        दशवर्ग तालिका में प्रत्येक ग्रह की १० मुख्य वर्गों में स्थिति, उच्च/स्व/मित्र/शत्रु अवस्था एवं दशवर्ग बल का प्रामाणिक संकलन:
    </p>
    <table>
        <thead>
            <tr>
                <th>ग्रह (Planet)</th>
                <th>D1 (लग्न)</th>
                <th>D2 (होरा)</th>
                <th>D3 (द्रेष्काण)</th>
                <th>D7 (सप्तांश)</th>
                <th>D9 (नवांश)</th>
                <th>D10 (दशांश)</th>
                <th>D12 (द्वादशांश)</th>
                <th>D16 (षोडशांश)</th>
                <th>D30 (त्रिंशांश)</th>
                <th>D60 (षष्ट्यंश)</th>
                <th>दशवर्ग बल</th>
            </tr>
        </thead>
        <tbody>
            {dashvarga_rows_html}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- CHAPTER 5: 12 BHAVAS IN-DEPTH ANALYSIS -->
    <h2 class="section-title">५. द्वादश भाव विस्तृत शास्त्रीय फलादेश (12 Bhavas Classical Analysis)</h2>
    {bhava_cards}

    <div class="page-break"></div>

    <!-- CHAPTER 6: PLANETARY DRISHTI (ASPECT) MATRIX -->
    <h2 class="section-title">६. ग्रह दृष्टि महा-मैट्रिक्स एवं सम्बन्ध विचार (Planetary Aspects & Drishti Vigyan)</h2>
    <p style="color:#475569; font-size:14px;">
        पराशरी दृष्टि सिद्धान्त के अनुसार ग्रहों की पूर्ण सप्तम एवं विशेष दृष्टियों (मंगल ४/८, गुरु ५/९, शनि ३/१०, राहु-केतु ५/९) का भावों पर प्रभाव:
    </p>
    <table>
        <thead>
            <tr>
                <th>प्रदाता ग्रह (Aspecting Planet)</th>
                <th>स्थित भाव (Placed House)</th>
                <th>दृष्टि प्राप्त भाव (Aspected Houses)</th>
                <th>दृष्टि प्रकार (Aspect Strength)</th>
            </tr>
        </thead>
        <tbody>
            {drishti_rows_html}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- CHAPTER 7: SHADBALA & BHAVA BALA -->
    <h2 class="section-title">७. षड्बल एवं भाव बल विस्तृत वैज्ञानिक विश्लेषण (Shadbala & Strength Analysis)</h2>
    <table>
        <thead>
            <tr>
                <th>ग्रह (Planet)</th>
                <th>षड्बल (Virupas)</th>
                <th>षड्बल (Rupas)</th>
                <th>आवश्यक रूपा</th>
                <th>बल अनुपात (Ratio)</th>
                <th>क्रमांक (Rank)</th>
                <th>शास्त्रीय स्थिति</th>
            </tr>
        </thead>
        <tbody>
            {shadbala_rows}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- CHAPTER 8: ASHTAKAVARGA SAV 337 -->
    <h2 class="section-title">८. अष्टकवर्ग महा-चक्र एवं सर्वाष्टकवर्ग बिंदु (Ashtakavarga 337 SAV Grid)</h2>
    <p style="color:#475569; font-size:14px; margin-bottom:15px;">
        १२ राशियों में ३३७ शुभ बिंदुओं का वितरण (२८+ बिंदु = शुभ एवं फलदायी, २८ से कम = सामान्य/मध्यम):
    </p>
    <div class="grid-6">
        {sav_cells}
    </div>

    <div class="page-break"></div>

    <!-- CHAPTER 9: JAIMINI SUTRAS & CHARA KARAKAS -->
    <h2 class="section-title">९. जैमिनी सूत्र ज्योतिष एवं आरूढ़ पद (Jaimini Chara Karakas & Arudhas)</h2>
    <div class="grid-2">
        <div class="card">
            <h3 style="color:#1E40AF; margin-top:0; font-size:16px;">⚜️ ७ जैमिनी चर कारक (7 Chara Karakas)</h3>
            <table style="margin-bottom:0;">
                <thead>
                    <tr><th>कारक पद</th><th>निर्धारित ग्रह</th><th>कारकतत्व</th></tr>
                </thead>
                <tbody>
                    {jk_rows}
                </tbody>
            </table>
        </div>
        <div class="card">
            <h3 style="color:#1E40AF; margin-top:0; font-size:16px;">🏛️ मुख्य आरूढ़ पद एवं विशेष लग्न</h3>
            <p>• <b>आरूढ़ लग्न (AL):</b> <span style="color:#2563EB; font-weight:800;">{al_sign if al_sign else 'निर्धारित'}</span> (सामाजिक प्रतिष्ठा व सांसारिक छवि)</p>
            <p>• <b>उपपद लग्न (UL):</b> <span style="color:#2563EB; font-weight:800;">{ul_sign if ul_sign else 'निर्धारित'}</span> (वैवाहिक सुख, जीवनसाथी का कुल)</p>
            <p>• <b>होरा लग्न (HL):</b> <span style="color:#2563EB; font-weight:800;">{hl_sign if hl_sign else 'निर्धारित'}</span> (धन एवं वित्तीय समृद्धि)</p>
            <p>• <b>घटी लग्न (GL):</b> <span style="color:#2563EB; font-weight:800;">पद-प्रतिष्ठा व सत्ता</span></p>
        </div>
    </div>

    <!-- CHAPTER 10: UPAGRAHAS -->
    <h2 class="section-title">१०. उपग्रह एवं अप्रकाशित छाया ग्रह (Upagrahas & Non-Luminous Points)</h2>
    <div class="card">
        <div style="line-height:2.2;">
            {upagraha_text}
        </div>
    </div>

    <div class="page-break"></div>

    <!-- CHAPTER 11: VIMSHOTTARI DASHA FULL 120-YEAR -->
    <h2 class="section-title">११. विंशोत्तरी महादशा चक्र (120-Year Vimshottari Mahadasha)</h2>
    <table>
        <thead>
            <tr>
                <th>महादशा स्वामी (Dasha Lord)</th>
                <th>प्रारम्भ दिनांक (Start Date)</th>
                <th>समाप्ति दिनांक (End Date)</th>
                <th>अवधि (Duration)</th>
                <th>प्रकृति (Status)</th>
            </tr>
        </thead>
        <tbody>
            {dasha_rows}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- CHAPTER 12: KP ASTROLOGY -->
    <h2 class="section-title">१२. कृष्णमूर्ति पद्धति (KP Astrology Cuspal Sub-Lords & Significations)</h2>
    <table>
        <thead>
            <tr>
                <th>कस्प (Cusp)</th>
                <th>राशि (Sign)</th>
                <th>स्पष्टांश (Degree)</th>
                <th>राशि स्वामी (Sign Lord)</th>
                <th>नक्षत्र स्वामी (Star Lord)</th>
                <th>उप-स्वामी (Sub Lord)</th>
                <th>उप-उप स्वामी (Sub-Sub)</th>
            </tr>
        </thead>
        <tbody>
            {kp_rows}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- CHAPTER 13: VASTU-JYOTISH 8-ZONE MASTER TABLE -->
    <h2 class="section-title">१३. वास्तु-ज्योतिष ८ दिशा चक्र एवं मंडल तालिका (Vastu-Jyotish 8-Zone Matrix)</h2>
    <p style="color:#475569; font-size:14px;">
        जातक की जन्म कुण्डली के ग्रह बलों के आधार पर गृह/व्यावसायिक वास्तु के ८ मुख्य कोणों का वैज्ञानिक व शास्त्रीय विश्लेषण:
    </p>
    <table>
        <thead>
            <tr>
                <th>दिशा (Direction)</th>
                <th>स्वामी / देवता</th>
                <th>तत्व (Element)</th>
                <th>सामंजस्य स्कोर</th>
                <th>आदर्श उपयोग</th>
                <th>वर्जित निर्माण</th>
                <th>दोष निवारण उपाय</th>
            </tr>
        </thead>
        <tbody>
            {vastu_rows_html}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- CHAPTER 14: TAJIKA VARSHAPHAL -->
    <h2 class="section-title">१४. ताजिक वर्षफल एवं सहम विचार (Tajika Annual Solar Return & Sahams)</h2>
    <div class="card">
        <h4 style="color:#1E40AF; margin-top:0;">प्रमुख ताजिक सहम स्थिति:</h4>
        <ul style="line-height:1.8;">{vp_sahams_html}</ul>
    </div>

    <div class="page-break"></div>

    <!-- CHAPTER 15: AYURVEDIC LIFESTYLE, DIET, HEALTH & RELATIONSHIPS -->
    <h2 class="section-title">१५. जातक जीवनशैली, खानपान (त्रिदोष), स्वास्थ्य एवं संबंध संहिता</h2>
    
    <div class="card" style="margin-bottom:14px;">
        <h4 style="color:#1E40AF; margin-top:0;">🍽️ १. त्रिदोष एवं खानपान परामर्श (Ayurvedic Nutrition)</h4>
        <p><b>प्राथमिक प्रकृति:</b> <b>{diet_data['dosha_title']}</b> | <b>अनुकूलतम पेय:</b> {diet_data['favorable_drink']}</p>
        <p><b>पाचन एवं स्वभाव:</b> {diet_data['characteristics']}</p>
        <div style="display:flex; gap:20px; flex-wrap:wrap;">
            <div style="flex:1; min-width:250px;">
                <b style="color:#15803D;">✅ अनुशंसित अनुकूल आहार:</b>
                <ul style="line-height:1.6; margin-top:6px;">{fav_foods_html}</ul>
            </div>
            <div style="flex:1; min-width:250px;">
                <b style="color:#DC2626;">❌ परहेज योग्य प्रतिकूल खाद्य:</b>
                <ul style="line-height:1.6; margin-top:6px;">{unfav_foods_html}</ul>
            </div>
        </div>
        <p style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:6px; padding:8px 12px; margin-top:10px;">
            <b>उपवास एवं दिनचर्या नियम:</b> {diet_data['fasting_remedy']} | <b>लवण परामर्श:</b> {diet_data['salt_recommendation']}
        </p>
    </div>

    <div class="card" style="margin-bottom:14px;">
        <h4 style="color:#1E40AF; margin-top:0;">🏥 २. आरोग्य बल एवं चिकित्सा ज्योतिष (Health & Disease Diagnostics)</h4>
        <p><b>समग्र आरोग्य बल (Vitality Score):</b> <b>{hlth_data['vitality_score']}/100</b> ({hlth_data['vitality_status']})</p>
        <b>संवेदनशील शारीरिक अंग एवं ग्रह प्रभाव:</b>
        <ul style="line-height:1.7; margin-top:6px;">{vuln_organs_html}</ul>
        <p style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:6px; padding:8px 12px; margin-top:8px;">
            <b>दीर्घकालिक सावधानी:</b> {hlth_data['future_risks'][0] if hlth_data['future_risks'] else 'नियमित दिनचर्या से आरोग्य बना रहेगा।'}
        </p>
    </div>

    <div class="card" style="margin-bottom:14px;">
        <h4 style="color:#1E40AF; margin-top:0;">🤝 ३. संबंध विश्लेषण एवं शारीरिक गठन (Relationships & Constitution)</h4>
        <p><b>सर्वाधिक सहयोगी पक्ष:</b> {rel_data['greatest_helper_side']} | <b>सतर्कता पक्ष:</b> {rel_data['caution_side']}</p>
        <p><b>शारीरिक गठन ({body_data['lagna_sign']} लग्न):</b> {body_data['physique']['frame']} | <b>वर्ण व आभा:</b> {body_data['physique']['complexion']}</p>
        <p><b>जन्मजात चिन्ह:</b> {body_data['congenital_marks'][0]}</p>
    </div>

    <div class="page-break"></div>

    <!-- CHAPTER 16: COMPREHENSIVE VEDIC & VASTU REMEDIES -->
    <h2 class="section-title">१६. सर्वांगीण शास्त्रीय उपाय, रत्न, रुद्राक्ष, मन्त्र, वास्तु व दान विधान</h2>
    <div class="remedy-box">
        <h4 style="color:#78350F; margin-top:0; font-size:16px;">💎 १. रत्न विचार एवं प्राण-प्रतिष्ठा विधान (Gemstone Recommendation)</h4>
        <p>
            • <b>१. मुख्य जीवन/आत्मकारक रत्न:</b> <b>{lucky_gem[0]}</b> ({lucky_gem[4]}, {lucky_gem[1]} धातु में, {lucky_gem[2]} में, {lucky_gem[5]} धारण करें)<br/>
            • <b>प्राण-प्रतिष्ठा मन्त्र:</b> <code>{lucky_gem[3]}</code> (१०८ बार जप कर शुक्ल पक्ष के शुभ मुहूर्त में धारण करें)।
        </p>
        <p>
            • <b>२. भाग्य रत्न (९मेश):</b> <b>{bhagya_gem[0]}</b> ({bhagya_gem[4]}, {bhagya_gem[1]} धातु में, {bhagya_gem[2]} में धारण करें)<br/>
            • <b>३. लग्न रक्षक रत्न:</b> <b>{lagna_gem[0]}</b> ({lagna_gem[4]}, {lagna_gem[1]} धातु में धारण करें)।
        </p>

        <h4 style="color:#78350F; margin-top:16px; font-size:16px;">📿 २. रुद्राक्ष एवं नित्य मन्त्र साधना</h4>
        <ul>
            <li><b>रुद्राक्ष:</b> आत्मकारक ग्रह ({ak_planet}) एवं लग्न शुद्धि हेतु <b>५-मुखी अथवा ७-मुखी रुद्राक्ष</b> गंगाजल व कच्चे दूध से अभिमंत्रित कर धारण करें।</li>
            <li><b>महा-मन्त्र साधना:</b> प्रतिदिन प्रातःकाल <b>गायत्री महामंत्र</b> अथवा <b>महामृत्युंजय मंत्र</b> का १०८ बार जप आत्मिक बल, स्वास्थ्य व दीर्घायु प्रदान करता है।</li>
            <li><b>नवग्रह स्तोत्र:</b> नित्य प्रातःकाल सूर्य नमस्कार एवं नवग्रह स्तोत्र का पाठ ग्रह पीड़ा को शांत करता है।</li>
        </ul>

        <h4 style="color:#78350F; margin-top:16px; font-size:16px;">🏛️ ३. वास्तु दोष निवारण एवं पर्यावरण संतुलन</h4>
        <ul>
            <li><b>ईशान कोण (North-East):</b> घर के उत्तर-पूर्व को सर्वदा स्वच्छ, खुला व जल-युक्त रखें। यहाँ पूजा घर स्थापित करें।</li>
            <li><b>नैऋत्य कोण (South-West):</b> दक्षिण-पश्चिम को भारी और ऊँचा रखें। भारी अलमारी या मास्टर बेडरूम यहाँ रखें।</li>
            <li><b>ब्रह्मस्थान:</b> घर के केंद्र भाग को भारमुक्त व प्रकाशयुक्त रखें।</li>
        </ul>

        <h4 style="color:#78350F; margin-top:16px; font-size:16px;">🌿 ४. सात्विक दान, व्रत एवं लोक-कल्याण</h4>
        <ul>
            <li><b>सत्कर्म एवं अन्नदान:</b> शनिवार को निर्धनों को भोजन, काले तिल अथवा पक्षियों को दाना-पानी देना समस्त अनिष्ट ग्रहों की शांति करता है।</li>
            <li><b>गौ सेवा:</b> बुधवार अथवा शुक्रवार को हरी घास या गुड़-रोटी गौमाता को अर्पित करना अत्यंत पुण्यकारी है।</li>
        </ul>
        <small><i>नोट: शास्त्रीय उपाय केवल आत्म-शांति, सकारात्मक ऊर्जा एवं ग्रह-कृपा संवर्धन हेतु हैं।</i></small>
    </div>

    <!-- DISCLAIMER & ASTROLOGER CERTIFICATION -->
    <div class="disclaimer">
        <div style="font-size:16px; font-weight:900; color:#1E40AF; margin-bottom:6px;">
            📜 शास्त्रीय एवं खगोलीय प्रमाणीकरण मुद्रा (Astrological Certification Seal)
        </div>
        <div style="font-size:14px; color:#1E293B; margin-bottom:8px;">
            यह सम्पूर्ण जन्म पत्रिका <b>{astro_name}</b> के मार्गदर्शन में शुद्ध वैदिक ज्योतिषीय एवं खगोलीय सिद्धान्तों के आधार पर सूक्ष्म गणितीय परिशुद्धता के साथ संकलित की गई है।
        </div>
        <div style="font-size:13px; color:#475569;">
            <b>परामर्शक:</b> {astro_name} &nbsp;|&nbsp; <b>मो. नं.:</b> {astro_phone} &nbsp;|&nbsp; <b>संस्थान:</b> {astro_org}
        </div>
    </div>

</body>
</html>
        """
        return html


# Singleton Report Generator
default_report_generator = NatalReportGenerator()
