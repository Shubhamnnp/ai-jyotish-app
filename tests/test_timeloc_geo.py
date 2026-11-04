"""
Unit Tests for Geocoding and Timezone Resolution (Phase 1 Task P1-T8).
Verifies:
1. Coordinate boundary validation.
2. Offline timezone resolution from coordinates via timezonefinder.
3. City lookup table.
4. Fallback chain behavior.
"""

import pytest
from src.jyotish.timeloc.geo import GeoLocationService, KNOWN_CITIES


def test_coordinate_validation():
    """Verify out-of-range coordinates raise ValueError."""
    # Invalid latitude
    with pytest.raises(ValueError, match="Invalid latitude"):
        GeoLocationService.validate_coordinates(95.0, 77.0)

    with pytest.raises(ValueError, match="Invalid latitude"):
        GeoLocationService.validate_coordinates(-91.0, 77.0)

    # Invalid longitude
    with pytest.raises(ValueError, match="Invalid longitude"):
        GeoLocationService.validate_coordinates(28.0, 185.0)

    with pytest.raises(ValueError, match="Invalid longitude"):
        GeoLocationService.validate_coordinates(28.0, -181.0)

    # Valid coordinates pass
    GeoLocationService.validate_coordinates(28.6139, 77.2090)
    GeoLocationService.validate_coordinates(-33.8688, 151.2093)


def test_timezonefinder_resolution():
    """Verify offline timezone resolution across various continents."""
    # Delhi, India
    assert GeoLocationService.resolve_timezone_for_coordinates(28.6139, 77.2090) == "Asia/Kolkata"

    # London, UK
    assert GeoLocationService.resolve_timezone_for_coordinates(51.5074, -0.1278) == "Europe/London"

    # New York, USA
    assert GeoLocationService.resolve_timezone_for_coordinates(40.7128, -74.0060) == "America/New_York"

    # Tokyo, Japan
    assert GeoLocationService.resolve_timezone_for_coordinates(35.6762, 139.6503) == "Asia/Tokyo"

    # Sydney, Australia
    assert GeoLocationService.resolve_timezone_for_coordinates(-33.8688, 151.2093) == "Australia/Sydney"


def test_city_catalog_lookup():
    """Verify lookup from offline city catalog."""
    res_lko = GeoLocationService.resolve_location(city="Lucknow")
    assert res_lko.resolution_source == "city_table"
    assert res_lko.timezone == "Asia/Kolkata"
    assert abs(res_lko.latitude - 26.8467) < 0.001

    res_nyc = GeoLocationService.resolve_location(city="New York")
    assert res_nyc.resolution_source == "city_table"
    assert res_nyc.timezone == "America/New_York"


def test_manual_override_and_fallback_chain():
    """Verify manual coordinate and timezone overrides."""
    # Coordinates without timezone: timezonefinder resolves
    res_coords = GeoLocationService.resolve_location(latitude=19.0760, longitude=72.8777)
    assert res_coords.resolution_source == "timezonefinder"
    assert res_coords.timezone == "Asia/Kolkata"

    # Explicit manual override
    res_manual = GeoLocationService.resolve_location(
        latitude=19.0760,
        longitude=72.8777,
        timezone="Custom/Zone"
    )
    assert res_manual.resolution_source == "manual"
    assert res_manual.timezone == "Custom/Zone"

    # Unknown city without coordinates raises ValueError
    with pytest.raises(ValueError, match="not found in offline catalog"):
        GeoLocationService.resolve_location(city="AtlantisHiddenCity")


def test_api_timeloc_endpoint():
    """Verify FastAPI endpoint /api/v1/astronomy/timeloc/resolve."""
    from fastapi.testclient import TestClient
    from src.jyotish.api.main import app

    client = TestClient(app)
    # 1. Resolve city
    res_city = client.get("/api/v1/astronomy/timeloc/resolve?city=Varanasi")
    assert res_city.status_code == 200
    data_city = res_city.json()
    assert data_city["city"] == "Varanasi"
    assert data_city["timezone"] == "Asia/Kolkata"

    # 2. Resolve coords
    res_geo = client.get("/api/v1/astronomy/timeloc/resolve?latitude=51.5074&longitude=-0.1278")
    assert res_geo.status_code == 200
    data_geo = res_geo.json()
    assert data_geo["timezone"] == "Europe/London"

    # 3. Invalid coords
    res_bad = client.get("/api/v1/astronomy/timeloc/resolve?latitude=999.0&longitude=0.0")
    assert res_bad.status_code == 400

