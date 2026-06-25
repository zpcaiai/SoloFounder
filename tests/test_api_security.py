from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import reset_settings_cache
from app.main import create_app
from app.repositories.factory import reset_repository_bundle


def _client(monkeypatch, *, env: str = "development", api_key: str | None = None) -> TestClient:
    monkeypatch.setenv("REVENUEPILOT_ENV", env)
    if api_key is None:
        monkeypatch.delenv("REVENUEPILOT_API_KEY", raising=False)
    else:
        monkeypatch.setenv("REVENUEPILOT_API_KEY", api_key)
    reset_settings_cache()
    reset_repository_bundle()
    return TestClient(create_app())


def test_development_allows_demo_user_without_headers(monkeypatch):
    client = _client(monkeypatch, env="development")
    response = client.post(
        "/api/skills/run",
        json={"skill_name": "productized_offer", "input_payload": {"selected_niche": "clinics"}},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    assert response.headers["X-Request-ID"]


def test_production_requires_user_id(monkeypatch):
    client = _client(monkeypatch, env="production", api_key="secret")
    response = client.get("/api/workflow-runs")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"


def test_production_fails_closed_without_auth_configuration(monkeypatch):
    client = _client(monkeypatch, env="production")
    response = client.get("/api/workflow-runs", headers={"X-User-Id": "user-1"})

    assert response.status_code == 503
    assert response.json()["detail"] == "API authentication is not configured"


def test_api_key_is_enforced_when_configured(monkeypatch):
    client = _client(monkeypatch, env="production", api_key="secret")

    missing = client.get("/api/workflow-runs", headers={"X-User-Id": "user-1"})
    assert missing.status_code == 401

    missing_user = client.get("/api/workflow-runs", headers={"X-API-Key": "secret"})
    assert missing_user.status_code == 401
    assert missing_user.json()["detail"] == "X-User-Id is required"

    ok = client.get("/api/workflow-runs", headers={"X-User-Id": "user-1", "X-API-Key": "secret"})
    assert ok.status_code == 200
