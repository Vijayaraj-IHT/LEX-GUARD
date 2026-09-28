"""Tests for application startup and health endpoint."""


def test_api_root(client):
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "LexGuard"
    assert data["status"] == "running"


def test_frontend_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "LexGuard" in response.text
    assert "text/html" in response.headers["content-type"]


def test_health_healthy(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert data["counts"]["reviewed_cases"] == 0
    assert data["counts"]["draft_cases"] == 0
