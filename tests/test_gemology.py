# tests/test_gemology.py
import pytest
import datetime
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.gemology import default_gemology_service, VedicGemologyService
from src.jyotish.ai.narrative import default_narrative_service
from src.jyotish.services.master_calculator import default_master_calculator


def test_mercury_8th_house_strictly_prohibited():
    """Verify that when Mercury is in 8th house, Panna (Emerald) is strictly prohibited."""
    # Create chart where Mercury is in 8th house
    # Aries lagna (lagna around 10 deg Aries), Mercury in Scorpio (8th house)
    bd = BirthData(
        name="Test Querent 8th Mercury",
        birth_date=datetime.date(1995, 11, 20),
        birth_time=datetime.time(14, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    mercury_house = chart.planets["Mercury"].house_from_lagna
    
    # Audit all planets
    audit = default_gemology_service.audit_all_planets(chart)
    merc_audit = audit["planets_audit"]["Mercury"]

    assert merc_audit["house"] == mercury_house
    if mercury_house in [6, 8, 12]:
        assert merc_audit["is_recommended"] is False
        assert merc_audit["status_code"] == "STRICTLY_PROHIBITED"
        assert "वर्जित" in merc_audit["verdict"]
        assert "रुद्राक्ष" in merc_audit["rudraksha"]
        assert "बुधाय नमः" in merc_audit["beej_mantra"]
        assert "मूंग" in merc_audit["daan_items"]


def test_gemology_dusthana_general_rules():
    """Test that all 6th, 8th, and 12th house placements are strictly prohibited from wearing gems."""
    bd = BirthData(
        name="Test Native",
        birth_date=datetime.date(1990, 5, 15),
        birth_time=datetime.time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    audit = default_gemology_service.audit_all_planets(chart)

    for p_name, p_info in audit["planets_audit"].items():
        if p_info["house"] in [6, 8, 12]:
            assert p_info["is_recommended"] is False
            assert p_info["status_code"] == "STRICTLY_PROHIBITED"
            assert "वर्जित" in p_info["verdict"]
            # Must have safe satvik alternatives
            assert len(p_info["rudraksha"]) > 0
            assert len(p_info["beej_mantra"]) > 0
            assert len(p_info["daan_items"]) > 0


def test_ai_sahayak_panna_prohibition_when_mercury_in_8th():
    """Verify that AI Sahayak chat consultation forbids Panna when Mercury is in 8th house."""
    # Construct a chart with Mercury in 8th house
    # We can check planets positions and find or adjust time so Mercury is in 8th house
    bd = BirthData(
        name="Shri Test",
        birth_date=datetime.date(1990, 5, 15),
        birth_time=datetime.time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    # Manually place Mercury in 8th house for precise deterministic testing
    chart.planets["Mercury"].house_from_lagna = 8
    
    master_bundle = default_master_calculator.calculate_all(chart)

    # User asks: "mere liye ratan kaun sa sahi rahega kya panna pehan lu?"
    response = default_narrative_service.chat_consultation(
        user_query="mere liye ratan kaun sa sahi rahega kya mai panna pehan sakta hu?",
        chart=chart,
        master_data=master_bundle,
        api_key=None,  # Tests deterministic fallback
        language="Hindi"
    )

    # Response must contain warning prohibiting Panna and recommending 4-mukhi rudraksha
    assert "पन्ना" in response
    assert ("वर्जित" in response or "निषेध" in response or "चेतावनी" in response)
    assert ("८वें" in response or "8" in response or "अष्टम" in response)
    assert "रुद्राक्ष" in response


def test_ai_sahayak_marriage_query_dual_kundali():
    """Verify that when queried about marriage, AI Sahayak synthesizes Natal + Prashna and answers precisely."""
    bd = BirthData(
        name="Shri Test",
        birth_date=datetime.date(1995, 8, 15),
        birth_time=datetime.time(10, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    master_bundle = default_master_calculator.calculate_all(chart)

    response = default_narrative_service.chat_consultation(
        user_query="meri shadi kb tak hogi?",
        chart=chart,
        master_data=master_bundle,
        api_key=None,
        language="Hindi"
    )

    assert ("विवाह" in response or "शादी" in response)
    assert ("प्रश्न" in response or "ताजिक" in response)
    assert ("सप्तम" in response or "भाव" in response)
    assert ("उपाय" in response or "मंत्र" in response)


def test_ai_sahayak_greeting_general_intelligence():
    """Verify that when the user simply says 'hii', AI Sahayak responds with a concise, respectful greeting without dumping full horoscope or cautions."""
    bd = BirthData(
        name="Shubham Tiwari",
        birth_date=datetime.date(1996, 6, 20),
        birth_time=datetime.time(11, 45),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    master_bundle = default_master_calculator.calculate_all(chart)

    # User says just "hii"
    response = default_narrative_service.chat_consultation(
        user_query="hii",
        chart=chart,
        master_data=master_bundle,
        api_key=None,
        language="Hindi"
    )

    # Must be a warm, concise greeting
    assert "नमस्ते" in response
    assert "Shubham Tiwari" in response
    assert ("मार्गदर्शन" in response or "प्रश्न" in response)
    # Must NOT vomit unsolicited dosha warnings or gemstone bans for a greeting
    assert "अष्टम भाव का दोष" not in response
    assert "पन्ना (Mercury) और माणिक्य (Sun) पहनना आपके लिए सर्वथा वर्जित" not in response
    assert len(response.splitlines()) < 10  # Must be short and proportional!


def test_ai_sahayak_gratitude_response():
    """Verify that when the user expresses gratitude like 'dhanyavad guruji', AI Sahayak responds with a blessing and courtesy."""
    bd = BirthData(
        name="Shubham Tiwari",
        birth_date=datetime.date(1996, 6, 20),
        birth_time=datetime.time(11, 45),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    master_bundle = default_master_calculator.calculate_all(chart)

    response = default_narrative_service.chat_consultation(
        user_query="dhanyavad guruji",
        chart=chart,
        master_data=master_bundle,
        api_key=None,
        language="Hindi"
    )

    assert ("कल्याणमस्तु" in response or "शुभम्" in response)
    assert "Shubham Tiwari" in response
    assert len(response.splitlines()) < 8


def test_ai_sahayak_business_query_suitability():
    """Verify that when queried about future business suitability ('kya mai bhavishya me vyapar kr paunga ya nhi'),
    AI Sahayak never gives absurd 1-3 weeks horary timing, but analyzes 7th/6th/10th houses and Mercury placement."""
    bd = BirthData(
        name="Shubham Tiwari",
        birth_date=datetime.date(1996, 6, 20),
        birth_time=datetime.time(11, 45),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    # Ensure Mercury is in 8th house for realistic test of Shubham's chart
    chart.planets["Mercury"].house_from_lagna = 8
    master_bundle = default_master_calculator.calculate_all(chart)

    response = default_narrative_service.chat_consultation(
        user_query="kya mai bhavishya me vyapar kr paunga ya nhi",
        chart=chart,
        master_data=master_bundle,
        api_key=None,
        language="Hindi"
    )

    # Must NEVER return absurd short-term 1-3 weeks horary timing for lifelong business suitability
    assert "1 से 3 सप्ताह के भीतर" not in response
    assert "Within 1-3 weeks" not in response

    # Must evaluate business (व्यापार) and houses/planets
    assert "व्यापार" in response
    assert ("सप्तम भाव" in response or "7" in response)
    assert ("दशम" in response or "षष्ठ" in response or "कर्म" in response)
    # Must caution about Mercury in 8th house if placed there
    assert ("बुध" in response and ("सतर्कता" in response or "चेतावनी" in response or "८वें" in response or "8" in response))
    # Must suggest realistic long-term timing (2026/2027)
    assert ("२०२६" in response or "2026" in response or "२०२७" in response or "2027" in response)


def test_ai_sahayak_guru_vakri_query_analysis():
    """Verify that when queried about retrograde Jupiter ('meri kundli me guru vakri ka kya prabhav h'),
    AI Sahayak analyzes Jupiter's house, lordship, Chesta Bala from classical Saravali/Phaladeepika,
    and NEVER returns horary '1 से 3 सप्ताह' or 'सकारात्मक / शीघ्र कार्य सिद्धि'."""
    bd = BirthData(
        name="Shubham Tiwari",
        birth_date=datetime.date(1996, 6, 20),
        birth_time=datetime.time(11, 45),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    master_bundle = default_master_calculator.calculate_all(chart)

    response = default_narrative_service.chat_consultation(
        user_query="meri kundli me guru vakri ka kya prabhav h",
        chart=chart,
        master_data=master_bundle,
        api_key=None,
        language="Hindi"
    )

    # Must NEVER output the broken horary countdown
    assert "1 से 3 सप्ताह के भीतर" not in response
    assert "Within 1-3 weeks" not in response
    assert "शीघ्र कार्य सिद्धि" not in response

    # Must specifically analyze Guru (Jupiter) and Vakri (Retrograde)
    assert ("गुरु" in response or "बृहस्पति" in response)
    assert "वक्री" in response
    assert ("चेष्टा बल" in response or "सारावली" in response or "फलदीपिका" in response)
    assert ("भाव" in response)
    assert ("उपाय" in response or "मंत्र" in response)
