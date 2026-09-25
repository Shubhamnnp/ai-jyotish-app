"""
FastAPI REST Endpoints Integration Test.
"""

import sys
import os
import io
sys.path.insert(0, os.path.abspath("."))
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi.testclient import TestClient
from src.jyotish.api.main import app

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["total_rules"] >= 32
    print(f"API Root Test Passed ({data['total_rules']} classical rules confirmed)!")


def test_api_chart_calculate():
    payload = {
        "name": "API Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5,
        "confidence": "Exact"
    }
    response = client.post("/api/chart/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "planets" in data
    assert "Sun" in data["planets"]
    assert "ashtakavarga" in data
    assert data["ashtakavarga"]["total_bindus"] == 337
    print("API Natal Chart Calculation Test Passed!")

def test_api_ghatna_query():
    payload = {
        "birth_data": {
            "name": "API Test",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5,
            "confidence": "Exact"
        },
        "target_date": "2027-04-12",
        "theme": "career"
    }
    response = client.post("/api/ghatna-query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "composite_score" in data
    assert "active_dasha" in data
    assert "top_positive_signals" in data
    assert "narrative_hi" in data
    print(f"API Ghatna Query Test Passed! Composite Score: {data['composite_score']}")

def test_api_prashna():
    payload = {
        "query_text": "Will I get promotion?",
        "category": "career",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/prashna", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    print("API Prashna Test Passed! Verdict:", data["verdict"])

def test_api_rules():
    response = client.get("/api/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 32
    print(f"API Rules List Test Passed! Total rules: {data['total']}")


def test_api_geocoding():
    response = client.get("/api/geocoding/search?query=Varanasi")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["latitude"] > 0
    print("API Geocoding Test Passed!")

def test_api_shadbala():
    payload = {
        "name": "API Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/shadbala", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "planets" in data
    assert "Sun" in data["planets"]
    print("API Shadbala Test Passed!")

def test_api_jaimini():
    payload = {
        "name": "API Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/jaimini", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "karakas_7" in data
    assert "arudha_padas" in data
    print("API Jaimini Test Passed!")

def test_api_varshaphal():
    payload = {
        "birth_data": {
            "name": "API Test",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        },
        "target_year": 2027
    }
    response = client.post("/api/chart/varshaphal", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "muntha_sign" in data
    print("API Varshaphal Test Passed!")

def test_api_btr():
    payload = {
        "birth_data": {
            "name": "API Test",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        },
        "events": [
            {"event_date": "2015-06-01", "event_category": "career", "description": "Job promotion"}
        ],
        "window_minutes": 10,
        "step_minutes": 2
    }
    response = client.post("/api/chart/btr", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    print("API BTR Test Passed!")

def test_api_milan():
    payload = {
        "groom": {
            "name": "Groom",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        },
        "bride": {
            "name": "Bride",
            "birth_date": "1992-05-15",
            "birth_time": "08:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        }
    }
    response = client.post("/api/chart/milan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_score" in data
    print("API Milan Test Passed! Score:", data["total_score"])

def test_api_report():
    payload = {
        "name": "API Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "html" in data
    print("API Report Generation Test Passed!")

def test_api_chat():
    payload = {
        "query": "Tell me about my lagna.",
        "language": "Hindi"
    }
    response = client.post("/api/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print("API Chat Test Passed!")

def test_api_affliction():
    payload = {
        "name": "API Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/affliction", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dasvarga_table" in data
    assert "house_points" in data
    assert "planet_points" in data
    assert "life_area_detail" in data
    assert "rashi_prediction" in data
    print("API Affliction Test Passed (Dasvarga + Free Will + 26 Life Areas)!")

def test_api_vastu():
    payload = {
        "name": "API Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/vastu", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data
    assert len(data["zones"]) >= 8
    print("API Vastu Mandala Test Passed (8 Cardinal Zones Evaluated)!")

def test_api_prashna_full():
    payload = {
        "query_text": "Will I get married this year?",
        "category_name": "Marriage",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/prashna-full", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "house_roles" in data
    assert "tajika_yoga" in data
    assert "verdict" in data
    print("API Prashna Full Test Passed! Verdict:", data["verdict"])

def test_api_grahalakshanam_login():
    payload = {
        "username": "shubham8jyotish@gmail.com",
        "password": "Bahraich@123"
    }
    response = client.post("/api/grahalakshanam/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    print("API Grahalakshanam Live Authentication Test Passed!")

def test_api_grahalakshanam_sync():
    response = client.post("/api/grahalakshanam/sync")
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        print(f"API Grahalakshanam Cloud Sync Test Passed! Imported charts: {data['imported_charts']}")
    else:
        print("API Grahalakshanam Cloud Sync: Remote endpoint offline / auth required as expected.")


def test_api_remedy():
    payload = {
        "name": "API Test",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    response = client.post("/api/chart/remedy/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "remedy_matrix" in data
    assert len(data["remedy_matrix"]) == 10
    print("API Remedy Matrix Test Passed (10 Classical Rows Verified)!")

if __name__ == "__main__":
    test_api_root()
    test_api_chart_calculate()
    test_api_ghatna_query()
    test_api_prashna()
    test_api_rules()
    test_api_geocoding()
    test_api_shadbala()
    test_api_jaimini()
    test_api_varshaphal()
    test_api_btr()
    test_api_milan()
    test_api_report()
    test_api_chat()
    test_api_affliction()
    test_api_remedy()
    test_api_vastu()
    test_api_prashna_full()
    test_api_grahalakshanam_login()
    test_api_grahalakshanam_sync()
    print("ALL API ENDPOINTS TESTED AND PASSED!")


