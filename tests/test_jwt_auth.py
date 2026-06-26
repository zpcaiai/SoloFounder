from __future__ import annotations

import time

from app.core.config import reset_settings_cache
from app.core.security import _decode_jwt
from app.main import create_app
from app.repositories.factory import reset_repository_bundle
from fastapi.testclient import TestClient


def _client(monkeypatch, *, env: str = "development", jwt_secret: str | None = None) -> TestClient:
    monkeypatch.setenv("REVENUEPILOT_ENV", env)
    if jwt_secret:
        monkeypatch.setenv("SUPABASE_JWT_SECRET", jwt_secret)
    else:
        monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    monkeypatch.delenv("REVENUEPILOT_API_KEY", raising=False)
    reset_settings_cache()
    reset_repository_bundle()
    return TestClient(create_app())


def _make_token(secret: str, sub: str = "user-from-jwt") -> str:
    import jwt

    payload = {"sub": sub, "exp": int(time.time()) + 3600, "aud": "authenticated"}
    return jwt.encode(payload, secret, algorithm="HS256")


def test_jwt_auth_extracts_user_id(monkeypatch):
    secret = "test-secret-key"
    client = _client(monkeypatch, env="production", jwt_secret=secret)
    token = _make_token(secret)

    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_jwt_auth_rejects_invalid_token(monkeypatch):
    secret = "test-secret-key"
    client = _client(monkeypatch, env="production", jwt_secret=secret)

    response = client.get(
        "/api/projects",
        headers={"Authorization": "Bearer invalid-token-here"},
    )
    assert response.status_code == 401


def test_jwt_auth_rejects_expired_token(monkeypatch):
    secret = "test-secret-key"
    client = _client(monkeypatch, env="production", jwt_secret=secret)

    import jwt

    payload = {"sub": "user-1", "exp": int(time.time()) - 100, "aud": "authenticated"}
    token = jwt.encode(payload, secret, algorithm="HS256")

    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_development_fallback_without_jwt(monkeypatch):
    client = _client(monkeypatch, env="development")
    response = client.get("/api/projects")
    assert response.status_code == 200


def test_decode_jwt_returns_payload():
    secret = "test-secret"
    import jwt

    payload = {"sub": "user-1", "exp": int(time.time()) + 3600, "aud": "authenticated"}
    token = jwt.encode(payload, secret, algorithm="HS256")
    decoded = _decode_jwt(token, secret)
    assert decoded["sub"] == "user-1"
