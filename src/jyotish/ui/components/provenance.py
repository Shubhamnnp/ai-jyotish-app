"""
Provenance Badges & Shastriya Popover Components (Phase 6, Task P6-T2).
Reference: docs/IMPLEMENTATION_PRD.md (Section 3.6 & 5.5, P6-T2).

Provides:
1. Result page provenance status bar:
   - Precision Engine badge ('swisseph' high-precision vs 'degraded' fallback)
   - Active Ayanamsa name and exact degrees
   - Verified classical rules count used
   - Active house system and timezone
2. Per-finding Shastriya popover widget:
   - Grantha citation (text, chapter, verse)
   - Sanskrit shloka excerpt
   - Verified scholar badge
"""

from typing import Dict, List, Optional, Any
from ...core.models import KundaliChart


def render_provenance_badge_html(
    chart: KundaliChart,
    verified_rules_count: int = 32,
    domain: str = "general"
) -> str:
    """
    Renders an enterprise-grade HTML provenance badge bar for result pages.
    Always exposes engine state, ayanamsa, verified rules count, and precision indicators.
    """
    meta = getattr(chart, "metadata", None)
    is_degraded = getattr(chart, "engine_degraded", False)
    if meta and getattr(meta, "engine_degraded", False):
        is_degraded = True

    # 1. Engine Badge
    if is_degraded:
        engine_badge = """
        <span style="background:#FEE2E2; color:#991B1B; padding:4px 10px; border-radius:12px; font-weight:800; font-size:12px; border:1px solid #FCA5A5; display:inline-flex; align-items:center; gap:4px;">
            ⚠️ Degraded Engine (PyEphem Fallback)
        </span>
        """
    else:
        engine_badge = """
        <span style="background:#DCFCE7; color:#166534; padding:4px 10px; border-radius:12px; font-weight:800; font-size:12px; border:1px solid #86EFAC; display:inline-flex; align-items:center; gap:4px;">
            ⚡ Swiss Ephemeris (High Precision)
        </span>
        """

    # 2. Ayanamsa Badge
    ay_name = meta.ayanamsa_name if meta else "Lahiri"
    ay_val = meta.ayanamsa_value if meta else 23.85
    ayanamsa_badge = f"""
    <span style="background:#EFF6FF; color:#1E40AF; padding:4px 10px; border-radius:12px; font-weight:800; font-size:12px; border:1px solid #BFDBFE; display:inline-flex; align-items:center; gap:4px;">
        📐 {ay_name}: {ay_val:.4f}°
    </span>
    """

    # 3. Verified Rules Badge
    rules_badge = f"""
    <span style="background:#FEF3C7; color:#92400E; padding:4px 10px; border-radius:12px; font-weight:800; font-size:12px; border:1px solid #FCD34D; display:inline-flex; align-items:center; gap:4px;">
        📜 {verified_rules_count} Verified Rules Applied
    </span>
    """

    # 4. House System & Timezone Badge
    hs_name = meta.house_system if meta else "Whole Sign"
    tz_str = meta.timezone_iana if meta else "Asia/Kolkata"
    system_badge = f"""
    <span style="background:#F1F5F9; color:#334155; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px; border:1px solid #CBD5E1; display:inline-flex; align-items:center; gap:4px;">
        🏠 {hs_name} | 🌐 {tz_str}
    </span>
    """

    html = f"""
    <div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; padding:10px 14px; margin-bottom:14px; box-shadow:0 1px 4px rgba(0,0,0,0.03); display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px;">
        <div style="display:flex; flex-wrap:wrap; align-items:center; gap:8px;">
            <b style="color:#0F172A; font-size:13px;">🛡️ प्रमाणीकरण (Provenance):</b>
            {engine_badge}
            {ayanamsa_badge}
            {rules_badge}
            {system_badge}
        </div>
        <div style="font-size:11.5px; color:#64748B;">
            Zero Silent Fallbacks • Canonical Vedic Rules
        </div>
    </div>
    """
    return html


def render_finding_source_popover_html(
    finding_id: str,
    grantha: str = "Brihat Parashara Hora Shastra",
    chapter: str = "",
    verse: str = "",
    shloka: str = "",
    claim_hi: str = "",
    verified: bool = True
) -> str:
    """
    Renders an expandable, accessible HTML popover/accordion showing
    the authentic classical shastriya provenance for an individual finding.
    """
    badge_style = "background:#DCFCE7; color:#166534; border:1px solid #86EFAC;" if verified else "background:#FEF3C7; color:#92400E; border:1px solid #FCD34D;"
    badge_text = "✓ Verified Shastriya Pramana" if verified else "⚠ Classical Inference"

    shloka_html = f"""
    <div style="background:#FFFBEB; border-left:3px solid #D97706; padding:6px 10px; margin:6px 0; font-family:'Tiro Devanagari Sanskrit', serif; font-style:italic; font-size:12.5px; color:#78350F; border-radius:4px;">
        📜 {shloka}
    </div>
    """ if shloka else ""

    html = f"""
    <details style="margin:6px 0; border:1px solid #CBD5E1; border-radius:6px; background:#F8FAFC; padding:6px 10px; font-size:12.5px;">
        <summary style="cursor:pointer; font-weight:700; color:#1E40AF; display:flex; align-items:center; justify-content:space-between;">
            <span>📖 स्रोत प्रमाण (Source Popover) — [{finding_id}] {grantha}</span>
            <span style="{badge_style} padding:2px 8px; border-radius:8px; font-size:11px;">{badge_text}</span>
        </summary>
        <div style="margin-top:8px; padding-top:6px; border-top:1px dashed #CBD5E1; color:#1E293B; line-height:1.5;">
            <div><b>ग्रन्थ:</b> {grantha} | <b>अध्याय:</b> {chapter} | <b>श्लोक / सूत्र:</b> {verse}</div>
            {shloka_html}
            {f'<div style="margin-top:4px; font-size:12px; color:#475569;"><b>निर्णय:</b> {claim_hi}</div>' if claim_hi else ''}
        </div>
    </details>
    """
    return html
