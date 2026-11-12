"""
Test suite for Shodashavarga Hardening (Phase 3 Task 5).
Verifies:
1. Canonical 16 Shodashavarga generation.
2. D60 Shashtiamsha deity mappings (odd signs direct, even signs reverse).
3. D60 Lagna deity and benefic/malefic classification.
4. Classical Vaisheshikamsa dignity tally according to BPHS Ch. 6.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.varga import (
    VargaCalculator,
    SHODASHAVARGA_CODES,
    D60_DEITIES,
    D60_MALEFIC_INDICES,
    VAISHESHIKAMSA_BENCHMARKS
)


@pytest.fixture
def test_chart():
    bdata = BirthData(
        name="Shodashavarga Benchmark",
        birth_date=date(1985, 11, 23),
        birth_time=time(8, 15, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_canonical_16_shodashavarga(test_chart):
    """Verify that calculate_all_shodashavarga returns exactly the 16 classical Parashari vargas."""
    vargas = VargaCalculator.calculate_all_shodashavarga(test_chart)
    assert len(vargas) == 16
    for code in SHODASHAVARGA_CODES:
        assert code in vargas, f"Missing Shodashavarga: {code}"
        vc = vargas[code]
        assert vc.varga_code == code
        assert 1 <= vc.lagna_sign_id <= 12
        assert len(vc.planets) >= 7


def test_d60_deities_odd_and_even_signs(test_chart):
    """
    Verify D60 deity assignment:
    - Odd signs: direct order (0 = Ghora, 59 = Chandrarekha)
    - Even signs: reverse order (0 = Chandrarekha, 59 = Ghora)
    """
    d60 = VargaCalculator.calculate_d60(test_chart)
    assert d60.varga_code == "D60"
    assert d60.lagna_deity is not None
    assert isinstance(d60.lagna_is_benefic_deity, bool)

    # Check lagna deity logic
    lagna_sign_id = test_chart.lagna_sign_id
    lagna_deg = test_chart.lagna_degree
    part = min(59, int(lagna_deg // 0.5))
    is_odd = (lagna_sign_id % 2 != 0)
    expected_idx = part if is_odd else (59 - part)
    assert d60.lagna_deity == D60_DEITIES[expected_idx]
    assert d60.lagna_is_benefic_deity == (expected_idx not in D60_MALEFIC_INDICES)

    # Verify each planet has a valid deity and benefic flag
    for p_name, pos in d60.planets.items():
        assert pos.deity is not None
        assert pos.deity in D60_DEITIES
        assert isinstance(pos.is_benefic_deity, bool)

        p_orig = test_chart.planets[p_name]
        p_part = min(59, int(p_orig.sign_degree // 0.5))
        p_is_odd = (p_orig.sign_id % 2 != 0)
        p_idx = p_part if p_is_odd else (59 - p_part)
        assert pos.deity == D60_DEITIES[p_idx]
        assert pos.is_benefic_deity == (p_idx not in D60_MALEFIC_INDICES)


def test_vaisheshikamsa_tally(test_chart):
    """Verify Vaisheshikamsa tally conforms to BPHS benchmarks."""
    results = VargaCalculator.calculate_vaisheshikamsa(test_chart)
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for p in planets:
        assert p in results
        data = results[p]
        assert "count" in data
        assert "designation" in data
        assert "vargas" in data
        assert 0 <= data["count"] <= 16
        assert len(data["vargas"]) == data["count"]

        # Check designation consistency
        c = data["count"]
        if c in VAISHESHIKAMSA_BENCHMARKS:
            assert data["designation"] == VAISHESHIKAMSA_BENCHMARKS[c]
        elif c == 1:
            assert "1 Varga" in data["designation"]
        elif c == 0:
            assert data["designation"] == "Sadharana"


def test_d60_deity_dual_reference_and_descriptions():
    """Verify BPHS Ch. 6 deity rich description retrieval for both benefic and malefic deities."""
    # 1. Benefic Deva
    deva_info = VargaCalculator.get_d60_deity_details("Deva")
    assert deva_info["name"] == "Deva"
    assert "सौम्य" in deva_info["nature"]
    assert "BPHS" in deva_info["grantha"]
    assert len(deva_info["phala"]) > 5

    # 2. Benefic Kubera
    kubera_info = VargaCalculator.get_d60_deity_details("Kubera")
    assert kubera_info["name"] == "Kubera"
    assert "सौम्य" in kubera_info["nature"]
    assert "धन" in kubera_info["phala"] or "ऐश्वर्य" in kubera_info["phala"]

    # 3. Malefic Ghora
    ghora_info = VargaCalculator.get_d60_deity_details("Ghora")
    assert ghora_info["name"] == "Ghora"
    assert "क्रूर" in ghora_info["nature"]
    assert "कष्ट" in ghora_info["phala"]

    # 4. Benefic Chandrarekha (59th deity)
    rekha_info = VargaCalculator.get_d60_deity_details("Chandrarekha")
    assert rekha_info["name"] == "Chandrarekha"
    assert "सौम्य" in rekha_info["nature"]
    assert "सौभाग्य" in rekha_info["phala"]
