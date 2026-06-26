from __future__ import annotations

from app.core.config import reset_settings_cache
from app.main import create_app
from fastapi.testclient import TestClient


def _client(monkeypatch, **env):
    reset_settings_cache()
    for key, value in env.items():
        monkeypatch.setenv(key, str(value))
    return TestClient(create_app())


def test_request_id_is_returned_and_logged_in_headers(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Response-Time-Ms"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_request_id_can_be_supplied_by_client(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_validation_errors_include_request_id(monkeypatch):
    client = _client(monkeypatch)
    response = client.post("/api/skills/run", json={})
    assert response.status_code == 422
    body = response.json()
    assert "request_id" in body
    assert response.headers["X-Request-ID"] == body["request_id"]


def test_rate_limit_blocks_excess_requests(monkeypatch):
    client = _client(monkeypatch, RATE_LIMIT_PER_MINUTE="2")

    # Same anonymous user (no X-User-Id) hits the shared bucket.
    assert client.get("/").status_code == 200
    assert client.get("/").status_code == 200
    response = client.get("/")
    assert response.status_code == 429
    body = response.json()
    assert body["detail"] == "Rate limit exceeded"
    assert "request_id" in body


def test_rate_limit_is_per_user(monkeypatch):
    client = _client(monkeypatch, RATE_LIMIT_PER_MINUTE="1")

    assert client.get("/", headers={"X-User-Id": "user-a"}).status_code == 200
    assert client.get("/", headers={"X-User-Id": "user-b"}).status_code == 200
    assert client.get("/", headers={"X-User-Id": "user-a"}).status_code == 429


def test_request_body_size_limit(monkeypatch):
    client = _client(monkeypatch, REVENUEPILOT_MAX_REQUEST_BODY_SIZE="10")
    response = client.post("/api/skills/run", json={"skill_name": "x", "input_payload": {"a": 1}})
    assert response.status_code == 413


def test_health_endpoint_reports_memory_mode(monkeypatch):
    client = _client(monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "memory"


def test_cors_headers_are_present(monkeypatch):
    client = _client(monkeypatch, CORS_ORIGINS="https://example.com")
    response = client.get("/", headers={"Origin": "https://example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "https://example.com"


def test_health_reports_degraded_when_db_unavailable(monkeypatch):
    class FakeRepo:
        class pool:
            @staticmethod
            async def health_check() -> bool:
                raise RuntimeError("db down")

    class FakeBundle:
        skill_runs = FakeRepo

    monkeypatch.setattr("app.main.get_repositories", lambda: FakeBundle())
    client = _client(monkeypatch, DATABASE_URL="postgresql://x/db", REVENUEPILOT_DB="postgres")
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "error"
