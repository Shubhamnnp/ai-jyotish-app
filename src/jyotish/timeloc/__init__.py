"""
Time and Location Service Package for JyotishOS (Phase 1).
"""

from .exceptions import (
    TimeLocationError,
    AmbiguousTimeError,
    NonExistentTimeError,
    InvalidTimezoneError,
)
from .historical_india import get_historical_indian_offset
from .service import TimeService, TimeResolutionResult
from .geo import GeoLocationService, GeoLocationResult, KNOWN_CITIES

__all__ = [
    "TimeLocationError",
    "AmbiguousTimeError",
    "NonExistentTimeError",
    "InvalidTimezoneError",
    "get_historical_indian_offset",
    "TimeService",
    "TimeResolutionResult",
    "GeoLocationService",
    "GeoLocationResult",
    "KNOWN_CITIES",
]
