from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_project_crud_lifecycle():
    client = TestClient(create_app())

    create = client.post(
        "/api/projects",
        json={"name": "Test Project", "description": "A test"},
        headers={"X-User-Id": "user-1"},
    )
    assert create.status_code == 200
    project = create.json()
    project_id = project["id"]
    assert project["data"]["name"] == "Test Project"

    get = client.get(f"/api/projects/{project_id}", headers={"X-User-Id": "user-1"})
    assert get.status_code == 200
    assert get.json()["id"] == project_id

    update = client.put(
        f"/api/projects/{project_id}",
        json={"name": "Updated Project"},
        headers={"X-User-Id": "user-1"},
    )
    assert update.status_code == 200
    assert update.json()["data"]["name"] == "Updated Project"

    listing = client.get("/api/projects", headers={"X-User-Id": "user-1"})
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    delete = client.delete(f"/api/projects/{project_id}", headers={"X-User-Id": "user-1"})
    assert delete.status_code == 200
    assert delete.json()["status"] == "deleted"

    get_after = client.get(f"/api/projects/{project_id}", headers={"X-User-Id": "user-1"})
    assert get_after.status_code == 404


def test_project_user_isolation():
    client = TestClient(create_app())
    create = client.post(
        "/api/projects",
        json={"name": "User A Project"},
        headers={"X-User-Id": "user-a"},
    )
    project_id = create.json()["id"]

    get_other = client.get(f"/api/projects/{project_id}", headers={"X-User-Id": "user-b"})
    assert get_other.status_code == 403

    list_other = client.get("/api/projects", headers={"X-User-Id": "user-b"})
    assert list_other.status_code == 200
    assert len(list_other.json()) == 0


def test_invalid_entity_id_returns_not_found():
    client = TestClient(create_app())
    response = client.get("/api/projects/not-a-uuid", headers={"X-User-Id": "user-1"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_idea_crud_and_convert():
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={"name": "P1"},
        headers={"X-User-Id": "user-1"},
    ).json()
    project_id = project["id"]

    idea = client.post(
        f"/api/projects/{project_id}/ideas",
        json={"title": "AI automation for clinics", "target_customer": "clinics"},
        headers={"X-User-Id": "user-1"},
    )
    assert idea.status_code == 200
    idea_id = idea.json()["id"]

    listing = client.get(f"/api/projects/{project_id}/ideas", headers={"X-User-Id": "user-1"})
    assert len(listing.json()) == 1

    update = client.put(
        f"/api/projects/{project_id}/ideas/{idea_id}",
        json={"status": "validated"},
        headers={"X-User-Id": "user-1"},
    )
    assert update.status_code == 200
    assert update.json()["data"]["status"] == "validated"


def test_offer_crud():
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={"name": "P1"},
        headers={"X-User-Id": "user-1"},
    ).json()
    project_id = project["id"]

    offer = client.post(
        f"/api/projects/{project_id}/offers",
        json={"offer_name": "Lead Sprint", "one_line_promise": "10 qualified leads in 30 days"},
        headers={"X-User-Id": "user-1"},
    )
    assert offer.status_code == 200
    offer_id = offer.json()["id"]

    get = client.get(f"/api/projects/{project_id}/offers/{offer_id}", headers={"X-User-Id": "user-1"})
    assert get.status_code == 200

    listing = client.get(f"/api/projects/{project_id}/offers", headers={"X-User-Id": "user-1"})
    assert len(listing.json()) == 1


def test_lead_and_deal_crud():
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={"name": "P1"},
        headers={"X-User-Id": "user-1"},
    ).json()
    project_id = project["id"]

    lead = client.post(
        f"/api/projects/{project_id}/leads",
        json={"name": "John Doe", "company": "Acme", "email": "john@acme.com"},
        headers={"X-User-Id": "user-1"},
    )
    assert lead.status_code == 200
    lead_id = lead.json()["id"]

    deal = client.post(
        f"/api/projects/{project_id}/deals",
        json={"lead_id": lead_id, "stage": "new", "expected_value": 5000},
        headers={"X-User-Id": "user-1"},
    )
    assert deal.status_code == 200
    deal_id = deal.json()["id"]

    mark_won = client.post(
        f"/api/projects/{project_id}/deals/{deal_id}/mark-won",
        headers={"X-User-Id": "user-1"},
    )
    assert mark_won.status_code == 200
    assert mark_won.json()["data"]["stage"] == "won"


