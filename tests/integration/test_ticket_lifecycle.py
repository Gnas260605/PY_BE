from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from tests.helpers import (
    generate_ticket_data,
    query_ticket_by_id,
    query_ticket_history,
    is_database_connected,
)


def test_ticket_lifecycle_happy_path_and_db_audit(
    client: TestClient,
    user_headers: dict[str, str],
    admin_headers: dict[str, str],
    tech_headers: dict[str, str],
):
    """
    Complete isolated ticket lifecycle:
    CREATE(OPEN) -> ASSIGN(ASSIGNED) -> STATUS(IN_PROGRESS) -> STATUS(RESOLVED) -> CLOSE(CLOSED)
    Includes strict verification of history timeline (5 records) and direct database state audit.
    """
    # 1. USER creates ticket -> Status: OPEN
    t_data = generate_ticket_data(device_id=1)
    res_create = client.post("/api/tickets", headers=user_headers, json=t_data)
    assert res_create.status_code == 201
    created_ticket = res_create.json()
    ticket_id = created_ticket["id"]
    assert created_ticket["status"] == "OPEN"
    assert created_ticket["technician_id"] is None
    assert created_ticket["resolved_at"] is None
    assert created_ticket["closed_at"] is None

    # 2. ADMIN assigns technician (tech01 has user_id 2) -> Status: ASSIGNED
    res_assign = client.patch(
        f"/api/tickets/{ticket_id}/assign",
        headers=admin_headers,
        json={"technician_id": 2},
    )
    assert res_assign.status_code == 200
    assigned_ticket = res_assign.json()
    assert assigned_ticket["status"] == "ASSIGNED"
    assert assigned_ticket["technician_id"] == 2

    # 3. TECHNICIAN changes status ASSIGNED -> IN_PROGRESS
    res_in_progress = client.patch(
        f"/api/tickets/{ticket_id}/status",
        headers=tech_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert res_in_progress.status_code == 200
    in_prog_ticket = res_in_progress.json()
    assert in_prog_ticket["status"] == "IN_PROGRESS"

    # 4. TECHNICIAN changes status IN_PROGRESS -> RESOLVED
    res_resolved = client.patch(
        f"/api/tickets/{ticket_id}/status",
        headers=tech_headers,
        json={"status": "RESOLVED"},
    )
    assert res_resolved.status_code == 200
    resolved_ticket = res_resolved.json()
    assert resolved_ticket["status"] == "RESOLVED"
    assert resolved_ticket["resolved_at"] is not None

    # 5. TECHNICIAN closes ticket RESOLVED -> CLOSED
    close_note = "QA Lifecycle Test completed successfully"
    res_close = client.patch(
        f"/api/tickets/{ticket_id}/close",
        headers=tech_headers,
        json={"note": close_note},
    )
    assert res_close.status_code == 200
    closed_ticket = res_close.json()
    assert closed_ticket["status"] == "CLOSED"
    assert closed_ticket["closed_at"] is not None

    # -------------------------------------------------------------
    # 6. HISTORY AUDIT: GET /api/tickets/{id}/history
    # -------------------------------------------------------------
    res_history = client.get(f"/api/tickets/{ticket_id}/history", headers=user_headers)
    assert res_history.status_code == 200
    history = res_history.json()

    # Must contain exactly 5 business records
    assert len(history) == 5, f"Expected exactly 5 history records, got {len(history)}: {history}"

    expected_actions = [
        ("CREATED", None, "OPEN"),
        ("ASSIGNED", "OPEN", "ASSIGNED"),
        ("STATUS_CHANGED", "ASSIGNED", "IN_PROGRESS"),
        ("STATUS_CHANGED", "IN_PROGRESS", "RESOLVED"),
        ("CLOSED", "RESOLVED", "CLOSED"),
    ]

    closed_count = 0
    previous_time = None

    for i, (record, (exp_action, exp_old, exp_new)) in enumerate(zip(history, expected_actions)):
        assert record["action"] == exp_action, f"Step {i}: Expected action {exp_action}, got {record['action']}"
        assert record["old_status"] == exp_old, f"Step {i}: Expected old_status {exp_old}, got {record['old_status']}"
        assert record["new_status"] == exp_new, f"Step {i}: Expected new_status {exp_new}, got {record['new_status']}"

        if record["action"] == "CLOSED":
            closed_count += 1
            assert record["detail"] == close_note

        # Verify performed_at ascending
        current_time = record["performed_at"]
        if previous_time is not None:
            assert current_time >= previous_time, f"History timestamp not ascending: {previous_time} -> {current_time}"
        previous_time = current_time

    # Assert CLOSED strictly occurs exactly once
    assert closed_count == 1, f"Expected CLOSED exactly once, but appeared {closed_count} times"

    # -------------------------------------------------------------
    # 7. DIRECT DB AUDIT: Query MySQL table directly
    # -------------------------------------------------------------
    if is_database_connected():
        db_ticket = query_ticket_by_id(ticket_id)
        assert db_ticket is not None, f"Ticket {ticket_id} not found in DB directly!"
        assert db_ticket["trang_thai"] == "CLOSED", f"Expected DB status CLOSED, got {db_ticket['trang_thai']}"
        assert db_ticket["technician_id"] == 2, f"Expected DB technician_id 2, got {db_ticket['technician_id']}"
        assert db_ticket["resolved_at"] is not None, "DB resolved_at must not be null"
        assert db_ticket["closed_at"] is not None, "DB closed_at must not be null"

        # Verify DB history matches API history
        db_history = query_ticket_history(ticket_id)
        assert len(db_history) == 5


def test_ticket_negative_transitions(
    client: TestClient,
    user_headers: dict[str, str],
    admin_headers: dict[str, str],
    tech_headers: dict[str, str],
):
    """Verify strictly forbidden ticket status transitions return 400 INVALID_TRANSITION."""
    # 1. Create a fresh ticket in OPEN status
    t_data = generate_ticket_data(device_id=1)
    res_c = client.post("/api/tickets", headers=user_headers, json=t_data)
    ticket_id = res_c.json()["id"]

    # Negative 1: OPEN -> ASSIGNED via PATCH /status (must be done via /assign instead)
    res_neg1 = client.patch(
        f"/api/tickets/{ticket_id}/status",
        headers=admin_headers,
        json={"status": "ASSIGNED"},
    )
    assert res_neg1.status_code == 400, f"Expected 400 for OPEN->ASSIGNED via /status, got {res_neg1.status_code}"
    assert res_neg1.json().get("detail") == "INVALID_TRANSITION"

    # Now assign it properly to tech01
    client.patch(f"/api/tickets/{ticket_id}/assign", headers=admin_headers, json={"technician_id": 2})

    # Move to IN_PROGRESS -> RESOLVED
    client.patch(f"/api/tickets/{ticket_id}/status", headers=tech_headers, json={"status": "IN_PROGRESS"})
    client.patch(f"/api/tickets/{ticket_id}/status", headers=tech_headers, json={"status": "RESOLVED"})

    # Negative 2: RESOLVED -> CLOSED via PATCH /status (must use /close instead)
    res_neg2 = client.patch(
        f"/api/tickets/{ticket_id}/status",
        headers=tech_headers,
        json={"status": "CLOSED"},
    )
    assert res_neg2.status_code == 400, f"Expected 400 for RESOLVED->CLOSED via /status, got {res_neg2.status_code}"
    assert res_neg2.json().get("detail") == "INVALID_TRANSITION"

    # Negative 3: Backward transition RESOLVED -> OPEN
    res_neg3 = client.patch(
        f"/api/tickets/{ticket_id}/status",
        headers=tech_headers,
        json={"status": "OPEN"},
    )
    assert res_neg3.status_code == 400
    assert res_neg3.json().get("detail") == "INVALID_TRANSITION"

    # Now close it properly via /close
    res_close1 = client.patch(f"/api/tickets/{ticket_id}/close", headers=tech_headers, json={"note": "Close 1"})
    assert res_close1.status_code == 200

    # Negative 4: Call /close a SECOND time on already CLOSED ticket (re-close)
    res_close2 = client.patch(f"/api/tickets/{ticket_id}/close", headers=tech_headers, json={"note": "Close 2"})
    assert res_close2.status_code == 400, f"Expected 400 for re-closing ticket, got {res_close2.status_code}"
    assert res_close2.json().get("detail") == "INVALID_TRANSITION"
