"""
Dasha Systems Package for JyotishOS (Phase 3 Task P3-T1).
"""

from .vimshottari import VimshottariDashaEngine, default_dasha_engine, default_vimshottari_engine
from .chara import CharaDashaEngine
from .yogini import YoginiDashaEngine

DASHA_CAPABILITIES = {
    "supported_dashas": ["vimshottari", "chara", "yogini", "ashtottari", "kalachakra"],
    "year_bases": ["solar", "savana", "nakshatra"],
    "max_hierarchy_levels": 5,  # Maha, Antar, Pratyantar, Sookshma, Prana
    "dasha_sandhi_detection": True,
}

__all__ = [
    "VimshottariDashaEngine",
    "default_dasha_engine",
    "default_vimshottari_engine",
    "CharaDashaEngine",
    "YoginiDashaEngine",
    "DASHA_CAPABILITIES",
]

