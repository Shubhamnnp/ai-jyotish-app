"""
Geocoding and Timezone Resolution Service for JyotishOS (Phase 1 Task P1-T8).
Features:
1. Deterministic offline resolution of latitude/longitude to IANA timezone via `timezonefinder`.
2. Curated offline city directory of major Indian and global astrological locations.
3. Fallback chain: city lookup table -> coordinates lookup via timezonefinder -> manual override.
4. Strict coordinate boundary validation (-90 <= lat <= 90, -180 <= lon <= 180).
"""

from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass
import timezonefinder


@dataclass
class GeoLocationResult:
    city: str
    latitude: float
    longitude: float
    timezone: str
    elevation: float = 0.0
    country: str = "India"
    resolution_source: str = "city_table"  # "city_table", "timezonefinder", "manual"


# Curated offline reference catalog for fast offline lookups
KNOWN_CITIES: Dict[str, Dict[str, Any]] = {
    "new delhi": {"lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata", "country": "India"},
    "delhi": {"lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata", "country": "India"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata", "country": "India"},
    "bombay": {"lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata", "country": "India"},
    "kolkata": {"lat": 22.5726, "lon": 88.3639, "tz": "Asia/Kolkata", "country": "India"},
    "calcutta": {"lat": 22.5726, "lon": 88.3639, "tz": "Asia/Kolkata", "country": "India"},
    "chennai": {"lat": 13.0827, "lon": 80.2707, "tz": "Asia/Kolkata", "country": "India"},
    "madras": {"lat": 13.0827, "lon": 80.2707, "tz": "Asia/Kolkata", "country": "India"},
    "bengaluru": {"lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata", "country": "India"},
    "bangalore": {"lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata", "country": "India"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "tz": "Asia/Kolkata", "country": "India"},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "tz": "Asia/Kolkata", "country": "India"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "tz": "Asia/Kolkata", "country": "India"},
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "tz": "Asia/Kolkata", "country": "India"},
    "lucknow": {"lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata", "country": "India"},
    "varanasi": {"lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata", "country": "India"},
    "kashi": {"lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata", "country": "India"},
    "patna": {"lat": 25.5941, "lon": 85.1376, "tz": "Asia/Kolkata", "country": "India"},
    "ujjain": {"lat": 23.1765, "lon": 75.7885, "tz": "Asia/Kolkata", "country": "India"},
    "haridwar": {"lat": 29.9457, "lon": 78.1642, "tz": "Asia/Kolkata", "country": "India"},
    "rishikesh": {"lat": 30.0869, "lon": 78.2676, "tz": "Asia/Kolkata", "country": "India"},
    "ayodhya": {"lat": 26.7922, "lon": 82.1998, "tz": "Asia/Kolkata", "country": "India"},
    "mathura": {"lat": 27.4924, "lon": 77.6737, "tz": "Asia/Kolkata", "country": "India"},
    "tirupati": {"lat": 13.6288, "lon": 79.4192, "tz": "Asia/Kolkata", "country": "India"},
    "madurai": {"lat": 9.9252, "lon": 78.1198, "tz": "Asia/Kolkata", "country": "India"},
    "puri": {"lat": 19.8135, "lon": 85.8312, "tz": "Asia/Kolkata", "country": "India"},
    "guwahati": {"lat": 26.1445, "lon": 91.7362, "tz": "Asia/Kolkata", "country": "India"},
    "chandigarh": {"lat": 30.7333, "lon": 76.7794, "tz": "Asia/Kolkata", "country": "India"},
    "bhopal": {"lat": 23.2599, "lon": 77.4126, "tz": "Asia/Kolkata", "country": "India"},
    "surat": {"lat": 21.1702, "lon": 72.8311, "tz": "Asia/Kolkata", "country": "India"},
    "nagpur": {"lat": 21.1458, "lon": 79.0882, "tz": "Asia/Kolkata", "country": "India"},
    "indore": {"lat": 22.7196, "lon": 75.8577, "tz": "Asia/Kolkata", "country": "India"},
    "shimla": {"lat": 31.1048, "lon": 77.1734, "tz": "Asia/Kolkata", "country": "India"},
    "srinagar": {"lat": 34.0837, "lon": 74.7973, "tz": "Asia/Kolkata", "country": "India"},
    "kochi": {"lat": 9.9312, "lon": 76.2673, "tz": "Asia/Kolkata", "country": "India"},
    "thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366, "tz": "Asia/Kolkata", "country": "India"},
    # Major global cities
    "london": {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "country": "United Kingdom"},
    "new york": {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "country": "United States"},
    "san francisco": {"lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles", "country": "United States"},
    "los angeles": {"lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "country": "United States"},
    "chicago": {"lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago", "country": "United States"},
    "toronto": {"lat": 43.6532, "lon": -79.3832, "tz": "America/Toronto", "country": "Canada"},
    "dubai": {"lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai", "country": "United Arab Emirates"},
    "singapore": {"lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore", "country": "Singapore"},
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo", "country": "Japan"},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney", "country": "Australia"},
    "melbourne": {"lat": -37.8136, "lon": 144.9631, "tz": "Australia/Melbourne", "country": "Australia"},
    "paris": {"lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris", "country": "France"},
    "berlin": {"lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin", "country": "Germany"},
    "cairo": {"lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo", "country": "Egypt"},
    "johannesburg": {"lat": -26.2041, "lon": 28.0473, "tz": "Africa/Johannesburg", "country": "South Africa"},
    "moscow": {"lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow", "country": "Russia"},
}


