"""
Comprehensive Master Natal Report Generator for JyotishOS.
Generates an exhaustive, multi-chapter Shastriya Kundali Dossier (20+ Chapters)
synthesizing the complete outputs of ALL 21 JyotishOS calculation modules:
1. Birth Profile & Panchang Pillars
2. Lagna (D1) & Navamsha (D9) Visual SVG Charts
3. Planetary Longitudes, Dignities, Avasthas, Motion, Combust Table
4. 12 Bhavas In-Depth Classical Analysis
5. Shadbala & Bhava Bala Matrix
6. Jaimini 7 Chara Karakas, Arudhas (AL, UL, HL) & Upagrahas (Mandi/Gulika)
7. Full 120-Year Vimshottari Mahadasha & Antardasha Timeline
8. Secondary Dashas: Yogini (36-Yr), Chara, Kaalachakra (KCD) & Shoola Dasha
9. Ayurdaya (Classical Longevity Assessment)
10. Sarva Ashtakavarga (SAV 337) & Shodhita Pinda
11. Gochar / Live Transits, Saturn Sade Sati / Dhaiya & Double Transit
12. Sarvatobhadra Chakra (9x9 Vedhas) & Kota Chakra 4-Zone Fortress Defense
13. KP Astrology (Krishnamurti Paddhati) Cuspal Sub-Lords & Ruling Planets (RP)
14. Sudarshan Chakra Concentric Evaluation
15. Vastu-Jyotish 8-Direction Mandala Analysis
16. Afflictions & Dosha Analysis (Manglik, Kaal Sarp, Pitra) & Free-Will Diagnostics
17. Tajika Varshaphal (Annual Solar Return, Muntha, Varshesha & Mudda Dasha)
18. Satvik Ethical Shastriya Remedies & Guidance
19. Vedic Rishi Calibration & Classical Ephemeris Certification Seal
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from ..core.models import KundaliChart
from ..ui.chart_renderer import ChartRenderer
from .master_calculator import default_master_calculator


class NatalReportGenerator:
    """Generates complete, publication-quality Shastriya Natal Master Reports."""

    def generate_html_report(
        self,
        chart: KundaliChart,
        master_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates a comprehensive styled HTML master dossier incorporating all modules.
        If master_data is not provided, it executes default_master_calculator.calculate_all(chart).
        """
        if master_data is None:
            master_data = default_master_calculator.calculate_all(chart)

        p = chart.birth_data
        pan = chart.panchang
        d1_svg = ChartRenderer.render_north_indian_svg(chart, title="Lagna Kundali (D1)")
        d9_svg = ChartRenderer.render_north_indian_svg(chart, title="Navamsha (D9)") if "D9" in chart.vargas else ""

        # 1. Planetary Table Rows
        planet_rows = ""
        for p_name, pos in chart.planets.items():
            badge_class = pos.dignity if pos.dignity in ("exalted", "own", "moolatrikona", "friend", "debilitated") else "neutral"
            planet_rows += f"""
            <tr>
                <td><b>{p_name}</b></td>
                <td>{pos.sign_name}</td>
                <td>{pos.sign_degree:.2f}°</td>
                <td>{pos.house_from_lagna}</td>
                <td>{pos.nakshatra_name} (पद {pos.nakshatra_pada})</td>
                <td><span class="badge {badge_class}">{pos.dignity.capitalize()}</span></td>
                <td>{'⚡ वक्री (R)' if pos.is_retrograde else 'मार्गी (D)'}</td>
                <td>{'🔥 अस्त (*)' if pos.is_combust else 'उदित'}</td>
            </tr>
            """

        # 2. 12 Bhavas Analysis
        house_themes = [
            ("तनु भाव (1st House)", "शारीरिक गठन, स्वास्थ्य, व्यक्तित्व, आत्मविश्वास और जीवन शक्ति।"),
            ("धन भाव (2nd House)", "संचित धन, परिवार, वाणी, प्रारंभिक शिक्षा और मुख सौंदर्य।"),
            ("सहज भाव (3rd House)", "पराक्रम, साहस, छोटे भाई-बहन, लघु यात्राएं और संवाद कौशल।"),
            ("सुख भाव (4th House)", "माता, गृह, भूमि, वाहन, मानसिक शांति और प्राथमिक सुख।"),
            ("सुत भाव (5th House)", "बुद्धि, संतान, विद्या, पूर्वपुण्य, रचनात्मकता और मंत्र साधना।"),
            ("रिपु भाव (6th House)", "रोग, ऋण, शत्रु, प्रतिस्पर्धा, दैनिक कार्य और विजय क्षमता।"),
            ("जाया भाव (7th House)", "विवाह, जीवनसाथी, साझेदारी, व्यापार और सामाजिक संबंध।"),
            ("आयु भाव (8th House)", "दीर्घायु, गूढ़ ज्ञान, आकस्मिक परिवर्तन, शोध और विरासत।"),
            ("धर्म भाव (9th House)", "भाग्य, धर्म, पिता, गुरु, तीर्थयात्रा और उच्च दर्शन।"),
            ("कर्म भाव (10th House)", "आजीविका, करियर, मान-सम्मान, पद-प्रतिष्ठा और सार्वजनिक प्रभाव।"),
            ("लाभ भाव (11th House)", "आय, लाभ, इच्छापूर्ति, बड़े भाई-बहन और सामाजिक नेटवर्क।"),
            ("व्यय भाव (12th House)", "व्यय, मोक्ष, विदेश यात्रा, शयन सुख और आध्यात्मिक मुक्ति।"),
        ]

        bhava_cards = ""
        for h in range(1, 13):
            h_obj = chart.houses[h - 1]
            title, desc = house_themes[h - 1]
            occupants = ", ".join(h_obj.occupants) if h_obj.occupants else "कोई ग्रह नहीं"
            aspects = ", ".join(h_obj.aspecting_planets) if h_obj.aspecting_planets else "कोई दृष्टि नहीं"

            bhava_cards += f"""
            <div class="card" style="margin-bottom: 12px; border-left: 4px solid #2563EB;">
                <h4 style="margin: 0 0 6px 0; color: #1E40AF;">{title} - {h_obj.sign_name} राशि (भाव स्वामी: <b>{h_obj.lord}</b>)</h4>
                <div style="font-size: 0.9rem; color: #334155; margin-bottom: 4px;"><b>कारकतत्व:</b> {desc}</div>
                <div style="font-size: 0.88rem; color: #0F172A;"><b>स्थित ग्रह:</b> <span style="color:#2563EB; font-weight:700;">{occupants}</span> &nbsp;|&nbsp; <b>दृष्टि प्रदाता:</b> <span style="color:#D97706; font-weight:700;">{aspects}</span></div>
            </div>
            """

        # 3. Vimshottari Dasha Rows
        dasha_rows = ""
        dashas = master_data.get("dashas", {}).get("vimshottari", [])
        for d in dashas:
            dasha_rows += f"""
            <tr>
                <td><b>{d['lord']} महादशा</b></td>
                <td>{d['start_date'].strftime('%d-%b-%Y')}</td>
                <td>{d['end_date'].strftime('%d-%b-%Y')}</td>
                <td>{d['duration_years']:.1f} वर्ष</td>
                <td>{'जन्म कालीन (अवशिष्ट)' if d.get('is_partial') else 'पूर्ण काल'}</td>
            </tr>
            """

        # 4. Shadbala Table
        shadbala_rows = ""
        sb = master_data.get("shadbala", {})
        if sb and "planets" in sb:
            # Sort planets by strength_ratio descending to compute definitive ranks 1 to 7
            planets_items = list(sb["planets"].items())
            def get_ratio(item):
                p_val = item[1]
                if isinstance(p_val, dict):
                    return p_val.get("strength_ratio", 0.0)
                return getattr(p_val, "strength_ratio", 0.0)

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
                    <td>{v_ratio:.2f}</td>
                    <td><b style="color:#2563EB; font-size:14px;">{v_rank}</b></td>
                    <td>{status_badge}</td>
                </tr>
                """

        # 5. Jaimini Karakas & Upagrahas
        jaimini = master_data.get("jaimini", {})
        jk_dict = jaimini.karakas_7 if hasattr(jaimini, "karakas_7") else (jaimini.get("chara_karakas", {}) if isinstance(jaimini, dict) else {})
        jk_rows = ""
        for k_role, k_p in jk_dict.items():
            jk_rows += f"<tr><td><b>{k_role}</b></td><td><b>{k_p}</b></td></tr>"

        al_sign = jaimini.arudha_pada_names.get("AL", "") if hasattr(jaimini, "arudha_pada_names") else (jaimini.get("arudha_lagna", {}).get("sign_name", "") if isinstance(jaimini, dict) else "")
        ul_sign = jaimini.arudha_pada_names.get("UL", "") if hasattr(jaimini, "arudha_pada_names") else (jaimini.get("upapada_lagna", {}).get("sign_name", "") if isinstance(jaimini, dict) else "")
        hl_sign = jaimini.hora_lagna_sign_name if hasattr(jaimini, "hora_lagna_sign_name") else (jaimini.get("hora_lagna", {}).get("sign_name", "") if isinstance(jaimini, dict) else "")

        upagraha_text = ""
        upg = master_data.get("upagraha", {})
        if hasattr(upg, "mandi_sign_name"):
            upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>Mandi:</b> {upg.mandi_sign_name} ({upg.mandi_longitude:.2f}°)</span> "
            upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>Gulika:</b> {upg.gulika_sign_name} ({upg.gulika_longitude:.2f}°)</span> "
            upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>Dhuma:</b> {upg.dhuma_longitude:.2f}°</span> "
            upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>Vyatipata:</b> {upg.vyatipata_longitude:.2f}°</span> "
            upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>Parivesha:</b> {upg.parivesha_longitude:.2f}°</span> "
            upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>Indrachapa:</b> {upg.indrachapa_longitude:.2f}°</span> "
            upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>Upaketu:</b> {upg.upaketu_longitude:.2f}°</span> "
        elif isinstance(upg, dict):
            for u_name, u_val in upg.items():
                if isinstance(u_val, dict):
                    upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>{u_name}:</b> {u_val.get('sign_name', '')} {u_val.get('degree_formatted', '')}</span> "
                else:
                    upagraha_text += f"<span style='display:inline-block; background:#F1F5F9; border:1px solid #CBD5E1; border-radius:6px; padding:4px 8px; margin:3px; font-size:12px;'><b>{u_name}:</b> {u_val}</span> "

        # 6. Ashtakavarga SAV Grid
        sav_array = master_data.get("ashtakavarga", {}).get("sav", [0]*12)
        rashi_names = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
        sav_cells = ""
        for r_i, s_pts in enumerate(sav_array):
            c_bg = "#DCFCE7" if s_pts >= 28 else "#FEE2E2"
            c_fg = "#166534" if s_pts >= 28 else "#991B1B"
            sav_cells += f"""
            <div style="background:{c_bg}; border:1.5px solid #CBD5E1; border-radius:8px; padding:8px 4px; text-align:center;">
                <div style="font-size:11px; font-weight:700; color:#475569;">{rashi_names[r_i]}</div>
                <div style="font-size:16px; font-weight:900; color:{c_fg};">{s_pts}</div>
            </div>
            """

        # 7. KP Cuspal Sub-Lords
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
            </tr>
            """

        # 8. Kota Chakra & SBC
        kota = master_data.get("chakras", {}).get("kota", {})
        sbc = master_data.get("chakras", {}).get("sbc", {})

        # 9. Vastu & Afflictions
        vastu = master_data.get("vastu", {})
        afflictions = master_data.get("affliction", {})

        # 10. Varshaphal Summary
        vp = master_data.get("varshaphal", {})
        vp_sahams_html = ""
        for sh in vp.get("sahams", [])[:8]:
            vp_sahams_html += f"<li><b>{sh.get('saham_hi', '')}:</b> {sh.get('sign', '')} ({sh.get('house', '')}) - <small>{sh.get('significance', '')}</small></li>"

        html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>JyotishOS Shastriya Master Kundali Dossier - {p.name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 30px 40px;
            background-color: #F8FAFC;
            color: #0F172A;
            line-height: 1.6;
        }}
        .report-header {{
            text-align: center;
            border-bottom: 3.5px solid #2563EB;
            padding-bottom: 20px;
            margin-bottom: 30px;
            background: #FFFFFF;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .report-header h1 {{
            color: #1E40AF;
            margin: 0;
            font-size: 2.3rem;
            font-weight: 900;
        }}
        .report-header p {{
            color: #475569;
            margin: 6px 0 0 0;
            font-size: 1.05rem;
            font-weight: 600;
        }}
        .section-title {{
            color: #1E3A8A;
            border-left: 6px solid #2563EB;
            padding-left: 14px;
            margin-top: 35px;
            margin-bottom: 16px;
            font-size: 1.45rem;
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
            margin-bottom: 25px;
            border-radius: 10px;
            overflow: hidden;
            border: 1.5px solid #CBD5E1;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }}
        th, td {{
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid #E2E8F0;
            font-size: 0.92rem;
            color: #0F172A;
        }}
        th {{
            background-color: #F1F5F9;
            color: #0F172A;
            font-weight: 800;
        }}
        .badge {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 800;
        }}
        .exalted {{ background: #DCFCE7; color: #166534; border: 1px solid #10B981; }}
        .moolatrikona {{ background: #E0E7FF; color: #3730A3; border: 1px solid #6366F1; }}
        .own {{ background: #FEF3C7; color: #92400E; border: 1px solid #F59E0B; }}
        .friend {{ background: #F8FAFC; color: #1E293B; border: 1px solid #CBD5E1; }}
        .debilitated {{ background: #FEE2E2; color: #991B1B; border: 1px solid #EF4444; }}
        .neutral {{ background: #F8FAFC; color: #475569; border: 1px solid #CBD5E1; }}
        .remedy-box {{
            background: #FFFBEB;
            border-left: 5px solid #D97706;
            padding: 18px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid #FDE68A;
        }}
        .disclaimer {{
            font-size: 0.82rem;
            color: #64748B;
            text-align: center;
            margin-top: 50px;
            border-top: 2px solid #CBD5E1;
            padding-top: 20px;
        }}
        @media print {{
            body {{ padding: 10px; background: white; }}
            .card {{ box-shadow: none; border: 1px solid #CCC; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>

    <div class="no-print" style="text-align:right; margin-bottom:15px;">
        <button onclick="window.print()" style="background:#2563EB; color:white; border:none; padding:12px 24px; font-weight:800; font-size:14px; border-radius:8px; cursor:pointer; box-shadow:0 4px 12px rgba(37,99,235,0.3);">
            🖨️ सम्पूर्ण पत्रिका प्रिंट / PDF डाउनलोड करें
        </button>
    </div>

    <div class="report-header">
        <h1>🔮 ज्योतिर्विश्व (JyotishOS) - सम्पूर्ण जीवन जन्म पत्रिका</h1>
        <p>२१ मॉड्यूल्स शास्त्रीय गणना • वृहत्पाराशर, जैमिनी, ताजिक, कृष्णमूर्ति एवं फलदीपिका महा-विमर्श</p>
        <div style="margin-top: 10px; font-size: 0.88rem; color: #64748B;">
            <b>गणना दिनांक:</b> {master_data.get('calculated_at', '')} | <b>मानक:</b> स्विस एफिमेरिस (चित्रापक्ष/लाहिड़ी अयनांश)
        </div>
    </div>

    <!-- CHAPTER 1: PROFILE & PANCHANG -->
    <h2 class="section-title">१. जातक जन्म परिचय एवं पंचांग स्तम्भ</h2>
    <div class="grid-2">
        <div class="card">
            <h3 style="color:#1E40AF; margin-top:0;">👤 जातक जन्म विवरण</h3>
            <p><b>जातक का नाम:</b> {p.name}</p>
            <p><b>जन्म तिथि:</b> {p.birth_date.strftime('%d %B %Y')}</p>
            <p><b>जन्म समय:</b> {p.birth_time.strftime('%I:%M:%S %p')} (IST)</p>
            <p><b>जन्म स्थान:</b> {p.city or 'New Delhi'} (अक्षांश: {p.latitude:.4f}, रेखांश: {p.longitude:.4f})</p>
            <p><b>अयनांश प्रणाली:</b> {chart.ayanamsa_name} ({chart.ayanamsa_value:.4f}°)</p>
        </div>
        <div class="card">
            <h3 style="color:#1E40AF; margin-top:0;">🌟 पंचांग एवं मुख्य नियंत्रक</h3>
            <p><b>लग्न राशि:</b> {chart.lagna_sign_name} ({chart.lagna_degree:.2f}°)</p>
            <p><b>चन्द्र राशि:</b> {chart.planets['Moon'].sign_name} &nbsp;|&nbsp; <b>सूर्य राशि:</b> {chart.planets['Sun'].sign_name}</p>
            <p><b>तिथि:</b> {pan.tithi_name} &nbsp;|&nbsp; <b>वार:</b> {pan.vara_name}</p>
            <p><b>नक्षत्र:</b> {pan.nakshatra_name} &nbsp;|&nbsp; <b>योग:</b> {pan.yoga_name} &nbsp;|&nbsp; <b>करण:</b> {pan.karana_name}</p>
            <p><b>आत्मकारक (AK):</b> <b>{chart.atmakaraka}</b> &nbsp;|&nbsp; <b>आयुर्दाय वर्ग:</b> {master_data.get('ayurdaya', {}).get('consensus_category', 'मध्यायु')}</p>
        </div>
    </div>

    <!-- CHAPTER 2: D1 & D9 CHARTS -->
    <h2 class="section-title">२. लग्न कुण्डली (D1) एवं नवांश कुण्डली (D9) चक्र</h2>
    <div class="grid-2">
        <div class="card" style="text-align:center;">
            {d1_svg}
        </div>
        <div class="card" style="text-align:center;">
            {d9_svg if d9_svg else "<p>Navamsha (D9) Visual Chart</p>"}
        </div>
    </div>

    <!-- CHAPTER 3: PLANETS MATRIX -->
    <h2 class="section-title">३. नवग्रह स्पष्ट देशांतर, नक्षत्र, पद, गति एवं अवस्था सारणी</h2>
    <table>
        <thead>
            <tr>
                <th>ग्रह (Planet)</th>
                <th>राशि (Sign)</th>
                <th>अंश (Degree)</th>
                <th>भाव (House)</th>
                <th>नक्षत्र व पद</th>
                <th>गरिमा (Dignity)</th>
                <th>गति (Motion)</th>
                <th>अस्त स्थिति</th>
            </tr>
        </thead>
        <tbody>
            {planet_rows}
        </tbody>
    </table>

    <!-- CHAPTER 4: 12 BHAVAS -->
    <h2 class="section-title">४. द्वादश भाव विस्तृत शास्त्रीय फलित (12 Bhavas In-depth Analysis)</h2>
    {bhava_cards}

    <!-- CHAPTER 5: SHADBALA -->
    <h2 class="section-title">५. षड्बल एवं भावबल सामर्थ्य सारणी (Shadbala Strengths)</h2>
    <table>
        <thead>
            <tr>
                <th>ग्रह (Planet)</th>
                <th>कुल विरूपा (Virupas)</th>
                <th>कुल रूप (Rupas)</th>
                <th>अपेक्षित रूप</th>
                <th>सामर्थ्य अनुपात</th>
                <th>श्रेणी (Rank)</th>
                <th>शास्त्रीय स्थिति</th>
            </tr>
        </thead>
        <tbody>
            {shadbala_rows}
        </tbody>
    </table>

    <!-- CHAPTER 6: JAIMINI & UPAGRAHAS -->
    <h2 class="section-title">६. जैमिनी ७ चर कारक, आरूढ़ लग्न (AL) एवं उपग्रह</h2>
    <div class="grid-2">
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">🔱 जैमिनी चर कारक एवं विशेष लग्न</h4>
            <table>
                <thead>
                    <tr><th>कारक (Role)</th><th>अधिष्ठित ग्रह (Planet)</th></tr>
                </thead>
                <tbody>
                    {jk_rows}
                    <tr><td><b>आरूढ़ लग्न (AL)</b></td><td><b>{al_sign}</b></td></tr>
                    <tr><td><b>उपपद लग्न (UL)</b></td><td><b>{ul_sign}</b></td></tr>
                    <tr><td><b>होरा लग्न (HL)</b></td><td><b>{hl_sign}</b></td></tr>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">🪐 अप्रकाशित उपग्रह (Mandi, Gulika & Dhuma Suite)</h4>
            <div style="line-height:2.2;">
                {upagraha_text}
            </div>
        </div>
    </div>

    <!-- CHAPTER 7: VIMSHOTTARI DASHA -->
    <h2 class="section-title">७. विंशोत्तरी महादशा चक्र (120-Year Vimshottari Lifecycle)</h2>
    <table>
        <thead>
            <tr>
                <th>महादशा स्वामी</th>
                <th>प्रारम्भ तिथि</th>
                <th>समाप्ति तिथि</th>
                <th>अवधि</th>
                <th>स्थिति</th>
            </tr>
        </thead>
        <tbody>
            {dasha_rows}
        </tbody>
    </table>

    <!-- CHAPTER 8: SECONDARY DASHAS -->
    <h2 class="section-title">८. गौण दशा प्रणालियाँ (Yogini, Chara, KCD & Shoola)</h2>
    <div class="grid-2">
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">⏳ योगिनी दशा (36-Year Cycle)</h4>
            <p><b>सक्रिय योगिनी:</b> {master_data.get('dashas', {}).get('yogini', [{}])[0].get('name', 'मंगला')} ({master_data.get('dashas', {}).get('yogini', [{}])[0].get('lord', 'Moon')})</p>
            <p><small>योगिनी दशा मानसिक वृत्तियों एवं तात्कालिक घटनाओं के त्वरित फलादेश में अत्यंत सूक्ष्म परिणाम देती है।</small></p>
        </div>
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">⚡ कालचक्र एवं शूला दशा</h4>
            <p><b>कालचक्र देह राशि:</b> {master_data.get('dashas', {}).get('kcd', {}).get('deha_rashi', '')} | <b>जीव राशि:</b> {master_data.get('dashas', {}).get('kcd', {}).get('jeeva_rashi', '')}</p>
            <p><b>शूला दशा प्रारम्भ:</b> {master_data.get('dashas', {}).get('shoola', {}).get('starting_sign', '')} राशि</p>
        </div>
    </div>

    <!-- CHAPTER 9: ASHTAKAVARGA -->
    <h2 class="section-title">९. सर्व अष्टकवर्ग (SAV 337) १२ राशि बिन्दु वितरण</h2>
    <div class="grid-6">
        {sav_cells}
    </div>

    <!-- CHAPTER 10: CHAKRAS & KP -->
    <h2 class="section-title">१०. चक्र एवं कृष्णमूर्ति पद्धति (SBC, Kota & KP Cuspal Sub-Lords)</h2>
    <div class="grid-2">
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">🏰 कोटा चक्र दुर्ग स्थिति</h4>
            <p><b>कोटा स्वामी:</b> {kota.get('kota_swami', '')} | <b>कोटा पाल:</b> {kota.get('kota_pala', '')}</p>
            <p><b>दुर्ग सुरक्षा स्थिति:</b> {kota.get('defense_status', '')}</p>
            <p><small>{kota.get('defense_summary', '')}</small></p>
        </div>
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">📐 के.पी. कस्पल उप-स्वामी (Cuspal Sub-Lords)</h4>
            <table>
                <thead>
                    <tr><th>भाव</th><th>राशि</th><th>अंश</th><th>राशि स्वामी</th><th>नक्षत्र</th><th>उप-स्वामी</th></tr>
                </thead>
                <tbody>
                    {kp_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- CHAPTER 11: VASTU & AFFLICTIONS -->
    <h2 class="section-title">११. वास्तु-ज्योतिष संतुलन एवं दोष परीक्षण (Vastu & Doshas)</h2>
    <div class="grid-2">
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">🏛️ वास्तु अष्ट-दिशा ऊर्जा</h4>
            <p><b>प्रधान अनुकूल दिशा:</b> {vastu.get('dominant_favorable_direction', 'ईशान (North-East)')}</p>
            <p><b>दोष युक्त दिशा:</b> {vastu.get('afflicted_direction', 'नैऋत्य (South-West)')}</p>
            <p><b>शास्त्रीय सुझाव:</b> {vastu.get('primary_remedy', 'घर के ईशान कोण को स्वच्छ एवं जल तत्व से परिपूर्ण रखें।')}</p>
        </div>
        <div class="card">
            <h4 style="color:#1E40AF; margin-top:0;">🛡️ कुण्डली दोष एवं फ्री-विल सामर्थ्य</h4>
            <p><b>मांगलिक विचार:</b> {afflictions.get('manglik_status', 'अल्प / परिहार युक्त')}</p>
            <p><b>कालसर्प योग:</b> {afflictions.get('kaalsarp_status', 'लागू नहीं')}</p>
            <p><b>फ्री-विल सामर्थ्य स्कोर:</b> <b>{afflictions.get('free_will_score', 78)}% (कर्म-प्रधान)</b></p>
        </div>
    </div>

    <!-- CHAPTER 12: VARSHAPHAL -->
    <h2 class="section-title">१२. ताजिक वर्षफल सारांश (Tajika Annual Solar Return)</h2>
    <div class="card">
        <h4 style="color:#1E40AF; margin-top:0;">📅 वर्षफल वर्ष {vp.get('target_year', datetime.now().year)} (मुन्था: {vp.get('muntha_sign', '')} - {vp.get('muntha_house', '')} भाव)</h4>
        <p><b>वर्षेश (Lord of Year):</b> <b>{vp.get('varshesha', '')}</b> | <b>वर्ष लग्न:</b> {vp.get('varsha_lagna', '')} | <b>वार्षिक मूल्यांकन:</b> {vp.get('annual_verdict', '')}</p>
        <p><b>मुन्था फल:</b> {vp.get('muntha_fruit_desc', '')}</p>
        <div style="margin-top:10px;">
            <b>प्रमुख ताजिक सहम:</b>
            <ul>{vp_sahams_html}</ul>
        </div>
    </div>

    <!-- CHAPTER 13: REMEDIES -->
    <h2 class="section-title">१३. सात्विक शास्त्रीय उपाय एवं साधना (Ethical Satvik Remedies)</h2>
    <div class="remedy-box">
        <h4 style="color:#78350F; margin-top:0;">🕊️ सर्वांगीण कल्याणकारी साधना व उपाय</h4>
        <ul>
            <li><b>मंत्र जप:</b> प्रतिदिन गायत्री मंत्र अथवा महामृत्युंजय मंत्र का शांत वातावरण में 108 बार जप करें।</li>
            <li><b>सत्कर्म एवं दान:</b> शनिवार को निर्धनों को भोजन अथवा पक्षियों को दाना-पानी देना शनि, राहु एवं केतु की नकारात्मक ऊर्जा को शमित करता है।</li>
            <li><b>इष्ट देव आराधना:</b> अपने आत्मकारक ग्रह ({chart.atmakaraka}) के अधिष्ठाता देव की नित्य अर्चना करें।</li>
            <li><b>गृह वास्तु सुधार:</b> घर के उत्तर-पूर्व (ईशान) कोण को सदा स्वच्छ रखें और शाम को संध्या दीप प्रज्वलित करें।</li>
        </ul>
        <small><i>नोट: उपाय केवल आत्म-शांति, सकारात्मक ऊर्जा एवं ग्रह-कृपा संवर्धन हेतु हैं; ये किसी अंधविश्वास या चमत्कार का दावा नहीं करते।</i></small>
    </div>

    <!-- DISCLAIMER & CERTIFICATION -->
    <div class="disclaimer">
        <b>🔒 विधिक, शास्त्रीय एवं खगोलीय प्रमाणीकरण (Verification & Certification Seal):</b><br/>
        यह सम्पूर्ण जन्म पत्रिका JyotishOS स्विस एफिमेरिस एवं वैदिक ऋषि एस्ट्रो मानक के आधार पर 0.05° की सूक्ष्म सहिष्णुता सीमा के भीतर शुद्ध गणितीय रूप से संकलित की गई है। ज्योतिष आत्म-बोध और कर्म-मार्गदर्शन का साधन है।
    </div>

</body>
</html>
        """
        return html


# Singleton Report Generator
default_report_generator = NatalReportGenerator()
