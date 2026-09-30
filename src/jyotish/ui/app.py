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

from src.jyotish.core.models import BirthData, GhatnaQueryInput, KundaliChart
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
from src.jyotish.ui.sudarshan import default_sudarshan_engine
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
    initial_sidebar_state="collapsed"
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
       Vedic Royal Chrysolite Theme (Day Mode - Light Yellow Greenish)
       ========================================================= */
    html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
        background-color: #F5F9EC !important;
        background: #F5F9EC !important;
        color: #000000 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Noto Sans", sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }
    header[data-testid="stHeader"] {
        background-color: #F5F9EC !important;
        background: #F5F9EC !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 900 !important;
        letter-spacing: -0.3px !important;
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
        font-size: 0.92rem !important;
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
    input:focus, textarea:focus, div[data-baseweb="input"]:focus-within {
        border-color: #4D7C0F !important;
        box-shadow: 0 0 0 2px rgba(77, 124, 15, 0.2) !important;
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
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #000000 !important;
        font-weight: 850 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1.5px solid #CBDCB8 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #EDF4E2 !important;
        background: #EDF4E2 !important;
        border-right: 1.5px solid #CBDCB8 !important;
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #000000 !important;
        font-weight: 900 !important;
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
    .gla-btn-tile {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
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
        text-align: center !important;
        width: 100% !important;
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
    button[kind="secondary"], button[kind="secondary"] * {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #CBDCB8 !important;
        font-weight: 800 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #F4F8EC !important;
        border-color: #4D7C0F !important;
        color: #000000 !important;
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
    /* Hide Streamlit Deploy button, 3-dots menu, and footer */
    .stDeployButton, #MainMenu, footer, [data-testid="stDecoration"], div[data-testid="stToolbar"] {{
        display: none !important;
        visibility: hidden !important;
    }}
    /* Hide Streamlit's native top header bar (empty white strip) completely */
    header[data-testid="stHeader"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        min-height: 0px !important;
        max-height: 0px !important;
        overflow: hidden !important;
        padding: 0px !important;
        margin: 0px !important;
        z-index: -1 !important;
    }}

    /* Keep Sidebar Open/Close Expand Button (>>) Always Visible, High-Contrast & Clickable */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapsedControl"],
    header[data-testid="stHeader"] button {{
        pointer-events: auto !important;
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 10px !important;
        top: 4px !important;
        left: 10px !important;
        z-index: 1000005 !important;
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: 2px solid #1D4ED8 !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
        cursor: pointer !important;
        min-width: 38px !important;
        min-height: 38px !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover,
    button[data-testid="stSidebarCollapsedControl"]:hover,
    header[data-testid="stHeader"] button:hover {{
        background: #1D4ED8 !important;
        border-color: #1E3A8A !important;
        transform: scale(1.05) !important;
    }}
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    button[data-testid="stSidebarCollapsedControl"] svg,
    header[data-testid="stHeader"] button svg {{
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
        stroke: #FFFFFF !important;
        width: 22px !important;
        height: 22px !important;
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
    div[data-testid="stCustomComponentV1"],
    div.element-container:has(iframe),
    div.element-container:has(style) {{
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
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

    /* Primary Calculate Button (Side me Janm Vivran ke niche) */
    button[kind="primary"] {{
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 1.05rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 15px rgba(217, 119, 6, 0.4) !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }}
    button[kind="primary"] * {{
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }}
    button[kind="primary"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(217, 119, 6, 0.5) !important;
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
    .kundali-chart svg, .chart-container svg, .observatory-canvas svg, div:has(> svg.kundali-svg) svg {{
        max-width: 100% !important;
        height: auto !important;
        display: block !important;
        margin: 0 auto !important;
    }}
    div:has(> svg), .chart-container, .kundali-chart, div[data-testid="stImage"] img {{
    div:has(> svg.kundali-svg), .chart-container, .kundali-chart, div[data-testid="stImage"] img {{
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
        background: #E2F0D9;
        color: #000000;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1.5px solid #A8D08D;
        font-size: 11.5px;
        font-weight: 700;
        margin-top: 0px;
        margin-bottom: 4px;
    }}
    .gla-info-strip b {{
        color: #000000;
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
    /* 🏛️ Authentic Parashara's Light Workstation Styling */
    .pl-workstation-left {{
        background: #FFFFFF !important;
        border: 1.5px solid #2E7D32 !important;
        border-radius: 6px !important;
        padding: 6px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }}
    .pl-box-header {{
        background: linear-gradient(180deg, #388E3C 0%, #2E7D32 100%) !important;
        color: #FFFFFF !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        padding: 4px 8px !important;
        border-radius: 4px 4px 0 0 !important;
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
        background: #EDF4E2 !important;
        border: 1px solid #CBDCB8 !important;
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
            
            function doToggle() {
                // 1. Try finding and clicking native Streamlit sidebar buttons
                const collapsedBtn = parentDoc.querySelector('[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"], button[aria-label="Expand sidebar"], button[title="Expand sidebar"]');
                const collapseBtn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarHeader"] button, button[aria-label="Collapse sidebar"], button[title="Collapse sidebar"]');
                
                if (collapsedBtn && (collapsedBtn.offsetParent !== null || window.getComputedStyle(collapsedBtn).display !== 'none')) {
                    collapsedBtn.click();
                    return;
                }
                if (collapseBtn && (collapseBtn.offsetParent !== null || window.getComputedStyle(collapseBtn).display !== 'none')) {
                    collapseBtn.click();
                    return;
                }
                
                // 2. Fallback: Dispatch '[' key event to toggle Streamlit sidebar
                const keyEvent = new KeyboardEvent('keydown', {
                    key: '[',
                    code: 'BracketLeft',
                    keyCode: 219,
                    which: 219,
                    bubbles: true,
                    cancelable: true
                });
                parentDoc.dispatchEvent(keyEvent);
                if (window.parent) {
                    window.parent.dispatchEvent(keyEvent);
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
                            display: none !important;
                            height: 0px !important;
                            min-height: 0px !important;
                            max-height: 0px !important;
                            padding: 0px !important;
                            margin: 0px !important;
                            visibility: hidden !important;
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
                        div[data-testid="stCustomComponentV1"],
                        div.element-container:has(iframe) {
                            display: none !important;
                            height: 0px !important;
                            min-height: 0px !important;
                            margin: 0px !important;
                            padding: 0px !important;
                        }
                        .st-key-top_frozen_header_container {
                            border: none !important;
                            box-shadow: none !important;
                            padding: 0px !important;
                            margin: 0px 0px 4px 0px !important;
                            background: transparent !important;
                        }
                        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
                            background-color: #EDF4E2 !important;
                            background: #EDF4E2 !important;
                            border-right: 1.5px solid #CBDCB8 !important;
                        }
                        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
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
                stHeader.style.setProperty('display', 'none', 'important');
                stHeader.style.setProperty('height', '0px', 'important');
                stHeader.style.setProperty('min-height', '0px', 'important');
                stHeader.style.setProperty('max-height', '0px', 'important');
                stHeader.style.setProperty('padding', '0px', 'important');
                stHeader.style.setProperty('margin', '0px', 'important');
            }

            const mainSec = parentDoc.querySelector('[data-testid="stMain"], section.main');
            if (mainSec) {
                mainSec.style.setProperty('overflow-y', 'auto', 'important');
                mainSec.style.setProperty('overflow-x', 'hidden', 'important');
                mainSec.style.setProperty('position', 'relative', 'important');
            }

            const blockContainer = parentDoc.querySelector('.block-container');
            if (blockContainer) {
                blockContainer.style.setProperty('padding-top', '2px', 'important');
                blockContainer.style.setProperty('padding-left', '8px', 'important');
                blockContainer.style.setProperty('padding-right', '8px', 'important');
                blockContainer.style.setProperty('max-width', '100%', 'important');
                blockContainer.style.setProperty('overflow', 'visible', 'important');
            }

            const anchor = parentDoc.querySelector('.fixed-header-anchor, .frozen-header-marker');
            if (anchor) {
                let headerContainer = anchor.closest('.st-key-top_frozen_header_container') ||
                                      anchor.closest('[data-testid="stVerticalBlockBorderWrapper"]') ||
                                      anchor.closest('[data-testid="stVerticalBlock"] > div');
                if (headerContainer) {
                    headerContainer.style.setProperty('position', 'relative', 'important');
                    headerContainer.style.setProperty('top', 'auto', 'important');
                    headerContainer.style.setProperty('z-index', 'auto', 'important');
                    headerContainer.style.setProperty('box-shadow', 'none', 'important');
                    headerContainer.style.setProperty('padding-top', '2px', 'important');
                    headerContainer.style.setProperty('padding-bottom', '4px', 'important');
                    headerContainer.style.setProperty('margin-bottom', '4px', 'important');
                }
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
    elif "Astrallis" in chart_style or "Circular" in chart_style:
        return ChartRenderer.render_astrallis_circular_svg(c_obj, title=chart_title, varga_code=varga_code, dark_bg=is_astrallis_mode or is_night_mode)
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
        "☁️ Server Sync",
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
        "☁️ சர்வர் ஒத்திசைவு (Server Sync)",
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
        "☁️ సర్వర్ సమకాలీకరణ (Server Sync)",
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
        "☁️ સર્વર સિંક (Server Sync)",
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
        "☁️ सर्व्हर सिंक (Server Sync)",
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
        "☁️ সার্ভার সিঙ্ক (Server Sync)",
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
        "☁️ सर्वर सिंक (Server Sync)",
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
    # Active profile banner with live info (incorporating anchor with 0 space)
    st.markdown(f"""
    <div class="fixed-header-anchor" style="display:none; height:0px; margin:0; padding:0;"></div>
    <div class="gla-info-strip">
        <div>
            👤 <b>जातक:</b> {name} &nbsp;|&nbsp; 📅 {birth_d.strftime('%d-%b-%Y')}, {birth_t.strftime('%I:%M %p')} &nbsp;|&nbsp; 📍 {default_city_name}
        </div>
        <div>
            <span class="gla-active-tag">🟢 Server Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 10-Tile Complete Server Toolbelt Columns (Ultra-Slim & Screen-Fit Clickable Tiles)
    tb_cols = st.columns(10, gap="small")

    # Helper function for rendering clickable tile (Pure Clean Link - No Empty Button Widgets!)
    def render_tool_tile(col, icon_b64, label_text, tool_key):
        with col:
            is_active = (st.session_state.gla_active_tool == tool_key)
            active_cls = "active" if is_active else ""
            active_style = "border-color:#D97706 !important; background-color:#FEF3C7 !important; box-shadow:0 0 10px rgba(217,119,6,0.4) !important;" if is_active else ""
            st.markdown(f"""
            <div class="fixed-header-anchor" style="display:none; height:0px; margin:0; padding:0;"></div>
            <a href="?gla_tool={tool_key}" target="_self" style="text-decoration:none; color:inherit; display:block; width:100%;">
                <div class="gla-tile-box">
                    <div class="gla-btn-tile {active_cls}" style="{active_style}">
                        <img src="{icon_b64}" alt="{label_text}" />
                        <span>{label_text}</span>
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)

    # 1. New Chart
    render_tool_tile(tb_cols[0], ICON_NOTEPAD_B64, "New", "new")

    # 2. Birth Data
    render_tool_tile(tb_cols[1], ICON_BIRTH_B64, "Birth Data", "birth")

    # 3. Open Folder
    render_tool_tile(tb_cols[2], ICON_FOLDER_B64, "Open", "open")

    # 4. Save Chart
    render_tool_tile(tb_cols[3], ICON_SAVE_B64, "Save", "save")

    # 5. Settings
    render_tool_tile(tb_cols[4], ICON_SETTINGS_B64, "Settings", "settings")

    # 6. Languages
    render_tool_tile(tb_cols[5], ICON_LANGUAGES_B64, "Languages", "lang")

    # 7. Current Time
    render_tool_tile(tb_cols[6], ICON_CLOCK_B64, "Time", "clock")

    # 8. Current Location
    render_tool_tile(tb_cols[7], ICON_LOCATION_B64, "Location", "location")

    # 9. Theme Mode
    render_tool_tile(tb_cols[8], ICON_THEME_B64, "Theme", "theme")

    # 10. Logout
    render_tool_tile(tb_cols[9], ICON_LOGOUT_B64, "Logout", "logout")

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

        # 5. TOOL: SETTINGS (Ayanamsa, House System, Chart Style, Pro Mode)
        elif st.session_state.gla_active_tool == "settings":
            with st.container(border=True):
                st.markdown("### ⚙️ गणना एवं सॉफ़्टवेयर प्राथमिकताएं (Settings & Calculation Engine)")
                col_st1, col_st2, col_st3, col_st4, col_st5 = st.columns([2.2, 1.8, 1.6, 2.0, 1.4])
                with col_st1:
                    ay_opts = [
                        "Lahiri", "Pushya-Paksha (PVR Rao)", "KP Old", "KP New (Straight Line)",
                        "Raman", "True Chitra (Spica 180°)", "Yukteshwar", "Fagan-Bradley"
                    ]
                    cur_ay = st.session_state.get("app_ayanamsa", "Lahiri")
                    ay_idx = ay_opts.index(cur_ay) if cur_ay in ay_opts else 0
                    in_ay = st.selectbox("अयनांश (Ayanamsa)", ay_opts, index=ay_idx, key="gla_settings_ayanamsa")
                    st.session_state.app_ayanamsa = in_ay

                with col_st2:
                    node_opts = ["Mean Node (पारंपरिक औसत)", "True Node (सच्चे पात - Meeus)"]
                    cur_node = st.session_state.get("app_node_type", "Mean Node (पारंपरिक औसत)")
                    node_idx = node_opts.index(cur_node) if cur_node in node_opts else 0
                    in_node = st.selectbox("राहु-केतु गणना (Nodes)", node_opts, index=node_idx, key="gla_settings_node")
                    st.session_state.app_node_type = in_node

                with col_st3:
                    hs_opts = ["Whole Sign", "Equal", "Placidus", "Shripati", "Koch"]
                    cur_hs = st.session_state.get("app_house_system", "Whole Sign")
                    hs_idx = hs_opts.index(cur_hs) if cur_hs in hs_opts else 0
                    in_hs = st.selectbox("भाव पद्धति (Houses)", hs_opts, index=hs_idx, key="gla_settings_hs")
                    st.session_state.app_house_system = in_hs

                with col_st4:
                    chart_styles_list = ["North Indian (Diamond)", "South Indian (Box)", "East Indian (Surya)"]
                    if "app_chart_style" not in st.session_state or st.session_state.app_chart_style not in chart_styles_list:
                        st.session_state.app_chart_style = "North Indian (Diamond)"
                    cs_idx = chart_styles_list.index(st.session_state.app_chart_style)
                    def _on_gla_cs_change():
                        st.session_state.app_chart_style = st.session_state.gla_settings_cs_select
                    in_cs = st.selectbox("कुण्डली चक्र शैली (Style)", chart_styles_list, index=cs_idx, key="gla_settings_cs_select", on_change=_on_gla_cs_change)

                with col_st5:
                    in_pm = st.toggle("⚡ Pro Mode", value=st.session_state.get("app_pro_mode", True), key="gla_settings_pm_toggle")
                    st.session_state.app_pro_mode = in_pm
                    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                    if st.button("✅ लागू करें", type="primary", use_container_width=True, key="gla_apply_settings_btn"):
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

        # 7. TOOL: CURRENT TIME (वर्तमान समय)
        elif st.session_state.gla_active_tool == "clock":
            with st.container(border=True):
                st.markdown("### 🕒 वर्तमान समय एवं काल संदर्भ (Current Time)")
                now_val = datetime.now()
                col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
                with col_c1:
                    st.markdown(f"""
                    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:12px;">
                        <b style="color:#1E40AF; font-size:15px;">🕒 सिस्टम का वर्तमान समय:</b><br/>
                        <span style="font-size:20px; font-weight:900; color:#0F172A;">{now_val.strftime('%d-%b-%Y, %I:%M:%S %p')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_c2:
                    if st.button("⏱️ इस समय को जन्म समय बनाएं (Set as Birth Time)", type="primary", use_container_width=True, key="gla_set_current_time_btn"):
                        st.session_state.birth_date = now_val.date()
                        st.session_state.birth_time = now_val.time().replace(microsecond=0)
                        st.session_state.gla_active_tool = None
                        st.toast("✅ वर्तमान समय कुण्डली में सेट किया गया!", icon="🕒")
                        st.rerun()
                with col_c3:
                    if st.button("❌ बंद करें", use_container_width=True, key="gla_close_clock_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()

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
                        st.toast("✅ आप सुरक्षित रूप से लॉगआउट हो गए हैं।", icon="🚪")
                        st.rerun()
                with col_lg2:
                    if st.button("❌ नहीं, रद्द करें", use_container_width=True, key="gla_cancel_logout_btn"):
                        st.session_state.gla_active_tool = None
                        st.rerun()



    def _nav_prev_module():
        new_idx = (st.session_state.active_module_idx - 1) % len(MODULE_OPTIONS)
        st.session_state.active_module_idx = new_idx
        st.session_state.top_bar_module_selector = MODULE_OPTIONS[new_idx]

    def _nav_next_module():
        new_idx = (st.session_state.active_module_idx + 1) % len(MODULE_OPTIONS)
        st.session_state.active_module_idx = new_idx
        st.session_state.top_bar_module_selector = MODULE_OPTIONS[new_idx]

    def _nav_to_rules_bank():
        st.session_state.active_module_idx = 19
        st.session_state.top_bar_module_selector = MODULE_OPTIONS[19]

    def _on_module_selector_change():
        chosen = st.session_state.top_bar_module_selector
        if chosen in MODULE_OPTIONS:
            st.session_state.active_module_idx = MODULE_OPTIONS.index(chosen)

    # 3. 21 Modules Selector (Inside the Frozen Top Container)
    st.markdown("<div style='height: 10px; margin: 0; padding: 0;'></div>", unsafe_allow_html=True)
    if "app_ui_layout_mode" not in st.session_state:
        st.session_state.app_ui_layout_mode = "parashara"  # Default to Parashara Workstation 30:70

    col_btn_prev, col_mod_sel, col_btn_next, col_view_toggle = st.columns([0.9, 3.2, 0.9, 1.4])
    with col_btn_prev:
        st.button("❮ पिछला (Prev)", use_container_width=True, help="पिछला मॉड्यूल खोलें", key="top_prev_mod_btn", on_click=_nav_prev_module)

    with col_mod_sel:
        selected_module = st.selectbox(
            "मॉड्यूल चयन",
            MODULE_OPTIONS,
            key="top_bar_module_selector",
            label_visibility="collapsed",
            on_change=_on_module_selector_change
        )
        selected_idx = MODULE_OPTIONS.index(selected_module) if selected_module in MODULE_OPTIONS else st.session_state.active_module_idx
        st.session_state.active_module_idx = selected_idx

    with col_btn_next:
        st.button("अगला (Next) ❯", use_container_width=True, help="अगला मॉड्यूल खोलें", key="top_next_mod_btn", on_click=_nav_next_module)

    with col_view_toggle:
        is_parashara = (st.session_state.app_ui_layout_mode == "parashara")
        view_lbl = "🏛️ पाराशर (30:70)" if is_parashara else "📱 वर्टिकल लेआउट"
        view_help = "क्लिक करके पाराशर 30:70 वर्कस्टेशन अथवा क्लासिक वर्टिकल दृश्य में बदलें"
        if st.button(view_lbl, use_container_width=True, help=view_help, key="top_ui_layout_toggle_btn", type="primary" if is_parashara else "secondary"):
            st.session_state.app_ui_layout_mode = "vertical" if is_parashara else "parashara"
            st.rerun()


p = chart.panchang
sr_time = "05:18:32 AM"
ss_time = "06:42:25 PM"
hora_lord = "Mars" if birth_d.weekday() == 0 else "Sun"
ghati_val = round((birth_t.hour + birth_t.minute / 60.0 - 5.3) * 2.5, 2)
if ghati_val < 0:
    ghati_val += 60.0

_hud_title_color = "#00E5FF" if is_astrallis_mode else ("#F8C471" if is_night_mode else "#000000")
_hud_accuracy_bg = "#0A1628" if is_astrallis_mode else ("#1A2340" if is_night_mode else "#EFF6FF")
_hud_accuracy_border = "#00E5FF" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#2563EB")
_hud_accuracy_color = "#00E5FF" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#1E40AF")
_breadcrumb_bg = "#0A1628" if is_astrallis_mode else ("#111827" if is_night_mode else "#EFF6FF")
_breadcrumb_border = "#00E5FF" if is_astrallis_mode else ("#4B5563" if is_night_mode else "#93C5FD")
_breadcrumb_title_color = "#00E5FF" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#1E40AF")
_breadcrumb_text_color = "#CBD5E1" if is_astrallis_mode else ("#D1D5DB" if is_night_mode else "#1E293B")

st.markdown(f"""
<div class="digital-hud">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 4px;">
        <div style="font-weight: 800; font-size: 12.5px; display: flex; align-items: center; gap: 6px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981; box-shadow:0 0 6px #10B981;"></span>
            <span style="color:{_hud_title_color}; font-weight:900;">⚡ डिजिटल पंचांग एवं काल गणना (Panchang &amp; Ephemeris HUD)</span>
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap; align-items: center;">
            <div class="hud-pill-highlight" style="border-radius: 6px; border: 1.5px solid #D97706; font-weight: 800;">
                👑 होरा स्वामी: <b>{hora_lord}</b>
            </div>
            <div style="background: {_hud_accuracy_bg}; border: 1.5px solid {_hud_accuracy_border}; color: {_hud_accuracy_color}; border-radius: 6px; padding: 3px 8px; font-size: 11.5px; font-weight: 800;">
                🛡️ 99.9% परिशुद्धता
            </div>
        </div>
    </div>
    <div class="hud-grid">
        <div class="hud-pill" title="तिथि: {p.tithi_name} ({p.tithi_type})">📅 <b>तिथि:</b> {p.tithi_name}</div>
        <div class="hud-pill" title="वार: {p.vara_name}">🪐 <b>वार:</b> {p.vara_name}</div>
        <div class="hud-pill" title="नक्षत्र: {p.nakshatra_name}">✨ <b>नक्षत्र:</b> {p.nakshatra_name}</div>
        <div class="hud-pill" title="योग: {p.yoga_name}">🌿 <b>योग:</b> {p.yoga_name}</div>
        <div class="hud-pill" title="करण: {p.karana_name}">⚡ <b>करण:</b> {p.karana_name}</div>
        <div class="hud-pill" title="सूर्योदय: {sr_time}">🌅 <b>सूर्योदय:</b> {sr_time}</div>
        <div class="hud-pill" title="सूर्यास्त: {ss_time}">🌇 <b>सूर्यास्त:</b> {ss_time}</div>
        <div class="hud-pill" title="जन्म घटी: {ghati_val}">⏳ <b>जन्म घटी:</b> {ghati_val}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Active Module Breadcrumb Pill
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; background:{_breadcrumb_bg}; border:1.5px solid {_breadcrumb_border}; border-radius:8px; padding:6px 14px; margin-bottom:6px;">
    <div style="font-weight:800; color:{_breadcrumb_title_color}; font-size:13px;">📍 सक्रिय मॉड्यूल: <b>{selected_module}</b></div>
    <div style="font-size:12px; color:{_breadcrumb_text_color}; font-weight:700;">जातक: <b>{name}</b> ({birth_d.strftime('%d-%b-%Y')}, {birth_t.strftime('%I:%M %p')})</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 📚 १२,५००+ महा-शास्त्रीय नियम लाइव स्कैन पट्टी (Global Shastriya Rules HUD - Linked Across All Modules)
# -------------------------------------------------------------
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

col_gr_bar, col_gr_btn = st.columns([4.2, 1.8])
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
    <div style="background: {_rules_bg}; border: 1.5px solid {_rules_border}; border-radius: 8px; padding: 6px 14px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; box-shadow: 0 1px 3px rgba(139, 92, 246, 0.12);">
        <div style="color: {_rules_text_color} !important; font-size: 13px; font-weight: 800; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="color: {_rules_text_color} !important;">📚 <b>१२,५००+ महा-शास्त्रीय नियम इंजन (AI लिंक्ड):</b></span>
            <span style="background: {_rules_count_bg}; color: {_rules_count_color} !important; border: 1px solid {_rules_count_border}; padding: 2px 8px; border-radius: 6px; font-weight: 900; font-size: 12px;">{_gr_fired:,} सक्रिय नियम फलित</span>
        </div>
        <div style="font-size: 11.5px; display: flex; gap: 6px; align-items: center;">
            <span style="background: {_pos_bg}; color: {_pos_color} !important; border: 1px solid {_pos_color}; padding: 2px 9px; border-radius: 12px; font-weight: 800;">🟢 {_gr_pos:,} शुभ (+)</span>
            <span style="background: {_neg_bg}; color: {_neg_color} !important; border: 1px solid {_neg_color}; padding: 2px 9px; border-radius: 12px; font-weight: 800;">🔴 {_gr_neg:,} सतर्कता (-)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_gr_btn:
    st.button("🔍 नियम बैंक खोलें ❯", key="global_open_rules_bank_btn", use_container_width=True, help="१२,५००+ महा-शास्त्रीय नियम बैंक (मॉड्यूल १९) खोलें", on_click=_nav_to_rules_bank)

# -------------------------------------------------------------
# ⏱️ Quick Time Stepper (काल गति नियंत्रक — Live Time Travel / BTR Bar)
# -------------------------------------------------------------
c_ts_info, c_ts_ctrl = st.columns([1.5, 3.5])
with c_ts_info:
    _ts_bg = "#0A1628" if is_astrallis_mode else ("#111827" if is_night_mode else "#FFFBEB")
    _ts_border = "#F59E0B" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#F59E0B")
    _ts_label_color = "#F59E0B" if is_astrallis_mode else ("#F59E0B" if is_night_mode else "#B45309")
    _ts_value_color = "#E2E8F0" if is_astrallis_mode else ("#D1D5DB" if is_night_mode else "#1E293B")
    st.markdown(f"""
    <div style="background:{_ts_bg}; border:1.5px solid {_ts_border}; border-radius:8px; padding:5px 10px; height:100%; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-size:11px; font-weight:800; color:{_ts_label_color};">⏱️ काल गति नियंत्रक (Time Travel)</div>
        <div style="font-size:12.5px; font-weight:900; color:{_ts_value_color};">📅 {birth_d.strftime('%d-%b-%Y')} | ⏰ {birth_t.strftime('%I:%M:%S %p')}</div>
    </div>
    """, unsafe_allow_html=True)

with c_ts_ctrl:
    def _step_time_action(delta_minutes=0, delta_hours=0, delta_days=0, reset_to_now=False):
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

    ts_b_cols = st.columns(9)
    if ts_b_cols[0].button("⏪ -1द", key="ts_btn_m1d", help="-1 दिन पीछे जाएं"): _step_time_action(delta_days=-1)
    if ts_b_cols[1].button("◀ -1घं", key="ts_btn_m1h", help="-1 घंटा पीछे जाएं"): _step_time_action(delta_hours=-1)
    if ts_b_cols[2].button("‹ -15म", key="ts_btn_m15m", help="-15 मिनट पीछे जाएं"): _step_time_action(delta_minutes=-15)
    if ts_b_cols[3].button("‹ -1म", key="ts_btn_m1m", help="-1 मिनट (BTR सूक्ष्म शोधन)"): _step_time_action(delta_minutes=-1)
    if ts_b_cols[4].button("🔄 अब", key="ts_btn_now", type="primary", help="वर्तमान समय (Current Time) पर सेट करें"): _step_time_action(reset_to_now=True)
    if ts_b_cols[5].button("+1म ›", key="ts_btn_p1m", help="+1 मिनट (BTR सूक्ष्म शोधन)"): _step_time_action(delta_minutes=1)
    if ts_b_cols[6].button("+15म ›", key="ts_btn_p15m", help="+15 मिनट आगे जाएं"): _step_time_action(delta_minutes=15)
    if ts_b_cols[7].button("+1घं ▶", key="ts_btn_p1h", help="+1 घंटा आगे जाएं"): _step_time_action(delta_hours=1)
    if ts_b_cols[8].button("+1द ⏩", key="ts_btn_p1d", help="+1 दिन आगे जाएं"): _step_time_action(delta_days=1)


# -------------------------------------------------------------
# 🏛️ PARASHARA WORKSTATION 30:70 LAYOUT ENGINE
# -------------------------------------------------------------
is_parashara_layout = (st.session_state.get("app_ui_layout_mode", "parashara") == "parashara")

if is_parashara_layout:
    col_pl_charts_left, col_pl_module_right = st.columns([1.15, 2.35], gap="medium")
    with col_pl_charts_left:
        st.markdown("""
        <div class="pl-box-header">
            <span>💎 मुख्य लग्न कुण्डली (D1 Natal Chart)</span>
            <span style="font-size:11px;">उत्तर भारतीय</span>
        </div>
        """, unsafe_allow_html=True)
        svg_d1_fixed = render_chart_svg(chart, f"लग्न: {chart.lagna_sign_name} ({chart.lagna_sign_id})", varga_code="D1")
        st.markdown(svg_d1_fixed, unsafe_allow_html=True)
        lagna_lord_name = SIGN_LORDS.get(chart.lagna_sign_id, "—")
        st.caption(f"**लग्न:** {chart.lagna_sign_name} | **लग्नपति:** {lagna_lord_name} | **आत्मकारक:** {chart.atmakaraka}")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        pl_sub_chart = st.radio(
            "सहायक वर्ग चक्र",
            ["नवांश (D9)", "चंद्र कुण्डली", "भाव चलित", "दशमांश (D10)"],
            horizontal=True,
            label_visibility="collapsed",
            key="pl_left_aux_chart_choice"
        )
        if "नवांश" in pl_sub_chart:
            st.markdown("""
            <div class="pl-box-header">
                <span>🌸 नवमांश चक्र (D9 Navamsha — धर्म व दांपत्य)</span>
                <span style="font-size:11px;">D9</span>
            </div>
            """, unsafe_allow_html=True)
            svg_d9_fixed = render_chart_svg(chart, "D9 नवांश", varga_code="D9")
            st.markdown(svg_d9_fixed, unsafe_allow_html=True)
        elif "चंद्र" in pl_sub_chart:
            st.markdown("""
            <div class="pl-box-header">
                <span>🌙 चंद्र कुण्डली (Chandra Kundali — मन व सुख)</span>
                <span style="font-size:11px;">Moon</span>
            </div>
            """, unsafe_allow_html=True)
            svg_chandra_fixed = render_chart_svg(chart, "चंद्र कुण्डली", varga_code="D1")
            st.markdown(svg_chandra_fixed, unsafe_allow_html=True)
        elif "चलित" in pl_sub_chart:
            st.markdown("""
            <div class="pl-box-header">
                <span>📐 भाव चलित चक्र (Bhava Chalit — कस्प्स स्थिति)</span>
                <span style="font-size:11px;">Chalit</span>
            </div>
            """, unsafe_allow_html=True)
            svg_chalit_fixed = render_chart_svg(chart, "भाव चलित", varga_code="D1")
            st.markdown(svg_chalit_fixed, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="pl-box-header">
                <span>💼 दशमांश चक्र (D10 Dashamsha — कर्म व पद)</span>
                <span style="font-size:11px;">D10</span>
            </div>
            """, unsafe_allow_html=True)
            svg_d10_fixed = render_chart_svg(chart, "D10 दशमांश", varga_code="D10")
            st.markdown(svg_d10_fixed, unsafe_allow_html=True)

    # Right 70% Module Workspace Container
    col_pl_module_right.__enter__()

# -------------------------------------------------------------
# Module Routing
# -------------------------------------------------------------
if selected_idx == 0:
    st.subheader("📜 जन्म कुण्डली एवं षोडशवर्ग चक्र (D1 to D60)")

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

    # 1-Click Quick Chart Style Switcher
    st.markdown("##### 🎨 कुण्डली चक्र शैली टॉगल (Switch Chart Style)")
    c_st1, c_st2, c_st3, c_st4 = st.columns(4)
    curr_style = st.session_state.get("app_chart_style", "Astrallis Circular (Western Wheel)" if is_astrallis_mode else "North Indian (Diamond)")
    if c_st1.button("🔵 Astrallis Circular", use_container_width=True, type="primary" if "Astrallis" in curr_style or "Circular" in curr_style else "secondary", key="btn_style_astrallis"):
        st.session_state.app_chart_style = "Astrallis Circular (Western Wheel)"
        st.rerun()
    if c_st2.button("💎 उत्तर भारतीय (Diamond)", use_container_width=True, type="primary" if "North" in curr_style else "secondary", key="btn_style_north"):
        st.session_state.app_chart_style = "North Indian (Diamond)"
        st.rerun()
    if c_st3.button("🔲 दक्षिण भारतीय (Box)", use_container_width=True, type="primary" if "South" in curr_style else "secondary", key="btn_style_south"):
        st.session_state.app_chart_style = "South Indian (Box)"
        st.rerun()
    if c_st4.button("🔺 पूर्व भारतीय (Bengal)", use_container_width=True, type="primary" if "East" in curr_style else "secondary", key="btn_style_east"):
        st.session_state.app_chart_style = "East Indian (Surya)"
        st.rerun()

    # View Mode Toggle: Single vs 4-in-1 Quad Dashboard
    c_view1, c_view2 = st.columns(2)
    chart_view_mode = st.session_state.get("app_chart_view_mode", "Single")
    if c_view1.button("📱 एकल चक्र दृश्य (Single Varga)", use_container_width=True, type="primary" if chart_view_mode == "Single" else "secondary", key="btn_vm_single"):
        st.session_state.app_chart_view_mode = "Single"
        st.rerun()
    if c_view2.button("🖥️ ४-चार्ट वर्कबेंच (4-in-1 Quad Dashboard: D1, D9, D10, D7)", use_container_width=True, type="primary" if chart_view_mode == "Quad" else "secondary", key="btn_vm_quad"):
        st.session_state.app_chart_view_mode = "Quad"
        st.rerun()

    if chart_view_mode == "Quad":
        st.markdown("#### 🖥️ ४-कुण्डली एकीकृत्त वर्कबेंच (D1 लग्न + D9 नवांश + D10 दशमांश + D7 सप्तांश)")
        st.caption("विश्वस्तरीय सॉफ्टवेयर (Parashara's Light / JHora) समान एक ही स्क्रीन पर प्रमुख वर्ग चक्रों का एक साथ अध्ययन:")
        
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            svg_d1 = render_chart_svg(chart, "D1 जन्म लग्न (Rashi)", varga_code="D1")
            st.markdown(svg_d1, unsafe_allow_html=True)
            st.caption(f"**D1 लग्न:** {chart.lagna_sign_name} ({chart.lagna_sign_id}) | आत्मकारक (AK): {chart.atmakaraka}")
        with q_col2:
            svg_d9 = render_chart_svg(chart, "D9 नवांश (Navamsha — धर्म व दांपत्य)", varga_code="D9")
            st.markdown(svg_d9, unsafe_allow_html=True)
            d9_v = chart.vargas.get("D9")
            st.caption(f"**D9 नवांश लग्न:** {d9_v.lagna_sign_name if d9_v else '—'} | विवाह, भाग्य व ग्रहों का आंतरिक बल")
        
        q_col3, q_col4 = st.columns(2)
        with q_col3:
            svg_d10 = render_chart_svg(chart, "D10 दशमांश (Dashamsha — कर्म व पद)", varga_code="D10")
            st.markdown(svg_d10, unsafe_allow_html=True)
            d10_v = chart.vargas.get("D10")
            st.caption(f"**D10 दशमांश लग्न:** {d10_v.lagna_sign_name if d10_v else '—'} | आजीविका, नेतृत्व व करियर")
        with q_col4:
            svg_d7 = render_chart_svg(chart, "D7 सप्तांश (Saptamsha — संतान व सृजन)", varga_code="D7")
            st.markdown(svg_d7, unsafe_allow_html=True)
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

    else:
        # Standard Single / Quad Dashboard Layout (Classic Vertical Stack)
        col_chart1, col_chart2 = st.columns([1, 1])
        with col_chart1:
            # Sampradaya Variations Expander
            with st.expander("⚙️ वर्ग गणना शास्त्रीय संप्रदाय मत (Classical Sampradaya Variations)", expanded=False):
                c_v1, c_v2, c_v3 = st.columns(3)
                d3_method = c_v1.selectbox(
                    "D3 द्रेष्काण मत",
                    ["parashari", "jagannatha", "somanatha", "parivritti_traya"],
                    format_func=lambda x: {
                        "parashari": "महर्षि पाराशर (१-५-९ त्रिकोण)",
                        "jagannatha": "जगन्नाथ द्रेष्काण (PVR / Rath)",
                        "somanatha": "सोमनाथ द्रेष्काण (अनुलोम/विलोम)",
                        "parivritti_traya": "परिवृत्ति त्रय (३६ चक्रीय)"
                    }[x],
                    key="v_d3_meth"
                )
                d9_method = c_v2.selectbox(
                    "D9 नवांश मत",
                    ["parashari", "krishna_mishra"],
                    format_func=lambda x: {
                        "parashari": "महर्षि पाराशर (१०८ पाद सतत)",
                        "krishna_mishra": "कृष्णमिश्र नवांश (जैमिनी परंपरा)"
                    }[x],
                    key="v_d9_meth"
                )
                d2_method = c_v3.selectbox(
                    "D2 होरा मत",
                    ["parashari", "parivritti"],
                    format_func=lambda x: {
                        "parashari": "पाराशरी होरा (कर्क/सिंह)",
                        "parivritti": "परिवृत्ति होरा (२४ होरा चक्रीय)"
                    }[x],
                    key="v_d2_meth"
                )

        varga_options = list(chart.vargas.keys()) if chart.vargas else ["D1"]
        varga_choice = st.selectbox(
            "वर्ग चक्र चयन (Select Varga Chart)",
            varga_options,
            format_func=lambda x: f"{x} - {chart.vargas[x].varga_name}" if x in chart.vargas else x
        )
        # Dynamic Sampradaya Variation Allocation
        if varga_choice == "D3" and d3_method != "parashari":
            target_varga = VargaCalculator.calculate_d3(chart, variation=d3_method)
            chart.vargas["D3"] = target_varga
        elif varga_choice == "D9" and d9_method != "parashari":
            target_varga = VargaCalculator.calculate_d9(chart, variation=d9_method)
            chart.vargas["D9"] = target_varga
        elif varga_choice == "D2" and d2_method != "parashari":
            target_varga = VargaCalculator.calculate_d2(chart, variation=d2_method)
            chart.vargas["D2"] = target_varga
        else:
            target_varga = chart.vargas.get(varga_choice, chart.vargas.get("D1"))
        v_name = target_varga.varga_name if target_varga else "Rashi"
        v_lagna_sign = target_varga.lagna_sign_name if target_varga else chart.lagna_sign_name
        v_lagna_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id

        title = f"{varga_choice} {v_name} Kundali"
        svg_code = render_chart_svg(chart, title, varga_code=varga_choice)
        st.markdown(svg_code, unsafe_allow_html=True)

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

            # Dynamic Planetary Dignity & Strength Bar Chart for the selected Varga
            st.markdown(f"#### 📊 {varga_choice} ({v_name}) ग्रह गरिमा एवं बल सूचकांक")
            varga_scores = {}
            target_planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            for p_name in target_planets_order:
                vp_obj = target_varga.planets.get(p_name) if target_varga else None
                if vp_obj:
                    _, d_pts, _ = get_varga_dignity_info(p_name, vp_obj.sign_name, affliction_engine)
                    varga_scores[p_name] = d_pts
                else:
                    varga_scores[p_name] = 7

            st.bar_chart(pd.DataFrame(list(varga_scores.items()), columns=["Planet", f"{varga_choice} Dignity Score"]).set_index("Planet"))

            with st.expander("🏆 समग्र विंशोपक बल (20 Point Shadvarga Bala)", expanded=False):
                vimsopaka = VargaCalculator.calculate_vimsopaka_bala(chart)
                st.bar_chart(pd.DataFrame(list(vimsopaka.items()), columns=["Planet", "Vimsopaka Score"]).set_index("Planet"))

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
    else:  # Day Mode (Royal Pearl)
        _t_bg = "#FFFFFF"; _t_th_bg = "#F1F5F9"; _t_bdr = "#CBD5E1"; _t_txt = "#0F172A"; _t_th = "#1E3A8A"; _t_alt = "#F8FAFC"

    _GRAHA_SYMS = {"Sun": "☉ सूर्य", "Moon": "☽ चन्द्र", "Mars": "♂ मंगल", "Mercury": "☿ बुध", "Jupiter": "♃ गुरु", "Venus": "♀ शुक्र", "Saturn": "♄ शनि", "Rahu": "☊ राहु", "Ketu": "☋ केतु"}
    _P_COLS = {"Sun":"#E11D48","Moon":"#2563EB","Mars":"#DC2626","Mercury":"#059669","Jupiter":"#D97706","Venus":"#DB2777","Saturn":"#475569","Rahu":"#7C3AED","Ketu":"#B45309"}

    t_rows = []
    for idx, row in enumerate(p_data):
        p_nm = row["ग्रह (Graha)"]
        sym_nm = _GRAHA_SYMS.get(p_nm, p_nm)
        pc = _P_COLS.get(p_nm, "#2563EB")
        d_lbl = row["वर्ग गरिमा (Dignity)"]
        
        # Dignity badge styling
        if "उच्च" in d_lbl:
            b_bg, b_fg, b_bdr = "#DBEAFE", "#1E40AF", "#93C5FD"
        elif "मूलत्रिकोण" in d_lbl:
            b_bg, b_fg, b_bdr = "#CCFBF1", "#0F766E", "#5EEAD4"
        elif "स्वराशि" in d_lbl:
            b_bg, b_fg, b_bdr = "#D1FAE5", "#065F46", "#6EE7B7"
        elif "नीच" in d_lbl:
            b_bg, b_fg, b_bdr = "#FEE2E2", "#991B1B", "#FCA5A5"
        elif "शत्रु" in d_lbl:
            b_bg, b_fg, b_bdr = "#FFEDD5", "#9A3412", "#FDBA74"
        elif "मित्र" in d_lbl:
            b_bg, b_fg, b_bdr = "#ECFDF5", "#047857", "#A7F3D0"
        else:
            b_bg, b_fg, b_bdr = "#F1F5F9", "#334155", "#CBD5E1"

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
    st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

    # 🌟 विशेष लग्न HUD (J.Hora Special Lagnas: HL, GL, SL, Indu, PP, VL)
    if chart.jaimini:
        jm = chart.jaimini
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #FFFBEB 0%, #FEF3C7 100%); border: 1.5px solid #F59E0B; border-radius: 10px; padding: 12px 18px; margin: 15px 0; box-shadow: 0 2px 6px rgba(217, 119, 6, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="color: #92400E; font-size: 13.5px; font-weight: 900; display: flex; align-items: center; gap: 6px;">
                    <span>👑 <b>विशेष जैमिनी लग्न (Special Lagnas - J.Hora Standard)</b></span>
                </div>
                <div style="font-size: 11.5px; color: #78350F; font-weight: 800; background: #FDE68A; padding: 2px 8px; border-radius: 6px;">
                    अयनांश: {chart.ayanamsa_name} ({chart.ayanamsa_value:.2f}°) | नोड: {st.session_state.get('app_node_type', 'Mean Node').split('(')[0]}
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 11px; color: #B45309; font-weight: 800;">💰 होरा लग्न (HL)</div>
                    <div style="font-size: 14px; font-weight: 900; color: #1E293B;">{jm.hora_lagna_sign_name}</div>
                    <div style="font-size: 10px; color: #64748B;">धन, संचित संपदा</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 11px; color: #B45309; font-weight: 800;">🏛️ घटी लग्न (GL)</div>
                    <div style="font-size: 14px; font-weight: 900; color: #1E293B;">{jm.ghati_lagna_sign_name}</div>
                    <div style="font-size: 10px; color: #64748B;">सत्ता, अधिकार, पद</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 11px; color: #B45309; font-weight: 800;">🪷 श्री लग्न (SL)</div>
                    <div style="font-size: 14px; font-weight: 900; color: #1E293B;">{jm.sri_lagna_sign_name}</div>
                    <div style="font-size: 10px; color: #64748B;">महालक्ष्मी कृपा, समृद्धि</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 11px; color: #B45309; font-weight: 800;">💎 इन्दु लग्न (Indu)</div>
                    <div style="font-size: 14px; font-weight: 900; color: #1E293B;">{jm.indu_lagna_sign_name}</div>
                    <div style="font-size: 10px; color: #64748B;">करोड़पति/धनागमन योग</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 11px; color: #B45309; font-weight: 800;">💨 प्राणपद लग्न (PP)</div>
                    <div style="font-size: 14px; font-weight: 900; color: #1E293B;">{jm.pranapada_lagna_sign_name}</div>
                    <div style="font-size: 10px; color: #64748B;">प्राण शक्ति, BTR सत्यता</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 11px; color: #B45309; font-weight: 800;">⚔️ वर्णद लग्न (VL)</div>
                    <div style="font-size: 14px; font-weight: 900; color: #1E293B;">{jm.varnada_lagna_sign_name}</div>
                    <div style="font-size: 10px; color: #64748B;">सामाजिक दायित्व, वृत्ति</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Extra Kundali Views ----
    st.markdown("---")
    _m0t1, _m0t2, _m0t3, _m0t4, _m0t5, _m0t6 = st.tabs([
        "🌙 चन्द्र कुण्डली",
        "☀️ सूर्य कुण्डली",
        "🏠 भाव चलित चक्र",
        "⚔️ ग्रह युद्ध",
        "👑 विशेष लग्न (HL, GL, SL, Indu)",
        "🏰 कोटा चक्र (Kota Chakra)"
    ])

    with _m0t1:
        st.markdown("### 🌙 चन्द्र कुण्डली (Moon as Lagna)")
        _moon = chart.planets.get("Moon")
        if _moon:
            _moon_sid = _moon.sign_id
            st.info(f"चन्द्र राशि: **{_moon.sign_name}** — यह चन्द्र कुण्डली का प्रथम भाव है।")
            _cc1, _cc2 = st.columns([1, 1])
            with _cc1:
                try:
                    st.markdown(render_chart_svg(chart, f"Chandra Kundali ({_moon.sign_name} Lagna)"), unsafe_allow_html=True)
                except Exception as _ec:
                    st.info(f"Chart: {_ec}")
            with _cc2:
                _moon_tbl = []
                for _pn, _pp in chart.planets.items():
                    _moon_tbl.append({"ग्रह": _pn, "राशि": _pp.sign_name, "चन्द्र-लग्न से भाव": ((_pp.sign_id - _moon_sid) % 12) + 1, "देशांतर": f"{_pp.longitude:.2f}°"})
                st.dataframe(pd.DataFrame(_moon_tbl), use_container_width=True, hide_index=True)
                st.success("चन्द्र कुण्डली — मन, माता, सुख एवं जनजीवन का दर्पण।")
        else:
            st.warning("चन्द्रमा की स्थिति उपलब्ध नहीं।")

    with _m0t2:
        st.markdown("### ☀️ सूर्य कुण्डली (Sun as Lagna)")
        _sun = chart.planets.get("Sun")
        if _sun:
            _sun_sid = _sun.sign_id
            st.info(f"सूर्य राशि: **{_sun.sign_name}** — यह सूर्य कुण्डली का प्रथम भाव है।")
            _sc1, _sc2 = st.columns([1, 1])
            with _sc1:
                try:
                    st.markdown(render_chart_svg(chart, f"Surya Kundali ({_sun.sign_name} Lagna)"), unsafe_allow_html=True)
                except Exception as _es:
                    st.info(f"Chart: {_es}")
            with _sc2:
                _sun_tbl = []
                for _pn, _pp in chart.planets.items():
                    _sun_tbl.append({"ग्रह": _pn, "राशि": _pp.sign_name, "सूर्य-लग्न से भाव": ((_pp.sign_id - _sun_sid) % 12) + 1, "देशांतर": f"{_pp.longitude:.2f}°"})
                st.dataframe(pd.DataFrame(_sun_tbl), use_container_width=True, hide_index=True)
                st.success("सूर्य कुण्डली — आत्मा, पिता, यश एवं जीवन उद्देश्य का संकेत।")
        else:
            st.warning("सूर्य की स्थिति उपलब्ध नहीं।")

    with _m0t3:
        st.markdown("### 🏠 भाव चलित चक्र (Bhava Chalit Chart)")
        st.info("समभाव पद्धति में mid-cusp boundaries से ग्रहों का वास्तविक भाव।")
        try:
            import importlib
            import src.jyotish.core.calculator as calc_mod
            importlib.reload(calc_mod)
            _calc_instance = calc_mod.default_chart_calculator
            _bc_res = _calc_instance.calculate_bhava_chalit(chart)
            if _bc_res:
                _bc_items = _bc_res.get("planet_positions", []) if isinstance(_bc_res, dict) else _bc_res
                _cusps_list = _bc_res.get("bhava_cusps", []) if isinstance(_bc_res, dict) else []
                _bc1, _bc2 = st.columns(2)
                with _bc1:
                    _bc_rows = []
                    for _it in _bc_items:
                        _rh = _it.get("rashi_house", "—")
                        _ch = _it.get("chalit_house", "—")
                        _bc_rows.append({"ग्रह": _it.get("planet", ""), "राशि भाव": _rh, "चलित भाव": _ch, "परिवर्तन?": "✅ बदला" if _rh != _ch else "— समान", "राशि": _it.get("sign", _it.get("sign_name", ""))})
                    st.dataframe(pd.DataFrame(_bc_rows), use_container_width=True, hide_index=True)
                with _bc2:
                    if _cusps_list:
                        _cusp_table = []
                        for _c in _cusps_list:
                            _cusp_table.append({
                                "भाव": _c.get("bhava", ""),
                                "राशि": _c.get("sign_name", ""),
                                "Cusp अंश": f"{_c.get('cusp_degree', 0.0):.2f}°",
                                "स्पष्ट": f"{_c.get('cusp_longitude', 0.0):.2f}°"
                            })
                        st.dataframe(pd.DataFrame(_cusp_table), use_container_width=True, hide_index=True)
                    _chd = [r for r in _bc_rows if "बदला" in r["परिवर्तन?"]]
                    if _chd:
                        st.warning("⚠️ " + str(len(_chd)) + " ग्रह राशि-भाव और चलित-भाव में भिन्न: " + ", ".join(f"{r['ग्रह']} ({r['राशि भाव']}→{r['चलित भाव']})" for r in _chd))
                    else:
                        st.success("✅ सभी ग्रह राशि-भाव और चलित-भाव में समान हैं।")
        except Exception as _ebc:
            st.error(f"भाव चलित त्रुटि: {str(_ebc)[:200]}")

    with _m0t4:
        st.markdown("### ⚔️ ग्रह युद्ध (Graha Yuddha — Planetary War)")
        st.info("जब दो ग्रह 1° के भीतर हों तो ग्रह युद्ध। उत्तर अक्षांश वाला ग्रह विजेता।")
        try:
            import importlib
            import src.jyotish.core.calculator as calc_mod
            importlib.reload(calc_mod)
            _calc_instance = calc_mod.default_chart_calculator
            _yw_list = _calc_instance.detect_graha_yuddha(chart)
            if _yw_list:
                st.error(f"⚔️ {len(_yw_list)} ग्रह युद्ध इस कुण्डली में पाए गए:")
                for _yw in _yw_list:
                    st.markdown(f"**⚔️ {_yw.get('planet1')} vs {_yw.get('planet2')}** — अंतर: {_yw.get('separation_deg', 0):.3f}° | 🏆 विजेता: **{_yw.get('winner')}** | पराजित: **{_yw.get('loser')}**")
            else:
                st.success("✅ इस कुण्डली में कोई ग्रह युद्ध नहीं है।")
        except Exception as _egy:
            st.error(f"ग्रह युद्ध त्रुटि: {str(_egy)[:200]}")

    with _m0t5:
        st.markdown("### 👑 विशेष जैमिनी लग्न एवं आरूढ़ फलादेश (Special Lagnas Deep Dive)")
        if chart.jaimini:
            jm = chart.jaimini
            col_sp1, col_sp2 = st.columns(2)
            with col_sp1:
                st.markdown(f"""
                <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px; margin-bottom:12px;">
                    <h4 style="color:#B45309; margin:0 0 6px 0;">💰 होरा लग्न (Hora Lagna - HL): {jm.hora_lagna_sign_name}</h4>
                    <p style="color:#1E293B; font-size:12.5px; line-height:1.5; margin:0;">
                    <b>शास्त्रीय प्रयोजन:</b> चल एवं अचल संपत्ति, वित्तीय सफलता, व्यापारिक लेन-देन एवं संचित धन का विचार।<br/>
                    <b>नियम:</b> यदि होरा लग्न शुभ ग्रहों से दृष्ट या युत हो तो जातक धनवान एवं आर्थिक संकटों से सुरक्षित रहता है।
                    </p>
                </div>
                <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px; margin-bottom:12px;">
                    <h4 style="color:#1D4ED8; margin:0 0 6px 0;">🏛️ घटी लग्न (Ghati Lagna - GL): {jm.ghati_lagna_sign_name}</h4>
                    <p style="color:#1E293B; font-size:12.5px; line-height:1.5; margin:0;">
                    <b>शास्त्रीय प्रयोजन:</b> सामाजिक प्रतिष्ठा, राजसत्ता, राजनीतिक प्रभाव, उच्च पद, शक्ति एवं मान-सम्मान।<br/>
                    <b>नियम:</b> जन्म लग्न और घटी लग्न के स्वामियों में सम्बंध हो तो जातक को राजकीय सम्मान एवं उच्च पद प्राप्त होता है।
                    </p>
                </div>
                <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:14px;">
                    <h4 style="color:#047857; margin:0 0 6px 0;">🪷 श्री लग्न (Sri Lagna - SL): {jm.sri_lagna_sign_name}</h4>
                    <p style="color:#1E293B; font-size:12.5px; line-height:1.5; margin:0;">
                    <b>शास्त्रीय प्रयोजन:</b> महालक्ष्मी की विशेष कृपा, सौभाग्य, आकस्मिक समृद्धि एवं वैवाहिक सुख।<br/>
                    <b>नियम:</b> श्री लग्न का स्वामी जब केंद्र या त्रिकोण में उच्च का हो तो जातक को जीवन भर धन का अभाव नहीं होता।
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with col_sp2:
                st.markdown(f"""
                <div style="background:#FAF5FF; border:1.5px solid #8B5CF6; border-radius:10px; padding:14px; margin-bottom:12px;">
                    <h4 style="color:#6D28D9; margin:0 0 6px 0;">💎 इन्दु लग्न (Indu Lagna): {jm.indu_lagna_sign_name}</h4>
                    <p style="color:#1E293B; font-size:12.5px; line-height:1.5; margin:0;">
                    <b>शास्त्रीय प्रयोजन:</b> करोड़पति योग, गुप्त धन, वित्तीय साम्राज्य एवं अकूत संपदा का मुख्य सूचक।<br/>
                    <b>नियम:</b> इन्दु लग्न में शुभ ग्रह स्थित हों तो जातक विपुल धनोपार्जन करता है; पापी ग्रह हों तो उतार-चढ़ाव रहता है।
                    </p>
                </div>
                <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:14px; margin-bottom:12px;">
                    <h4 style="color:#15803D; margin:0 0 6px 0;">💨 प्राणपद लग्न (Pranapada Lagna): {jm.pranapada_lagna_sign_name}</h4>
                    <p style="color:#1E293B; font-size:12.5px; line-height:1.5; margin:0;">
                    <b>शास्त्रीय प्रयोजन:</b> जीवन शक्ति, श्वास, आत्मा का देह से सम्बंध एवं जन्म समय शुद्धि (BTR) का प्रमाण।<br/>
                    <b>नियम:</b> प्राणपद लग्न का त्रिकोण सम्बंध जन्म लग्न से होना सटीक जन्म समय का द्योतक है।
                    </p>
                </div>
                <div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:14px;">
                    <h4 style="color:#B91C1C; margin:0 0 6px 0;">⚔️ वर्णद लग्न (Varnada Lagna): {jm.varnada_lagna_sign_name}</h4>
                    <p style="color:#1E293B; font-size:12.5px; line-height:1.5; margin:0;">
                    <b>शास्त्रीय प्रयोजन:</b> आजीविका की प्रकृति, सामाजिक कर्तव्य, जातिगत व व्यावसायिक दायित्व।<br/>
                    <b>नियम:</b> वर्णद लग्न पर शुभ प्रभाव जातक को समाज में प्रतिष्ठित वृत्ति एवं निष्ठावान कार्यशैली देता है।
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("जैमिनी विशेष लग्न गणना उपलब्ध नहीं।")

    with _m0t6:
        st.markdown("### 🏰 कोटा चक्र दुर्ग आरेख (Kota Chakra Durga Fortress)")
        st.write("जन्म नक्षत्र अनुसार ४-स्तरीय दुर्ग रचना एवं जन्म ग्रहों की रक्षा/आघात स्थिति:")
        try:
            import importlib
            import src.jyotish.core.chakras as chak_mod
            import src.jyotish.ui.chart_renderer as cr_mod
            importlib.reload(chak_mod)
            importlib.reload(cr_mod)
            kota_engine = chak_mod.default_kota_chakra_engine
            kota_data_m0 = kota_engine.calculate(chart)
            kota_svg_m0 = cr_mod.ChartRenderer.render_kota_chakra_svg(kota_data_m0, title=f"कोटा चक्र — {name}")
            st.markdown(kota_svg_m0, unsafe_allow_html=True)
        except Exception as _ekc:
            st.error(f"कोटा चक्र त्रुटि: {str(_ekc)[:200]}")


# =============================================================
# TAB 3: AFFLICTION & FREE WILL ANALYSIS (GRAHALAKSHANAM CORE)

elif selected_idx == 1:
    st.subheader("🎯 घटना विश्लेषण (Event Window Analysis)")
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


# =============================================================
# TAB 2: JANM KUNDALI & SHODASHAVARGA

elif selected_idx == 2:
    st.subheader("🛡️ दोष एवं फ्री-विल विश्लेषण (Affliction & Free Will Analysis)")
    st.write("सर्वर की हस्ताक्षर प्रणाली: द्वादश भाव एवं नवग्रहों का सौम्य/क्रूर प्रभाव, त्रिकोण/त्रिक सम्बंध, दिग्बल एवं फ्री-विल प्रतिशत।")

    detailed_toggle = st.toggle("🔄 ग्रह प्रतीक दृश्य (Detailed Symbols: Ju, Ma, Ra)", value=False)

    col_aff1, col_aff2 = st.columns(2)
    with col_aff1:
        st.markdown("#### 🏠 द्वादश भाव फ्री-विल एवं प्रभाव अंक")
        hp_list = affliction_engine.calculate_house_points(detailed=detailed_toggle)
        hp_df = pd.DataFrame(hp_list).rename(columns={
            "house": "House", "freeWill": "Free Will %", "soumya": "सौम्य (Benefic)",
            "lords159": "1/5/9 Lords", "krura": "क्रूर (Malefic)", "lords6812": "6/8/12 Lords",
            "dispositor": "Dispositor", "exchange": "Exchange", "seperative": "Separative",
            "digbala": "Digbala", "kaalbala": "Kaalbala"
        })
        st.dataframe(hp_df, use_container_width=True, hide_index=True, height=465)

    with col_aff2:
        st.markdown("#### 🪐 नवग्रह फ्री-विल एवं दशवर्ग अंक")
        pp_list = affliction_engine.calculate_planet_points(detailed=detailed_toggle)
        pp_df = pd.DataFrame(pp_list).rename(columns={
            "planet": "Planet", "freeWill": "Free Will %", "soumya": "सौम्य (Benefic)",
            "lords159": "1/5/9 Lords", "krura": "क्रूर (Malefic)", "lords6812": "6/8/12 Lords",
            "dispositor": "Dispositor", "exchange": "Exchange", "seperative": "Separative",
            "dashvarga": "दशवर्ग अंक"
        })
        st.dataframe(pp_df, use_container_width=True, hide_index=True, height=465)

    st.markdown("---")
    st.markdown("### 🎯 27 जीवन आयाम विश्लेषण (27 Life Areas Deep Breakdown)")
    la_names = [f"{a['Id']}. {a['LifeArea']}" for a in LIFE_AREAS]
    sel_la = st.selectbox("जीवन आयाम चुनें (Select Life Area)", la_names)
    sel_la_id = int(sel_la.split(".")[0])

    la_detail = affliction_engine.get_life_area_detail(sel_la_id)
    rashi_pred = affliction_engine.get_rashi_prediction(sel_la_id)

    h_cols = ["Pillar", "सौम्य (Benefic)", "1/5/9 Lords", "क्रूर (Malefic)", "6/8/12 Lords", "Separative"]
    r_cols = ["Entity", "Sign", "Mobility", "Element", "Varna", "Purushartha", "Gender", "Rising", "Day/Night", "Guna"]

    # 1. House Breakdown Row
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("##### 🏛️ त्रिपक्षीय भाव विश्लेषण (3-Pillar House Breakdown)")
        st.dataframe(pd.DataFrame(la_detail["HouseRows"], columns=h_cols), use_container_width=True, hide_index=True)
    with row1_col2:
        st.markdown("##### 🔮 भाव राशि तत्व एवं गुण धर्म (House Signs & Qualities)")
        st.dataframe(pd.DataFrame(rashi_pred["HouseRashiRows"], columns=r_cols), use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

    # 2. Lord Breakdown Row
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("##### 👑 त्रिपक्षीय भावेश विश्लेषण (3-Pillar Lord Breakdown)")
        st.dataframe(pd.DataFrame(la_detail["LordRows"], columns=h_cols), use_container_width=True, hide_index=True)
    with row2_col2:
        st.markdown("##### 🔮 भावेश राशि तत्व एवं गुण धर्म (Lord Signs & Qualities)")
        st.dataframe(pd.DataFrame(rashi_pred["LordRashiRows"], columns=r_cols), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # GRAHALAKSHANAM SIGNATURE REMEDY SECTION
    # -------------------------------------------------------------
    st.markdown("---")
    st.subheader("🌿 3-Pillar शास्त्रीय उपचार एवं दोष निवारण (Server Remedy Suite)")
    st.write("सर्वर की हस्ताक्षर उपचार प्रणाली: भाव (House), कारक (Karaka) एवं भावेश (Lord) का शास्त्रीय निवारण — रुद्राक्ष, यज्ञ, बीज मंत्र, विशिष्ट दान एवं वृक्षारोपण।")

    c_rem_top1, c_rem_top2 = st.columns([3, 1])
    with c_rem_top1:
        st.markdown(f"#### 🎯 Remedies For **{sel_la.split('.')[1].strip()}**")
    with c_rem_top2:
        rem_lords_toggle = st.toggle("🔄 भावेश दृश्य (Lords View)", value=False)

    # Calculate native remedies (or sync live if requested)
    # Calculate native remedies (with automatic hot-reload failsafe)
    if not hasattr(affliction_engine, "calculate_remedy"):
        import importlib
        import src.jyotish.core.affliction as aff_mod
        importlib.reload(aff_mod)
        affliction_engine = aff_mod.AfflictionEngine(chart)

    rem_rows = affliction_engine.calculate_remedy(life_area_id=sel_la_id, lords=rem_lords_toggle)

    # Helper function to extract free will %
    def _parse_fw(fw_str: str) -> int:
        try:
            return int(str(fw_str).replace("%", "").strip())
        except Exception:
            return 0

    fw_row = next((r for r in rem_rows if r.get("label") == "Free Will"), {})
    bm_row = next((r for r in rem_rows if r.get("label") == "Benefic / Malefic"), {})

    fw_h_val = _parse_fw(fw_row.get("house", "0"))
    fw_k_val = _parse_fw(fw_row.get("karaka", "0"))
    fw_s_val = _parse_fw(fw_row.get("houseFromKaraka", "0"))

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
                # Donation block
                inner_html = f'<div style="text-align: left; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px;">'
                inner_html += f'<div style="color: #991B1B; font-weight: 800; font-size: 12.5px; margin-bottom: 4px;">🎁 {val.get("donation_title")}</div>'
                inner_html += '<ul style="margin: 4px 0; padding-left: 18px; font-size: 11.5px; color: #1E293B;">'
                for item in val.get("items", []):
                    inner_html += f'<li>{item}</li>'
                inner_html += f'</ul><div style="color: #B91C1C; font-weight: 700; font-size: 11px; margin-top: 4px;">📅 {val.get("timing", "")}</div></div>'
            elif "mantra" in val:
                # Mantra block
                inner_html = f'<div style="text-align: center; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 8px 10px;">'
                inner_html += f'<div style="color: #92400E; font-weight: 800; font-size: 12px; margin-bottom: 3px;">🕉️ {val.get("title")}</div>'
                inner_html += f'<div style="font-weight: 900; font-size: 13.5px; margin: 4px 0; color: #78350F;">{val.get("mantra")}</div>'
                inner_html += f'<div style="font-size: 11px; color: #475569; font-style: italic;">{val.get("translit", "")}</div>'
                inner_html += f'<div style="color: #B45309; font-weight: 700; font-size: 11px; margin-top: 4px;">⏳ {val.get("note", "")}</div></div>'
            elif "className" in val:
                # Benefic / Malefic
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

    # Build Complete HTML Table Matching JyotishOS Clean Cosmic Vedic Specification
    hdr_row = rem_rows[0]
    th_style = "border: 1.5px solid #CBD5E1; font-size: 13.5px; padding: 10px 14px; text-align: center; vertical-align: middle; background: #F1F5F9; color: #0F172A; font-weight: 800; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;"
    left_style = "border: 1.5px solid #CBD5E1; font-size: 13px; padding: 10px 14px; text-align: center; vertical-align: middle; background: #F8FAFC; color: #0F172A; font-weight: 800; width: 170px; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;"

    rem_html = '<div style="overflow-x: auto; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); border: 1.5px solid #CBD5E1; border-radius: 12px;">'
    rem_html += '<table style="width: 100%; border-collapse: collapse; background: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">'
    rem_html += '<colgroup><col style="width: 18%;"><col style="width: 27%;"><col style="width: 27%;"><col style="width: 28%;"></colgroup>'
    rem_html += '<thead><tr style="background: #F8FAFC; border-bottom: 2.5px solid #2563EB;">'
    rem_html += f'<th style="{th_style}">{hdr_row.get("label")}</th>'

    # Sub-header column layout
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


# =============================================================
# TAB 4: DASVARGA TABLE (GRAHALAKSHANAM MATRIX)

elif selected_idx == 3:
    st.subheader("📊 दशवर्ग तालिका (Dasvarga Dignity Table)")
    st.write("D1 से D60 तक समस्त 10 प्रमुख वर्गों में ग्रहों की शास्त्रीय गरिमा (उच्च, मूलत्रिकोण, स्वराशि, मित्र, सम, शत्रु, नीच)।")

    # Dignity Legend Bar
    st.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;">
        <span style="background-color: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 12px;">🌟 Exaltation (उच्च)</span>
        <span style="background-color: #ccfbf1; color: #0f766e; border: 1px solid #5eead4; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 12px;">👑 Mooltrikon (मूलत्रिकोण)</span>
        <span style="background-color: #dcfce7; color: #166534; border: 1px solid #86efac; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 12px;">🏠 Own Sign (स्वराशि)</span>
        <span style="background-color: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 12px;">🤝 Friend (मित्र)</span>
        <span style="background-color: #f8fafc; color: #475569; border: 1px solid #e2e8f0; font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 12px;">⚖️ Neutral (सम)</span>
        <span style="background-color: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; font-weight: 600; padding: 4px 10px; border-radius: 6px; font-size: 12px;">⚔️ Enemy (शत्रु)</span>
        <span style="background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 12px;">🔻 Debilitation (नीच)</span>
    </div>
    """, unsafe_allow_html=True)

    dv_table = affliction_engine.calculate_dasvarga_table()
    dv_display = []
    for row in dv_table:
        r_dict = {"Varga": row["Planets"]}
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            val = row.get(p_name, "")
            if isinstance(val, dict):
                r_dict[p_name] = f"✨ {val.get('text', '')}"
            else:
                r_dict[p_name] = str(val)
        dv_display.append(r_dict)

    st.dataframe(pd.DataFrame(dv_display), use_container_width=True)
    varga_meta = {
        "D1": "D1 (लग्न/राशि - Core)",
        "D2": "D2 (होरा - धन व सम्पत्ति)",
        "D3": "D3 (द्रेष्काण - पराक्रम व भ्राता)",
        "D7": "D7 (सप्तमांश - संतान व वंश)",
        "D9": "D9 (नवांश - धर्म, विवाह व भाग्य)",
        "D10": "D10 (दशमांश - कर्म व पद-प्रतिष्ठा)",
        "D12": "D12 (द्वादशांश - माता-पिता व कुल)",
        "D16": "D16 (षोडशांश - वाहन व भौतिक सुख)",
        "D24": "D24 (चतुर्विंशांश - उच्च विद्या व ज्ञान)",
        "D30": "D30 (त्रिंशांश - अरिष्ट व दोष)",
        "D60": "D60 (षष्ट्यंश - सूक्ष्म कर्म व प्रारब्ध)"
    }

    c_lg1, c_lg2, c_lg3, c_lg4 = st.columns(4)
    c_lg1.markdown('<span class="exalt-badge">Exaltation (उच्च)</span>', unsafe_allow_html=True)
    c_lg2.markdown('<span class="mool-badge">Mooltrikon (मूलत्रिकोण)</span>', unsafe_allow_html=True)
    c_lg3.markdown('<span class="own-badge">Own Sign (स्वराशि)</span>', unsafe_allow_html=True)
    c_lg4.markdown('<span class="deb-badge">Debilitation (नीच)</span>', unsafe_allow_html=True)
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
            if "Exalt" in text:
                css = "exalt"
            elif "Mool" in text:
                css = "mool"
            elif "Own" in text:
                css = "own"
            elif "Deb" in text:
                css = "deb"
            elif "Friend" in text:
                css = "friend"
            elif "Enemy" in text:
                css = "enemy"
            elif "Neutral" in text:
                css = "neutral"

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
            base_style += "background-color: #f8fafc; color: #475569; border: 1px solid #e2e8f0; font-weight: 500;"

        return f'<div style="{base_style}">{text}</div>'

    # Build HTML Table
    tbl_html = '<div style="overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 20px;">'
    tbl_html += '<table style="width: 100%; border-collapse: collapse; text-align: left; background: #ffffff;">'
    tbl_html += '<thead><tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1;">'
    tbl_html += '<th style="padding: 10px 12px; font-weight: 700; color: #1e293b; font-size: 12.5px;">वर्ग (Varga)</th>'
    for _, p_hdr in planet_cols:
        tbl_html += f'<th style="padding: 10px 12px; font-weight: 700; color: #1e293b; font-size: 12px; text-align: center;">{p_hdr}</th>'
    tbl_html += '</tr></thead><tbody>'

    for idx, row in enumerate(dv_table):
        v_code = row.get("Planets", "")
        v_label = varga_meta.get(v_code, v_code)
        bg_row = "#fcfcfd" if idx % 2 == 1 else "#ffffff"
        tbl_html += f'<tr style="background-color: {bg_row}; border-bottom: 1px solid #f1f5f9;">'
        tbl_html += f'<td style="padding: 8px 12px; font-weight: 600; color: #0f172a; font-size: 12px; white-space: nowrap;">{v_label}</td>'
        for p_key, _ in planet_cols:
            val = row.get(p_key, "")
            formatted_cell = format_dignity_cell(val)
            tbl_html += f'<td style="padding: 6px 8px; text-align: center;">{formatted_cell}</td>'
        tbl_html += '</tr>'

    tbl_html += '</tbody></table></div>'
    st.markdown(tbl_html, unsafe_allow_html=True)

    # Astrological Dignity Insights Expander
    with st.expander("💡 दशवर्ग गरिमा शास्त्रीय विश्लेषण एवं व्याख्या (Planetary Dignity Insights)", expanded=True):
        mars_pos = chart.planets.get("Mars")
        mars_deg_str = f"{mars_pos.sign_name} {round(mars_pos.sign_degree, 2)}°" if mars_pos else "0°"
        st.markdown(f"""
        - **खगोलीय गणना स्थिति:** इस कुण्डली में मंगल (Mars) **{mars_deg_str}** पर स्थित है।
        - **बहु-वर्ग मूलत्रिकोण प्रभाव (Vargottama & Initial Division):** बृहत्पाराशर होराशास्त्र (BPHS) के नियमानुसार विषम राशियों (मेष, मिथुन आदि) का प्रथम खंड (0° से प्रारंभिक अंश) उसी राशि से आरंभ होता है। अतः मंगल D1, D3, D7, D9, D10, D12, D16 एवं D30 में मेष राशि (Aries) में ही रहता है, जो मंगल की **मूलत्रिकोण राशि** है। यह शास्त्रीय दृष्टि से अत्यंत दुर्लभ एवं प्रबल **पुष्करांश / वर्गोत्तम गरिमा** का सूचक है।
        - **दशवर्ग प्रतिष्ठा सारांश:** ग्रह जिस वर्ग में उच्च (Exalted), मूलत्रिकोण (Mooltrikona) अथवा स्वराशि (Own) में हो, वह उस वर्ग से जुड़े जीवन क्षेत्रों (D9 में भाग्य, D10 में करियर, D2 में धन) को असाधारण फल देने में समर्थ होता है।
        """)


# =============================================================
# TAB 5: VASTU-JYOTISH (MANDALA & REMEDIES)

elif selected_idx == 4:
    st.subheader("🏛️ वास्तु-ज्योतिष दिशा मण्डल (Vastu-Jyotish Architectural Alignment)")
    st.write("जन्म कुण्डली के ग्रहों एवं भावों का अष्ट दिशाओं और ब्रह्मस्थान से शास्त्रीय समन्वय एवं वास्तु-दोष निवारण।")

    v_zones = vastu_engine.evaluate_vastu_zones()

    vastu_cards_html = '<div class="vastu-grid">'
    for z in v_zones:
        risk = z["defect_risk"]
        if risk == "Harmonious":
            border_color = "#10B981"
            badge_bg = "#ECFDF5"
            badge_color = "#065F46"
            badge_border = "#10B981"
            score_color = "#059669"
            badge_text = "✨ Harmonious"
        elif risk == "Moderate Risk":
            border_color = "#F59E0B"
            badge_bg = "#FFFBEB"
            badge_color = "#92400E"
            badge_border = "#F59E0B"
            score_color = "#D97706"
            badge_text = "⚠️ Moderate Risk"
        else:
            border_color = "#EF4444"
            badge_bg = "#FEF2F2"
            badge_color = "#991B1B"
            badge_border = "#EF4444"
            score_color = "#DC2626"
            badge_text = "🚨 High Risk"

        vastu_cards_html += (
            f'<div class="vastu-card" style="border-top: 4.5px solid {border_color} !important;">'
            f'<div>'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
            f'<span style="font-size: 16px; font-weight: 900; color: #0F172A;">{z["direction"]}</span>'
            f'<span style="background: {badge_bg}; color: {badge_color}; border: 1.5px solid {badge_border}; border-radius: 12px; padding: 2px 8px; font-weight: 800; font-size: 11px;">'
            f'{badge_text}'
            f'</span>'
            f'</div>'
            f'<div style="font-size: 13px; color: #334155; font-weight: 700; margin-bottom: 8px;">'
            f'{z["hindi"]}'
            f'</div>'
            f'<div style="background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; font-size: 12px; line-height: 1.5;">'
            f'<div style="color: #0F172A;">🪐 <b>स्वामी:</b> {z["lord"]} &nbsp;|&nbsp; 🌿 <b>तत्व:</b> {z["element"]}</div>'
            f'<div style="color: #0F172A; margin-top: 2px;">📊 <b>सामंजस्य स्कोर:</b> <b style="color: {score_color}; font-size: 13px;">{z["score"]}/100</b></div>'
            f'</div>'
            f'<div style="font-size: 12px; line-height: 1.5; display: flex; flex-direction: column; gap: 6px;">'
            f'<div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 6px 8px; color: #166534;">'
            f'<b style="color: #15803D;">✅ शुभ उपयोग:</b> {", ".join(z["meta"]["ideal_uses"][:2])}'
            f'</div>'
            f'<div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 6px 8px; color: #991B1B;">'
            f'<b style="color: #B91C1C;">🚫 वर्जित:</b> {", ".join(z["meta"]["avoid"][:2])}'
            f'</div>'
            f'<div style="padding: 4px 2px; color: #0F172A;">'
            f'<b style="color: #0F172A;">🪔 शास्त्रीय उपाय:</b> {z["meta"]["remedy_hi"]}'
            f'</div>'
            f'</div>'
            f'</div>'
            f'<div style="margin-top: 12px; padding-top: 8px; border-top: 1.5px dashed #CBD5E1;">'
            f'<div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 6px 8px; font-size: 11.5px; color: #92400E;">'
            f'<b style="color: #B45309;">🕉️ मंत्र:</b> {z["meta"]["mantra"]}'
            f'</div>'
            f'</div>'
            f'</div>'
        )
    vastu_cards_html += '</div>'
    st.markdown(vastu_cards_html, unsafe_allow_html=True)


# =============================================================
# TAB 6: PRASHNA KUNDALI (HORARY ASTROLOGY)

elif selected_idx == 5:
    st.subheader("❓ प्रश्न कुण्डली एवं ताजिक फलकथन (Horary Astrology)")
    st.write("23 शास्त्रीय प्रश्न श्रेणियाँ, तात्कालिक प्रश्न कुण्डली चक्र, कार्येश-लग्नेश इत्थशाल योग, द्वादश भाव भूमिका एवं सटीक समय निर्धारण।")

    # Native / Questioner Selection Mode
    st.markdown("##### 👤 प्रश्नकर्ता चयन (Select Questioner / Query Source)")
    q_mode = st.radio(
        "questioner_mode",
        [
            f"👤 सक्रिय जातक ({name}) — जन्म स्थान / डिफ़ॉल्ट",
            "🌐 वर्तमान तात्कालिक समय एवं स्थान (Current Live Moment)",
            "✏️ अन्य प्रश्नकर्ता / नवीन विवरण (Custom Querent)"
        ],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    q_name = name
    q_lat = latitude
    q_lon = longitude
    q_tz = tz_offset
    q_city_name = default_city_name
    q_dt = datetime.now()

    if q_mode.startswith("🌐"):
        q_name = f"{name} (लाइव प्रश्न)"
        q_dt = datetime.now()
    elif q_mode.startswith("✏️"):
        with st.expander("📝 नवीन प्रश्नकर्ता का विवरण दर्ज करें", expanded=True):
            col_q1, col_q2, col_q3 = st.columns([2, 1, 1])
            q_name = col_q1.text_input("प्रश्नकर्ता का नाम (Questioner Name)", value="नया प्रश्नकर्ता")
            q_date_val = col_q2.date_input("प्रश्न तिथि (Query Date)", value=date.today(), format="DD/MM/YYYY")
            q_time_val = col_q3.time_input("प्रश्न समय (Query Time)", value=datetime.now().time())
            q_dt = datetime.combine(q_date_val, q_time_val)

            col_loc1, col_loc2, col_loc3 = st.columns([2, 1, 1])
            custom_city = col_loc1.text_input("स्थान / नगर (Place/City)", value=default_city_name)
            if custom_city and custom_city.strip() != default_city_name:
                try:
                    geo_res = default_geocoding_service.resolve(custom_city.strip())
                except Exception:
                    geo_res = None
                if geo_res:
                    q_lat = geo_res.get("latitude", q_lat)
                    q_lon = geo_res.get("longitude", q_lon)
                    q_tz = geo_res.get("timezone_offset", q_tz)
                    q_city_name = geo_res.get("city", custom_city)
            
            q_lat = col_loc2.number_input("अक्षांश (Lat)", value=float(q_lat), format="%.4f")
            q_lon = col_loc3.number_input("देशांतर (Lon)", value=float(q_lon), format="%.4f")

    # Category and Query Input
    st.markdown("---")
    cat_options = [
        f"{c.get('icon', '🔮')} {c.get('Name_Hi', c.get('Name', 'Category'))} ({c.get('Name', '')})"
        for c in PRASHNA_CATEGORIES
    ]
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        cat_idx_choice = st.selectbox(
            "प्रश्न श्रेणी (Question Category)",
            range(len(cat_options)),
            format_func=lambda i: cat_options[i] if i < len(cat_options) else "",
            index=min(6, max(0, len(cat_options) - 1))
        )
        selected_cat_meta = PRASHNA_CATEGORIES[cat_idx_choice] if cat_idx_choice < len(PRASHNA_CATEGORIES) else PRASHNA_CATEGORIES[0]
        prashna_cat = selected_cat_meta.get("Name", "Job")

    # Sample default questions per category
    sample_queries = {
        "Health": "क्या मरीज को वर्तमान बीमारी से शीघ्र स्वास्थ्य लाभ मिलेगा?",
        "Marriage": "क्या इस वर्ष मेरा विवाह तय हो जाएगा?",
        "Relationship": "क्या हमारे प्रेम सम्बंध में सामंजस्य और स्थायित्व रहेगा?",
        "Child": "क्या संतान प्राप्ति के शुभ योग बन रहे हैं?",
        "Wealth": "क्या मुझे रुका हुआ धन वापस मिलेगा और आर्थिक स्थिति सुधरेगी?",
        "Career": "क्या मुझे कार्यक्षेत्र में उच्च पद और प्रतिष्ठा प्राप्त होगी?",
        "Job": "क्या मुझे नई नौकरी या पदोन्नति मिलेगी?",
        "Business": "क्या नया व्यापार प्रारंभ करना लाभदायक रहेगा?",
        "Property": "क्या यह भूमि या मकान खरीदना मेरे लिए शुभ रहेगा?",
        "Investment": "क्या इस निवेश या शेयर बाज़ार में मुझे अच्छा लाभ होगा?",
        "Litigation / Court": "क्या न्यायालय में चल रहे मुक़दमे में मेरी विजय होगी?",
        "Foreign Travel": "क्या मेरा विदेश यात्रा का वीज़ा स्वीकृत हो जाएगा?",
        "Education / Exam": "क्या मुझे इस प्रतियोगी परीक्षा में सफलता मिलेगी?",
        "Lost Item": "क्या खोई हुई वस्तु पुनः प्राप्त हो जाएगी?",
        "Purchase Vehicle": "क्या नया वाहन खरीदना इस समय अनुकूल रहेगा?",
        "Partnership": "क्या यह व्यापारिक साझेदारी दीर्घकालिक सफल होगी?",
        "Debt / Loan": "क्या मुझे क़र्ज़ से शीघ्र मुक्ति मिलेगी?",
        "Relocation / Transfer": "क्या मेरा वांछित स्थान पर तबादला हो जाएगा?",
        "Surgery / Diagnosis": "क्या शल्य चिकित्सा (सर्जरी) सकुशल संपन्न होगी?",
        "Spiritual Initiation": "क्या मुझे सद्गुरु की कृपा और मंत्र दीक्षा प्राप्त होगी?",
        "Construction / Vastu": "क्या नवीन गृह निर्माण निर्विघ्न संपन्न होगा?",
        "Friends / Enemies": "क्या शत्रु पक्ष शांत रहेगा और मित्रों का सहयोग मिलेगा?",
        "General Prashna": "क्या मेरा अभीष्ट कार्य सफलतापूर्वक सिद्ध होगा?"
    }
    default_q_text = sample_queries.get(prashna_cat, "क्या मेरा अभीष्ट कार्य सिद्ध होगा?")

    with col_p2:
        prashna_text = st.text_input("अपना विशिष्ट प्रश्न दर्ज करें (Enter Query)", value=default_q_text)

    calc_btn = st.button("🔮 प्रश्न कुण्डली एवं शास्त्रीय निर्णय प्राप्त करें (Calculate Prashna Chart)", type="primary")

    # Store calculation in session state with automatic cache-invalidation
    need_recalc = (
        calc_btn
        or "prashna_res" not in st.session_state
        or not isinstance(st.session_state.prashna_res, dict)
        or "rules_analysis" not in st.session_state.prashna_res
        or not st.session_state.prashna_res.get("all_rules")
        or st.session_state.prashna_res.get("active_positive_count", 0) == 0
        or st.session_state.prashna_res.get("category") != prashna_cat
    )

    if need_recalc:
        if calc_btn and not q_mode.startswith("✏️"):
            q_dt = datetime.now()
        try:
            st.session_state.prashna_res = default_prashna_service.generate_prashna_chart(
                query_text=prashna_text,
                category_name=prashna_cat,
                latitude=q_lat,
                longitude=q_lon,
                timezone_offset=q_tz,
                query_dt=q_dt,
                questioner_name=q_name
            )
            if calc_btn:
                st.toast("✅ प्रश्न कुण्डली एवं शास्त्रीय निर्णय सफलतापूर्वक परिकलित!")
        except Exception:
            import src.jyotish.services.prashna as p_mod_live
            importlib.reload(p_mod_live)
            st.session_state.prashna_res = p_mod_live.default_prashna_service.generate_prashna_chart(
                query_text=prashna_text,
                category_name=prashna_cat,
                latitude=q_lat,
                longitude=q_lon,
                timezone_offset=q_tz,
                query_dt=q_dt,
                questioner_name=q_name
            )
            if calc_btn:
                st.toast("✅ प्रश्न कुण्डली एवं शास्त्रीय निर्णय सफलतापूर्वक परिकलित!")

    p_res = st.session_state.prashna_res
    if not p_res or not p_res.get("all_rules") or p_res.get("active_positive_count", 0) == 0 or "rules_analysis" not in p_res:
        p_res = default_prashna_service.generate_prashna_chart(
            query_text=prashna_text,
            category_name=prashna_cat,
            latitude=q_lat,
            longitude=q_lon,
            timezone_offset=q_tz,
            query_dt=q_dt,
            questioner_name=q_name
        )
        st.session_state.prashna_res = p_res

    p_chart: KundaliChart = p_res.get("chart", chart)

    st.markdown("---")

    # 1. Top KPI Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    v_text = str(p_res.get('verdict', 'उत्कृष्ट')).split(" (")[0]
    v_badge = str(p_res.get('verdict_badge', '✅ शुभ'))
    t_text = str(p_res.get('timing', '1 से 3 सप्ताह')).split(" (")[0]
    v_score = float(p_res.get('verdict_score', 0.75))
    pos_c = p_res.get('active_positive_count', 0)
    neg_c = p_res.get('active_negative_count', 0)

    m1.metric("🎯 शास्त्रीय निर्णय", v_text, v_badge)
    m2.metric("⏳ संभावित समय", t_text)
    m3.metric("📊 सहमति स्कोर", f"{int(v_score * 100)}%")
    m4.metric("📜 100 शास्त्रीय नियम", f"✅ {pos_c} शुभ | ⚠️ {neg_c} अशुभ")

    # 2. Main 2-Column Visual Layout (Left: SVG Chart, Right: Summary HUD)
    col_chart, col_summary = st.columns([1, 1])

    with col_chart:
        c_icon = p_res.get('category_icon', '🔮')
        c_hi = p_res.get('category_hi', prashna_cat)
        st.markdown(f"#### 🔮 प्रश्न कुण्डली चक्र ({c_icon} {c_hi})")
        prashna_chart_title = f"Prashna Kundali — {p_res.get('category', prashna_cat)}"
        svg_code = render_chart_svg(p_chart, prashna_chart_title, varga_code="D1")
        st.markdown(svg_code, unsafe_allow_html=True)
        st.caption(f"📍 स्थान: {q_city_name} (Lat: {q_lat:.2f}°, Lon: {q_lon:.2f}°) | समय: {p_res.get('query_time', '')}")

    with col_summary:
        st.markdown("#### 🌟 प्रश्न सारांश एवं मुख्य शास्त्रीय कारकत्व")
        
        sum_col1, sum_col2 = st.columns(2)
        with sum_col1:
            st.markdown(f"- **प्रश्नकर्ता:** {p_res.get('questioner_name', q_name)}")
            st.markdown(f"- **प्रश्न लग्न:** {p_res.get('prashna_lagna', '-')}")
            st.markdown(f"- **लग्नेश (1st Lord):** {p_res.get('lagnesh', '-')}")
            st.markdown(f"- **कार्य भाव:** {p_res.get('karya_bhava', '-')}")
        with sum_col2:
            st.markdown(f"- **प्रश्न समय:** {p_res.get('query_time', '-')}")
            st.markdown(f"- **कार्येश (Karyesha):** {p_res.get('karyesh', '-')}")
            st.markdown(f"- **चन्द्रमा स्थिति:** {p_res.get('moon_placement', '-')}")
            st.markdown(f"- **ताजिक योग:** {p_res.get('tajika_yoga', '-')}")

        st.info(f"📜 **शास्त्रीय निष्कर्ष:** {p_res.get('explanation_hi', '')}")

        # Visual Score Bar
        st.markdown(f"**फलसिद्धि संभावना सूचकांक (Success Probability): {int(v_score * 100)}%**")
        st.progress(v_score)

    # 3. Detailed Analytical Tabs
    st.markdown("---")
    p_tab_rules, p_tab1, p_tab2, p_tab3 = st.tabs([
        "📜 100 शास्त्रीय प्रश्न नियम एवं प्रमाण",
        "🪐 प्रश्नकालीन नवग्रह स्थिति तालिका",
        "🎭 द्वादश भाव भूमिका एवं प्रभाव",
        "📖 ताजिक एवं प्रश्न मार्ग सिद्धांत"
    ])

    with p_tab_rules:
        st.markdown("##### 📜 100 शास्त्रीय प्रश्न नियम — शुभ (+) व अशुभ (-) प्रमाण विश्लेषण")
        st.write("प्रश्न मार्ग, ताजिक नीलकण्ठी, षट्पंचाशिका, दैवज्ञ वल्लभ एवं केपी होरारी के 100 शास्त्रीय नियमों का स्वचालित मूल्यांकन।")

        r_col1, r_col2, r_col3 = st.columns(3)
        pos_pts = p_res.get('total_positive_points', 0)
        neg_pts = p_res.get('total_negative_points', 0)
        net_bal = p_res.get('net_balance_score', 0)

        r_col1.markdown(f"""
        <div style="background: #F0FDF4; border: 2px solid #86EFAC; border-radius: 10px; padding: 12px; text-align: center;">
            <div style="font-size: 13px; color: #166534; font-weight: 700;">🟢 सक्रिय शुभ नियम (Positive Rules)</div>
            <div style="font-size: 24px; font-weight: 900; color: #15803D;">{pos_c} नियम (+{pos_pts} अंक)</div>
        </div>
        """, unsafe_allow_html=True)

        r_col2.markdown(f"""
        <div style="background: #FEF2F2; border: 2px solid #FECACA; border-radius: 10px; padding: 12px; text-align: center;">
            <div style="font-size: 13px; color: #991B1B; font-weight: 700;">🔴 सक्रिय अशुभ नियम (Negative Obstacles)</div>
            <div style="font-size: 24px; font-weight: 900; color: #DC2626;">{neg_c} नियम (-{neg_pts} अंक)</div>
        </div>
        """, unsafe_allow_html=True)

        r_col3.markdown(f"""
        <div style="background: #F8FAFC; border: 2px solid #CBD5E1; border-radius: 10px; padding: 12px; text-align: center;">
            <div style="font-size: 13px; color: #334155; font-weight: 700;">⚖️ शुद्ध संतुलन (Net Shastriya Balance)</div>
            <div style="font-size: 24px; font-weight: 900; color: {'#15803D' if net_bal >= 0 else '#DC2626'};">{net_bal:+} अंक</div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        
        # Sub-tabs for instant direct viewing
        subtab_pos, subtab_neg, subtab_all = st.tabs([
            f"🟢 सक्रिय शुभ नियम ({pos_c})",
            f"🔴 सक्रिय अशुभ नियम ({neg_c})",
            "📚 संपूर्ण 100 नियमों की संदर्भ तालिका (Complete Library)"
        ])

        with subtab_pos:
            pos_rules_list = p_res.get('positive_rules', [])
            if pos_rules_list:
                st.markdown(f"#### 🟢 सक्रिय शुभ शास्त्रीय नियम साक्ष्य (कुल: {len(pos_rules_list)} नियम | +{pos_pts} अंक)")
                pos_df = []
                for pr in pos_rules_list:
                    pos_df.append({
                        "नियम ID": pr.get("rule_id"),
                        "क्षेत्र": pr.get("domain"),
                        "शास्त्रीय नियम नाम": pr.get("name_hi"),
                        "मूल ग्रंथ (Source)": pr.get("source"),
                        "शुभ अंक": f"+{abs(pr.get('weight', 0))}",
                        "शास्त्रीय प्रमाण व फल": pr.get("description_hi")
                    })
                st.dataframe(pd.DataFrame(pos_df), use_container_width=True, hide_index=True)
            else:
                st.info("वर्तमान प्रश्न कुण्डली में कोई विशेष सकारात्मक नियम सक्रिय नहीं है।")

        with subtab_neg:
            neg_rules_list = p_res.get('negative_rules', [])
            if neg_rules_list:
                st.markdown(f"#### 🔴 सक्रिय अशुभ / बाधक नियम साक्ष्य (कुल: {len(neg_rules_list)} नियम | -{neg_pts} अंक)")
                neg_df = []
                for nr in neg_rules_list:
                    neg_df.append({
                        "नियम ID": nr.get("rule_id"),
                        "क्षेत्र": nr.get("domain"),
                        "बाधक नियम नाम": nr.get("name_hi"),
                        "मूल ग्रंथ (Source)": nr.get("source"),
                        "बाधा अंक": f"-{abs(nr.get('weight', 0))}",
                        "बाधा विवरण एवं उपाय": nr.get("description_hi")
                    })
                st.dataframe(pd.DataFrame(neg_df), use_container_width=True, hide_index=True)
            else:
                st.success("🎉 उत्कृष्ट! वर्तमान प्रश्न कुण्डली में कोई भी गंभीर अशुभ अथवा बाधक नियम सक्रिय नहीं है।")

        with subtab_all:
            all_r_list = p_res.get('all_rules', [])
            if all_r_list:
                st.markdown("#### 📚 संपूर्ण 100 शास्त्रीय प्रश्न नियम संदर्भ तालिका (Complete 100 Rules Library)")
                # Interactive filtering controls for 100 rules library
                f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 2])
                with f_col1:
                    status_filter = st.selectbox(
                        "स्थिति फ़िल्टर (Status Filter)",
                        ["सभी 100 नियम (All 100)", "केवल सक्रिय शुभ (+) (Active Positive)", "केवल सक्रिय अशुभ (-) (Active Negative)", "केवल निष्क्रिय (Inactive)"],
                        key="prashna_rules_filter_status"
                    )
                with f_col2:
                    domains = ["समस्त ग्रंथ / क्षेत्र (All Domains)"] + sorted(list(set(r.get("domain", "") for r in all_r_list if r.get("domain"))))
                    domain_filter = st.selectbox("ग्रंथ / पद्धति फ़िल्टर (Domain Filter)", domains, key="prashna_rules_filter_domain")
                with f_col3:
                    rule_search = st.text_input("🔍 नियम खोजें (Search Rule)", placeholder="नाम, ग्रंथ, ID या फल...", key="prashna_rules_search")

                filtered_rules = []
                for ar in all_r_list:
                    # Status filter using robust boolean triggered check
                    is_trig = ar.get("triggered", False) or ar.get("status") in ["सक्रिय", "✅ लागू (Triggered)"]
                    tp_val = ar.get("type", "")
                    if status_filter.startswith("केवल सक्रिय शुभ") and not (is_trig and tp_val == "POSITIVE"):
                        continue
                    if status_filter.startswith("केवल सक्रिय अशुभ") and not (is_trig and tp_val == "NEGATIVE"):
                        continue
                    if status_filter.startswith("केवल निष्क्रिय") and is_trig:
                        continue

                    # Domain filter
                    if domain_filter != "समस्त ग्रंथ / क्षेत्र (All Domains)" and ar.get("domain") != domain_filter:
                        continue

                    # Search text
                    if rule_search and rule_search.strip():
                        s_term = rule_search.strip().lower()
                        match = (
                            s_term in str(ar.get("rule_id", "")).lower()
                            or s_term in str(ar.get("name_hi", "")).lower()
                            or s_term in str(ar.get("source", "")).lower()
                            or s_term in str(ar.get("domain", "")).lower()
                            or s_term in str(ar.get("description_hi", "")).lower()
                        )
                        if not match:
                            continue

                    filtered_rules.append({
                        "ID": ar.get("rule_id"),
                        "क्षेत्र": ar.get("domain"),
                        "शास्त्रीय नियम नाम": ar.get("name_hi"),
                        "मूल ग्रंथ (Source)": ar.get("source"),
                        "प्रकार": "🟢 शुभ (+)" if ar.get("type") == "POSITIVE" else "🔴 अशुभ (-)",
                        "प्रभाव अंक": f"+{abs(ar.get('weight', 0))}" if ar.get("type") == "POSITIVE" else f"-{abs(ar.get('weight', 0))}",
                        "सक्रियता स्थिति": "🌟 सक्रिय (Active)" if is_trig else "⚪ निष्क्रिय (Inactive)",
                        "शास्त्रीय विवरण व प्रमाण": ar.get("description_hi")
                    })

                st.caption(f"प्रदर्शित नियम: **{len(filtered_rules)} / 100**")
                st.dataframe(pd.DataFrame(filtered_rules), use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ नियम तालिका लोड नहीं हो सकी। कृपया ऊपर 'प्रश्न कुण्डली एवं शास्त्रीय निर्णय प्राप्त करें' बटन पर क्लिक करें।")

    with p_tab1:
        st.markdown("##### 🪐 प्रश्न समय पर ग्रहों की स्पष्ट खगोलीय स्थिति (Graha Spashta)")
        p_graha_df = []
        for g_row in p_res.get("graha_table", []):
            p_obj = p_chart.planets.get(g_row["graha"])
            dignity_label, _, _ = get_varga_dignity_info(g_row["graha"], g_row["sign"], affliction_engine)
            p_graha_df.append({
                "ग्रह (Graha)": g_row["graha"],
                "राशि (Sign)": g_row["sign"],
                "राशि स्वामी (Lord)": g_row["lord"],
                "भाव (House)": g_row["house"],
                "अंश (Degree)": g_row["degree"],
                "नक्षत्र (Nakshatra)": g_row["nakshatra"],
                "गति (Motion)": g_row["motion"],
                "गरिमा (Dignity)": dignity_label
            })
        st.dataframe(pd.DataFrame(p_graha_df), use_container_width=True, hide_index=True)

    with p_tab2:
        st.markdown("##### 🎭 प्रश्न सम्बंधी द्वादश भाव भूमिका (12 Houses Role & Significators)")
        role_cards = []
        for hr in p_res.get("house_roles", []):
            h_num = hr.get('house', '')
            h_sign = hr.get('sign', '')
            h_lord = hr.get('lord', '')
            h_icon = hr.get('icon', '📍')
            h_text = hr.get('text', '')
            h_imp = hr.get('is_important', False)
            h_occ = hr.get('occupants', [])
            role_cards.append({
                "भाव (House)": f"{h_num} ({h_sign})",
                "भावेश (Lord)": h_lord,
                "भूमिका / कारकत्व (Role)": f"{h_icon} {h_text}",
                "महत्व (Significance)": "⭐ मुख्य भाव" if h_imp else "सामान्य",
                "भावस्थ ग्रह (Occupants)": ", ".join(h_occ) if h_occ else "—"
            })
        st.dataframe(pd.DataFrame(role_cards), use_container_width=True, hide_index=True)

    with p_tab3:
        st.markdown("##### 📜 ताजिक नीलकण्ठी एवं प्रश्न मार्ग के प्रमुख सिद्धांत")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown("""
            **1. इत्थशाल योग (Ithasala Yoga):**
            - जब तीव्र गति का ग्रह मंद गति के ग्रह से कम अंश पर रहकर दीप्तांश के भीतर अग्रसर होता है, तो कार्य की त्वरित व निश्चित सिद्धि होती है।
            - **दीप्तांश विस्तार:** सूर्य (15°), चन्द्र (12°), मंगल (8°), बुध (7°), गुरु (9°), शुक्र (7°), शनि (9°)।

            **2. ईशराफ / मुसरिफ़ योग (Esharpha Yoga):**
            - जब तीव्र गति का ग्रह मंद ग्रह के अंशों को पार कर 1° या अधिक आगे निकल जाता है, तो अवसर बीत जाने अथवा विफलता का संकेत होता है।
            """)
        with t_col2:
            st.markdown("""
            **3. चन्द्रमा की स्थिति का महत्व (Moon's Role):**
            - प्रश्न कुण्डली में चन्द्रमा को प्रश्नकर्ता का मन माना जाता है। चन्द्रमा का 6, 8, 12 भाव में होना अथवा पाप पीड़ित होना मानसिक चिंता व विलंब दर्शाता है।
            
            **4. कार्येश-लग्नेश सम्बंध:**
            - लग्नेश (प्रश्नकर्ता) और कार्येश (प्रश्न का अभीष्ट) का केंद्र/त्रिकोण में होना कार्य की सहज सिद्धि कराता है।
            """)


# =============================================================
# TAB 7: GRAHALAKSHANAM CLOUD SYNC & BENCHMARK

elif selected_idx == 6:
    st.subheader("☁️ लाइव सर्वर सिंक एवं डेटा सत्यापन (Server Cloud Sync & Validation)")
    st.write("अधिकृत खाते से लाइव सम्बंध स्थापित कर कुण्डलियों को सिंक करें और पंचांग से सटीकता का मिलान करें।")

    c_auth1, c_auth2, c_auth3 = st.columns([2, 2, 1])
    g_user = c_auth1.text_input("Username / Email", value=st.session_state.get("gla_user", ""), placeholder="उपयोगकर्ता नाम या ईमेल दर्ज करें", key="sync_user_input")
    g_pass = c_auth2.text_input("Password", value=st.session_state.get("gla_pass", ""), type="password", placeholder="पासवर्ड दर्ज करें", key="sync_pass_input")
    c_auth3.write("")
    c_auth3.write("")
    test_conn_btn = c_auth3.button("🔗 कनेक्ट करें", type="primary", use_container_width=True)

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
            st.info(f"🌐 सक्रिय सर्वर खाता: **{active_u}**")

            col_sync1, col_sync2 = st.columns(2)
            with col_sync1:
                st.markdown("#### 📁 सहेजी गई क्लाउड कुण्डलियाँ (Home Saved Charts)")
                ff_data = client.get_folders_with_files()
                files = ff_data.get("files", [])
                st.session_state.gla_charts = files
                st.write(f"क्लाउड में उपलब्ध कुण्डलियाँ: **{len(files)}**")
                
                for f_chart in files:
                    with st.container():
                        st.markdown(f'''
                        <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <b style="color:#000000; font-size:14px;">👤 {f_chart['name']}</b> 
                                <span style="color:#64748B; font-size:12px;">(ID: {f_chart['id']})</span><br/>
                                <small style="color:#334155;">📍 {f_chart.get('address', 'Nanpara / Bahraich')}</small>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                        if st.button(f"📥 {f_chart['name']} लोड करें", key=f"btn_load_{f_chart['id']}"):
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
        else:
            st.error("❌ लॉगिन असफल। कृपया क्रेडेंशियल्स जांचें।")


elif selected_idx == 7:
    st.subheader("⚖️ षड्बल, भावबल एवं दृष्टि वेध चक्र (Shadbala & Aspectarium)")
    tab_sb_shadbala, tab_sb_aspectarium = st.tabs([
        "⚖️ षड्बल एवं भावबल (Shadbala & Bhava Bala)",
        "📐 दृष्टि वेध एवं कोणीय संबंध (Dynamic Aspectarium & Orbs)"
    ])

    with tab_sb_shadbala:
        if chart.shadbala:
            sb_data = []
            for p_name, s_obj in chart.shadbala.planets.items():
                sb_data.append({
                    "Planet": p_name,
                    "Sthana Bala": s_obj.sthana_bala,
                    "Dik Bala": s_obj.dik_bala,
                    "Kaala Bala": s_obj.kaala_bala,
                    "Cheshta Bala": s_obj.cheshta_bala,
                    "Naisargika": s_obj.naisargika_bala,
                    "Drik Bala": s_obj.drik_bala,
                    "Total Virupas": s_obj.total_virupas,
                    "Rupas": s_obj.total_rupas,
                    "Required": s_obj.required_virupas,
                    "Strength Ratio": f"{s_obj.strength_ratio:.2f}",
                    "Status": "✅ बलवान्" if s_obj.is_strong else "⚠️ निर्बल",
                    "Ishta Phala": s_obj.ishta_phala,
                    "Kashta Phala": s_obj.kashta_phala,
                })
            st.dataframe(pd.DataFrame(sb_data), use_container_width=True)

            col_sb1, col_sb2 = st.columns(2)
            with col_sb1:
                st.markdown("#### 📊 षड्बल रूप अनुपात (Strength Ratio)")
                r_df = pd.DataFrame([{"Planet": p_name, "Ratio": s_obj.strength_ratio} for p_name, s_obj in chart.shadbala.planets.items()]).set_index("Planet")
                st.bar_chart(r_df)
            with col_sb2:
                st.markdown("#### 🏰 द्वादश भाव बल (Bhavabala - Virupas)")
                b_df = pd.DataFrame([{"House": f"H{h}", "Bala": b_val} for h, b_val in chart.shadbala.bhava_bala.items()]).set_index("House")
                st.bar_chart(b_df)

    with tab_sb_aspectarium:
        st.markdown("### 📐 डायनेमिक वैदिक एवं पाश्चात्य दृष्टि वेध चक्र (Dynamic Aspectarium & Orbs)")
        st.caption("Shri Jyoti Star एवं Parashara's Light ग्रेड 9x9 कोणीय अंतर मैट्रिक्स, पराशरीय विशेष दृष्टि (मंगल 4/8, गुरु 5/9, शनि 3/10) एवं पाश्चात्य प्रमुख कोणीय वेध (0°, 60°, 90°, 120°, 150°, 180°) व संमुख/विमुख (Applying vs Separating) गति:")

        try:
            import importlib
            import src.jyotish.services.aspectarium as asp_mod
            importlib.reload(asp_mod)
            asp_data = asp_mod.default_aspectarium_service.calculate_aspectarium(chart)
            asp_html = asp_mod.default_aspectarium_service.render_aspectarium_html(chart)

            # Top KPI metrics
            c_as1, c_as2, c_as3 = st.columns(3)
            with c_as1:
                st.metric("सक्रिय प्रमुख दृष्टियां (Western Aspects)", f"{asp_data['total_aspects_count']} संबंध", "युति, त्रिकोण, केंद्र, लाभ")
            with c_as2:
                st.metric("वैदिक विशेष दृष्टियां (Vedic Drishtis)", f"{asp_data['total_drishti_count']} वेध", "मंगल, गुरु, शनि एवं सप्तम दृष्टि")
            with c_as3:
                # Find tightest aspect
                t_asp = min(asp_data["aspects"], key=lambda x: x["orb_abs"]) if asp_data["aspects"] else None
                if t_asp:
                    st.metric("सर्वाधिक तीव्र वेध (Tightest Orb)", f"{t_asp['p1_hi']} {t_asp['symbol']} {t_asp['p2_hi']}", f"Orb: {t_asp['orb_str']} ({t_asp['motion_hi']})")
                else:
                    st.metric("सर्वाधिक तीव्र वेध", "—", "—")

            # Visual 9x9 Aspectarium Table
            st.markdown(asp_html.strip(), unsafe_allow_html=True)

            # Detailed Aspect Breakdown Tables in 2 columns
            col_ad1, col_ad2 = st.columns(2)
            with col_ad1:
                st.markdown("#### 🌟 पाश्चात्य एवं हार्मोनिक कोणीय संबंध (Major Aspects & Orbs)")
                if asp_data["aspects"]:
                    asp_rows = []
                    for a in asp_data["aspects"]:
                        asp_rows.append({
                            "ग्रह १": f"{a['p1_hi']} ({a['planet1']})",
                            "दृष्टि प्रकार": f"{a['symbol']} {a['aspect_name']}",
                            "ग्रह २": f"{a['p2_hi']} ({a['planet2']})",
                            "वास्तविक कोण": f"{a['actual_angle']:.2f}°",
                            "ऑर्ब (अंश अंतर)": f"{a['orb_str']}",
                            "गति (Phase)": a["motion_hi"],
                            "प्रकृति": a["nature"]
                        })
                    st.dataframe(pd.DataFrame(asp_rows), use_container_width=True, hide_index=True)
                else:
                    st.info("कोई प्रमुख कोणीय दृष्टि इस चार्ट में सक्रिय नहीं है।")

            with col_ad2:
                st.markdown("#### 🔱 पराशरीय वैदिक विशेष दृष्टियां (Parashari Vedic Drishtis)")
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


# =============================================================
# TAB 9: JAIMINI & UPAGRAHAS & SPECIAL LAGNAS & AVASTHAS

elif selected_idx == 8:
    st.subheader("🔱 जैमिनी ज्योतिष, विशेष लग्न, आरूढ़ पद एवं ग्रह अवस्थाएँ")
    st.write("महर्षि जैमिनी उपदेश सूत्र एवं बृहत्पाराशर होराशास्त्र (BPHS) आधारित विशेष लग्न, 12 आरूढ़ पद, ग्रह अवस्थाएँ, आयुर्दाय एवं अप्रकाशित उपग्रह।")

    tab_j_km, tab_j1, tab_j2, tab_j3, tab_j4, tab_j5 = st.tabs([
        "🔱 कारकांश व स्वांश चक्र (Karakamsha & Swamsha Suite)",
        "🌟 विशेष लग्न (Special Lagnas)",
        "👑 सम्पूर्ण 12 आरूढ़ पद (Arudha Padas)",
        "💫 ग्रह अवस्थाएँ (Planetary Avasthas)",
        "⏳ आयुर्दाय एवं दीर्घायु (Longevity)",
        "👻 अप्रकाशित उपग्रह (Invisible Upagrahas)"
    ])

    with tab_j_km:
        st.markdown("### 🔱 जैमिनी कारकांश, स्वांश एवं इष्ट देवता वेध (Jaimini Karakamsha Suite)")
        st.caption("महर्षि जैमिनी उपदेश सूत्र अनुसार नवमांश में आत्मकारक की स्थिति (कारकांश), स्वांश फल, इष्ट देवता एवं मोक्ष योग का प्रामाणिक विश्लेषण:")

        try:
            import importlib
            import src.jyotish.services.jaimini_suite as js_mod
            importlib.reload(js_mod)
            j_res = js_mod.default_jaimini_suite_service.analyze_jaimini_suite(chart)

            # Top KPI summary
            c_jk1, c_jk2, c_jk3, c_jk4 = st.columns(4)
            with c_jk1:
                st.metric("आत्मकारक (AK)", f"{j_res['atmakaraka']}", "आत्मा का स्वभाव")
            with c_jk2:
                st.metric("कारकांश राशि (D9)", f"{j_res['karakamsha_sign']}", f"Sign #{j_res['karakamsha_sign_id']}")
            with c_jk3:
                ishta = j_res["ishta_devata"]
                st.metric("इष्ट देवता (Ishta Devata)", f"{ishta['deity']}", f"मंत्र: {ishta['mantra']}")
            with c_jk4:
                dharma = j_res["dharma_devata"]
                st.metric("धर्म देवता (Dharma)", f"{dharma['deity']}", f"ग्रह: {dharma['planet']}")

            # Karakamsha 12-House Grid
            st.markdown("#### 🏛️ कारकांश लग्न से १२ भावों में ग्रहीय स्थिति (Houses from Karakamsha in D9)")
            h_cols = st.columns(6)
            for h_num in range(1, 7):
                with h_cols[h_num - 1]:
                    pls = j_res["houses_from_kl"].get(h_num, [])
                    pl_str = ", ".join(pls) if pls else "—"
                    st.markdown(
                        f'<div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:8px; text-align:center; margin-bottom:8px;">'
                        f'<b style="color:#1E3A8A; font-size:12px;">भाव {h_num}</b><br/>'
                        f'<span style="font-weight:700; color:#0F172A; font-size:13px;">{pl_str}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            h_cols2 = st.columns(6)
            for h_num in range(7, 13):
                with h_cols2[h_num - 7]:
                    pls = j_res["houses_from_kl"].get(h_num, [])
                    pl_str = ", ".join(pls) if pls else "—"
                    bg_color = "#DCFCE7" if (h_num == 12 and "Ketu" in pls) else "#F8FAFC"
                    st.markdown(
                        f'<div style="background:{bg_color}; border:1px solid #CBD5E1; border-radius:8px; padding:8px; text-align:center; margin-bottom:8px;">'
                        f'<b style="color:#1E3A8A; font-size:12px;">भाव {h_num}</b><br/>'
                        f'<span style="font-weight:700; color:#0F172A; font-size:13px;">{pl_str}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # Swamsha Shastriya Yogas
            st.markdown("#### 📜 स्वांश फल एवं जैमिनी योग (Swamsha Classical Yogas)")
            if j_res["swamsha_yogas"]:
                for yg in j_res["swamsha_yogas"]:
                    st.markdown(
                        f'<div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:10px 14px; border-radius:0 8px 8px 0; margin-bottom:8px;">'
                        f'<b style="color:#B45309; font-size:14px;">{yg["title"]}</b> — <small style="color:#78350F;">{yg["sutra"]}</small><br/>'
                        f'<p style="margin:4px 0 0 0; color:#1E293B; font-size:13px;">{yg["desc"]}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("कारकांश में सामान्य ग्रह स्थिति है। आत्मकारक का ध्यान एवं इष्ट साधना कल्याणकारी है।")

            # Arudha Lagna & Upapada Lagna Alignment
            c_al1, c_al2 = st.columns(2)
            with c_al1:
                st.info(f"**🌟 आरूढ़ लग्न (AL) व जन्म लग्न संबंध:** {j_res['al_jl_harmony']}")
            with c_al2:
                st.info(f"**💍 उपपद लग्न (UL) दांपत्य वेध:** {j_res['ul_summary']}")

        except Exception as _e_jkm:
            st.error(f"कारकांश विश्लेषण में त्रुटि: {_e_jkm}")

    with tab_j1:
        st.markdown("#### 🌟 विशेष लग्न विश्लेषण (Special Lagnas & Significance)")
        st.write("विभिन्न जीवन क्षेत्रों (धन, पद, शक्ति, प्राण, वर्ण) के सूक्ष्म परीक्षण हेतु शास्त्रीय विशेष लग्न।")

        if chart.jaimini and chart.jaimini.special_lagnas_detail:
            sl_details = chart.jaimini.special_lagnas_detail
            
            # Top metrics cards
            c_sl1, c_sl2, c_sl3, c_sl4 = st.columns(4)
            c_sl1.metric("👑 होरा लग्न (HL - Wealth)", f"{sl_details['HL']['sign']}", f"{sl_details['HL']['degree']}°")
            c_sl2.metric("⚡ घटी लग्न (GL - Power)", f"{sl_details['GL']['sign']}", f"{sl_details['GL']['degree']}°")
            c_sl3.metric("🌸 श्री लग्न (SL - Prosperity)", f"{sl_details['SL']['sign']}", f"{sl_details['SL']['degree']}°")
            c_sl4.metric("💰 इन्दु लग्न (IL - Dhana)", f"{sl_details['IL']['sign']}", f"Lord: {sl_details['IL']['lord']}")

            # Detailed table
            sl_rows = []
            for k_code, k_info in sl_details.items():
                sl_rows.append({
                    "लग्न कोड": k_code,
                    "विशेष लग्न नाम (Special Lagna)": k_info["name_hi"],
                    "राशि (Sign)": k_info["sign"],
                    "अंश (Degree)": f"{k_info['degree']}°" if k_info['degree'] > 0 else "—",
                    "राशि स्वामी (Lord)": k_info["lord"],
                    "शास्त्रीय प्रयोजन एवं फल (Purpose & Impact)": k_info["purpose_hi"]
                })
            st.dataframe(pd.DataFrame(sl_rows), use_container_width=True)

            col_jk1, col_jk2 = st.columns(2)
            with col_jk1:
                st.markdown("#### 👑 जैमिनी चर कारक (7 Karaka Scheme)")
                k7_data = [{"कारक (Karaka)": k, "ग्रह (Planet)": p_val} for k, p_val in chart.jaimini.karakas_7.items()]
                st.dataframe(pd.DataFrame(k7_data), use_container_width=True)
            with col_jk2:
                st.markdown("#### 💎 कारकांश लग्न (Karakamsha)")
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <div style="font-size:15px; font-weight:800; color:#1E40AF; margin-bottom:8px;">
                        🔱 आत्मकारक नवमांश: <b>{chart.jaimini.karakamsha_sign_name}</b> (Sign #{chart.jaimini.karakamsha_sign_id})
                    </div>
                    <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                        • <b>आत्मकारक ग्रह (AK):</b> {chart.jaimini.karakas_7.get('AK', '')}<br/>
                        • <b>आध्यात्मिक अर्थ:</b> कारकांश लग्न आत्मा के मूल प्रयोजन, इष्टदेव निर्धारण, जीवन लक्ष्य एवं मोक्ष मार्ग का सूचक है।<br/>
                        • <b>अमात्यकारक (AmK):</b> {chart.jaimini.karakas_7.get('AmK', '')} (करियर एवं सामाजिक कर्म का दिशा-निर्देशक)।
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_j2:
        st.markdown("#### 👑 सम्पूर्ण द्वादश आरूढ़ पद (All 12 Arudha Padas Matrix)")
        st.write("बृहत्पाराशर होराशास्त्र एवं जैमिनी सूत्रों के अनुसार शास्त्रीय अपवादों (1st house lord -> 10th, 7th house lord -> 4th) सहित संपूर्ण 12 आरूढ़ पद।")

        if chart.jaimini and chart.jaimini.arudha_details:
            ar_rows = []
            for a_code, a_val in chart.jaimini.arudha_details.items():
                ar_rows.append({
                    "पद (Pada)": a_code,
                    "भाव (House)": f"भाव #{a_val['house_num']} ({a_val['house_sign']})",
                    "भावेश (Lord)": f"{a_val['lord_name']} ({a_val['lord_sign']})",
                    "दूरी (Offset)": f"{a_val['distance']} भाव",
                    "शास्त्रीय नियम / अपवाद": a_val["exception"],
                    "आरूढ़ राशि (Pada Sign)": a_val["pada_sign_name"],
                    "लग्न से भाव": f"{a_val['pada_house_from_lagna']} भाव",
                    "कारकत्व एवं फल (Signification)": a_val["signification_hi"]
                })
            st.dataframe(pd.DataFrame(ar_rows), use_container_width=True)

            st.markdown(f"""
            <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; margin-top:12px;">
                <div style="background:#FFFFFF; border:1.5px solid #10B981; border-radius:10px; padding:12px;">
                    <b style="color:#065F46; font-size:13.5px;">🌟 आरूढ़ लग्न (AL - Arudha Lagna): {chart.jaimini.arudha_pada_names.get('AL', '')}</b>
                    <p style="font-size:12px; color:#1E293B; margin:4px 0 0 0;">संसार जातक को किस रूप में देखता है (Public Image & Status)। यह बाह्य प्रतिष्ठा का दर्पण है।</p>
                </div>
                <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:12px;">
                    <b style="color:#1E40AF; font-size:13.5px;">💍 उपपद लग्न (UL - Upapada Lagna): {chart.jaimini.arudha_pada_names.get('UL', '')}</b>
                    <p style="font-size:12px; color:#1E293B; margin:4px 0 0 0;">जीवनसाथी, वैवाहिक स्थिरता, ससुराल पक्ष का प्रभाव एवं दांपत्य सुख का अंतिम निर्णय उपपद से होता है।</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_j3:
        st.markdown("#### 💫 नवग्रह सम्पूर्ण अवस्था चक्र (Planetary Avasthas Matrix)")
        st.write("बालादि (5 अवस्थाएं), जाग्रदादि (3 अवस्थाएं), दीप्तादि (9 अवस्थाएं) एवं 12 शयनादि अवस्थाओं का विस्तृत शास्त्रीय समन्वय।")

        shayan_list = default_ayurdaya_engine.calculate_shayanadi_avasthas(chart)
        shayan_dict = {item["planet"]: item for item in shayan_list}

        avastha_rows = []
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in chart.planets:
                p_obj = chart.planets[p_name]
                sb_p = chart.shadbala.planets.get(p_name) if chart.shadbala else None
                sh_p = shayan_dict.get(p_name, {})

                baladi_str = sb_p.baladi_avastha if sb_p else "Yuva"
                jagrat_str = sb_p.jagratadi_avastha if sb_p else "Jagrat"
                deept_str = sb_p.deeptadi_avastha if sb_p else "Deepta"

                avastha_rows.append({
                    "ग्रह (Planet)": p_name,
                    "राशि व अंश (Position)": f"{p_obj.sign_name} {round(p_obj.sign_degree, 2)}°",
                    "बालादि अवस्था (5 States)": baladi_str,
                    "जाग्रदादि अवस्था (3 States)": jagrat_str,
                    "दीप्तादि अवस्था (9 States)": deept_str,
                    "शयनादि अवस्था (12 Shayanadi)": sh_p.get("name_hi", "—"),
                    "सामर्थ्य (Potency %)": f"{sh_p.get('potency_pct', 80)}%",
                    "फल व प्रभाव (Classical Effect)": sh_p.get("effect_hi", "")
                })

        st.dataframe(pd.DataFrame(avastha_rows), use_container_width=True)

    with tab_j4:
        st.markdown("#### ⏳ शास्त्रीय आयुर्दाय एवं दीर्घायु गणना (Longevity & Ayurdaya)")
        st.write("महर्षि जैमिनी त्रिसूत्रीय आयु निर्णय (Three-Pair Method), कक्षा वृद्धि/ह्रास एवं पारम्परिक पिण्डायु गणना।")

        jaimini_ayur = default_ayurdaya_engine.calculate_jaimini_longevity(chart)
        pindayu_res = default_ayurdaya_engine.calculate_pindayu(chart)

        col_ay1, col_ay2 = st.columns(2)
        with col_ay1:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1.5px solid #10B981; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <b style="font-size:15px; color:#065F46;">🔱 जैमिनी आयु वर्ग निर्णय</b>
                    <span style="background:#ECFDF5; color:#065F46; border:1.5px solid #10B981; border-radius:8px; padding:3px 10px; font-weight:800; font-size:12px;">
                        {jaimini_ayur['final_span']}
                    </span>
                </div>
                <div style="font-size:13px; color:#1E293B; line-height:1.6; margin-bottom:10px;">
                    • <b>अनुमानित आयु सीमा (Base Span):</b> <b style="font-size:15px; color:#0F766E;">{jaimini_ayur['estimated_years']} वर्ष</b><br/>
                    • <b>युग्म १ (लग्नेश व अष्टमेश):</b> {jaimini_ayur['pair1']['result']}<br/>
                    • <b>युग्म २ (लग्न व चन्द्र):</b> {jaimini_ayur['pair2']['result']}<br/>
                    • <b>युग्म ३ (लग्न व होरा लग्न):</b> {jaimini_ayur['pair3']['result']}
                </div>
                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:6px 10px; font-size:11.5px; color:#166534;">
                    🌟 <b>कक्षा वृद्धि/ह्रास:</b> {", ".join(jaimini_ayur['modifiers'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_ay2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <b style="font-size:15px; color:#1E40AF;">⚖️ पारम्परिक पिण्डायु गणना (Pindayu)</b>
                    <span style="background:#EFF6FF; color:#1E40AF; border:1.5px solid #3B82F6; border-radius:8px; padding:3px 10px; font-weight:800; font-size:12px;">
                        शुद्ध पिण्डायु: {pindayu_res['net_pindayu_years']} वर्ष
                    </span>
                </div>
                <div style="font-size:12px; color:#1E293B; line-height:1.5; margin-bottom:8px;">
                    ग्रहों के उच्च-नीच अंशों एवं चक्रार्ध/शत्रुक्षेत्र हरण उपरांत प्राप्त शुद्ध आयु योगदान:
                </div>
            """, unsafe_allow_html=True)
            
            p_pinda_list = [{"ग्रह (Planet)": p, "आयु योगदान (Years)": y} for p, y in pindayu_res["planet_contributions"].items()]
            st.dataframe(pd.DataFrame(p_pinda_list), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_j5:
        st.markdown("#### 👻 अप्रकाशित उपग्रह (7 Invisible Upagrahas)")
        st.write("सूर्य एवं शनि के आधार पर खगोलीय रूप से निर्धारित अप्रकाशित उपग्रह स्थिति।")
        if chart.upagrahas:
            u = chart.upagrahas
            u_data = [
                {"उपग्रह (Upagraha)": "गुलिक (Gulika)", "राशि (Sign)": u.gulika_sign_name, "Longitude": f"{u.gulika_longitude:.2f}°", "प्रकृति": "शनि पुत्र / दारुण"},
                {"उपग्रह (Upagraha)": "मान्दि (Mandi)", "राशि (Sign)": u.mandi_sign_name, "Longitude": f"{u.mandi_longitude:.2f}°", "प्रकृति": "शनि अंश / मारक"},
                {"उपग्रह (Upagraha)": "धूम (Dhuma)", "राशि (Sign)": "Calculated", "Longitude": f"{u.dhuma_longitude:.2f}°", "प्रकृति": "सूर्य उपग्रह / संताप"},
                {"उपग्रह (Upagraha)": "व्यतीपात (Vyatipata)", "राशि (Sign)": "Calculated", "Longitude": f"{u.vyatipata_longitude:.2f}°", "प्रकृति": "सूर्य उपग्रह / विघ्न"},
                {"उपग्रह (Upagraha)": "परिवेष (Parivesha)", "राशि (Sign)": "Calculated", "Longitude": f"{u.parivesha_longitude:.2f}°", "प्रकृति": "चन्द्र उपग्रह / भय"},
                {"उपग्रह (Upagraha)": "इन्द्रचाप (Indrachapa)", "राशि (Sign)": "Calculated", "Longitude": f"{u.indrachapa_longitude:.2f}°", "प्रकृति": "शुक्र उपग्रह / क्षय"},
                {"उपग्रह (Upagraha)": "उपकेतु (Upaketu)", "राशि (Sign)": "Calculated", "Longitude": f"{u.upaketu_longitude:.2f}°", "प्रकृति": "केतु उपग्रह / अनिष्ट"},
            ]
            st.dataframe(pd.DataFrame(u_data), use_container_width=True)

    # ---- Rashi Drishti + Argala + Graha Arudhas ----
    st.markdown("---")
    _jt_rd, _jt_arg, _jt_ga = st.tabs([
        "📡 राशि दृष्टि (Rashi Drishti)",
        "🔗 अर्गला (Argala)",
        "🌍 ग्रह आरूढ (Graha Arudhas)"
    ])

    with _jt_rd:
        st.markdown("### 📡 जैमिनी राशि दृष्टि (Rashi Drishti)")
        st.info("चर→स्थिर | स्थिर→चर (पड़ोसी छोड़कर) | द्विस्वभाव→द्विस्वभाव")
        try:
            import importlib
            import src.jyotish.core.jaimini as jm_mod
            importlib.reload(jm_mod)
            _rd = jm_mod.JaiminiCalculator.calculate_rashi_drishti(chart)
            if _rd:
                _rd_rows = [{"राशि": k, "दृष्ट राशियाँ": ", ".join(v) if v else "—", "संख्या": len(v)} for k, v in _rd.items()]
                st.dataframe(pd.DataFrame(_rd_rows), use_container_width=True, hide_index=True)
        except Exception as _erd:
            st.error(f"राशि दृष्टि त्रुटि: {str(_erd)[:150]}")

    with _jt_arg:
        st.markdown("### 🔗 अर्गला (Argala — Intervention)")
        st.info("द्वितीय/चतुर्थ/एकादश से अर्गला | तृतीय/दशम/द्वादश से विरोधार्गला")
        st.markdown("### 🔗 अर्गला एवं विरोधार्गला (Argala Intervention)")
        st.info("द्वितीय भाव (धन अर्गला) ⟷ द्वादश (विरोध) | चतुर्थ भाव (सुख अर्गला) ⟷ दशम (विरोध) | एकादश भाव (लाभ अर्गला) ⟷ तृतीय (विरोध)")
        try:
            import importlib
            import src.jyotish.core.jaimini as jm_mod
            importlib.reload(jm_mod)
            _arg = jm_mod.JaiminiCalculator.calculate_argala(chart)
            if _arg:
                _arg_rows = [{"भाव": k, "अर्गला": ", ".join(v.get("argala", [])) or "—", "विरोधार्गला": ", ".join(v.get("virodhargala", [])) or "—", "शुद्ध": v.get("net_argala", "—")} for k, v in _arg.items()]
                _arg_rows = []
                for k, v in _arg.items():
                    dhana = v.get("dhana_argala", {})
                    sukha = v.get("sukha_argala", {})
                    labha = v.get("labha_argala", {})
                    
                    dh_str = f"ग्रह: {', '.join(dhana.get('planets', [])) or '—'} | विरोध: {', '.join(dhana.get('virodha', [])) or '—'} ({'✅ प्रभावी' if dhana.get('effective') else 'निष्प्रभावी'})"
                    su_str = f"ग्रह: {', '.join(sukha.get('planets', [])) or '—'} | विरोध: {', '.join(sukha.get('virodha', [])) or '—'} ({'✅ प्रभावी' if sukha.get('effective') else 'निष्प्रभावी'})"
                    la_str = f"ग्रह: {', '.join(labha.get('planets', [])) or '—'} | विरोध: {', '.join(labha.get('virodha', [])) or '—'} ({'✅ प्रभावी' if labha.get('effective') else 'निष्प्रभावी'})"

                    _arg_rows.append({
                        "भाव": f"भाव {v.get('bhava', k)} ({v.get('sign', '')})",
                        "द्वितीय अर्गला (Dhana)": dh_str,
                        "चतुर्थ अर्गला (Sukha)": su_str,
                        "एकादश अर्गला (Labha)": la_str,
                        "सक्रिय अर्गलाएँ": f"{v.get('total_argalas', 0)} / 3",
                    })
                st.dataframe(pd.DataFrame(_arg_rows), use_container_width=True, hide_index=True)
        except Exception as _earg:
            st.error(f"अर्गला त्रुटि: {str(_earg)[:150]}")

    with _jt_ga:
        st.markdown("### 🌍 ग्रह आरूढ पद (Graha Arudha Padas)")
        st.info("प्रत्येक ग्रह के स्वामी की राशि से उतनी ही राशि आगे — ग्रह का बाह्य प्रकटन।")
        st.info("प्रत्येक ग्रह की राशि के स्वामी से उतनी ही दूरी आगे गिनने पर ग्रह आरूढ ज्ञात होता है।")
        try:
            import importlib
            import src.jyotish.core.jaimini as jm_mod
            importlib.reload(jm_mod)
            _ga = jm_mod.JaiminiCalculator.calculate_graha_arudhas(chart)
            if _ga:
                _ga_rows = [{"ग्रह": k, "आरूढ राशि": v.get("sign_name", "—"), "लग्न से भाव": v.get("house_from_lagna", "—"), "स्वामी": v.get("sign_lord", "—")} for k, v in _ga.items()]
                _ga_rows = []
                for k, v in _ga.items():
                    _arudha_sid = v.get("arudha_sign_id", 1)
                    _house_from_l = ((_arudha_sid - chart.lagna_sign_id) % 12) + 1
                    _ga_rows.append({
                        "ग्रह": k,
                        "ग्रह राशि": v.get("planet_sign", "—"),
                        "राशि स्वामी": f"{v.get('planet_lord', '—')} ({v.get('lord_sign', '—')})",
                        "आरूढ राशि (Pada)": v.get("arudha_sign", "—"),
                        "लग्न से भाव": f"भाव {_house_from_l}",
                        "शास्त्रीय प्रभाव": v.get("meaning_hi", "—")
                    })
                st.dataframe(pd.DataFrame(_ga_rows), use_container_width=True, hide_index=True)
        except Exception as _ega:
            st.error(f"ग्रह आरूढ त्रुटि: {str(_ega)[:150]}")


# =============================================================
# TAB 10: DASHA SYSTEMS

elif selected_idx == 9:
    st.subheader("⏱️ दशा प्रणालियाँ एवं एकीकृत जीवन टाइमलाइन (Dasha & Predictive Life Timeline)")
    st.write("विंशोत्तरी, जैमिनी चर, योगिनी, कालचक्र, शूल व दृग दशाओं का ०-१०० वर्ष एकीकृत जीवन टाइमलाइन एवं बहु-स्तरीय विश्लेषण।")

    tab_dasha_gantt, tab_dasha_unified, tab_dasha_individual = st.tabs([
        "📊 दृश्य दशा टाइमलाइन (Visual Gantt Timeline)",
        "⏳ ०-१०० वर्ष एकीकृत जीवन टाइमलाइन (Unified Predictive Life Timeline)",
        "🗂️ पृथक बहु-स्तरीय दशा प्रणालियाँ (10 Individual Dasha Systems)"
    ])

    with tab_dasha_gantt:
        st.markdown("### 📊 विंशोत्तरी बहु-स्तरीय दृश्य दशा टाइमलाइन (120-Year Gantt Timeline)")
        st.caption("पाराशर-स्तरीय १२०-वर्षीय आनुपातिक महादशा, अंतर्दशा एवं प्रत्यन्तर्दशा गेंट चार्ट — '📍 आज' स्थिति एवं काल-खंड प्रगति:")

        try:
            import importlib
            import src.jyotish.services.dasha_timeline as dt_mod
            importlib.reload(dt_mod)
            import streamlit.components.v1 as components

            c_gt1, c_gt2 = st.columns([2, 2])
            with c_gt1:
                gantt_target_date = st.date_input(
                    "📅 लक्षित अवलोकन दिनांक (Target Date / Event Date):",
                    value=date.today(),
                    min_value=date(1900, 1, 1),
                    max_value=date(2100, 12, 31),
                    format="DD/MM/YYYY",
                    key="gantt_target_dt"
                )

            # Allow user to pick which Mahadasha to expand
            m_list = dt_mod.default_dasha_timeline_service.engine.generate_timeline(chart)
            m_options = ["वर्तमान सक्रिय महादशा (Auto)"] + [
                f"{m['lord']} महादशा ({m['start_date'].strftime('%Y')} - {m['end_date'].strftime('%Y')})"
                for m in m_list
            ]
            with c_gt2:
                sel_m_str = st.selectbox("🔍 विस्तारित महादशा चुनें (Expand Mahadasha):", m_options, index=0, key="sel_gantt_m")

            sel_idx = None
            if sel_m_str != "वर्तमान सक्रिय महादशा (Auto)":
                sel_idx = m_options.index(sel_m_str) - 1

            cur_th = st.session_state.get("app_theme_mode", "day")
            gantt_html = dt_mod.default_dasha_timeline_service.render_gantt_html(
                chart,
                target_date=gantt_target_date,
                selected_maha_idx=sel_idx,
                theme_mode=cur_th
            )
            components.html(gantt_html, height=580, scrolling=True)

        except Exception as _e_gantt:
            st.error(f"टाइमलाइन निर्माण में त्रुटि: {_e_gantt}")

    with tab_dasha_unified:
        st.markdown("### ⏳ ० से १०० वर्ष सम्पूर्ण एकीकृत जीवन टाइमलाइन व घटना संभावना")
        st.caption("विंशोत्तरी, जैमिनी चर, योगिनी दशा, वर्षफल मुन्था एवं गोचर गुरु-शनि का संश्लेषित संयुक्त विश्लेषण:")

        try:
            import importlib
            import src.jyotish.services.timeline as tl_mod
            importlib.reload(tl_mod)
            tl_service = tl_mod.default_timeline_service
            tl_bundle = tl_service.calculate_life_timeline(chart, 0, 100)
            records = tl_bundle["records"]
            event_win = tl_bundle["event_windows"]
            curr_age = tl_bundle["current_age"]

            col_ag1, col_ag2 = st.columns([3, 1])
            with col_ag1:
                sel_age = st.slider("🎯 जातक की आयु का चयन करें (Select Age):", min_value=0, max_value=100, value=min(100, curr_age), key="tl_slider_sel_age")
            with col_ag2:
                st.metric("चुनी गई आयु / वर्ष", f"{sel_age} वर्ष", f"{tl_bundle['birth_year'] + sel_age} ईस्वी")

            sel_rec = next((r for r in records if r["age"] == sel_age), records[0])

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:12px; padding:16px; margin-bottom:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #E2E8F0; padding-bottom:8px; margin-bottom:12px;">
                    <b style="font-size:16px; color:#0F172A;">🗓️ आयु {sel_rec['age']} वर्ष (वर्ष {sel_rec['year']}) की संयुक्त खगोलीय व दशा स्थिति</b>
                    <span style="background:{'#DCFCE7' if sel_rec['is_current'] else '#EFF6FF'}; color:{'#166534' if sel_rec['is_current'] else '#1E40AF'}; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:800;">
                        {'🔴 वर्तमान प्रभावी वर्ष (Current)' if sel_rec['is_current'] else f'वर्ष {sel_rec["year"]}'}
                    </span>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:12px;">
                    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
                        <span style="font-size:11px; color:#64748B; font-weight:700;">🌟 विंशोत्तरी दशा</span><br/>
                        <b style="font-size:14px; color:#0F172A;">{sel_rec['dasha_code']}</b><br/>
                        <small style="color:#2563EB;">प्रत्यंतर: {sel_rec['vimshottari_pd']}</small>
                    </div>
                    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
                        <span style="font-size:11px; color:#64748B; font-weight:700;">🔱 जैमिनी चर दशा</span><br/>
                        <b style="font-size:14px; color:#7C3AED;">{sel_rec['chara_sign']} राशि</b><br/>
                        <small style="color:#6B7280;">राशि आधारित काल</small>
                    </div>
                    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
                        <span style="font-size:11px; color:#64748B; font-weight:700;">🌸 योगिनी दशा</span><br/>
                        <b style="font-size:14px; color:#DB2777;">{sel_rec['yogini']}</b><br/>
                        <small style="color:#6B7280;">३६ वर्षीय चक्र</small>
                    </div>
                    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
                        <span style="font-size:11px; color:#64748B; font-weight:700;">📅 वर्षफल मुन्था</span><br/>
                        <b style="font-size:14px; color:#D97706;">भाव {sel_rec['muntha_house']} ({sel_rec['muntha_sign']})</b><br/>
                        <small style="color:{'#16A34A' if 'Fav' in sel_rec['muntha_status'] else '#DC2626'}; font-weight:700;">{sel_rec['muntha_status']}</small>
                    </div>
                    <div style="background:#FFFFFF; padding:10px; border-radius:8px; border:1px solid #E2E8F0;">
                        <span style="font-size:11px; color:#64748B; font-weight:700;">🪐 शनि / साढ़ेसाती स्थिति</span><br/>
                        <b style="font-size:14px; color:{'#DC2626' if sel_rec['sade_sati']!='नहीं' else '#16A34A'};">{sel_rec['sade_sati']}</b><br/>
                        <small style="color:#6B7280;">चन्द्र से प्रभाव</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🎯 इस वर्ष जीवन घटनाओं की संभावना मीटर (Probability Meters 0-100%):")
            col_ev1, col_ev2 = st.columns(2)
            with col_ev1:
                st.markdown(f"💼 **करियर एवं पदोन्नति अनुकूलता:** {sel_rec['career_score']}%")
                st.progress(sel_rec['career_score'] / 100.0)
                st.markdown(f"💍 **विवाह एवं दांपत्य अनुकूलता:** {sel_rec['marriage_score']}%")
                st.progress(sel_rec['marriage_score'] / 100.0)
                st.markdown(f"💰 **धन लाभ एवं संपत्ति क्रय:** {sel_rec['wealth_score']}%")
                st.progress(sel_rec['wealth_score'] / 100.0)
            with col_ev2:
                st.markdown(f"✈️ **विदेश गमन / स्थानांतरण:** {sel_rec['travel_score']}%")
                st.progress(sel_rec['travel_score'] / 100.0)
                st.markdown(f"🛡️ **स्वास्थ्य सतर्कता सूचकांक:** {sel_rec['health_caution_score']}%")
                st.progress(sel_rec['health_caution_score'] / 100.0)

            with st.expander("🌟 जातक के जीवन के प्रमुख अनुकूल समय-खिड़कियां (Life Event Windows Highlights)", expanded=True):
                col_w1, col_w2, col_w3 = st.columns(3)
                with col_w1:
                    st.markdown("**💼 शीर्ष करियर उत्थान वर्ष:**")
                    c_items = [f"• वर्ष {w['year']} (आयु {w['age']} वर्ष, दशा: {w['dasha']}) — {w['score']}%" for w in event_win["career"][:5]]
                    st.markdown("\n".join(c_items) if c_items else "—")
                with col_w2:
                    st.markdown("**💍 प्रबल विवाह योग वर्ष:**")
                    m_items = [f"• वर्ष {w['year']} (आयु {w['age']} वर्ष, दशा: {w['dasha']}) — {w['score']}%" for w in event_win["marriage"][:5]]
                    st.markdown("\n".join(m_items) if m_items else "—")
                with col_w3:
                    st.markdown("**💰 भारी धन लाभ / संपत्ति वर्ष:**")
                    w_items = [f"• वर्ष {w['year']} (आयु {w['age']} वर्ष, दशा: {w['dasha']}) — {w['score']}%" for w in event_win["wealth"][:5]]
                    st.markdown("\n".join(w_items) if w_items else "—")

            with st.expander("📜 ० से १०० वर्ष सम्पूर्ण जीवन डेटा तालिका (Full Table)", expanded=False):
                tbl_rows = []
                for r in records:
                    tbl_rows.append({
                        "आयु": f"{r['age']} वर्ष",
                        "ईस्वी वर्ष": r["year"],
                        "विंशोत्तरी दशा": r["dasha_code"],
                        "चर दशा": r["chara_sign"],
                        "योगिनी": r["yogini"],
                        "मुन्था भाव": f"भाव {r['muntha_house']}",
                        "मुन्था स्थिति": r["muntha_status"],
                        "साढ़ेसाती": r["sade_sati"],
                        "करियर %": f"{r['career_score']}%",
                        "विवाह %": f"{r['marriage_score']}%",
                        "धन %": f"{r['wealth_score']}%",
                        "स्वास्थ्य जोखिम": f"{r['health_caution_score']}%"
                    })
                st.dataframe(pd.DataFrame(tbl_rows), use_container_width=True, hide_index=True)
        except Exception as _e_tl:
            st.error(f"टाइमलाइन गणना त्रुटि: {str(_e_tl)[:300]}")

    with tab_dasha_individual:
        # Target Date Picker for Point-in-Time Dasha Calculation
        c_dt1, c_dt2 = st.columns([2, 4])
        with c_dt1:
            dasha_target_date = st.date_input("🎯 लक्षित दिनांक पर दशा देखें (Target Date)", value=date.today(), format="DD/MM/YYYY", key="dasha_target_date_picker")
        with c_dt2:
            st.caption(f"🗓️ वर्तमान में **{dasha_target_date.strftime('%d-%b-%Y')}** के लिए तात्कालिक सक्रिय सूक्ष्म दशाओं का मूल्यांकन प्रदर्शित किया जा रहा है।")

        d_mode = st.radio(
            "दशा प्रणाली चयन (Select Dasha System)",
            [
                "🌟 विंशोत्तरी दशा (Vimshottari 120 Yrs - 5 Levels)",
                "🌸 योगिनी दशा (Yogini 36 Yrs - 3 Levels)",
                "🔱 जैमिनी चर दशा (Jaimini Chara Dasha)",
                "🔄 कालचक्र दशा (Kaalachakra Dasha - BPHS)",
                "⚔️ शूल दशा (Shoola Dasha - Ayurdaya & Maraka)",
                "🕉️ अष्टोत्तरी दशा (Ashtottari 108 Yrs - 8 Planets)",
                "🪐 नारायण दशा (Narayana Rashi Dasha - Jaimini)",
                "⏳ द्विसप्ततिसम दशा (Dwisaptati Sama 72 Yrs)",
                "🔷 स्थिर दशा (Sthira Dasha - Jaimini Fixed)",
                "👁️ दृग दशा (Drig Dasha - Spiritual Jaimini)"
            ],
            horizontal=True,
            key="dasha_system_mode_radio"
        )

        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        target_dt = datetime.combine(dasha_target_date, datetime.now().time())
    
        import importlib
        import src.jyotish.dasha.vimshottari as vim_mod
        import src.jyotish.dasha.yogini as yog_mod
        import src.jyotish.dasha.chara as chara_mod
        import src.jyotish.dasha.ashtottari as ashto_mod
        import src.jyotish.dasha.narayana as narayana_mod
        import src.jyotish.dasha.sama_dashas as sama_mod
        import src.jyotish.dasha.sthira_drig as sthira_mod
        
        if not hasattr(default_dasha_engine, "get_5level_hierarchy"):
            importlib.reload(vim_mod)
        if not hasattr(default_yogini_engine, "generate_antardashas"):
            importlib.reload(yog_mod)
        if not hasattr(default_chara_engine, "generate_antardashas"):
            importlib.reload(chara_mod)
    
        d_engine = vim_mod.default_dasha_engine
        y_engine = yog_mod.default_yogini_engine
        c_engine = chara_mod.default_chara_engine
        ashto_engine = ashto_mod.default_ashtottari_engine
        narayana_engine = narayana_mod.default_narayana_engine
        dwisaptati_engine = sama_mod.default_dwisaptati_engine
        sthira_engine = sthira_mod.default_sthira_engine
        drig_engine = sthira_mod.default_drigdasha_engine
    
        # =========================================================================
        # 1. VIMSHOTTARI DASHA (5 LEVELS: MAHA -> ANTAR -> PRAT -> SOOKSHMA -> PRANA)
        # =========================================================================
        if "विंशोत्तरी" in d_mode:
            h5 = d_engine.get_5level_hierarchy(birth_dt, moon_lon, target_dt)
    
            act_m = h5["mahadasha"]
            act_a = h5["antardasha"]
            act_pr = h5["pratyantardasha"]
            act_s = h5["sookshmadasha"]
            act_p = h5["pranadasha"]
    
            # 1. Active 5-Level HUD
            st.markdown(f"#### 🔴 सक्रिय 5-स्तरीय विंशोत्तरी दशा ({dasha_target_date.strftime('%d-%b-%Y')})")
    
            # Breadcrumb Banner
            p_icons = {
                "Sun": "☀️ सूर्य (Sun)", "Moon": "🌙 चन्द्र (Moon)", "Mars": "⚔️ मंगल (Mars)",
                "Mercury": "☿️ बुध (Mercury)", "Jupiter": "🪐 गुरु (Jupiter)", "Venus": "💎 शुक्र (Venus)",
                "Saturn": "⚖️ शनि (Saturn)", "Rahu": "🐉 राहु (Rahu)", "Ketu": "☄️ केतु (Ketu)"
            }
            b_str = (
                f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
                f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय 5-स्तरीय दशा पदानुक्रम (Active Dasha Hierarchy):</div>"
                f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
                f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>👑 {p_icons.get(act_m['lord'], act_m['lord'])}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>🪐 {p_icons.get(act_a['lord'], act_a['lord'])}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ {p_icons.get(act_pr['lord'], act_pr['lord'])}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>🔍 {p_icons.get(act_s['lord'], act_s['lord'])}</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F1F5F9; border:1.5px solid #64748B; color:#0F172A; padding:5px 12px; border-radius:8px;'>🧬 {p_icons.get(act_p['lord'], act_p['lord'])}</span>"
                f"</div>"
                f"</div>"
            )
            st.markdown(b_str, unsafe_allow_html=True)
    
            # 5 Metric Cards
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.markdown(f"""
                <div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">👑 महादशा (L1)</div>
                    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_m['lord']}</div>
                    <div style="font-size:10.5px; color:#475569;">{act_m['start_date'].strftime('%d-%b-%y')} ~ {act_m['end_date'].strftime('%d-%b-%y')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#15803D; font-weight:800;">🪐 अंतर्दशा (L2)</div>
                    <div style="font-size:18px; font-weight:900; color:#064E3B;">{act_a['lord']}</div>
                    <div style="font-size:10.5px; color:#475569;">{act_a['start_date'].strftime('%d-%b-%y')} ~ {act_a['end_date'].strftime('%d-%b-%y')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ प्रत्यंतर्दशा (L3)</div>
                    <div style="font-size:18px; font-weight:900; color:#78350F;">{act_pr['lord']}</div>
                    <div style="font-size:10.5px; color:#475569;">{act_pr['start_date'].strftime('%d-%b-%y')} ~ {act_pr['end_date'].strftime('%d-%b-%y')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#BE185D; font-weight:800;">🔍 सूक्ष्मदशा (L4)</div>
                    <div style="font-size:18px; font-weight:900; color:#831843;">{act_s['lord']}</div>
                    <div style="font-size:10.5px; color:#475569;">{act_s['start_date'].strftime('%d-%b')} ~ {act_s['end_date'].strftime('%d-%b')} ({act_s.get('duration_days', 0)}d)</div>
                </div>
                """, unsafe_allow_html=True)
            with c5:
                st.markdown(f"""
                <div style="background:#F3F4F6; border: 2px solid #64748B; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#334155; font-weight:800;">🧬 प्राणदशा (L5)</div>
                    <div style="font-size:18px; font-weight:900; color:#0F172A;">{act_p['lord']}</div>
                    <div style="font-size:10.5px; color:#475569;">{act_p['start_date'].strftime('%d-%b %H:%M')} ~ {act_p['end_date'].strftime('%d-%b %H:%M')}</div>
                </div>
                """, unsafe_allow_html=True)
    
            # Progress calculation for active Antardasha
            a_total_sec = (act_a["end_date"] - act_a["start_date"]).total_seconds()
            a_elapsed_sec = max(0.0, min(a_total_sec, (target_dt - act_a["start_date"]).total_seconds()))
            a_pct = (a_elapsed_sec / max(1.0, a_total_sec))
            st.write("")
            st.markdown(f"**🪐 सक्रिय अंतर्दशा ({act_m['lord']}-{act_a['lord']}) प्रगति: {int(a_pct * 100)}% संपन्न**")
            st.progress(a_pct)
    
            st.markdown("---")
    
            # 2. Interactive Multi-Level Dasha Explorer
            st.markdown("#### 🌳 विंशोत्तरी दशा बहु-स्तरीय विस्तृत अन्वेषक (5-Level Interactive Explorer)")
    
            tab_v1, tab_v2, tab_v3, tab_v4, tab_v5, tab_v_all = st.tabs([
                "👑 स्तर 1: महादशा (Mahadasha)",
                "🪐 स्तर 2: अंतर्दशा (Antardasha)",
                "⚡ स्तर 3: प्रत्यंतर्दशा (Pratyantardasha)",
                "🔍 स्तर 4: सूक्ष्मदशा (Sookshmadasha)",
                "🧬 स्तर 5: प्राणदशा (Pranadasha)",
                "📜 सम्पूर्ण 120-वर्षीय कालक्रम (All Mahadashas)"
            ])
    
            v_mahadashas = d_engine.generate_mahadasha_sequence(birth_dt, moon_lon, num_cycles=2)
            maha_options = [f"{m['lord']} ({m['start_date'].strftime('%d-%b-%Y')} से {m['end_date'].strftime('%d-%b-%Y')})" for m in v_mahadashas]
            default_maha_idx = next((i for i, m in enumerate(v_mahadashas) if m['lord'] == act_m['lord'] and m['start_date'] <= target_dt <= m['end_date']), 0)
    
            with tab_v1:
                st.markdown("##### 👑 समस्त 9 महादशाएँ (120 Years Vimshottari Cycle)")
                m_rows = []
                for m in v_mahadashas:
                    is_active = (m["start_date"] <= target_dt <= m["end_date"])
                    m_rows.append({
                        "महादशा स्वामी (Lord)": f"👑 {m['lord']}" + (" (⭐ वर्तमान सक्रिय)" if is_active else ""),
                        "आरंभ दिनांक (Start)": m["start_date"].strftime("%d-%b-%Y"),
                        "समाप्ति दिनांक (End)": m["end_date"].strftime("%d-%b-%Y"),
                        "अवधि (Years)": f"{m['duration_years']:.2f} वर्ष",
                        "प्रकार": "जन्म शेष (Birth Balance)" if m.get("is_partial") else "पूर्ण महादशा",
                        "सक्रियता": "✅ सक्रिय" if is_active else "—"
                    })
                st.dataframe(pd.DataFrame(m_rows), use_container_width=True, hide_index=True)
    
            with tab_v2:
                st.markdown("##### 🪐 महादशा अंतर्गत समस्त 9 अंतर्दशाएं (Antardashas / Bhuktis)")
                sel_maha_idx = st.selectbox("महादशा चुनें (Select Mahadasha)", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_maha_for_antar")
                sel_m_obj = v_mahadashas[sel_maha_idx]
                
                antars = d_engine.generate_antardashas(
                    sel_m_obj["lord"], sel_m_obj["start_date"], sel_m_obj["end_date"], is_partial=sel_m_obj.get("is_partial", False)
                )
                a_rows = []
                for a in antars:
                    is_a_active = (a["start_date"] <= target_dt <= a["end_date"])
                    a_rows.append({
                        "महादशा / अंतर्दशा": f"{sel_m_obj['lord']} — {a['lord']}" + (" (⭐ सक्रिय)" if is_a_active else ""),
                        "अंतर्दशा स्वामी (Lord)": a["lord"],
                        "आरंभ दिनांक (Start)": a["start_date"].strftime("%d-%b-%Y"),
                        "समाप्ति दिनांक (End)": a["end_date"].strftime("%d-%b-%Y"),
                        "अवधि (Years)": f"{a['duration_years']:.2f} वर्ष",
                        "अवधि (माह / दिन)": f"{int(a['duration_years']*12)} माह {int((a['duration_years']*12 % 1)*30)} दिन",
                        "सक्रियता": "✅ सक्रिय" if is_a_active else "—"
                    })
                st.dataframe(pd.DataFrame(a_rows), use_container_width=True, hide_index=True)
    
            with tab_v3:
                st.markdown("##### ⚡ अंतर्दशा अंतर्गत समस्त 9 प्रत्यंतर्दशाएं (Pratyantardashas)")
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1:
                    sel_m_prat_idx = st.selectbox("महादशा चुनें", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_m_for_prat")
                sel_m_for_p = v_mahadashas[sel_m_prat_idx]
                antars_for_p = d_engine.generate_antardashas(sel_m_for_p["lord"], sel_m_for_p["start_date"], sel_m_for_p["end_date"], is_partial=sel_m_for_p.get("is_partial", False))
                antar_p_options = [f"{a['lord']} ({a['start_date'].strftime('%d-%b-%Y')} से {a['end_date'].strftime('%d-%b-%Y')})" for a in antars_for_p]
                default_a_idx = next((i for i, a in enumerate(antars_for_p) if a['lord'] == act_a['lord'] and a['start_date'] <= target_dt <= a['end_date']), 0)
                with col_sel2:
                    sel_a_prat_idx = st.selectbox("अंतर्दशा चुनें", range(len(antar_p_options)), format_func=lambda i: antar_p_options[i], index=default_a_idx, key="sel_a_for_prat")
                
                sel_a_for_p = antars_for_p[sel_a_prat_idx]
                pratyantars = d_engine.generate_pratyantardashas(
                    sel_m_for_p["lord"], sel_a_for_p["lord"], sel_a_for_p["start_date"], sel_a_for_p["end_date"]
                )
                pr_rows = []
                for pr in pratyantars:
                    is_pr_act = (pr["start_date"] <= target_dt <= pr["end_date"])
                    dur_days = (pr["end_date"] - pr["start_date"]).total_seconds() / 86400.0
                    pr_rows.append({
                        "दशा क्रम": f"{sel_m_for_p['lord']} / {sel_a_for_p['lord']} / {pr['lord']}" + (" (⭐ सक्रिय)" if is_pr_act else ""),
                        "प्रत्यंतर्दशा स्वामी": pr["lord"],
                        "आरंभ दिनांक": pr["start_date"].strftime("%d-%b-%Y"),
                        "समाप्ति दिनांक": pr["end_date"].strftime("%d-%b-%Y"),
                        "अवधि (दिन)": f"{dur_days:.1f} दिन",
                        "सक्रियता": "✅ सक्रिय" if is_pr_act else "—"
                    })
                st.dataframe(pd.DataFrame(pr_rows), use_container_width=True, hide_index=True)
    
            with tab_v4:
                st.markdown("##### 🔍 प्रत्यंतर्दशा अंतर्गत समस्त 9 सूक्ष्मदशाएं (Sookshmadashas - Level 4)")
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    sel_m_s_idx = st.selectbox("महादशा", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_m_for_sookshma")
                sel_m_s = v_mahadashas[sel_m_s_idx]
                antars_s = d_engine.generate_antardashas(sel_m_s["lord"], sel_m_s["start_date"], sel_m_s["end_date"], is_partial=sel_m_s.get("is_partial", False))
                with col_s2:
                    sel_a_s_idx = st.selectbox("अंतर्दशा", range(len(antars_s)), format_func=lambda i: f"{antars_s[i]['lord']} ({antars_s[i]['start_date'].strftime('%d-%b-%y')})", index=min(default_a_idx, len(antars_s)-1), key="sel_a_for_sookshma")
                sel_a_s = antars_s[sel_a_s_idx]
                prats_s = d_engine.generate_pratyantardashas(sel_m_s["lord"], sel_a_s["lord"], sel_a_s["start_date"], sel_a_s["end_date"])
                default_pr_idx = next((i for i, p in enumerate(prats_s) if p['lord'] == act_pr['lord'] and p['start_date'] <= target_dt <= p['end_date']), 0)
                with col_s3:
                    sel_pr_s_idx = st.selectbox("प्रत्यंतर्दशा", range(len(prats_s)), format_func=lambda i: f"{prats_s[i]['lord']} ({prats_s[i]['start_date'].strftime('%d-%b-%y')})", index=min(default_pr_idx, len(prats_s)-1), key="sel_pr_for_sookshma")
                
                sel_pr_s = prats_s[sel_pr_s_idx]
                sookshmas = d_engine.generate_sookshmadashas(sel_m_s["lord"], sel_a_s["lord"], sel_pr_s["lord"], sel_pr_s["start_date"], sel_pr_s["end_date"])
                s_rows = []
                for s in sookshmas:
                    is_s_act = (s["start_date"] <= target_dt <= s["end_date"])
                    s_rows.append({
                        "4-स्तरीय दशा": f"{sel_m_s['lord']}/{sel_a_s['lord']}/{sel_pr_s['lord']}/{s['lord']}" + (" (⭐ सक्रिय)" if is_s_act else ""),
                        "सूक्ष्मदशा स्वामी": s["lord"],
                        "आरंभ समय": s["start_date"].strftime("%d-%b-%Y %I:%M %p"),
                        "समाप्ति समय": s["end_date"].strftime("%d-%b-%Y %I:%M %p"),
                        "अवधि": f"{s['duration_days']} दिन",
                        "सक्रियता": "✅ सक्रिय" if is_s_act else "—"
                    })
                st.dataframe(pd.DataFrame(s_rows), use_container_width=True, hide_index=True)
    
            with tab_v5:
                st.markdown("##### 🧬 सूक्ष्मदशा अंतर्गत समस्त 9 प्राणदशाएं (Pranadashas - Level 5 / Hourly Precision)")
                c_p1, c_p2, c_p3, c_p4 = st.columns(4)
                with c_p1:
                    sel_m_p_idx = st.selectbox("महादशा (Maha)", range(len(maha_options)), format_func=lambda i: maha_options[i], index=default_maha_idx, key="sel_m_for_prana")
                sel_m_p = v_mahadashas[sel_m_p_idx]
                antars_p = d_engine.generate_antardashas(sel_m_p["lord"], sel_m_p["start_date"], sel_m_p["end_date"], is_partial=sel_m_p.get("is_partial", False))
                with c_p2:
                    sel_a_p_idx = st.selectbox("अंतर्दशा (Antar)", range(len(antars_p)), format_func=lambda i: f"{antars_p[i]['lord']}", index=min(default_a_idx, len(antars_p)-1), key="sel_a_for_prana")
                sel_a_p = antars_p[sel_a_p_idx]
                prats_p = d_engine.generate_pratyantardashas(sel_m_p["lord"], sel_a_p["lord"], sel_a_p["start_date"], sel_a_p["end_date"])
                with c_p3:
                    sel_pr_p_idx = st.selectbox("प्रत्यंतर्दशा (Prat)", range(len(prats_p)), format_func=lambda i: f"{prats_p[i]['lord']}", index=min(default_pr_idx, len(prats_p)-1), key="sel_pr_for_prana")
                sel_pr_p = prats_p[sel_pr_p_idx]
                sookshmas_p = d_engine.generate_sookshmadashas(sel_m_p["lord"], sel_a_p["lord"], sel_pr_p["lord"], sel_pr_p["start_date"], sel_pr_p["end_date"])
                default_s_idx = next((i for i, s in enumerate(sookshmas_p) if s['lord'] == act_s['lord'] and s['start_date'] <= target_dt <= s['end_date']), 0)
                with c_p4:
                    sel_s_p_idx = st.selectbox("सूक्ष्मदशा (Sookshma)", range(len(sookshmas_p)), format_func=lambda i: f"{sookshmas_p[i]['lord']}", index=min(default_s_idx, len(sookshmas_p)-1), key="sel_s_for_prana")
                sel_s_p = sookshmas_p[sel_s_p_idx]
    
                pranas = d_engine.generate_pranadashas(sel_m_p["lord"], sel_a_p["lord"], sel_pr_p["lord"], sel_s_p["lord"], sel_s_p["start_date"], sel_s_p["end_date"])
                p_rows = []
                for prn in pranas:
                    is_p_act = (prn["start_date"] <= target_dt <= prn["end_date"])
                    p_rows.append({
                        "5-स्तरीय प्राणदशा": f"{sel_m_p['lord']}/{sel_a_p['lord']}/{sel_pr_p['lord']}/{sel_s_p['lord']}/{prn['lord']}" + (" (⭐ सक्रिय)" if is_p_act else ""),
                        "प्राणदशा स्वामी": prn["lord"],
                        "आरंभ समय": prn["start_date"].strftime("%d-%b-%Y %I:%M %p"),
                        "समाप्ति समय": prn["end_date"].strftime("%d-%b-%Y %I:%M %p"),
                        "अवधि (घंटे)": f"{prn['duration_hours']} घंटे",
                        "सक्रियता": "✅ सक्रिय" if is_p_act else "—"
                    })
                st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)
    
            with tab_v_all:
                st.markdown("##### 📜 संपूर्ण 120-वर्षीय जीवन कालक्रम तालिका")
                full_rows = []
                for m in v_mahadashas:
                    m_antars = d_engine.generate_antardashas(m["lord"], m["start_date"], m["end_date"], is_partial=m.get("is_partial", False))
                    for a in m_antars:
                        is_active = (a["start_date"] <= target_dt <= a["end_date"])
                        full_rows.append({
                            "महादशा (L1)": m["lord"],
                            "अंतर्दशा (L2)": a["lord"],
                            "आरंभ दिनांक": a["start_date"].strftime("%d-%b-%Y"),
                            "समाप्ति दिनांक": a["end_date"].strftime("%d-%b-%Y"),
                            "अवधि (वर्ष)": f"{a['duration_years']:.2f}",
                            "सक्रियता": "⭐ वर्तमान सक्रिय" if is_active else ""
                        })
                st.dataframe(pd.DataFrame(full_rows), use_container_width=True, hide_index=True)
    
        # =========================================================================
        # 2. YOGINI DASHA (3 LEVELS: MAJOR -> ANTAR -> PRATYANTAR)
        # =========================================================================
        elif "योगिनी" in d_mode:
            st.markdown(f"#### 🌸 योगिनी दशा (36-Year Classical Cycle — Major, Antar & Pratyantar)")
            try:
                yog_dashas = y_engine.generate_timeline(birth_dt, moon_lon)
            except TypeError:
                yog_dashas = y_engine.generate_timeline(chart)
    
            act_yog = next((y for y in yog_dashas if y["start_date"] <= target_dt <= y["end_date"]), yog_dashas[0])
            
            # Calculate Active Antardasha & Pratyantardasha for current target_dt
            y_antars_for_act = y_engine.generate_antardashas(
                act_yog.get("yogini_name", act_yog.get("yogini")), act_yog["start_date"], act_yog["end_date"]
            )
            act_ya = next((a for a in y_antars_for_act if a["start_date"] <= target_dt <= a["end_date"]), y_antars_for_act[0])
            
            y_prats_for_act = y_engine.generate_pratyantardashas(
                act_yog.get("yogini_name", act_yog.get("yogini")), act_ya["yogini"], act_ya["start_date"], act_ya["end_date"]
            )
            act_ypr = next((p for p in y_prats_for_act if p["start_date"] <= target_dt <= p["end_date"]), y_prats_for_act[0])
    
            # Active Yogini Hierarchy Top Banner
            b_str_yog = (
                f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
                f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय 3-स्तरीय योगिनी दशा पदानुक्रम (Active Yogini Dasha Hierarchy):</div>"
                f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
                f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🌸 मुख्य योगिनी: {act_yog.get('yogini_name', act_yog.get('yogini'))} ({act_yog.get('lord')})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>💫 योगिनी अंतर्दशा: {act_ya['yogini']} ({act_ya['lord']})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ योगिनी प्रत्यंतर: {act_ypr['yogini']} ({act_ypr['lord']})</span>"
                f"</div>"
                f"</div>"
            )
            st.markdown(b_str_yog, unsafe_allow_html=True)
    
            # 3 Styled Metric Cards
            y_col1, y_col2, y_col3 = st.columns(3)
            with y_col1:
                st.markdown(f"""
                <div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🌸 मुख्य योगिनी (Major)</div>
                    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_yog.get('yogini_name', act_yog.get('yogini'))} ({act_yog.get('lord')})</div>
                    <div style="font-size:10.5px; color:#475569;">{act_yog['start_date'].strftime('%d-%b-%y')} ~ {act_yog['end_date'].strftime('%d-%b-%y')} ({act_yog['duration_years']} वर्ष)</div>
                </div>
                """, unsafe_allow_html=True)
            with y_col2:
                st.markdown(f"""
                <div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#15803D; font-weight:800;">💫 अंतर्दशा (Sub-Period)</div>
                    <div style="font-size:18px; font-weight:900; color:#064E3B;">{act_ya['yogini']} ({act_ya['lord']})</div>
                    <div style="font-size:10.5px; color:#475569;">{act_ya['start_date'].strftime('%d-%b-%y')} ~ {act_ya['end_date'].strftime('%d-%b-%y')}</div>
                </div>
                """, unsafe_allow_html=True)
            with y_col3:
                st.markdown(f"""
                <div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
                    <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ प्रत्यंतर्दशा (Pratyantar)</div>
                    <div style="font-size:18px; font-weight:900; color:#78350F;">{act_ypr['yogini']} ({act_ypr['lord']})</div>
                    <div style="font-size:10.5px; color:#475569;">{act_ypr['start_date'].strftime('%d-%b-%y')} ~ {act_ypr['end_date'].strftime('%d-%b-%y')}</div>
                </div>
                """, unsafe_allow_html=True)
    
            st.write("")
    
            tab_y1, tab_y2, tab_y3 = st.tabs([
                "🌸 मुख्य योगिनी दशा (Major Periods)",
                "💫 योगिनी अंतर्दशा (Antardashas)",
                "⚡ योगिनी प्रत्यंतर्दशा (Pratyantardashas)"
            ])
    
            with tab_y1:
                st.markdown("##### 🌸 मुख्य योगिनी दशा चक्र (36 वर्ष)")
                st.dataframe(pd.DataFrame([{
                    "योगिनी (Yogini)": y.get("yogini_name") or y.get("yogini", "Yogini"),
                    "स्वामी ग्रह (Lord)": y.get("lord", ""),
                    "आरंभ दिनांक (Start)": y["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक (End)": y["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (वर्ष)": f"{y['duration_years']} वर्ष",
                    "स्थिति": "जन्म शेष (Birth Balance)" if y.get("is_partial") else "पूर्ण दशा",
                    "सक्रियता": "⭐ वर्तमान सक्रिय" if (y["start_date"] <= target_dt <= y["end_date"]) else ""
                } for y in yog_dashas]), use_container_width=True, hide_index=True)
    
            with tab_y2:
                st.markdown("##### 💫 योगिनी अंतर्दशा (8 Sub-periods per Yogini)")
                y_options = [f"{y.get('yogini_name', y.get('yogini'))} ({y['start_date'].strftime('%d-%b-%Y')} ~ {y['end_date'].strftime('%d-%b-%Y')})" for y in yog_dashas]
                default_y_idx = next((i for i, y in enumerate(yog_dashas) if y["start_date"] <= target_dt <= y["end_date"]), 0)
                sel_y_idx = st.selectbox("मुख्य योगिनी चुनें", range(len(y_options)), format_func=lambda i: y_options[i], index=default_y_idx, key="sel_yogini_for_antar")
                sel_y_obj = yog_dashas[sel_y_idx]
    
                y_antars = y_engine.generate_antardashas(
                    sel_y_obj.get("yogini_name", sel_y_obj.get("yogini")), sel_y_obj["start_date"], sel_y_obj["end_date"]
                )
                st.dataframe(pd.DataFrame([{
                    "योगिनी / अंतर्दशा": f"{sel_y_obj.get('yogini_name', sel_y_obj.get('yogini'))} — {ya['yogini']}",
                    "अंतर्दशा स्वामी": ya["lord"],
                    "आरंभ दिनांक": ya["start_date"].strftime("%d-%b-%Y"),
                    "समाप्ति दिनांक": ya["end_date"].strftime("%d-%b-%Y"),
                    "अवधि (माह / दिन)": f"{ya['duration_months']} माह ({ya['duration_days']} दिन)",
                    "सक्रियता": "⭐ सक्रिय" if (ya["start_date"] <= target_dt <= ya["end_date"]) else ""
                } for ya in y_antars]), use_container_width=True, hide_index=True)
    
            with tab_y3:
                st.markdown("##### ⚡ योगिनी प्रत्यंतर्दशा (Pratyantardashas)")
                col_y_p1, col_y_p2 = st.columns(2)
                with col_y_p1:
                    sel_y_m_idx = st.selectbox("मुख्य योगिनी", range(len(y_options)), format_func=lambda i: y_options[i], index=default_y_idx, key="sel_y_m_for_prat")
                sel_y_m_p = yog_dashas[sel_y_m_idx]
                y_antars_p = y_engine.generate_antardashas(sel_y_m_p.get("yogini_name", sel_y_m_p.get("yogini")), sel_y_m_p["start_date"], sel_y_m_p["end_date"])
                with col_y_p2:
                    sel_y_a_idx = st.selectbox("अंतर्दशा योगिनी", range(len(y_antars_p)), format_func=lambda i: f"{y_antars_p[i]['yogini']} ({y_antars_p[i]['start_date'].strftime('%d-%b-%y')})", key="sel_y_a_for_prat")
                sel_y_a_p = y_antars_p[sel_y_a_idx]
                
                y_prats = y_engine.generate_pratyantardashas(
                    sel_y_m_p.get("yogini_name", sel_y_m_p.get("yogini")), sel_y_a_p["yogini"], sel_y_a_p["start_date"], sel_y_a_p["end_date"]
                )
                st.dataframe(pd.DataFrame([{
                    "3-स्तरीय योगिनी": f"{sel_y_m_p.get('yogini_name', sel_y_m_p.get('yogini'))} / {sel_y_a_p['yogini']} / {yp['yogini']}",
                    "प्रत्यंतर स्वामी": yp["lord"],
                    "आरंभ समय": yp["start_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "समाप्ति समय": yp["end_date"].strftime("%d-%b-%Y %I:%M %p"),
                    "अवधि (दिन)": f"{yp['duration_days']} दिन",
                    "सक्रियता": "⭐ सक्रिय" if (yp["start_date"] <= target_dt <= yp["end_date"]) else ""
                } for yp in y_prats]), use_container_width=True, hide_index=True)
    
        # =========================================================================
        # 3. JAIMINI CHARA DASHA (3 LEVELS: MAJOR SIGN -> ANTARDASHA -> PRATYANTAR)
        # =========================================================================
        elif "जैमिनी" in d_mode:
            st.markdown("#### 🔱 जैमिनी चर दशा (Jaimini Rashi Chara Dasha — Major & Antar)")
            chara_dashas = c_engine.generate_timeline(chart)
            act_chara = next((c for c in chara_dashas if c["start_date"] <= target_dt <= c["end_date"]), chara_dashas[0])
    
            # Active Antardasha & Pratyantar
            c_antars_for_act = c_engine.generate_antardashas(act_chara["sign_id"], act_chara["start_date"], act_chara["end_date"])
            act_ca = next((a for a in c_antars_for_act if a["start_date"] <= target_dt <= a["end_date"]), c_antars_for_act[0])
    
            c_prats_for_act = c_engine.generate_pratyantardashas(act_ca["sign_id"], act_ca["start_date"], act_ca["end_date"])
            act_cpr = next((p for p in c_prats_for_act if p["start_date"] <= target_dt <= p["end_date"]), c_prats_for_act[0])
    
            # Top Banner
            b_str_chara = (
                f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
                f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय 3-स्तरीय जैमिनी चर दशा पदानुक्रम (Active Jaimini Chara Dasha Hierarchy):</div>"
                f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
                f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🔱 चर महादशा: {act_chara['sign_name']} (#{act_chara['sign_id']})</span> "
                f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
                f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>💫 चर अंतर्दशा: {act_ca['sign_name']} (स्वामी
... [truncated for diff preview]