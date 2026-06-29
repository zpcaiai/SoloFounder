from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import reset_settings_cache
from app.main import create_app


@pytest.fixture(autouse=True)
def _reset_settings_after():
    yield
    reset_settings_cache()


def _client(monkeypatch, origins: str) -> TestClient:
    monkeypatch.setenv("CORS_ORIGINS", origins)
    reset_settings_cache()
    return TestClient(create_app())


def test_wildcard_origin_disables_credentials(monkeypatch):
    client = _client(monkeypatch, "*")
    r = client.get("/health", headers={"Origin": "https://example.com"})
    assert r.headers.get("access-control-allow-origin") == "*"
    # Browsers reject credentials with a wildcard origin, so the header must be absent.
    assert "access-control-allow-credentials" not in r.headers


def test_explicit_origin_enables_credentials(monkeypatch):
    client = _client(monkeypatch, "https://app.example.com")
    r = client.get("/health", headers={"Origin": "https://app.example.com"})
    assert r.headers.get("access-control-allow-origin") == "https://app.example.com"
    assert r.headers.get("access-control-allow-credentials") == "true"
