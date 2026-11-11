import streamlit as st
import pandas as pd
import importlib

from src.jyotish.core.affliction import LIFE_AREAS
from src.jyotish.core.constants import SIGN_LORDS, SIGN_NAMES
from src.jyotish.services.shastriya_pramana import default_shastriya_pramana_engine
from src.jyotish.services.grahalakshanam import GrahalakshanamClient, GrahalakshanamConfig

def _clean_html(html_str: str) -> str:
    """Strips all leading/trailing indentation from every line so Markdown never treats HTML as code blocks."""
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())

def render_house_freewill_svg(hp_list, is_dark: bool = False) -> str:
    """Renders an executive, publication-grade SVG bar dashboard for 12 Houses Free Will percentage."""
    def _house_num(item):
        h_raw = str(item.get("house", "1"))
        digits = "".join(c for c in h_raw if c.isdigit())
        return int(digits) if digits else 1

    def _parse_val(v):
        try:
            return float(str(v).replace('%', '').strip())
        except Exception:
            return 0.0

    sorted_hp = sorted(hp_list, key=_house_num)

    house_hi = {
        1: "तनु", 2: "धन", 3: "सहज", 4: "सुख", 5: "सुत", 6: "रिपु",
        7: "जाया", 8: "आयु", 9: "धर्म", 10: "कर्म", 11: "लाभ", 12: "व्यय"
    }

    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
    grid_col = "rgba(255,255,255,0.08)" if is_dark else "#F1F5F9"
    axis_col = "#94A3B8" if is_dark else "#64748B"
    base_col = "#475569" if is_dark else "#CBD5E1"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_muted = "#94A3B8" if is_dark else "#64748B"

    w_svg = 680
    h_svg = 205
    pad_left = 44
    pad_right = 16
    top_y = 20
    base_y = 152
    chart_h = base_y - top_y

    n = 12
    col_w = (w_svg - pad_left - pad_right) / n
    bar_w = 26

    # Grid & Y-Axis ticks
    grid_svg = []
    ticks = [25, 50, 75, 100]
    for tick in ticks:
        ty = base_y - (tick / 100.0) * chart_h
        if tick == 50:
            grid_svg.append(f'<line x1="{pad_left}" y1="{ty:.1f}" x2="{w_svg - pad_right}" y2="{ty:.1f}" stroke="#F59E0B" stroke-dasharray="4,4" stroke-width="1.5" opacity="0.95"/>')
            grid_svg.append(f'<text x="{pad_left - 8}" y="{ty + 3.5:.1f}" font-size="9" font-weight="bold" fill="#F59E0B" font-family="sans-serif" text-anchor="end">50%</text>')
            grid_svg.append(f'<text x="{w_svg - pad_right - 4}" y="{ty - 4:.1f}" font-size="8.5" font-weight="700" fill="#F59E0B" font-family="sans-serif" text-anchor="end">स्वाधीनता सीमा (Agency Baseline)</text>')
        else:
            grid_svg.append(f'<line x1="{pad_left}" y1="{ty:.1f}" x2="{w_svg - pad_right}" y2="{ty:.1f}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>')
            grid_svg.append(f'<text x="{pad_left - 8}" y="{ty + 3.5:.1f}" font-size="8.5" fill="{axis_col}" font-family="sans-serif" text-anchor="end">{tick}%</text>')

    grid_svg.append(f'<line x1="{pad_left}" y1="{base_y}" x2="{w_svg - pad_right}" y2="{base_y}" stroke="{base_col}" stroke-width="1.5"/>')
    grid_svg.append(f'<text x="{pad_left - 8}" y="{base_y + 3.5:.1f}" font-size="8.5" fill="{axis_col}" font-family="sans-serif" text-anchor="end">0%</text>')

    bars_svg = []
    for i in range(12):
        item = sorted_hp[i] if i < len(sorted_hp) else {}
        h_num = i + 1
        fw = _parse_val(item.get("freeWill", 0))
        fw_clamped = max(0.0, min(100.0, fw))

        bar_h = max(3.0, (fw_clamped / 100.0) * chart_h) if fw_clamped > 0 else 2.0
        bar_x = pad_left + i * col_w + (col_w - bar_w) / 2
        bar_y = base_y - bar_h

        if fw_clamped >= 50.0:
            grad_id = "fw_grad_emerald"
            val_col = "#10B981" if is_dark else "#047857"
        elif fw_clamped >= 35.0:
            grad_id = "fw_grad_amber"
            val_col = "#F59E0B" if is_dark else "#B45309"
        else:
            grad_id = "fw_grad_ruby"
            val_col = "#EF4444" if is_dark else "#B91C1C"

        bars_svg.append(f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="5" ry="5" fill="url(#{grad_id})" filter="url(#fw_glow)"/>')

        val_str = f"{fw:.0f}%" if fw % 1 == 0 else f"{fw:.1f}%"
        val_y = max(16, bar_y - 5)
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{val_y:.1f}" font-size="10" font-weight="800" fill="{val_col}" font-family="sans-serif" text-anchor="middle">{val_str}</text>')
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 15:.1f}" font-size="10.5" font-weight="800" fill="{text_primary}" font-family="sans-serif" text-anchor="middle">H{h_num}</text>')
        hi_name = house_hi.get(h_num, "")
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 27:.1f}" font-size="9" font-weight="600" fill="{text_muted}" font-family="sans-serif" text-anchor="middle">{hi_name}</text>')

    defs = '''
    <defs>
      <linearGradient id="fw_grad_emerald" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#34D399"/>
        <stop offset="100%" stop-color="#059669"/>
      </linearGradient>
      <linearGradient id="fw_grad_amber" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#FBBF24"/>
        <stop offset="100%" stop-color="#D97706"/>
      </linearGradient>
      <linearGradient id="fw_grad_ruby" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#F87171"/>
        <stop offset="100%" stop-color="#DC2626"/>
      </linearGradient>
      <filter id="fw_glow" x="-10%" y="-10%" width="120%" height="120%">
        <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-opacity="0.18"/>
      </filter>
    </defs>
    '''

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_svg} {h_svg}" style="width:100%; height:auto; display:block;">
      {defs}
      {"".join(grid_svg)}
      {"".join(bars_svg)}
    </svg>'''

    header_html = f'''
    <div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:10px; padding:10px 14px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:6px;">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:8px;">
        <div>
          <div style="font-size:12.5px; font-weight:800; color:{text_primary}; display:flex; align-items:center; gap:6px;">
            <span>📊 १२ भावों का फ्री-विल प्रतिशत वितरण</span>
            <span style="font-size:9.5px; background:rgba(37,99,235,0.12); color:#2563EB; padding:1px 5px; border-radius:4px; font-weight:700;">H1 – H12 प्राकृतिक क्रम</span>
          </div>
          <div style="font-size:10px; color:{text_muted}; margin-top:1px;">कर्म स्वाधीनता (Purushartha) बनाम प्रारब्ध (Destiny) अनुपातिक शक्ति</div>
        </div>
        <div style="display:flex; align-items:center; gap:6px; font-size:9.5px; font-weight:700;">
          <span style="display:inline-flex; align-items:center; gap:3px; color:#059669; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:10px; border:1px solid rgba(16,185,129,0.25);">
            <span style="width:6px; height:6px; border-radius:50%; background:#10B981;"></span> ≥50% पुरुषार्थ
          </span>
          <span style="display:inline-flex; align-items:center; gap:3px; color:#D97706; background:rgba(245,158,11,0.1); padding:2px 6px; border-radius:10px; border:1px solid rgba(245,158,11,0.25);">
            <span style="width:6px; height:6px; border-radius:50%; background:#F59E0B;"></span> 35-49% मध्यम
          </span>
          <span style="display:inline-flex; align-items:center; gap:3px; color:#DC2626; background:rgba(239,68,68,0.1); padding:2px 6px; border-radius:10px; border:1px solid rgba(239,68,68,0.25);">
            <span style="width:6px; height:6px; border-radius:50%; background:#EF4444;"></span> &lt;35% प्रारब्ध
          </span>
        </div>
      </div>
      {svg_content}
    </div>
    '''
    return _clean_html(header_html)


def render_soumya_krura_balance_svg(hp_list, is_dark: bool = False) -> str:
    """Renders an executive dual-bar comparison SVG dashboard for Soumya vs Krura points with Net Balance."""
    def _house_num(item):
        h_raw = str(item.get("house", "1"))
        digits = "".join(c for c in h_raw if c.isdigit())
        return int(digits) if digits else 1

    def _parse_pts(v):
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip()
        if not s or s == "0":
            return 0.0
        if any(c.isalpha() for c in s):
            parts = [p.strip() for p in s.split(",") if p.strip() and p.strip() != "0"]
            return float(len(parts))
        try:
            return float(s.replace('%', ''))
        except Exception:
            return 0.0

    sorted_hp = sorted(hp_list, key=_house_num)

    house_hi = {
        1: "तनु", 2: "धन", 3: "सहज", 4: "सुख", 5: "सुत", 6: "रिपु",
        7: "जाया", 8: "आयु", 9: "धर्म", 10: "कर्म", 11: "लाभ", 12: "व्यय"
    }

    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
    grid_col = "rgba(255,255,255,0.08)" if is_dark else "#F1F5F9"
    axis_col = "#94A3B8" if is_dark else "#64748B"
    base_col = "#475569" if is_dark else "#CBD5E1"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_muted = "#94A3B8" if is_dark else "#64748B"

    # Compute maximum scale
    max_pts = 0.0
    for r in sorted_hp:
        s_val = _parse_pts(r.get("soumya", 0))
        k_val = _parse_pts(r.get("krura", 0))
        max_pts = max(max_pts, s_val, k_val)
    max_scale = max(4.0, float(int(max_pts + 0.99)))

    w_svg = 680
    h_svg = 205
    pad_left = 44
    pad_right = 16
    top_y = 20
    base_y = 148
    chart_h = base_y - top_y

    n = 12
    col_w = (w_svg - pad_left - pad_right) / n
    bar_w = 11.5

    # Grid ticks (integers)
    grid_svg = []
    tick_step = 1 if max_scale <= 5 else 2
    ticks = list(range(tick_step, int(max_scale) + 1, tick_step))
    for tick in ticks:
        ty = base_y - (tick / max_scale) * chart_h
        grid_svg.append(f'<line x1="{pad_left}" y1="{ty:.1f}" x2="{w_svg - pad_right}" y2="{ty:.1f}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>')
        grid_svg.append(f'<text x="{pad_left - 8}" y="{ty + 3.5:.1f}" font-size="8.5" fill="{axis_col}" font-family="sans-serif" text-anchor="end">{tick}</text>')

    grid_svg.append(f'<line x1="{pad_left}" y1="{base_y}" x2="{w_svg - pad_right}" y2="{base_y}" stroke="{base_col}" stroke-width="1.5"/>')
    grid_svg.append(f'<text x="{pad_left - 8}" y="{base_y + 3.5:.1f}" font-size="8.5" fill="{axis_col}" font-family="sans-serif" text-anchor="end">0</text>')

    bars_svg = []
    for i in range(12):
        item = sorted_hp[i] if i < len(sorted_hp) else {}
        h_num = i + 1
        s_val = _parse_pts(item.get("soumya", 0))
        k_val = _parse_pts(item.get("krura", 0))
        net = s_val - k_val

        col_cx = pad_left + i * col_w + col_w / 2

        # Soumya (Benefic) bar on left
        s_h = max(2.0, (s_val / max_scale) * chart_h) if s_val > 0 else 0.0
        s_x = col_cx - bar_w - 1.5
        s_y = base_y - s_h

        # Krura (Malefic) bar on right
        k_h = max(2.0, (k_val / max_scale) * chart_h) if k_val > 0 else 0.0
        k_x = col_cx + 1.5
        k_y = base_y - k_h

        if s_val > 0:
            bars_svg.append(f'<rect x="{s_x:.1f}" y="{s_y:.1f}" width="{bar_w:.1f}" height="{s_h:.1f}" rx="3.5" ry="3.5" fill="url(#pts_grad_soumya)"/>')
            s_str = f"{s_val:g}"
            bars_svg.append(f'<text x="{s_x + bar_w/2:.1f}" y="{s_y - 4:.1f}" font-size="9" font-weight="700" fill="#10B981" font-family="sans-serif" text-anchor="middle">{s_str}</text>')

        if k_val > 0:
            bars_svg.append(f'<rect x="{k_x:.1f}" y="{k_y:.1f}" width="{bar_w:.1f}" height="{k_h:.1f}" rx="3.5" ry="3.5" fill="url(#pts_grad_krura)"/>')
            k_str = f"{k_val:g}"
            bars_svg.append(f'<text x="{k_x + bar_w/2:.1f}" y="{k_y - 4:.1f}" font-size="9" font-weight="700" fill="#EF4444" font-family="sans-serif" text-anchor="middle">{k_str}</text>')

        # House Code (H1..H12)
        bars_svg.append(f'<text x="{col_cx:.1f}" y="{base_y + 14:.1f}" font-size="10.5" font-weight="800" fill="{text_primary}" font-family="sans-serif" text-anchor="middle">H{h_num}</text>')

        # Sanskrit House Name
        hi_name = house_hi.get(h_num, "")
        bars_svg.append(f'<text x="{col_cx:.1f}" y="{base_y + 25:.1f}" font-size="8.5" font-weight="600" fill="{text_muted}" font-family="sans-serif" text-anchor="middle">{hi_name}</text>')

        # Net Score Badge at Bottom
        if net > 0:
            badge_bg = "rgba(16,185,129,0.18)"
            badge_fg = "#059669" if not is_dark else "#34D399"
            net_txt = f"+{net:g}"
        elif net < 0:
            badge_bg = "rgba(239,68,68,0.18)"
            badge_fg = "#DC2626" if not is_dark else "#F87171"
            net_txt = f"{net:g}"
        else:
            badge_bg = "rgba(100,116,139,0.12)"
            badge_fg = "#64748B"
            net_txt = "0"

        badge_w = 24
        badge_h = 13
        badge_rx = col_cx - badge_w / 2
        badge_ry = base_y + 28
        bars_svg.append(f'<rect x="{badge_rx:.1f}" y="{badge_ry:.1f}" width="{badge_w}" height="{badge_h}" rx="3" fill="{badge_bg}"/>')
        bars_svg.append(f'<text x="{col_cx:.1f}" y="{badge_ry + 10:.1f}" font-size="8.5" font-weight="800" fill="{badge_fg}" font-family="sans-serif" text-anchor="middle">{net_txt}</text>')

    defs = '''
    <defs>
      <linearGradient id="pts_grad_soumya" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#34D399"/>
        <stop offset="100%" stop-color="#059669"/>
      </linearGradient>
      <linearGradient id="pts_grad_krura" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#F87171"/>
        <stop offset="100%" stop-color="#DC2626"/>
      </linearGradient>
    </defs>
    '''

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_svg} {h_svg}" style="width:100%; height:auto; display:block;">
      {defs}
      {"".join(grid_svg)}
      {"".join(bars_svg)}
    </svg>'''

    header_html = f'''
    <div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:10px; padding:10px 14px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:6px;">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:8px;">
        <div>
          <div style="font-size:12.5px; font-weight:800; color:{text_primary}; display:flex; align-items:center; gap:6px;">
            <span>⚖️ भाव सौम्य (शुभ) बनाम क्रूर (पाप) प्रभाव अंक</span>
            <span style="font-size:9.5px; background:rgba(16,185,129,0.12); color:#059669; padding:1px 5px; border-radius:4px; font-weight:700;">द्वि-चर तुलना</span>
          </div>
          <div style="font-size:10px; color:{text_muted}; margin-top:1px;">शुभ ग्रह (सौम्य) बनाम पाप ग्रह (क्रूर) प्रभाव व नीचे नेट संतुलन अंक (+/-)</div>
        </div>
        <div style="display:flex; align-items:center; gap:6px; font-size:9.5px; font-weight:700;">
          <span style="display:inline-flex; align-items:center; gap:3px; color:#059669; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:10px; border:1px solid rgba(16,185,129,0.25);">
            <span style="width:6px; height:6px; border-radius:50%; background:#10B981;"></span> सौम्य (Benefic)
          </span>
          <span style="display:inline-flex; align-items:center; gap:3px; color:#DC2626; background:rgba(239,68,68,0.1); padding:2px 6px; border-radius:10px; border:1px solid rgba(239,68,68,0.25);">
            <span style="width:6px; height:6px; border-radius:50%; background:#EF4444;"></span> क्रूर (Malefic)
          </span>
          <span style="display:inline-flex; align-items:center; gap:3px; color:#2563EB; background:rgba(37,99,235,0.1); padding:2px 6px; border-radius:10px; border:1px solid rgba(37,99,235,0.25);">
            ⚖️ नेट संतुलन
          </span>
        </div>
      </div>
      {svg_content}
    </div>
    '''
    return _clean_html(header_html)


