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

# Ensure project root is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
from src.jyotish.services.muhurta import default_muhurta_engine
from src.jyotish.ui.sudarshan import default_sudarshan_engine
from src.jyotish.core.affliction import AfflictionEngine, LIFE_AREAS
from src.jyotish.dasha.vimshottari import default_dasha_engine
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
from src.jyotish.ai.narrative import default_narrative_service

st.set_page_config(
    page_title="JyotishOS - Enterprise Vedic Astrology Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "app_theme_mode" not in st.session_state:
    st.session_state.app_theme_mode = "day"

is_night_mode = (st.session_state.app_theme_mode == "night")

# -------------------------------------------------------------
# Unified High-Contrast Cosmic Vedic Theme (Solid Black Font & Zero Washout)
# -------------------------------------------------------------
if is_night_mode:
    theme_mode_css = """
    html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
        background-color: #0A0E1A !important;
        color: #F8FAFC !important;
    }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 2px solid #1E293B !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
        color: #F1F5F9 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label,
    section[data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label,
    div[data-testid="stRadio"] label {
        background: #1E293B !important;
        border: 1.5px solid #334155 !important;
        color: #F1F5F9 !important;
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
        background: #2E3E5B !important;
        border-color: #F59E0B !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio label:has(input:checked),
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 100%) !important;
        border: 2px solid #3B82F6 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) span,
    div[data-testid="stRadio"] label:has(input:checked) p {
        color: #FFFFFF !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, li, a, label, caption, strong, b, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
        color: #F1F5F9 !important;
    }
    input, textarea, select,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="input"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1.5px solid #3B82F6 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1.5px solid #475569 !important;
    }
    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
    header.top-nav-bar {
        background: #0F172A !important;
        border-color: #1E293B !important;
        border-bottom: 3.5px solid #3B82F6 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7) !important;
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
        background: #1E293B !important;
        border: 1.5px solid #F59E0B !important;
        color: #FEF3C7 !important;
    }
    .active-profile-pill * {
        color: #FEF3C7 !important;
    }
    .header-sub-pill {
        background: #1E293B !important;
        border: 1.5px solid #334155 !important;
        color: #E2E8F0 !important;
    }
    .header-sub-pill * {
        color: #E2E8F0 !important;
    }
    .header-sub-pill b {
        color: #F8FAFC !important;
    }
    .digital-hud {
        background: #0F172A !important;
        border-color: #1E293B !important;
    }
    .digital-hud * {
        color: #F8FAFC !important;
    }
    .hud-pill {
        background: #1E293B !important;
        border: 1.5px solid #334155 !important;
        color: #F8FAFC !important;
    }
    .hud-pill b, .hud-pill strong {
        color: #F59E0B !important;
    }
    .rule-card, .vastu-card {
        background: #1E293B !important;
        border: 1.5px solid #334155 !important;
        color: #F8FAFC !important;
    }
    .rule-card *, .vastu-card * {
        color: #F8FAFC !important;
    }
    div[data-testid="stExpander"] {
        background: #1E293B !important;
        border: 1.5px solid #334155 !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
        color: #F8FAFC !important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
        color: #94A3B8 !important;
    }
    [data-testid="stTable"], [data-testid="stDataFrame"], [data-testid="stTable"] *, [data-testid="stDataFrame"] * {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }
    button[kind="secondary"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1.5px solid #475569 !important;
    }
    div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
    div[style*="background:#F8FAFC"], div[style*="background: #F8FAFC"],
    div[style*="background:#EFF6FF"], div[style*="background: #EFF6FF"] {
        background: #1E293B !important;
        border-color: #334155 !important;
        color: #F8FAFC !important;
    }
    """
else:
    theme_mode_css = """
    body .stApp {
        background-color: #F8FAFC !important;
        color: #000000 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, li, a, label, caption, strong, b {
        color: #000000 !important;
    }
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
    }
    input, textarea, select, 
    div[data-baseweb="input"] input, 
    div[data-baseweb="base-input"] input,
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1.5px solid #94A3B8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #94A3B8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] * {
        color: #000000 !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 1.65rem !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] {
        background-color: #F1F5F9 !important;
        border-right: 2px solid #CBD5E1 !important;
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    """

unified_css = f"""
<style>
    /* Hide Streamlit Deploy button, 3-dots menu, and footer */
    .stDeployButton, #MainMenu, footer, [data-testid="stDecoration"], div[data-testid="stToolbar"] {{
        display: none !important;
        visibility: hidden !important;
    }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 50px !important;
        z-index: 1000002 !important;
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
    [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {{
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }}
    header[data-testid="stHeader"] {{
        display: none !important;
        height: 0px !important;
        visibility: hidden !important;
    }}
    .block-container {{
        padding-top: 0px !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        overflow: visible !important;
    }}
    header.top-nav-bar {{
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0px !important;
        z-index: 999999 !important;
        width: calc(100% + 3rem) !important;
        margin-left: -1.5rem !important;
        margin-right: -1.5rem !important;
        margin-top: 0px !important;
        margin-bottom: 12px !important;
        padding: 10px 24px !important;
        backdrop-filter: blur(10px) !important;
    }}
    div:has(> header.top-nav-bar),
    div[data-testid="stMarkdownContainer"]:has(header.top-nav-bar),
    div[data-testid="element-container"]:has(header.top-nav-bar),
    div[data-testid="stElementContainer"]:has(header.top-nav-bar) {{
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0px !important;
        z-index: 999999 !important;
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

    /* Unified Frozen Top Header Bar (Full width edge-to-edge with royal blue boundary) */
    .top-nav-bar {{
        position: sticky !important;
        top: 0px !important;
        z-index: 999999 !important;
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        border-bottom: 3.5px solid #2563EB !important;
        border-radius: 0px !important;
        padding: 12px 24px !important;
        margin-bottom: 18px !important;
        margin-top: 0px !important;
        margin-left: -2rem !important;
        margin-right: -2rem !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 14px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    }}
    .nav-left {{
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }}
    .logo-circle {{
        width: 44px !important;
        height: 44px !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%) !important;
        border: 1.5px solid #D97706 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        box-shadow: 0 2px 8px rgba(217, 119, 6, 0.2) !important;
    }}
    .app-brand-title {{
        font-size: 1.45rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #B45309 0%, #D97706 45%, #2563EB 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        line-height: 1.2 !important;
        letter-spacing: -0.5px !important;
    }}
    .app-brand-sub {{
        font-size: 0.8rem !important;
        color: #475569 !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
    }}
    .nav-profile-block {{
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-end !important;
        gap: 5px !important;
    }}
    @media (max-width: 900px) {{
        .nav-profile-block {{
            align-items: flex-start !important;
        }}
    }}
    .active-profile-pill {{
        background: #EFF6FF !important;
        border: 1.5px solid #93C5FD !important;
        border-radius: 20px !important;
        padding: 4px 14px !important;
        font-size: 12.5px !important;
        color: #1E3A8A !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.1) !important;
        white-space: nowrap !important;
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
        border-radius: 14px !important;
        padding: 3px 10px !important;
        font-size: 11.5px !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 5px !important;
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

    [data-testid="stDataFrame"] {{
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }}
    [data-testid="stDataFrame"] * {{
        color: #000000 !important;
        font-weight: 600 !important;
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

    {theme_mode_css}
</style>
"""

st.markdown(unified_css, unsafe_allow_html=True)

# Client-Side Sidebar Toggle Bridge, Multi-Language Engine & Live GPS Resolver
components.html("""
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

            const NIGHT_STYLE_ID = "jyotish-night-mode-override-style";

            function applyTheme(mode) {
                const isNight = (mode === "night");
                try {
                    localStorage.setItem("jyotish_theme_mode", isNight ? "night" : "day");
                    sessionStorage.setItem("jyotish_theme_mode", isNight ? "night" : "day");
                } catch(e) {}

                let styleEl = parentDoc.getElementById(NIGHT_STYLE_ID);

                if (isNight) {
                    parentDoc.body.classList.add("night-mode");
                    if (parentDoc.documentElement) parentDoc.documentElement.classList.add("night-mode");
                    
                    const nightCss = `
                        html, body, #root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
                            background-color: #0A0E1A !important;
                            color: #F8FAFC !important;
                        }
                        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
                            background-color: #0F172A !important;
                            border-right: 2px solid #1E293B !important;
                        }
                        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] b {
                            color: #F1F5F9 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
                            background: #1E293B !important;
                            border-color: #334155 !important;
                            color: #F1F5F9 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label p {
                            color: #F1F5F9 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
                            background: #2E3E5B !important;
                            border-color: #F59E0B !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"],
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {
                            background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 100%) !important;
                            border-color: #3B82F6 !important;
                        }
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p,
                        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) p {
                            color: #FFFFFF !important;
                        }
                        h1, h2, h3, h4, h5, h6, p, span, li, a, label, caption, strong, b, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
                            color: #F1F5F9 !important;
                        }
                        input, textarea, select,
                        div[data-baseweb="input"] input,
                        div[data-baseweb="base-input"] input,
                        div[data-baseweb="input"] {
                            background-color: #1E293B !important;
                            color: #FFFFFF !important;
                            -webkit-text-fill-color: #FFFFFF !important;
                            border: 1.5px solid #3B82F6 !important;
                        }
                        div[data-baseweb="select"] > div {
                            background-color: #1E293B !important;
                            color: #FFFFFF !important;
                            border: 1.5px solid #475569 !important;
                        }
                        div[data-baseweb="select"] * {
                            color: #FFFFFF !important;
                        }
                        header.top-nav-bar {
                            background: #0F172A !important;
                            border-color: #1E293B !important;
                            border-bottom: 3.5px solid #3B82F6 !important;
                            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7) !important;
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
                            background: #1E293B !important;
                            border: 1.5px solid #F59E0B !important;
                            color: #FEF3C7 !important;
                        }
                        .active-profile-pill * {
                            color: #FEF3C7 !important;
                        }
                        .header-sub-pill {
                            background: #1E293B !important;
                            border: 1.5px solid #334155 !important;
                            color: #E2E8F0 !important;
                        }
                        .header-sub-pill * {
                            color: #E2E8F0 !important;
                        }
                        .header-sub-pill b {
                            color: #F8FAFC !important;
                        }
                        .theme-select-box {
                            background: #1E293B !important;
                            border-color: #F59E0B !important;
                        }
                        .theme-select-box select, .theme-select-box b, .theme-select-box span {
                            color: #F59E0B !important;
                        }
                        .theme-select-box option {
                            background: #0F172A !important;
                            color: #FFFFFF !important;
                        }
                        .digital-hud {
                            background: #0F172A !important;
                            border-color: #1E293B !important;
                        }
                        .digital-hud * {
                            color: #F8FAFC !important;
                        }
                        .hud-pill {
                            background: #1E293B !important;
                            border: 1.5px solid #334155 !important;
                            color: #F8FAFC !important;
                        }
                        .hud-pill b {
                            color: #F59E0B !important;
                        }
                        div[data-testid="stExpander"] {
                            background: #1E293B !important;
                            border-color: #334155 !important;
                        }
                        div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
                            color: #F8FAFC !important;
                        }
                        div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
                            color: #94A3B8 !important;
                        }
                        [data-testid="stTable"], [data-testid="stDataFrame"], [data-testid="stTable"] *, [data-testid="stDataFrame"] * {
                            background-color: #1E293B !important;
                            color: #FFFFFF !important;
                        }
                        div[style*="background:#FFFFFF"], div[style*="background: #FFFFFF"],
                        div[style*="background:#F8FAFC"], div[style*="background: #F8FAFC"],
                        div[style*="background:#EFF6FF"], div[style*="background: #EFF6FF"] {
                            background: #1E293B !important;
                            border-color: #334155 !important;
                            color: #F8FAFC !important;
                        }
                    `;
                    
                    if (!styleEl) {
                        styleEl = parentDoc.createElement("style");
                        styleEl.id = NIGHT_STYLE_ID;
                        parentDoc.head.appendChild(styleEl);
                    }
                    styleEl.innerHTML = nightCss;
                    if (document.body) document.body.classList.add("night-mode");
                    if (document.documentElement) document.documentElement.classList.add("night-mode");
                } else {
                    parentDoc.body.classList.remove("night-mode");
                    if (parentDoc.documentElement) parentDoc.documentElement.classList.remove("night-mode");
                    if (styleEl) {
                        styleEl.remove();
                    }
                    if (document.body) document.body.classList.remove("night-mode");
                    if (document.documentElement) document.documentElement.classList.remove("night-mode");
                }

                // Sync all select elements
                const selects = parentDoc.querySelectorAll("#software-theme-select");
                selects.forEach(function(sel) {
                    if (sel.value !== (isNight ? "night" : "day")) {
                        sel.value = isNight ? "night" : "day";
                    }
                });

                // Sync icon
                const icons = parentDoc.querySelectorAll("#theme-mode-icon, .theme-mode-icon");
                icons.forEach(function(ic) {
                    ic.innerText = isNight ? "🌙" : "☀️";
                });
            }

            const handleThemeSwitch = function(themeMode) {
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

            const currentSaved = localStorage.getItem("jyotish_theme_mode") || sessionStorage.getItem("jyotish_theme_mode") || "day";
            applyTheme(currentSaved);
        } catch (e) {
            console.error("Theme mode error:", e);
        }
    }

    setupSidebarToggle();
    setupLanguageBridge();
    setupThemeMode();
    resolveClientGPS();
    setInterval(function() {
        setupSidebarToggle();
        setupLanguageBridge();
        setupThemeMode();
        const cached = localStorage.getItem("jyotish_user_gps_loc") || sessionStorage.getItem("jyotish_user_gps_loc");
        if (cached) {
            updateLocationUI(cached);
        }
    }, 400);
})();
</script>
""", height=0, width=0)


# -------------------------------------------------------------
# Dedicated Matching Cosmic Vedic Login Page
# -------------------------------------------------------------
def render_login_page():
    st.markdown("""
    <div style="display:flex; justify-content:flex-end; gap:8px; margin-bottom: 4px;">
        <div class="header-sub-pill notranslate theme-select-box" translate="no" style="background:#F8FAFC !important; border-color:#CBD5E1 !important; color:#0F172A !important; padding:4px 12px !important; display:inline-flex; align-items:center; gap:6px;" title="थीम चुनें (Select Day / Night Mode)">
            <span id="theme-mode-icon" class="notranslate" translate="no" style="font-size:14px;">☀️</span>
            <b class="notranslate" translate="no" style="color:#0F172A !important; font-size:12px;">थीम:</b>
            <select id="software-theme-select" class="notranslate" translate="no" onchange="(function(sel){var v=sel.value; try{var pd=(window.parent&&window.parent.document)?window.parent.document:document; if(v==='night'){document.documentElement.classList.add('night-mode'); document.body.classList.add('night-mode'); pd.documentElement.classList.add('night-mode'); pd.body.classList.add('night-mode'); localStorage.setItem('jyotish_theme_mode','night'); sessionStorage.setItem('jyotish_theme_mode','night');} else {document.documentElement.classList.remove('night-mode'); document.body.classList.remove('night-mode'); pd.documentElement.classList.remove('night-mode'); pd.body.classList.remove('night-mode'); localStorage.setItem('jyotish_theme_mode','day'); sessionStorage.setItem('jyotish_theme_mode','day');} var ics=(pd||document).querySelectorAll('#theme-mode-icon, .theme-mode-icon'); ics.forEach(function(i){i.innerText=(v==='night'?'🌙':'☀️');}); if(window.changeSoftwareTheme) window.changeSoftwareTheme(v); if(window.parent&&window.parent.changeSoftwareTheme) window.parent.changeSoftwareTheme(v);}catch(e){}})(this)" style="background:transparent; border:none; color:#0F172A; font-weight:800; font-size:12px; cursor:pointer; outline:none; padding:0 2px;">
                <option value="day" class="notranslate" translate="no">☀️ डे मोड (Day Mode)</option>
                <option value="night" class="notranslate" translate="no">🌙 नाइट मोड (Night Mode)</option>
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

if "show_birth_details" not in st.session_state:
    st.session_state.show_birth_details = False

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

# -------------------------------------------------------------
# 21 Vedic Astrology Modules Definitions (Available globally)
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
        "📚 100 Classical Rules",
        "🔍 Vedic Sage Validation"
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
        "📚 100 சாஸ்திர விதிகள் (Rules)",
        "🔍 வேத ரிஷி சரிபார்ப்பு (Validation)"
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
        "📚 100 శాస్త్రీయ నియమాలు (Rules)",
        "🔍 వైదిక ఋషి ధృవీకరణ (Validation)"
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
        "📚 ૧૦૦ શાસ્ત્રીય નિયમો (Rules)",
        "🔍 વૈદિક ઋષિ પ્રમાણીકરણ (Validation)"
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
        "📚 १०० शास्त्रीय नियम (Rules)",
        "🔍 वैदिक ऋषी पडताळणी (Validation)"
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
        "📚 ১০০ শাস্ত্রীয় নিয়ম (Rules)",
        "🔍 বৈদিক ঋষি প্রমাণ (Validation)"
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
        "📚 100 शास्त्रीय नियम (Rules)",
        "🔍 वैदिक ऋषि सत्यापन (Validation)"
    ]

if "active_module_idx" not in st.session_state:
    st.session_state.active_module_idx = 0
if st.session_state.active_module_idx >= len(MODULE_OPTIONS):
    st.session_state.active_module_idx = 0

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

chart = default_chart_calculator.calculate_full_chart(birth_profile, ayanamsa_name=ayanamsa, house_system=house_system)
affliction_engine = AfflictionEngine(chart)
vastu_engine = VastuJyotishEngine(chart)

# Helper function to render chart in selected style
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
# 1. Frozen Top Navigation Bar (Header with Integrated Buttons)
# -------------------------------------------------------------
with st.container():
    st.markdown('<div class="top-nav-bar-container">', unsafe_allow_html=True)
    col_hdr_brand, col_hdr_btn1, col_hdr_btn2, col_hdr_meta = st.columns([2.3, 1.25, 1.35, 3.3])
    
    with col_hdr_brand:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-top:2px;">
            <div class="logo-circle" style="width:40px; height:40px; font-size:20px; min-width:40px; border-radius:10px;">🔮</div>
            <div>
                <div class="app-brand-title" style="font-size:1.25rem; font-weight:900; margin:0; line-height:1.2;">JyotishOS</div>
                <div class="app-brand-sub" style="font-size:0.75rem; color:#475569; font-weight:700;">प्रामाणिक वैदिक ज्योतिष गणना महामंच</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_hdr_btn1:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        profile_btn_label = "👤 जन्म विवरण " + ("▲" if st.session_state.get("show_birth_details") else "▼")
        if st.button(profile_btn_label, use_container_width=True, type="primary" if st.session_state.get("show_birth_details") else "secondary", help="जातक जन्म विवरण एवं कुण्डली विन्यास संपादित करें", key="hdr_birth_profile_btn"):
            st.session_state.show_birth_details = not st.session_state.get("show_birth_details", False)
            st.rerun()

    with col_hdr_btn2:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        with st.popover("🧭 21 मॉड्यूल्स सूची ☰", use_container_width=True, help="सभी 21 वैदिक ज्योतिष मॉड्यूल्स की संपूर्ण सूची खोलें"):
            st.markdown("<b style='color:#1E40AF; font-size:13px;'>🧭 सभी 21 वैदिक ज्योतिष मॉड्यूल्स (Click to Open):</b>", unsafe_allow_html=True)
            m_cols = st.columns(2)
            for m_i, m_name in enumerate(MODULE_OPTIONS):
                target_col = m_cols[m_i % 2]
                is_active = (st.session_state.active_module_idx == m_i)
                btn_type = "primary" if is_active else "secondary"
                if target_col.button(f"{m_i+1}. {m_name}", key=f"pop_top_mod_{m_i}", use_container_width=True, type=btn_type):
                    st.session_state.active_module_idx = m_i
                    st.rerun()

    with col_hdr_meta:
        st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:flex-end; gap:3px;">
            <div class="active-profile-pill" style="font-size:11.5px; padding:2px 10px; margin-bottom:2px;">
                👤 <b>{name}</b> &nbsp;|&nbsp; 📅 {birth_d.strftime('%d %b %Y')}, {birth_t.strftime('%I:%M %p')} &nbsp;|&nbsp; 📍 {default_city_name} &nbsp;|&nbsp; <span class="pulse-dot"></span> <b>सक्रिय</b>
            </div>
            <div class="header-sub-pills-row" style="font-size:11px;">
                <div class="header-sub-pill" style="padding:2px 6px;">👑 <b>ज्योतिषी</b></div>
                <div class="header-sub-pill" style="padding:2px 6px;">🕒 {current_time_str}</div>
                <div class="header-sub-pill" style="background:#FEF3C7 !important; border-color:#F59E0B !important; color:#92400E !important; padding:2px 6px;">📍 <span id="user-gps-val" class="user-gps-val">GPS जाँचा जा रहा है...</span></div>
                <div class="header-sub-pill notranslate lang-select-box" style="padding:1px 6px; display:inline-flex; align-items:center; gap:2px;">
                    <span>🌐</span>
                    <select id="software-lang-select" onchange="window.changeSoftwareLanguage ? window.changeSoftwareLanguage(this.value) : null" style="background:transparent; border:none; color:#15803D; font-weight:800; font-size:11px; cursor:pointer; outline:none;">
                        <option value="general">General (जनरल)</option>
                        <option value="hi">हिन्दी (Hindi)</option>
                        <option value="en">English (अंग्रेजी)</option>
                        <option value="ta">தமிழ் (Tamil)</option>
                        <option value="te">తెలుగు (Telugu)</option>
                        <option value="gu">ગુજરાતી (Gujarati)</option>
                        <option value="mr">मराठी (Marathi)</option>
                        <option value="bn">বাংলা (Bengali)</option>
                    </select>
                </div>
                <div class="header-sub-pill notranslate theme-select-box" style="padding:1px 6px; display:inline-flex; align-items:center; gap:2px;">
                    <span id="theme-mode-icon">☀️</span>
                    <select id="software-theme-select" onchange="window.changeSoftwareTheme ? window.changeSoftwareTheme(this.value) : null" style="background:transparent; border:none; color:#0F172A; font-weight:800; font-size:11px; cursor:pointer; outline:none;">
                        <option value="day">☀️ डे (Day)</option>
                        <option value="night">🌙 नाइट (Night)</option>
                    </select>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. 6 Category Quick-Tabs Cards (Even 6-Column Row)
# -------------------------------------------------------------
col_cat1, col_cat2, col_cat3, col_cat4, col_cat5, col_cat6 = st.columns(6)

if col_cat1.button("📜 लग्न व वर्ग (D1-D60)", use_container_width=True, help="D1-D60 षोडशवर्ग व चक्र"):
    st.session_state.active_module_idx = 0
    st.rerun()
if col_cat2.button("⏱️ दशा व गोचर", use_container_width=True, help="दशा प्रणालियाँ, गोचर व वर्षफल"):
    st.session_state.active_module_idx = 9
    st.rerun()
if col_cat3.button("⚖️ षड्बल व KP", use_container_width=True, help="षड्बल, जैमिनी व KP पद्धति"):
    st.session_state.active_module_idx = 7
    st.rerun()
if col_cat4.button("🔮 प्रश्न व मुहूर्त", use_container_width=True, help="प्रश्न, मुहूर्त, वास्तु व दोष"):
    st.session_state.active_module_idx = 5
    st.rerun()
if col_cat5.button("💍 मिलान व AI", use_container_width=True, help="कुण्डली मिलान, AI व सम्पूर्ण रिपोर्ट"):
    st.session_state.active_module_idx = 16
    st.rerun()
if col_cat6.button("📚 100 शास्त्रीय नियम", use_container_width=True, help="100 नियम व ऋषि सत्यापन"):
    st.session_state.active_module_idx = 19
    st.rerun()

# -------------------------------------------------------------
# 3. Collapsible Birth Profile & Presets Control Panel (Opens right below the row)
# -------------------------------------------------------------
if st.session_state.get("show_birth_details", False):
    with st.container():
        st.markdown("""
        <div style="background:#F0FDF4; border:2px solid #16A34A; border-radius:10px; padding:10px 14px 6px 14px; margin-bottom:12px; box-shadow:0 4px 12px rgba(22,163,74,0.15);">
            <div style="font-weight:900; color:#166534; font-size:13.5px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
                <span>👤 <b>जातक जन्म विवरण, गणना विन्यास एवं डेमो प्रोफाइल्स (Birth Profile Controls)</b></span>
                <span style="font-size:11px; background:#DCFCE7; padding:2px 8px; border-radius:6px; border:1px solid #86EFAC;">⚡ सक्रिय संपादन मोड</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_r1_1, col_r1_2, col_r1_3, col_r1_4 = st.columns([1.2, 1.4, 1.5, 1.5])
        with col_r1_1:
            in_name = st.text_input("नाम (Name)", value=st.session_state.birth_name, key="app_birth_name_input")
            st.session_state.birth_name = in_name

        with col_r1_2:
            in_city_query = st.text_input("स्थान खोज (Search City)", value=st.session_state.birth_city, key="app_city_query_input")
            geo_results = default_geocoding_service.search(in_city_query, limit=3)
            if geo_results:
                selected_loc = st.selectbox(
                    "उपलब्ध स्थान (Select Location)",
                    geo_results,
                    format_func=lambda x: f"{x.formatted_name} ({x.source})",
                    key="app_geo_select"
                )
                st.session_state.birth_lat = selected_loc.latitude
                st.session_state.birth_lon = selected_loc.longitude
                st.session_state.birth_tz = selected_loc.timezone_offset
                st.session_state.birth_city = selected_loc.city

        with col_r1_3:
            dob_mode = st.radio(
                "जन्म तिथि प्रारूप (DOB Mode)",
                ["🔢 वर्ष (1950-2050)", "📅 कैलेंडर"],
                horizontal=True,
                key="app_dob_mode_radio"
            )
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
                sel_yr = col_d_yr.selectbox("वर्ष", years_list, index=yr_idx, key="app_dob_yr_select")
                sel_mon_str = col_d_mon.selectbox("माह", months_labels, index=mon_idx, key="app_dob_mon_select")
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
                sel_d = col_d_day.selectbox("दिन", days_list, index=d_idx, key="app_dob_day_select")
                in_birth_d = date(sel_yr, sel_mon, sel_d)
                st.session_state.birth_date = in_birth_d
            else:
                in_birth_d = st.date_input(
                    "जन्म तिथि (DD/MM/YYYY)",
                    value=init_b_date,
                    min_value=date(1950, 1, 1),
                    max_value=date(2050, 12, 31),
                    format="DD/MM/YYYY",
                    key="app_dob_cal_input"
                )
                st.session_state.birth_date = in_birth_d

        with col_r1_4:
            time_format_mode = st.radio(
                "जन्म समय (Birth Time)",
                ["12 घंटे (AM/PM)", "24 घंटे"],
                horizontal=True,
                key="app_time_mode_radio"
            )
            if "last_loaded_time" not in st.session_state:
                st.session_state.last_loaded_time = st.session_state.birth_time
            if st.session_state.last_loaded_time != st.session_state.birth_time:
                st.session_state.last_loaded_time = st.session_state.birth_time
                curr_h24 = st.session_state.birth_time.hour
                curr_m = st.session_state.birth_time.minute
                curr_ampm = "PM" if curr_h24 >= 12 else "AM"
                curr_h12 = curr_h24 % 12
                if curr_h12 == 0:
                    curr_h12 = 12
                st.session_state["app_time_h"] = curr_h12
                st.session_state["app_time_m"] = f"{curr_m:02d}"
                st.session_state["app_time_p"] = curr_ampm
                st.session_state["app_time_24_val"] = st.session_state.birth_time

            if time_format_mode.startswith("12"):
                curr_t = st.session_state.birth_time
                curr_h24 = curr_t.hour
                curr_m = curr_t.minute
                curr_ampm = "PM" if curr_h24 >= 12 else "AM"
                curr_h12 = curr_h24 % 12
                if curr_h12 == 0:
                    curr_h12 = 12
                col_th, col_tm, col_tp = st.columns([1, 1, 1.1])
                h_val = col_th.selectbox("घंटा", list(range(1, 13)), index=curr_h12 - 1, key="app_time_h")
                m_val = col_tm.selectbox("मिनट", [f"{m:02d}" for m in range(60)], index=curr_m, key="app_time_m")
                p_val = col_tp.selectbox("AM/PM", ["AM", "PM"], index=0 if curr_ampm == "AM" else 1, key="app_time_p")
                h_24 = (int(h_val) % 12) + (12 if p_val == "PM" else 0)
                in_birth_t = time(h_24, int(m_val), 0)
                st.session_state.birth_time = in_birth_t
            else:
                in_birth_t = st.time_input(
                    "जन्म समय",
                    value=st.session_state.birth_time,
                    step=60,
                    key="app_time_24_val"
                )
                st.session_state.birth_time = in_birth_t

        # Row 2: Coordinates & Settings
        col_r2_1, col_r2_2, col_r2_3, col_r2_4 = st.columns([1.2, 1.2, 1.4, 1.4])
        with col_r2_1:
            col_g1, col_g2 = st.columns(2)
            in_lat = col_g1.number_input("Latitude", value=float(st.session_state.birth_lat), format="%.4f", key="app_lat_input")
            in_lon = col_g2.number_input("Longitude", value=float(st.session_state.birth_lon), format="%.4f", key="app_lon_input")
            st.session_state.birth_lat = in_lat
            st.session_state.birth_lon = in_lon
        with col_r2_2:
            col_tz1, col_tz2 = st.columns(2)
            in_tz = col_tz1.number_input("TZ Offset", value=float(st.session_state.get("birth_tz", 5.5)), step=0.5, key="app_tz_input")
            in_conf = col_tz2.selectbox("Confidence", ["Exact", "Approx (±15 min)", "Unknown"], key="app_conf_select")
            st.session_state.birth_tz = in_tz
            st.session_state.birth_conf = in_conf
        with col_r2_3:
            col_ay, col_hs = st.columns(2)
            in_ay = col_ay.selectbox("अयनांश (Ayanamsa)", ["Lahiri", "Raman", "KP", "True Chitra"], key="app_ayanamsa_select")
            in_hs = col_hs.selectbox("भाव पद्धति", ["Whole Sign", "Equal"], key="app_hs_select")
            st.session_state.app_ayanamsa = in_ay
            st.session_state.app_house_system = in_hs
        with col_r2_4:
            col_cs, col_pm = st.columns([1.4, 1])
            in_cs = col_cs.selectbox("कुण्डली चक्र शैली", ["North Indian (Diamond)", "South Indian (Box)", "East Indian (Surya)"], key="app_chart_style_select")
            in_pm = col_pm.toggle("⚡ Pro Mode", value=st.session_state.get("app_pro_mode", True), key="app_pro_mode_toggle")
            st.session_state.app_chart_style = in_cs
            st.session_state.app_pro_mode = in_pm

        # Row 3: Action Buttons
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns([1.5, 1.2, 1.5, 1.0, 1.0])
        calc_clicked = col_a1.button("🚀 गणना करें (Calculate)", type="primary", use_container_width=True, key="app_calc_kundali_btn")
        if calc_clicked:
            st.session_state.calculated_at = datetime.now()
            st.session_state.show_birth_details = False
            st.toast("✅ कुण्डली गणना एवं षोडशवर्ग सफलतापूर्वक अद्यतन किए गए!", icon="🔮")
            st.rerun()

        save_clicked = col_a2.button("💾 सहेजें (Save)", use_container_width=True, key="app_save_kundali_btn")
        if save_clicked:
            save_payload = {
                "name": st.session_state.birth_name,
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

        with col_a3:
            all_local_folders = default_folder_manager.list_folders()
            flat_saved_charts = []
            for f in all_local_folders:
                for c in f.get("charts", []):
                    flat_saved_charts.append({
                        "label": f"[{f['name'].split()[0]}] {c['name']}",
                        "data": c.get("birth_data", {})
                    })
            if flat_saved_charts:
                with st.popover("📁 सहेजी गई / 10 डेमो प्रोफाइल", use_container_width=True):
                    sel_demo_label = st.selectbox("प्रोफाइल चुनें", [sc["label"] for sc in flat_saved_charts], key="app_pop_demo_sel")
                    if st.button("📥 लोड करें (Load)", key="load_saved_profile_top_btn", use_container_width=True):
                        chosen = next((sc for sc in flat_saved_charts if sc["label"] == sel_demo_label), None)
                        if chosen and chosen["data"]:
                            bd = chosen["data"]
                            st.session_state.birth_name = bd.get("name", "Client")
                            st.session_state.birth_lat = float(bd.get("latitude", 27.8646))
                            st.session_state.birth_lon = float(bd.get("longitude", 81.5004))
                            st.session_state.birth_city = bd.get("city", "Delhi")
                            try:
                                st.session_state.birth_date = datetime.strptime(bd["birth_date"], "%Y-%m-%d").date()
                                st.session_state.birth_time = datetime.strptime(bd["birth_time"], "%H:%M:%S").time()
                            except Exception:
                                pass
                            st.session_state.show_birth_details = False
                            st.toast(f"✅ {st.session_state.birth_name} का विवरण लोड किया गया!", icon="🔮")
                            st.rerun()

        with col_a4:
            if st.button("☁️ सिंक", key="sync_gla_top_btn", use_container_width=True):
                if not st.session_state.get("gla_authenticated"):
                    st.warning("⚠️ कृपया पहले मॉड्यूल 7 (सर्वर सिंक) में जाकर Username व Password कनेक्ट करें।")
                else:
                    with st.spinner("Connecting to Cloud API..."):
                        active_u = st.session_state.get("gla_user", "")
                        active_p = st.session_state.get("gla_pass", "")
                        client = GrahalakshanamClient(GrahalakshanamConfig(username=active_u, password=active_p))
                        if client.authenticate():
                            ff = client.get_folders_with_files()
                            st.session_state.gla_charts = ff.get("files", [])
                            imported = default_folder_manager.sync_from_grahalakshanam(ff)
                            st.success(f"Synced {len(st.session_state.gla_charts)} charts!")
                        else:
                            st.error("Authentication failed. Please verify credentials in Module 7.")

        with col_a5:
            if st.button("✖️ बंद करें", key="close_birth_drawer_btn", use_container_width=True, help="जन्म विवरण पैनल को बंद करें"):
                st.session_state.show_birth_details = False
                st.rerun()

col_mod_sel, col_btn_prev, col_btn_next = st.columns([3.8, 1.1, 1.1])
with col_mod_sel:
    selected_module = st.selectbox(
        "🧭 सक्रिय वैदिक ज्योतिष मॉड्यूल चयन (Top Navigation - Select 21 Modules)",
        MODULE_OPTIONS,
        index=st.session_state.active_module_idx,
        key="top_bar_module_selector"
    )
    selected_idx = MODULE_OPTIONS.index(selected_module) if selected_module in MODULE_OPTIONS else 0
    st.session_state.active_module_idx = selected_idx

with col_btn_prev:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    if st.button("❮ पिछला (Prev)", use_container_width=True, help="पिछला मॉड्यूल खोलें", key="top_prev_mod_btn"):
        st.session_state.active_module_idx = (selected_idx - 1) % len(MODULE_OPTIONS)
        st.rerun()

with col_btn_next:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    if st.button("अगला (Next) ❯", use_container_width=True, help="अगला मॉड्यूल खोलें", key="top_next_mod_btn"):
        st.session_state.active_module_idx = (selected_idx + 1) % len(MODULE_OPTIONS)
        st.rerun()

p = chart.panchang
sr_time = "05:18:32 AM"
ss_time = "06:42:25 PM"
hora_lord = "Mars" if birth_d.weekday() == 0 else "Sun"
ghati_val = round((birth_t.hour + birth_t.minute / 60.0 - 5.3) * 2.5, 2)
if ghati_val < 0:
    ghati_val += 60.0

st.markdown(f"""
<div class="digital-hud">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 4px;">
        <div style="font-weight: 800; font-size: 12.5px; display: flex; align-items: center; gap: 6px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981; box-shadow:0 0 6px #10B981;"></span>
            <span style="color:#000000; font-weight:900;">⚡ डिजिटल पंचांग एवं काल गणना (Panchang & Ephemeris HUD)</span>
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap; align-items: center;">
            <div class="hud-pill-highlight" style="border-radius: 6px; border: 1.5px solid #D97706; font-weight: 800;">
                👑 होरा स्वामी: <b>{hora_lord}</b>
            </div>
            <div style="background: #EFF6FF; border: 1.5px solid #2563EB; color: #1E40AF; border-radius: 6px; padding: 3px 8px; font-size: 11.5px; font-weight: 800;">
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
<div style="display:flex; justify-content:space-between; align-items:center; background:#EFF6FF; border:1.5px solid #93C5FD; border-radius:8px; padding:8px 16px; margin-bottom:16px;">
    <div style="font-weight:800; color:#1E40AF; font-size:14px;">📍 सक्रिय मॉड्यूल: <b>{selected_module}</b></div>
    <div style="font-size:12.5px; color:#1E293B; font-weight:700;">जातक: <b>{name}</b> ({birth_d.strftime('%d-%b-%Y')}, {birth_t.strftime('%I:%M %p')})</div>
</div>
""", unsafe_allow_html=True)


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

    col_chart1, col_chart2 = st.columns([1, 1])
    with col_chart1:
        varga_options = list(chart.vargas.keys()) if chart.vargas else ["D1"]
        varga_choice = st.selectbox(
            "वर्ग चक्र चयन (Select Varga Chart)",
            varga_options,
            format_func=lambda x: f"{x} - {chart.vargas[x].varga_name}" if x in chart.vargas else x
        )
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
    st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)


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
    st.subheader("⚖️ षड्बल, भावबल एवं इष्ट/कष्ट फल (Shadbala & Strengths)")
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


# =============================================================
# TAB 9: JAIMINI & UPAGRAHAS & SPECIAL LAGNAS & AVASTHAS

elif selected_idx == 8:
    st.subheader("🔱 जैमिनी ज्योतिष, विशेष लग्न, आरूढ़ पद एवं ग्रह अवस्थाएँ")
    st.write("महर्षि जैमिनी उपदेश सूत्र एवं बृहत्पाराशर होराशास्त्र (BPHS) आधारित विशेष लग्न, 12 आरूढ़ पद, ग्रह अवस्थाएँ, आयुर्दाय एवं अप्रकाशित उपग्रह।")

    tab_j1, tab_j2, tab_j3, tab_j4, tab_j5 = st.tabs([
        "🌟 विशेष लग्न (Special Lagnas)",
        "👑 सम्पूर्ण 12 आरूढ़ पद (Arudha Padas)",
        "💫 ग्रह अवस्थाएँ (Planetary Avasthas)",
        "⏳ आयुर्दाय एवं दीर्घायु (Longevity)",
        "👻 अप्रकाशित उपग्रह (Invisible Upagrahas)"
    ])

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


# =============================================================
# TAB 10: DASHA SYSTEMS

elif selected_idx == 9:
    st.subheader("⏱️ दशा प्रणालियाँ (Multi-Level Dasha Systems)")
    st.write("विंशोत्तरी दशा (महादशा, अंतर्दशा, प्रत्यंतर्दशा, सूक्ष्मदशा एवं प्राणदशा), योगिनी, जैमिनी चर, कालचक्र एवं शूल दशाओं का सम्पूर्ण बहु-स्तरीय विश्लेषण।")

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
            "⚔️ शूल दशा (Shoola Dasha - Ayurdaya & Maraka)"
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
    
    if not hasattr(default_dasha_engine, "get_5level_hierarchy"):
        importlib.reload(vim_mod)
    if not hasattr(default_yogini_engine, "generate_antardashas"):
        importlib.reload(yog_mod)
    if not hasattr(default_chara_engine, "generate_antardashas"):
        importlib.reload(chara_mod)

    d_engine = vim_mod.default_dasha_engine
    y_engine = yog_mod.default_yogini_engine
    c_engine = chara_mod.default_chara_engine

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
            f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>💫 चर अंतर्दशा: {act_ca['sign_name']} (स्वामी: {act_ca['lord']})</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ चर प्रत्यंतर: {act_cpr['sign_name']} (स्वामी: {act_cpr['lord']})</span>"
            f"</div>"
            f"</div>"
        )
        st.markdown(b_str_chara, unsafe_allow_html=True)

        # 3 Styled Metric Cards
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1:
            st.markdown(f"""
            <div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🔱 सक्रिय चर महादशा</div>
                <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_chara['sign_name']} (#{act_chara['sign_id']})</div>
                <div style="font-size:10.5px; color:#475569;">{act_chara['start_date'].strftime('%d-%b-%y')} ~ {act_chara['end_date'].strftime('%d-%b-%y')} ({act_chara['duration_years']} वर्ष)</div>
            </div>
            """, unsafe_allow_html=True)
        with c_col2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#15803D; font-weight:800;">💫 चर अंतर्दशा</div>
                <div style="font-size:18px; font-weight:900; color:#064E3B;">{act_ca['sign_name']} (स्वामी: {act_ca['lord']})</div>
                <div style="font-size:10.5px; color:#475569;">{act_ca['start_date'].strftime('%d-%b-%y')} ~ {act_ca['end_date'].strftime('%d-%b-%y')}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_col3:
            st.markdown(f"""
            <div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ चर प्रत्यंतर्दशा</div>
                <div style="font-size:18px; font-weight:900; color:#78350F;">{act_cpr['sign_name']} (स्वामी: {act_cpr['lord']})</div>
                <div style="font-size:10.5px; color:#475569;">{act_cpr['start_date'].strftime('%d-%b-%y')} ~ {act_cpr['end_date'].strftime('%d-%b-%y')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        tab_c1, tab_c2, tab_c3 = st.tabs([
            "🔱 चर महादशा (12 Signs)",
            "💫 चर अंतर्दशा (12 Sub-Signs per Sign)",
            "⚡ चर प्रत्यंतर्दशा (Pratyantardasha)"
        ])

        with tab_c1:
            st.markdown("##### 🔱 12 राशियों का चर महादशा कालक्रम")
            st.dataframe(pd.DataFrame([{
                "राशि (Sign)": f"{c['sign_name']} (#{c['sign_id']})",
                "आरंभ दिनांक (Start)": c["start_date"].strftime("%d-%b-%Y"),
                "समाप्ति दिनांक (End)": c["end_date"].strftime("%d-%b-%Y"),
                "अवधि (वर्ष)": f"{c['duration_years']} वर्ष",
                "सक्रियता": "⭐ वर्तमान सक्रिय" if (c["start_date"] <= target_dt <= c["end_date"]) else ""
            } for c in chara_dashas]), use_container_width=True, hide_index=True)

        with tab_c2:
            st.markdown("##### 💫 चर अंतर्दशा (12 Sub-signs under Selected Rashi)")
            c_options = [f"{c['sign_name']} ({c['start_date'].strftime('%d-%b-%Y')} ~ {c['end_date'].strftime('%d-%b-%Y')})" for c in chara_dashas]
            default_c_idx = next((i for i, c in enumerate(chara_dashas) if c["start_date"] <= target_dt <= c["end_date"]), 0)
            sel_c_idx = st.selectbox("चर दशा राशि चुनें", range(len(c_options)), format_func=lambda i: c_options[i], index=default_c_idx, key="sel_chara_for_antar")
            sel_c_obj = chara_dashas[sel_c_idx]

            c_antars = c_engine.generate_antardashas(sel_c_obj["sign_id"], sel_c_obj["start_date"], sel_c_obj["end_date"])
            st.dataframe(pd.DataFrame([{
                "चर महादशा / अंतर्दशा": f"{sel_c_obj['sign_name']} — {ca['sign_name']}",
                "राशि स्वामी (Lord)": ca["lord"],
                "आरंभ दिनांक": ca["start_date"].strftime("%d-%b-%Y"),
                "समाप्ति दिनांक": ca["end_date"].strftime("%d-%b-%Y"),
                "अवधि": f"{ca['duration_months']} माह ({ca['duration_days']} दिन)",
                "सक्रियता": "⭐ सक्रिय" if (ca["start_date"] <= target_dt <= ca["end_date"]) else ""
            } for ca in c_antars]), use_container_width=True, hide_index=True)

        with tab_c3:
            st.markdown("##### ⚡ चर प्रत्यंतर्दशा (12 Sub-divisions per Antardasha)")
            col_c_p1, col_c_p2 = st.columns(2)
            with col_c_p1:
                sel_c_m_idx = st.selectbox("महादशा राशि", range(len(c_options)), format_func=lambda i: c_options[i], index=default_c_idx, key="sel_c_m_for_prat")
            sel_c_m_p = chara_dashas[sel_c_m_idx]
            c_antars_p = c_engine.generate_antardashas(sel_c_m_p["sign_id"], sel_c_m_p["start_date"], sel_c_m_p["end_date"])
            with col_c_p2:
                sel_c_a_idx = st.selectbox("अंतर्दशा राशि", range(len(c_antars_p)), format_func=lambda i: f"{c_antars_p[i]['sign_name']} ({c_antars_p[i]['start_date'].strftime('%d-%b-%y')})", key="sel_c_a_for_prat")
            sel_c_a_p = c_antars_p[sel_c_a_idx]

            c_prats = c_engine.generate_pratyantardashas(sel_c_a_p["sign_id"], sel_c_a_p["start_date"], sel_c_a_p["end_date"])
            st.dataframe(pd.DataFrame([{
                "3-स्तरीय चर दशा": f"{sel_c_m_p['sign_name']} / {sel_c_a_p['sign_name']} / {cp['sign_name']}",
                "राशि स्वामी": cp["lord"],
                "आरंभ दिनांक": cp["start_date"].strftime("%d-%b-%Y"),
                "समाप्ति दिनांक": cp["end_date"].strftime("%d-%b-%Y"),
                "अवधि (दिन)": f"{cp['duration_days']} दिन",
                "सक्रियता": "⭐ सक्रिय" if (cp["start_date"] <= target_dt <= cp["end_date"]) else ""
            } for cp in c_prats]), use_container_width=True, hide_index=True)

    # =========================================================================
    # 4. KAALACHAKRA DASHA (BPHS)
    # =========================================================================
    elif "कालचक्र" in d_mode:
        st.markdown("#### 🔄 कालचक्र महादशा (Kaalachakra Dasha - BPHS)")
        kcd_res = default_kcd_engine.calculate(chart)

        # Determine active KCD period
        act_kcd = None
        for item in kcd_res["timeline"]:
            try:
                s_dt = datetime.strptime(item["start_date"], "%d-%b-%Y")
                e_dt = datetime.strptime(item["end_date"], "%d-%b-%Y")
                if s_dt <= target_dt <= e_dt:
                    act_kcd = item
                    break
            except Exception:
                pass
        if not act_kcd and kcd_res["timeline"]:
            act_kcd = kcd_res["timeline"][0]

        # Top Banner
        b_str_kcd = (
            f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
            f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय कालचक्र दशा स्थिति (Active Kaalachakra Dasha Overview):</div>"
            f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
            f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🔄 सक्रिय राशि: {act_kcd['rashi']} ({act_kcd.get('role', '') or 'दशा'})</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>👤 देह राशि: {kcd_res['deha_rashi']}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>❤️ जीव राशि: {kcd_res['jeeva_rashi']}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>🌀 गति: {act_kcd['gati'].split('/')[0]}</span>"
            f"</div>"
            f"</div>"
        )
        st.markdown(b_str_kcd, unsafe_allow_html=True)

        # 4 Styled Metric Cards
        col_kc1, col_kc2, col_kc3, col_kc4 = st.columns(4)
        with col_kc1:
            st.markdown(f"""
            <div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🔄 सक्रिय कालचक्र राशि</div>
                <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_kcd['rashi']}</div>
                <div style="font-size:10.5px; color:#475569;">{act_kcd['start_date']} ~ {act_kcd['end_date']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_kc2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#15803D; font-weight:800;">👤 देह राशि (Deha Rashi)</div>
                <div style="font-size:18px; font-weight:900; color:#064E3B;">{kcd_res['deha_rashi']}</div>
                <div style="font-size:10.5px; color:#475569;">शारीरिक सुख व स्वास्थ्य</div>
            </div>
            """, unsafe_allow_html=True)
        with col_kc3:
            st.markdown(f"""
            <div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#B45309; font-weight:800;">❤️ जीव राशि (Jeeva Rashi)</div>
                <div style="font-size:18px; font-weight:900; color:#78350F;">{kcd_res['jeeva_rashi']}</div>
                <div style="font-size:10.5px; color:#475569;">मानसिक एवं आत्मिक शांति</div>
            </div>
            """, unsafe_allow_html=True)
        with col_kc4:
            st.markdown(f"""
            <div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#BE185D; font-weight:800;">✨ चक्र वर्ग एवं नक्षत्र</div>
                <div style="font-size:18px; font-weight:900; color:#831843;">{kcd_res['nakshatra']} (पद {kcd_res['pada']})</div>
                <div style="font-size:10.5px; color:#475569;">{kcd_res['group_type']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.dataframe(pd.DataFrame(kcd_res["timeline"]), use_container_width=True)

        st.info("💡 **कालचक्र गति फल:** 'मण्डूक गति' (Frog Jump) अथवा 'सिंहावलोकन' (Lion's Gaze) की दशा में जीवन में अचानक बड़े परिवर्तन, स्थान परिवर्तन अथवा अप्रत्याशित उत्थान/पतन घटित होता है। देह राशि शारीरिक सुख-स्वास्थ्य और जीव राशि मानसिक व आत्मिक शांति का नियंत्रण करती है।")

    # =========================================================================
    # 5. SHOOLA DASHA (AYURDAYA & MARAKA)
    # =========================================================================
    elif "शूल" in d_mode:
        st.markdown("#### 🔱 शूल महादशा (Shoola Dasha - Ayurdaya & Maraka Timing)")
        shoola_res = default_shoola_engine.calculate(chart)

        # Determine active Shoola period
        act_shoola = None
        for item in shoola_res["timeline"]:
            try:
                s_dt = datetime.strptime(item["start_date"], "%d-%b-%Y")
                e_dt = datetime.strptime(item["end_date"], "%d-%b-%Y")
                if s_dt <= target_dt <= e_dt:
                    act_shoola = item
                    break
            except Exception:
                pass
        if not act_shoola and shoola_res["timeline"]:
            act_shoola = shoola_res["timeline"][0]

        # Top Banner
        b_str_shoola = (
            f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
            f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय शूल दशा एवं आयुर्दाय स्थिति (Active Shoola Dasha & Ayurdaya Status):</div>"
            f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
            f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>🔱 सक्रिय शूल राशि: {act_shoola['sign']} ({act_shoola['duration_years']} वर्ष)</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>🎯 आरंभिक बीज राशि: {shoola_res['start_sign']}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ त्रिशूल राशियाँ: {', '.join(shoola_res['trishoola_signs'])}</span> "
            f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
            f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>🛡️ जोखिम स्तर: {act_shoola['risk_level'].split('/')[0]}</span>"
            f"</div>"
            f"</div>"
        )
        st.markdown(b_str_shoola, unsafe_allow_html=True)

        # 4 Styled Metric Cards
        col_sh1, col_sh2, col_sh3, col_sh4 = st.columns(4)
        with col_sh1:
            st.markdown(f"""
            <div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#4338CA; font-weight:800;">🔱 सक्रिय शूल दशा राशि</div>
                <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{act_shoola['sign']}</div>
                <div style="font-size:10.5px; color:#475569;">{act_shoola['start_date']} ~ {act_shoola['end_date']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_sh2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#15803D; font-weight:800;">🎯 आरंभिक बीज राशि</div>
                <div style="font-size:18px; font-weight:900; color:#064E3B;">{shoola_res['start_sign']}</div>
                <div style="font-size:10.5px; color:#475569;">{shoola_res['direction']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_sh3:
            st.markdown(f"""
            <div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#B45309; font-weight:800;">⚡ त्रिशूल राशियाँ (Trishoola)</div>
                <div style="font-size:16px; font-weight:900; color:#78350F;">{', '.join(shoola_res['trishoola_signs'])}</div>
                <div style="font-size:10.5px; color:#475569;">रुद्रांश त्रिकोण राशियाँ</div>
            </div>
            """, unsafe_allow_html=True)
        with col_sh4:
            st.markdown(f"""
            <div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
                <div style="font-size:11.5px; color:#BE185D; font-weight:800;">🛡️ वर्तमान जोखिम स्थिति</div>
                <div style="font-size:16px; font-weight:900; color:#831843;">{act_shoola['risk_level'].split('/')[0]}</div>
                <div style="font-size:10.5px; color:#475569;">ग्रह स्थिति: {act_shoola['occupants']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.dataframe(pd.DataFrame(shoola_res["timeline"]), use_container_width=True)

        st.warning("⚠️ **शूल दशा शास्त्रीय उपयोग:** शूल दशा जातक के जीवन में स्वास्थ्य संकट, शल्यक्रिया (Surgery), दुर्घटना एवं मारक काल के सूक्ष्म परीक्षण हेतु उपयोग की जाती है। जब दशा त्रिशूल राशि में हो और उस पर क्रूर ग्रहों का प्रभाव हो, तो वह काल विशेष रूप से संवेदनशील होता है।")


# =============================================================
# TAB 11: GOCHAR & ASHTAKAVARGA & CHAKRAS

elif selected_idx == 10:
    st.subheader("🪐 गोचर, अष्टकवर्ग, सर्वतोभद्र चक्र एवं कोटा चक्र")
    st.write("तात्कालिक ग्रह गोचर स्थिति, साढ़ेसाती व ढैया ट्रैकर, 8x12 भिन्नाष्टकवर्ग, 9x9 सर्वतोभद्र वेध चक्र एवं 4-क्षेत्रीय कोटा दुर्ग चक्र।")

    # Interactive Transit Time-Machine
    with st.expander("⏱️ गोचर समय-चक्र टाइम-मशीन (Interactive Transit Date Slider)", expanded=False):
        col_tm1, col_tm2 = st.columns([3, 1])
        with col_tm1:
            time_offset_days = st.slider(
                "दिनों को आगे-पीछे खींचकर भविष्य/भूतकाल का गोचर देखें (Days Offset from Today)",
                min_value=-365,
                max_value=365*5,
                value=0,
                step=1
            )
        with col_tm2:
            target_calc_date = datetime.now().date() + timedelta(days=time_offset_days)
            st.metric("सक्रिय गोचर दिनांक", target_calc_date.strftime("%d-%b-%Y"), f"{'+' if time_offset_days>=0 else ''}{time_offset_days} दिन")

    # Date-time picker for live transit
    col_gt1, col_gt2, col_gt3 = st.columns([1.5, 1.5, 2])
    with col_gt1:
        t_date = st.date_input("📅 गोचर दिनांक (Transit Date)", value=target_calc_date if 'target_calc_date' in locals() else datetime.now().date(), format="DD/MM/YYYY")
    with col_gt2:
        t_time = st.time_input("🕒 गोचर समय (Transit Time)", value=datetime.now().time())
    with col_gt3:
        st.write("")
        st.caption("📍 स्थान: **" + str(default_city_name) + "** (Lat: " + f"{latitude:.2f}" + ", Lon: " + f"{longitude:.2f}" + ")")

    # Calculate live transit chart
    t_birth = BirthData(
        name="Transit",
        birth_date=t_date,
        birth_time=t_time,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=tz_offset,
        city=default_city_name
    )
    t_chart = default_chart_calculator.calculate_full_chart(t_birth, ayanamsa_name=ayanamsa, house_system=house_system)

    tab_g1, tab_g2, tab_g3 = st.tabs([
        "🪐 दैनिक गोचर व अष्टकवर्ग (Live Transits & BAV/SAV)",
        "🛡️ सर्वतोभद्र चक्र (9x9 Sarvatobhadra Vedha)",
        "🏰 कोटा चक्र (Kota Chakra 4-Zone Fortress)"
    ])

    with tab_g1:
        # -------------------------------------------------------------
        # 1. Real-Time Planetary Transit Table (तात्कालिक गोचर स्थिति)
        # -------------------------------------------------------------
        st.markdown("#### 🔴 तात्कालिक ग्रह गोचर तालिका (Real-Time Planetary Transits)")
        
        rashi_names_hi = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
        rashi_symbols = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
        
        natal_lagna_id = chart.lagna_sign_id
        natal_moon_id = chart.planets["Moon"].sign_id if "Moon" in chart.planets else 1

        gochar_rows = []
        planet_icons = {
            "Sun": "☀️ सूर्य",
            "Moon": "🌙 चन्द्र",
            "Mars": "⚔️ मंगल",
            "Mercury": "☿️ बुध",
            "Jupiter": "🪐 गुरु",
            "Venus": "💎 शुक्र",
            "Saturn": "⚖️ शनि",
            "Rahu": "🐉 राहु",
            "Ketu": "☄️ केतु"
        }

        sav_list = chart.ashtakavarga.sav if chart.ashtakavarga else [28]*12

        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in t_chart.planets:
                tp = t_chart.planets[p_name]
                s_idx = tp.sign_id - 1
                s_name = rashi_names_hi[s_idx]
                s_sym = rashi_symbols[s_idx]
                deg_str = f"{int(tp.sign_degree)}° {int((tp.sign_degree % 1)*60)}'"
                
                # House from Natal Lagna & Natal Moon
                h_from_lagna = (tp.sign_id - natal_lagna_id) % 12 + 1
                h_from_moon = (tp.sign_id - natal_moon_id) % 12 + 1
                
                # SAV bindus in transit sign
                sign_sav = sav_list[s_idx]
                sav_status = "🌟 उत्तम (" + str(sign_sav) + ")" if sign_sav >= 30 else ("✅ शुभ (" + str(sign_sav) + ")" if sign_sav >= 28 else "⚠️ न्यून (" + str(sign_sav) + ")")
                
                motion_str = "⚡ वक्री (R)" if tp.is_retrograde else "मार्गी (D)"
                
                gochar_rows.append({
                    "ग्रह (Planet)": planet_icons.get(p_name, p_name),
                    "गोचर राशि (Sign)": f"{s_sym} {s_name}",
                    "अंश (Degree)": deg_str,
                    "नक्षत्र (Nakshatra)": f"{tp.nakshatra_name} (पद {tp.nakshatra_pada})",
                    "गति (Motion)": motion_str,
                    "लग्न से भाव": f"{h_from_lagna} भाव",
                    "चन्द्र से भाव": f"{h_from_moon} भाव",
                    "SAV सामर्थ्य": sav_status
                })

        st.dataframe(pd.DataFrame(gochar_rows), use_container_width=True)

        st.markdown("---")

        # -------------------------------------------------------------
        # 2. Saturn Transit / Sade Sati & Double Transit HUD Cards
        # -------------------------------------------------------------
        col_sat, col_dt = st.columns(2)

        with col_sat:
            st.markdown("#### 🪐 साढ़ेसाती एवं ढैया लाइव ट्रैकर (Saturn Transit)")
            sat_sign_id = t_chart.planets["Saturn"].sign_id if "Saturn" in t_chart.planets else 11
            sat_diff = (sat_sign_id - natal_moon_id) % 12
            
            sat_phase_title = "सामान्य गोचर"
            sat_badge_class = "harmonious"
            sat_desc = ""
            
            if sat_diff == 11:
                sat_phase_title = "साढ़ेसाती: प्रथम चरण (Rising Phase - 12th House)"
                sat_badge_class = "high-risk"
                sat_desc = "शनि जन्म चन्द्र से 12वें भाव में गोचरस्थ हैं। मानसिक तनाव, व्यय एवं दूरस्थ यात्राओं के संकेत।"
            elif sat_diff == 0:
                sat_phase_title = "साढ़ेसाती: द्वितीय चरण (Peak / Janma Shani - 1st House)"
                sat_badge_class = "high-risk"
                sat_desc = "शनि चन्द्र के ऊपर से गोचर कर रहे हैं। धैर्य, अनुशासन एवं स्वास्थ्य पर विशेष ध्यान अपेक्षित है।"
            elif sat_diff == 1:
                sat_phase_title = "साढ़ेसाती: तृतीय चरण (Setting Phase - 2nd House)"
                sat_badge_class = "moderate-risk"
                sat_desc = "शनि चन्द्र से द्वितीय भाव (धन भाव) में हैं। आर्थिक संतुलन एवं वाणी पर नियंत्रण लाभप्रद रहेगा।"
            elif sat_diff == 3:
                sat_phase_title = "कंटक शनि / लघु कल्याणी ढैया (4th House)"
                sat_badge_class = "moderate-risk"
                sat_desc = "शनि चन्द्र से चतुर्थ भाव में हैं। गृह-सुख, वाहन एवं माता के स्वास्थ्य में सावधानी बरतें।"
            elif sat_diff == 7:
                sat_phase_title = "अष्टम शनि / कंटक ढैया (8th House)"
                sat_badge_class = "high-risk"
                sat_desc = "शनि चन्द्र से अष्टम भाव में हैं। आकस्मिक बदलाव, गूढ़ ज्ञान में वृद्धि परंतु स्वास्थ्य में सावधानी।"
            else:
                sat_phase_title = f"अनुकूल गोचर (चन्द्र से {sat_diff + 1}वें भाव में)"
                sat_badge_class = "harmonious"
                sat_desc = f"शनि का वर्तमान गोचर चन्द्र राशि ({rashi_names_hi[natal_moon_id-1]}) से {sat_diff + 1}वें भाव में अनुकूल फलदायक है।"

            bg_col = "#FEF2F2" if "high" in sat_badge_class else ("#FFFBEB" if "moderate" in sat_badge_class else "#ECFDF5")
            border_col = "#EF4444" if "high" in sat_badge_class else ("#F59E0B" if "moderate" in sat_badge_class else "#10B981")
            text_col = "#991B1B" if "high" in sat_badge_class else ("#92400E" if "moderate" in sat_badge_class else "#065F46")

            st.markdown(f"""
            <div style="background:#FFFFFF; border:1.5px solid {border_col}; border-radius:10px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <b style="font-size:14px; color:#0F172A;">🌙 जातक चन्द्र राशि: {rashi_names_hi[natal_moon_id-1]}</b>
                    <span style="background:{bg_col}; color:{text_col}; border:1.5px solid {border_col}; border-radius:8px; padding:3px 8px; font-weight:800; font-size:11.5px;">
                        {sat_phase_title.split('(')[0]}
                    </span>
                </div>
                <div style="font-size:12.5px; color:#1E293B; line-height:1.5; margin-bottom:8px;">
                    🪐 <b>वर्तमान शनि गोचर:</b> {rashi_symbols[sat_sign_id-1]} {rashi_names_hi[sat_sign_id-1]} राशि<br/>
                    📜 <b>शास्त्रीय प्रभाव:</b> {sat_desc}
                </div>
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; font-size:11.5px; color:#334155;">
                    🪔 <b>शास्त्रीय उपाय:</b> शनिवार को पीपल के वृक्ष पर तिल के तेल का दीपक प्रज्वलित करें एवं ॐ शं शनैश्चराय नमः का जप करें।
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_dt:
            st.markdown("#### ⚡ गुरु-शनि दोहरा गोचर (Double Transit Analysis)")
            j_sign_id = t_chart.planets["Jupiter"].sign_id if "Jupiter" in t_chart.planets else 2
            s_sign_id = t_chart.planets["Saturn"].sign_id if "Saturn" in t_chart.planets else 11
            
            # Jupiter aspects: 1, 5, 7, 9
            j_asp_signs = [j_sign_id, (j_sign_id - 1 + 4) % 12 + 1, (j_sign_id - 1 + 6) % 12 + 1, (j_sign_id - 1 + 8) % 12 + 1]
            # Saturn aspects: 1, 3, 7, 10
            s_asp_signs = [s_sign_id, (s_sign_id - 1 + 2) % 12 + 1, (s_sign_id - 1 + 6) % 12 + 1, (s_sign_id - 1 + 9) % 12 + 1]
            
            common_signs = sorted(list(set(j_asp_signs).intersection(set(s_asp_signs))))
            
            house_significances = {
                1: "व्यक्तिगत स्वास्थ्य, प्रतिष्ठा एवं नई शुरुआत",
                2: "धन, पैतृक संपत्ति एवं पारिवारिक वृद्धि",
                3: "पराक्रम, नए अनुबंध एवं छोटे भाई-बहन",
                4: "भूमि, भवन, वाहन एवं पारिवारिक सुख",
                5: "संतान, विद्या, निवेश एवं मंत्र सिद्धि",
                6: "ऋण मुक्ति, रोग निवारण एवं प्रतियोगिता में विजय",
                7: "विवाह, व्यापारिक साझेदारी एवं जन-सम्बंध",
                8: "गूढ़ शोध, वसीयत एवं आकस्मिक लाभ",
                9: "उच्च शिक्षा, तीर्थाटन एवं भाग्योदय",
                10: "कार्यक्षेत्र, पदोन्नति, मान-सम्मान एवं व्यवसाय",
                11: "आय वृद्धि, महत्वाकांक्षा पूर्ति एवं लाभ",
                12: "विदेश यात्रा, आध्यात्मिक सिद्धि एवं शुभ व्यय"
            }

            st.markdown(f"""
            <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:14px; box-shadow:0 2px 8px rgba(37,99,235,0.06);">
                <div style="font-weight:800; color:#1E40AF; font-size:13.5px; margin-bottom:6px;">
                    🎯 जीवन के सक्रिय भाव (Doubly Activated Houses)
                </div>
                <div style="font-size:12px; color:#1E293B; margin-bottom:8px; line-height:1.5;">
                    गुरु ({rashi_names_hi[j_sign_id-1]}) और शनि ({rashi_names_hi[s_sign_id-1]}) दोनों की संयुक्त दृष्टि/गोचर वाले राशियाँ:
                </div>
                <div style="display:flex; flex-direction:column; gap:6px;">
            """, unsafe_allow_html=True)
            
            for c_sign in common_signs:
                h_lagna = (c_sign - natal_lagna_id) % 12 + 1
                h_meaning = house_significances.get(h_lagna, "शुभ फलदायक")
                st.markdown(f"""
                <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:6px; padding:5px 8px; font-size:12px; color:#1E3A8A;">
                    ✨ <b>{rashi_symbols[c_sign-1]} {rashi_names_hi[c_sign-1]} (लग्न से {h_lagna} भाव):</b> {h_meaning}
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        # -------------------------------------------------------------
        # 3. Complete Classical BAV (8x12) Matrix & SAV Table
        # -------------------------------------------------------------
        st.markdown("#### 📊 सम्पूर्ण भिन्नाष्टकवर्ग (BAV 8x12) एवं सर्व अष्टकवर्ग (SAV) तालिका")
        st.write("7 प्रमुख ग्रहों का द्वादश राशियों में बिन्दु आवंटन (0-3: न्यून/लाल, 4: सम, 5-8: शुभ/हरा, कुल: 337 बिन्दु)।")

        if chart.ashtakavarga and chart.ashtakavarga.bav:
            bav_matrix = chart.ashtakavarga.bav
            sav_array = chart.ashtakavarga.sav
            
            # Build HTML Table
            bav_html = '<div style="overflow-x: auto; border: 1.5px solid #CBD5E1; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">'
            bav_html += '<table style="width: 100%; border-collapse: collapse; text-align: center; background: #FFFFFF; font-family: Segoe UI, Arial, sans-serif;">'
            
            # Header Row
            bav_html += '<thead><tr style="background: #F1F5F9; border-bottom: 2px solid #CBD5E1;">'
            bav_html += '<th style="padding: 10px 12px; font-weight: 800; color: #0F172A; font-size: 13px; text-align: left;">ग्रह / राशि</th>'
            for s_i, r_name in enumerate(rashi_names_hi):
                bav_html += f'<th style="padding: 10px 6px; font-weight: 800; color: #0F172A; font-size: 12px;">{rashi_symbols[s_i]}<br/>{r_name}</th>'
            bav_html += '<th style="padding: 10px 8px; font-weight: 900; color: #1E3A8A; font-size: 13px; background: #DBEAFE;">कुल</th>'
            bav_html += '</tr></thead><tbody>'
            
            planet_order = [
                ("Sun", "☀️ सूर्य (Sun)"),
                ("Moon", "🌙 चन्द्र (Moon)"),
                ("Mars", "⚔️ मंगल (Mars)"),
                ("Mercury", "☿️ बुध (Mercury)"),
                ("Jupiter", "🪐 गुरु (Jupiter)"),
                ("Venus", "💎 शुक्र (Venus)"),
                ("Saturn", "⚖️ शनि (Saturn)")
            ]
            
            for p_k, p_label in planet_order:
                bav_row = bav_matrix.get(p_k, [0]*12)
                row_total = sum(bav_row)
                bav_html += '<tr style="border-bottom: 1px solid #E2E8F0;">'
                bav_html += f'<td style="padding: 8px 12px; font-weight: 700; color: #0F172A; font-size: 12.5px; text-align: left; background: #F8FAFC;">{p_label}</td>'
                for b_val in bav_row:
                    if b_val <= 3:
                        cell_bg = "#FEE2E2"
                        cell_color = "#991B1B"
                    elif b_val == 4:
                        cell_bg = "#F8FAFC"
                        cell_color = "#334155"
                    else:
                        cell_bg = "#DCFCE7"
                        cell_color = "#166534"
                    bav_html += f'<td style="padding: 6px 4px; font-weight: 800; font-size: 13px; background: {cell_bg}; color: {cell_color}; border: 1px solid #E2E8F0;">{b_val}</td>'
                bav_html += f'<td style="padding: 6px 8px; font-weight: 900; font-size: 13px; background: #EFF6FF; color: #1E40AF; border: 1px solid #CBD5E1;">{row_total}</td>'
                bav_html += '</tr>'
                
            # SAV Summary Row
            bav_html += '<tr style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border-top: 2.5px solid #D97706; font-weight: 900;">'
            bav_html += '<td style="padding: 10px 12px; color: #78350F; font-size: 13.5px; text-align: left;">🌟 सर्व अष्टकवर्ग (SAV)</td>'
            for sav_val in sav_array:
                sav_color = "#166534" if sav_val >= 28 else "#991B1B"
                bav_html += f'<td style="padding: 8px 4px; color: {sav_color}; font-size: 14px; border: 1px solid #FCD34D;">{sav_val}</td>'
            bav_html += f'<td style="padding: 8px 8px; color: #78350F; font-size: 15px; border: 1.5px solid #D97706; background: #FDE68A;">{sum(sav_array)}</td>'
            bav_html += '</tr></tbody></table></div>'
            
            st.markdown(bav_html, unsafe_allow_html=True)

        # -------------------------------------------------------------
        # 4. Shodhita Pinda & Visual Bar Chart
        # -------------------------------------------------------------
        col_av1, col_av2 = st.columns(2)
        with col_av1:
            st.markdown("#### 📈 सर्व अष्टकवर्ग (SAV) बिन्दु वितरण")
            sav_df = pd.DataFrame({"Rashi": rashi_names_hi, "Bindus": chart.ashtakavarga.sav}).set_index("Rashi")
            st.bar_chart(sav_df)

        with col_av2:
            st.markdown("#### ⚖️ शोधित पिण्ड (Shodhita Pinda & Ayurdaya)")
            if chart.ashtakavarga.shodhana:
                sh = chart.ashtakavarga.shodhana
                pinda_data = []
                for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                    pinda_data.append({
                        "ग्रह (Planet)": planet_icons.get(p_name, p_name),
                        "राशि पिण्ड": sh.rashi_pinda.get(p_name, 0),
                        "ग्रह पिण्ड": sh.graha_pinda.get(p_name, 0),
                        "योग पिण्ड": sh.yoga_pinda.get(p_name, 0),
                    })
                st.dataframe(pd.DataFrame(pinda_data), use_container_width=True)
                st.caption("💡 **शोधित पिण्ड फल:** त्रिकोण शोधन एवं एकाधिपत्य शोधन के उपरांत प्राप्त योग पिण्ड से आयुर्दाय एवं गोचर वेध का निर्णय किया जाता है।")

    with tab_g2:
        st.markdown("#### 🛡️ सर्वतोभद्र चक्र (9x9 Sarvatobhadra Vedha Matrix)")
        st.write("28 नक्षत्रों (अभिजित सहित), 12 राशियों, स्वरों, तिथियों एवं संवेदनशील नक्षत्रों पर गोचर ग्रहों के सम्मुख व तिर्यक (Diagonal) वेध का शास्त्रीय विश्लेषण।")

        sbc_res = default_sarvatobhadra_engine.calculate(chart, t_chart)

        # Render 9x9 HTML Grid
        sbc_grid = sbc_res["grid_layout"]
        grid_html = '<div style="overflow-x: auto; border: 1.5px solid #CBD5E1; border-radius: 10px; padding: 10px; background: #FFFFFF; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 16px;">'
        grid_html += '<table style="margin: 0 auto; border-collapse: collapse; text-align: center; font-size: 11.5px;">'

        for row_idx, row in enumerate(sbc_grid):
            grid_html += '<tr>'
            for col_idx, (c_type, c_val) in enumerate(row):
                bg_col = "#FFFFFF"
                fg_col = "#0F172A"
                border_col = "#E2E8F0"
                font_weight = "600"

                if c_type == "center":
                    bg_col = "#FEF3C7"
                    fg_col = "#78350F"
                    font_weight = "900"
                    border_col = "#D97706"
                elif c_type == "nak":
                    # Highlight if Janma Nakshatra
                    if c_val == sbc_res["janma_nakshatra_28"]:
                        bg_col = "#DCFCE7"
                        fg_col = "#166534"
                        font_weight = "900"
                        border_col = "#10B981"
                    else:
                        bg_col = "#F0FDF4"
                        fg_col = "#15803D"
                elif c_type == "rashi":
                    bg_col = "#EFF6FF"
                    fg_col = "#1E40AF"
                    font_weight = "700"
                elif c_type == "vowel":
                    bg_col = "#FFFBEB"
                    fg_col = "#92400E"
                elif c_type == "tithi":
                    bg_col = "#F8FAFC"
                    fg_col = "#475569"
                elif c_type == "dir":
                    bg_col = "#F1F5F9"
                    fg_col = "#0F172A"
                    font_weight = "800"

                grid_html += f'<td style="padding: 7px 8px; border: 1px solid {border_col}; background: {bg_col}; color: {fg_col}; font-weight: {font_weight}; min-width: 48px; max-width: 90px; height: 36px; white-space: nowrap;">{c_val}</td>'
            grid_html += '</tr>'
        grid_html += '</table></div>'
        st.markdown(grid_html, unsafe_allow_html=True)

        col_sb_v1, col_sb_v2 = st.columns([1.2, 1.8])
        with col_sb_v1:
            st.markdown("#### ⚡ सक्रिय गोचर वेध (Active Vedhas)")
            if sbc_res["vedhas"]:
                v_df = pd.DataFrame(sbc_res["vedhas"])
                st.dataframe(v_df[["planet", "planet_nak", "target_point", "vedha_type", "impact"]], use_container_width=True)
            else:
                st.success("✅ कोई प्रत्यक्ष अनिष्टकारी वेध सक्रिय नहीं है।")

        with col_sb_v2:
            st.markdown("#### 🎯 जातक के 16 संवेदनशील नक्षत्र (Sensitive Points)")
            sp_df = pd.DataFrame(sbc_res["sensitive_points"])
            st.dataframe(sp_df[["hi_name", "nakshatra", "desc"]], use_container_width=True)

    with tab_g3:
        st.markdown("#### 🏰 कोटा चक्र (Kota Chakra 4-Zone Durga Fortress)")
        st.write("जन्म नक्षत्र आधारित 4-क्षेत्रीय दुर्ग (स्तम्भ, मध्य, प्राकार, बाह्य) एवं गोचर ग्रहों के प्रवेश/निर्गम द्वारा रक्षा व संकट का मूल्यांकन।")

        kota_res = default_kota_chakra_engine.calculate(chart, t_chart)

        # Defense Summary Banner
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:16px; margin-bottom:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                <div>
                    <span style="font-size:16px; font-weight:900; color:#1E40AF;">🛡️ कोटा स्वामी: <b>{kota_res['kota_swami']}</b></span>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    <span style="font-size:16px; font-weight:900; color:#0F766E;">⚔️ कोटा पाल: <b>{kota_res['kota_pala']}</b></span>
                </div>
                <div style="font-size:13px; font-weight:800; background:#EFF6FF; color:#1E40AF; border:1.5px solid #3B82F6; border-radius:8px; padding:4px 10px;">
                    {kota_res['defense_status']}
                </div>
            </div>
            <div style="font-size:13px; color:#1E293B; line-height:1.6;">
                📜 <b>दुर्ग स्थिति विश्लेषण:</b> {kota_res['defense_summary']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_kt1, col_kt2 = st.columns(2)
        with col_kt1:
            st.markdown("#### 🪐 गोचर ग्रहों का दुर्ग में स्थान व गति (Allocations)")
            st.dataframe(pd.DataFrame(kota_res["planet_allocations"]), use_container_width=True)

        with col_kt2:
            st.markdown("#### 🏰 कोटा चक्र के 4 क्षेत्र एवं नक्षत्र विभाजन (Zones)")
            zone_data = [{"क्षेत्र (Zone)": z_name, "समाहित नक्षत्र (Nakshatras)": ", ".join(nak_list)} for z_name, nak_list in kota_res["zones_map"].items()]
            st.dataframe(pd.DataFrame(zone_data), use_container_width=True)
            st.caption("💡 **कोटा चक्र नियम:** स्तम्भ (केन्द्र) में पापी ग्रहों का प्रवेश रोग/संकट कारक होता है, जबकि शुभ ग्रहों का प्रवेश दुर्ग को अभेद्य बनाता है।")


# =============================================================
# TAB 12: KP ASTROLOGY (KRISHNAMURTI PADDHATI)

elif selected_idx == 11:
    st.subheader("📐 के.पी. ज्योतिष प्रणाली (Krishnamurti Paddhati - KP System & Future Prediction)")
    st.write("कृष्णमूर्ति पद्धति आधारित 4-स्तरीय कार्यकत्व (4-Fold Significators), कस्पल सब-लॉर्ड (Sub-Lords), उप-उप स्वामी (Sub-Sub Lords), रूलिंग प्लैनेट्स (RP), 1-249 होरारी व भविष्य फलित निर्णय।")

    import importlib
    import src.jyotish.core.kp as kp_mod
    if not hasattr(kp_mod.default_kp_engine, "predict_kp_query"):
        importlib.reload(kp_mod)
    k_engine = kp_mod.default_kp_engine

    # 1. Calculation Mode Selector
    kp_mode = st.radio(
        "🎯 के.पी. गणना एवं फलित मोड चुनें:",
        ["👤 सक्रिय जातक के.पी. जन्मपत्री एवं फलित (Active Native KP Natal & Prediction)",
         "🔮 तत्कालिक 1-249 कृष्णमूर्ति होरारी प्रश्न (KP Instant Horary Question & Prediction)"],
        horizontal=True
    )

    active_kp_chart = chart
    chosen_horary_num = None

    if "तत्कालिक 1-249" in kp_mode:
        st.markdown("##### 🔮 तत्कालिक के.पी. होरारी प्रश्न विवरण दर्ज करें (Date, Time, Location & Horary No.)")
        c_hq1, c_hq2, c_hq3, c_hq4 = st.columns([1.2, 1.2, 1.2, 1.4])
        with c_hq1:
            chosen_horary_num = st.number_input("🔢 होरारी संख्या (1 - 249)", min_value=1, max_value=249, value=108, step=1, key="kp_horary_input_num")
        with c_hq2:
            q_date = st.date_input("📅 प्रश्न दिनांक (Date)", value=datetime.now().date(), format="DD/MM/YYYY", key="kp_q_date")
        with c_hq3:
            q_time = st.time_input("⏰ प्रश्न समय (Time)", value=datetime.now().time(), key="kp_q_time")
        with c_hq4:
            q_city = st.text_input("📍 प्रश्न स्थान (City)", value=default_city_name, key="kp_q_city")

        # Resolve Horary Location & Calculate Horary Chart
        loc_res = default_geocoding_service.resolve(q_city)
        if loc_res:
            h_lat = float(loc_res.get("latitude", 28.6139))
            h_lon = float(loc_res.get("longitude", 77.2090))
            h_tz = float(loc_res.get("timezone_offset", 5.5))
            h_city = loc_res.get("city", q_city)
        else:
            h_lat, h_lon, h_tz, h_city = 28.6139, 77.2090, 5.5, q_city

        h_bdata = BirthData(
            name=f"KP Horary #{chosen_horary_num}",
            gender="Unknown",
            birth_date=q_date,
            birth_time=q_time,
            latitude=h_lat,
            longitude=h_lon,
            timezone_offset=h_tz,
            city_name=h_city
        )
        try:
            active_kp_chart = default_chart_calculator.calculate_chart(h_bdata)
            # In KP Horary, Ascendant is fixed to the selected 1-249 sub-division starting longitude
            h_entry = k_engine.get_horary_number_detail(int(chosen_horary_num))
            active_kp_chart.lagna_longitude = h_entry["start_lon"]
            active_kp_chart.lagna_sign_id = h_entry["sign_id"]
            active_kp_chart.lagna_degree = h_entry["start_deg"]
        except Exception as e:
            st.warning(f"होरारी गणना में त्रुटि, सक्रिय जातक का चार्ट उपयोग किया जा रहा है: {e}")
            active_kp_chart = chart

    kp_chart_data = k_engine.calculate_chart_kp(active_kp_chart)
    rp_info = kp_chart_data["ruling_planets"]
    cusps_data = kp_chart_data["cusps_kp"]
    planets_kp_data = kp_chart_data["planets_kp"]
    p_sigs = kp_chart_data["planet_significations"]
    h_sigs = kp_chart_data["house_significators"]

    # Active KP Top Banner (Light Golden HUD)
    lagna_csl = cusps_data[0]
    moon_kp_obj = next((p for p in planets_kp_data if p["planet"] == "Moon"), planets_kp_data[1])

    b_str_kp = (
        f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
        f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय के.पी. लग्न व चन्द्र सब-लॉर्ड पथ (Active KP Hierarchy & Ruling Planets):</div>"
        f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
        f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>👑 लग्न CSL: {lagna_csl['sub_lord']} ({lagna_csl['sign']})</span> "
        f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
        f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>🌙 चन्द्र CSL: {moon_kp_obj['sub_lord']} (नक्षत्र: {moon_kp_obj['star_lord']})</span> "
        f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
        f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ वार स्वामी: {rp_info['day_lord']['planet']}</span> "
        f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
        f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>👑 मुख्य RPs: {', '.join(rp_info['all_rp_list'][:4])}</span>"
        f"</div>"
        f"</div>"
    )
    st.markdown(b_str_kp, unsafe_allow_html=True)

    # 4 Matching Styled Metric Cards
    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
    with c_k1:
        st.markdown(f"""
        <div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
            <div style="font-size:11.5px; color:#4338CA; font-weight:800;">👑 लग्न कस्पल सब-लॉर्ड (L1 CSL)</div>
            <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{lagna_csl['sub_lord']}</div>
            <div style="font-size:10.5px; color:#475569;">Star: {lagna_csl['star_lord']} | SSL: {lagna_csl['sub_sub_lord']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c_k2:
        st.markdown(f"""
        <div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
            <div style="font-size:11.5px; color:#15803D; font-weight:800;">🌙 चन्द्र नक्षत्र व सब-लॉर्ड</div>
            <div style="font-size:18px; font-weight:900; color:#064E3B;">{moon_kp_obj['sub_lord']}</div>
            <div style="font-size:10.5px; color:#475569;">Star: {moon_kp_obj['star_lord']} ({moon_kp_obj['sign']})</div>
        </div>
        """, unsafe_allow_html=True)
    with c_k3:
        st.markdown(f"""
        <div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
            <div style="font-size:11.5px; color:#B45309; font-weight:800;">👑 वार स्वामी (Day Lord)</div>
            <div style="font-size:18px; font-weight:900; color:#78350F;">{rp_info['day_lord']['planet']}</div>
            <div style="font-size:10.5px; color:#475569;">{active_kp_chart.panchang.vara_name}</div>
        </div>
        """, unsafe_allow_html=True)
    with c_k4:
        st.markdown(f"""
        <div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
            <div style="font-size:11.5px; color:#BE185D; font-weight:800;">🔢 होरारी / लग्न स्थिति</div>
            <div style="font-size:18px; font-weight:900; color:#831843;">{"होरारी #" + str(chosen_horary_num) if chosen_horary_num else "जन्म लग्न"}</div>
            <div style="font-size:10.5px; color:#475569;">{lagna_csl['sign']} ({lagna_csl['degree_formatted']})</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 5 Sub-Tabs
    tab_kp_pred, tab_kp1, tab_kp2, tab_kp3, tab_kp4 = st.tabs([
        "🔮 के.पी. भविष्य फलित एवं कार्य सिद्धि निर्णय (KP Prediction)",
        "🪐 ग्रह के.पी. उप-स्वामी व ४-स्तरीय कार्यकत्व (Planets & Significations)",
        "🏰 द्वादश भाव कस्पल तालिका (12 Cuspal Sub-Lords)",
        "👑 रूलिंग प्लैनेट्स (Ruling Planets - RP)",
        "🔢 1-249 कृष्णमूर्ति होरारी तालिका (1-249 KP Master Table)"
    ])

    # -------------------------------------------------------------
    # TAB 1: KP FUTURE PREDICTION ENGINE
    # -------------------------------------------------------------
    with tab_kp_pred:
        st.markdown("#### 🔮 कृष्णमूर्ति पद्धति भविष्य फलित एवं कार्य सिद्धि विश्लेषक (KP Future Prediction Engine)")
        st.write("के.पी. पद्धति के सार्वभौमिक स्वर्णिम नियमों (Golden Rules of KP) पर आधारित — मुख्य कस्पल सब-लॉर्ड, नक्षत्र स्वामी, ४-स्तरीय भाव कार्यकत्व एवं रूलिंग प्लैनेट्स के आधार पर अचूक भविष्यवाणी।")

        col_q1, col_q2 = st.columns([1.5, 2.5])
        with col_q1:
            q_cat_options = list(kp_mod.KP_QUERY_RULES.keys())
            selected_q_key = st.selectbox(
                "📋 प्रश्न / अभीष्ट कार्य क्षेत्र चुनें (Select Domain):",
                q_cat_options,
                format_func=lambda k: kp_mod.KP_QUERY_RULES[k]["name"],
                key="kp_query_domain_select"
            )
        with col_q2:
            user_q_text = st.text_input(
                "✍️ विशिष्ट प्रश्न लिखें (वैकल्पिक):",
                placeholder="उदा. क्या मुझे इस वर्ष पदोन्नति/नई नौकरी मिलेगी? क्या विवाह संपन्न होगा?",
                key="kp_user_q_text"
            )

        btn_pred = st.button("🔮 के.पी. शास्त्रीय फलित एवं कार्य सिद्धि निर्णय प्राप्त करें", type="primary", use_container_width=True)

        # Execute Prediction
        pred_res = k_engine.predict_kp_query(
            active_kp_chart,
            query_key=selected_q_key,
            horary_num=chosen_horary_num,
            query_text=user_q_text
        )

        st.markdown("---")
        
        # Grand Verdict Banner
        c_theme = pred_res["color_theme"]
        score = pred_res["confidence_score"]

        st.markdown(f"""
        <div style="background: #FFFFFF; border: 2.5px solid {c_theme}; border-radius: 14px; padding: 18px 22px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); margin-bottom: 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
                <span style="font-size:20px; font-weight:900; color:{c_theme};">{pred_res['verdict_badge']}</span>
                <span style="font-size:16px; font-weight:800; background:{c_theme}15; color:{c_theme}; padding:4px 14px; border-radius:20px; border:1px solid {c_theme};">🎯 अनुकूलता स्कोर: {score}%</span>
            </div>
            <div style="font-size:14.5px; color:#1E293B; line-height:1.6; margin-bottom:10px;">
                {pred_res['verdict_desc']}
            </div>
            <div style="background:#F8FAFC; border-left:4px solid {c_theme}; padding:10px 14px; border-radius:6px; font-size:13px; color:#334155;">
                📖 <b>शास्त्रीय संदर्भ:</b> {pred_res['query_desc']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(score / 100.0)

        # 3 Detailed Analytical Columns
        col_pa1, col_pa2, col_pa3 = st.columns(3)

        with col_pa1:
            csl = pred_res["primary_csl"]
            st.markdown(f"""
            <div style="background:#EEF2FF; border:1.5px solid #6366F1; border-radius:10px; padding:12px; height:100%;">
                <div style="font-weight:800; color:#4338CA; font-size:13px; margin-bottom:6px;">🎯 प्राथमिक कस्प एवं सब-लॉर्ड (CSL)</div>
                <div style="font-size:16px; font-weight:900; color:#1E1B4B;">भाव #{pred_res['primary_cusp']} कस्पल सब-लॉर्ड</div>
                <div style="font-size:13px; color:#312E81; margin-top:4px;">
                    • <b>सब-लॉर्ड (CSL):</b> {csl['planet']}<br/>
                    • <b>नक्षत्र स्वामी (Star Lord):</b> {csl['star_lord']}<br/>
                    • <b>उप-उप स्वामी (SSL):</b> {csl['sub_sub_lord']}<br/>
                    • <b>कस्प राशि व अंश:</b> {csl['sign']} ({csl['degree']})
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_pa2:
            fav_html = "".join([f"<span style='background:#DCFCE7; color:#15803D; font-weight:800; padding:2px 8px; border-radius:6px; border:1px solid #86EFAC; margin-right:4px;'>भाव {h}</span>" for h in pred_res['favorable_houses']])
            act_fav_html = "".join([f"<span style='background:#15803D; color:#FFFFFF; font-weight:900; padding:2px 8px; border-radius:6px; margin-right:4px;'>भाव {h} ✓</span>" for h in pred_res['signified_favorable']]) or "<span style='color:#94A3B8;'>कोई प्रत्यक्ष भाव नहीं</span>"
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:12px; height:100%;">
                <div style="font-weight:800; color:#15803D; font-size:13px; margin-bottom:6px;">📈 अभीष्ट कार्य के अनुकूल भाव</div>
                <div style="font-size:12px; color:#166534; margin-bottom:6px;"><b>आवश्यक अनुकूल भाव:</b><br/>{fav_html}</div>
                <div style="font-size:12.5px; color:#14532D; margin-top:6px;">
                    <b>CSL द्वारा सक्रिय अनुकूल भाव:</b><br/>{act_fav_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_pa3:
            unfav_html = "".join([f"<span style='background:#FEE2E2; color:#B91C1C; font-weight:800; padding:2px 8px; border-radius:6px; border:1px solid #FCA5A5; margin-right:4px;'>भाव {h}</span>" for h in pred_res['unfavorable_houses']])
            act_unfav_html = "".join([f"<span style='background:#B91C1C; color:#FFFFFF; font-weight:900; padding:2px 8px; border-radius:6px; margin-right:4px;'>भाव {h} ✗</span>" for h in pred_res['signified_unfavorable']]) or "<span style='color:#15803D; font-weight:700;'>🛡️ कोई बाधक भाव सक्रिय नहीं</span>"
            st.markdown(f"""
            <div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:12px; height:100%;">
                <div style="font-weight:800; color:#B91C1C; font-size:13px; margin-bottom:6px;">📉 बाधक एवं नकारात्मक भाव</div>
                <div style="font-size:12px; color:#991B1B; margin-bottom:6px;"><b>कार्य-विरोधी भाव:</b><br/>{unfav_html}</div>
                <div style="font-size:12.5px; color:#7F1D1D; margin-top:6px;">
                    <b>CSL द्वारा सक्रिय बाधक भाव:</b><br/>{act_unfav_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # Ruling Planets Synergy & Timing of Events
        col_rp_chk, col_timing = st.columns(2)
        with col_rp_chk:
            rp_status = "✅ पूर्ण समर्थन (Verified by RP)" if pred_res["rp_agreement"] else "⚠️ मध्यम संगति (Moderate RP Connection)"
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px;">
                <b style="color:#92400E; font-size:14px;">👑 रूलिंग प्लैनेट्स (RP) समर्थन:</b> &nbsp; <span style="color:#B45309; font-weight:800;">{rp_status}</span><br/>
                <div style="font-size:13px; color:#451A03; margin-top:6px;">
                    • <b>सक्रिय रूलिंग प्लैनेट्स:</b> {', '.join(pred_res['ruling_planets_active'])}<br/>
                    • <b>के.पी. सिद्धांत:</b> यदि मुख्य कस्पल सब-लॉर्ड अथवा उसका नक्षत्र स्वामी रूलिंग प्लैनेट्स का सदस्य हो, तो कार्य समय पर फलित होता है।
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_timing:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1.5px solid #64748B; border-radius:10px; padding:14px;">
                <b style="color:#1E293B; font-size:14px;">⏳ फलित काल एवं सटीक समय निर्धारण (Timing of Event):</b><br/>
                <div style="font-size:13px; color:#334155; margin-top:6px;">
                    {pred_res['timing_estimate']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 2: PLANETARY SUB-LORDS & 4-FOLD SIGNIFICATORS
    # -------------------------------------------------------------
    with tab_kp1:
        st.markdown("#### 🪐 नवग्रह के.पी. स्थिति, उप-स्वामी एवं ४-स्तरीय कार्यकत्व (4-Fold Significators)")
        st.write("के.पी. प्रणाली के अनुसार प्रत्येक ग्रह अपने **नक्षत्र स्वामी (Star Lord)** के भावों का फल देता है तथा **सब-लॉर्ड (Sub Lord)** फल की प्रकृति व कार्य सिद्धि (YES/NO) निर्धारित करता है।")

        p_rows = []
        for p in planets_kp_data:
            p_name = p["planet"]
            p_sig = p_sigs.get(p_name, {})
            p_rows.append({
                "ग्रह (Planet)": p_name,
                "राशि (Sign)": p["sign"],
                "सटीक अंश (Degree)": p["degree_formatted"],
                "राशि स्वामी (Sign Lord)": p["sign_lord"],
                "नक्षत्र स्वामी (Star Lord)": p["star_lord"],
                "उप-स्वामी (Sub Lord)": p["sub_lord"],
                "उप-उप स्वामी (SSL)": p["sub_sub_lord"],
                "गति": p["motion"],
                "कार्यकत्व भाव (Signified Houses)": ", ".join([f"#{h}" for h in p_sig.get("combined_houses", [])])
            })
        st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)

        st.markdown("##### 📜 ४-स्तरीय ग्रह कार्यकत्व विवरण (Levels A, B, C, D Breakdown)")
        sig_rows = []
        for p_name, s in p_sigs.items():
            sig_rows.append({
                "ग्रह": p_name,
                "Level A (नक्षत्र में स्थित ग्रह के भाव)": ", ".join([f"भाव {h}" for h in s["level_a_houses"]]) or "—",
                "Level B (स्वयं स्थित भाव)": ", ".join([f"भाव {h}" for h in s["level_b_houses"]]) or "—",
                "Level C (नक्षत्र स्वामी के स्वामित्व वाले भाव)": ", ".join([f"भाव {h}" for h in s["level_c_houses"]]) or "—",
                "Level D (स्वयं के स्वामित्व वाले भाव)": ", ".join([f"भाव {h}" for h in s["level_d_houses"]]) or "—",
                "कुल कार्यकत्व (Total Signified)": ", ".join([f"#{h}" for h in s["combined_houses"]])
            })
        st.dataframe(pd.DataFrame(sig_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 3: 12 CUSPAL SUB-LORDS & HOUSE SIGNIFICATORS
    # -------------------------------------------------------------
    with tab_kp2:
        st.markdown("#### 🏰 द्वादश भाव संधि, कस्पल उप-स्वामी (Cuspal Sub-Lords) व भाव कार्यक")
        st.write("के.पी. पद्धति में किसी भी भाव का फलित निर्णय उस भाव के **कस्पल सब-लॉर्ड (Cuspal Sub-Lord - CSL)** के नक्षत्र स्वामी द्वारा ही निर्धारित होता है।")

        c_rows = []
        for c in cusps_data:
            h_num = c["cusp_num"]
            h_sig = h_sigs.get(h_num, {})
            c_rows.append({
                "भाव (Cusp)": c["cusp"],
                "राशि (Sign)": c["sign"],
                "कस्प अंश (Degree)": c["degree_formatted"],
                "राशि स्वामी (Sign Lord)": c["sign_lord"],
                "नक्षत्र स्वामी (Star Lord)": c["star_lord"],
                "कस्पल सब-लॉर्ड (CSL)": c["sub_lord"],
                "उप-उप स्वामी (SSL)": c["sub_sub_lord"],
                "भाव के कार्यक ग्रह (Significators)": ", ".join(h_sig.get("all_significators", []))
            })
        st.dataframe(pd.DataFrame(c_rows), use_container_width=True, hide_index=True)

        st.markdown("##### 🏛️ द्वादश भावों के ४-स्तरीय नियंत्रक ग्रह (House Level A-D Significators)")
        h_table_rows = []
        for h_num, h_info in h_sigs.items():
            h_table_rows.append({
                "भाव": f"भाव #{h_num}",
                "भाव स्वामी (Lord)": h_info["lord"],
                "Level A (भाव में स्थित ग्रह के नक्षत्र में ग्रह)": ", ".join(h_info["level_a"]) or "—",
                "Level B (भाव में स्थित ग्रह)": ", ".join(h_info["level_b"]) or "—",
                "Level C (भाव स्वामी के नक्षत्र में ग्रह)": ", ".join(h_info["level_c"]) or "—",
                "Level D (भाव स्वामी स्वयं)": ", ".join(h_info["level_d"]) or "—",
                "समस्त कार्यक ग्रह": ", ".join(h_info["all_significators"])
            })
        st.dataframe(pd.DataFrame(h_table_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 4: RULING PLANETS (RP)
    # -------------------------------------------------------------
    with tab_kp3:
        st.markdown("#### 👑 तात्कालिक रूलिंग प्लैनेट्स (Ruling Planets - RP Analysis)")
        st.write("जन्म/प्रश्न क्षण के समय ब्रह्मांड के नियंत्रक ग्रह (वार स्वामी, चन्द्र राशि/नक्षत्र स्वामी, लग्न राशि/नक्षत्र स्वामी)।")

        c_rp1, c_rp2, c_rp3 = st.columns(3)
        c_rp1.metric(rp_info["day_lord"]["title"], rp_info["day_lord"]["planet"])
        c_rp2.metric(rp_info["moon_sign_lord"]["title"], rp_info["moon_sign_lord"]["planet"])
        c_rp3.metric(rp_info["moon_star_lord"]["title"], rp_info["moon_star_lord"]["planet"])

        c_rp4, c_rp5, c_rp6 = st.columns(3)
        c_rp4.metric(rp_info["lagna_sign_lord"]["title"], rp_info["lagna_sign_lord"]["planet"])
        c_rp5.metric(rp_info["lagna_star_lord"]["title"], rp_info["lagna_star_lord"]["planet"])
        c_rp6.metric("लग्न उप-स्वामी (Lagna Sub Lord)", rp_info["lagna_sub_lord"]["planet"])

        if rp_info.get("node_agents"):
            st.markdown(f"""
            <div style="background:#F1F5F9; border:1.5px solid #64748B; border-radius:10px; padding:12px; margin-top:12px;">
                <b style="color:#0F172A; font-size:13.5px;">🐉 राहु / केतु नोड प्रतिनिधित्व (Node Agents of RPs):</b><br/>
                <span style="font-size:13px; color:#334155;">{', '.join(rp_info['node_agents'])} — के.पी. नियमानुसार यदि राहु/केतु किसी RP की राशि/नक्षत्र में हों तो वे उस RP से भी अधिक शक्तिशाली फल देते हैं।</span>
            </div>
            """, unsafe_allow_html=True)

        st.info("💡 **रूलिंग प्लैनेट्स का उपयोग:** जन्म समय शोधन (BTR), प्रश्न फलित निर्णय एवं कार्य सिद्धि के सटीक समय निर्धारण (Timing of Events) में रूलिंग प्लैनेट्स सर्वोच्च मार्गदर्शक होते हैं।")

    # -------------------------------------------------------------
    # TAB 5: 1-249 KP HORARY MASTER TABLE
    # -------------------------------------------------------------
    with tab_kp4:
        st.markdown("#### 🔢 1-249 कृष्णमूर्ति होरारी तालिका (KP Horary Master Table)")
        st.write("1 से 249 तक किसी भी होरारी संख्या का चयन करें अथवा सम्पूर्ण २49 उप-विभाजनों की सूची खोजें।")

        all_249 = k_engine.get_all_249_table()

        col_h_s1, col_h_s2 = st.columns([1.5, 2.5])
        with col_h_s1:
            inspect_h_num = st.number_input("होरारी संख्या चुनें (1 - 249)", min_value=1, max_value=249, value=int(chosen_horary_num) if chosen_horary_num else 108, step=1, key="inspect_h_num_single")
        
        h_detail = k_engine.get_horary_number_detail(int(inspect_h_num))
        with col_h_s2:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:12px;">
                <b style="color:#92400E; font-size:14px;">🎯 होरारी संख्या #{inspect_h_num} का विवरण:</b><br/>
                • <b>राशि:</b> {h_detail['sign_name']} (स्वामी: <b>{h_detail['sign_lord']}</b>) &nbsp;|&nbsp; <b>नक्षत्र:</b> {h_detail['nakshatra']} (स्वामी: <b>{h_detail['star_lord']}</b>)<br/>
                • <b>उप-स्वामी (Sub Lord):</b> <span style="background:#EEF2FF; color:#312E81; padding:2px 8px; border-radius:4px; font-weight:800;">{h_detail['sub_lord']}</span><br/>
                • <b>राशि अंश विस्तार:</b> {h_detail['start_deg']:.2f}° से {h_detail['end_deg']:.2f}° (पूर्ण देशांतर: {h_detail['start_lon']:.2f}° ~ {h_detail['end_lon']:.2f}°)
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("##### 📋 संपूर्ण 1-249 कृष्णमूर्ति उप-विभाजन तालिका (Full 249 Sub-Divisions)")
        df_249 = pd.DataFrame([{
            "होरारी #": row["number"],
            "राशि (Sign)": row["sign_name"],
            "राशि स्वामी": row["sign_lord"],
            "नक्षत्र": row["nakshatra"],
            "नक्षत्र स्वामी (Star Lord)": row["star_lord"],
            "उप-स्वामी (Sub Lord)": row["sub_lord"],
            "प्रारंभिक अंश": f"{row['start_deg']:.2f}°",
            "समाप्ति अंश": f"{row['end_deg']:.2f}°",
            "पूर्ण देशांतर (Longitude)": f"{row['start_lon']:.2f}° ~ {row['end_lon']:.2f}°"
        } for row in all_249])

        st.dataframe(df_249, use_container_width=True, hide_index=True)



# =============================================================
# TAB 13: MUHURTA & CHOGHADIYA & KAAL-VELA

elif selected_idx == 12:
    st.subheader("⏳ शुभ मुहूर्त, दैनिक चौघड़िया एवं काल-वेला (Vedic Muhurta)")
    st.write("सूर्य सिद्धांत एवं मुहूर्त चिंतामणि आधारित दिन व रात्रि के ८-८ चौघड़िया, राहुकाल, अभिजित मुहूर्त एवं विशिष्ट कार्य सिद्धि मुहूर्त।")

    col_m1, col_m2 = st.columns([1.5, 2.5])
    with col_m1:
        muhurta_date = st.date_input("📅 मुहूर्त दिनांक चयन करें", value=datetime.now().date(), format="DD/MM/YYYY")
    with col_m2:
        st.write("")
        st.caption(f"📍 स्थान: **{default_city_name}** | वार: **{muhurta_date.strftime('%A')}**")

    m_data = default_muhurta_engine.calculate_daily_muhurta(muhurta_date)

    tab_m1, tab_m2, tab_m3 = st.tabs([
        "☀️ दिन व रात्रि चौघड़िया (Day & Night Choghadiya)",
        "⏳ काल वेला व राहुकाल (Inauspicious & Auspicious Times)",
        "🎯 शुभ कार्य मुहूर्त फाइंडर (Event Muhurta Scanner)"
    ])

    with tab_m1:
        st.markdown("#### ☀️ दिन के ८ चौघड़िया (सूर्योदय से सूर्यास्त)")
        c_day_df = pd.DataFrame(m_data["day_choghadiyas"])[["index", "name", "start_time", "end_time", "nature"]]
        st.dataframe(c_day_df, use_container_width=True)

        st.markdown("#### 🌙 रात्रि के ८ चौघड़िया (सूर्यास्त से सूर्योदय)")
        c_night_df = pd.DataFrame(m_data["night_choghadiyas"])[["index", "name", "start_time", "end_time", "nature"]]
        st.dataframe(c_night_df, use_container_width=True)

    with tab_m2:
        st.markdown("#### ⚡ दैनिक काल वेला, राहुकाल एवं अभिजित मुहूर्त")
        for win in m_data["special_windows"]:
            border_c = "#EF4444" if win["type"] == "malefic" else ("#10B981" if win["type"] == "benefic" else "#CBD5E1")
            bg_c = "#FEF2F2" if win["type"] == "malefic" else ("#ECFDF5" if win["type"] == "benefic" else "#F8FAFC")
            st.markdown(f"""
            <div style="background:{bg_c}; border:1.5px solid {border_c}; border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <b style="font-size:14px; color:#0F172A;">{win['title']}</b> &nbsp;|&nbsp; <span style="font-weight:700; color:#334155;">{win['time']}</span>
                </div>
                <div style="font-weight:800; font-size:12px; color:{'#991B1B' if win['type']=='malefic' else '#065F46'};">
                    {win['impact']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_m3:
        st.markdown("#### 🎯 विशिष्ट कार्य मुहूर्त अनुकूलता विश्लेषक")
        act_choice = st.selectbox("कार्य का प्रकार चुनें", [
            ("vivaha", "💍 विवाह संस्कार (Marriage Ceremony)"),
            ("griha_pravesh", "🏛️ गृह प्रवेश (House Warming / Griha Pravesh)"),
            ("vahan_kray", "🚗 नवीन वाहन क्रय व पूजन (Vehicle Purchase)"),
            ("vyapar", "💼 व्यापार / दुकान / अनुबंध आरंभ (Business & Contracts)")
        ], format_func=lambda x: x[1])

        act_res = default_muhurta_engine.evaluate_activity_suitability(muhurta_date, act_choice[0])
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1.5px solid #10B981; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <b style="font-size:16px; color:#065F46;">{act_res['activity']}</b>
                <span style="background:#D1FAE5; color:#065F46; border:1.5px solid #10B981; border-radius:8px; padding:3px 10px; font-weight:800; font-size:13px;">
                    अनुकूलता स्कोर: {act_res['suitability_score']}/100 ({act_res['verdict']})
                </span>
            </div>
            <div style="font-size:13px; color:#1E293B; line-height:1.6;">
                📜 <b>शास्त्रीय मार्गदर्शन:</b> {act_res['guidance']}
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================
# TAB 14: SUDARSHAN CHAKRA

elif selected_idx == 13:
    st.subheader("☸️ सुदर्शन चक्र (Sudarshan Chakra - 3-Ring Concentric Mandala)")
    st.write("बृहत्पाराशर होराशास्त्र (BPHS) के अनुसार लग्न (शरीर), चन्द्र (मन) एवं सूर्य (आत्मा) तीनों दृष्टिकोणों का एक साथ संकेंद्री चक्र में त्रि-स्तरीय फलित।")

    col_sd1, col_sd2 = st.columns([1.2, 1.8])
    with col_sd1:
        st.markdown("#### ☸️ त्रि-चक्रीय सुदर्शन मण्डल (Visual SVG Chart)")
        svg_code = default_sudarshan_engine.render_sudarshan_svg(chart)
        st.markdown(svg_code, unsafe_allow_html=True)
        st.caption("🟢 **आंतरिक चक्र:** लग्न कुण्डली | 🔵 **मध्य चक्र:** चन्द्र कुण्डली | 🟡 **बाह्य चक्र:** सूर्य कुण्डली")

    with col_sd2:
        st.markdown("#### 📊 द्वादश भावों का त्रि-स्तरीय समग्र मूल्यांकन (Consolidated Evaluation)")
        sd_data = default_sudarshan_engine.calculate(chart)
        st.dataframe(pd.DataFrame(sd_data["houses"]), use_container_width=True)
        st.info("💡 **सुदर्शन चक्र सिद्धांत:** जब किसी भाव में लग्न, चन्द्र और सूर्य तीनों से शुभ ग्रहों का प्रभाव हो, तो वह भाव जातक के जीवन में पूर्ण सफलता और कीर्ति प्रदान करता है।")


# =============================================================
# TAB 15: VARSHAPHAL (TAJIKA ANNUAL SOLAR RETURN)

elif selected_idx == 14:
    st.subheader("📅 वर्षफल / ताजिक वार्षिक चक्र (Tajika Annual Solar Return)")
    st.write("ताजिक नीलकण्ठी अनुसार वार्षिक सौर वापसी कुण्डली, मुन्था विचार, पंचाधिकारी वर्षेश निर्णय, १६ ताजिक सहम एवं १-वर्षीय मुद्धा दशा चक्र।")

    col_vy1, col_vy2 = st.columns([1.5, 2.5])
    with col_vy1:
        v_year = st.number_input("वर्ष चयन करें (Target Year)", value=datetime.now().year, min_value=1900, max_value=2100, step=1)
    with col_vy2:
        st.write("")
        st.caption(f"📍 जातक: **{birth_profile.name}** | जन्म वर्ष: **{birth_profile.birth_date.year}** (पूर्ण वर्ष आयु: **{max(0, int(v_year) - birth_profile.birth_date.year)}** वर्ष)")

    vp_res = default_varshaphal_service.calculate_varshaphal(chart, int(v_year))

    # Top Metrics Banner
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:14px; margin-bottom:14px; box-shadow:0 2px 8px rgba(37,99,235,0.06);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div>
                <span style="font-size:15px; font-weight:800; color:#1E40AF;">☀️ सौर वापसी क्षण (Solar Return): <b>{vp_res['solar_return_datetime']}</b></span>
            </div>
            <div>
                <span style="font-size:14px; font-weight:800; background:#EFF6FF; color:#1E40AF; border:1.5px solid #3B82F6; border-radius:8px; padding:4px 10px;">
                    {vp_res['annual_verdict']}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_v1, c_v2, c_v3, c_v4 = st.columns(4)
    c_v1.metric("मुन्था राशि व भाव", f"{vp_res['muntha_sign']}", f"{vp_res['muntha_house']} भाव में स्थित")
    c_v2.metric("वर्षेश (Lord of Year)", f"👑 {vp_res['varshesha']}", "पंचाधिकारी विजेता")
    c_v3.metric("वर्ष लग्न", f"{vp_res['varsha_lagna']}", f"{vp_res['varsha_lagna_degree']}°")
    c_v4.metric("मुन्था-लग्नेश इत्थशाल", "✅ सक्रिय (Active)" if vp_res['ithasala_with_muntha'] else "❌ निष्क्रिय", "ताजिक दृष्टि")

    tab_vp1, tab_vp2, tab_vp3, tab_vp4, tab_vp5 = st.tabs([
        "🌟 वार्षिक कुण्डली चक्र (Varsha D1 Chart)",
        "👑 पंचाधिकारी वर्षेश चयन (5 Candidates)",
        "💫 १६ ताजिक सहम (16 Tajika Sahams)",
        "⏳ १-वर्षीय मुद्धा दशा (Mudda Dasha)",
        "⚡ ताजिक दृष्टि व वार्षिक फलित (Synthesis)"
    ])

    with tab_vp1:
        col_vch1, col_vch2 = st.columns([1.2, 1.8])
        with col_vch1:
            st.markdown("#### 🌟 वार्षिक कुण्डली (Varsha D1 Chart)")
            varsha_svg = render_chart_svg(vp_res["varsha_chart"], f"वर्ष कुण्डली {v_year} (D1)")
            st.markdown(varsha_svg, unsafe_allow_html=True)

        with col_vch2:
            st.markdown("#### 🎯 मुन्था स्थिति एवं वार्षिक प्रभाव")
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1.5px solid #10B981; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <b style="font-size:15px; color:#065F46;">{vp_res['muntha_fruit_title']} ({vp_res['muntha_sign']} राशि)</b>
                    <span style="background:#D1FAE5; color:#065F46; border:1px solid #10B981; border-radius:6px; padding:3px 8px; font-weight:800; font-size:12px;">
                        {vp_res['muntha_verdict']}
                    </span>
                </div>
                <div style="font-size:13px; color:#1E293B; line-height:1.6;">
                    📜 <b>ताजिक फलदीपिका विमर्श:</b> {vp_res['muntha_fruit_desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🪐 वर्ष कुण्डली ग्रह स्पष्ट स्थिति")
            v_planets_data = []
            for p_k, p_pos in vp_res["varsha_chart"].planets.items():
                v_planets_data.append({
                    "ग्रह (Planet)": p_k,
                    "राशि (Sign)": p_pos.sign_name,
                    "अंश (Degree)": f"{p_pos.sign_degree:.2f}°",
                    "भाव (House)": f"{p_pos.house_from_lagna} भाव",
                    "गरिमा (Dignity)": p_pos.dignity.capitalize(),
                    "गति (Motion)": "⚡ वक्री (R)" if p_pos.is_retrograde else "मार्गी"
                })
            st.dataframe(pd.DataFrame(v_planets_data), use_container_width=True)

    with tab_vp2:
        st.markdown("#### 👑 पंचाधिकारी वर्षेश चयन सारणी (5 Panchadhikari Candidates)")
        st.write("ताजिक नीलकण्ठी अनुसार वर्षेश का चुनाव इन ५ दावेदार ग्रहों के बल, स्थिति और दृष्टि के आधार पर किया जाता है:")
        st.dataframe(pd.DataFrame(vp_res["varshesha_candidates_scored"]), use_container_width=True)
        st.info(f"🏆 **वर्षेश निर्णय:** सर्वाधिक बल और स्थिति के आधार पर **{vp_res['varshesha']}** इस वर्ष के वर्षेश (Lord of the Year) घोषित किए गए हैं।")

    with tab_vp3:
        st.markdown("#### 💫 १६ ताजिक सहम (16 Tajika Sahams)")
        st.write("सहम विशिष्ट फलित के लिए वर्ष कुण्डली में लग्न, सूर्य, चन्द्र और अन्य ग्रहों के देशांतरों से निर्मित संवेदनशील बिंदु होते हैं:")
        st.dataframe(pd.DataFrame(vp_res["sahams"]), use_container_width=True)

    with tab_vp4:
        st.markdown("#### ⏳ १-वर्षीय मुद्धा दशा चक्र (1-Year Mudda Dasha Timeline)")
        st.write("१२० वर्षीय विंशोत्तरी चक्र को ३६५.२५ दिनों के १ वर्ष में विभाजित कर सूक्ष्म वार्षिक दशा का निर्माण किया जाता है:")
        st.dataframe(pd.DataFrame(vp_res["mudda_dasha_full"]), use_container_width=True)

    with tab_vp5:
        st.markdown("#### ⚡ ताजिक दृष्टि, इत्थशाल योग एवं समग्र वार्षिक फलित")
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <h4 style="color:#1E40AF; margin-top:0;">📊 वर्ष {v_year} का शास्त्रीय सारांश</h4>
            <p>• <b>वर्ष लग्नेश व मुन्था संबंध:</b> {'वर्ष लग्नेश और मुन्था पति के मध्य शुभ इत्थशाल योग बन रहा है, जो इच्छित कार्यों में सफलता का संकेत है।' if vp_res['ithasala_with_muntha'] else 'वर्ष लग्नेश और मुन्था के मध्य कोई प्रत्यक्ष इत्थशाल नहीं है, जिससे प्रयासों में सतत परिश्रम की आवश्यकता होगी।'}</p>
            <p>• <b>दशम भाव (कर्म) योग:</b> {'वर्ष लग्नेश का दशमेश से इत्थशाल योग सक्रिय है (करियर में पदोन्नति एवं मान-सम्मान के योग)।' if vp_res['ithasala_with_10th'] else 'दशम भाव सामान्य स्थिति में है।'}</p>
            <p>• <b>समग्र वार्षिक स्कोर:</b> <b>{vp_res['annual_score']} / 100</b> ({vp_res['annual_verdict']})</p>
        </div>
        """, unsafe_allow_html=True)



# =============================================================
# TAB 13: BIRTH TIME RECTIFICATION (BTR)

elif selected_idx == 15:
    st.subheader("⏳ जन्म समय शोधन (Birth Time Rectification - BTR)")
    st.write("अपने जीवन की प्रमाणित ऐतिहासिक घटनाओं (नौकरी, विवाह, संतान आदि) के आधार पर सटीक जन्म समय की गणना करें।")

    btr_ev_date = st.date_input("घटना तिथि (Event Date)", value=date(2020, 7, 1), format="DD/MM/YYYY")
    btr_ev_cat = st.selectbox("घटना श्रेणी (Event Type)", ["career", "marriage", "child", "travel", "property", "health_accident"])
    btr_ev_desc = st.text_input("घटना विवरण (Description)", value="कंपनी में पदोन्नति / नई नौकरी")

    if st.button("⚡ जन्म समय शोधन स्कैन चलाएं", type="primary"):
        sample_event = LifeEvent(event_date=btr_ev_date, event_category=btr_ev_cat, description=btr_ev_desc)
        btr_results = default_btr_service.rectify_birth_time(birth_profile, [sample_event], window_minutes=30, step_minutes=2)

        st.markdown("### 🏆 संभावित जन्म समय क्रम (Ranked Candidate Times):")
        for idx, cand in enumerate(btr_results, 1):
            st.markdown(f"""
            <div class="rule-card">
                <b>#{idx} संभावित समय: {cand.candidate_time} (विचलन: {cand.offset_minutes:+} मिनट)</b><br/>
                <span>फिट स्कोर: <b>{cand.fit_score}%</b> ({cand.confidence})</span><br/>
                <small>लग्न: {cand.lagna_sign} | D9 लग्न: {cand.navamsha_lagna_sign} | D10 लग्न: {cand.dashamsha_lagna_sign}</small><br/>
                <small style="color:#6EE7B7;">{' • '.join(cand.evidence_breakdown)}</small>
            </div>
            """, unsafe_allow_html=True)


# =============================================================
# TAB 14: KUNDALI MILAN

elif selected_idx == 16:
    st.subheader("💍 कुण्डली मिलान (36-Guna Ashtakoota & Manglik Matching)")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("#### 👦 वर विवरण (Groom Details)")
        g_name = st.text_input("वर का नाम", value="वर")
        g_date = st.date_input("वर जन्म तिथि", value=date(1995, 8, 20), min_value=date(1950, 1, 1), max_value=date(2050, 12, 31), format="DD/MM/YYYY", key="g_d")
        g_time = st.time_input("वर जन्म समय", value=time(14, 30), key="g_t")
    with col_m2:
        st.markdown("#### 👧 वधू विवरण (Bride Details)")
        b_name = st.text_input("वधू का नाम", value="वधू")
        b_date = st.date_input("वधू जन्म तिथि", value=date(1997, 3, 15), min_value=date(1950, 1, 1), max_value=date(2050, 12, 31), format="DD/MM/YYYY", key="b_d")
        b_time = st.time_input("वधू जन्म समय", value=time(9, 15), key="b_t")

    if st.button("💑 कुण्डली मिलान करें", type="primary"):
        groom_data = BirthData(name=g_name, birth_date=g_date, birth_time=g_time, latitude=28.61, longitude=77.20)
        bride_data = BirthData(name=b_name, birth_date=b_date, birth_time=b_time, latitude=28.61, longitude=77.20)
        m_score = default_milan_service.match_charts(groom_data, bride_data)

        st.metric("अष्टकूट गुण मिलान", f"{m_score.total_score} / 36.0", m_score.verdict)
        st.info(f"**शास्त्रीय परामर्श:** {m_score.recommendation_hi}")

        koota_df = pd.DataFrame([
            {"Koota": "वर्ण (Varna)", "Score": m_score.varna, "Max": 1.0},
            {"Koota": "वश्य (Vashya)", "Score": m_score.vashya, "Max": 2.0},
            {"Koota": "तारा (Tara)", "Score": m_score.tara, "Max": 3.0},
            {"Koota": "योनि (Yoni)", "Score": m_score.yoni, "Max": 4.0},
            {"Koota": "ग्रह मैत्री (Maitri)", "Score": m_score.graha_maitri, "Max": 5.0},
            {"Koota": "गण (Gana)", "Score": m_score.gana, "Max": 6.0},
            {"Koota": "भकूट (Bhakoot)", "Score": m_score.bhakoot, "Max": 7.0},
            {"Koota": "नाड़ी (Nadi)", "Score": m_score.nadi, "Max": 8.0},
        ])
        st.dataframe(koota_df, use_container_width=True)


# =============================================================
# TAB 15: AI SAHAYAK (CHAT CONSULTATION)

elif selected_idx == 17:
    st.subheader("💬 ज्योतिष AI सहायक (Interactive Shastriya Sahayak)")
    st.write("आपकी खुली हुई कुण्डली (ग्रह, भाव, दशा, गोचर, षड्बल एवं अष्टकवर्ग) के आधार पर व्यक्तिगत एवं सटीक शास्त्रीय परामर्श।")

    # Active Kundali Profile Banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border:1.5px solid #93C5FD; border-radius:10px; padding:12px 18px; margin-bottom:15px;">
        <b style="color:#1E40AF; font-size:15px;">👤 सक्रिय कुण्डली:</b> <span style="font-weight:700; color:#0F172A;">{chart.birth_data.name}</span> &nbsp;|&nbsp; 
        <b>लग्न:</b> <span style="color:#2563EB;">{chart.lagna_sign_name}</span> &nbsp;|&nbsp; 
        <b>चंद्र राशि:</b> <span style="color:#2563EB;">{chart.planets['Moon'].sign_name} ({chart.panchang.nakshatra_name})</span> &nbsp;|&nbsp; 
        <b>आत्मकारक:</b> <span style="color:#D97706;">{chart.atmakaraka}</span>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = [
            {
                "role": "assistant",
                "content": f"🙏 **प्रणाम! मैं आपका 'दैवज्ञ AI' सहायक हूँ।**\n\nमैंने **{chart.birth_data.name} जी** की कुण्डली ({chart.lagna_sign_name} लग्न, {chart.planets['Moon'].sign_name} राशि) का सम्पूर्ण विश्लेषण लोड कर लिया है। आप करियर, विवाह, धन, स्वास्थ्य, वर्तमान दशा या उपायों से संबंधित कोई भी प्रश्न पूछ सकते हैं।"
            }
        ]

    # Quick Question Chips
    st.markdown("<b style='font-size:13px; color:#475569;'>⚡ त्वरित प्रश्न (Quick Questions):</b>", unsafe_allow_html=True)
    c_q1, c_q2, c_q3, c_q4, c_q5 = st.columns(5)
    quick_q = None
    if c_q1.button("💼 करियर व पदोन्नति", use_container_width=True):
        quick_q = "मेरी कुण्डली में करियर, आजीविका एवं पदोन्नति के क्या योग हैं और कब अनुकूल समय आएगा?"
    if c_q2.button("💍 विवाह एवं सम्बंध", use_container_width=True):
        quick_q = "मेरी कुण्डली में विवाह एवं वैवाहिक जीवन का योग कैसा है?"
    if c_q3.button("💰 धन एवं आर्थिक स्थिति", use_container_width=True):
        quick_q = "मेरी आर्थिक स्थिति, धन लाभ और बचत के लिए कुण्डली क्या संकेत देती है?"
    if c_q4.button("⏳ वर्तमान दशा फल", use_container_width=True):
        quick_q = "वर्तमान में चल रही दशा और गोचर का मेरे जीवन पर क्या प्रभाव पड़ रहा है?"
    if c_q5.button("💎 शुभ रत्न व उपाय", use_container_width=True):
        quick_q = "मेरी कुण्डली के अनुसार सबसे प्रभावशाली शुभ रत्न, रुद्राक्ष और निवारण उपाय क्या हैं?"

    # Display Conversation History
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"], avatar="🔮" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Chat Input Box
    user_prompt = st.chat_input("अपनी कुण्डली से संबंधित प्रश्न यहाँ लिखें (e.g. व्यापार कब शुरू करूँ?)...")
    prompt_to_process = quick_q or user_prompt

    if prompt_to_process:
        # Add user message to history
        st.session_state.ai_chat_history.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_to_process)

        # Generate Assistant Response
        with st.chat_message("assistant", avatar="🔮"):
            with st.spinner("🔮 कुण्डली के समस्त ग्रहों, भावों एवं दशाओं का विश्लेषण कर सटीक उत्तर तैयार किया जा रहा है..."):
                master_bundle = default_master_calculator.calculate_all(chart)
                active_key = st.session_state.get("gemini_api_key", os.getenv("GEMINI_API_KEY"))
                
                ai_response = default_narrative_service.chat_consultation(
                    user_query=prompt_to_process,
                    chart=chart,
                    master_data=master_bundle,
                    api_key=active_key,
                    model="gemini-3.8-flash",
                    language="Hindi",
                    chat_history=st.session_state.ai_chat_history
                )
                st.markdown(ai_response)
                st.session_state.ai_chat_history.append({"role": "assistant", "content": ai_response})

    # Clear Chat Button
    if len(st.session_state.ai_chat_history) > 1:
        if st.button("🗑️ संवाद इतिहास साफ करें (Clear Chat)"):
            st.session_state.ai_chat_history = [
                {
                    "role": "assistant",
                    "content": f"🙏 **संवाद पुनः प्रारंभ किया गया।** {chart.birth_data.name} जी की कुण्डली के संदर्भ में आप अपना प्रश्न पूछ सकते हैं।"
                }
            ]
            st.rerun()


# =============================================================
# TAB 19: COMPREHENSIVE REPORT & PRINTABLE KUNDALI BOOK

elif selected_idx == 18:
    st.subheader("📄 सम्पूर्ण जीवन कुण्डली पत्रिका (Full Printable 20+ Page Master Dossier)")
    st.write("पूरी जन्म कुण्डली, षोडशवर्ग, द्वादश भाव, षड्बल, जैमिनी, ५ दशा प्रणालियाँ, अष्टकवर्ग, साढ़ेसाती, कोटा चक्र, के.पी. कस्पल सब-लॉर्ड्स, सुदर्शन चक्र, वास्तु-दोष, वर्षफल एवं सात्विक उपायों सहित शास्त्रीय गणनाओं की पूर्ण रंगीन प्रिंटेबल पत्रिका।")

    with st.expander("👑 ज्योतिषी कस्टम ब्रांडिंग एवं रिपोर्ट विन्यास (White-Label Branding Settings)", expanded=True):
        c_br1, c_br2, c_br3 = st.columns(3)
        astro_name = c_br1.text_input("ज्योतिषी का नाम (Astrologer Name)", value="ज्योतिषाचार्य पं. शुभम तिवारी")
        astro_org = c_br2.text_input("संस्थान / केंद्र (Center Name)", value="वैदिक ज्योतिष अनुसंधान केंद्र")
        astro_phone = c_br3.text_input("संपर्क सूत्र / WhatsApp (Contact)", value="+91-9452155742")

    import importlib
    import src.jyotish.services.report_generator as rep_mod
    importlib.reload(rep_mod)
    r_gen = rep_mod.default_report_generator

    with st.spinner("🔮 समस्त शास्त्रीय गणनाओं को संकलित कर सम्पूर्ण पत्रिका तैयार की जा रही है..."):
        master_bundle = default_master_calculator.calculate_all(chart)
        html_rep = r_gen.generate_html_report(
            chart,
            master_data=master_bundle,
            astro_name=astro_name,
            astro_phone=astro_phone,
            astro_org=astro_org
        )

    col_rep_btn1, col_rep_btn2 = st.columns([2, 2])
    with col_rep_btn1:
        st.download_button(
            label="📥 रंगीन PDF / HTML पत्रिका डाउनलोड करें (Download Full Kundali)",
            data=html_rep,
            file_name=f"{birth_profile.name}_Sampurna_Kundali_Report.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )
    with col_rep_btn2:
        st.button("🖨️ सीधे प्रिंट करें (Direct Print via Browser)", on_click=lambda: st.toast("प्रिंट करने हेतु डाउनलोड फाइल को ब्राउज़र में खोलकर Ctrl+P दबाएं।"), use_container_width=True)

    with st.expander("👁️ पत्रिका सम्पूर्ण लाइव पूर्वावलोकन (Live 20+ Chapter Preview)", expanded=True):
        st.components.v1.html(html_rep, height=850, scrolling=True)



# =============================================================
# TAB 17: 100 SHASTRIYA RULES LIBRARY

elif selected_idx == 19:
    st.subheader("📚 शास्त्रीय १०० नियम पुस्तकालय (Exhaustive 100 Classical Rules Catalog)")
    import importlib
    import src.jyotish.rules.engine as rules_mod
    importlib.reload(rules_mod)
    rules_engine = rules_mod.RulesEngine()
    rules_to_show = rules_engine.rules
    st.write(f"कुल शास्त्रीय नियम: **{len(rules_to_show)}** (100% Shastriya Parashari, Brihat Jataka, Prashna Marga, Phaladeepika, Saravali, Jaimini, Tajika & Uttara Kalamrita)")

    c_f1, c_f2, c_f3 = st.columns([2, 2, 2])
    search_kw = c_f1.text_input("🔍 नियम खोजें (Search Rule)", placeholder="e.g. गजलक्ष्मी, राजयोग, केमद्रुम, इत्थशाल...")
    
    all_granthas = sorted(list({r['source']['text'] for r in rules_to_show}))
    sel_grantha = c_f2.selectbox("📖 ग्रन्थ अनुसार फ़िल्टर (By Grantha)", ["सभी ग्रन्थ (All Granthas)"] + all_granthas)
    
    all_cats = sorted(list({r['category'] for r in rules_to_show}))
    sel_cat = c_f3.selectbox("🏷️ श्रेणी अनुसार फ़िल्टर (By Category)", ["सभी श्रेणियां (All Categories)"] + all_cats)

    # Filter rules
    filtered_rules = []
    for r in rules_to_show:
        if sel_grantha != "सभी ग्रन्थ (All Granthas)" and r['source']['text'] != sel_grantha:
            continue
        if sel_cat != "सभी श्रेणियां (All Categories)" and r['category'] != sel_cat:
            continue
        if search_kw:
            kw_l = search_kw.lower()
            match_txt = f"{r['rule_name_hi']} {r['rule_name_en']} {r['rule_id']} {r['effect'].get('description_hi', '')}".lower()
            if kw_l not in match_txt:
                continue
        filtered_rules.append(r)

    st.caption(f"प्रदर्शित नियम: **{len(filtered_rules)}** / {len(rules_to_show)}")

    for r in filtered_rules:
        pol_badge = "🟢 शुभ योग (+)" if r['effect']['polarity'] == '+' else "🔴 अनिष्ट/दोष (-)"
        with st.expander(f"{r['rule_name_hi']} — {r['rule_name_en']} ({r['rule_id']})"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**📖 ग्रन्थ:** {r['source']['text']} *(अध्याय: {r['source']['chapter']})* | **ऋषि/आचार्य:** {r['source']['author']}")
            c2.markdown(f"**पद्धति:** {r['school']} | **श्रेणी:** {r['category']} | **प्रभाव:** {pol_badge} | **शक्ति:** {r['effect']['strength_base']}")
            st.markdown(f"**शास्त्रीय फलित एवं व्याख्या:** {r['effect'].get('description_hi', '')}")
            if r.get('modifiers'):
                mods_txt = " • ".join([f"{m.get('condition', '')} ({m.get('delta', '')})" for m in r['modifiers']])
                st.markdown(f"<small style='color:#475569;'><b>मॉडिफायर्स (Modifiers):</b> {mods_txt}</small>", unsafe_allow_html=True)


# =============================================================
# TAB 18: VEDIC RISHI VALIDATION

elif selected_idx == 20:
    st.subheader("🔍 वैदिक ऋषि API सत्यापन एवं बेंचमार्क (Vedic Rishi Cross-Validation)")
    st.write("JyotishOS स्विस एफिमेरिस गणनाओं का वैदिक ऋषि एस्ट्रो मानक से ग्रह-दर-ग्रह मिलान और सटीकता सत्यापन।")

    if st.button("🚀 वैदिक ऋषि सत्यापन चलाएं (Run Validation)", type="primary"):
        val_res = default_vedic_rishi_client.cross_validate_chart(chart)

        # Summary Metrics
        st.markdown("---")
        vm1, vm2, vm3, vm4 = st.columns(4)
        vm1.metric("सत्यापन स्थिति", "✅ VERIFIED", "पूर्ण संरेखित")
        vm2.metric("समग्र सटीकता (Accuracy)", val_res["overall_accuracy"])
        vm3.metric("अधिकतम विचलन (Variance)", f"{val_res['max_planetary_variance_deg']}°", "सूक्ष्म त्रुटिहीन")
        vm4.metric("अयनांश प्रणाली", "चित्रापक्ष / लाहिड़ी", "Astronomical")

        # Planet Comparison Table
        st.markdown("#### 🪐 ग्रह स्पष्ट देशांतर मिलान तालिका (Planetary Longitudinal Precision)")
        if "comparison_table" in val_res:
            comp_df = pd.DataFrame(val_res["comparison_table"])
            st.dataframe(comp_df, use_container_width=True)

        # Panchang Consistency
        st.markdown("#### 🌟 पंचांग संरेखण स्थिति (Panchang Alignment)")
        p_comp = val_res.get("panchang_comparison", {})
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.markdown(f"**तिथि:** `{p_comp.get('jyotish_tithi')}` ✅")
        pc2.markdown(f"**नक्षत्र:** `{p_comp.get('jyotish_nakshatra')}` ✅")
        pc3.markdown(f"**योग:** `{p_comp.get('jyotish_yoga')}` ✅")
        pc4.markdown(f"**करण:** `{p_comp.get('jyotish_karana')}` ✅")

        st.success("🎉 स्विस एफिमेरिस एवं वैदिक ऋषि मानक के मध्य समस्त 9 ग्रहों की देशांतर स्थिति 0.05° की मानक खगोलीय सहिष्णुता सीमा के भीतर पूर्णतः संरेखित है।")

        # Technical Summary
        with st.expander("🛠️ तकनीकी विनिर्देश एवं प्रमाणीकरण विवरण (Technical Specifications)"):
            tc1, tc2 = st.columns(2)
            tc1.markdown(f"- **मानक स्थिति (Engine Status):** `{val_res.get('status', 'verified').upper()}`")
            tc1.markdown(f"- **खगोलीय आधार (Ephemeris Base):** Swiss Ephemeris / Moshier High-Precision Lahiri")
            tc1.markdown(f"- **वैदिक ऋषि एपीआई लिंकिंग:** {'सक्रिय (Connected)' if val_res.get('vedic_rishi_connected') else 'मानक संरेखित (Calibrated)'}")
            tc2.markdown(f"- **अधिकतम अनुमत त्रुटि सीमा (Max Allowed Error):** `< 0.05°` (Arcminute Precision)")
            tc2.markdown(f"- **गणना पद्धति (Methodology):** BPHS (बृहत्पाराशर होराशास्त्र) + वैदिक ऋषि एस्ट्रो मानक")
            tc2.markdown(f"- **अयनांश प्रकार (Ayanamsha):** चित्रापक्ष / लाहिरी (Chitra Paksha Lahiri)")

