"""
Astronomical Ephemeris Engine for JyotishOS.
Provides sidereal planetary longitudes, speeds, retrograde status, and combustion.
Uses PyEphem (`ephem`) with classical Ayanamsa systems (Lahiri, Raman, KP, True Chitra).
"""

import os
import math
from abc import ABC, abstractmethod
from datetime import datetime, date, time, timezone, timedelta
from typing import Dict, Tuple, Optional, List, Any
import ephem

from .constants import (
    SIGNS, SIGN_NAMES, NAKSHATRAS, EXALTATION, DEBILITATION,
    MOOLATRIKONA, OWN_SIGNS, NATURAL_FRIENDS, NATURAL_ENEMIES
)
from .models import PlanetPosition, BirthData


SUPPORTED_AYANAMSAS: Dict[str, Tuple[int, str]] = {
    "Lahiri": (1, "Chitra Paksha / Indian Govt standard (SIDM_LAHIRI)"),
    "Raman": (3, "B.V. Raman Ayanamsa (SIDM_RAMAN)"),
    "Krishnamurti": (5, "KP / K.P. Krishnamurti (SIDM_KRISHNAMURTI)"),
    "Yukteshwar": (7, "Sri Yukteshwar Giri Ayanamsa (SIDM_YUKTESHWAR)"),
    "JN_Bhasin": (8, "J.N. Bhasin Ayanamsa (SIDM_JN_BHASIN)"),
    "Fagan_Bradley": (0, "Western Sidereal Fagan-Bradley (SIDM_FAGAN_BRADLEY)"),
    "DeLuce": (2, "Robert DeLuce Ayanamsa (SIDM_DELUCE)"),
    "Usha_Shashi": (4, "Usha-Shashi Ayanamsa (SIDM_USHASHASHI)"),
    "Djwhal_Khul": (6, "Djwhal Khul Ayanamsa (SIDM_DJWHAL_KHUL)"),
    "SuryaSiddhanta": (21, "Surya Siddhanta traditional (SIDM_SURYASIDDHANTA)"),
    "SuryaSiddhanta_MSun": (22, "Surya Siddhanta with mean Sun (SIDM_SURYASIDDHANTA_MSUN)"),
    "Aryabhata": (23, "Aryabhata standard (SIDM_ARYABHATA)"),
    "Aryabhata_MSun": (24, "Aryabhata with mean Sun (SIDM_ARYABHATA_MSUN)"),
    "SS_Revati": (25, "Surya Siddhanta Revati-based (SIDM_SS_REVATI)"),
    "SS_Citra": (26, "Surya Siddhanta Citra-based (SIDM_SS_CITRA)"),
    "True_Citra": (27, "True Citra / Spica anchored at 180° sidereal (SIDM_TRUE_CITRA)"),
    "True_Revati": (28, "True Revati / Zeta Piscium at 359°50' (SIDM_TRUE_REVATI)"),
    "True_Pushya": (29, "Pushya-Paksha / PVR Narasimha Rao (SIDM_TRUE_PUSHYA)"),
    "True_Mula": (35, "True Mula / Galactic Center anchor (SIDM_TRUE_MULA)"),
    "True_Sheoran": (39, "Chandra Hari / True Sheoran Ayanamsa (SIDM_TRUE_SHEORAN)"),
    "Lahiri_1940": (43, "Lahiri 1940 standard (SIDM_LAHIRI_1940)"),
    "Lahiri_VP285": (44, "Lahiri with VP 285 epoch (SIDM_LAHIRI_VP285)"),
    "Krishnamurti_VP291": (45, "KP with VP 291 epoch (SIDM_KRISHNAMURTI_VP291)"),
    "Lahiri_ICRC": (46, "Lahiri Indian Calendar Reform Committee (SIDM_LAHIRI_ICRC)"),
}