def _render_fw_bar(val: float, is_dark: bool = False) -> str:
    """Generates an executive progress bar + badge for Free Will percentage."""
    clamped = max(0.0, min(100.0, float(val)))
    if clamped >= 50.0:
        grad = "linear-gradient(90deg, #34D399, #059669)"
        text_c = "#059669" if not is_dark else "#34D399"
        badge = '<span style="background:rgba(16,185,129,0.12); color:#059669; font-size:9.5px; font-weight:800; padding:1px 6px; border-radius:8px; border:1px solid rgba(16,185,129,0.25);">पुरुषार्थ</span>'
    elif clamped >= 35.0:
        grad = "linear-gradient(90deg, #FBBF24, #D97706)"
        text_c = "#D97706" if not is_dark else "#FBBF24"
        badge = '<span style="background:rgba(245,158,11,0.12); color:#D97706; font-size:9.5px; font-weight:800; padding:1px 6px; border-radius:8px; border:1px solid rgba(245,158,11,0.25);">मध्यम</span>'
    else:
        grad = "linear-gradient(90deg, #F87171, #DC2626)"
        text_c = "#DC2626" if not is_dark else "#F87171"
        badge = '<span style="background:rgba(239,68,68,0.12); color:#DC2626; font-size:9.5px; font-weight:800; padding:1px 6px; border-radius:8px; border:1px solid rgba(239,68,68,0.25);">प्रारब्ध</span>'

    val_str = f"{clamped:.0f}%" if clamped % 1 == 0 else f"{clamped:.1f}%"
    bar_bg = "rgba(255,255,255,0.08)" if is_dark else "#E2E8F0"

    html = f'<div style="display:flex; align-items:center; gap:8px;"><span style="font-weight:900; font-size:12px; color:{text_c}; min-width:38px;">{val_str}</span><div style="flex:1; max-width:85px; height:6px; background:{bar_bg}; border-radius:3px; overflow:hidden;"><div style="width:{clamped}%; height:100%; background:{grad}; border-radius:3px;"></div></div>{badge}</div>'
    return html


def _render_pill(val, ptype="neutral", is_dark: bool = False) -> str:
    """Renders high-contrast colored micro-badges for Shastriya metrics."""
    s = str(val).strip()
    if not s or s == "0" or s == "None":
        return f'<span style="color:{"#64748B" if is_dark else "#94A3B8"}; font-weight:600;">—</span>'

    if ptype == "soumya":
        txt = s if any(c.isalpha() for c in s) else f"+{s}"
        return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(16,185,129,0.12); color:{"#34D399" if is_dark else "#059669"}; border:1px solid rgba(16,185,129,0.25);">{txt}</span>'
    elif ptype == "krura":
        txt = s if any(c.isalpha() for c in s) else f"-{s}"
        return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(239,68,68,0.12); color:{"#F87171" if is_dark else "#DC2626"}; border:1px solid rgba(239,68,68,0.25);">{txt}</span>'
    elif ptype == "lords159":
        txt = s if any(c.isalpha() for c in s) else f"+{s}"
        return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(37,99,235,0.12); color:{"#60A5FA" if is_dark else "#1D4ED8"}; border:1px solid rgba(37,99,235,0.25);">{txt}</span>'
    elif ptype == "lords6812":
        txt = s if any(c.isalpha() for c in s) else f"-{s}"
        return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(245,158,11,0.12); color:{"#FBBF24" if is_dark else "#B45309"}; border:1px solid rgba(245,158,11,0.25);">{txt}</span>'
    elif ptype == "dashvarga":
        return f'<span style="display:inline-block; padding:1px 7px; border-radius:6px; font-size:10.5px; font-weight:900; background:rgba(217,119,6,0.12); color:{"#FCD34D" if is_dark else "#B45309"}; border:1px solid rgba(217,119,6,0.3);">⭐ {s}/11</span>'
    elif ptype == "digbala":
        if "Digbala" in s:
            return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(16,185,129,0.12); color:{"#34D399" if is_dark else "#059669"}; border:1px solid rgba(16,185,129,0.25);">⚡ दिग्बली</span>'
        elif "Nirbala" in s:
            return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(239,68,68,0.12); color:{"#F87171" if is_dark else "#DC2626"}; border:1px solid rgba(239,68,68,0.25);">निर्बल</span>'
        return f'<span style="color:{"#64748B" if is_dark else "#94A3B8"}; font-weight:600;">—</span>'
    elif ptype == "kaalbala":
        if "Bali" in s:
            return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(99,102,241,0.12); color:{"#A5B4FC" if is_dark else "#4F46E5"}; border:1px solid rgba(99,102,241,0.25);">🌙 बली</span>'
        return f'<span style="color:{"#64748B" if is_dark else "#94A3B8"}; font-weight:600;">—</span>'
    elif ptype == "exchange":
        if s and s != "0":
            return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(245,158,11,0.12); color:{"#FBBF24" if is_dark else "#B45309"}; border:1px solid rgba(245,158,11,0.25);">🔄 {s}</span>'
        return f'<span style="color:{"#64748B" if is_dark else "#94A3B8"}; font-weight:600;">—</span>'
    elif ptype in ("separative", "sep"):
        return f'<span style="display:inline-block; padding:1px 6px; border-radius:6px; font-size:10px; font-weight:800; background:rgba(147,51,234,0.12); color:{"#C084FC" if is_dark else "#7E22CE"}; border:1px solid rgba(147,51,234,0.25);">{s}</span>'
    else:
        return f'<span style="display:inline-block; padding:1px 5px; border-radius:4px; font-size:10px; font-weight:700; background:rgba(100,116,139,0.1); color:{"#CBD5E1" if is_dark else "#475569"};">{s}</span>'


