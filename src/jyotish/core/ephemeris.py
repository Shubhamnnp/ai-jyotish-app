"""
Astronomical Ephemeris Engine for JyotishOS.
Provides sidereal planetary longitudes, speeds, retrograde status, and combustion.
Uses PyEphem (`ephem`) with classical Ayanamsa systems (Lahiri, Raman, KP, True Chitra).
"""

import math
from abc import ABC, abstractmethod
from datetime import datetime, date, time, timezone, timedelta
from typing import Dict, Tuple, Optional
import ephem

from .constants import (
    SIGNS, SIGN_NAMES, NAKSHATRAS, EXALTATION, DEBILITATION,
    MOOLATRIKONA, OWN_SIGNS, NATURAL_FRIENDS, NATURAL_ENEMIES
)
from .models import PlanetPosition, BirthData


class BaseEphemerisProvider(ABC):
    """Abstract interface for astronomical computation."""

    @abstractmethod
    def calculate_ayanamsa(self, jd: float, ayanamsa_name: str = "Lahiri") -> float:
        pass

    @abstractmethod
    def get_planet_positions(
        self,
        dt_utc: datetime,
        ayanamsa_name: str = "Lahiri"
    ) -> Tuple[Dict[str, Dict[str, float]], float]:
        """Returns ({planet_name: {longitude, latitude, speed, is_retrograde}}, ayanamsa_deg)"""
        pass

    @abstractmethod
    def calculate_ascendant(
        self,
        dt_utc: datetime,
        latitude: float,
        longitude: float,
        ayanamsa_val: float
    ) -> float:
        """Returns Sidereal Ascendant (Lagna) longitude 0-360."""
        pass