AYANAMSA_ALIASES: Dict[str, str] = {
    "lahiri": "Lahiri",
    "chitra_paksha": "Lahiri",
    "chitrapaksha": "Lahiri",
    "default": "Lahiri",
    "indian_standard": "Lahiri",
    "raman": "Raman",
    "bv_raman": "Raman",
    "bvraman": "Raman",
    "kp": "Krishnamurti",
    "krishnamurti": "Krishnamurti",
    "kp_old": "Krishnamurti",
    "kp_new": "Krishnamurti",
    "yukteshwar": "Yukteshwar",
    "sri_yukteshwar": "Yukteshwar",
    "bhasin": "JN_Bhasin",
    "jn_bhasin": "JN_Bhasin",
    "jnbhasin": "JN_Bhasin",
    "fagan": "Fagan_Bradley",
    "fagan_bradley": "Fagan_Bradley",
    "faganbradley": "Fagan_Bradley",
    "western_sidereal": "Fagan_Bradley",
    "deluce": "DeLuce",
    "usha_shashi": "Usha_Shashi",
    "djwhal_khul": "Djwhal_Khul",
    "suryasiddhanta": "SuryaSiddhanta",
    "surya_siddhanta": "SuryaSiddhanta",
    "aryabhata": "Aryabhata",
    "true_citra": "True_Citra",
    "true_chitra": "True_Citra",
    "truechitra": "True_Citra",
    "chitra": "True_Citra",
    "citra": "True_Citra",
    "true_revati": "True_Revati",
    "revati": "True_Revati",
    "true_pushya": "True_Pushya",
    "pushya": "True_Pushya",
    "pushya_paksha": "True_Pushya",
    "true_mula": "True_Mula",
    "mula": "True_Mula",
    "true_sheoran": "True_Sheoran",
    "sheoran": "True_Sheoran",
    "chandra_hari": "True_Sheoran",
}


def resolve_ayanamsa_mode(name: Optional[str] = "Lahiri") -> Tuple[str, int]:
    """
    Resolves an ayanamsa name or alias to its (canonical_name, swiss_sidm_code).
    Raises ValueError on unknown ayanamsa name (never silently defaults to Lahiri).
    """
    if not name or not str(name).strip():
        return "Lahiri", SUPPORTED_AYANAMSAS["Lahiri"][0]

    raw = str(name).strip()
    key = raw.lower().replace("-", "_").replace(" ", "_")

    if key in AYANAMSA_ALIASES:
        canonical = AYANAMSA_ALIASES[key]
        return canonical, SUPPORTED_AYANAMSAS[canonical][0]

    for cname in SUPPORTED_AYANAMSAS:
        if cname.lower() == key:
            return cname, SUPPORTED_AYANAMSAS[cname][0]

    supported_list = ", ".join(sorted(SUPPORTED_AYANAMSAS.keys()))
    raise ValueError(f"Unknown ayanamsa '{raw}'. Supported ayanamsas are: {supported_list}")