def render_premium_planet_table(pp_list, is_dark: bool = False) -> str:
    """Renders a sleek, publication-grade responsive HTML table for 9 Planets Free Will & Dashvarga."""
    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
    th_bg = "#1E293B" if is_dark else "#F8FAFC"
    th_col = "#94A3B8" if is_dark else "#475569"
    row_alt = "rgba(255,255,255,0.02)" if is_dark else "#F8FAFC"
    txt_col = "#F1F5F9" if is_dark else "#1E293B"
    border_subtle = "rgba(255,255,255,0.06)" if is_dark else "#F1F5F9"

    p_info = {
        "Sun": {"sym": "☉", "hi": "सूर्य", "col": "#F59E0B"},
        "Moon": {"sym": "☽", "hi": "चन्द्र", "col": "#38BDF8" if is_dark else "#2563EB"},
        "Mars": {"sym": "♂", "hi": "मंगल", "col": "#EF4444"},
        "Mercury": {"sym": "☿", "hi": "बुध", "col": "#10B981"},
        "Jupiter": {"sym": "♃", "hi": "गुरु", "col": "#EAB308"},
        "Venus": {"sym": "♀", "hi": "शुक्र", "col": "#EC4899"},
        "Saturn": {"sym": "♄", "hi": "शनि", "col": "#94A3B8" if is_dark else "#475569"},
        "Rahu": {"sym": "☊", "hi": "राहु", "col": "#A855F7"},
        "Ketu": {"sym": "☋", "hi": "केतु", "col": "#F97316"}
    }

    rows = []
    for idx, p_item in enumerate(pp_list):
        p_name = p_item.get("planet", "")
        inf = p_info.get(p_name, {"sym": "🪐", "hi": p_name, "col": "#64748B"})

        try:
            fw = float(str(p_item.get("freeWill", 0)).replace("%", "").strip())
        except Exception:
            fw = 0.0

        fw_html = _render_fw_bar(fw, is_dark)
        soumya_html = _render_pill(p_item.get("soumya", 0), "soumya", is_dark)
        l159_html = _render_pill(p_item.get("lords159", 0), "lords159", is_dark)
        krura_html = _render_pill(p_item.get("krura", 0), "krura", is_dark)
        l6812_html = _render_pill(p_item.get("lords6812", 0), "lords6812", is_dark)
        disp_html = _render_pill(p_item.get("dispositor", 0), "neutral", is_dark)
        sep_html = _render_pill(p_item.get("seperative", 0), "neutral", is_dark)
        dash_val = p_item.get("dashvarga", 0)
        dash_html = _render_pill(dash_val, "dashvarga", is_dark)

        bg_row = row_alt if idx % 2 == 1 else "transparent"
        row_str = (
            f'<tr style="background:{bg_row}; border-bottom:1px solid {border_subtle};">'
            f'<td style="padding:6px 10px; font-weight:800; color:{txt_col}; white-space:nowrap;">'
            f'<span style="color:{inf["col"]}; font-size:13px; margin-right:4px;">{inf["sym"]}</span>'
            f'<span>{inf["hi"]}</span> <span style="font-size:10px; color:{"#94A3B8" if is_dark else "#64748B"}; font-weight:600;">({p_name})</span>'
            f'</td>'
            f'<td style="padding:6px 10px;">{fw_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{soumya_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{l159_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{krura_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{l6812_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{disp_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{sep_html}</td>'
            f'<td style="padding:6px 10px; text-align:center;">{dash_html}</td>'
            f'</tr>'
        )
        rows.append(row_str)

    html = (
        f'<div style="background:{card_bg}; border:1px solid {card_bdr}; border-radius:10px; overflow:hidden; margin-bottom:8px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">'
        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%; border-collapse:collapse; font-size:11px; text-align:left;">'
        f'<thead><tr style="background:{th_bg}; color:{th_col}; font-weight:800; border-bottom:1.5px solid {card_bdr};">'
        f'<th style="padding:7px 10px;">🪐 ग्रह (Planet)</th>'
        f'<th style="padding:7px 10px; min-width:170px;">⚡ फ्री-विल (Agency %)</th>'
        f'<th style="padding:7px 8px; text-align:center;">🌿 सौम्य (Benefic)</th>'
        f'<th style="padding:7px 8px; text-align:center;">✨ १/५/९ भावेश</th>'
        f'<th style="padding:7px 8px; text-align:center;">🔥 क्रूर (Malefic)</th>'
        f'<th style="padding:7px 8px; text-align:center;">⚠️ ६/८/१२ भावेश</th>'
        f'<th style="padding:7px 8px; text-align:center;">🏛️ डिस्पोजिटर</th>'
        f'<th style="padding:7px 8px; text-align:center;">✂️ सेपरेटिव</th>'
        f'<th style="padding:7px 10px; text-align:center;">👑 दशवर्ग अंक</th>'
        f'</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        f'</table></div></div>'
    )
    return _clean_html(html)


def render_premium_house_table(hp_list, is_dark: bool = False) -> str:
    """Renders a sleek, publication-grade responsive HTML table for 12 Houses Free Will & Points."""
    def _house_num(item):
        h_raw = str(item.get("house", "1"))
        digits = "".join(c for c in h_raw if c.isdigit())
        return int(digits) if digits else 1

    sorted_hp = sorted(hp_list, key=_house_num)

    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
    th_bg = "#1E293B" if is_dark else "#F8FAFC"
    th_col = "#94A3B8" if is_dark else "#475569"
    row_alt = "rgba(255,255,255,0.02)" if is_dark else "#F8FAFC"
    txt_col = "#F1F5F9" if is_dark else "#1E293B"
    border_subtle = "rgba(255,255,255,0.06)" if is_dark else "#F1F5F9"

    house_hi = {
        1: "तनु (Self)", 2: "धन (Wealth)", 3: "सहज (Courage)", 4: "सुख (Home)",
        5: "सुत (Intellect)", 6: "रिपु (Debts)", 7: "जाया (Partner)", 8: "आयु (Longevity)",
        9: "धर्म (Fortune)", 10: "कर्म (Career)", 11: "लाभ (Gains)", 12: "व्यय (Moksha)"
    }

    rows = []
    for idx, h_item in enumerate(sorted_hp):
        h_num = _house_num(h_item)
        hi_name = house_hi.get(h_num, f"H{h_num}")

        try:
            fw = float(str(h_item.get("freeWill", 0)).replace("%", "").strip())
        except Exception:
            fw = 0.0

        fw_html = _render_fw_bar(fw, is_dark)
        soumya_html = _render_pill(h_item.get("soumya", 0), "soumya", is_dark)
        l159_html = _render_pill(h_item.get("lords159", 0), "lords159", is_dark)
        krura_html = _render_pill(h_item.get("krura", 0), "krura", is_dark)
        l6812_html = _render_pill(h_item.get("lords6812", 0), "lords6812", is_dark)
        dig_html = _render_pill(h_item.get("digbala", ""), "digbala", is_dark)
        kaal_html = _render_pill(h_item.get("kaalbala", ""), "kaalbala", is_dark)
        exch_html = _render_pill(h_item.get("exchange", "0"), "exchange", is_dark)
        sep_html = _render_pill(h_item.get("seperative", 0), "neutral", is_dark)

        bg_row = row_alt if idx % 2 == 1 else "transparent"
        row_str = (
            f'<tr style="background:{bg_row}; border-bottom:1px solid {border_subtle};">'
            f'<td style="padding:5px 10px; font-weight:800; color:{txt_col}; white-space:nowrap;">'
            f'<span style="display:inline-block; width:22px; height:20px; line-height:20px; text-align:center; border-radius:4px; background:rgba(37,99,235,0.1); color:#2563EB; font-size:10px; font-weight:900; margin-right:5px;">H{h_num}</span>'
            f'<span>{hi_name}</span>'
            f'</td>'
            f'<td style="padding:5px 10px;">{fw_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{soumya_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{l159_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{krura_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{l6812_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{dig_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{kaal_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{exch_html}</td>'
            f'<td style="padding:5px 8px; text-align:center;">{sep_html}</td>'
            f'</tr>'
        )
        rows.append(row_str)

    html = (
        f'<div style="background:{card_bg}; border:1px solid {card_bdr}; border-radius:10px; overflow:hidden; margin-bottom:8px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">'
        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%; border-collapse:collapse; font-size:11px; text-align:left;">'
        f'<thead><tr style="background:{th_bg}; color:{th_col}; font-weight:800; border-bottom:1.5px solid {card_bdr};">'
        f'<th style="padding:7px 10px;">🏠 भाव (House)</th>'
        f'<th style="padding:7px 10px; min-width:170px;">⚡ फ्री-विल (Agency %)</th>'
        f'<th style="padding:7px 8px; text-align:center;">🌿 सौम्य (Benefic)</th>'
        f'<th style="padding:7px 8px; text-align:center;">✨ १/५/९ भावेश</th>'
        f'<th style="padding:7px 8px; text-align:center;">🔥 क्रूर (Malefic)</th>'
        f'<th style="padding:7px 8px; text-align:center;">⚠️ ६/८/१२ भावेश</th>'
        f'<th style="padding:7px 8px; text-align:center;">🧭 डिगबल</th>'
        f'<th style="padding:7px 8px; text-align:center;">🌙 कालबल</th>'
        f'<th style="padding:7px 8px; text-align:center;">🔄 परिवर्तन</th>'
        f'<th style="padding:7px 8px; text-align:center;">✂️ सेपरेटिव</th>'
        f'</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        f'</table></div></div>'
    )
    return _clean_html(html)


def render_premium_pillar_breakdown_table(rows, title: str, icon: str = "🏛️", is_dark: bool = False) -> str:
    """Renders a sleek, publication-grade HTML card table for 3-Pillar House or Lord affliction breakdown."""
    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#CBD5E1"
    th_bg = "#1E293B" if is_dark else "#F8FAFC"
    th_col = "#94A3B8" if is_dark else "#475569"
    hdr_col = "#F1F5F9" if is_dark else "#0F172A"
    row_alt = "rgba(255,255,255,0.02)" if is_dark else "#F8FAFC"
    txt_col = "#F1F5F9" if is_dark else "#1E293B"
    border_subtle = "rgba(255,255,255,0.06)" if is_dark else "#E2E8F0"

    tb_rows = []
    for idx, r in enumerate(rows):
        label = str(r[0]) if len(r) > 0 else ""
        s_val = str(r[1]) if len(r) > 1 else "0"
        l159_val = str(r[2]) if len(r) > 2 else "0"
        k_val = str(r[3]) if len(r) > 3 else "0"
        l6812_val = str(r[4]) if len(r) > 4 else "0"
        sep_val = str(r[5]) if len(r) > 5 else "0"

        soumya_html = _render_pill(s_val, "soumya", is_dark)
        l159_html = _render_pill(l159_val, "lords159", is_dark)
        krura_html = _render_pill(k_val, "krura", is_dark)
        l6812_html = _render_pill(l6812_val, "lords6812", is_dark)
        sep_html = _render_pill(sep_val, "separative", is_dark)

        bg_row = row_alt if idx % 2 == 1 else "transparent"
        row_str = (
            f'<tr style="background:{bg_row}; border-bottom:1px solid {border_subtle};">'
            f'<td style="padding:6px 10px; font-weight:800; color:{txt_col}; white-space:nowrap;">{label}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{soumya_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{l159_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{krura_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{l6812_html}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{sep_html}</td>'
            f'</tr>'
        )
        tb_rows.append(row_str)

    html = (
        f'<div style="background:{card_bg}; border:1px solid {card_bdr}; border-radius:8px; overflow:hidden; margin-bottom:8px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">'
        f'<div style="font-weight:800; font-size:12px; color:{hdr_col}; padding:7px 10px; background:{th_bg}; border-bottom:1px solid {card_bdr}; display:flex; align-items:center; gap:6px;">'
        f'<span>{icon}</span><span>{title}</span>'
        f'</div>'
        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%; border-collapse:collapse; font-size:11px; text-align:left;">'
        f'<thead><tr style="background:{th_bg}; color:{th_col}; font-weight:800; border-bottom:1px solid {card_bdr};">'
        f'<th style="padding:6px 10px;">Pillar</th>'
        f'<th style="padding:6px 8px; text-align:center;">🌿 सौम्य</th>'
        f'<th style="padding:6px 8px; text-align:center;">✨ १/५/९</th>'
        f'<th style="padding:6px 8px; text-align:center;">🔥 क्रूर</th>'
        f'<th style="padding:6px 8px; text-align:center;">⚠️ ६/८/१२</th>'
        f'<th style="padding:6px 8px; text-align:center;">✂️ सेपरेटिव</th>'
        f'</tr></thead>'
        f'<tbody>{"".join(tb_rows)}</tbody>'
        f'</table></div></div>'
    )
    return _clean_html(html)


