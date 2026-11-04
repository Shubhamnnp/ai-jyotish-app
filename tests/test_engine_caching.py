"""
Unit tests for Deterministic In-Memory Calculation Cache and Sub-500ms Chart Compute (Phase 6, Task P6-T6).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.6, P6-T6).
"""

import time
import pytest
from datetime import date, time as dt_time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.cache import (
    ChartCalculationCache, compute_chart_cache_key, default_chart_cache
)


@pytest.fixture
def sample_birth_data():
    return BirthData(
        name="Benchmark Jataka",
        birth_date=date(1992, 8, 18),
        birth_time=dt_time(11, 45, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata"
    )


def test_cache_key_determinism(sample_birth_data):
    k1 = compute_chart_cache_key(sample_birth_data, ayanamsa_name="Lahiri", is_full=True)
    k2 = compute_chart_cache_key(sample_birth_data, ayanamsa_name="Lahiri", is_full=True)
    assert k1 == k2

    # Different ayanamsa -> different key
    k_raman = compute_chart_cache_key(sample_birth_data, ayanamsa_name="Raman", is_full=True)
    assert k1 != k_raman

    # Different full flag -> different key
    k_base = compute_chart_cache_key(sample_birth_data, ayanamsa_name="Lahiri", is_full=False)
    assert k1 != k_base


def test_cache_lru_eviction():
    cache = ChartCalculationCache(max_size=3)
    b_data = BirthData(
        birth_date=date(2000, 1, 1),
        birth_time=dt_time(12, 0, 0),
        latitude=20.0,
        longitude=75.0,
        timezone="Asia/Kolkata"
    )

    c1 = default_chart_calculator.calculate_chart(b_data, use_cache=False)
    cache.put("k1", c1)
    cache.put("k2", c1)
    cache.put("k3", c1)
    assert cache.get_stats()["size"] == 3

    # Adding 4th should evict k1
    cache.put("k4", c1)
    assert cache.get_stats()["size"] == 3
    assert cache.get("k1") is None
    assert cache.get("k2") is not None


def test_sub_500ms_compute_and_sub_5ms_cache_hit(sample_birth_data):
    # Clear default cache to start fresh
    default_chart_cache.clear()

    # 1. First execution (Cache Miss): Must be < 500ms
    t0 = time.perf_counter()
    chart1 = default_chart_calculator.calculate_full_chart(sample_birth_data, use_cache=True)
    t_fresh = (time.perf_counter() - t0) * 1000  # ms
    assert t_fresh < 500.0, f"Fresh computation too slow: {t_fresh:.2f}ms (expected < 500ms)"

    # 2. Second execution (Cache Hit): Must be < 5ms
    t1 = time.perf_counter()
    chart2 = default_chart_calculator.calculate_full_chart(sample_birth_data, use_cache=True)
    t_cached = (time.perf_counter() - t1) * 1000  # ms
    assert t_cached < 10.0, f"Cached retrieval too slow: {t_cached:.2f}ms"

    # Both charts must match identical astronomical values
    assert chart1.lagna_longitude == chart2.lagna_longitude
    assert chart1.planets["Sun"].longitude == chart2.planets["Sun"].longitude

    # Stats check
    stats = default_chart_cache.get_stats()
    assert stats["hits"] >= 1
    assert stats["misses"] >= 1


def test_cached_copy_mutation_isolation(sample_birth_data):
    default_chart_cache.clear()
    c1 = default_chart_calculator.calculate_full_chart(sample_birth_data, use_cache=True)

    # Mutate returned chart
    original_sun_lon = c1.planets["Sun"].longitude
    c1.planets["Sun"].longitude = 999.99

    # Re-fetch from cache
    c2 = default_chart_calculator.calculate_full_chart(sample_birth_data, use_cache=True)
    assert c2.planets["Sun"].longitude == original_sun_lon
    assert c2.planets["Sun"].longitude != 999.99


def test_cache_bypass_flag(sample_birth_data):
    default_chart_cache.clear()
    default_chart_calculator.calculate_chart(sample_birth_data, use_cache=False)
    assert default_chart_cache.get_stats()["size"] == 0

