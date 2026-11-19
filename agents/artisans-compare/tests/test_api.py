"""
Tests pour le service Artisans Compare
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from models import Artisan, Badge

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_artisans():
    response = client.get("/artisans/search?specialty=plomberie&location=Lyon")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "name" in data[0]
        assert "rating" in data[0]


def test_get_artisan_details():
    response = client.get("/artisans/art_001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "art_001"
    assert "reviews" in data


def test_get_artisan_not_found():
    response = client.get("/artisans/nonexistent")
    assert response.status_code == 404


def test_compare_artisans():
    payload = {
        "project_type": "plomberie",
        "location": "Lyon",
        "budget": 500,
        "artisan_ids": ["art_001", "art_002"]
    }
    response = client.post("/artisans/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "artisans" in data
    assert "metrics" in data
    assert "recommendation_reason" in data


def test_compare_artisans_wrong_count():
    payload = {
        "project_type": "plomberie",
        "location": "Lyon",
        "artisan_ids": ["art_001"]  # Seulement 1 artisan
    }
    response = client.post("/artisans/compare", json=payload)
    assert response.status_code == 400


def test_get_reviews():
    response = client.get("/artisans/art_001/reviews")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_match_artisans():
    payload = {
        "project_type": "electricite",
        "location": "Lyon",
        "budget": 1000,
        "urgency": "normal"
    }
    response = client.post("/artisans/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "matches" in data
    assert isinstance(data["matches"], list)


def test_get_specialties():
    response = client.get("/specialties")
    assert response.status_code == 200
    data = response.json()
    assert "specialties" in data
    assert len(data["specialties"]) > 0


def test_get_badges():
    response = client.get("/badges")
    assert response.status_code == 200
    data = response.json()
    assert "badges" in data
    assert len(data["badges"]) > 0


def test_landing_recommended():
    response = client.get("/landing/recommended?project_type=plomberie&location=Lyon")
    assert response.status_code == 200
    data = response.json()
    assert "artisans" in data
    assert "title" in data


def test_landing_after_analysis():
    response = client.get("/landing/after-analysis?quote_id=quote_123&project_type=peinture&detected_price=1200")
    assert response.status_code == 200
    data = response.json()
    assert "artisans" in data
    assert "context" in data