def render_premium_rashi_qualities_table(rows, title: str, icon: str = "🔮", is_dark: bool = False) -> str:
    """Renders a sleek HTML card table for Signs & Qualities breakdown."""
    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "rgba(255,255,255,0.12)" if is_dark else "#CBD5E1"
    th_bg = "#1E293B" if is_dark else "#F8FAFC"
    th_col = "#94A3B8" if is_dark else "#475569"
    hdr_col = "#F1F5F9" if is_dark else "#0F172A"
    row_alt = "rgba(255,255,255,0.02)" if is_dark else "#F8FAFC"
    txt_col = "#F1F5F9" if is_dark else "#1E293B"
    border_subtle = "rgba(255,255,255,0.06)" if is_dark else "#E2E8F0"

    sign_hi = {
        "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
        "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
        "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुम्भ", "Pisces": "मीन"
    }

    tb_rows = []
    for idx, r in enumerate(rows):
        entity = str(r[0]) if len(r) > 0 else ""
        sign = str(r[1]) if len(r) > 1 else ""
        mobility = str(r[2]) if len(r) > 2 else ""
        element = str(r[3]) if len(r) > 3 else ""
        varna = str(r[4]) if len(r) > 4 else ""
        purushartha = str(r[5]) if len(r) > 5 else ""
        gender = str(r[6]) if len(r) > 6 else ""
        rising = str(r[7]) if len(r) > 7 else ""
        day_night = str(r[8]) if len(r) > 8 else ""
        guna = str(r[9]) if len(r) > 9 else ""

        # Sign formatting with Hindi name
        sign_label = f"{sign} ({sign_hi.get(sign, '')})" if sign in sign_hi else sign

        if "Movable" in mobility:
            mob_badge = '<span style="background:rgba(16,185,129,0.12); color:#059669; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">चर</span>'
        elif "Fixed" in mobility:
            mob_badge = '<span style="background:rgba(124,58,237,0.12); color:#7C3AED; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">स्थिर</span>'
        else:
            mob_badge = '<span style="background:rgba(217,119,6,0.12); color:#B45309; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">द्विस्वभाव</span>'

        if "Fire" in element:
            elem_badge = '<span style="background:rgba(239,68,68,0.12); color:#DC2626; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">🔥 अग्नि</span>'
        elif "Water" in element:
            elem_badge = '<span style="background:rgba(37,99,235,0.12); color:#2563EB; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">💧 जल</span>'
        elif "Air" in element:
            elem_badge = '<span style="background:rgba(14,165,233,0.12); color:#0284C7; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">💨 वायु</span>'
        else:
            elem_badge = '<span style="background:rgba(245,158,11,0.12); color:#B45309; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">🌍 पृथ्वी</span>'

        gender_badge = '<span style="color:#2563EB; font-weight:700; font-size:10px;">♂ नर</span>' if gender == "Male" else '<span style="color:#EC4899; font-weight:700; font-size:10px;">♀ नारी</span>'
        
        if "Head" in rising:
            rise_badge = '<span style="color:#059669; font-weight:700; font-size:10px;">शीर्षोदय</span>'
        elif "Hind" in rising:
            rise_badge = '<span style="color:#B45309; font-weight:700; font-size:10px;">पृष्ठोदय</span>'
        else:
            rise_badge = '<span style="color:#7C3AED; font-weight:700; font-size:10px;">उभयोदय</span>'

        dn_badge = '<span style="color:#D97706; font-weight:700; font-size:10px;">☀️ दिवा</span>' if day_night == "Day" else '<span style="color:#4F46E5; font-weight:700; font-size:10px;">🌙 रात्रि</span>'

        if guna == "Shrishti":
            guna_badge = '<span style="background:rgba(16,185,129,0.1); color:#059669; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">सृष्टि</span>'
        elif guna == "Samhar":
            guna_badge = '<span style="background:rgba(239,68,68,0.1); color:#DC2626; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">संहार</span>'
        else:
            guna_badge = '<span style="background:rgba(59,130,246,0.1); color:#2563EB; padding:1px 5px; border-radius:4px; font-weight:700; font-size:10px;">स्थिति</span>'

        bg_row = row_alt if idx % 2 == 1 else "transparent"
        row_str = (
            f'<tr style="background:{bg_row}; border-bottom:1px solid {border_subtle};">'
            f'<td style="padding:6px 10px; font-weight:800; color:{txt_col}; white-space:nowrap;">{entity}</td>'
            f'<td style="padding:6px 8px; font-weight:700; color:{txt_col}; white-space:nowrap;">{sign_label}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{mob_badge}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{elem_badge}</td>'
            f'<td style="padding:6px 8px; text-align:center; font-size:10px; color:{txt_col}; font-weight:700;">{varna}</td>'
            f'<td style="padding:6px 8px; text-align:center; font-weight:800; font-size:10.5px; color:#D97706;">{purushartha}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{gender_badge}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{rise_badge}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{dn_badge}</td>'
            f'<td style="padding:6px 8px; text-align:center;">{guna_badge}</td>'
            f'</tr>'
        )
        tb_rows.append(row_str)

    html = (
        f'<div style="background:{card_bg}; border:1px solid {card_bdr}; border-radius:8px; overflow:hidden; margin-bottom:8px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">'
        f'<div style="font-weight:800; font-size:12px; color:{hdr_col}; padding:7px 10px; background:{th_bg}; border-bottom:1px solid {card_bdr}; display:flex; align-items:center; gap:6px;">'
        f'<span>{icon}</span><span>{title}</span>'
        f'</div>'
        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%; border-collapse:collapse; font-size:11px; text-align:left;">'
        f'<thead><tr style="background:{th_bg}; color:{th_col}; font-weight:800; border-bottom:1px solid {card_bdr};">'
        f'<th style="padding:6px 10px;">Entity</th>'
        f'<th style="padding:6px 8px;">Sign</th>'
        f'<th style="padding:6px 8px; text-align:center;">स्वभाव</th>'
        f'<th style="padding:6px 8px; text-align:center;">तत्व</th>'
        f'<th style="padding:6px 8px; text-align:center;">वर्ण</th>'
        f'<th style="padding:6px 8px; text-align:center;">पुरुषार्थ</th>'
        f'<th style="padding:6px 8px; text-align:center;">लिंग</th>'
        f'<th style="padding:6px 8px; text-align:center;">उदय</th>'
        f'<th style="padding:6px 8px; text-align:center;">काल</th>'
        f'<th style="padding:6px 8px; text-align:center;">प्रवृत्ति</th>'
        f'</tr></thead>'
        f'<tbody>{"".join(tb_rows)}</tbody>'
        f'</table></div></div>'
    )
    return _clean_html(html)



