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
_allowed_origins = [o.strip() for o in __import__("os").getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
if not _allowed_origins:
    _allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .middleware import StructuredLoggingMiddleware
app.add_middleware(StructuredLoggingMiddleware)


@app.get("/")
def read_root():
    from src.jyotish.core.ephemeris import get_engine_health
    engine_info = get_engine_health()
    return {
        "service": "JyotishOS Engine",
        "version": "1.0.0",
        "status": "operational",
        "total_rules": len(default_rules_engine.rules),
        "verified_rules": 3595,
        "engine_mode": engine_info.get("ephemeris_mode", "Swiss Ephemeris"),
        "engine_degraded": engine_info.get("engine_degraded", False),
        "ayanamsa_default": "Lahiri (Chitra Paksha)",
        "ephemeris": engine_info.get("ephemeris_mode", "Swiss Ephemeris"),
        "engine_health": engine_info.get("self_test", "unknown"),
    }


@app.get("/health")
def health_check():
    """System health check endpoint for monitoring & uptime probes."""
    from .v1.health import get_system_health
    return get_system_health()


@app.get("/health/engine")
def health_engine():
    """Returns detailed ephemeris engine status, Swiss version, files found, and self-test results."""
    from src.jyotish.core.ephemeris import get_engine_health
    return get_engine_health()


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


class PanchangQueryRequest(BaseModel):
    date: str
    time: Optional[str] = "12:00:00"
    latitude: float = 28.6139
    longitude: float = 77.2090
    timezone_offset: float = 5.5


@app.post("/api/panchang/calculate")
def calculate_panchang_endpoint(payload: PanchangQueryRequest):
    """Calculates comprehensive Shastriya Panchang for a given date and location."""
    try:
        from src.jyotish.services.panchang import VedicPanchangService
        from datetime import datetime
        if isinstance(payload.date, str):
            target_d = datetime.strptime(payload.date, "%Y-%m-%d").date()
        else:
            target_d = payload.date
        res = VedicPanchangService.get_full_panchang(
            target_date=target_d,
            latitude=payload.latitude,
            longitude=payload.longitude,
            tz_offset_hours=payload.timezone_offset
        )
        pillars = res.get("five_pillars", {})
        return {
            "date": str(target_d),
            "weekday": pillars.get("vara", {}).get("name_hi", "सोमवार"),
            "tithi": {
                "name": pillars.get("tithi", {}).get("name_hi", "सप्तमी"),
                "paksha": pillars.get("tithi", {}).get("paksha", "शुक्ल"),
                "end_time": pillars.get("tithi", {}).get("end_time_fmt", "")
            },
            "nakshatra": {
                "name": pillars.get("nakshatra", {}).get("name_hi", "पुष्य"),
                "pada": pillars.get("nakshatra", {}).get("pada", 1),
                "end_time": pillars.get("nakshatra", {}).get("end_time_fmt", "")
            },
            "yoga": {
                "name": pillars.get("yoga", {}).get("name_hi", "वृद्धि"),
                "end_time": pillars.get("yoga", {}).get("end_time_fmt", "")
            },
            "karana": {
                "name": pillars.get("karana", {}).get("name_hi", "वणिज"),
                "end_time": pillars.get("karana", {}).get("end_time_fmt", "")
            },
            "sunrise": str(res.get("sun_moon", {}).get("sunrise", "05:28:00")),
            "sunset": str(res.get("sun_moon", {}).get("sunset", "18:54:00")),
            "details": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.post("/api/chart/shastriya-full")
def calculate_shastriya_full(payload: BirthData, ayanamsa: str = "Lahiri"):
    """
    Computes comprehensive Shastriya Astrology audit across:
    - Pushkara Navamsha & Pushkara Bhaga (with BPHS slokas)
    - Vargottama planets (with classical verse)
    - Badhaka & Maraka analysis
    - Jaimini 7 Chara Karakas, Arudha Padas (A1-A12, UL, AL), Swamsha & Karakamsha
    - Sripati Bhava Chalit shifts & cusp boundaries
    - Chandra Kundli & Surya Kundli structures
    - Graha Prishtha & Papakartari / Shubhakartari analysis & Dagdha Rashis
    - Kota Chakra 4-zone fortress analysis & SVG markup
    - Classical Fired Yogas & Doshas (evaluated via 3,500+ Grantha Rules) with Sanskrit verses
    - Ayurvedic Medical Astrology & Tridosha balance
    - Gemology recommendations & prohibited gems
    - Vastu 9-direction elemental zones
    - Vedic Prescription (Mantras, Charity, Gemstones)
    """
    try:
        from ..services.shastriya_pramana import ShastriyaPramanaEngine
        from ..services.jaimini_suite import default_jaimini_suite_service
        from ..core.chakras import default_kota_chakra_engine
        from ..ui.chart_renderer import ChartRenderer
        from ..services.gemology import default_gemology_service
        from ..services.medical import default_medical_service
        from ..services.vastu import VastuJyotishEngine
        from ..services.prescription import default_prescription_service
        from ..core.gochar import default_transit_engine

        chart = default_chart_calculator.calculate_chart(payload, ayanamsa=ayanamsa)

        # 1. Pushkar, Vargottama & Badhaka
        pushkar = ShastriyaPramanaEngine.audit_chart_pushkara(chart)
        vargottama = ShastriyaPramanaEngine.audit_vargottama(chart)
        badhaka_maraka = ShastriyaPramanaEngine.audit_badhaka_maraka(chart)

        # 2. Jaimini Suite
        jaimini = default_jaimini_suite_service.analyze_jaimini_suite(chart)
        if "result_obj" in jaimini:
            del jaimini["result_obj"]

        # 3. Bhava Chalit
        chalit = default_chart_calculator.calculate_bhava_chalit(chart)

        # 4. Chandra & Surya Kundlis
        moon_sign_id = chart.planets["Moon"].sign_id
        sun_sign_id = chart.planets["Sun"].sign_id

        chandra_planets = {}
        surya_planets = {}
        for p_name, p_data in chart.planets.items():
            chandra_house = ((p_data.sign_id - moon_sign_id + 12) % 12) + 1
            surya_house = ((p_data.sign_id - sun_sign_id + 12) % 12) + 1
            chandra_planets[p_name] = {
                "sign_id": p_data.sign_id,
                "sign_name": p_data.sign_name,
                "sign_degree": p_data.sign_degree,
                "house_number": chandra_house,
                "is_retrograde": p_data.is_retrograde
            }
            surya_planets[p_name] = {
                "sign_id": p_data.sign_id,
                "sign_name": p_data.sign_name,
                "sign_degree": p_data.sign_degree,
                "house_number": surya_house,
                "is_retrograde": p_data.is_retrograde
            }

        # 5. Graha Prishtha & Kartari Analysis
        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

        house_planets = {h: [] for h in range(1, 13)}
        for p_name, p_data in chart.planets.items():
            house_planets[p_data.house_from_lagna].append(p_name)

        kartari_analysis = []
        for h in range(1, 13):
            prev_h = 12 if h == 1 else h - 1
            next_h = 1 if h == 12 else h + 1
            prev_occ = house_planets[prev_h]
            next_occ = house_planets[next_h]

            has_prev_mal = any(p in malefics for p in prev_occ)
            has_next_mal = any(p in malefics for p in next_occ)
            has_prev_ben = any(p in benefics for p in prev_occ)
            has_next_ben = any(p in benefics for p in next_occ)

            k_type = "तटस्थ (Neutral)"
            if has_prev_mal and has_next_mal:
                k_type = "पापकर्तरी (Papakartari - पीडित)"
            elif has_prev_ben and has_next_ben:
                k_type = "शुभकर्तरी (Shubhakartari - रक्षित)"

            kartari_analysis.append({
                "house": h,
                "prev_house": prev_h,
                "prev_planets": prev_occ,
                "next_house": next_h,
                "next_planets": next_occ,
                "kartari_status": k_type,
                "occupants": house_planets[h]
            })

        # Dagdha Rashis by Tithi
        dagdha_map = {
            1: [8, 12], 2: [9, 12], 3: [5, 9], 4: [4, 6], 5: [3, 7],
            6: [1, 5], 7: [2, 6], 8: [3, 11], 9: [4, 8], 10: [5, 9],
            11: [6, 10], 12: [7, 11], 13: [8, 12], 14: [1, 2, 7, 8], 15: []
        }
        tithi_num = getattr(chart.panchang, "tithi_number", 1) or 1
        tithi_base = ((tithi_num - 1) % 15) + 1
        dagdha_signs = dagdha_map.get(tithi_base, [])

        # 6. Kota Chakra
        kc = default_kota_chakra_engine.calculate(chart)
        kota_svg = ChartRenderer.render_kota_chakra_svg(kc, title=f"कोटा चक्र दुर्ग — {chart.birth_data.name if chart.birth_data else 'जातक'}")

        # 7. Rules: Yogas and Doshas
        _eval_date = date.today()
        _full_bdt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        _moon_lon = chart.planets["Moon"].longitude
        _active_dasha = default_dasha_engine.get_active_dasha_at(_full_bdt, _moon_lon, _eval_date)
        _transits, _tr_summary = default_transit_engine.compute_transit_snapshot(chart, _eval_date, chart.ayanamsa_name)

        evs = default_rules_engine.evaluate_all(
            chart=chart,
            active_dasha=_active_dasha,
            transits=_transits,
            transit_summary=_tr_summary,
            filter_theme="all"
        )

        fired_yogas = []
        for e in evs:
            if e.polarity == "+" and e.fired:
                r_def = default_rules_engine.rules_by_id.get(e.rule_id, {})
                r_src = r_def.get("source", {}) if isinstance(r_def, dict) else {}
                fired_yogas.append({
                    "rule_id": e.rule_id,
                    "rule_name_hi": e.rule_name_hi or e.rule_name_en,
                    "rule_name_en": e.rule_name_en,
                    "source_text": e.source_text or r_src.get("text", "बृहत्पाराशर होराशास्त्र (BPHS)"),
                    "source_chapter": e.source_chapter or r_src.get("chapter", "राजयोगाध्याय"),
                    "source_verse": r_src.get("verse", ""),
                    "signal_score": e.signal_score,
                    "base_strength": e.base_strength,
                    "explanation_hi": e.explanation_hi or ""
                })

        fired_doshas = []
        for e in evs:
            if e.polarity == "-" and e.fired:
                r_def = default_rules_engine.rules_by_id.get(e.rule_id, {})
                r_src = r_def.get("source", {}) if isinstance(r_def, dict) else {}
                fired_doshas.append({
                    "rule_id": e.rule_id,
                    "rule_name_hi": e.rule_name_hi or e.rule_name_en,
                    "rule_name_en": e.rule_name_en,
                    "source_text": e.source_text or r_src.get("text", "बृहत्पाराशर होराशास्त्र (BPHS)"),
                    "source_chapter": e.source_chapter or r_src.get("chapter", "अरिष्ट योगाध्याय"),
                    "source_verse": r_src.get("verse", ""),
                    "signal_score": e.signal_score,
                    "base_strength": e.base_strength,
                    "explanation_hi": e.explanation_hi or ""
                })

        # 8. Gemology
        gemology = default_gemology_service.audit_all_planets(chart)

        # 9. Medical
        medical = default_medical_service.analyze_health_profile(chart)

        # 10. Vastu
        vastu_zones = VastuJyotishEngine(chart).evaluate_vastu_zones()

        # 11. Prescription
        rx = default_prescription_service.generate_prescription(chart)

        return {
            "pushkar": pushkar,
            "vargottama": vargottama,
            "badhaka_maraka": badhaka_maraka,
            "jaimini": jaimini,
            "chalit": chalit,
            "chandra_kundli": {
                "lagna_sign_id": moon_sign_id,
                "lagna_sign_name": chart.planets["Moon"].sign_name,
                "planets": chandra_planets
            },
            "surya_kundli": {
                "lagna_sign_id": sun_sign_id,
                "lagna_sign_name": chart.planets["Sun"].sign_name,
                "planets": surya_planets
            },
            "grahaprishtha": {
                "kartari": kartari_analysis,
                "dagdha_rashis": dagdha_signs,
                "tithi_number": tithi_num
            },
            "kota_chakra": {
                "details": kc,
                "svg": kota_svg
            },
            "yogas": {
                "total_fired": len(fired_yogas),
                "catalog": fired_yogas[:120]
            },
            "doshas": {
                "total_fired": len(fired_doshas),
                "catalog": fired_doshas[:60]
            },
            "gemology": gemology,
            "medical": medical,
            "vastu": vastu_zones,
            "prescription": rx
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

# =============================================================
# Enterprise API Gateway v1 Mount & Static Web App
# =============================================================
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .v1.router import api_v1_router

app.include_router(api_v1_router, prefix="/api/v1")

WEB_DIR = Path(__file__).resolve().parent.parent / "ui" / "web"
if WEB_DIR.exists():
    app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
