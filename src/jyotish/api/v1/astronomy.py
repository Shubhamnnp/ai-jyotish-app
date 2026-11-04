"""
Astronomy & Ephemeris API endpoints for JyotishOS (Phase 1).
Exposes supported ayanamsa systems, planetary state, and ephemeris diagnostics.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from src.jyotish.core.ephemeris import (
    SUPPORTED_AYANAMSAS,
    default_ephemeris_provider,
    get_engine_health
)

router = APIRouter(prefix="/astronomy", tags=["Astronomy & Ephemeris"])


class AyanamsaInfo(BaseModel):
    name: str
    swiss_sidm_code: int
    description: str
    reference_j2000_degrees: float


@router.get("/ayanamsas", response_model=List[AyanamsaInfo])
def get_supported_ayanamsas():
    """Lists all validated astronomical sidereal ayanamsa modes and their J2000 offsets."""
    jd_j2000 = 2451545.0  # 2000-01-01 12:00:00 UTC
    results = []
    for name, (code, desc) in sorted(SUPPORTED_AYANAMSAS.items()):
        val = default_ephemeris_provider.calculate_ayanamsa(jd_j2000, name)
        results.append(
            AyanamsaInfo(
                name=name,
                swiss_sidm_code=code,
                description=desc,
                reference_j2000_degrees=round(val, 6)
            )
        )
    return results


@router.get("/engine/health")
def get_astronomy_health():
    """Diagnostic health status for astronomical ephemeris engine."""
    return get_engine_health()

