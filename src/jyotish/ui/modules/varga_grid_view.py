import streamlit as st
import pandas as pd
from typing import Dict, Any
import importlib
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.core.constants import SIGN_LORDS, SIGN_NAMES
import src.jyotish.core.affliction as aff_mod

def render_dignity_legend_bar() -> str:
    """Renders the standard dignity badge legend bar."""
    return """
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;">
        <span style="background-color: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 11.5px;">🌟 Exaltation (उच्च)</span>
        <span style="background-color: #ccfbf1; color: #0f766e; border: 1px solid #5eead4; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 11.5px;">👑 Mooltrikon (मूलत्रिकोण)</span>
        <span style="background-color: #dcfce7; color: #166534; border: 1px solid #86efac; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 11.5px;">🏠 Own Sign (स्वराशि)</span>
        <span style="background-color: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 11.5px;">🤝 Friend (मित्र)</span>
        <span style="background-color: #f8fafc; color: #475569; border: 1px solid #e2e8f0; font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 11.5px;">⚖️ Neutral (सम)</span>
        <span style="background-color: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 11.5px;">⚔️ Enemy (शत्रु)</span>
        <span style="background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 11.5px;">🔻 Debilitation (नीच)</span>
    </div>
    """


def _clean_html(s: str) -> str:
    """Helper to remove leading/trailing whitespace and prevent markdown 4-space code block glitch."""
    return "".join(line.strip() for line in s.splitlines() if line.strip())