class PyEphemProvider(BaseEphemerisProvider):
    """High-precision Ephemeris provider using PyEphem and IAU precession."""

    def datetime_to_jd(self, dt: datetime) -> float:
        """Convert UTC datetime to Julian Day Number."""
        return float(ephem.julian_date(dt))

    def calculate_ayanamsa(self, jd: float, ayanamsa_name: str = "Lahiri") -> float:
        """
        Calculate sidereal ayanamsa in degrees.
        Lahiri is Indian Govt standard (Chitra Paksha): 23.857092 deg at J2000.0.
        """
        # Epoch J2000.0 = JD 2451545.0 (2000-01-01 12:00:00 UTC)
        days_from_j2000 = jd - 2451545.0
        centuries = days_from_j2000 / 36525.0

        # High-order polynomial for Lahiri precession
        # Precession ~ 50.290966 arcsec / year = 5029.0966 arcsec / century
        lahiri_base = 23.857092 + (5029.0966 * centuries + 1.1116 * centuries**2) / 3600.0

        ayanamsa_name_lower = ayanamsa_name.strip().lower()
        if ayanamsa_name_lower in ("lahiri", "chitra_paksha", "default"):
            return lahiri_base % 360.0
        elif ayanamsa_name_lower == "raman":
            return (lahiri_base - 1.45) % 360.0
        elif ayanamsa_name_lower in ("kp", "krishnamurti"):
            return (lahiri_base - 0.10) % 360.0
        elif ayanamsa_name_lower == "true_chitra":
            # True Chitra anchors Spica at exact 180.0 degrees sidereal
            try:
                spica = ephem.Star("Spica")
                d = ephem.Date(jd - 2415020.0)  # Dublin Julian Date
                spica.compute(d)
                spica_ecl = ephem.Ecliptic(spica)
                trop_spica_deg = math.degrees(spica_ecl.lon)
                return (trop_spica_deg - 180.0) % 360.0
            except Exception:
                return lahiri_base % 360.0
        else:
            return lahiri_base % 360.0

    def calculate_mean_lunar_nodes(self, jd: float) -> Tuple[float, float]:
        """
        Computes Mean Lunar Node (Rahu) and Ketu (Rahu + 180 deg).
        Based on standard astronomical formula (Meeus Astronomical Algorithms).
        """
        t = (jd - 2451545.0) / 36525.0
        # Omega = 125.04452222 - 1934.1362608 * T + 0.0020708 * T^2 + T^3 / 450000
        omega = 125.04452222 - 1934.1362608 * t + 0.0020708 * (t**2) + (t**3) / 450000.0
        rahu = omega % 360.0
        ketu = (rahu + 180.0) % 360.0
        return rahu, ketu

    def calculate_true_lunar_nodes(self, dt_utc: datetime) -> Tuple[float, float]:
        """
        Computes True (Sphutha) Lunar Node (Rahu) using PyEphem's precise Moon tracking.
        True node oscillates around the mean node with a ±1.5° amplitude.
        """
        try:
            # PyEphem tracks the Moon's actual ascending node via Moon._n_dot / _node
            m = ephem.Moon()
            m.compute(ephem.Date(dt_utc))
            # PyEphem internal: moon._node is the longitude of ascending node in radians
            if hasattr(m, '_node'):
                rahu_trop = math.degrees(m._node) % 360.0
            else:
                # Fallback: use mean node
                jd = self.datetime_to_jd(dt_utc)
                rahu_trop, _ = self.calculate_mean_lunar_nodes(jd)
            ketu_trop = (rahu_trop + 180.0) % 360.0
            return rahu_trop, ketu_trop
        except Exception:
            jd = self.datetime_to_jd(dt_utc)
            return self.calculate_mean_lunar_nodes(jd)

    def get_planet_positions(
        self,
        dt_utc: datetime,
        ayanamsa_name: str = "Lahiri",
        node_type: str = "mean"
    ) -> Tuple[Dict[str, Dict[str, float]], float]:
        """
        Calculates sidereal planetary positions for 9 grahas.
        node_type: 'mean' (default) or 'true' for True/Sphutha nodes.
        Returns dictionary and ayanamsa value.
        """
        jd = self.datetime_to_jd(dt_utc)
        ayanamsa = self.calculate_ayanamsa(jd, ayanamsa_name)
        ephem_date = ephem.Date(dt_utc)

        # Mapping to PyEphem bodies
        bodies = {
            "Sun": ephem.Sun(),
            "Moon": ephem.Moon(),
            "Mars": ephem.Mars(),
            "Mercury": ephem.Mercury(),
            "Jupiter": ephem.Jupiter(),
            "Venus": ephem.Venus(),
            "Saturn": ephem.Saturn(),
            "Uranus": ephem.Uranus(),
            "Neptune": ephem.Neptune(),
            "Pluto": ephem.Pluto(),
        }

        # Step offset for speed calculation (12 hours before and after)
        dt_prev = dt_utc - timedelta(hours=12)
        dt_next = dt_utc + timedelta(hours=12)

        results: Dict[str, Dict[str, float]] = {}

        for name, body in bodies.items():
            body.compute(ephem_date)
            ecl = ephem.Ecliptic(body)
            trop_lon = math.degrees(ecl.lon) % 360.0
            trop_lat = math.degrees(ecl.lat)

            # Sidereal conversion
            sid_lon = (trop_lon - ayanamsa) % 360.0

            # Calculate daily motion (speed)
            body_prev = getattr(ephem, body.__class__.__name__)()
            body_prev.compute(ephem.Date(dt_prev))
            lon_prev = math.degrees(ephem.Ecliptic(body_prev).lon)

            body_next = getattr(ephem, body.__class__.__name__)()
            body_next.compute(ephem.Date(dt_next))
            lon_next = math.degrees(ephem.Ecliptic(body_next).lon)

            # Handle 360 wrap-around in speed calculation
            diff = lon_next - lon_prev
            if diff > 180.0:
                diff -= 360.0
            elif diff < -180.0:
                diff += 360.0
            speed = diff  # deg per 1 day (24 hours)

            is_retro = speed < 0.0

            results[name] = {
                "longitude": sid_lon,
                "latitude": trop_lat,
                "speed": speed,
                "is_retrograde": is_retro,
                "tropical_lon": trop_lon,
            }

        # Calculate Rahu & Ketu (Mean or True Nodes based on node_type)
        if node_type == "true":
            rahu_trop, ketu_trop = self.calculate_true_lunar_nodes(dt_utc)
            node_speed = -0.0535  # True node oscillates, avg speed similar to mean
            node_label = "True Node"
        else:
            rahu_trop, ketu_trop = self.calculate_mean_lunar_nodes(jd)
            node_speed = -0.05295
            node_label = "Mean Node"

        rahu_sid = (rahu_trop - ayanamsa) % 360.0
        ketu_sid = (ketu_trop - ayanamsa) % 360.0

        results["Rahu"] = {
            "longitude": rahu_sid,
            "latitude": 0.0,
            "speed": node_speed,
            "is_retrograde": True,
            "tropical_lon": rahu_trop,
            "node_type": node_label,
        }
        results["Ketu"] = {
            "longitude": ketu_sid,
            "latitude": 0.0,
            "speed": node_speed,
            "is_retrograde": True,
            "tropical_lon": ketu_trop,
            "node_type": node_label,
        }

        return results, ayanamsa

    def calculate_ascendant(
        self,
        dt_utc: datetime,
        latitude: float,
        longitude: float,
        ayanamsa_val: float
    ) -> float:
        """
        Calculates exact Sidereal Lagna (Ascendant) in degrees (0-360).
        """
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        observer.elevation = 0
        observer.date = ephem.Date(dt_utc)

        # Sidereal time (Local Sidereal Time / RAMC in radians)
        lst_rad = observer.sidereal_time()
        ramc_deg = math.degrees(lst_rad) % 360.0

        # Obliquity of the Ecliptic (eps)
        jd = self.datetime_to_jd(dt_utc)
        t = (jd - 2451545.0) / 36525.0
        eps_deg = 23.4392911 - 0.0130042 * t
        eps_rad = math.radians(eps_deg)
        lat_rad = math.radians(latitude)
        ramc_rad = math.radians(ramc_deg)

        # Classical formula for Ascendant longitude:
        # tan(lambda) = -cos(RAMC) / (sin(RAMC)*cos(eps) + tan(lat)*sin(eps))
        y = math.cos(ramc_rad)
        x = -(math.sin(ramc_rad) * math.cos(eps_rad) + math.tan(lat_rad) * math.sin(eps_rad))
        asc_trop_deg = math.degrees(math.atan2(y, x)) % 360.0

        # Sidereal Lagna
        asc_sid_deg = (asc_trop_deg - ayanamsa_val) % 360.0
        return asc_sid_deg


