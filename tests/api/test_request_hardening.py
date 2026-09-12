from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from tests.helpers import (
    generate_ticket_data,
    query_ticket_by_id,
    is_database_connected,
)


def test_post_ticket_extra_fields_forbidden(client: TestClient, user_headers: dict[str, str]):
    """POST /api/tickets with unexpected fields must be rejected (400) and cause NO DB mutation."""
    payload = generate_ticket_data()
    # Inject forbidden fields
    payload["user_id"] = 9999
    payload["status"] = "CLOSED"
    payload["technician_id"] = 9999
    payload["hack_param"] = "malicious_input"

    response = client.post("/api/tickets", headers=user_headers, json=payload)
    assert response.status_code == 400, f"Expected 400 for extra fields, got {response.status_code}"

    body = response.json()
    assert body.get("detail") == "INVALID_INPUT"

    # Verify no DB mutation: query by title
    if is_database_connected():
        from app.db.connection import connection_scope
        with connection_scope() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM TICKETS WHERE tieu_de = %s", (payload["title"],))
            row = cursor.fetchone()
            assert row is None, "Database was mutated despite invalid input rejection!"


def test_patch_ticket_extra_and_forbidden_fields(
    client: TestClient, user_headers: dict[str, str]
):
    """PATCH /api/tickets/{id} with forbidden fields (status, technician_id, user_id, closed_at) must be rejected with 400."""
    # First create a valid ticket to test patch on
    valid_payload = generate_ticket_data()
    res_create = client.post("/api/tickets", headers=user_headers, json=valid_payload)
    assert res_create.status_code == 201
    ticket_id = res_create.json()["id"]

    # Read original state before test
    initial_db_state = query_ticket_by_id(ticket_id)

    # Attempt to tamper with status and technician via PATCH /tickets/{id}
    tamper_payload = {
        "title": "Valid title edit",
        "status": "CLOSED",
        "technician_id": 2,
        "closed_at": "2026-01-01T00:00:00",
    }
    res_patch = client.patch(f"/api/tickets/{ticket_id}", headers=user_headers, json=tamper_payload)
    assert res_patch.status_code == 400, f"Expected 400 for forbidden patch fields, got {res_patch.status_code}"

    # Verify No DB Mutation occurred
    if is_database_connected():
        post_db_state = query_ticket_by_id(ticket_id)
        assert post_db_state is not None
        assert post_db_state["trang_thai"] == "OPEN"
        assert post_db_state["technician_id"] is None
        assert post_db_state["closed_at"] is None
        # Title must remain untouched because the entire request was rejected
        assert post_db_state["tieu_de"] == valid_payload["title"]


def test_post_login_extra_fields_forbidden(client: TestClient):
    """POST /api/login with extra/injected fields must return 400."""
    payload = {
        "username": "admin",
        "password": "CS466@123",
        "role": "SUPERADMIN",
        "is_admin": True,
    }
    response = client.post("/api/login", json=payload)
    assert response.status_code == 400, f"Expected 400 for extra fields in login, got {response.status_code}"
    body = response.json()
    assert body.get("detail") == "INVALID_INPUT"
