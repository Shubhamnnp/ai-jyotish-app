"""
Combustion and Planetary Orbs Engine for JyotishOS (Phase 1 Task P1-T9).
Provides configurable classical combustion orbs according to:
1. Brihat Parashara Hora Shastra (BPHS) & Surya Siddhanta (Classical default).
2. Varahamihira / Brihat Jataka tradition.
3. Custom school or practitioner configuration.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field


# Classical default combustion orbs in degrees (BPHS / Surya Siddhanta)
# Moon: 12°, Mars: 17°, Mercury: 14° (12° when retrograde), Jupiter: 11°, Venus: 10° (8° when retrograde), Saturn: 15°
BPHS_SURYA_SIDDHANTA_ORBS = {
    "direct": {
        "Moon": 12.0,
        "Mars": 17.0,
        "Mercury": 14.0,
        "Jupiter": 11.0,
        "Venus": 10.0,
        "Saturn": 15.0,
    },
    "retrograde": {
        "Mercury": 12.0,
        "Venus": 8.0,
    }
}

VARAHAMIHIRA_ORBS = {
    "direct": {
        "Moon": 12.0,
        "Mars": 17.0,
        "Mercury": 13.0,
        "Jupiter": 11.0,
        "Venus": 9.0,
        "Saturn": 15.0,
    },
    "retrograde": {
        "Mercury": 12.0,
        "Venus": 8.0,
    }
}

COMBUSTION_SCHOOL_PRESETS: Dict[str, Dict[str, Dict[str, float]]] = {
    "bphs": BPHS_SURYA_SIDDHANTA_ORBS,
    "surya_siddhanta": BPHS_SURYA_SIDDHANTA_ORBS,
    "classical": BPHS_SURYA_SIDDHANTA_ORBS,
    "varahamihira": VARAHAMIHIRA_ORBS,
    "brihat_jataka": VARAHAMIHIRA_ORBS,
}


@dataclass
class CombustionOrbConfig:
    """Configurable combustion orbs per school or practitioner."""
    school_name: str = "BPHS / Surya Siddhanta"
    direct_orbs: Dict[str, float] = field(default_factory=lambda: dict(BPHS_SURYA_SIDDHANTA_ORBS["direct"]))
    retrograde_orbs: Dict[str, float] = field(default_factory=lambda: dict(BPHS_SURYA_SIDDHANTA_ORBS["retrograde"]))

    @classmethod
    def from_school(cls, school_key: str, custom_overrides: Optional[Dict[str, float]] = None) -> "CombustionOrbConfig":
        normalized = school_key.strip().lower().replace(" ", "_").replace("/", "_")
        preset = COMBUSTION_SCHOOL_PRESETS.get(normalized, BPHS_SURYA_SIDDHANTA_ORBS)
        direct = dict(preset["direct"])
        retro = dict(preset.get("retrograde", {}))

        if custom_overrides:
            for p, orb in custom_overrides.items():
                direct[p] = float(orb)

        display_name = "Varahamihira" if "varahamihira" in normalized or "jataka" in normalized else "BPHS / Surya Siddhanta"
        return cls(
            school_name=display_name,
            direct_orbs=direct,
            retrograde_orbs=retro
        )

    def get_limit(self, planet_name: str, is_retrograde: bool = False) -> float:
        if is_retrograde and planet_name in self.retrograde_orbs:
            return self.retrograde_orbs[planet_name]
        return self.direct_orbs.get(planet_name, 10.0)


class CombustionCalculator:
    """Calculates planetary combustion (Astangata) relative to the Sun."""

    @staticmethod
    def calculate_angular_separation(planet_lon: float, sun_lon: float) -> float:
        """Computes minimal longitudinal difference between planet and Sun (0 to 180 deg)."""
        diff = abs((planet_lon % 360.0) - (sun_lon % 360.0))
        if diff > 180.0:
            diff = 360.0 - diff
        return diff

    @classmethod
    def check_combustion(
        cls,
        planet_name: str,
        planet_lon: float,
        sun_lon: float,
        is_retrograde: bool = False,
        config: Optional[CombustionOrbConfig] = None
    ) -> bool:
        if planet_name in ("Sun", "Rahu", "Ketu"):
            return False

        cfg = config or CombustionOrbConfig()
        diff = cls.calculate_angular_separation(planet_lon, sun_lon)
        limit = cfg.get_limit(planet_name, is_retrograde)
        return diff <= limit

    @classmethod
    def get_combustion_detail(
        cls,
        planet_name: str,
        planet_lon: float,
        sun_lon: float,
        is_retrograde: bool = False,
        config: Optional[CombustionOrbConfig] = None
    ) -> Dict[str, Any]:
        cfg = config or CombustionOrbConfig()
        if planet_name in ("Sun", "Rahu", "Ketu"):
            return {
                "planet": planet_name,
                "is_combust": False,
                "separation_degrees": 0.0,
                "orb_limit": 0.0,
                "school": cfg.school_name,
                "is_retrograde": is_retrograde,
            }

        diff = cls.calculate_angular_separation(planet_lon, sun_lon)
        limit = cfg.get_limit(planet_name, is_retrograde)
        is_combust = diff <= limit

        return {
            "planet": planet_name,
            "is_combust": is_combust,
            "separation_degrees": round(diff, 4),
            "orb_limit": limit,
            "school": cfg.school_name,
            "is_retrograde": is_retrograde,
        }