def test_landing_page_publish_unpublish():
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={"name": "P1"},
        headers={"X-User-Id": "user-1"},
    ).json()
    project_id = project["id"]

    lp = client.post(
        f"/api/projects/{project_id}/landing-pages",
        json={"title": "My Landing Page"},
        headers={"X-User-Id": "user-1"},
    )
    assert lp.status_code == 200
    lp_id = lp.json()["id"]

    publish = client.post(
        f"/api/projects/{project_id}/landing-pages/{lp_id}/publish",
        headers={"X-User-Id": "user-1"},
    )
    assert publish.status_code == 200
    assert publish.json()["data"]["published"] is True

    unpublish = client.post(
        f"/api/projects/{project_id}/landing-pages/{lp_id}/unpublish",
        headers={"X-User-Id": "user-1"},
    )
    assert unpublish.status_code == 200
    assert unpublish.json()["data"]["published"] is False


def test_revenue_crud_and_summary():
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={"name": "P1"},
        headers={"X-User-Id": "user-1"},
    ).json()
    project_id = project["id"]

    for amount in [1000, 2000, 3000]:
        client.post(
            f"/api/projects/{project_id}/revenue",
            json={"amount": amount, "customer_name": "Test"},
            headers={"X-User-Id": "user-1"},
        )

    summary = client.get(
        f"/api/projects/{project_id}/revenue/summary/total",
        headers={"X-User-Id": "user-1"},
    )
    assert summary.status_code == 200
    assert summary.json()["total_revenue"] == 6000
    assert summary.json()["count"] == 3


def test_dashboard_returns_summary():
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={"name": "P1"},
        headers={"X-User-Id": "user-1"},
    ).json()
    project_id = project["id"]

    client.post(
        f"/api/projects/{project_id}/leads",
        json={"name": "Lead 1"},
        headers={"X-User-Id": "user-1"},
    )
    client.post(
        f"/api/projects/{project_id}/offers",
        json={"offer_name": "Offer 1"},
        headers={"X-User-Id": "user-1"},
    )

    dashboard = client.get(
        f"/api/projects/{project_id}/dashboard",
        headers={"X-User-Id": "user-1"},
    )
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert data["active_leads"] == 1
    assert data["offers_count"] == 1
    assert len(data["next_actions"]) > 0


def test_profile_upsert():
    client = TestClient(create_app())

    get_empty = client.get("/api/profile", headers={"X-User-Id": "user-1"})
    assert get_empty.status_code == 200

    upsert = client.put(
        "/api/profile",
        json={"display_name": "John", "email": "john@test.com"},
        headers={"X-User-Id": "user-1"},
    )
    assert upsert.status_code == 200
    assert upsert.json()["data"]["display_name"] == "John"

    get_after = client.get("/api/profile", headers={"X-User-Id": "user-1"})
    assert get_after.status_code == 200
    assert get_after.json()["data"]["display_name"] == "John"


def test_delivery_project_and_tasks():
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={"name": "P1"},
        headers={"X-User-Id": "user-1"},
    ).json()
    project_id = project["id"]

    dp = client.post(
        f"/api/projects/{project_id}/delivery/projects",
        json={"title": "Delivery Project", "client_name": "Acme"},
        headers={"X-User-Id": "user-1"},
    )
    assert dp.status_code == 200
    dp_id = dp.json()["id"]

    task = client.post(
        f"/api/projects/{project_id}/delivery/projects/{dp_id}/tasks",
        json={"delivery_project_id": dp_id, "title": "Setup environment"},
        headers={"X-User-Id": "user-1"},
    )
    assert task.status_code == 200

    tasks = client.get(
        f"/api/projects/{project_id}/delivery/projects/{dp_id}/tasks",
        headers={"X-User-Id": "user-1"},
    )
    assert tasks.status_code == 200
    assert len(tasks.json()) == 1