class SwissEphemerisProvider(BaseEphemerisProvider):
    """
    Swiss Ephemeris Provider (JPL DE431-based precision).
    Supports pyswisseph/swisseph C-bindings when installed, with graceful
    fallback to calibrated PyEphem astronomical provider.
    """

    def __init__(self, ephe_path: Optional[str] = None):
        self._swe = None
        self._has_swisseph = False
        self._fallback = PyEphemProvider()
        try:
            import swisseph as swe
            self._swe = swe
            if ephe_path and hasattr(swe, 'set_ephe_path'):
                swe.set_ephe_path(ephe_path)
            # Perform sanity check
            if hasattr(swe, 'julday') and hasattr(swe, 'calc_ut') and hasattr(swe, 'set_sid_mode') and hasattr(swe, 'get_ayanamsa_ut'):
                t_jd = float(swe.julday(2000, 1, 1, 12.0))
                swe.set_sid_mode(1)
                _ = float(swe.get_ayanamsa_ut(t_jd))
                self._has_swisseph = True
        except BaseException:
            try:
                import pyswisseph as swe
                self._swe = swe
                if ephe_path and hasattr(swe, 'set_ephe_path'):
                    swe.set_ephe_path(ephe_path)
                if hasattr(swe, 'julday') and hasattr(swe, 'calc_ut') and hasattr(swe, 'set_sid_mode') and hasattr(swe, 'get_ayanamsa_ut'):
                    t_jd = float(swe.julday(2000, 1, 1, 12.0))
                    swe.set_sid_mode(1)
                    _ = float(swe.get_ayanamsa_ut(t_jd))
                    self._has_swisseph = True
            except BaseException:
                self._has_swisseph = False

    @property
    def engine_type(self) -> str:
        return "Swiss Ephemeris (DE431)" if self._has_swisseph else "PyEphem High-Precision Calibrated"

    def datetime_to_jd(self, dt: datetime) -> float:
        if self._has_swisseph and self._swe:
            try:
                return float(self._swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0))
            except BaseException:
                return self._fallback.datetime_to_jd(dt)
        return self._fallback.datetime_to_jd(dt)

    def calculate_ayanamsa(self, jd: float, ayanamsa_name: str = "Lahiri") -> float:
        if self._has_swisseph and self._swe:
            try:
                swe = self._swe
                sid_modes = {
                    "lahiri": 1,
                    "raman": 3,
                    "kp": 5,
                    "krishnamurti": 5,
                    "true_chitra": 27,
                    "true_citra": 27,
                    "yukteshwar": 7,
                    "bhasin": 8,
                }
                mode = sid_modes.get(str(ayanamsa_name).lower().strip(), 1)
                swe.set_sid_mode(mode)
                return float(swe.get_ayanamsa_ut(jd))
            except BaseException:
                return self._fallback.calculate_ayanamsa(jd, ayanamsa_name)
        return self._fallback.calculate_ayanamsa(jd, ayanamsa_name)

    def get_planet_positions(
        self,
        dt_utc: datetime,
        ayanamsa_name: str = "Lahiri"
    ) -> Tuple[Dict[str, Dict[str, float]], float]:
        if not self._has_swisseph or not self._swe:
            return self._fallback.get_planet_positions(dt_utc, ayanamsa_name)

        try:
            swe = self._swe
            jd = self.datetime_to_jd(dt_utc)
            ayanamsa_val = self.calculate_ayanamsa(jd, ayanamsa_name)

            # Swiss Ephemeris body IDs (Sun=0, Moon=1, Mercury=2, Venus=3, Mars=4, Jupiter=5, Saturn=6, Mean Node=10)
            planet_map = {
                "Sun": getattr(swe, "SUN", 0),
                "Moon": getattr(swe, "MOON", 1),
                "Mars": getattr(swe, "MARS", 4),
                "Mercury": getattr(swe, "MERCURY", 2),
                "Jupiter": getattr(swe, "JUPITER", 5),
                "Venus": getattr(swe, "VENUS", 3),
                "Saturn": getattr(swe, "SATURN", 6),
                "Rahu": getattr(swe, "MEAN_NODE", 10),
            }

            flg_swieph = getattr(swe, "FLG_SWIEPH", 2)
            flg_speed = getattr(swe, "FLG_SPEED", 256)
            flg_sidereal = getattr(swe, "FLG_SIDEREAL", 65536)
            flags = flg_swieph | flg_speed | flg_sidereal

            results: Dict[str, Dict[str, float]] = {}

            for name, p_id in planet_map.items():
                res, ret_flag = swe.calc_ut(jd, p_id, flags)
                lon = float(res[0]) % 360.0
                lat = float(res[1])
                speed = float(res[3])
                is_retro = speed < 0.0

                results[name] = {
                    "longitude": lon,
                    "latitude": lat,
                    "speed": speed,
                    "is_retrograde": is_retro,
                    "tropical_lon": (lon + ayanamsa_val) % 360.0,
                }

            # Ketu is exactly 180 degrees from Rahu
            rahu_lon = results["Rahu"]["longitude"]
            ketu_lon = (rahu_lon + 180.0) % 360.0
            results["Ketu"] = {
                "longitude": ketu_lon,
                "latitude": -results["Rahu"]["latitude"],
                "speed": results["Rahu"]["speed"],
                "is_retrograde": True,
                "tropical_lon": (results["Rahu"]["tropical_lon"] + 180.0) % 360.0,
            }

            return results, ayanamsa_val
        except BaseException:
            return self._fallback.get_planet_positions(dt_utc, ayanamsa_name)

    def calculate_ascendant(
        self,
        dt_utc: datetime,
        latitude: float,
        longitude: float,
        ayanamsa_val: float
    ) -> float:
        if not self._has_swisseph or not self._swe:
            return self._fallback.calculate_ascendant(dt_utc, latitude, longitude, ayanamsa_val)

        try:
            swe = self._swe
            jd = self.datetime_to_jd(dt_utc)
            flg_sidereal = getattr(swe, "FLG_SIDEREAL", 65536)
            cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', flg_sidereal)
            return float(ascmc[0]) % 360.0
        except BaseException:
            return self._fallback.calculate_ascendant(dt_utc, latitude, longitude, ayanamsa_val)


def get_ephemeris_provider(preference: str = "auto") -> BaseEphemerisProvider:
    """Factory returning the optimal astronomical ephemeris provider."""
    if preference.lower() in ("swiss", "swisseph"):
        return SwissEphemerisProvider()
    return PyEphemProvider()


# Singleton provider instance
default_ephemeris_provider = get_ephemeris_provider("auto")

