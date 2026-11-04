"""
Time and Location Service for JyotishOS (Phase 1 Task P1-T7).
Converts local birth datetimes to high-precision UTC datetimes with:
1. Standard IANA timezone resolution via Python standard library `zoneinfo`.
2. Strict detection and error raising for ambiguous and non-existent DST transitions.
3. Historical Indian time rules (1942–45 War Time +6:30, 1962/1965/1971 DST, pre-1906 LMT).
"""

from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from .exceptions import AmbiguousTimeError, NonExistentTimeError, InvalidTimezoneError
from .historical_india import get_historical_indian_offset


@dataclass
class TimeResolutionResult:
    utc_datetime: datetime
    local_datetime: datetime
    timezone_name: str
    offset_hours: float
    fold_applied: Optional[int]
    is_dst: bool
    historical_rule: Optional[str] = None
    historical_lmt_applied: bool = False


class TimeService:
    """Standard IANA and historical time resolution engine for natal astrology."""

    @staticmethod
    def resolve_to_utc(
        local_date: date,
        local_time: time,
        timezone_name: str = "Asia/Kolkata",
        fold: Optional[int] = None,
        longitude: Optional[float] = None,
        apply_historical_indian: bool = True,
        use_lmt_pre_1906: bool = True,
    ) -> TimeResolutionResult:
        """
        Converts local date and time to UTC datetime using IANA zoneinfo and historical rules.

        Raises:
            InvalidTimezoneError: If timezone_name is not recognized.
            AmbiguousTimeError: If local time occurs twice during DST fall-back and fold is not specified.
            NonExistentTimeError: If local time falls into a DST spring-forward clock jump gap.
        """
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            raise InvalidTimezoneError(timezone_name)
        except Exception:
            raise InvalidTimezoneError(timezone_name)

        naive_dt = datetime.combine(local_date, local_time)

        # 1. Historical Indian Time Rules Check for Asia/Kolkata
        if timezone_name in ("Asia/Kolkata", "Asia/Calcutta", "IST") and apply_historical_indian:
            hist_offset, hist_desc = get_historical_indian_offset(
                dt_local=naive_dt,
                longitude=longitude,
                use_lmt_pre_1906=use_lmt_pre_1906
            )
            if hist_offset is not None:
                # Direct UTC conversion using specific historical offset
                offset_delta = timedelta(hours=hist_offset)
                dt_utc = (naive_dt - offset_delta).replace(tzinfo=timezone.utc)
                is_lmt = "LMT" in (hist_desc or "")
                return TimeResolutionResult(
                    utc_datetime=dt_utc,
                    local_datetime=naive_dt,
                    timezone_name=timezone_name,
                    offset_hours=hist_offset,
                    fold_applied=fold,
                    is_dst=hist_offset > 5.5,
                    historical_rule=hist_desc,
                    historical_lmt_applied=is_lmt
                )

        # 2. Check for Ambiguous or Non-Existent Times (DST transitions)
        dt_fold0 = naive_dt.replace(tzinfo=tz, fold=0)
        dt_fold1 = naive_dt.replace(tzinfo=tz, fold=1)
        utc_0 = dt_fold0.astimezone(timezone.utc)
        utc_1 = dt_fold1.astimezone(timezone.utc)

        if utc_0 != utc_1:
            back_0 = utc_0.astimezone(tz).replace(tzinfo=None)
            back_1 = utc_1.astimezone(tz).replace(tzinfo=None)

            # In a spring-forward gap, the local time never existed: round-trip fails for both folds
            if back_0 != naive_dt and back_1 != naive_dt:
                raise NonExistentTimeError(naive_dt.strftime("%Y-%m-%d %H:%M:%S"), timezone_name)

            # In a fall-back ambiguous overlap, both folds exist
            if fold is None:
                raise AmbiguousTimeError(naive_dt.strftime("%Y-%m-%d %H:%M:%S"), timezone_name)

            chosen_fold = 1 if fold == 1 else 0
            chosen_dt = naive_dt.replace(tzinfo=tz, fold=chosen_fold)
            utc_dt = chosen_dt.astimezone(timezone.utc)
            offset_seconds = chosen_dt.utcoffset().total_seconds() if chosen_dt.utcoffset() else 0.0
            return TimeResolutionResult(
                utc_datetime=utc_dt,
                local_datetime=naive_dt,
                timezone_name=timezone_name,
                offset_hours=offset_seconds / 3600.0,
                fold_applied=chosen_fold,
                is_dst=bool(chosen_dt.dst()),
                historical_rule=None
            )

        offset_seconds = dt_fold0.utcoffset().total_seconds() if dt_fold0.utcoffset() else 0.0
        return TimeResolutionResult(
            utc_datetime=utc_0,
            local_datetime=naive_dt,
            timezone_name=timezone_name,
            offset_hours=offset_seconds / 3600.0,
            fold_applied=None,
            is_dst=bool(dt_fold0.dst()),
            historical_rule=None
        )
