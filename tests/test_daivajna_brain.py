"""
Unit tests for Daivajna Deep Shastriya Brain Service (वैदिक ज्योतिष महा-मस्तिष्क).
Verifies:
1. Detection of atypical/complex chart configurations (Graha Yuddha, Gandanta, Neecha, Pushkara, etc.)
2. Autonomous deep research execution with classical Sanskrit slokas and exceptions
3. Multi-tenant cache isolation per user and per chart
"""

import os
import tempfile
import pytest
from datetime import date, time
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.models import BirthData
from src.jyotish.services.daivajna_brain import DaivajnaBrainService


@pytest.fixture
def sample_chart():
    bdata = BirthData(
        name="Test Native Complex",
        birth_date=date(1994, 5, 16),
        birth_time=time(17, 0, 0),
        latitude=28.0327,
        longitude=81.3787,
        timezone_offset=5.5,
        city="Nanpara, UP"
    )
    return default_chart_calculator.calculate_chart(bdata)


@pytest.fixture
def brain_service():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    service = DaivajnaBrainService(cache_path=tmp_path)
    yield service

    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    except Exception:
        pass


def test_complexity_detection(sample_chart, brain_service):
    audit = brain_service.detect_chart_complexities(sample_chart)
    assert "score" in audit
    assert "level" in audit
    assert "items" in audit
    assert isinstance(audit["items"], list)
    assert len(audit["items"]) > 0

    # Verify fields in each item
    for item in audit["items"]:
        assert "type" in item
        assert "title" in item
        assert "severity" in item
        assert "detail" in item
        assert "shastra" in item


def test_execute_deep_research_and_caching(sample_chart, brain_service):
    user_a = "axemple@gmail.com"
    user_b = "deepakexample@gmail.com"

    # User A runs deep research
    res_a = brain_service.execute_deep_research(
        chart=sample_chart,
        owner_email=user_a,
        user_prompt="विस्तृत ग्रह विश्लेषण व शास्त्रीय प्रमाण"
    )

    assert res_a["status"] == "success"
    assert "complexity_audit" in res_a
    assert "research_report_md" in res_a
    assert "citations" in res_a

    # Classical Sanskrit shlokas and sections must be in the report
    report_text = res_a["research_report_md"]
    assert "प्रामाणिक ग्रन्थ संदर्भ एवं मूल संस्कृत श्लोक" in report_text
    assert "सूक्ष्म गणितीय अपवाद" in report_text
    assert "परम-सटीक संश्लेषित फलादेश" in report_text
    assert "दैवज्ञ अनुभूत शास्त्रीय वैदिक उपचार" in report_text

    # User A gets cached research
    cached_a = brain_service.get_cached_research(sample_chart, owner_email=user_a)
    assert cached_a is not None
    assert cached_a["chart_name"] == res_a["chart_name"]

    # User B MUST NOT see User A's cached research (Multi-Tenant Isolation)
    cached_b = brain_service.get_cached_research(sample_chart, owner_email=user_b)
    assert cached_b is None