def render_varga_dignity_dashboard(summary: Dict[str, Any], total_vargas: int = 11, is_dark: bool = False, title: str = "") -> str:
    """Renders an executive horizontal stacked dignity distribution and Vaisheshikamsa dashboard for 7 planets."""
    w_svg = 700
    h_svg = 265
    pad_left = 135
    pad_right = 135
    top_y = 12
    row_h = 35
    bar_h = 18

    bar_max_w = w_svg - pad_left - pad_right

    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_muted = "#94A3B8" if is_dark else "#64748B"

    items_svg = []
    planets = [
        ("Sun", "☀️ सूर्य (Sun)", "#F59E0B"),
        ("Moon", "🌙 चन्द्र (Moon)", "#38BDF8"),
        ("Mars", "⚔️ मंगल (Mars)", "#EF4444"),
        ("Mercury", "☿️ बुध (Mercury)", "#10B981"),
        ("Jupiter", "🪐 गुरु (Jupiter)", "#FBBF24"),
        ("Venus", "💎 शुक्र (Venus)", "#EC4899"),
        ("Saturn", "⚖️ शनि (Saturn)", "#6366F1")
    ]

    for idx, (p_key, p_lbl, p_col) in enumerate(planets):
        p_data = summary.get(p_key, {})
        counts = p_data.get("counts", {})
        score = p_data.get("score_20", 0.0)
        vais_hi = p_data.get("vaisheshikamsa_hi", "सामान्य")
        is_varg = p_data.get("is_vargottama", False)
        good_cnt = p_data.get("auspicious_count", 0)

        y = top_y + idx * row_h
        # Planet Label
        varg_badge = " [वर्गोत्तम]" if is_varg else ""
        items_svg.append(f'<text x="{pad_left - 10}" y="{y + bar_h - 4}" font-size="11" font-weight="bold" fill="{p_col}" font-family="sans-serif" text-anchor="end">{p_lbl}{varg_badge}</text>')

        # Background track
        items_svg.append(f'<rect x="{pad_left}" y="{y}" width="{bar_max_w}" height="{bar_h}" fill="rgba(148, 163, 184, 0.12)" rx="3" ry="3"/>')

        # Stacked Bar segments
        order = [
            ("exalt", "#3B82F6"),
            ("mool", "#0D9488"),
            ("own", "#10B981"),
            ("friend", "#84CC16"),
            ("neutral", "#94A3B8"),
            ("enemy", "#F97316"),
            ("deb", "#EF4444")
        ]
        cur_x = pad_left
        for cat, col in order:
            cnt = counts.get(cat, 0)
            if cnt > 0:
                seg_w = (cnt / total_vargas) * bar_max_w
                items_svg.append(f'<rect x="{cur_x:.1f}" y="{y}" width="{seg_w:.1f}" height="{bar_h}" fill="{col}" rx="2" ry="2"/>')
                if seg_w >= 14:
                    items_svg.append(f'<text x="{cur_x + seg_w/2:.1f}" y="{y + bar_h - 5}" font-size="9.5" font-weight="bold" fill="#FFFFFF" font-family="sans-serif" text-anchor="middle">{cnt}</text>')
                cur_x += seg_w

        # Right Score & Vaisheshikamsa Badge
        score_col = "#10B981" if score >= 14 else ("#F59E0B" if score >= 10 else "#EF4444")
        items_svg.append(f'<text x="{w_svg - pad_right + 8}" y="{y + bar_h - 4}" font-size="11" font-weight="800" fill="{score_col}" font-family="sans-serif">{score:.1f}/20</text>')
        items_svg.append(f'<text x="{w_svg - 10}" y="{y + bar_h - 4}" font-size="10.5" font-weight="bold" fill="#D97706" font-family="sans-serif" text-anchor="end">👑 {vais_hi} ({good_cnt})</text>')

    svg_str = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_svg} {h_svg}" style="width:100%; height:auto; display:block;">
      {"".join(items_svg)}
    </svg>'''

    title_html = f'''
    <div style="font-size:13px; font-weight:800; color:{text_primary}; margin-bottom:4px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
      <span>📊 {title or "वर्ग गरिमा एवं वैशेषिकांश वितरण (Varga Dignity Distribution)"}</span>
      <span style="font-size:10px; background:rgba(37,99,235,0.12); color:#2563EB; padding:2px 8px; border-radius:4px; font-weight:700;">विंशोपक अंक व वैशेषिकांश संज्ञा</span>
    </div>
    ''' if title else ''

    return f'''
    <div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:12px; padding:14px 16px; box-shadow:0 4px 14px rgba(0,0,0,0.06); margin-bottom:14px;">
      {title_html}
      {svg_str}
    </div>
    '''


def render_styled_varga_table_html(varga_table_data, varga_meta_dict, is_dark: bool = False) -> str:
    """Renders the executive HTML table with color-coded dignity badges for each planet across divisional charts."""
    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
    hdr_bg = "#1F2937" if is_dark else "#F1F5F9"
    hdr_bdr = "#374151" if is_dark else "#CBD5E1"
    text_primary = "#F8FAFC" if is_dark else "#1E293B"
    row_alt_bg = "#1F2937" if is_dark else "#FCFCFD"
    row_bg = "#111827" if is_dark else "#FFFFFF"
    row_bdr = "#374151" if is_dark else "#F1F5F9"

    planet_cols = [
        ("Sun", "☀️ सूर्य (Sun)"),
        ("Moon", "🌙 चन्द्र (Moon)"),
        ("Mars", "⚔️ मंगल (Mars)"),
        ("Mercury", "☿️ बुध (Mercury)"),
        ("Jupiter", "🪐 गुरु (Jupiter)"),
        ("Venus", "💎 शुक्र (Venus)"),
        ("Saturn", "⚖️ शनि (Saturn)")
    ]

    def format_dignity_cell(val):
        text = ""
        css = ""
        if isinstance(val, dict):
            text = val.get("text", "")
            css = val.get("className", "")
        else:
            text = str(val)
            if "Exalt" in text: css = "exalt"
            elif "Mool" in text: css = "mool"
            elif "Own" in text: css = "own"
            elif "Deb" in text: css = "deb"
            elif "Friend" in text: css = "friend"
            elif "Enemy" in text: css = "enemy"
            elif "Neutral" in text: css = "neutral"

        base_style = "padding: 6px 8px; font-size: 11.5px; border-radius: 5px; text-align: center; white-space: nowrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;"
        if css == "exalt":
            base_style += "background-color: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; font-weight: 700;"
        elif css == "mool":
            base_style += "background-color: #ccfbf1; color: #0f766e; border: 1px solid #5eead4; font-weight: 700;"
        elif css == "own":
            base_style += "background-color: #dcfce7; color: #166534; border: 1px solid #86efac; font-weight: 700;"
        elif css == "deb":
            base_style += "background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; font-weight: 700;"
        elif css == "friend":
            base_style += "background-color: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; font-weight: 500;"
        elif css == "enemy":
            base_style += "background-color: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; font-weight: 500;"
        else:
            base_style += ("background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; font-weight: 500;" if is_dark 
                           else "background-color: #f8fafc; color: #475569; border: 1px solid #e2e8f0; font-weight: 500;")

        return f'<div style="{base_style}">{text}</div>'

    tbl_html = f'<div style="overflow-x: auto; border: 1.5px solid {card_bdr}; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px;">'
    tbl_html += f'<table style="width: 100%; border-collapse: collapse; text-align: left; background: {card_bg};">'
    tbl_html += f'<thead><tr style="background: {hdr_bg}; border-bottom: 2px solid {hdr_bdr};">'
    tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary}; font-size: 12.5px;">वर्ग (Varga)</th>'
    for _, p_hdr in planet_cols:
        tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary}; font-size: 12px; text-align: center;">{p_hdr}</th>'
    tbl_html += '</tr></thead><tbody>'

    for idx, row in enumerate(varga_table_data):
        v_code = row.get("Planets", "")
        v_label = varga_meta_dict.get(v_code, v_code)
        bg_row = row_alt_bg if idx % 2 == 1 else row_bg
        tbl_html += f'<tr style="background-color: {bg_row}; border-bottom: 1px solid {row_bdr};">'
        tbl_html += f'<td style="padding: 8px 12px; font-weight: 700; color: {text_primary}; font-size: 12px; white-space: nowrap;">{v_label}</td>'
        for p_key, _ in planet_cols:
            val = row.get(p_key, "")
            formatted_cell = format_dignity_cell(val)
            tbl_html += f'<td style="padding: 6px 8px; text-align: center;">{formatted_cell}</td>'
        tbl_html += '</tr>'

    tbl_html += '</tbody></table></div>'
    return tbl_html



def render_varga_grid_view(chart, tabs=None):
    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark

    if tabs is None:
        tabs = [
            '📊 दशवर्ग (D1-D10)',
            '🏛️ षोडशवर्ग (D1-D60)',
            '📜 वर्ग सारांश व प्रमाण'
        ]

    import src.jyotish.core.affliction as aff_mod
    affliction_engine = aff_mod.AfflictionEngine(chart)
    _is_dark = is_astrallis_mode or is_night_mode

    # Master metadata for all 16 divisional charts
    varga_meta_full = {
        "D1": "D1 (लग्न/राशि - Core Physical & Mental Self)",
        "D2": "D2 (होरा - धन, संपदा व कुटुम्ब संपत्ति)",
        "D3": "D3 (द्रेष्काण - पराक्रम, भ्राता व साहस)",
        "D4": "D4 (चतुर्थांश - भाग्य, भूमि, भवन व सुख)",
        "D7": "D7 (सप्तमांश - संतान, संतति व वंश वृद्धि)",
        "D9": "D9 (नवांश - धर्म, विवाह, जीवनसाथी व सूक्ष्म भाग्य)",
        "D10": "D10 (दशमांश - कर्म, पद-प्रतिष्ठा, व्यवसाय व कीर्ति)",
        "D12": "D12 (द्वादशांश - माता-पिता, पितृ व कुल संस्कार)",
        "D16": "D16 (षोडशांश - वाहन, भौतिक सुख, ऐश्वर्य व आनंद)",
        "D20": "D20 (विंशांश - आध्यात्मिक साधना, उपासना व तप)",
        "D24": "D24 (चतुर्विंशांश - उच्च विद्या, ज्ञान, बुद्धि व मेधा)",
        "D27": "D27 (सप्तविंशांश - अवचेतन शक्ति, बल व दुर्बलता)",
        "D30": "D30 (त्रिंशांश - अरिष्ट, पाप, विपत्ति व दोष)",
        "D40": "D40 (खवेदांश - शुभाशुभ फल व मातृक पूर्वजन्म)",
        "D45": "D45 (अक्षवेदांश - सदाचार, चरित्र व समग्र भाग्य)",
        "D60": "D60 (षष्ट्यंश - सूक्ष्म प्रारब्ध, संचित कर्म व सर्व फल)",
        "D72": "D72 (अष्टोत्तरांश - सूक्ष्म आध्यात्मिक सिद्धि व बल)",
        "D81": "D81 (नवनवांश - अंतरंग आत्म-सामर्थ्य व सूक्ष्म चरित्र)",
        "D108": "D108 (अष्टोत्तरशतांश - नक्षत्र-पाद चक्र व नाड़ी सूक्ष्म फल)",
        "D144": "D144 (द्वादश-द्वादशांश - आनुवंशिक पूर्वज संस्कार व वंश ऋण)",
        "D150": "D150 (नाड्यांश - देव केरलम् / चंद्र कला नाड़ी सूक्ष्म रेखा)"
    }

    vais_data = [
        {"शुभ वर्ग संख्या": "२ वर्ग", "शास्त्रीय संज्ञा": "पारिजात (Parijata)", "फलित प्रभाव": "सामान्य सुख, जीवन में स्थिरता, धन व समाज में सामान्य कीर्ति।"},
        {"शुभ वर्ग संख्या": "३ वर्ग", "शास्त्रीय संज्ञा": "उत्तम (Uttama)", "फलित प्रभाव": "सद्विचार, उत्तम आचरण, विनयशीलता, विद्या लाभ व लोकसम्मान।"},
        {"शुभ वर्ग संख्या": "४ वर्ग", "शास्त्रीय संज्ञा": "गोपुर (Gopura)", "फलित प्रभाव": "प्रचुर भूमि, वाहन, पशु-धन, बौद्धिक ऐश्वर्य व कुटुम्ब का पोषण।"},
        {"शुभ वर्ग संख्या": "५ वर्ग", "शास्त्रीय संज्ञा": "सिंहासन (Simhasana)", "फलित प्रभाव": "राजतुल्य प्रतिष्ठा, शासन-प्रशासन में अधिकार, नेतृत्व व प्रभुत्व।"},
        {"शुभ वर्ग संख्या": "६ वर्ग", "शास्त्रीय संज्ञा": "पारावत (Paravata)", "फलित प्रभाव": "सर्वप्रिय व्यक्तित्व, उत्तम सवारी, राज्य द्वारा सम्मानित व अक्षय कीर्ति।"},
        {"शुभ वर्ग संख्या": "७ वर्ग", "शास्त्रीय संज्ञा": "देवलोक (Devaloka)", "फलित प्रभाव": "राजाधिराज पद, देवतुल्य आदर, महान धार्मिक कार्य व दीर्घायु।"},
        {"शुभ वर्ग संख्या": "८ वर्ग", "शास्त्रीय संज्ञा": "ऐरावत (Airavata)", "फलित प्रभाव": "सम्राट तुल्य वैभव, गजराज समान ऐश्वर्य, कीर्ति का दिगन्त विस्तार।"},
        {"शुभ वर्ग संख्या": "९ वर्ग", "शास्त्रीय संज्ञा": "वैशेषिक (Vaisheshika)", "फलित प्रभाव": "सर्वमनोरथ सिद्धि, अद्वितीय शास्त्रज्ञान, विश्वविख्यात प्रतिष्ठा।"},
        {"शुभ वर्ग संख्या": "१० वर्ग", "शास्त्रीय संज्ञा": "भास्वदांश (Bhasvadamsa)", "फलित प्रभाव": "सूर्य समान तेज, अपराजेय प्रभाव, अमर यश व राजपूजित।"},
        {"शुभ वर्ग संख्या": "११ वर्ग", "शास्त्रीय संज्ञा": "इन्द्रलोक (Indraloka)", "फलित प्रभाव": "इन्द्रसम ऐश्वर्य, अपार संपदा, भोग-विलास व कीर्ति।"},
        {"शुभ वर्ग संख्या": "१२ वर्ग", "शास्त्रीय संज्ञा": "कल्पवृक्ष (Kalpavriksha)", "फलित प्रभाव": "सर्व मनोकामनाओं की पूर्ति, अक्षय दानशीलता व अमूल्य सम्पत्ति।"},
        {"शुभ वर्ग संख्या": "१३ वर्ग", "शास्त्रीय संज्ञा": "ब्रह्मलोक (Brahmaloka)", "फलित प्रभाव": "परम ज्ञान, तपस्या का फल, आत्मसाक्षात्कार व शाश्वत प्रतिष्ठा।"},
        {"शुभ वर्ग संख्या": "१४ वर्ग", "शास्त्रीय संज्ञा": "शिवलोक (Shivaloka)", "फलित प्रभाव": "परम शक्ति, कल्याणकारी स्वभाव, शत्रुओं पर विजय व मोक्ष मार्ग।"},
        {"शुभ वर्ग संख्या": "१५ वर्ग", "शास्त्रीय संज्ञा": "विष्णुलोक (Vishnuloka)", "फलित प्रभाव": "अक्षय श्री, धर्म-रक्षा, जननायकत्व व परम पद प्राप्ति।"},
        {"शुभ वर्ग संख्या": "१६ वर्ग", "शास्त्रीय संज्ञा": "कामधेनु (Kamadhenu)", "फलित प्रभाव": "अखंड साम्राज्य, सर्वसिद्धि, जीवन-मृत्यु के चक्र से मुक्ति व मोक्ष।"}
    ]

    varga_deity_data = [
        {"वर्ग": "D1", "नाम": "लग्न / राशि", "भाग": "1", "फलित प्रयोजन": "समग्र देह, शारीरिक स्वास्थ्य, रूप, रंग व सामान्य स्वभाव", "अधिष्ठाता देवता": "द्वादश आदित्य"},
        {"वर्ग": "D2", "नाम": "होरा", "भाग": "2", "फलित प्रयोजन": "धन, संपत्ति, पैतृक वैभव, वाणी व कुटुम्ब सुख", "अधिष्ठाता देवता": "सूर्य एवं चन्द्र (पितर व देव)"},
        {"वर्ग": "D3", "नाम": "द्रेष्काण", "भाग": "3", "फलित प्रयोजन": "पराक्रम, छोटे भाई-बहन, साहस, उद्यम व मृत्यु कारण", "अधिष्ठाता देवता": "नारद, अगस्त्य, दुर्वासा"},
        {"वर्ग": "D4", "नाम": "चतुर्थांश", "भाग": "4", "फलित प्रयोजन": "भूमि, भवन, अचल संपत्ति, वाहन व सामान्य भाग्य", "अधिष्ठाता देवता": "सनक, सनन्द, सनातन, सनत्कुमार"},
        {"वर्ग": "D7", "नाम": "सप्तमांश", "भाग": "7", "फलित प्रयोजन": "संतान सुख, वंश वृद्धि, पौत्र-दौहित्र व संतति सामर्थ्य", "अधिष्ठाता देवता": "क्षार, क्षीर, दधि, घृत, इक्षु, मद्य, शुद्धजल"},
        {"वर्ग": "D9", "नाम": "नवांश", "भाग": "9", "फलित प्रयोजन": "धर्म, जीवनसाथी, दांपत्य सुख, सूक्ष्म भाग्य व आंतरिक गुण", "अधिष्ठाता देवता": "देव, मनुष्य, राक्षस गण"},
        {"वर्ग": "D10", "नाम": "दशमांश", "भाग": "10", "फलित प्रयोजन": "आजीविका, कर्म, पद-प्रतिष्ठा, व्यापार, यश व सामाजिक अधिकार", "अधिष्ठाता देवता": "दश दिक्पाल (इन्द्र, अग्नि आदि)"},
        {"वर्ग": "D12", "नाम": "द्वादशांश", "भाग": "12", "फलित प्रयोजन": "माता-पिता का सुख, पूर्वजों का ऋण व कुल परंपरा", "अधिष्ठाता देवता": "गणेश, अश्विनीकुमार, यम, सर्प"},
        {"वर्ग": "D16", "नाम": "षोडशांश", "भाग": "16", "फलित प्रयोजन": "वाहन सुख, भौतिक सुख-साधन, यात्राएं व आनंद", "अधिष्ठाता देवता": "ब्रह्मा, विष्णु, शिव, सूर्य"},
        {"वर्ग": "D20", "नाम": "विंशांश", "भाग": "20", "फलित प्रयोजन": "आध्यात्मिक प्रगति, उपासना, मन्त्र सिद्धि व भक्ति भाव", "अधिष्ठाता देवता": "काली, गौरी, जया, विजया आदि"},
        {"वर्ग": "D24", "नाम": "चतुर्विंशांश", "भाग": "24", "फलित प्रयोजन": "उच्च शिक्षा, विद्या, मेधा शक्ति, ज्ञान व अनुसंधान", "अधिष्ठाता देवता": "स्कन्द, प्रजापति आदि"},
        {"वर्ग": "D27", "नाम": "सप्तविंशांश", "भाग": "27", "फलित प्रयोजन": "शारीरिक बल, अवचेतन सामर्थ्य व मानसिक सहनशीलता", "अधिष्ठाता देवता": "वसु, वरुण, मित्र, अर्यमा आदि"},
        {"वर्ग": "D30", "नाम": "त्रिंशांश", "भाग": "30", "फलित प्रयोजन": "अरिष्ट, रोग, विपत्ति, शत्रु भय, दुर्घटना व पूर्वजन्म दोष", "अधिष्ठाता देवता": "यम, वायु, इन्द्र, वरुण, कुबेर"},
        {"वर्ग": "D40", "नाम": "खवेदांश", "भाग": "40", "फलित प्रयोजन": "मातृक पक्ष का शुभाशुभ फल, शुभ-अशुभ संस्कार व घटनाक्रम", "अधिष्ठाता देवता": "विष्णु व चन्द्र देव"},
        {"वर्ग": "D45", "नाम": "अक्षवेदांश", "भाग": "45", "फलित प्रयोजन": "चारित्रिक शुद्धता, सदाचार, नैतिक बल व समग्र जीवन की पवित्रता", "अधिष्ठाता देवता": "ब्रह्मा, शिव, विष्णु"},
        {"वर्ग": "D60", "नाम": "षष्ट्यंश", "भाग": "60", "फलित प्रयोजन": "सूक्ष्म प्रारब्ध, संचित कर्मों का पूर्ण लेखा-जोखा व सर्वोच्च फलित", "अधिष्ठाता देवता": "६० षष्ट्यंश अधिष्ठाता (घोर, राक्षस, देव आदि)"}
    ]

    dasvarga_codes = ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D24", "D30", "D60"]
    shodashvarga_codes = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]

    # Compute summaries
    dv_summary = affliction_engine.calculate_varga_dignity_summary(dasvarga_codes)
    sv_summary = affliction_engine.calculate_varga_dignity_summary(shodashvarga_codes)

    # Classical Shastriya Shloka Card Definition
    bphs_varga_shloka = {
        "title": "बृहत्पाराशर होराशास्त्रम् — वैशेषिकांश एवं वर्ग बल विचार",
        "source": "महर्षि पराशर विरचित BPHS (अध्याय ६ एवं ४५)",
        "shloka": "पारिजातांशके जाते धनवान् कीर्तिमान् सुधीः।\nउत्तमे च गुणाध्यक्षो गोपुरे धान्यवान् भवेत्॥\nसिंहासने नृपप्रायः पारावते महायशाः।\nदेवलोके नृपो भूयादैरावते तु भूपतिः॥",
        "meaning": "पारिजात (२ शुभ वर्ग) में उत्पन्न जातक धनवान, कीर्तिमान व बुद्धिमान होता है। उत्तम (३ वर्ग) में गुणवान, गोपुर (४ वर्ग) में प्रचुर संपत्तिवान, सिंहासन (५ वर्ग) में राजतुल्य, पारावत (६ वर्ग) में महायशस्वी, देवलोक (७ वर्ग) में राजा और ऐरावत (८ वर्ग) में चक्रवर्ती सम्राट समान प्रतिष्ठा प्राप्त करता है।"
    }

    # Active Native Micro-Planetary Longitudes & DMS Calculations
    lagna_sname = getattr(chart, "lagna_sign_name", "Aries")
    moon = chart.planets.get("Moon")
    
    top_p = max(sv_summary.keys(), key=lambda p: sv_summary[p]["score_20"]) if sv_summary else "Jupiter"
    top_v_name = sv_summary[top_p]["vaisheshikamsa_hi"] if sv_summary else "पारिजात"
    varg_count = sum(1 for p in sv_summary.values() if p.get("is_vargottama")) if sv_summary else 0
    avg_score = sum(p["score_20"] for p in sv_summary.values()) / len(sv_summary) if sv_summary else 0.0

    # Level 1 Module Tabs CSS & Unified Spacing
    st.markdown("""
    <style>
    /* Zero excess whitespace for Level 1 tabs and Level 2 sub-tabs */
    div[data-testid="stTabs"] {
        margin-top: 0px !important;
        margin-bottom: 4px !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] {
        padding-top: 4px !important;
        padding-bottom: 2px !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] > div > div[data-testid="stTabs"],
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] div[data-testid="stTabs"] {
        margin-top: 2px !important;
        margin-bottom: 3px !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"] {
        margin-top: 1px !important;
        margin-bottom: 1px !important;
        padding: 3px 5px !important;
        gap: 4px !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"] button[role="tab"] {
        padding: 4px 12px !important;
        font-size: 12.5px !important;
    }
    /* Uniform equal spacing for all Expanders so they never stick together */
    div[data-testid="stExpander"] {
        margin-top: 14px !important;
        margin-bottom: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 3 Dedicated Tabs immediately at the top (Zero Top Whitespace)
    tab_dv, tab_sv, tab_saransh = st.tabs(tabs)

    # =========================================================================
    # TAB 1: DASHVARGA (10 PRINCIPAL DIVISIONS)
    # =========================================================================
    with tab_dv:
        subtab_dv_dignity, subtab_dv_table, subtab_dv_praman = st.tabs([
            "1. 📊 दशवर्ग ग्रह गरिमा एवं वैशेषिकांश वितरण",
            "2. 📋 दशवर्ग टेबल (Table)",
            "3. 📜 दशवर्ग शास्त्रीय प्रमाण एवं फलादेश"
        ])

        with subtab_dv_dignity:
            # Top 4 KPI Metrics for Dasvarga
            top_dv_planet = max(dv_summary.keys(), key=lambda p: dv_summary[p]["score_20"])
            vargottama_planets = [p for p in dv_summary if dv_summary[p]["is_vargottama"]]
            varg_str = ", ".join(vargottama_planets) if vargottama_planets else "कोई नहीं"
            total_exalt_own_dv = sum(dv_summary[p]["own_mool_exalt"] for p in dv_summary)
            deb_dv = [(p, dv_summary[p]["counts"]["deb"]) for p in dv_summary if dv_summary[p]["counts"]["deb"] > 0]
            deb_str = ", ".join([f"{p} ({c})" for p, c in deb_dv]) if deb_dv else "शून्य (उत्तम)"

            c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
            c_kpi1.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #10B981; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(16,185,129,0.08);">
                <div style="font-size:11px; color:#059669; font-weight:800;">🌟 सर्वोच्च प्रतिष्ठित ग्रह</div>
                <div style="font-size:16px; font-weight:900; color:{'#34D399' if _is_dark else '#065F46'};">{top_dv_planet} ({dv_summary[top_dv_planet]['score_20']:.1f}/20)</div>
                <div style="font-size:10.5px; color:#64748B;">👑 {dv_summary[top_dv_planet]['vaisheshikamsa_hi']} ({dv_summary[top_dv_planet]['auspicious_count']} शुभ वर्ग)</div>
            </div>
            """, unsafe_allow_html=True)

            c_kpi2.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #3B82F6; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(59,130,246,0.08);">
                <div style="font-size:11px; color:#2563EB; font-weight:800;">👑 वर्गोत्तम ग्रह (D1 = D9)</div>
                <div style="font-size:16px; font-weight:900; color:{'#60A5FA' if _is_dark else '#1E40AF'};">{varg_str}</div>
                <div style="font-size:10.5px; color:#64748B;">नवांश व लग्न में समान राशि बल</div>
            </div>
            """, unsafe_allow_html=True)

            c_kpi3.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #8B5CF6; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(139,92,246,0.08);">
                <div style="font-size:11px; color:#7C3AED; font-weight:800;">🛡️ उच्च/मूल/स्व वर्ग योग</div>
                <div style="font-size:16px; font-weight:900; color:{'#A78BFA' if _is_dark else '#5B21B6'};">{total_exalt_own_dv} वर्ग स्थितियां</div>
                <div style="font-size:10.5px; color:#64748B;">१० वर्गों में प्रबल गरिमा संख्या</div>
            </div>
            """, unsafe_allow_html=True)

            c_kpi4.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #F59E0B; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(245,158,11,0.08);">
                <div style="font-size:11px; color:#D97706; font-weight:800;">⚠️ नीच वर्ग दृष्टि/सतर्कता</div>
                <div style="font-size:16px; font-weight:900; color:{'#FBBF24' if _is_dark else '#92400E'};">{deb_str}</div>
                <div style="font-size:10.5px; color:#64748B;">उपाय एवं शांति अपेक्षित क्षेत्र</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # Executive Graph for Dasvarga
            st.markdown(render_varga_dignity_dashboard(
                dv_summary, total_vargas=len(dasvarga_codes), is_dark=_is_dark,
                title="दशवर्ग ग्रह गरिमा एवं वैशेषिकांश वितरण (Dasvarga Planetary Dignity & Vaisheshikamsa)"
            ), unsafe_allow_html=True)

            # Dignity Legend Bar
            st.markdown(render_dignity_legend_bar(), unsafe_allow_html=True)

        with subtab_dv_table:
            # Dignity Legend Bar
            st.markdown(render_dignity_legend_bar(), unsafe_allow_html=True)

            # Styled HTML Table (NO redundant st.dataframe!)
            dv_table = affliction_engine.calculate_dasvarga_table()
            st.markdown(render_styled_varga_table_html(dv_table, varga_meta_full, is_dark=_is_dark), unsafe_allow_html=True)

        with subtab_dv_praman:
            # ─── Interactive Dasvarga Domain Insight Explorer ───
            with st.expander("🔍 विशिष्ट दशवर्ग फलित अन्वेषक (Dasvarga Life-Domain Deep Dive)", expanded=True):
                sel_dv_code = st.selectbox(
                    "विश्लेषण हेतु वर्ग चुनें (Select Dasvarga)",
                    dasvarga_codes,
                    format_func=lambda x: varga_meta_full.get(x, x),
                    key="dv_deep_dive_sel"
                )
                _t_varga = chart.vargas.get(sel_dv_code) if chart.vargas else None
                if _t_varga:
                    _v_l_sign = getattr(_t_varga, "lagna_sign_name", chart.lagna_sign_name)
                    _v_l_lord = SIGN_LORDS.get(_v_l_sign, "—")
                    _v_p_map = getattr(_t_varga, "planets", {})

                    _ex_p = [pn for pn, pp in _v_p_map.items() if getattr(pp, "sign_name", "") == {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"}.get(pn)]
                    _own_p = [pn for pn, pp in _v_p_map.items() if SIGN_LORDS.get(getattr(pp, "sign_name", "")) == pn]
                    _deb_p = [pn for pn, pp in _v_p_map.items() if getattr(pp, "sign_name", "") == {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"}.get(pn)]

                    st.markdown(_clean_html(f"""
                    <div style="background:{'#1E293B' if _is_dark else '#F8FAFC'}; border:1.5px solid #CBD5E1; border-radius:10px; padding:12px 16px; font-size:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-weight:900; color:{'#60A5FA' if _is_dark else '#1E40AF'}; font-size:13.5px;">🎯 {varga_meta_full.get(sel_dv_code, sel_dv_code)}</span>
                            <span style="font-size:11px; font-weight:800; background:#EFF6FF; color:#1E40AF; padding:2px 8px; border-radius:4px;">वर्ग लग्न: {_v_l_sign} (स्वामी: {_v_l_lord})</span>
                        </div>
                        <div style="line-height:1.6; color:{'#E2E8F0' if _is_dark else '#1E293B'};">
                            • 🌟 <b>उच्च ग्रह:</b> {', '.join(_ex_p) if _ex_p else 'कोई नहीं'} {'— इस क्षेत्र में विशिष्ट कीर्ति व अधिकार' if _ex_p else ''}<br/>
                            • 🏰 <b>स्वगृही ग्रह:</b> {', '.join(_own_p) if _own_p else 'कोई नहीं'} {'— इस क्षेत्र में आत्म-निर्भरता व स्थायित्व' if _own_p else ''}<br/>
                            • ⚠️ <b>नीच ग्रह:</b> {', '.join(_deb_p) if _deb_p else 'कोई नहीं (दोष मुक्त)'} {'— अतिरिक्त साधना व जागरूकता अपेक्षित' if _deb_p else ''}
                        </div>
                    </div>
                    """), unsafe_allow_html=True)
                else:
                    st.caption(f"{sel_dv_code} वर्ग गणना उपलब्ध नहीं।")

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # Classical Dasvarga Shloka & Pramana Card
            st.markdown(_clean_html(f"""
            <div style="background: rgba(37, 99, 235, 0.08); border-left: 4px solid #2563EB; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px;">
                <div style="font-weight: 700; color: #1D4ED8; font-size: 13.5px; margin-bottom: 4px;">📖 बृहत्पाराशर होराशास्त्रम् — दशवर्ग फल एवं विंशोपक बल विधान</div>
                <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
                    दशवर्गेषु ये खेटाः स्वांशेषु स्वोच्चकेषु च।<br/>
                    तेषां वीर्यं प्रवक्ष्यामि शृणु त्वं द्विजसत्तम॥<br/>
                    वर्गोत्तमे स्थिताः सर्वे कुर्वन्ति विपुलं यशः।<br/>
                    दशवर्गबलेनैव सम्पूर्णं फलमादिशेत्॥
                </div>
                <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
                    <b>हिंदी भावार्थ:</b> दशवर्गों में जो ग्रह स्वराशि, मूलत्रिकोण अथवा उच्चांश में स्थित होते हैं, वे जातक को अक्षय बल, ऐश्वर्य व कीर्ति प्रदान करते हैं। विशेष रूप से लग्न व नवांश में वर्गोत्तम ग्रह जातक को अतुल्य ख्याति दिलाता है। फलादेश का अंतिम निर्णय दशवर्ग बल देखकर ही करना चाहिए।
                </div>
            </div>
            """), unsafe_allow_html=True)

            # Vaisheshikamsa Summary for Dasvarga (Up to 10 Auspicious Vargas)
            st.markdown("##### 👑 दशवर्ग वैशेषिकांश संज्ञाएं (Dasvarga Vaisheshikamsa System)")
            dv_vais_data = [
                {"शुभ वर्ग संख्या": "२ वर्ग", "शास्त्रीय संज्ञा": "पारिजात (Parijata)", "फलित प्रभाव": "सामान्य सुख, जीवन में स्थिरता, धन व समाज में सामान्य कीर्ति।"},
                {"शुभ वर्ग संख्या": "३ वर्ग", "शास्त्रीय संज्ञा": "उत्तम (Uttama)", "फलित प्रभाव": "सद्विचार, उत्तम आचरण, विनयशीलता, विद्या लाभ व लोकसम्मान।"},
                {"शुभ वर्ग संख्या": "४ वर्ग", "शास्त्रीय संज्ञा": "गोपुर (Gopura)", "फलित प्रभाव": "प्रचुर भूमि, वाहन, पशु-धन, बौद्धिक ऐश्वर्य व कुटुम्ब का पोषण।"},
                {"शुभ वर्ग संख्या": "५ वर्ग", "शास्त्रीय संज्ञा": "सिंहासन (Simhasana)", "फलित प्रभाव": "राजतुल्य प्रतिष्ठा, शासन-प्रशासन में अधिकार, नेतृत्व व प्रभुत्व।"},
                {"शुभ वर्ग संख्या": "६ वर्ग", "शास्त्रीय संज्ञा": "पारावत (Paravata)", "फलित प्रभाव": "सर्वप्रिय व्यक्तित्व, उत्तम सवारी, राज्य द्वारा सम्मानित व अक्षय कीर्ति।"},
                {"शुभ वर्ग संख्या": "७ वर्ग", "शास्त्रीय संज्ञा": "देवलोक (Devaloka)", "फलित प्रभाव": "राजाधिराज पद, देवतुल्य आदर, महान धार्मिक कार्य व दीर्घायु।"},
                {"शुभ वर्ग संख्या": "८ वर्ग", "शास्त्रीय संज्ञा": "ऐरावत (Airavata)", "फलित प्रभाव": "सम्राट तुल्य वैभव, गजराज समान ऐश्वर्य, कीर्ति का दिगन्त विस्तार।"},
                {"शुभ वर्ग संख्या": "९ वर्ग", "शास्त्रीय संज्ञा": "वैशेषिक (Vaisheshika)", "फलित प्रभाव": "सर्वमनोरथ सिद्धि, अद्वितीय शास्त्रज्ञान, विश्वविख्यात प्रतिष्ठा।"},
                {"शुभ वर्ग संख्या": "१० वर्ग", "शास्त्रीय संज्ञा": "भास्वदांश (Bhasvadamsa)", "फलित प्रभाव": "सूर्य समान तेज, अपराजेय प्रभाव, अमर यश व राजपूजित।"}
            ]
            st.dataframe(pd.DataFrame(dv_vais_data), use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 2: SHODASHVARGA (16 FULL DIVISIONS)
    # =========================================================================
    with tab_sv:
        subtab_sv_dignity, subtab_sv_table, subtab_sv_praman = st.tabs([
            "1. 🏛️ षोडशवर्ग समग्र गरिमा एवं वैशेषिकांश वितरण",
            "2. 📋 षोडशवर्ग टेबल (Table)",
            "3. 📜 षोडशवर्ग शास्त्रीय प्रमाण एवं फलादेश"
        ])

        with subtab_sv_dignity:
            # Top 4 KPI Metrics for Shodashvarga
            top_sv_planet = max(sv_summary.keys(), key=lambda p: sv_summary[p]["score_20"])
            avg_sv_score = sum(sv_summary[p]["score_20"] for p in sv_summary) / len(sv_summary)
            total_auspicious_sv = sum(sv_summary[p]["auspicious_count"] for p in sv_summary)
            deb_sv = [(p, sv_summary[p]["counts"]["deb"]) for p in sv_summary if sv_summary[p]["counts"]["deb"] > 0]
            deb_sv_str = ", ".join([f"{p} ({c})" for p, c in deb_sv]) if deb_sv else "शून्य (अति उत्तम)"

            s_kpi1, s_kpi2, s_kpi3, s_kpi4 = st.columns(4)
            s_kpi1.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #10B981; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(16,185,129,0.08);">
                <div style="font-size:11px; color:#059669; font-weight:800;">🌟 षोडशवर्ग शिरोमणि ग्रह</div>
                <div style="font-size:16px; font-weight:900; color:{'#34D399' if _is_dark else '#065F46'};">{top_sv_planet} ({sv_summary[top_sv_planet]['score_20']:.1f}/20)</div>
                <div style="font-size:10.5px; color:#64748B;">👑 {sv_summary[top_sv_planet]['vaisheshikamsa_hi']} ({sv_summary[top_sv_planet]['auspicious_count']}/16 शुभ वर्ग)</div>
            </div>
            """, unsafe_allow_html=True)

            s_kpi2.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #8B5CF6; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(139,92,246,0.08);">
                <div style="font-size:11px; color:#7C3AED; font-weight:800;">⚡ औसत षोडशवर्ग बल</div>
                <div style="font-size:16px; font-weight:900; color:{'#A78BFA' if _is_dark else '#5B21B6'};">{avg_sv_score:.1f} / 20</div>
                <div style="font-size:10.5px; color:#64748B;">समग्र १६ वर्गों की सामूहिक सामर्थ्य</div>
            </div>
            """, unsafe_allow_html=True)

            s_kpi3.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #3B82F6; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(59,130,246,0.08);">
                <div style="font-size:11px; color:#2563EB; font-weight:800;">🛡️ कुल शुभ वर्ग स्थितियां</div>
                <div style="font-size:16px; font-weight:900; color:{'#60A5FA' if _is_dark else '#1E40AF'};">{total_auspicious_sv} / 112</div>
                <div style="font-size:10.5px; color:#64748B;">स्वोच्चमित्रांश योग (७ ग्रह x १६ वर्ग)</div>
            </div>
            """, unsafe_allow_html=True)

            s_kpi4.markdown(f"""
            <div style="background:{'#111827' if _is_dark else '#FFFFFF'}; border:1.5px solid #EF4444; border-radius:10px; padding:10px 14px; box-shadow:0 2px 6px rgba(239,68,68,0.08);">
                <div style="font-size:11px; color:#DC2626; font-weight:800;">⚠️ नीच वर्ग स्थितियां</div>
                <div style="font-size:16px; font-weight:900; color:{'#F87171' if _is_dark else '#991B1B'};">{deb_sv_str}</div>
                <div style="font-size:10.5px; color:#64748B;">१६ वर्गों में नीच राशि स्थिति</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # Executive Graph for Shodashvarga
            st.markdown(render_varga_dignity_dashboard(
                sv_summary, total_vargas=len(shodashvarga_codes), is_dark=_is_dark,
                title="षोडशवर्ग समग्र गरिमा एवं वैशेषिकांश वितरण (Complete 16-Varga Dignity Matrix)"
            ), unsafe_allow_html=True)

            # Dignity Legend Bar
            st.markdown(render_dignity_legend_bar(), unsafe_allow_html=True)

        with subtab_sv_table:
            # Dignity Legend Bar
            st.markdown(render_dignity_legend_bar(), unsafe_allow_html=True)

            # Styled HTML Table for all 16 Vargas
            sv_table = affliction_engine.calculate_shodashvarga_table()
            st.markdown(render_styled_varga_table_html(sv_table, varga_meta_full, is_dark=_is_dark), unsafe_allow_html=True)

        with subtab_sv_praman:
            # ─── Interactive Higher Shodashvarga & Nadi Varga Domain Insight Explorer ───
            with st.expander("🔬 सूक्ष्म षोडशवर्ग एवं नाड़ी उच्च-वर्ग अन्वेषक (Higher Vargas Deep Dive: D16-D150)", expanded=True):
                higher_codes = ["D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60", "D72", "D81", "D108", "D144", "D150"]
                sel_hv_code = st.selectbox(
                    "सूक्ष्म वर्ग चुनें (Select Division)",
                    higher_codes,
                    format_func=lambda x: varga_meta_full.get(x, x),
                    key="hv_deep_dive_sel"
                )
                _hv_varga = chart.vargas.get(sel_hv_code) if (chart.vargas and sel_hv_code in chart.vargas) else None
                if not _hv_varga and chart is not None:
                    from src.jyotish.core.varga import VargaCalculator
                    fn_map = {
                        "D72": VargaCalculator.calculate_d72,
                        "D81": VargaCalculator.calculate_d81,
                        "D108": VargaCalculator.calculate_d108,
                        "D144": VargaCalculator.calculate_d144,
                        "D150": VargaCalculator.calculate_d150,
                    }
                    if sel_hv_code in fn_map:
                        _hv_varga = fn_map[sel_hv_code](chart)

                if _hv_varga:
                    _hv_l_sign = getattr(_hv_varga, "lagna_sign_name", chart.lagna_sign_name)
                    _hv_l_lord = SIGN_LORDS.get(_hv_l_sign, "—")
                    _hv_p_map = getattr(_hv_varga, "planets", {})
                    _hv_deity = getattr(_hv_varga, "lagna_deity", None)

                    _h_ex_p = [pn for pn, pp in _hv_p_map.items() if getattr(pp, "sign_name", "") == {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"}.get(pn)]
                    _h_own_p = [pn for pn, pp in _hv_p_map.items() if SIGN_LORDS.get(getattr(pp, "sign_name", "")) == pn]
                    _h_deb_p = [pn for pn, pp in _hv_p_map.items() if getattr(pp, "sign_name", "") == {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"}.get(pn)]

                    deity_badge = f'<span style="font-size:11px; font-weight:800; background:#FEF3C7; color:#B45309; padding:2px 8px; border-radius:4px; margin-left:6px;">अधिष्ठाता: {_hv_deity}</span>' if _hv_deity else ''

                    st.markdown(_clean_html(f"""
                    <div style="background:{'#1E293B' if _is_dark else '#F8FAFC'}; border:1.5px solid #CBD5E1; border-radius:10px; padding:12px 16px; font-size:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-weight:900; color:{'#A78BFA' if _is_dark else '#6D28D9'}; font-size:13.5px;">👑 {varga_meta_full.get(sel_hv_code, sel_hv_code)}</span>
                            <div>
                                <span style="font-size:11px; font-weight:800; background:#F5F3FF; color:#6D28D9; padding:2px 8px; border-radius:4px;">सूक्ष्म वर्ग लग्न: {_hv_l_sign} (स्वामी: {_hv_l_lord})</span>
                                {deity_badge}
                            </div>
                        </div>
                        <div style="line-height:1.6; color:{'#E2E8F0' if _is_dark else '#1E293B'};">
                            • 🌟 <b>उच्च ग्रह:</b> {', '.join(_h_ex_p) if _h_ex_p else 'कोई नहीं'}<br/>
                            • 🏰 <b>स्वगृही ग्रह:</b> {', '.join(_h_own_p) if _h_own_p else 'कोई नहीं'}<br/>
                            • ⚠️ <b>नीच ग्रह:</b> {', '.join(_h_deb_p) if _h_deb_p else 'कोई नहीं (दोष मुक्त)'}
                        </div>
                    </div>
                    """), unsafe_allow_html=True)

                    # Quick planetary breakdown table for the selected higher varga
                    hv_rows = []
                    for pn, pp in _hv_p_map.items():
                        hv_rows.append({
                            "ग्रह": pn,
                            "वर्ग राशि": pp.sign_name,
                            "भाव": f"भाव {pp.house_number}",
                            "वर्ग अंश": f"{pp.degree_in_varga:.1f}°",
                            "अधिष्ठाता": getattr(pp, "deity", "—") or "—"
                        })
                    if hv_rows:
                        st.dataframe(pd.DataFrame(hv_rows), use_container_width=True, hide_index=True)
                else:
                    st.caption(f"{sel_hv_code} वर्ग गणना उपलब्ध नहीं।")

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # 16 Vargas Utility & Deities Table
            st.markdown("##### 📖 षोडशवर्गों का शास्त्रीय प्रयोजन एवं अधिष्ठाता देवता (16 Vargas Classical Utility & Deities)")
            st.dataframe(pd.DataFrame(varga_deity_data), use_container_width=True, hide_index=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # BPHS Vaisheshikamsa System
            st.markdown("##### 👑 महर्षि पाराशर प्रणीत वैशेषिकांश संज्ञाएं एवं फल (BPHS Ch. 45 Vaisheshikamsa System)")
            st.dataframe(pd.DataFrame(vais_data), use_container_width=True, hide_index=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # Classical Scriptural Pramana Shlokas
            st.markdown("##### 📜 शास्त्रीय प्रमाण एवं मूल श्लोक संग्रह (Classical Scriptural Pramana)")
            sv_shl = SHASTRIYA_SHLOKAS.get("shodashvarga_vaisheshikamsa", {})
            if sv_shl:
                sv_lines = "<br/>".join(sv_shl['shloka'].splitlines())
                st.markdown(_clean_html(f"""
                <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px;">
                    <div style="font-weight: 700; color: #B45309; font-size: 13.5px; margin-bottom: 4px;">📖 {sv_shl['grantha']}</div>
                    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
                        {sv_lines}
                    </div>
                    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
                        <b>हिंदी भावार्थ:</b> {sv_shl['anuvad_hi']}
                    </div>
                    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
                        <b>शास्त्रीय नियम:</b> {sv_shl['rule']}
                    </div>
                </div>
                """), unsafe_allow_html=True)

    # =========================================================================
    # TAB 3: SARANSH, ALL DETAILS & SHASTRIYA PRAMAN
    # =========================================================================
    with tab_saransh:
        st.markdown("#### 📜 दशवर्ग एवं षोडशवर्ग संपूर्ण सारांश एवं शास्त्रीय प्रमाण (Dossier & Shastriya Praman)")
        st.caption("पारिजातादि वैशेषिकांश संज्ञाएं, नवग्रह सूक्ष्म सारांश, १६ वर्गों का शास्त्रीय प्रयोजन एवं बृहत्पाराशर होराशास्त्रम् के मूल प्रमाण श्लोक।")

        # Subsection 1: Planetary Detailed Dossier
        st.markdown("##### 🪐 सप्तग्रह दशवर्ग व षोडशवर्ग तुलनात्मक सारांश (Comparative Planetary Dossier)")
        dossier_rows = []
        d1_c = chart.planets
        d9_c = affliction_engine.all_vargas.get("D9")

        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p_pos = d1_c.get(p_name)
            if p_pos:
                ansh = int(p_pos.sign_degree)
                kala = int(round((p_pos.sign_degree - ansh) * 60.0))
                if kala >= 60:
                    kala = 0
                    ansh += 1
                dms = f"{ansh}° {kala:02d}'"
                nak_str = getattr(p_pos, 'nakshatra', '—')
                pada_str = f"चरण {getattr(p_pos, 'pada', '—')}" if getattr(p_pos, 'pada', None) else ""
                nak_pada = f"[{nak_str} {pada_str}]".strip()
                h_num = getattr(p_pos, 'house', None)
                h_str = f" ({h_num} भाव)" if h_num else ""
                d1_sign = f"{p_pos.sign_name} {dms}{h_str} {nak_pada}"
            else:
                d1_sign = "-"
            d9_sign = d9_c.planets[p_name].sign_name if (d9_c and p_name in d9_c.planets) else "-"
            is_varg = "👑 हाँ (वर्गोत्तम)" if dv_summary[p_name]["is_vargottama"] else "—"
            dv_t = f"{dv_summary[p_name]['vaisheshikamsa_hi']} ({dv_summary[p_name]['auspicious_count']}/11)"
            sv_t = f"{sv_summary[p_name]['vaisheshikamsa_hi']} ({sv_summary[p_name]['auspicious_count']}/16)"
            sc = f"{sv_summary[p_name]['score_20']:.1f}/20"

            dossier_rows.append({
                "ग्रह (Planet)": p_name,
                "लग्न (D1) राशि, अंश-कला व नक्षत्र": d1_sign,
                "नवांश (D9) राशि": d9_sign,
                "वर्गोत्तम": is_varg,
                "दशवर्ग संज्ञा": dv_t,
                "षोडशवर्ग संज्ञा": sv_t,
                "विंशोपक अंक": sc
            })

        st.dataframe(pd.DataFrame(dossier_rows), use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Subsection 2: Vaisheshikamsa System
        st.markdown("##### 👑 महर्षि पाराशर प्रणीत वैशेषिकांश संज्ञाएं एवं फल (BPHS Ch. 45 Vaisheshikamsa System)")
        st.markdown("""
        जब कोई ग्रह अपने **उच्च (Exaltation), मूलत्रिकोण (Moolatrikona), स्वराशि (Own Sign) अथवा मित्र राशि (Friendly Sign)** के वर्गों में स्थित होता है, तो उसे शुभ वर्ग (स्वोच्चमित्रांश) कहा जाता है। ऐसे शुभ वर्गों की संख्या के अनुसार ग्रह को निम्नलिखित शास्त्रीय संज्ञा व फल प्राप्त होता है:
        """)

        vais_data = [
            {"शुभ वर्ग संख्या": "२ वर्ग", "शास्त्रीय संज्ञा": "पारिजात (Parijata)", "फलित प्रभाव": "सामान्य सुख, जीवन में स्थिरता, धन व समाज में सामान्य कीर्ति।"},
            {"शुभ वर्ग संख्या": "३ वर्ग", "शास्त्रीय संज्ञा": "उत्तम (Uttama)", "फलित प्रभाव": "सद्विचार, उत्तम आचरण, विनयशीलता, विद्या लाभ व लोकसम्मान।"},
            {"शुभ वर्ग संख्या": "४ वर्ग", "शास्त्रीय संज्ञा": "गोपुर (Gopura)", "फलित प्रभाव": "प्रचुर भूमि, वाहन, पशु-धन, बौद्धिक ऐश्वर्य व कुटुम्ब का पोषण।"},
            {"शुभ वर्ग संख्या": "५ वर्ग", "शास्त्रीय संज्ञा": "सिंहासन (Simhasana)", "फलित प्रभाव": "राजतुल्य प्रतिष्ठा, शासन-प्रशासन में अधिकार, नेतृत्व व प्रभुत्व।"},
            {"शुभ वर्ग संख्या": "६ वर्ग", "शास्त्रीय संज्ञा": "पारावत (Paravata)", "फलित प्रभाव": "सर्वप्रिय व्यक्तित्व, उत्तम सवारी, राज्य द्वारा सम्मानित व अक्षय कीर्ति।"},
            {"शुभ वर्ग संख्या": "७ वर्ग", "शास्त्रीय संज्ञा": "देवलोक (Devaloka)", "फलित प्रभाव": "राजाधिराज पद, देवतुल्य आदर, महान धार्मिक कार्य व दीर्घायु।"},
            {"शुभ वर्ग संख्या": "८ वर्ग", "शास्त्रीय संज्ञा": "ऐरावत (Airavata)", "फलित प्रभाव": "सम्राट तुल्य वैभव, गजराज समान ऐश्वर्य, कीर्ति का दिगन्त विस्तार।"},
            {"शुभ वर्ग संख्या": "९ वर्ग", "शास्त्रीय संज्ञा": "वैशेषिक (Vaisheshika)", "फलित प्रभाव": "सर्वमनोरथ सिद्धि, अद्वितीय शास्त्रज्ञान, विश्वविख्यात प्रतिष्ठा।"},
            {"शुभ वर्ग संख्या": "१० वर्ग", "शास्त्रीय संज्ञा": "भास्वदांश (Bhasvadamsa)", "फलित प्रभाव": "सूर्य समान तेज, अपराजेय प्रभाव, अमर यश व राजपूजित।"},
            {"शुभ वर्ग संख्या": "११ वर्ग", "शास्त्रीय संज्ञा": "इन्द्रलोक (Indraloka)", "फलित प्रभाव": "इन्द्रसम ऐश्वर्य, अपार संपदा, भोग-विलास व कीर्ति।"},
            {"शुभ वर्ग संख्या": "१२ वर्ग", "शास्त्रीय संज्ञा": "कल्पवृक्ष (Kalpavriksha)", "फलित प्रभाव": "सर्व मनोकामनाओं की पूर्ति, अक्षय दानशीलता व अमूल्य सम्पत्ति।"},
            {"शुभ वर्ग संख्या": "१३ वर्ग", "शास्त्रीय संज्ञा": "ब्रह्मलोक (Brahmaloka)", "फलित प्रभाव": "परम ज्ञान, तपस्या का फल, आत्मसाक्षात्कार व शाश्वत प्रतिष्ठा।"},
            {"शुभ वर्ग संख्या": "१४ वर्ग", "शास्त्रीय संज्ञा": "शिवलोक (Shivaloka)", "फलित प्रभाव": "परम शक्ति, कल्याणकारी स्वभाव, शत्रुओं पर विजय व मोक्ष मार्ग।"},
            {"शुभ वर्ग संख्या": "१५ वर्ग", "शास्त्रीय संज्ञा": "विष्णुलोक (Vishnuloka)", "फलित प्रभाव": "अक्षय श्री, धर्म-रक्षा, जननायकत्व व परम पद प्राप्ति।"},
            {"शुभ वर्ग संख्या": "१६ वर्ग", "शास्त्रीय संज्ञा": "कामधेनु (Kamadhenu)", "फलित प्रभाव": "अखंड साम्राज्य, सर्वसिद्धि, जीवन-मृत्यु के चक्र से मुक्ति व मोक्ष।"}
        ]
        st.dataframe(pd.DataFrame(vais_data), use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Subsection 3: 16 Vargas Utility & Deities Table
        st.markdown("##### 📖 षोडशवर्गों का शास्त्रीय प्रयोजन एवं अधिष्ठाता देवता (16 Vargas Classical Utility & Deities)")
        varga_deity_data = [
            {"वर्ग": "D1", "नाम": "लग्न / राशि", "भाग": "1", "फलित प्रयोजन": "समग्र देह, शारीरिक स्वास्थ्य, रूप, रंग व सामान्य स्वभाव", "अधिष्ठाता देवता": "द्वादश आदित्य"},
            {"वर्ग": "D2", "नाम": "होरा", "भाग": "2", "फलित प्रयोजन": "धन, संपत्ति, पैतृक वैभव, वाणी व कुटुम्ब सुख", "अधिष्ठाता देवता": "सूर्य एवं चन्द्र (पितर व देव)"},
            {"वर्ग": "D3", "नाम": "द्रेष्काण", "भाग": "3", "फलित प्रयोजन": "पराक्रम, छोटे भाई-बहन, साहस, उद्यम व मृत्यु कारण", "अधिष्ठाता देवता": "नारद, अगस्त्य, दुर्वासा"},
            {"वर्ग": "D4", "नाम": "चतुर्थांश", "भाग": "4", "फलित प्रयोजन": "भूमि, भवन, अचल संपत्ति, वाहन व सामान्य भाग्य", "अधिष्ठाता देवता": "सनक, सनन्द, सनातन, सनत्कुमार"},
            {"वर्ग": "D7", "नाम": "सप्तमांश", "भाग": "7", "फलित प्रयोजन": "संतान सुख, वंश वृद्धि, पौत्र-दौहित्र व संतति सामर्थ्य", "अधिष्ठाता देवता": "क्षार, क्षीर, दधि, घृत, इक्षु, मद्य, शुद्धजल"},
            {"वर्ग": "D9", "नाम": "नवांश", "भाग": "9", "फलित प्रयोजन": "धर्म, जीवनसाथी, दांपत्य सुख, सूक्ष्म भाग्य व आंतरिक गुण", "अधिष्ठाता देवता": "देव, मनुष्य, राक्षस गण"},
            {"वर्ग": "D10", "नाम": "दशमांश", "भाग": "10", "फलित प्रयोजन": "आजीविका, कर्म, पद-प्रतिष्ठा, व्यापार, यश व सामाजिक अधिकार", "अधिष्ठाता देवता": "दश दिक्पाल (इन्द्र, अग्नि आदि)"},
            {"वर्ग": "D12", "नाम": "द्वादशांश", "भाग": "12", "फलित प्रयोजन": "माता-पिता का सुख, पूर्वजों का ऋण व कुल परंपरा", "अधिष्ठाता देवता": "गणेश, अश्विनीकुमार, यम, सर्प"},
            {"वर्ग": "D16", "नाम": "षोडशांश", "भाग": "16", "फलित प्रयोजन": "वाहन सुख, भौतिक सुख-साधन, यात्राएं व आनंद", "अधिष्ठाता देवता": "ब्रह्मा, विष्णु, शिव, सूर्य"},
            {"वर्ग": "D20", "नाम": "विंशांश", "भाग": "20", "फलित प्रयोजन": "आध्यात्मिक प्रगति, उपासना, मन्त्र सिद्धि व भक्ति भाव", "अधिष्ठाता देवता": "काली, गौरी, जया, विजया आदि"},
            {"वर्ग": "D24", "नाम": "चतुर्विंशांश", "भाग": "24", "फलित प्रयोजन": "उच्च शिक्षा, विद्या, मेधा शक्ति, ज्ञान व अनुसंधान", "अधिष्ठाता देवता": "स्कन्द, प्रजापति आदि"},
            {"वर्ग": "D27", "नाम": "सप्तविंशांश", "भाग": "27", "फलित प्रयोजन": "शारीरिक बल, अवचेतन सामर्थ्य व मानसिक सहनशीलता", "अधिष्ठाता देवता": "वसु, वरुण, मित्र, अर्यमा आदि"},
            {"वर्ग": "D30", "नाम": "त्रिंशांश", "भाग": "30", "फलित प्रयोजन": "अरिष्ट, रोग, विपत्ति, शत्रु भय, दुर्घटना व पूर्वजन्म दोष", "अधिष्ठाता देवता": "यम, वायु, इन्द्र, वरुण, कुबेर"},
            {"वर्ग": "D40", "नाम": "खवेदांश", "भाग": "40", "फलित प्रयोजन": "मातृक पक्ष का शुभाशुभ फल, शुभ-अशुभ संस्कार व घटनाक्रम", "अधिष्ठाता देवता": "विष्णु व चन्द्र देव"},
            {"वर्ग": "D45", "नाम": "अक्षवेदांश", "भाग": "45", "फलित प्रयोजन": "चारित्रिक शुद्धता, सदाचार, नैतिक बल व समग्र जीवन की पवित्रता", "अधिष्ठाता देवता": "ब्रह्मा, शिव, विष्णु"},
            {"वर्ग": "D60", "नाम": "षष्ट्यंश", "भाग": "60", "फलित प्रयोजन": "सूक्ष्म प्रारब्ध, संचित कर्मों का पूर्ण लेखा-जोखा व सर्वोच्च फलित", "अधिष्ठाता देवता": "६० षष्ट्यंश अधिष्ठाता (घोर, राक्षस, देव आदि)"}
        ]
        st.dataframe(pd.DataFrame(varga_deity_data), use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Subsection 4: Scriptural Pramana Shlokas
        st.markdown("##### 📜 शास्त्रीय प्रमाण एवं मूल श्लोक संग्रह (Classical Scriptural Pramana)")

        sv_shl = SHASTRIYA_SHLOKAS.get("shodashvarga_vaisheshikamsa", {})
        if sv_shl:
            sv_lines = "<br/>".join(sv_shl['shloka'].splitlines())
            st.markdown(_clean_html(f"""
            <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px;">
                <div style="font-weight: 700; color: #B45309; font-size: 13.5px; margin-bottom: 4px;">📖 {sv_shl['grantha']}</div>
                <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
                    {sv_lines}
                </div>
                <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
                    <b>हिंदी भावार्थ:</b> {sv_shl['anuvad_hi']}
                </div>
                <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
                    <b>शास्त्रीय नियम:</b> {sv_shl['rule']}
                </div>
            </div>
            """), unsafe_allow_html=True)

        vg_shl = SHASTRIYA_SHLOKAS.get("vargottama", {})
        if vg_shl:
            vg_lines = "<br/>".join(vg_shl['shloka'].splitlines())
            st.markdown(_clean_html(f"""
            <div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px;">
                <div style="font-weight: 700; color: #047857; font-size: 13.5px; margin-bottom: 4px;">📖 फलदीपिका — वर्गोत्तम विचार (अध्याय ३, श्लोक ९) एवं बृहज्जातक</div>
                <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
                    {vg_lines}
                </div>
                <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
                    <b>हिंदी भावार्थ:</b> {vg_shl['anuvad_hi']}
                </div>
                <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
                    <b>शास्त्रीय नियम:</b> {vg_shl['rule']}
                </div>
            </div>
            """), unsafe_allow_html=True)



    # ─── Shastriya Pramana & Classical Overview moved to Bottom (Zero Top Scroll) ───
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    with st.expander(f"📜 शास्त्रीय प्रमाण — {bphs_varga_shloka['title']}", expanded=False):
        st.markdown(_clean_html(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {bphs_varga_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{bphs_varga_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {bphs_varga_shloka['meaning']}
            </div>
        </div>
        """), unsafe_allow_html=True)

    with st.expander("🔮 लग्न, शिरोमणि व विंशोपक बल सारांश (Key Lagna, Top Planet & Vimshopaka Summary)", expanded=False):
        c_vg1, c_vg2, c_vg3, c_vg4 = st.columns(4)
        c_vg1.metric("लग्न एवं राशि", f"{lagna_sname}", f"चन्द्र: {moon.sign_name if moon else '—'}")
        c_vg2.metric("शिरोमणि ग्रह", f"{top_p}", f"{top_v_name} ({sv_summary[top_p]['score_20']:.1f}/20)")
        c_vg3.metric("वर्गोत्तम ग्रह", f"{varg_count} ग्रह", "D1 व D9 समरूप")
        c_vg4.metric("औसत विंशोपक बल", f"{avg_score:.1f} / 20", "१६ वर्गों का सामूहिक बल")

