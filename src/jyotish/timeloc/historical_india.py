"""
Historical Indian Time Rules (Phase 1 Task P1-T7).
Incorporates:
1. Pre-1906 LMT (Local Mean Time, prior to 1 January 1906 introduction of standard IST).
2. 1942-1945 World War II War Time (+6:30, 1 September 1942 - 15 October 1945).
3. 1962 Sino-Indian War emergency DST (+6:30, 20 Oct 1962 - 21 Nov 1962).
4. 1965 Indo-Pak War emergency DST (+6:30, 6 Sep 1965 - 23 Sep 1965).
5. 1971 Indo-Pak War emergency DST (+6:30, 3 Dec 1971 - 17 Dec 1971).
"""

from datetime import datetime, date
from typing import Optional, Tuple, Dict, Any


def get_historical_indian_offset(
    dt_local: datetime,
    longitude: Optional[float] = None,
    use_lmt_pre_1906: bool = True
) -> Tuple[Optional[float], Optional[str]]:
    """
    Evaluates historical Indian time rules for a given local datetime.
    Returns:
        (offset_hours, rule_description) if a historical rule applies, or (None, None) for standard IST (+5.5).
    """
    dt_val = dt_local.date() if isinstance(dt_local, datetime) else dt_local

    # 1. Pre-1906 Local Mean Time (LMT)
    if dt_val < date(1906, 1, 1):
        if use_lmt_pre_1906 and longitude is not None:
            # LMT = longitude / 15.0 hours (4 minutes per degree)
            lmt_offset = longitude / 15.0
            return lmt_offset, f"Pre-1906 Local Mean Time (LMT) for longitude {longitude:.4f}°"
        # If longitude not provided, default to standard Madras Time / early railway time (+5:21:14 = 5.3538888)
        return 5.3538888, "Pre-1906 Madras Railway Time (+5:21:14)"

    # 2. World War II Indian War Time (+6:30)
    # 1 September 1942 through 15 October 1945
    if date(1942, 9, 1) <= dt_val <= date(1945, 10, 15):
        return 6.5, "1942-1945 Indian War Time (Daylight Saving +6:30)"

    # 3. 1962 Sino-Indian War Emergency DST (+6:30)
    if date(1962, 10, 20) <= dt_val <= date(1962, 11, 21):
        return 6.5, "1962 Sino-Indian War Emergency DST (+6:30)"

    # 4. 1965 Indo-Pakistani War Emergency DST (+6:30)
    if date(1965, 9, 6) <= dt_val <= date(1965, 9, 23):
        return 6.5, "1965 Indo-Pak War Emergency DST (+6:30)"

    # 5. 1971 Indo-Pakistani War Emergency DST (+6:30)
    if date(1971, 12, 3) <= dt_val <= date(1971, 12, 17):
        return 6.5, "1971 Indo-Pak War Emergency DST (+6:30)"

    # Standard IST (+5:30)
    return None, None
