"""API Integration tests for health and portfolio endpoints."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_portfolio_recommendation_endpoint():
    response = client.post(
        "/api/portfolio/recommendation",
        json={"savings_amount": 75000}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["input_savings"] == 75000
    assert "recommended_allocation" in data
    assert len(data["recommended_allocation"]) > 0


def test_portfolio_recommendation_invalid():
    response = client.post(
        "/api/portfolio/recommendation",
        json={"savings_amount": -100}
    )
    assert response.status_code == 400


if __name__ == "__main__":
    test_root_endpoint()
    test_health_endpoint()
    test_portfolio_recommendation_endpoint()
    test_portfolio_recommendation_invalid()
    print("✅ All API tests passed!")
