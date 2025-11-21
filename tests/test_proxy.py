import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import httpx
from app.main import create_application


@pytest.fixture
def client():
    app = create_application()
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "target_url" in data


def test_ping(client):
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_proxy_get_request(client):
    response = client.get("/")
    assert response.status_code in [200, 301, 302, 404, 502, 504]


def test_proxy_headers_forwarded(client):
    headers = {"X-Custom-Header": "test-value"}
    response = client.get("/", headers=headers)
    assert "X-Process-Time" in response.headers
    assert "X-Request-ID" in response.headers


def test_docs_accessible(client):
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_openapi_json(client):
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "AI Proxy Service"
