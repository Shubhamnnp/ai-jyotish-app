"""
Unit tests for Grounded Interactive Chat & API v1 (Phase 5, Task P5-T8).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T8).

Verifies:
1. Career question generates a domain Evidence Pack with citations and provenance.
2. Ungrounded non-astrological questions are strictly refused.
3. Unsafe death-timing questions are intercepted by the safety layer in chat.
"""

import sys
import os
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.api.main import app

client = TestClient(app)


@pytest.fixture
def sample_payload():
    return {
        "birth_data": {
            "name": "Swami Vivekananda",
            "birth_date": "1863-01-12",
            "birth_time": "06:33:00",
            "latitude": 22.5726,
            "longitude": 88.3639,
            "timezone_offset": 5.5,
            "city": "Kolkata",
            "confidence": "Exact"
        },
        "question": "How does my horoscope indicate career and profession?",
        "language": "en",
        "ayanamsa": "Lahiri"
    }


def test_grounded_career_consultation(sample_payload):
    """Verify chat endpoint generates grounded consultation from Evidence Pack."""
    response = client.post("/api/v1/chat/consult", json=sample_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["domain"] == "career"
    assert data["evidence_status"] == "Strongly Grounded on Evidence Pack"
    assert len(data["citations"]) > 0
    assert len(data["consultation_narrative"]) > 50
    assert len(data["provenance"]) > 0
    assert "ethical_disclaimer" in data


def test_ungrounded_general_memory_refusal(sample_payload):
    """Verify system refuses to answer non-astrological external memory questions."""
    sample_payload["question"] = "Can you write quicksort in python code?"
    response = client.post("/api/v1/chat/consult", json=sample_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["domain"] == "unsupported"
    assert "Refused" in data["evidence_status"]
    assert "cannot answer questions from general memory" in data["consultation_narrative"]
    assert len(data["citations"]) == 0


def test_chat_safety_redirection(sample_payload):
    """Verify death-timing query in chat is intercepted by safety layer."""
    sample_payload["question"] = "Tell me when will I die and what is my death date?"
    response = client.post("/api/v1/chat/consult", json=sample_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["domain"] == "safety_redirection"
    assert "Safety Layer" in data["evidence_status"]
    assert "Maha Mrityunjaya" in data["consultation_narrative"]
    assert len(data["citations"]) == 0
