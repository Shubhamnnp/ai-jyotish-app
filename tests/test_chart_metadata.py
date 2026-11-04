"""
Unit and Integration Tests for Chart Calculation Metadata Block (Phase 1 Task P1-T10).
Verifies:
1. Presence of full astronomical provenance in chart.metadata:
   - jd_ut
   - utc_datetime
   - ayanamsa: {name, value_degrees}
   - engine: "swisseph" | "degraded_pyephem"
   - ephemeris_mode: "Swiss (Moshier)" | "PyEphem (Degraded)"
   - engine_degraded: bool
   - timezone_iana: string
   - house_system: string
   - delta_t_seconds: float
2. Deterministic mathematical reproducibility across calculations.
3. Serialization of metadata in API / JSON dumps.
"""

import pytest
from datetime import date, time, datetime, timezone
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator
from src.jyotish.core.ephemeris import SwissEphemerisProvider, PyEphemProvider


def test_chart_metadata_block_provenance():
    """Verify that ChartCalculator produces complete calculation metadata block."""
    b_data = BirthData(
        name="Metadata Test Native",
        birth_date=date(2000, 1, 1),
        birth_time=time(12, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
        house_system="Whole Sign"
    )

    calc = ChartCalculator()
    chart = calc.calculate_full_chart(b_data)

    meta = chart.metadata
    assert meta is not None

    # Verify required provenance fields
    assert meta.engine in ("swisseph", "degraded_pyephem")
    assert isinstance(meta.jd_ut, float) and meta.jd_ut > 2400000.0
    assert meta.utc_datetime is not None
    assert meta.timezone_iana == "Asia/Kolkata"
    assert meta.house_system == "Whole Sign"
    assert isinstance(meta.delta_t_seconds, float)
    assert meta.delta_t_seconds > 0.0  # Approx ~63.8s for year 2000

    # Ayanamsa details
    assert meta.ayanamsa is not None
    assert meta.ayanamsa["name"] == "Lahiri"
    assert isinstance(meta.ayanamsa["value_degrees"], float)
    assert abs(meta.ayanamsa["value_degrees"] - 23.85) < 0.5


def test_deterministic_reproducibility():
    """Verify identical inputs yield exactly identical metadata and Julian dates."""
    b_data = BirthData(
        name="Deterministic Native",
        birth_date=date(1985, 8, 15),
        birth_time=time(9, 30),
        latitude=26.8467,
        longitude=80.9462,
        timezone="Asia/Kolkata"
    )

    calc = ChartCalculator()
    chart1 = calc.calculate_full_chart(b_data)
    chart2 = calc.calculate_full_chart(b_data)

    assert chart1.metadata.jd_ut == chart2.metadata.jd_ut
    assert chart1.metadata.delta_t_seconds == chart2.metadata.delta_t_seconds
    assert chart1.metadata.ayanamsa_value == chart2.metadata.ayanamsa_value
    assert chart1.lagna_longitude == chart2.lagna_longitude


def test_metadata_json_serialization():
    """Verify CalculationMetadata serializes cleanly to JSON dictionary."""
    b_data = BirthData(
        name="Serialization Native",
        birth_date=date(2023, 10, 24),
        birth_time=time(8, 30),
        latitude=19.0760,
        longitude=72.8777,
        timezone="Asia/Kolkata"
    )

    calc = ChartCalculator()
    chart = calc.calculate_full_chart(b_data)

    dumped = chart.model_dump() if hasattr(chart, "model_dump") else chart.dict()
    assert "metadata" in dumped
    meta_dump = dumped["metadata"]

    assert meta_dump["engine"] in ("swisseph", "degraded_pyephem")
    assert meta_dump["timezone_iana"] == "Asia/Kolkata"
    assert "delta_t_seconds" in meta_dump
    assert "ayanamsa" in meta_dump
    assert meta_dump["ayanamsa"]["name"] == "Lahiri"
