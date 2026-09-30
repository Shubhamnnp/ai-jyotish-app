"""
Event Analysis & Retrospective Verification Endpoints for /api/v1/events.
Exposes 6-Pillar Past Event Verification and Future Event Window queries.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...events.past_verification import (
    PastEventVerificationEngine,
    PastEventVerificationInput,
    PastEventVerificationResult,
    default_past_event_engine
)

router = APIRouter(prefix="/events", tags=["v1-events"])


@router.post("/verify-past", response_model=PastEventVerificationResult)
def verify_past_event(
    inp: PastEventVerificationInput,
    persist_to_db: bool = Query(default=False)
):
    """
    Evaluates retrospective queries across the 6 Classical Pillars:
    1. Natal D1 House Promise
    2. Prashna Horary Overlay
    3. Divisional Varga (D9/D10/D7)
    4. Active Vimshottari Dasha Hierarchy
    5. Historical Double Transit (Gochar)
    6. Shastriya Rules Knowledge Base (12,500+ Rules)
    """
    try:
        result = default_past_event_engine.verify_past_event(inp)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Past event verification failed: {e}")
