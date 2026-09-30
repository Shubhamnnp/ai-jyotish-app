"""
Chart Calculation Endpoints for /api/v1/charts.
Calculates D1 to D60 Shodashavarga, Ashtakavarga, and planetary dignities.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from ...core.models import BirthData, KundaliChart
from ...core.calculator import default_chart_calculator
from ...core.varga import VargaCalculator
from ...core.ashtakavarga import AshtakavargaCalculator

router = APIRouter(prefix="/charts", tags=["v1-charts"])


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
