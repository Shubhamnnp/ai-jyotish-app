import pytest
from unittest.mock import MagicMock
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.panchang_view import (
    _extract_native_kundali_details,
    _evaluate_native_navratri_fasting,
    _evaluate_native_vivaha_and_manglik,
    _evaluate_native_chandra_tara_bala,
    render_vedic_panchang_view
)


@pytest.fixture
def mock_chart():
    chart = MagicMock()
    chart.lagna_sign_id = 1  # Aries (Mesha), Mars lagnesha
    chart.lagna_degree = 15.5  # 15° 30'
    chart.atmakaraka = "Sun"

    class PlanetMock:
        def __init__(self, sign_id, degree=15.0, dignity="own", house_from_lagna=1, sign_name="Aries"):
            self.sign_id = sign_id
            self.degree = degree
            self.dignity = dignity
            self.house_from_lagna = house_from_lagna
            self.sign_name = sign_name

    chart.planets = {
        "Sun": PlanetMock(1, degree=10.25, dignity="exalted", house_from_lagna=1, sign_name="Aries"),
        "Moon": PlanetMock(4, degree=20.5, dignity="own", house_from_lagna=4, sign_name="Cancer"),
        "Mars": PlanetMock(10, degree=28.0, dignity="exalted", house_from_lagna=10, sign_name="Capricorn"),
        "Mercury": PlanetMock(6, degree=15.0, dignity="exalted", house_from_lagna=6, sign_name="Virgo"),
        "Jupiter": PlanetMock(9, degree=12.0, dignity="own", house_from_lagna=9, sign_name="Sagittarius"),
        "Venus": PlanetMock(7, degree=18.0, dignity="own", house_from_lagna=7, sign_name="Libra"),
        "Saturn": PlanetMock(11, degree=5.0, dignity="own", house_from_lagna=11, sign_name="Aquarius"),
        "Rahu": PlanetMock(3, degree=14.0, dignity="neutral", house_from_lagna=3, sign_name="Gemini"),
        "Ketu": PlanetMock(9, degree=14.0, dignity="neutral", house_from_lagna=9, sign_name="Sagittarius")
    }
    return chart


@pytest.fixture
def mock_birth_profile():
    profile = MagicMock()
    profile.name = "परीक्षार्थी जातक"
    profile.city = "वाराणसी"
    profile.date_of_birth = None
    return profile


@pytest.fixture
def mock_panchang_data():
    return {
        "five_pillars": {
            "tithi": {"name": "अष्टमी", "paksha": "शुक्ल", "end_time_str": "05:40 PM"},
            "vara": {"name_hi": "गुरुवार", "lord": "गुरु"},
            "nakshatra": {"nakshatra_id": 8, "name": "पुष्य", "pada": 2, "lord": "शनि"},
            "yoga": {"name": "शोभन", "nature": "शुभ"},
            "karana": {"current": {"name": "बव", "type": "चर"}}
        },
        "planetary_transit": {
            "planets": [
                {"name": "Sun / सूर्य", "sign_id": 1, "is_combust": False},
                {"name": "Moon / चन्द्र", "sign_id": 4, "is_combust": False},
                {"name": "Mars / मंगल", "sign_id": 10, "is_combust": False},
                {"name": "Mercury / बुध", "sign_id": 6, "is_combust": False},
                {"name": "Jupiter / गुरु", "sign_id": 9, "is_combust": False},
                {"name": "Venus / शुक्र", "sign_id": 7, "is_combust": False},
                {"name": "Saturn / शनि", "sign_id": 11, "is_combust": False}
            ]
        },
        "bhadra": {"is_fatal_on_earth": False, "is_present": False},
        "muhurtas": {
            "shubh_windows": [{"title": "अभिजित मुहूर्त", "time": "11:45 AM - 12:35 PM", "badge": "शुभ", "color": "#059669", "status": "कार्य सिद्धि"}],
            "ashubh_windows": [{"title": "राहु काल", "time": "01:30 PM - 03:00 PM", "badge": "अशुभ", "color": "#DC2626", "status": "त्याज्य"}]
        }
    }


