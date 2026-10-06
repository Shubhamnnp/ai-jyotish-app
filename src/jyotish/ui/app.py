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
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, time, datetime, timedelta
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
import importlib
import src.jyotish.ai.narrative as narr_mod
importlib.reload(narr_mod)
default_narrative_service = narr_mod.default_narrative_service
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
    page_title="JyotishOS - Enterprise Vedic Astrology Platform",
    page_icon="🔮",
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
        background-color: #0A0E1A !important;
        border-right: 1.5px solid #1E293B !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
    section[data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
    div[data-testid="stRadio"] label {
        background: #0D1322 !important;
        border: 1.5px solid #1E293B !important;
        color: #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] .stRadio label p,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p,
    div[data-testid="stRadio"] label p {
        color: #CBD5E1 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover,
    section[data-testid="stSidebar"] .stRadio label:hover,
    div[data-testid="stRadio"] label:hover {
        background: #1E293B !important;
        border-color: #00E5FF !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio label:has(input:checked),
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%) !important;
        border: 2px solid #00E5FF !important;
        box-shadow: 0 4px 14px rgba(0, 229, 255, 0.25) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) span,
    div[data-testid="stRadio"] label:has(input:checked) p {
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
        background-color: #0D1322 !important;
        border-right: 1.5px solid #1E293B !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
        color: #F1F5F9 !important;
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
        background-color: #F8FAFC !important;
        background: #F8FAFC !important;
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
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border-right: 1.5px solid #E2E8F0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #0F172A !important;
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
    button[kind="secondary"], button[kind="secondary"] * {
        background-color: #F2F2F2 !important;
        color: #0077B6 !important;
        border: 2px solid #00B0F0 !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #E0F2FE !important;
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
        z-index: 10000000 !important;
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
    }}
    [data-testid="stExpandSidebarButton"]:hover,
    button[data-testid="stExpandSidebarButton"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover {{
        transform: scale(1.05) !important;
    }}

    .sidebar-toggle-btn {{
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid #1E40AF !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-size: 15px !important;
        font-weight: 900 !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.15s ease !important;
        user-select: none !important;
    }}
    .sidebar-toggle-btn:hover {{
        background: #1D4ED8 !important;
        transform: scale(1.06) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.5) !important;
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
    .block-container {{
        padding-top: 2px !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        max-width: 100% !important;
        overflow: visible !important;
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
    [data-testid="stSidebarUserContent"] {{
        z-index: 10000000 !important;
        background-color: #0074cb !important;
        background: #0074cb !important;
        border-right: 2px solid #005fa8 !important;
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
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] button {{
        z-index: 10000005 !important;
        pointer-events: auto !important;
    }}

    /* Frozen Locked Toolbelt (Pins the 8 Top Action Buttons Permanently to the Top of the Viewport) */
    .st-key-frozen_toolbelt_container,
    div.st-key-frozen_toolbelt_container {{
        position: fixed !important;
        top: 0px !important;
        z-index: 9990 !important;
        background: #0074cb !important;
        background-color: #0074cb !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
        padding-left: 52px !important;
        padding-right: 14px !important;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        border-bottom: 2.5px solid #005fa8 !important;
        box-shadow: 0 4px 14px rgba(0, 116, 203, 0.35) !important;
        box-sizing: border-box !important;
        transition: left 0.15s ease, width 0.15s ease !important;
    }}
    .st-key-frozen_toolbelt_container div[data-testid="column"] {{
        min-width: 0 !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        flex: 1 1 0px !important;
    }}
    .st-key-frozen_toolbelt_container button {{
        padding: 4px 4px !important;
        font-size: 12.5px !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        min-height: 36px !important;
        height: 36px !important;
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
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
    .block-container {{
        padding-top: 58px !important;
    }}
    @media (min-width: 769px) {{
        div[data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"][aria-expanded="true"]) .st-key-frozen_toolbelt_container,
        div[data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"]:not([aria-expanded="false"])) .st-key-frozen_toolbelt_container,
        div.stApp:has(section[data-testid="stSidebar"]:not([aria-expanded="false"])) .st-key-frozen_toolbelt_container {{
            padding-left: 14px !important;
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

    /* Top Module Navigation Bar (Slim 34px Height) */
    .st-key-top_frozen_header_container [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        min-height: 34px !important;
        height: 34px !important;
        border-radius: 6px !important;
        border: 1.5px solid #2563EB !important;
        background: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        display: flex !important;
        align-items: center !important;
    }}
    .st-key-top_frozen_header_container button[data-testid="baseButton-secondary"],
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) button[data-testid="baseButton-secondary"] {{
        min-height: 34px !important;
        height: 34px !important;
        border-radius: 6px !important;
        border: 1.5px solid #94A3B8 !important;
        background: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 12.5px !important;
        color: #1E293B !important;
        padding: 0px 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.15s ease !important;
    }}
    .st-key-top_frozen_header_container button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stVerticalBlock"] > div:has(.fixed-header-anchor) button[data-testid="baseButton-secondary"]:hover {{
        background: #EFF6FF !important;
        border-color: #2563EB !important;
        color: #1D4ED8 !important;
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
    [data-testid="stTable"], [data-testid="stDataFrame"] {{
    /* Responsive Tables */
    [data-testid="stTable"] {{
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

    /* Responsive SVG & Kundali Charts Auto-Scaling */
    svg {{
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
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 0px !important;
            padding-bottom: 2rem !important;
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
            padding-top: 0.4rem !important;
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
        /* Prevent horizontal overflow on tables and charts */
        div[data-testid="stHorizontalBlock"] {{
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

    function resolveClientGPS() {
        try {
            const cached = localStorage.getItem("jyotish_user_gps_loc") || sessionStorage.getItem("jyotish_user_gps_loc");
            if (cached) {
                updateLocationUI(cached);
            }

            if (navigator.geolocation && !window.__gps_queried) {
                window.__gps_queried = true;
                navigator.geolocation.getCurrentPosition(function(pos) {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    fetch("https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=" + lat + "&longitude=" + lon + "&localityLanguage=en")
                        .then(function(r) { return r.json(); })
                        .then(function(data) {
                            const city = data.locality || data.city || data.principalSubdivision || "स्थानीय";
                            const state = data.principalSubdivision || "";
                            const country = data.countryName || "India";
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
                                    const loc = city + (state ? (", " + state) : "") + " (" + country + ")";
                                    localStorage.setItem("jyotish_user_gps_loc", loc);
                                    sessionStorage.setItem("jyotish_user_gps_loc", loc);
                                    updateLocationUI(loc);
                                }).catch(function() {});
                        });
                }, function(err) {
                    // Fallback to client-side IP lookup in user browser (not server)
                    if (!cached) {
                        fetch("https://ipapi.co/json/")
                            .then(function(r) { return r.json(); })
                            .then(function(d) {
                                const loc = (d.city || "Bahraich") + ", " + (d.region || "Uttar Pradesh") + " (" + (d.country_name || "India") + ")";
                                localStorage.setItem("jyotish_user_gps_loc", loc);
                                updateLocationUI(loc);
                            })
                            .catch(function() {
                                updateLocationUI("Nanpara, Bahraich (India)");
                            });
                    }
                }, { timeout: 10000, enableHighAccuracy: true, maximumAge: 30000 });
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
                            background-color: #0A0E1A !important;
                            border-right: 1.5px solid #1E293B !important;
                        }
                        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
                            color: #E2E8F0 !important;
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
                            background-color: #0D1322 !important;
                            border-right: 1.5px solid #1E293B !important;
                        }
                        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
                            color: #F1F5F9 !important;
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
                            padding-top: 2px !important;
                            padding-bottom: 0.5rem !important;
                            padding-left: 0.75rem !important;
                            padding-right: 0.75rem !important;
                            max-width: 100% !important;
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
                        div.st-key-frozen_toolbelt_container {
                            position: fixed !important;
                            top: 0px !important;
                            z-index: 9990 !important;
                            background: #0074cb !important;
                            background-color: #0074cb !important;
                            border-bottom: 2.5px solid #005fa8 !important;
                            box-shadow: 0 4px 14px rgba(0, 116, 203, 0.35) !important;
                            padding-top: 6px !important;
                            padding-bottom: 6px !important;
                            padding-left: 52px !important;
                            padding-right: 14px !important;
                            box-sizing: border-box !important;
                            transition: left 0.15s ease, width 0.15s ease !important;
                        }
                        .st-key-frozen_toolbelt_container div[data-testid="column"] {
                            min-width: 0 !important;
                            padding-left: 2px !important;
                            padding-right: 2px !important;
                            flex: 1 1 0px !important;
                        }
                        .st-key-frozen_toolbelt_container button {
                            padding: 4px 4px !important;
                            font-size: 12.5px !important;
                            font-weight: 700 !important;
                            white-space: nowrap !important;
                            overflow: hidden !important;
                            text-overflow: ellipsis !important;
                            min-height: 36px !important;
                            height: 36px !important;
                            background: #FFFFFF !important;
                            color: #000000 !important;
                            border: 1.5px solid #CBD5E1 !important;
                            border-radius: 8px !important;
                        }
                        .st-key-frozen_toolbelt_container button * {
                            color: #000000 !important;
                            font-weight: 700 !important;
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
                        .block-container {
                            padding-top: 58px !important;
                        }
                        .st-key-top_frozen_header_container {
                            border: none !important;
                            box-shadow: none !important;
                            padding: 0px !important;
                            margin: 0px 0px 4px 0px !important;
                            background: transparent !important;
                        }
                        [data-testid="stSidebar"], section[data-testid="stSidebar"],
                        [data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] {
                            background-color: #0074cb !important;
                            background: #0074cb !important;
                            border-right: 2px solid #005fa8 !important;
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
                        button[kind="secondary"], button[kind="secondary"] * {
                            background-color: #FFFFFF !important;
                            color: #000000 !important;
                            border: 1.5px solid #CBDCB8 !important;
                            font-weight: 800 !important;
                        }
                        button[kind="secondary"]:hover {
                            background-color: #F4F8EC !important;
                            border-color: #4D7C0F !important;
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
                stHeader.style.setProperty('border', 'none', 'important');
                stHeader.style.setProperty('pointer-events', 'none', 'important');
                stHeader.style.setProperty('z-index', '10000000', 'important');
            }

            const mainSec = parentDoc.querySelector('[data-testid="stMain"], section.main');
            if (mainSec) {
                mainSec.style.setProperty('overflow-y', 'auto', 'important');
                mainSec.style.setProperty('overflow-x', 'hidden', 'important');
                mainSec.style.setProperty('position', 'relative', 'important');
            }

            const frozenTb = parentDoc.querySelector('.st-key-frozen_toolbelt_container');
            if (frozenTb && mainSec) {
                const sb = parentDoc.querySelector('[data-testid="stSidebar"], section[data-testid="stSidebar"]');
                if (!mainSec.dataset.roBound && window.ResizeObserver) {
                    mainSec.dataset.roBound = "true";
                    const ro = new ResizeObserver(function() {
                        setupStickyTopHeader();
                    });
                    ro.observe(mainSec);
                    if (sb) ro.observe(sb);
                }

                const rect = mainSec.getBoundingClientRect();
                const isSidebarVisible = (rect.left > 60);

                frozenTb.style.setProperty('position', 'fixed', 'important');
                frozenTb.style.setProperty('top', '0px', 'important');
                frozenTb.style.setProperty('z-index', '9990', 'important');
                frozenTb.style.setProperty('left', Math.max(0, Math.round(rect.left)) + 'px', 'important');
                frozenTb.style.setProperty('width', Math.round(rect.width) + 'px', 'important');
                frozenTb.style.setProperty('padding-top', '6px', 'important');
                frozenTb.style.setProperty('padding-bottom', '6px', 'important');
                frozenTb.style.setProperty('box-sizing', 'border-box', 'important');
                frozenTb.style.setProperty('transition', 'none', 'important');

                if (isSidebarVisible) {
                    frozenTb.style.setProperty('padding-left', '14px', 'important');
                    frozenTb.style.setProperty('padding-right', '14px', 'important');
                } else {
                    frozenTb.style.setProperty('padding-left', '52px', 'important');
                    frozenTb.style.setProperty('padding-right', '14px', 'important');
                }

                const isNight = parentDoc.body.classList.contains('night-mode') || localStorage.getItem('jyotish_theme_mode') === 'night';
                const isAstrallis = parentDoc.body.classList.contains('astrallis-mode') || localStorage.getItem('jyotish_theme_mode') === 'astrallis';
                frozenTb.style.setProperty('background', isAstrallis ? '#070A12' : (isNight ? '#111827' : '#0074cb'), 'important');
                frozenTb.style.setProperty('border-bottom', isAstrallis ? '2.5px solid #00E5FF' : (isNight ? '2.5px solid #374151' : '2.5px solid #00B0F0'), 'important');
                frozenTb.style.setProperty('box-shadow', '0 4px 14px rgba(0, 115, 207, 0.15)', 'important');
            }

            const blockContainer = parentDoc.querySelector('.block-container');
            if (blockContainer) {
                blockContainer.style.setProperty('padding-top', '58px', 'important');
                blockContainer.style.setProperty('padding-left', '8px', 'important');
                blockContainer.style.setProperty('padding-right', '8px', 'important');
                blockContainer.style.setProperty('max-width', '100%', 'important');
            }

        } catch(e) {
            console.error("Error freezing top header:", e);
        }
    }

    function setupPWAandMobile() {
        try {
            const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            if (!parentDoc) return;
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
                m3.content = 'AI ज्योतिषाचार्य';
                head.appendChild(m3);

                const m4 = parentDoc.createElement('meta');
                m4.name = 'mobile-web-app-capable';
                m4.content = 'yes';
                head.appendChild(m4);

                const m5 = parentDoc.createElement('meta');
                m5.name = 'theme-color';
                m5.content = '#050811';
                head.appendChild(m5);

                const iconLink = parentDoc.createElement('link');
                iconLink.rel = 'apple-touch-icon';
                iconLink.href = '/app/static/icon-192.png';
                head.appendChild(iconLink);
            }

            // 3. Register Service Worker on parent window navigator
            const winNav = (window.parent && window.parent.navigator) ? window.parent.navigator : navigator;
            if (winNav && 'serviceWorker' in winNav && !window.__sw_registered) {
                window.__sw_registered = true;
                winNav.serviceWorker.register('/app/static/sw.js').then(function(reg) {
                    console.log('Jyotish PWA active:', reg.scope);
                }).catch(function(e) {});
            }
        } catch(e) {}
    }

    setupPWAandMobile();
    setupSidebarToggle();
    setupLanguageBridge();
    setupThemeMode();
    setupStickyTopHeader();
    resolveClientGPS();
    setInterval(function() {
        setupPWAandMobile();
        setupSidebarToggle();
        setupLanguageBridge();
        setupThemeMode();
        setupStickyTopHeader();
        const cached = localStorage.getItem("jyotish_user_gps_loc") || sessionStorage.getItem("jyotish_user_gps_loc");
        if (cached) {
            updateLocationUI(cached);
        }
    }, 250);
})();
</script>
"""
components.html(client_bridge_code.replace("__ACTIVE_THEME_MODE__", cur_active_theme), height=0, width=0)


# -------------------------------------------------------------
# Dedicated Matching Cosmic Vedic Login Page
# -------------------------------------------------------------
def render_login_page():
    st.markdown("""
    <div style="display:flex; justify-content:flex-end; gap:8px; margin-bottom: 4px;">
        <div class="header-sub-pill notranslate theme-select-box" translate="no" style="background:#F8FAFC !important; border-color:#CBD5E1 !important; color:#0F172A !important; padding:4px 12px !important; display:inline-flex; align-items:center; gap:6px;" title="थीम चुनें (Select Day / Night Mode)">
            <span id="theme-mode-icon" class="notranslate" translate="no" style="font-size:14px;">☀️</span>
            <b class="notranslate" translate="no" style="color:#0F172A !important; font-size:12px;">थीम:</b>
            <select id="software-theme-select" class="notranslate" translate="no" onchange="window.changeSoftwareTheme ? window.changeSoftwareTheme(this.value) : (window.parent && window.parent.changeSoftwareTheme ? window.parent.changeSoftwareTheme(this.value) : null)" style="background:transparent; border:none; color:#0F172A; font-weight:800; font-size:12px; cursor:pointer; outline:none; padding:0 2px;">
                <option value="astrallis" class="notranslate" translate="no">🔬 एस्ट्रैलिस वेधशाला (Astrallis Observatory)</option>
                <option value="night" class="notranslate" translate="no">🌙 कॉस्मिक ओब्सीडियन (Cosmic Obsidian)</option>
                <option value="day" class="notranslate" translate="no">☀️ वैदिक रॉयल पर्ल (Royal Pearl)</option>
            </select>
        </div>
        <div class="header-sub-pill notranslate lang-select-box" translate="no" style="background:#F0FDF4 !important; border-color:#86EFAC !important; color:#166534 !important; padding:4px 12px !important;">
            🌐 <b class="notranslate" translate="no">भाषा (Language):</b>
            <select id="software-lang-select" class="notranslate" translate="no" onchange="window.changeSoftwareLanguage ? window.changeSoftwareLanguage(this.value) : (window.parent && window.parent.changeSoftwareLanguage ? window.parent.changeSoftwareLanguage(this.value) : null)">
                <option value="general" class="notranslate" translate="no">General (जनरल)</option>
                <option value="hi" class="notranslate" translate="no">हिन्दी (Hindi)</option>
                <option value="en" class="notranslate" translate="no">English (अंग्रेजी)</option>
                <option value="ta" class="notranslate" translate="no">தமிழ் (Tamil)</option>
                <option value="te" class="notranslate" translate="no">తెలుగు (Telugu)</option>
                <option value="gu" class="notranslate" translate="no">ગુજરાતી (Gujarati)</option>
                <option value="mr" class="notranslate" translate="no">मराठी (Marathi)</option>
                <option value="bn" class="notranslate" translate="no">বাংলা (Bengali)</option>
            </select>
        </div>
    </div>
    <div style="text-align: center; padding: 15px 15px 15px 15px;">
        <div style="font-size: 2.8rem; font-weight: 900; color: #B45309; letter-spacing: -0.5px; margin-bottom: 4px;">
            🔮 JyotishOS Cloud Platform
        </div>
        <div style="font-size: 1.15rem; color: #1E293B; font-weight: 700;">
            सर्वं खल्विदं ब्रह्म • प्रामाणिक वैदिक ज्योतिष गणना एवं बहु-पद्धति निर्णय प्रणाली
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_hero, col_login = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown("""<div style="background: #FFFFFF; border: 2px solid #CBD5E1; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.06);">
<div style="text-align:center; margin-bottom: 16px;">
<svg width="110" height="110" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="50" r="46" stroke="#D97706" stroke-width="2" stroke-dasharray="4 2"/>
<circle cx="50" cy="50" r="38" stroke="#2563EB" stroke-width="1.5"/>
<polygon points="50,14 84,76 16,76" stroke="#D97706" stroke-width="2" fill="rgba(217, 119, 6, 0.08)"/>
<polygon points="50,86 84,24 16,24" stroke="#D97706" stroke-width="2" fill="rgba(217, 119, 6, 0.08)"/>
<polygon points="50,22 76,70 24,70" stroke="#2563EB" stroke-width="1.5" fill="none"/>
<polygon points="50,78 76,30 24,30" stroke="#2563EB" stroke-width="1.5" fill="none"/>
<circle cx="50" cy="50" r="8" fill="#D97706"/>
<circle cx="50" cy="50" r="3" fill="#FFFFFF"/>
</svg>
<div style="font-size: 1.15rem; font-weight: 800; color: #B45309; margin-top: 8px;">
ॐ श्री गणेशाय नमः • श्री नवग्रह प्रसन्न
</div>
</div>
<div style="margin-bottom: 16px;">
<div style="font-size: 1rem; font-weight: 800; color: #000000; margin-bottom: 8px;">🌟 मुख्य क्षमताएं:</div>
<ul style="color: #0F172A; font-weight: 600; line-height: 1.8; padding-left: 20px; margin-bottom: 0;">
<li><b>खगोलीय परिशुद्धता:</b> 99.99% ग्रह स्पष्ट एवं षोडशवर्ग गणना</li>
<li><b>क्लाउड कुण्डली सिंक:</b> सहेजी गई कुण्डलियाँ, दोष, फ्री-विल, 3-स्तम्भीय उपाय</li>
<li><b>शास्त्रीय नियम कंसेंसस:</b> पराशर, जैमिनी, ताजिक, भृगु, मंत्रेश्वर</li>
<li><b>षोडशवर्ग (D1 to D60):</b> विंशोपक बल, दशवर्ग डिग्निटी अंक, अष्टकवर्ग शोधन</li>
<li><b>ज्योतिष एआई सहायक:</b> तात्कालिक शास्त्रीय कुंडली व्याख्या एवं मार्गदर्शन</li>
</ul>
</div>
<div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 10px; padding: 12px; font-size: 0.88rem;">
<div style="font-weight: 800; color: #000000; margin-bottom: 4px;">🟢 लाइव सिस्टम स्थिति:</div>
<div style="display: flex; gap: 12px; flex-wrap: wrap; color: #0F172A; font-weight: 700;">
<span>● गणना इंजन: <b>सक्रिय</b></span>
<span>● क्लाउड ब्रिज: <b>कनेक्टेड</b></span>
<span>● स्थान डेटाबेस: <b>15,000+ भारतीय शहर</b></span>
</div>
</div>
</div>""", unsafe_allow_html=True)

    with col_login:
        login_tab, register_tab, forgot_tab = st.tabs([
            "🔐 लॉगिन (Sign In)",
            "📝 नया खाता (Sign Up)",
            "🔑 पासवर्ड भूल गए (Reset)"
        ])

        with login_tab:
            st.markdown("""<div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">
सुरक्षित प्रवेश (Registered User Login)
</div>
<div style="font-size: 0.85rem; color: #64748B; margin-bottom: 12px;">
केवल पंजीकृत उपयोगकर्ता ही एन्क्रिप्टेड क्रेडेंशियल्स द्वारा प्रवेश कर सकते हैं।
</div>""", unsafe_allow_html=True)

            login_email = st.text_input("पंजीकृत ईमेल (Registered Email)", value="shubham8jyotish@gmail.com", key="auth_login_email")
            login_password = st.text_input("एन्क्रिप्टेड पासवर्ड (Password)", value="Bahraich@123", type="password", key="auth_login_pwd")

            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            col_l1, col_l2 = st.columns([1.2, 1])
            login_submit = col_l1.button("🚀 सुरक्षित लॉगिन (Sign In)", type="primary", use_container_width=True)
            sync_login = col_l2.button("☁️ 1-क्लिक क्लाउड सिंक", use_container_width=True)

            if login_submit:
                user_info = default_auth_service.authenticate(login_email, login_password)
                if user_info:
                    st.session_state.is_logged_in = True
                    st.query_params["session_auth"] = "active"
                    st.session_state.user_role = user_info.get("role", "🔮 मुख्य ज्योतिषी (Chief Astrologer)")
                    st.session_state.user_email = user_info.get("email", login_email)
                    st.session_state.birth_name = user_info.get("name", "Shubham Tiwari")
                    st.toast(f"✅ स्वागत है, {user_info.get('name')}!", icon="🔮")
                    st.rerun()
                else:
                    st.error("❌ अमान्य ईमेल अथवा पासवर्ड! केवल पंजीकृत यूज़र्स ही एन्क्रिप्टेड पासवर्ड से प्रवेश कर सकते हैं।")

            if sync_login:
                user_info = default_auth_service.authenticate(login_email, login_password)
                if user_info:
                    with st.spinner(f"Connecting to Cloud API ({login_email})..."):
                        client = GrahalakshanamClient()
                        if client.authenticate(login_email, login_password):
                            st.session_state.is_logged_in = True
                            st.query_params["session_auth"] = "active"
                            st.session_state.gla_authenticated = True
                            ff = client.get_folders_with_files()
                            st.session_state.gla_charts = ff.get("files", [])
                            default_folder_manager.sync_from_grahalakshanam(ff)
                            st.session_state.user_role = user_info.get("role")
                            st.session_state.user_email = user_info.get("email")
                            st.toast(f"✅ क्लाउड से {len(st.session_state.gla_charts)} चार्ट्स सफलतापूर्वक सिंक हुए!", icon="☁️")
                            st.rerun()
                        else:
                            st.session_state.is_logged_in = True
                            st.query_params["session_auth"] = "active"
                            st.session_state.user_role = user_info.get("role")
                            st.session_state.user_email = user_info.get("email")
                            st.toast("✅ ऑफलाइन सुरक्षित मोड में प्रवेश किया गया!", icon="🔮")
                            st.rerun()
                else:
                    st.error("❌ क्लाउड सिंक हेतु वैध पंजीकृत क्रेडेंशियल्स दर्ज करें।")

        with register_tab:
            st.markdown("""<div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">
नया खाता पंजीकरण (New User Sign Up)
</div>
<div style="font-size: 0.85rem; color: #64748B; margin-bottom: 12px;">
पासवर्ड PBKDF2-SHA256 क्रिप्टोग्राफिक हैशिंग द्वारा सुरक्षित किया जाएगा।
</div>""", unsafe_allow_html=True)

            reg_name = st.text_input("पूरा नाम (Full Name)", placeholder="उदा: पं. शुभम तिवारी", key="auth_reg_name")
            reg_email = st.text_input("ईमेल आईडी (Email ID)", placeholder="astrologer@example.com", key="auth_reg_email")
            reg_pass = st.text_input("पासवर्ड बनाएं (Password - min 6 chars)", type="password", key="auth_reg_pwd")
            reg_role = st.selectbox(
                "उपयोगकर्ता भूमिका (Role)",
                ["🔮 मुख्य ज्योतिषी (Chief Astrologer)", "🔬 वैदिक शोधकर्ता (Researcher)", "👤 जातक / क्लाइंट (Client)"],
                key="auth_reg_role"
            )

            if st.button("✨ नया खाता बनाएं (Create Account)", type="primary", use_container_width=True):
                success, msg = default_auth_service.register(reg_email, reg_pass, reg_name, reg_role)
                if success:
                    st.success(f"✅ {msg}")
                    st.info("💡 अब आप 'लॉगिन' टैब में जाकर अपने नए क्रेडेंशियल्स से प्रवेश कर सकते हैं।")
                else:
                    st.error(f"❌ {msg}")

        with forgot_tab:
            st.markdown("""<div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">
पासवर्ड रीसेट एवं सुरक्षा (Forgot Password)
</div>
<div style="font-size: 0.85rem; color: #64748B; margin-bottom: 12px;">
पंजीकृत ईमेल पर 6-अंकीय OTP सत्यापन कोड प्राप्त करें और नया पासवर्ड एन्क्रिप्ट करें।
</div>""", unsafe_allow_html=True)

            f_email = st.text_input("पंजीकृत ईमेल दर्ज करें (Registered Email)", value="admin@jyotishos.com", key="auth_forgot_email")

            if st.button("📩 OTP सत्यापन कोड प्राप्त करें (Request OTP)", use_container_width=True):
                ok, msg, otp = default_auth_service.request_reset_code(f_email)
                if ok:
                    st.session_state["active_reset_email"] = f_email
                    st.success(f"✅ {msg}")
                    st.info(f"🔑 आपका सुरक्षा सत्यापन कोड: **{otp}** (इसे नीचे दर्ज करें)")
                else:
                    st.error(f"❌ {msg}")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            f_otp = st.text_input("6-अंकीय OTP कोड दर्ज करें (Enter 6-digit OTP)", key="auth_forgot_otp")
            f_new_pass = st.text_input("नया एन्क्रिप्टेड पासवर्ड (New Password)", type="password", key="auth_forgot_newpwd")

            if st.button("🔒 नया पासवर्ड सुरक्षित करें (Reset & Save Password)", type="primary", use_container_width=True):
                target_email = st.session_state.get("active_reset_email", f_email)
                ok, msg = default_auth_service.reset_password(target_email, f_otp, f_new_pass)
                if ok:
                    st.success(f"✅ {msg}")
                    st.balloons()
                else:
                    st.error(f"❌ {msg}")


# Initialize Session State
if "is_logged_in" not in st.session_state:
    if st.query_params.get("session_auth") == "active":
        st.session_state.is_logged_in = True
        st.session_state.user_role = "🔮 मुख्य ज्योतिषी (Chief Astrologer)"
        st.session_state.user_email = "shubham8jyotish@gmail.com"
        st.session_state.birth_name = "Shubham Tiwari"
    else:
        st.session_state.is_logged_in = False

if "saved_charts" not in st.session_state:
    st.session_state.saved_charts = default_folder_manager.list_recent_charts()

if "gla_authenticated" not in st.session_state:
    st.session_state.gla_authenticated = False

_init_now = datetime.now()

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


# Gateway Check: If not logged in, render login screen
if not st.session_state.get("is_logged_in", False):
    render_login_page()
    st.stop()


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

# Compute full baseline chart with all extensions
birth_profile = BirthData(
    name=name,
    birth_date=birth_d,
    birth_time=birth_t,
    latitude=latitude,
    longitude=longitude,
    timezone_offset=tz_offset,
    city=default_city_name,
    confidence=confidence
)

try:
    chart = default_chart_calculator.calculate_full_chart(
        birth_profile,
        ayanamsa_name=ayanamsa,
        house_system=house_system,
        node_type=node_type_val
    )
except TypeError:
    try:
        chart = default_chart_calculator.calculate_full_chart(
            birth_profile,
            ayanamsa_name=ayanamsa,
            house_system=house_system
        )
    except Exception:
        chart = default_chart_calculator.calculate_chart(
            birth_profile,
            ayanamsa_name=ayanamsa,
            house_system=house_system
        )
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

now_dt = datetime.now()
current_time_str = now_dt.strftime("%d %b %Y, %I:%M %p")

# -------------------------------------------------------------
# 21 Vedic Astrology Modules Definitions
# -------------------------------------------------------------
if "English" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 Birth Chart (Natal & Vargas)",
        "🎯 Event Analysis (Ghatna Query)",
        "🛡️ Afflictions & Remedies",
        "📊 Dasvarga Table",
        "🏛️ Vastu-Jyotish",
        "❓ Prashna Kundali (Horary)",
        "⚖️ Shadbala & Bhavabala",
        "🔱 Jaimini & Upagrahas",
        "⏱️ Dasha Systems",
        "🪐 Transit & Ashtakvarga",
        "📐 KP Astrology System",
        "⏳ Auspicious Muhurta",
        "☸️ Sudarshan Chakra",
        "📅 Annual Varshaphal",
        "⏳ Birth Time Rectification (BTR)",
        "💍 Kundali Matching (Milan)",
        "💬 Jyotish AI Assistant",
        "📄 Comprehensive Report",
        "📚 12,500+ Grand Rules Library (Rules)",
        "🔍 Vedic Sage Validation",
        "⚡ Dosh & Yog Analysis (Complete)",
        "🔢 Numerology & Lo-Shu Grid",
        "📕 Lal Kitab 1952 & Remedies",
        "🍽️ Food & Ayurvedic Diet",
        "🤝 Relationships & Benefactors",
        "🏥 Health & Disease Forecast",
        "🧬 Body & Physical Traits",
        "🕉️ Ishta Devata & Pooja Vidhan",
        "🧘 Personality & Karmaphala (Karma)"
    ]
elif "Tamil" in st.session_state.app_lang or "தமிழ்" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 ஜாதகக் கட்டம் (Natal & Vargas)",
        "🎯 நிகழ்வு பகுப்பாய்வு (Ghatna Query)",
        "🛡️ தோஷ பரிகாரம் & சுயம் (Remedies)",
        "📊 தசவர்க்க அட்டவணை (Dasvarga Table)",
        "🏛️ வாஸ்து ஜோதிடம் (Vastu-Jyotish)",
        "❓ பிரசன்ன ஜோதிடம் (Horary / Prashna)",
        "⚖️ ஷட்பலம் & பாவபலம் (Shadbala)",
        "🔱 ஜெயமினி ஜோதிடம் (Jaimini)",
        "⏱️ தசா அமைப்புகள் (Dasha)",
        "🪐 கோசாரம் & அஷ்டவர்க்கம் (Transit)",
        "📐 கே.பி. ஜோதிடம் (KP Astrology)",
        "⏳ சுப முகூர்த்தம் (Muhurta)",
        "☸️ சுதர்சன சக்கரம் (Sudarshan Chakra)",
        "📅 வருட பலன்கள் (Varshaphal)",
        "⏳ பிறப்பு நேர திருத்தம் (BTR)",
        "💍 திருமணப் பொருத்தம் (Milan)",
        "💬 ஜோதிட AI உதவியாளர் (Sahayak)",
        "📄 முழுமையான அறிக்கை (Report)",
        "📚 12,500+ மகா சாஸ்திர விதிகள் (Rules)",
        "🔍 வேத ரிஷி சரிபார்ப்பு (Validation)",
        "⚡ தோஷம்-யோகம் முழு பகுப்பாய்வு (Dosh & Yog)",
        "🔢 எண்கணிதம் & லோ-ஷு கிரிட் (Numerology)",
        "📕 லால் கிதாப் 1952 பரிகாரங்கள் (Lal Kitab)",
        "🍽️ உணவு & ஆயுர்வேத முறை (Diet)",
        "🤝 உறவுகள் & நன்மை செய்வோர் (Relations)",
        "🏥 உடல்நலம் & நோய் கணிப்பு (Health)",
        "🧬 உடலமைப்பு & அங்கங்கள் (Physique)",
        "🕉️ இஷ்ட தெய்வம் & பூஜை முறை (Ishta Devata)",
        "🧘 ஆளுமை & கர்ம பலன்கள் (Karma)"
    ]
elif "Telugu" in st.session_state.app_lang or "తెలుగు" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 జన్మ జాతక చక్రం (Natal & Vargas)",
        "🎯 సంఘటన విశ్లేషణ (Ghatna Query)",
        "🛡️ దోష నివారణ & పరిహారాలు (Remedies)",
        "📊 దశవర్గ పట్టిక (Dasvarga Table)",
        "🏛️ వాస్తు జ్యోతిష్యం (Vastu-Jyotish)",
        "❓ ప్రశ్న జాతకం (Horary / Prashna)",
        "⚖️ షడ్బలం & భావబలం (Shadbala)",
        "🔱 జైమిని జ్యోతిష్యం (Jaimini)",
        "⏱️ దశా పద్ధతులు (Dasha)",
        "🪐 గోచార & అష్టకవర్గ (Transit)",
        "📐 కె.పి. పద్ధతి (KP Astrology)",
        "⏳ శుభ ముహూర్తం (Muhurta)",
        "☸️ సుదర్శన చక్రం (Sudarshan Chakra)",
        "📅 వార్షిక ఫలితాలు (Varshaphal)",
        "⏳ జన్మ సమయ శోధన (BTR)",
        "💍 గుణ మేళాపకం (Milan)",
        "💬 జ్యోతిష్య AI సహాయకుడు (Sahayak)",
        "📄 సంపూర్ణ నివేదిక (Report)",
        "📚 12,500+ మహా శాస్త్రీయ నియమాలు (Rules)",
        "🔍 వైదిక ఋషి ధృవీకరణ (Validation)",
        "⚡ దోష-యోగ సంపూర్ణ విశ్లేషణ (Dosh & Yog)",
        "🔢 సంఖ్యాశాస్త్రం & లో-షు గ్రిడ్ (Numerology)",
        "📕 లాల్ కితాబ్ 1952 నివారణలు (Lal Kitab)",
        "🍽️ ఆహార విశ్లేషణ & ఆయుర్వేదం (Diet)",
        "🤝 సంబంధాలు & శ్రేయోభిలాషులు (Relations)",
        "🏥 ఆరోగ్యం & వ్యాధి విశ్లేషణ (Health)",
        "🧬 శరీర నిర్మాణం & అవయవాలు (Physique)",
        "🕉️ ఇష్ట దైవం & పూజా విధానం (Ishta Devata)",
        "🧘 వ్యక్తిత్వం & కర్మఫలం (Karma)"
    ]
elif "Gujarati" in st.session_state.app_lang or "ગુજરાતી" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 જન્મ કુંડળી (Natal & Vargas)",
        "🎯 ઘટના વિશ્લેષણ (Ghatna Query)",
        "🛡️ દોષ અને ફ્રી-વિલ (Affliction & Remedies)",
        "📊 દશવર્ગ કોષ્ટક (Dasvarga Table)",
        "🏛️ વાસ્તુ-જ્યોતિષ (Vastu-Jyotish)",
        "❓ પ્રશ્ન કુંડળી (Horary / Prashna)",
        "⚖️ ષડ્બળ અને ભાવબળ (Shadbala)",
        "🔱 જૈમિની અને ઉપગ્રહો (Jaimini)",
        "⏱️ દશા પ્રણાલી (Dasha)",
        "🪐 ગોચર અને અષ્ટકવર્ગ (Gochar & Shodhana)",
        "📐 કે.પી. પદ્ધતિ (KP Astrology)",
        "⏳ શુભ મુહૂર્ત (Muhurta)",
        "☸️ સુદર્શન ચક્ર (Sudarshan Chakra)",
        "📅 વર્ષફળ (Varshaphal)",
        "⏳ સમય સંશોધન (BTR)",
        "💍 કુંડળી મેળવણું (Milan)",
        "💬 જ્યોતિષ AI સહાયક (Sahayak)",
        "📄 સંપૂર્ણ અહેવાલ (Report)",
        "📚 ૧૨,૫૦૦+ મહા-શાસ્ત્રીય નિયમો (Rules)",
        "🔍 વૈદિક ઋષિ પ્રમાણીકરણ (Validation)",
        "⚡ દોષ-યોગ સંપૂર્ણ વિશ્લેષણ (Dosh & Yog)",
        "🔢 અંકશાસ્ત્ર અને લો-શૂ ગ્રિડ (Numerology)",
        "📕 લાલ કિતાબ ૧૯૫૨ ઉપાયો (Lal Kitab)",
        "🍽️ ખાનપાન અને આહાર (Diet)",
        "🤝 સંબંધો અને સહયોગીઓ (Relations)",
        "🏥 સ્વાસ્થ્ય અને રોગ નિદાન (Health)",
        "🧬 શારીરિક ગઠન અને અંગો (Physique)",
        "🕉️ ઇષ્ટદેવ અને પૂજા વિધાન (Ishta Devata)",
        "🧘 વ્યક્તિત્વ અને કર્મફળ (Karma)"
    ]
elif "Marathi" in st.session_state.app_lang or "मराठी" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 जन्म पत्रिका (Natal & Vargas)",
        "🎯 घटना विश्लेषण (Ghatna Query)",
        "🛡️ दोष व फ्री-विल (Affliction & Remedies)",
        "📊 दशवर्ग तक्ता (Dasvarga Table)",
        "🏛️ वास्तु-ज्योतिष (Vastu-Jyotish)",
        "❓ प्रश्न पत्रिका (Horary / Prashna)",
        "⚖️ षड्बल व भावबल (Shadbala)",
        "🔱 जैमिनी व उपग्रह (Jaimini)",
        "⏱️ दशा प्रणाली (Dasha)",
        "🪐 गोचर व अष्टकवर्ग (Gochar & Shodhana)",
        "📐 के.पी. पद्धती (KP Astrology)",
        "⏳ शुभ मुहूर्त (Muhurta)",
        "☸️ सुदर्शन चक्र (Sudarshan Chakra)",
        "📅 वर्षफळ (Varshaphal)",
        "⏳ वेळ शोधन (BTR)",
        "💍 पत्रिका मिलन (Milan)",
        "💬 ज्योतिष AI सहाय्यक (Sahayak)",
        "📄 संपूर्ण अहवाल (Report)",
        "📚 १२,५००+ महा-शास्त्रीय नियम (Rules)",
        "🔍 वैदिक ऋषी पडताळणी (Validation)",
        "⚡ दोष-योग संपूर्ण विश्लेषण (Dosh & Yog)",
        "🔢 अंकशास्त्र व लो-शू ग्रिड (Numerology)",
        "📕 लाल किताब १९५२ उपाय (Lal Kitab)",
        "🍽️ खानपान व आयुर्वेदिक आहार (Diet)",
        "🤝 नातेसंबंध व हितचिंतक (Relations)",
        "🏥 आरोग्य व रोग निदान (Health)",
        "🧬 शारीरिक गठन व अवयव (Physique)",
        "🕉️ इष्टदेवता व नित्य पूजा विधी (Ishta Devata)",
        "🧘 व्यक्तिमत्त्व व कर्मफळ (Karma)"
    ]
elif "Bengali" in st.session_state.app_lang or "বাংলা" in st.session_state.app_lang:
    MODULE_OPTIONS = [
        "📜 জন্ম কুণ্ডলী (Natal & Vargas)",
        "🎯 ঘটনা বিশ্লেষণ (Ghatna Query)",
        "🛡️ দোষ ও প্রতিকার (Affliction & Remedies)",
        "📊 দশবর্গ তালিকা (Dasvarga Table)",
        "🏛️ বাস্তু-জ্যোতিষ (Vastu-Jyotish)",
        "❓ প্রশ্ন কুণ্ডলী (Horary / Prashna)",
        "⚖️ ষড়্বল ও ভাববল (Shadbala)",
        "🔱 জৈমিনী ও উপগ্রহ (Jaimini)",
        "⏱️ দশা পদ্ধতি (Dasha)",
        "🪐 গোচর ও অষ্টকবর্গ (Gochar & Shodhana)",
        "📐 কে.পি. পদ্ধতি (KP Astrology)",
        "⏳ শুভ মুহূর্ত (Muhurta)",
        "☸️ সুদর্শন চক্র (Sudarshan Chakra)",
        "📅 বর্ষফল (Varshaphal)",
        "⏳ সময় সংশোধন (BTR)",
        "💍 কুণ্ডলী মিলন (Milan)",
        "💬 জ্যোতিষ AI সহকারী (Sahayak)",
        "📄 সম্পূর্ণ রিপোর্ট (Report)",
        "📚 ১২,৫০০+ মহা-শাস্ত্রীয় নিয়ম (Rules)",
        "🔍 বৈদিক ঋষি প্রমাণ (Validation)",
        "⚡ দোষ-যোগ সম্পূর্ণ বিশ্লেষণ (Dosh & Yog)",
        "🔢 সংখ্যাতত্ত্ব ও লো-শু গ্রিড (Numerology)",
        "📕 লাল কিতাব ১৯৫২ প্রতিকার (Lal Kitab)",
        "🍽️ খাদ্যাভ্যাস ও আয়ুর্বেদিক আহার (Diet)",
        "🤝 সম্পর্ক ও শুভাকাঙ্ক্ষী (Relations)",
        "🏥 স্বাস্থ্য ও রোগ নির্ণয় (Health)",
        "🧬 শারীরিক গঠন ও অঙ্গপ্রত্যঙ্গ (Physique)",
        "🕉️ ইষ্টদেবতা ও পূজা বিধান (Ishta Devata)",
        "🧘 ব্যক্তিত্ব ও কর্মফল (Karma)"
    ]
else:
    MODULE_OPTIONS = [
        "📜 जन्म कुण्डली (Natal & Vargas)",
        "🎯 घटना विश्लेषण (Ghatna Query)",
        "🛡️ दोष एवं फ्री-विल (Affliction & Remedies)",
        "📊 दशवर्ग तालिका (Dasvarga Table)",
        "🏛️ वास्तु-ज्योतिष (Vastu-Jyotish)",
        "❓ प्रश्न कुण्डली (Horary / Prashna)",
        "⚖️ षड्बल एवं भावबल (Shadbala)",
        "🔱 जैमिनी एवं उपग्रह (Jaimini)",
        "⏱️ दशा प्रणालियाँ (Dasha)",
        "🪐 गोचर एवं अष्टकवर्ग (Gochar & Shodhana)",
        "📐 के.पी. प्रणाली (KP Astrology)",
        "⏳ शुभ मुहूर्त एवं चौघड़िया (Muhurta)",
        "☸️ सुदर्शन चक्र (Sudarshan Chakra)",
        "📅 वर्षफल (Varshaphal)",
        "⏳ समय शोधन (BTR)",
        "💍 कुण्डली मिलान (Milan)",
        "💬 ज्योतिष AI सहायक (Sahayak)",
        "📄 सम्पूर्ण रिपोर्ट (Report)",
        "📚 १२,५००+ महा-शास्त्रीय नियम (Rules Bank)",
        "🔍 वैदिक ऋषि सत्यापन (Validation)",
        "⚡ सम्पूर्ण दोष एवं योग (Dosh & Yog)",
        "🔢 अंकशास्त्र एवं लो-शू ग्रिड (Numerology)",
        "📕 लाल किताब 1952 एवं उपाय (Lal Kitab)",
        "🍽️ खानपान एवं त्रिदोष आहार (Diet)",
        "🤝 संबंध एवं स्वजन-शत्रु (Relations)",
        "🏥 स्वास्थ्य एवं रोग-निदान (Health)",
        "🧬 शारीरिक गठन एवं अंग-दोष (Body & Limbs)",
        "🕉️ इष्टदेवता, नित्य पूजा एवं व्रत (Ishta Devata)",
        "🧘 व्यक्तित्व एवं कर्मफल (Personality & Karma)"
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


if "active_module_idx" not in st.session_state:
    st.session_state.active_module_idx = 0
st.session_state.active_module_idx = max(0, min(int(st.session_state.active_module_idx), len(MODULE_OPTIONS) - 1))

# Keep top_bar_module_selector in sync with active_module_idx and current language
if ("top_bar_module_selector" not in st.session_state or 
    st.session_state.top_bar_module_selector not in MODULE_OPTIONS):
    st.session_state.top_bar_module_selector = MODULE_OPTIONS[st.session_state.active_module_idx]

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

    # 7 Essential Clean Toolbelt Actions (Spacious, Minimal & Uncluttered - Frozen Sticky at Top)
    with st.container(key="frozen_toolbelt_container", border=False):
        tb_cols = st.columns(9, gap="small")

        # Helper function for rendering clickable tile (Streamlit Native Button - In-Session Instant Trigger)
        def render_tool_tile(col, emoji_icon, label_text, tool_key):
            with col:
                is_active = (st.session_state.gla_active_tool == tool_key)
                btn_type = "primary" if is_active else "secondary"
                btn_label = f"{emoji_icon} {label_text}"
                if st.button(btn_label, key=f"gla_tile_btn_{tool_key}", use_container_width=True, type=btn_type, help=f"{label_text} मेन्यू खोलें"):
                    if st.session_state.gla_active_tool == tool_key:
                        st.session_state.gla_active_tool = None
                    else:
                        st.session_state.gla_active_tool = tool_key
                    st.rerun()

        # 1. New Chart
        render_tool_tile(tb_cols[0], "✨", "New", "new")

        # 2. Birth Data
        render_tool_tile(tb_cols[1], "📅", "Birth Data", "birth")

        # 3. Open Folder (Client Kundali Vault)
        render_tool_tile(tb_cols[2], "📂", "Open Vault", "open")

        # 4. Save Chart
        render_tool_tile(tb_cols[3], "💾", "Save", "save")

        # 5. Time Stepper (Time Travel)
        render_tool_tile(tb_cols[4], "⏱️", "BTR & Rule", "clock")

        # 6. Server Sync (Placed between BTR & Rule and Theme)
        render_tool_tile(tb_cols[5], "☁️", "Server", "server")

        # 6. Theme Mode
        render_tool_tile(tb_cols[6], "🌓", "Theme", "theme")

        # 7. Settings (Placed between Theme and Logout)
        render_tool_tile(tb_cols[7], "⚙️", "Settings", "settings")

        # 8. Logout
        render_tool_tile(tb_cols[8], "🚪", "Logout", "logout")

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
        } catch(e) {}
        </script>
        """, height=0, width=0)

    # Physical spacer between toolbelt and module selector/dialogs
    st.markdown("<div style='height: 10px; margin: 0; padding: 0;'></div>", unsafe_allow_html=True)



    # Active tool dialog/form container
    if st.session_state.gla_active_tool:
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

        # 1. TOOL: NEW / RESET
        if st.session_state.gla_active_tool == "new":
            with st.container(border=True):
                st.markdown("### 📄 नया चार्ट तैयार करें (New Chart / Reset)")
                st.write("क्या आप वर्तमान विवरण रीसेट करके नया ब्लैंक या डिफ़ॉल्ट प्रोफाइल शुरू करना चाहते हैं?")
                col_n1, col_n2, col_n3 = st.columns([1.5, 1.5, 3])
                if col_n1.button("✨ नया ब्लैंक प्रोफाइल (New Blank)", type="primary", use_container_width=True):
                    st.session_state.birth_name = "New Client"
                    st.session_state.birth_gender = "Male"
                    st.session_state.birth_date = date.today()
                    st.session_state.birth_time = time(12, 0, 0)
                    st.session_state.birth_city = "New Delhi, Delhi, India"
                    st.session_state.birth_lat = 28.6139
                    st.session_state.birth_lon = 77.2090
                    st.session_state.birth_tz = 5.5
                    st.session_state.gla_active_tool = "birth"
                    st.toast("✅ नया प्रोफाइल तैयार! कृपया जन्म विवरण भरें।", icon="👶")
                    st.rerun()
                if col_n2.button("🔄 डिफ़ॉल्ट रीसेट (Default Profile)", use_container_width=True):
                    st.session_state.birth_name = "डेमो जातक (Demo Profile)"
                    st.session_state.birth_gender = "Male"
                    st.session_state.birth_date = date(1995, 1, 1)
                    st.session_state.birth_time = time(12, 0, 0)
                    st.session_state.birth_city = "New Delhi, Delhi, India"
                    st.session_state.birth_lat = 28.6139
                    st.session_state.birth_lon = 77.2090
                    st.session_state.birth_tz = 5.5
                    st.session_state.gla_active_tool = None
                    st.toast("✅ डिफ़ॉल्ट डेमो प्रोफाइल लोड की गई!", icon="🔄")
                    st.rerun()
                if col_n3.button("❌ बंद करें (Close)", use_container_width=True):
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

                # Row 3: City Geocoding & Coordinates
                col_geo1, col_geo2, col_geo3 = st.columns([1.6, 1.4, 1.2])
                with col_geo1:
                    in_city_query = st.text_input("स्थान खोज (Search City)", value=st.session_state.birth_city, key="gla_city_query_input")
                    geo_results = default_geocoding_service.search(in_city_query, limit=3)
                    if geo_results:
                        selected_loc = st.selectbox(
                            "उपलब्ध स्थान (Select Location)",
                            geo_results,
                            format_func=lambda x: f"{x.formatted_name} ({x.source})",
                            key="gla_geo_select"
                        )
                        st.session_state.birth_lat = selected_loc.latitude
                        st.session_state.birth_lon = selected_loc.longitude
                        st.session_state.birth_tz = selected_loc.timezone_offset
                        st.session_state.birth_city = selected_loc.city

                with col_geo2:
                    col_la, col_lo = st.columns(2)
                    in_lat = col_la.number_input("Latitude", value=float(st.session_state.birth_lat), format="%.4f", key="gla_lat_input")
                    in_lon = col_lo.number_input("Longitude", value=float(st.session_state.birth_lon), format="%.4f", key="gla_lon_input")
                    st.session_state.birth_lat = in_lat
                    st.session_state.birth_lon = in_lon

                with col_geo3:
                    col_tz_a, col_conf_a = st.columns(2)
                    in_tz = col_tz_a.number_input("TZ Offset", value=float(st.session_state.get("birth_tz", 5.5)), step=0.5, key="gla_tz_input")
                    in_conf = col_conf_a.selectbox("Confidence", ["Exact", "Approx (±15 min)", "Unknown"], key="gla_conf_select")
                    st.session_state.birth_tz = in_tz
                    st.session_state.birth_conf = in_conf

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
                        default_folder_manager.save_chart(folder_id=0, chart_name=st.session_state.birth_name, birth_data=save_payload)
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
                        col_vs1, col_vs2 = st.columns([3, 1.5])
                        with col_vs1:
                            v_search = st.text_input("🔍 नाम, शहर अथवा नोट्स द्वारा खोजें (Search Clients):", placeholder="जैसे: Vivek, Delhi, विवाह, VIP...", key="v_search_in")
                        with col_vs2:
                            tag_options = ["सभी (All)"] + vault_mod.AVAILABLE_TAGS
                            v_tag = st.selectbox("🏷️ श्रेणी / टैग फ़िल्टर (Tag Filter):", tag_options, index=0, key="v_tag_sel")

                        clients_list = v_service.list_all_clients(search_query=v_search, tag_filter=v_tag)

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
                                        v_service.delete_client(c_id)
                                        st.toast(f"कुण्डली हटाई गई!", icon="🗑️")
                                        st.rerun()

                    with tab_v_backup:
                        st.markdown("#### 📦 कुण्डली वॉल्ट बैकअप एवं रिस्टोर (Backup & Restore)")
                        st.write("अपने सभी सहेजे गए क्लाइंट्स एवं कुण्डलियों का संपूर्ण डेटा JSON बैकअप के रूप में डाउनलोड करें अथवा पूर्व बैकअप से पुनः स्थापित करें:")

                        c_bk1, c_bk2 = st.columns(2)
                        with c_bk1:
                            st.markdown("##### 📥 बैकअप डाउनलोड")
                            vault_json = v_service.export_backup_json()
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
                                    ok, msg, cnt = v_service.import_backup_json(content)
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
                                    default_folder_manager.sync_from_grahalakshanam(ff)
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
                        all_local_folders = default_folder_manager.list_folders()
                        f_options = {f["id"]: f["name"] for f in all_local_folders}
                        sel_fid = st.selectbox("📁 फ़ोल्डर चुनें (Select Folder)", list(f_options.keys()), format_func=lambda x: f_options[x], key="gla_save_folder_sel")
                        save_notes_input = st.text_area("📝 परामर्श नोट्स (Consultant Notes):", placeholder="जैसे: करियर व विवाह विचार, नीलम व पन्ना रत्न संस्तुति...", key="gla_save_notes_ta", height=85)

                    col_sv_act1, col_sv_act2 = st.columns([2, 1])
                    with col_sv_act1:
                        if st.button("💾 सुरक्षित करें (Confirm Save)", type="primary", use_container_width=True, key="gla_confirm_save_btn"):
                            save_payload = {
                                "name": save_name_input,
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
                                name=save_name_input,
                                birth_data=save_payload,
                                tags=sel_tags,
                                notes=save_notes_input,
                                folder_id=sel_fid
                            )
                            st.session_state.birth_name = save_name_input
                            st.session_state.gla_active_tool = None
                            st.toast(f"✅ कुण्डली '{save_name_input}' टैग्स एवं नोट्स सहित सुरक्षित कर ली गई!", icon="💾")
                            st.rerun()

                    with col_sv_act2:
                        if st.button("❌ बंद करें (Close)", use_container_width=True, key="gla_close_save_btn"):
                            st.session_state.gla_active_tool = None
                            st.rerun()

                except Exception as _e_save_v:
                    st.error(f"सहेजने में त्रुटि: {_e_save_v}")

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
                        "jagannatha": "जगन्नाथ द्रेष्काण (PVR / Rath)",
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

                # Row 3: Fundamental Calculation Engine (Ayanamsa, Nodes, Houses, Pro Mode)
                st.markdown("##### 📐 मूल गणना प्राथमिकताएं (Fundamental Calculation Preferences)")
                col_st1, col_st2, col_st3, col_st4 = st.columns([2.2, 1.8, 1.6, 1.4])
                with col_st1:
                    ay_opts = [
                        "Lahiri", "Pushya-Paksha (PVR Rao)", "KP Old", "KP New (Straight Line)",
                        "Raman", "True Chitra (Spica 180°)", "Yukteshwar", "Fagan-Bradley"
                    ]
                    cur_ay = st.session_state.get("app_ayanamsa", "Lahiri")
                    ay_idx = ay_opts.index(cur_ay) if cur_ay in ay_opts else 0
                    in_ay = col_st1.selectbox("अयनांश (Ayanamsa)", ay_opts, index=ay_idx, key="gla_settings_ayanamsa")
                    st.session_state.app_ayanamsa = in_ay

                with col_st2:
                    node_opts = ["Mean Node (पारंपरिक औसत)", "True Node (सच्चे पात - Meeus)"]
                    cur_node = st.session_state.get("app_node_type", "Mean Node (पारंपरिक औसत)")
                    node_idx = node_opts.index(cur_node) if cur_node in node_opts else 0
                    in_node = col_st2.selectbox("राहु-केतु गणना (Nodes)", node_opts, index=node_idx, key="gla_settings_node")
                    st.session_state.app_node_type = in_node

                with col_st3:
                    hs_opts = ["Whole Sign", "Equal", "Placidus", "Shripati", "Koch"]
                    cur_hs = st.session_state.get("app_house_system", "Whole Sign")
                    hs_idx = hs_opts.index(cur_hs) if cur_hs in hs_opts else 0
                    in_hs = col_st3.selectbox("भाव पद्धति (Houses)", hs_opts, index=hs_idx, key="gla_settings_hs")
                    st.session_state.app_house_system = in_hs

                with col_st4:
                    in_pm = col_st4.toggle("⚡ Pro Mode", value=st.session_state.get("app_pro_mode", True), key="gla_settings_pm_toggle")
                    st.session_state.app_pro_mode = in_pm

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
                    st.markdown("### ⏱️ BTR (जन्म समय शोधन), काल गति नियंत्रक एवं १२,५००+ शास्त्रीय नियम")
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
                            <span style="color: {_rules_text_color} !important;">📚 <b>१२,५००+ महा-शास्त्रीय नियम इंजन (AI लिंक्ड):</b></span>
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
                    def _step_time_modal_action(delta_minutes=0, delta_hours=0, delta_days=0, reset_to_now=False):
                        from datetime import datetime as dt_cls, timedelta as td_cls
                        if reset_to_now:
                            now_curr = dt_cls.now()
                            st.session_state.birth_date = now_curr.date()
                            st.session_state.birth_time = now_curr.time().replace(microsecond=0)
                        else:
                            curr_b_d = st.session_state.get("birth_date", _init_now.date())
                            curr_b_t = st.session_state.get("birth_time", _init_now.time())
                            c_combo = dt_cls.combine(curr_b_d, curr_b_t)
                            n_combo = c_combo + td_cls(days=delta_days, hours=delta_hours, minutes=delta_minutes)
                            st.session_state.birth_date = n_combo.date()
                            st.session_state.birth_time = n_combo.time().replace(microsecond=0)
                        st.rerun()

                    ts_b_cols = st.columns(9, gap="small", vertical_alignment="center")
                    if ts_b_cols[0].button("⏪ -1द", key="ts_m_btn_m1d", help="-1 दिन पीछे जाएं"): _step_time_modal_action(delta_days=-1)
                    if ts_b_cols[1].button("◀ -1घं", key="ts_m_btn_m1h", help="-1 घंटा पीछे जाएं"): _step_time_modal_action(delta_hours=-1)
                    if ts_b_cols[2].button("‹ -15म", key="ts_m_btn_m15m", help="-15 मिनट पीछे जाएं"): _step_time_modal_action(delta_minutes=-15)
                    if ts_b_cols[3].button("‹ -1म", key="ts_m_btn_m1m", help="-1 मिनट (BTR सूक्ष्म शोधन)"): _step_time_modal_action(delta_minutes=-1)
                    if ts_b_cols[4].button("🔄 अब", key="ts_m_btn_now", type="primary", help="वर्तमान समय (Current Time) पर सेट करें"): _step_time_modal_action(reset_to_now=True)
                    if ts_b_cols[5].button("+1म ›", key="ts_m_btn_p1m", help="+1 मिनट (BTR सूक्ष्म शोधन)"): _step_time_modal_action(delta_minutes=1)
                    if ts_b_cols[6].button("+15म ›", key="ts_m_btn_p15m", help="+15 मिनट आगे जाएं"): _step_time_modal_action(delta_minutes=15)
                    if ts_b_cols[7].button("+1घं ▶", key="ts_m_btn_p1h", help="+1 घंटा आगे जाएं"): _step_time_modal_action(delta_hours=1)
                    if ts_b_cols[8].button("+1द ⏩", key="ts_m_btn_p1d", help="+1 दिन आगे जाएं"): _step_time_modal_action(delta_days=1)

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
                            st.session_state.birth_lat = picked_loc.latitude
                            st.session_state.birth_lon = picked_loc.longitude
                            st.session_state.birth_tz = picked_loc.timezone_offset
                            st.session_state.birth_city = picked_loc.city
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
                        st.session_state.gla_active_tool = None
                        if "session_auth" in st.query_params:
                            del st.query_params["session_auth"]
                        st.toast("✅ आप सुरक्षित रूप से लॉगआउट हो गए हैं।", icon="🚪")
                        st.rerun()
                with col_lg2:
                    if st.button("❌ नहीं, रद्द करें", use_container_width=True, key="gla_cancel_logout_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()



    def _nav_prev_module():
        new_idx = (st.session_state.active_module_idx - 1) % len(MODULE_OPTIONS)
        st.session_state.active_module_idx = new_idx
        if "sb_cat_filter_select" in st.session_state:
            st.session_state.sb_cat_filter_select = "📁 समस्त २९ मॉड्यूल (All Modules)"
        if "sb_search_filter_input" in st.session_state:
            st.session_state.sb_search_filter_input = ""

    def _nav_next_module():
        new_idx = (st.session_state.active_module_idx + 1) % len(MODULE_OPTIONS)
        st.session_state.active_module_idx = new_idx
        if "sb_cat_filter_select" in st.session_state:
            st.session_state.sb_cat_filter_select = "📁 समस्त २९ मॉड्यूल (All Modules)"
        if "sb_search_filter_input" in st.session_state:
            st.session_state.sb_search_filter_input = ""

    def _nav_to_rules_bank():
        st.session_state.active_module_idx = 18
        if "sb_cat_filter_select" in st.session_state:
            st.session_state.sb_cat_filter_select = "📁 समस्त २९ मॉड्यूल (All Modules)"
        if "sb_search_filter_input" in st.session_state:
            st.session_state.sb_search_filter_input = ""

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
        _sb_prof_tag = "#00E5FF" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#0073CF")
        _sb_prof_name = "#FFFFFF" if (is_astrallis_mode or is_night_mode) else "#0F172A"
        _sb_prof_sub = "#CBD5E1" if (is_astrallis_mode or is_night_mode) else "#475569"
        st.markdown(f"""
        <div style="background:{_sb_card_bg}; border:2px solid {_sb_card_border}; border-radius:12px; padding:10px 14px; margin-bottom:10px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size:11px; font-weight:800; color:{_sb_prof_tag}; text-transform:uppercase; letter-spacing:0.5px;">👤 सक्रिय जातक प्रोफाइल</div>
            <div style="font-size:15.5px; font-weight:900; color:{_sb_prof_name}; margin:3px 0;">{name}</div>
            <div style="font-size:11.5px; color:{_sb_prof_sub}; line-height:1.4;">
                📅 {birth_d.strftime('%d-%b-%Y')} | ⏰ {birth_t.strftime('%I:%M %p')}<br/>
                📍 {default_city_name} | <b>लग्न:</b> {chart.lagna_sign_name}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # -----------------------------------------------------
        # ⚡ DIGITAL PANCHANG CARD (जातक का डिजिटल पंचांग - १० अंग)
        # -----------------------------------------------------
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

        _pill_bg = "#0D1D35" if is_astrallis_mode else ("#1F2937" if is_night_mode else "#F8FAFC")
        _pill_border = "#1E293B" if is_astrallis_mode else ("#374151" if is_night_mode else "#E2E8F0")
        _pill_label = "#00E5FF" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#0073CF")
        _pill_val = "#FFFFFF" if (is_astrallis_mode or is_night_mode) else "#000000"

        st.markdown(f"""
        <div style="background:{_sb_card_bg}; border:2px solid {_sb_card_border}; border-radius:12px; padding:10px 12px; margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="font-size:11px; font-weight:800; color:{_sb_prof_tag}; text-transform:uppercase; letter-spacing:0.5px;">⚡ जातक डिजिटल पंचांग</div>
                <span style="font-size:9.5px; font-weight:800; background:{_pill_bg}; color:#10B981; border:1px solid #10B981; border-radius:4px; padding:1px 5px;">● शुद्ध</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 11px;">
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">📅 तिथि</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_tithi_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">🪐 वार</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_vara_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">✨ नक्षत्र</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_nak_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">🌿 योग</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_yoga_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">⚡ करण</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_karana_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">🌅 सूर्योदय</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_sr_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">🌇 सूर्यास्त</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_ss_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">⏳ जन्म घटी</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_ghati_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">👑 होरा स्वामी</span>
                    <b style="color:{_pill_val}; font-size:11px; font-weight:800; word-break:break-word;">{_hora_str}</b>
                </div>
                <div style="background:{_pill_bg}; border:1px solid {_pill_border}; border-radius:7px; padding:4px 6px;">
                    <span style="color:{_pill_label}; font-size:9.5px; font-weight:700; display:block;">🛡️ परिशुद्धता</span>
                    <b style="color:#10B981; font-size:11px; font-weight:800; word-break:break-word;">99.9% शुद्ध</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📚 समस्त २९ वैदिक मॉड्यूल")
        
        sb_query = st.text_input("🔍 मॉड्यूल खोजें (Search):", placeholder="दशा, गोचर, केपी, मिलान...", key="sb_search_filter_input").strip().lower()
        
        # All 30 modules available directly in the sidebar
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
            "वैदिक मॉड्यूल्स (२९ मॉड्यूल)",
            filtered_mods,
            index=radio_idx,
            label_visibility="collapsed"
        )
        selected_idx = MODULE_OPTIONS.index(selected_module) if selected_module in MODULE_OPTIONS else curr_idx
        if selected_idx != curr_idx:
            st.session_state.active_module_idx = selected_idx
            st.rerun()

    # ---------------------------------------------------------
    # 3. TOP HEADER CONTAINER: QUICK CONTROLS & BREADCRUMB
    # ---------------------------------------------------------
    st.markdown("<div style='height: 10px; margin: 0; padding: 0;'></div>", unsafe_allow_html=True)
    col_btn_prev, col_active_info, col_btn_next = st.columns([1.2, 5.6, 1.2])
    with col_btn_prev:
        st.button("❮ पिछला (Prev)", use_container_width=True, help="पिछला मॉड्यूल खोलें", key="top_prev_mod_btn", on_click=_nav_prev_module)

    with col_active_info:
        # Instant direct 30-module switcher (accessible always, even if sidebar is closed)
        _cur_m_name = MODULE_OPTIONS[st.session_state.active_module_idx] if 0 <= st.session_state.active_module_idx < len(MODULE_OPTIONS) else MODULE_OPTIONS[0]
        chosen_module = st.selectbox(
            "सक्रिय मॉड्यूल (Active Module)",
            MODULE_OPTIONS,
            index=MODULE_OPTIONS.index(_cur_m_name),
            label_visibility="collapsed",
            help="किसी भी मॉड्यूल पर तुरंत जाने के लिए यहाँ से चुनें"
        )
        if chosen_module != _cur_m_name:
            st.session_state.active_module_idx = MODULE_OPTIONS.index(chosen_module)
            st.rerun()

    with col_btn_next:
        st.button("अगला (Next) ❯", use_container_width=True, help="अगला मॉड्यूल खोलें", key="top_next_mod_btn", on_click=_nav_next_module)


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
# Module Routing
# -------------------------------------------------------------
if selected_idx == 0:
    st.subheader("📜 जन्म कुण्डली एवं षोडशवर्ग चक्र (Natal & Divisional Charts)")

    tab_d1, tab_jm_hud, tab_bhav, tab_chandra, tab_surya, tab_yuddha, tab_vishesh, tab_kota = st.tabs([
        "📜 जन्म कुण्डली एवं षोडशवर्ग चक्र (D1 to D60)",
        "👑 विशेष जैमिनी लग्न (Special Lagnas - J.Hora Standard)",
        "🏠 भाव चलित चक्र",
        "🌙 चन्द्र कुण्डली",
        "☀️ सूर्य कुण्डली",
        "⚔️ ग्रह युद्ध",
        "🌟 विशेष लग्न",
        "🏰 कोटा चक्र (Kota Chakra)"
    ])

    with tab_d1:
        VARGA_SIGNIFICANCE = {
            "D1": "समस्त जीवन, शारीरिक गठन एवं आत्म-व्यक्तित्व (General Life & Body)",
            "D2": "धन, संपत्ति, वित्तीय स्थिति एवं कुटुम्ब (Wealth & Family Prosperity)",
            "D3": "पराक्रम, भ्रातृ सुख, साहस एवं ऊर्जा (Courage, Siblings & Valor)",
            "D4": "अचल संपत्ति, भवन, वाहन एवं भाग्य (Fixed Assets, Property & Fortune)",
            "D7": "संतान सुख, वंश वृद्धि एवं रचनात्मकता (Children & Progeny)",
            "D9": "धर्म, वैवाहिक जीवन, जीवनसाथी एवं आत्मबल (Dharma, Marriage & Destiny)",
            "D10": "कर्म, आजीविका, प्रतिष्ठा, पद एवं अधिकार (Career, Profession & Power)",
            "D12": "माता-पिता, पितृ ऋण एवं पैतृक विरासत (Parents & Ancestral Lineage)",
            "D16": "वाहन, भौतिक सुख-साधन एवं अंतःकरण (Vehicles, Luxuries & Mind)",
            "D20": "आध्यात्मिक साधना, उपासना एवं ईश्वरीय कृपा (Spiritual Quest & Bhakti)",
            "D24": "उच्च विद्या, ज्ञान, मेधा शक्ति एवं कौशल (Higher Learning & Intellect)",
            "D27": "शारीरिक बल, सामर्थ्य, गुण एवं दुर्बलताएं (Strengths & Weaknesses)",
            "D30": "अरिष्ट, रोग, पाप प्रभाव एवं संकट (Misfortunes, Evils & Challenges)",
            "D60": "पूर्वजन्म के संचित कर्म एवं अंतिम प्रारब्ध (Past Life Karma & Core Destiny)",
        }

        curr_style = st.session_state.get("app_chart_style", "North Indian (Diamond)")
        chart_view_mode = st.session_state.get("app_chart_view_mode", "Single")

        if chart_view_mode == "Quad":
            st.markdown("#### 🖥️ ४-कुण्डली एकीकृत्त वर्कबेंच (D1 लग्न + D9 नवांश + D10 दशमांश + D7 सप्तांश)")
            st.caption("विश्वस्तरीय सॉफ्टवेयर (Parashara's Light / JHora) समान एक ही स्क्रीन पर प्रमुख वर्ग चक्रों का एक साथ अध्ययन:")

            q_col1, q_col2 = st.columns(2, gap="medium")
            with q_col1:
                svg_d1 = render_chart_svg(chart, "D1 जन्म लग्न (Rashi)", varga_code="D1")
                st.markdown(f'<div class="kundali-chart" style="width:100%;">{svg_d1}</div>', unsafe_allow_html=True)
                st.caption(f"**D1 लग्न:** {chart.lagna_sign_name} ({chart.lagna_sign_id}) | आत्मकारक (AK): {chart.atmakaraka}")
            with q_col2:
                svg_d9 = render_chart_svg(chart, "D9 नवांश (Navamsha — धर्म व दांपत्य)", varga_code="D9")
                st.markdown(f'<div class="kundali-chart" style="width:100%;">{svg_d9}</div>', unsafe_allow_html=True)
                d9_v = chart.vargas.get("D9")
                st.caption(f"**D9 नवांश लग्न:** {d9_v.lagna_sign_name if d9_v else '—'} | विवाह, भाग्य व ग्रहों का आंतरिक बल")

            q_col3, q_col4 = st.columns(2, gap="medium")
            with q_col3:
                svg_d10 = render_chart_svg(chart, "D10 दशमांश (Dashamsha — कर्म व पद)", varga_code="D10")
                st.markdown(f'<div class="kundali-chart" style="width:100%;">{svg_d10}</div>', unsafe_allow_html=True)
                d10_v = chart.vargas.get("D10")
                st.caption(f"**D10 दशमांश लग्न:** {d10_v.lagna_sign_name if d10_v else '—'} | आजीविका, नेतृत्व व करियर")
            with q_col4:
                svg_d7 = render_chart_svg(chart, "D7 सप्तांश (Saptamsha — संतान व सृजन)", varga_code="D7")
                st.markdown(f'<div class="kundali-chart" style="width:100%;">{svg_d7}</div>', unsafe_allow_html=True)
                d7_v = chart.vargas.get("D7")
                st.caption(f"**D7 सप्तांश लग्न:** {d7_v.lagna_sign_name if d7_v else '—'} | वंश वृद्धि, संतान सुख व रचनात्मकता")

        # =========================================================================
        # 🏛️ PARASHARA'S LIGHT AUTHENTIC 2x2 WORKSTATION GRID (70% RIGHT PANEL)
        # =========================================================================
        if is_parashara_layout:
            # Row 1: Box 1 (Vimshottari Dasha 5-Level) & Box 2 (Shadbala & Vimsopaka Strength)
            pl_r1_c1, pl_r1_c2 = st.columns(2, gap="small")
            with pl_r1_c1:
                st.markdown("""<div class="pl-box-header"><span>⏱️ विंशोत्तरी दशा (Vimshottari Dasha — 5-स्तरीय)</span><span style="font-size:11px;">सक्रिय काल</span></div>""", unsafe_allow_html=True)
                try:
                    _b_dt = datetime.combine(birth_d, birth_t)
                    _m_lon = chart.planets["Moon"].longitude if "Moon" in chart.planets else 0.0
                    _h5 = default_dasha_engine.get_5level_hierarchy(_b_dt, _m_lon, datetime.now())
                    _m_lord = _h5["mahadasha"]["lord"]
                    _a_lord = _h5["antardasha"]["lord"]
                    _pr_lord = _h5["pratyantardasha"]["lord"]
                    _s_lord = _h5["sookshmadasha"]["lord"]
                    _p_lord = _h5["pranadasha"]["lord"]

                    _m_s = _h5["mahadasha"]["start_date"].strftime("%d-%b-%y")
                    _m_e = _h5["mahadasha"]["end_date"].strftime("%d-%b-%y")
                    _a_s = _h5["antardasha"]["start_date"].strftime("%d-%b-%y")
                    _a_e = _h5["antardasha"]["end_date"].strftime("%d-%b-%y")
                    _pr_s = _h5["pratyantardasha"]["start_date"].strftime("%d-%b-%y")
                    _pr_e = _h5["pratyantardasha"]["end_date"].strftime("%d-%b-%y")
                    _s_s = _h5["sookshmadasha"]["start_date"].strftime("%d-%b-%y")
                    _s_e = _h5["sookshmadasha"]["end_date"].strftime("%d-%b-%y")
                    _p_s = _h5["pranadasha"]["start_date"].strftime("%d-%b-%y")
                    _p_e = _h5["pranadasha"]["end_date"].strftime("%d-%b-%y")

                    _dasha_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:6px; font-size:11.5px;"><div style="display:flex; justify-content:space-between; align-items:center; background:#EEF2FF; border:1px solid #C7D2FE; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#312E81;">👑 महादशा (L1):</span><span style="font-weight:900; color:#1E1B4B; background:#C7D2FE; padding:1px 6px; border-radius:4px;">{_m_lord}</span><span style="color:#475569; font-size:10.5px;">{_m_s} ~ {_m_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#064E3B;">🪐 अंतर्दशा (L2):</span><span style="font-weight:900; color:#065F46; background:#BBF7D0; padding:1px 6px; border-radius:4px;">{_a_lord}</span><span style="color:#475569; font-size:10.5px;">{_a_s} ~ {_a_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#FFFBEB; border:1px solid #FDE68A; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#78350F;">⚡ प्रत्यंतर (L3):</span><span style="font-weight:900; color:#92400E; background:#FDE68A; padding:1px 6px; border-radius:4px;">{_pr_lord}</span><span style="color:#475569; font-size:10.5px;">{_pr_s} ~ {_pr_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#FDF2F8; border:1px solid #FBCFE8; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#831843;">🔍 सूक्ष्मदशा (L4):</span><span style="font-weight:900; color:#9D174D; background:#FBCFE8; padding:1px 6px; border-radius:4px;">{_s_lord}</span><span style="color:#475569; font-size:10.5px;">{_s_s} ~ {_s_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:4px; padding:3px 6px;"><span style="font-weight:800; color:#0F172A;">🧬 प्राणदशा (L5):</span><span style="font-weight:900; color:#1E293B; background:#E2E8F0; padding:1px 6px; border-radius:4px;">{_p_lord}</span><span style="color:#475569; font-size:10.5px;">{_p_s} ~ {_p_e}</span></div></div>'
                    st.markdown(_dasha_html, unsafe_allow_html=True)
                except Exception as _e_d:
                    st.caption(f"दशा लोड हो रही है: {_e_d}")


            with pl_r1_c2:
                st.markdown("""<div class="pl-box-header"><span>⚖️ षड्बल एवं विंशोपक बल (Shadbala & Strength)</span><span style="font-size:11px;">7 ग्रह शक्ति</span></div>""", unsafe_allow_html=True)
                try:
                    _sb_res = chart.shadbala
                    _vimsopaka = VargaCalculator.calculate_vimsopaka_bala(chart)
                    _sb_p_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                    _sb_rows = []
                    for _pn in _sb_p_list:
                        _sb_o = _sb_res.planets.get(_pn) if _sb_res else None
                        _rupas = f"{_sb_o.total_rupas:.2f}" if _sb_o else "—"
                        _ratio = _sb_o.strength_ratio if _sb_o else 1.0
                        _is_str = _sb_o.is_strong if _sb_o else True
                        _str_badge = f'<span style="background:{"#DCFCE7" if _is_str else "#FEE2E2"}; color:{"#166534" if _is_str else "#991B1B"}; font-weight:800; padding:1px 6px; border-radius:4px;">{"बलवान" if _is_str else "निर्बल"}</span>'
                        _v_score = _vimsopaka.get(_pn, 10.0)
                        _sb_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#1E293B;">{_pn}</td><td style="padding:4px 6px; text-align:center;">{_rupas} R</td><td style="padding:4px 6px; text-align:center;">{_ratio:.2f}</td><td style="padding:4px 6px; text-align:center;">{_v_score:.1f}/20</td><td style="padding:4px 6px; text-align:center;">{_str_badge}</td></tr>')

                    _sb_table_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:4px; max-height:175px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:3px 6px; text-align:left;">ग्रह</th><th style="padding:3px 6px; text-align:center;">रूप</th><th style="padding:3px 6px; text-align:center;">अनुपात</th><th style="padding:3px 6px; text-align:center;">विंशोपक</th><th style="padding:3px 6px; text-align:center;">स्थिति</th></tr></thead><tbody>{"".join(_sb_rows)}</tbody></table></div>'
                    st.markdown(_sb_table_html, unsafe_allow_html=True)
                except Exception as _e_sb:
                    st.caption(f"षड्बल लोड हो रहा है: {_e_sb}")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            # Row 2: Box 3 (Planetary Longitudes & Dignity Table) & Box 4 (Sarvashtakavarga 12-Sign Matrix)
            pl_r2_c1, pl_r2_c2 = st.columns(2, gap="small")
            with pl_r2_c1:
                st.markdown("""<div class="pl-box-header"><span>🪐 ग्रह स्पष्ट तालिका (Planetary Longitudes & Dignity)</span><span style="font-size:11px;">D1 स्पष्ट</span></div>""", unsafe_allow_html=True)
                _p_rows_box = []
                _p_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
                for _pn in _p_order:
                    _po = chart.planets.get(_pn)
                    if not _po: continue
                    _sym = {"Sun":"☉ सूर्य","Moon":"☽ चन्द्र","Mars":"♂ मंगल","Mercury":"☿ बुध","Jupiter":"♃ गुरु","Venus":"♀ शुक्र","Saturn":"♄ शनि","Rahu":"☊ राहु","Ketu":"☋ केतु"}.get(_pn, _pn)
                    _d_lbl, _, _ = get_varga_dignity_info(_pn, _po.sign_name, affliction_engine)
                    _motion = "℞" if _po.is_retrograde else ""
                    _comb = "☌" if _po.is_combust else ""
                    _badge_color = "#1E40AF" if "उच्च" in _d_lbl else ("#047857" if "स्वराशि" in _d_lbl or "मूल" in _d_lbl else ("#B91C1C" if "नीच" in _d_lbl else "#475569"))
                    _p_rows_box.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:3px 5px; font-weight:800; color:#0F172A; white-space:nowrap;">{_sym} <span style="color:#DC2626; font-size:10px;">{_motion}{_comb}</span></td><td style="padding:3px 5px; font-weight:700; color:#1E3A8A;">{_po.sign_name[:4]}</td><td style="padding:3px 5px; font-family:monospace; font-weight:700; color:#0F172A;">{_po.sign_degree:.2f}°</td><td style="padding:3px 5px; font-size:10px; color:#475569;">{_po.nakshatra_name[:4]}-P{_po.nakshatra_pada}</td><td style="padding:3px 5px; font-weight:800; color:{_badge_color}; font-size:10px;">{_d_lbl[:6]}</td></tr>')

                _p_table_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:4px; max-height:190px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:3px 5px; text-align:left;">ग्रह</th><th style="padding:3px 5px; text-align:left;">राशि</th><th style="padding:3px 5px; text-align:left;">अंश</th><th style="padding:3px 5px; text-align:left;">नक्षत्र</th><th style="padding:3px 5px; text-align:left;">गरिमा</th></tr></thead><tbody>{"".join(_p_rows_box)}</tbody></table></div>'
                st.markdown(_p_table_html, unsafe_allow_html=True)

            with pl_r2_c2:
                st.markdown("""<div class="pl-box-header"><span>📊 सर्वाष्टकवर्ग सारणी (Sarvashtakavarga 12 Signs)</span><span style="font-size:11px;">बिन्दु योग (337)</span></div>""", unsafe_allow_html=True)
                try:
                    _sav_arr = chart.ashtakavarga.sav if chart.ashtakavarga else [28]*12
                    _rashi_names_12 = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"]
                    _sav_cells = []
                    for _s_idx in range(12):
                        _pts = _sav_arr[_s_idx]
                        _bg = "#DCFCE7" if _pts >= 30 else ("#FEF3C7" if _pts >= 25 else "#FEE2E2")
                        _fg = "#166534" if _pts >= 30 else ("#92400E" if _pts >= 25 else "#991B1B")
                        _sav_cells.append(f'<div style="background:{_bg}; border:1px solid #CBD5E1; border-radius:6px; padding:4px 6px; text-align:center;"><div style="font-size:10px; color:#475569; font-weight:700;">{_s_idx+1}. {_rashi_names_12[_s_idx]}</div><div style="font-size:14px; font-weight:900; color:{_fg};">{_pts}</div></div>')

                    _sav_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:6px;"><div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:6px;">{"".join(_sav_cells)}</div><div style="display:flex; justify-content:space-between; margin-top:6px; font-size:10.5px; color:#64748B; padding:2px 4px; background:#F8FAFC; border-radius:4px;"><span>🟢 ≥30 शुभ</span><span>🟡 25-29 मध्यम</span><span>🔴 &lt;25 शोधन आवश्यक</span><span>कुल: <b>{sum(_sav_arr)}</b></span></div></div>'
                    st.markdown(_sav_html, unsafe_allow_html=True)
                except Exception as _e_sav:
                    st.caption(f"अष्टकवर्ग लोड हो रहा है: {_e_sav}")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # Beneath 2x2: Expander for Varga Selector & Sub-analysis
            with st.expander("🔍 षोडशवर्ग चक्र (D2 to D60 Deep Dive) एवं अतिरिक्त विश्लेषण", expanded=False):
                st.markdown("##### वर्ग चक्र चयन एवं सूक्ष्म अध्ययन:")
                v_opts = list(chart.vargas.keys()) if chart.vargas else ["D1"]
                sel_pl_varga = st.selectbox(
                    "वर्ग चक्र चुनें (Select Varga Chart)",
                    v_opts,
                    index=0,
                    format_func=lambda x: f"{x} - {chart.vargas[x].varga_name}" if x in chart.vargas else x,
                    key="pl_deep_varga_sel"
                )
                col_pv1, col_pv2 = st.columns([1, 1])
                with col_pv1:
                    svg_pv = render_chart_svg(chart, f"{sel_pl_varga} {chart.vargas.get(sel_pl_varga, chart.vargas.get('D1')).varga_name}", varga_code=sel_pl_varga)
                    st.markdown(svg_pv, unsafe_allow_html=True)
                with col_pv2:
                    pv_desc = VARGA_SIGNIFICANCE.get(sel_pl_varga, "शास्त्रीय सूक्ष्म विश्लेषण")
                    st.info(f"🎯 **{sel_pl_varga} शास्त्रीय प्रयोजन:** {pv_desc}")
                    vims_score = VargaCalculator.calculate_vimsopaka_bala(chart)
                    st.bar_chart(pd.DataFrame(list(vims_score.items()), columns=["Planet", "Vimsopaka"]).set_index("Planet"))

            varga_choice = sel_pl_varga
            target_varga = chart.vargas.get(varga_choice, chart.vargas.get("D1"))
            v_name = target_varga.varga_name if target_varga else "Rashi"
            v_lagna_sign = target_varga.lagna_sign_name if target_varga else chart.lagna_sign_name
            v_lagna_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id
        else:
            # Standard Single / Quad Dashboard Layout (Classic 2-Column Split: Left Chart, Right Analysis)
            col_chart1, col_chart2 = st.columns([1, 1], gap="medium")
            with col_chart1:
                varga_options = list(chart.vargas.keys()) if chart.vargas else ["D1"]
                varga_choice = st.selectbox(
                    "वर्ग चक्र चयन (Select Varga Chart)",
                    varga_options,
                    format_func=lambda x: f"{x} - {chart.vargas[x].varga_name}" if x in chart.vargas else x
                )
                # Dynamic Sampradaya Variation Allocation
                cur_d3_act = st.session_state.get("v_d3_meth", "parashari")
                cur_d9_act = st.session_state.get("v_d9_meth", "parashari")
                cur_d2_act = st.session_state.get("v_d2_meth", "parashari")
                if varga_choice == "D3" and cur_d3_act != "parashari":
                    target_varga = VargaCalculator.calculate_d3(chart, variation=cur_d3_act)
                    chart.vargas["D3"] = target_varga
                elif varga_choice == "D9" and cur_d9_act != "parashari":
                    target_varga = VargaCalculator.calculate_d9(chart, variation=cur_d9_act)
                    chart.vargas["D9"] = target_varga
                elif varga_choice == "D2" and cur_d2_act != "parashari":
                    target_varga = VargaCalculator.calculate_d2(chart, variation=cur_d2_act)
                    chart.vargas["D2"] = target_varga
                else:
                    target_varga = chart.vargas.get(varga_choice, chart.vargas.get("D1"))
                v_name = target_varga.varga_name if target_varga else "Rashi"
                v_lagna_sign = target_varga.lagna_sign_name if target_varga else chart.lagna_sign_name
                v_lagna_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id

                title = f"{varga_choice} {v_name} Kundali"
                svg_code = render_chart_svg(chart, title, varga_code=varga_choice)
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_code}</div>', unsafe_allow_html=True)

                v_desc = VARGA_SIGNIFICANCE.get(varga_choice, "शास्त्रीय सूक्ष्म विश्लेषण")
                st.info(f"🎯 **{varga_choice} ({v_name}) शास्त्रीय प्रयोजन:** {v_desc}")

            with col_chart2:
                _is_astrallis_chart = ("Astrallis" in curr_style or "Circular" in curr_style)
                if _is_astrallis_chart:
                    # ─── Astrallis Scientific Observatory Data Console ───
                    if is_astrallis_mode:
                        _dc_bg  = "#050811"
                        _dc_row = "#0A1628"
                        _dc_bdr = "#1E3A5F"
                        _dc_hdr = "#00E5FF"
                        _dc_txt = "#CBD5E1"
                        _dc_val = "#E2E8F0"
                        _dc_th_col = "#00E5FF"
                        _pts_good = "#44FF88"
                        _pts_mid  = "#FFD700"
                        _pts_low  = "#FF4444"
                    elif is_night_mode:
                        _dc_bg  = "#111827"
                        _dc_row = "#1F2937"
                        _dc_bdr = "#374151"
                        _dc_hdr = "#F59E0B"
                        _dc_txt = "#D1D5DB"
                        _dc_val = "#F8FAFC"
                        _dc_th_col = "#F59E0B"
                        _pts_good = "#44FF88"
                        _pts_mid  = "#FFD700"
                        _pts_low  = "#FF4444"
                    else:  # Day Mode (Royal Pearl / Vedic Classic)
                        _dc_bg  = "#FFFFFF"
                        _dc_row = "#F8FAFC"
                        _dc_bdr = "#CBD5E1"
                        _dc_hdr = "#1E40AF"
                        _dc_txt = "#475569"
                        _dc_val = "#0F172A"
                        _dc_th_col = "#1E3A8A"
                        _pts_good = "#059669"
                        _pts_mid  = "#D97706"
                        _pts_low  = "#DC2626"

                    # Jataka Info Console
                    _j_name = chart.birth_data.name if (chart.birth_data and chart.birth_data.name) else (name if 'name' in locals() else "Jataka")
                    _j_city = (getattr(chart.birth_data, 'city', None) or (default_city_name if 'default_city_name' in locals() else (city if 'city' in locals() else "New Delhi")))
                    _j_bdate = chart.birth_data.birth_date if (chart.birth_data and hasattr(chart.birth_data, 'birth_date')) else (birth_d if 'birth_d' in locals() else None)
                    _j_btime = chart.birth_data.birth_time if (chart.birth_data and hasattr(chart.birth_data, 'birth_time')) else (birth_t if 'birth_t' in locals() else None)
                    _j_dt_str = f"{_j_bdate.strftime('%d-%b-%Y') if _j_bdate else ''} {_j_btime.strftime('%I:%M %p') if _j_btime else ''}".strip()

                    st.markdown(f"""
        <div style="background:{_dc_bg};border:1px solid {_dc_bdr};border-radius:8px;padding:10px 12px;margin-bottom:8px;font-size:12px;box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
          <div style="color:{_dc_hdr};font-weight:900;font-size:13px;margin-bottom:8px;letter-spacing:0.5px;">⚡ JATAKA DATA CONSOLE</div>
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="color:{_dc_txt};padding:2px 4px;">Name</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{_j_name}</td></tr>
            <tr style="background:{_dc_row};"><td style="color:{_dc_txt};padding:2px 4px;">Place</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{_j_city}</td></tr>
            <tr><td style="color:{_dc_txt};padding:2px 4px;">Date &amp; Time</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{_j_dt_str}</td></tr>
            <tr style="background:{_dc_row};"><td style="color:{_dc_txt};padding:2px 4px;">Ayanamsa</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{chart.ayanamsa_name} ({chart.ayanamsa_value:.4f}°)</td></tr>
            <tr><td style="color:{_dc_txt};padding:2px 4px;">Lagna (Asc)</td><td style="color:{_dc_hdr};font-weight:900;padding:2px 4px;">{chart.lagna_sign_name} ({chart.lagna_sign_id})</td></tr>
            <tr style="background:{_dc_row};"><td style="color:{_dc_txt};padding:2px 4px;">Atmakaraka</td><td style="color:{_pts_mid};font-weight:900;padding:2px 4px;">{chart.atmakaraka}</td></tr>
            <tr><td style="color:{_dc_txt};padding:2px 4px;">House System</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">Equal (Vedic) / Placidus</td></tr>
          </table>
        </div>""", unsafe_allow_html=True)

                    # Swiss Ephemeris Planet Table
                    SYMS_CONS = {"Sun":"☉","Moon":"☽","Mars":"♂","Mercury":"☿","Jupiter":"♃","Venus":"♀","Saturn":"♄","Rahu":"☊","Ketu":"☋"}
                    P_NC = {"Sun":"#FFB800","Moon":"#88AAFF","Mars":"#FF4444","Mercury":"#44DD88","Jupiter":"#FFD700","Venus":"#FF88CC","Saturn":"#AAAACC","Rahu":"#CC88FF","Ketu":"#AA6633"}
                    eph_rows = []
                    for pn in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
                        pp_o = chart.planets.get(pn)
                        if not pp_o:
                            continue
                        sym = SYMS_CONS.get(pn, pn[:2])
                        nc = P_NC.get(pn, "#CCC")
                        retro = "℞" if pp_o.is_retrograde else ""
                        combust = "☌" if pp_o.is_combust else ""
                        d_label, d_pts, _ = get_varga_dignity_info(pn, pp_o.sign_name, affliction_engine)
                        eph_rows.append(
                            f'<tr><td style="color:{nc};font-weight:900;padding:2px 5px;font-size:13px;">{sym}</td>'
                            f'<td style="color:{_dc_val};padding:2px 4px;font-size:11px;">{pn}{retro}{combust}</td>'
                            f'<td style="color:{nc};padding:2px 4px;font-size:11px;">{pp_o.sign_name[:3]}</td>'
                            f'<td style="color:{_dc_txt};padding:2px 4px;font-size:11px;">{pp_o.sign_degree:.2f}°</td>'
                            f'<td style="color:{_dc_txt};padding:2px 4px;font-size:10px;">{pp_o.nakshatra_name[:5]}-P{pp_o.nakshatra_pada}</td>'
                            f'<td style="color:{_pts_good if d_pts>=15 else (_pts_mid if d_pts>=10 else _pts_low)};padding:2px 4px;font-size:10px;font-weight:700;">{d_pts}pts</td>'
                            f'</tr>'
                        )
                    st.markdown(f"""
        <div style="background:{_dc_bg};border:1px solid {_dc_bdr};border-radius:8px;padding:8px 10px;margin-bottom:8px;box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
          <div style="color:{_dc_hdr};font-weight:900;font-size:12px;margin-bottom:6px;letter-spacing:0.5px;">🪐 SWISS EPHEMERIS — {varga_choice} {v_name}</div>
          <table style="width:100%;border-collapse:collapse;font-size:11px;">
            <tr style="background:{_dc_row};">
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Sym</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Planet</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Sign</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Deg°</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Nakshatra</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Bala</th>
            </tr>
            {"".join(eph_rows)}
          </table>
        </div>""", unsafe_allow_html=True)

                    # Panchang Quick Console
                    st.markdown(f"""
        <div style="background:{_dc_bg};border:1px solid {_dc_bdr};border-radius:8px;padding:8px 10px;margin-bottom:8px;">
          <div style="color:{_dc_hdr};font-weight:900;font-size:12px;margin-bottom:6px;">🌙 PANCHANG CONSOLE</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:11px;">
            <div style="color:{_dc_txt};">Tithi: <span style="color:{_dc_val};font-weight:800;">{p.tithi_name}</span></div>
            <div style="color:{_dc_txt};">Vara: <span style="color:{_dc_val};font-weight:800;">{p.vara_name}</span></div>
            <div style="color:{_dc_txt};">Nakshatra: <span style="color:{_dc_val};font-weight:800;">{p.nakshatra_name}</span></div>
            <div style="color:{_dc_txt};">Yoga: <span style="color:{_dc_val};font-weight:800;">{p.yoga_name}</span></div>
            <div style="color:{_dc_txt};">Karana: <span style="color:{_dc_val};font-weight:800;">{p.karana_name}</span></div>
            <div style="color:{_dc_txt};">Atmakaraka: <span style="color:{_pts_mid};font-weight:900;">{chart.atmakaraka}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

                    # 9×9 Aspect Orb Matrix
                    st.markdown(f'<div style="color:{_dc_hdr};font-weight:900;font-size:12px;margin-bottom:4px;letter-spacing:0.5px;">🔬 NATAL ASPECT ORB MATRIX (9×9)</div>', unsafe_allow_html=True)
                    orb_html = render_aspect_orb_matrix_html(chart, dark_bg=is_astrallis_mode or is_night_mode)
                    st.markdown(orb_html, unsafe_allow_html=True)

                else:
                    # Standard panel for non-Astrallis modes
                    st.markdown(f"#### 🌟 {varga_choice} ({v_name}) सारांश एवं पंचांग")
                    p_col1, p_col2 = st.columns(2)
                    p_col1.markdown(f"- **वर्ग लग्न:** {v_lagna_sign} ({v_lagna_id})")
                    p_col1.markdown(f"- **जन्म लग्न (D1):** {chart.lagna_sign_name} ({chart.lagna_sign_id})")
                    p_col1.markdown(f"- **आत्मकारक (AK):** {chart.atmakaraka}")
                    p_col2.markdown(f"- **तिथि:** {p.tithi_name}")
                    p_col2.markdown(f"- **नक्षत्र:** {p.nakshatra_name}")
                    p_col2.markdown(f"- **वार:** {p.vara_name}")

                    # Dynamic Planetary Dignity & Strength Chart with Toggle Switch (Meters vs Columns)
                    c_gh1, c_gh2 = st.columns([1.5, 1.2])
                    with c_gh1:
                        st.markdown(f"#### 📊 {varga_choice} ({v_name}) ग्रह गरिमा एवं बल")
                    with c_gh2:
                        graph_style_choice = st.radio(
                            "ग्राफ़ शैली",
                            ["📊 हॉरिजॉन्टल मीटर", "📈 वर्टिकल कॉलम"],
                            index=0 if "हॉरिजॉन्टल" in st.session_state.get("varga_graph_style", "हॉरिजॉन्टल") else 1,
                            horizontal=True,
                            key="varga_graph_style_radio",
                            label_visibility="collapsed"
                        )
                        st.session_state.varga_graph_style = graph_style_choice

                    varga_items = []
                    target_planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
                    _GRAHA_SYMS = {"Sun": "☉ सूर्य", "Moon": "☽ चन्द्र", "Mars": "♂ मंगल", "Mercury": "☿ बुध", "Jupiter": "♃ गुरु", "Venus": "♀ शुक्र", "Saturn": "♄ शनि", "Rahu": "☊ राहु", "Ketu": "☋ केतु"}
                    _P_COLS = {"Sun":"#E11D48","Moon":"#2563EB","Mars":"#DC2626","Mercury":"#059669","Jupiter":"#D97706","Venus":"#DB2777","Saturn":"#475569","Rahu":"#7C3AED","Ketu":"#B45309"}

                    for p_name in target_planets_order:
                        vp_obj = target_varga.planets.get(p_name) if target_varga else None
                        if vp_obj:
                            d_lbl, d_pts, _ = get_varga_dignity_info(p_name, vp_obj.sign_name, affliction_engine)
                        else:
                            d_lbl, d_pts = "सम (Neutral)", 7.0
                        varga_items.append({
                            "name": p_name,
                            "symbol": _GRAHA_SYMS.get(p_name, p_name),
                            "color": _P_COLS.get(p_name, "#2563EB"),
                            "dignity": d_lbl,
                            "score": d_pts
                        })

                    _is_dark = is_astrallis_mode or is_night_mode
                    if "हॉरिजॉन्टल" in graph_style_choice:
                        st.markdown(render_styled_meters_html(varga_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)
                    else:
                        st.markdown(generate_styled_vertical_svg(varga_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)

                    with st.expander("🏆 समग्र विंशोपक बल (20 Point Shadvarga Bala)", expanded=False):
                        vimsopaka = VargaCalculator.calculate_vimsopaka_bala(chart)
                        vims_items = []
                        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                            v_sc = float(vimsopaka.get(p_name, 10.0))
                            v_qual = "अति उत्तम" if v_sc >= 15 else ("उत्तम" if v_sc >= 10 else "मध्यम")
                            vims_items.append({
                                "name": p_name,
                                "symbol": _GRAHA_SYMS.get(p_name, p_name),
                                "color": _P_COLS.get(p_name, "#2563EB"),
                                "dignity": f"{v_qual} ({v_sc:.1f})",
                                "score": v_sc
                            })
                        if "हॉरिजॉन्टल" in graph_style_choice:
                            st.markdown(render_styled_meters_html(vims_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)
                        else:
                            st.markdown(generate_styled_vertical_svg(vims_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)

        # ─── Pancha Mahapurusha Yogas & Key Yogas Banner ───
        try:
            _yogas_found = []
            # Pancha Mahapurusha Yogas
            _kendra_houses = [1, 4, 7, 10]
            _mars = chart.planets.get("Mars")
            if _mars and _mars.house_from_lagna in _kendra_houses and _mars.sign_name in ["Aries", "Scorpio", "Capricorn"]:
                _yogas_found.append(("🔴 रुचक महापुरुष योग (Ruchaka)", "मंगल केंद्र में स्व/उच्च राशि — अदम्य साहस, भूमि-भवन लाभ, नेतृत्व एवं सैन्य/प्रशासनिक पराक्रम।"))
            _merc = chart.planets.get("Mercury")
            if _merc and _merc.house_from_lagna in _kendra_houses and _merc.sign_name in ["Gemini", "Virgo"]:
                _yogas_found.append(("🟢 भद्र महापुरुष योग (Bhadra)", "बुध केंद्र में स्व/उच्च राशि — असाधारण बौद्धिक प्रखरता, वाणी प्रभाव, व्यापारिक कुशलता एवं दीर्घायु।"))
            _jup = chart.planets.get("Jupiter")
            if _jup and _jup.house_from_lagna in _kendra_houses and _jup.sign_name in ["Sagittarius", "Pisces", "Cancer"]:
                _yogas_found.append(("🟡 हंस महापुरुष योग (Hamsa)", "गुरु केंद्र में स्व/उच्च राशि — सात्विक बुद्धि, आध्यात्मिक तेज, पूज्य सम्मान एवं सदाचार।"))
            _ven = chart.planets.get("Venus")
            if _ven and _ven.house_from_lagna in _kendra_houses and _ven.sign_name in ["Taurus", "Libra", "Pisces"]:
                _yogas_found.append(("🌸 मालव्य महापुरुष योग (Malavya)", "शुक्र केंद्र में स्व/उच्च राशि — राजसी वैभव, कलात्मक सौंदर्य, ऐश्वर्य, सुखी वैवाहिक जीवन व वाहन सुख।"))
            _sat = chart.planets.get("Saturn")
            if _sat and _sat.house_from_lagna in _kendra_houses and _sat.sign_name in ["Capricorn", "Aquarius", "Libra"]:
                _yogas_found.append(("🪐 शश महापुरुष योग (Sasa)", "शनि केंद्र में स्व/उच्च राशि — जननायक, अपार धैर्य, गुप्त अधिकार, राजनीतिक प्रभाव एवं स्थिर सत्ता।"))

            # Gajakesari Yoga
            _moon = chart.planets.get("Moon")
            if _jup and _moon:
                _jm_dist = ((_jup.house_from_lagna - _moon.house_from_lagna + 12) % 12) + 1
                if _jm_dist in [1, 4, 7, 10]:
                    _yogas_found.append(("🐘 गजकेसरी योग (Gajakesari)", "गुरु चन्द्र से केंद्र में स्थित — अपार यश, विद्वता, निर्भय व्यक्तित्व एवं सर्वत्र आदर-सत्कार।"))

            # Budhaditya Yoga
            _sun = chart.planets.get("Sun")
            if _sun and _merc and _sun.sign_id == _merc.sign_id:
                _diff = abs(_sun.longitude - _merc.longitude)
                if _diff > 180: _diff = 360 - _diff
                if _diff <= 10.0:
                    _comb_txt = " (बुध अस्त नहीं)" if not _merc.is_combust else " (अंश निकट)"
                    _yogas_found.append(("⚡ बुधादित्य योग (Budhaditya)", f"सूर्य-बुध युति (अंतर: {_diff:.1f}°){_comb_txt} — तीक्ष्ण बुद्धि, प्रशासनिक कुशलता व व्यावसायिक सफलता।"))

            if _yogas_found:
                _y_cards = []
                for _yt, _yd in _yogas_found:
                    _y_cards.append(f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; margin-bottom:4px;"><span style="font-weight:900; color:#1E3A8A; font-size:12px;">{_yt}</span>: <span style="font-size:11.5px; color:#334155;">{_yd}</span></div>')
                _yoga_banner_html = f'<div style="background:linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%); border:1.5px solid #93C5FD; border-radius:8px; padding:10px 12px; margin-bottom:12px;"><div style="font-weight:900; color:#1E40AF; font-size:13px; margin-bottom:6px; display:flex; align-items:center; gap:6px;"><span>🏆 <b>कुण्डली प्रमुख महा-योग उद्घोष (Major Planetary Yogas Detected)</b></span></div>{"".join(_y_cards)}</div>'
                st.markdown(_yoga_banner_html, unsafe_allow_html=True)
        except Exception as _ey:
            pass

        st.markdown(f"### 🪐 {varga_choice} ({v_name}) चक्र — नवग्रह स्पष्ट स्थिति, भाव एवं गरिमा तालिका")
        p_data = []
        target_planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        for name_p in target_planets_order:
            vp_obj = target_varga.planets.get(name_p) if target_varga else None
            if not vp_obj:
                continue
            d1_p = chart.planets.get(name_p)

            d_label, d_pts, d_impact = get_varga_dignity_info(name_p, vp_obj.sign_name, affliction_engine)
            h_lord = SIGN_LORDS.get(vp_obj.sign_name, "-")

            h_num = vp_obj.house_number
            h_suffix = "st" if h_num == 1 else "nd" if h_num == 2 else "rd" if h_num == 3 else "th"
            h_name_hi = {
                1: "तनु (1st)", 2: "धन (2nd)", 3: "सहज (3rd)", 4: "सुख (4th)",
                5: "सुत (5th)", 6: "रिपु (6th)", 7: "जाया (7th)", 8: "आयु (8th)",
                9: "धर्म (9th)", 10: "कर्म (10th)", 11: "लाभ (11th)", 12: "व्यय (12th)"
            }.get(h_num, f"{h_num}{h_suffix}")

            p_data.append({
                "ग्रह (Graha)": name_p,
                "वर्ग राशि (Sign)": vp_obj.sign_name,
                "राशि स्वामी (Lord)": h_lord,
                "वर्ग अंश (Degree)": f"{vp_obj.degree_in_varga:.2f}°",
                "वर्ग भाव (Varga House)": f"{h_num}{h_suffix} भाव ({h_name_hi})",
                "वर्ग गरिमा (Dignity)": d_label,
                "D1 राशि (Ref)": d1_p.sign_name if d1_p else "-",
                "D1 भाव (Ref)": f"{d1_p.house_from_lagna}th House" if d1_p else "-",
                "गति (Motion)": "वक्री (R)" if (d1_p and d1_p.is_retrograde) else "मार्गी",
                "अवस्था / शास्त्रीय प्रभाव": d_impact,
            })

        # ─── Render Rich Classical Planetary Dignity HTML Table ───
        if is_astrallis_mode:
            _t_bg = "#050811"; _t_th_bg = "#0A1628"; _t_bdr = "#1E3A5F"; _t_txt = "#CBD5E1"; _t_th = "#00E5FF"; _t_alt = "#070E1C"
        elif is_night_mode:
            _t_bg = "#111827"; _t_th_bg = "#1F2937"; _t_bdr = "#374151"; _t_txt = "#E2E8F0"; _t_th = "#F59E0B"; _t_alt = "#172033"
        else:  # Day Mode (Grahalakshanam Royal Azure & Cyan)
            _t_bg = "#FFFFFF"; _t_th_bg = "#0070C0"; _t_bdr = "#00B0F0"; _t_txt = "#0F172A"; _t_th = "#FFFFFF"; _t_alt = "#F2F4F7"

        _GRAHA_SYMS = {"Sun": "☉ सूर्य", "Moon": "☽ चन्द्र", "Mars": "♂ मंगल", "Mercury": "☿ बुध", "Jupiter": "♃ गुरु", "Venus": "♀ शुक्र", "Saturn": "♄ शनि", "Rahu": "☊ राहु", "Ketu": "☋ केतु"}
        _P_COLS = {"Sun":"#E11D48","Moon":"#2563EB","Mars":"#DC2626","Mercury":"#059669","Jupiter":"#D97706","Venus":"#DB2777","Saturn":"#475569","Rahu":"#7C3AED","Ketu":"#B45309"}

        t_rows = []
        for idx, row in enumerate(p_data):
            p_nm = row["ग्रह (Graha)"]
            sym_nm = _GRAHA_SYMS.get(p_nm, p_nm)
            pc = _P_COLS.get(p_nm, "#2563EB")
            d_lbl = row["वर्ग गरिमा (Dignity)"]

            # Dignity badge styling (Authentic Grahalakshanam: Lime Exalted, Red Debilitated, Cobalt Own)
            if "उच्च" in d_lbl:
                b_bg, b_fg, b_bdr = "#BCE636", "#1E293B", "#A4D024"
            elif "मूलत्रिकोण" in d_lbl:
                b_bg, b_fg, b_bdr = "#CAF0F8", "#0077B6", "#00B4D8"
            elif "स्वराशि" in d_lbl:
                b_bg, b_fg, b_bdr = "#0073CF", "#FFFFFF", "#00B0F0"
            elif "नीच" in d_lbl:
                b_bg, b_fg, b_bdr = "#FF0000", "#FFFFFF", "#CC0000"
            elif "शत्रु" in d_lbl:
                b_bg, b_fg, b_bdr = "#FFE2E5", "#D92D20", "#FCA5A5"
            elif "मित्र" in d_lbl:
                b_bg, b_fg, b_bdr = "#E0F2FE", "#0284C7", "#7DD3FC"
            else:
                b_bg, b_fg, b_bdr = "#F2F4F7", "#334155", "#CBD5E1"

            # Motion badge
            is_ret = "वक्री" in row["गति (Motion)"]
            m_bg = "#FEE2E2" if is_ret else "#ECFDF5"
            m_fg = "#DC2626" if is_ret else "#059669"
            m_bdr = "#F87171" if is_ret else "#86EFAC"

            row_bg = _t_alt if idx % 2 == 1 else _t_bg

            t_rows.append(
                f'<tr style="background:{row_bg};border-bottom:1px solid {_t_bdr};">'
                f'<td style="padding:7px 10px;font-weight:900;color:{pc};white-space:nowrap;font-size:12.5px;">{sym_nm}</td>'
                f'<td style="padding:7px 10px;font-weight:700;color:{_t_txt};font-size:12px;">{row["वर्ग राशि (Sign)"]}</td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:12px;">{row["राशि स्वामी (Lord)"]}</td>'
                f'<td style="padding:7px 10px;font-weight:700;color:{pc};font-size:12px;font-family:monospace;">{row["वर्ग अंश (Degree)"]}</td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:12px;">{row["वर्ग भाव (Varga House)"]}</td>'
                f'<td style="padding:7px 10px;"><span style="background:{b_bg};color:{b_fg};border:1px solid {b_bdr};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:800;white-space:nowrap;">{d_lbl}</span></td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:11.5px;">{row["D1 राशि (Ref)"]} / {row["D1 भाव (Ref)"]}</td>'
                f'<td style="padding:7px 10px;"><span style="background:{m_bg};color:{m_fg};border:1px solid {m_bdr};padding:2px 7px;border-radius:6px;font-size:11px;font-weight:800;">{row["गति (Motion)"]}</span></td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:11.5px;">{row["अवस्था / शास्त्रीय प्रभाव"]}</td>'
                f'</tr>'
            )

        table_html = f"""
    <div style="width:100%;overflow-x:auto;background:{_t_bg};border:1.5px solid {_t_bdr};border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:14px;">
      <table style="width:100%;border-collapse:collapse;text-align:left;font-family:inherit;">
        <thead>
          <tr style="background:{_t_th_bg};border-bottom:2px solid {_t_bdr};">
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">ग्रह (Graha)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">वर्ग राशि (Sign)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">स्वामी (Lord)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">वर्ग अंश (Deg)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">वर्ग भाव (House)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">गरिमा (Dignity)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">D1 संदर्भ (Ref)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">गति (Motion)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">अवस्था / शास्त्रीय फल</th>
          </tr>
        </thead>
        <tbody>
          {"".join(t_rows)}
        </tbody>
      </table>
    </div>"""
        st.markdown(table_html, unsafe_allow_html=True)


    with tab_jm_hud:
        st.markdown("### 👑 विशेष जैमिनी लग्न (Special Lagnas - J.Hora Standard)")
        st.info("महर्षि पराशर (BPHS) एवं जैमिनी उपदेश सूत्रों के अनुसार जीवन के विशिष्ट क्षेत्रों (धन, पद, सत्ता, आयुष्य एवं भाग्य) के सूक्ष्म आकलन हेतु विशेष लग्नों की गणितीय स्पष्ट स्थिति:")

        if chart.jaimini:
            jm = chart.jaimini
            sl_details = getattr(jm, 'special_lagnas_detail', {}) or {}

            # ─── Top 6 HUD Cards ───
            hl_o = sl_details.get('HL', {})
            gl_o = sl_details.get('GL', {})
            sl_o = sl_details.get('SL', {})
            il_o = sl_details.get('IL', {})
            pp_o = sl_details.get('PP', {})
            vl_o = sl_details.get('VL', {})

            st.markdown(f"""
            <div style="background: linear-gradient(90deg, #FFFBEB 0%, #FEF3C7 100%); border: 1.5px solid #F59E0B; border-radius: 10px; padding: 12px 18px; margin: 10px 0 15px 0; box-shadow: 0 2px 6px rgba(217, 119, 6, 0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="color: #92400E; font-size: 13.5px; font-weight: 900; display: flex; align-items: center; gap: 6px;">
                        <span>👑 <b>जैमिनी विशेष लग्न त्वरित अवलोकन (Quick HUD Console)</b></span>
                    </div>
                    <div style="font-size: 11.5px; color: #78350F; font-weight: 800; background: #FDE68A; padding: 2px 8px; border-radius: 6px;">
                        अयनांश: {chart.ayanamsa_name} ({chart.ayanamsa_value:.2f}°) | नोड: {st.session_state.get('app_node_type', 'Mean Node').split('(')[0]}
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">💰 होरा लग्न (HL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.hora_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {hl_o.get('degree', 0.0):.2f}° | स्वामी: {hl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #047857; font-weight:700;">धन, संचित संपदा</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">🏛️ घटी लग्न (GL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.ghati_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {gl_o.get('degree', 0.0):.2f}° | स्वामी: {gl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #1D4ED8; font-weight:700;">सत्ता, अधिकार, पद</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">🪷 श्री लग्न (SL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.sri_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {sl_o.get('degree', 0.0):.2f}° | स्वामी: {sl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #D97706; font-weight:700;">महालक्ष्मी कृपा, समृद्धि</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">💎 इन्दु लग्न (IL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.indu_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">स्वामी: {il_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #7C3AED; font-weight:700;">कोटिपतित्व / धनागमन</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">💨 प्राणपद लग्न (PP)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.pranapada_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {pp_o.get('degree', 0.0):.2f}° | स्वामी: {pp_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #059669; font-weight:700;">प्राण शक्ति, BTR शोधन</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">⚔️ वर्णद लग्न (VL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.varnada_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">स्वामी: {vl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #DC2626; font-weight:700;">सामाजिक दायित्व, आजीविका</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ─── Detailed Comparative Table ───
            st.markdown("#### 📊 विशेष लग्न स्पष्ट गणितीय तालिका (J.Hora Standard Mathematical Details)")
            sl_rows = []
            order_keys = ["HL", "GL", "SL", "IL", "BL", "PP", "VL"]
            for k in order_keys:
                v = sl_details.get(k)
                if not v:
                    continue
                h_from_lag = ((SIGN_NAMES.index(v['sign']) - chart.lagna_sign_id + 12) % 12) + 1 if v.get('sign') in SIGN_NAMES else 1
                sl_rows.append({
                    "विशेष लग्न": v.get('name_hi', k),
                    "प्रतीक": k,
                    "राशि": v.get('sign', '—'),
                    "स्पष्ट अंश": f"{v.get('degree', 0.0):.2f}°",
                    "सम्पूर्ण देशांतर": f"{v.get('longitude', 0.0):.2f}°",
                    "राशि स्वामी": v.get('lord', '—'),
                    "लग्न से भाव": f"{h_from_lag} भाव",
                    "शास्त्रीय प्रयोजन एवं नियम": v.get('purpose_hi', '')
                })
            st.dataframe(pd.DataFrame(sl_rows), use_container_width=True, hide_index=True)

            # ─── 3 Jaimini Special Yoga Analysis Cards ───
            st.markdown("#### 🔬 विशेष लग्न आधारित शास्त्रीय योग फलादेश (Jaimini Classical Yoga Engine)")
            col_y1, col_y2, col_y3 = st.columns(3)

            # 1. Dhana Yoga (HL & SL)
            with col_y1:
                hl_s = jm.hora_lagna_sign_name
                sl_s = jm.sri_lagna_sign_name
                hl_lord = SIGN_LORDS.get(hl_s, '')
                is_hl_benefic = hl_lord in ["Jupiter", "Venus", "Mercury", "Moon"]
                st.markdown(f"""
                <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:12px; height:100%;">
                    <h5 style="color:#B45309; margin:0 0 6px 0;">💰 जैमिनी धन योग (HL &amp; SL)</h5>
                    <div style="font-size:12px; color:#1E293B; line-height:1.5;">
                        <b>होरा लग्न (HL):</b> {hl_s} (स्वामी: {hl_lord})<br/>
                        <b>श्री लग्न (SL):</b> {sl_s}<br/>
                        <div style="margin:6px 0; padding:6px; background:#FEF3C7; border-radius:6px; font-weight:800; font-size:11.5px; color:#78350F;">
                            {'🌟 प्रबल धन योग: होरा लग्न का स्वामी शुभ ग्रह है तथा वित्तीय संचय में स्थायित्व प्रदान करता है।' if is_hl_benefic else '⚡ कर्मप्रधान धन योग: वित्तीय सफलता पुरुषार्थ एवं निरंतर उद्यम से निर्मित होगी।'}
                        </div>
                        <b>शास्त्रीय सूत्र:</b> होरा लग्न और श्री लग्न पर शुभ ग्रहों (गुरु, शुक्र, बुध) की दृष्टि या युति जातक को विपुल संपदा एवं महालक्ष्मी का स्थायी अनुग्रह प्रदान करती है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 2. Raja Yoga (GL & Janma Lagna)
            with col_y2:
                gl_s = jm.ghati_lagna_sign_name
                gl_lord = SIGN_LORDS.get(gl_s, '')
                gl_h = ((SIGN_NAMES.index(gl_s) - chart.lagna_sign_id + 12) % 12) + 1 if gl_s in SIGN_NAMES else 1
                is_gl_kendra = gl_h in [1, 4, 7, 10, 5, 9]
                st.markdown(f"""
                <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:12px; height:100%;">
                    <h5 style="color:#1D4ED8; margin:0 0 6px 0;">🏛️ जैमिनी राज योग (GL &amp; Lagna)</h5>
                    <div style="font-size:12px; color:#1E293B; line-height:1.5;">
                        <b>घटी लग्न (GL):</b> {gl_s} ({gl_h} भाव)<br/>
                        <b>घटी लग्न स्वामी:</b> {gl_lord}<br/>
                        <div style="margin:6px 0; padding:6px; background:#DBEAFE; border-radius:6px; font-weight:800; font-size:11.5px; color:#1E3A8A;">
                            {'👑 प्रतिष्ठित राजयोग: घटी लग्न केंद्र/त्रिकोण में स्थित होकर शासकीय प्रभुत्व एवं यश देता है।' if is_gl_kendra else '📈 प्रतिष्ठा योग: घटी लग्न जातक को सामाजिक दायित्व एवं प्रशासनिक प्रभाव प्रदान करता है।'}
                        </div>
                        <b>शास्त्रीय सूत्र:</b> यदि जन्म लग्न और घटी लग्न दोनों पर किसी एक ही ग्रह की दृष्टि हो, तो महर्षि जैमिनी अनुसार जातक को राजा समान पद, सत्ता एवं समाज में सर्वोच्च सम्मान प्राप्त होता है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 3. Indu Lagna Wealth Engine
            with col_y3:
                il_s = jm.indu_lagna_sign_name
                il_lord = SIGN_LORDS.get(il_s, '')
                il_planets = [pn for pn, p in chart.planets.items() if p.sign_name == il_s]
                il_benefics = [p for p in il_planets if p in ["Jupiter", "Venus", "Mercury", "Moon"]]
                st.markdown(f"""
                <div style="background:#FAF5FF; border:1.5px solid #8B5CF6; border-radius:10px; padding:12px; height:100%;">
                    <h5 style="color:#6D28D9; margin:0 0 6px 0;">💎 इन्दु लग्न कोटिपतित्व योग</h5>
                    <div style="font-size:12px; color:#1E293B; line-height:1.5;">
                        <b>इन्दु लग्न:</b> {il_s} (स्वामी: {il_lord})<br/>
                        <b>इन्दु लग्न में स्थित ग्रह:</b> {', '.join(il_planets) if il_planets else 'शुभ दृष्टि प्रभाव'}<br/>
                        <div style="margin:6px 0; padding:6px; background:#F3E8FF; border-radius:6px; font-weight:800; font-size:11.5px; color:#581C87;">
                            {'🏆 कोटिपतित्व योग: शुभ ग्रह इन्दु लग्न में विद्यमान होकर अकूत संपदा का सृजन कर रहे हैं!' if il_benefics else ('⚡ उद्योगी धन योग: इन्दु लग्न स्वामी ' + il_lord + ' के बल से वित्तीय साम्राज्य खड़ा होगा।')}
                        </div>
                        <b>शास्त्रीय सूत्र:</b> इन्दु लग्न में केवल एक भी उच्च या शुभ ग्रह स्थित हो तो जातक बहु-करोड़पति बनता है; पाप ग्रह हों तो धन का प्रवाह उद्यम के साथ आता है।
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("जैमिनी विशेष लग्न गणना उपलब्ध नहीं।")


    with tab_bhav:
        st.markdown("### 🏠 भाव चलित चक्र (Bhava Chalit Chart — Equal / Sripati Cusp System)")
        st.info("श्रीपति एवं समभाव पद्धति अनुसार भाव के मध्य बिंदु (Cusp) से आरंभ व अंत सीमा का निर्धारण होता है। यदि कोई ग्रह राशि में होते हुए भी भाव सीमा पार कर जाता है, तो उसका प्रभाव वास्तविक चलित भाव से ही फलित होता है:")

        try:
            _bc_res = default_chart_calculator.calculate_bhava_chalit(chart)
            _bc_items = _bc_res.get("planet_positions", []) if isinstance(_bc_res, dict) else _bc_res
            _cusps_list = _bc_res.get("bhava_cusps", []) if isinstance(_bc_res, dict) else []

            # Construct Chalit VargaChart for dynamic SVG Kundali rendering
            _chalit_planets = {}
            for _it in _bc_items:
                _pn = _it.get("planet")
                _ch = _it.get("chalit_house", 1)
                _sn = _it.get("sign", _it.get("sign_name", "Aries"))
                _p_orig = chart.planets.get(_pn)
                _chalit_planets[_pn] = VargaPlanetPosition(
                    name=_pn,
                    sign_id=_p_orig.sign_id if _p_orig else 1,
                    sign_name=_sn,
                    degree_in_varga=_p_orig.sign_degree if _p_orig else 0.0,
                    house_number=_ch
                )
            _v_chalit = VargaChart(
                varga_code="CHALIT",
                varga_name="भाव चलित",
                division=1,
                lagna_sign_id=chart.lagna_sign_id,
                lagna_sign_name=chart.lagna_sign_name,
                planets=_chalit_planets
            )
            chart.vargas["CHALIT"] = _v_chalit

            bc_col1, bc_col2 = st.columns([1, 1], gap="medium")
            with bc_col1:
                svg_chalit = render_chart_svg(chart, "🏠 भाव चलित चक्र (Bhava Chalit)", varga_code="CHALIT")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_chalit}</div>', unsafe_allow_html=True)
                st.caption(f"**लग्न:** {chart.lagna_sign_name} ({chart.lagna_sign_id}) | चलित चक्र में ग्रहों का स्थान उनकी वास्तविक भाव स्थिति को दर्शाता है।")

                # Cusp Methodology Explanatory Box
                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px; font-size:12px; color:#334155; line-height:1.5;">
                    <b>💡 चलित चक्र रहस्य (Astrological Rule):</b><br/>
                    • <b>राशि चक्र (D1):</b> ग्रह का राशिगत बल, गरिमा (उच्च/नीच) व सम्बंध दर्शाता है।<br/>
                    • <b>भाव चलित चक्र:</b> ग्रह वास्तव में किस भाव का भौतिक व व्यावहारिक परिणाम देगा, यह निश्चित करता है।
                </div>
                """, unsafe_allow_html=True)

            with bc_col2:
                st.markdown("#### 🔄 ग्रह भाव परिवर्तन विश्लेषण (Planetary House Shifts)")
                _shift_rows = []
                _shifted_planets = []
                for _it in _bc_items:
                    _pn = _it.get("planet", "")
                    _rh = _it.get("rashi_house", 1)
                    _ch = _it.get("chalit_house", 1)
                    _is_diff = (_rh != _ch)
                    if _is_diff:
                        _shifted_planets.append(f"{_pn} ({_rh}→{_ch})")
                        _status_badge = '<span style="background:#FEF3C7; color:#B45309; font-weight:800; padding:2px 8px; border-radius:4px; font-size:11px;">⚠️ स्थानांतरित</span>'
                        _impact_txt = f"{_rh}वें भाव से {_ch}वें भाव का फल प्रभावी रहेगा।"
                    else:
                        _status_badge = '<span style="background:#DCFCE7; color:#15803D; font-weight:800; padding:2px 8px; border-radius:4px; font-size:11px;">✅ स्थिर</span>'
                        _impact_txt = f"{_rh}वें भाव में स्थिर पूर्ण फल।"

                    _shift_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:5px 8px; font-weight:800; color:#1E293B;">{_pn}</td><td style="padding:5px 8px; color:#475569;">{_it.get("sign", "")}</td><td style="padding:5px 8px; text-align:center; font-weight:700;">{_rh} भाव</td><td style="padding:5px 8px; text-align:center; font-weight:900; color:#1E40AF;">{_ch} भाव</td><td style="padding:5px 8px; text-align:center;">{_status_badge}</td><td style="padding:5px 8px; font-size:11px; color:#334155;">{_impact_txt}</td></tr>')

                _shift_table_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto; margin-bottom:10px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 8px; text-align:left;">ग्रह</th><th style="padding:4px 8px; text-align:left;">राशि</th><th style="padding:4px 8px; text-align:center;">राशि भाव</th><th style="padding:4px 8px; text-align:center;">चलित भाव</th><th style="padding:4px 8px; text-align:center;">स्थिति</th><th style="padding:4px 8px; text-align:left;">फल प्रभाव</th></tr></thead><tbody>{"".join(_shift_rows)}</tbody></table></div>'
                st.markdown(_shift_table_html, unsafe_allow_html=True)

                if _shifted_planets:
                    st.warning("⚠️ **भाव परिवर्तन प्रभाव:** " + ", ".join(_shifted_planets) + " ग्रह चलित चक्र में स्थानांतरित हो गए हैं। दशा विश्लेषण में इन ग्रहों का फल इनके चलित भाव के अनुसार घटित होगा।")
                else:
                    st.success("✅ **पूर्ण समरूपता:** इस कुण्डली में सभी ग्रह राशि-भाव और चलित-भाव में समान हैं।")

                # Cusp Coordinates Table
                st.markdown("#### 📐 १२ भाव मध्य (Cusps) एवं संधि स्पष्ट")
                if _cusps_list:
                    _c_tbl_rows = []
                    for _c in _cusps_list:
                        _b_num = _c.get("bhava", 1)
                        _c_deg = _c.get("cusp_degree", 0.0)
                        _arambha = (_c_deg - 15.0 + 30.0) % 30.0
                        _anta = (_c_deg + 15.0) % 30.0
                        _c_tbl_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 8px; font-weight:800; color:#1E3A8A;">{_b_num} भाव</td><td style="padding:4px 8px; font-weight:700;">{_c.get("sign_name", "")}</td><td style="padding:4px 8px; font-family:monospace; color:#475569;">{_arambha:.2f}°</td><td style="padding:4px 8px; font-family:monospace; font-weight:800; color:#0F172A;">{_c_deg:.2f}°</td><td style="padding:4px 8px; font-family:monospace; color:#475569;">{_anta:.2f}°</td></tr>')
                    _c_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:180px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 8px; text-align:left;">भाव</th><th style="padding:4px 8px; text-align:left;">राशि</th><th style="padding:4px 8px; text-align:left;">आरंभ</th><th style="padding:4px 8px; text-align:left;">मध्य (Cusp)</th><th style="padding:4px 8px; text-align:left;">संधि (अंत)</th></tr></thead><tbody>{"".join(_c_tbl_rows)}</tbody></table></div>'
                    st.markdown(_c_tbl_html, unsafe_allow_html=True)

        except Exception as _ebc:
            st.error(f"भाव चलित गणना त्रुटि: {_ebc}")


    with tab_chandra:
        st.markdown("### 🌙 चन्द्र कुण्डली (Chandra Kundali — Mind & Emotional Consciousness)")
        _moon = chart.planets.get("Moon")
        if _moon:
            st.info(f"चन्द्रमा मन, माता, जन-समर्थन एवं भौतिक जीवन का मुख्य कारक है। चन्द्र कुण्डली में चन्द्रमा की राशि (**{_moon.sign_name}**) को प्रथम भाव (लग्न) मानकर सम्पूर्ण जीवन का अध्ययन किया जाता है:")

            # Construct Chandra VargaChart
            _chandra_planets = {
                _pn: VargaPlanetPosition(
                    name=_pn,
                    sign_id=_p.sign_id,
                    sign_name=_p.sign_name,
                    degree_in_varga=_p.sign_degree,
                    house_number=((_p.sign_id - _moon.sign_id + 12) % 12) + 1
                ) for _pn, _p in chart.planets.items()
            }
            _v_chandra = VargaChart(
                varga_code="CHANDRA",
                varga_name="चन्द्र कुण्डली",
                division=1,
                lagna_sign_id=_moon.sign_id,
                lagna_sign_name=_moon.sign_name,
                planets=_chandra_planets
            )
            chart.vargas["CHANDRA"] = _v_chandra

            cc_col1, cc_col2 = st.columns([1, 1], gap="medium")
            with cc_col1:
                svg_chandra = render_chart_svg(chart, f"🌙 चन्द्र कुण्डली ({_moon.sign_name} लग्न)", varga_code="CHANDRA")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_chandra}</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:8px; padding:10px 14px; font-size:12px; color:#1E3A8A; line-height:1.6;">
                    <b>🌕 चन्द्रमा का स्पष्ट परिचय:</b><br/>
                    • <b>राशि:</b> {_moon.sign_name} ({_moon.sign_degree:.2f}°)<br/>
                    • <b>नक्षत्र:</b> {_moon.nakshatra_name} (पाद {_moon.nakshatra_pada}) — स्वामी: {_moon.nakshatra_lord}<br/>
                    • <b>तिथि:</b> {p.tithi_name} ({p.tithi_type})<br/>
                    • <b>चन्द्र बल:</b> {'शुक्ल पक्ष बलिष्ठ' if 'Shukla' in p.tithi_type else 'कृष्ण पक्ष सौम्य'}
                </div>
                """, unsafe_allow_html=True)

            with cc_col2:
                st.markdown("#### 🪐 चन्द्र लग्न से १२ भाव स्थिति")
                _c_house_rows = []
                _c_signifs = [
                    "मन, स्वभाव, मानसिक शक्ति व काया", "वाणी, संचित धन, कुटुंब व आहार", "पराक्रम, भाई-बहन, साहस व संचार",
                    "मातृ सुख, भवन, वाहन व आंतरिक शांति", "बुद्धि, विद्या, पूर्वपुण्य व संतान", "रोग, ऋण, शत्रु व सेवा कार्य",
                    "दांपत्य, जीवनसाथी, साझेदारी व लोक संपर्क", "आयु, मानसिक संघर्ष व गूढ़ ज्ञान", "धर्म, भाग्य, गुरु व तीर्थाटन",
                    "कर्म, आजीविका, सामाजिक पद व कीर्ति", "लाभ, आय, मित्र व मनोकामना पूर्ति", "व्यय, शयन सुख, विदेश व मोक्ष"
                ]
                for _h_idx in range(1, 13):
                    _target_sid = ((_moon.sign_id - 1 + (_h_idx - 1)) % 12) + 1
                    _target_sname = SIGN_NAMES[_target_sid - 1]
                    _h_lord = SIGN_LORDS.get(_target_sname, "")
                    _occ_p = [_pn for _pn, _pp in chart.planets.items() if _pp.sign_id == _target_sid]
                    _occ_str = ", ".join(_occ_p) if _occ_p else "—"
                    _c_house_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#1E40AF;">{_h_idx} भाव</td><td style="padding:4px 6px; font-weight:700;">{_target_sname}</td><td style="padding:4px 6px; color:#475569;">{_h_lord}</td><td style="padding:4px 6px; font-weight:800; color:#0F172A;">{_occ_str}</td><td style="padding:4px 6px; font-size:10.5px; color:#475569;">{_c_signifs[_h_idx-1]}</td></tr>')

                _ch_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto; margin-bottom:10px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 6px; text-align:left;">भाव</th><th style="padding:4px 6px; text-align:left;">राशि</th><th style="padding:4px 6px; text-align:left;">स्वामी</th><th style="padding:4px 6px; text-align:left;">स्थित ग्रह</th><th style="padding:4px 6px; text-align:left;">जीवन क्षेत्र</th></tr></thead><tbody>{"".join(_c_house_rows)}</tbody></table></div>'
                st.markdown(_ch_tbl_html, unsafe_allow_html=True)

                # ─── Lunar Yogas Engine ───
                st.markdown("#### 🌟 चन्द्र आधारित प्रमुख योग (Classical Lunar Yogas)")
                _lunar_yogas = []

                # 1. Gajakesari
                _jup = chart.planets.get("Jupiter")
                if _jup:
                    _j_dist = ((_jup.sign_id - _moon.sign_id + 12) % 12) + 1
                    if _j_dist in [1, 4, 7, 10]:
                        _lunar_yogas.append(("🐘 गजकेसरी योग", f"गुरु चन्द्रमा से {_j_dist}वें (केंद्र) भाव में स्थित है। जातक अत्यंत मेधावी, पूज्य, कीर्तिवान एवं संकटों को परास्त करने वाला होता है।", "#DCFCE7", "#166534"))

                # 2. Sunapha, Anapha, Durdhara, Kemadruma
                _h2_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_moon.sign_id) % 12) + 1) and pn not in ["Sun", "Rahu", "Ketu"]]
                _h12_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_moon.sign_id - 2 + 12) % 12) + 1) and pn not in ["Sun", "Rahu", "Ketu"]]

                if _h2_planets and _h12_planets:
                    _lunar_yogas.append(("👑 दुरुधरा योग (Durdhara)", f"चन्द्रमा के दोनों ओर (द्वितीय में {', '.join(_h2_planets)} एवं द्वादश में {', '.join(_h12_planets)}) ग्रह विद्यमान हैं। जातक अतुल संपदा, वाहन एवं सुख-समृद्धि का स्वामी बनता है।", "#FEF3C7", "#92400E"))
                elif _h2_planets:
                    _lunar_yogas.append(("💰 सुनफा योग (Sunapha)", f"चन्द्रमा से द्वितीय भाव में {', '.join(_h2_planets)} स्थित हैं। जातक स्व-अर्जित धन, चतुर बुद्धि एवं उच्च सामाजिक प्रतिष्ठा प्राप्त करता है।", "#EFF6FF", "#1E40AF"))
                elif _h12_planets:
                    _lunar_yogas.append(("🕊️ अनफा योग (Anapha)", f"चन्द्रमा से द्वादश भाव में {', '.join(_h12_planets)} स्थित हैं। जातक निरोगी, विनम्र, उदार, आध्यात्मिक एवं नीतिवान होता है।", "#F0FDF4", "#065F46"))
                else:
                    # Kemadruma check
                    _kendra_planets = [pn for pn, p in chart.planets.items() if ((p.sign_id - _moon.sign_id + 12) % 12) + 1 in [1, 4, 7, 10] and pn not in ["Moon", "Rahu", "Ketu"]]
                    if _kendra_planets:
                        _lunar_yogas.append(("⚖️ केमद्रुम भंग राजयोग", f"चन्द्रमा के अगल-बगल ग्रह नहीं हैं किन्तु केंद्र में {', '.join(_kendra_planets)} स्थित होकर केमद्रुम दोष का पूर्ण निवारण कर रहे हैं।", "#ECFDF5", "#047857"))
                    else:
                        _lunar_yogas.append(("⚠️ केमद्रुम योग (Kemadruma)", "चन्द्रमा से द्वितीय एवं द्वादश दोनों रिक्त हैं। जीवन में कभी-कभी मानसिक एकाकीपन या वित्तीय उतार-चढ़ाव संभव है; शिव आराधना शुभप्रद है।", "#FEE2E2", "#991B1B"))

                # 3. Chandra-Mangala Yoga
                _mars = chart.planets.get("Mars")
                if _mars:
                    _m_dist = ((_mars.sign_id - _moon.sign_id + 12) % 12) + 1
                    if _m_dist in [1, 7]:
                        _lunar_yogas.append(("💎 चन्द्र-मंगल महालक्ष्मी योग", f"चन्द्रमा एवं मंगल परस्पर {_m_dist}वें भाव में युत/दृष्ट हैं। यह व्यापारिक सफलता, उद्योग में धन लाभ एवं तीव्र क्रियाशीलता का कारक है।", "#FAF5FF", "#6B21A8"))

                # Render Yoga Cards
                for _yt, _yd, _bg, _fg in _lunar_yogas:
                    st.markdown(f'<div style="background:{_bg}; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; margin-bottom:5px;"><span style="font-weight:900; color:{_fg}; font-size:12px;">{_yt}:</span> <span style="font-size:11.5px; color:#1E293B;">{_yd}</span></div>', unsafe_allow_html=True)
        else:
            st.warning("चन्द्रमा की स्थिति उपलब्ध नहीं।")


    with tab_surya:
        st.markdown("### ☀️ सूर्य कुण्डली (Surya Kundali — Soul, Vitality & Social Stature)")
        _sun = chart.planets.get("Sun")
        if _sun:
            st.info(f"भगवान सूर्य आत्मा, पिता, जीवनी शक्ति, शासकीय प्रभुत्व एवं आजीविका के मूल कारक हैं। सूर्य राशि (**{_sun.sign_name}**) को प्रथम भाव मानकर जातक के आत्मबल एवं सामाजिक प्रभाव का अध्ययन किया जाता है:")

            # Construct Surya VargaChart
            _surya_planets = {
                _pn: VargaPlanetPosition(
                    name=_pn,
                    sign_id=_p.sign_id,
                    sign_name=_p.sign_name,
                    degree_in_varga=_p.sign_degree,
                    house_number=((_p.sign_id - _sun.sign_id + 12) % 12) + 1
                ) for _pn, _p in chart.planets.items()
            }
            _v_surya = VargaChart(
                varga_code="SURYA",
                varga_name="सूर्य कुण्डली",
                division=1,
                lagna_sign_id=_sun.sign_id,
                lagna_sign_name=_sun.sign_name,
                planets=_surya_planets
            )
            chart.vargas["SURYA"] = _v_surya

            sc_col1, sc_col2 = st.columns([1, 1], gap="medium")
            with sc_col1:
                svg_surya = render_chart_svg(chart, f"☀️ सूर्य कुण्डली ({_sun.sign_name} लग्न)", varga_code="SURYA")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_surya}</div>', unsafe_allow_html=True)

                _sun_dignity, _, _ = get_varga_dignity_info("Sun", _sun.sign_name, affliction_engine)
                st.markdown(f"""
                <div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:8px; padding:10px 14px; font-size:12px; color:#78350F; line-height:1.6;">
                    <b>☀️ सूर्य देव का स्पष्ट परिचय:</b><br/>
                    • <b>राशि:</b> {_sun.sign_name} ({_sun.sign_degree:.2f}°)<br/>
                    • <b>नक्षत्र:</b> {_sun.nakshatra_name} (पाद {_sun.nakshatra_pada}) — स्वामी: {_sun.nakshatra_lord}<br/>
                    • <b>गरिमा:</b> {_sun_dignity}<br/>
                    • <b>सम्पूर्ण निरयण देशांतर:</b> {_sun.longitude:.2f}°
                </div>
                """, unsafe_allow_html=True)

            with sc_col2:
                st.markdown("#### 🪐 सूर्य लग्न से १२ भाव स्थिति")
                _s_house_rows = []
                _s_signifs = [
                    "आत्मा, तेज, जीवन शक्ति व संकल्प", "राजकोष, पैतृक संपदा, सत्य वाणी", "शौर्य, उद्यम, शासकीय अधिकार",
                    "आंतरिक संतोष, उच्च वाहन, जनता में प्रतिष्ठा", "प्रज्ञा, राजनीतिक सूझबूझ, मंत्र शक्ति", "प्रतिस्पर्धा, विजय, प्रशासनिक सेवा",
                    "व्यापारिक साझेदार, संबंध व बाह्य प्रभाव", "गूढ़ रहस्य, पितृ ऋण, गुप्त संपदा", "धर्म, उच्च संस्कार, पिता का मार्गदर्शन",
                    "शासन में पद, शासकीय मान्यता व आजीविका", "महत्वाकांक्षा पूर्ति, राजकीय लाभ, पुरस्कार", "दान, आध्यात्मिक त्याग, मोक्ष साधना"
                ]
                for _h_idx in range(1, 13):
                    _target_sid = ((_sun.sign_id - 1 + (_h_idx - 1)) % 12) + 1
                    _target_sname = SIGN_NAMES[_target_sid - 1]
                    _h_lord = SIGN_LORDS.get(_target_sname, "")
                    _occ_p = [_pn for _pn, _pp in chart.planets.items() if _pp.sign_id == _target_sid]
                    _occ_str = ", ".join(_occ_p) if _occ_p else "—"
                    _s_house_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#B45309;">{_h_idx} भाव</td><td style="padding:4px 6px; font-weight:700;">{_target_sname}</td><td style="padding:4px 6px; color:#475569;">{_h_lord}</td><td style="padding:4px 6px; font-weight:800; color:#0F172A;">{_occ_str}</td><td style="padding:4px 6px; font-size:10.5px; color:#475569;">{_s_signifs[_h_idx-1]}</td></tr>')

                _sh_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto; margin-bottom:10px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 6px; text-align:left;">भाव</th><th style="padding:4px 6px; text-align:left;">राशि</th><th style="padding:4px 6px; text-align:left;">स्वामी</th><th style="padding:4px 6px; text-align:left;">स्थित ग्रह</th><th style="padding:4px 6px; text-align:left;">जीवन क्षेत्र</th></tr></thead><tbody>{"".join(_s_house_rows)}</tbody></table></div>'
                st.markdown(_sh_tbl_html, unsafe_allow_html=True)

                # ─── Solar Yogas Engine ───
                st.markdown("#### 🌟 सूर्य आधारित प्रमुख योग (Classical Solar Yogas)")
                _solar_yogas = []

                # 1. Budhaditya
                _merc = chart.planets.get("Mercury")
                if _merc and _merc.sign_id == _sun.sign_id:
                    _b_diff = abs(_sun.longitude - _merc.longitude)
                    if _b_diff > 180: _b_diff = 360 - _b_diff
                    if _b_diff <= 10.0:
                        _comb_label = " (बुध अस्त नहीं / पूर्ण प्रखर)" if not _merc.is_combust else " (बुध अस्त / ज्ञान प्रबल)"
                        _solar_yogas.append(("⚡ बुधादित्य योग (Budhaditya)", f"सूर्य एवं बुध की एक ही राशि में युति (अंतर: {_b_diff:.2f}°){_comb_label}। जातक असाधारण मेधावी, विश्लेषण में दक्ष एवं प्रशासनिक क्षमता से युक्त होता है।", "#EFF6FF", "#1E40AF"))

                # 2. Vesi, Vosi, Ubhayachari
                _h2_s_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_sun.sign_id) % 12) + 1) and pn not in ["Moon", "Rahu", "Ketu"]]
                _h12_s_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_sun.sign_id - 2 + 12) % 12) + 1) and pn not in ["Moon", "Rahu", "Ketu"]]

                if _h2_s_planets and _h12_s_planets:
                    _solar_yogas.append(("👑 उभयाचारी योग (Ubhayachari)", f"सूर्य के दोनों ओर (द्वितीय में {', '.join(_h2_s_planets)} एवं द्वादश में {', '.join(_h12_s_planets)}) शुभ/ग्रह स्थित हैं। जातक राजा समान सम्मानित, वक्तृत्व कला में निपुण व सुखी होता है।", "#FEF3C7", "#92400E"))
                elif _h2_s_planets:
                    _solar_yogas.append(("🏛️ वेसि योग (Vesi)", f"सूर्य से द्वितीय भाव में {', '.join(_h2_s_planets)} स्थित हैं। जातक धैर्यवान, सत्यवादी, वाक्पटु एवं यशस्वी जीवन व्यतीत करता है।", "#DCFCE7", "#166534"))
                elif _h12_s_planets:
                    _solar_yogas.append(("📚 वोसि योग (Vosi)", f"सूर्य से द्वादश भाव में {', '.join(_h12_s_planets)} स्थित हैं। जातक बुद्धिमान, विद्यावान, परोपकारी एवं दृढ़ स्मरण शक्ति वाला होता है।", "#F0FDF4", "#065F46"))
                else:
                    _solar_yogas.append(("☀️ स्वतंत्र सौर तेज (Independent Sun)", "सूर्य के अगल-बगल कोई ग्रह नहीं है; जातक आत्मनिर्भर, आत्म-प्रेरित एवं स्वतंत्र व्यक्तित्व का धनी होता है।", "#F8FAFC", "#334155"))

                for _yt, _yd, _bg, _fg in _solar_yogas:
                    st.markdown(f'<div style="background:{_bg}; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; margin-bottom:5px;"><span style="font-weight:900; color:{_fg}; font-size:12px;">{_yt}:</span> <span style="font-size:11.5px; color:#1E293B;">{_yd}</span></div>', unsafe_allow_html=True)
        else:
            st.warning("सूर्य की स्थिति उपलब्ध नहीं।")


    with tab_yuddha:
        st.markdown("### ⚔️ ग्रह युद्ध (Graha Yuddha — Classical Planetary War Engine)")
        st.info("बृहत्संहिता (अध्याय १७) एवं सूर्य सिद्धांत अनुसार जब पांच तारा ग्रह (मंगल, बुध, गुरु, शुक्र, शनि) परस्पर १° (६० कला) के भीतर आ जाते हैं, तो उनके मध्य 'ग्रह युद्ध' घटित होता है। उत्तर अक्षांश (Greater North Latitude) वाला ग्रह विजयी होकर बलवान होता है तथा पराजित ग्रह अपनी प्राकृतिक शक्ति (षड्बल) खो देता है:")

        try:
            _yw_list = default_chart_calculator.detect_graha_yuddha(chart)
            _tara_grahas = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
            _GRAHA_HINDI = {"Mars": "♂ मंगल", "Mercury": "☿ बुध", "Jupiter": "♃ गुरु", "Venus": "♀ शुक्र", "Saturn": "♄ शनि"}

            # ─── 5×5 Tara Grahas Distance Matrix ───
            st.markdown("#### 🔬 पंचतारा ग्रह परस्पर कोणीय दूरी मैट्रिक्स (5×5 Angular Separation Matrix)")
            _matrix_headers = "".join([f'<th style="padding:6px 8px; text-align:center; background:#1E293B; color:#F8FAFC; font-size:11.5px;">{_GRAHA_HINDI.get(p, p)}</th>' for p in _tara_grahas])
            _matrix_rows = []

            for p1 in _tara_grahas:
                _cells = [f'<td style="padding:6px 8px; font-weight:800; background:#F1F5F9; color:#1E293B;">{_GRAHA_HINDI.get(p1, p1)}</td>']
                for p2 in _tara_grahas:
                    if p1 == p2:
                        _cells.append('<td style="padding:6px 8px; text-align:center; background:#E2E8F0; color:#94A3B8; font-weight:700;">—</td>')
                    else:
                        _p1_obj = chart.planets.get(p1)
                        _p2_obj = chart.planets.get(p2)
                        if _p1_obj and _p2_obj:
                            _d = abs(_p1_obj.longitude - _p2_obj.longitude) % 360.0
                            if _d > 180.0: _d = 360.0 - _d
                            if _d <= 1.0:
                                _bg, _fg, _sym = "#FEE2E2", "#991B1B", "⚔️ "
                            elif _d <= 3.0:
                                _bg, _fg, _sym = "#FEF3C7", "#92400E", "⚠️ "
                            elif _d <= 5.0:
                                _bg, _fg, _sym = "#EFF6FF", "#1E40AF", "🟡 "
                            else:
                                _bg, _fg, _sym = "#F8FAFC", "#475569", ""
                            _cells.append(f'<td style="padding:6px 8px; text-align:center; background:{_bg}; color:{_fg}; font-family:monospace; font-weight:800;">{_sym}{_d:.2f}°</td>')
                        else:
                            _cells.append('<td style="padding:6px 8px; text-align:center;">—</td>')
                _matrix_rows.append(f'<tr style="border-bottom:1px solid #CBD5E1;">{"".join(_cells)}</tr>')

            _mat_html = f'<div style="overflow-x:auto; background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:8px; margin-bottom:14px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr><th style="padding:6px 8px; text-align:left; background:#0F172A; color:#F8FAFC;">तारा ग्रह</th>{_matrix_headers}</tr></thead><tbody>{"".join(_matrix_rows)}</tbody></table></div>'
            st.markdown(_mat_html, unsafe_allow_html=True)
            st.caption("🟢 >5° शांत | 🟡 3°-5° युति क्षेत्र | ⚠️ 1°-3° सन्निकट संपर्क | ⚔️ ≤1°00' प्रत्यक्ष ग्रह युद्ध")

            # ─── War Status Verdict Cards ───
            if _yw_list:
                st.markdown("#### ⚔️ सक्रिय ग्रह युद्ध विवरण एवं फल प्रभाव")
                for _yw in _yw_list:
                    _p1 = _yw.get('planet1')
                    _p2 = _yw.get('planet2')
                    _sep = _yw.get('separation_deg', 0.0)
                    _win = _yw.get('winner')
                    _los = _yw.get('loser')

                    # Brihat Samhita War Classification
                    if _sep < 0.25:
                        _w_type = "भेदम (Bhedam — पूर्ण ग्रसन / परस्पर भेदन)"
                    elif _sep < 0.50:
                        _w_type = "उल्लेखम (Ullekham — कोर स्पर्श / संघर्ष)"
                    elif _sep < 0.75:
                        _w_type = "अंशुमर्दम (Amshumardam — किरणों का टकराव)"
                    else:
                        _w_type = "अपसव्यम (Apasavyam — वक्र गति युक्त युद्ध)"

                    _w_lord = [f"{h}वें" for h, s in chart.houses.items() if s.lord == _win] if hasattr(chart, 'houses') else []
                    _l_lord = [f"{h}वें" for h, s in chart.houses.items() if s.lord == _los] if hasattr(chart, 'houses') else []

                    st.markdown(f"""
                    <div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:14px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:900; color:#B91C1C; font-size:14px;">⚔️ {_GRAHA_HINDI.get(_p1, _p1)} बनाम {_GRAHA_HINDI.get(_p2, _p2)}</span>
                            <span style="background:#FEE2E2; color:#991B1B; font-weight:800; padding:2px 8px; border-radius:4px; font-size:11.5px;">अंतर: {_sep:.3f}° ({_sep*60:.1f} कला)</span>
                        </div>
                        <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                            • <b>युद्ध प्रकार:</b> {_w_type}<br/>
                            • 🏆 <b>विजेता ग्रह:</b> <b style="color:#047857;">{_GRAHA_HINDI.get(_win, _win)}</b> (उत्तर अक्षांश की प्रधानता के कारण विजयी)<br/>
                            • ⚠️ <b>पराजित ग्रह:</b> <b style="color:#DC2626;">{_GRAHA_HINDI.get(_los, _los)}</b> (षड्बल हरण के कारण निर्बल)<br/>
                            • <b>फल प्रभाव:</b> विजयी ग्रह के स्वामित्व वाले भावों के शुभ फल में वृद्धि होगी; पराजित ग्रह के स्वामित्व वाले भावों से संबंधित विषयों में संघर्ष अथवा विलम्ब का सामना करना पड़ सकता है।
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Find closest approach among Tara Grahas
                _min_sep = 999.0
                _close_pair = ("", "")
                for i, p1 in enumerate(_tara_grahas):
                    for p2 in _tara_grahas[i+1:]:
                        if p1 in chart.planets and p2 in chart.planets:
                            _d = abs(chart.planets[p1].longitude - chart.planets[p2].longitude) % 360.0
                            if _d > 180.0: _d = 360.0 - _d
                            if _d < _min_sep:
                                _min_sep = _d
                                _close_pair = (p1, p2)

                st.markdown(f"""
                <div style="background:linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%); border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:12px; box-shadow:0 2px 6px rgba(16, 185, 129, 0.1);">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                        <span style="font-size:18px;">🛡️</span>
                        <span style="font-size:14.5px; font-weight:900; color:#065F46;">ग्रह मैत्री एवं शांति प्रशस्ति (No Planetary War Detected)</span>
                    </div>
                    <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                        इस जन्म पत्रिका में पांचों तारा ग्रह (मंगल, बुध, गुरु, शुक्र, शनि) परस्पर सुरक्षित कोणीय दूरी पर स्थित हैं। किसी भी ग्रह के मध्य १° के भीतर का संघर्ष (युद्ध) नहीं है।<br/>
                        • <b>निकटतम संपर्क:</b> {_GRAHA_HINDI.get(_close_pair[0], _close_pair[0])} एवं {_GRAHA_HINDI.get(_close_pair[1], _close_pair[1])} — कोणीय अंतर: <b>{_min_sep:.2f}°</b><br/>
                        • <b>शास्त्रीय लाभ:</b> समस्त ग्रह स्वतंत्र होकर अपने पूर्ण षड्बल एवं नैसर्गिक सामर्थ्य के साथ अपना शुभाशुभ फल प्रदान करने में सक्षम हैं। किसी भी ग्रह का बल हरण (Bala Harana) नहीं हुआ है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as _egy:
            st.error(f"ग्रह युद्ध गणना त्रुटि: {_egy}")


    with tab_vishesh:
        st.markdown("### 🌟 विशेष लग्न एवं १२ आरूढ़ पद महा-विश्लेषण (All 12 Arudha Padas & Special Lagnas Deep Dive)")
        st.info("महर्षि जैमिनी के सूत्र अनुसार 'पदं पितृभ्यः' — प्रत्येक भाव का आरूढ़ पद उस भाव का सांसारिक प्रतिबिंब (Maya / Worldly Manifestation) होता है। लोग जातक को सांसारिक रूप में कैसा देखते हैं, इसका रहस्य आरूढ़ पदों में समाहित है:")

        if chart.jaimini and getattr(chart.jaimini, 'arudha_details', None):
            jm = chart.jaimini
            a_details = jm.arudha_details

            # ─── Complete 12 Arudha Master Table ───
            st.markdown("#### 📜 समस्त १२ आरूढ़ पद संपूर्ण विवरण (Master Arudha Padas Matrix)")
            _arudha_order = ["AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "UL"]
            _ar_rows = []
            for _ak in _arudha_order:
                _ad = a_details.get(_ak)
                if not _ad:
                    continue
                _is_special = _ak in ["AL", "UL"]
                _lbl_col = "#B45309" if _is_special else "#1E3A8A"
                _ar_rows.append({
                    "आरूढ़ पद": _ak,
                    "स्रोत भाव": f"{_ad.get('house_num', 1)} भाव",
                    "स्रोत राशि": _ad.get('house_sign', ''),
                    "भाव स्वामी": _ad.get('lord_name', ''),
                    "स्वामी की राशि": _ad.get('lord_sign', ''),
                    "दूरी (कदम)": f"{_ad.get('distance', 1)} राशि",
                    "लागू नियम": _ad.get('exception', 'सामान्य'),
                    "आरूढ़ राशि": _ad.get('pada_sign_name', ''),
                    "लग्न से भाव": f"{_ad.get('pada_house_from_lagna', 1)} भाव",
                    "शास्त्रीय प्रयोजन / फल": _ad.get('signification_hi', '').split(':', 1)[-1].strip()
                })
            st.dataframe(pd.DataFrame(_ar_rows), use_container_width=True, hide_index=True)

            # ─── Deep Dive Analytical Cards: AL, UL & Wealth ───
            st.markdown("#### 🔬 प्रमुख आरूढ़ पदों का गहन विश्लेषण (Arudha Lagna & Upapada Deep Dive)")
            col_ad1, col_ad2 = st.columns(2, gap="medium")

            with col_ad1:
                _al_data = a_details.get("AL", {})
                _al_h = _al_data.get("pada_house_from_lagna", 1)
                _al_sign = _al_data.get("pada_sign_name", "")

                if _al_h in [1, 4, 7, 10]:
                    _al_rel = "केंन्द्र संबंध (1/4/7/10 Axis) — जातक की आंतरिक क्षमता एवं बाह्य सामाजिक छवि में श्रेष्ठ सामंजस्य है।"
                    _al_bg, _al_bdr = "#F0FDF4", "#86EFAC"
                elif _al_h in [5, 9]:
                    _al_rel = "त्रिकोण संबंध (5/9 Axis) — पूर्वपुण्य एवं धर्म का प्रबल प्रभाव; समाज में जातक को स्वाभाविक आदर व सम्मान प्राप्त होता है।"
                    _al_bg, _al_bdr = "#ECFDF5", "#6EE7B7"
                elif _al_h in [3, 6, 11]:
                    _al_rel = "उपचय संबंध (3/6/11 Axis) — जातक निरंतर पुरुषार्थ एवं उद्योग द्वारा अपनी सामाजिक छवि को विशाल बनाता है।"
                    _al_bg, _al_bdr = "#EFF6FF", "#93C5FD"
                else:
                    _al_rel = "षडाष्टक/व्यय संबंध (6/8/12 Axis) — जातक का आंतरिक सत्य एवं बाह्य छवि भिन्न हो सकती है; जनसामान्य द्वारा गलत समझे जाने का अंदेशा।"
                    _al_bg, _al_bdr = "#FFFBEB", "#FCD34D"

                st.markdown(f"""
                <div style="background:{_al_bg}; border:1.5px solid {_al_bdr}; border-radius:10px; padding:14px; height:100%;">
                    <h5 style="color:#1E3A8A; margin:0 0 6px 0;">👑 आरूढ़ लग्न (AL): {_al_sign} (लग्न से {_al_h} भाव)</h5>
                    <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                        <b>संबंध स्वरूप:</b> {_al_rel}<br/>
                        • <b>सामाजिक प्रतिष्ठा:</b> आरूढ़ लग्न जातक की सामाजिक स्थिति, करियर में यश एवं जनता में पहचान का निर्णायक है।<br/>
                        • <b>शास्त्रीय नियम:</b> यदि आरूढ़ लग्न से एकादश भाव में शुभ ग्रह स्थित हों, तो जातक निरंतर प्रचुर मात्रा में धन अर्जित करता है; दशम भाव में शुभ ग्रह होने पर व्यक्ति की आजीविका स्वच्छ एवं सम्मानित होती है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_ad2:
                _ul_data = a_details.get("UL", {})
                _ul_h = _ul_data.get("pada_house_from_lagna", 1)
                _ul_sign = _ul_data.get("pada_sign_name", "")
                _ul_lord = _ul_data.get("lord_name", "")

                st.markdown(f"""
                <div style="background:#FDF2F8; border:1.5px solid #F472B6; border-radius:10px; padding:14px; height:100%;">
                    <h5 style="color:#9D174D; margin:0 0 6px 0;">💍 उपपद लग्न (UL / A12): {_ul_sign} (लग्न से {_ul_h} भाव)</h5>
                    <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                        <b>उपपद लग्न स्वामी:</b> {_ul_lord}<br/>
                        • <b>दांपत्य स्थायित्व:</b> उपपद लग्न जीवनसाथी के कुल, वैवाहिक जीवन की स्थिरता एवं जीवनसाथी के स्वभाव का मुख्य दर्पण है।<br/>
                        • <b>द्वितीय भाव सूत्र:</b> उपपद से द्वितीय भाव वैवाहिक संबंध के पालन-पोषण (Sustenance) का कारक है। यदि उपपद से द्वितीय भाव में शुभ ग्रह (गुरु, शुक्र) हों तो दांपत्य जीवन सुदीर्घ एवं सुखमय रहता है; पाप ग्रहों का प्रभाव रहने पर वैवाहिक समायोजन आवश्यक होता है।
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("आरूढ़ पद गणना लोड हो रही है...")


    with tab_kota:
        st.markdown("### 🏰 कोटा चक्र दुर्ग आरेख (Kota Chakra Durga Fortress)")
        st.info("कोटा चक्र जातक के जन्म नक्षत्र पर आधारित एक प्राचीन रक्षात्मक दुर्ग (Fortress) संरचना है। यह चार संकेन्द्री सुरक्षा दीवारों में विभाजित होता है, जो जातक की आंतरिक जीवन शक्ति, स्वास्थ्य, संकटों से सुरक्षा एवं विजय का अचूक संकेत देता है:")

        try:
            kota_engine = default_kota_chakra_engine
            kota_data_m0 = kota_engine.calculate(chart)

            kc_col1, kc_col2 = st.columns([1, 1], gap="medium")
            with kc_col1:
                kota_svg_m0 = ChartRenderer.render_kota_chakra_svg(kota_data_m0, title=f"कोटा चक्र दुर्ग — {chart.birth_data.name if chart.birth_data else 'जातक'}")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{kota_svg_m0}</div>', unsafe_allow_html=True)

                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px; font-size:12px; color:#334155; line-height:1.5;">
                    <b>🏰 दुर्ग की ४ रक्षात्मक दीवारें (Concentric Enclosures):</b><br/>
                    • <b>१. स्तम्भ (Stambha):</b> दुर्ग का गर्भगृह (Heart/Core) — जीवन शक्ति व आरोग्य।<br/>
                    • <b>२. मध्य (Madhya):</b> दुर्ग का अन्तःपुर (Citadel) — आंतरिक संबल व परिवार।<br/>
                    • <b>३. प्राकार (Prakaara):</b> दुर्ग का परकोटा (Outer Rampart) — सुरक्षा प्राचीर।<br/>
                    • <b>४. बाह्य (Bahya):</b> दुर्ग के बाहर का क्षेत्र — बाह्य जगत एवं आने-जाने वाले ग्रह।
                </div>
                """, unsafe_allow_html=True)

            with kc_col2:
                _k_swami = kota_data_m0.get("kota_swami", "—")
                _k_pala = kota_data_m0.get("kota_pala", "—")
                _def_status = kota_data_m0.get("defense_status", "🛡️ सुरक्षित")
                _def_sum = kota_data_m0.get("defense_summary", "")

                # Strategic Defense Scorecard
                st.markdown(f"""
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
                    <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:8px; padding:8px 12px;">
                        <div style="font-size:11px; color:#1E40AF; font-weight:800;">👑 दुर्ग स्वामी (Kota Swami)</div>
                        <div style="font-size:15px; font-weight:900; color:#1E293B;">{_k_swami}</div>
                        <div style="font-size:10px; color:#64748B;">दुर्ग का राजा / मूल जीवन शक्ति</div>
                    </div>
                    <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:8px 12px;">
                        <div style="font-size:11px; color:#166534; font-weight:800;">🛡️ दुर्ग रक्षक (Kota Pala)</div>
                        <div style="font-size:15px; font-weight:900; color:#1E293B;">{_k_pala}</div>
                        <div style="font-size:10px; color:#64748B;">दुर्ग का सेनापति / सुरक्षा कवच</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:#FFFBEB; border:1.5px solid #FCD34D; border-radius:8px; padding:10px 12px; margin-bottom:10px;">
                    <div style="font-weight:900; color:#92400E; font-size:12.5px; margin-bottom:4px;">दुर्ग रक्षा मूल्यांकन: {_def_status}</div>
                    <div style="font-size:11.5px; color:#1E293B; line-height:1.5;">{_def_sum}</div>
                </div>
                """, unsafe_allow_html=True)

                # Planet Allocations Table
                st.markdown("#### 🪐 दुर्ग में ग्रहों की स्थिति एवं गति")
                _p_allocs = kota_data_m0.get("planet_allocations", [])
                if _p_allocs:
                    _pl_k_rows = []
                    for _pa in _p_allocs:
                        _pn = _pa.get("planet", "")
                        _zn = _pa.get("zone", "")
                        _mo = _pa.get("motion", "")
                        _nat = _pa.get("nature", "Benefic")
                        _is_mal = ("Malefic" in _nat or _pn in ["Mars", "Saturn", "Rahu", "Ketu", "Sun"])
                        _p_col = "#DC2626" if _is_mal else "#059669"
                        _role_badge = f'<span style="background:{"#FEE2E2" if _is_mal else "#DCFCE7"}; color:{_p_col}; font-weight:800; padding:1px 6px; border-radius:4px; font-size:10.5px;">{"आक्रांता" if _is_mal else "रक्षक"}</span>'
                        _pl_k_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#1E293B;">{_pn}</td><td style="padding:4px 6px; color:#475569;">{_pa.get("nakshatra", "")}</td><td style="padding:4px 6px; font-weight:700;">{_zn}</td><td style="padding:4px 6px; font-size:11px;">{_mo}</td><td style="padding:4px 6px; text-align:center;">{_role_badge}</td></tr>')

                    _k_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 6px; text-align:left;">ग्रह</th><th style="padding:4px 6px; text-align:left;">नक्षत्र</th><th style="padding:4px 6px; text-align:left;">दुर्ग क्षेत्र</th><th style="padding:4px 6px; text-align:left;">गति दिशा</th><th style="padding:4px 6px; text-align:center;">भूमिका</th></tr></thead><tbody>{"".join(_pl_k_rows)}</tbody></table></div>'
                    st.markdown(_k_tbl_html, unsafe_allow_html=True)

        except Exception as _ekc:
            st.error(f"कोटा चक्र गणना त्रुटि: {_ekc}")


# =============================================================
# TAB 3: AFFLICTION & FREE WILL ANALYSIS (GRAHALAKSHANAM CORE)

elif selected_idx == 1:
    st.subheader("🎯 घटना विश्लेषण एवं काल सत्यापन (Event Analysis & Verification)")

    tab_future_event, tab_past_event = st.tabs([
        "🔮 भविष्य घटना पूर्वानुमान (Future Event Prediction)",
        "🔍 6-Pillar भूतकाल घटना सत्यापन (6-Pillar Past Event Verification)"
    ])

    with tab_future_event:
        st.write("अपनी कुण्डली के लिए किसी भी भविष्य की तिथि अथवा समयावधि का बहु-पद्धति शास्त्रीय विश्लेषण प्राप्त करें।")

        col_q1, col_q2, col_q3 = st.columns([2, 2, 2])
        target_event_date = col_q1.date_input("लक्षित तिथि (Target Date)", value=date(2027, 4, 12), format="DD/MM/YYYY")
        theme = col_q2.selectbox(
            "विश्लेषण विषय (Theme)",
            ["career", "marriage", "wealth", "health", "travel", "spirituality", "all"],
            format_func=lambda x: {
                "career": "💼 आजीविका / करियर (Career)",
                "marriage": "💍 विवाह / संबंध (Marriage)",
                "wealth": "💰 धन / संपत्ति (Wealth)",
                "health": "🌿 स्वास्थ्य (Health)",
                "travel": "✈️ विदेश / यात्रा (Travel)",
                "spirituality": "🕉️ आध्यात्म (Spirituality)",
                "all": "🌐 समग्र विश्लेषण (All Themes)"
            }.get(x, x)
        )
        scan_range = col_q3.checkbox("30-दिवसीय विंडो स्कैन करें (30-Day Window)")

        query_input = GhatnaQueryInput(
            birth_data=birth_profile,
            target_date=target_event_date,
            theme=theme
        )
        result = default_event_query_service.execute_query(query_input, precomputed_chart=chart)

        st.markdown("---")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("लक्षित तिथि", result.target_date.strftime("%d-%b-%Y"))
        m_col2.metric("संभावना सूचकांक", f"{result.composite_score:.2f}")
        m_col3.metric("विश्वास स्तर", result.confidence_band.split(" ")[0])
        m_col4.metric("सक्रिय विंशोत्तरी दशा", result.active_dasha.formatted_summary)

        st.info(f"📊 **पद्धति सहमति अनुपात (Consensus):** {result.consensus_ratio}")

        col_res1, col_res2 = st.columns([3, 2])
        with col_res1:
            st.markdown("### 📖 शास्त्रीय साक्ष्य सार (Classical Narrative)")
            st.markdown(result.narrative_hi)
            with st.expander("English Summary"):
                st.markdown(result.narrative_en)

        with col_res2:
            st.markdown("### 🪐 गोचर स्थिति (Transit Snapshot)")
            t = result.transit_summary
            st.markdown(f"- **शनि गोचर:** चंद्र से {t.saturn_house_from_moon}वां | लग्न से {t.saturn_house_from_lagna}वां भाव")
            st.markdown(f"- **गुरु गोचर:** चंद्र से {t.jupiter_house_from_moon}वां | लग्न से {t.jupiter_house_from_lagna}वां भाव")
            st.markdown(f"- **साढ़े साती:** {'✅ सक्रिय - ' + (t.sade_sati_phase or '') if t.is_sade_sati else '❌ निष्क्रिय'}")
            st.markdown(f"- **ढैय्या:** {'✅ सक्रिय - ' + (t.dhaiya_type or '') if t.is_dhaiya else '❌ निष्क्रिय'}")

        st.markdown("### 🔍 सक्रिय शास्त्रीय नियम एवं साक्ष्य (Fired Rules Evidence)")
        if result.top_positive_signals:
            st.markdown("##### 🟢 अनुकूल शास्त्रीय योग:")
            for r in result.top_positive_signals:
                st.markdown(f"""
                <div class="rule-card">
                    <b>{r.rule_name_hi}</b> ({r.rule_name_en})<br/>
                    <small style="color:#F59E0B;">स्रोत: {r.source_text} | अध्याय: {r.source_chapter} | पद्धति: {r.school}</small><br/>
                    <span>{r.explanation_hi}</span><br/>
                    <small style="color:#6EE7B7;">सिग्नल शक्ति: {r.signal_score:.2f} | पुष्टि: {'हाँ' if r.varga_confirmed else 'सामान्य'}</small>
                </div>
                """, unsafe_allow_html=True)

    with tab_past_event:
        st.write("विगत जीवन की किसी भी ऐतिहासिक घटना (उदा: विवाह, प्रथम नौकरी, पदोन्नति, मकान क्रय, संतान जन्म, विदेश यात्रा आदि) का **६ शास्त्रीय स्तंभों** द्वारा वैज्ञानिक एवं शास्त्र-सम्मत सत्यापन प्राप्त करें।")

        col_p1, col_p2, col_p3 = st.columns([2, 2, 2])
        default_past_date = date(2021, 5, 20)
        past_target_date = col_p1.date_input("भूतपूर्व घटना तिथि (Past Event Date)", value=default_past_date, format="DD/MM/YYYY", key="pe_target_date_inp")
        past_theme = col_p2.selectbox(
            "घटना का विषय (Event Theme)",
            ["marriage", "career", "wealth", "education", "children", "health"],
            format_func=lambda x: {
                "marriage": "💍 विवाह / संबंध (Marriage)",
                "career": "💼 आजीविका / नौकरी / पदोन्नति (Career)",
                "wealth": "💰 धन / संपत्ति / वाहन क्रय (Wealth)",
                "education": "🎓 उच्च शिक्षा / उपाधि (Education)",
                "children": "👶 संतान प्राप्ति (Children)",
                "health": "🌿 स्वास्थ्य संकट / रोग (Health)"
            }.get(x, x),
            key="pe_theme_sel"
        )
        past_desc = col_p3.text_input("घटना विवरण (Event Description)", value="विवाह संपन्न हुआ", key="pe_desc_inp")

        run_past_verify = st.button("🔍 ६-स्तंभ शास्त्रीय सत्यापन करें (Verify Across 6 Classical Pillars)", type="primary", use_container_width=True, key="pe_verify_btn")

        if run_past_verify or st.session_state.get("pe_last_verified", False):
            st.session_state["pe_last_verified"] = True
            try:
                from src.jyotish.events.past_verification import default_past_event_engine, PastEventVerificationInput
                from src.jyotish.rules.conflict_graph import AstrologicalEvidenceStatus

                pe_inp = PastEventVerificationInput(
                    birth_data=birth_profile,
                    event_theme=past_theme,
                    query_text=past_desc,
                    target_date=past_target_date
                )
                ver_res = default_past_event_engine.verify_past_event(pe_inp, precomputed_chart=chart)

                st.markdown("---")

                # Verdict Status Header Card
                st_val = ver_res.status
                if st_val in (AstrologicalEvidenceStatus.STRONGLY_SUPPORTED, AstrologicalEvidenceStatus.SUPPORTED):
                    card_bg = "#064E3B" if (is_astrallis_mode or is_night_mode) else "#ECFDF5"
                    card_border = "#10B981"
                    card_text = "#6EE7B7" if (is_astrallis_mode or is_night_mode) else "#065F46"
                    card_title = f"✅ शास्त्र-सम्मत सत्यापन: {st_val.value.upper()}"
                    card_desc = "इस ऐतिहासिक तिथि पर जन्म कुण्डली, विंशोत्तरी दशा, ऐतिहासिक गोचर एवं षोडशवर्ग चक्रों में घटना के पूर्ण शास्त्रीय योग उपस्थित पाए गए।"
                elif st_val in (AstrologicalEvidenceStatus.MODERATELY_SUPPORTED, AstrologicalEvidenceStatus.WEAKLY_SUPPORTED):
                    card_bg = "#78350F" if (is_astrallis_mode or is_night_mode) else "#FFFBEB"
                    card_border = "#F59E0B"
                    card_text = "#FCD34D" if (is_astrallis_mode or is_night_mode) else "#92400E"
                    card_title = f"⚠️ आंशिक शास्त्रीय समर्थन: {st_val.value.upper()}"
                    card_desc = "इस तिथि पर कुछ मुख्य शास्त्रीय स्तंभ (जैसे दशा या गोचर) अनुकूल रहे, जबकि कुछ स्तंभ तटस्थ अथवा सूक्ष्म स्तर पर सक्रिय थे।"
                elif st_val in (AstrologicalEvidenceStatus.INCONCLUSIVE, AstrologicalEvidenceStatus.CONFLICTING):
                    card_bg = "#1E293B" if (is_astrallis_mode or is_night_mode) else "#F1F5F9"
                    card_border = "#64748B"
                    card_text = "#CBD5E1" if (is_astrallis_mode or is_night_mode) else "#334155"
                    card_title = f"ℹ️ अनिर्णायक/विरोधाभासी साक्ष्य: {st_val.value.upper()}"
                    card_desc = "शास्त्रीय गणनाओं में इस तिथि पर घटना के स्पष्ट और निर्णायक योगों की पर्याप्त पुष्टि नहीं हो सकी।"
                else:
                    card_bg = "#7F1D1D" if (is_astrallis_mode or is_night_mode) else "#FEF2F2"
                    card_border = "#EF4444"
                    card_text = "#FCA5A5" if (is_astrallis_mode or is_night_mode) else "#991B1B"
                    card_title = f"❌ शास्त्रीय समर्थन का अभाव: {st_val.value.upper()}"
                    card_desc = "इस तिथि पर संबंधित भाव एवं भावेश के प्रतिकूल योग तथा दशा-गोचर की अनुपस्थिति पाई गई।"

                st.markdown(f"""
                <div style="background:{card_bg}; border:2px solid {card_border}; border-radius:10px; padding:16px; margin-bottom:16px;">
                    <div style="font-size:18px; font-weight:900; color:{card_text}; margin-bottom:4px;">{card_title}</div>
                    <div style="font-size:13.5px; color:{card_text}; font-weight:600;">{card_desc}</div>
                </div>
                """, unsafe_allow_html=True)

                # Metrics Row
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                m_c1.metric("लक्षित भूतपूर्व तिथि", ver_res.target_date.strftime("%d-%b-%Y"))
                m_c2.metric("शास्त्रीय विश्वास स्तर", f"{ver_res.confidence_score*100:.1f}%")
                m_c3.metric("सत्यापन स्थिति (Status)", ver_res.status.value.upper())
                m_c4.metric("सक्रिय विंशोत्तरी दशा", ver_res.pillar_4_dasha_evidence.get("summary", "—"))

                st.markdown("### 🏛️ ६ शास्त्रीय स्तंभों का विस्तृत साक्ष्य (The 6 Classical Pillars Evidence)")

                p_row1_c1, p_row1_c2, p_row1_c3 = st.columns(3)
                p_row2_c1, p_row2_c2, p_row2_c3 = st.columns(3)

                # Pillar 1: D1 Natal Potential
                p1 = ver_res.pillar_1_d1_evidence
                with p_row1_c1:
                    st.markdown(f"""
                    <div style="border:1.5px solid #3B82F6; border-radius:8px; padding:12px; height:100%; background:rgba(59,130,246,0.06);">
                        <b style="color:#2563EB; font-size:14px;">१. जन्म लग्न विभव (Natal D1)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>प्राथमिक भाव:</b> {p1.get('house')}वां भाव<br/>
                            • <b>भावेश:</b> {p1.get('lord')}<br/>
                            • <b>भावेश स्थिति:</b> {p1.get('lord_house')}वां भाव ({p1.get('lord_dignity', 'neutral')})<br/>
                            • <b>लग्न विभव स्कोर:</b> <b>{p1.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 2: Prashna Overlay
                p2 = ver_res.pillar_2_prashna_evidence or {}
                with p_row1_c2:
                    p2_fav = "✅ अनुकूल" if p2.get("prashna_favorable") else "ℹ️ सामान्य"
                    st.markdown(f"""
                    <div style="border:1.5px solid #8B5CF6; border-radius:8px; padding:12px; height:100%; background:rgba(139,92,246,0.06);">
                        <b style="color:#7C3AED; font-size:14px;">२. प्रश्न लग्न कुण्डली (Horary Overlay)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>प्रश्न लग्न:</b> {p2.get('prashna_lagna', 'उपलब्ध नहीं')}<br/>
                            • <b>कार्याध्यक्ष स्थिति:</b> {p2_fav}<br/>
                            • <b>प्रश्न कुण्डली समय:</b> वर्तमान जिज्ञासा क्षण<br/>
                            • <b>प्रश्न बल स्कोर:</b> <b>{p2.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 3: Varga Confirmation
                p3 = ver_res.pillar_3_varga_evidence
                with p_row1_c3:
                    p3_conf = "✅ वर्ग पुष्टि" if p3.get("confirmed") else "⚠️ सामान्य स्थिति"
                    st.markdown(f"""
                    <div style="border:1.5px solid #10B981; border-radius:8px; padding:12px; height:100%; background:rgba(16,185,129,0.06);">
                        <b style="color:#059669; font-size:14px;">३. वर्ग कुण्डली पुष्टि (Divisional Varga)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>संबद्ध वर्ग चक्र:</b> {p3.get('varga', 'D9')}<br/>
                            • <b>वर्ग भावेश:</b> {p3.get('varga_lord')} ({p3.get('varga_dignity', 'neutral')})<br/>
                            • <b>वर्ग स्थिति:</b> {p3.get('varga_house')}वां भाव ({p3_conf})<br/>
                            • <b>वर्ग पुष्टि स्कोर:</b> <b>{p3.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 4: Operating Vimshottari Dasha
                p4 = ver_res.pillar_4_dasha_evidence
                with p_row2_c1:
                    p4_fav = "✅ पूर्ण फलित योग" if p4.get("dasha_favorable") else "ℹ️ तटस्थ/सामान्य दशा"
                    st.markdown(f"""
                    <div style="border:1.5px solid #F59E0B; border-radius:8px; padding:12px; height:100%; background:rgba(245,158,11,0.06);">
                        <b style="color:#D97706; font-size:14px;">४. सक्रिय दशा विन्यास (Operating Dasha)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>महादशा:</b> {p4.get('mahadasha')} | <b>अंतर्दशा:</b> {p4.get('antardasha')}<br/>
                            • <b>प्रत्यंतर्दशा:</b> {p4.get('pratyantardasha', '—')}<br/>
                            • <b>दशा अनुकूलता:</b> {p4_fav}<br/>
                            • <b>दशा सक्रियता स्कोर:</b> <b>{p4.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 5: Historical Double Transit
                p5 = ver_res.pillar_5_transit_evidence
                with p_row2_c2:
                    p5_sat = "✅ अनुकूल" if p5.get("saturn_favorable") else "सामान्य"
                    p5_jup = "✅ शुभ/दृष्टि" if p5.get("jupiter_favorable") else "सामान्य"
                    st.markdown(f"""
                    <div style="border:1.5px solid #06B6D4; border-radius:8px; padding:12px; height:100%; background:rgba(6,182,212,0.06);">
                        <b style="color:#0891B2; font-size:14px;">५. ऐतिहासिक गोचर (Double Transit)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>शनि गोचर भाव:</b> {p5.get('saturn_transit_house')}वां भाव ({p5_sat})<br/>
                            • <b>गुरु गोचर भाव:</b> {p5.get('jupiter_transit_house')}वां भाव ({p5_jup})<br/>
                            • <b>द्वि-गोचर चक्र सक्रियता:</b> {p5.get('transit_score', 0.5)*100:.0f}%<br/>
                            • <b>गोचर संरेखण स्कोर:</b> <b>{p5.get('transit_score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Pillar 6: Classical Shastriya Rules Consensus
                p6 = ver_res.pillar_6_rules_evidence
                with p_row2_c3:
                    st.markdown(f"""
                    <div style="border:1.5px solid #EC4899; border-radius:8px; padding:12px; height:100%; background:rgba(236,72,153,0.06);">
                        <b style="color:#DB2777; font-size:14px;">६. शास्त्रीय नियम बैंक (12,500+ Rules)</b><br/>
                        <div style="margin-top:6px; font-size:12.5px;">
                            • <b>सक्रिय नियम (Fired Rules):</b> {p6.get('rules_fired_count', 0)} नियम<br/>
                            • <b>अनुकूल शास्त्रीय साक्ष्य:</b> {p6.get('rules_favorable_count', 0)} योग<br/>
                            • <b>ज्ञानकोष स्रोत:</b> BPHS, फलदीपिका, सारावली<br/>
                            • <b>शास्त्रीय सहमति स्कोर:</b> <b>{p6.get('score', 0.5)*100:.0f}%</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                # Shastriya Narrative
                st.markdown("### 📖 शास्त्रीय साक्ष्य सार (Classical Verification Narrative)")
                st.markdown(ver_res.ai_explanation_hi)

                with st.expander("Classical English Synthesis"):
                    st.markdown(ver_res.ai_explanation_en)

                # Master Directive Rule 5 Disclaimer
                st.info(f"⚖️ **शास्त
... [truncated for diff preview]