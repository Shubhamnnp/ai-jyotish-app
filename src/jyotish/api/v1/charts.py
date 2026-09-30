"""
Chart Calculation Endpoints for /api/v1/charts.
Calculates D1 to D60 Shodashavarga, Ashtakavarga, Shadbala, Multi-Dasha, and Milan compatibility.
"""

from datetime import datetime, date, time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...core.models import BirthData, KundaliChart
from ...core.calculator import default_chart_calculator
from ...core.varga import VargaCalculator
from ...core.ashtakavarga import AshtakavargaCalculator
from ...core.shadbala import default_shadbala_calculator
from ...dasha.vimshottari import default_dasha_engine
from ...dasha.yogini import default_yogini_engine
from ...dasha.ashtottari import default_ashtottari_engine
from ...dasha.chara import default_chara_engine
from ...services.milan import default_milan_service

router = APIRouter(prefix="/charts", tags=["v1-charts"])


class MultiDashaRequest(BaseModel):
    birth_data: BirthData
    target_date: Optional[date] = None
    ayanamsa: str = "Lahiri"


class MilanRequest(BaseModel):
    groom: BirthData
    bride: BirthData


@router.post("/calculate", response_model=KundaliChart)
def calculate_chart(birth_data: BirthData, ayanamsa: str = "Lahiri"):
    """Calculates full natal chart with Shodashavarga and Ashtakavarga."""
    try:
        chart = default_chart_calculator.calculate_full_chart(birth_data, ayanamsa_name=ayanamsa)
        if not chart.vargas:
            chart.vargas = VargaCalculator.calculate_all_vargas(chart)
        if not chart.ashtakavarga:
            chart.ashtakavarga = AshtakavargaCalculator.calculate(chart)
        return chart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {e}")


@router.post("/dashas")
def calculate_multi_dashas(payload: MultiDashaRequest):
    """
    Calculates 4 classical Dasha systems simultaneously for a given target date:
    1. Vimshottari (Maha, Antar, Pratyantar)
    2. Yogini (36-year cycle)
    3. Jaimini Chara Dasha (Sign-based)
    4. Ashtottari Dasha (108-year conditional cycle)
    """
    try:
        chart = default_chart_calculator.calculate_chart(payload.birth_data, ayanamsa_name=payload.ayanamsa)
        target_d = payload.target_date or date.today()
        full_dt = datetime.combine(payload.birth_data.birth_date, payload.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude

        # 1. Vimshottari
        vim_hierarchy = default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, target_d)

        # 2. Yogini
        yog_active = default_yogini_engine.get_active_yogini_at(full_dt, moon_lon, target_d)

        # 3. Ashtottari
        ash_active = default_ashtottari_engine.get_active_dasha_at(chart, target_d)

        # 4. Chara Dasha
        cha_active = default_chara_engine.get_active_chara_dasha_at(chart, target_d)

        return {
            "target_date": target_d.isoformat(),
            "ayanamsa": payload.ayanamsa,
            "vimshottari": {
                "summary": vim_hierarchy.formatted_summary,
                "mahadasha": vim_hierarchy.mahadasha,
                "antardasha": vim_hierarchy.antardasha,
                "pratyantardasha": vim_hierarchy.pratyantardasha,
            },
            "yogini": {
                "yogini": yog_active.get("yogini_name", yog_active.get("yogini")),
                "lord": yog_active.get("lord"),
                "duration_years": yog_active.get("duration_years"),
                "start_date": yog_active.get("start_date").isoformat() if hasattr(yog_active.get("start_date"), "isoformat") else str(yog_active.get("start_date")),
                "end_date": yog_active.get("end_date").isoformat() if hasattr(yog_active.get("end_date"), "isoformat") else str(yog_active.get("end_date")),
            },
            "ashtottari": {
                "summary": ash_active.get("summary"),
                "mahadasha": ash_active.get("mahadasha", {}).get("lord") if isinstance(ash_active.get("mahadasha"), dict) else str(ash_active.get("mahadasha")),
                "antardasha": ash_active.get("antardasha", {}).get("lord") if isinstance(ash_active.get("antardasha"), dict) else str(ash_active.get("antardasha")),
            },
            "chara": {
                "sign_name": cha_active.get("sign_name"),
                "duration_years": cha_active.get("duration_years"),
                "start_date": cha_active.get("start_date").isoformat() if hasattr(cha_active.get("start_date"), "isoformat") else str(cha_active.get("start_date")),
                "end_date": cha_active.get("end_date").isoformat() if hasattr(cha_active.get("end_date"), "isoformat") else str(cha_active.get("end_date")),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-dasha calculation error: {e}")


@router.post("/shadbala")
def calculate_shadbala_endpoint(birth_data: BirthData, ayanamsa: str = "Lahiri"):
    """Calculates 6-fold Shadbala strengths, Rupas, and planetary rank order."""
    try:
        chart = default_chart_calculator.calculate_chart(birth_data, ayanamsa_name=ayanamsa)
        shadbala_summary = default_shadbala_calculator.calculate(chart)
        return {
            "planets": shadbala_summary.planets,
            "bhava_bala": shadbala_summary.bhava_bala,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shadbala calculation error: {e}")


@router.post("/milan")
def calculate_milan_endpoint(payload: MilanRequest):
    """Calculates 36-Guna Ashtakoota Milan compatibility and Manglik Dosha analysis."""
    try:
        milan_result = default_milan_service.match_charts(payload.groom, payload.bride)
        return milan_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Milan calculation error: {e}")
