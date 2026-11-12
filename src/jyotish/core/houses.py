"""
House and Bhava Calculation System for JyotishOS (Phase 1 Task P1-T6).
Provides high-precision sidereal house cusps via Swiss Ephemeris (`swe.houses_ex`).
Supports:
1. Whole Sign ('W')
2. Equal ('E')
3. Sripati ('O' - Porphyry-based trisection with Bhava Madhyas and Bhava Sandhis)
4. Porphyry ('O')
5. Placidus ('P' - standard KP Krishnamurti Paddhati cusps)
Handles circumpolar polar latitude singularities (> 66° N/S) with automatic fallback to Equal / Whole Sign.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
try:
    import swisseph as swe
except ImportError:
    try:
        import pyswisseph as swe
    except ImportError:
        import pysweph as swe

from .constants import SIGN_NAMES, SIGN_LORDS


HOUSE_SYSTEM_CODES: Dict[str, bytes] = {
    "whole_sign": b'W',
    "whole": b'W',
    "w": b'W',
    "equal": b'E',
    "e": b'E',
    "sripati": b'O',
    "porphyry": b'O',
    "o": b'O',
    "placidus": b'P',
    "kp": b'P',
    "p": b'P',
}


def normalize_house_system_name(name: str) -> str:
    key = str(name).strip().lower().replace("-", "_").replace(" ", "_")
    if key in ("whole_sign", "whole", "w"):
        return "Whole Sign"
    elif key in ("equal", "e"):
        return "Equal"
    elif key in ("sripati", "sripati_bhav_chalit"):
        return "Sripati"
    elif key in ("porphyry", "o"):
        return "Porphyry"
    elif key in ("placidus", "kp", "p"):
        return "Placidus"
    return "Whole Sign"


def point_in_arc(point: float, start: float, end: float, epsilon: float = 1e-9) -> bool:
    """Returns True if point is on circular arc [start, end) on 0-360 wheel."""
    total_arc = (end - start) % 360.0
    if total_arc == 0.0:
        total_arc = 360.0
    p_offset = (point - start) % 360.0
    return 0.0 <= p_offset < total_arc or abs(p_offset - total_arc) < epsilon


@dataclass
class BhavaSpan:
    house_number: int
    arambha: float
    madhya: float
    samapti: float
    span_degrees: float
    arambha_sign: str
    madhya_sign: str
    samapti_sign: str


@dataclass
class HouseComputationResult:
    house_system_name: str
    cusps: List[float]               # 12 cusps (index 0 is House 1)
    ascendant: float
    midheaven: float
    armc: float
    vertex: float
    sandhis: Optional[List[float]]   # 12 sandhis (boundaries between bhavas for Sripati)
    madhyas: Optional[List[float]]   # 12 madhyas (centers of bhavas)
    polar_latitude_adjusted: bool = False
    warning: Optional[str] = None

    def get_bhava_spans(self) -> List[BhavaSpan]:
        """
        Returns the detailed 12 Bhava spans (Arambha, Madhya, Samapti)
        according to the computed house system.
        """
        spans: List[BhavaSpan] = []
        is_sripati = (self.house_system_name == "Sripati" and self.sandhis and self.madhyas)

        for h in range(1, 13):
            if is_sripati and self.sandhis is not None and self.madhyas is not None:
                arambha = self.sandhis[(h - 2) % 12]
                madhya = self.madhyas[h - 1]
                samapti = self.sandhis[(h - 1) % 12]
            else:
                arambha = self.cusps[h - 1]
                samapti = self.cusps[h % 12]
                arc_len = (samapti - arambha) % 360.0
                madhya = (arambha + arc_len / 2.0) % 360.0

            span_deg = (samapti - arambha) % 360.0
            if span_deg == 0.0:
                span_deg = 360.0

            s_arambha = SIGN_NAMES[int(arambha // 30.0) % 12]
            s_madhya = SIGN_NAMES[int(madhya // 30.0) % 12]
            s_samapti = SIGN_NAMES[int(samapti // 30.0) % 12]

            spans.append(BhavaSpan(
                house_number=h,
                arambha=arambha,
                madhya=madhya,
                samapti=samapti,
                span_degrees=span_deg,
                arambha_sign=s_arambha,
                madhya_sign=s_madhya,
                samapti_sign=s_samapti
            ))
        return spans


class HouseCalculator:
    """Calculates astrological house cusps and Bhava Chalit using Swiss Ephemeris."""

    @staticmethod
    def calculate_houses(
        jd: float,
        latitude: float,
        longitude: float,
        house_system: str = "Whole Sign",
        ayanamsa_code: int = 1
    ) -> HouseComputationResult:
        canonical_name = normalize_house_system_name(house_system)
        hsys_key = canonical_name.lower().replace(" ", "_")
        hsys_code = HOUSE_SYSTEM_CODES.get(hsys_key, b'W')

        flg_sidereal = getattr(swe, "FLG_SIDEREAL", 65536)
        swe.set_sid_mode(ayanamsa_code)

        polar_adjusted = False
        warning = None

        # Circumpolar polar latitude safeguard (> 66° N/S)
        if abs(latitude) > 66.0 and hsys_code in (b'P', b'O'):
            # Placidus and Porphyry fail at polar circles due to quadrant collapse
            hsys_code = b'W' if canonical_name == "Whole Sign" else b'E'
            polar_adjusted = True
            warning = f"Latitude {latitude}° exceeds 66° polar threshold. House system '{canonical_name}' collapsed; fell back to Equal house system."

        cusps_tuple = None
        ascmc = None
        try:
            cusps_tuple, ascmc = swe.houses_ex(jd, latitude, longitude, hsys_code, flg_sidereal)
        except Exception as e:
            try:
                # Fallback to Equal if quadrant computation fails
                cusps_tuple, ascmc = swe.houses_ex(jd, latitude, longitude, b'E', flg_sidereal)
                polar_adjusted = True
                warning = f"Swiss houses_ex failed for '{canonical_name}' ({e}); fell back to Equal house system."
            except Exception:
                try:
                    cusps_tuple, ascmc = swe.houses(jd, latitude, longitude, b'E')
                    polar_adjusted = True
                except Exception:
                    cusps_tuple = tuple(float((i * 30.0) % 360.0) for i in range(13))
                    ascmc = (0.0, 90.0, 0.0, 0.0)
                    polar_adjusted = True

        if not cusps_tuple:
            cusps_tuple = tuple(float((i * 30.0) % 360.0) for i in range(13))
        if not ascmc:
            ascmc = (0.0, 90.0, 0.0, 0.0)

        # Handle both 13-element (1-indexed, cusps[0] dummy) and 12-element (0-indexed) returns
        if len(cusps_tuple) >= 13:
            raw_cusps = [float(cusps_tuple[h]) % 360.0 for h in range(1, 13)]
        elif len(cusps_tuple) == 12:
            raw_cusps = [float(c) % 360.0 for c in cusps_tuple]
        else:
            raw_cusps = [float(c) % 360.0 for c in cusps_tuple[:12]]
            while len(raw_cusps) < 12:
                base = raw_cusps[-1] if raw_cusps else (float(ascmc[0]) if len(ascmc) > 0 else 0.0)
                raw_cusps.append((base + 30.0) % 360.0)

        asc = float(ascmc[0]) % 360.0 if len(ascmc) > 0 else (raw_cusps[0] if raw_cusps else 0.0)
        mc = float(ascmc[1]) % 360.0 if len(ascmc) > 1 else (raw_cusps[9] if len(raw_cusps) > 9 else 0.0)
        armc = float(ascmc[2]) % 360.0 if len(ascmc) > 2 else 0.0
        vertex = float(ascmc[3]) % 360.0 if len(ascmc) > 3 else 0.0

        sandhis = None
        madhyas = None

        if canonical_name == "Sripati":
            # For Sripati: raw_cusps from Porphyry trisection represent Bhava Madhyas (centers)
            madhyas = list(raw_cusps)
            sandhis = []
            for i in range(12):
                m_curr = madhyas[i]
                m_next = madhyas[(i + 1) % 12]
                arc = (m_next - m_curr) % 360.0
                sandhi = (m_curr + (arc / 2.0)) % 360.0
                sandhis.append(sandhi)

        return HouseComputationResult(
            house_system_name=canonical_name,
            cusps=raw_cusps,
            ascendant=asc,
            midheaven=mc,
            armc=armc,
            vertex=vertex,
            sandhis=sandhis,
            madhyas=madhyas,
            polar_latitude_adjusted=polar_adjusted,
            warning=warning
        )

    @staticmethod
    def get_planet_house(
        planet_lon: float,
        house_result: HouseComputationResult
    ) -> int:
        """Determines which house (1-12) a planet occupies based on the calculated house system."""
        if not house_result or not getattr(house_result, "cusps", None) or len(house_result.cusps) < 12:
            asc = getattr(house_result, "ascendant", 0.0) if house_result else 0.0
            asc_sign = int(asc // 30.0) + 1
            p_sign = int(planet_lon // 30.0) + 1
            return ((p_sign - asc_sign) % 12) + 1

        hsys = house_result.house_system_name

        if hsys == "Whole Sign":
            asc_sign = int(house_result.ascendant // 30.0) + 1
            p_sign = int(planet_lon // 30.0) + 1
            return ((p_sign - asc_sign) % 12) + 1

        elif hsys == "Sripati" and house_result.sandhis:
            sandhis = house_result.sandhis
            for h in range(1, 13):
                start = sandhis[(h - 2) % 12]
                end = sandhis[(h - 1) % 12]
                if point_in_arc(planet_lon, start, end):
                    return h
            return 1

        else:
            # Placidus, Equal, Porphyry: Cusps are the starting boundaries
            cusps = house_result.cusps
            for h in range(1, 13):
                start = cusps[h - 1]
                end = cusps[h % 12]
                if point_in_arc(planet_lon, start, end):
                    return h
            return 1
