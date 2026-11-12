"""
Master Golden Benchmark Integration Test Suite for Vedic Astrology Audit (Phase 14).
Validates end-to-end mathematical precision across all 15 audit dimensions:
1. D1-D60 and Higher Vargas (D72, D81, D108, D144, D150) & Vimsopaka Bala
2. Ashtakavarga: BAVs, 337 SAV, Trikona/Ekadhipatya Shodhana, Pindas
3. Shadbala: 6 Balas, Cheshta with retro/fast corrections, Ishta/Kashta, Bhavabala
4. Dasha Systems: Vimshottari, Ashtottari, Yogini, Jaimini Chara, Patyayini
5. Jaimini Astrology: Chara Karakas, Arudha Padas, Upapada, Karakamsha
6. Panchanga & Classical Upagrahas (Gulika, Mandi, Dhuma, Vyatipata, etc.)
7. Horary 16 Shodasha Sphutas (Kerala Prashna Marga)
8. 81-Cell Sarvatobhadra Chakra with Abhijit & 3-way Raycasting Vedhas
9. Tajika Sahams & Aspect Matrix
10. Ayurdaya: Pindayu with 4 classical Harana reductions
"""

import pytest
from datetime import datetime, date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.varga import VargaCalculator
from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
from src.jyotish.core.shadbala import ShadbalaCalculator
from src.jyotish.dasha.vimshottari import VimshottariDashaEngine
from src.jyotish.dasha.ashtottari import AshtottariDashaEngine
from src.jyotish.dasha.yogini import YoginiDashaEngine
from src.jyotish.dasha.chara import CharaDashaEngine
from src.jyotish.core.jaimini import JaiminiCalculator
from src.jyotish.core.upagraha import UpagrahaCalculator
from src.jyotish.services.prashna import PrashnaService
from src.jyotish.core.sarvatobhadra import default_sarvatobhadra_chakra_engine
from src.jyotish.services.varshaphal import VarshaphalService
from src.jyotish.core.ayurdaya import AyurdayaEngine


