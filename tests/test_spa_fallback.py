from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_root_serves_spa_html():
    response = _client().get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<div id=\"root\">" in response.text


def test_client_side_route_serves_spa_html():
    # Deep links to client-side routes must return the SPA shell, not 404.
    response = _client().get("/ideas")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_unknown_api_route_returns_json_404():
    response = _client().get("/api/this-route-does-not-exist")
    assert response.status_code == 404
    assert "application/json" in response.headers["content-type"]
    body = response.json()
    assert body["detail"] == "Not Found"
    # Error envelope carries the correlation id for support/debugging.
    assert "request_id" in body
    assert response.headers.get("X-Request-ID")


def test_unknown_reserved_namespace_returns_404_not_html():
    for path in ("/api", "/openapi-not-real", "/docs/missing"):
        response = _client().get(path)
        assert response.status_code == 404, path
        assert "text/html" not in response.headers["content-type"], path
