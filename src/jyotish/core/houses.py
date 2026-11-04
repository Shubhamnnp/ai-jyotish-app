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
import swisseph as swe

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


def point_in_arc(point: float, start: float, end: float) -> bool:
    """Returns True if point is on circular arc [start, end) on 0-360 wheel."""
    total_arc = (end - start) % 360.0
    p_offset = (point - start) % 360.0
    return 0.0 <= p_offset < total_arc


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

        try:
            cusps_tuple, ascmc = swe.houses_ex(jd, latitude, longitude, hsys_code, flg_sidereal)
        except Exception as e:
            # Fallback to Equal if quadrant computation fails
            cusps_tuple, ascmc = swe.houses_ex(jd, latitude, longitude, b'E', flg_sidereal)
            polar_adjusted = True
            warning = f"Swiss houses_ex failed for '{canonical_name}' ({e}); fell back to Equal house system."

        # cusps_tuple has length 13: index 0 dummy, index 1..12 are houses 1..12
        raw_cusps = [float(cusps_tuple[h]) % 360.0 for h in range(1, 13)]
        asc = float(ascmc[0]) % 360.0
        mc = float(ascmc[1]) % 360.0
        armc = float(ascmc[2]) % 360.0
        vertex = float(ascmc[3]) % 360.0

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