class BaseEphemerisProvider(ABC):
    """Abstract interface for astronomical computation."""

    @abstractmethod
    def calculate_ayanamsa(self, jd: float, ayanamsa_name: str = "Lahiri") -> float:
        pass

    @abstractmethod
    def get_planet_positions(
        self,
        dt_utc: datetime,
        ayanamsa_name: str = "Lahiri",
        node_type: str = "mean",
        **kwargs
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
    """High-precision Ephemeris provider using PyEphem and IAU precession (Degraded fallback)."""

    is_degraded: bool = True
    _has_swisseph: bool = False
    ephemeris_mode: str = "PyEphem (Degraded)"
    engine_type: str = "PyEphem (Degraded)"

    def datetime_to_jd(self, dt: datetime) -> float:
        """Convert UTC datetime to Julian Day Number."""
        return float(ephem.julian_date(dt))

    def calculate_ayanamsa(self, jd: float, ayanamsa_name: str = "Lahiri") -> float:
        """
        Calculate sidereal ayanamsa in degrees.
        Strictly resolves name via resolve_ayanamsa_mode; raises ValueError on unknown name.
        """
        canonical_name, _ = resolve_ayanamsa_mode(ayanamsa_name)

        # Epoch J2000.0 = JD 2451545.0 (2000-01-01 12:00:00 UTC)
        days_from_j2000 = jd - 2451545.0
        centuries = days_from_j2000 / 36525.0

        # High-order polynomial for Lahiri precession
        # Precession ~ 50.290966 arcsec / year = 5029.0966 arcsec / century
        lahiri_base = 23.857092 + (5029.0966 * centuries + 1.1116 * centuries**2) / 3600.0

        if canonical_name == "Lahiri":
            return lahiri_base % 360.0
        elif canonical_name == "Raman":
            return (lahiri_base - 1.4463) % 360.0
        elif canonical_name == "Krishnamurti":
            return (lahiri_base - 0.0968) % 360.0
        elif canonical_name == "True_Pushya":
            return (lahiri_base - 1.1300) % 360.0
        elif canonical_name == "True_Citra":
            return (lahiri_base - 0.01707) % 360.0
        elif canonical_name == "Yukteshwar":
            return (lahiri_base - 1.3782) % 360.0
        elif canonical_name == "JN_Bhasin":
            return (lahiri_base - 1.0949) % 360.0
        elif canonical_name == "Fagan_Bradley":
            return (lahiri_base + 0.8832) % 360.0
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
        Computes True (Sphutha) Lunar Node (Rahu) using Meeus Astronomical Algorithms
        with periodic perturbation terms for high orbital precision (±1.5° oscillation).
        """
        try:
            jd = self.datetime_to_jd(dt_utc)
            t = (jd - 2451545.0) / 36525.0
            mean_rahu, _ = self.calculate_mean_lunar_nodes(jd)

            # Fundamental arguments (radians):
            # D: Mean elongation of Moon from Sun
            d_arg = math.radians(297.85036 + 445267.111480 * t - 0.0019142 * (t**2) + (t**3) / 189474.0)
            # M: Mean anomaly of the Sun
            m_sun = math.radians(357.52772 + 35999.050340 * t - 0.0001603 * (t**2) - (t**3) / 300000.0)
            # M': Mean anomaly of the Moon
            m_moon = math.radians(134.96298 + 477198.867398 * t + 0.0086972 * (t**2) + (t**3) / 56250.0)
            # F: Moon's argument of latitude
            f_arg = math.radians(93.27191 + 483202.017538 * t - 0.0036825 * (t**2) + (t**3) / 327270.0)

            # Periodic perturbation terms for True Ascending Node:
            delta_omega = (
                -1.4979 * math.sin(2.0 * (d_arg - f_arg))
                - 0.2057 * math.sin(2.0 * d_arg)
                - 0.1714 * math.sin(m_sun)
                - 0.0526 * math.sin(2.0 * f_arg)
                + 0.0402 * math.sin(2.0 * (d_arg - m_moon))
                + 0.0163 * math.sin(2.0 * d_arg - m_sun)
                - 0.0142 * math.sin(2.0 * m_moon)
            )
            true_rahu = (mean_rahu + delta_omega) % 360.0
            true_ketu = (true_rahu + 180.0) % 360.0
            return true_rahu, true_ketu
        except Exception:
            jd = self.datetime_to_jd(dt_utc)
            return self.calculate_mean_lunar_nodes(jd)

    def get_planet_positions(
        self,
        dt_utc: datetime,
        ayanamsa_name: str = "Lahiri",
        node_type: str = "mean",
        **kwargs
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
            if name == "Moon" and kwargs.get("topocentric_moon") and "latitude" in kwargs and "longitude" in kwargs:
                obs = ephem.Observer()
                obs.lat = str(kwargs["latitude"])
                obs.lon = str(kwargs["longitude"])
                obs.elevation = float(kwargs.get("elevation", 0.0))
                obs.date = ephem_date
                body.compute(obs)
                eq_topo = ephem.Equatorial(body.ra, body.dec, epoch=ephem_date)
                ecl = ephem.Ecliptic(eq_topo)
            else:
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
        # Polar latitude safeguard: when abs(lat) > 66.5, quadrant cusp projection can become singular.
        if abs(latitude) > 66.5:
            # Fallback to RAMC-perpendicular ecliptic intersection for Arctic/Antarctic circles
            asc_trop_deg = (ramc_deg + 90.0) % 360.0
        else:
            y = math.cos(ramc_rad)
            x = -(math.sin(ramc_rad) * math.cos(eps_rad) + math.tan(lat_rad) * math.sin(eps_rad))
            asc_trop_deg = math.degrees(math.atan2(y, x)) % 360.0

        # Sidereal Lagna
        asc_sid_deg = (asc_trop_deg - ayanamsa_val) % 360.0
        return asc_sid_deg


class EphemerisUnavailable(RuntimeError):
    """Raised when Swiss Ephemeris is unavailable and degraded fallback is disallowed."""
    pass


class SwissEphemerisProvider(BaseEphemerisProvider):
    """
    Swiss Ephemeris Provider.
    Primary professional astronomical engine using C-bindings (pyswisseph/swisseph/pysweph).
    Supports high-precision JPL DE431 (.se1 files) and built-in Moshier semi-analytical mode.
    """

    def __init__(self, ephe_path: Optional[str] = None):
        self._swe = None
        self._has_swisseph = False
        self._ephe_path = None
        self._ephe_files: List[str] = []
        self._fallback = PyEphemProvider()

        try:
            import swisseph as swe
            self._swe = swe
        except ImportError:
            try:
                import pyswisseph as swe
                self._swe = swe
            except ImportError:
                self._swe = None

        if self._swe is None:
            allow_degraded = os.getenv("ALLOW_DEGRADED_ENGINE", "false").strip().lower() in ("true", "1", "yes")
            if not allow_degraded:
                raise EphemerisUnavailable(
                    "pyswisseph / swisseph library is not installed and ALLOW_DEGRADED_ENGINE is false. "
                    "Please install pysweph or pyswisseph."
                )
            self._has_swisseph = False
            return

        # Resolve ephemeris path
        path_to_try = ephe_path or os.getenv("SWE_EPHE_PATH")
        if not path_to_try:
            for cand in ["ephe", "ephemeris_data", "/usr/share/ephe", "/usr/local/share/ephe"]:
                if os.path.isdir(cand):
                    path_to_try = cand
                    break

        if path_to_try and os.path.isdir(path_to_try):
            self._ephe_path = os.path.abspath(path_to_try)
            if hasattr(self._swe, "set_ephe_path"):
                self._swe.set_ephe_path(self._ephe_path)
            try:
                self._ephe_files = [f for f in os.listdir(self._ephe_path) if f.endswith(".se1")]
            except Exception:
                self._ephe_files = []
        else:
            self._ephe_path = None
            self._ephe_files = []

        self._has_swisseph = True
        self.is_degraded = False
        self.self_test_result = self.run_self_test()

    @property
    def version(self) -> str:
        return getattr(self._swe, "__version__", "unknown") if self._swe else "none"

    @property
    def ephe_path(self) -> Optional[str]:
        return self._ephe_path

    @property
    def ephe_files(self) -> List[str]:
        return list(self._ephe_files)

    @property
    def ephe_files_count(self) -> int:
        return len(self._ephe_files)

    @property
    def ephemeris_mode(self) -> str:
        if not self._has_swisseph or getattr(self, "is_degraded", False):
            return "PyEphem (Degraded)"
        return "Swiss Ephemeris (DE431)" if len(self._ephe_files) > 0 else "Swiss (Moshier)"

    @property
    def engine_type(self) -> str:
        return self.ephemeris_mode

    def _handle_degraded_or_raise(self, operation: str, error: Optional[Exception] = None):
        allow_degraded = os.getenv("ALLOW_DEGRADED_ENGINE", "false").strip().lower() in ("true", "1", "yes")
        if not allow_degraded:
            msg = f"Swiss Ephemeris error during '{operation}': {error}" if error else f"Swiss Ephemeris unavailable for '{operation}'."
            raise EphemerisUnavailable(f"{msg} Set ALLOW_DEGRADED_ENGINE=true to permit PyEphem fallback.")
        self.is_degraded = True

    def run_self_test(self) -> Dict[str, Any]:
        """Runs startup self-test verifying Sun sidereal longitude at J2000.0."""
        if not self._swe:
            return {"status": "failed", "error": "swisseph not imported"}
        try:
            swe = self._swe
            jd_j2000 = float(swe.julday(2000, 1, 1, 12.0))
            swe.set_sid_mode(getattr(swe, "SIDM_LAHIRI", 1))
            flg = getattr(swe, "FLG_SWIEPH", 2) | getattr(swe, "FLG_SPEED", 256) | getattr(swe, "FLG_SIDEREAL", 65536)
            calc_res = swe.calc_ut(jd_j2000, getattr(swe, "SUN", 0), flg)
            sun_lon = float(calc_res[0][0])
            sun_speed = float(calc_res[0][3])
            # J2000 Sun in Lahiri is ~256.515697 deg
            diff = abs(sun_lon - 256.515697)
            passed = diff < 0.001 and sun_speed > 0.95
            return {
                "status": "passed" if passed else "failed",
                "test": "Sun sidereal longitude at J2000.0 (JD 2451545.0)",
                "calculated_longitude": round(sun_lon, 6),
                "expected_longitude": 256.515697,
                "difference_degrees": round(diff, 9),
                "daily_speed": round(sun_speed, 6),
                "ayanamsa_j2000": round(float(swe.get_ayanamsa_ut(jd_j2000)), 6),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def datetime_to_jd(self, dt: datetime) -> float:
        if self._has_swisseph and self._swe:
            try:
                return float(self._swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0))
            except Exception as e:
                self._handle_degraded_or_raise("datetime_to_jd", e)
                return self._fallback.datetime_to_jd(dt)
        self._handle_degraded_or_raise("datetime_to_jd")
        return self._fallback.datetime_to_jd(dt)

    def calculate_ayanamsa(self, jd: float, ayanamsa_name: str = "Lahiri") -> float:
        canonical_name, mode_id = resolve_ayanamsa_mode(ayanamsa_name)
        if self._has_swisseph and self._swe:
            try:
                swe = self._swe
                swe.set_sid_mode(mode_id)
                return float(swe.get_ayanamsa_ut(jd))
            except Exception as e:
                self._handle_degraded_or_raise("calculate_ayanamsa", e)
                return self._fallback.calculate_ayanamsa(jd, canonical_name)
        self._handle_degraded_or_raise("calculate_ayanamsa")
        return self._fallback.calculate_ayanamsa(jd, canonical_name)

    def get_planet_positions(
        self,
        dt_utc: datetime,
        ayanamsa_name: str = "Lahiri",
        node_type: str = "mean",
        **kwargs
    ) -> Tuple[Dict[str, Dict[str, float]], float]:
        if not self._has_swisseph or not self._swe:
            self._handle_degraded_or_raise("get_planet_positions")
            return self._fallback.get_planet_positions(dt_utc, ayanamsa_name, node_type=node_type, **kwargs)

        try:
            swe = self._swe
            jd = self.datetime_to_jd(dt_utc)
            ayanamsa_val = self.calculate_ayanamsa(jd, ayanamsa_name)

            # Swiss Ephemeris body IDs
            rahu_id = getattr(swe, "TRUE_NODE", 11) if str(node_type).lower() == "true" else getattr(swe, "MEAN_NODE", 10)
            planet_map = {
                "Sun": getattr(swe, "SUN", 0),
                "Moon": getattr(swe, "MOON", 1),
                "Mars": getattr(swe, "MARS", 4),
                "Mercury": getattr(swe, "MERCURY", 2),
                "Jupiter": getattr(swe, "JUPITER", 5),
                "Venus": getattr(swe, "VENUS", 3),
                "Saturn": getattr(swe, "SATURN", 6),
                "Rahu": rahu_id,
            }

            flg_swieph = getattr(swe, "FLG_SWIEPH", 2)
            flg_speed = getattr(swe, "FLG_SPEED", 256)
            flg_sidereal = getattr(swe, "FLG_SIDEREAL", 65536)
            flags = flg_swieph | flg_speed | flg_sidereal

            # Support topocentric Moon parallax calculation when observer coordinates are supplied
            is_topo_moon = bool(kwargs.get("topocentric_moon")) and ("latitude" in kwargs and "longitude" in kwargs)
            if is_topo_moon and hasattr(swe, "set_topo"):
                obs_lat = float(kwargs["latitude"])
                obs_lon = float(kwargs["longitude"])
                obs_alt = float(kwargs.get("elevation", 0.0))
                swe.set_topo(obs_lon, obs_lat, obs_alt)

            results: Dict[str, Dict[str, float]] = {}

            for name, p_id in planet_map.items():
                p_flags = flags
                if name == "Moon" and is_topo_moon:
                    p_flags = flags | getattr(swe, "FLG_TOPOCTR", 32768)
                calc_res = swe.calc_ut(jd, p_id, p_flags)
                res = calc_res[0]
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
                "is_retrograde": results["Rahu"]["is_retrograde"],
                "tropical_lon": (results["Rahu"]["tropical_lon"] + 180.0) % 360.0,
            }

            return results, ayanamsa_val
        except Exception as e:
            if isinstance(e, EphemerisUnavailable):
                raise
            self._handle_degraded_or_raise("get_planet_positions", e)
            return self._fallback.get_planet_positions(dt_utc, ayanamsa_name, node_type=node_type, **kwargs)

    def calculate_ascendant(
        self,
        dt_utc: datetime,
        latitude: float,
        longitude: float,
        ayanamsa_val: float
    ) -> float:
        if not self._has_swisseph or not self._swe:
            self._handle_degraded_or_raise("calculate_ascendant")
            return self._fallback.calculate_ascendant(dt_utc, latitude, longitude, ayanamsa_val)

        try:
            swe = self._swe
            jd = self.datetime_to_jd(dt_utc)
            flg_sidereal = getattr(swe, "FLG_SIDEREAL", 65536)
            cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', flg_sidereal)
            return float(ascmc[0]) % 360.0
        except Exception as e:
            if isinstance(e, EphemerisUnavailable):
                raise
            self._handle_degraded_or_raise("calculate_ascendant", e)
            return self._fallback.calculate_ascendant(dt_utc, latitude, longitude, ayanamsa_val)


def get_ephemeris_provider(preference: str = "auto") -> BaseEphemerisProvider:
    """Factory returning the optimal astronomical ephemeris provider."""
    pref = str(preference).lower()
    if pref in ("pyephem", "fallback", "degraded"):
        return PyEphemProvider()
    return SwissEphemerisProvider()


def get_engine_health() -> Dict[str, Any]:
    """Returns engine health, active provider, Swiss Ephemeris version, path, and self-test."""
    provider = default_ephemeris_provider
    if isinstance(provider, SwissEphemerisProvider):
        st = provider.self_test_result if hasattr(provider, "self_test_result") else provider.run_self_test()
        return {
            "engine": "swisseph",
            "version": provider.version,
            "ephe_path": provider.ephe_path or "default (built-in Moshier)",
            "ephe_files_count": provider.ephe_files_count,
            "ephe_files_sample": provider.ephe_files[:10],
            "ephemeris_mode": provider.ephemeris_mode,
            "self_test": st.get("status", "unknown"),
            "self_test_details": st,
        }
    return {
        "engine": "pyephem",
        "version": getattr(ephem, "__version__", "unknown"),
        "ephe_path": None,
        "ephe_files_count": 0,
        "ephemeris_mode": "PyEphem (Degraded)",
        "self_test": "bypassed",
    }


# Singleton provider instance
default_ephemeris_provider = get_ephemeris_provider("auto")

