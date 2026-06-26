from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.factory import get_repositories
from app.services.skill_runner import skill_runner


def test_list_skills():
    client = TestClient(create_app())
    response = client.get("/api/skills/list")
    assert response.status_code == 200
    assert "productized_offer" in response.json()


def test_get_skill_run_requires_auth_in_production(monkeypatch):
    monkeypatch.setenv("REVENUEPILOT_ENV", "production")
    monkeypatch.setenv("REVENUEPILOT_API_KEY", "secret")
    client = TestClient(create_app())
    response = client.get("/api/skills/runs")
    assert response.status_code == 401
    body = response.json()
    assert "detail" in body


def test_list_and_get_skill_runs(monkeypatch):
    client = TestClient(create_app())
    asyncio.run(
        skill_runner.run(
            user_id="user-ui",
            project_id="project-ui",
            skill_name="productized_offer",
            input_payload={"selected_niche": "local clinics"},
        )
    )

    response = client.get("/api/skills/runs", headers={"X-User-Id": "user-ui"})
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) == 1
    assert runs[0]["skill_name"] == "productized_offer"

    run_id = runs[0]["id"]
    response = client.get(f"/api/skills/runs/{run_id}", headers={"X-User-Id": "user-ui"})
    assert response.status_code == 200
    assert response.json()["id"] == run_id


def test_get_skill_run_enforces_user_isolation(monkeypatch):
    client = TestClient(create_app())
    asyncio.run(
        skill_runner.run(
            user_id="user-a",
            project_id="project-a",
            skill_name="productized_offer",
            input_payload={"selected_niche": "local clinics"},
        )
    )
    run = next(iter(get_repositories().skill_runs.records.values()))

    response = client.get(f"/api/skills/runs/{run.id}", headers={"X-User-Id": "user-b"})
    assert response.status_code == 403
