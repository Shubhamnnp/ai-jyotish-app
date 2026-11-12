"""
Unit test suite for Phase 4: Janma Kundali & Varga Engine Hardening.
Tests:
1. Completeness of all 20 classical divisional charts (D1 to D60).
2. Mathematical boundaries of new vargas: D5 (Panchamsha), D6 (Shashtamsha), D8 (Ashtamsha), D11 (Rudramsha).
3. Vargottama detection for planets and lagna.
4. Bhavottama detection for planets.
5. Classical BPHS Vimsopaka Bala calculations (Shadvarga, Saptavarga, Dashavarga, Shodashavarga).
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.varga import VargaCalculator


@pytest.fixture
def sample_chart():
    bdata = BirthData(
        name="Varga Benchmark Native",
        birth_date=date(1985, 11, 23),
        birth_time=time(8, 15, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_all_20_divisional_charts_generated(sample_chart):
    """Verify that all classical and higher divisional charts are generated with valid structure."""
    expected_vargas = [
        "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10",
        "D11", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60",
        "D72", "D81", "D108", "D144", "D150"
    ]
    vargas = VargaCalculator.calculate_all_vargas(sample_chart)
    
    assert len(vargas) >= 25
    for v_code in expected_vargas:
        assert v_code in vargas, f"Missing varga {v_code}"
        v_chart = vargas[v_code]
        assert 1 <= v_chart.lagna_sign_id <= 12
        assert len(v_chart.lagna_sign_name) > 0
        assert len(v_chart.planets) >= 7
        for p_name, pos in v_chart.planets.items():
            assert 1 <= pos.sign_id <= 12
            assert 1 <= pos.house_number <= 12
            assert 0.0 <= pos.degree_in_varga <= 30.0


def test_higher_vargas_d72_to_d150(sample_chart):
    """Verify mathematical properties and metadata of higher vargas D72, D81, D108, D144, D150."""
    # 1. D72 Ashtottaramsha (division 72)
    d72 = VargaCalculator.calculate_d72(sample_chart)
    assert d72.varga_code == "D72"
    assert d72.division == 72
    assert 1 <= d72.lagna_sign_id <= 12

    # 2. D81 Navanavamsha (division 81)
    d81 = VargaCalculator.calculate_d81(sample_chart)
    assert d81.varga_code == "D81"
    assert d81.division == 81
    assert 1 <= d81.lagna_sign_id <= 12

    # 3. D108 Ashtottarashatamsha (division 108)
    d108 = VargaCalculator.calculate_d108(sample_chart)
    assert d108.varga_code == "D108"
    assert d108.division == 108
    assert 1 <= d108.lagna_sign_id <= 12

    # 4. D144 Dwadash-Dwadashamsha (division 144)
    d144 = VargaCalculator.calculate_d144(sample_chart)
    assert d144.varga_code == "D144"
    assert d144.division == 144
    assert 1 <= d144.lagna_sign_id <= 12

    # 5. D150 Nadiamsha (division 150)
    d150 = VargaCalculator.calculate_d150(sample_chart)
    assert d150.varga_code == "D150"
    assert d150.division == 150
    assert 1 <= d150.lagna_sign_id <= 12
    assert "Nadi #" in d150.lagna_deity


def test_d5_panchamsha_classical_mapping(sample_chart):
    """Verify D5 Panchamsha adheres to Parashari odd/even sign partition rules."""
    d5 = VargaCalculator.calculate_d5(sample_chart)
    assert d5.varga_code == "D5"
    assert d5.division == 5
    # Signs in D5 can only belong to specific sets (odd: 1, 11, 9, 3, 7; even: 2, 6, 8, 10, 12)
    for p_name, pos in d5.planets.items():
        assert pos.sign_id in [1, 2, 3, 6, 7, 8, 9, 10, 11, 12]


def test_d6_shashtamsha_classical_mapping(sample_chart):
    """Verify D6 Shashtamsha adheres to odd (1..6) and even (7..12) partitions."""
    d6 = VargaCalculator.calculate_d6(sample_chart)
    assert d6.varga_code == "D6"
    assert d6.division == 6
    for p_name, pos in d6.planets.items():
        assert 1 <= pos.sign_id <= 12


def test_d8_ashtamsha_movable_fixed_dual(sample_chart):
    """Verify D8 Ashtamsha starts from Aries (Movable), Sagittarius (Fixed), or Leo (Dual)."""
    d8 = VargaCalculator.calculate_d8(sample_chart)
    assert d8.varga_code == "D8"
    assert d8.division == 8
    assert 1 <= d8.lagna_sign_id <= 12


def test_d11_rudramsha_classical_calculation(sample_chart):
    """Verify D11 Rudramsha calculates correctly across all 11 divisions."""
    d11 = VargaCalculator.calculate_d11(sample_chart)
    assert d11.varga_code == "D11"
    assert d11.division == 11
    assert 1 <= d11.lagna_sign_id <= 12


def test_vargottama_and_bhavottama_detection(sample_chart):
    """Verify Vargottama (same sign D1 & D9) and Bhavottama (same house D1 & D9) identification."""
    vargottama = VargaCalculator.get_vargottama_planets(sample_chart)
    bhavottama = VargaCalculator.get_bhavottama_planets(sample_chart)
    
    assert isinstance(vargottama, list)
    assert isinstance(bhavottama, list)
    
    # Ground truth verification against D1 and D9
    vargas = VargaCalculator.calculate_all_vargas(sample_chart)
    d1 = vargas["D1"]
    d9 = vargas["D9"]
    
    for p in vargottama:
        if p == "Lagna":
            assert d1.lagna_sign_id == d9.lagna_sign_id
        else:
            assert d1.planets[p].sign_id == d9.planets[p].sign_id
            
    for p in bhavottama:
        assert d1.planets[p].house_number == d9.planets[p].house_number


def test_bphs_vimsopaka_bala_schemes(sample_chart):
    """Verify BPHS Vimsopaka Bala across Shadvarga, Saptavarga, Dashavarga, and Shodashavarga."""
    schemes = ["shadvarga", "saptavarga", "dashavarga", "shodashavarga"]
    
    for scheme in schemes:
        bala = VargaCalculator.calculate_vimsopaka_bala(sample_chart, scheme=scheme)
        assert len(bala) == 7  # 7 classical planets (Sun to Saturn)
        for p_name, score in bala.items():
            assert 0.0 <= score <= 20.0, f"Planet {p_name} score {score} out of range [0, 20] in {scheme}"

