


"""
JyotishOS Interactive Streamlit SaaS Platform.
Unites:
1. Deterministic Ephemeris Engine (Swiss Ephemeris & PyEphem)
2. Grahalakshanam Full Feature Parity:
   - Affliction & Free Will Analysis (12 Houses & 9 Planets with Count/Symbol toggle)
   - Dasvarga Table (D1-D60 color-coded dignity grid)
   - Vastu-Jyotish (8 Directions Mandala, chart diagnosis, Hindi/English remedies)
   - Prashna (23 Categories, Tajika Ithasala, House roles with emojis)
   - Server Cloud Sync & Benchmark (Secure multi-tenant authentication)
3. Classical 32 Rules Execution & Multi-System Consensus
4. Geocoding API & Location Resolver
5. Vedic Rishi API Cross-Validation
6. Complete Shodashavarga (D1-D60), Shadbala, Jaimini, and Upagrahas
7. Secondary Dashas: 36-Yr Yogini & Jaimini Chara Dasha
8. Varshaphal (Tajika Solar Return Annual Chart)
9. Birth Time Rectification (BTR) & Kundali Milan (36-Guna Ashtakoota & Manglik)
10. Gemini AI Astrological Sahayak & Full Printable HTML/PDF Report
"""

import sys
import os
import re
import json
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, time, datetime, timedelta, timezone
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Ensure project root, src, and current directory are in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "..", "..", ".."))
src_dir = os.path.abspath(os.path.join(curr_dir, "..", ".."))
for p in [curr_dir, src_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Evict cached core modules in Streamlit runtime so newly deployed code is always reloaded
for _mod in list(sys.modules.keys()):
    if _mod.startswith("src.jyotish"):
        del sys.modules[_mod]

from src.jyotish.core.models import (
    BirthData, GhatnaQueryInput, KundaliChart,
    VargaChart, VargaPlanetPosition
)
from src.jyotish.core.constants import SIGN_LORDS, SIGNS, SIGN_NAMES, NAKSHATRAS, GRAHAS
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.varga import VargaCalculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.shadbala import default_shadbala_calculator
from src.jyotish.core.jaimini import default_jaimini_calculator
from src.jyotish.core.upagraha import default_upagraha_calculator
from src.jyotish.core.chakras import default_sarvatobhadra_engine, default_kota_chakra_engine
from src.jyotish.core.ayurdaya import default_ayurdaya_engine
from src.jyotish.core.kp import default_kp_engine
from src.jyotish.ui.components.birth_form import (
    BIRTH_CONFIDENCE_LEVELS,
    AYANAMSA_CATALOGUE,
    HOUSE_SYSTEM_CATALOGUE,
    NODE_TYPE_CATALOGUE,
    ASTRO_SCHOOLS_CATALOGUE,
    get_historical_tz_note,
    evaluate_geo_ambiguity
)
import importlib
try:
    from src.jyotish.services.muhurta import default_muhurta_engine, default_muhurta_scanner
except ImportError:
    try:
        import src.jyotish.services.muhurta as _muh_mod
        importlib.reload(_muh_mod)
        from src.jyotish.services.muhurta import default_muhurta_engine, default_muhurta_scanner
    except Exception:
        from src.jyotish.services.muhurta import default_muhurta_engine
        default_muhurta_scanner = None

try:
    from src.jyotish.services.prescription import default_prescription_service
except ImportError:
    try:
        import src.jyotish.services.prescription as _presc_mod
        importlib.reload(_presc_mod)
        from src.jyotish.services.prescription import default_prescription_service
    except Exception:
        default_prescription_service = None

try:
    from src.jyotish.services.transit_calendar import default_transit_calendar_service
except ImportError:
    try:
        import src.jyotish.services.transit_calendar as _cal_mod
        importlib.reload(_cal_mod)
        from src.jyotish.services.transit_calendar import default_transit_calendar_service
    except Exception:
        default_transit_calendar_service = None
from src.jyotish.ui.sudarshan import (
    default_sudarshan_engine,
    SIGN_NAMES_HI,
    PLANET_NAMES_HI,
    PLANET_SHORT_HI,
    SIGN_LORDS,
)
from src.jyotish.core.affliction import AfflictionEngine, LIFE_AREAS
from src.jyotish.dasha.vimshottari import default_dasha_engine
default_vimshottari_engine = default_dasha_engine
from src.jyotish.dasha.yogini import default_yogini_engine
from src.jyotish.dasha.chara import default_chara_engine
from src.jyotish.dasha.kcd import default_kcd_engine
from src.jyotish.dasha.shoola import default_shoola_engine
from src.jyotish.services.event_query import default_event_query_service
from src.jyotish.services.prashna import default_prashna_service, PRASHNA_CATEGORIES
from src.jyotish.services.varshaphal import default_varshaphal_service
from src.jyotish.services.btr import default_btr_service, LifeEvent
from src.jyotish.services.milan import default_milan_service
from src.jyotish.services.geocoding import default_geocoding_service
from src.jyotish.services.gemology import default_gemology_service
from src.jyotish.services.vedic_rishi import default_vedic_rishi_client
from src.jyotish.services.report_generator import default_report_generator
from src.jyotish.services.master_calculator import default_master_calculator
from src.jyotish.services.vastu import VastuJyotishEngine, VASTU_DIRECTIONS
from src.jyotish.services.grahalakshanam import GrahalakshanamClient, GrahalakshanamConfig
from src.jyotish.services.folder_manager import default_folder_manager
from src.jyotish.services.auth import default_auth_service
from src.jyotish.rules.engine import default_rules_engine
from src.jyotish.ui.chart_renderer import ChartRenderer
from src.jyotish.ai.narrative import default_narrative_service
from src.jyotish.services.shastriya_pramana import default_shastriya_pramana_engine, SHASTRIYA_SHLOKAS
try:
    from src.jyotish.ui.grahalakshanam_icons import (
        ICON_NOTEPAD_B64,
        ICON_BIRTH_B64,
        ICON_FOLDER_B64,
        ICON_SAVE_B64,
        ICON_SETTINGS_B64,
        ICON_LANGUAGES_B64,
        ICON_CLOCK_B64,
        ICON_LOCATION_B64,
        ICON_THEME_B64,
        ICON_LOGOUT_B64
    )
except (ImportError, ModuleNotFoundError):
    try:
        from jyotish.ui.grahalakshanam_icons import (
            ICON_NOTEPAD_B64,
            ICON_BIRTH_B64,
            ICON_FOLDER_B64,
            ICON_SAVE_B64,
            ICON_SETTINGS_B64,
            ICON_LANGUAGES_B64,
            ICON_CLOCK_B64,
            ICON_LOCATION_B64,
            ICON_THEME_B64,
            ICON_LOGOUT_B64
        )
    except (ImportError, ModuleNotFoundError):
        from grahalakshanam_icons import (
            ICON_NOTEPAD_B64,
            ICON_BIRTH_B64,
            ICON_FOLDER_B64,
            ICON_SAVE_B64,
            ICON_SETTINGS_B64,
            ICON_LANGUAGES_B64,
            ICON_CLOCK_B64,
            ICON_LOCATION_B64,
            ICON_THEME_B64,
            ICON_LOGOUT_B64
        )

st.set_page_config(
    page_title="ब्रह्महोरा (BrahmaHora Pro) - Sovereign Vedic Astrology Workstation",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "app_theme_mode" not in st.session_state:
    st.session_state.app_theme_mode = "day"

if "theme" in st.query_params:
    _qp_th = str(st.query_params.get("theme", "")).lower().strip()
    if _qp_th in ["day", "night", "astrallis"]:
        st.session_state.app_theme_mode = _qp_th

is_astrallis_mode = (st.session_state.app_theme_mode == "astrallis")
is_night_mode = (st.session_state.app_theme_mode == "night")

# -------------------------------------------------------------
# Three-Way Precision Theme Engine: Astrallis Observatory / Cosmic Obsidian / Royal Pearl
# -------------------------------------------------------------
if is_astrallis_mode:
    theme_mode_css = """
    /* =========================================================
       Astrallis Scientific Observatory Workstation Theme
       ========================================================= */
    html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
        background-color: #050811 !important;
        color: #E2E8F0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Noto Sans", sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
    }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #EBF5E4 !important;
        background: #EBF5E4 !important;
        border-right: 1.5px solid #C8DEC0 !important;
    }
    /* ---------------------------------------------------------
       Hide Streamlit native header bars / side bars lines at top of sidebar
       --------------------------------------------------------- */
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"],
    [data-testid="stSidebar"] header,
    section[data-testid="stSidebar"] > div:first-child > div:first-child > div:first-child:empty {
        display: none !important;
        height: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    [data-testid="stSidebar"] {
        border-right: none !important;
    }
    section[data-testid="stSidebar"] {
        border-right: 1.5px solid #C8DEC0 !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        border: none !important;
        outline: none !important;
    }
    /* ===== SIDEBAR BASE TEXT — light greenish background → black text ===== */
    [data-testid="stSidebar"] > div > div,
    [data-testid="stSidebar"] .stMarkdownContainer,
    [data-testid="stSidebar"] .stMarkdownContainer > p,
    [data-testid="stSidebar"] .stMarkdownContainer > h1,
    [data-testid="stSidebar"] .stMarkdownContainer > h2,
    [data-testid="stSidebar"] .stMarkdownContainer > h3,
    [data-testid="stSidebar"] .element-container > .stMarkdownContainer > *,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] b,
    [data-testid="stSidebar"] div {
        color: #000000 !important;
    }
    /* ===== LIGHT GREENISH + YELLOWISH MIX CARDS (Pistachio Yellow Cream) ===== */
    [data-testid="stSidebar"] .sb-card-white {
        background-color: #F3FCE0 !important;
        background: linear-gradient(145deg, #F9FDE6 0%, #EBF8D3 100%) !important;
        border: 1.5px solid #BDDE85 !important;
        border-radius: 14px !important;
        margin-top: 14px !important;
        margin-bottom: 18px !important;
        padding: 13px 15px !important;
        box-shadow: 0 4px 12px rgba(110, 160, 40, 0.12) !important;
    }
    [data-testid="stSidebar"] .sb-card-white,
    [data-testid="stSidebar"] .sb-card-white * {
        color: #000000 !important;
    }
    /* ===== RADIO LABELS — Light greenish-yellow on bhagwa background ===== */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
    section[data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
    div[data-testid="stRadio"] label {
        background: linear-gradient(135deg, #F8FEEF 0%, #EDF8DB 100%) !important;
        border: 1.5px solid #B8E088 !important;
        color: #000000 !important;
        box-shadow: 0 1px 3px rgba(100, 150, 30, 0.15) !important;
        border-radius: 6px !important;
        padding: 5px 8px !important;
        margin-bottom: 4px !important;
        display: flex !important;
        align-items: center !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label span,
    section[data-testid="stSidebar"] .stRadio label p,
    section[data-testid="stSidebar"] .stRadio label span,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label span,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        color: #000000 !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover,
    section[data-testid="stSidebar"] .stRadio label:hover,
    div[data-testid="stRadio"] label:hover {
        background: #E2F5C2 !important;
        border-color: #7BBF3A !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio label:has(input:checked),
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #5C9A1E 0%, #76B828 100%) !important;
        border: 2px solid #D97706 !important;
        box-shadow: 0 3px 10px rgba(92, 154, 30, 0.35) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) span,
    div[data-testid="stRadio"] label:has(input:checked) p,
    div[data-testid="stRadio"] label:has(input:checked) span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, li, a, label, caption, strong, b, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
        color: #E2E8F0 !important;
    }
    /* ===== NUCLEAR OVERRIDE: SIDEBAR ELEMENTS ALWAYS BLACK TEXT & GREENISH-YELLOW CARDS ===== */
    /* These rules must come AFTER the global rule above to win the cascade */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] b, [data-testid="stSidebar"] strong, [data-testid="stSidebar"] i,
    [data-testid="stSidebar"] em, [data-testid="stSidebar"] a, [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] caption, [data-testid="stSidebar"] small {
        color: #000000 !important;
    }
    .sb-card-white {
        background-color: #F4FCE3 !important;
        background: linear-gradient(145deg, #F9FDE8 0%, #EBF8D8 100%) !important;
        border-color: #C3E69B !important;
    }
    .sb-card-white,
    .sb-card-white h1, .sb-card-white h2, .sb-card-white h3,
    .sb-card-white h4, .sb-card-white h5, .sb-card-white h6,
    .sb-card-white p, .sb-card-white span, .sb-card-white div,
    .sb-card-white b, .sb-card-white strong, .sb-card-white i,
    .sb-card-white em, .sb-card-white a, .sb-card-white li,
    .sb-card-white label, .sb-card-white caption, .sb-card-white small {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .sb-card-white,
    [data-testid="stSidebar"] .sb-card-white *,
    [data-testid="stSidebar"] .sb-card-white h1,
    [data-testid="stSidebar"] .sb-card-white h2,
    [data-testid="stSidebar"] .sb-card-white h3,
    [data-testid="stSidebar"] .sb-card-white p,
    [data-testid="stSidebar"] .sb-card-white span,
    [data-testid="stSidebar"] .sb-card-white div,
    [data-testid="stSidebar"] .sb-card-white b,
    [data-testid="stSidebar"] .sb-card-white strong {
        color: #000000 !important;
    }
    /* Inner sub-blocks inside cards */
    [data-testid="stSidebar"] .sb-card-white div[style*="background:"] {
        background-color: #EBF8D8 !important;
        border-color: #C3E69B !important;
    }
    [data-testid="stSidebar"] .sb-card-white span,
    [data-testid="stSidebar"] .sb-card-white b,
    [data-testid="stSidebar"] .sb-card-white div {
        color: #000000 !important;
    }

    input, textarea, select,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="input"] {
        background-color: #0A0E1A !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1.5px solid #1E293B !important;
        border-radius: 6px !important;
    }
    input:focus, textarea:focus, div[data-baseweb="input"]:focus-within {
        border-color: #00E5FF !important;
        box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.25) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #0A0E1A !important;
        color: #FFFFFF !important;
        border: 1.5px solid #1E293B !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
    header.top-nav-bar {
        background: #0A0E1A !important;
        border-color: #1E293B !important;
        border-bottom: 3px solid #00E5FF !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8) !important;
    }
    .top-nav-bar * {
        color: #E2E8F0 !important;
    }
    .app-brand-title {
        background: linear-gradient(90deg, #00E5FF 0%, #38BDF8 50%, #F59E0B 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    .app-brand-sub {
        color: #94A3B8 !important;
    }
    .active-profile-pill {
        background: #0D1322 !important;
        border: 1.5px solid #00E5FF !important;
        color: #E0F2FE !important;
    }
    .active-profile-pill * {
        color: #E0F2FE !important;
    }
    .header-sub-pill {
        background: #0D1322 !important;
        border: 1.5px solid #1E293B !important;
        color: #CBD5E1 !important;
    }
    .header-sub-pill * {
        color: #CBD5E1 !important;
    }
    .header-sub-pill b {
        color: #F8FAFC !important;
    }
    .digital-hud {
        background: #080C14 !important;
        border-color: #1E293B !important;
    }
    .digital-hud * {
        color: #E2E8F0 !important;
    }
    .hud-pill {
        background: #0D1322 !important;
        border: 1.5px solid #1E293B !important;
        color: #E2E8F0 !important;
    }
    .hud-pill b, .hud-pill strong {
        color: #00E5FF !important;
    }
    .rule-card, .vastu-card {
        background: #080C14 !important;
        border: 1.5px solid #1E293B !important;
        color: #E2E8F0 !important;
    }
    .rule-card *, .vastu-card * {
        color: #E2E8F0 !important;
    }
    div[data-testid="stExpander"] {
        background: #080C14 !important;
        border: 1.5px solid #1E293B !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
        color: #00E5FF !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
        color: #94A3B8 !important;
    }
    [data-testid="stMetric"] {
        background: #080C14 !important;
        border: 1.5px solid #1E293B !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5) !important;
    }
    [data-testid="stTable"], [data-testid="stDataFrame"], [data-testid="stTable"] *, [data-testid="stDataFrame"] * {
    [data-testid="stTable"], [data-testid="stTable"] * {
        background-color: #050811 !important;
        color: #F1F5F9 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    button[kind="secondary"] {
        background-color: #0D1322 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #1E293B !important;
    }
    button[kind="secondary"]:hover {
        background-color: #1E293B !important;
        border-color: #00E5FF !important;
    }
    /* Astrallis Tabs */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: #080C14 !important;
        border: 1.5px solid #1E293B !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        color: #94A3B8 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:hover {
        color: #F8FAFC !important;
        background: rgba(30, 41, 59, 0.7) !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #1E293B !important;
        color: #00E5FF !important;
        border: 1.5px solid #00E5FF !important;
        box-shadow: 0 2px 12px rgba(0, 229, 255, 0.25) !important;
    }
    /* Astrallis Chat */
    [data-testid="stChatMessage"] {
        background: #080C14 !important;
        border: 1.5px solid #1E293B !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stChatInput"] {
        background-color: #080C14 !important;
        border-color: #1E293B !important;
    }
    div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
    div[style*="background:#F8FAFC"], div[style*="background: #F8FAFC"],
    div[style*="background:#EFF6FF"], div[style*="background: #EFF6FF"] {
        background: #080C14 !important;
        border-color: #1E293B !important;
        color: #E2E8F0 !important;
    }
    /* Aspect Ray Glow Classes */
    .aspect-trine { stroke: #22C55E !important; stroke-width: 1.6 !important; opacity: 0.9 !important; }
    .aspect-square { stroke: #EF4444 !important; stroke-width: 1.6 !important; opacity: 0.9 !important; }
    .aspect-sextile { stroke: #06B6D4 !important; stroke-width: 1.4 !important; opacity: 0.85 !important; }
    .aspect-opp { stroke: #F43F5E !important; stroke-width: 1.8 !important; stroke-dasharray: 4,2 !important; opacity: 0.95 !important; }
    .aspect-conj { stroke: #EAB308 !important; stroke-width: 2 !important; opacity: 0.9 !important; }
    .aspect-quincunx { stroke: #A855F7 !important; stroke-width: 1.2 !important; stroke-dasharray: 2,2 !important; opacity: 0.8 !important; }
    .observatory-canvas {
        background: radial-gradient(circle at center, #060911 0%, #000000 100%) !important;
        border: 1.5px solid #1E293B !important;
        border-radius: 12px !important;
    }
    """
elif is_night_mode:
    theme_mode_css = """
    /* =========================================================
       Cosmic Vedic Obsidian Luxury Theme (Night Mode)
       ========================================================= */
    html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
        background-color: #070A12 !important;
        color: #F8FAFC !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Noto Sans", sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #EBF5E4 !important;
        background: #EBF5E4 !important;
        border-right: 1.5px solid #C8DEC0 !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
    section[data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
    div[data-testid="stRadio"] label {
        background: #111827 !important;
        border: 1.5px solid #1F2937 !important;
        color: #F1F5F9 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p,
    div[data-testid="stRadio"] label p {
        color: #F1F5F9 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover,
    section[data-testid="stSidebar"] .stRadio label:hover,
    div[data-testid="stRadio"] label:hover {
        background: #1E293B !important;
        border-color: #F59E0B !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio label:has(input:checked),
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #1E293B 0%, #1E3A8A 100%) !important;
        border: 2px solid #F59E0B !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.25) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) span,
    div[data-testid="stRadio"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, li, a, label, caption, strong, b, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
        color: #F1F5F9 !important;
    }
    input, textarea, select,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="input"] {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1.5px solid #374151 !important;
        border-radius: 8px !important;
    }
    input:focus, textarea:focus, div[data-baseweb="input"]:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #374151 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
    header.top-nav-bar {
        background: #0D1322 !important;
        border-color: #1E293B !important;
        border-bottom: 3.5px solid #F59E0B !important;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.8) !important;
    }
    .top-nav-bar * {
        color: #F8FAFC !important;
    }
    .app-brand-title {
        background: linear-gradient(90deg, #F59E0B 0%, #FBBF24 50%, #60A5FA 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    .app-brand-sub {
        color: #94A3B8 !important;
    }
    .active-profile-pill {
        background: #111827 !important;
        border: 1.5px solid #F59E0B !important;
        color: #FEF3C7 !important;
    }
    .active-profile-pill * {
        color: #FEF3C7 !important;
    }
    .header-sub-pill {
        background: #111827 !important;
        border: 1.5px solid #1F2937 !important;
        color: #E2E8F0 !important;
    }
    .header-sub-pill * {
        color: #E2E8F0 !important;
    }
    .header-sub-pill b {
        color: #F8FAFC !important;
    }
    .digital-hud {
        background: #0D1322 !important;
        border-color: #1E293B !important;
    }
    .digital-hud * {
        color: #F8FAFC !important;
    }
    .hud-pill {
        background: #111827 !important;
        border: 1.5px solid #1F2937 !important;
        color: #F8FAFC !important;
    }
    .hud-pill b, .hud-pill strong {
        color: #F59E0B !important;
    }
    .rule-card, .vastu-card {
        background: #111827 !important;
        border: 1.5px solid #1F2937 !important;
        color: #F8FAFC !important;
    }
    .rule-card *, .vastu-card * {
        color: #F8FAFC !important;
    }
    div[data-testid="stExpander"] {
        background: #111827 !important;
        border: 1.5px solid #1F2937 !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
        color: #F8FAFC !important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
        color: #94A3B8 !important;
    }
    [data-testid="stMetric"] {
        background: #111827 !important;
        border: 1.5px solid #1F2937 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stTable"], [data-testid="stDataFrame"], [data-testid="stTable"] *, [data-testid="stDataFrame"] * {
    [data-testid="stTable"], [data-testid="stTable"] * {
        background-color: #111827 !important;
        color: #FFFFFF !important;
    }
    button[kind="secondary"] {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #374151 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #1F2937 !important;
        border-color: #60A5FA !important;
    }
    div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
    div[style*="background:#F8FAFC"], div[style*="background: #F8FAFC"],
    div[style*="background:#EFF6FF"], div[style*="background: #EFF6FF"] {
        background: #111827 !important;
        border-color: #1F2937 !important;
        color: #F8FAFC !important;
    }
    .st-key-top_frozen_header_container,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.fixed-header-anchor),
    div.st-key-top_frozen_header_container > div[data-testid="stVerticalBlock"] {
        background: #070A12 !important;
        border-bottom: 2.5px solid #1E293B !important;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.85) !important;
    }
    .top-nav-bar {
        background: #0D1322 !important;
        border: 1.5px solid #1E293B !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.6) !important;
    }
    .top-nav-bar * {
        color: #F8FAFC !important;
    }
    .st-key-top_frozen_header_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #111827 !important;
        border-color: #3B82F6 !important;
        color: #F8FAFC !important;
    }
    .st-key-top_frozen_header_container button[data-testid="baseButton-secondary"],
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) button[data-testid="baseButton-secondary"] {
        background: #111827 !important;
        border-color: #374151 !important;
        color: #F8FAFC !important;
    }
    .st-key-top_frozen_header_container button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) button[data-testid="baseButton-secondary"]:hover {
        background: #1F2937 !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
    }
    .st-key-top_frozen_header_container [data-testid="stExpander"],
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) [data-testid="stExpander"] {
        background: #0D1322 !important;
        border-color: #1E293B !important;
    }
    /* Dark Mode Tabs */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: #0D1322 !important;
        border: 1.5px solid #1E293B !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        color: #94A3B8 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:hover {
        color: #F8FAFC !important;
        background: rgba(31, 41, 55, 0.6) !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #1F2937 !important;
        color: #F59E0B !important;
        border: 1.5px solid #F59E0B !important;
        box-shadow: 0 2px 12px rgba(245, 158, 11, 0.25) !important;
    }
    /* Dark Mode Chat */
    [data-testid="stChatMessage"] {
        background: #111827 !important;
        border: 1.5px solid #1F2937 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    [data-testid="stChatInput"] {
        background-color: #111827 !important;
        border-color: #374151 !important;
    }
    """
else:
    theme_mode_css = """
    /* =========================================================
       Grahalakshanam Authentic Theme (Day Mode - Royal Azure & Cyan)
       ========================================================= */
    html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
        background-color: #F8FAFC !important;
        background: #F8FAFC !important;
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Noto Sans", sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        height: 0px !important;
        min-height: 0px !important;
        max-height: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
        pointer-events: none !important;
        overflow: visible !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 900 !important;
        letter-spacing: -0.3px !important;
    }
    p, span, li, a, caption, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    strong, b {
        color: #0F172A !important;
        font-weight: 900 !important;
    }
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 0.92rem !important;
    }
    input, textarea, select, 
    div[data-baseweb="input"] input, 
    div[data-baseweb="base-input"] input,
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    input:focus, textarea:focus, div[data-baseweb="input"]:focus-within {
        border-color: #0073CF !important;
        box-shadow: 0 0 0 2px rgba(0, 115, 207, 0.2) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="select"] * {
        color: #0F172A !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #0073CF !important;
        font-weight: 900 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #475569 !important;
        font-weight: 850 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1.5px solid #00B0F0 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        box-shadow: 0 2px 8px rgba(0, 115, 207, 0.08) !important;
    }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #EBF5E4 !important;
        background: #EBF5E4 !important;
        border-right: 1.5px solid #C8DEC0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #0073CF !important;
        font-weight: 900 !important;
    }
    header.top-nav-bar {
        background: #0073CF !important;
        border-color: #00B0F0 !important;
        border-bottom: 3.5px solid #00B0F0 !important;
        box-shadow: 0 4px 18px rgba(0, 115, 207, 0.15) !important;
    }
    .top-nav-bar * {
        color: #FFFFFF !important;
    }
    .gla-info-strip {
        background: linear-gradient(90deg, #0073CF 0%, #0077B6 100%) !important;
        border: 1.5px solid #00B0F0 !important;
        color: #FFFFFF !important;
    }
    .gla-info-strip * {
        color: #FFFFFF !important;
    }
    .gla-info-strip b {
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }
    .gla-active-tag {
        color: #FFFFFF !important;
        background: #00B0F0 !important;
        border: 1px solid #38BDF8 !important;
        font-weight: 800 !important;
    }
    .gla-tile-belt {
        background: #FFFFFF !important;
        border: 1.5px solid #00B0F0 !important;
        border-radius: 8px !important;
        padding: 3px 6px !important;
    }
    .gla-btn-tile {
        background-color: #F2F2F2 !important;
        border: 2px solid #00B0F0 !important;
        border-radius: 10px !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        padding: 3px 2px !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: all 0.15s ease !important;
    }
    .gla-btn-tile:hover {
        background-color: #E0F2FE !important;
        border-color: #0073CF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 8px rgba(0, 115, 207, 0.25) !important;
    }
    .gla-tile-box.gla-active-tile .gla-btn-tile,
    .gla-btn-tile.active {
        background-color: #0073CF !important;
        border: 2px solid #00B0F0 !important;
        box-shadow: 0 0 10px rgba(0, 115, 207, 0.45) !important;
    }
    .gla-tile-box.gla-active-tile .gla-btn-tile span,
    .gla-btn-tile.active span {
        color: #FFFFFF !important;
    }
    .gla-btn-tile img {
        width: 20px !important;
        height: 20px !important;
        max-width: 20px !important;
        max-height: 20px !important;
        object-fit: contain !important;
        display: block !important;
        margin: 0 auto !important;
    }
    .gla-btn-tile span {
        color: #0077B6 !important;
        font-weight: 750 !important;
        font-size: 10px !important;
        line-height: 1.2 !important;
        margin-top: 2px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: block !important;
        text-align: center !important;
        width: 100% !important;
    }
    .digital-hud {
        background: #FFFFFF !important;
        border: 1.5px solid #00B0F0 !important;
        box-shadow: 0 2px 8px rgba(0, 115, 207, 0.08) !important;
    }
    .digital-hud * {
        color: #0F172A !important;
    }
    .hud-pill {
        background: #F0F9FF !important;
        border: 1.5px solid #BAE6FD !important;
        color: #0C4A6E !important;
    }
    .hud-pill b, .hud-pill strong {
        color: #0284C7 !important;
        font-weight: 900 !important;
    }
    .rule-card, .vastu-card {
        background: #FFFFFF !important;
        border: 1.5px solid #00B0F0 !important;
        box-shadow: 0 2px 8px rgba(0, 115, 207, 0.08) !important;
        color: #0F172A !important;
    }
    .rule-card *, .vastu-card * {
        color: #0F172A !important;
    }
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1.5px solid #00B0F0 !important;
        color: #0F172A !important;
    }
    div[data-testid="stExpander"] * {
        color: #0F172A !important;
    }
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    button[kind="secondary"] * {
        border: none !important;
        background: transparent !important;
        background-color: transparent !important;
        color: inherit !important;
        font-weight: 700 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #EFF6FF !important;
        border-color: #0073CF !important;
        color: #0073CF !important;
    }
    /* Day Mode Tabs */

    /* ═══════════════════════════════════════════════════════════════
       Distinct Luxury Gemstone Colors for Every Module Tab in Day Mode
       ═══════════════════════════════════════════════════════════════ */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: #F1F5F9 !important;
        background: #F8FAFC !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 6px !important;
        gap: 8px !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        color: #475569 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        white-space: nowrap !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }
    [data-testid="stTabs"] button[role="tab"]:hover {
        color: #0F172A !important;
        background: rgba(255, 255, 255, 0.6) !important;
    }

    /* Tab 1: Ruby Crimson (Surya) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 1) {
        background: #FFF1F2 !important;
        color: #9F1239 !important;
        border: 1.5px solid #FECDD3 !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #FFFFFF !important;
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 1):hover {
        background: #FFE4E6 !important;
        border-color: #F43F5E !important;
        color: #881337 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 1)[aria-selected="true"] {
        background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #9F1239 !important;
        box-shadow: 0 4px 14px rgba(225, 29, 72, 0.35) !important;
    }

    /* Tab 2: Sapphire Ocean Blue (Chandra) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 2) {
        background: #EFF6FF !important;
        color: #1D4ED8 !important;
        border: 1.5px solid #BFDBFE !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 2):hover {
        background: #DBEAFE !important;
        border-color: #3B82F6 !important;
        color: #1E40AF !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 2)[aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #1E40AF !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }

    /* Tab 3: Emerald Jade Green (Budha) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 3) {
        background: #ECFDF5 !important;
        color: #047857 !important;
        border: 1.5px solid #A7F3D0 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 3):hover {
        background: #D1FAE5 !important;
        border-color: #10B981 !important;
        color: #065F46 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 3)[aria-selected="true"] {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #065F46 !important;
        box-shadow: 0 4px 14px rgba(5, 150, 105, 0.35) !important;
    }

    /* Tab 4: Topaz Gold Amber (Guru) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 4) {
        background: #FEF3C7 !important;
        color: #92400E !important;
        border: 1.5px solid #FDE68A !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 4):hover {
        background: #FDE68A !important;
        border-color: #F59E0B !important;
        color: #78350F !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 4)[aria-selected="true"] {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #78350F !important;
        box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35) !important;
    }

    /* Tab 5: Coral Crimson Orange (Mangal) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 5) {
        background: #FFF7ED !important;
        color: #C2410C !important;
        border: 1.5px solid #FFEDD5 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 5):hover {
        background: #FFEDD5 !important;
        border-color: #F97316 !important;
        color: #9A3412 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 5)[aria-selected="true"] {
        background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #9A3412 !important;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.35) !important;
    }

    /* Tab 6: Amethyst Royal Purple (Rahu) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 6) {
        background: #FAF5FF !important;
        color: #6B21A8 !important;
        border: 1.5px solid #E9D5FF !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 6):hover {
        background: #F3E8FF !important;
        border-color: #A855F7 !important;
        color: #581C87 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 6)[aria-selected="true"] {
        background: linear-gradient(135deg, #7E22CE 0%, #6B21A8 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #581C87 !important;
        box-shadow: 0 4px 14px rgba(126, 34, 206, 0.35) !important;
    }

    /* Tab 7: Turquoise Cyan (Ketu) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 7) {
        background: #ECFEFF !important;
        color: #0E7490 !important;
        border: 1.5px solid #A5F3FC !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 7):hover {
        background: #CFFAFE !important;
        border-color: #06B6D4 !important;
        color: #155E75 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 7)[aria-selected="true"] {
        background: linear-gradient(135deg, #0891B2 0%, #0E7490 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #155E75 !important;
        box-shadow: 0 4px 14px rgba(8, 145, 178, 0.35) !important;
    }

    /* Tab 8: Diamond Violet Magenta (Shukra) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 8) {
        background: #FDF4FF !important;
        color: #86198F !important;
        border: 1.5px solid #F5D0FE !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 8):hover {
        background: #FAE8FF !important;
        border-color: #D946EF !important;
        color: #701A75 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 8)[aria-selected="true"] {
        background: linear-gradient(135deg, #C026D3 0%, #9333EA 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #701A75 !important;
        box-shadow: 0 4px 14px rgba(192, 38, 211, 0.35) !important;
    }

    /* Tab 9: Deep Indigo Midnight (Shani) */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 9) {
        background: #EEF2FF !important;
        color: #4338CA !important;
        border: 1.5px solid #C7D2FE !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 9):hover {
        background: #E0E7FF !important;
        border-color: #6366F1 !important;
        color: #3730A3 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 9)[aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #312E81 !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
    }

    /* Tab 10: Rose Blossom */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 10) {
        background: #FFF1F2 !important;
        color: #BE185D !important;
        border: 1.5px solid #FBCFE8 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 10):hover {
        background: #FCE7F3 !important;
        border-color: #EC4899 !important;
        color: #9D174D !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 10)[aria-selected="true"] {
        background: linear-gradient(135deg, #DB2777 0%, #BE185D 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #9D174D !important;
        box-shadow: 0 4px 14px rgba(219, 39, 119, 0.35) !important;
    }

    /* Tab 11: Vibrant Teal Ocean */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 11) {
        background: #F0FDFA !important;
        color: #0F766E !important;
        border: 1.5px solid #99F6E4 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 11):hover {
        background: #CCFBF1 !important;
        border-color: #14B8A6 !important;
        color: #115E59 !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 11)[aria-selected="true"] {
        background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #115E59 !important;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35) !important;
    }

    /* Tab 12: Warm Saffron Amber */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 12) {
        background: #FFFBEB !important;
        color: #B45309 !important;
        border: 1.5px solid #D97706 !important;
        box-shadow: 0 2px 8px rgba(217, 119, 6, 0.15) !important;
        border: 1.5px solid #FDE68A !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 12):hover {
        background: #FEF3C7 !important;
        border-color: #F59E0B !important;
        color: #92400E !important;
    }
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 12)[aria-selected="true"] {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #B45309 !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35) !important;
    }

    /* Day Mode Chat */
    [data-testid="stChatMessage"] {
        background: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
    }
    [data-testid="stChatInput"] {
        border-radius: 12px !important;
        border: 1.5px solid #CBD5E1 !important;
    }
    /* Day Mode Tables */
    [data-testid="stTable"], [data-testid="stTable"] * {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    [data-testid="stTable"] th {
        background-color: #EDF4E2 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-bottom: 2px solid #CBDCB8 !important;
    }
    [data-testid="stTable"] td {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }

    /* Day Mode Universal Contrast Enforcement - Light Yellow Greenish Backgrounds & Black Text */
    div[style*="background:#050811"], div[style*="background: #050811"],
    div[style*="background:#111827"], div[style*="background: #111827"],
    div[style*="background:#0D1322"], div[style*="background: #0D1322"],
    div[style*="background:#080C14"], div[style*="background: #080C14"],
    div[style*="background:#0A0E1A"], div[style*="background: #0A0E1A"],
    div[style*="background:#1E293B"], div[style*="background: #1E293B"],
    div[style*="background:#1F2937"], div[style*="background: #1F2937"],
    div[style*="background:#070A12"], div[style*="background: #070A12"],
    div[style*="background:#0A1628"], div[style*="background: #0A1628"],
    div[style*="background:#000000"], div[style*="background: #000000"],
    div[style*="background: black"], div[style*="background:black"] {
        background: #FFFFFF !important;
        border-color: #CBDCB8 !important;
        color: #000000 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    }
    div[style*="background:#050811"] *, div[style*="background: #050811"] *,
    div[style*="background:#111827"] *, div[style*="background: #111827"] *,
    div[style*="background:#0D1322"] *, div[style*="background: #0D1322"] *,
    div[style*="background:#080C14"] *, div[style*="background: #080C14"] *,
    div[style*="background:#0A0E1A"] *, div[style*="background: #0A0E1A"] *,
    div[style*="background:#1E293B"] *, div[style*="background: #1E293B"] *,
    div[style*="background:#1F2937"] *, div[style*="background: #1F2937"] *,
    div[style*="background:#070A12"] *, div[style*="background: #070A12"] *,
    div[style*="background:#0A1628"] *, div[style*="background: #0A1628"] *,
    div[style*="background:#000000"] *, div[style*="background: #000000"] *,
    div[style*="background: black"] *, div[style*="background:black"] * {
        color: #000000 !important;
    }

    /* Convert all white or washed-out text to solid black in Day Mode */
    div[style*="color:#FFFFFF"], div[style*="color: #FFFFFF"],
    div[style*="color:#ffffff"], div[style*="color: #ffffff"],
    div[style*="color:#F8FAFC"], div[style*="color: #F8FAFC"],
    div[style*="color:#E2E8F0"], div[style*="color: #E2E8F0"],
    span[style*="color:#FFFFFF"], span[style*="color: #FFFFFF"],
    span[style*="color:#ffffff"], span[style*="color: #ffffff"],
    span[style*="color:#F8FAFC"], span[style*="color: #F8FAFC"],
    span[style*="color:#E2E8F0"], span[style*="color: #E2E8F0"],
    b[style*="color:#FFFFFF"], b[style*="color: #FFFFFF"],
    b[style*="color:#ffffff"], b[style*="color: #ffffff"],
    strong[style*="color:#FFFFFF"], strong[style*="color: #FFFFFF"],
    strong[style*="color:#ffffff"], strong[style*="color: #ffffff"] {
        color: #000000 !important;
    }
    """

unified_css = f"""
<style>
    /* Hide Streamlit Deploy button, 3-dots menu, status widget and footer, but keep stToolbar transparent */
    .stDeployButton,
    button[data-testid="stDeployButton"],
    #MainMenu,
    [data-testid="stMainMenuTrigger"],
    footer,
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stToolbarActions"] {{
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }}
    div[data-testid="stToolbar"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none !important;
    }}
    /* Streamlit top header bar: transparent & non-blocking so sidebar toggle controls remain visible */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        border: none !important;
        padding: 0px !important;
        margin: 0px !important;
        pointer-events: none !important;
        z-index: 9999995 !important;
        height: 44px !important;
        min-height: 44px !important;
        max-height: 44px !important;
    }}

    /* Keep Sidebar Open/Close Expand Button (>>) Always Visible, High-Contrast & Clickable */
    [data-testid="stExpandSidebarButton"],
    [data-testid="stExpandSidebarButton"] button,
    button[data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button,
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] button,
    button[data-testid="stSidebarCollapsedControl"] {{
        pointer-events: auto !important;
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 10000005 !important;
        cursor: pointer !important;
        color: #F59E0B !important;
        background: transparent !important;
        border: none !important;
    }}
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="collapsedControl"] svg {{
        fill: #F59E0B !important;
        stroke: #F59E0B !important;
        color: #F59E0B !important;
        width: 18px !important;
        height: 18px !important;
    }}
    [data-testid="stExpandSidebarButton"]:hover,
    button[data-testid="stExpandSidebarButton"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover {{
        transform: scale(1.05) !important;
    }}

    .sidebar-toggle-btn {{
        background: rgba(255, 255, 255, 0.12) !important;
        color: #F59E0B !important;
        border: 1.5px solid rgba(245, 158, 11, 0.7) !important;
        border-radius: 6px !important;
        padding: 0 !important;
        width: 34px !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        font-size: 13px !important;
        font-weight: 900 !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.15s ease !important;
        user-select: none !important;
    }}
    .sidebar-toggle-btn:hover {{
        background: rgba(245, 158, 11, 0.22) !important;
        border-color: #F59E0B !important;
        color: #FDE047 !important;
        transform: scale(1.05) !important;
    }}
    .sidebar-toggle-btn:active {{
        transform: scale(0.95) !important;
    }}

    /* Clean top spacing & allow frozen sticky header */
    [data-testid="stAppViewContainer"] {{
        overflow-x: hidden !important;
        overflow-y: hidden !important;
    }}
    [data-testid="stMain"], section.main {{
        overflow-y: auto !important;
        overflow-x: hidden !important;
        position: relative !important;
        height: 100vh !important;
    }}
    /* Fit Screen & Root Viewport Optimization */
    html, body, #root, .stApp {{
        max-width: 100vw !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }}
    .block-container {{
        padding-top: 62px !important;
        padding-bottom: 2rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow: visible !important;
    }}
    @media (max-width: 1024px) {{
        .block-container {{
            padding-top: 68px !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
    }}
    @media (max-width: 768px) {{
        .block-container {{
            padding-top: 108px !important;
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            padding-bottom: 2.5rem !important;
        }}
    }}
    @media (max-width: 480px) {{
        .block-container {{
            padding-top: 118px !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }}
    }}
    div[data-testid="stVerticalBlock"] {{
        overflow: visible !important;
        gap: 0.35rem !important;
    }}
    div[data-testid="stHorizontalBlock"] {{
        gap: 0.35rem !important;
    }}
    div[data-testid="stCustomComponentV1"]:has(iframe[height="0"]),
    div.element-container:has(iframe[height="0"]),
    div.element-container:has(style) {{
        position: absolute !important;
        opacity: 0 !important;
        height: 0px !important;
        min-height: 0px !important;
        max-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }}

    /* Sidebar and collapse control must always sit above the fixed header */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarResizer"],
    [data-testid="stSidebar"] div[class*="eelgd2m"],
    [data-testid="stSidebar"] div[style*="col-resize"] {{
        z-index: 10000000 !important;
        background-color: #EBF5E4 !important;
        background: #EBF5E4 !important;
        border-right: 1.5px solid #C8DEC0 !important;
    }}
    section[data-testid="stSidebar"] *,
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] b,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {{
        color: #000000 !important;
    }}
    /* Streamlit 1.63 native sidebar expand button (>>) anchored firmly at top: 6px, left: 10px on the header line */
    button[data-testid="stExpandSidebarButton"],
    [data-testid="stExpandSidebarButton"],
    header[data-testid="stHeader"] button[data-testid="stExpandSidebarButton"],
    header[data-testid="stHeader"] [data-testid="stExpandSidebarButton"],
    header[data-testid="stHeader"] [data-testid="collapsedControl"],
    header[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"],
    div[data-testid="collapsedControl"],
    div[data-testid="stSidebarCollapsedControl"] {{
        position: fixed !important;
        top: 7px !important;
        left: 10px !important;
        width: 36px !important;
        height: 34px !important;
        min-height: 34px !important;
        max-height: 34px !important;
        margin: 0px !important;
        padding: 0px !important;
        z-index: 10000005 !important;
        pointer-events: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1.5px solid rgba(245, 158, 11, 0.75) !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35) !important;
        cursor: pointer !important;
        box-sizing: border-box !important;
        transform: none !important;
        transition: all 0.15s ease !important;
    }}
    button[data-testid="stExpandSidebarButton"]:hover,
    [data-testid="stExpandSidebarButton"]:hover {{
        background: rgba(245, 158, 11, 0.25) !important;
        border-color: #FDE047 !important;
        transform: scale(1.05) !important;
    }}
    button[data-testid="stExpandSidebarButton"] *,
    button[data-testid="stExpandSidebarButton"] span,
    button[data-testid="stExpandSidebarButton"] svg,
    [data-testid="stExpandSidebarButton"] svg {{
        fill: #F59E0B !important;
        color: #F59E0B !important;
        stroke: #F59E0B !important;
        font-size: 18px !important;
    }}

    /* Header Collapse Full-Screen Mode */
    body.header-collapsed .st-key-frozen_toolbelt_container,
    body.header-collapsed div.st-key-frozen_toolbelt_container,
    body.header-collapsed div[class*="st-key-frozen_toolbelt_container"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        overflow: hidden !important;
    }}
    body.header-collapsed .block-container {{
        padding-top: 14px !important;
    }}

    /* Frozen Locked Toolbelt - Deep Cosmic Navy Executive Palette */
    .st-key-frozen_toolbelt_container,
    div.st-key-frozen_toolbelt_container,
    div[class*="st-key-frozen_toolbelt_container"] {{
        position: fixed !important;
        top: 0px !important;
        left: 0px !important;
        right: 0px !important;
        width: 100% !important;
        z-index: 9999990 !important;
        background: linear-gradient(90deg, #0A192F 0%, #0F2744 35%, #14355A 70%, #0B1C33 100%) !important;
        background-color: #0A192F !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        padding-top: 5px !important;
        padding-bottom: 5px !important;
        padding-left: 10px !important;
        padding-right: 12px !important;
        margin: 0px !important;
        border-bottom: 2px solid #F59E0B !important;
        box-shadow: 0 4px 20px rgba(3, 8, 18, 0.6), 0 1px 6px rgba(245, 158, 11, 0.3) !important;
        box-sizing: border-box !important;
        transition: left 0.15s ease, width 0.15s ease !important;
    }}
    .st-key-frozen_toolbelt_container div[data-testid="stHorizontalBlock"],
    div[class*="st-key-frozen_toolbelt_container"] div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        min-height: 36px !important;
        height: 36px !important;
        max-height: 36px !important;
        visibility: visible !important;
        opacity: 1 !important;
        gap: 8px !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }}
    .st-key-frozen_toolbelt_container div[data-testid="column"],
    div[class*="st-key-frozen_toolbelt_container"] div[data-testid="column"] {{
        min-width: 0 !important;
        padding-left: 3px !important;
        padding-right: 3px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 36px !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin: 0 !important;
    }}
    /* Dedicated spacing for the toggle button slot so it never collides with module selectbox */
    .st-key-frozen_toolbelt_container div[data-testid="column"]:first-child,
    div[class*="st-key-frozen_toolbelt_container"] div[data-testid="column"]:first-child {{
        min-width: 52px !important;
        width: 52px !important;
        flex: 0 0 52px !important;
        margin-right: 8px !important;
    }}
    /* Header Brand Typography Protection: Pure white Hindi and radiant gold English */
    .st-key-frozen_toolbelt_container span.hdr-brand-hi,
    .st-key-frozen_toolbelt_container b.hdr-brand-hi,
    span.hdr-brand-hi,
    b.hdr-brand-hi,
    .header-brand-box .hdr-brand-hi,
    .header-title-box .hdr-brand-hi {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 900 !important;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.95), 0 0 10px rgba(245, 158, 11, 0.35) !important;
        font-size: 21px !important;
        letter-spacing: 1px !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
    }}
    .st-key-frozen_toolbelt_container span.hdr-brand-en,
    .st-key-frozen_toolbelt_container b.hdr-brand-en,
    span.hdr-brand-en,
    b.hdr-brand-en,
    .header-brand-box .hdr-brand-en,
    .header-title-box .hdr-brand-en {{
        color: #FBBF24 !important;
        -webkit-text-fill-color: #FBBF24 !important;
        font-weight: 900 !important;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.95), 0 0 10px rgba(245, 158, 11, 0.45) !important;
        font-size: 18px !important;
        letter-spacing: 2.5px !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }}
    /* Perfect vertical alignment across all header container wrappers (36px workstation height) */
    .st-key-frozen_toolbelt_container div[data-testid="column"] > div[data-testid="stVerticalBlock"],
    .st-key-frozen_toolbelt_container div[data-testid="column"] div[data-testid="stElementContainer"],
    .st-key-frozen_toolbelt_container div[data-testid="column"] div[data-testid="stMarkdownContainer"],
    .st-key-frozen_toolbelt_container div[data-testid="column"] div[data-testid="stMarkdownContainer"] p,
    .st-key-frozen_toolbelt_container div[data-testid="column"] .stMarkdown {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        margin: 0px !important;
        padding: 0px !important;
        line-height: 1 !important;
    }}
    .header-toggle-slot {{
        width: 100% !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    /* Header Open Sovereign Brand: Clean, Unboxed, Dead-Center Gold Badge (Option A) */
    .header-brand-open {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
        box-sizing: border-box !important;
        white-space: nowrap !important;
        user-select: none !important;
        cursor: default !important;
        margin: 0 auto !important;
        text-align: center !important;
    }}
    .header-brand-open svg {{
        filter: drop-shadow(0 0 6px rgba(245, 158, 11, 0.75)) drop-shadow(0 1px 3px rgba(0, 0, 0, 0.95)) !important;
        flex-shrink: 0 !important;
        display: block !important;
        margin: 0 !important;
        transition: transform 0.25s ease !important;
    }}
    .header-brand-open:hover svg {{
        transform: scale(1.06) rotate(3deg) !important;
    }}
    .header-brand-open .hdr-brand-title {{
        color: #FBBF24 !important;
        -webkit-text-fill-color: #FBBF24 !important;
        font-weight: 900 !important;
        font-size: 16.5px !important;
        letter-spacing: 2.6px !important;
        line-height: 1 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        white-space: nowrap !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.95), 0 0 12px rgba(245, 158, 11, 0.45) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    @media (max-width: 1280px) {{
        .header-brand-open .hdr-brand-title {{
            font-size: 14.5px !important;
            letter-spacing: 2px !important;
        }}
    }}
    .st-key-frozen_toolbelt_container button {{
        padding: 2px 4px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        min-height: 34px !important;
        height: 34px !important;
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }}
    .st-key-frozen_toolbelt_container button * {{
        color: #000000 !important;
        font-weight: 700 !important;
    }}
    .st-key-frozen_toolbelt_container button:hover {{
        background: #F0F7FF !important;
        border-color: #005fa8 !important;
        color: #000000 !important;
    }}
    .st-key-frozen_toolbelt_container button[kind="primary"],
    .st-key-frozen_toolbelt_container button[data-testid="baseButton-primary"] {{
        background: #E0F2FE !important;
        border: 2px solid #005fa8 !important;
        color: #000000 !important;
    }}
    .st-key-frozen_toolbelt_container button[kind="primary"] *,
    .st-key-frozen_toolbelt_container button[data-testid="baseButton-primary"] * {{
        color: #000000 !important;
    }}
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] {{
        margin: 0px !important;
        padding: 0px !important;
    }}
    /* Header selectbox trigger: 36px height, soft luxury ivory/white card with smooth golden hover (Option A) */
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] > div,
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] div[class*="e1fp86qc0"] {{
        min-height: 36px !important;
        height: 36px !important;
        max-height: 36px !important;
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        font-weight: 750 !important;
        font-size: 13px !important;
        color: #0F172A !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 2px 5px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.2s ease !important;
        box-sizing: border-box !important;
    }}
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] > div:hover,
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] > div:focus-within {{
        border-color: #F59E0B !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.35) !important;
    }}

    /* Header Selectbox Dropdown Lists: Ensure dropdown opens right attached to header in front of all layers */
    div[data-testid="stSelectboxVirtualDropdown"],
    [data-testid="stSelectboxVirtualDropdown"],
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div:has(> [data-testid="stSelectboxVirtualDropdown"]) {{
        z-index: 10000030 !important;
        border-radius: 8px !important;
        border: 1.5px solid #F59E0B !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5), 0 2px 8px rgba(245, 158, 11, 0.25) !important;
        background: #FFFFFF !important;
        max-height: min(440px, 75vh) !important;
    }}
    /* Inner listbox container: MUST scroll vertically with custom sleek scrollbar */
    div[data-testid="stSelectboxVirtualDropdown"] ul,
    div[data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
    div[data-testid="stSelectboxVirtualDropdown"] div[class*="e1fp86qc5"],
    ul[role="listbox"],
    div[role="listbox"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"] ul {{
        padding: 4px !important;
        background: #FFFFFF !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        max-height: min(400px, 70vh) !important;
        overscroll-behavior: contain !important;
        pointer-events: auto !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: thin !important;
        scrollbar-color: #CBD5E1 #F1F5F9 !important;
    }}
    /* Sleek WebKit scrollbar for listbox options */
    div[data-testid="stSelectboxVirtualDropdown"] [role="listbox"]::-webkit-scrollbar,
    div[data-testid="stSelectboxVirtualDropdown"] div[class*="e1fp86qc5"]::-webkit-scrollbar,
    div[role="listbox"]::-webkit-scrollbar,
    ul[role="listbox"]::-webkit-scrollbar,
    div[data-baseweb="popover"] ul::-webkit-scrollbar {{
        width: 8px !important;
        display: block !important;
    }}
    div[data-testid="stSelectboxVirtualDropdown"] [role="listbox"]::-webkit-scrollbar-track,
    div[data-testid="stSelectboxVirtualDropdown"] div[class*="e1fp86qc5"]::-webkit-scrollbar-track,
    div[role="listbox"]::-webkit-scrollbar-track,
    ul[role="listbox"]::-webkit-scrollbar-track,
    div[data-baseweb="popover"] ul::-webkit-scrollbar-track {{
        background: #F1F5F9 !important;
        border-radius: 4px !important;
    }}
    div[data-testid="stSelectboxVirtualDropdown"] [role="listbox"]::-webkit-scrollbar-thumb,
    div[data-testid="stSelectboxVirtualDropdown"] div[class*="e1fp86qc5"]::-webkit-scrollbar-thumb,
    div[role="listbox"]::-webkit-scrollbar-thumb,
    ul[role="listbox"]::-webkit-scrollbar-thumb,
    div[data-baseweb="popover"] ul::-webkit-scrollbar-thumb {{
        background: #CBD5E1 !important;
        border-radius: 4px !important;
        border: 1px solid #E2E8F0 !important;
    }}
    div[data-testid="stSelectboxVirtualDropdown"] [role="listbox"]::-webkit-scrollbar-thumb:hover,
    div[data-testid="stSelectboxVirtualDropdown"] div[class*="e1fp86qc5"]::-webkit-scrollbar-thumb:hover,
    div[role="listbox"]::-webkit-scrollbar-thumb:hover,
    ul[role="listbox"]::-webkit-scrollbar-thumb:hover,
    div[data-baseweb="popover"] ul::-webkit-scrollbar-thumb:hover {{
        background: #F59E0B !important;
    }}
    div[data-testid="stSelectboxVirtualDropdown"] [role="option"],
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="menu"] [role="option"] {{
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        padding: 7px 12px !important;
        border-radius: 5px !important;
        transition: background 0.12s ease, color 0.12s ease !important;
        cursor: pointer !important;
    }}
    div[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
    div[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"],
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="menu"] [role="option"]:hover {{
        background: #FEF3C7 !important;
        color: #92400E !important;
        font-weight: 800 !important;
    }}
    /* Base padding handled dynamically */
    @media (min-width: 769px) {{
        div[data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"][aria-expanded="true"]) .st-key-frozen_toolbelt_container,
        div[data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"]:not([aria-expanded="false"])) .st-key-frozen_toolbelt_container,
        div.stApp:has(section[data-testid="stSidebar"]:not([aria-expanded="false"])) .st-key-frozen_toolbelt_container {{
            padding-left: 8px !important;
            padding-right: 12px !important;
        }}
    }}

    /* Frozen Sticky Header Container (Pins to the Top of the App) */
    .st-key-top_frozen_header_container,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor),
    div[data-testid="stVerticalBlock"] > div:has([data-testid="stMarkdownContainer"] .fixed-header-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.fixed-header-anchor),
    div.st-key-top_frozen_header_container > div[data-testid="stVerticalBlock"] {{
        position: relative !important;
        background: transparent !important;
        border: none !important;
        border-bottom: none !important;
        border-radius: 0px !important;
        padding: 0px !important;
        margin-top: 0px !important;
        margin-bottom: 4px !important;
        box-shadow: none !important;
    }}

    /* Top Single-Line Navigation Header Bar (Ultra-Crisp 34px Uniform Height) */
    .st-key-top_frozen_header_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        min-height: 34px !important;
        height: 34px !important;
        max-height: 34px !important;
        border-radius: 6px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 12.5px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.15s ease !important;
    }}
    .st-key-top_frozen_header_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {{
        border-color: #2563EB !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.18) !important;
    }}
    .st-key-top_frozen_header_container button,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) button,
    .st-key-frozen_toolbelt_container button {{
        min-height: 34px !important;
        height: 34px !important;
        max-height: 34px !important;
        border-radius: 6px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        color: #1E293B !important;
        padding: 0px 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.15s ease !important;
    }}
    .st-key-top_frozen_header_container button:hover,
    .st-key-frozen_toolbelt_container button:hover {{
        background: #EFF6FF !important;
        border-color: #2563EB !important;
        color: #1D4ED8 !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.18) !important;
    }}
    .st-key-top_frozen_header_container [data-testid="stExpander"],
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) [data-testid="stExpander"] {{
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }}
    .st-key-top_frozen_header_container [data-testid="stExpander"] summary,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) [data-testid="stExpander"] summary {{
        font-weight: 800 !important;
        color: #1E293B !important;
        padding: 4px 10px !important;
        font-size: 12.5px !important;
        min-height: 30px !important;
    }}

    /* Sidebar Radio Navigation List (18 Modules as Clean, 100% Equal Size Cards) */
    [data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] .stRadio > div,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {{
        width: 100% !important;
        min-height: 48px !important;
        box-sizing: border-box !important;
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin-bottom: 2px !important;
        color: #000000 !important;
        font-weight: 700 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        display: flex !important;
        align-items: center !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div {{
        display: flex !important;
        align-items: center !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] {{
        width: 100% !important;
        flex: 1 !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p {{
        margin: 0px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #000000 !important;
        line-height: 1.3 !important;
        width: 100% !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {{
        background: #FEF3C7 !important;
        border-color: #D97706 !important;
        transform: translateY(-1px);
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {{
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
        border-color: #2563EB !important;
        border-width: 2px !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2) !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) p {{
        color: #1E3A8A !important;
        font-weight: 800 !important;
    }}

    /* Primary Calculate Button (Grahalakshanam Royal Azure Gradient) */
    button[kind="primary"] {{
        background: linear-gradient(135deg, #0073CF 0%, #0077B6 100%) !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 1.05rem !important;
        border: 1px solid #00B0F0 !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 15px rgba(0, 115, 207, 0.35) !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }}
    button[kind="primary"] * {{
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }}
    button[kind="primary"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 176, 240, 0.45) !important;
    }}

    /* Secondary Buttons */
    button[kind="secondary"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}
    button[kind="secondary"]:hover {{
        background-color: #F8FAFC !important;
        border-color: #94A3B8 !important;
    }}

    /* Unified Frozen Top Header Bar */
    .top-nav-bar {{
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 4px 12px !important;
        margin-bottom: 4px !important;
        margin-top: 0px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .nav-left {{
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }}
    .logo-circle {{
        width: 32px !important;
        height: 32px !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%) !important;
        border: 1.5px solid #D97706 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        box-shadow: 0 2px 6px rgba(217, 119, 6, 0.2) !important;
    }}
    .app-brand-title {{
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #B45309 0%, #D97706 45%, #2563EB 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        line-height: 1.15 !important;
        letter-spacing: -0.3px !important;
    }}
    .app-brand-sub {{
        font-size: 0.72rem !important;
        color: #475569 !important;
        font-weight: 700 !important;
        letter-spacing: 0.1px !important;
    }}
    .header-sub-pills-row {{
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        flex-wrap: wrap !important;
        justify-content: flex-end !important;
    }}
    .header-sub-pill {{
        background: #F8FAFC !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 2px 8px !important;
        font-size: 11px !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        white-space: nowrap !important;
    }}
    .header-sub-pill b {{
        font-weight: 800 !important;
        color: #0F172A !important;
    }}
    .pulse-dot {{
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        background: #10B981 !important;
        box-shadow: 0 0 8px #10B981 !important;
        display: inline-block !important;
    }}

    .main-header {{
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #B45309 0%, #D97706 40%, #2563EB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
    }}
    .digital-hud {{
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        padding: 8px 14px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }}
    .digital-hud * {{
        color: #000000 !important;
    }}
    .hud-grid {{
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 6px !important;
        width: 100% !important;
    }}
    @media (max-width: 992px) {{
        .hud-grid {{
            grid-template-columns: repeat(2, 1fr) !important;
        }}
    }}
    .hud-pill {{
        background: #F8FAFC !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
        font-size: 12px !important;
        color: #000000 !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        min-height: 30px !important;
        box-sizing: border-box !important;
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    .hud-pill b, .hud-pill strong {{
        color: #000000 !important;
        font-weight: 900 !important;
    }}
    .hud-pill-highlight {{
        border-color: #D97706 !important;
        background: #FEF3C7 !important;
        color: #92400E !important;
        display: inline-flex !important;
        padding: 3px 10px !important;
        font-size: 12px !important;
    }}
    .hud-pill-highlight b {{
        color: #78350F !important;
    }}
    .rule-card {{
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        padding: 14px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
    }}
    .rule-card * {{
        color: #000000 !important;
    }}

    /* Vastu-Jyotish Grid & Uniform High-Contrast Cards */
    .vastu-grid {{
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 16px !important;
        margin-top: 14px !important;
        margin-bottom: 24px !important;
        width: 100% !important;
    }}
    @media (max-width: 992px) {{
        .vastu-grid {{
            grid-template-columns: repeat(2, 1fr) !important;
        }}
    }}
    @media (max-width: 640px) {{
        .vastu-grid {{
            grid-template-columns: 1fr !important;
        }}
    }}
    .vastu-card {{
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        height: 100% !important;
        min-height: 380px !important;
        box-sizing: border-box !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }}
    .vastu-card:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08) !important;
        border-color: #94A3B8 !important;
    }}
    .vastu-card * {{
        color: #0F172A !important;
    }}

    /* High-contrast Badges */
    .own-badge {{ color: #065F46 !important; font-weight: 800; background: #D1FAE5 !important; border: 1.5px solid #10B981 !important; padding: 3px 8px; border-radius: 6px; }}
    .mool-badge {{ color: #115E59 !important; font-weight: 800; background: #CCFBF1 !important; border: 1.5px solid #14B8A6 !important; padding: 3px 8px; border-radius: 6px; }}
    .exalt-badge {{ color: #1E40AF !important; font-weight: 800; background: #DBEAFE !important; border: 1.5px solid #3B82F6 !important; padding: 3px 8px; border-radius: 6px; }}
    .deb-badge {{ color: #991B1B !important; font-weight: 800; background: #FEE2E2 !important; border: 1.5px solid #EF4444 !important; padding: 3px 8px; border-radius: 6px; }}

    /* Responsive DataFrames & Tables */
    [data-testid="stTable"], [data-testid="stDataFrame"], div:has(> table) {{
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 12px !important;
    }}
    [data-testid="stDataFrame"] * {{
        color: #000000 !important;
        font-weight: 600 !important;
    }}
    [data-testid="stTable"] table {{
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }}

    /* Segmented Luxury Tabs with Horizontal Swiping on Mobile */
    [data-testid="stTabs"] {{
        width: 100% !important;
        margin-top: 6px !important;
        margin-bottom: 14px !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: none !important;
        border-radius: 12px !important;
        padding: 5px !important;
        gap: 6px !important;
        padding: 6px !important;
        gap: 8px !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar {{
        display: none !important;
    }}
    [data-testid="stTabs"] button[role="tab"] {{
        flex-shrink: 0 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        border: 1.5px solid transparent !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        white-space: nowrap !important;
        cursor: pointer !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* Distinct Luxury Gemstone Colors for Every Module Tab */
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 1) {{ background: #FFF1F2 !important; color: #9F1239 !important; border: 1.5px solid #FECDD3 !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 1)[aria-selected="true"] {{ background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%) !important; color: #FFFFFF !important; border: 1.5px solid #9F1239 !important; box-shadow: 0 4px 14px rgba(225, 29, 72, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 2) {{ background: #EFF6FF !important; color: #1D4ED8 !important; border: 1.5px solid #BFDBFE !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 2)[aria-selected="true"] {{ background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important; color: #FFFFFF !important; border: 1.5px solid #1E40AF !important; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 3) {{ background: #ECFDF5 !important; color: #047857 !important; border: 1.5px solid #A7F3D0 !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 3)[aria-selected="true"] {{ background: linear-gradient(135deg, #059669 0%, #047857 100%) !important; color: #FFFFFF !important; border: 1.5px solid #065F46 !important; box-shadow: 0 4px 14px rgba(5, 150, 105, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 4) {{ background: #FEF3C7 !important; color: #92400E !important; border: 1.5px solid #FDE68A !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 4)[aria-selected="true"] {{ background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important; color: #FFFFFF !important; border: 1.5px solid #78350F !important; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 5) {{ background: #FFF7ED !important; color: #C2410C !important; border: 1.5px solid #FFEDD5 !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 5)[aria-selected="true"] {{ background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important; color: #FFFFFF !important; border: 1.5px solid #9A3412 !important; box-shadow: 0 4px 14px rgba(234, 88, 12, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 6) {{ background: #FAF5FF !important; color: #6B21A8 !important; border: 1.5px solid #E9D5FF !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 6)[aria-selected="true"] {{ background: linear-gradient(135deg, #7E22CE 0%, #6B21A8 100%) !important; color: #FFFFFF !important; border: 1.5px solid #581C87 !important; box-shadow: 0 4px 14px rgba(126, 34, 206, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 7) {{ background: #ECFEFF !important; color: #0E7490 !important; border: 1.5px solid #A5F3FC !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 7)[aria-selected="true"] {{ background: linear-gradient(135deg, #0891B2 0%, #0E7490 100%) !important; color: #FFFFFF !important; border: 1.5px solid #155E75 !important; box-shadow: 0 4px 14px rgba(8, 145, 178, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 8) {{ background: #FDF4FF !important; color: #86198F !important; border: 1.5px solid #F5D0FE !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 8)[aria-selected="true"] {{ background: linear-gradient(135deg, #C026D3 0%, #9333EA 100%) !important; color: #FFFFFF !important; border: 1.5px solid #701A75 !important; box-shadow: 0 4px 14px rgba(192, 38, 211, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 9) {{ background: #EEF2FF !important; color: #4338CA !important; border: 1.5px solid #C7D2FE !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 9)[aria-selected="true"] {{ background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important; color: #FFFFFF !important; border: 1.5px solid #312E81 !important; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 10) {{ background: #FFF1F2 !important; color: #BE185D !important; border: 1.5px solid #FBCFE8 !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 10)[aria-selected="true"] {{ background: linear-gradient(135deg, #DB2777 0%, #BE185D 100%) !important; color: #FFFFFF !important; border: 1.5px solid #9D174D !important; box-shadow: 0 4px 14px rgba(219, 39, 119, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 11) {{ background: #F0FDFA !important; color: #0F766E !important; border: 1.5px solid #99F6E4 !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 11)[aria-selected="true"] {{ background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%) !important; color: #FFFFFF !important; border: 1.5px solid #115E59 !important; box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35) !important; }}

    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 12) {{ background: #FFFBEB !important; color: #B45309 !important; border: 1.5px solid #FDE68A !important; }}
    [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 12)[aria-selected="true"] {{ background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important; color: #FFFFFF !important; border: 1.5px solid #B45309 !important; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35) !important; }}

    /* Responsive SVG & Kundali Charts Auto-Scaling (Scoped strictly to Kundali SVGs, never global svg or Vega-Lite charts) */
    .kundali-chart svg, .chart-container svg, .observatory-canvas svg, div:has(> svg.kundali-svg) svg, svg.kundali-svg {{
        width: 80% !important;
        max-width: 80% !important;
        height: auto !important;
        aspect-ratio: 1 / 1 !important;
        display: block !important;
        margin: 0 auto !important;
    }}
    div:has(> svg.kundali-svg), .chart-container, .kundali-chart, div[data-testid="stImage"] img {{
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }}

    /* Luxury Card-styled Expanders */
    div[data-testid="stExpander"] {{
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        overflow: hidden !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stExpander"]:hover {{
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
    }}
    div[data-testid="stExpander"] summary {{
        padding: 10px 14px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }}

    /* Custom Modern Slim Scrollbars */
    ::-webkit-scrollbar {{
        width: 6px !important;
        height: 6px !important;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent !important;
    }}
    ::-webkit-scrollbar-thumb {{
        background: rgba(148, 163, 184, 0.4) !important;
        border-radius: 4px !important;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(148, 163, 184, 0.7) !important;
    }}

    /* =========================================================
       ⏱️ Quick Time Stepper & Shastriya Rules HUD (Auto-Adjusting Responsive Grid)
       ========================================================= */
    div[data-testid="column"]:has(div[class*="st-key-ts_btn_"]) {{
        min-width: 0 !important;
        flex: 1 1 0% !important;
        padding-left: 1px !important;
        padding-right: 1px !important;
    }}
    div[class*="st-key-ts_btn_"] {{
        width: 100% !important;
    }}
    div[class*="st-key-ts_btn_"] button {{
        width: 100% !important;
        min-width: 0 !important;
        padding: 2px 1px !important;
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        border-radius: 7px !important;
        box-sizing: border-box !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #1E293B !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        margin: 0 !important;
        transition: all 0.15s ease-in-out !important;
    }}
    div[class*="st-key-ts_btn_"] button:hover {{
        border-color: #F59E0B !important;
        background: #FFFBEB !important;
        color: #B45309 !important;
        box-shadow: 0 2px 5px rgba(245, 158, 11, 0.2) !important;
    }}
    div[class*="st-key-ts_btn_"] button p {{
        font-size: 11px !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
        letter-spacing: -0.2px !important;
    }}
    div[class*="st-key-ts_btn_now"] button {{
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        border: 1.5px solid #0284C7 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3) !important;
    }}
    div[class*="st-key-ts_btn_now"] button:hover {{
        background: linear-gradient(135deg, #0369A1 0%, #075985 100%) !important;
        border-color: #0369A1 !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 8px rgba(2, 132, 199, 0.45) !important;
    }}
    div[class*="st-key-ts_btn_now"] button p {{
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }}
    div[class*="st-key-global_open_rules_bank_btn"] {{
        width: 100% !important;
    }}
    div[class*="st-key-global_open_rules_bank_btn"] button {{
        width: 100% !important;
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        padding: 2px 6px !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #6D28D9 !important;
        box-shadow: 0 2px 6px rgba(124, 58, 237, 0.25) !important;
        margin: 0 !important;
        transition: all 0.15s ease-in-out !important;
    }}
    div[class*="st-key-global_open_rules_bank_btn"] button:hover {{
        background: linear-gradient(135deg, #6D28D9 0%, #5B21B6 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(124, 58, 237, 0.35) !important;
    }}
    div[class*="st-key-global_open_rules_bank_btn"] button p {{
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 12px !important;
        white-space: nowrap !important;
    }}

    /* =========================================================
       Comprehensive Multi-Device Responsiveness (Mobile, Tablet, Desktop)
       ========================================================= */

    /* Mobile Phones (max-width: 768px) */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            padding-top: 108px !important;
            padding-bottom: 2.5rem !important;
        }}
        .main-header {{
            font-size: 1.5rem !important;
            letter-spacing: -0.3px !important;
        }}
        .app-brand-title {{
            font-size: 1.05rem !important;
        }}
        .top-nav-bar {{
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 6px !important;
            padding: 6px 8px !important;
        }}
        .nav-left {{
            justify-content: space-between !important;
            width: 100% !important;
        }}
        .header-sub-pills-row {{
            width: 100% !important;
            justify-content: flex-start !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
            scrollbar-width: none !important;
            padding-bottom: 2px !important;
        }}
        .header-sub-pills-row::-webkit-scrollbar {{
            display: none !important;
        }}
        .header-sub-pill {{
            font-size: 10.5px !important;
            padding: 2px 6px !important;
        }}
        .hud-grid {{
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 4px !important;
        }}
        .hud-pill {{
            font-size: 11px !important;
            min-height: 28px !important;
            padding: 3px 6px !important;
        }}
        .vastu-grid {{
            grid-template-columns: 1fr !important;
            gap: 12px !important;
        }}
        /* Mobile Touch Targets (Min 44px for easy thumb tapping) */
        button[kind="primary"], button[kind="secondary"], .sidebar-toggle-btn {{
            min-height: 44px !important;
        }}
        [data-testid="stTabs"] button[role="tab"] {{
            padding: 10px 14px !important;
            font-size: 12.5px !important;
            min-height: 42px !important;
        }}
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {{
            min-height: 44px !important;
            padding: 10px 12px !important;
        }}
        /* Metric cards stacking */
        [data-testid="stMetric"] {{
            padding: 10px 12px !important;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.3rem !important;
        }}
    }}

    /* Tablets & iPads (769px - 1024px) */
    @media (min-width: 769px) and (max-width: 1024px) {{
        .block-container {{
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }}
        .main-header {{
            font-size: 1.85rem !important;
        }}
        .hud-grid {{
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 6px !important;
        }}
        .vastu-grid {{
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 14px !important;
        }}
    }}

    /* Large Desktops (1025px+) */
    @media (min-width: 1025px) {{
        .hud-grid {{
            grid-template-columns: repeat(4, 1fr) !important;
        }}
        .vastu-grid {{
            grid-template-columns: repeat(3, 1fr) !important;
        }}
    }}

    /* Google Translate Clean Styling - Zero Distortion */
    .goog-te-banner-frame.skiptranslate, .goog-te-gadget, #goog-gt-tt, .goog-te-spinner-pos, iframe.goog-te-banner-frame {{
        display: none !important;
        visibility: hidden !important;
    }}
    body {{
        top: 0px !important;
    }}
    #google_translate_element {{
        display: none !important;
    }}
    .skiptranslate iframe {{
        display: none !important;
    }}
    .goog-tooltip, .goog-tooltip:hover {{
        display: none !important;
    }}
    .goog-text-highlight {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    #software-lang-select {{
        border: none !important;
        background: transparent !important;
        font-weight: 800 !important;
        font-size: 11.5px !important;
        color: #166534 !important;
        cursor: pointer !important;
        outline: none !important;
    }}
    #software-lang-select option {{
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-weight: 700 !important;
    }}

    /* Mobile & PWA Responsive Optimization */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            padding-top: 108px !important;
        }}
        .top-nav-bar {{
            padding: 8px 10px !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
        }}
        .app-brand-title {{
            font-size: 1.1rem !important;
        }}
        .active-profile-pill, .header-sub-pill, .hud-pill {{
            font-size: 0.72rem !important;
            padding: 3px 6px !important;
        }}
        /* Mobile touch button sizing */
        button, .stButton > button, [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {{
            min-height: 42px !important;
            touch-action: manipulation !important;
        }}
        /* Fluid column stacking on mobile so charts, tables and cards never squish or overlap */
        div[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:not(:has(div[class*="st-key-ts_btn_"])) {{
            flex-direction: column !important;
            gap: 12px !important;
        }}
        div[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:not(:has(div[class*="st-key-ts_btn_"])) > div[data-testid="column"] {{
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
            padding: 0 !important;
            margin-bottom: 6px !important;
        }}
        /* Keep Top Frozen Header Bar in a clean compact flex row across mobile */
        .st-key-frozen_toolbelt_container div[data-testid="stHorizontalBlock"],
        div[class*="st-key-frozen_toolbelt_container"] div[data-testid="stHorizontalBlock"] {{
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 4px !important;
            overflow-x: visible !important;
            overflow-y: visible !important;
        }}
        .st-key-frozen_toolbelt_container div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
        div[class*="st-key-frozen_toolbelt_container"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
            width: auto !important;
            min-width: 48% !important;
            flex: 1 1 48% !important;
            margin-bottom: 0px !important;
            padding: 0 2px !important;
        }}
        /* Prevent horizontal overflow on tables and charts */
        div[data-testid="stHorizontalBlock"]:not(.st-key-frozen_toolbelt_container div[data-testid="stHorizontalBlock"]) {{
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }}
    }}

    /* Server Component Toolbar & 10-Tile Suite (Compact Screen Fit & Ultra-Slim 48px) */
    div[data-testid="column"]:has(.gla-tile-box) {{
        min-height: 52px !important;
        height: 52px !important;
        padding: 0 !important;
        margin: 0 !important;
        margin: 0 0 6px 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }}
    div[data-testid="column"]:has(.gla-tile-box) > div[data-testid="stVerticalBlock"] {{
        gap: 0 !important;
        height: 52px !important;
        min-height: 52px !important;
    }}
    div[data-testid="column"]:has(.gla-tile-box) div[data-testid="stElementContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
        height: 50px !important;
        min-height: 50px !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.gla-tile-box) {{
        min-height: 52px !important;
        margin-top: 4px !important;
        margin-bottom: 12px !important;
        position: relative !important;
        clear: both !important;
    }}
    .gla-tile-box {{
        width: 100% !important;
        height: 48px !important;
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
    }}
    .gla-btn-tile {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 48px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        padding: 3px 2px !important;
        box-sizing: border-box !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease-in-out !important;
        text-align: center !important;
        margin: 0 auto !important;
    }}
    div[data-testid="column"]:has(.gla-tile-box):hover .gla-btn-tile,
    .gla-btn-tile:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 8px rgba(22, 163, 74, 0.2) !important;
        background-color: #F0FDF4 !important;
        border-color: #16A34A !important;
    }}
    .gla-tile-box.gla-active-tile .gla-btn-tile,
    .gla-btn-tile.active {{
        background-color: #FEF3C7 !important;
        border: 2px solid #D97706 !important;
        box-shadow: 0 0 10px rgba(217, 119, 6, 0.4) !important;
    }}
    .gla-btn-tile img {{
        width: 20px !important;
        height: 20px !important;
        max-width: 20px !important;
        max-height: 20px !important;
        object-fit: contain !important;
        display: block !important;
        margin: 0 auto !important;
    }}
    .gla-btn-tile span {{
        font-size: 10px !important;
        font-weight: 750 !important;
        color: #0F172A !important;
        line-height: 1.2 !important;
        margin-top: 2px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }}
    .gla-info-strip {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #0073CF 0%, #0077B6 100%);
        color: #FFFFFF;
        padding: 5px 12px;
        border-radius: 8px;
        border: 1.5px solid #00B0F0;
        font-size: 12px;
        font-weight: 700;
        margin-top: 0px;
        margin-bottom: 4px;
        box-shadow: 0 2px 8px rgba(0, 115, 207, 0.15);
    }}
    .gla-info-strip b {{
        color: #FFFFFF;
    }}
    .gla-info-strip * {{
        color: #FFFFFF;
    }}
    .gla-tile-box {{
        position: relative;
        width: 48px;
        height: 48px;
        margin: 0 auto;
    }}
    /* Toolbelt Row: Ensure full height and clean spacing */
    div[data-testid="stHorizontalBlock"]:has(.gla-tile-box) {{
        padding: 0 2px !important;
    }}
    /* 🏛️ Authentic Grahalakshanam Workstation Styling */
    .pl-workstation-left {{
        background: #FFFFFF !important;
        border: 1.5px solid #00B0F0 !important;
        border-radius: 8px !important;
        padding: 6px !important;
        box-shadow: 0 2px 8px rgba(0, 115, 207, 0.08) !important;
    }}
    .pl-box-header {{
        background: linear-gradient(180deg, #0073CF 0%, #005FAD 100%) !important;
        color: #FFFFFF !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        padding: 5px 10px !important;
        border-radius: 6px 6px 0 0 !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 0px !important;
    }}
    .pl-box-header,
    .pl-box-header *,
    .pl-box-header span,
    .pl-box-header b {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}
    .pl-tab-pill-bar {{
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 4px !important;
        margin-bottom: 8px !important;
        padding: 4px !important;
        background: #F0F9FF !important;
        border: 1px solid #BAE6FD !important;
        border-radius: 6px !important;
    }}

    
    /* Universal Card, Expanders, Metrics & Table Anti-Overlap Alignment */
    .rule-card, .vastu-card, .digital-hud, div[data-testid="stMetric"],
    div[data-testid="stExpander"], div[style*="border-left"] {{
        box-sizing: border-box !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
        word-break: normal !important;
    }}
    /* ═════════════════════════════════════════════════════════════════
       Ultra-Crisp Professional Auth Panel & Login Buttons Styling
       ═════════════════════════════════════════════════════════════════ */
    .auth-card-wrapper {{
        max-width: 440px !important;
        width: 100% !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }}
    div[class*="st-key-link_goto_"] button,
    div[class*="st-key-back_to_login_"] button,
    div[class*="st-key-demo_btn_"] button,
    div[class*="st-key-btn_send_otp"] button {{
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        min-height: 38px !important;
        height: 38px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease !important;
        padding: 0 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    div[class*="st-key-link_goto_"] button:hover,
    div[class*="st-key-back_to_login_"] button:hover,
    div[class*="st-key-demo_btn_"] button:hover,
    div[class*="st-key-btn_send_otp"] button:hover {{
        background: #EFF6FF !important;
        background-color: #EFF6FF !important;
        border-color: #2563EB !important;
        color: #1D4ED8 !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.18) !important;
    }}
    div[class*="st-key-link_goto_"] button *,
    div[class*="st-key-back_to_login_"] button *,
    div[class*="st-key-demo_btn_"] button *,
    div[class*="st-key-btn_send_otp"] button * {{
        border: none !important;
        background: transparent !important;
        background-color: transparent !important;
        color: inherit !important;
        font-weight: 700 !important;
    }}
    @media (max-width: 768px) {{
        div[data-testid="column"]:empty {{
            display: none !important;
            height: 0px !important;
            min-height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
        }}
        .auth-top-bar {{
            justify-content: center !important;
            margin-bottom: 12px !important;
        }}
    }}

    {theme_mode_css}
</style>
"""

st.markdown(unified_css, unsafe_allow_html=True)

# Client-Side Sidebar Toggle Bridge, Multi-Language Engine & Live GPS Resolver
cur_active_theme = st.session_state.get("app_theme_mode", "day")
client_bridge_code = """
<script>
(function() {
    function setupSidebarToggle() {
        try {
            const parentDoc = window.parent.document;
            if (!parentDoc) return;
            
            const toggleBtns = parentDoc.querySelectorAll('.sidebar-toggle-btn, #sidebar-toggle-action-btn');
            toggleBtns.forEach(function(btn) {
                if (!btn.dataset.bound) {
                    btn.dataset.bound = "true";
                    btn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        doToggle();
                    });
                }
            });

            // Direct capture-phase click handler on parent document for the Sidebar button
            if (!parentDoc.dataset.sidebarBound) {
                parentDoc.dataset.sidebarBound = "true";
                parentDoc.addEventListener('click', function(e) {
                    const btn = e.target.closest('button');
                    if (btn && (btn.innerText.includes('Sidebar') || btn.innerText.includes('☰') || (btn.getAttribute('key') && btn.getAttribute('key').includes('sidebar')))) {
                        if (btn.closest('.st-key-frozen_toolbelt_container') || btn.innerText.includes('Sidebar')) {
                            const success = doToggle();
                            if (success) {
                                e.preventDefault();
                                e.stopPropagation();
                            }
                        }
                    }
                }, true);
            }
            
            function doToggle() {
                try {
                    const sb = parentDoc.querySelector('[data-testid="stSidebar"], section[data-testid="stSidebar"]');
                    const isExpanded = sb && (
                        sb.getAttribute('aria-expanded') === 'true' ||
                        (sb.getAttribute('aria-expanded') !== 'false' && (sb.offsetWidth > 50 || (sb.getBoundingClientRect && sb.getBoundingClientRect().width > 50)))
                    );

                    const expandBtn = parentDoc.querySelector(
                        'button[data-testid="stExpandSidebarButton"], ' +
                        '[data-testid="stExpandSidebarButton"] button, ' +
                        '[data-testid="stExpandSidebarButton"], ' +
                        '[data-testid="stSidebarCollapsedControl"] button, ' +
                        'button[data-testid="stSidebarCollapsedControl"], ' +
                        '[data-testid="collapsedControl"] button, ' +
                        'button[aria-label*="Expand sidebar"], ' +
                        'button[title*="Expand sidebar"]'
                    );

                    const collapseBtn = parentDoc.querySelector(
                        'button[data-testid="stSidebarCollapseButton"], ' +
                        '[data-testid="stSidebarCollapseButton"] button, ' +
                        '[data-testid="stSidebarCollapseButton"], ' +
                        '[data-testid="stSidebarHeader"] button, ' +
                        'button[aria-label*="Collapse sidebar"], ' +
                        'button[title*="Collapse sidebar"]'
                    );

                    let clicked = false;
                    if (isExpanded) {
                        if (collapseBtn) {
                            collapseBtn.click();
                            clicked = true;
                        } else if (expandBtn) {
                            expandBtn.click();
                            clicked = true;
                        }
                    } else {
                        if (expandBtn) {
                            expandBtn.click();
                            clicked = true;
                        } else if (collapseBtn) {
                            collapseBtn.click();
                            clicked = true;
                        }
                    }

                    if (clicked) {
                        [20, 60, 120, 200, 300, 450].forEach(function(delay) {
                            setTimeout(setupStickyTopHeader, delay);
                        });
                    }
                    return clicked;
                } catch (err) {
                    console.error('Sidebar toggle bridge error:', err);
                    return false;
                }
            }

            parentWin.__doToggleSidebar = doToggle;
            window.__doToggleSidebar = doToggle;
            if (parentDoc.defaultView) {
                parentDoc.defaultView.__doToggleSidebar = doToggle;
            }
        } catch (err) {
            console.error('Sidebar toggle bridge error:', err);
        }
    }
    
    // Comprehensive Multi-Language Translation Engine & Live DOM Replacer
    const LANG_DICTIONARY = {
        "en": {
            "जन्म कुण्डली": "Birth Chart & Vargas",
            "घटना विश्लेषण": "Event Analysis (Ghatna)",
            "दोष एवं फ्री-विल": "Afflictions & Remedies",
            "दशवर्ग तालिका": "Dasvarga Table",
            "वास्तु-ज्योतिष": "Vastu-Jyotish",
            "प्रश्न कुण्डली": "Horary / Prashna",
            "सर्वर सिंक": "Server Sync",
            "षड्बल एवं भावबल": "Shadbala & Bhavabala",
            "जैमिनी एवं उपग्रह": "Jaimini & Upagraha",
            "दशा प्रणालियाँ": "Dasha Systems",
            "गोचर एवं अष्टकवर्ग": "Transit & Ashtakvarga",
            "के.पी. प्रणाली": "KP Astrology",
            "शुभ मुहूर्त एवं चौघड़िया": "Muhurta & Choghadiya",
            "सुदर्शन चक्र": "Sudarshan Chakra",
            "वर्षफल": "Varshaphal (Annual)",
            "समय शोधन": "Birth Time Rectification",
            "कुण्डली मिलान": "Kundali Matching",
            "ज्योतिष AI सहायक": "Jyotish AI Assistant",
            "ज्योतिषीय पञ्चाङ्ग": "Vedic Jyotish Panchang",
            "सम्पूर्ण रिपोर्ट": "Comprehensive Report",
            "100 शास्त्रीय नियम": "100 Classical Rules",
            "वैदिक ऋषि सत्यापन": "Vedic Sage Validation",
            "वर्तमान समय": "Current Time",
            "वर्तमान स्थान": "Current Location",
            "प्रणाली: सक्रिय": "System: Online",
            "भूमिका: ज्योतिषी": "Role: Astrologer",
            "कुण्डली गणना करें": "Calculate Kundali",
            "तिथि": "Tithi", "वार": "Vara", "नक्षत्र": "Nakshatra", "योग": "Yoga", "करण": "Karana",
            "सूर्योदय": "Sunrise", "सूर्यास्त": "Sunset", "जन्म घटी": "Janma Ghati", "होरा स्वामी": "Hora Lord",
            "भाषा": "Language", "नाम": "Name", "जन्म दिनांक": "Birth Date", "जन्म समय": "Birth Time",
            "स्थान": "Location", "शहर": "City", "अक्षांश": "Latitude", "रेखांश": "Longitude",
            "अयनांश": "Ayanamsa", "भाव प्रणाली": "House System", "कुण्डली शैली": "Chart Style",
            "सहेजें": "Save", "लॉगिन": "Login", "पासवर्ड": "Password", "ईमेल": "Email"
        },
        "ta": {
            "जन्म कुण्डली": "ஜாதகக் கட்டம் (Natal & Vargas)",
            "घटना विश्लेषण": "நிகழ்வு பகுப்பாய்வு (Ghatna)",
            "दोष एवं फ्री-विल": "தோஷ பரிகாரம் & சுயம் (Remedies)",
            "दशवर्ग तालिका": "தசவர்க்க அட்டவணை (Dasvarga)",
            "वास्तु-ज्योतिष": "வாஸ்து ஜோதிடம் (Vastu)",
            "प्रश्न कुण्डली": "பிரசன்ன ஜோதிடம் (Prashna)",
            "सर्वर सिंक": "சர்வர் ஒத்திசைவு (Server Sync)",
            "षड्बल एवं भावबल": "ஷட்பலம் & பாவபலம் (Shadbala)",
            "जैमिनी एवं उपग्रह": "ஜெயமினி ஜோதிடம் (Jaimini)",
            "दशा प्रणालियाँ": "தசா அமைப்புகள் (Dasha)",
            "गोचर एवं अष्टकवर्ग": "கோசாரம் & அஷ்டவர்க்கம் (Transit)",
            "के.पी. प्रणाली": "கே.பி. ஜோதிடம் (KP System)",
            "शुभ मुहूर्त एवं चौघड़िया": "சுப முகூர்த்தம் (Muhurta)",
            "सुदर्शन चक्र": "சுதர்சன சக்கரம் (Sudarshan Chakra)",
            "वर्षफल": "வருட பலன்கள் (Varshaphal)",
            "समय शोधन": "பிறப்பு நேர திருத்தம் (BTR)",
            "कुण्डली मिलान": "திருமணப் பொருத்தம் (Milan)",
            "ज्योतिष AI सहायक": "ஜோதிட AI உதவியாளர் (Sahayak)",
            "सम्पूर्ण रिपोर्ट": "முழுமையான ஜாதக அறிக்கை (Report)",
            "100 शास्त्रीय नियम": "100 சாஸ்திர விதிகள் (Rules)",
            "वैदिक ऋषि सत्यापन": "வேத ரிஷி சரிபார்ப்பு (Validation)",
            "वर्तमान समय": "தற்போதைய நேரம்", "वर्तमान स्थान": "தற்போதைய இடம்",
            "प्रणाली: सक्रिय": "கணினி: ஆன்லைன்", "भूमिका: ज्योतिषी": "பங்கு: ஜோதிடர்",
            "कुण्डली गणना करें": "ஜாதகம் கணக்கிடுக",
            "तिथि": "திதி", "वार": "வாரம்", "नक्षत्र": "நட்சத்திரம்", "योग": "யோகம்", "करण": "கரணம்",
            "सूर्योदय": "சூரியோதயம்", "सूर्यास्त": "சூரிய அஸ்தமனம்", "जन्म घटी": "ஜென்ம கடிகை", "होरा स्वामी": "ஹோரா அதிபதி",
            "भाषा": "மொழி", "नाम": "பெயர்", "स्थान": "இடம்"
        },
        "te": {
            "जन्म कुण्डली": "జన్మ జాతక చక్రం (Natal & Vargas)",
            "घटना विश्लेषण": "సంఘటన విశ్లేషణ (Ghatna)",
            "दोष एवं फ्री-विल": "దోష నివారణ & పరిహారాలు (Remedies)",
            "दशवर्ग तालिका": "దశవర్గ పట్టిక (Dasvarga)",
            "वास्तु-ज्योतिष": "వాస్తు జ్యోతిష్యం (Vastu)",
            "प्रश्न कुण्डली": "ప్రశ్న జాతకం (Prashna)",
            "सर्वर सिंक": "సర్వర్ సమకాలీకరణ (Server Sync)",
            "षड्बल एवं भावबल": "షడ్బలం & భావబలం (Shadbala)",
            "जैमिनी एवं उपग्रह": "జైమిని జ్యోతిష్యం (Jaimini)",
            "दशा प्रणालियाँ": "దశా పద్ధతులు (Dasha)",
            "गोचर एवं अष्टकवर्ग": "గోచార & అష్టకవర్గ (Transit)",
            "के.पी. प्रणाली": "కె.పి. పద్ధతి (KP Astrology)",
            "शुभ मुहूर्त एवं चौघड़िया": "శుభ ముహూర్తం (Muhurta)",
            "सुदर्शन चक्र": "సుదర్శన చక్రం (Sudarshan Chakra)",
            "वर्षफल": "వార్షిక ఫలితాలు (Varshaphal)",
            "समय शोधन": "జన్మ సమయ శోధన (BTR)",
            "कुण्डली मिलान": "గుణ మేళాపకం (Milan)",
            "ज्योतिष AI सहायक": "జ్యోతిష్య AI సహాయకుడు (Sahayak)",
            "सम्पूर्ण रिपोर्ट": "సంపూర్ణ జాతక నివేదిక (Report)",
            "100 शास्त्रीय नियम": "100 శాస్త్రీయ నియమాలు (Rules)",
            "वैदिक ऋषि सत्यापन": "వైదిక ఋషి ధృవీకరణ (Validation)",
            "वर्तमान समय": "ప్రస్తుత సమయం", "वर्तमान स्थान": "ప్రస్తుత స్థానం",
            "प्रणाली: सक्रिय": "వ్యవస్థ: ఆన్‌లైన్", "भूमिका: ज्योतिषी": "పాత్ర: జ్యోతిష్యుడు",
            "कुण्डली गणना करें": "జాతకం గణించండి",
            "तिथि": "తిథి", "वार": "వారం", "नक्षत्र": "నక్షత్రం", "योग": "యోగం", "करण": "కరణం",
            "सूर्योदय": "సూర్యోదయం", "सूर्यास्त": "సూర్యాస్తమయం", "जन्म घटी": "జన్మ ఘడియలు", "होरा स्वामी": "హోరా అధిపతి",
            "भाषा": "భాష", "नाम": "పేరు", "स्थान": "స్థలం"
        },
        "gu": {
            "जन्म कुण्डली": "જન્મ કુંડળી અને ષોડશવર્ગ",
            "घटना विश्लेषण": "ઘટના વિશ્લેષણ",
            "दोष एवं फ्री-विल": "દોષ અને ફ્રી-વિલ ઉપાયો",
            "दशवर्ग तालिका": "દશવર્ગ કોષ્ટક",
            "वास्तु-ज्योतिष": "વાસ્તુ જ્યોતિષ",
            "प्रश्न कुण्डली": "પ્રશ્ન કુંડળી",
            "सर्वर सिंक": "સર્વર સિંક",
            "षड्बल एवं भावबल": "ષડ્બળ અને ભાવબળ",
            "जैमिनी एवं उपग्रह": "જૈમિની અને ઉપગ્રહો",
            "दशा प्रणालियाँ": "દશા પ્રણાલી",
            "गोचर एवं अष्टकवर्ग": "ગોચર અને અષ્ટકવર્ગ",
            "के.पी. प्रणाली": "કે.પી. પદ્ધતિ",
            "शुभ मुहूर्त एवं चौघड़िया": "શુભ મુહૂર્ત",
            "सुदर्शन चक्र": "સુદર્શન ચક્ર",
            "वर्षफल": "વર્ષફળ",
            "समय शोधन": "સમય સંશોધન",
            "कुण्डली मिलान": "કુંડળી મેળવણું",
            "ज्योतिष AI सहायक": "જ્યોતિષ AI સહાયક",
            "सम्पूर्ण रिपोर्ट": "સંપૂર્ણ અહેવાલ",
            "100 शास्त्रीय नियम": "૧૦૦ શાસ્ત્રીય નિયમો",
            "वैदिक ऋषि सत्यापन": "વૈદિક ઋષિ પ્રમાણીકરણ",
            "वर्तमान समय": "વર્તમાન સમય",
            "वर्तमान स्थान": "વર્તમાન સ્થળ",
            "प्रणाली: सक्रिय": "પ્રણાલી: સક્રિય",
            "भूमिका: ज्योतिषी": "ભૂમિકા: જ્યોતિષી",
            "कुण्डली गणना करें": "કુંડળી ગણતરી કરો",
            "तिथि": "તિથિ", "वार": "વાર", "નक्षत्र": "નક્ષત્ર", "योग": "યોગ", "करण": "કરણ",
            "सूर्योदय": "સૂર્યોદય", "सूर्यास्त": "સૂર્યાસ્ત", "जन्म घटी": "જન્મ ઘટી", "होरा स्वामी": "હોરા સ્વામી",
            "भाषा": "ભાષા", "नाम": "નામ"
        },
        "mr": {
            "जन्म कुण्डली": "जन्म पत्रिका व षोडशवर्ग",
            "घटना विश्लेषण": "घटना विश्लेषण",
            "दोष एवं फ्री-विल": "दोष व फ्री-विल उपाय",
            "दशवर्ग तालिका": "दशवर्ग तक्ता",
            "वास्तु-ज्योतिष": "वास्तु ज्योतिष",
            "प्रश्न कुण्डली": "प्रश्न पत्रिका",
            "सर्वर सिंक": "सर्व्हर सिंक",
            "षड्बल एवं भावबल": "षड्बल व भावबल",
            "जैमिनी एवं उपग्रह": "जैमिनी व उपग्रह",
            "दशा प्रणालियाँ": "दशा प्रणाली",
            "गोचर एवं अष्टकवर्ग": "गोचर व अष्टकवर्ग",
            "के.पी. प्रणाली": "के.पी. पद्धती",
            "शुभ मुहूर्त एवं चौघड़िया": "शुभ मुहूर्त",
            "सुदर्शन चक्र": "सुदर्शन चक्र",
            "वर्षफल": "वर्षफळ",
            "समय शोधन": "वेळ शोधन",
            "कुण्डली मिलान": "पत्रिका मिलन",
            "ज्योतिष AI सहायक": "ज्योतिष AI सहाय्यक",
            "सम्पूर्ण रिपोर्ट": "संपूर्ण अहवाल",
            "100 शास्त्रीय नियम": "१०० शास्त्रीय नियम",
            "वैदिक ऋषि सत्यापन": "वैदिक ऋषी पडताळणी",
            "वर्तमान समय": "चालू वेळ",
            "वर्तमान स्थान": "सध्याचे स्थान",
            "प्रणाली: सक्रिय": "प्रणाली: सक्रिय",
            "भूमिका: ज्योतिषी": "भूमिका: ज्योतिषी",
            "कुण्डली गणना करें": "पत्रिका गणना करा",
            "तिथि": "तिथी", "वार": "वार", "नक्षत्र": "नक्षत्र", "योग": "योग", "करण": "करण",
            "सूर्योदय": "सूर्योदय", "सूर्यास्त": "सूर्यास्त", "जन्म घटी": "जन्म घटी", "होरा स्वामी": "होरा स्वामी",
            "भाषा": "भाषा", "नाम": "नाव"
        },
        "bn": {
            "जन्म कुण्डली": "জন্ম কুণ্ডলী ও ষোড়শবর্গ",
            "घटना विश्लेषण": "ঘটনা বিশ্লেষণ",
            "दोष एवं फ्री-विल": "দোষ ও প্রতিকার",
            "दशवर्ग तालिका": "দশবর্গ তালিকা",
            "वास्तु-ज्योतिष": "বাস্তু জ্যোতিষ",
            "प्रश्न कुण्डली": "প্রশ্ন কুণ্ডলী",
            "सर्वर सिंक": "সার্ভার সিঙ্ক",
            "षड्बल एवं भावबल": "ষড়্বল ও ভাববল",
            "जैमिनी एवं उपग्रह": "জৈমিনী ও উপগ্রহ",
            "दशा प्रणालियाँ": "দশা পদ্ধতি",
            "गोचर एवं अष्टकवर्ग": "গোচর ও অষ্টকবর্গ",
            "के.पी. प्रणाली": "কে.পি. পদ্ধতি",
            "शुभ मुहूर्त एवं चौघड़िया": "শুভ মুহূর্ত",
            "सुदर्शन चक्र": "সুদর্শন চক্র",
            "वर्षफल": "বর্ষফল",
            "समय शोधन": "সময় সংশোধন",
            "कुण्डली मिलान": "কুণ্ডলী মিলন",
            "ज्योतिष AI सहायक": "জ্যোতিষ AI সহকারী",
            "सम्पूर्ण रिपोर्ट": "সম্পূর্ণ রিপোর্ট",
            "100 शास्त्रीय नियम": "১০০ শাস্ত্রীয় নিয়ম",
            "वैदिक ऋषि सत्यापन": "বৈদিক ঋষি প্রমাণ",
            "वर्तमान समय": "বর্তমান সময়",
            "वर्तमान स्थान": "বর্তমান অবস্থান",
            "प्रणाली: सक्रिय": "সিস্টেম: সক্রিয়",
            "भूमिका: ज्योतिषी": "ভূমিকা: জ্যোতিষী",
            "कुण्डली गणना करें": "কুণ্ডলী গণনা করুন",
            "तिथि": "তিথি", "वार": "বার", "নक्षत्र": "নক্ষত্র", "योग": "যোগ", "করণ": "করণ",
            "सूर्योदय": "সূর্যোদয়", "सूर्याস্ত": "সূর্যাস্ত", "जन्म घटी": "জন্ম ঘটি", "होरा स्वामी": "হোরা স্বামী",
            "भाषा": "ভাষা", "नाम": "নাম"
        }
    };

    function applyDOMTranslations(targetLang) {
        try {
            const parentDoc = window.parent.document;
            if (!parentDoc) return;
            
            if (targetLang === "general" || !targetLang || targetLang === "hi") {
                // Restore original if general
                const elements = parentDoc.querySelectorAll('[data-orig-text]');
                elements.forEach(function(el) {
                    el.innerText = el.getAttribute('data-orig-text');
                    el.removeAttribute('data-orig-text');
                });
                return;
            }

            const dict = LANG_DICTIONARY[targetLang];
            if (!dict) return;

            // Walk text nodes in parentDoc
            const walker = parentDoc.createTreeWalker(
                parentDoc.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            let node;
            while ((node = walker.nextNode())) {
                const parentEl = node.parentElement;
                if (!parentEl || parentEl.tagName === 'SCRIPT' || parentEl.tagName === 'STYLE' || parentEl.id === 'software-lang-select' || (parentEl.closest && parentEl.closest('.notranslate, #software-lang-select, select, option, .lang-select-box'))) {
                    continue;
                }

                let text = node.nodeValue;
                if (!text || !text.trim()) continue;

                for (let k in dict) {
                    if (text.includes(k)) {
                        if (!parentEl.getAttribute('data-orig-text')) {
                            parentEl.setAttribute('data-orig-text', parentEl.innerText);
                        }
                        node.nodeValue = text.split(k).join(dict[k]);
                        text = node.nodeValue;
                    }
                }
            }
        } catch (err) {
            console.error('DOM Translation error:', err);
        }
    }

    function setupLanguageBridge() {
        try {
            const parentDoc = window.parent.document;
            const parentWin = window.parent;
            if (!parentDoc || !parentWin) return;

            function setGoogleTransCookie(lang) {
                const domain = parentWin.location.hostname;
                if (lang === 'general' || lang === 'hi' || !lang) {
                    const cookies = ['googtrans'];
                    const domains = ['', domain, '.' + domain];
                    cookies.forEach(function(c) {
                        domains.forEach(function(d) {
                            parentDoc.cookie = c + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;' + (d ? ' domain=' + d + ';' : '');
                        });
                    });
                } else {
                    const transVal = '/hi/' + lang;
                    parentDoc.cookie = 'googtrans=' + transVal + '; path=/;';
                    if (domain) {
                        parentDoc.cookie = 'googtrans=' + transVal + '; path=/; domain=' + domain + ';';
                        parentDoc.cookie = 'googtrans=' + transVal + '; path=/; domain=.' + domain + ';';
                    }
                }
            }

            const handleLanguageSwitch = function(langCode) {
                localStorage.setItem("jyotish_app_lang", langCode);
                sessionStorage.setItem("jyotish_app_lang", langCode);
                setGoogleTransCookie(langCode);
                
                // Sync all language dropdowns on page
                const selects = parentDoc.querySelectorAll('#software-lang-select');
                selects.forEach(function(sel) {
                    if (sel.value !== langCode) {
                        sel.value = langCode;
                    }
                });

                // 1. Instant DOM Translation (Zero Lag)
                applyDOMTranslations(langCode);

                // 2. Google Translate Integration
                if (langCode === "general" || langCode === "hi" || !langCode) {
                    const combo = parentDoc.querySelector('.goog-te-combo');
                    if (combo) {
                        combo.value = "hi";
                        combo.dispatchEvent(new Event('change'));
                    }
                    setTimeout(function() {
                        parentWin.location.reload();
                    }, 100);
                    return;
                }
                
                const combo = parentDoc.querySelector('.goog-te-combo');
                if (combo) {
                    combo.value = langCode;
                    combo.dispatchEvent(new Event('change'));
                } else {
                    setTimeout(function() {
                        parentWin.location.reload();
                    }, 150);
                }
            };

            parentWin.changeSoftwareLanguage = handleLanguageSwitch;
            window.changeSoftwareLanguage = handleLanguageSwitch;

            // Bind change events to all select boxes
            const selects = parentDoc.querySelectorAll('#software-lang-select');
            selects.forEach(function(sel) {
                if (!sel.dataset.bound) {
                    sel.dataset.bound = "true";
                    sel.addEventListener('change', function(e) {
                        handleLanguageSwitch(e.target.value);
                    });
                }
            });

            // Inject Google Translate script if not present
            if (!parentDoc.getElementById('google-translate-script')) {
                let gdiv = parentDoc.getElementById('google_translate_element');
                if (!gdiv) {
                    gdiv = parentDoc.createElement('div');
                    gdiv.id = 'google_translate_element';
                    gdiv.style.display = 'none';
                    parentDoc.body.appendChild(gdiv);
                }

                parentWin.googleTranslateElementInit = function() {
                    new parentWin.google.translate.TranslateElement({
                        pageLanguage: 'hi',
                        includedLanguages: 'hi,en,gu,mr,bn,te,ta',
                        autoDisplay: false
                    }, 'google_translate_element');
                };

                const s = parentDoc.createElement('script');
                s.id = 'google-translate-script';
                s.type = 'text/javascript';
                s.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
                parentDoc.head.appendChild(s);
            }

            // Apply saved language
            const activeLang = localStorage.getItem("jyotish_app_lang") || "general";
            selects.forEach(function(sel) {
                if (sel.value !== activeLang) {
                    sel.value = activeLang;
                }
            });
            if (activeLang && activeLang !== "general" && activeLang !== "hi") {
                applyDOMTranslations(activeLang);
            }
        } catch (e) {
            console.error('Language bridge error:', e);
        }
    }

    // Live Client GPS Geolocation Resolver
    function updateLocationUI(locStr) {
        try {
            const parentDoc = window.parent.document;
            if (!parentDoc) return;
            const els = parentDoc.querySelectorAll('#user-gps-val, .user-gps-val');
            els.forEach(function(el) {
                el.innerText = locStr;
            });
        } catch (e) {}
    }

    // Clean any stale cloud datacenter (The Dalles, Oregon) cache immediately
    try {
        const cachedLoc = localStorage.getItem("jyotish_user_gps_loc") || "";
        if (cachedLoc.includes("The Dalles") || cachedLoc.includes("Oregon") || cachedLoc.includes("United States")) {
            localStorage.removeItem("jyotish_user_gps_loc");
            localStorage.removeItem("jyotish_user_gps_lat");
            localStorage.removeItem("jyotish_user_gps_lon");
            sessionStorage.removeItem("jyotish_user_gps_loc");
        }
    } catch(e) {}

    function requestDeviceGPS(target) {
        target = target || "nat_prashna";
        const pWin = (window.parent && window.parent.location) ? window.parent : window;
        const nav = (pWin.navigator && pWin.navigator.geolocation) 
                    ? pWin.navigator 
                    : ((window.navigator && window.navigator.geolocation) ? window.navigator : null);

        if (!nav || !nav.geolocation) {
            alert("⚠️ आपके डिवाइस या ब्राउज़र में GPS जियोलोकेशन समर्थित नहीं है। (Geolocation not supported)");
            return;
        }

        nav.geolocation.getCurrentPosition(
            function(pos) {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                // Guard against datacenter coordinates (The Dalles, Oregon: lat ~45.5 to 45.7, lon ~ -121.3 to -121.0)
                if (Math.abs(lat - 45.5946) < 0.8 && Math.abs(lon - (-121.1787)) < 0.8) {
                    alert("📍 डिवाइस ने क्लाउड सर्वर का स्थान (The Dalles, Oregon) लौटाया है।\\n\\nकृपया सुनिश्चित करें कि आपके डिवाइस (लैपटॉप/मोबाइल) में GPS/लोकेशन सेवा चालू है, और ब्राउज़र में GPS अनुमति दी गई है।");
                    return;
                }
                try {
                    localStorage.setItem("jyotish_user_gps_lat", lat.toFixed(5));
                    localStorage.setItem("jyotish_user_gps_lon", lon.toFixed(5));
                    const u = new URL(pWin.location.href);
                    u.searchParams.set("gps_lat", lat.toFixed(5));
                    u.searchParams.set("gps_lon", lon.toFixed(5));
                    u.searchParams.set("gps_target", target);
                    pWin.location.href = u.toString();
                } catch(e) {
                    pWin.location.search = "?gps_lat=" + encodeURIComponent(lat.toFixed(5)) + "&gps_lon=" + encodeURIComponent(lon.toFixed(5)) + "&gps_target=" + encodeURIComponent(target);
                }
            },
            function(err) {
                let msg = "GPS अनुमति त्रुटि: " + err.message;
                if (err.code === 1) {
                    msg = "📍 डिवाइस GPS अनुमति अस्वीकृत (Location Permission Denied)।\\n\\nकृपया अपने ब्राउज़र के एड्रेस बार में लॉक (🔒) आइकन अथवा साइट सेटिंग्स पर क्लिक करके 'Location' को 'Allow' (अनुमति दें) करें, फिर पुनः GPS बटन दबाएं।";
                } else if (err.code === 2) {
                    msg = "📍 डिवाइस GPS सिग्नल प्राप्त नहीं हो सका। कृपया सुनिश्चित करें कि मोबाइल/कंप्यूटर में Location/GPS सेवा चालू है।";
                } else if (err.code === 3) {
                    msg = "⏱️ GPS अनुरोध समय समाप्त (Timeout) हो गया। कृपया दोबारा प्रयास करें।";
                }
                alert(msg);
            },
            { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
        );
    }

    parentWin.requestDeviceGPS = requestDeviceGPS;
    window.requestDeviceGPS = requestDeviceGPS;

    function bindGpsButtons() {
        try {
            const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            if (!pDoc) return;
            const buttons = pDoc.querySelectorAll('button');
            buttons.forEach(function(btn) {
                const txt = btn.innerText || "";
                if (txt.includes("वर्तमान GPS स्थान") && !btn.dataset.gpsBound) {
                    btn.dataset.gpsBound = "true";
                    btn.addEventListener('click', function() {
                        let target = "nat_prashna";
                        if (txt.includes("नवीन") || (btn.closest && btn.closest('.stTabs [data-baseweb="tab-panel"]:nth-child(2)'))) {
                            target = "new_prashna";
                        } else if (btn.closest && (btn.closest('.st-key-btn_birth_get_gps') || btn.closest('[data-testid="stExpander"]'))) {
                            target = "birth";
                        }
                        requestDeviceGPS(target);
                    }, true);
                }
            });
        } catch(e) {}
    }

    function switchAppTab(target) {
        try {
            const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            if (!pDoc) return false;

            const mainSec = pDoc.querySelector('[data-testid="stMain"], section.main') || pDoc;
            const allTabs = Array.from(mainSec.querySelectorAll('.stTabs [role="tab"], [data-baseweb="tab-list"] button[role="tab"]'))
                .filter(b => !b.closest('[role="dialog"]') && !b.closest('[data-testid="stModal"]') && !b.closest('.st-key-frozen_toolbelt_container'));

            if (!allTabs || allTabs.length === 0) return false;

            let targetBtn = null;
            if (typeof target === 'string' && target.trim()) {
                const q = target.trim();
                targetBtn = allTabs.find(b => {
                    const txt = (b.textContent || "").trim();
                    return txt === q || txt.includes(q) || q.includes(txt);
                });
            }
            if (!targetBtn) {
                const idx = (typeof target === 'number') ? target : parseInt(target);
                if (!isNaN(idx) && idx >= 0 && idx < allTabs.length) {
                    targetBtn = allTabs[idx];
                }
            }

            if (targetBtn) {
                if (targetBtn.getAttribute('aria-selected') === 'true') {
                    return true;
                }
                targetBtn.focus();
                targetBtn.click();
                return true;
            }
        } catch(e) {
            console.warn("Tab switch error:", e);
        }
        return false;
    }
    parentWin.switchAppTab = switchAppTab;
    window.switchAppTab = switchAppTab;

    function setupTabSwitcher() {
        try {
            const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            if (!pDoc || pDoc.__tabDropdownObserverBound) return;
            pDoc.__tabDropdownObserverBound = true;

            pDoc.addEventListener('click', function(e) {
                const opt = e.target ? e.target.closest('li[role="option"], div[role="option"], [data-baseweb="menu-item"]') : null;
                if (!opt) return;
                const optText = (opt.innerText || opt.textContent || "").trim();
                if (!optText) return;

                const pWin = (window.parent || window);
                const tabsList = pWin.__CURRENT_MODULE_TABS || window.__CURRENT_MODULE_TABS || [];
                const matchedTab = tabsList.find(t => {
                    const st = t.trim();
                    return optText === st || optText.includes(st) || st.includes(optText);
                });

                if (matchedTab) {
                    switchAppTab(matchedTab);
                    setTimeout(function() { switchAppTab(matchedTab); }, 60);
                    setTimeout(function() { switchAppTab(matchedTab); }, 180);
                }
            }, true);
        } catch(e) {}
    }

    function resolveClientGPS() {
        try {
            const cached = localStorage.getItem("jyotish_user_gps_loc") || sessionStorage.getItem("jyotish_user_gps_loc");
            if (cached && !cached.includes("The Dalles") && !cached.includes("Oregon")) {
                updateLocationUI(cached);
            }

            const pWin = (window.parent && window.parent.location) ? window.parent : window;
            const nav = (pWin.navigator && pWin.navigator.geolocation) 
                        ? pWin.navigator 
                        : ((window.navigator && window.navigator.geolocation) ? window.navigator : null);

            if (nav && nav.geolocation && !window.__gps_queried) {
                window.__gps_queried = true;
                nav.geolocation.getCurrentPosition(function(pos) {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    if (Math.abs(lat - 45.5946) < 0.8 && Math.abs(lon - (-121.1787)) < 0.8) {
                        return; // Ignore datacenter coords
                    }
                    localStorage.setItem("jyotish_user_gps_lat", lat.toFixed(5));
                    localStorage.setItem("jyotish_user_gps_lon", lon.toFixed(5));
                    fetch("https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=" + lat + "&longitude=" + lon + "&localityLanguage=en")
                        .then(function(r) { return r.json(); })
                        .then(function(data) {
                            const city = data.locality || data.city || data.principalSubdivision || "स्थानीय";
                            const state = data.principalSubdivision || "";
                            const country = data.countryName || "India";
                            if (country === "United States" || city === "The Dalles") return;
                            const loc = city + (state && state !== city ? (", " + state) : "") + " (" + country + ")";
                            localStorage.setItem("jyotish_user_gps_loc", loc);
                            sessionStorage.setItem("jyotish_user_gps_loc", loc);
                            updateLocationUI(loc);
                        })
                        .catch(function() {
                            fetch("https://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&lon=" + lon)
                                .then(function(r) { return r.json(); })
                                .then(function(d) {
                                    const a = d.address || {};
                                    const city = a.city || a.town || a.village || a.county || "स्थानीय";
                                    const state = a.state || "";
                                    const country = a.country || "India";
                                    if (country === "United States" || city === "The Dalles") return;
                                    const loc = city + (state ? (", " + state) : "") + " (" + country + ")";
                                    localStorage.setItem("jyotish_user_gps_loc", loc);
                                    sessionStorage.setItem("jyotish_user_gps_loc", loc);
                                    updateLocationUI(loc);
                                }).catch(function() {});
                        });
                }, function(err) {
                    // Fallback to client-side IP lookup in user browser (not server)
                    if (!cached || cached.includes("The Dalles") || cached.includes("Oregon")) {
                        fetch("https://ipapi.co/json/")
                            .then(function(r) { return r.json(); })
                            .then(function(d) {
                                if (d.country_code === "US" || d.region === "Oregon" || d.city === "The Dalles") {
                                    updateLocationUI("नई दिल्ली, भारत (डिफ़ॉल्ट)");
                                    return;
                                }
                                const loc = (d.city || "नई दिल्ली") + ", " + (d.region || "दिल्ली") + " (" + (d.country_name || "India") + ")";
                                localStorage.setItem("jyotish_user_gps_loc", loc);
                                updateLocationUI(loc);
                            })
                            .catch(function() {
                                updateLocationUI("नई दिल्ली, भारत (डिफ़ॉल्ट)");
                            });
                    }
                }, { timeout: 15000, enableHighAccuracy: true, maximumAge: 30000 });
            }
        } catch (e) {
            console.error('GPS resolver error:', e);
        }
    }

    // Comprehensive Day Mode / Night Mode Theme Engine
    function setupThemeMode() {
        try {
            const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            const parentWin = window.parent || window;
            if (!parentDoc) return;

            const THEME_STYLE_ID = "jyotish-theme-override-style";
            const SERVER_THEME_MODE = "__ACTIVE_THEME_MODE__";

            function applyTheme(mode) {
                if (!mode || (mode !== "astrallis" && mode !== "night" && mode !== "day")) {
                    mode = "day";
                }
                const isAstrallis = (mode === "astrallis");
                const isNight = (mode === "night");
                try {
                    localStorage.setItem("jyotish_theme_mode", mode);
                    sessionStorage.setItem("jyotish_theme_mode", mode);
                } catch(e) {}

                let styleEl = parentDoc.getElementById(THEME_STYLE_ID);
                if (!styleEl) {
                    styleEl = parentDoc.getElementById("jyotish-night-mode-override-style");
                    if (styleEl) styleEl.id = THEME_STYLE_ID;
                }

                if (parentDoc.body && parentDoc.body.dataset.appliedThemeMode === mode && styleEl && styleEl.innerHTML.length > 50) {
                    return;
                }
                if (parentDoc.body) {
                    parentDoc.body.dataset.appliedThemeMode = mode;
                }

                if (isAstrallis) {
                    parentDoc.body.classList.remove("night-mode");
                    parentDoc.body.classList.add("astrallis-mode");
                    if (parentDoc.documentElement) {
                        parentDoc.documentElement.classList.remove("night-mode");
                        parentDoc.documentElement.classList.add("astrallis-mode");
                    }
                    
                    const astrallisCss = `
                        html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
                            background-color: #050811 !important;
                            color: #E2E8F0 !important;
                        }
                        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
                            background-color: #EBF5E4 !important;
                            background: #EBF5E4 !important;
                            border-right: 1.5px solid #C8DEC0 !important;
                        }
                        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
                            color: #000000 !important;
                        }
                        section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
                        section[data-testid="stSidebar"] .stRadio label,
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
                        div[data-testid="stRadio"] label {
                            background: #0D1322 !important;
                            border: 1.5px solid #1E293B !important;
                            color: #E2E8F0 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p {
                            color: #CBD5E1 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
                            background: #1E293B !important;
                            border-color: #00E5FF !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"],
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {
                            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%) !important;
                            border: 2px solid #00E5FF !important;
                            box-shadow: 0 4px 14px rgba(0, 229, 255, 0.25) !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p,
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) p {
                            color: #FFFFFF !important;
                            font-weight: 800 !important;
                        }
                        h1, h2, h3, h4, h5, h6, p, span, li, a, label, caption, strong, b, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
                            color: #E2E8F0 !important;
                        }
                        input, textarea, select,
                        div[data-baseweb="input"] input,
                        div[data-baseweb="base-input"] input,
                        div[data-baseweb="input"] {
                            background-color: #0A0E1A !important;
                            color: #FFFFFF !important;
                            -webkit-text-fill-color: #FFFFFF !important;
                            border: 1.5px solid #1E293B !important;
                            border-radius: 6px !important;
                        }
                        div[data-baseweb="select"] > div {
                            background-color: #0A0E1A !important;
                            color: #FFFFFF !important;
                            border: 1.5px solid #1E293B !important;
                            border-radius: 6px !important;
                        }
                        div[data-baseweb="select"] * {
                            color: #FFFFFF !important;
                        }
                        header.top-nav-bar {
                            background: #0A0E1A !important;
                            border-color: #1E293B !important;
                            border-bottom: 3px solid #00E5FF !important;
                            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8) !important;
                        }
                        .top-nav-bar * {
                            color: #E2E8F0 !important;
                        }
                        .app-brand-title {
                            background: linear-gradient(90deg, #00E5FF 0%, #38BDF8 50%, #F59E0B 100%) !important;
                            -webkit-background-clip: text !important;
                            -webkit-text-fill-color: transparent !important;
                        }
                        .app-brand-sub {
                            color: #94A3B8 !important;
                        }
                        .active-profile-pill {
                            background: #0D1322 !important;
                            border: 1.5px solid #00E5FF !important;
                            color: #E0F2FE !important;
                        }
                        .active-profile-pill * {
                            color: #E0F2FE !important;
                        }
                        .header-sub-pill {
                            background: #0D1322 !important;
                            border: 1.5px solid #1E293B !important;
                            color: #CBD5E1 !important;
                        }
                        .header-sub-pill * {
                            color: #CBD5E1 !important;
                        }
                        .header-sub-pill b {
                            color: #F8FAFC !important;
                        }
                        .theme-select-box {
                            background: #0D1322 !important;
                            border-color: #00E5FF !important;
                        }
                        .theme-select-box select, .theme-select-box b, .theme-select-box span {
                            color: #00E5FF !important;
                        }
                        .theme-select-box option {
                            background: #0A0E1A !important;
                            color: #FFFFFF !important;
                        }
                        .digital-hud {
                            background: #080C14 !important;
                            border-color: #1E293B !important;
                        }
                        .digital-hud * {
                            color: #E2E8F0 !important;
                        }
                        .hud-pill {
                            background: #0D1322 !important;
                            border: 1.5px solid #1E293B !important;
                            color: #E2E8F0 !important;
                        }
                        .hud-pill b, .hud-pill strong {
                            color: #00E5FF !important;
                        }
                        .rule-card, .vastu-card {
                            background: #080C14 !important;
                            border: 1.5px solid #1E293B !important;
                            color: #E2E8F0 !important;
                        }
                        .rule-card *, .vastu-card * {
                            color: #E2E8F0 !important;
                        }
                        div[data-testid="stExpander"] {
                            background: #080C14 !important;
                            border: 1.5px solid #1E293B !important;
                        }
                        div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
                            color: #00E5FF !important;
                            font-family: 'JetBrains Mono', monospace !important;
                        }
                        div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
                            color: #94A3B8 !important;
                        }
                        [data-testid="stMetric"] {
                            background: #080C14 !important;
                            border: 1.5px solid #1E293B !important;
                            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5) !important;
                        }
                        [data-testid="stTable"], [data-testid="stDataFrame"], [data-testid="stTable"] *, [data-testid="stDataFrame"] * {
                            background-color: #050811 !important;
                            color: #F1F5F9 !important;
                            font-family: 'JetBrains Mono', monospace !important;
                        }
                        button[kind="secondary"] {
                            background-color: #0D1322 !important;
                            color: #FFFFFF !important;
                            border: 1.5px solid #1E293B !important;
                        }
                        button[kind="secondary"]:hover {
                            background-color: #1E293B !important;
                            border-color: #00E5FF !important;
                        }
                        [data-testid="stTabs"] [data-baseweb="tab-list"] {
                            background: #080C14 !important;
                            border: 1.5px solid #1E293B !important;
                        }
                        [data-testid="stTabs"] button[role="tab"] {
                            color: #94A3B8 !important;
                        }
                        [data-testid="stTabs"] button[role="tab"]:hover {
                            color: #F8FAFC !important;
                            background: rgba(30, 41, 59, 0.7) !important;
                        }
                        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
                            background: #1E293B !important;
                            color: #00E5FF !important;
                            border: 1.5px solid #00E5FF !important;
                            box-shadow: 0 2px 12px rgba(0, 229, 255, 0.25) !important;
                        }
                        [data-testid="stChatMessage"] {
                            background: #080C14 !important;
                            border: 1.5px solid #1E293B !important;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
                        }
                        [data-testid="stChatInput"] {
                            background-color: #080C14 !important;
                            border-color: #1E293B !important;
                        }
                        div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
                        div[style*="background:#F8FAFC"], div[style*="background: #F8FAFC"],
                        div[style*="background:#EFF6FF"], div[style*="background: #EFF6FF"] {
                            background: #080C14 !important;
                            border-color: #1E293B !important;
                            color: #E2E8F0 !important;
                        }
                        .aspect-trine { stroke: #22C55E !important; stroke-width: 1.6 !important; opacity: 0.9 !important; }
                        .aspect-square { stroke: #EF4444 !important; stroke-width: 1.6 !important; opacity: 0.9 !important; }
                        .aspect-sextile { stroke: #06B6D4 !important; stroke-width: 1.4 !important; opacity: 0.85 !important; }
                        .aspect-opp { stroke: #F43F5E !important; stroke-width: 1.8 !important; stroke-dasharray: 4,2 !important; opacity: 0.95 !important; }
                        .aspect-conj { stroke: #EAB308 !important; stroke-width: 2 !important; opacity: 0.9 !important; }
                        .aspect-quincunx { stroke: #A855F7 !important; stroke-width: 1.2 !important; stroke-dasharray: 2,2 !important; opacity: 0.8 !important; }
                        .observatory-canvas {
                            background: radial-gradient(circle at center, #060911 0%, #000000 100%) !important;
                            border: 1.5px solid #1E293B !important;
                            border-radius: 12px !important;
                        }
                        .pl-box-header, .pl-box-header *, .pl-box-header span, .pl-box-header b {
                            background: linear-gradient(180deg, #1E3A8A 0%, #0F172A 100%) !important;
                            color: #00E5FF !important;
                            -webkit-text-fill-color: #00E5FF !important;
                            border-bottom: 1px solid #00E5FF !important;
                        }
                    `;
                    if (!styleEl) {
                        styleEl = parentDoc.createElement("style");
                        styleEl.id = THEME_STYLE_ID;
                        parentDoc.head.appendChild(styleEl);
                    }
                    styleEl.innerHTML = astrallisCss;
                } else if (isNight) {
                    parentDoc.body.classList.remove("astrallis-mode");
                    parentDoc.body.classList.add("night-mode");
                    if (parentDoc.documentElement) {
                        parentDoc.documentElement.classList.remove("astrallis-mode");
                        parentDoc.documentElement.classList.add("night-mode");
                    }
                    
                    const nightCss = `
                        html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
                            background-color: #070A12 !important;
                            color: #F8FAFC !important;
                        }
                        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
                            background-color: #EBF5E4 !important;
                            background: #EBF5E4 !important;
                            border-right: 1.5px solid #C8DEC0 !important;
                        }
                        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
                            color: #000000 !important;
                        }
                        section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
                        section[data-testid="stSidebar"] .stRadio label,
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
                        div[data-testid="stRadio"] label {
                            background: #111827 !important;
                            border: 1.5px solid #1F2937 !important;
                            color: #F1F5F9 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p {
                            color: #F1F5F9 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
                            background: #1E293B !important;
                            border-color: #F59E0B !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"],
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {
                            background: linear-gradient(135deg, #1E293B 0%, #1E3A8A 100%) !important;
                            border: 2px solid #F59E0B !important;
                            box-shadow: 0 4px 14px rgba(245, 158, 11, 0.25) !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p,
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) p {
                            color: #FFFFFF !important;
                            font-weight: 800 !important;
                        }
                        h1, h2, h3, h4, h5, h6, p, span, li, a, label, caption, strong, b, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
                            color: #F1F5F9 !important;
                        }
                        input, textarea, select,
                        div[data-baseweb="input"] input,
                        div[data-baseweb="base-input"] input,
                        div[data-baseweb="input"] {
                            background-color: #111827 !important;
                            color: #FFFFFF !important;
                            -webkit-text-fill-color: #FFFFFF !important;
                            border: 1.5px solid #374151 !important;
                            border-radius: 8px !important;
                        }
                        div[data-baseweb="select"] > div {
                            background-color: #111827 !important;
                            color: #FFFFFF !important;
                            border: 1.5px solid #374151 !important;
                            border-radius: 8px !important;
                        }
                        div[data-baseweb="select"] * {
                            color: #FFFFFF !important;
                        }
                        header.top-nav-bar {
                            background: #0D1322 !important;
                            border-color: #1E293B !important;
                            border-bottom: 3.5px solid #F59E0B !important;
                            box-shadow: 0 4px 25px rgba(0, 0, 0, 0.8) !important;
                        }
                        .top-nav-bar * {
                            color: #F8FAFC !important;
                        }
                        .app-brand-title {
                            background: linear-gradient(90deg, #F59E0B 0%, #FBBF24 50%, #60A5FA 100%) !important;
                            -webkit-background-clip: text !important;
                            -webkit-text-fill-color: transparent !important;
                        }
                        .app-brand-sub {
                            color: #94A3B8 !important;
                        }
                        .active-profile-pill {
                            background: #111827 !important;
                            border: 1.5px solid #F59E0B !important;
                            color: #FEF3C7 !important;
                        }
                        .active-profile-pill * {
                            color: #FEF3C7 !important;
                        }
                        .header-sub-pill {
                            background: #111827 !important;
                            border: 1.5px solid #1F2937 !important;
                            color: #E2E8F0 !important;
                        }
                        .header-sub-pill * {
                            color: #E2E8F0 !important;
                        }
                        .header-sub-pill b {
                            color: #F8FAFC !important;
                        }
                        .theme-select-box {
                            background: #111827 !important;
                            border-color: #F59E0B !important;
                        }
                        .theme-select-box select, .theme-select-box b, .theme-select-box span {
                            color: #F59E0B !important;
                        }
                        .theme-select-box option {
                            background: #0D1322 !important;
                            color: #FFFFFF !important;
                        }
                        .digital-hud {
                            background: #0D1322 !important;
                            border-color: #1E293B !important;
                        }
                        .digital-hud * {
                            color: #F8FAFC !important;
                        }
                        .hud-pill {
                            background: #111827 !important;
                            border: 1.5px solid #1F2937 !important;
                            color: #F8FAFC !important;
                        }
                        .hud-pill b, .hud-pill strong {
                            color: #F59E0B !important;
                        }
                        .rule-card, .vastu-card {
                            background: #111827 !important;
                            border: 1.5px solid #1F2937 !important;
                            color: #F8FAFC !important;
                        }
                        .rule-card *, .vastu-card * {
                            color: #F8FAFC !important;
                        }
                        div[data-testid="stExpander"] {
                            background: #111827 !important;
                            border: 1.5px solid #1F2937 !important;
                        }
                        div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
                            color: #F8FAFC !important;
                        }
                        div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
                            color: #94A3B8 !important;
                        }
                        [data-testid="stMetric"] {
                            background: #111827 !important;
                            border: 1.5px solid #1F2937 !important;
                            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
                        }
                        [data-testid="stTable"], [data-testid="stDataFrame"], [data-testid="stTable"] *, [data-testid="stDataFrame"] * {
                            background-color: #111827 !important;
                            color: #FFFFFF !important;
                        }
                        button[kind="secondary"] {
                            background-color: #111827 !important;
                            color: #FFFFFF !important;
                            border: 1.5px solid #374151 !important;
                        }
                        button[kind="secondary"]:hover {
                            background-color: #1F2937 !important;
                            border-color: #60A5FA !important;
                        }
                        /* Tabs Night Mode */
                        [data-testid="stTabs"] [data-baseweb="tab-list"] {
                            background: #0D1322 !important;
                            border: 1.5px solid #1E293B !important;
                        }
                        [data-testid="stTabs"] button[role="tab"] {
                            color: #94A3B8 !important;
                        }
                        [data-testid="stTabs"] button[role="tab"]:hover {
                            color: #F8FAFC !important;
                            background: rgba(31, 41, 55, 0.6) !important;
                        }
                        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
                            background: #1F2937 !important;
                            color: #F59E0B !important;
                            border: 1.5px solid #F59E0B !important;
                            box-shadow: 0 2px 12px rgba(245, 158, 11, 0.25) !important;
                        }
                        /* Chat Night Mode */
                        [data-testid="stChatMessage"] {
                            background: #111827 !important;
                            border: 1.5px solid #1F2937 !important;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
                        }
                        [data-testid="stChatInput"] {
                            background-color: #111827 !important;
                            border-color: #374151 !important;
                        }
                        div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
                        div[style*="background:#F8FAFC"], div[style*="background: #F8FAFC"],
                        div[style*="background:#EFF6FF"], div[style*="background: #EFF6FF"] {
                            background: #111827 !important;
                            border-color: #1F2937 !important;
                            color: #F8FAFC !important;
                        }
                        .pl-box-header, .pl-box-header *, .pl-box-header span, .pl-box-header b {
                            background: linear-gradient(180deg, #374151 0%, #1F2937 100%) !important;
                            color: #F59E0B !important;
                            -webkit-text-fill-color: #F59E0B !important;
                            border-bottom: 1px solid #F59E0B !important;
                        }
                    `;
                    
                    if (!styleEl) {
                        styleEl = parentDoc.createElement("style");
                        styleEl.id = THEME_STYLE_ID;
                        parentDoc.head.appendChild(styleEl);
                    }
                    styleEl.innerHTML = nightCss;
                } else {
                    parentDoc.body.classList.remove("astrallis-mode");
                    parentDoc.body.classList.remove("night-mode");
                    parentDoc.body.classList.add("day-mode");
                    if (parentDoc.documentElement) {
                        parentDoc.documentElement.classList.remove("astrallis-mode");
                        parentDoc.documentElement.classList.remove("night-mode");
                        parentDoc.documentElement.classList.add("day-mode");
                    }
                    let dayStyleEl = parentDoc.getElementById(THEME_STYLE_ID);
                    if (!dayStyleEl) {
                        dayStyleEl = parentDoc.createElement("style");
                        dayStyleEl.id = THEME_STYLE_ID;
                        parentDoc.head.appendChild(dayStyleEl);
                    }
                    
                    const dayCss = `
                        html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
                            background-color: #F5F9EC !important;
                            background: #F5F9EC !important;
                            color: #000000 !important;
                        }
                        header[data-testid="stHeader"] {
                            background: transparent !important;
                            border: none !important;
                            padding: 0px !important;
                            margin: 0px !important;
                            pointer-events: none !important;
                            z-index: 10000000 !important;
                        }
                        div[data-testid="stToolbar"] {
                            background: transparent !important;
                            pointer-events: none !important;
                        }
                        .block-container {
                            padding-top: 62px !important;
                            padding-bottom: 2rem !important;
                            padding-left: 1.25rem !important;
                            padding-right: 1.25rem !important;
                            max-width: 100% !important;
                            box-sizing: border-box !important;
                        }
                        @media (max-width: 768px) {
                            .block-container {
                                padding-top: 108px !important;
                                padding-left: 0.65rem !important;
                                padding-right: 0.65rem !important;
                            }
                        }
                        div[data-testid="stVerticalBlock"] {
                            gap: 0.35rem !important;
                        }
                        div[data-testid="stCustomComponentV1"]:has(iframe[height="0"]),
                        div.element-container:has(iframe[height="0"]) {
                            position: absolute !important;
                            opacity: 0 !important;
                            height: 0px !important;
                            min-height: 0px !important;
                            max-height: 0px !important;
                            margin: 0px !important;
                            padding: 0px !important;
                            overflow: hidden !important;
                            pointer-events: none !important;
                        }
                        section[data-testid="stSidebar"],
                        [data-testid="stSidebar"] {
                            z-index: 10000000 !important;
                        }
                        [data-testid="stExpandSidebarButton"],
                        [data-testid="stExpandSidebarButton"] button,
                        button[data-testid="stExpandSidebarButton"],
                        [data-testid="stSidebarCollapseButton"],
                        [data-testid="stSidebarCollapseButton"] button,
                        [data-testid="collapsedControl"],
                        [data-testid="collapsedControl"] button,
                        [data-testid="stSidebarCollapsedControl"],
                        [data-testid="stSidebarCollapsedControl"] button {
                            z-index: 10000005 !important;
                            pointer-events: auto !important;
                        }
                        .st-key-frozen_toolbelt_container,
                        div.st-key-frozen_toolbelt_container,
                        div[class*="st-key-frozen_toolbelt_container"] {
                            position: fixed !important;
                            top: 0px !important;
                            left: 0px !important;
                            right: 0px !important;
                            width: 100% !important;
                            z-index: 9999990 !important;
                            background: linear-gradient(90deg, #0A192F 0%, #0F2744 35%, #14355A 70%, #0B1C33 100%) !important;
                            background-color: #0A192F !important;
                            display: block !important;
                            visibility: visible !important;
                            opacity: 1 !important;
                            border-bottom: 2px solid #F59E0B !important;
                            box-shadow: 0 4px 18px rgba(5, 12, 24, 0.45) !important;
                            padding-top: 5px !important;
                            padding-bottom: 5px !important;
                            padding-left: 10px !important;
                            padding-right: 12px !important;
                            margin: 0px !important;
                            box-sizing: border-box !important;
                            transition: left 0.15s ease, width 0.15s ease !important;
                        }
                        .st-key-frozen_toolbelt_container div[data-testid="stHorizontalBlock"],
                        div[class*="st-key-frozen_toolbelt_container"] div[data-testid="stHorizontalBlock"] {
                            display: flex !important;
                            flex-direction: row !important;
                            align-items: center !important;
                            flex-wrap: nowrap !important;
                            width: 100% !important;
                            min-height: 34px !important;
                            visibility: visible !important;
                            opacity: 1 !important;
                            gap: 6px !important;
                            margin: 0 !important;
                            padding: 0 !important;
                            overflow: visible !important;
                        }
                        .st-key-frozen_toolbelt_container div[data-testid="column"],
                        div[class*="st-key-frozen_toolbelt_container"] div[data-testid="column"] {
                            min-width: 0 !important;
                            padding-left: 2px !important;
                            padding-right: 2px !important;
                            display: flex !important;
                            align-items: center !important;
                            visibility: visible !important;
                            opacity: 1 !important;
                        }
                        .st-key-frozen_toolbelt_container button {
                            padding: 2px 4px !important;
                            font-size: 12px !important;
                            font-weight: 700 !important;
                            white-space: nowrap !important;
                            overflow: hidden !important;
                            text-overflow: ellipsis !important;
                            min-height: 33px !important;
                            height: 33px !important;
                            background: #FFFFFF !important;
                            color: #000000 !important;
                            border: 1.5px solid #CBD5E1 !important;
                            border-radius: 6px !important;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
                        }
                        .st-key-frozen_toolbelt_container button * {
                            color: #000000 !important;
                            font-weight: 700 !important;
                        }
                        .st-key-frozen_toolbelt_container button.sidebar-toggle-btn,
                        .st-key-frozen_toolbelt_container button.header-hide-btn,
                        .st-key-frozen_toolbelt_container button#top_bar_header_hide_btn,
                        .st-key-frozen_toolbelt_container .sidebar-toggle-btn,
                        .st-key-frozen_toolbelt_container .header-hide-btn {
                            background: rgba(255, 255, 255, 0.22) !important;
                            color: #FFFFFF !important;
                            border: 1.5px solid rgba(255, 255, 255, 0.75) !important;
                            border-radius: 6px !important;
                            width: 34px !important;
                            min-width: 34px !important;
                            max-width: 34px !important;
                            height: 32px !important;
                            min-height: 32px !important;
                            max-height: 32px !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            padding: 0 !important;
                            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
                            cursor: pointer !important;
                            line-height: 1 !important;
                        }
                        .st-key-frozen_toolbelt_container button.sidebar-toggle-btn *,
                        .st-key-frozen_toolbelt_container button.header-hide-btn *,
                        .st-key-frozen_toolbelt_container button#top_bar_header_hide_btn *,
                        .st-key-frozen_toolbelt_container .sidebar-toggle-btn *,
                        .st-key-frozen_toolbelt_container .header-hide-btn * {
                            color: #FFFFFF !important;
                        }
                        .st-key-frozen_toolbelt_container button.sidebar-toggle-btn:hover,
                        .st-key-frozen_toolbelt_container button.header-hide-btn:hover,
                        .st-key-frozen_toolbelt_container button#top_bar_header_hide_btn:hover,
                        .st-key-frozen_toolbelt_container .sidebar-toggle-btn:hover,
                        .st-key-frozen_toolbelt_container .header-hide-btn:hover {
                            background: rgba(255, 255, 255, 0.38) !important;
                            border-color: #FFFFFF !important;
                            color: #FFFFFF !important;
                        }
                        .st-key-hdr_top_prev_mod_btn button,
                        .st-key-hdr_top_next_mod_btn button,
                        .st-key-hdr_top_prev_tab_btn button,
                        .st-key-hdr_top_next_tab_btn button {
                            font-size: 14px !important;
                            font-weight: 900 !important;
                            color: #0284C7 !important;
                            padding: 0px 2px !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            background: #FFFFFF !important;
                        }
                        .st-key-hdr_top_prev_mod_btn button *,
                        .st-key-hdr_top_next_mod_btn button *,
                        .st-key-hdr_top_prev_tab_btn button *,
                        .st-key-hdr_top_next_tab_btn button * {
                            color: #0284C7 !important;
                            font-weight: 900 !important;
                        }
                        .st-key-frozen_toolbelt_container button:hover {
                            background: #F0F7FF !important;
                            border-color: #005fa8 !important;
                            color: #000000 !important;
                        }
                        .st-key-frozen_toolbelt_container button[kind="primary"],
                        .st-key-frozen_toolbelt_container button[data-testid="baseButton-primary"] {
                            background: #E0F2FE !important;
                            border: 2px solid #005fa8 !important;
                            color: #000000 !important;
                        }
                        .st-key-frozen_toolbelt_container button[kind="primary"] *,
                        .st-key-frozen_toolbelt_container button[data-testid="baseButton-primary"] * {
                            color: #000000 !important;
                        }
                        .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] {
                            margin: 0px !important;
                            padding: 0px !important;
                        }
                        .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] > div,
                        .st-key-frozen_toolbelt_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
                            min-height: 34px !important;
                            height: 34px !important;
                            border-radius: 6px !important;
                            border: 1.5px solid #CBD5E1 !important;
                            background: #FFFFFF !important;
                            font-weight: 750 !important;
                            font-size: 12.5px !important;
                            color: #0F172A !important;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
                            display: flex !important;
                            align-items: center !important;
                        }
                        div[data-testid="stSelectboxVirtualDropdown"],
                        [data-testid="stSelectboxVirtualDropdown"],
                        div[data-baseweb="popover"],
                        div[data-baseweb="menu"] {
                            z-index: 10000030 !important;
                            border-radius: 8px !important;
                            border: 1.5px solid #F59E0B !important;
                            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5) !important;
                        }
                        div[data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
                        div[data-testid="stSelectboxVirtualDropdown"] div[class*="e1fp86qc5"],
                        div[role="listbox"],
                        ul[role="listbox"],
                        div[data-baseweb="popover"] ul,
                        div[data-baseweb="menu"] ul {
                            overflow-y: auto !important;
                            overflow-x: hidden !important;
                            max-height: min(400px, 70vh) !important;
                            overscroll-behavior: contain !important;
                            pointer-events: auto !important;
                            -webkit-overflow-scrolling: touch !important;
                        }
                        /* Dynamic header clearance */
                        .st-key-top_frozen_header_container {
                            border: none !important;
                            box-shadow: none !important;
                            padding: 0px !important;
                            margin: 0px 0px 4px 0px !important;
                            background: transparent !important;
                        }
                        [data-testid="stSidebar"], section[data-testid="stSidebar"],
                        [data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"],
                        [data-testid="stSidebarResizer"],
                        [data-testid="stSidebar"] div[class*="eelgd2m"],
                        [data-testid="stSidebar"] div[style*="col-resize"] {
                            background-color: #EBF5E4 !important;
                            background: #EBF5E4 !important;
                            border-right: 1.5px solid #C8DEC0 !important;
                        }
                        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b,
                        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
                            color: #000000 !important;
                        }
                        section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
                        section[data-testid="stSidebar"] .stRadio label,
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
                        div[data-testid="stRadio"] label {
                            background: #FFFFFF !important;
                            border: 1.5px solid #CBDCB8 !important;
                            color: #000000 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p {
                            color: #000000 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
                            background: #F4F8EC !important;
                            border-color: #4D7C0F !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"],
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {
                            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%) !important;
                            border: 2px solid #4D7C0F !important;
                            box-shadow: 0 4px 14px rgba(77, 124, 15, 0.2) !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p,
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) p {
                            color: #000000 !important;
                            font-weight: 900 !important;
                        }
                        h1, h2, h3, h4, h5, h6 {
                            color: #000000 !important;
                            font-weight: 900 !important;
                        }
                        p, span, li, a, caption, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
                            color: #000000 !important;
                            font-weight: 600 !important;
                        }
                        strong, b {
                            color: #000000 !important;
                            font-weight: 900 !important;
                        }
                        label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
                            color: #000000 !important;
                            font-weight: 800 !important;
                        }
                        input, textarea, select,
                        div[data-baseweb="input"] input,
                        div[data-baseweb="base-input"] input,
                        div[data-baseweb="input"] {
                            background-color: #FFFFFF !important;
                            color: #000000 !important;
                            -webkit-text-fill-color: #000000 !important;
                            border: 1.5px solid #CBDCB8 !important;
                            border-radius: 8px !important;
                            font-weight: 700 !important;
                        }
                        div[data-baseweb="select"] > div {
                            background-color: #FFFFFF !important;
                            color: #000000 !important;
                            border: 1.5px solid #CBDCB8 !important;
                            border-radius: 8px !important;
                            font-weight: 700 !important;
                        }
                        div[data-baseweb="select"] * {
                            color: #000000 !important;
                        }
                        header.top-nav-bar {
                            background: #FFFFFF !important;
                            border-color: #CBDCB8 !important;
                            border-bottom: 3.5px solid #65A30D !important;
                            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.06) !important;
                        }
                        .top-nav-bar * {
                            color: #000000 !important;
                        }
                        .gla-info-strip {
                            background: #E2F0D9 !important;
                            border: 1.5px solid #A8D08D !important;
                            color: #000000 !important;
                        }
                        .gla-info-strip * {
                            color: #000000 !important;
                        }
                        .gla-info-strip b {
                            color: #000000 !important;
                            font-weight: 900 !important;
                        }
                        .gla-active-tag {
                            color: #000000 !important;
                            background: #C5E0B4 !important;
                            border: 1px solid #70AD47 !important;
                            font-weight: 800 !important;
                        }
                        .gla-tile-belt {
                            background: #FFFFFF !important;
                            border: 1px solid #CBD5E1 !important;
                            border-radius: 6px !important;
                            padding: 2px 4px !important;
                        }
                        div[data-testid="column"]:has(.gla-tile-box) {
                            min-height: 52px !important;
                            height: 52px !important;
                            padding: 0 !important;
                            margin: 0 !important;
                        }
                        div[data-testid="column"]:has(.gla-tile-box) > div[data-testid="stVerticalBlock"] {
                            gap: 0 !important;
                            height: 52px !important;
                            min-height: 52px !important;
                        }
                        div[data-testid="column"]:has(.gla-tile-box) div[data-testid="stElementContainer"] {
                            margin: 0 !important;
                            padding: 0 !important;
                        }
                        div[data-testid="stHorizontalBlock"]:has(.gla-tile-box) {
                            min-height: 52px !important;
                            margin-top: 4px !important;
                            margin-bottom: 12px !important;
                            position: relative !important;
                            clear: both !important;
                        }
                        .gla-tile-box {
                            width: 100% !important;
                            height: 48px !important;
                            position: relative !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            box-sizing: border-box !important;
                        }
                        .gla-btn-tile {
                            background-color: #FFFFFF !important;
                            border: 1.5px solid #CBD5E1 !important;
                            border-radius: 8px !important;
                            width: 100% !important;
                            height: 48px !important;
                            min-height: 48px !important;
                            max-height: 48px !important;
                            padding: 3px 2px !important;
                            box-sizing: border-box !important;
                            display: flex !important;
                            flex-direction: column !important;
                            align-items: center !important;
                            justify-content: center !important;
                            cursor: pointer !important;
                            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
                            transition: all 0.15s ease-in-out !important;
                            text-align: center !important;
                            margin: 0 auto !important;
                        }
                        div[data-testid="column"]:has(.gla-tile-box):hover .gla-btn-tile,
                        .gla-btn-tile:hover {
                            background-color: #F0FDF4 !important;
                            border-color: #16A34A !important;
                            transform: translateY(-1px) !important;
                            box-shadow: 0 3px 8px rgba(22, 163, 74, 0.2) !important;
                        }
                        .gla-tile-box.gla-active-tile .gla-btn-tile,
                        .gla-btn-tile.active {
                            background-color: #FEF3C7 !important;
                            border: 2px solid #D97706 !important;
                            box-shadow: 0 0 10px rgba(217, 119, 6, 0.4) !important;
                        }
                        .gla-btn-tile img {
                            width: 20px !important;
                            height: 20px !important;
                            max-width: 20px !important;
                            max-height: 20px !important;
                            object-fit: contain !important;
                            display: block !important;
                            margin: 0 auto !important;
                        }
                        .gla-btn-tile span {
                            color: #0F172A !important;
                            font-weight: 750 !important;
                            font-size: 10px !important;
                            line-height: 1.2 !important;
                            margin-top: 2px !important;
                            white-space: nowrap !important;
                            overflow: hidden !important;
                            text-overflow: ellipsis !important;
                            display: block !important;
                            width: 100% !important;
                            text-align: center !important;
                        }
                        .active-profile-pill {
                            background: #EDF4E2 !important;
                            border: 1.5px solid #4D7C0F !important;
                            color: #000000 !important;
                        }
                        .active-profile-pill * {
                            color: #000000 !important;
                        }
                        .header-sub-pill {
                            background: #F4F8EC !important;
                            border: 1.5px solid #CBDCB8 !important;
                            color: #000000 !important;
                        }
                        .header-sub-pill * {
                            color: #000000 !important;
                        }
                        .header-sub-pill b {
                            color: #000000 !important;
                        }
                        .theme-select-box {
                            background: #FFFFFF !important;
                            border-color: #65A30D !important;
                        }
                        .theme-select-box select, .theme-select-box b, .theme-select-box span {
                            color: #000000 !important;
                        }
                        .theme-select-box option {
                            background: #FFFFFF !important;
                            color: #000000 !important;
                        }
                        .digital-hud {
                            background: #FFFFFF !important;
                            border: 1.5px solid #CBDCB8 !important;
                        }
                        .digital-hud * {
                            color: #000000 !important;
                        }
                        .hud-pill {
                            background: #F4F8EC !important;
                            border: 1.5px solid #CBDCB8 !important;
                            color: #000000 !important;
                        }
                        .hud-pill b, .hud-pill strong {
                            color: #365314 !important;
                            font-weight: 900 !important;
                        }
                        .rule-card, .vastu-card {
                            background: #FFFFFF !important;
                            border: 1.5px solid #CBDCB8 !important;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
                            color: #000000 !important;
                        }
                        .rule-card *, .vastu-card * {
                            color: #000000 !important;
                        }
                        div[data-testid="stExpander"] {
                            background: #FFFFFF !important;
                            border: 1.5px solid #CBDCB8 !important;
                            color: #000000 !important;
                        }
                        div[data-testid="stExpander"] * {
                            color: #000000 !important;
                        }
                        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
                            color: #000000 !important;
                            font-weight: 900 !important;
                        }
                        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
                            color: #000000 !important;
                            font-weight: 850 !important;
                        }
                        [data-testid="stMetric"] {
                            background: #FFFFFF !important;
                            border: 1.5px solid #CBDCB8 !important;
                        }
                        [data-testid="stTable"], [data-testid="stTable"] * {
                            background-color: #FFFFFF !important;
                            color: #000000 !important;
                        }
                        [data-testid="stTable"] th {
                            background-color: #EDF4E2 !important;
                            color: #000000 !important;
                            font-weight: 900 !important;
                        }
                        button[kind="secondary"] {
                            background-color: #FFFFFF !important;
                            color: #1E293B !important;
                            border: 1.5px solid #CBD5E1 !important;
                            border-radius: 8px !important;
                            font-weight: 700 !important;
                            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
                        }
                        button[kind="secondary"] * {
                            border: none !important;
                            background: transparent !important;
                            background-color: transparent !important;
                            color: inherit !important;
                            font-weight: 700 !important;
                        }
                        button[kind="secondary"]:hover {
                            background-color: #EFF6FF !important;
                            border-color: #2563EB !important;
                            color: #1D4ED8 !important;
                        }
                        /* Tabs Day Mode - Multi-color tabs */
                        [data-testid="stTabs"] [data-baseweb="tab-list"] {
                            background: #F4F8EC !important;
                            border: 1.5px solid #CBDCB8 !important;
                            border-radius: 10px !important;
                            padding: 4px 6px !important;
                            gap: 4px !important;
                        }
                        [data-testid="stTabs"] button[role="tab"] {
                            border-radius: 8px !important;
                            font-weight: 800 !important;
                            font-size: 0.88rem !important;
                            padding: 6px 14px !important;
                            margin: 2px 3px !important;
                            transition: all 0.2s ease !important;
                        }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 1) { background: #FFF1F2 !important; color: #9F1239 !important; border: 1.5px solid #FECDD3 !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 1)[aria-selected="true"] { background: linear-gradient(135deg, #E11D48 0%, #BE123C 100%) !important; color: #FFFFFF !important; border: 1.5px solid #9F1239 !important; box-shadow: 0 4px 14px rgba(225, 29, 72, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 2) { background: #EFF6FF !important; color: #1D4ED8 !important; border: 1.5px solid #BFDBFE !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 2)[aria-selected="true"] { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important; color: #FFFFFF !important; border: 1.5px solid #1E40AF !important; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 3) { background: #ECFDF5 !important; color: #047857 !important; border: 1.5px solid #A7F3D0 !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 3)[aria-selected="true"] { background: linear-gradient(135deg, #059669 0%, #047857 100%) !important; color: #FFFFFF !important; border: 1.5px solid #065F46 !important; box-shadow: 0 4px 14px rgba(5, 150, 105, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 4) { background: #FEF3C7 !important; color: #92400E !important; border: 1.5px solid #FDE68A !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 4)[aria-selected="true"] { background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important; color: #FFFFFF !important; border: 1.5px solid #78350F !important; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 5) { background: #FFF7ED !important; color: #C2410C !important; border: 1.5px solid #FFEDD5 !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 5)[aria-selected="true"] { background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important; color: #FFFFFF !important; border: 1.5px solid #9A3412 !important; box-shadow: 0 4px 14px rgba(234, 88, 12, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 6) { background: #FAF5FF !important; color: #6B21A8 !important; border: 1.5px solid #E9D5FF !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 6)[aria-selected="true"] { background: linear-gradient(135deg, #7E22CE 0%, #6B21A8 100%) !important; color: #FFFFFF !important; border: 1.5px solid #581C87 !important; box-shadow: 0 4px 14px rgba(126, 34, 206, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 7) { background: #ECFEFF !important; color: #0E7490 !important; border: 1.5px solid #A5F3FC !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 7)[aria-selected="true"] { background: linear-gradient(135deg, #0891B2 0%, #0E7490 100%) !important; color: #FFFFFF !important; border: 1.5px solid #155E75 !important; box-shadow: 0 4px 14px rgba(8, 145, 178, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 8) { background: #FDF4FF !important; color: #86198F !important; border: 1.5px solid #F5D0FE !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 8)[aria-selected="true"] { background: linear-gradient(135deg, #C026D3 0%, #9333EA 100%) !important; color: #FFFFFF !important; border: 1.5px solid #701A75 !important; box-shadow: 0 4px 14px rgba(192, 38, 211, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 9) { background: #EEF2FF !important; color: #4338CA !important; border: 1.5px solid #C7D2FE !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 9)[aria-selected="true"] { background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important; color: #FFFFFF !important; border: 1.5px solid #312E81 !important; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 10) { background: #FFF1F2 !important; color: #BE185D !important; border: 1.5px solid #FBCFE8 !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 10)[aria-selected="true"] { background: linear-gradient(135deg, #DB2777 0%, #BE185D 100%) !important; color: #FFFFFF !important; border: 1.5px solid #9D174D !important; box-shadow: 0 4px 14px rgba(219, 39, 119, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 11) { background: #F0FDFA !important; color: #0F766E !important; border: 1.5px solid #99F6E4 !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 11)[aria-selected="true"] { background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%) !important; color: #FFFFFF !important; border: 1.5px solid #115E59 !important; box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35) !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 12) { background: #FFFBEB !important; color: #B45309 !important; border: 1.5px solid #FDE68A !important; }
                        [data-testid="stTabs"] button[role="tab"]:nth-child(12n + 12)[aria-selected="true"] { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important; color: #FFFFFF !important; border: 1.5px solid #B45309 !important; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35) !important; }
                        [data-testid="stChatMessage"] {
                            background: #FFFFFF !important;
                            border: 1.5px solid #CBDCB8 !important;
                            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
                            color: #000000 !important;
                        }
                        [data-testid="stChatMessage"] * {
                            color: #000000 !important;
                        }
                        [data-testid="stChatInput"] {
                            background-color: #FFFFFF !important;
                            border-color: #CBDCB8 !important;
                            color: #000000 !important;
                        }
                        div[style*="background:#050811"], div[style*="background: #050811"],
                        div[style*="background:#111827"], div[style*="background: #111827"],
                        div[style*="background:#0D1322"], div[style*="background: #0D1322"],
                        div[style*="background:#080C14"], div[style*="background: #080C14"],
                        div[style*="background:#0A0E1A"], div[style*="background: #0A0E1A"],
                        div[style*="background:#1E293B"], div[style*="background: #1E293B"],
                        div[style*="background:#1F2937"], div[style*="background: #1F2937"],
                        div[style*="background:#070A12"], div[style*="background: #070A12"],
                        div[style*="background:#0A1628"], div[style*="background: #0A1628"],
                        div[style*="background:#000000"], div[style*="background: #000000"],
                        div[style*="background: black"], div[style*="background:black"] {
                            background: #FFFFFF !important;
                            border-color: #CBDCB8 !important;
                            color: #000000 !important;
                        }
                        div[style*="color:#FFFFFF"], div[style*="color: #FFFFFF"],
                        div[style*="color:#ffffff"], div[style*="color: #ffffff"],
                        div[style*="color:#F8FAFC"], div[style*="color: #F8FAFC"],
                        div[style*="color:#E2E8F0"], div[style*="color: #E2E8F0"],
                        div[style*="color:#CBD5E1"], div[style*="color: #CBD5E1"],
                        span[style*="color:#FFFFFF"], span[style*="color: #FFFFFF"],
                        span[style*="color:#ffffff"], span[style*="color: #ffffff"],
                        span[style*="color:#F8FAFC"], span[style*="color: #F8FAFC"],
                        span[style*="color:#E2E8F0"], span[style*="color: #E2E8F0"],
                        span[style*="color:#CBD5E1"], span[style*="color: #CBD5E1"],
                        b[style*="color:#FFFFFF"], b[style*="color: #FFFFFF"],
                        b[style*="color:#ffffff"], b[style*="color: #ffffff"],
                        strong[style*="color:#FFFFFF"], strong[style*="color: #FFFFFF"],
                        strong[style*="color:#ffffff"], strong[style*="color: #ffffff"] {
                            color: #000000 !important;
                        }
                        /* Keep Parashara Header green with crisp white text */
                        .pl-box-header, .pl-box-header *, .pl-box-header span, .pl-box-header b {
                            background: linear-gradient(180deg, #388E3C 0%, #2E7D32 100%) !important;
                            color: #FFFFFF !important;
                            -webkit-text-fill-color: #FFFFFF !important;
                        }
                    `;
                    dayStyleEl.innerHTML = dayCss;
                }

                // Sync all select elements
                const selects = parentDoc.querySelectorAll("#software-theme-select");
                selects.forEach(function(sel) {
                    if (sel.value !== mode) {
                        sel.value = mode;
                    }
                });

                // Sync icon
                const icons = parentDoc.querySelectorAll("#theme-mode-icon, .theme-mode-icon");
                icons.forEach(function(ic) {
                    ic.innerText = (mode === "astrallis" ? "🔬" : (mode === "night" ? "🌙" : "☀️"));
                });
            }

            const handleThemeSwitch = function(themeMode) {
                if (parentDoc.body) {
                    delete parentDoc.body.dataset.appliedThemeMode;
                }
                applyTheme(themeMode);
            };

            parentWin.changeSoftwareTheme = handleThemeSwitch;
            window.changeSoftwareTheme = handleThemeSwitch;
            if (parentDoc.defaultView) {
                parentDoc.defaultView.changeSoftwareTheme = handleThemeSwitch;
            }

            const themeSelects = parentDoc.querySelectorAll("#software-theme-select");
            themeSelects.forEach(function(sel) {
                sel.onchange = function(e) {
                    handleThemeSwitch(sel.value);
                };
                if (!sel.dataset.themeBound) {
                    sel.dataset.themeBound = "true";
                    sel.addEventListener("change", function(e) {
                        handleThemeSwitch(e.target.value);
                    });
                }
            });

            // Master resolution: server session theme takes precedence, then localStorage, default to day
            const authoritativeTheme = (SERVER_THEME_MODE && SERVER_THEME_MODE !== "__ACTIVE_THEME_MODE__") 
                ? SERVER_THEME_MODE 
                : (localStorage.getItem("jyotish_theme_mode") || "day");
            applyTheme(authoritativeTheme);
        } catch (e) {
            console.error("Theme mode error:", e);
        }
    }

    function setupStickyTopHeader() {
        try {
            const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            if (!parentDoc) return;

            const stHeader = parentDoc.querySelector('header[data-testid="stHeader"]');
            if (stHeader) {
                stHeader.style.setProperty('background', 'transparent', 'important');
                stHeader.style.setProperty('background-color', 'transparent', 'important');
                stHeader.style.setProperty('border', 'none', 'important');
                stHeader.style.setProperty('pointer-events', 'none', 'important');
                stHeader.style.setProperty('height', '44px', 'important');
                stHeader.style.setProperty('min-height', '44px', 'important');
                stHeader.style.setProperty('max-height', '44px', 'important');
                stHeader.style.setProperty('z-index', '9999995', 'important');
            }

            const mainSec = parentDoc.querySelector('[data-testid="stMain"], section.main');
            if (mainSec) {
                mainSec.style.setProperty('overflow-y', 'auto', 'important');
                mainSec.style.setProperty('overflow-x', 'hidden', 'important');
                mainSec.style.setProperty('position', 'relative', 'important');
            }

            const frozenTb = parentDoc.querySelector('.st-key-frozen_toolbelt_container, [class*="st-key-frozen_toolbelt_container"]');
            if (frozenTb) {
                const sb = parentDoc.querySelector('[data-testid="stSidebar"], section[data-testid="stSidebar"]');
                const sbContent = sb ? sb.querySelector('[data-testid="stSidebarContent"]') : null;

                if (!window._jyotishResizeBound) {
                    window._jyotishResizeBound = true;
                    window.addEventListener('resize', setupStickyTopHeader);
                    if (window.parent && window.parent !== window) {
                        try { window.parent.addEventListener('resize', setupStickyTopHeader); } catch(e){}
                    }
                }

                if (mainSec && !mainSec.dataset.roBound && window.ResizeObserver) {
                    mainSec.dataset.roBound = "true";
                    const ro = new ResizeObserver(function() {
                        setupStickyTopHeader();
                    });
                    ro.observe(mainSec);
                    if (sb) ro.observe(sb);
                    if (sbContent) ro.observe(sbContent);
                }

                const clientW = parentDoc.documentElement.clientWidth || window.innerWidth;
                const isMobile = (clientW <= 768 || window.innerWidth <= 768);
                let isSidebarVisible = false;
                let leftPos = 0;
                let headerW = clientW;

                if (!isMobile && sb) {
                    const sbRect = sb.getBoundingClientRect();
                    const isExpanded = sb.getAttribute('aria-expanded') !== 'false' && (sbRect.width > 60 && sbRect.right > 60);
                    if (isExpanded) {
                        isSidebarVisible = true;
                        let edge = sbRect.right;
                        if (sbContent) {
                            const scRect = sbContent.getBoundingClientRect();
                            if (scRect.right > 60) {
                                edge = Math.min(edge, scRect.right);
                            }
                        }
                        const resizer = parentDoc.querySelector('[data-testid="stSidebarResizer"], [data-testid="stSidebar"] div[style*="col-resize"]');
                        if (resizer) {
                            const rzRect = resizer.getBoundingClientRect();
                            if (rzRect.left > 60 && rzRect.left < edge + 30) {
                                edge = Math.min(edge, rzRect.left);
                            }
                        }
                        // Seamless 0px contact with 1px overlap to eliminate sub-pixel gaps
                        leftPos = Math.max(0, Math.floor(edge) - 1);
                        headerW = Math.max(0, clientW - leftPos);
                    }
                }

                if (isMobile || !isSidebarVisible || leftPos >= clientW - 100) {
                    leftPos = 0;
                    headerW = clientW;
                }
                if (!headerW || headerW <= 100 || isNaN(headerW)) headerW = clientW;
                if (!leftPos || leftPos < 0 || isNaN(leftPos)) leftPos = 0;

                // Check if user has collapsed the header for full-screen mode
                const isHeaderCollapsed = (
                    parentDoc.body.classList.contains('header-collapsed') ||
                    localStorage.getItem('jyotish_header_collapsed') === 'true'
                );

                // Clean up any legacy injected hideBtn if present so it does not duplicate
                const oldHideBtn = parentDoc.getElementById('jyotish_header_hide_btn');
                if (oldHideBtn) {
                    oldHideBtn.remove();
                }

                // Header Show icon ( v ) floating on the screen when header is collapsed
                let floatPill = parentDoc.getElementById('jyotish_floating_header_pill');
                if (!floatPill) {
                    floatPill = parentDoc.createElement('div');
                    floatPill.id = 'jyotish_floating_header_pill';
                    parentDoc.body.appendChild(floatPill);
                }
                floatPill.innerHTML = '<span style="font-weight:900; font-size:15px; line-height:1; background:rgba(255,255,255,0.25); border-radius:50%; width:22px; height:22px; display:inline-flex; align-items:center; justify-content:center; border:1.5px solid #FFFFFF; margin-right:4px;">v</span> <span style="font-size:12px; font-weight:800; letter-spacing:0.3px;">हेडर दिखाएं</span>';
                floatPill.title = 'हेडर दिखाएं (Show Header v)';
                floatPill.onclick = function() {
                    const pW = (window.parent && window.parent.location) ? window.parent : window;
                    if (pW.__toggleJyotishHeader) {
                        pW.__toggleJyotishHeader();
                    } else if (window.__toggleJyotishHeader) {
                        window.__toggleJyotishHeader();
                    }
                };

                if (isHeaderCollapsed) {
                    parentDoc.body.classList.add('header-collapsed');
                    frozenTb.style.setProperty('display', 'none', 'important');
                    floatPill.style.display = 'flex';
                    floatPill.style.cssText = `
                        display: flex !important;
                        align-items: center;
                        gap: 6px;
                        position: fixed !important;
                        top: 8px !important;
                        right: 12px !important;
                        z-index: 99999999 !important;
                        background: linear-gradient(135deg, #0284C7, #0369A1) !important;
                        color: #FFFFFF !important;
                        padding: 5px 14px !important;
                        border-radius: 20px !important;
                        font-size: 13px !important;
                        font-weight: 800 !important;
                        box-shadow: 0 4px 16px rgba(0, 115, 207, 0.45) !important;
                        cursor: pointer !important;
                        user-select: none !important;
                        border: 1.5px solid rgba(255, 255, 255, 0.6) !important;
                        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
                    `;
                    floatPill.onmouseover = function() { this.style.transform = 'scale(1.05)'; };
                    floatPill.onmouseout = function() { this.style.transform = 'scale(1.0)'; };
                } else {
                    parentDoc.body.classList.remove('header-collapsed');
                    frozenTb.style.setProperty('display', 'block', 'important');
                    floatPill.style.display = 'none';
                }

                frozenTb.style.setProperty('position', 'fixed', 'important');
                frozenTb.style.setProperty('top', '0px', 'important');
                frozenTb.style.setProperty('z-index', '9999990', 'important');
                frozenTb.style.setProperty('left', leftPos + 'px', 'important');
                frozenTb.style.setProperty('width', headerW + 'px', 'important');
                if (!isHeaderCollapsed) {
                    frozenTb.style.setProperty('visibility', 'visible', 'important');
                    frozenTb.style.setProperty('opacity', '1', 'important');
                }
                frozenTb.style.setProperty('padding-top', '5px', 'important');
                frozenTb.style.setProperty('padding-bottom', '5px', 'important');
                frozenTb.style.setProperty('padding-right', '10px', 'important');
                frozenTb.style.setProperty('margin', '0px', 'important');
                frozenTb.style.setProperty('box-sizing', 'border-box', 'important');
                frozenTb.style.setProperty('transition', 'none', 'important');

                if (isMobile) {
                    frozenTb.style.setProperty('padding-left', '6px', 'important');
                } else if (isSidebarVisible) {
                    frozenTb.style.setProperty('padding-left', '8px', 'important');
                } else {
                    frozenTb.style.setProperty('padding-left', '8px', 'important');
                }

                const isNight = parentDoc.body.classList.contains('night-mode') || localStorage.getItem('jyotish_theme_mode') === 'night';
                const isAstrallis = parentDoc.body.classList.contains('astrallis-mode') || localStorage.getItem('jyotish_theme_mode') === 'astrallis';
                const themeBg = isAstrallis ? '#070A12' : (isNight ? '#111827' : 'linear-gradient(90deg, #0A192F 0%, #0F2744 35%, #14355A 70%, #0B1C33 100%)');
                const themeBgColor = isAstrallis ? '#070A12' : (isNight ? '#111827' : '#0A192F');
                frozenTb.style.setProperty('background', themeBg, 'important');
                frozenTb.style.setProperty('background-color', themeBgColor, 'important');
                frozenTb.style.setProperty('border-bottom', isAstrallis ? '2.5px solid #00E5FF' : (isNight ? '2.5px solid #374151' : '2px solid #F59E0B'), 'important');
                frozenTb.style.setProperty('box-shadow', '0 4px 18px rgba(5, 12, 24, 0.45)', 'important');

                // Colorize resizer handle to match sidebar greenish theme
                const resizers = parentDoc.querySelectorAll('[data-testid="stSidebarResizer"], [data-testid="stSidebar"] div[style*="col-resize"], [data-testid="stSidebar"] div[class*="eelgd2m3"]');
                resizers.forEach(function(rz) {
                    rz.style.setProperty('background', '#EBF5E4', 'important');
                    rz.style.setProperty('background-color', '#EBF5E4', 'important');
                });

                // Position native sidebar expand button (>>) firmly at top: 6px, left: 8px inside Col 1 slot
                const expBtn = parentDoc.querySelector('button[data-testid="stExpandSidebarButton"], [data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"]');
                if (expBtn) {
                    expBtn.style.setProperty('position', 'fixed', 'important');
                    expBtn.style.setProperty('top', '6px', 'important');
                    expBtn.style.setProperty('left', '8px', 'important');
                    expBtn.style.setProperty('width', '34px', 'important');
                    expBtn.style.setProperty('height', '32px', 'important');
                    expBtn.style.setProperty('margin', '0px', 'important');
                    expBtn.style.setProperty('padding', '0px', 'important');
                    expBtn.style.setProperty('z-index', '10000005', 'important');
                    expBtn.style.setProperty('display', 'flex', 'important');
                    expBtn.style.setProperty('align-items', 'center', 'important');
                    expBtn.style.setProperty('justify-content', 'center', 'important');
                    expBtn.style.setProperty('transform', 'none', 'important');
                }

                // Ensure selectbox dropdown lists (Module, Tab, Menu) always open on top directly from the header & can scroll
                if (!parentDoc.__headerDropdownObserverBound) {
                    parentDoc.__headerDropdownObserverBound = true;
                    const elevateDropdowns = function() {
                        const dds = parentDoc.querySelectorAll('[data-testid="stSelectboxVirtualDropdown"], [data-baseweb="popover"], [data-baseweb="menu"]');
                        dds.forEach(function(d) {
                            d.style.setProperty('z-index', '10000030', 'important');
                        });
                        const scrollables = parentDoc.querySelectorAll('[data-testid="stSelectboxVirtualDropdown"] [role="listbox"], [data-testid="stSelectboxVirtualDropdown"] div[class*="e1fp86qc5"], [role="listbox"], ul[role="listbox"], [data-baseweb="popover"] ul');
                        scrollables.forEach(function(s) {
                            s.style.setProperty('z-index', '10000030', 'important');
                            s.style.setProperty('overflow-y', 'auto', 'important');
                            s.style.setProperty('overflow-x', 'hidden', 'important');
                            s.style.setProperty('max-height', 'min(400px, 70vh)', 'important');
                            s.style.setProperty('pointer-events', 'auto', 'important');
                        });
                    };
                    const mo = new MutationObserver(elevateDropdowns);
                    mo.observe(parentDoc.body, { childList: true, subtree: true });
                    elevateDropdowns();
                }
            }

            const blockContainer = parentDoc.querySelector('.block-container');
            if (blockContainer) {
                const isMobile = (window.innerWidth <= 768);
                const isHeaderCollapsed = (
                    parentDoc.body.classList.contains('header-collapsed') ||
                    localStorage.getItem('jyotish_header_collapsed') === 'true'
                );
                if (isHeaderCollapsed) {
                    blockContainer.style.setProperty('padding-top', isMobile ? '12px' : '16px', 'important');
                } else {
                    const defaultMinH = isMobile ? 104 : 52;
                    const tbH = (frozenTb && frozenTb.offsetHeight && frozenTb.offsetHeight > 30) ? frozenTb.offsetHeight : defaultMinH;
                    const padTop = Math.max(tbH + 12, defaultMinH + 12);
                    blockContainer.style.setProperty('padding-top', padTop + 'px', 'important');
                }
                blockContainer.style.setProperty('padding-left', isMobile ? '8px' : '16px', 'important');
                blockContainer.style.setProperty('padding-right', isMobile ? '8px' : '16px', 'important');
                blockContainer.style.setProperty('max-width', '100%', 'important');
                blockContainer.style.setProperty('box-sizing', 'border-box', 'important');
            }

        } catch(e) {
            console.error("Error freezing top header:", e);
        }
    }

    function toggleHeaderCollapse() {
        try {
            const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            const isCurrentlyCollapsed = parentDoc.body.classList.contains('header-collapsed') || localStorage.getItem('jyotish_header_collapsed') === 'true';
            if (isCurrentlyCollapsed) {
                parentDoc.body.classList.remove('header-collapsed');
                localStorage.setItem('jyotish_header_collapsed', 'false');
            } else {
                parentDoc.body.classList.add('header-collapsed');
                localStorage.setItem('jyotish_header_collapsed', 'true');
            }
            setupStickyTopHeader();
        } catch(e) {}
    }

    const pWin = (window.parent && window.parent.location) ? window.parent : window;
    pWin.__toggleJyotishHeader = toggleHeaderCollapse;
    window.__toggleJyotishHeader = toggleHeaderCollapse;

    function setupPWAandMobile() {
        try {
            const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            if (!parentDoc) return;
            const parentWin = (window.parent && window.parent.location) ? window.parent : window;
            const head = parentDoc.head || parentDoc.getElementsByTagName('head')[0];
            if (!head) return;

            // 1. PWA Manifest link
            if (!parentDoc.querySelector('link[rel="manifest"]')) {
                const manifestLink = parentDoc.createElement('link');
                manifestLink.rel = 'manifest';
                manifestLink.href = '/app/static/manifest.json';
                head.appendChild(manifestLink);
            }

            // 2. Mobile web app capable & Apple touch meta tags
            if (!parentDoc.querySelector('meta[name="apple-mobile-web-app-capable"]')) {
                const m1 = parentDoc.createElement('meta');
                m1.name = 'apple-mobile-web-app-capable';
                m1.content = 'yes';
                head.appendChild(m1);

                const m2 = parentDoc.createElement('meta');
                m2.name = 'apple-mobile-web-app-status-bar-style';
                m2.content = 'black-translucent';
                head.appendChild(m2);

                const m3 = parentDoc.createElement('meta');
                m3.name = 'apple-mobile-web-app-title';
                m3.content = 'ब्रह्महोरा ज्योतिष्';
                head.appendChild(m3);

                const m4 = parentDoc.createElement('meta');
                m4.name = 'mobile-web-app-capable';
                m4.content = 'yes';
                head.appendChild(m4);

                const m5 = parentDoc.createElement('meta');
                m5.name = 'theme-color';
                m5.content = '#0073CF';
                head.appendChild(m5);

                const iconLink = parentDoc.createElement('link');
                iconLink.rel = 'apple-touch-icon';
                iconLink.href = '/app/static/icon-192.png';
                head.appendChild(iconLink);
            }

            // 3. Register Service Worker on parent window navigator
            const winNav = (parentWin && parentWin.navigator) ? parentWin.navigator : navigator;
            if (winNav && 'serviceWorker' in winNav && !parentWin.__sw_registered) {
                parentWin.__sw_registered = true;
                winNav.serviceWorker.register('/app/static/sw.js').then(function(reg) {
                    console.log('BrahmaHora PWA active:', reg.scope);
                }).catch(function(e) {
                    winNav.serviceWorker.register('/static/sw.js').catch(function(){});
                });
            }

            // 4. Capture beforeinstallprompt for 1-Click Install
            if (!parentWin.__pwa_install_listener_attached) {
                parentWin.__pwa_install_listener_attached = true;
                parentWin.addEventListener('beforeinstallprompt', function(e) {
                    e.preventDefault();
                    parentWin.__pwa_deferred_prompt = e;
                    console.log('PWA Install prompt captured and ready');
                });
            }
        } catch(e) {}
    }

    setupPWAandMobile();
    setupSidebarToggle();
    setupLanguageBridge();
    setupThemeMode();
    setupStickyTopHeader();
    bindGpsButtons();
    resolveClientGPS();
    setupTabSwitcher();
    setInterval(function() {
        setupPWAandMobile();
        setupSidebarToggle();
        setupLanguageBridge();
        setupThemeMode();
        setupStickyTopHeader();
        bindGpsButtons();
        setupTabSwitcher();
        const cached = localStorage.getItem("jyotish_user_gps_loc") || sessionStorage.getItem("jyotish_user_gps_loc");
        if (cached) {
            updateLocationUI(cached);
        }
    }, 250);
})();
</script>
"""
components.html(client_bridge_code.replace("__ACTIVE_THEME_MODE__", cur_active_theme), height=0, width=0)

if st.session_state.get("trigger_browser_gps"):
    _t_target = st.session_state.pop("trigger_browser_gps", "nat_prashna")
    components.html(f"""
    <script>
    (function() {{
        try {{
            const pWin = (window.parent && window.parent.location) ? window.parent : window;
            if (pWin.requestDeviceGPS) {{
                pWin.requestDeviceGPS("{_t_target}");
            }} else if (window.requestDeviceGPS) {{
                window.requestDeviceGPS("{_t_target}");
            }} else {{
                const nav = (pWin.navigator && pWin.navigator.geolocation) ? pWin.navigator : navigator;
                if (nav && nav.geolocation) {{
                    nav.geolocation.getCurrentPosition(function(pos) {{
                        const lat = pos.coords.latitude;
                        const lon = pos.coords.longitude;
                        const u = new URL(pWin.location.href);
                        u.searchParams.set("gps_lat", lat.toFixed(5));
                        u.searchParams.set("gps_lon", lon.toFixed(5));
                        u.searchParams.set("gps_target", "{_t_target}");
                        pWin.location.href = u.toString();
                    }}, function(err) {{
                        let msg = "GPS अनुमति त्रुटि: " + err.message;
                        if (err.code === 1) {{
                            msg = "📍 डिवाइस GPS अनुमति अस्वीकृत (Location Permission Denied)। कृपया ब्राउज़र एड्रेस बार में लॉक (🔒) आइकन पर क्लिक करके लोकेशन को 'Allow' करें।";
                        }}
                        alert(msg);
                    }}, {{ enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }});
                }}
            }}
        }} catch(e) {{
            console.error("GPS trigger error:", e);
        }}
    }})();
    </script>
    """, height=0, width=0)






# -------------------------------------------------------------
# Dedicated Matching Cosmic Vedic Login Page
# -------------------------------------------------------------
def login_user_session(user_info: Dict[str, Any]):
    """Store authenticated user info in session state and update activity timestamp."""
    st.session_state.is_logged_in = True
    st.session_state.auth_user = user_info
    st.session_state.user_role = user_info.get("role", "jatak")
    st.session_state.user_role_display = user_info.get("role_display", "👤 जातक (General User)")
    st.session_state.user_email = (user_info.get("email") or user_info.get("username") or "").strip().lower()
    st.session_state.user_is_paid = user_info.get("is_paid", False)
    st.session_state.birth_name = user_info.get("name", "User")
    st.session_state["last_activity_ts"] = _tmod.time()
    st.session_state.recent_charts_history = []
    if "session_auth" in st.query_params:
        del st.query_params["session_auth"]
    if "session_timeout" in st.query_params:
        del st.query_params["session_timeout"]


def render_login_page():
    import textwrap


    if st.session_state.get("session_timed_out_banner", False):
        st.warning("⚠️ **सुरक्षा सत्र समाप्त (Session Timeout):** ३० मिनट तक कोई गतिविधि न होने के कारण सुरक्षा हेतु स्वतः लॉगआउट कर दिया गया है। कृपया पुनः लॉगिन करें।")
        st.session_state["session_timed_out_banner"] = False

    # Center-fit single card container layout
    _, col_card, _ = st.columns([1, 1.35, 1])

    with col_card:
        st.markdown('<div class="auth-card-wrapper">', unsafe_allow_html=True)
        # 1. Sacred Header: Logo + Sanskrit Shlok + Navagraha Shlok
        st.markdown(textwrap.dedent("""\
        <div style="text-align: center; margin-bottom: 14px;">
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
                <svg width="74" height="74" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 4px 10px rgba(217, 119, 6, 0.25));">
                    <circle cx="50" cy="50" r="46" stroke="#D97706" stroke-width="2.2" stroke-dasharray="4 2"/>
                    <circle cx="50" cy="50" r="38" stroke="#2563EB" stroke-width="1.8"/>
                    <polygon points="50,14 84,76 16,76" stroke="#D97706" stroke-width="2" fill="rgba(217, 119, 6, 0.08)"/>
                    <polygon points="50,86 84,24 16,24" stroke="#D97706" stroke-width="2" fill="rgba(217, 119, 6, 0.08)"/>
                    <polygon points="50,22 76,70 24,70" stroke="#2563EB" stroke-width="1.5" fill="none"/>
                    <polygon points="50,78 76,30 24,30" stroke="#2563EB" stroke-width="1.5" fill="none"/>
                    <circle cx="50" cy="50" r="7.5" fill="#D97706"/>
                    <circle cx="50" cy="50" r="2.8" fill="#FFFFFF"/>
                </svg>
            </div>
            <div style="font-size: 13.5px; font-weight: 800; color: #D97706; letter-spacing: 0.6px; margin-bottom: 3px;">
                ॐ श्री गणेशाय नमः • श्री नवग्रह प्रसन्न
            </div>
            <div style="font-size: 12.5px; font-weight: 600; color: #92400E; line-height: 1.5; margin-bottom: 8px; font-style: italic;">
                ॐ आदित्याय च सोमाय मङ्गलाय बुधाय च।<br>
                गुरुशुक्रशनिभ्यश्च राहवे केतवे नमः॥
            </div>
            <div style="font-size: 26px; font-weight: 900; color: #0F172A; letter-spacing: 1.5px; margin-bottom: 2px;">
                BRAMHAHORA
            </div>
            <div style="font-size: 11px; color: #64748B; font-weight: 600;">
                सर्वं खल्विदं ब्रह्म • प्रामाणिक वैदिक ज्योतिष अनुसंधान एवं निर्णय प्रणाली
            </div>
        </div>
        """), unsafe_allow_html=True)

        auth_view = st.session_state.get("auth_active_view", "login")

        # -------------------------------------------------------------
        # View 1: Default Clean Login (यूजरनेम, पासवर्ड, लॉगिन, लिंक्स)
        # -------------------------------------------------------------
        if auth_view == "login":
            with st.container(border=True):
                st.markdown(textwrap.dedent("""\
                <div style="text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">सुरक्षित प्रवेश (Sign In)</div>
                    <div style="font-size: 0.78rem; color: #64748B;">अपने पंजीकृत यूज़रनेम एवं पासवर्ड द्वारा लॉगिन करें।</div>
                </div>
                """), unsafe_allow_html=True)

                with st.form("clean_login_form"):
                    login_user = st.text_input(
                        "👤 यूज़रनेम / ईमेल (Username / Email)",
                        placeholder="उदा: user@jyotishos.com",
                        key="login_user_input_val"
                    )
                    login_pass = st.text_input(
                        "🔒 पासवर्ड (Password)",
                        placeholder="••••••••",
                        type="password",
                        key="login_pass_input_val"
                    )
                    login_submit = st.form_submit_button("🚀 लॉगिन करें (Sign In)", type="primary", use_container_width=True)

                if login_submit:
                    u_clean = login_user.strip().lower()
                    p_clean = login_pass.strip()
                    if not u_clean:
                        st.error("❌ कृपया यूज़रनेम अथवा ईमेल दर्ज करें।")
                    elif not p_clean:
                        st.error("❌ कृपया पासवर्ड दर्ज करें।")
                    else:
                        u_info = default_auth_service.authenticate(u_clean, p_clean)
                        if u_info:
                            login_user_session(u_info)
                            st.toast(f"✅ स्वागत है, {u_info.get('name')} ({u_info.get('role_display')})!", icon="🔮")
                            st.rerun()
                        else:
                            st.error("❌ अमान्य यूज़रनेम या पासवर्ड! कृपया सही क्रेडेंशियल्स दर्ज करें।")

                # Action Links: Forgot Password & Sign Up
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                col_f, col_s = st.columns(2)
                with col_f:
                    if st.button("🔑 पासवर्ड भूल गए?", key="link_goto_forgot", use_container_width=True):
                        st.session_state["auth_active_view"] = "forgot"
                        st.rerun()
                with col_s:
                    if st.button("📝 नया खाता बनाएं (Sign Up)", key="link_goto_signup", use_container_width=True):
                        st.session_state["auth_active_view"] = "signup"
                        st.rerun()

        # -------------------------------------------------------------
        # View 2: Sign Up (नया खाता पंजीकरण + त्वरित 1-क्लिक डेमो प्रवेश)
        # -------------------------------------------------------------
        elif auth_view == "signup":
            with st.container(border=True):
                st.markdown(textwrap.dedent("""\
                <div style="text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">📝 नया खाता पंजीकरण (Sign Up)</div>
                    <div style="font-size: 0.78rem; color: #64748B;">PBKDF2 क्रिप्टोग्राफी द्वारा सुरक्षित नया खाता बनाएं।</div>
                </div>
                """), unsafe_allow_html=True)

                with st.form("clean_signup_form"):
                    reg_name = st.text_input("पूरा नाम (Full Name)", placeholder="उदा: पं. शुभम तिवारी", key="signup_name_inp")
                    reg_email = st.text_input("ईमेल / यूज़रनेम (Email / Username)", placeholder="user@example.com", key="signup_email_inp")
                    reg_pass = st.text_input("पासवर्ड (Password - min 6 chars)", type="password", placeholder="••••••••", key="signup_pass_inp")
                    reg_role = st.selectbox(
                        "भूमिका (Account Role)",
                        [
                            "👤 जातक (General User - निःशुल्क)",
                            "🔮 ज्योतिषी (Professional Astrologer - समस्त ३० मॉड्यूल)"
                        ],
                        key="signup_role_inp"
                    )
                    reg_code = st.text_input("🎟️ परचेज कोड (वैकल्पिक, यदि उपलब्ध हो)", placeholder="उदा: BH-PRO-XXXX-YYYY", key="signup_code_inp")
                    signup_submit = st.form_submit_button("✨ नया खाता बनाएं (Create Account)", type="primary", use_container_width=True)

                if signup_submit:
                    target_role = "jyotishi" if "ज्योतिषी" in reg_role else "jatak"
                    p_code = reg_code.strip() if (reg_code and reg_code.strip()) else None
                    try:
                        ok, msg, uinfo = default_auth_service.register(
                            email=reg_email,
                            password=reg_pass,
                            name=reg_name,
                            role=target_role,
                            purchase_code=p_code
                        )
                    except Exception as _e:
                        ok, msg, uinfo = False, f"त्रुटि: {str(_e)}", None

                    if ok:
                        st.success(f"✅ {msg}")
                        if uinfo:
                            login_user_session(uinfo)
                            st.rerun()
                        else:
                            st.session_state["auth_active_view"] = "login"
                            st.rerun()
                    else:
                        st.error(f"❌ {msg}")

                # ⚡ 1-Click Demo Testing Access (INSIDE SIGNUP PAGE AS REQUESTED)
                st.markdown(textwrap.dedent("""\
                <div style="display:flex; align-items:center; margin: 14px 0 8px 0;">
                    <div style="flex:1; height:1px; background:#E2E8F0;"></div>
                    <span style="font-size:10.5px; font-weight:700; color:#94A3B8; padding:0 8px;">त्वरित 1-क्लिक परीक्षण (Demo Access)</span>
                    <div style="flex:1; height:1px; background:#E2E8F0;"></div>
                </div>
                """), unsafe_allow_html=True)

                d1, d2, d3 = st.columns(3)
                with d1:
                    if st.button("🔬 शोधकर्ता", use_container_width=True, key="demo_btn_res_c", help="सुपर-एडमिन: 30 मॉड्यूल, परचेज कोड सूची"):
                        u = default_auth_service.authenticate("researcher@jyotishos.com", "Research@2026") or default_auth_service.authenticate("shubham8jyotish@gmail.com", "Bahraich@123")
                        if u:
                            login_user_session(u)
                            st.rerun()
                with d2:
                    if st.button("🔮 ज्योतिषी", use_container_width=True, key="demo_btn_jyo_c", help="प्रो ज्योतिषी: 30 मॉड्यूल, क्लाइंट वॉल्ट"):
                        u = default_auth_service.authenticate("astrologer@jyotishos.com", "Astro@2026")
                        if u:
                            login_user_session(u)
                            st.rerun()
                with d3:
                    if st.button("👤 जातक", use_container_width=True, key="demo_btn_jat_c", help="निःशुल्क: कुण्डली, AI, पंचांग"):
                        u = default_auth_service.authenticate("jatak@jyotishos.com", "Jatak@2026")
                        if u:
                            login_user_session(u)
                            st.rerun()

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.button("← पहले से खाता है? लॉगिन करें (Back to Sign In)", key="back_to_login_s", use_container_width=True):
                    st.session_state["auth_active_view"] = "login"
                    st.rerun()

        # -------------------------------------------------------------
        # View 3: Forgot Password (पासवर्ड रीसेट एवं OTP)
        # -------------------------------------------------------------
        elif auth_view == "forgot":
            with st.container(border=True):
                st.markdown(textwrap.dedent("""\
                <div style="text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">🔑 पासवर्ड रीसेट (Reset Password)</div>
                    <div style="font-size: 0.78rem; color: #64748B;">ईमेल OTP सत्यापन द्वारा नया पासवर्ड बनाएं।</div>
                </div>
                """), unsafe_allow_html=True)

                f_email = st.text_input("पंजीकृत ईमेल दर्ज करें (Registered Email)", placeholder="user@example.com", key="forgot_email_inp")
                if st.button("📩 OTP सत्यापन कोड प्राप्त करें", use_container_width=True, key="btn_send_otp"):
                    if not f_email.strip():
                        st.error("❌ कृपया ईमेल पता दर्ज करें।")
                    else:
                        ok, msg, dev_otp = default_auth_service.request_reset_code(f_email.strip())
                        if ok:
                            st.session_state["active_reset_email"] = f_email.strip().lower()
                            st.success(f"✅ {msg}")
                            if dev_otp:
                                st.info(f"🔑 सुरक्षा कोड (OTP): **{dev_otp}**")
                        else:
                            st.error(f"❌ {msg}")

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                with st.form("clean_reset_form"):
                    f_otp = st.text_input("6-अंकीय OTP कोड (Enter OTP)", placeholder="उदा: 582194", key="forgot_otp_inp")
                    f_newpwd = st.text_input("नया पासवर्ड (New Password - min 6 chars)", type="password", placeholder="••••••••", key="forgot_newpwd_inp")
                    reset_submit = st.form_submit_button("🔒 नया पासवर्ड सहेजें (Reset)", type="primary", use_container_width=True)

                if reset_submit:
                    target_email = st.session_state.get("active_reset_email", f_email.strip().lower())
                    if not f_otp.strip():
                        st.error("❌ कृपया OTP कोड दर्ज करें।")
                    elif not f_newpwd.strip():
                        st.error("❌ कृपया नया पासवर्ड दर्ज करें।")
                    else:
                        ok, msg = default_auth_service.reset_password(target_email, f_otp.strip(), f_newpwd.strip())
                        if ok:
                            st.success(f"✅ {msg}")
                            st.balloons()
                            st.session_state["auth_active_view"] = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.button("← वापस लॉगिन पर जाएं (Back to Sign In)", key="back_to_login_f", use_container_width=True):
                    st.session_state["auth_active_view"] = "login"
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



# Initialize Session State
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    st.session_state.user_role = "jatak"
    st.session_state.user_role_display = "👤 जातक (General User)"
    st.session_state.user_email = ""
    st.session_state.user_is_paid = False


if "saved_charts" not in st.session_state:
    try:
        st.session_state.saved_charts = default_folder_manager.list_recent_charts(owner_email=st.session_state.get("user_email"))
    except TypeError:
        try:
            st.session_state.saved_charts = default_folder_manager.list_recent_charts()
        except Exception:
            st.session_state.saved_charts = []
    except Exception:
        st.session_state.saved_charts = []

if "gla_authenticated" not in st.session_state:
    st.session_state.gla_authenticated = False

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    """Returns the true current datetime in user's local timezone (defaults to IST, UTC+5:30)."""
    utc_now = datetime.now(timezone.utc)
    return (utc_now + timedelta(hours=tz_offset_hours)).replace(tzinfo=None)

# Process GPS coordinates from URL query parameters if passed by JS bridge
_qp = st.query_params
if "gps_lat" in _qp and "gps_lon" in _qp:
    try:
        _g_lat = float(_qp.get("gps_lat"))
        _g_lon = float(_qp.get("gps_lon"))
        _g_target = str(_qp.get("gps_target", "nat_prashna"))

        # Guard against cloud hosting datacenter coordinates (The Dalles, Oregon: ~45.5946, -121.1787)
        if (abs(_g_lat - 45.5946) < 0.8 and abs(_g_lon - (-121.1787)) < 0.8) or (_g_lat == 0.0 and _g_lon == 0.0):
            st.warning("⚠️ डिवाइस से वास्तविक GPS सिग्नल नहीं मिला (क्लाउड सर्वर का स्थान The Dalles, Oregon प्राप्त हुआ था)। कृपया डिवाइस पर GPS ऑन करें या शहर खोजें।")
        else:
            _g_loc = default_geocoding_service.reverse_geocode(_g_lat, _g_lon)
            _city_name = f"{_g_loc.city}, {_g_loc.state}" if _g_loc else f"{_g_lat:.4f}, {_g_lon:.4f}"
            _tz_offset = _g_loc.timezone_offset if _g_loc else 5.5

            if _g_target == "new_prashna":
                st.session_state.new_prashna_lat = _g_lat
                st.session_state.new_prashna_lon = _g_lon
                st.session_state.new_prashna_city = _city_name
                st.session_state.new_prashna_tz = _tz_offset
                if "new_prashna_city_input" in st.session_state:
                    st.session_state.new_prashna_city_input = _city_name
                if "new_prashna_lat_num" in st.session_state:
                    st.session_state.new_prashna_lat_num = _g_lat
                if "new_prashna_lon_num" in st.session_state:
                    st.session_state.new_prashna_lon_num = _g_lon
                if "new_prashna_tz_num" in st.session_state:
                    st.session_state.new_prashna_tz_num = _tz_offset
                if "prashna_new_res" in st.session_state:
                    st.session_state.prashna_new_res = None
                st.toast(f"📍 नवीन प्रश्न GPS स्थान: {_city_name} ({_g_lat:.4f}, {_g_lon:.4f})", icon="🛰️")
            else:
                st.session_state.birth_lat = _g_lat
                st.session_state.birth_lon = _g_lon
                st.session_state.birth_city = _city_name
                st.session_state.birth_tz = _tz_offset
                if "gla_city_query_input" in st.session_state:
                    st.session_state.gla_city_query_input = _city_name
                if "gla_lat_input" in st.session_state:
                    st.session_state.gla_lat_input = _g_lat
                if "gla_lon_input" in st.session_state:
                    st.session_state.gla_lon_input = _g_lon
                if "gla_tz_input" in st.session_state:
                    st.session_state.gla_tz_input = _tz_offset
                if "prashna_native_res" in st.session_state:
                    st.session_state.prashna_native_res = None
                if "active_prashna_res" in st.session_state:
                    st.session_state.active_prashna_res = None
                st.toast(f"📍 GPS स्थान प्राप्त: {_city_name} ({_g_lat:.4f}, {_g_lon:.4f})", icon="🛰️")

        del st.query_params["gps_lat"]
        del st.query_params["gps_lon"]
        if "gps_target" in st.query_params:
            del st.query_params["gps_target"]
    except Exception:
        pass

_init_now = get_live_local_now(st.session_state.get("birth_tz", 5.5))

# Pre-populate with live charts
if "gla_charts" not in st.session_state or not st.session_state.gla_charts:
    st.session_state.gla_charts = []

if "birth_name" not in st.session_state:
    st.session_state.birth_name = "डेमो जातक (Demo Profile)"
if "birth_date" not in st.session_state:
    st.session_state.birth_date = _init_now.date()
if "birth_time" not in st.session_state:
    st.session_state.birth_time = _init_now.time().replace(microsecond=0)
if "birth_lat" not in st.session_state:
    st.session_state.birth_lat = 28.6139
if "birth_lon" not in st.session_state:
    st.session_state.birth_lon = 77.2090
if "birth_city" not in st.session_state:
    st.session_state.birth_city = "New Delhi, Delhi, India"
if "birth_gender" not in st.session_state:
    st.session_state.birth_gender = "Male"


# -------------------------------------------------------------
# ⏳ 30-Minute Inactivity Auto-Logout Security Guard
# -------------------------------------------------------------
import time as _tmod

SESSION_INACTIVITY_LIMIT = 30 * 60  # 30 minutes in seconds = 1800s
_curr_ts = _tmod.time()

if st.session_state.get("is_logged_in", False):
    _is_client_timeout = (st.query_params.get("session_timeout") == "1")
    _last_active = st.session_state.get("last_activity_ts", _curr_ts)
    _elapsed = _curr_ts - _last_active

    if _is_client_timeout or (_elapsed > SESSION_INACTIVITY_LIMIT):
        st.session_state.is_logged_in = False
        st.session_state.gla_authenticated = False
        st.session_state.pop("auth_user", None)
        st.session_state.user_email = ""
        st.session_state.recent_charts_history = []
        st.session_state["session_timed_out_banner"] = True
        if "session_auth" in st.query_params:
            del st.query_params["session_auth"]
        if "session_timeout" in st.query_params:
            del st.query_params["session_timeout"]
        st.rerun()
    else:
        st.session_state["last_activity_ts"] = _curr_ts

# Gateway Check: If not logged in, render login screen
if not st.session_state.get("is_logged_in", False):
    render_login_page()
    st.stop()

# 🕒 Client-Side Inactivity Monitor (30 Minutes = 1800000ms)
components.html("""
<script>
(function() {
    const IDLE_LIMIT = 30 * 60 * 1000;
    let timer = null;

    function resetTimer() {
        if (timer) clearTimeout(timer);
        timer = setTimeout(function() {
            try {
                const p = (window.parent && window.parent !== window) ? window.parent : window;
                const url = new URL(p.location.href);
                url.searchParams.set("session_timeout", "1");
                url.searchParams.delete("session_auth");
                p.location.href = url.href;
            } catch(e) {}
        }, IDLE_LIMIT);
    }

    const events = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll'];
    events.forEach(evt => {
        window.addEventListener(evt, resetTimer, {passive: true});
        try {
            if (window.parent && window.parent !== window) {
                window.parent.addEventListener(evt, resetTimer, {passive: true});
            }
        } catch(e) {}
    });
    resetTimer();
})();
</script>
""", height=0, width=0)


# -------------------------------------------------------------
# App State & Multi-Language Configuration
# -------------------------------------------------------------
if "app_theme_mode" not in st.session_state:
    st.session_state.app_theme_mode = "day"

if "app_lang" not in st.session_state:
    st.session_state.app_lang = "General (जनरल)"

LANG_OPTIONS = [
    "General (जनरल)",
    "हिन्दी (Hindi)",
    "English (अंग्रेजी)",
    "தமிழ் (Tamil)",
    "తెలుగు (Telugu)",
    "ગુજરાતી (Gujarati)",
    "मराठी (Marathi)",
    "বাংলা (Bengali)"
]

# Ensure baseline variables
name = st.session_state.get("birth_name", "डेमो जातक")
init_b_date = st.session_state.get("birth_date", _init_now.date())
if isinstance(init_b_date, datetime):
    init_b_date = init_b_date.date()
if init_b_date < date(1950, 1, 1):
    init_b_date = date(1950, 1, 1)
elif init_b_date > date(2050, 12, 31):
    init_b_date = date(2050, 12, 31)
birth_d = init_b_date

birth_t = st.session_state.get("birth_time", _init_now.time().replace(microsecond=0))
latitude = float(st.session_state.get("birth_lat", 28.6139))
longitude = float(st.session_state.get("birth_lon", 77.2090))
default_city_name = st.session_state.get("birth_city", "New Delhi, Delhi, India")
tz_offset = float(st.session_state.get("birth_tz", 5.5))
confidence = st.session_state.get("birth_conf", "Exact")
ayanamsa = st.session_state.get("app_ayanamsa", "Lahiri")
node_type_val = "true" if "True" in str(st.session_state.get("app_node_type", "Mean")) else "mean"
house_system = st.session_state.get("app_house_system", "Whole Sign")
chart_style = st.session_state.get("app_chart_style", "North Indian (Diamond)")
pro_mode = st.session_state.get("app_pro_mode", True)

is_topocentric = bool(st.session_state.get("app_is_topocentric", False))
altitude_m = float(st.session_state.get("app_altitude", 0.0))

# Compute full baseline chart with all extensions
birth_profile = BirthData(
    name=name,
    birth_date=birth_d,
    birth_time=birth_t,
    latitude=latitude,
    longitude=longitude,
    timezone_offset=tz_offset,
    city=default_city_name,
    confidence=confidence,
    altitude=altitude_m,
    is_topocentric=is_topocentric
)

try:
    chart = default_chart_calculator.calculate_full_chart(
        birth_profile,
        ayanamsa_name=ayanamsa,
        house_system=house_system,
        node_type=node_type_val,
        topocentric_moon=is_topocentric,
        elevation=altitude_m
    )
except Exception:
    try:
        chart = default_chart_calculator.calculate_full_chart(
            birth_profile,
            ayanamsa_name=ayanamsa,
            house_system=house_system,
            topocentric_moon=is_topocentric,
            elevation=altitude_m
        )
    except Exception:
        try:
            chart = default_chart_calculator.calculate_chart(
                birth_profile,
                ayanamsa_name=ayanamsa,
                house_system=house_system
            )
        except Exception:
            chart = default_chart_calculator.calculate_chart(
                birth_profile,
                use_cache=False
            )

if getattr(chart, "engine_degraded", False) or (getattr(chart, "metadata", None) and getattr(chart.metadata, "engine_degraded", False)):
    st.warning("⚠️ **Warning: Planetary calculations are running in degraded fallback mode (PyEphem).** Professional astronomical precision may be reduced. Please ensure Swiss Ephemeris is active.")

if getattr(chart, "metadata", None):
    meta = chart.metadata
    from src.jyotish.ui.components.provenance import render_provenance_badge_html
    st.markdown(render_provenance_badge_html(chart, verified_rules_count=32), unsafe_allow_html=True)
    with st.expander("🌐 Astronomical Provenance & Metadata Details (Shastriya Pramana)", expanded=False):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Engine", meta.engine)
        c2.metric("Julian Day (UT)", f"{meta.jd_ut:.5f}")
        c3.metric("Delta T", f"{meta.delta_t_seconds:.2f}s")
        c4.metric("Ayanamsa", f"{meta.ayanamsa_name} ({meta.ayanamsa_value:.4f}°)")
        c5.metric("Coord Mode", getattr(chart, "calculation_mode", "Geocentric"))
        st.caption(f"Timezone: `{meta.timezone_iana}` | House System: `{meta.house_system}` | Ephemeris: `{meta.ephemeris_mode}` | Mode: `{getattr(chart, 'calculation_mode', 'Geocentric')}` (Moon Parallax: `{getattr(chart, 'moon_parallax_arcmin', 0.0):.2f}'`) | UTC: `{meta.utc_datetime}`")
affliction_engine = AfflictionEngine(chart)
vastu_engine = VastuJyotishEngine(chart)

# Helper function to render chart in selected style
from src.jyotish.ui.chart_renderer import render_aspect_orb_matrix_html

def render_chart_svg(c_obj: KundaliChart, chart_title: str, varga_code: str = "D1") -> str:
    if "South" in chart_style:
        return ChartRenderer.render_south_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    elif "East" in chart_style:
        return ChartRenderer.render_east_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    return ChartRenderer.render_north_indian_svg(c_obj, title=chart_title, varga_code=varga_code)

def get_varga_dignity_info(planet: str, sign_name: str, aff_eng: Optional[AfflictionEngine] = None) -> Tuple[str, int, str]:
    target_aff = aff_eng or affliction_engine
    text, css = target_aff.get_dignity(planet, sign_name)
    if css == "exalt":
        return "🌟 उच्च (Exalted)", 20, "परमोच्च बल एवं अत्यंत शुभ फल"
    elif css == "mool":
        return "💎 मूलत्रिकोण (Moolatrikona)", 18, "प्रबल शुभ एवं फलदायक"
    elif css == "own":
        return "👑 स्वराशि (Own Sign)", 15, "सशक्त एवं अनुकूल"
    elif css == "friend":
        return "🤝 मित्र राशि (Friend Sign)", 11, "मित्रवत एवं सहयोगी"
    elif css == "neutral":
        return "⚖️ सम राशि (Neutral)", 7, "तटस्थ / सामान्य फल"
    elif css == "enemy":
        return "⚔️ शत्रु राशि (Enemy Sign)", 4, "प्रतिरोधी एवं संघर्ष"
    elif css == "deb":
        return "⚠️ नीच (Debilitated)", 0, "कमजोर / उपाय आवश्यक"
    return "⚖️ सामान्य", 7, "सामान्य"

now_dt = get_live_local_now(st.session_state.get('birth_tz', 5.5))
current_time_str = now_dt.strftime("%d %b %Y, %I:%M %p")

# -------------------------------------------------------------
# 21 Vedic Astrology Modules Definitions
# -------------------------------------------------------------
if "English" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 Birth Chart (Kundali)",
        "🎯 Event Analysis (Events)",
        "🛡️ Afflictions & Remedies (Remedies)",
        "📊 Varga Grid (Vargas)",
        "🏛️ Vastu Astrology (Vastu)",
        "❓ Horary Chart (Prashna)",
        "⚖️ Planetary Strengths (Bala)",
        "🔱 Jaimini Astrology (Jaimini)",
        "⏱️ Dasha Systems (Dasha)",
        "🪐 Transit & Ashtakvarga (Transit)",
        "📐 KP Astrology (KP System)",
        "⏳ Auspicious Timing (Muhurta)",
        "☸️ Sudarshan Chakra (Sudarshan)",
        "📅 Solar Return (Varshaphal)",
        "⏳ Birth Time Rectification (BTR)",
        "💍 Kundali Matching (Matching)",
        "💬 Daivajna AI (AI Astrologer)",
        "📄 Kundali Reports (Reports)",
        "📚 Rules Library (Rules)",
        "🔍 Calculation Validation (Validation)",
        "⚡ Yogas & Doshas (Yog & Dosh)",
        "🔢 Numerology (Lo-Shu)",
        "📕 Lal Kitab (Lal Kitab)",
        "🍽️ Ayurvedic Diet (Diet)",
        "🤝 Relationships (Relations)",
        "🏥 Health & Disease (Health)",
        "🧬 Body & Physique (Physique)",
        "🕉️ Ishta Devata & Pooja (Pooja)",
        "🧘 Karma & Destiny (Karma)",
        "📅 Vedic Panchang (Panchang)",
        "📜 Classical Predictions (Predictions)",
        "✋ Palmistry & Samudrika (Palmistry)"
    ]
elif "Tamil" in st.session_state.app_lang or "தமிழ்" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 ஜாதகம் (Kundali)",
        "🎯 நிகழ்வு (Events)",
        "🛡️ பரிகாரம் (Remedies)",
        "📊 வர்க்க அட்டவணை (Vargas)",
        "🏛️ வாஸ்து (Vastu)",
        "❓ பிரசன்னம் (Prashna)",
        "⚖️ ஷட்பலம் (Bala)",
        "🔱 ஜெயமினி (Jaimini)",
        "⏱️ தசா முறை (Dasha)",
        "🪐 கோசாரம் (Transit)",
        "📐 கே.பி. ஜோதிடம் (KP)",
        "⏳ முகூர்த்தம் (Muhurta)",
        "☸️ சுதர்சனம் (Sudarshan)",
        "📅 வருட பலன் (Varshaphal)",
        "⏳ நேர திருத்தம் (BTR)",
        "💍 பொருத்தம் (Matching)",
        "💬 தசா AI (AI Astrologer)",
        "📄 அறிக்கை (Reports)",
        "📚 சாஸ்திர விதி (Rules)",
        "🔍 சரிபார்ப்பு (Validation)",
        "⚡ யோகம்-தோஷம் (Yog & Dosh)",
        "🔢 எண்கணிதம் (Numerology)",
        "📕 லால் கிதாப் (Lal Kitab)",
        "🍽️ உணவு முறை (Diet)",
        "🤝 உறவுகள் (Relations)",
        "🏥 உடல்நலம் (Health)",
        "🧬 உடலமைப்பு (Physique)",
        "🕉️ இஷ்ட தெய்வம் (Pooja)",
        "🧘 கர்ம பலன் (Karma)",
        "📅 பஞ்சாங்கம் (Panchang)",
        "📜 சாஸ்திர பலன் (Predictions)",
        "✋ கைரேகை ஜோதிடம் (Palmistry)"
    ]
elif "Telugu" in st.session_state.app_lang or "తెలుగు" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 జన్మ జాతకం (Kundali)",
        "🎯 సంఘటనలు (Events)",
        "🛡️ పరిహారాలు (Remedies)",
        "📊 వర్గ చక్రాలు (Vargas)",
        "🏛️ వాస్తు (Vastu)",
        "❓ ప్రశ్న జాతకం (Prashna)",
        "⚖️ షడ్బలం (Bala)",
        "🔱 జైమిని (Jaimini)",
        "⏱️ దశా విధానం (Dasha)",
        "🪐 గోచారం (Transit)",
        "📐 కె.పి. పద్ధతి (KP)",
        "⏳ ముహూర్తం (Muhurta)",
        "☸️ సుదర్శన చక్రం (Sudarshan)",
        "📅 వార్షిక ఫలం (Varshaphal)",
        "⏳ సమయ శోధన (BTR)",
        "💍 గుణ మేళాపకం (Matching)",
        "💬 దైవజ్ఞ AI (AI Astrologer)",
        "📄 నివేదిక (Reports)",
        "📚 నియమాల నిధి (Rules)",
        "🔍 ధృవీకరణ (Validation)",
        "⚡ యోగ-దోషాలు (Yog & Dosh)",
        "🔢 సంఖ్యాశాస్త్రం (Numerology)",
        "📕 లాల్ కితాబ్ (Lal Kitab)",
        "🍽️ ఆహార నియమాలు (Diet)",
        "🤝 సంబంధాలు (Relations)",
        "🏥 ఆరోగ్యం (Health)",
        "🧬 శరీర నిర్మాణం (Physique)",
        "🕉️ ఇష్ట దైవం (Pooja)",
        "🧘 కర్మఫలం (Karma)",
        "📅 పంచాంగం (Panchang)",
        "📜 శాస్త్రీయ ఫలితాలు (Predictions)",
        "✋ హస్తసాముద్రికం (Palmistry)"
    ]
elif "Gujarati" in st.session_state.app_lang or "ગુજરાતી" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 જન્મ કુંડળી (Kundali)",
        "🎯 ઘટના વિશ્લેષણ (Events)",
        "🛡️ દોષ અને ઉપાય (Remedies)",
        "📊 વર્ગ કોષ્ટક (Vargas)",
        "🏛️ વાસ્તુ જ્યોતિષ (Vastu)",
        "❓ પ્રશ્ન કુંડળી (Prashna)",
        "⚖️ ષડ્બળ (Bala)",
        "🔱 જૈમિની (Jaimini)",
        "⏱️ દશા પ્રણાલી (Dasha)",
        "🪐 ગોચર અને અષ્ટકવર્ગ (Transit)",
        "📐 કે.પી. પદ્ધતિ (KP)",
        "⏳ શુભ મુહૂર્ત (Muhurta)",
        "☸️ સુદર્શન ચક્ર (Sudarshan)",
        "📅 વર્ષફળ (Varshaphal)",
        "⏳ સમય સંશોધન (BTR)",
        "💍 મેળવણું (Matching)",
        "💬 જ્યોતિષ AI (AI Astrologer)",
        "📄 કુંડળી અહેવાલ (Reports)",
        "📚 નિયમ પુસ્તકાલય (Rules)",
        "🔍 ગણતરી ચકાસણી (Validation)",
        "⚡ દોષ-યોગ (Yog & Dosh)",
        "🔢 અંકશાસ્ત્ર (Numerology)",
        "📕 લાલ કિતાબ (Lal Kitab)",
        "🍽️ આહાર અને પથ્ય (Diet)",
        "🤝 સંબંધો (Relations)",
        "🏥 સ્વાસ્થ્ય (Health)",
        "🧬 શારીરિક ગઠન (Physique)",
        "🕉️ ઇષ્ટદેવ પૂજા (Pooja)",
        "🧘 કર્મફળ (Karma)",
        "📅 વૈદિક પંચાંગ (Panchang)",
        "📜 શાસ્ત્રીય ફલાદેશ (Predictions)",
        "✋ હસ્તરેખા વિજ્ઞાન (Palmistry)"
    ]
elif "Marathi" in st.session_state.app_lang or "मराठी" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 जन्म पत्रिका (Kundali)",
        "🎯 घटना विश्लेषण (Events)",
        "🛡️ दोष व उपाय (Remedies)",
        "📊 वर्ग तक्ता (Vargas)",
        "🏛️ वास्तु ज्योतिष (Vastu)",
        "❓ प्रश्न पत्रिका (Prashna)",
        "⚖️ षड्बल (Bala)",
        "🔱 जैमिनी (Jaimini)",
        "⏱️ दशा प्रणाली (Dasha)",
        "🪐 गोचर व अष्टकवर्ग (Transit)",
        "📐 के.पी. पद्धती (KP)",
        "⏳ शुभ मुहूर्त (Muhurta)",
        "☸️ सुदर्शन चक्र (Sudarshan)",
        "📅 वर्षफळ (Varshaphal)",
        "⏳ वेळ शोधन (BTR)",
        "💍 पत्रिका मिलन (Matching)",
        "💬 दैवज्ञ AI (AI Astrologer)",
        "📄 पत्रिका अहवाल (Reports)",
        "📚 नियम संग्रह (Rules)",
        "🔍 पडताळणी (Validation)",
        "⚡ योग व दोष (Yog & Dosh)",
        "🔢 अंकशास्त्र (Numerology)",
        "📕 लाल किताब (Lal Kitab)",
        "🍽️ त्रिदोष व आहार (Diet)",
        "🤝 नातेसंबंध (Relations)",
        "🏥 आरोग्य (Health)",
        "🧬 शारीरिक गठन (Physique)",
        "🕉️ इष्टदेवता पूजा (Pooja)",
        "🧘 कर्मफळ (Karma)",
        "📅 वैदिक पंचांग (Panchang)",
        "📜 शास्त्रीय फलादेश (Predictions)",
        "✋ हस्तरेषा विज्ञान (Palmistry)"
    ]
elif "Bengali" in st.session_state.app_lang or "বাংলা" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 জন্ম কুণ্ডলী (Kundali)",
        "🎯 ঘটনা বিশ্লেষণ (Events)",
        "🛡️ দোষ ও প্রতিকার (Remedies)",
        "📊 বর্গ তালিকা (Vargas)",
        "🏛️ বাস্তু জ্যোতিষ (Vastu)",
        "❓ প্রশ্ন কুণ্ডলী (Prashna)",
        "⚖️ ষড়্বল (Bala)",
        "🔱 জৈমিনী (Jaimini)",
        "⏱️ দশা পদ্ধতি (Dasha)",
        "🪐 গোচর ও অষ্টকবর্গ (Transit)",
        "📐 কে.পি. পদ্ধতি (KP)",
        "⏳ শুভ মুহূর্ত (Muhurta)",
        "☸️ সুদর্শন চক্র (Sudarshan)",
        "📅 বর্ষফল (Varshaphal)",
        "⏳ সময় সংশোধন (BTR)",
        "💍 কুণ্ডলী মিলন (Matching)",
        "💬 জ্যোতিষ AI (AI Astrologer)",
        "📄 রিপোর্ট (Reports)",
        "📚 শাস্ত্রীয় নিয়ম (Rules)",
        "🔍 গণনা প্রমাণ (Validation)",
        "⚡ দোষ-যোগ (Yog & Dosh)",
        "🔢 সংখ্যাতত্ত্ব (Numerology)",
        "📕 লাল কিতাব (Lal Kitab)",
        "🍽️ আহার ও স্বাস্থ্য (Diet)",
        "🤝 সম্পর্ক (Relations)",
        "🏥 স্বাস্থ্য (Health)",
        "🧬 শারীরিক গঠন (Physique)",
        "🕉️ ইষ্টদেবতা পূজা (Pooja)",
        "🧘 কর্মফল (Karma)",
        "📅 বৈদিক পঞ্জিকা (Panchang)",
        "📜 শাস্ত্রীয় ফলাফল (Predictions)",
        "✋ হস্তরেখা বিজ্ঞান (Palmistry)"
    ]
else:
    MODULE_OPTIONS = [
        "📜 जन्म कुण्डली (Kundali)",
        "🎯 घटना विश्लेषण (Events)",
        "🛡️ दोष व उपाय (Remedies)",
        "📊 वर्ग तालिका (Vargas)",
        "🏛️ वास्तु ज्योतिष (Vastu)",
        "❓ प्रश्न कुण्डली (Prashna)",
        "⚖️ षड्बल व भावबल (Bala)",
        "🔱 जैमिनी व उपग्रह (Jaimini)",
        "⏱️ दशा प्रणालियाँ (Dasha)",
        "🪐 गोचर व अष्टकवर्ग (Transit)",
        "📐 के.पी. ज्योतिष (KP System)",
        "⏳ शुभ मुहूर्त (Muhurta)",
        "☸️ सुदर्शन चक्र (Sudarshan)",
        "📅 ताजिक वर्षफल (Varshaphal)",
        "⏳ जन्म समय शोधन (BTR)",
        "💍 कुण्डली मिलान (Matching)",
        "💬 दैवज्ञ AI (AI Astrologer)",
        "📄 कुण्डली रिपोर्ट (Reports)",
        "📚 नियम बैंक (Rules Library)",
        "🔍 गणना सत्यापन (Validation)",
        "⚡ योग व दोष (Yog & Dosh)",
        "🔢 अंकशास्त्र (Numerology)",
        "📕 लाल किताब (Lal Kitab)",
        "🍽️ त्रिदोष व आहार (Diet)",
        "🤝 संबंध व स्वजन (Relations)",
        "🏥 स्वास्थ्य व रोग (Health)",
        "🧬 शारीरिक गठन (Physique)",
        "🕉️ इष्टदेवता व पूजा (Pooja)",
        "🧘 व्यक्तित्व व कर्मफल (Karma)",
        "📅 वैदिक पञ्चाङ्ग (Panchang)",
        "📜 शास्त्रीय फलादेश (Predictions)",
        "✋ हस्तरेखा व सामुद्रिक (Palmistry)"
    ]


def render_styled_meters_html(items, max_val=20, is_dark=False):
    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "#374151" if is_dark else "#E2E8F0"
    track_bg = "#1F2937" if is_dark else "#F1F5F9"
    track_bdr = "#374151" if is_dark else "#CBD5E1"
    val_color = "#F8FAFC" if is_dark else "#0F172A"
    dim_color = "#94A3B8" if is_dark else "#64748B"

    rows_html = []
    for item in items:
        p_name = item["name"]
        sym = item.get("symbol", p_name)
        p_color = item.get("color", "#2563EB")
        d_lbl = item.get("dignity", "")
        score = float(item.get("score", 0.0))
        pct = min(100.0, max(4.0, (score / max_val) * 100.0))

        if "उच्च" in d_lbl or score >= 17:
            bar_grad = "linear-gradient(90deg, #10B981 0%, #059669 100%)"
            b_bg, b_fg, b_bdr = ("#064E3B", "#6EE7B7", "#059669") if is_dark else ("#DCFCE7", "#166534", "#86EFAC")
        elif "मूलत्रिकोण" in d_lbl or "स्वराशि" in d_lbl or score >= 14:
            bar_grad = "linear-gradient(90deg, #3B82F6 0%, #1D4ED8 100%)"
            b_bg, b_fg, b_bdr = ("#1E3A8A", "#93C5FD", "#2563EB") if is_dark else ("#DBEAFE", "#1D4ED8", "#93C5FD")
        elif "मित्र" in d_lbl or score >= 11:
            bar_grad = "linear-gradient(90deg, #06B6D4 0%, #0284C7 100%)"
            b_bg, b_fg, b_bdr = ("#164E63", "#7DD3FC", "#0284C7") if is_dark else ("#E0F2FE", "#0284C7", "#7DD3FC")
        elif "सम" in d_lbl or score >= 8:
            bar_grad = "linear-gradient(90deg, #F59E0B 0%, #D97706 100%)"
            b_bg, b_fg, b_bdr = ("#78350F", "#FDE68A", "#D97706") if is_dark else ("#FEF3C7", "#92400E", "#FCD34D")
        elif "शत्रु" in d_lbl or score >= 5:
            bar_grad = "linear-gradient(90deg, #F97316 0%, #EA580C 100%)"
            b_bg, b_fg, b_bdr = ("#7C2D12", "#FED7AA", "#EA580C") if is_dark else ("#FFEDD5", "#C2410C", "#FDBA74")
        else:
            bar_grad = "linear-gradient(90deg, #EF4444 0%, #DC2626 100%)"
            b_bg, b_fg, b_bdr = ("#7F1D1D", "#FCA5A5", "#DC2626") if is_dark else ("#FEE2E2", "#991B1B", "#FCA5A5")

        dignity_badge_html = f'<div style="width:84px; text-align:center;"><span style="background:{b_bg}; color:{b_fg}; border:1px solid {b_bdr}; border-radius:4px; padding:1px 5px; font-size:10px; font-weight:800; display:inline-block; width:100%; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">{d_lbl}</span></div>' if d_lbl else ''

        row = f'''<div style="display:flex; align-items:center; gap:8px; margin-bottom:7px;">
  <div style="width:105px; font-weight:800; font-size:12px; color:{p_color}; display:flex; align-items:center; gap:4px; white-space:nowrap;">
    <span>{sym}</span>
  </div>
  {dignity_badge_html}
  <div style="flex:1; background:{track_bg}; border-radius:6px; height:12px; overflow:hidden; position:relative; border:1px solid {track_bdr};">
    <div style="width:{pct:.1f}%; height:100%; background:{bar_grad}; border-radius:5px;"></div>
  </div>
  <div style="width:58px; text-align:right; font-weight:900; font-size:11.5px; color:{val_color}; font-family:monospace;">
    {score:.1f} <span style="font-size:9.5px; color:{dim_color}; font-weight:600;">/{int(max_val)}</span>
  </div>
</div>'''
        rows_html.append(row)

    return f'<div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:10px; padding:12px 14px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:12px;">' + "".join(rows_html) + '</div>'


def generate_styled_vertical_svg(items, max_val=20, is_dark=False):
    svg_bg = "#111827" if is_dark else "#FFFFFF"
    svg_bdr = "#374151" if is_dark else "#E2E8F0"
    grid_col = "#374151" if is_dark else "#E2E8F0"
    base_col = "#64748B" if is_dark else "#94A3B8"
    score_col = "#FFFFFF" if is_dark else "#0F172A"

    n = len(items)
    w_svg = 540
    h_svg = 215
    top_y = 28
    base_y = 160
    chart_h = base_y - top_y

    pad_left = 32
    col_w = (w_svg - pad_left - 10) / n
    bar_w = min(30, col_w - 8)

    grid_lines = []
    for g_val in [5, 10, 15, 20]:
        g_y = base_y - (g_val / max_val) * chart_h
        grid_lines.append(f'<line x1="{pad_left}" y1="{g_y:.1f}" x2="{w_svg-10}" y2="{g_y:.1f}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>')
        grid_lines.append(f'<text x="{pad_left - 6}" y="{g_y + 3:.1f}" font-size="9" fill="{base_col}" font-family="sans-serif" text-anchor="end">{g_val}</text>')

    bars_svg = []
    for i, item in enumerate(items):
        p_name = item["name"]
        sym = item.get("symbol", p_name)
        p_color = item.get("color", "#2563EB")
        d_lbl = item.get("dignity", "")
        score = float(item.get("score", 0.0))
        bar_h = max(4.0, (score / max_val) * chart_h)
        bar_x = pad_left + i * col_w + (col_w - bar_w) / 2
        bar_y = base_y - bar_h

        if "उच्च" in d_lbl or score >= 17:
            fill_c = "#10B981"
        elif "मूलत्रिकोण" in d_lbl or "स्वराशि" in d_lbl or score >= 14:
            fill_c = "#3B82F6"
        elif "मित्र" in d_lbl or score >= 11:
            fill_c = "#06B6D4"
        elif "सम" in d_lbl or score >= 8:
            fill_c = "#F59E0B"
        elif "शत्रु" in d_lbl or score >= 5:
            fill_c = "#F97316"
        else:
            fill_c = "#EF4444"

        bars_svg.append(f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" ry="4" fill="{fill_c}" opacity="0.9"/>')
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{bar_y - 5:.1f}" font-size="10.5" font-weight="bold" fill="{score_col}" font-family="sans-serif" text-anchor="middle">{score:.1f}</text>')
        short_sym = sym.split()[0] if " " in sym else sym
        short_hi = sym.split()[1] if " " in sym else p_name[:3]
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 16:.1f}" font-size="10" font-weight="bold" fill="{p_color}" font-family="sans-serif" text-anchor="middle">{short_sym} {short_hi}</text>')
        if d_lbl:
            short_d = d_lbl.split()[0] if "(" in d_lbl else d_lbl
            bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 30:.1f}" font-size="9" font-weight="bold" fill="{fill_c}" font-family="sans-serif" text-anchor="middle">{short_d[:4]}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_svg} {h_svg}" style="width:100%; height:auto; background:{svg_bg}; border:1.5px solid {svg_bdr}; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:12px;">
  {"".join(grid_lines)}
  <line x1="{pad_left}" y1="{base_y}" x2="{w_svg-10}" y2="{base_y}" stroke="{base_col}" stroke-width="1.5"/>
  {"".join(bars_svg)}
</svg>'''


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
    h_svg = 245
    pad_left = 46
    pad_right = 16
    top_y = 30
    base_y = 188
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
            grid_svg.append(f'<text x="{pad_left - 8}" y="{ty + 3.5:.1f}" font-size="9.5" font-weight="bold" fill="#F59E0B" font-family="sans-serif" text-anchor="end">50%</text>')
            grid_svg.append(f'<text x="{w_svg - pad_right - 4}" y="{ty - 4:.1f}" font-size="8.5" font-weight="700" fill="#F59E0B" font-family="sans-serif" text-anchor="end">स्वाधीनता सीमा (Agency Baseline)</text>')
        else:
            grid_svg.append(f'<line x1="{pad_left}" y1="{ty:.1f}" x2="{w_svg - pad_right}" y2="{ty:.1f}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>')
            grid_svg.append(f'<text x="{pad_left - 8}" y="{ty + 3.5:.1f}" font-size="9" fill="{axis_col}" font-family="sans-serif" text-anchor="end">{tick}%</text>')

    grid_svg.append(f'<line x1="{pad_left}" y1="{base_y}" x2="{w_svg - pad_right}" y2="{base_y}" stroke="{base_col}" stroke-width="1.5"/>')
    grid_svg.append(f'<text x="{pad_left - 8}" y="{base_y + 3.5:.1f}" font-size="9" fill="{axis_col}" font-family="sans-serif" text-anchor="end">0%</text>')

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
        val_y = max(top_y - 2, bar_y - 6)
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{val_y:.1f}" font-size="10.5" font-weight="800" fill="{val_col}" font-family="sans-serif" text-anchor="middle">{val_str}</text>')
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 16:.1f}" font-size="11" font-weight="800" fill="{text_primary}" font-family="sans-serif" text-anchor="middle">H{h_num}</text>')
        hi_name = house_hi.get(h_num, "")
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 29:.1f}" font-size="9.5" font-weight="600" fill="{text_muted}" font-family="sans-serif" text-anchor="middle">{hi_name}</text>')

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
    <div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:12px; padding:14px 16px; box-shadow:0 4px 14px rgba(0,0,0,0.06); margin-bottom:14px;">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
        <div>
          <div style="font-size:13px; font-weight:800; color:{text_primary}; display:flex; align-items:center; gap:6px;">
            <span>📊 १२ भावों का फ्री-विल प्रतिशत वितरण</span>
            <span style="font-size:10px; background:rgba(37,99,235,0.12); color:#2563EB; padding:1px 6px; border-radius:4px; font-weight:700;">H1 – H12 प्राकृतिक क्रम</span>
          </div>
          <div style="font-size:10.5px; color:{text_muted}; margin-top:2px;">कर्म स्वाधीनता (Purushartha) बनाम प्रारब्ध (Destiny) अनुपातिक शक्ति</div>
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:10px; font-weight:700;">
          <span style="display:inline-flex; align-items:center; gap:4px; color:#059669; background:rgba(16,185,129,0.1); padding:2px 7px; border-radius:12px; border:1px solid rgba(16,185,129,0.25);">
            <span style="width:7px; height:7px; border-radius:50%; background:#10B981;"></span> ≥50% पुरुषार्थ
          </span>
          <span style="display:inline-flex; align-items:center; gap:4px; color:#D97706; background:rgba(245,158,11,0.1); padding:2px 7px; border-radius:12px; border:1px solid rgba(245,158,11,0.25);">
            <span style="width:7px; height:7px; border-radius:50%; background:#F59E0B;"></span> 35-49% मध्यम
          </span>
          <span style="display:inline-flex; align-items:center; gap:4px; color:#DC2626; background:rgba(239,68,68,0.1); padding:2px 7px; border-radius:12px; border:1px solid rgba(239,68,68,0.25);">
            <span style="width:7px; height:7px; border-radius:50%; background:#EF4444;"></span> &lt;35% प्रारब्ध
          </span>
        </div>
      </div>
      {svg_content}
    </div>
    '''
    return header_html


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
    h_svg = 245
    pad_left = 46
    pad_right = 16
    top_y = 30
    base_y = 188
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
        grid_svg.append(f'<text x="{pad_left - 8}" y="{ty + 3.5:.1f}" font-size="9" fill="{axis_col}" font-family="sans-serif" text-anchor="end">{tick}</text>')

    grid_svg.append(f'<line x1="{pad_left}" y1="{base_y}" x2="{w_svg - pad_right}" y2="{base_y}" stroke="{base_col}" stroke-width="1.5"/>')
    grid_svg.append(f'<text x="{pad_left - 8}" y="{base_y + 3.5:.1f}" font-size="9" fill="{axis_col}" font-family="sans-serif" text-anchor="end">0</text>')

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
        bars_svg.append(f'<text x="{col_cx:.1f}" y="{base_y + 15:.1f}" font-size="11" font-weight="800" fill="{text_primary}" font-family="sans-serif" text-anchor="middle">H{h_num}</text>')

        # Sanskrit House Name
        hi_name = house_hi.get(h_num, "")
        bars_svg.append(f'<text x="{col_cx:.1f}" y="{base_y + 27:.1f}" font-size="9" font-weight="600" fill="{text_muted}" font-family="sans-serif" text-anchor="middle">{hi_name}</text>')

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

        badge_w = 26
        badge_h = 13
        badge_rx = col_cx - badge_w / 2
        badge_ry = base_y + 32
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

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_svg} {h_svg + 8}" style="width:100%; height:auto; display:block;">
      {defs}
      {"".join(grid_svg)}
      {"".join(bars_svg)}
    </svg>'''

    header_html = f'''
    <div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:12px; padding:14px 16px; box-shadow:0 4px 14px rgba(0,0,0,0.06); margin-bottom:14px;">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
        <div>
          <div style="font-size:13px; font-weight:800; color:{text_primary}; display:flex; align-items:center; gap:6px;">
            <span>⚖️ भाव सौम्य (शुभ) बनाम क्रूर (पाप) प्रभाव अंक</span>
            <span style="font-size:10px; background:rgba(16,185,129,0.12); color:#059669; padding:1px 6px; border-radius:4px; font-weight:700;">द्वि-चर तुलना</span>
          </div>
          <div style="font-size:10.5px; color:{text_muted}; margin-top:2px;">शुभ ग्रह (सौम्य) बनाम पाप ग्रह (क्रूर) प्रभाव व नीचे नेट संतुलन अंक (+/-)</div>
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:10px; font-weight:700;">
          <span style="display:inline-flex; align-items:center; gap:4px; color:#059669; background:rgba(16,185,129,0.1); padding:2px 7px; border-radius:12px; border:1px solid rgba(16,185,129,0.25);">
            <span style="width:7px; height:7px; border-radius:50%; background:#10B981;"></span> सौम्य (Benefic)
          </span>
          <span style="display:inline-flex; align-items:center; gap:4px; color:#DC2626; background:rgba(239,68,68,0.1); padding:2px 7px; border-radius:12px; border:1px solid rgba(239,68,68,0.25);">
            <span style="width:7px; height:7px; border-radius:50%; background:#EF4444;"></span> क्रूर (Malefic)
          </span>
          <span style="display:inline-flex; align-items:center; gap:4px; color:#2563EB; background:rgba(37,99,235,0.1); padding:2px 7px; border-radius:12px; border:1px solid rgba(37,99,235,0.25);">
            ⚖️ नेट संतुलन
          </span>
        </div>
      </div>
      {svg_content}
    </div>
    '''
    return header_html


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


def render_vastu_compass_wheel_svg(zones: list, is_dark: bool = False) -> str:
    import math

    def polar_to_cart(cx, cy, r, deg):
        rad = math.radians(deg - 90)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    def get_arc_path(cx, cy, r_in, r_out, start_deg, end_deg):
        x1_out, y1_out = polar_to_cart(cx, cy, r_out, start_deg)
        x2_out, y2_out = polar_to_cart(cx, cy, r_out, end_deg)
        x2_in, y2_in = polar_to_cart(cx, cy, r_in, end_deg)
        x1_in, y1_in = polar_to_cart(cx, cy, r_in, start_deg)
        return f"M {x1_out:.1f} {y1_out:.1f} A {r_out} {r_out} 0 0 1 {x2_out:.1f} {y2_out:.1f} L {x2_in:.1f} {y2_in:.1f} A {r_in} {r_in} 0 0 0 {x1_in:.1f} {y1_in:.1f} Z"

    cx, cy = 250, 250
    bg_circle = "#0b1021" if is_dark else "#f8fafc"
    border_circle = "#334155" if is_dark else "#cbd5e1"
    text_main = "#f8fafc" if is_dark else "#0f172a"
    text_sub = "#94a3b8" if is_dark else "#64748b"

    zone_dict = {z.get("direction"): z for z in zones}

    dirs = [
        ("North", 0, "उत्तर (N)", "बुध (Mercury)"),
        ("North-East", 45, "ईशान (NE)", "गुरु (Jupiter)"),
        ("East", 90, "पूर्व (E)", "सूर्य (Sun)"),
        ("South-East", 135, "आग्नेय (SE)", "शुक्र (Venus)"),
        ("South", 180, "दक्षिण (S)", "मंगल (Mars)"),
        ("South-West", 225, "नैऋत्य (SW)", "राहु (Rahu)"),
        ("West", 270, "पश्चिम (W)", "शनि (Saturn)"),
        ("North-West", 315, "वायव्य (NW)", "चन्द्र (Moon)"),
    ]

    wedges_svg = []
    for d_name, mid_ang, label, fallback_lord in dirs:
        z = zone_dict.get(d_name, {})
        score = z.get("score", 70)
        lord = z.get("lord", fallback_lord)

        if score >= 75:
            color = "#10b981"
            fill_opacity = "0.22"
        elif score >= 50:
            color = "#f59e0b"
            fill_opacity = "0.22"
        else:
            color = "#ef4444"
            fill_opacity = "0.25"

        path_d = get_arc_path(cx, cy, 90, 230, mid_ang - 22.5, mid_ang + 22.5)
        tx, ty = polar_to_cart(cx, cy, 160, mid_ang)

        wedges_svg.append(
            f'<path d="{path_d}" fill="{color}" fill-opacity="{fill_opacity}" stroke="{color}" stroke-width="2"/>'
            f'<text x="{tx:.1f}" y="{(ty - 10):.1f}" text-anchor="middle" fill="{text_main}" font-size="12" font-weight="bold">{label}</text>'
            f'<text x="{tx:.1f}" y="{(ty + 6):.1f}" text-anchor="middle" fill="{text_sub}" font-size="10.5">{lord}</text>'
            f'<text x="{tx:.1f}" y="{(ty + 22):.1f}" text-anchor="middle" fill="{color}" font-size="12" font-weight="bold">{score}/100</text>'
        )

    b_zone = zone_dict.get("Center", {})
    b_score = b_zone.get("score", 85)
    b_color = "#3b82f6"

    center_svg = (
        f'<circle cx="{cx}" cy="{cy}" r="82" fill="{b_color}" fill-opacity="0.20" stroke="{b_color}" stroke-width="2.5"/>'
        f'<text x="{cx}" y="{cy - 12}" text-anchor="middle" fill="{text_main}" font-size="13" font-weight="bold">ब्रह्मस्थान</text>'
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" fill="{text_sub}" font-size="10.5">Brahmasthan (Akasha)</text>'
        f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" fill="{b_color}" font-size="12" font-weight="bold">{b_score}/100</text>'
    )

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="450" style="max-width: 500px; margin: 0 auto; display: block;">',
        f'<defs><radialGradient id="compassBg" cx="50%" cy="50%" r="50%">',
        f'<stop offset="0%" stop-color="{bg_circle}" stop-opacity="0.9"/>',
        f'<stop offset="100%" stop-color="{bg_circle}" stop-opacity="1"/>',
        f'</radialGradient></defs>',
        f'<circle cx="{cx}" cy="{cy}" r="240" fill="url(#compassBg)" stroke="{border_circle}" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="236" fill="none" stroke="{border_circle}" stroke-width="1" stroke-dasharray="4,4"/>',
        "".join(wedges_svg),
        center_svg,
        '</svg>'
    ]

    return "".join(svg_parts)


MODULE_TABS_REGISTRY = {
    0: [
        "☸️ लग्न व वर्ग चक्र (D1-D60)",
        "🌟 पुष्कर व वर्गोत्तम",
        "👑 जैमिनी विशेष लग्न",
        "🏠 भाव चलित",
        "🌙 चन्द्र कुण्डली",
        "☀️ सूर्य कुण्डली",
        "⚔️ ग्रह युद्ध",
        "🏰 १२ आरूढ़ पद (Arudha Padas)",
        "🏰 कोटा चक्र"
    ],
    1: [
        "🔮 भविष्य घटना पूर्वानुमान",
        "🔍 भूतकाल घटना सत्यापन"
    ],
    2: [
        "🛡️ ग्रह दोष व फ्री-विल",
        "🎯 २७ जीवन क्षेत्र स्कोर",
        "🌿 वैदिक उपचार व उपाय",
        "⚠️ बाधक व मारक विचार"
    ],
    3: [
        "📊 दशवर्ग (D1-D10)",
        "🏛️ षोडशवर्ग (D1-D60)",
        "📜 वर्ग सारांश व प्रमाण"
    ],
    4: [
        "🧭 सम्पूर्ण वास्तु मण्डल",
        "🌅 पूर्व (East)",
        "⚡ आग्नेय (SE)",
        "🔴 दक्षिण (South)",
        "⛰️ नैऋत्य (SW)",
        "🌊 पश्चिम (West)",
        "💨 वायव्य (NW)",
        "💰 उत्तर (North)",
        "🕉️ ईशान (NE)",
        "🌌 ब्रह्मस्थान (Center)"
    ],
    5: [
        "👤 जातक प्रश्न विश्लेषण",
        "✍️ नया तात्कालिक प्रश्न",
        "🪐 प्रश्न ग्रह स्थिति",
        "🎭 द्वादश भाव भूमिका",
        "📖 ताजिक व इत्थशाल",
        "📜 १०० शास्त्रीय प्रश्न नियम"
    ],
    6: [
        "⚖️ षड्बल सारणी",
        "🔬 ६ बल विश्लेषण",
        "🏰 १२ भाव बल",
        "🎭 ग्रह अवस्था व इष्ट-कष्ट",
        "📐 दृष्टि चक्र (Aspectarium)",
        "📜 षड्बल प्रमाण"
    ],
    7: [
        "🔱 कारकांश व स्वांश",
        "👑 ७ चर कारक",
        "🌟 विशेष लग्न व योग",
        "🏰 १२ आरूढ़ पद",
        "📡 राशि दृष्टि",
        "🔗 अर्गला विचार",
        "🌍 ग्रह आरूढ़",
        "⏳ आयुर्दाय गणना",
        "👻 अप्रकाशित उपग्रह",
        "📜 जैमिनी उपदेश सूत्र"
    ],
    8: [
        "📊 १२०-वर्ष गेंट चार्ट",
        "⏳ जीवन टाइमलाइन",
        "🌟 विंशोत्तरी (५ स्तर)",
        "🌸 योगिनी दशा (३६ वर्ष)",
        "🔱 जैमिनी चर दशा",
        "🔄 कालचक्र दशा",
        "⚔️ शूल दशा (मारक)",
        "🕉️ अष्टोत्तरी दशा",
        "🪐 नारायण दशा",
        "⏳ द्विसप्ततिसम दशा",
        "🔷 स्थिर दशा",
        "👁️ दृग दशा",
        "🎯 बहु-दशा संगम",
        "📜 शास्त्रीय प्रमाण व उपाय"
    ],
    9: [
        "🎯 जन्म-गोचर चक्र",
        "🪐 दैनिक गोचर",
        "⌛ साढ़ेसाती व ढैया",
        "⚡ दोहरा गोचर (गुरु-शनि)",
        "📊 अष्टकवर्ग (SAV/BAV)",
        "⚖️ त्रिकोण शोधन",
        "🔬 कक्षी गोचर",
        "📋 प्रस्ताराष्टकवर्ग",
        "🔵 भृगु बिन्दु",
        "🛡️ सर्वतोभद्र चक्र",
        "🏰 कोटा चक्र दुर्ग",
        "📈 वित्तीय ज्योतिष वेध",
        "📊 ग्रह गति व तरंग",
        "📅 मासिक गोचर कैलेंडर"
    ],
    10: [
        "🔮 के.पी. कार्य सिद्धि",
        "🪐 ४-स्तरीय कार्यकत्व",
        "🏰 कस्पल सब-लॉर्ड",
        "👑 रूलिंग प्लैनेट्स (RP)",
        "🔢 १-२४९ होरारी तालिका",
        "📐 पाश्चात्य दृष्टि वेध",
        "⏱️ के.पी. दशा भुक्ति",
        "📊 २२ घटना मैट्रिक्स",
        "📜 के.पी. स्वर्णिम नियम"
    ],
    11: [
        "📜 जन्म पञ्चाङ्ग व तत्व",
        "☀️ अहोरात्र चौघड़िया",
        "⏳ राहुकाल व अभिजित",
        "🌕 ताराबल व चन्द्रबल",
        "🏛️ १६ संस्कार मुहूर्त",
        "🔍 मुहूर्त खोजक (Scanner)",
        "📜 २१ महादोष विचार",
        "🪔 दोष परिहार व शांति"
    ],
    12: [
        "☸️ त्रि-चक्रीय मण्डल",
        "📊 १२ भाव त्रिविध फल",
        "⏳ सुदर्शन दशा",
        "🪐 त्रि-लग्न संरेखण",
        "🔍 त्रि-आयामी फलित",
        "📈 अष्टकवर्ग समन्वय",
        "⚖️ त्रि-शरीर मीमांसा",
        "📜 पाराशर प्रमाण (अ. ७४)",
        "🪔 सुदर्शन कवच व मन्त्र"
    ],
    13: [
        "🌟 वर्ष कुण्डली (D1)",
        "🎯 मुन्था विचार",
        "👑 वर्षेश चयन",
        "⚖️ पंचवर्गीय व हर्ष बल",
        "⚡ १६ ताजिक योग",
        "💫 ३६ ताजिक सहम",
        "⏳ मुद्धा व योगिनी दशा",
        "📊 १२ भाव वर्षफल",
        "🗓️ मासफल (१२ मास)",
        "🪔 वर्षेश शांति उपाय"
    ],
    14: [
        "🏆 घटना मिलान शोधन",
        "🌿 तत्व व लिंग शोधन",
        "☸️ कुण्ड व प्राणपद लग्न",
        "📐 D9 व D60 सीमा",
        "👑 के.पी. रूलिंग प्लैनेट्स",
        "⚖️ पूर्व व शोधित तुलना",
        "🎯 सेकंड्स सूक्ष्म स्लाइडर",
        "📜 शास्त्रीय सूत्र व प्रमाण"
    ],
    15: [
        "📊 अष्टकूट (३६ गुण)",
        "🛡️ महादोष व १६ परिहार",
        "🔥 मांगलिक व भौम साम्य",
        "☸️ उभय कुण्डली (D1/D9)",
        "👶 बीज-क्षेत्र व संतान",
        "🏛️ उपपद व ससुराल पक्ष",
        "⏱️ दशा-संधि कालक्रम",
        "📈 अष्टकवर्ग सिनैस्ट्री",
        "💼 व्यापार साझेदारी",
        "🖨️ मिलान रिपोर्ट व उपाय"
    ],
    16: [
        "💬 वैदिक परामर्श AI"
    ],
    17: [
        "📚 सम्पूर्ण ५०-पेज पत्रिका",
        "📋 १-पेज परामर्श पर्ची"
    ],
    18: [
        "📚 १२,५०० नियम बैंक",
        "🔍 ग्रन्थ एक्सप्लोरर",
        "🔬 कुण्डली अनुसंधान इंजन",
        "🛡️ Rules Lab (Admin)"
    ],
    19: [
        "🔍 वैदिक ऋषि सत्यापन"
    ],
    20: [
        "🔴 सक्रिय दोष",
        "🟢 राजयोग व धनयोग",
        "📋 १२,५०० शास्त्रीय नियम",
        "💊 कुण्डली अनुसार उपाय"
    ],
    21: [
        "📊 ३×३ लो-शू ग्रिड",
        "🪐 मूलांक व भाग्यांक",
        "🧩 मिसिंग नंबर व उपाय",
        "💎 लकी फैक्टर्स व नाम शोधन"
    ],
    22: [
        "🏠 १२ पक्के खाने",
        "⚠️ ९ कर्मिक ऋण व पितृ दोष",
        "💤 सोए हुए घर व ग्रह",
        "🌿 १०८ प्रामाणिक टोटके"
    ],
    23: [
        "🌿 त्रिदोष प्रकृति",
        "✅ अनुकूल आहार",
        "❌ वर्जित आहार",
        "⏰ भोजन नियम व उपवास"
    ],
    24: [
        "👫 जीवनसाथी व दांपत्य",
        "👨‍👩‍👦 परिवार व स्वजन",
        "🌟 मित्र व सहायक",
        "⚔️ शत्रु व विरोधी"
    ],
    25: [
        "🩺 देह वेध आरेख (Anatomy)",
        "💪 आरोग्य बल व स्थिति",
        "⚠️ संभावित रोग जोखिम",
        "📋 ग्रह-अंग चिकित्सा सारणी",
        "🌿 निवारक उपाय व दिनचर्या"
    ],
    26: [
        "🏃 कद-काठी व रंग-रूप",
        "🦴 १२ कालपुरुष अंग",
        "🎯 तिल, मस्से व चिन्ह",
        "🔮 सुरक्षा व आसन परामर्श"
    ],
    27: [
        "🕉️ इष्टदेवता व मोक्ष",
        "📿 कुलदेवता व मन्त्र साधना",
        "🪔 नित्य पूजा विधान",
        "📅 व्रत व उपवास नियम",
        "🚩 नवरात्रि ९ दिवसीय विधान"
    ],
    28: [
        "💼 नौकरी बनाम व्यापार",
        "🎓 शिक्षा व मेधा",
        "⚖️ आचरण व प्रवृत्तियां",
        "🚫 व्यसन व प्रलोभन",
        "🏛️ पैतृक संपत्ति व सुख",
        "🕉️ पूर्वजन्म प्रारब्ध व ऋण"
    ],
    29: [
        "🌟 पञ्चाङ्ग ५ स्तम्भ",
        "🚩 पर्व, व्रत व एकादशी",
        "🪔 पक्ष व श्राद्ध",
        "🏛️ २४-घंटे लग्न सारणी",
        "⏰ शुभ-अशुभ मुहूर्त",
        "☀️ चौघड़िया व होरा",
        "🛡️ भद्रा व पञ्चक",
        "⚖️ चन्द्रबल व ताराबल",
        "🪐 गोचर व मंत्रिमंडल",
        "📜 दैनिक सङ्कल्प मन्त्र",
        "📅 मासिक पञ्चाङ्ग",
        "🤖 AI पञ्चाङ्ग सारथी"
    ],
    30: [
        "🌟 ५० जीवन आयाम",
        "❓ १०० प्रश्न-उत्तर (FAQs)",
        "🔬 सर्व-गणना संश्लेषण",
        "📜 ग्रन्थ प्रमाण व उपाय"
    ],
    31: [
        "✋ १. विज़ुअल हस्त-नक्शा (Palm Map)",
        "📜 २. समग्र शास्त्रीय फलादेश (Predictions)",
        "🪐 ३. नवग्रह पर्वत एवं बल (Mounts)",
        "📏 ४. रेखाएं एवं आयु काल-विभाजन (Age Dating)",
        "⚜️ ५. विशिष्ट दिव्य चिन्ह व योग (Yogas)",
        "🔗 ६. कुण्डली-हस्तरेखा समन्वय (Synthesis)",
        "🪔 ७. दोष निवारण एवं वैदिक उपाय (Remedies)"
    ]
}

if "active_module_idx" not in st.session_state:
    st.session_state.active_module_idx = 0
st.session_state.active_module_idx = max(0, min(int(st.session_state.active_module_idx), len(MODULE_OPTIONS) - 1))

# Check if user selected a new module from top_bar_module_selector and sync active_module_idx
if "top_bar_module_selector" in st.session_state and st.session_state.top_bar_module_selector in MODULE_OPTIONS:
    _sel_m_idx = MODULE_OPTIONS.index(st.session_state.top_bar_module_selector)
    if _sel_m_idx != st.session_state.active_module_idx:
        st.session_state.active_module_idx = _sel_m_idx
        st.session_state.active_tab_idx = 0
        st.session_state.tab_switch_requested = 0
        st.session_state._last_module_sync_idx = _sel_m_idx

if "active_tab_idx" not in st.session_state:
    st.session_state.active_tab_idx = 0

if "_last_module_sync_idx" not in st.session_state:
    st.session_state._last_module_sync_idx = st.session_state.active_module_idx
elif st.session_state._last_module_sync_idx != st.session_state.active_module_idx:
    st.session_state._last_module_sync_idx = st.session_state.active_module_idx
    st.session_state.active_tab_idx = 0
    st.session_state.tab_switch_requested = 0

cur_mod_tabs = MODULE_TABS_REGISTRY.get(st.session_state.active_module_idx, ["1. 📊 मुख्य विहंगावलोकन (Main View)"])

# If user selected a tab from top_bar_tab_selector, sync active_tab_idx immediately
cur_tab_key = f"top_bar_tab_selector_{st.session_state.active_module_idx}"
if cur_tab_key in st.session_state and st.session_state[cur_tab_key] in cur_mod_tabs:
    st.session_state.active_tab_idx = cur_mod_tabs.index(st.session_state[cur_tab_key])
elif "top_bar_tab_selector" in st.session_state and st.session_state.top_bar_tab_selector in cur_mod_tabs:
    st.session_state.active_tab_idx = cur_mod_tabs.index(st.session_state.top_bar_tab_selector)

st.session_state.active_tab_idx = max(0, min(int(st.session_state.active_tab_idx), len(cur_mod_tabs) - 1))

# Keep top_bar_module_selector in sync with active_module_idx before widget render
st.session_state.top_bar_module_selector = MODULE_OPTIONS[st.session_state.active_module_idx]

# Keep top_bar_tab_selector in sync before widget render
st.session_state[cur_tab_key] = cur_mod_tabs[st.session_state.active_tab_idx]

def _nav_prev_module():
    new_idx = (st.session_state.active_module_idx - 1) % len(MODULE_OPTIONS)
    st.session_state.active_module_idx = new_idx
    st.session_state.active_tab_idx = 0
    st.session_state.tab_switch_requested = 0
    if "sb_cat_filter_select" in st.session_state:
        st.session_state.sb_cat_filter_select = "📁 समस्त २९ मॉड्यूल (All Modules)"
    if "sb_search_filter_input" in st.session_state:
        st.session_state.sb_search_filter_input = ""

def _nav_next_module():
    new_idx = (st.session_state.active_module_idx + 1) % len(MODULE_OPTIONS)
    st.session_state.active_module_idx = new_idx
    st.session_state.active_tab_idx = 0
    st.session_state.tab_switch_requested = 0
    if "sb_cat_filter_select" in st.session_state:
        st.session_state.sb_cat_filter_select = "📁 समस्त २९ मॉड्यूल (All Modules)"
    if "sb_search_filter_input" in st.session_state:
        st.session_state.sb_search_filter_input = ""

def _nav_prev_tab():
    cur_tabs = MODULE_TABS_REGISTRY.get(st.session_state.active_module_idx, ["1. 📊 मुख्य विहंगावलोकन (Main View)"])
    new_tab = (st.session_state.active_tab_idx - 1) % len(cur_tabs)
    st.session_state.active_tab_idx = new_tab
    st.session_state.tab_switch_requested = new_tab

def _nav_next_tab():
    cur_tabs = MODULE_TABS_REGISTRY.get(st.session_state.active_module_idx, ["1. 📊 मुख्य विहंगावलोकन (Main View)"])
    new_tab = (st.session_state.active_tab_idx + 1) % len(cur_tabs)
    st.session_state.active_tab_idx = new_tab
    st.session_state.tab_switch_requested = new_tab

def _nav_to_rules_bank():
    st.session_state.active_module_idx = 18
    st.session_state.active_tab_idx = 0
    st.session_state.tab_switch_requested = 0
    if "sb_cat_filter_select" in st.session_state:
        st.session_state.sb_cat_filter_select = "📁 समस्त २९ मॉड्यूल (All Modules)"
    if "sb_search_filter_input" in st.session_state:
        st.session_state.sb_search_filter_input = ""

# -------------------------------------------------------------
# 🌟 FROZEN STICKY TOP HEADER SECTION (Pinned at Top)
# -------------------------------------------------------------
with st.container(key="top_frozen_header_container", border=False):
    # 1. Authentic Server Component Toolbar & Modals (Exact UI Parity - 10 Icons Suite)
    if "gla_active_tool" not in st.session_state:
        st.session_state.gla_active_tool = None

    # Sync with query parameter if user clicked an anchor tile
    if "gla_tool" in st.query_params:
        param_tool = st.query_params.get("gla_tool")
        if param_tool:
            st.session_state.gla_active_tool = param_tool if st.session_state.gla_active_tool != param_tool else None
        try:
            del st.query_params["gla_tool"]
        except Exception:
            pass
    # Invisible anchor for sticky top header calculations
    st.markdown('<div class="fixed-header-anchor" style="display:none; height:0px; margin:0; padding:0;"></div>', unsafe_allow_html=True)

    # Track recent charts history in session
    if "recent_charts_history" not in st.session_state:
        st.session_state.recent_charts_history = []
    if "birth_name" in st.session_state and st.session_state.birth_name:
        _c_name = st.session_state.birth_name
        _c_date = st.session_state.birth_date.strftime("%Y-%m-%d") if hasattr(st.session_state.birth_date, "strftime") else str(st.session_state.birth_date)
        _c_time = st.session_state.birth_time.strftime("%H:%M:%S") if hasattr(st.session_state.birth_time, "strftime") else str(st.session_state.birth_time)
        _c_city = st.session_state.get("birth_city", "New Delhi")
        _c_lat = float(st.session_state.get("birth_lat", 28.6139))
        _c_lon = float(st.session_state.get("birth_lon", 77.2090))
        _c_tz = float(st.session_state.get("birth_tz", 5.5))
        _c_owner = str(st.session_state.get("user_email", "")).strip().lower()
        if not any(r.get("name") == _c_name and r.get("date") == _c_date and r.get("owner_email") == _c_owner for r in st.session_state.recent_charts_history):
            st.session_state.recent_charts_history.insert(0, {
                "name": _c_name, "date": _c_date, "time": _c_time,
                "city": _c_city, "lat": _c_lat, "lon": _c_lon, "tz": _c_tz,
                "owner_email": _c_owner
            })
            st.session_state.recent_charts_history = st.session_state.recent_charts_history[:5]

    # ═════════════════════════════════════════════════════════════════════
    # 🌟 UNIFIED SINGLE-LINE COSMIC NAVY WORKSTATION HEADER (1ST LINE ONLY)
    # [ sidebar Show icon (<<) ] [ Logo ] [ Bramhahora ] [ Module List ] [ Tab List ] [ Menu ]
    # ═══════════════════════════════════════════════════════════════════════════════════════
    with st.container(key="frozen_toolbelt_container", border=False):
        # संतुलित कार्यक्षेत्र अनुपात: [ >> ] [ समस्त मॉड्यूल ] [ सक्रिय टैब ] [ मेन्यू ]
        hdr_c_toggle, hdr_c_mod, hdr_c_tab, hdr_c_menu = st.columns(
            [0.80, 6.60, 6.60, 4.40],
            gap="small",
            vertical_alignment="center"
        )

        with hdr_c_toggle:
            st.markdown(
                '<div class="header-toggle-slot" id="header_sidebar_toggle_slot" '
                'title="साइडबार टॉगल करें (Toggle Sidebar)" '
                'style="display:flex; align-items:center; justify-content:center; width:100%; height:36px; min-width:28px;"></div>',
                unsafe_allow_html=True
            )

        with hdr_c_mod:
            _cur_m_name = MODULE_OPTIONS[st.session_state.active_module_idx] if 0 <= st.session_state.active_module_idx < len(MODULE_OPTIONS) else MODULE_OPTIONS[0]
            chosen_module = st.selectbox(
                "समस्त मॉड्यूल सूची (All Modules)",
                MODULE_OPTIONS,
                index=MODULE_OPTIONS.index(_cur_m_name),
                label_visibility="collapsed",
                key="top_bar_module_selector",
                help="समस्त मॉड्यूल सूची (All Modules)"
            )
            if chosen_module != _cur_m_name:
                st.session_state.active_module_idx = MODULE_OPTIONS.index(chosen_module)
                st.session_state.active_tab_idx = 0
                st.session_state.tab_switch_requested = 0
                st.session_state._last_module_sync_idx = st.session_state.active_module_idx
                st.rerun()

        with hdr_c_tab:
            _cur_t_idx = min(st.session_state.active_tab_idx, len(cur_mod_tabs) - 1)
            tab_widget_key = f"top_bar_tab_selector_{st.session_state.active_module_idx}"
            chosen_tab = st.selectbox(
                "सक्रिय मॉड्यूल के सभी टैब (Active Module Tabs)",
                cur_mod_tabs,
                index=_cur_t_idx,
                label_visibility="collapsed",
                key=tab_widget_key,
                help="सक्रिय मॉड्यूल के सभी टैब की सूची (Active Module Tabs)"
            )
            if cur_mod_tabs.index(chosen_tab) != st.session_state.active_tab_idx:
                st.session_state.active_tab_idx = cur_mod_tabs.index(chosen_tab)
                st.session_state.tab_switch_requested = st.session_state.active_tab_idx
                st.rerun()

        with hdr_c_menu:
            cur_th = st.session_state.get("app_theme_mode", "day")
            th_lbl = "डे मोड" if cur_th in ["astrallis", "night"] else "नाइट मोड"
            cur_lang = st.session_state.get("app_lang", "General (जनरल)")
            is_hindi = ("जनरल" in cur_lang or "Hindi" in cur_lang)
            lang_lbl = "English" if is_hindi else "हिंदी"

            u_role = st.session_state.get("user_role", "jatak")
            MENU_ACTION_ITEMS = [
                "⚡ मेन्यू (Menu)...",
                "✨ नया जातक (New Kundali)",
                "📂 कुण्डली वॉल्ट (Client Vault)",
                "💾 कुण्डली सहेजें (Save Kundali)",
                "📝 परामर्श नोट्स (Consultation Notes)",
                "📄 PDF रिपोर्ट (Download PDF)",
                "💬 दैवज्ञ AI परामर्श (AI Astrologer)",
                f"🌐 भाषा: {lang_lbl}",
                f"🌓 थीम: {th_lbl}",
                "⚙️ सेटिंग्स (Settings)"
            ]
            if u_role == "researcher":
                MENU_ACTION_ITEMS.append("👑 एडमिन (Admin Control)")
            else:
                MENU_ACTION_ITEMS.append("🎟️ प्रो लाइसेंस (Activate License)")
            MENU_ACTION_ITEMS.append("🚪 लॉगआउट (Logout)")

            _menu_nonce = st.session_state.get("top_bar_menu_nonce", 0)
            selected_action = st.selectbox(
                "मेन्यू सूची (Menu List)",
                MENU_ACTION_ITEMS,
                index=0,
                label_visibility="collapsed",
                key=f"top_bar_menu_action_selector_{_menu_nonce}",
                help="मेन्यू सूची (नया जातक, वॉल्ट, सहेजें, नोट्स, PDF रिपोर्ट, AI परामर्श, सेटिंग्स, भाषा, थीम, लॉगआउट)"
            )

            if selected_action != MENU_ACTION_ITEMS[0]:
                if "नया जातक" in selected_action or "New" in selected_action:
                    st.session_state.gla_active_tool = "new"
                elif "वॉल्ट" in selected_action or "Vault" in selected_action:
                    st.session_state.gla_active_tool = "open"
                elif "सहेजें" in selected_action or "Save" in selected_action:
                    st.session_state.gla_active_tool = "save"
                elif "नोट्स" in selected_action or "Notes" in selected_action:
                    st.session_state.gla_active_tool = "notes"
                elif "PDF" in selected_action:
                    st.session_state.gla_active_tool = "pdf"
                elif "दैवज्ञ AI" in selected_action or "AI" in selected_action:
                    st.session_state.gla_active_tool = "daivajna_brain"
                elif "भाषा" in selected_action or "Language" in selected_action:
                    st.session_state.app_lang = "English (अंग्रेजी)" if is_hindi else "General (जनरल)"
                    st.toast(f"✅ भाषा परिवर्तित: {st.session_state.app_lang}", icon="🌐")
                elif "थीम" in selected_action or "Mode" in selected_action:
                    st.session_state.app_theme_mode = "day" if cur_th in ["astrallis", "night"] else "astrallis"
                    st.toast(f"✅ थीम मोड: {st.session_state.app_theme_mode.upper()}", icon="🌓")
                elif "सेटिंग्स" in selected_action or "Settings" in selected_action or "Setup" in selected_action:
                    st.session_state.gla_active_tool = "settings"
                elif "एडमिन" in selected_action or "Admin" in selected_action:
                    st.session_state.gla_active_tool = "admin"
                elif "लाइसेंस" in selected_action or "License" in selected_action:
                    st.session_state.gla_active_tool = "license"
                elif "लॉगआउट" in selected_action or "Logout" in selected_action:
                    st.session_state.gla_active_tool = "logout"

                st.session_state["top_bar_menu_nonce"] = _menu_nonce + 1
                st.rerun()



        _cur_tabs_json = json.dumps(cur_mod_tabs)
        components.html(f"""
        <script>
        (function() {{
            try {{
                const tabs = {_cur_tabs_json};
                const pWin = (window.parent || window);
                pWin.__CURRENT_MODULE_TABS = tabs;
                window.__CURRENT_MODULE_TABS = tabs;
            }} catch(e) {{}}
        }})();
        </script>
        """, height=0, width=0)

    if st.session_state.get("sidebar_toggle_requested"):
        st.session_state.sidebar_toggle_requested = False
        components.html("""
        <script>
        try {
            const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            const sb = pDoc.querySelector('[data-testid="stSidebar"], section[data-testid="stSidebar"]');
            const isExp = sb && (
                sb.getAttribute('aria-expanded') === 'true' ||
                (sb.getAttribute('aria-expanded') !== 'false' && (sb.offsetWidth > 50 || (sb.getBoundingClientRect && sb.getBoundingClientRect().width > 50)))
            );
            const expBtn = pDoc.querySelector(
                'button[data-testid="stExpandSidebarButton"], ' +
                '[data-testid="stExpandSidebarButton"] button, ' +
                '[data-testid="stExpandSidebarButton"], ' +
                '[data-testid="stSidebarCollapsedControl"] button, ' +
                'button[data-testid="stSidebarCollapsedControl"], ' +
                '[data-testid="collapsedControl"] button, ' +
                'button[aria-label*="Expand sidebar"], ' +
                'button[title*="Expand sidebar"]'
            );
            const colBtn = pDoc.querySelector(
                'button[data-testid="stSidebarCollapseButton"], ' +
                '[data-testid="stSidebarCollapseButton"] button, ' +
                '[data-testid="stSidebarCollapseButton"], ' +
                '[data-testid="stSidebarHeader"] button, ' +
                'button[aria-label*="Collapse sidebar"], ' +
                'button[title*="Collapse sidebar"]'
            );
            if (isExp && colBtn) {
                colBtn.click();
            } else if (expBtn) {
                expBtn.click();
            } else if (colBtn) {
                colBtn.click();
            }
            try {
                if (window.parent && window.parent.setupStickyTopHeader) {
                    setTimeout(window.parent.setupStickyTopHeader, 80);
                    setTimeout(window.parent.setupStickyTopHeader, 250);
                }
            } catch(e_sync) {}
        } catch(e) {}
        </script>
        """, height=0, width=0)

    # Physical spacer between toolbelt and module selector/dialogs
    st.markdown("<div style='height: 8px; margin: 0; padding: 0;'></div>", unsafe_allow_html=True)

    # Active tool dialog/form container
    if st.session_state.gla_active_tool:
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

        # 1. TOOL: NEW / RESET & QUICK PRESETS
        if st.session_state.gla_active_tool == "new":
            with st.container(border=True):
                st.markdown("### ✨ नया प्रोफाइल, तात्कालिक प्रश्न एवं प्रीसेट्स (New Chart & Quick Presets)")
                st.write("कृपया अपनी आवश्यकतानुसार उपयुक्त विकल्प चुनें:")

                col_n1, col_n2, col_n3, col_n4, col_n5 = st.columns([1.5, 1.8, 1.6, 1.6, 1])
                with col_n1:
                    if st.button("📄 नया ब्लैंक (New Blank)", type="primary", use_container_width=True, help="नया खाली प्रोफाइल तैयार करें"):
                        st.session_state.birth_name = "New Client"
                        st.session_state.birth_gender = "Male"
                        st.session_state.birth_date = date.today()
                        st.session_state.birth_time = time(12, 0, 0)
                        st.session_state.birth_city = "New Delhi, Delhi, India"
                        st.session_state.birth_lat = 28.6139
                        st.session_state.birth_lon = 77.2090
                        st.session_state.birth_tz = 5.5
                        st.session_state["gla_city_query_input"] = "New Delhi, Delhi, India"
                        st.session_state["gla_lat_input"] = 28.6139
                        st.session_state["gla_lon_input"] = 77.2090
                        st.session_state["gla_tz_input"] = 5.5
                        st.session_state.last_applied_geo_loc = "New Delhi, Delhi, India_28.6139_77.2090"
                        st.session_state.gla_active_tool = "birth"
                        st.toast("✅ नया प्रोफाइल तैयार! कृपया जन्म विवरण भरें।", icon="👶")
                        st.rerun()

                with col_n2:
                    if st.button("🔮 तात्कालिक प्रश्न कुण्डली (Horary)", use_container_width=True, help="वर्तमान समय व स्थान की प्रश्न कुण्डली बनाएं"):
                        now_dt = datetime.now()
                        st.session_state.birth_name = f"प्रश्न कुण्डली ({now_dt.strftime('%H:%M:%S')})"
                        st.session_state.birth_gender = "Male"
                        st.session_state.birth_date = now_dt.date()
                        st.session_state.birth_time = now_dt.time().replace(microsecond=0)
                        st.session_state.calculated_at = now_dt
                        st.session_state.gla_active_tool = None
                        st.toast(f"✅ तात्कालिक प्रश्न कुण्डली ({now_dt.strftime('%I:%M:%S %p')}) तैयार!", icon="🔮")
                        st.rerun()

                with col_n3:
                    if st.button("👶 नवजात शिशु (Newborn)", use_container_width=True, help="आज की तिथि व वर्तमान समय से शिशु कुण्डली बनाएं"):
                        now_dt = datetime.now()
                        st.session_state.birth_name = "नवजात शिशु (Newborn Baby)"
                        st.session_state.birth_gender = "Male"
                        st.session_state.birth_date = now_dt.date()
                        st.session_state.birth_time = now_dt.time().replace(microsecond=0)
                        st.session_state.gla_active_tool = "birth"
                        st.toast("👶 शिशु का जन्म समय सेट किया गया! विवरण जांचें।", icon="👶")
                        st.rerun()

                with col_n4:
                    if st.button("💍 वर-वधू मिलान (Match Pair)", use_container_width=True, help="कुण्डली मिलान मॉड्यूल (Module 19) खोलें"):
                        st.session_state.active_module_idx = 19
                        st.session_state.gla_active_tool = None
                        st.toast("💍 कुण्डली मिलान मॉड्यूल खोला गया!", icon="💍")
                        st.rerun()

                with col_n5:
                    if st.button("🔄 डेमो (Demo)", use_container_width=True, help="डिफ़ॉल्ट डेमो प्रोफाइल लोड करें"):
                        st.session_state.birth_name = "डेमो जातक (Demo Profile)"
                        st.session_state.birth_gender = "Male"
                        st.session_state.birth_date = date(1995, 1, 1)
                        st.session_state.birth_time = time(12, 0, 0)
                        st.session_state.birth_city = "New Delhi, Delhi, India"
                        st.session_state.birth_lat = 28.6139
                        st.session_state.birth_lon = 77.2090
                        st.session_state.birth_tz = 5.5
                        st.session_state["gla_city_query_input"] = "New Delhi, Delhi, India"
                        st.session_state["gla_lat_input"] = 28.6139
                        st.session_state["gla_lon_input"] = 77.2090
                        st.session_state["gla_tz_input"] = 5.5
                        st.session_state.last_applied_geo_loc = "New Delhi, Delhi, India_28.6139_77.2090"
                        st.session_state.gla_active_tool = None
                        st.toast("✅ डिफ़ॉल्ट डेमो प्रोफाइल लोड की गई!", icon="🔄")
                        st.rerun()

                st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                if st.button("❌ बंद करें (Close)", use_container_width=True, key="btn_close_new_dialog"):
                    st.session_state.gla_active_tool = None
                    st.rerun()

        # 2. TOOL: BIRTH DATA (Authentic Grahalakshanam Birth Form)
        elif st.session_state.gla_active_tool == "birth":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #00b0f0; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#0077b6;">
                        👶 Server जन्म विवरण प्रपत्र (Birth Data Entry)
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_bf1, col_bf2, col_bf3 = st.columns([1.8, 1.2, 1.5])
                with col_bf1:
                    in_name = st.text_input("जातक का नाम (Name)", value=st.session_state.birth_name, key="gla_birth_name_input")
                    st.session_state.birth_name = in_name

                with col_bf2:
                    current_gender = st.session_state.get("birth_gender", "Male")
                    in_gender = st.radio("लिंग (Gender)", ["Male (पुरुष)", "Female (स्त्री)"], index=0 if current_gender == "Male" else 1, horizontal=True, key="gla_birth_gender_radio")
                    st.session_state.birth_gender = "Male" if "Male" in in_gender else "Female"

                with col_bf3:
                    dob_mode = st.radio("तिथि मोड (Date Mode)", ["🔢 वर्ष (1950-2050)", "📅 कैलेंडर"], horizontal=True, key="gla_dob_mode_radio")

                # Row 2: Date & Time pickers
                col_dt1, col_dt2 = st.columns([1.5, 1.5])
                with col_dt1:
                    if "1950" in dob_mode or "वर्ष" in dob_mode:
                        col_d_day, col_d_mon, col_d_yr = st.columns([1, 1.2, 1.2])
                        years_list = list(range(1950, 2051))
                        cur_yr = init_b_date.year if init_b_date.year in years_list else 1995
                        yr_idx = years_list.index(cur_yr)
                        months_labels = [
                            "01-जनवरी", "02-फरवरी", "03-मार्च", "04-अप्रैल",
                            "05-मई", "06-जून", "07-जुलाई", "08-अगस्त",
                            "09-सितंबर", "10-अक्टूबर", "11-नवंबर", "12-दिसंबर"
                        ]
                        cur_mon = init_b_date.month
                        mon_idx = cur_mon - 1
                        sel_yr = col_d_yr.selectbox("वर्ष (Year)", years_list, index=yr_idx, key="gla_dob_yr_select")
                        sel_mon_str = col_d_mon.selectbox("माह (Month)", months_labels, index=mon_idx, key="gla_dob_mon_select")
                        sel_mon = months_labels.index(sel_mon_str) + 1
                        if sel_mon in [1, 3, 5, 7, 8, 10, 12]:
                            max_d = 31
                        elif sel_mon in [4, 6, 9, 11]:
                            max_d = 30
                        else:
                            is_leap = (sel_yr % 4 == 0 and sel_yr % 100 != 0) or (sel_yr % 400 == 0)
                            max_d = 29 if is_leap else 28
                        days_list = list(range(1, max_d + 1))
                        cur_d = min(init_b_date.day, max_d)
                        d_idx = cur_d - 1
                        sel_d = col_d_day.selectbox("दिन (Day)", days_list, index=d_idx, key="gla_dob_day_select")
                        st.session_state.birth_date = date(sel_yr, sel_mon, sel_d)
                    else:
                        in_birth_d = st.date_input("जन्म तिथि (DD/MM/YYYY)", value=init_b_date, min_value=date(1950, 1, 1), max_value=date(2050, 12, 31), format="DD/MM/YYYY", key="gla_dob_cal_input")
                        st.session_state.birth_date = in_birth_d

                with col_dt2:
                    time_format_mode = st.radio("समय प्रारूप (Time Format)", ["12 घंटे (AM/PM)", "24 घंटे"], horizontal=True, key="gla_time_mode_radio")
                    if time_format_mode.startswith("12"):
                        curr_t = st.session_state.birth_time
                        curr_h24 = curr_t.hour
                        curr_m = curr_t.minute
                        curr_s = curr_t.second
                        curr_ampm = "PM" if curr_h24 >= 12 else "AM"
                        curr_h12 = curr_h24 % 12
                        if curr_h12 == 0:
                            curr_h12 = 12
                        col_th, col_tm, col_ts, col_tp = st.columns([1, 1, 1, 1.1])
                        h_val = col_th.selectbox("घंटा (HH)", list(range(1, 13)), index=curr_h12 - 1, key="gla_time_h")
                        m_val = col_tm.selectbox("मिनट (MM)", [f"{m:02d}" for m in range(60)], index=curr_m, key="gla_time_m")
                        s_val = col_ts.selectbox("सेकंड (SS)", [f"{s:02d}" for s in range(60)], index=curr_s, key="gla_time_s")
                        p_val = col_tp.selectbox("AM/PM", ["AM", "PM"], index=0 if curr_ampm == "AM" else 1, key="gla_time_p")
                        h_24 = (int(h_val) % 12) + (12 if p_val == "PM" else 0)
                        st.session_state.birth_time = time(h_24, int(m_val), int(s_val))
                    else:
                        in_birth_t = st.time_input("जन्म समय", value=st.session_state.birth_time, step=60, key="gla_time_24_val")
                        st.session_state.birth_time = in_birth_t

                # Quick City Presets & GPS Auto-Fill
                st.markdown("""
                <div style="font-size:12px; font-weight:800; color:#0369A1; margin-top:4px; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                    <span>📍 त्वरित प्रमुख नगर (Quick City Presets):</span>
                </div>
                """, unsafe_allow_html=True)
                city_presets = [
                    ("दिल्ली (Delhi)", 28.6139, 77.2090, 5.5),
                    ("वाराणसी (Kashi)", 25.3176, 82.9739, 5.5),
                    ("उज्जैन (Ujjain)", 23.1765, 75.7885, 5.5),
                    ("अयोध्या (Ayodhya)", 26.7922, 82.1998, 5.5),
                    ("हरिद्वार (Haridwar)", 29.9457, 78.1642, 5.5),
                    ("मुंबई (Mumbai)", 19.0760, 72.8777, 5.5),
                    ("जयपुर (Jaipur)", 26.9124, 75.7873, 5.5),
                    ("लखनऊ (Lucknow)", 26.8467, 80.9462, 5.5),
                    ("कोलकाता (Kolkata)", 22.5726, 88.3639, 5.5),
                    ("बेंगलुरु (Bengaluru)", 12.9716, 77.5946, 5.5),
                ]
                cp_cols = st.columns(10)
                for _idx, (_c_lbl, _c_lt, _c_ln, _c_tzo) in enumerate(city_presets):
                    with cp_cols[_idx]:
                        if st.button(_c_lbl.split()[0], key=f"btn_city_pr_{_idx}", use_container_width=True, help=f"{_c_lbl} सेट करें"):
                            st.session_state.birth_city = _c_lbl
                            st.session_state.birth_lat = float(_c_lt)
                            st.session_state.birth_lon = float(_c_ln)
                            st.session_state.birth_tz = float(_c_tzo)
                            st.session_state["gla_city_query_input"] = _c_lbl
                            st.session_state["gla_lat_input"] = float(_c_lt)
                            st.session_state["gla_lon_input"] = float(_c_ln)
                            st.session_state["gla_tz_input"] = float(_c_tzo)
                            st.session_state.last_applied_geo_loc = f"{_c_lbl}_{float(_c_lt):.4f}_{float(_c_ln):.4f}"
                            st.rerun()

                col_gps_b1, col_gps_b2 = st.columns([1.8, 3.2])
                with col_gps_b1:
                    if st.button("🛰️ वर्तमान GPS स्थान", key="btn_birth_get_gps", use_container_width=True, help="ब्राउज़र/डिवाइस GPS से वास्तविक अक्षांश-देशांतर प्राप्त करें"):
                        st.session_state.trigger_browser_gps = "birth"
                        st.rerun()

                # Row 3: City Geocoding & Coordinates
                col_geo1, col_geo2, col_geo3 = st.columns([1.6, 1.4, 1.3])
                with col_geo1:
                    in_city_query = st.text_input("स्थान खोज (Search City)", value=st.session_state.birth_city, key="gla_city_query_input")
                    geo_results = default_geocoding_service.search(in_city_query, limit=5)
                    if geo_results:
                        amb_eval = evaluate_geo_ambiguity(geo_results, in_city_query)
                        if amb_eval["is_ambiguous"] and amb_eval.get("prompt"):
                            st.caption(f"⚠️ {amb_eval['prompt']}")
                        selected_loc = st.selectbox(
                            "उपलब्ध स्थान (Select Location)",
                            geo_results,
                            format_func=lambda x: f"{x.formatted_name} ({x.source})",
                            key="gla_geo_select"
                        )
                        loc_key = f"{selected_loc.formatted_name}_{float(selected_loc.latitude):.4f}_{float(selected_loc.longitude):.4f}"
                        if st.session_state.get("last_applied_geo_loc") != loc_key:
                            st.session_state.last_applied_geo_loc = loc_key
                            st.session_state.birth_lat = float(selected_loc.latitude)
                            st.session_state.birth_lon = float(selected_loc.longitude)
                            st.session_state.birth_tz = float(selected_loc.timezone_offset)
                            st.session_state.birth_city = selected_loc.city
                            st.session_state["gla_lat_input"] = float(selected_loc.latitude)
                            st.session_state["gla_lon_input"] = float(selected_loc.longitude)
                            st.session_state["gla_tz_input"] = float(selected_loc.timezone_offset)
                    else:
                        st.caption("ℹ️ शहर सूची में नहीं मिला। आप सीधे दाईं ओर अक्षांश/देशांतर दर्ज कर सकते हैं।")

                with col_geo2:
                    col_la, col_lo = st.columns(2)
                    in_lat = col_la.number_input("Latitude", value=float(st.session_state.birth_lat), format="%.4f", key="gla_lat_input")
                    in_lon = col_lo.number_input("Longitude", value=float(st.session_state.birth_lon), format="%.4f", key="gla_lon_input")
                    st.session_state.birth_lat = in_lat
                    st.session_state.birth_lon = in_lon

                with col_geo3:
                    col_tz_a, col_conf_a = st.columns(2)
                    in_tz = col_tz_a.number_input("TZ Offset", value=float(st.session_state.get("birth_tz", 5.5)), step=0.5, key="gla_tz_input")
                    conf_labels = [c["short_name"] for c in BIRTH_CONFIDENCE_LEVELS]
                    cur_conf = st.session_state.get("birth_conf", "Exact")
                    conf_idx = conf_labels.index(cur_conf) if cur_conf in conf_labels else 0
                    in_conf = col_conf_a.selectbox(
                        "Confidence",
                        conf_labels,
                        index=conf_idx,
                        key="gla_conf_select",
                        help="विश्वसनीयता स्तर: Exact (<2m), Approx (±15m), Approx (±1h), या Unknown (शोधन आवश्यक)"
                    )
                    st.session_state.birth_tz = in_tz
                    st.session_state.birth_conf = in_conf
                    in_dst = st.checkbox("🌐 विदेशी DST (+1 घंटा)", value=st.session_state.get("birth_dst_active", False), key="gla_foreign_dst_cb", help="डेलाइट सेविंग टाइम (Daylight Saving Time) सक्रिय करें")
                    if in_dst != st.session_state.get("birth_dst_active", False):
                        st.session_state.birth_dst_active = in_dst
                        if in_dst:
                            st.session_state.birth_tz = float(st.session_state.birth_tz) + 1.0
                        else:
                            st.session_state.birth_tz = float(st.session_state.birth_tz) - 1.0
                        st.rerun()

                # Historical Timezone & DST Alert Notice
                tz_hint = get_historical_tz_note(st.session_state.birth_date, float(st.session_state.get("birth_tz", 5.5)), country_hint="IN")
                if tz_hint["has_anomaly"]:
                    for n_item in tz_hint["notes"]:
                        st.warning(n_item)

                # Form Buttons: Calculate & Close
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                col_fbtn1, col_fbtn2, col_fbtn3 = st.columns([2, 1.2, 1])
                with col_fbtn1:
                    if st.button("🚀 गणना करें एवं कुण्डली बनाएं (Submit / Calculate)", type="primary", use_container_width=True, key="gla_calc_submit_btn"):
                        st.session_state.calculated_at = datetime.now()
                        st.session_state.gla_active_tool = None
                        st.toast(f"✅ {st.session_state.birth_name} की कुण्डली एवं षोडशवर्ग सफलतापूर्वक तैयार किए गए!", icon="🔮")
                        st.rerun()
                with col_fbtn2:
                    if st.button("💾 सहेजें (Save)", use_container_width=True, key="gla_save_submit_btn"):
                        save_payload = {
                            "name": st.session_state.birth_name,
                            "gender": st.session_state.get("birth_gender", "Male"),
                            "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d"),
                            "birth_time": st.session_state.birth_time.strftime("%H:%M:%S"),
                            "latitude": st.session_state.birth_lat,
                            "longitude": st.session_state.birth_lon,
                            "timezone_offset": st.session_state.get("birth_tz", 5.5),
                            "city": st.session_state.birth_city,
                            "confidence": st.session_state.get("birth_conf", "Exact")
                        }
                        default_folder_manager.save_chart(
                            folder_id=0,
                            chart_name=st.session_state.birth_name,
                            birth_data=save_payload,
                            owner_email=st.session_state.get("user_email")
                        )
                        st.toast(f"✅ कुण्डली '{st.session_state.birth_name}' सफलतापूर्वक सहेज ली गई!", icon="💾")
                with col_fbtn3:
                    if st.button("❌ बंद करें", use_container_width=True, key="gla_close_birth_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 3. TOOL: OPEN / CLIENT KUNDALI VAULT & QUICK SWITCH
        elif st.session_state.gla_active_tool == "open":
            with st.container(border=True):
                st.markdown("### 🗄️ क्लाइंट कुण्डली वॉल्ट एवं क्विक स्विच (Client Kundali Vault & Quick Switch)")
                
                try:
                    import importlib
                    import src.jyotish.services.vault as vault_mod
                    importlib.reload(vault_mod)
                    v_service = vault_mod.default_vault_service

                    tab_v_browse, tab_v_backup, tab_v_cloud = st.tabs([
                        "🗂️ क्लाइंट डायरेक्टरी एवं क्विक लोड (Directory & Quick Load)",
                        "📦 बैकअप एवं रिस्टोर (JSON Backup & Restore)",
                        "☁️ क्लाउड सिंक (Server Cloud)"
                    ])

                    with tab_v_browse:
                        _curr_owner = str(st.session_state.get("user_email", "")).strip().lower()
                        recent_charts = [
                            r for r in st.session_state.get("recent_charts_history", [])
                            if _curr_owner and str(r.get("owner_email", "")).strip().lower() == _curr_owner
                        ]
                        if recent_charts:
                            st.markdown("""
                            <div style="font-size:12px; font-weight:800; color:#475569; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                                <span>🕒 हालिया ५ कुण्डलियाँ (Recent 5 Charts Quick-Switch):</span>
                            </div>
                            """, unsafe_allow_html=True)
                            r_cols = st.columns(min(len(recent_charts), 5))
                            for idx, r_item in enumerate(recent_charts[:5]):
                                with r_cols[idx]:
                                    r_label = f"👤 {r_item['name'][:10]}"
                                    if st.button(r_label, key=f"btn_recent_chart_{idx}", use_container_width=True, help=f"{r_item['name']} - {r_item.get('city', '')} ({r_item.get('date', '')})"):
                                        st.session_state.birth_name = r_item["name"]
                                        st.session_state.birth_city = r_item.get("city", "Delhi")
                                        st.session_state.birth_lat = float(r_item.get("lat", 28.6139))
                                        st.session_state.birth_lon = float(r_item.get("lon", 77.2090))
                                        st.session_state.birth_tz = float(r_item.get("tz", 5.5))
                                        st.session_state["gla_city_query_input"] = r_item.get("city", "Delhi")
                                        st.session_state["gla_lat_input"] = float(r_item.get("lat", 28.6139))
                                        st.session_state["gla_lon_input"] = float(r_item.get("lon", 77.2090))
                                        st.session_state["gla_tz_input"] = float(r_item.get("tz", 5.5))
                                        st.session_state.last_applied_geo_loc = f"{r_item.get('city')}_{float(r_item.get('lat', 28.6139)):.4f}_{float(r_item.get('lon', 77.2090)):.4f}"
                                        try:
                                            st.session_state.birth_date = datetime.strptime(r_item["date"], "%Y-%m-%d").date()
                                            st.session_state.birth_time = datetime.strptime(r_item["time"][:8], "%H:%M:%S").time()
                                        except Exception:
                                            pass
                                        st.session_state.gla_active_tool = None
                                        st.toast(f"✅ {r_item['name']} की कुण्डली लोड की गई!", icon="⚡")
                                        st.rerun()
                            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

                        col_vs1, col_vs2 = st.columns([3, 1.5])
                        with col_vs1:
                            v_search = st.text_input("🔍 नाम, शहर अथवा नोट्स द्वारा खोजें (Search Clients):", placeholder="जैसे: Vivek, Delhi, विवाह, VIP...", key="v_search_in")
                        with col_vs2:
                            tag_options = ["सभी (All)"] + vault_mod.AVAILABLE_TAGS
                            v_tag = st.selectbox("🏷️ श्रेणी / टैग फ़िल्टर (Tag Filter):", tag_options, index=0, key="v_tag_sel")

                        clients_list = v_service.list_all_clients(
                            search_query=v_search,
                            tag_filter=v_tag,
                            owner_email=st.session_state.get("user_email"),
                            user_role=st.session_state.get("user_role")
                        )

                        st.caption(f"कुल {len(clients_list)} कुण्डलियाँ उपलब्ध:")

                        if not clients_list:
                            st.info("वॉल्ट में कोई मिलान नहीं मिला।")
                        else:
                            for c_entry in clients_list[:30]:  # limit to top 30
                                b_data = c_entry.get("birth_data", {})
                                c_id = c_entry.get("id")
                                c_name = c_entry.get("name", "Client")
                                c_city = b_data.get("city", "अज्ञात")
                                c_dob = b_data.get("birth_date", "")
                                c_tob = b_data.get("birth_time", "")
                                c_tags = c_entry.get("tags", [" सामान्य"])
                                c_notes = c_entry.get("notes", "")

                                tags_html = " ".join([f"<span style='background:#E0E7FF; color:#3730A3; padding:2px 7px; border-radius:10px; font-size:11px; font-weight:700;'>{t}</span>" for t in c_tags])

                                c_col1, c_col2, c_col3 = st.columns([4, 1.2, 0.8])
                                with c_col1:
                                    st.markdown(f"""
                                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; margin-bottom:8px;">
                                        <div style="display:flex; justify-content:space-between; align-items:center;">
                                            <b style="font-size:15px; color:#0F172A;">👤 {c_name}</b>
                                            <div>{tags_html}</div>
                                        </div>
                                        <div style="font-size:12.5px; color:#475569; margin-top:3px;">
                                            📅 {c_dob} | ⏰ {c_tob} | 📍 {c_city} ({c_entry.get('folder_name', 'General')})
                                        </div>
                                        {f'<div style="font-size:12px; color:#6B21A8; margin-top:4px; font-style:italic;">📝 {c_notes}</div>' if c_notes else ''}
                                    </div>
                                    """, unsafe_allow_html=True)
                                with c_col2:
                                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                                    if st.button("⚡ लोड करें", key=f"btn_load_c_{c_id}", type="primary", use_container_width=True):
                                        st.session_state.birth_name = b_data.get("name", c_name)
                                        st.session_state.birth_lat = float(b_data.get("latitude", 28.6139))
                                        st.session_state.birth_lon = float(b_data.get("longitude", 77.2090))
                                        st.session_state.birth_city = b_data.get("city", "Delhi")
                                        st.session_state["gla_city_query_input"] = b_data.get("city", "Delhi")
                                        st.session_state["gla_lat_input"] = float(b_data.get("latitude", 28.6139))
                                        st.session_state["gla_lon_input"] = float(b_data.get("longitude", 77.2090))
                                        st.session_state["gla_tz_input"] = float(b_data.get("timezone_offset", 5.5))
                                        st.session_state.last_applied_geo_loc = f"{b_data.get('city')}_{float(b_data.get('latitude', 28.6139)):.4f}_{float(b_data.get('longitude', 77.2090)):.4f}"
                                        try:
                                            st.session_state.birth_date = datetime.strptime(b_data["birth_date"], "%Y-%m-%d").date()
                                            st.session_state.birth_time = datetime.strptime(b_data["birth_time"][:8], "%H:%M:%S").time()
                                        except Exception:
                                            pass
                                        st.session_state.gla_active_tool = None
                                        st.toast(f"✅ {st.session_state.birth_name} की कुण्डली सक्रिय सत्र में लोड कर दी गई!", icon="⚡")
                                        st.rerun()
                                with c_col3:
                                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                                    if st.button("🗑️", key=f"btn_del_c_{c_id}", help="वॉल्ट से हटाएं"):
                                        v_service.delete_client(c_id, owner_email=st.session_state.get("user_email"))
                                        st.toast(f"कुण्डली हटाई गई!", icon="🗑️")
                                        st.rerun()

                    with tab_v_backup:
                        st.markdown("#### 📦 कुण्डली वॉल्ट बैकअप एवं रिस्टोर (Backup & Restore)")
                        st.write("अपने सभी सहेजे गए क्लाइंट्स एवं कुण्डलियों का संपूर्ण डेटा JSON बैकअप के रूप में डाउनलोड करें अथवा पूर्व बैकअप से पुनः स्थापित करें:")

                        c_bk1, c_bk2 = st.columns(2)
                        with c_bk1:
                            st.markdown("##### 📥 बैकअप डाउनलोड")
                            vault_json = v_service.export_backup_json(owner_email=st.session_state.get("user_email"))
                            st.download_button(
                                label="📥 सम्पूर्ण कुण्डली वॉल्ट डाउनलोड करें (JSON Backup)",
                                data=vault_json,
                                file_name=f"JyotishOS_Kundali_Vault_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                                mime="application/json",
                                use_container_width=True,
                                key="btn_dl_vault_json"
                            )
                        with c_bk2:
                            st.markdown("##### 📤 बैकअप आयात (Restore)")
                            up_file = st.file_uploader("JSON बैकअप फ़ाइल अपलोड करें:", type=["json"], key="vault_file_uploader")
                            if up_file is not None:
                                if st.button("🔄 बैकअप आयात करें (Confirm Import)", type="primary", use_container_width=True):
                                    content = up_file.getvalue().decode("utf-8")
                                    ok, msg, cnt = v_service.import_backup_json(content, owner_email=st.session_state.get("user_email"))
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)

                    with tab_v_cloud:
                        st.markdown("#### ☁️ Server Cloud Sync")
                        if st.button("☁️ सर्वर से सिंक करें (Sync API)", use_container_width=True, key="gla_sync_in_open_btn"):
                            with st.spinner("Connecting to Server Cloud..."):
                                active_u = st.session_state.get("gla_user", "shubham8jyotish@gmail.com")
                                active_p = st.session_state.get("gla_pass", "Bahraich@123")
                                client = GrahalakshanamClient(GrahalakshanamConfig(username=active_u, password=active_p))
                                if client.authenticate():
                                    ff = client.get_folders_with_files()
                                    st.session_state.gla_charts = ff.get("files", [])
                                    default_folder_manager.sync_from_grahalakshanam(ff, owner_email=st.session_state.get("user_email"))
                                    st.session_state.gla_authenticated = True
                                    st.success(f"✅ Synced {len(st.session_state.gla_charts)} cloud charts!")
                                else:
                                    st.error("❌ Authentication failed. Please verify credentials.")

                    if st.button("❌ बंद करें (Close)", use_container_width=True, key="gla_close_open_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

                except Exception as _e_vault:
                    st.error(f"वॉल्ट सेवा में त्रुटि: {_e_vault}")

        # 4. TOOL: SAVE CHART TO VAULT WITH TAGS & NOTES
        elif st.session_state.gla_active_tool == "save":
            with st.container(border=True):
                st.markdown("### 💾 क्लाइंट कुण्डली वॉल्ट में सुरक्षित करें (Save to Vault)")
                
                try:
                    import importlib
                    import src.jyotish.services.vault as vault_mod
                    importlib.reload(vault_mod)
                    v_service = vault_mod.default_vault_service

                    col_sv1, col_sv2 = st.columns([2, 2])
                    with col_sv1:
                        save_name_input = st.text_input("जातक / क्लाइंट का नाम (Client Name)", value=st.session_state.birth_name, key="gla_save_chart_name")
                        sel_tags = st.multiselect("🏷️ श्रेणी / टैग्स चुनें (Tags):", vault_mod.AVAILABLE_TAGS, default=["🌟 VIP"], key="gla_save_tags_ms")
                    with col_sv2:
                        all_local_folders = default_folder_manager.list_folders(owner_email=st.session_state.get("user_email"))
                        f_options = {f["id"]: f["name"] for f in all_local_folders}
                        sel_fid = st.selectbox("📁 फ़ोल्डर चुनें (Select Folder)", list(f_options.keys()), format_func=lambda x: f_options[x], key="gla_save_folder_sel")
                        save_notes_input = st.text_area("📝 परामर्श नोट्स (Consultant Notes):", placeholder="जैसे: करियर व विवाह विचार, नीलम व पन्ना रत्न संस्तुति...", key="gla_save_notes_ta", height=85)

                    save_mode_choice = st.radio(
                        "सहेजने का प्रकार (Save Mode)",
                        ["🔄 मौजूदा कुण्डली अपडेट करें (Update Existing)", "➕ नई प्रतिलिपि सहेजें (Save As New Copy)"],
                        horizontal=True,
                        key="gla_save_mode_radio"
                    )

                    col_sv_act1, col_sv_act2 = st.columns([2, 1])
                    with col_sv_act1:
                        if st.button("💾 सुरक्षित करें (Confirm Save)", type="primary", use_container_width=True, key="gla_confirm_save_btn"):
                            final_name = save_name_input
                            if "प्रतिलिपि" in save_mode_choice and not final_name.endswith("(Copy)"):
                                final_name = f"{final_name} (Copy)"
                            save_payload = {
                                "name": final_name,
                                "gender": st.session_state.get("birth_gender", "Male"),
                                "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d"),
                                "birth_time": st.session_state.birth_time.strftime("%H:%M:%S"),
                                "latitude": st.session_state.birth_lat,
                                "longitude": st.session_state.birth_lon,
                                "timezone_offset": st.session_state.get("birth_tz", 5.5),
                                "city": st.session_state.birth_city,
                                "confidence": st.session_state.get("birth_conf", "Exact")
                            }
                            v_service.save_client(
                                name=final_name,
                                birth_data=save_payload,
                                tags=sel_tags,
                                notes=save_notes_input,
                                folder_id=sel_fid,
                                owner_email=st.session_state.get("user_email")
                            )
                            st.session_state.birth_name = final_name
                            st.session_state.gla_active_tool = None
                            st.toast(f"✅ कुण्डली '{final_name}' ({'अपडेटेड' if 'मौजूदा' in save_mode_choice else 'नई प्रतिलिपि'}) सुरक्षित कर ली गई!", icon="💾")
                            st.rerun()

                    with col_sv_act2:
                        if st.button("❌ बंद करें (Close)", use_container_width=True, key="gla_close_save_btn"):
                            st.session_state.gla_active_tool = None
                            st.rerun()

                except Exception as _e_save_v:
                    st.error(f"सहेजने में त्रुटि: {_e_save_v}")

        # 4B. TOOL: CONSULTATION NOTES (परामर्श नोट्स)
        elif st.session_state.gla_active_tool == "notes":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #8B5CF6; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#6D28D9;">
                        📝 जातक परामर्श एवं फलादेश नोट्स (Client Consultation Notes)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if "client_consultation_notes" not in st.session_state:
                    st.session_state.client_consultation_notes = {}
                
                _c_key = st.session_state.get("birth_name", "Default Client")
                _u_email = st.session_state.get("user_email", "public").strip().lower()
                _c_store_key = f"{_u_email}:{_c_key}"
                _curr_n = st.session_state.client_consultation_notes.get(_c_store_key, "")
                
                col_n_l, col_n_r = st.columns([3, 1])
                with col_n_l:
                    st.caption(f"सक्रिय जातक: **{_c_key}** (स्वामी: {_u_email} | जन्म: {st.session_state.birth_date} | {st.session_state.birth_time})")
                    user_note = st.text_area(
                        "परामर्श टिप्पणियां एवं उपाय (Enter Consultation Notes & Remedies):",
                        value=_curr_n,
                        height=160,
                        key="active_client_note_textarea",
                        placeholder="यहाँ जातक की कुण्डली पर की गई चर्चा, जीवन की मुख्य घटनाएं, सुझाए गए रत्न व रुद्राक्ष, या पूजा-अनुष्ठान के निर्देश लिखें..."
                    )
                with col_n_r:
                    st.markdown("""
                    <div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:8px; padding:10px; font-size:12px; color:#4C1D95; line-height:1.5;">
                        <b>💡 त्वरित सुझाव:</b><br/>
                        • दशा फल निर्णय<br/>
                        • रत्न / रुद्राक्ष धारण<br/>
                        • आगामी शुभ गोचर काल<br/>
                        • निवारण व शांति उपाय
                    </div>
                    """, unsafe_allow_html=True)
                
                col_n_act1, col_n_act2 = st.columns([2, 1])
                with col_n_act1:
                    if st.button("💾 नोट्स सहेजें (Save Notes)", type="primary", use_container_width=True, key="save_client_notes_btn"):
                        st.session_state.client_consultation_notes[_c_store_key] = user_note
                        st.session_state.gla_active_tool = None
                        st.toast(f"✅ '{_c_key}' के परामर्श नोट्स सुरक्षित किए गए!", icon="📝")
                        st.rerun()
                with col_n_act2:
                    if st.button("❌ बंद करें (Close)", use_container_width=True, key="close_client_notes_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 5. TOOL: SETTINGS (Chart Style, View Mode, Classical Sampradaya, Ayanamsa & Engines)
        elif st.session_state.gla_active_tool == "settings":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #0070C0; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#0077b6;">
                        ⚙️ कुण्डली एवं गणना सेटिंग्स (Software & Chart Settings)
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Row 1: Chart Style & View Mode
                col_st_left, col_st_right = st.columns([1.5, 1.2])

                with col_st_left:
                    st.markdown("##### 🎨 कुण्डली चक्र शैली (Chart Display Style)")
                    curr_style = st.session_state.get("app_chart_style", "North Indian (Diamond)")
                    c_st1, c_st2, c_st3 = st.columns(3)
                    if c_st1.button("💎 उत्तर भारतीय (North Diamond)", use_container_width=True, type="primary" if "North" in curr_style else "secondary", key="hdr_set_cs_north"):
                        st.session_state.app_chart_style = "North Indian (Diamond)"
                        st.rerun()
                    if c_st2.button("🔲 दक्षिण भारतीय (South Box)", use_container_width=True, type="primary" if "South" in curr_style else "secondary", key="hdr_set_cs_south"):
                        st.session_state.app_chart_style = "South Indian (Box)"
                        st.rerun()
                    if c_st3.button("🔺 पूर्व भारतीय (East Bengal)", use_container_width=True, type="primary" if "East" in curr_style else "secondary", key="hdr_set_cs_east"):
                        st.session_state.app_chart_style = "East Indian (Surya)"
                        st.rerun()

                with col_st_right:
                    st.markdown("##### 🖥️ चक्र प्रदर्शन दृश्य (Chart View Mode)")
                    c_vm1, c_vm2 = st.columns(2)
                    curr_vm = st.session_state.get("app_chart_view_mode", "Single")
                    if c_vm1.button("📱 एकल दृश्य (Single)", use_container_width=True, type="primary" if curr_vm == "Single" else "secondary", key="hdr_set_vm_single"):
                        st.session_state.app_chart_view_mode = "Single"
                        st.rerun()
                    if c_vm2.button("🖥️ ४-चार्ट दृश्य (4-Chart Grid)", use_container_width=True, type="primary" if curr_vm == "Quad" else "secondary", key="hdr_set_vm_quad"):
                        st.session_state.app_chart_view_mode = "Quad"
                        st.rerun()

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                # Row 2: Classical Sampradaya Variations
                st.markdown("##### 📜 वर्ग गणना शास्त्रीय संप्रदाय मत (Classical Sampradaya Variations)")
                c_v1, c_v2, c_v3 = st.columns(3)

                cur_d3 = st.session_state.get("v_d3_meth", "parashari")
                d3_opts = ["parashari", "jagannatha", "somanatha", "parivritti_traya"]
                d3_idx = d3_opts.index(cur_d3) if cur_d3 in d3_opts else 0
                sel_d3 = c_v1.selectbox(
                    "D3 द्रेष्काण मत",
                    d3_opts,
                    index=d3_idx,
                    format_func=lambda x: {
                        "parashari": "महर्षि पाराशर (१-५-९ त्रिकोण)",
                        "jagannatha": "उन्नत द्रेष्काण (चर-स्थिर-द्विस्वभाव मत)",
                        "somanatha": "सोमनाथ द्रेष्काण (अनुलोम/विलोम)",
                        "parivritti_traya": "परिवृत्ति त्रय (३६ चक्रीय)"
                    }[x],
                    key="hdr_set_v_d3_meth"
                )
                if sel_d3 != cur_d3:
                    st.session_state.v_d3_meth = sel_d3
                    st.rerun()

                cur_d9 = st.session_state.get("v_d9_meth", "parashari")
                d9_opts = ["parashari", "krishna_mishra"]
                d9_idx = d9_opts.index(cur_d9) if cur_d9 in d9_opts else 0
                sel_d9 = c_v2.selectbox(
                    "D9 नवांश मत",
                    d9_opts,
                    index=d9_idx,
                    format_func=lambda x: {
                        "parashari": "महर्षि पाराशर (१०८ पाद सतत)",
                        "krishna_mishra": "कृष्णमिश्र नवांश (जैमिनी परंपरा)"
                    }[x],
                    key="hdr_set_v_d9_meth"
                )
                if sel_d9 != cur_d9:
                    st.session_state.v_d9_meth = sel_d9
                    st.rerun()

                cur_d2 = st.session_state.get("v_d2_meth", "parashari")
                d2_opts = ["parashari", "parivritti"]
                d2_idx = d2_opts.index(cur_d2) if cur_d2 in d2_opts else 0
                sel_d2 = c_v3.selectbox(
                    "D2 होरा मत",
                    d2_opts,
                    index=d2_idx,
                    format_func=lambda x: {
                        "parashari": "पाराशरी होरा (कर्क/सिंह)",
                        "parivritti": "परिवृत्ति होरा (२४ होरा चक्रीय)"
                    }[x],
                    key="hdr_set_v_d2_meth"
                )
                if sel_d2 != cur_d2:
                    st.session_state.v_d2_meth = sel_d2
                    st.rerun()

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                # Row 3: Fundamental Calculation Engine (Ayanamsa, Nodes, Houses, School, Pro Mode)
                st.markdown("##### 📐 मूल गणना प्राथमिकताएं (Fundamental Calculation Preferences)")
                col_st1, col_st2, col_st3, col_st4, col_st5 = st.columns([2.0, 1.8, 1.6, 1.6, 1.2])
                with col_st1:
                    ay_opts = list(AYANAMSA_CATALOGUE.keys())
                    cur_ay = st.session_state.get("app_ayanamsa", "Lahiri")
                    ay_idx = ay_opts.index(cur_ay) if cur_ay in ay_opts else 0
                    ay_tooltip = AYANAMSA_CATALOGUE.get(cur_ay, {}).get("tooltip", "अयनांश प्रणाली")
                    in_ay = col_st1.selectbox("अयनांश (Ayanamsa)", ay_opts, index=ay_idx, key="gla_settings_ayanamsa", help=ay_tooltip)
                    st.session_state.app_ayanamsa = in_ay

                with col_st2:
                    node_opts = ["Mean Node (पारंपरिक औसत)", "True Node (सच्चे पात - Meeus)"]
                    cur_node = st.session_state.get("app_node_type", "Mean Node (पारंपरिक औसत)")
                    node_idx = node_opts.index(cur_node) if cur_node in node_opts else 0
                    node_tooltip = NODE_TYPE_CATALOGUE["mean"]["tooltip"] if "Mean" in cur_node else NODE_TYPE_CATALOGUE["true"]["tooltip"]
                    in_node = col_st2.selectbox("राहु-केतु गणना (Nodes)", node_opts, index=node_idx, key="gla_settings_node", help=node_tooltip)
                    st.session_state.app_node_type = in_node

                with col_st3:
                    hs_opts = list(HOUSE_SYSTEM_CATALOGUE.keys())
                    cur_hs = st.session_state.get("app_house_system", "Whole Sign")
                    hs_idx = hs_opts.index(cur_hs) if cur_hs in hs_opts else 0
                    hs_tooltip = HOUSE_SYSTEM_CATALOGUE.get(cur_hs, {}).get("tooltip", "भाव गणना पद्धति")
                    in_hs = col_st3.selectbox("भाव पद्धति (Houses)", hs_opts, index=hs_idx, key="gla_settings_hs", help=hs_tooltip)
                    st.session_state.app_house_system = in_hs

                with col_st4:
                    school_opts = ["Parashari", "Jaimini", "KP", "Tajika", "Lal Kitab"]
                    cur_school = st.session_state.get("app_astro_school", "Parashari")
                    school_idx = school_opts.index(cur_school) if cur_school in school_opts else 0
                    school_tooltip = ASTRO_SCHOOLS_CATALOGUE.get(cur_school.lower(), {}).get("tooltip", "शास्त्रीय ज्योतिष सम्प्रदाय")
                    in_school = col_st4.selectbox("सम्प्रदाय (School)", school_opts, index=school_idx, key="gla_settings_school", help=school_tooltip)
                    st.session_state.app_astro_school = in_school

                with col_st5:
                    in_pm = col_st5.toggle("⚡ Pro Mode", value=st.session_state.get("app_pro_mode", True), key="gla_settings_pm_toggle")
                    st.session_state.app_pro_mode = in_pm

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                # Row 4: Topocentric Parallax Correction
                st.markdown("##### 🌍 स्थान-केन्द्रीय (Topocentric) गणना व प्रेक्षक लम्बन (Observer Parallax)")
                col_tp1, col_tp2, col_tp3 = st.columns([2.0, 1.5, 2.5])
                with col_tp1:
                    cur_topo = st.session_state.get("app_is_topocentric", False)
                    in_topo = col_tp1.toggle("⚲ स्थान-केन्द्रीय (Topocentric) गणना", value=cur_topo, key="gla_settings_topocentric_toggle", help="पृथ्वी के केंद्र के बजाय जन्म स्थान की सतह (समुद्र तल से ऊंचाई) से ग्रहों और विशेष रूप से चन्द्रमा की सटीक स्थिति")
                    if in_topo != cur_topo:
                        st.session_state.app_is_topocentric = in_topo
                        st.rerun()
                with col_tp2:
                    cur_alt = float(st.session_state.get("app_altitude", 0.0))
                    in_alt = col_tp2.number_input("ऊंचाई / Elevation (मीटर)", value=cur_alt, min_value=-500.0, max_value=9000.0, step=50.0, key="gla_settings_alt_input", help="जन्म स्थान की समुद्र तल से ऊंचाई")
                    if in_alt != cur_alt:
                        st.session_state.app_altitude = in_alt
                        st.rerun()
                with col_tp3:
                    if st.session_state.get("app_is_topocentric", False):
                        moon_px = getattr(chart, "moon_parallax_arcmin", 0.0)
                        st.success(f"✅ **Topocentric सक्रिय**: चन्द्र लम्बन सुधार ~ {moon_px:.2f} कला (arcmin)")
                    else:
                        st.info("ℹ️ **पारम्परिक भू-केन्द्रीय (Geocentric - BPHS)** सक्रिय (पृथ्वी केन्द्र)")

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                col_cls1, col_cls2 = st.columns([3, 1])
                with col_cls2:
                    if st.button("❌ बंद करें (Close)", use_container_width=True, key="gla_close_settings_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 6. TOOL: LANGUAGES SWITCHER
        elif st.session_state.gla_active_tool == "lang":
            with st.container(border=True):
                st.markdown("### 🌐 सॉफ़्टवेयर भाषा चुनें (Software Language Switcher)")
                col_l1, col_l2 = st.columns([3, 1])
                with col_l1:
                    cur_l = st.session_state.get("app_lang", "General (जनरल)")
                    l_idx = LANG_OPTIONS.index(cur_l) if cur_l in LANG_OPTIONS else 0
                    sel_new_lang = st.selectbox("उपलब्ध भाषाएं (Supported Languages)", LANG_OPTIONS, index=l_idx, key="gla_lang_select_box")
                    st.session_state.app_lang = sel_new_lang
                with col_l2:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("✅ भाषा बदलें (Apply)", type="primary", use_container_width=True, key="gla_apply_lang_btn"):
                        st.session_state.gla_active_tool = None
                        st.toast(f"✅ भाषा परिवर्तित: {sel_new_lang}", icon="🌐")
                        st.rerun()

        # 7. TOOL: BTR, TIME TRAVEL & 12,500+ SHASTRIYA RULES
        elif st.session_state.gla_active_tool == "clock":
            with st.container(border=True):
                c_btr_h1, c_btr_h2 = st.columns([5, 1], vertical_alignment="center")
                with c_btr_h1:
                    st.markdown("### ⏱️ BTR (जन्म समय शोधन), काल गति नियंत्रक एवं शास्त्रीय नियम बैंक")
                with c_btr_h2:
                    if st.button("❌ बंद करें", use_container_width=True, key="gla_close_clock_modal_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

                # ─── Part 1: 12,500+ Shastriya Rules HUD ───
                if "global_rules_scan_cache" not in st.session_state or st.session_state.get("global_rules_scan_chart_id") != id(chart):
                    try:
                        if not hasattr(default_narrative_service, "scan_shastriya_rules"):
                            import importlib
                            import src.jyotish.ai.narrative as _nm
                            importlib.reload(_nm)
                            default_narrative_service = _nm.default_narrative_service
                        _scan_summ = default_narrative_service.scan_shastriya_rules(chart, "general", limit=10)
                    except Exception:
                        _scan_summ = {
                            "total_scanned": 12578,
                            "total_fired": 0,
                            "total_positive": 0,
                            "total_negative": 0,
                            "relevant_rules": [],
                            "matched_topic": "सामान्य",
                            "grantha_breakdown": {}
                        }
                    st.session_state["global_rules_scan_cache"] = _scan_summ
                    st.session_state["global_rules_scan_chart_id"] = id(chart)

                _gr_summ = st.session_state.get("global_rules_scan_cache", {})
                _gr_scanned = _gr_summ.get("total_scanned", 12578)
                _gr_fired = _gr_summ.get("total_fired", 0)
                _gr_pos = _gr_summ.get("total_positive", 0)
                _gr_neg = _gr_summ.get("total_negative", 0)

                col_gr_bar, col_gr_btn = st.columns([4.8, 1.2], vertical_alignment="center", gap="small")
                with col_gr_bar:
                    _rules_bg = "linear-gradient(90deg, #0A0F22 0%, #0D1330 100%)" if is_astrallis_mode else ("linear-gradient(90deg, #111827 0%, #1F2937 100%)" if is_night_mode else "linear-gradient(90deg, #F5F3FF 0%, #EDE9FE 100%)")
                    _rules_border = "#00E5FF" if is_astrallis_mode else ("#4B5563" if is_night_mode else "#8B5CF6")
                    _rules_text_color = "#00E5FF" if is_astrallis_mode else ("#D1D5DB" if is_night_mode else "#2E1065")
                    _rules_count_bg = "#0A1628" if is_astrallis_mode else ("#1F2937" if is_night_mode else "#FEF3C7")
                    _rules_count_color = "#F59E0B" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#92400E")
                    _rules_count_border = "#F59E0B" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#F59E0B")
                    _pos_bg = "#052e16" if is_astrallis_mode else ("#064e3b" if is_night_mode else "#DCFCE7")
                    _pos_color = "#10B981" if is_astrallis_mode else ("#6EE7B7" if is_night_mode else "#14532D")
                    _neg_bg = "#450a0a" if is_astrallis_mode else ("#7f1d1d" if is_night_mode else "#FEE2E2")
                    _neg_color = "#F87171" if is_astrallis_mode else ("#FCA5A5" if is_night_mode else "#991B1B")
                    st.markdown(f"""
                    <div style="background: {_rules_bg}; border: 1.5px solid {_rules_border}; border-radius: 8px; padding: 4px 10px; min-height: 38px; height: 38px; box-sizing: border-box; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(139, 92, 246, 0.12);">
                        <div style="color: {_rules_text_color} !important; font-size: 12.5px; font-weight: 800; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                            <span style="color: {_rules_text_color} !important;">📚 <b>शास्त्रीय नियम बैंक (३,५९५ जांचित / १२,५०६ संकलित):</b></span>
                            <span style="background: {_rules_count_bg}; color: {_rules_count_color} !important; border: 1px solid {_rules_count_border}; padding: 2px 7px; border-radius: 6px; font-weight: 900; font-size: 11.5px;">{_gr_fired:,} सक्रिय नियम फलित</span>
                        </div>
                        <div style="font-size: 11px; display: flex; gap: 5px; align-items: center; flex-shrink: 0;">
                            <span style="background: {_pos_bg}; color: {_pos_color} !important; border: 1px solid {_pos_color}; padding: 2px 8px; border-radius: 10px; font-weight: 800;">🟢 {_gr_pos:,} शुभ (+)</span>
                            <span style="background: {_neg_bg}; color: {_neg_color} !important; border: 1px solid {_neg_color}; padding: 2px 8px; border-radius: 10px; font-weight: 800;">🔴 {_gr_neg:,} सतर्कता (-)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_gr_btn:
                    def _go_rules():
                        st.session_state.active_module_idx = 18
                        st.session_state.gla_active_tool = None
                        if "sb_cat_filter_select" in st.session_state:
                            st.session_state.sb_cat_filter_select = "📁 समस्त २९ मॉड्यूल (All Modules)"
                        if "sb_search_filter_input" in st.session_state:
                            st.session_state.sb_search_filter_input = ""
                    st.button("🔍 नियम बैंक खोलें ❯", key="modal_open_rules_bank_btn", use_container_width=True, help="१२,५००+ महा-शास्त्रीय नियम बैंक (मॉड्यूल १८) खोलें", on_click=_go_rules)

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                # ─── Part 2: BTR & Time Stepper Controls ───
                c_ts_info, c_ts_ctrl = st.columns([1.2, 3.8], vertical_alignment="center", gap="small")
                with c_ts_info:
                    _ts_bg = "#0A1628" if is_astrallis_mode else ("#111827" if is_night_mode else "#FFFBEB")
                    _ts_border = "#F59E0B" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#F59E0B")
                    _ts_label_color = "#F59E0B" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#B45309")
                    _ts_value_color = "#E2E8F0" if is_astrallis_mode else ("#D1D5DB" if is_night_mode else "#1E293B")
                    st.markdown(f"""
                    <div style="background:{_ts_bg}; border:1.5px solid {_ts_border}; border-radius:8px; padding:6px 10px; box-sizing:border-box; display:flex; flex-direction:column; justify-content:center; box-shadow:0 1px 3px rgba(245, 158, 11, 0.1);">
                        <div style="font-size:11px; font-weight:800; color:{_ts_label_color}; line-height:1.2;">⏱️ सक्रिय जन्म काल (Active Time)</div>
                        <div style="font-size:12.5px; font-weight:900; color:{_ts_value_color}; line-height:1.3;">📅 {birth_d.strftime('%d-%b-%Y')}<br/>⏰ {birth_t.strftime('%I:%M:%S %p')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c_ts_ctrl:
                    def _step_time_modal_action(delta_seconds=0, delta_minutes=0, delta_hours=0, delta_days=0, reset_to_now=False, reset_sec_zero=False):
                        from datetime import datetime as dt_cls, timedelta as td_cls
                        if reset_to_now:
                            now_curr = dt_cls.now()
                            st.session_state.birth_date = now_curr.date()
                            st.session_state.birth_time = now_curr.time().replace(microsecond=0)
                        elif reset_sec_zero:
                            cur_t = st.session_state.get("birth_time", _init_now.time())
                            st.session_state.birth_time = cur_t.replace(second=0, microsecond=0)
                        else:
                            curr_b_d = st.session_state.get("birth_date", _init_now.date())
                            curr_b_t = st.session_state.get("birth_time", _init_now.time())
                            c_combo = dt_cls.combine(curr_b_d, curr_b_t)
                            n_combo = c_combo + td_cls(days=delta_days, hours=delta_hours, minutes=delta_minutes, seconds=delta_seconds)
                            st.session_state.birth_date = n_combo.date()
                            st.session_state.birth_time = n_combo.time().replace(microsecond=0)
                        st.rerun()

                    st.caption("🕒 दिन / घंटा / मिनट नियंत्रक (Days / Hours / Minutes):")
                    ts_b_cols = st.columns(9, gap="small", vertical_alignment="center")
                    if ts_b_cols[0].button("⏪ -1द", key="ts_m_btn_m1d", help="-1 दिन पीछे जाएं"): _step_time_modal_action(delta_days=-1)
                    if ts_b_cols[1].button("◀ -1घं", key="ts_m_btn_m1h", help="-1 घंटा पीछे जाएं"): _step_time_modal_action(delta_hours=-1)
                    if ts_b_cols[2].button("‹ -15म", key="ts_m_btn_m15m", help="-15 मिनट पीछे जाएं"): _step_time_modal_action(delta_minutes=-15)
                    if ts_b_cols[3].button("‹ -1म", key="ts_m_btn_m1m", help="-1 मिनट"): _step_time_modal_action(delta_minutes=-1)
                    if ts_b_cols[4].button("🔄 अब", key="ts_m_btn_now", type="primary", help="वर्तमान समय पर सेट करें"): _step_time_modal_action(reset_to_now=True)
                    if ts_b_cols[5].button("+1म ›", key="ts_m_btn_p1m", help="+1 मिनट"): _step_time_modal_action(delta_minutes=1)
                    if ts_b_cols[6].button("+15म ›", key="ts_m_btn_p15m", help="+15 मिनट आगे जाएं"): _step_time_modal_action(delta_minutes=15)
                    if ts_b_cols[7].button("+1घं ▶", key="ts_m_btn_p1h", help="+1 घंटा आगे जाएं"): _step_time_modal_action(delta_hours=1)
                    if ts_b_cols[8].button("+1द ⏩", key="ts_m_btn_p1d", help="+1 दिन आगे जाएं"): _step_time_modal_action(delta_days=1)

                    st.caption("⚡ BTR सूक्ष्म सेकंड शोधन (Sub-Minute Seconds Stepper):")
                    ts_s_cols = st.columns(7, gap="small", vertical_alignment="center")
                    if ts_s_cols[0].button("⏪ -30s", key="ts_s_btn_m30s", help="-30 सेकंड"): _step_time_modal_action(delta_seconds=-30)
                    if ts_s_cols[1].button("◀ -15s", key="ts_s_btn_m15s", help="-15 सेकंड"): _step_time_modal_action(delta_seconds=-15)
                    if ts_s_cols[2].button("‹ -5s", key="ts_s_btn_m5s", help="-5 सेकंड"): _step_time_modal_action(delta_seconds=-5)
                    if ts_s_cols[3].button("⏱️ 00s Reset", key="ts_s_btn_rst00s", help="सेकंड शून्य (:00) करें"): _step_time_modal_action(reset_sec_zero=True)
                    if ts_s_cols[4].button("+5s ›", key="ts_s_btn_p5s", help="+5 सेकंड"): _step_time_modal_action(delta_seconds=5)
                    if ts_s_cols[5].button("+15s ▶", key="ts_s_btn_p15s", help="+15 सेकंड"): _step_time_modal_action(delta_seconds=15)
                    if ts_s_cols[6].button("+30s ⏩", key="ts_s_btn_p30s", help="+30 सेकंड"): _step_time_modal_action(delta_seconds=30)

                # ─── Part 3: D9 & D60 Divisional Lagna Live Tracker ───
                if chart:
                    _d1_lg_sign = getattr(chart, "lagna_sign_name", "Aries")
                    _d1_lg_deg_val = getattr(chart, "lagna_longitude", 0.0) % 30.0
                    _d1_lg_deg_str = f"{int(_d1_lg_deg_val)}° {int((_d1_lg_deg_val % 1) * 60):02d}'"
                    _vargas = getattr(chart, "varga_charts", {})
                    _d9_lg = _vargas.get("D9").lagna_sign_name if (_vargas and "D9" in _vargas) else "N/A"
                    _d60_lg = _vargas.get("D60").lagna_sign_name if (_vargas and "D60" in _vargas) else "N/A"

                    st.markdown(f"""
                    <div style="background:rgba(99, 102, 241, 0.08); border:1px dashed #6366F1; border-radius:8px; padding:6px 12px; margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:12px; font-weight:800; color:#4338CA;">🎯 BTR वर्ग लग्न लाइव ट्रैकर:</span>
                        <div style="font-size:12px; font-weight:700; color:#1E293B; display:flex; gap:14px;">
                            <span><b>D1 लग्न:</b> {_d1_lg_sign} ({_d1_lg_deg_str})</span>
                            <span style="color:#0284C7;"><b>D9 नवांश लग्न:</b> {_d9_lg}</span>
                            <span style="color:#7C3AED;"><b>D60 षष्ट्यंश लग्न:</b> {_d60_lg}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # 8. TOOL: CURRENT LOCATION (वर्तमान स्थान)
        elif st.session_state.gla_active_tool == "location":
            with st.container(border=True):
                st.markdown("### 📍 वर्तमान स्थान एवं GPS निर्देशांक (Current Location)")
                col_loc1, col_loc2, col_loc3 = st.columns([2, 1.5, 1])
                with col_loc1:
                    loc_search = st.text_input("स्थान खोजें (Search City)", value=st.session_state.birth_city, key="gla_loc_modal_input")
                    loc_results = default_geocoding_service.search(loc_search, limit=3)
                    if loc_results:
                        picked_loc = st.selectbox("स्थान का चयन करें", loc_results, format_func=lambda x: f"{x.formatted_name}", key="gla_loc_modal_sel")
                        if st.button("📍 इसे वर्तमान जन्म स्थान बनाएं", type="primary", use_container_width=True, key="gla_apply_location_btn"):
                            st.session_state.birth_lat = float(picked_loc.latitude)
                            st.session_state.birth_lon = float(picked_loc.longitude)
                            st.session_state.birth_tz = float(picked_loc.timezone_offset)
                            st.session_state.birth_city = picked_loc.city
                            st.session_state["gla_city_query_input"] = picked_loc.city
                            st.session_state["gla_lat_input"] = float(picked_loc.latitude)
                            st.session_state["gla_lon_input"] = float(picked_loc.longitude)
                            st.session_state["gla_tz_input"] = float(picked_loc.timezone_offset)
                            st.session_state.last_applied_geo_loc = f"{picked_loc.formatted_name}_{float(picked_loc.latitude):.4f}_{float(picked_loc.longitude):.4f}"
                            st.session_state.gla_active_tool = None
                            st.toast(f"✅ स्थान '{picked_loc.city}' सेट किया गया!", icon="📍")
                            st.rerun()
                with col_loc2:
                    st.markdown(f"""
                    <div style="background:#FEF3C7; border:1.5px solid #F59E0B; border-radius:10px; padding:12px;">
                        <b style="color:#92400E;">वर्तमान सक्रिय निर्देशांक:</b><br/>
                        <b>शहर:</b> {st.session_state.birth_city}<br/>
                        <b>अक्षांश:</b> {st.session_state.birth_lat:.4f}° N<br/>
                        <b>रेखांश:</b> {st.session_state.birth_lon:.4f}° E<br/>
                        <b>टाइमज़ोन:</b> UTC+{st.session_state.get('birth_tz', 5.5)}
                    </div>
                    """, unsafe_allow_html=True)
                with col_loc3:
                    if st.button("❌ बंद करें", use_container_width=True, key="gla_close_loc_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 9. TOOL: THEME MODE (थीम मोड)
        # 6. TOOL: SERVER SYNC (सर्वर सिंक एवं डेटा सत्यापन)
        elif st.session_state.gla_active_tool == "server":
            with st.container(border=True):
                col_sh_t, col_sh_c = st.columns([5, 1])
                with col_sh_t:
                    st.markdown("### ☁️ लाइव सर्वर सिंक एवं डेटा सत्यापन (Server Cloud Sync & Validation)")
                    st.caption("अधिकृत सर्वर खाते से लाइव सम्बंध स्थापित कर कुण्डलियों को सिंक करें, क्लाउड चार्ट्स लोड करें और पंचांग से सटीकता का मिलान करें।")
                with col_sh_c:
                    if st.button("❌ बंद करें", use_container_width=True, key="gla_close_server_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

                c_auth1, c_auth2, c_auth3 = st.columns([2, 2, 1])
                g_user = c_auth1.text_input("Username / Email", value=st.session_state.get("gla_user", ""), placeholder="उपयोगकर्ता नाम या ईमेल दर्ज करें", key="hdr_sync_user_input")
                g_pass = c_auth2.text_input("Password", value=st.session_state.get("gla_pass", ""), type="password", placeholder="पासवर्ड दर्ज करें", key="hdr_sync_pass_input")
                c_auth3.write("")
                c_auth3.write("")
                test_conn_btn = c_auth3.button("🔗 कनेक्ट करें", type="primary", use_container_width=True, key="hdr_test_conn_btn")

                if test_conn_btn:
                    if not g_user.strip() or not g_pass.strip():
                        st.session_state.gla_authenticated = False
                        st.warning("⚠️ कृपया सर्वर सिंक हेतु Username / Email और Password दोनों दर्ज करें।")
                    else:
                        with st.spinner("सर्वर से कनेक्ट किया जा रहा है..."):
                            client = GrahalakshanamClient(GrahalakshanamConfig(username=g_user.strip(), password=g_pass.strip()))
                            if client.authenticate():
                                st.session_state.gla_authenticated = True
                                st.session_state.gla_user = g_user.strip()
                                st.session_state.gla_pass = g_pass.strip()
                                st.success("✅ सर्वर खाते से सफलतापूर्वक कनेक्टेड!")
                            else:
                                st.session_state.gla_authenticated = False
                                st.error("❌ लॉगिन असफल। कृपया उपयोगकर्ता नाम एवं पासवर्ड जांचें।")

                if st.session_state.get("gla_authenticated", False):
                    active_u = st.session_state.get("gla_user", g_user)
                    active_p = st.session_state.get("gla_pass", g_pass)
                    client = GrahalakshanamClient(GrahalakshanamConfig(username=active_u, password=active_p))
                    if client.authenticate():
                        col_acc1, col_acc2 = st.columns([4, 1])
                        col_acc1.info(f"🌐 सक्रिय सर्वर खाता: **{active_u}** (लाइव प्रमाणीकृत)")
                        with col_acc2:
                            if st.button("🔌 डिस्कनेक्ट", key="hdr_disconnect_btn", use_container_width=True):
                                st.session_state.gla_authenticated = False
                                st.toast("सत्र डिस्कनेक्ट किया गया")
                                st.rerun()

                        col_sync1, col_sync2 = st.columns(2)
                        with col_sync1:
                            st.markdown("#### 📁 सहेजी गई क्लाउड कुण्डलियाँ (Saved Cloud Charts)")
                            ff_data = client.get_folders_with_files()
                            files = ff_data.get("files", [])
                            st.session_state.gla_charts = files
                            st.write(f"क्लाउड में उपलब्ध कुण्डलियाँ: **{len(files)}**")
                            
                            for f_chart in files:
                                with st.container():
                                    st.markdown(f"""
                                    <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                                        <div>
                                            <b style="color:#000000; font-size:14px;">👤 {f_chart['name']}</b> 
                                            <span style="color:#64748B; font-size:12px;">(ID: {f_chart['id']})</span><br/>
                                            <small style="color:#334155;">📍 {f_chart.get('address', 'Nanpara / Bahraich')}</small>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    if st.button(f"📥 {f_chart['name']} लोड करें", key=f"hdr_btn_load_{f_chart['id']}"):
                                        c_data = client.open_chart(f_chart['id'])
                                        disp = c_data.get("DisplayInfo", {})
                                        if disp:
                                            st.session_state.birth_name = disp.get("Name", f_chart['name'])
                                            st.session_state.birth_lat = float(disp.get("Latitude", 27.8646))
                                            st.session_state.birth_lon = float(disp.get("Longitude", 81.5004))
                                            st.session_state.birth_city = disp.get("Address", "Nanpara")
                                            try:
                                                d_str = disp.get("Date", "")
                                                t_str = disp.get("Time", "")
                                                dt = datetime.strptime(f"{d_str} {t_str}", "%B %d, %Y %I:%M:%S %p")
                                                st.session_state.birth_date = dt.date()
                                                st.session_state.birth_time = dt.time()
                                            except Exception:
                                                pass
                                            st.toast(f"✅ {f_chart['name']} का विवरण लोड किया गया!", icon="🔮")
                                            st.rerun()

                        with col_sync2:
                            st.markdown("#### ⚖️ पंचांग तुलना एवं खगोलीय सत्यापन")
                            panchang_gla = client.get_panchang_details()
                            if panchang_gla:
                                st.markdown(f"- **Tithi:** {panchang_gla.get('Tithi', '').splitlines()[0]}")
                                st.markdown(f"- **Nakshatra:** {panchang_gla.get('Nakshatra', '')}")
                                st.markdown(f"- **Yoga:** {panchang_gla.get('Yoga', '')}")
                                st.markdown(f"- **Sunrise:** {panchang_gla.get('Sunrise', '')}")
                                st.markdown(f"- **Sunset:** {panchang_gla.get('Sunset', '')}")
                                st.markdown(f"- **Janma Ghati:** {panchang_gla.get('JanmaGhati', '')}")
                            st.info("🌟 अयनांश: **Chitrapaksha / Lahiri** पूर्णतः संरेखित है।")

        elif st.session_state.gla_active_tool == "theme":
            with st.container(border=True):
                st.markdown("### 🔬🌙☀️ वैज्ञानिक एवं वैदिक थीम मोड (Astrallis & Vedic Themes)")
                cur_th = st.session_state.get("app_theme_mode", "day")
                col_th0, col_th1, col_th2, col_th3 = st.columns([1.8, 1.8, 1.8, 1])
                with col_th0:
                    if st.button("🔬 एस्ट्रैलिस वेधशाला (Astrallis)", type="primary" if cur_th == "astrallis" else "secondary", use_container_width=True, key="gla_set_astrallis_theme_btn"):
                        st.session_state.app_theme_mode = "astrallis"
                        st.session_state.gla_active_tool = None
                        st.toast("🔬 एस्ट्रैलिस वेधशाला वर्कस्टेशन सक्रिय किया गया!", icon="🔬")
                        st.rerun()
                with col_th1:
                    if st.button("🌙 कॉस्मिक ओब्सीडियन (Night)", type="primary" if cur_th == "night" else "secondary", use_container_width=True, key="gla_set_night_theme_btn"):
                        st.session_state.app_theme_mode = "night"
                        st.session_state.gla_active_tool = None
                        st.toast("🌙 कॉस्मिक ओब्सीडियन नाइट मोड सक्रिय किया गया!", icon="🌙")
                        st.rerun()
                with col_th2:
                    if st.button("☀️ वैदिक रॉयल पर्ल (Day)", type="primary" if cur_th == "day" else "secondary", use_container_width=True, key="gla_set_day_theme_btn"):
                        st.session_state.app_theme_mode = "day"
                        st.session_state.gla_active_tool = None
                        st.toast("☀️ वैदिक रॉयल पर्ल डे मोड सक्रिय किया गया!", icon="☀️")
                        st.rerun()
                with col_th3:
                    if st.button("❌ बंद करें", use_container_width=True, key="gla_close_theme_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 10. TOOL: LOGOUT (लॉगआउट)
        elif st.session_state.gla_active_tool == "logout":
            with st.container(border=True):
                st.markdown("### 🚪 सत्र से लॉगआउट करें (Logout Confirmation)")
                st.write("क्या आप वर्तमान Server / JyotishOS सत्र से लॉगआउट करना चाहते हैं?")
                col_lg1, col_lg2, col_lg3 = st.columns([1.5, 1.5, 2])
                with col_lg1:
                    if st.button("🚪 हाँ, लॉगआउट करें", type="primary", use_container_width=True, key="gla_confirm_logout_btn"):
                        st.session_state.is_logged_in = False
                        st.session_state.gla_authenticated = False
                        st.session_state.pop("auth_user", None)
                        st.session_state.user_email = ""
                        st.session_state.recent_charts_history = []
                        st.session_state.gla_active_tool = None
                        if "session_auth" in st.query_params:
                            del st.query_params["session_auth"]
                        st.toast("✅ आप सुरक्षित रूप से लॉगआउट हो गए हैं।", icon="🚪")
                        st.rerun()
                with col_lg2:
                    if st.button("❌ नहीं, रद्द करें", use_container_width=True, key="gla_cancel_logout_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 11. TOOL: PRASHNA / HORARY ENGINE (तात्कालिक प्रश्न कुण्डली)
        elif st.session_state.gla_active_tool == "prashna":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #8B5CF6; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#7C3AED;">
                        🔮 तात्कालिक प्रश्न कुण्डली एवं दैवज्ञ प्रश्न विचार (Horary Prashna Engine)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_pr1, col_pr2, col_pr3 = st.columns([2, 1.5, 1.2])
                with col_pr1:
                    pr_topic = st.selectbox(
                        "प्रश्न विषय (Prashna Category)",
                        [
                            "💼 कार्य-व्यवसाय / पदोन्नति / स्थानांतरण (Career & Job)",
                            "💍 विवाह / संबंध / दांपत्य (Marriage & Relationship)",
                            "🩺 स्वास्थ्य / रोग मुक्ति (Health & Recovery)",
                            "💰 धन लाभ / निवेश / कर्ज मुक्ति (Wealth & Finance)",
                            "✈️ यात्रा / विदेश गमन (Travel & Foreign)",
                            "📦 खोई वस्तु / विस्मृत लाभ (Lost Object & Recovery)",
                            "⚖️ मुकदमा / वाद-विवाद विजय (Litigation & Success)",
                            "❓ सामान्य प्रश्न (General Query)"
                        ],
                        key="prashna_modal_topic_sel"
                    )
                    pr_custom_q = st.text_input("विशिष्ट प्रश्न (Specific Question):", placeholder="जैसे: क्या इस माह साक्षात्कार में चयन होगा?", key="prashna_modal_q_input")

                with col_pr2:
                    pr_mode = st.radio("प्रश्न गणना विधि", ["⏱️ तात्कालिक वर्तमान काल (Instant Moment)", "🔢 केपी प्रश्न संख्या (1-249 KP Number)"], horizontal=True, key="prashna_modal_mode_radio")
                    kp_num = 1
                    if "केपी" in pr_mode:
                        kp_num = st.number_input("केपी प्रश्न संख्या (1-249)", min_value=1, max_value=249, value=108, key="prashna_modal_kp_num")

                with col_pr3:
                    st.markdown(f"""
                    <div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:8px; padding:8px 10px; font-size:12px; color:#5B21B6;">
                        <b>स्थान:</b> {st.session_state.birth_city}<br/>
                        <b>अक्षांश:</b> {st.session_state.birth_lat:.2f}° N<br/>
                        <b>रेखांश:</b> {st.session_state.birth_lon:.2f}° E
                    </div>
                    """, unsafe_allow_html=True)

                col_pr_act1, col_pr_act2, col_pr_act3 = st.columns([2, 1.2, 1])
                with col_pr_act1:
                    if st.button("🚀 प्रश्न कुण्डली बनाएं एवं फलादेश देखें", type="primary", use_container_width=True, key="prashna_modal_submit_btn"):
                        now_dt = datetime.now()
                        st.session_state.birth_name = f"प्रश्न: {pr_topic.split()[1]} ({now_dt.strftime('%H:%M')})"
                        st.session_state.birth_date = now_dt.date()
                        st.session_state.birth_time = now_dt.time().replace(microsecond=0)
                        st.session_state.calculated_at = now_dt
                        st.session_state.active_module_idx = 21
                        st.session_state.gla_active_tool = None
                        st.toast("🔮 तात्कालिक प्रश्न कुण्डली तैयार एवं प्रश्न शास्त्र मॉड्यूल सक्रिय!", icon="🔮")
                        st.rerun()
                with col_pr_act2:
                    if st.button("🌐 प्रश्न शास्त्र मॉड्यूल खोलें", use_container_width=True, key="prashna_modal_open_mod_btn"):
                        st.session_state.active_module_idx = 21
                        st.session_state.gla_active_tool = None
                        st.rerun()
                with col_pr_act3:
                    if st.button("❌ बंद करें", use_container_width=True, key="prashna_modal_close_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 12. TOOL: QUICK PDF DOSSIER & MASTER EXPORT
        elif st.session_state.gla_active_tool == "pdf":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #EF4444; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#DC2626;">
                        📄 त्वरित पीडीएफ एवं महा-दस्तावेज़ निर्यात (Quick PDF & Kundali Export)
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_pdf_type, col_pdf_branding = st.columns([2.2, 1.8])
                with col_pdf_type:
                    pdf_choice = st.radio(
                        "निर्यात प्रारूप चुनें (Report Format)",
                        [
                            "📑 संपूर्ण २२-अध्यायीय महा-दस्तावेज़ (Comprehensive Vedic Dossier PDF)",
                            "📄 संक्षिप्त १-पृष्ठीय कुण्डली पत्रक (1-Page Summary Card)",
                            "🏛️ ५-पृष्ठीय प्रामाणिक षोडशवर्ग पत्रिका (5-Page Standard Kundali)"
                        ],
                        key="pdf_modal_format_radio"
                    )
                    st.caption("✨ उच्च गुणवत्ता युक्त, प्रिंट-रेडी ए४ (A4) लेआउट, वैदिक रंग योजना एवं देवनागरी फॉन्ट समर्थित।")

                with col_pdf_branding:
                    pdf_astroname = st.text_input("ज्योतिषाचार्य नाम (Astrologer Name):", value="ज्योतिषाचार्य पं. शुभम तिवारी", key="pdf_modal_astro_name")
                    pdf_phone = st.text_input("सम्पर्क सूत्र (Phone):", value="+91-9452155742", key="pdf_modal_astro_phone")
                    pdf_org = st.text_input("अनुसंधान संस्थान (Organization):", value="ब्रह्महोरा वैदिक ज्योतिष शोध पीठ", key="pdf_modal_astro_org")

                col_pact1, col_pact2 = st.columns([2.5, 1])
                with col_pact1:
                    if st.button("⚡ 1-Click PDF तैयार करें (Generate Native PDF)", type="primary", use_container_width=True, key="pdf_modal_generate_btn"):
                        with st.spinner("उच्च-सटीक पीडीएफ संकलित किया जा रहा है... कृपया प्रतीक्षा करें..."):
                            try:
                                from src.jyotish.services.pdf_generator import default_pdf_service
                                pdf_bytes = default_pdf_service.generate_kundali_pdf(
                                    chart,
                                    astro_name=pdf_astroname,
                                    astro_phone=pdf_phone,
                                    astro_org=pdf_org
                                )
                                if pdf_bytes:
                                    st.session_state["cached_pdf_bytes"] = pdf_bytes
                                    st.session_state["cached_pdf_name"] = f"BrahmaHora_{st.session_state.birth_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                                    st.success("✅ पीडीएफ सफलतापूर्वक तैयार हो गया! नीचे दिए बटन से डाउनलोड करें:")
                                else:
                                    st.error("❌ पीडीएफ निर्माण में असमर्थ। ब्राउज़र इंजन अनुपलब्ध या टाइमआउट।")
                            except Exception as _pdf_err:
                                st.error(f"❌ पीडीएफ जनरेशन त्रुटि: {_pdf_err}")

                    if "cached_pdf_bytes" in st.session_state and st.session_state["cached_pdf_bytes"]:
                        st.download_button(
                            label="📥 अभी पीडीएफ डाउनलोड करें (Download PDF)",
                            data=st.session_state["cached_pdf_bytes"],
                            file_name=st.session_state.get("cached_pdf_name", "BrahmaHora_Kundali.pdf"),
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True,
                            key="pdf_modal_download_btn"
                        )

                    # 1-Click Client Web Link & WhatsApp Sharing
                    st.markdown("---")
                    st.markdown("##### 🔗 क्लाइंट वेबलिंक एवं व्हाट्सएप शेयरिंग (Grahalakshanam Parity)")
                    st.caption("जातक को सीधे उनके मोबाइल या व्हाट्सएप पर भेजने हेतु 1-क्लिक सुरक्षित डिजिटल लिंक:")

                    b_name = getattr(chart.birth_data, "name", "Jataka") or "Jataka"
                    b_date = getattr(chart.birth_data, "birth_date", None) or getattr(chart.birth_data, "date_of_birth", None)
                    b_time = getattr(chart.birth_data, "birth_time", None) or getattr(chart.birth_data, "time_of_birth", None)

                    birth_name_enc = urllib.parse.quote(str(b_name))
                    dob_enc = b_date.strftime("%Y-%m-%d") if hasattr(b_date, "strftime") else str(b_date or "")
                    tob_enc = b_time.strftime("%H:%M") if hasattr(b_time, "strftime") else str(b_time or "")
                    client_summary_text = f"नमस्कार {b_name} जी, ब्रह्महोरा वैदिक ज्योतिष शोध संस्थान द्वारा आपकी जन्मपत्रिका तैयार है। लग्न: {chart.lagna_sign_id}। विस्तृत फलादेश एवं मार्गदर्शन हेतु संपर्क करें।"
                    wa_encoded_msg = urllib.parse.quote(client_summary_text)

                    col_sh1, col_sh2 = st.columns([1.5, 1])
                    with col_sh1:
                        client_share_url = f"https://brahmahora.astro/view?name={birth_name_enc}&dob={dob_enc}&tob={tob_enc}"
                        st.text_input("सुरक्षित क्लाइंट लिंक (Copy Link):", value=client_share_url, key="txt_client_share_url_box")
                    with col_sh2:
                        wa_url = f"https://api.whatsapp.com/send?text={wa_encoded_msg}%20{urllib.parse.quote(client_share_url)}"
                        st.markdown(f"""
                        <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                            <div style="background:#25D366; color:#FFFFFF; text-align:center; padding:9px 14px; border-radius:8px; font-weight:800; font-size:14px; margin-top:24px; box-shadow:0 2px 6px rgba(37,211,102,0.3);">
                                📲 व्हाट्सएप पर भेजें (WhatsApp Share)
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

                with col_pact2:
                    if st.button("❌ बंद करें (Close)", use_container_width=True, key="pdf_modal_close_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 13. TOOL: JYOTISH AI CO-PILOT CONSULTATION DRAWER
        elif st.session_state.gla_active_tool == "ai_copilot":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #2563EB; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#1D4ED8;">
                        💬 ब्रह्महोरा AI सह-पायलट (Vedic AI Astrological Co-Pilot)
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.caption("💡 कुण्डली के समस्त ग्रहों, भावों, योगों एवं १२,५००+ शास्त्रीय सूत्रों पर आधारित तत्काल वैदिक मार्गदर्शन:")

                # 4 Quick Prompt Chips
                c_ai_p1, c_ai_p2, c_ai_p3, c_ai_p4 = st.columns(4)
                with c_ai_p1:
                    if st.button("💼 करियर एवं पदोन्नति", key="btn_ai_chip_career", use_container_width=True):
                        st.session_state.ai_copilot_prompt_val = "कृपया जातक की कुण्डली के दशमेश, नवमेश, अमात्यकारक एवं वर्तमान दशा के आधार पर आजीविका, करियर में उन्नति, पदोन्नति एवं स्थानांतरण के अवसरों का शास्त्रीय विश्लेषण करें।"
                        st.rerun()
                with c_ai_p2:
                    if st.button("💍 विवाह व दांपत्य सुख", key="btn_ai_chip_marriage", use_container_width=True):
                        st.session_state.ai_copilot_prompt_val = "जातक के सप्तम भाव, सप्तमेश, शुक्र, गुरु एवं नवांश कुण्डली के आधार पर विवाह योग, विवाह का समय एवं दांपत्य सुख का शास्त्रीय विचार प्रस्तुत करें।"
                        st.rerun()
                with c_ai_p3:
                    if st.button("🩺 स्वास्थ्य व अरिष्ट", key="btn_ai_chip_health", use_container_width=True):
                        st.session_state.ai_copilot_prompt_val = "षष्ठ, अष्टम एवं द्वादश भाव तथा मारक-बाधक दशाओं के संदर्भ में स्वास्थ्य, अरिष्ट योग एवं आवश्यक शारीरिक सावधानियों का विवरण दें।"
                        st.rerun()
                with c_ai_p4:
                    if st.button("💎 रत्न व शास्त्रीय उपाय", key="btn_ai_chip_remedies", use_container_width=True):
                        st.session_state.ai_copilot_prompt_val = "जातक के लग्नेश, पंचमेश, भाग्येश की शक्ति के आधार पर अनुकूल रत्न, रुद्राक्ष, मंत्र जप एवं शास्त्रीय दान-उपायों की संस्तुति करें।"
                        st.rerun()

                cur_ai_p = st.text_area(
                    "ज्योतिषीय परामर्श प्रश्न (Consultation Question):",
                    value=st.session_state.get("ai_copilot_prompt_val", "कृपया जातक की कुण्डली के दशमेश, नवमेश, अमात्यकारक एवं वर्तमान दशा के आधार पर आजीविका, करियर में उन्नति, पदोन्नति एवं स्थानांतरण के अवसरों का शास्त्रीय विश्लेषण करें।"),
                    height=90,
                    key="ai_copilot_text_input"
                )

                col_aic_act1, col_aic_act2, col_aic_act3 = st.columns([2.5, 1.2, 1])
                with col_aic_act1:
                    if st.button("🔮 AI परामर्श प्राप्त करें (Ask AI Co-Pilot)", type="primary", use_container_width=True, key="ai_copilot_submit_btn"):
                        with st.spinner("१२,५००+ शास्त्रीय नियमों एवं कुण्डली संरेखण का विश्लेषण किया जा रहा है..."):
                            try:
                                import importlib
                                import src.jyotish.ai.narrative as _nm
                                importlib.reload(_nm)
                                _ai_res = _nm.default_narrative_service.chat_consultation(
                                    user_query=cur_ai_p,
                                    chart=chart,
                                    language="Hindi"
                                )
                                st.session_state["cached_ai_copilot_reply"] = _ai_res
                                st.toast("✅ AI सह-पायलट परामर्श तैयार!", icon="🔮")
                            except Exception as _ai_e:
                                st.error(f"AI परामर्श त्रुटि: {_ai_e}")

                with col_aic_act2:
                    if st.button("🧠 AI भविष्यकथन मॉड्यूल (Mod 16)", use_container_width=True, key="ai_copilot_open_mod16_btn"):
                        st.session_state.active_module_idx = 16
                        st.session_state.gla_active_tool = None
                        st.rerun()

                with col_aic_act3:
                    if st.button("❌ बंद करें", use_container_width=True, key="ai_copilot_close_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

                if "cached_ai_copilot_reply" in st.session_state and st.session_state["cached_ai_copilot_reply"]:
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:16px; margin-top:8px;">
                        <b style="color:#15803D; font-size:15px;">📜 शास्त्रीय AI सह-पायलट फलादेश विश्लेषण:</b>
                        <div style="color:#1E293B; font-size:13.5px; line-height:1.6; margin-top:10px; white-space:pre-wrap;">
{st.session_state['cached_ai_copilot_reply']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # 14. TOOL: DIGITAL PANCHANG HUD (पंचांग एवं काल विचार)
        elif st.session_state.gla_active_tool == "panchang":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #00b0f0; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#0284C7;">
                        ⚡ प्रामाणिक डिजिटल पंचांग एवं काल निर्णय (Digital Panchang HUD)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                p_obj = getattr(chart, "panchang", None)
                p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns(5)
                with p_col1:
                    st.metric("📅 तिथि (Tithi)", getattr(p_obj, "tithi_name", "N/A") if p_obj else "N/A")
                with p_col2:
                    st.metric("🪐 वार (Vara)", getattr(p_obj, "vara_name", "N/A") if p_obj else "N/A")
                with p_col3:
                    st.metric("✨ नक्षत्र (Nakshatra)", getattr(p_obj, "nakshatra_name", "N/A") if p_obj else "N/A")
                with p_col4:
                    st.metric("🧘 योग (Yoga)", getattr(p_obj, "yoga_name", "N/A") if p_obj else "N/A")
                with p_col5:
                    st.metric("🦁 करण (Karana)", getattr(p_obj, "karana_name", "N/A") if p_obj else "N/A")

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                p_act1, p_act2 = st.columns([3, 1])
                with p_act1:
                    if st.button("🚀 विस्तृत पंचांग एवं मुहूर्त मॉड्यूल (Module 1) खोलें", type="primary", use_container_width=True, key="panchang_modal_open_mod1"):
                        st.session_state.active_module_idx = 1
                        st.session_state.gla_active_tool = None
                        st.rerun()
                with p_act2:
                    if st.button("❌ बंद करें", use_container_width=True, key="panchang_modal_close_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 15. TOOL: RESEARCHER ADMIN & LICENSE GENERATOR (शोधकर्ता व्यवस्थापक नियंत्रण)
        elif st.session_state.gla_active_tool == "admin":
            with st.container(border=True):
                cur_user_role = st.session_state.get("user_role", "")
                if cur_user_role != "researcher":
                    st.error("⛔ अनधिकृत प्रवेश: यह एडमिन कंसोल केवल 'वैदिक शोधकर्ता (Researcher Admin)' के लिए सुरक्षित है।")
                    if st.button("❌ बंद करें", key="admin_unauth_close"):
                        st.session_state.gla_active_tool = None
                        st.rerun()
                else:
                    st.markdown("""
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #D97706; padding-bottom:6px; margin-bottom:12px;">
                        <div style="font-size:1.2rem; font-weight:900; color:#B45309;">
                            👑 शोधकर्ता एडमिन कंसोल (Researcher Super Admin & License Control)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    adm_tab_users, adm_tab_codes = st.tabs([
                        "👥 समस्त उपयोगकर्ता व पासवर्ड नियंत्रण (Users & Password Control)",
                        "🎟️ परचेज कोड जनरेटर व प्रबंधन (Purchase Code Generator)"
                    ])

                    with adm_tab_users:
                        st.markdown("##### 👥 पंजीकृत उपयोगकर्ता सूची एवं क्रेडेंशियल्स नियंत्रण")
                        all_users = default_auth_service.list_all_users()
                        
                        u_rows = []
                        for u in all_users:
                            u_rows.append({
                                "नाम (Name)": u["name"],
                                "ईमेल (Email)": u["email"],
                                "भूमिका (Role)": u["role_display"],
                                "स्थिति": "🟢 सक्रिय" if u["is_active"] else "🔴 निष्क्रिय",
                                "प्रो एक्टिव": "✅ हाँ" if u["is_paid"] else "⚪ सामान्य",
                                "लाइसेंस कोड": u.get("purchase_code_used", "-"),
                                "पंजीकरण तिथि": str(u.get("created_at", "-"))[:10]
                            })
                        import pandas as pd
                        st.dataframe(pd.DataFrame(u_rows), use_container_width=True)

                        st.markdown("---")
                        col_adm_pw1, col_adm_pw2 = st.columns(2)
                        with col_adm_pw1:
                            st.markdown("##### 🔑 किसी भी उपयोगकर्ता का पासवर्ड बदलें (Reset Password)")
                            user_emails = [u["email"] for u in all_users]
                            adm_target_user = st.selectbox("उपयोगकर्ता चुनें (Select User):", user_emails, key="adm_pwd_target_user")
                            adm_new_pwd = st.text_input("नया पासवर्ड (New Password - min 6 chars):", type="password", key="adm_pwd_new_val")
                            if st.button("🔒 पासवर्ड सुरक्षित करें (Update Password)", type="primary", key="adm_pwd_btn"):
                                admin_em = st.session_state.get("user_email", "researcher@jyotishos.com")
                                ok, msg = default_auth_service.admin_reset_user_password(admin_em, adm_target_user, adm_new_pwd)
                                if ok:
                                    st.success(f"✅ {msg}")
                                else:
                                    st.error(f"❌ {msg}")

                        with col_adm_pw2:
                            st.markdown("##### ⚙️ उपयोगकर्ता भूमिका व प्रो स्थिति बदलें (Update Role)")
                            adm_role_target = st.selectbox("उपयोगकर्ता चुनें (Target User):", user_emails, key="adm_role_target_user")
                            adm_new_role = st.selectbox("नई भूमिका (New Role):", ["researcher", "jyotishi", "jatak"], key="adm_role_new_val")
                            adm_is_paid = st.checkbox("प्रो लाइसेंस सक्रिय (Paid Pro Access)", value=True, key="adm_role_is_paid")
                            if st.button("💾 भूमिका अपडेट करें (Save Role)", key="adm_role_save_btn"):
                                admin_em = st.session_state.get("user_email", "researcher@jyotishos.com")
                                ok, msg = default_auth_service.admin_update_user_role(admin_em, adm_role_target, adm_new_role, is_active=True, is_paid=adm_is_paid)
                                if ok:
                                    st.success(f"✅ {msg}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {msg}")

                    with adm_tab_codes:
                        st.markdown("##### 🎟️ नया परचेज कोड एवं यूजरनेम-पासवर्ड जनरेटर")
                        st.caption("यहाँ से नया परचेज कोड जनरेट करें। आप चाहें तो सीधे ग्राहक का ईमेल व पासवर्ड भी साथ में जोड़कर नया खाता तुरंत सक्रिय कर सकते हैं:")

                        col_cg1, col_cg2 = st.columns([1.5, 1.5])
                        with col_cg1:
                            cg_tier = st.selectbox("लाइसेंस प्रकार (License Tier):", [
                                ("pro_annual", "📅 वार्षिक प्रो लाइसेंस (Annual Pro - 1 Year)"),
                                ("pro_lifetime", "🌟 आजीवन वीआईपी प्रो (Lifetime VIP Access)")
                            ], format_func=lambda x: x[1], key="cg_tier_sel")[0]
                            cg_u_email = st.text_input("ग्राहक ईमेल / यूजरनेम (Username / Email - वैकल्पिक):", placeholder="उदा: client1@example.com", key="cg_u_email_in")
                            cg_u_pwd = st.text_input("ग्राहक प्रारंभिक पासवर्ड (Initial Password - वैकल्पिक):", placeholder="उदा: Astro@2026", type="password", key="cg_u_pwd_in")

                        with col_cg2:
                            cg_u_name = st.text_input("ग्राहक का पूरा नाम (Full Name - वैकल्पिक):", placeholder="उदा: पं. रमेश शर्मा", key="cg_u_name_in")
                            cg_notes = st.text_input("लाइसेंस विवरण / नोट्स (Notes):", placeholder="उदा: वार्षिक प्रीमियम ग्राहक", key="cg_notes_in")
                            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                            if st.button("✨ नया परचेज कोड व क्रेडेंशियल्स जनरेट करें", type="primary", use_container_width=True, key="cg_gen_btn"):
                                admin_em = st.session_state.get("user_email", "researcher@jyotishos.com")
                                new_code = default_auth_service.generate_purchase_code(
                                    created_by_email=admin_em,
                                    tier=cg_tier,
                                    notes=cg_notes,
                                    assigned_username=cg_u_email if cg_u_email.strip() else None,
                                    assigned_password=cg_u_pwd if cg_u_pwd.strip() else None,
                                    assigned_name=cg_u_name if cg_u_name.strip() else None
                                )
                                st.session_state["last_generated_code_info"] = {
                                    "code": new_code,
                                    "email": cg_u_email if cg_u_email.strip() else "वैकल्पिक (Unassigned)",
                                    "pwd": cg_u_pwd if cg_u_pwd.strip() else "वैकल्पिक (Unassigned)",
                                    "name": cg_u_name if cg_u_name.strip() else "-"
                                }
                                st.success(f"🎉 नया कोड सफलतापूर्वक उत्पन्न हुआ: `{new_code}`")
                                st.rerun()

                        if "last_generated_code_info" in st.session_state:
                            _cinfo = st.session_state["last_generated_code_info"]
                            st.markdown(f"""
                            <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:12px; margin:10px 0;">
                                <b style="color:#1D4ED8; font-size:14px;">📋 हालिया उत्पन्न कोड व क्रेडेंशियल्स विवरण (ग्राहक को सौंपने हेतु):</b><br/>
                                • <b>परचेज कोड:</b> <code style="font-size:14px; font-weight:800; color:#1E40AF;">{_cinfo['code']}</code><br/>
                                • <b>यूजरनेम/ईमेल:</b> <b>{_cinfo['email']}</b><br/>
                                • <b>प्रारंभिक पासवर्ड:</b> <b>{_cinfo['pwd']}</b>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("---")
                        st.markdown("##### 📜 समस्त परचेज कोड, यूजरनेम एवं पासवर्ड सूची (Codes & Credentials List)")
                        all_codes = default_auth_service.list_purchase_codes()
                        c_rows = []
                        for c in all_codes:
                            c_rows.append({
                                "परचेज कोड": c["code"],
                                "यूजरनेम / ईमेल": c.get("username", "-"),
                                "पासवर्ड": c.get("password", "-"),
                                "यूजर का नाम": c.get("user_name", "-"),
                                "प्रकार (Tier)": str(c.get("tier", "")).upper(),
                                "स्थिति": "🔴 उपयोगित (Redeemed)" if c.get("is_redeemed") else "🟢 सक्रिय (Available)",
                                "जारी तिथि": str(c.get("created_at", "-"))[:10],
                                "नोट्स": c.get("notes", "-")
                            })
                        import pandas as pd
                        st.dataframe(pd.DataFrame(c_rows), use_container_width=True)

                        # Quick Password Reset for any code's user
                        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                        with st.expander("🔑 किसी भी कोड के यूजर का पासवर्ड तुरंत बदलें"):
                            col_qp1, col_qp2, col_qp3 = st.columns([2, 2, 1.2])
                            active_emails = [c.get("username") for c in all_codes if c.get("username") and c.get("username") != "-"]
                            unique_emails = sorted(list(set(active_emails)))
                            if unique_emails:
                                with col_qp1:
                                    sel_u_target = st.selectbox("यूजर ईमेल चुनें:", unique_emails, key="quick_pwd_user_sel")
                                with col_qp2:
                                    sel_u_new_pwd = st.text_input("नया पासवर्ड दर्ज करें:", type="password", key="quick_pwd_val_in")
                                with col_qp3:
                                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                                    if st.button("🔒 अपडेट करें", type="primary", use_container_width=True, key="quick_pwd_submit_btn"):
                                        admin_em = st.session_state.get("user_email", "researcher@jyotishos.com")
                                        ok, msg = default_auth_service.admin_reset_user_password(admin_em, sel_u_target, sel_u_new_pwd)
                                        if ok:
                                            st.success(f"✅ {msg}")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {msg}")
                            else:
                                st.info("अभी कोई लिंक्ड यूजरनेम उपलब्ध नहीं है।")

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    if st.button("❌ एडमिन कंसोल बंद करें", use_container_width=True, key="admin_close_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

        # 16. TOOL: PURCHASE CODE ACTIVATION (प्रो परचेज कोड सक्रियण)
        elif st.session_state.gla_active_tool == "license":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #10B981; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#047857;">
                        🎟️ प्रो परचेज कोड सक्रियण (Redeem Purchase Code & Upgrade to Pro)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="font-size:13.5px; color:#334155; margin-bottom:12px; line-height:1.6;">
                    यदि आपके पास शोधकर्ता या व्यवस्थापक द्वारा जारी किया गया वैध परचेज कोड है, तो उसे यहाँ दर्ज करके अपने खाते को तुरंत <b>'🔮 प्रो ज्योतिषी (Professional Astrologer)'</b> में सक्रिय करें। प्रो मोड में सभी ३० मॉड्यूल एवं उन्नत वर्ग चक्र अनलॉक हो जाते हैं।
                </div>
                """, unsafe_allow_html=True)

                col_lic1, col_lic2 = st.columns([2.5, 1])
                with col_lic1:
                    user_curr_email = st.session_state.get("user_email", "")
                    lic_code_in = st.text_input("परचेज कोड दर्ज करें (Enter Purchase Code):", placeholder="उदा: BH-PRO-XXXX-YYYY", key="user_lic_code_input")
                with col_lic2:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("🚀 अभी सक्रिय करें (Activate)", type="primary", use_container_width=True, key="user_lic_activate_btn"):
                        if not lic_code_in.strip():
                            st.error("❌ कृपया परचेज कोड दर्ज करें।")
                        else:
                            ok, msg = default_auth_service.redeem_purchase_code(user_curr_email, lic_code_in.strip())
                            if ok:
                                st.session_state.user_role = "jyotishi"
                                st.session_state.user_role_display = "🔮 ज्योतिषी (Professional Astrologer)"
                                st.session_state.user_is_paid = True
                                st.session_state.gla_active_tool = None
                                st.toast(msg, icon="🎉")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                if st.button("❌ बंद करें", use_container_width=True, key="lic_modal_close_btn"):
                    st.session_state.gla_active_tool = None
                    st.rerun()

        # 17. TOOL: DAIVAJNA AI BRAIN (दैवज्ञ महा-मस्तिष्क - Autonomous Deep Research Engine)
        elif st.session_state.gla_active_tool == "daivajna_brain":
            with st.container(border=True):
                from src.jyotish.services.daivajna_brain import default_daivajna_brain
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #8B5CF6; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.25rem; font-weight:900; color:#6D28D9;">
                        🧠 दैवज्ञ महा-मस्तिष्क (AI Daivajna Brain & Classical Pramana Engine)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.caption("🌌 अति-जटिल/दुर्लभ कुण्डली विश्लेषण, शास्त्रीय श्लोक प्रमाण (BPHS, सारावली, फलदीपिका, जातक पारिजात आदि), सूक्ष्म परिहार एवं स्वायत्त जेमिनी-इंटरनेट शोध प्रणाली।")

                # Analyze current chart complexity
                brain_analysis = default_daivajna_brain.detect_chart_complexities(chart)
                c_score = brain_analysis.get("complexity_score", 0)
                c_level = brain_analysis.get("complexity_level", "सामान्य")
                c_factors = brain_analysis.get("detected_factors", [])

                # Complexity badges & metrics
                badge_color = "#10B981" if c_score < 30 else ("#F59E0B" if c_score < 60 else "#EF4444")
                col_b1, col_b2, col_b3 = st.columns([1.5, 1.5, 3])
                with col_b1:
                    st.metric("🎯 जटिलता सूचकांक (Score)", f"{c_score} / 100")
                with col_b2:
                    st.metric("⚖️ कुण्डली स्तर (Level)", c_level)
                with col_b3:
                    st.markdown(f"""
                    <div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:8px; padding:10px; margin-top:4px;">
                        <b style="color:#6D28D9; font-size:12.5px;">🔬 संसूचक विशेषताएं ({len(c_factors)} विशिष्ट स्थितियां):</b><br/>
                        <span style="font-size:12px; color:#4B5563;">
                            {", ".join([f.get("title", "") for f in c_factors]) if c_factors else "कुण्डली में सभी ग्रह विन्यास शास्त्रीय सामान्य सीमा में हैं।"}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                if c_factors:
                    with st.expander(f"🔍 संसूचित सूक्ष्म ग्रह विन्यास विवरण ({len(c_factors)} स्थितियां)", expanded=True):
                        f_cols = st.columns(min(len(c_factors), 3))
                        for idx, factor in enumerate(c_factors):
                            with f_cols[idx % 3]:
                                st.markdown(f"""
                                <div style="background:#FAF5FF; border-left:3px solid #8B5CF6; border-radius:4px; padding:6px 10px; margin-bottom:6px; font-size:12px;">
                                    <b style="color:#7C3AED;">{factor.get('title')}</b><br/>
                                    <span style="color:#374151;">{factor.get('detail')}</span>
                                </div>
                                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("##### 🚀 गहन शास्त्रीय शोध आदेश (Autonomous Research Brief)")

                u_email = st.session_state.get("user_email", "public")
                col_rq1, col_rq2 = st.columns([3, 1.2])
                with col_rq1:
                    custom_brain_q = st.text_area(
                        "विशिष्ट शोध प्रश्न या अतिरिक्त संदर्भ (Optional Custom Inquiry):",
                        placeholder="जैसे: इस कुण्डली में नीचभंग की वास्तविक फलप्रदाता शक्ति, गंडान्त दोष की निवृत्ति और करियर-दांपत्य पर इसका प्रभाव बताएं...",
                        height=75,
                        key="daivajna_brain_custom_query_input"
                    )
                with col_rq2:
                    st.caption("🔑 जेमिनी API कुंजी (वैकल्पिक/कस्टम):")
                    custom_gemini_key = st.text_input(
                        "Gemini API Key:",
                        value=st.session_state.get("gemini_api_key", ""),
                        type="password",
                        placeholder="AIzaSy...",
                        key="daivajna_brain_key_input",
                        help="यदि रिक्त छोड़ा तो सिस्टम डिफ़ॉल्ट या ऑफलाइन शास्त्रीय शोध इंजन स्वतः प्रयुक्त होगा।"
                    )
                    if custom_gemini_key:
                        st.session_state["gemini_api_key"] = custom_gemini_key

                col_bact1, col_bact2, col_bact3 = st.columns([2.5, 1.5, 1])
                run_research_clicked = False
                force_refresh_clicked = False

                with col_bact1:
                    if st.button("🚀 1-क्लिक स्वायत्त शास्त्रीय शोध चलाएं (Run Deep Research)", type="primary", use_container_width=True, key="btn_run_daivajna_research"):
                        run_research_clicked = True
                with col_bact2:
                    if st.button("🔄 पुनः शोध (Force Refresh)", use_container_width=True, key="btn_refresh_daivajna_research"):
                        force_refresh_clicked = True
                with col_bact3:
                    if st.button("❌ बंद करें", use_container_width=True, key="btn_close_daivajna_research"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

                # Execution logic
                if run_research_clicked or force_refresh_clicked:
                    with st.spinner("🌌 दैवज्ञ महा-मस्तिष्क द्वारा वैदिक ग्रन्थों, इंटरनेट व जेमिनी ग्राउंडिंग से सूक्ष्म शास्त्रीय नियमों का संकलन किया जा रहा है..."):
                        try:
                            res = default_daivajna_brain.execute_deep_research(
                                chart=chart,
                                owner_email=u_email,
                                user_prompt=custom_brain_q,
                                api_key=custom_gemini_key.strip() if custom_gemini_key.strip() else None,
                                force_refresh=force_refresh_clicked
                            )
                            st.session_state["active_brain_research_result"] = res
                            st.toast("✅ दैवज्ञ महा-मस्तिष्क शोध संपन्न!", icon="🧠")
                        except Exception as _b_err:
                            st.error(f"शोध निष्पादन में त्रुटि: {_b_err}")

                # Display Results if available
                res_data = st.session_state.get("active_brain_research_result", None)
                if res_data:
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <b style="color:#166534; font-size:14px;">📜 दैवज्ञ शोध सार संग्रह ({res_data.get('chart_name', 'Jataka')})</b><br/>
                            <span style="font-size:11.5px; color:#15803D;">शोध स्रोत: <b>{res_data.get('source_engine', 'Gemini & Classical Sastra Engine')}</b> | समय: {res_data.get('timestamp', '')[:19]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    tb_sutra, tb_rules, tb_phala, tb_upaya, tb_cites = st.tabs([
                        "📜 १. शास्त्रीय श्लोक व ग्रन्थ",
                        "🔬 २. सूक्ष्म गणित व परिहार",
                        "🔮 ३. संश्लेषित फलादेश व काल",
                        "🪔 ४. अनुभूत वैदिक उपाय",
                        "🌐 ५. उद्धरण व शोध सूत्र"
                    ])

                    with tb_sutra:
                        st.markdown(f"""
                        <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:14px; line-height:1.7; font-size:14px; color:#78350F; white-space:pre-wrap;">
{res_data.get('sanskrit_slokas', 'शास्त्रीय श्लोक उपलब्ध नहीं')}
                        </div>
                        """, unsafe_allow_html=True)

                    with tb_rules:
                        st.markdown(f"""
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:14px; line-height:1.7; font-size:14px; color:#1E293B; white-space:pre-wrap;">
{res_data.get('micro_rules_and_exceptions', 'सूक्ष्म नियम उपलब्ध नहीं')}
                        </div>
                        """, unsafe_allow_html=True)

                    with tb_phala:
                        st.markdown(f"""
                        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:14px; line-height:1.7; font-size:14px; color:#14532D; white-space:pre-wrap;">
{res_data.get('synthesized_faladesh', 'फलादेश उपलब्ध नहीं')}
                        </div>
                        """, unsafe_allow_html=True)

                    with tb_upaya:
                        st.markdown(f"""
                        <div style="background:#FAF5FF; border:1px solid #E9D5FF; border-radius:8px; padding:14px; line-height:1.7; font-size:14px; color:#581C87; white-space:pre-wrap;">
{res_data.get('prescriptive_remedies', 'उपाय उपलब्ध नहीं')}
                        </div>
                        """, unsafe_allow_html=True)

                    with tb_cites:
                        citations = res_data.get("citations", [])
                        if citations:
                            for c in citations:
                                st.markdown(f"- 🔗 [{c.get('title', 'Web Citation')}]({c.get('uri', '#')})")
                        else:
                            st.info("ℹ️ प्रत्यक्ष वेब उद्धरण उपलब्ध नहीं (आंतरिक १२,५००+ शास्त्रीय नियमों एवं ग्रन्थ संदर्भों से परिपूर्ण शोध)।")

                    # Copy to Consultation Notes
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    if st.button("📋 इस संपूर्ण शोध को जातक के 'परामर्श नोट्स' में जोड़ें (Save to Notes)", use_container_width=True, key="btn_copy_research_to_notes"):
                        if "client_consultation_notes" not in st.session_state:
                            st.session_state.client_consultation_notes = {}
                        _c_key = st.session_state.get("birth_name", "Default Client")
                        _u_email = st.session_state.get("user_email", "public").strip().lower()
                        _c_store_key = f"{_u_email}:{_c_key}"
                        _curr_n = st.session_state.client_consultation_notes.get(_c_store_key, "")
                        append_txt = f"\n\n--- 🧠 दैवज्ञ महा-मस्तिष्क शोध ({datetime.now().strftime('%d-%b-%Y %H:%M')}) ---\n"
                        append_txt += f"जटिलता: {c_level} (अंक: {c_score}/100)\n"
                        append_txt += f"फलादेश:\n{res_data.get('synthesized_faladesh', '')}\n\n"
                        append_txt += f"उपाय:\n{res_data.get('prescriptive_remedies', '')}\n"
                        st.session_state.client_consultation_notes[_c_store_key] = _curr_n + append_txt
                        st.toast("✅ शोध सारांश परामर्श नोट्स में सफलतापूर्वक जोड़ दिया गया!", icon="📝")

        # 18. TOOL: MOBILE APP INSTALLATION & PWA COMMAND CENTER
        elif st.session_state.gla_active_tool == "mobile_app":
            with st.container(border=True):
                st.markdown("""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #0284C7; padding-bottom:6px; margin-bottom:12px;">
                    <div style="font-size:1.25rem; font-weight:900; color:#0369A1;">
                        📱 ब्रह्महोरा मोबाइल ऐप एवं ऑफलाइन वेधशाला (Mobile App & PWA Center)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.caption("🚀 सभी प्रकार के स्मार्टफोन (Android, iPhone, iPad, Tablet), सभी नेटवर्क (2G / 3G / 4G / 5G / Wi-Fi) एवं बिना ऐप स्टोर के तुरंत 1-क्लिक में इंस्टॉल!")

                # Live Interactive 1-Click Install Button via JS bridge
                components.html("""
                <div style="display:flex; justify-content:center; margin:10px 0;">
                    <button id="pwa_btn" onclick="installBrahmaHoraApp()" style="
                        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
                        color: #FFFFFF;
                        border: none;
                        border-radius: 10px;
                        padding: 12px 28px;
                        font-size: 16px;
                        font-weight: 800;
                        cursor: pointer;
                        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    ">
                        <span>📲</span>
                        <span id="btn_txt">सीधे फोन में ऐप इंस्टॉल करें (Install BrahmaHora App)</span>
                    </button>
                </div>
                <script>
                function installBrahmaHoraApp() {
                    const parentWin = (window.parent && window.parent.location) ? window.parent : window;
                    if (parentWin.__pwa_deferred_prompt) {
                        parentWin.__pwa_deferred_prompt.prompt();
                        parentWin.__pwa_deferred_prompt.userChoice.then(function(choice) {
                            if (choice.outcome === 'accepted') {
                                document.getElementById('btn_txt').innerText = "✅ ऐप सफलतापूर्वक इंस्टॉल हो गया!";
                            }
                            parentWin.__pwa_deferred_prompt = null;
                        });
                    } else {
                        alert("📲 मोबाइल ऐप इंस्टॉल करने के लिए:\\n\\n• Android फोन: Chrome के ऊपर दायें कोने में 3 बिंदू (⋮) दबाएं और 'Install app' या 'Add to Home screen' चुनें।\\n• iPhone: Safari के नीचे 'Share' (📤) दबाएं और 'Add to Home Screen' चुनें।");
                    }
                }
                </script>
                """, height=70)

                # Tabs for Platform-wise Easy Guide
                tb_android, tb_ios, tb_features, tb_apk = st.tabs([
                    "🤖 एंड्रॉइड फोन (Android)",
                    "🍎 आईफोन (iPhone / iOS)",
                    "⚡ मोबाइल डेटा व नेटवर्क लाभ",
                    "📦 स्टैंडअलोन APK पैकेजिंग"
                ])

                with tb_android:
                    st.markdown("""
                    <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:16px; line-height:1.7;">
                        <b style="color:#15803D; font-size:16px;">🤖 Android फोन (Samsung, Realme, Redmi, Vivo, Oppo, OnePlus) पर 10 सेकंड में इंस्टॉल करें:</b>
                        <ol style="margin-top:10px; padding-left:20px; font-size:14px; color:#1E293B;">
                            <li>अपने फोन के <b>Google Chrome</b> या <b>Samsung Internet</b> ब्राउज़र में इस लिंक को खोलें।</li>
                            <li>स्क्रीन के ऊपर दायें कोने में स्थित <b>तीन बिंदू (⋮)</b> पर टैप करें।</li>
                            <li>मेन्यू में <b>'Install app (ऐप इंस्टॉल करें)'</b> या <b>'Add to Home screen (होम स्क्रीन पर जोड़ें)'</b> पर टैप करें।</li>
                            <li>पुष्टि के लिए <b>'Install'</b> पर क्लिक करें।</li>
                            <li>🎉 अब आपके फोन की होम स्क्रीन पर <b>ब्रह्महोरा (BrahmaHora)</b> का असली ऐप आइकन बन जाएगा। अब इसे WhatsApp या YouTube की तरह बिना ब्राउज़र एड्रेस बार के फुल-स्क्रीन इस्तेमाल करें!</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)

                with tb_ios:
                    st.markdown("""
                    <div style="background:#F8FAFC; border:1.5px solid #0284C7; border-radius:10px; padding:16px; line-height:1.7;">
                        <b style="color:#0369A1; font-size:16px;">🍎 Apple iPhone एवं iPad पर इंस्टॉल करने की विधि:</b>
                        <ol style="margin-top:10px; padding-left:20px; font-size:14px; color:#1E293B;">
                            <li>अपने iPhone के <b>Safari Browser</b> में यह लिंक खोलें।</li>
                            <li>स्क्रीन के सबसे नीचे बीच में स्थित <b>Share (📤 चौकोर बॉक्स में ऊपर तीर)</b> बटन दबाएं।</li>
                            <li>मेन्यू को थोड़ा नीचे स्क्रॉल करें और <b>'Add to Home Screen' (+ होम स्क्रीन में जोड़ें)</b> पर टैप करें।</li>
                            <li>ऊपर दायें कोने में <b>'Add (जोड़ें)'</b> पर क्लिक करें।</li>
                            <li>🎉 आपके iPhone की होम स्क्रीन पर ब्रह्महोरा ऐप का आइकन आ जाएगा और यह एकदम असली iOS ऐप की तरह खुलेगा!</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)

                with tb_features:
                    col_mf1, col_mf2 = st.columns(2)
                    with col_mf1:
                        st.markdown("""
                        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:12px; margin-bottom:10px;">
                            <b style="color:#1D4ED8; font-size:14px;">🌐 सभी नेटवर्क पर सुपर-फ़ास्ट (2G/3G/4G/5G/Wi-Fi)</b><br/>
                            <span style="font-size:12.5px; color:#334155;">
                                इसमें स्मार्ट डेटा कंप्रेशन और PWA सर्विस वर्कर कैशे सक्रिय है, जिससे 2G या धीमे इंटरनेट पर भी कुण्डली बिना अटके तेजी से खुलती है और कम से कम मोबाइल डेटा खर्च होता है।
                            </span>
                        </div>
                        <div style="background:#FAF5FF; border:1px solid #E9D5FF; border-radius:8px; padding:12px;">
                            <b style="color:#7C3AED; font-size:14px;">🛰️ मोबाइल GPS से सटीक अक्षांश-देशांतर</b><br/>
                            <span style="font-size:12.5px; color:#334155;">
                                जातक का जन्म स्थान या प्रश्न कुण्डली बनाते समय फोन के इनबिल्ट GPS चिपसेट से 1-क्लिक में सटीक Latitude/Longitude प्राप्त हो जाते हैं।
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_mf2:
                        st.markdown("""
                        <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:12px; margin-bottom:10px;">
                            <b style="color:#B45309; font-size:14px;">📴 सर्विस वर्कर ऑफलाइन सुरक्षा</b><br/>
                            <span style="font-size:12.5px; color:#334155;">
                                सफर के दौरान यदि नेटवर्क चला जाए, तब भी आपकी खुली हुई कुण्डली, ग्रह स्थितियां और षोडशवर्ग चार्ट्स स्क्रीन पर सुरक्षित रहते हैं।
                            </span>
                        </div>
                        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:12px;">
                            <b style="color:#15803D; font-size:14px;">📲 1-क्लिक व्हाट्सएप व डिजिटल शेयरिंग</b><br/>
                            <span style="font-size:12.5px; color:#334155;">
                                कुण्डली का 22-अध्यायीय PDF अथवा सुरक्षित डिजिटल लिंक सीधे जातक के व्हाट्सएप नंबर पर 1-क्लिक में मोबाइल से भेजा जा सकता है।
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                with tb_apk:
                    st.markdown("""
                    <div style="background:#FFF7ED; border:1.5px solid #F97316; border-radius:10px; padding:16px; line-height:1.7;">
                        <b style="color:#C2410C; font-size:15px;">📦 गूगल प्ले स्टोर हेतु स्टैंडअलोन APK / AAB पैकेजिंग:</b><br/>
                        <span style="font-size:13.5px; color:#431407;">
                            चूंकि हमारी ऐप में <code>manifest.json</code> और <code>sw.js</code> पूर्णतः सक्रिय हैं, आप <b>PWABuilder (Google / Microsoft समर्थित)</b> का उपयोग करके केवल १ मिनट में स्टैंडअलोन <b>Android APK फ़ाइल</b> और <b>Google Play Store AAB बंडल</b> बना सकते हैं:
                        </span>
                        <div style="margin-top:12px;">
                            <a href="https://www.pwabuilder.com" target="_blank" style="text-decoration:none;">
                                <div style="display:inline-block; background:#EA580C; color:#FFFFFF; font-weight:800; font-size:13.5px; padding:8px 18px; border-radius:8px;">
                                    🚀 PWABuilder पर APK जनरेट करें (Open PWABuilder)
                                </div>
                            </a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("❌ बंद करें (Close)", use_container_width=True, key="btn_close_mobile_app_modal"):
                    st.session_state.gla_active_tool = None
                    st.rerun()

    # ---------------------------------------------------------
    # 🎨 THEME STYLING TOKENS FOR SIDEBAR & HEADER BREADCRUMB (Grahalakshanam Palette)
    # ---------------------------------------------------------
    _sb_card_bg = "#0A1628" if is_astrallis_mode else ("#111827" if is_night_mode else "#FFFFFF")
    _sb_card_border = "#00E5FF" if is_astrallis_mode else ("#4B5563" if is_night_mode else "#CBD5E1")
    _breadcrumb_bg = "#0A1628" if is_astrallis_mode else ("#111827" if is_night_mode else "#F2F4F7")
    _breadcrumb_border = "#00E5FF" if is_astrallis_mode else ("#4B5563" if is_night_mode else "#00B0F0")
    _breadcrumb_title_color = "#00E5FF" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#0073CF")
    _breadcrumb_text_color = "#CBD5E1" if is_astrallis_mode else ("#D1D5DB" if is_night_mode else "#1E293B")

    # ---------------------------------------------------------
    # 📚 LEFT SIDEBAR: ACTIVE CLIENT PROFILE & ALL 30 VEDIC MODULES
    # ---------------------------------------------------------
    with st.sidebar:
        # 1. 👤 सक्रिय जातक प्रोफाइल कार्ड (Active Jatak Profile Card - Light Greenish-Yellow)
        _rashi_hi_map = {
            "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
            "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
            "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
        }
        _lagna_en = getattr(chart, "lagna_sign_name", "Libra")
        _lagna_hi = _rashi_hi_map.get(_lagna_en, _lagna_en)
        _moon_planet = chart.planets.get("Moon") if hasattr(chart, "planets") else None
        _moon_en = getattr(_moon_planet, "sign_name", "Gemini") if _moon_planet else "Gemini"
        _moon_hi = _rashi_hi_map.get(_moon_en, _moon_en)

        st.markdown(f"""
        <div class="sb-card-white" style="border:1.5px solid #BDDE85; border-top:4px solid #76B828; border-radius:14px; padding:12px 14px; margin-top:6px; margin-bottom:18px; box-shadow:0 4px 12px rgba(110,160,40,0.12);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div style="font-size:11.5px; font-weight:800; color:#000000 !important; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:4px;">
                    <span>👤</span> <span style="color:#000000 !important;">सक्रिय जातक प्रोफाइल</span>
                </div>
                <span style="font-size:9.5px; font-weight:800; background:#E2F5C2; color:#000000 !important; border:1px solid #B8E088; border-radius:4px; padding:2px 7px;">● जातक</span>
            </div>
            <div style="font-size:16px; font-weight:900; color:#000000 !important; margin:3px 0 6px 0; letter-spacing:0.2px;">{name}</div>
            <div style="font-size:11.5px; color:#000000 !important; line-height:1.6;">
                📅 <b style="color:#000000 !important;">{birth_d.strftime('%d-%b-%Y')}</b> &nbsp;|&nbsp; ⏰ <b style="color:#000000 !important;">{birth_t.strftime('%I:%M %p')}</b><br/>
                📍 <span style="color:#000000 !important;">{default_city_name}</span> &nbsp;|&nbsp; <b style="color:#000000 !important;">लग्न:</b> <span style="font-weight:800; color:#000000 !important;">{_lagna_en} ({_lagna_hi})</span><br/>
                🌙 <b style="color:#000000 !important;">चन्द्र राशि:</b> <span style="font-weight:800; color:#000000 !important;">{_moon_en} ({_moon_hi})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. ⚡ सक्रिय जातक का पंचांग कार्ड (Jatak Birth Panchang Card - Light Greenish-Yellow)
        p_sb = getattr(chart, "panchang", None)
        _tithi_str = getattr(p_sb, "tithi_name", "N/A") if p_sb else "N/A"
        _vara_str = getattr(p_sb, "vara_name", "N/A") if p_sb else "N/A"
        _nak_str = getattr(p_sb, "nakshatra_name", "N/A") if p_sb else "N/A"
        _yoga_str = getattr(p_sb, "yoga_name", "N/A") if p_sb else "N/A"
        _karana_str = getattr(p_sb, "karana_name", "N/A") if p_sb else "N/A"

        _sr_str = "05:48 AM"
        _ss_str = "06:34 PM"

        # Accurate Janma Ghati calculation (2.5 ghatis per hour from sunrise ~05:48 AM)
        _sr_hour = 5.8
        _birth_hour = birth_t.hour + birth_t.minute / 60.0 + birth_t.second / 3600.0
        _diff_hour = (_birth_hour - _sr_hour) % 24
        _ghati_val = round(_diff_hour * 2.5, 2)
        _ghati_str = f"{_ghati_val} घटी"

        # Vedic Hora Lord calculation:
        _hora_order = ["सूर्य", "शुक्र", "बुध", "चन्द्र", "शनि", "गुरु", "मंगल"]
        _day_start = {6: 0, 0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4}
        _s_idx = _day_start.get(birth_d.weekday(), 0)
        _h_offset = int(_diff_hour) % 7
        _hora_str = _hora_order[(_s_idx + _h_offset) % 7]

        # Shastriya Daily Muhurta Calculations for Jatak birth date
        try:
            _muh_calc = default_shastriya_pramana_engine.calculate_daily_muhurta_windows(birth_d)
            _rahu_str = f"{_muh_calc['rahu_kaal']['start']} ~ {_muh_calc['rahu_kaal']['end']}"
            _abhijit_str = f"{_muh_calc['abhijit']['start']} ~ {_muh_calc['abhijit']['end']}"
            _gulika_str = f"{_muh_calc['gulika_kaal']['start']} ~ {_muh_calc['gulika_kaal']['end']}"
            _yama_str = f"{_muh_calc['yamaghanta']['start']} ~ {_muh_calc['yamaghanta']['end']}"
            _brahma_str = f"{_muh_calc['brahma_muhurta']['start']} ~ {_muh_calc['brahma_muhurta']['end']}"
            _sr_str = _muh_calc.get("sunrise", "05:48 AM")
            _ss_str = _muh_calc.get("sunset", "06:34 PM")
        except Exception:
            _rahu_str = "04:30 PM ~ 06:00 PM"
            _abhijit_str = "11:45 AM ~ 12:35 PM"
            _gulika_str = "03:00 PM ~ 04:30 PM"
            _yama_str = "12:00 PM ~ 01:30 PM"
            _brahma_str = "04:24 AM ~ 05:12 AM"

        st.markdown(f"""
        <div class="sb-card-white" style="border:1.5px solid #BDDE85; border-top:4px solid #D97706; border-radius:14px; padding:12px 14px; margin-top:16px; margin-bottom:18px; box-shadow:0 4px 12px rgba(110,160,40,0.12);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="font-size:11.5px; font-weight:800; color:#000000 !important; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:4px;">
                    <span>⚡</span> <span style="color:#000000 !important;">जातक जन्म पंचांग एवं मुहूर्त</span>
                </div>
                <span style="font-size:9.5px; font-weight:800; background:#E2F5C2; color:#000000 !important; border:1px solid #B8E088; border-radius:4px; padding:2px 7px;">● जन्मकालीन</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 11px;">
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">📅 जन्म तिथि</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_tithi_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🪐 जन्म वार</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_vara_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">✨ जन्म नक्षत्र</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_nak_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🌿 जन्म योग</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_yoga_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">⚡ जन्म करण</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_karana_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">👑 जन्म होरा</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_hora_str}</b>
                </div>
                <div style="background:#E2F5C2; border:1.5px solid #76B828; border-radius:7px; padding:5px 7px; grid-column: span 2;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🌟 अभिजित मुहूर्त (विजय काल)</span>
                    <b style="color:#000000 !important; font-size:11.5px; font-weight:900;">{_abhijit_str}</b>
                </div>
                <div style="background:#FFE6E6; border:1.5px solid #E57373; border-radius:7px; padding:5px 7px; grid-column: span 2;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🔴 राहुकाल (सर्वथा वर्जित)</span>
                    <b style="color:#000000 !important; font-size:11.5px; font-weight:900;">{_rahu_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🔱 गुलिक काल</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_gulika_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">⏳ यमघण्ट काल</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_yama_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🌅 सूर्योदय / सूर्यास्त</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_sr_str} / {_ss_str}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">⏱ जन्म घटी</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_ghati_str}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. 🪐 आज का पंचांग लाइव कार्ड (Today's Live Panchang Card - High Contrast White with Emerald Accent)
        _now_dt = datetime.now()
        try:
            _today_lat = float(st.session_state.get("birth_lat", 28.6139))
            _today_lon = float(st.session_state.get("birth_lon", 77.2090))
            _today_tz = float(st.session_state.get("birth_tz", 5.5))
            _today_city = str(st.session_state.get("birth_city", "New Delhi"))
            
            _today_bdata = BirthData(
                name="आज का पंचांग",
                birth_date=_now_dt.date(),
                birth_time=_now_dt.time(),
                latitude=_today_lat,
                longitude=_today_lon,
                timezone_offset=_today_tz,
                city=_today_city
            )
            _today_chart = default_chart_calculator.calculate_chart(_today_bdata)
            _tp = getattr(_today_chart, "panchang", None)
            _t_tithi = getattr(_tp, "tithi_name", "N/A") if _tp else "N/A"
            _t_vara = getattr(_tp, "vara_name", "N/A") if _tp else "N/A"
            _t_nak = getattr(_tp, "nakshatra_name", "N/A") if _tp else "N/A"
            _t_yoga = getattr(_tp, "yoga_name", "N/A") if _tp else "N/A"
            _t_karana = getattr(_tp, "karana_name", "N/A") if _tp else "N/A"
            
            _today_muh = default_shastriya_pramana_engine.calculate_daily_muhurta_windows(_now_dt.date())
            _t_rahu = f"{_today_muh['rahu_kaal']['start']} ~ {_today_muh['rahu_kaal']['end']}"
            _t_abhijit = f"{_today_muh['abhijit']['start']} ~ {_today_muh['abhijit']['end']}"
            _t_gulika = f"{_today_muh['gulika_kaal']['start']} ~ {_today_muh['gulika_kaal']['end']}"
            _t_yama = f"{_today_muh['yamaghanta']['start']} ~ {_today_muh['yamaghanta']['end']}"
            _t_brahma = f"{_today_muh['brahma_muhurta']['start']} ~ {_today_muh['brahma_muhurta']['end']}"
            _t_sunrise = _today_muh.get("sunrise", "06:15 AM")
            _t_sunset = _today_muh.get("sunset", "06:00 PM")
        except Exception:
            _t_tithi, _t_vara, _t_nak, _t_yoga, _t_karana = "कृष्ण पक्ष षष्ठी", "शनिवार", "पुनर्वसु", "सिद्ध", "वणिज"
            _t_rahu = "09:00 AM ~ 10:30 AM"
            _t_abhijit = "11:36 AM ~ 12:24 PM"
            _t_gulika = "06:00 AM ~ 07:30 AM"
            _t_yama = "01:30 PM ~ 03:00 PM"
            _t_brahma = "04:24 AM ~ 05:12 AM"
            _t_sunrise = "06:30 AM"
            _t_sunset = "05:40 PM"
            _today_city = "New Delhi"

        # Current live Hora calculation:
        _t_curr_hour = _now_dt.hour + _now_dt.minute / 60.0
        _t_diff_hour = (_t_curr_hour - 6.0) % 24
        _t_s_idx = _day_start.get(_now_dt.weekday(), 0)
        _h_live_offset = int(_t_diff_hour) % 7
        _t_hora = _hora_order[(_t_s_idx + _h_live_offset) % 7]

        st.markdown(f"""
        <div class="sb-card-white" style="border:1.5px solid #BDDE85; border-top:4px solid #10B981; border-radius:14px; padding:12px 14px; margin-top:16px; margin-bottom:18px; box-shadow:0 4px 12px rgba(110,160,40,0.12);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div style="font-size:11.5px; font-weight:800; color:#000000 !important; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:4px;">
                    <span>🪐</span> <span style="color:#000000 !important;">आज का पंचांग (Live Gochar)</span>
                </div>
                <span style="font-size:9.5px; font-weight:800; background:#E2F5C2; color:#000000 !important; border:1px solid #B8E088; border-radius:4px; padding:2px 7px;">● लाइव आज</span>
            </div>
            <div style="font-size:11.5px; color:#000000 !important; line-height:1.5; margin-bottom:8px;">
                📅 <b style="color:#000000 !important;">{_now_dt.strftime('%d-%b-%Y')} ({_t_vara})</b> &nbsp;|&nbsp; ⏰ <b style="color:#000000 !important;">{_now_dt.strftime('%I:%M %p')}</b><br/>
                📍 <span style="color:#000000 !important;">{_today_city}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 11px;">
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">📅 आज की तिथि</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_t_tithi}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🪐 आज का वार</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_t_vara}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">✨ आज का नक्षत्र</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_t_nak}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🌿 आज का योग</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_t_yoga}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">⚡ आज का करण</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_t_karana}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">👑 वर्तमान होरा</span>
                    <b style="color:#000000 !important; font-size:11px; font-weight:800; word-break:break-word;">{_t_hora} स्वामी</b>
                </div>
                <div style="background:#E2F5C2; border:1.5px solid #76B828; border-radius:7px; padding:5px 7px; grid-column: span 2;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🌟 आज का अभिजित मुहूर्त (विजय काल)</span>
                    <b style="color:#000000 !important; font-size:11.5px; font-weight:900;">{_t_abhijit}</b>
                </div>
                <div style="background:#FFE6E6; border:1.5px solid #E57373; border-radius:7px; padding:5px 7px; grid-column: span 2;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🔴 आज का राहुकाल (सर्वथा वर्जित)</span>
                    <b style="color:#000000 !important; font-size:11.5px; font-weight:900;">{_t_rahu}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🔱 आज का गुलिक</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_t_gulika}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">⏳ आज का यमघण्ट</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_t_yama}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🌅 सूर्योदय / 🌇 सूर्यास्त</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_t_sunrise} / {_t_sunset}</b>
                </div>
                <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:7px; padding:5px 7px;">
                    <span style="color:#000000 !important; font-size:9.5px; font-weight:800; display:block;">🧘 ब्रह्म मुहूर्त</span>
                    <b style="color:#000000 !important; font-size:10.5px; font-weight:800;">{_t_brahma}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 5. 📜 शास्त्रीय प्रमाण एवं फलादेश (दोनों पंचांग: जातक पंचांग व आज का पंचांग)
        st.markdown(f"""
        <div class="sb-card-white" style="border:1.5px solid #BDDE85; border-top:4px solid #D97706; border-radius:14px; padding:12px 14px; margin-top:16px; margin-bottom:20px; box-shadow:0 4px 12px rgba(110,160,40,0.12);">
            <div style="font-size:11.5px; font-weight:900; color:#000000 !important; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:5px; margin-bottom:8px;">
                <span>📜</span> <span style="color:#000000 !important;">शास्त्रीय प्रमाण एवं फलादेश</span>
            </div>
            <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:8px; padding:8px 10px; margin-bottom:8px;">
                <div style="font-size:9.5px; font-weight:800; color:#000000 !important; text-transform:uppercase; margin-bottom:3px;">🏛️ पंचाङ्ग फल श्लोक (मुहूर्त चिंतामणि):</div>
                <div style="font-size:10.5px; font-weight:800; color:#000000 !important; line-height:1.5; margin-bottom:4px;">
                    तिथेश्च श्रियमाप्नोति वारादायुष्यवर्धनम्।<br/>
                    नक्षत्राद्धरते पापं योगाद्रोगनिवारणम्॥<br/>
                    करणात् कार्यसिद्धिः स्यात् पञ्चाङ्गस्य फलं शृणु॥
                </div>
                <div style="font-size:9.5px; color:#000000 !important; line-height:1.35;">
                    <b style="color:#000000 !important;">भावार्थ:</b> <span style="color:#000000 !important;">तिथि = लक्ष्मी, वार = दीर्घायु, नक्षत्र = पापनाश, योग = रोगमुक्ति, करण = कार्यसिद्धि।</span>
                </div>
            </div>
            <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:8px; padding:8px 10px; margin-bottom:6px;">
                <div style="font-size:10px; font-weight:800; color:#000000 !important; margin-bottom:5px;">👶 जातक जन्म पंचांग फलादेश:</div>
                <div style="font-size:10px; color:#000000 !important; line-height:1.5;">
                    <div style="margin-bottom:4px;"><b style="color:#000000 !important;">📅 तिथि ({_tithi_str}):</b> <span style="color:#000000 !important;">कुशाग्र बुद्धि, पराक्रम व समाज में सम्मान।</span></div>
                    <div style="margin-bottom:4px;"><b style="color:#000000 !important;">🪐 वार ({_vara_str}):</b> <span style="color:#000000 !important;">गंभीरता, कार्य-दक्षता व सतत प्रयत्न से सिद्धि।</span></div>
                    <div style="margin-bottom:4px;"><b style="color:#000000 !important;">✨ नक्षत्र ({_nak_str}):</b> <span style="color:#000000 !important;">विद्यानुरागी, विचारशील व दृढ़ संकल्पी।</span></div>
                    <div style="margin-bottom:4px;"><b style="color:#000000 !important;">🌿 योग/करण ({_yoga_str}/{_karana_str}):</b> <span style="color:#000000 !important;">आरोग्यता व कार्य-सिद्धि में सहायक।</span></div>
                    <div><b style="color:#000000 !important;">👑 जन्म होरा ({_hora_str}):</b> <span style="color:#000000 !important;">आत्मबल व निर्णय क्षमता का संबल।</span></div>
                </div>
            </div>
            <div style="background:#EDF8DB; border:1px solid #C3E69B; border-radius:8px; padding:8px 10px;">
                <div style="font-size:10px; font-weight:800; color:#000000 !important; margin-bottom:5px;">🪐 आज का गोचर फल व मुहूर्त निर्णय:</div>
                <div style="font-size:10px; color:#000000 !important; line-height:1.5;">
                    <div style="margin-bottom:4px;"><b style="color:#000000 !important;">📅 आज ({_t_vara}, {_t_tithi}):</b> <span style="color:#000000 !important;">व्यावहारिक कर्म, अध्ययन व शुभ संवाद हेतु अनुकूल।</span></div>
                    <div style="margin-bottom:4px;"><b style="color:#000000 !important;">🌟 अभिजित ({_t_abhijit}):</b> <span style="color:#000000 !important;">मुहूर्त चिंतामणि अनुसार विजय काल — नवीन कार्य हेतु सर्वोत्तम।</span></div>
                    <div style="margin-bottom:4px;"><b style="color:#000000 !important;">🔴 राहुकाल ({_t_rahu}):</b> <span style="color:#000000 !important;">कालामृत अनुसार — नया कार्य, यात्रा व अनुबंध वर्जित।</span></div>
                    <div><b style="color:#000000 !important;">👑 वर्तमान होरा ({_t_hora}):</b> <span style="color:#000000 !important;">{_t_hora} ग्रह के अनुकूल कार्य (ज्ञान, संवाद) हेतु प्रशस्त।</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 6. 📚 समस्त ३१ वैदिक मॉड्यूल सूची (All 31 Vedic Modules List)
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px; margin-bottom:6px;">
            <span style="font-size:13px; font-weight:900; color:#000000; text-transform:uppercase; letter-spacing:0.5px;">📚 समस्त {len(MODULE_OPTIONS)} वैदिक मॉड्यूल</span>
        </div>
        """, unsafe_allow_html=True)
        
        sb_query = st.text_input("🔍 मॉड्यूल खोजें (Search):", placeholder="दशा, गोचर, केपी, मिलान...", key="sb_search_filter_input").strip().lower()
        
        # All modules available directly in the sidebar
        if sb_query:
            matched_indices = [i for i in range(len(MODULE_OPTIONS)) if sb_query in MODULE_OPTIONS[i].lower()]
            cand_indices = matched_indices if matched_indices else list(range(len(MODULE_OPTIONS)))
        else:
            cand_indices = list(range(len(MODULE_OPTIONS)))
        
        filtered_mods = [MODULE_OPTIONS[i] for i in cand_indices]
        
        curr_idx = st.session_state.get("active_module_idx", 0)
        curr_mod_name = MODULE_OPTIONS[curr_idx] if (0 <= curr_idx < len(MODULE_OPTIONS)) else MODULE_OPTIONS[0]
        
        radio_idx = filtered_mods.index(curr_mod_name) if curr_mod_name in filtered_mods else 0
        
        selected_module = st.radio(
            f"वैदिक मॉड्यूल्स ({len(MODULE_OPTIONS)} मॉड्यूल)",
            filtered_mods,
            index=radio_idx,
            label_visibility="collapsed"
        )
        selected_idx = MODULE_OPTIONS.index(selected_module) if selected_module in MODULE_OPTIONS else curr_idx
        if selected_idx != curr_idx:
            st.session_state.active_module_idx = selected_idx
            st.rerun()

    # ---------------------------------------------------------
    # 3. ACTIVE MODULE BREADCRUMB INDICATOR
    # ---------------------------------------------------------


p = chart.panchang

_breadcrumb_bg = "#0A1628" if is_astrallis_mode else ("#111827" if is_night_mode else "#EFF6FF")
_breadcrumb_border = "#00E5FF" if is_astrallis_mode else ("#4B5563" if is_night_mode else "#93C5FD")
_breadcrumb_title_color = "#00E5FF" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#1E40AF")
_breadcrumb_text_color = "#CBD5E1" if is_astrallis_mode else ("#D1D5DB" if is_night_mode else "#1E293B")

# Active Module Breadcrumb Pill
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; background:{_breadcrumb_bg}; border:1.5px solid {_breadcrumb_border}; border-radius:8px; padding:6px 14px; margin-bottom:6px;">
    <div style="font-weight:800; color:{_breadcrumb_title_color}; font-size:13px;">📍 सक्रिय मॉड्यूल: <b>{selected_module}</b></div>
    <div style="font-size:12px; color:{_breadcrumb_text_color}; font-weight:700;">जातक: <b>{name}</b> ({birth_d.strftime('%d-%b-%Y')}, {birth_t.strftime('%I:%M %p')})</div>
</div>
""", unsafe_allow_html=True)



# -------------------------------------------------------------
# 🏛️ FULL-VIEWPORT RESPONSIVE WORKSTATION
# -------------------------------------------------------------
is_parashara_layout = False

# -------------------------------------------------------------
# Module Access Control & RBAC Guard for Free Jatak Tier
# -------------------------------------------------------------
cur_user_role = st.session_state.get("user_role", "jatak")
jatak_allowed_modules = [0, 1, 16, 17, 30]

if cur_user_role == "jatak" and selected_idx not in jatak_allowed_modules:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); border: 2px solid #6366F1; border-radius: 14px; padding: 26px; color: #FFFFFF; box-shadow: 0 10px 25px rgba(0,0,0,0.2); margin: 15px 0;">
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
            <span style="font-size: 32px;">🔒</span>
            <div>
                <h3 style="margin: 0; color: #F59E0B; font-size: 1.35rem; font-weight: 800;">उन्नत प्रो मॉड्यूल (Professional Astrologer Only)</h3>
                <p style="margin: 3px 0 0 0; color: #E0E7FF; font-size: 0.95rem;">
                    यह मॉड्यूल (<b>{selected_module}</b>) केवल प्रो ज्योतिषी एवं शोधकर्ताओं के लिए उपलब्ध है।
                </p>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.08); border-radius: 10px; padding: 14px; margin: 14px 0; font-size: 0.92rem; line-height: 1.6;">
            <b>✨ प्रो ज्योतिषी (Professional Astrologer) सदस्यता में क्या शामिल है:</b>
            <ul style="margin: 6px 0 0 0; padding-left: 20px;">
                <li>समस्त ३० वैदिक मॉड्यूल (विंशोत्तरी/जैमिनी/योगिनी दशाएं, अष्टकवर्ग, गोचर, वर्षफल ताजिक, केपी, भाव स्पष्ट)</li>
                <li>षोडशवर्ग चक्र (D1 से D60 षष्ट्यंश तक सूक्ष्म विवेचन)</li>
                <li>जन्म समय शोधन (BTR - Classical Epoch Rectification)</li>
                <li>असीमित जातक कुण्डली वॉल्ट एवं परामर्श नोट्स सुरक्षित करने की सुविधा</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 🎟️ परचेज कोड द्वारा तुरंत प्रो सक्रिय करें (Activate Pro Access)")
        col_up_code, col_up_btn = st.columns([2.5, 1.2])
        with col_up_code:
            user_input_code = st.text_input(
                "परचेज कोड (Enter Purchase Code):",
                placeholder="उदा: BH-PRO-XXXX-YYYY",
                key="module_guard_purchase_code"
            )
        with col_up_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 अभी सक्रिय करें (Activate)", type="primary", use_container_width=True, key="guard_activate_code_btn"):
                if not user_input_code.strip():
                    st.error("❌ कृपया अपना परचेज कोड दर्ज करें।")
                else:
                    curr_user_em = st.session_state.get("user_email", "")
                    ok, msg = default_auth_service.redeem_purchase_code(curr_user_em, user_input_code.strip())
                    if ok:
                        st.session_state.user_role = "jyotishi"
                        st.session_state.user_role_display = "🔮 ज्योतिषी (Professional Astrologer)"
                        st.session_state.user_is_paid = True
                        st.toast(msg, icon="🎉")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        col_bk1, col_bk2 = st.columns([1.5, 3])
        with col_bk1:
            if st.button("🔙 निःशुल्क जन्म कुण्डली (D1) पर जाएं", use_container_width=True, key="guard_return_to_d1_btn"):
                st.session_state.active_module_idx = 0
                st.session_state.active_tab_idx = 0
                st.rerun()
    st.stop()

# -------------------------------------------------------------
# Module Routing
# -------------------------------------------------------------
if selected_idx == 0:
    import importlib
    import src.jyotish.ui.modules.d1_varga_view as d1_varga_view_mod
    importlib.reload(d1_varga_view_mod)
    d1_varga_view_mod.render_d1_varga_view(chart=chart, birth_profile=birth_profile, tz_offset=tz_offset, default_city_name=default_city_name, render_chart_svg_fn=render_chart_svg, tabs=MODULE_TABS_REGISTRY.get(0))

elif selected_idx == 1:
    import src.jyotish.ui.modules.event_view as event_view_mod
    event_view_mod.render_event_view(chart=chart, birth_profile=birth_profile, tz_offset=tz_offset, tabs=MODULE_TABS_REGISTRY.get(1))

elif selected_idx == 2:
    import importlib
    import src.jyotish.ui.modules.remedies_view as remedies_view_mod
    importlib.reload(remedies_view_mod)
    remedies_view_mod.render_remedies_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(2))

elif selected_idx == 3:
    import importlib
    import src.jyotish.ui.modules.varga_grid_view as varga_grid_view_mod
    importlib.reload(varga_grid_view_mod)
    varga_grid_view_mod.render_varga_grid_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(3))

elif selected_idx == 4:
    import importlib
    import src.jyotish.ui.modules.vastu_view as vastu_view_mod
    importlib.reload(vastu_view_mod)
    vastu_view_mod.render_vastu_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(4))

elif selected_idx == 5:
    import importlib
    import src.jyotish.ui.modules.prashna_view as prashna_view_mod
    importlib.reload(prashna_view_mod)
    prashna_view_mod.render_prashna_view(chart=chart, tz_offset=tz_offset, latitude=latitude, longitude=longitude, default_city_name=default_city_name, render_chart_svg_fn=render_chart_svg, tabs=MODULE_TABS_REGISTRY.get(5))

elif selected_idx == 6:
    import importlib
    import src.jyotish.ui.modules.shadbala_view as shadbala_view_mod
    importlib.reload(shadbala_view_mod)
    shadbala_view_mod.render_shadbala_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(6))

elif selected_idx == 7:
    import importlib
    import src.jyotish.ui.modules.jaimini_view as jaimini_view_mod
    importlib.reload(jaimini_view_mod)
    jaimini_view_mod.render_jaimini_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(7))

elif selected_idx == 8:
    import importlib
    import src.jyotish.ui.modules.dasha_view as dasha_view_mod
    importlib.reload(dasha_view_mod)
    dasha_view_mod.render_dasha_view(chart=chart, tz_offset=tz_offset, tabs=MODULE_TABS_REGISTRY.get(8))

elif selected_idx == 9:
    import importlib
    import src.jyotish.ui.modules.transit_view as transit_view_mod
    importlib.reload(transit_view_mod)
    transit_view_mod.render_transit_view(chart=chart, ayanamsa=ayanamsa, house_system=house_system, node_type_val=node_type_val, tz_offset=tz_offset, latitude=latitude, longitude=longitude, default_city_name=default_city_name, tabs=MODULE_TABS_REGISTRY.get(9))

elif selected_idx == 10:
    import importlib
    import src.jyotish.ui.modules.kp_view as kp_view_mod
    importlib.reload(kp_view_mod)
    kp_view_mod.render_kp_view(chart=chart, tz_offset=tz_offset, default_city_name=default_city_name, tabs=MODULE_TABS_REGISTRY.get(10))

elif selected_idx == 11:
    import importlib
    import src.jyotish.ui.modules.muhurta_view as muhurta_view_mod
    importlib.reload(muhurta_view_mod)
    muhurta_view_mod.render_muhurta_view(chart=chart, tz_offset=tz_offset, default_city_name=default_city_name, tabs=MODULE_TABS_REGISTRY.get(11))

elif selected_idx == 12:
    import importlib
    import src.jyotish.ui.modules.sudarshan_chakra_view as sudarshan_view_mod
    importlib.reload(sudarshan_view_mod)
    sudarshan_view_mod.render_sudarshan_chakra_view(chart=chart, birth_profile=birth_profile, tz_offset=tz_offset, tabs=MODULE_TABS_REGISTRY.get(12))

elif selected_idx == 13:
    import importlib
    import src.jyotish.ui.modules.varshaphal_view as varshaphal_view_mod
    importlib.reload(varshaphal_view_mod)
    varshaphal_view_mod.render_varshaphal_view(chart=chart, birth_profile=birth_profile, tz_offset=tz_offset, render_chart_svg_fn=render_chart_svg, tabs=MODULE_TABS_REGISTRY.get(13))

elif selected_idx == 14:
    import importlib
    import src.jyotish.ui.modules.btr_view as btr_view_mod
    importlib.reload(btr_view_mod)
    btr_view_mod.render_btr_view(chart=chart, birth_profile=birth_profile, tabs=MODULE_TABS_REGISTRY.get(14))

elif selected_idx == 15:
    import importlib
    import src.jyotish.ui.modules.matching_view as matching_view_mod
    importlib.reload(matching_view_mod)
    matching_view_mod.render_matching_view(birth_profile=birth_profile, render_chart_svg_fn=render_chart_svg, tabs=MODULE_TABS_REGISTRY.get(15))

elif selected_idx == 16:
    import importlib
    import src.jyotish.ui.modules.daivajna_view as daivajna_view_mod
    importlib.reload(daivajna_view_mod)
    daivajna_view_mod.render_daivajna_view(chart=chart)

elif selected_idx == 17:
    import importlib
    import src.jyotish.ui.modules.reports_view as reports_view_mod
    importlib.reload(reports_view_mod)
    reports_view_mod.render_reports_view(chart=chart, birth_profile=birth_profile, tabs=MODULE_TABS_REGISTRY.get(17))

elif selected_idx == 18:
    import importlib
    import src.jyotish.ui.modules.rules_library_view as rules_view_mod
    importlib.reload(rules_view_mod)
    rules_view_mod.render_rules_library_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(18))

elif selected_idx == 19:
    import importlib
    import src.jyotish.ui.modules.validation_view as validation_view_mod
    importlib.reload(validation_view_mod)
    validation_view_mod.render_validation_view(chart=chart)

elif selected_idx == 20:
    import importlib
    import src.jyotish.ui.modules.yogas_doshas_view as yogas_view_mod
    importlib.reload(yogas_view_mod)
    yogas_view_mod.render_yogas_doshas_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(20))

elif selected_idx == 21:
    import importlib
    import src.jyotish.ui.modules.numerology_view as numerology_view_mod
    importlib.reload(numerology_view_mod)
    numerology_view_mod.render_numerology_view(birth_profile=birth_profile, tabs=MODULE_TABS_REGISTRY.get(21))

elif selected_idx == 22:
    import importlib
    import src.jyotish.ui.modules.lal_kitab_view as lal_kitab_view_mod
    importlib.reload(lal_kitab_view_mod)
    lal_kitab_view_mod.render_lal_kitab_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(22))

elif selected_idx == 23:
    import importlib
    import src.jyotish.ui.modules.ayurvedic_diet_view as diet_view_mod
    importlib.reload(diet_view_mod)
    diet_view_mod.render_ayurvedic_diet_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(23))

elif selected_idx == 24:
    import importlib
    import src.jyotish.ui.modules.relationships_view as rel_view_mod
    importlib.reload(rel_view_mod)
    rel_view_mod.render_relationships_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(24))

elif selected_idx == 25:
    import importlib
    import src.jyotish.ui.modules.health_disease_view as health_view_mod
    importlib.reload(health_view_mod)
    health_view_mod.render_health_disease_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(25))

elif selected_idx == 26:
    import importlib
    import src.jyotish.ui.modules.body_anatomy_view as body_view_mod
    importlib.reload(body_view_mod)
    body_view_mod.render_body_anatomy_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(26))

elif selected_idx == 27:
    import importlib
    import src.jyotish.ui.modules.pooja_view as pooja_view_mod
    importlib.reload(pooja_view_mod)
    pooja_view_mod.render_pooja_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(27))

elif selected_idx == 28:
    import importlib
    import src.jyotish.ui.modules.karma_view as karma_view_mod
    importlib.reload(karma_view_mod)
    karma_view_mod.render_karma_view(chart=chart, tabs=MODULE_TABS_REGISTRY.get(28))

elif selected_idx == 29:
    import importlib
    import src.jyotish.services.panchang as panchang_svc_mod
    importlib.reload(panchang_svc_mod)
    import src.jyotish.ui.panchang_view as panchang_view_mod
    importlib.reload(panchang_view_mod)

    panchang_view_mod.render_vedic_panchang_view(
        chart=chart,
        birth_profile=birth_profile,
        is_dark=st.session_state.get("dark_mode", False)
    )

elif selected_idx == 30:
    import importlib
    import src.jyotish.services.shastriya_faladesh as shastriya_svc_mod
    importlib.reload(shastriya_svc_mod)
    import src.jyotish.ui.shastriya_faladesh_view as shastriya_view_mod
    importlib.reload(shastriya_view_mod)

    shastriya_view_mod.render_shastriya_faladesh_view(
        chart=chart,
        birth_profile=birth_profile,
        is_dark=st.session_state.get("dark_mode", False),
        tz_offset=tz_offset
    )

elif selected_idx == 31:
    import importlib
    import src.jyotish.ui.modules.palmistry_view as palmistry_view_mod
    importlib.reload(palmistry_view_mod)

    palmistry_view_mod.render_palmistry_view(
        chart=chart,
        tabs=MODULE_TABS_REGISTRY.get(31)
    )

# -------------------------------------------------------------
# 🎯 GUARANTEED ACTIVE TAB SWITCHER (Post-Render DOM Execution)
# -------------------------------------------------------------
_active_tab_to_activate = int(st.session_state.get("active_tab_idx", 0))
_cur_target_tab_title = cur_mod_tabs[_active_tab_to_activate] if _active_tab_to_activate < len(cur_mod_tabs) else ""
_target_title_json = json.dumps(_cur_target_tab_title)

components.html(f"""
<script>
(function() {{
    const targetIdx = {_active_tab_to_activate};
    const targetTitle = {_target_title_json};
    let done = false;

    function activateTab() {{
        if (done) return true;
        try {{
            const pWin = (window.parent || window);
            if (pWin.switchAppTab) {{
                if (targetTitle && pWin.switchAppTab(targetTitle)) {{
                    done = true;
                    return true;
                }}
                if (pWin.switchAppTab(targetIdx)) {{
                    done = true;
                    return true;
                }}
            }}

            const pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            if (!pDoc) return false;
            const mainSec = pDoc.querySelector('[data-testid="stMain"], section.main') || pDoc;
            const allTabs = Array.from(mainSec.querySelectorAll('.stTabs [role="tab"], [data-baseweb="tab-list"] button[role="tab"]'))
                .filter(b => !b.closest('[role="dialog"]') && !b.closest('[data-testid="stModal"]') && !b.closest('.st-key-frozen_toolbelt_container'));
            if (!allTabs || allTabs.length === 0) return false;

            let targetBtn = null;
            if (targetTitle) {{
                targetBtn = allTabs.find(b => {{
                    const txt = (b.textContent || "").trim();
                    return txt === targetTitle || txt.includes(targetTitle) || targetTitle.includes(txt);
                }});
            }}
            if (!targetBtn && targetIdx >= 0 && targetIdx < allTabs.length) {{
                targetBtn = allTabs[targetIdx];
            }}

            if (targetBtn) {{
                if (targetBtn.getAttribute('aria-selected') === 'true') {{
                    done = true;
                    return true;
                }}
                targetBtn.focus();
                targetBtn.click();
                done = true;
                return true;
            }}
        }} catch(e) {{}}
        return false;
    }}

    // Try immediately, and retry if tabs are still hydrating
    if (!activateTab()) {{
        let count = 0;
        const timer = setInterval(function() {{
            count++;
            if (activateTab() || count >= 15) {{
                clearInterval(timer);
            }}
        }}, 80);
    }}
}})();
</script>
""", height=0, width=0)