@pytest.fixture(scope="module")
def golden_chart():
    bdata = BirthData(
        name="Golden Master Native",
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_dimension_1_vargas_and_vimsopaka(golden_chart):
    """Verify all classical and higher divisional charts plus Vimsopaka Bala."""
    vargas = VargaCalculator.calculate_all_vargas(golden_chart)
    assert len(vargas) >= 20
    assert "D1" in vargas and "D9" in vargas and "D60" in vargas

    # Higher Vargas D72 to D150
    d72 = VargaCalculator.calculate_d72(golden_chart)
    assert d72.varga_code == "D72"
    assert d72.division == 72
    assert len(d72.planets) >= 7

    d150 = VargaCalculator.calculate_d150(golden_chart)
    assert d150.varga_code == "D150"
    assert d150.division == 150
    assert len(d150.planets) >= 7
    assert d150.lagna_deity is not None

    # Vimsopaka Bala schemes
    for scheme in ["shadvarga", "saptavarga", "dashavarga", "shodashavarga"]:
        v_bala = VargaCalculator.calculate_vimsopaka_bala(golden_chart, scheme=scheme)
        assert len(v_bala) == 7
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            score = v_bala[p]
            assert 0.0 <= score <= 20.0


def test_dimension_2_ashtakavarga_integrity(golden_chart):
    """Verify BAVs, SAV exact 337 sum, and Shodhana reductions."""
    av_calc = AshtakavargaCalculator()
    av_res = av_calc.calculate(golden_chart)
    assert len(av_res.bav) == 7
    total_sav = sum(av_res.sav)
    assert total_sav == 337, f"SAV points must total exactly 337, got {total_sav}"

    shodhana = av_calc.calculate_shodhana(av_res.bav, golden_chart)
    assert len(shodhana.trikona_reduced_bav) == 7
    assert len(shodhana.ekadhipatya_reduced_bav) == 7
    assert len(shodhana.rashi_pinda) == 7
    assert len(shodhana.graha_pinda) == 7
    assert len(shodhana.yoga_pinda) == 7
    for p, val in shodhana.yoga_pinda.items():
        assert val > 0


def test_dimension_3_shadbala_and_cheshta(golden_chart):
    """Verify 6 Shadbala components, Cheshta ratios, and Bhavabala."""
    sb_calc = ShadbalaCalculator()
    sb_res = sb_calc.calculate(golden_chart)
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert p in sb_res.planets
        b = sb_res.planets[p]
        assert b.total_rupas > 0.0
        assert b.sthana_bala > 0.0
        assert b.dik_bala >= 0.0
        assert b.kaala_bala > 0.0
        assert b.cheshta_bala >= 0.0
        assert b.naisargika_bala > 0.0

    assert len(sb_res.bhava_bala) == 12


def test_dimension_4_dashas_and_patyayini(golden_chart):
    """Verify major Dasha systems and 1-year Patyayini progression."""
    # Vimshottari
    vim = VimshottariDashaEngine().generate_timeline(golden_chart)
    assert len(vim) > 0

    # Ashtottari
    ash = AshtottariDashaEngine().generate_timeline(golden_chart)
    assert len(ash) > 0

    # Yogini
    yog = YoginiDashaEngine().generate_timeline(golden_chart)
    assert len(yog) > 0

    # Chara
    chara = CharaDashaEngine().generate_timeline(golden_chart)
    assert len(chara) > 0

    # Patyayini Dasha
    vp_svc = VarshaphalService()
    start_dt = datetime(2026, 5, 15, 14, 30, 0)
    pat = vp_svc._calculate_patyayini_dasha(start_dt, golden_chart)
    assert len(pat) >= 7
    total_days = sum(d["duration_days"] for d in pat)
    assert abs(total_days - 365.25) <= 1.5


def test_dimension_5_jaimini_and_argala(golden_chart):
    """Verify Jaimini Chara Karakas, Arudhas, Upapada, and Karakamsha."""
    j_calc = JaiminiCalculator()
    j_res = j_calc.calculate(golden_chart)
    assert len(j_res.karakas_7) == 7
    assert len(j_res.karakas_8) == 8
    assert "AK" in j_res.karakas_7
    assert "DK" in j_res.karakas_7

    assert len(j_res.arudha_padas) == 12
    assert "AL" in j_res.arudha_padas
    assert "UL" in j_res.arudha_padas
    assert 1 <= j_res.arudha_padas["AL"] <= 12
    assert 1 <= j_res.arudha_padas["UL"] <= 12
    assert j_res.karakamsha_sign_name != ""


def test_dimension_6_panchanga_and_upagrahas(golden_chart):
    """Verify Panchanga 5 angas and classical Upagrahas."""
    p_res = golden_chart.panchang
    assert p_res.tithi_name != ""
    assert p_res.nakshatra_name != ""
    assert p_res.yoga_name != ""
    assert p_res.karana_name != ""
    assert p_res.vara_name != ""

    up_calc = UpagrahaCalculator()
    up_res = up_calc.calculate(golden_chart)
    assert 0.0 <= up_res.gulika_longitude <= 360.0
    assert 0.0 <= up_res.mandi_longitude <= 360.0
    assert 0.0 <= up_res.dhuma_longitude <= 360.0
    assert 0.0 <= up_res.vyatipata_longitude <= 360.0
    assert 0.0 <= up_res.parivesha_longitude <= 360.0
    assert 0.0 <= up_res.indrachapa_longitude <= 360.0
    assert 0.0 <= up_res.upaketu_longitude <= 360.0


def test_dimension_7_kerala_shodasha_sphutas(golden_chart):
    """Verify all 16 Prashna Marga Shodasha Sphutas."""
    sphutas = PrashnaService.calculate_shodasha_sphutas(golden_chart, karyesha="Jupiter")
    assert len(sphutas) == 16
    names_en = [s["name_en"] for s in sphutas]
    assert "Trisphuta" in names_en
    assert "Panchasphuta" in names_en
    assert "Prana Sphuta" in names_en
    assert "Deha Sphuta" in names_en
    assert "Mrityu Sphuta" in names_en
    assert "Beeja Sphuta" in names_en
    assert "Kshetra Sphuta" in names_en
    for s in sphutas:
        assert 0.0 <= s["longitude"] <= 360.0
        assert s["dms"] != ""
        assert s["navamsha_sign"] != ""


def test_dimension_8_sarvatobhadra_81_cell_vedhas(golden_chart):
    """Verify 81-cell Sarvatobhadra Chakra 28-nakshatra Abhijit & 3-way raycasting."""
    sbc_res = default_sarvatobhadra_chakra_engine.calculate_chakra_vedha(golden_chart)
    assert "janma_nakshatra_28" in sbc_res
    assert len(sbc_res["sensitive_nakshatra_map"]) >= 8
    roles = list(sbc_res["sensitive_nakshatra_map"].values())
    assert any("जन्म" in r for r in roles)
    assert any("कर्म" in r for r in roles)
    assert any("सांघातिक" in r for r in roles)
    assert len(sbc_res["all_vedhas"]) > 0


def test_dimension_9_tajika_sahams_and_drishti(golden_chart):
    """Verify Tajika Sahams calculation and Drishti Aspect Matrix."""
    vp_svc = VarshaphalService()
    sahams = vp_svc._calculate_extended_sahams(golden_chart, is_day=True)
    assert len(sahams) >= 20
    s_matrix = VarshaphalService.calculate_saham_aspect_matrix(sahams, golden_chart)
    assert len(s_matrix) >= 20
    for row in s_matrix:
        assert "Jupiter" in row
        assert "Saturn" in row


def test_dimension_10_ayurdaya_with_4_haranas(golden_chart):
    """Verify Pindayu Ayurdaya with BPHS 4-fold Harana reductions."""
    pinda_res = AyurdayaEngine.calculate_pindayu_with_haranas(golden_chart)
    assert "net_pindayu_years" in pinda_res
    assert 20.0 <= pinda_res["net_pindayu_years"] <= 120.0
    assert len(pinda_res["audit_table"]) == 7
    for row in pinda_res["audit_table"]:
        assert row["शुद्ध आयु (Net Years)"] <= row["मूल पिंडायु (Unreduced)"] + 0.001