class GeoLocationService:
    """Offline deterministic geocoding and IANA timezone resolution service."""

    _tf: Optional[timezonefinder.TimezoneFinder] = None

    @classmethod
    def _get_tf(cls) -> timezonefinder.TimezoneFinder:
        if cls._tf is None:
            cls._tf = timezonefinder.TimezoneFinder()
        return cls._tf

    @classmethod
    def validate_coordinates(cls, latitude: float, longitude: float) -> None:
        """Validates that latitude and longitude are within standard physical ranges."""
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Invalid latitude {latitude}. Latitude must be between -90.0 and 90.0 degrees.")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Invalid longitude {longitude}. Longitude must be between -180.0 and 180.0 degrees.")

    @classmethod
    def resolve_timezone_for_coordinates(cls, latitude: float, longitude: float) -> Optional[str]:
        """Resolves latitude and longitude to IANA timezone name via timezonefinder."""
        cls.validate_coordinates(latitude, longitude)
        tf = cls._get_tf()
        return tf.timezone_at(lat=latitude, lng=longitude)

    @classmethod
    def resolve_location(
        cls,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: Optional[str] = None,
        elevation: float = 0.0,
    ) -> GeoLocationResult:
        """
        Resolves location and timezone following the PRD fallback chain:
        1. Explicit manual lat/lon with timezone override.
        2. Known city lookup table.
        3. Coordinates resolution to IANA timezone via timezonefinder.
        """
        # Case 1: Manual coordinates provided
        if latitude is not None and longitude is not None:
            cls.validate_coordinates(latitude, longitude)
            if timezone:
                return GeoLocationResult(
                    city=city or f"({latitude:.4f}, {longitude:.4f})",
                    latitude=latitude,
                    longitude=longitude,
                    timezone=timezone,
                    elevation=elevation,
                    resolution_source="manual"
                )

            # Resolve timezone via timezonefinder
            resolved_tz = cls.resolve_timezone_for_coordinates(latitude, longitude)
            if resolved_tz:
                return GeoLocationResult(
                    city=city or f"({latitude:.4f}, {longitude:.4f})",
                    latitude=latitude,
                    longitude=longitude,
                    timezone=resolved_tz,
                    elevation=elevation,
                    resolution_source="timezonefinder"
                )
            # Default fallback for unassigned marine/border coordinates
            return GeoLocationResult(
                city=city or f"({latitude:.4f}, {longitude:.4f})",
                latitude=latitude,
                longitude=longitude,
                timezone="Asia/Kolkata",
                elevation=elevation,
                resolution_source="fallback"
            )

        # Case 2: City name provided without coordinates
        if city:
            c_key = city.strip().lower()
            if c_key in KNOWN_CITIES:
                entry = KNOWN_CITIES[c_key]
                return GeoLocationResult(
                    city=city.title(),
                    latitude=entry["lat"],
                    longitude=entry["lon"],
                    timezone=timezone or entry["tz"],
                    elevation=elevation,
                    country=entry.get("country", "India"),
                    resolution_source="city_table"
                )
            raise ValueError(f"City '{city}' not found in offline catalog. Please supply explicit latitude and longitude coordinates.")

        raise ValueError("Either a city name or latitude/longitude coordinates must be provided.")
