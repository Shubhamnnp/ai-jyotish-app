"""
Upagraha (Shadow Planets) Engine for JyotishOS.
Calculates classical Upagrahas:
1. Aprakasha Grahas derived from the Sun (BPHS Ch. 3):
   - Dhuma = Sun + 133°20'
   - Vyatipata = 360° - Dhuma
   - Parivesha (Paridhi) = Vyatipata + 180°
   - Indrachapa (Kodanda) = 360° - Parivesha
   - Upaketu (Sikhi) = Indrachapa + 16°40'
   - Classical invariant: (Upaketu + 30°) % 360 == Sun
2. Kala Upagrahas: Gulika and Mandi (BPHS Ch. 3 / Phaladeepika Ch. 25):
   - Diurnal / Nocturnal 8-fold division of the day (Dinamana) and night (Ratrimana).
   - Saturn's portion:
       Day: Monday=6th, Tuesday=5th, Wednesday=4th, Thursday=3rd, Friday=2nd, Saturday=1st, Sunday=7th.
       Night: Monday=2nd, Tuesday=1st, Wednesday=7th, Thursday=6th, Friday=5th, Saturday=4th, Sunday=3rd.
   - Gulika is the Ascendant (Lagna) at the START of Saturn's portion.
   - Mandi is the Ascendant (Lagna) at the MIDDLE of Saturn's portion.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, date, time, timedelta
import math

from .constants import SIGN_NAMES
from .models import KundaliChart, UpagrahaResult

try:
    import swisseph as swe
    _HAS_SWISSEPH = True
except ImportError:
    swe = None
    _HAS_SWISSEPH = False


class UpagrahaCalculator:
    """Calculates classical shadow points (Aprakasha Grahas and Kala Upagrahas)."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> UpagrahaResult:
        """Computes all classical upagrahas for the chart."""
        sun_lon = chart.planets["Sun"].longitude

        # 1. Classical Aprakasha Grahas derived from Sun (BPHS Ch. 3)
        dhuma = (sun_lon + 133.33333333333334) % 360.0
        vyatipata = (360.0 - dhuma) % 360.0
        parivesha = (vyatipata + 180.0) % 360.0
        indrachapa = (360.0 - parivesha) % 360.0
        upaketu = (indrachapa + 16.666666666666668) % 360.0

        dhuma_sign = SIGN_NAMES[int(dhuma // 30.0)]
        vyatipata_sign = SIGN_NAMES[int(vyatipata // 30.0)]
        parivesha_sign = SIGN_NAMES[int(parivesha // 30.0)]
        indrachapa_sign = SIGN_NAMES[int(indrachapa // 30.0)]
        upaketu_sign = SIGN_NAMES[int(upaketu // 30.0)]

        # 2. Gulika & Mandi via Classical Diurnal 8-part division
        gulika_lon, mandi_lon, seg, is_night, dinamana_h, ratrimana_h = cls._calculate_gulika_mandi(chart)

        gulika_sign_idx = int(gulika_lon // 30.0)
        mandi_sign_idx = int(mandi_lon // 30.0)

        return UpagrahaResult(
            gulika_sign_name=SIGN_NAMES[gulika_sign_idx],
            gulika_longitude=round(gulika_lon, 4),
            mandi_sign_name=SIGN_NAMES[mandi_sign_idx],
            mandi_longitude=round(mandi_lon, 4),
            dhuma_longitude=round(dhuma, 4),
            vyatipata_longitude=round(vyatipata, 4),
            parivesha_longitude=round(parivesha, 4),
            indrachapa_longitude=round(indrachapa, 4),
            upaketu_longitude=round(upaketu, 4),
            dhuma_sign_name=dhuma_sign,
            vyatipata_sign_name=vyatipata_sign,
            parivesha_sign_name=parivesha_sign,
            indrachapa_sign_name=indrachapa_sign,
            upaketu_sign_name=upaketu_sign,
            gulika_segment=seg,
            is_night_birth=is_night,
            dinamana_hours=dinamana_h,
            ratrimana_hours=ratrimana_h,
        )

    @classmethod
    def _calculate_gulika_mandi(
        cls, chart: KundaliChart
    ) -> Tuple[float, float, int, bool, Optional[float], Optional[float]]:
        """
        Calculates Gulika and Mandi based on classical Parashara & Phaladeepika principles.
        Returns: (gulika_lon, mandi_lon, segment, is_night, dinamana_hours, ratrimana_hours)
        """
        bdata = chart.birth_data
        b_date = bdata.birth_date
        lat = bdata.latitude
        lon = bdata.longitude

        # Obtain birth JD and timezone
        if chart.metadata and chart.metadata.jd_ut:
            birth_jd = chart.metadata.jd_ut
        else:
            # Fallback estimation of JD
            b_t = bdata.birth_time
            if isinstance(b_t, str):
                b_t = datetime.strptime(b_t, "%H:%M:%S" if len(b_t.split(":")) == 3 else "%H:%M").time()
            tz_off = float(bdata.timezone_offset if bdata.timezone_offset is not None else 5.5)
            dt_local = datetime.combine(b_date, b_t)
            dt_utc = dt_local - timedelta(hours=tz_off)
            y, m, d = dt_utc.year, dt_utc.month, dt_utc.day
            hour_dec = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
            if _HAS_SWISSEPH:
                birth_jd = swe.julday(y, m, d, hour_dec)
            else:
                birth_jd = 2440587.5 + (dt_utc.timestamp() / 86400.0)

        if _HAS_SWISSEPH:
            try:
                # Determine local midnight in UTC
                tz_hours = float(bdata.timezone_offset if bdata.timezone_offset is not None else 5.5)
                local_mid_utc = datetime.combine(b_date, time(0, 0)) - timedelta(hours=tz_hours)
                jd_mid = swe.julday(
                    local_mid_utc.year, local_mid_utc.month, local_mid_utc.day,
                    local_mid_utc.hour + local_mid_utc.minute / 60.0
                )

                # Sunrise and sunset of the birth date
                ret_sr = swe.rise_trans(jd_mid, swe.SUN, geopos=(lon, lat, 0), rsmi=swe.CALC_RISE)
                today_sr = ret_sr[1][0]
                ret_ss = swe.rise_trans(today_sr, swe.SUN, geopos=(lon, lat, 0), rsmi=swe.CALC_SET)
                today_ss = ret_ss[1][0]
                ret_next_sr = swe.rise_trans(today_ss, swe.SUN, geopos=(lon, lat, 0), rsmi=swe.CALC_RISE)
                next_sr = ret_next_sr[1][0]

                if birth_jd < today_sr:
                    # Birth is before sunrise today -> night of previous day
                    jd_prev_mid = jd_mid - 1.0
                    ret_psr = swe.rise_trans(jd_prev_mid, swe.SUN, geopos=(lon, lat, 0), rsmi=swe.CALC_RISE)
                    ret_pss = swe.rise_trans(ret_psr[1][0], swe.SUN, geopos=(lon, lat, 0), rsmi=swe.CALC_SET)
                    period_start = ret_pss[1][0]
                    period_end = today_sr
                    is_night = True
                    ref_date = b_date - timedelta(days=1)
                elif birth_jd >= today_ss:
                    # Birth is after sunset today -> night of today
                    period_start = today_ss
                    period_end = next_sr
                    is_night = True
                    ref_date = b_date
                else:
                    # Daytime birth
                    period_start = today_sr
                    period_end = today_ss
                    is_night = False
                    ref_date = b_date

                dinamana_hours = (today_ss - today_sr) * 24.0
                ratrimana_hours = (next_sr - today_ss) * 24.0

                w = ref_date.weekday()  # Monday=0, Sunday=6
                if not is_night:
                    seg = (5 - w) % 7 + 1
                else:
                    seg = (1 - w) % 7 + 1

                seg_dur = (period_end - period_start) / 8.0
                gulika_jd = period_start + (seg - 1) * seg_dur
                mandi_jd = period_start + (seg - 0.5) * seg_dur

                from .ephemeris import resolve_ayanamsa_mode
                _, ay_code = resolve_ayanamsa_mode(chart.ayanamsa_name)
                swe.set_sid_mode(ay_code, 0.0, 0.0)

                _, asc_g = swe.houses_ex(gulika_jd, lat, lon, b'W')
                gulika_lon = asc_g[0] % 360.0

                _, asc_m = swe.houses_ex(mandi_jd, lat, lon, b'W')
                mandi_lon = asc_m[0] % 360.0

                return gulika_lon, mandi_lon, seg, is_night, round(dinamana_hours, 2), round(ratrimana_hours, 2)
            except Exception:
                pass

        # Fallback if Swiss Ephemeris is unavailable or in extreme polar conditions
        # Default: 12-hour day (6:00 to 18:00)
        w = b_date.weekday()
        b_t = bdata.birth_time
        if isinstance(b_t, str):
            b_t = datetime.strptime(b_t, "%H:%M:%S" if len(b_t.split(":")) == 3 else "%H:%M").time()
        birth_hour = b_t.hour + b_t.minute / 60.0
        if birth_hour < 6.0:
            is_night = True
            ref_date = b_date - timedelta(days=1)
            w = ref_date.weekday()
            seg = (1 - w) % 7 + 1
            gulika_hour = 18.0 + (seg - 1) * 1.5
            mandi_hour = 18.0 + (seg - 0.5) * 1.5
        elif birth_hour >= 18.0:
            is_night = True
            ref_date = b_date
            seg = (1 - w) % 7 + 1
            gulika_hour = 18.0 + (seg - 1) * 1.5
            mandi_hour = 18.0 + (seg - 0.5) * 1.5
        else:
            is_night = False
            ref_date = b_date
            seg = (5 - w) % 7 + 1
            gulika_hour = 6.0 + (seg - 1) * 1.5
            mandi_hour = 6.0 + (seg - 0.5) * 1.5

        hour_offset = (gulika_hour - birth_hour)
        gulika_lon = (chart.lagna_longitude + hour_offset * 15.0) % 360.0
        mandi_offset = (mandi_hour - birth_hour)
        mandi_lon = (chart.lagna_longitude + mandi_offset * 15.0) % 360.0

        return gulika_lon, mandi_lon, seg, is_night, 12.0, 12.0


default_upagraha_calculator = UpagrahaCalculator()
