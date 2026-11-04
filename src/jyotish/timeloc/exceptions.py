"""
Time and Location Exceptions for JyotishOS (Phase 1 Task P1-T7).
"""

class TimeLocationError(ValueError):
    """Base exception for time and location processing errors."""
    pass


class AmbiguousTimeError(TimeLocationError):
    """Raised when a local time occurs twice during a daylight saving fall-back transition."""
    def __init__(self, dt_str: str, timezone_name: str):
        super().__init__(
            f"Local time '{dt_str}' in timezone '{timezone_name}' is ambiguous due to DST transition. "
            "Please specify 'fold=0' (first occurrence / DST) or 'fold=1' (second occurrence / Standard time)."
        )
        self.dt_str = dt_str
        self.timezone_name = timezone_name


class NonExistentTimeError(TimeLocationError):
    """Raised when a local time does not exist due to a daylight saving spring-forward gap."""
    def __init__(self, dt_str: str, timezone_name: str):
        super().__init__(
            f"Local time '{dt_str}' in timezone '{timezone_name}' does not exist due to DST spring-forward clock jump. "
            "Please verify and adjust the local birth time."
        )
        self.dt_str = dt_str
        self.timezone_name = timezone_name


class InvalidTimezoneError(TimeLocationError):
    """Raised when an unrecognized IANA timezone string is provided."""
    def __init__(self, timezone_name: str):
        super().__init__(
            f"Unrecognized IANA timezone '{timezone_name}'. Must be a valid standard IANA name (e.g. 'Asia/Kolkata', 'America/New_York')."
        )
        self.timezone_name = timezone_name