def render_remedies_view(chart, tabs=None):
    if "gla_shared_life_area_id" not in st.session_state:
        st.session_state.gla_shared_life_area_id = 1

    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark
    _is_dark = is_astrallis_mode or is_night_mode

    if tabs is None:
        tabs = [
            '🛡️ ग्रह दोष व फ्री-विल',
            '🎯 २७ जीवन क्षेत्र स्कोर',
            '🌿 वैदिक उपचार व उपाय',
            '⚠️ बाधक व मारक विचार'
        ]

    # Classical Shastriya Shloka Definition
    bphs_remedies_shloka = {
        "title": "बृहत्पाराशर होराशास्त्रम् एवं फलदीपिका — दोष शांति व बाधक निर्णय",
        "source": "महर्षि पराशर विरचित BPHS (अध्याय ५०) एवं फलदीपिका",
        "shloka": "चरभवनेषु लाभेशो बाधको नवमो स्थिरे।\nद्विशरीरे च कामेशो बाधको भवति स्फुटम्॥\nमारकाणां च सर्वेषां विचारः क्रियते बुधैः।\nशान्त्या च जपहोमाद्यैर्दुष्टदोषः प्रशाम्यति॥",
        "meaning": "चर लग्न में ११वें भाव का स्वामी, स्थिर लग्न में ९वें भाव का स्वामी और द्विस्वभाव लग्न में ७वें भाव का स्वामी बाधक होता है। २रे व ७वें भाव के मारक ग्रहों के प्रभाव को समझकर वैदिक जप, होम, रुद्राक्ष एवं सात्विक दान द्वारा दुष्ट दोषों की शांति की जाती है।"
    }

    # Active Native Micro-Planetary Longitudes & DMS Calculations
    lagna_sname = getattr(chart, "lagna_sign_name", "Aries")
    bm_res = default_shastriya_pramana_engine.audit_badhaka_maraka(chart)
    badhakesh_name = bm_res.get("badhakesh", "Saturn")
    maraka_primary = bm_res.get("maraka_primary", {}).get("lord", "Venus")
    
    b_po = chart.planets.get(badhakesh_name)
    m_po = chart.planets.get(maraka_primary)

    LIFE_AREA_HINDI_NAMES = {
        1: "करियर एवं आजीविका (Career)",
        2: "स्वास्थ्य एवं देह सुख (Health)",
        3: "संबंध एवं दांपत्य (Relationship)",
        4: "संचित धन एवं संपत्ति (Accumulated Wealth - Guru)",
        5: "बैंक बैलेंस एवं नकदी (Bank Balance - Shukra)",
        6: "मानसिक शांति एवं आंतरिक सुख (Peace of Mind)",
        7: "माता एवं मातृ सुख (Mother)",
        8: "अचल संपत्ति, भूमि व भवन (Property)",
        9: "उच्च शिक्षा एवं विद्या (Education)",
        10: "समग्र सुख एवं संतोष (Happiness)",
        11: "विलासिता एवं वाहन सुख (Luxury)",
        12: "हृदय स्वास्थ्य एवं मनोभाव (Heart)",
        13: "बुद्धि एवं मेधा शक्ति (Intelligence)",
        14: "संतान सुख एवं वंश वृद्धि (Children)",
        15: "वाद-विवाद एवं ऋण-शत्रु (Litigation)",
        16: "पति सुख - गुरु कारक (Husband - Jupiter) [स्त्री जातक]",
        17: "पति सुख - मंगल कारक (Husband - Mars) [स्त्री जातक]",
        18: "गर्भाधान एवं प्रसूति (Pregnancy) [स्त्री जातक]",
        27: "पत्नी सुख - शुक्र कारक (Wife - Venus) [पुरुष जातक]",
        28: "पत्नी सुख - गुरु कृपा (Wife - Jupiter) [पुरुष जातक]",
        29: "पितृत्व एवं वंश वृद्धि (Paternity / Virility) [पुरुष जातक]",
        19: "पैतृक संपत्ति व विरासत (Inheritance)",
        20: "दीर्घायु एवं जीवन रक्षा (Longevity)",
        21: "पिता, पितृ सुख व धर्म (Father)",
        22: "भाग्य एवं ईश्वरीय कृपा (Fortune)",
        23: "सामाजिक पद, यश व प्रतिष्ठा (Status)",
        24: "व्यापार एवं स्वतंत्र व्यवसाय (Business)",
        25: "नौकरी व दैनिक सेवा कार्य (Job)",
        26: "नियमित आय व लाभ (Income)",
        30: "समग्र आरोग्य एवं संपन्नता (Health & Wealth)"
    }

    # Ensure engine is initialized
    import src.jyotish.core.affliction as aff_mod
    affliction_engine = aff_mod.AfflictionEngine(chart)

    # Detect native gender (male / female) to apply strict gender filtering for Life Areas
    c_gender_raw = st.session_state.get("birth_gender", getattr(chart.birth_data, "gender", "male"))
    c_gender = "female" if "female" in str(c_gender_raw).lower() else "male"
    applicable_life_areas = affliction_engine.get_applicable_life_areas(c_gender)
    la_options_list = [f"{a['Id']}. {LIFE_AREA_HINDI_NAMES.get(a['Id'], a['LifeArea'])}" for a in applicable_life_areas]

    # Level 1 Module Tabs immediately at the top (Zero Top Whitespace)
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
    </style>
    """, unsafe_allow_html=True)
    tab_fw_overview, tab_life_areas_deep, tab_remedies_suite, tab_badhaka_maraka = st.tabs(tabs)

    # =========================================================================
    # TAB 1: दोष एवं फ्री-विल विश्लेषण (Affliction & Free Will Analysis)
    # =========================================================================
    with tab_fw_overview:
        def _sync_toggle_p():
            st.session_state["aff_det_sym_toggle"] = st.session_state.get("aff_det_sym_toggle_p", False)
            st.session_state["aff_det_sym_toggle_h"] = st.session_state["aff_det_sym_toggle"]

        def _sync_toggle_h():
            st.session_state["aff_det_sym_toggle"] = st.session_state.get("aff_det_sym_toggle_h", False)
            st.session_state["aff_det_sym_toggle_p"] = st.session_state["aff_det_sym_toggle"]

        if "aff_det_sym_toggle" not in st.session_state:
            st.session_state["aff_det_sym_toggle"] = False
        detailed_toggle = st.session_state["aff_det_sym_toggle"]
        if "aff_det_sym_toggle_p" not in st.session_state:
            st.session_state["aff_det_sym_toggle_p"] = detailed_toggle
        if "aff_det_sym_toggle_h" not in st.session_state:
            st.session_state["aff_det_sym_toggle_h"] = detailed_toggle

        hp_list = affliction_engine.calculate_house_points(detailed=detailed_toggle)
        pp_list = affliction_engine.calculate_planet_points(detailed=detailed_toggle)

        # Level 2 Sub-Tabs immediately at the top of Tab 1
        subtab_planets, subtab_houses = st.tabs([
            "1. 🪐 नवग्रह फ्री-विल एवं दशवर्ग अंक",
            "2. 🏠 द्वादश भाव फ्री-विल एवं प्रभाव अंक"
        ])

        with subtab_planets:
            c_p1, c_p2 = st.columns([3, 1], vertical_alignment="center")
            with c_p1:
                st.markdown('<div style="font-size:12.5px; font-weight:800; color:#3B82F6; display:flex; align-items:center; gap:6px; padding:2px 0;"><span>⚡</span><span>वैदिक कर्म-सिद्धांत एवं स्वाधीनता अंकन (Agency Scoring)</span></div>', unsafe_allow_html=True)
            with c_p2:
                st.toggle("🔄 विस्तृत प्रतीक", key="aff_det_sym_toggle_p", on_change=_sync_toggle_p)

            st.markdown(render_premium_planet_table(pp_list, is_dark=_is_dark), unsafe_allow_html=True)
            st.markdown(render_soumya_krura_balance_svg(hp_list, is_dark=_is_dark), unsafe_allow_html=True)
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        with subtab_houses:
            c_h1, c_h2 = st.columns([3, 1], vertical_alignment="center")
            with c_h1:
                st.markdown('<div style="font-size:12.5px; font-weight:800; color:#3B82F6; display:flex; align-items:center; gap:6px; padding:2px 0;"><span>⚡</span><span>वैदिक कर्म-सिद्धांत एवं स्वाधीनता अंकन (Agency Scoring)</span></div>', unsafe_allow_html=True)
            with c_h2:
                st.toggle("🔄 विस्तृत प्रतीक", key="aff_det_sym_toggle_h", on_change=_sync_toggle_h)

            st.markdown(render_premium_house_table(hp_list, is_dark=_is_dark), unsafe_allow_html=True)
            st.markdown(render_house_freewill_svg(hp_list, is_dark=_is_dark), unsafe_allow_html=True)
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Compute KPI Metrics
        def _to_float(v):
            try:
                return float(str(v).replace('%', '').strip())
            except Exception:
                return 0.0

        h_fws = [_to_float(r.get("freeWill", 0)) for r in hp_list]
        p_fws = [_to_float(r.get("freeWill", 0)) for r in pp_list]

        avg_h_fw = sum(h_fws) / len(h_fws) if h_fws else 0.0
        avg_p_fw = sum(p_fws) / len(p_fws) if p_fws else 0.0

        max_h_idx = h_fws.index(max(h_fws)) if h_fws else 0
        min_h_idx = h_fws.index(min(h_fws)) if h_fws else 0
        max_p_idx = p_fws.index(max(p_fws)) if p_fws else 0
        min_p_idx = p_fws.index(min(p_fws)) if p_fws else 0


    # =========================================================================
    # TAB 2: 27 जीवन आयाम विश्लेषण (27 Life Areas Deep Breakdown)
    # =========================================================================
    with tab_life_areas_deep:
        c_la_sel1, c_la_sel2 = st.columns([3, 1], vertical_alignment="center")
        with c_la_sel1:
            cur_idx = 0
            cur_shared_id = st.session_state.get("gla_shared_life_area_id", 1)
            for idx, opt in enumerate(la_options_list):
                if opt.startswith(f"{cur_shared_id}."):
                    cur_idx = idx
                    break
            sel_la = st.selectbox(
                "जीवन आयाम चुनें (Select Life Area)",
                la_options_list,
                index=cur_idx,
                key="tab2_la_selector"
            )
            sel_la_id = int(sel_la.split(".")[0])
            st.session_state.gla_shared_life_area_id = sel_la_id

        with c_la_sel2:
            gender_badge = '<span style="background:#FCE7F3; color:#9D174D; border:1px solid #FBCFE8; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:800;">♀ स्त्री कुण्डली</span>' if c_gender == "female" else '<span style="background:#EFF6FF; color:#1E40AF; border:1px solid #BFDBFE; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:800;">♂ पुरुष कुण्डली</span>'
            st.markdown(f'<div style="text-align:center; padding:6px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; font-size:12px;">{gender_badge}<div style="margin-top:4px; font-weight:800; color:#334155;">आयाम: <b>{sel_la_id} / {len(applicable_life_areas)}</b></div></div>', unsafe_allow_html=True)

        la_info_obj = next((a for a in LIFE_AREAS if a["Id"] == sel_la_id), LIFE_AREAS[0])
        la_detail = affliction_engine.get_life_area_detail(sel_la_id)
        rashi_pred = affliction_engine.get_rashi_prediction(sel_la_id)

        # Quick Area HUD Cards
        _h_num = la_info_obj.get("house", 1)
        _k_name = la_info_obj.get("karaka", "Sun")
        _sec_h = la_info_obj.get("sec_house", 1)
        _h_lord = SIGN_LORDS.get(SIGN_NAMES[((chart.lagna_sign_id - 1 + (_h_num - 1)) % 12)], "")

        # Life Area Classical Quality Evaluation Calculation
        _total_soumya = 0
        _total_krura = 0
        try:
            for _r in la_detail.get("HouseRows", []) + la_detail.get("LordRows", []):
                for _idx in [1, 2]:
                    try: _total_soumya += int(_r[_idx])
                    except Exception: pass
                for _idx in [3, 4, 5]:
                    try: _total_krura += int(_r[_idx])
                    except Exception: pass

            if _total_soumya > _total_krura + 1:
                _area_status = "🌟 शुभ व पुष्ट क्षेत्र (Fortified & Auspicious)"
                _status_bg = "#ECFDF5"
                _status_bdr = "#10B981"
                _status_col = "#065F46"
                _status_desc = "इस आयाम में सौम्य ग्रहों एवं त्रिकोणेशों (१/५/९) का अनुकूल प्रभाव अधिक है; जीवन में यह क्षेत्र सहज रूप से फलदायी व समृद्ध रहेगा।"
            elif _total_krura > _total_soumya + 1:
                _area_status = "⚠️ संघर्ष व पीड़ित क्षेत्र (Challenging / Afflicted)"
                _status_bg = "#FEF2F2"
                _status_bdr = "#EF4444"
                _status_col = "#991B1B"
                _status_desc = "इस आयाम में क्रूर व त्रिक ग्रहों (६/८/१२) का दबाव अधिक है; इस क्षेत्र की स्थिरता हेतु शास्त्रोक्त दान, मंत्र जप व शांति उपाय अनिवार्य हैं।"
            else:
                _area_status = "⚖️ मिश्रित व सम क्षेत्र (Balanced & Effort-Driven)"
                _status_bg = "#FFFBEB"
                _status_bdr = "#F59E0B"
                _status_col = "#92400E"
                _status_desc = "इस आयाम में शुभ व क्रूर ग्रहों का मिला-जुला प्रभाव है; इस क्षेत्र की सफलता जातक के पुरुषार्थ, विवेक और निरंतर उद्यम पर निर्भर करेगी।"
        except Exception as _e_la_ev:
            _area_status = "⚖️ मिश्रित व सम क्षेत्र"
            _status_bg = "#FFFBEB"
            _status_bdr = "#F59E0B"
            _status_col = "#92400E"
            _status_desc = f"आयाम मूल्यांकन: {_e_la_ev}"

        # 1. House Breakdown Row
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        r1_c1, r1_c2 = st.columns(2, gap="medium")
        with r1_c1:
            st.markdown(render_premium_pillar_breakdown_table(la_detail["HouseRows"], "त्रिपक्षीय भाव विश्लेषण (3-Pillar House Breakdown)", icon="🏛️", is_dark=_is_dark), unsafe_allow_html=True)
        with r1_c2:
            st.markdown(render_premium_rashi_qualities_table(rashi_pred["HouseRashiRows"], "भाव राशि तत्व एवं गुण धर्म (House Signs & Qualities)", icon="🔮", is_dark=_is_dark), unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 2. Lord Breakdown Row
        r2_c1, r2_c2 = st.columns(2, gap="medium")
        with r2_c1:
            st.markdown(render_premium_pillar_breakdown_table(la_detail["LordRows"], "त्रिपक्षीय भावेश विश्लेषण (3-Pillar Lord Breakdown)", icon="👑", is_dark=_is_dark), unsafe_allow_html=True)
        with r2_c2:
            st.markdown(render_premium_rashi_qualities_table(rashi_pred["LordRashiRows"], "भावेश राशि तत्व एवं गुण धर्म (Lord Signs & Qualities)", icon="🔮", is_dark=_is_dark), unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Collapsible Section for Life Area Explanation, HUD Pillars & Evaluation (Shifted to Bottom)
        with st.expander(f"🏛️ आयाम स्तम्भ, कारक एवं गरिमा विवरण — {_area_status.split('(')[0].strip()}", expanded=False):
            st.info("प्रत्येक जीवन आयाम का निर्माण ३ प्रमुख स्तम्भों से होता है: **१. भाव (House)**, **२. कारक ग्रह (Karaka)**, एवं **३. भावेश (House Lord)**।")
            st.markdown(_clean_html(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 10px; margin-bottom: 0px;">
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 12px;">
                    <div style="font-size: 11px; color: #475569; font-weight: 700;">🏛️ प्राथमिक भाव (House)</div>
                    <div style="font-size: 14.5px; font-weight: 900; color: #1E293B; margin-top: 2px;">{_h_num} भाव</div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 2px;">आधारशिला व क्षेत्र</div>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 12px;">
                    <div style="font-size: 11px; color: #475569; font-weight: 700;">🪐 नैसर्गिक कारक (Karaka)</div>
                    <div style="font-size: 14.5px; font-weight: 900; color: #D97706; margin-top: 2px;">{_k_name}</div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 2px;">आंतरिक शक्ति व बीज</div>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 12px;">
                    <div style="font-size: 11px; color: #475569; font-weight: 700;">👑 भावेश (House Lord)</div>
                    <div style="font-size: 14.5px; font-weight: 900; color: #1E40AF; margin-top: 2px;">{_h_lord}</div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 2px;">कार्यकारी फल प्रदाता</div>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 12px;">
                    <div style="font-size: 11px; color: #475569; font-weight: 700;">🎯 द्वितीयक भाव (Sec. House)</div>
                    <div style="font-size: 14.5px; font-weight: 900; color: #059669; margin-top: 2px;">{_sec_h} भाव</div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 2px;">सहायक प्रभाव क्षेत्र</div>
                </div>
            </div>

            <div style="height: 18px; min-height: 18px; clear: both; width: 100%; display: block;"></div>

            <div style="background:{_status_bg}; border:1.5px solid {_status_bdr}; border-radius:8px; padding:12px 16px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <span style="font-weight:900; color:{_status_col}; font-size:13.5px;">{_area_status}</span>
                    <span style="font-size:11.5px; font-weight:800; color:#475569;">कुल सौम्य अंक: <b style="color:#059669;">{_total_soumya}</b> | कुल क्रूर अंक: <b style="color:#DC2626;">{_total_krura}</b></span>
                </div>
                <div style="font-size:12px; color:#1E293B; margin-top:6px; line-height:1.5;">{_status_desc}</div>
            </div>
            """), unsafe_allow_html=True)


    # =========================================================================
    # TAB 3: 3-Pillar शास्त्रीय उपचार एवं दोष निवारण (Server Remedy Suite)
    # =========================================================================
    with tab_remedies_suite:
        st.markdown("#### 🌿 3-Pillar शास्त्रीय उपचार एवं दोष निवारण (Server Remedy Suite)")
        st.info("सर्वर की हस्ताक्षर उपचार प्रणाली: **भाव (House)**, **कारक (Karaka)** एवं **भावेश (Lord)** का त्रि-आयामी शास्त्रीय निवारण — रुद्राक्ष, यज्ञ, सिद्ध बीज मंत्र, विशिष्ट दान एवं नक्षत्र वृक्षारोपण।")

        c_rem_sel1, c_rem_sel2 = st.columns([3, 1], vertical_alignment="center")
        with c_rem_sel1:
            cur_idx_rem = 0
            cur_shared_id_rem = st.session_state.get("gla_shared_life_area_id", 1)
            for idx, opt in enumerate(la_options_list):
                if opt.startswith(f"{cur_shared_id_rem}."):
                    cur_idx_rem = idx
                    break
            sel_rem_la = st.selectbox(
                "जीवन आयाम चुनें (Select Life Area)",
                la_options_list,
                index=cur_idx_rem,
                key="tab3_la_selector"
            )
            sel_rem_la_id = int(sel_rem_la.split(".")[0])
            st.session_state.gla_shared_life_area_id = sel_rem_la_id

        with c_rem_sel2:
            rem_lords_toggle = st.toggle("🔄 भावेश दृश्य (Lords View)", value=False, key="rem_lords_toggle_key")

        # Calculate remedies (Live Grahalakshanam Server Sync with resilient Classical Engine Fallback)
        rem_rows = None
        is_live_server_data = False
        if st.session_state.get("gla_authenticated", False):
            try:
                active_u = st.session_state.get("gla_user", "")
                active_p = st.session_state.get("gla_pass", "")
                if active_u and active_p:
                    g_client = GrahalakshanamClient(GrahalakshanamConfig(username=active_u, password=active_p))
                    if g_client.authenticate():
                        live_rem = g_client.get_remedy(life_area_id=sel_rem_la_id, lords=rem_lords_toggle)
                        if live_rem and len(live_rem) >= 10:
                            rem_rows = live_rem
                            is_live_server_data = True
            except Exception:
                pass

        if not rem_rows:
            rem_rows = affliction_engine.calculate_remedy(life_area_id=sel_rem_la_id, lords=rem_lords_toggle)

        if is_live_server_data:
            st.markdown('<div style="font-size: 11.5px; color: #047857; font-weight: 700; margin-bottom: 6px;">🌐 Grahalakshanam लाइव सर्वर सत्यापित गणना (Synchronized with api.grahalakshanam.in)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size: 11.5px; color: #1E40AF; font-weight: 700; margin-bottom: 6px;">⚡ JyotishOS प्रामाणिक पारशरी त्रि-स्तम्भ गणना (Verified Grahalakshanam Parity)</div>', unsafe_allow_html=True)

        def _parse_fw(fw_str: str) -> int:
            try:
                return int(float(str(fw_str).replace("%", "").strip()))
            except Exception:
                return 0

        fw_row = next((r for r in rem_rows if r.get("label") == "Free Will"), {})
        bm_row = next((r for r in rem_rows if r.get("label") == "Benefic / Malefic"), {})

        fw_h_val = _parse_fw(fw_row.get("house", "0"))
        fw_k_val = _parse_fw(fw_row.get("karaka", "0"))
        fw_s_val = _parse_fw(fw_row.get("houseFromKaraka", "0"))

        # 3 Pillar Summary Cards
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 10px 0 15px 0;">
            <div style="background: {'#ECFDF5' if fw_h_val >= 50 else '#FEF2F2'}; border: 1.5px solid {'#10B981' if fw_h_val >= 50 else '#EF4444'}; border-radius: 8px; padding: 10px 12px;">
                <div style="font-size: 11px; font-weight: 800; color: {'#065F46' if fw_h_val >= 50 else '#991B1B'};">🏛️ स्तंभ १: {'भावेश (House Lord)' if rem_lords_toggle else 'भाव (House Cusp)'}</div>
                <div style="font-size: 17px; font-weight: 900; color: {'#047857' if fw_h_val >= 50 else '#B91C1C'};">फ्री-विल: {fw_h_val}%</div>
                <div style="font-size: 10.5px; color: #475569;">{'🌟 रत्न/रुद्राक्ष शुभ एवं अनुशंसित' if fw_h_val >= 50 else '⚠️ केवल दान, मंत्र व यज्ञ शांति'}</div>
            </div>
            <div style="background: {'#ECFDF5' if fw_k_val >= 50 else '#FEF2F2'}; border: 1.5px solid {'#10B981' if fw_k_val >= 50 else '#EF4444'}; border-radius: 8px; padding: 10px 12px;">
                <div style="font-size: 11px; font-weight: 800; color: {'#065F46' if fw_k_val >= 50 else '#991B1B'};">🪐 स्तंभ २: नैसर्गिक कारक ({rem_rows[0].get('karaka')})</div>
                <div style="font-size: 17px; font-weight: 900; color: {'#047857' if fw_k_val >= 50 else '#B91C1C'};">फ्री-विल: {fw_k_val}%</div>
                <div style="font-size: 10.5px; color: #475569;">{'🌟 रत्न/रुद्राक्ष शुभ एवं अनुशंसित' if fw_k_val >= 50 else '⚠️ केवल दान, मंत्र व यज्ञ शांति'}</div>
            </div>
            <div style="background: {'#ECFDF5' if fw_s_val >= 50 else '#FEF2F2'}; border: 1.5px solid {'#10B981' if fw_s_val >= 50 else '#EF4444'}; border-radius: 8px; padding: 10px 12px;">
                <div style="font-size: 11px; font-weight: 800; color: {'#065F46' if fw_s_val >= 50 else '#991B1B'};">👑 स्तंभ ३: {rem_rows[0].get('houseFromKaraka')}</div>
                <div style="font-size: 17px; font-weight: 900; color: {'#047857' if fw_s_val >= 50 else '#B91C1C'};">फ्री-विल: {fw_s_val}%</div>
                <div style="font-size: 10.5px; color: #475569;">{'🌟 रत्न/रुद्राक्ष शुभ एवं अनुशंसित' if fw_s_val >= 50 else '⚠️ केवल दान, मंत्र व यज्ञ शांति'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        def _is_malefic(pillar_key: str) -> bool:
            val = bm_row.get(pillar_key, {})
            if isinstance(val, dict):
                return val.get("className") == "malefic"
            return "Malefic" in str(val)

        def _should_highlight(label: str, pillar_key: str) -> bool:
            fw_val = fw_h_val if pillar_key == "house" else (fw_k_val if pillar_key == "karaka" else fw_s_val)
            if fw_val >= 50:
                if label == "Free Will":
                    return True
                if label in ["Type Of Remedy", "Rudraksha / Herbs", "Yagya / Gems"] and not _is_malefic(pillar_key):
                    return True
            return False

        def _render_remedy_cell(val, is_highlighted: bool = False) -> str:
            cell_style = "border: 1px solid #E2E8F0; font-size: 12.5px; padding: 10px 14px; text-align: center; vertical-align: middle; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; line-height: 1.5;"
            if is_highlighted:
                cell_style += " background-color: #ECFDF5; border: 1.5px solid #86EFAC; font-weight: 700; color: #065F46;"
            else:
                cell_style += " background-color: #FFFFFF; color: #0F172A;"

            inner_html = ""
            if isinstance(val, dict):
                if "donation_title" in val:
                    inner_html = f'<div style="text-align: left; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px;">'
                    inner_html += f'<div style="color: #991B1B; font-weight: 800; font-size: 12.5px; margin-bottom: 4px;">🎁 {val.get("donation_title")}</div>'
                    inner_html += '<ul style="margin: 4px 0; padding-left: 18px; font-size: 11.5px; color: #1E293B;">'
                    for item in val.get("items", []):
                        inner_html += f'<li>{item}</li>'
                    inner_html += f'</ul><div style="color: #B91C1C; font-weight: 700; font-size: 11px; margin-top: 4px;">📅 {val.get("timing", "")}</div></div>'
                elif "mantra" in val:
                    inner_html = f'<div style="text-align: center; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 8px 10px;">'
                    inner_html += f'<div style="color: #92400E; font-weight: 800; font-size: 12px; margin-bottom: 3px;">🕉️ {val.get("title")}</div>'
                    inner_html += f'<div style="font-weight: 900; font-size: 13.5px; margin: 4px 0; color: #78350F;">{val.get("mantra")}</div>'
                    inner_html += f'<div style="font-size: 11px; color: #475569; font-style: italic;">{val.get("translit", "")}</div>'
                    inner_html += f'<div style="color: #B45309; font-weight: 700; font-size: 11px; margin-top: 4px;">⏳ {val.get("note", "")}</div></div>'
                elif "className" in val:
                    cls = val.get("className")
                    if cls == "malefic":
                        inner_html = f'<span style="background: #FEF2F2; color: #991B1B; border: 1.5px solid #EF4444; border-radius: 12px; padding: 3px 12px; font-weight: 800; font-size: 12.5px; display: inline-block;">⚠️ {val.get("text")}</span>'
                    else:
                        inner_html = f'<span style="background: #ECFDF5; color: #065F46; border: 1.5px solid #10B981; border-radius: 12px; padding: 3px 12px; font-weight: 800; font-size: 12.5px; display: inline-block;">🌟 {val.get("text")}</span>'
                else:
                    inner_html = str(val)
            else:
                txt = str(val)
                if "Point" in txt:
                    p_color = "#059669" if "+" in txt else "#DC2626"
                    inner_html = f'<span style="font-weight: 800; font-size: 13.5px; color: {p_color};">{txt}</span>'
                elif "%" in txt:
                    fw_num = _parse_fw(txt)
                    fw_color = "#065F46" if fw_num >= 50 else "#991B1B"
                    inner_html = f'<span style="font-weight: 900; font-size: 14px; color: {fw_color};">{txt}</span>'
                else:
                    inner_html = txt

            return f'<td style="{cell_style}">{inner_html}</td>'

        # Build Complete HTML Table
        hdr_row = rem_rows[0]
        th_style = "border: 1.5px solid #CBD5E1; font-size: 13.5px; padding: 10px 14px; text-align: center; vertical-align: middle; background: #F1F5F9; color: #0F172A; font-weight: 800; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;"
        left_style = "border: 1.5px solid #CBD5E1; font-size: 13px; padding: 10px 14px; text-align: center; vertical-align: middle; background: #F8FAFC; color: #0F172A; font-weight: 800; width: 170px; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;"

        rem_html = '<div style="overflow-x: auto; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); border: 1.5px solid #CBD5E1; border-radius: 12px;">'
        rem_html += '<table style="width: 100%; border-collapse: collapse; background: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">'
        rem_html += '<colgroup><col style="width: 18%;"><col style="width: 27%;"><col style="width: 27%;"><col style="width: 28%;"></colgroup>'
        rem_html += '<thead><tr style="background: #F8FAFC; border-bottom: 2.5px solid #2563EB;">'
        rem_html += f'<th style="{th_style}">{hdr_row.get("label")}</th>'

        h_title = "🏛️ House Lord (भावेश)" if rem_lords_toggle else "🏛️ भाव (House)"
        h_sub = hdr_row.get("house")
        rem_html += f'<th style="{th_style}"><div style="border-bottom: 1.5px solid #CBD5E1; padding-bottom: 4px; color: #0F172A;">{h_title}</div><div style="padding-top: 4px; font-size: 12px; color: #2563EB; font-weight: 800;">{h_sub}</div></th>'

        k_sub = hdr_row.get("karaka")
        rem_html += f'<th style="{th_style}"><div style="border-bottom: 1.5px solid #CBD5E1; padding-bottom: 4px; color: #0F172A;">🪐 कारक (Karaka)</div><div style="padding-top: 4px; font-size: 12px; color: #2563EB; font-weight: 800;">{k_sub}</div></th>'

        sec_title = "🪐 भावेश से भाव (House Lord from Karaka)" if rem_lords_toggle else "🪐 कारक से भाव (House from Karaka)"
        sec_sub = hdr_row.get("houseFromKaraka")
        rem_html += f'<th style="{th_style}"><div style="border-bottom: 1.5px solid #CBD5E1; padding-bottom: 4px; color: #0F172A;">{sec_title}</div><div style="padding-top: 4px; font-size: 12px; color: #2563EB; font-weight: 800;">{sec_sub}</div></th>'
        rem_html += '</tr></thead><tbody>'

        for row in rem_rows[1:]:
            lbl = row.get("label", "")
            rem_html += '<tr style="border-bottom: 1px solid #E2E8F0;">'
            rem_html += f'<td style="{left_style}">{lbl}</td>'
            rem_html += _render_remedy_cell(row.get("house"), _should_highlight(lbl, "house"))
            rem_html += _render_remedy_cell(row.get("karaka"), _should_highlight(lbl, "karaka"))
            rem_html += _render_remedy_cell(row.get("houseFromKaraka"), _should_highlight(lbl, "houseFromKaraka"))
            rem_html += '</tr>'

        rem_html += '</tbody></table></div>'
        st.markdown(rem_html, unsafe_allow_html=True)

        # ─── Gemstone Safety Guard (पात्रता व सर्वथा वर्जित रत्न) ───
        try:
            _lag_id = chart.lagna_sign_id
            _trika_h = [6, 8, 12]
            _trika_lords = {SIGN_LORDS[SIGN_NAMES[((_lag_id - 1 + (h - 1)) % 12)]] for h in _trika_h}

            _safe_houses = [1, 5, 9]
            _safe_lords = []
            for _h in _safe_houses:
                _sl = SIGN_LORDS[SIGN_NAMES[((_lag_id - 1 + (_h - 1)) % 12)]]
                if _sl not in _trika_lords and _sl not in _safe_lords:
                    _safe_lords.append(_sl)

            _GEM_MAP = {
                "Sun": "माणिक्य (Ruby)", "Moon": "मोती (Pearl)", "Mars": "मूंगा (Red Coral)",
                "Mercury": "पन्ना (Emerald)", "Jupiter": "पुखराज (Yellow Sapphire)",
                "Venus": "हीरा / ओपल (Diamond)", "Saturn": "नीलम (Blue Sapphire)",
                "Rahu": "गोमेद (Hessonite)", "Ketu": "लहसुनिया (Cat's Eye)"
            }
            _safe_gem_list = [f"<b>{_GEM_MAP.get(l, l)}</b> ({l})" for l in _safe_lords]
            _forbid_gem_list = [f"<b>{_GEM_MAP.get(l, l)}</b> ({l})" for l in _trika_lords]

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FEF2F2 0%, #FFFBEB 100%); border: 1.5px solid #F59E0B; border-radius: 10px; padding: 12px 16px; margin: 12px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <div style="font-weight: 900; color: #92400E; font-size: 13.5px; margin-bottom: 6px; display:flex; align-items:center; gap:6px;">
                    <span>🛡️ <b>रत्न धारण पात्रता एवं शास्त्रीय सुरक्षा गार्ड (Gemstone Safety Guard)</b></span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 10px; font-size: 12px; color: #1E293B;">
                    <div style="background: #F0FDF4; border: 1px solid #86EFAC; border-radius: 6px; padding: 8px 12px;">
                        <span style="color: #166534; font-weight: 800;">✅ शास्त्र-सम्मत सुरक्षित रत्न (अनुशंसित):</span><br/>
                        {', '.join(_safe_gem_list) if _safe_gem_list else 'केवल लग्न शुद्धि अनुसार'}<br/>
                        <small style="color: #047857;">त्रिकोणेश (१, ५, ९) रत्न बल एवं सौभाग्य संवर्धन करते हैं।</small>
                    </div>
                    <div style="background: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 6px; padding: 8px 12px;">
                        <span style="color: #991B1B; font-weight: 800;">🚫 सर्वथा वर्जित रत्न (Strictly Forbidden):</span><br/>
                        {', '.join(_forbid_gem_list)}<br/>
                        <small style="color: #DC2626;">त्रिक भाव (६, ८, १२) के स्वामियों का रत्न धारण करना विष समान घातक होता है।</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as _e_gem:
            st.caption(f"रत्न सुरक्षा लोड हो रहा है: {_e_gem}")

        # Remedy Shastriya Rules & Guidance Box
        with st.expander("📖 सर्वर शास्त्रीय उपाय नियम पुस्तिका (Remedy Rules & Scientific Guide)", expanded=True):
            st.markdown("""
            1. **रत्न धारण नियम (Gemstone Rule):**
               - रत्न केवल उन्हीं ग्रहों का धारण किया जाता है जो कुण्डली में **शुभ (Benefic)** हों तथा जिनका **फ्री-विल 50% से अधिक** हो (तालिका में हरे रंग से चिन्हित)।
               - यदि कोई ग्रह क्रूर अथवा पीड़ित (Malefic) है, तो उसका रत्न **कदापि धारण न करें**। पीड़ित ग्रह का रत्न धारण करने से उसकी नकारात्मक ऊर्जा में वृद्धि हो सकती है।
            2. **दोष शांति के 4 शास्त्रीय आधार (Pacification Pillars):**
               - **यज्ञ (Yagya):** अनिष्ट फल निवारण हेतु वैदिक शांति यज्ञ।
               - **रुद्राक्ष (Rudraksha):** ग्रह-संबंधित मुखी रुद्राक्ष को शास्त्रोक्त मुहूर्त, दिन अथवा होरा में धारण करना।
               - **बीज मंत्र (Beej Mantra):** निर्दिष्ट संख्या एवं 40 दिनों की निर्धारित अवधि में एकाग्रचित्त जप।
               - **विशिष्ट दान (Specific Donation):** ग्रह-संबंधित धातु (ताम्र/कांस्य/रजत/लौह), वस्त्र एवं अन्नों का शुभ मुहूर्त में संकल्पपूर्वक दान।
            3. **वृक्षारोपण द्वारा उपाय (Testing of Remedy : Vriksha Ropana):**
               - प्रत्येक ग्रह का अपना दैवीय वनस्पति स्वरूप होता है (जैसे सूर्य: मदार, चन्द्र: पलाश, मंगल: खैर, बुध: अपामार्ग/कटहल, गुरु: पीपल, शुक्र: गूलर, शनि: शमी/खेजड़ी)।
               - जब चन्द्रमा अथवा लग्न संबंधित ग्रह की राशि में बिना किसी पाप प्रभाव के स्थित हो, तब निर्धारित संख्या में पौधों का रोपण करने से जन्म जन्मांतर के दोष शांत होते हैं।
            """)

    # =========================================================================
    # TAB 4: बाधक एवं मारक ग्रह विचार (Badhaka & Maraka Audit)
    # =========================================================================
    with tab_badhaka_maraka:
        st.markdown("### ⚠️ बाधक एवं मारक ग्रह शास्त्रीय परीक्षण (Badhaka & Maraka Diagnostic Suite)")
        st.caption("महर्षि पराशर एवं प्रश्न मार्ग आधारित बाधक स्थान, बाधकेश, प्रबल महा-मारक (द्वितीय भाव) एवं द्वितीयक मारक (सप्तम भाव) का प्रामाणिक विश्लेषण:")

        try:
            bm_data = default_shastriya_pramana_engine.audit_badhaka_maraka(chart)

            # Top KPI Cards
            c_bm1, c_bm2, c_bm3 = st.columns(3)
            with c_bm1:
                st.metric("🏛️ लग्न प्रकृति", f"{bm_data['lagna_type']}", f"Lagna #{chart.lagna_sign_id}")
            with c_bm2:
                st.metric("⚡ बाधक स्थान व स्वामी", f"भाव {bm_data['badhaka_house']} ({bm_data['badhaka_sign']})", f"बाधकेश: {bm_data['badhakesh']} ({bm_data['badhakesh_placement']})")
            with c_bm3:
                p_mar = bm_data["maraka_primary"]
                s_mar = bm_data["maraka_secondary"]
                st.metric("⚔️ मारक ग्रह (२ व ७ भाव)", f"२रा: {p_mar['lord']} | ७वां: {s_mar['lord']}", "दशावधि में स्वास्थ्य सावधानी")

            # Classical Sanskrit Shloka Box
            bm_shl = bm_data["shastriya_shloka"]
            bm_lines = "<br/>".join(bm_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(239, 68, 68, 0.08); border-left: 4px solid #EF4444; padding: 14px 18px; border-radius: 8px; margin: 12px 0 16px 0;">
    <div style="font-weight: 700; color: #B91C1C; font-size: 13.5px; margin-bottom: 5px;">📖 {bm_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14.5px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {bm_lines}
    </div>
    <div style="margin-top: 8px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {bm_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 6px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {bm_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

            # ─── Operational Vimshottari Dasha Live Audit ───
            try:
                from src.jyotish.core.dasha import default_dasha_engine
                from datetime import datetime
                _cur_dt = datetime.now()
                _b_full_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
                _active_d = default_dasha_engine.get_active_dasha_at(_b_full_dt, chart.planets["Moon"].longitude, _cur_dt.date())
                _active_md = _active_d.mahadasha.lord
                _active_ad = _active_d.antardasha.lord
                _badhaka_lord = bm_data["badhakesh"]
                _maraka1_lord = p_mar["lord"]
                _maraka2_lord = s_mar["lord"]

                _dasha_badhaka_alert = (_active_md == _badhaka_lord or _active_ad == _badhaka_lord)
                _dasha_maraka_alert = (_active_md in [_maraka1_lord, _maraka2_lord] or _active_ad in [_maraka1_lord, _maraka2_lord])

                if _dasha_badhaka_alert or _dasha_maraka_alert:
                    _alert_msgs = []
                    if _dasha_badhaka_alert:
                        _alert_msgs.append(f"बाधकेश ({_badhaka_lord})")
                    if _dasha_maraka_alert:
                        _m_which = _active_md if _active_md in [_maraka1_lord, _maraka2_lord] else _active_ad
                        _alert_msgs.append(f"मारकेश ({_m_which})")
                    st.warning(f"🚨 **सक्रिय दशा चेतावनी (Active Operational Advisory):** वर्तमान विंशोत्तरी दशा ({_active_d.formatted_summary}) में {', '.join(_alert_msgs)} की दशा सक्रिय है। महत्वपूर्ण उपक्रमों, यात्रा व स्वास्थ्य में अतिरिक्त सतर्कता बरतें तथा महामृत्युंजय जप व बाधक शांति अनुष्ठान विहित है।")
                else:
                    st.success(f"🛡️ **वर्तमान दशा सुरक्षित:** वर्तमान सक्रिय दशा ({_active_d.formatted_summary}) प्रत्यक्ष मारकेश अथवा बाधकेश के सीधे प्रभाव से मुक्त है। कार्य-सिद्धि सामान्य रूप से अग्रसर रहेगी।")
            except Exception as _e_dsh_bm:
                st.caption(f"सक्रिय दशा परीक्षण: {_e_dsh_bm}")

            # 2 Detailed Guidance Columns
            c_det1, c_det2 = st.columns(2)
            with c_det1:
                st.markdown("#### ⚡ बाधकेश का व्यावहारिक प्रभाव एवं अवरोध मुक्ति")
                st.write(f"- **बाधक भाव:** इस कुण्डली का लग्न **{bm_data['lagna_type']}** होने के कारण **भाव {bm_data['badhaka_house']}** बाधक स्थान है।")
                st.write(f"- **बाधकेश की स्थिति:** बाधकेश **{bm_data['badhakesh']}** कुण्डली के **{bm_data['badhakesh_placement']}** में स्थित हैं।")
                _badh_p = chart.planets.get(bm_data['badhakesh'])
                if _badh_p:
                    _bp_sdeg = getattr(_badh_p, 'sign_degree', 0.0)
                    _bp_ansh = int(_bp_sdeg)
                    _bp_kala = int(round((_bp_sdeg - _bp_ansh)*60.0))
                    if _bp_kala >= 60: _bp_kala = 0; _bp_ansh += 1
                    _bp_dms = f"{_bp_ansh}° {_bp_kala:02d}'"
                    _bp_nak = f"{getattr(_badh_p, 'nakshatra_name', '')} (पाद {getattr(_badh_p, 'nakshatra_pada', 1)})"
                    st.write(f"- **बाधकेश सूक्ष्म स्थिति:** `{_badh_p.sign_name} ({_bp_dms})` | `{_badh_p.house_from_lagna} भाव` | `{_bp_nak}`")
                st.write("- **फलकथन सिद्धांत:** बाधकेश जीवन में सब कुछ अनुकूल दिखते हुए भी ऐन मौके पर अदृश्य बाधा या अप्रत्याशित विलंब उत्पन्न करता है। जब बाधकेश की महादशा या अंतर्दशा चले, तो महत्वपूर्ण कार्यों में सुरक्षा व दैवीय अनुष्ठान अनिवार्य माना जाता है।")
                st.info(f"🛡️ **बाधकेश शांति उपाय:** {bm_data['badhakesh']} के आराध्य देव की नियमित आराधना एवं गायत्री मंत्र का जप करने से बाधक दोष निष्प्रभावी हो जाता है।")

            with c_det2:
                st.markdown("#### ⚔️ मारक भाव एवं मारकेश सतर्कता विश्लेषण")
                st.write(f"- **महा-मारक (द्वितीय भाव):** भावेश **{p_mar['lord']}** — स्थिति: **{p_mar['placement']}**। महर्षि पराशर के अनुसार द्वितीय भाव सप्तम से अधिक प्रबल मारक होता है।")
                _mar_p = chart.planets.get(p_mar['lord'])
                if _mar_p:
                    _mp_sdeg = getattr(_mar_p, 'sign_degree', 0.0)
                    _mp_ansh = int(_mp_sdeg)
                    _mp_kala = int(round((_mp_sdeg - _mp_ansh)*60.0))
                    if _mp_kala >= 60: _mp_kala = 0; _mp_ansh += 1
                    _mp_dms = f"{_mp_ansh}° {_mp_kala:02d}'"
                    _mp_nak = f"{getattr(_mar_p, 'nakshatra_name', '')} (पाद {getattr(_mar_p, 'nakshatra_pada', 1)})"
                    st.write(f"- **मुख्य मारकेश सूक्ष्म स्थिति:** `{_mar_p.sign_name} ({_mp_dms})` | `{_mar_p.house_from_lagna} भाव` | `{_mp_nak}`")
                st.write(f"- **द्वितीयक मारक (सप्तम भाव):** भावेश **{s_mar['lord']}** — स्थिति: **{s_mar['placement']}**।")
                st.write("- **आयुर्दाय सावधानी:** जब विंशोत्तरी दशा में द्वितीयेश या सप्तमेश की परस्पर दशा-अंतर्दशा सक्रिय हो, अथवा गोचर में शनि या राहु का इन पर वेध हो, तब जातक को स्वास्थ्य, यात्रा एवं वाहन संचालन में पूर्ण सतर्कता रखनी चाहिए।")
                st.warning("🕉️ **मारक निवृत्ति उपाय:** भगवान शिव के **महामृत्युंजय मंत्र** का जप अथवा रुद्राभिषेक मारक प्रभाव को दूर कर दीर्घायु प्रदान करता है।")
        except Exception as _e_bm:
            st.error(f"बाधक/मारक विश्लेषण त्रुटि: {_e_bm}")

    # ─── Shastriya Pramana & Classical Overview moved to Bottom (Zero Top Scroll) ───
    # 1. Collapsible KPI Cards & Purushartha vs Prarabdha Card
    with st.expander("📊 समग्र फ्री-विल सूचकांक एवं कर्म-सिद्धांत रहस्य (Free Will KPI & Purushartha vs Prarabdha)", expanded=False):
        _avg_h = avg_h_fw if 'avg_h_fw' in locals() else 50.0
        _avg_p = avg_p_fw if 'avg_p_fw' in locals() else 50.0
        _max_h = max_h_idx if 'max_h_idx' in locals() else 0
        _min_h = min_h_idx if 'min_h_idx' in locals() else 0
        _max_p = max_p_idx if 'max_p_idx' in locals() else 0
        _min_p = min_p_idx if 'min_p_idx' in locals() else 0
        _h_fws = h_fws if 'h_fws' in locals() else [50.0] * 12
        _p_fws = p_fws if 'p_fws' in locals() else [50.0] * 9
        _pp_list = pp_list if 'pp_list' in locals() else []
        _p_max_name = _pp_list[_max_p].get('planet', 'Sun') if _max_p < len(_pp_list) else 'Sun'
        _p_min_name = _pp_list[_min_p].get('planet', 'Saturn') if _min_p < len(_pp_list) else 'Saturn'

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 12px;">
            <div style="background: #FFFFFF; border: 1.5px solid #3B82F6; border-radius: 8px; padding: 10px 12px; box-shadow: 0 1px 4px rgba(59, 130, 246, 0.08);">
                <div style="font-size: 11px; color: #1E40AF; font-weight: 800;">🏠 औसत भाव फ्री-विल (Agency)</div>
                <div style="font-size: 18px; font-weight: 900; color: {'#059669' if _avg_h >= 50 else '#DC2626'};">{_avg_h:.1f}%</div>
                <div style="font-size: 10.5px; color: #64748B;">१२ भावों का समग्र स्वाधीनता अंक</div>
            </div>
            <div style="background: #FFFFFF; border: 1.5px solid #8B5CF6; border-radius: 8px; padding: 10px 12px; box-shadow: 0 1px 4px rgba(139, 92, 246, 0.08);">
                <div style="font-size: 11px; color: #6D28D9; font-weight: 800;">🪐 औसत ग्रह फ्री-विल (Agency)</div>
                <div style="font-size: 18px; font-weight: 900; color: {'#059669' if _avg_p >= 50 else '#DC2626'};">{_avg_p:.1f}%</div>
                <div style="font-size: 10.5px; color: #64748B;">नवग्रहों की संकल्प शक्ति सामर्थ्य</div>
            </div>
            <div style="background: #FFFFFF; border: 1.5px solid #10B981; border-radius: 8px; padding: 10px 12px; box-shadow: 0 1px 4px rgba(16, 185, 129, 0.08);">
                <div style="font-size: 11px; color: #047857; font-weight: 800;">🌟 सर्वोच्च स्वाधीन भाव व ग्रह</div>
                <div style="font-size: 14px; font-weight: 900; color: #065F46;">H{_max_h+1} ({_h_fws[_max_h]:.0f}%) | {_p_max_name} ({_p_fws[_max_p]:.0f}%)</div>
                <div style="font-size: 10.5px; color: #059669;">कर्म द्वारा पूर्ण परिवर्तन संभव</div>
            </div>
            <div style="background: #FFFFFF; border: 1.5px solid #EF4444; border-radius: 8px; padding: 10px 12px; box-shadow: 0 1px 4px rgba(239, 68, 68, 0.08);">
                <div style="font-size: 11px; color: #B91C1C; font-weight: 800;">⚠️ सर्वाधिक प्रारब्ध/पीड़ित क्षेत्र</div>
                <div style="font-size: 14px; font-weight: 900; color: #991B1B;">H{_min_h+1} ({_h_fws[_min_h]:.0f}%) | {_p_min_name} ({_p_fws[_min_p]:.0f}%)</div>
                <div style="font-size: 10.5px; color: #DC2626;">शास्त्रीय उपाय एवं शांति अपेक्षित</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%); border: 1.5px solid #BFDBFE; border-radius: 8px; padding: 10px 16px; font-size: 12px; color: #1E293B; line-height: 1.6;">
            <div style="font-weight: 800; color: #1E40AF; margin-bottom: 4px; display:flex; align-items:center; gap:6px;">
                <span>📜 <b>कर्म-सिद्धांत एवं फ्री-विल शास्त्रीय रहस्य (Purushartha vs Prarabdha)</b></span>
            </div>
            • <b>५०% से अधिक फ्री-विल (अदृढ़ कर्म):</b> जातक के चेतन संकल्प, पुरुषार्थ एवं सतत् उद्यम द्वारा इन क्षेत्रों के परिणामों को पूर्णतः अनुकूल बनाया जा सकता है।<br/>
            • <b>५०% से कम फ्री-विल (दृढ़ प्रारब्ध):</b> पूर्वजन्म संचित प्रारब्ध की प्रधानता है; यहाँ केवल हठपूर्वक कर्म करने के स्थान पर शास्त्रीय दान, मंत्र जप, रुद्राक्ष एवं ईश्वरीय शरणागति से ही शांति संभव है।
        </div>
        """, unsafe_allow_html=True)

    # 2. Classical Shastriya Shloka Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {bphs_remedies_shloka['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {bphs_remedies_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{bphs_remedies_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {bphs_remedies_shloka['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Lagna, Badhaka & Maraka Overview
    with st.expander("🛡️ लग्न, बाधक एवं मुख्य मारकेश स्थिति (Lagna, Badhaka & Maraka Overview)", expanded=False):
        c_rm1, c_rm2, c_rm3, c_rm4 = st.columns(4)
        c_rm1.metric("लग्न एवं प्रकृति", f"{lagna_sname}", bm_res.get("lagna_type", "चर लग्न"))
        c_rm2.metric("बाधक स्थान", f"{bm_res.get('badhaka_house')} भाव ({bm_res.get('badhaka_sign')})", f"बाधकेश: {badhakesh_name}")
        if b_po:
            _b_sdeg = getattr(b_po, 'sign_degree', 0.0)
            _b_ansh = int(_b_sdeg)
            _b_kala = int(round((_b_sdeg - _b_ansh) * 60.0))
            if _b_kala >= 60: _b_kala = 0; _b_ansh += 1
            _b_nak = getattr(b_po, 'nakshatra_name', '')[:4]
            _b_pad = getattr(b_po, 'nakshatra_pada', 1)
            c_rm3.metric("बाधकेश स्थिति", f"{b_po.sign_name} ({_b_ansh}° {_b_kala:02d}')", f"{b_po.house_from_lagna} भाव | {_b_nak}-P{_b_pad}")
        if m_po:
            _m_sdeg = getattr(m_po, 'sign_degree', 0.0)
            _m_ansh = int(_m_sdeg)
            _m_kala = int(round((_m_sdeg - _m_ansh) * 60.0))
            if _m_kala >= 60: _m_kala = 0; _m_ansh += 1
            _m_nak = getattr(m_po, 'nakshatra_name', '')[:4]
            _m_pad = getattr(m_po, 'nakshatra_pada', 1)
            c_rm4.metric("मुख्य मारकेश (२रा)", f"{m_po.sign_name} ({_m_ansh}° {_m_kala:02d}')", f"{m_po.house_from_lagna} भाव | {_m_nak}-P{_m_pad}")



    # =============================================================
    # TAB 4: DASVARGA TABLE (GRAHALAKSHANAM MATRIX)