def test_shastriya_pramana_panchanga_phala():
    """Verify classical shloka for Panchanga Phala in SHASTRIYA_SHLOKAS."""
    assert "panchanga_phala" in SHASTRIYA_SHLOKAS
    p_shloka = SHASTRIYA_SHLOKAS["panchanga_phala"]
    assert "तिथेस्तु श्रियमाप्नोति" in p_shloka["shloka_sanskrit"]
    assert "तैत्तिरीय ब्राह्मण" in p_shloka["grantha"]
    assert "पञ्चाङ्ग" in p_shloka["anuvad_hi"]


def test_native_kundali_extraction_and_navratri_fasting(mock_chart, mock_birth_profile):
    """Verify native Kundali extraction (ansh, kala, nakshatra pada) and Navratri decision."""
    n_info = _extract_native_kundali_details(mock_chart, mock_birth_profile)

    assert n_info["lagna_id"] == 1
    assert "मेष" in n_info["lagna_name"]
    assert n_info["lagna_ansh"] == 15
    assert n_info["lagna_kala"] == 30  # 15.5 deg -> 15 deg 30 min
    assert n_info["lagna_pada"] >= 1
    assert "Mars" in n_info["lagnesha"]
    assert n_info["moon_sign_id"] == 4
    assert n_info["moon_ansh"] == 20
    assert n_info["moon_kala"] == 30

    # Navratri fasting evaluation
    nav_res = _evaluate_native_navratri_fasting(n_info)
    assert "best_tithi" in nav_res
    assert "देवी" in nav_res["devi_sadhana"] or "मां" in nav_res["devi_sadhana"]
    assert "shastriya_reason" in nav_res
    assert len(nav_res["positives"]) > 0
    assert len(nav_res["cautions"]) > 0


def test_native_vivaha_and_manglik_tribala(mock_chart, mock_birth_profile, mock_panchang_data):
    """Verify Tribala Shuddhi and Manglik deeds evaluation for active native."""
    n_info = _extract_native_kundali_details(mock_chart, mock_birth_profile)
    viv_res = _evaluate_native_vivaha_and_manglik(n_info, mock_panchang_data)

    assert "tribala" in viv_res
    tribala = viv_res["tribala"]
    assert "surya" in tribala
    assert "guru" in tribala
    assert "chandra" in tribala
    assert "status" in tribala["surya"]
    assert "status" in tribala["guru"]
    assert "status" in tribala["chandra"]

    assert "deeds" in viv_res
    assert len(viv_res["deeds"]) >= 5
    assert "ashtama_lagna_name" in viv_res


def test_native_chandra_tara_bala(mock_chart, mock_birth_profile, mock_panchang_data):
    """Verify personalized Chandrabala and Tarabala calculation for active native."""
    n_info = _extract_native_kundali_details(mock_chart, mock_birth_profile)
    ct_res = _evaluate_native_chandra_tara_bala(n_info, mock_panchang_data)

    assert "c_diff" in ct_res
    assert "c_score" in ct_res
    assert "c_status" in ct_res
    assert "tara_num" in ct_res
    assert 1 <= ct_res["tara_num"] <= 9
    assert "tara_name" in ct_res
    assert "tara_badge" in ct_res


def test_app_tabs_registry_module29():
    """Verify MODULE_TABS_REGISTRY[29] in app.py has 12 synchronized tabs."""
    import re
    with open("src/jyotish/ui/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'29:\s*\[(.*?)\]', content, re.DOTALL)
    assert match is not None, "MODULE_TABS_REGISTRY[29] not found in app.py"
    raw_tabs = match.group(1)
    tabs = [line.strip().strip('",\'') for line in raw_tabs.splitlines() if line.strip().strip('",\'')]
    assert len(tabs) == 12
    assert tabs == [
        "🌟 पञ्चाङ्ग ५ स्तम्भ",
        "🚩 पर्व, व्रत व एकादशी",
        "🪔 पक्ष व श्राद्ध",
        "🏛️ २४-घंटे लग्न सारणी",
        "⏰ शुभ-अशुभ मुहूर्त",
        "☀️ चौघड़िया व होरा",
        "🛡️ भद्रा व पञ्चक",
        "⚖️ चन्द्रबल व ताराबल",
        "🪐 गोचर व मंत्रिमंडल",
        "📜 दैनिक सङ्कल्प मन्त्र",
        "📅 मासिक पञ्चाङ्ग",
        "🤖 AI पञ्चाङ्ग सारथी"
    ]
