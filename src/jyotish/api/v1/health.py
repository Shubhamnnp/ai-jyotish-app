"""
Health Check and Observability Endpoints for JyotishOS API (Phase 6, Task P6-T5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.5, P6-T5).

Rules:
1. Reports Swiss Ephemeris status, loaded ephe files, and calculation precision.
2. Reports quarantined rules statistics (scholar_verified, machine_checked, draft).
3. If Swiss Ephemeris is unavailable or degraded, flags engine_degraded=True. Never silently fall back.
"""

import time
import os
import ctypes
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...core.ephemeris import get_engine_health
from ...rules.engine import default_rules_engine
from ...rules.quarantine import get_quarantine_stats

router = APIRouter(prefix="/health", tags=["health"])

_START_TIME = time.time()


def get_process_memory_mb() -> float:
    """Returns Resident Set Size (RSS) memory of current process in MB."""
    try:
        from ctypes import wintypes
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ('cb', wintypes.DWORD),
                ('PageFaultCount', wintypes.DWORD),
                ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t),
                ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t),
            ]
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return round(counters.WorkingSetSize / (1024 * 1024), 2)
    except Exception:
        pass
    return 0.0


class SystemHealthResponse(BaseModel):
    """Structured health response for JyotishOS engine."""
    status: str = "healthy"  # "healthy" or "degraded"
    uptime_seconds: float
    timestamp: str
    engine_degraded: bool = False
    ephemeris: Dict[str, Any]
    rules: Dict[str, Any]
    system: Dict[str, Any]


@router.get("", response_model=SystemHealthResponse)
@router.get("/", response_model=SystemHealthResponse)
def get_system_health():
    """
    Returns high-level health report of the JyotishOS backend:
    - Ephemeris engine mode and verification
    - Quarantine & scholar rules breakdown
    - Uptime and memory footprint
    """
    ephe_health = get_engine_health()
    rules_stats = get_quarantine_stats(default_rules_engine.rules)
    uptime = round(time.time() - _START_TIME, 2)
    memory_mb = get_process_memory_mb()

    # Engine is degraded if ephemeris mode is not Swiss or self test failed
    ephe_mode = ephe_health.get("ephemeris_mode", "")
    self_test = ephe_health.get("self_test", "")
    is_degraded = ("Swiss" not in ephe_mode) or (self_test != "passed")

    status_str = "degraded" if is_degraded else "healthy"

    return SystemHealthResponse(
        status=status_str,
        uptime_seconds=uptime,
        timestamp=datetime.now(timezone.utc).isoformat(),
        engine_degraded=is_degraded,
        ephemeris=ephe_health,
        rules=rules_stats,
        system={
            "memory_rss_mb": memory_mb,
            "pid": os.getpid()
        }
    )


@router.get("/engine")
def get_engine_health_endpoint():
    """Returns detailed ephemeris engine status, Swiss version, files found, and self-test."""
    return get_engine_health()

