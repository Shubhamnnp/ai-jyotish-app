"""
FastAPI REST API Gateway for JyotishOS.
Exposes endpoints for:
- Natal Chart Calculation (D1 to D10, Ashtakavarga, Panchang)
- Active Dasha Lookup
- Ghatna Query (Event Window Analysis)
- Prashna Kundali (Horary)
- Classical Rules Catalog
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..core.models import (
    BirthData, KundaliChart, GhatnaQueryInput, GhatnaQueryResult, ActiveDashaHierarchy
)
from ..core.calculator import default_chart_calculator
from ..core.varga import VargaCalculator
from ..core.ashtakavarga import AshtakavargaCalculator
from ..dasha.vimshottari import default_dasha_engine
from ..services.event_query import default_event_query_service
from ..services.prashna import default_prashna_service
from ..rules.engine import default_rules_engine
from ..ai.narrative import default_narrative_service


app = FastAPI(
    title="JyotishOS API",
    description="Deterministic Vedic Astrology Engine with Explainable Classical Rules and Multi-System Consensus",
    version="1.0.0"
)

# CORS middleware for Next.js / Web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "service": "JyotishOS Engine",
        "version": "1.0.0",
        "status": "operational",
        "total_rules": len(default_rules_engine.rules),
        "ayanamsa_default": "Lahiri (Chitra Paksha)",
        "ephemeris": "PyEphem (IAU high-precision sidereal)",
    }


@app.post("/api/chart/calculate", response_model=KundaliChart)
def calculate_natal_chart(birth_data: BirthData, ayanamsa: str = "Lahiri"):
    """Calculates full natal chart including Divisional charts and Ashtakavarga."""
    try:
        chart = default_chart_calculator.calculate_chart(birth_data, ayanamsa_name=ayanamsa)
        chart.vargas = VargaCalculator.calculate_all_vargas(chart)
        chart.ashtakavarga = AshtakavargaCalculator.calculate(chart)
        return chart
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DashaQueryRequest(BaseModel):
    birth_data: BirthData
    target_date: date


@app.post("/api/dasha/active", response_model=ActiveDashaHierarchy)
def get_active_dasha(payload: DashaQueryRequest):
    """Returns active 3-level Vimshottari Dasha for a specific event date."""
    try:
        chart = default_chart_calculator.calculate_chart(payload.birth_data)
        full_dt = datetime.combine(payload.birth_data.birth_date, payload.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        return default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, payload.target_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ghatna-query", response_model=GhatnaQueryResult)
def run_ghatna_query(query_input: GhatnaQueryInput, language: str = "Hindi"):
    """
    Executes the Core MVP Ghatna Query (Event Window Analysis):
    Calculates natal baseline, dasha, gochar transits, fires applicable shastriya rules,
    and returns multi-system consensus with evidence and narrative.
    """
    try:
        result = default_event_query_service.execute_query(query_input)
        # Optional AI enhancement if configured
        ai_narrative = default_narrative_service.synthesize_narrative(result, language=language)
        if language.lower().startswith("hi"):
            result.narrative_hi = ai_narrative
        else:
            result.narrative_en = ai_narrative
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PrashnaRequest(BaseModel):
    query_text: str
    category: str = "career"
    latitude: float = 28.6139
    longitude: float = 77.2090
    timezone_offset: float = 5.5


@app.post("/api/prashna")
def run_prashna_query(payload: PrashnaRequest):
    """Executes query-time Horary chart calculation and Arudha/Karyesh analysis."""
    try:
        return default_prashna_service.generate_prashna_chart(
            query_text=payload.query_text,
            query_category=payload.category,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_offset=payload.timezone_offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rules")
def list_rules(category: Optional[str] = None):
    """Returns the loaded classical rules library."""
    rules = default_rules_engine.rules
    if category:
        rules = [r for r in rules if r.get("category") == category]
    return {
        "total": len(rules),
        "rules": rules
    }


# =============================================================
# Advanced Astrological SaaS Endpoints
# =============================================================

@app.get("/api/geocoding/search")
def search_location(query: str):
    """Searches location via Geocoding API (Offline Gazetteer + Nominatim)."""
    from ..services.geocoding import default_geocoding_service
    return default_geocoding_service.search(query)


@app.post("/api/vedic-rishi/validate")
def validate_with_vedic_rishi(birth_data: BirthData):
    """Cross-validates JyotishOS calculations against Vedic Rishi API."""
    from ..services.vedic_rishi import default_vedic_rishi_client
    chart = default_chart_calculator.calculate_full_chart(birth_data)
    return default_vedic_rishi_client.cross_validate_chart(chart)


@app.post("/api/chart/shadbala")
def get_shadbala(birth_data: BirthData):
    """Calculates 6-fold Shadbala, Bhava Bala, and Planetary Avasthas."""
    from ..core.shadbala import default_shadbala_calculator
    chart = default_chart_calculator.calculate_chart(birth_data)
    return default_shadbala_calculator.calculate(chart)


@app.post("/api/chart/jaimini")
def get_jaimini_details(birth_data: BirthData):
    """Calculates Jaimini Chara Karakas, Karakamsha, Arudha Padas, and Special Lagnas."""
    from ..core.jaimini import default_jaimini_calculator
    chart = default_chart_calculator.calculate_chart(birth_data)
    return default_jaimini_calculator.calculate(chart)


class VarshaphalRequest(BaseModel):
    birth_data: BirthData
    target_year: int = 2027


@app.post("/api/chart/varshaphal")
def get_varshaphal(payload: VarshaphalRequest):
    """Calculates Tajika Solar Return Annual Chart, Muntha, Varshesha, and Sahams."""
    from ..services.varshaphal import default_varshaphal_service
    chart = default_chart_calculator.calculate_chart(payload.birth_data)
    return default_varshaphal_service.calculate_varshaphal(chart, payload.target_year)


class BTRRequest(BaseModel):
    birth_data: BirthData
    events: List[Any]
    window_minutes: int = 30
    step_minutes: int = 2


@app.post("/api/chart/btr")
def run_btr(payload: BTRRequest):
    """Runs Birth Time Rectification against past verified life events."""
    from ..services.btr import default_btr_service, LifeEvent
    ev_objs = [
        LifeEvent(
            event_date=e["event_date"] if isinstance(e, dict) else e.event_date,
            event_category=e["event_category"] if isinstance(e, dict) else e.event_category,
            description=e.get("description", "") if isinstance(e, dict) else getattr(e, "description", "")
        )
        for e in payload.events
    ]
    return default_btr_service.rectify_birth_time(
        payload.birth_data, ev_objs, payload.window_minutes, payload.step_minutes
    )


class MilanRequest(BaseModel):
    groom: BirthData
    bride: BirthData


@app.post("/api/chart/milan")
def run_milan(payload: MilanRequest):
    """Calculates 36-Guna Ashtakoota and Manglik Dosha matching."""
    from ..services.milan import default_milan_service
    return default_milan_service.match_charts(payload.groom, payload.bride)


@app.post("/api/chart/report")
def generate_report(birth_data: BirthData):
    """Generates complete standalone HTML Natal Report with print styling."""
    from ..services.report_generator import default_report_generator
    chart = default_chart_calculator.calculate_full_chart(birth_data)
    html_content = default_report_generator.generate_html_report(chart)
    return {"html": html_content}


class ChatRequest(BaseModel):
    query: str
    birth_data: Optional[BirthData] = None
    language: str = "Hindi"


@app.post("/api/ai/chat")
def chat_consultation_endpoint(payload: ChatRequest):
    """Interactive Gemini AI Astrological Sahayak consultation."""
    chart = None
    active_dasha = "Vimshottari"
    if payload.birth_data:
        chart = default_chart_calculator.calculate_full_chart(payload.birth_data)
    response_text = default_narrative_service.chat_consultation(
        user_query=payload.query,
        chart=chart,
        active_dasha_summary=active_dasha,
        language=payload.language
    )
    return {"response": response_text}


@app.post("/api/chart/affliction")
def get_affliction_report(birth_data: BirthData, detailed: bool = False, life_area_id: int = 1):
    """Calculates Dasvarga table, House points, Planet points, Life Area breakdown, and Classical Remedies."""
    from ..core.affliction import AfflictionEngine
    chart = default_chart_calculator.calculate_chart(birth_data)
    engine = AfflictionEngine(chart)
    return {
        "dasvarga_table": engine.calculate_dasvarga_table(),
        "house_points": engine.calculate_house_points(detailed=detailed),
        "planet_points": engine.calculate_planet_points(detailed=detailed),
        "life_area_detail": engine.get_life_area_detail(life_area_id),
        "rashi_prediction": engine.get_rashi_prediction(life_area_id),
        "remedy": engine.calculate_remedy(life_area_id=life_area_id, lords=detailed)
    }


@app.post("/api/chart/remedy/{life_area_id}")
def get_remedy_matrix(birth_data: BirthData, life_area_id: int, lords: bool = False):
    """Calculates 3-pillar Grahalakshanam remedy matrix: Rudraksha, Yagya, Gems, Mantra, Donation, Vriksha."""
    from ..core.affliction import AfflictionEngine
    chart = default_chart_calculator.calculate_chart(birth_data)
    engine = AfflictionEngine(chart)
    return {
        "life_area_id": life_area_id,
        "lords": lords,
        "remedy_matrix": engine.calculate_remedy(life_area_id=life_area_id, lords=lords)
    }


@app.get("/api/grahalakshanam/remedy/{life_area_id}")
def get_grahalakshanam_live_remedy(life_area_id: int, lords: bool = False):
    """Proxies live Grahalakshanam remedy endpoint for active cloud session."""
    return default_grahalakshanam_client.get_remedy(life_area_id, lords=lords)


@app.post("/api/chart/vastu")
def get_vastu_report(birth_data: BirthData):
    """Calculates 8-direction Vastu mandala, planetary correlation, and shastriya remedies."""
    from ..services.vastu import VastuJyotishEngine
    chart = default_chart_calculator.calculate_chart(birth_data)
    engine = VastuJyotishEngine(chart)
    return {"zones": engine.evaluate_vastu_zones()}


class PrashnaFullRequest(BaseModel):
    query_text: str
    category_name: str = "Career"
    latitude: float = 28.6139
    longitude: float = 77.2090
    timezone_offset: float = 5.5


@app.post("/api/chart/prashna-full")
def run_prashna_full(payload: PrashnaFullRequest):
    """Calculates complete Horary chart with Tajika Ithasala, house roles, and timings."""
    return default_prashna_service.generate_prashna_chart(
        query_text=payload.query_text,
        category_name=payload.category_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset=payload.timezone_offset
    )


class GlaLoginRequest(BaseModel):
    username: str = ""
    password: str = ""


@app.post("/api/grahalakshanam/login")
def grahalakshanam_login(payload: GlaLoginRequest):
    """Authenticates with Grahalakshanam API and returns JWT token."""
    from ..services.grahalakshanam import GrahalakshanamClient, GrahalakshanamConfig
    client = GrahalakshanamClient(GrahalakshanamConfig(username=payload.username, password=payload.password))
    success = client.authenticate()
    if not success:
        raise HTTPException(status_code=401, detail="Server authentication failed")
    return {"token": client.token, "user": client.user_data}


@app.get("/api/grahalakshanam/folders")
def grahalakshanam_folders():
    """Fetches saved folders and charts from Grahalakshanam."""
    from ..services.grahalakshanam import GrahalakshanamClient
    client = GrahalakshanamClient()
    if not client.authenticate():
        raise HTTPException(status_code=401, detail="Authentication failed")
    return client.get_folders_with_files()


@app.post("/api/grahalakshanam/sync")
def grahalakshanam_sync():
    """Syncs all charts from Grahalakshanam into JyotishOS local database."""
    from ..services.grahalakshanam import GrahalakshanamClient
    from ..services.folder_manager import default_folder_manager
    client = GrahalakshanamClient()
    if not client.authenticate():
        raise HTTPException(status_code=401, detail="Authentication failed")
    folders_files = client.get_folders_with_files()
    imported = default_folder_manager.sync_from_grahalakshanam(folders_files)
    return {"status": "success", "imported_charts": imported}



