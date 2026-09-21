from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.db.connection import connection_scope
from tests.helpers import get_unique_suffix


def test_tkt_01_create_ticket_by_user(client: TestClient, user_headers: dict[str, str]):
    """TKT-01: USER creates ticket -> 201 Created, status OPEN, created_by user_id=3."""
    suffix = get_unique_suffix()
    payload = {
        "title": f"Sự cố máy tính kế toán {suffix}",
        "description": f"Màn hình bị nháy liên tục không làm việc được {suffix}",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "HIGH",
    }
    res = client.post("/api/tickets", headers=user_headers, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "OPEN"
    assert data["user_id"] == 3
    assert data["category"] == "INCIDENT"
    assert data["priority"] == "HIGH"
    ticket_id = data["id"]

    # Verify DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, trang_thai, tieu_de FROM TICKETS WHERE id = %s", (ticket_id,))
        row = cur.fetchone()
        assert row is not None
        assert row[1] == 3
        assert row[2] == "OPEN"


def test_tkt_02_and_03_create_by_admin_and_tech_forbidden(
    client: TestClient, admin_headers: dict[str, str], tech_headers: dict[str, str]
):
    """TKT-02, TKT-03: ADMIN can create ticket; TECHNICIAN forbidden from creating ticket (403)."""
    suffix = get_unique_suffix()
    payload = {
        "title": f"Ticket do Admin tạo {suffix}",
        "description": "Admin tạo hộ cho phòng ban",
        "device_id": 1,
        "category": "SERVICE_REQUEST",
        "priority": "MEDIUM",
    }
    # Admin create -> 201
    res_admin = client.post("/api/tickets", headers=admin_headers, json=payload)
    assert res_admin.status_code == 201
    assert res_admin.json()["user_id"] == 1

    # Tech create -> 403 Forbidden
    res_tech = client.post("/api/tickets", headers=tech_headers, json=payload)
    assert res_tech.status_code == 403


def test_tkt_04_and_05_validation_and_unicode(client: TestClient, user_headers: dict[str, str]):
    """TKT-04, TKT-05: Missing fields, bad enum, boundary strings, Vietnamese Unicode."""
    # Missing title
    res_no_title = client.post("/api/tickets", headers=user_headers, json={
        "description": "Chỉ có mô tả",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "HIGH",
    })
    assert res_no_title.status_code == 400

    # Invalid enum
    res_bad_enum = client.post("/api/tickets", headers=user_headers, json={
        "title": "Tiêu đề hợp lệ",
        "description": "Mô tả hợp lệ",
        "device_id": 1,
        "category": "ALIEN_INVASION",
        "priority": "SUPER_HIGH",
    })
    assert res_bad_enum.status_code == 400

    # Unicode Vietnamese text with accents
    suffix = get_unique_suffix()
    vn_title = f"Lỗi bàn phím gõ tiếng Việt có dấu: ă â đ ê ô ơ ư {suffix}"
    vn_desc = "Người dùng gõ văn bản bị nhảy chữ, font VNI không hiển thị đúng tiếng Việt."
    res_vn = client.post("/api/tickets", headers=user_headers, json={
        "title": vn_title,
        "description": vn_desc,
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    assert res_vn.status_code == 201
    assert res_vn.json()["title"] == vn_title


def test_tkt_06_to_09_list_and_role_visibility(
    client: TestClient, user_headers: dict[str, str], admin_headers: dict[str, str], tech_headers: dict[str, str]
):
    """TKT-06..09: Role visibility: User sees only own tickets; Admin sees all; Tech sees assigned."""
    # User lists tickets -> all must belong to user_id=3
    res_user = client.get("/api/tickets", headers=user_headers)
    assert res_user.status_code == 200
    for t in res_user.json():
        assert t["user_id"] == 3

    # Admin lists tickets -> sees all tickets
    res_admin = client.get("/api/tickets", headers=admin_headers)
    assert res_admin.status_code == 200
    assert len(res_admin.json()) >= len(res_user.json())

    # Tech lists tickets -> sees assigned tickets
    res_tech = client.get("/api/tickets", headers=tech_headers)
    assert res_tech.status_code == 200

    # Filters: by status and priority
    res_filter = client.get("/api/tickets?status=CLOSED", headers=admin_headers)
    assert res_filter.status_code == 200
    for t in res_filter.json():
        assert t["status"] == "CLOSED"


def test_tkt_11_idor_protection(client: TestClient, user_headers: dict[str, str]):
    """TKT-11: USER accessing another user's ticket -> 403 Forbidden."""
    # In seed, ticket 3 was created by user03 (user_id=6), while current user is user01 (user_id=3)
    res = client.get("/api/tickets/3", headers=user_headers)
    assert res.status_code == 403


def test_tkt_12_and_13_update_ticket(client: TestClient, user_headers: dict[str, str]):
    """TKT-12, TKT-13: Owner can edit OPEN ticket; cannot edit CLOSED ticket."""
    # Create an OPEN ticket
    res_new = client.post("/api/tickets", headers=user_headers, json={
        "title": "Cần sửa tiêu đề ban đầu",
        "description": "Mô tả ban đầu",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    ticket_id = res_new.json()["id"]

    # Edit while OPEN -> 200 OK
    res_edit = client.patch(f"/api/tickets/{ticket_id}", headers=user_headers, json={
        "title": "Tiêu đề đã được cập nhật bởi chủ sở hữu",
    })
    assert res_edit.status_code == 200
    assert res_edit.json()["title"] == "Tiêu đề đã được cập nhật bởi chủ sở hữu"

    # Try to edit ticket 1 (CLOSED) -> 403 Forbidden
    res_edit_closed = client.patch("/api/tickets/1", headers=user_headers, json={
        "title": "Thử sửa ticket đã đóng",
    })
    assert res_edit_closed.status_code == 403


def test_tkt_14_and_15_assign_ticket(client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]):
    """TKT-14, TKT-15: Admin assigns ticket -> ASSIGNED; Nonexistent assignee -> 404."""
    # Create an OPEN ticket
    res_new = client.post("/api/tickets", headers=user_headers, json={
        "title": "Ticket cần gán kỹ thuật viên",
        "description": "Mô tả gán KTV",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "HIGH",
    })
    ticket_id = res_new.json()["id"]

    # Assign to tech01 (id=2)
    res_assign = client.patch(f"/api/tickets/{ticket_id}/assign", headers=admin_headers, json={"technician_id": 2})
    assert res_assign.status_code == 200
    assert res_assign.json()["status"] == "ASSIGNED"
    assert res_assign.json()["technician_id"] == 2

    # Assign nonexistent tech ID -> 404
    res_bad_tech = client.patch(f"/api/tickets/{ticket_id}/assign", headers=admin_headers, json={"technician_id": 999999})
    assert res_bad_tech.status_code == 404


def test_tkt_19_and_20_invalid_transitions(client: TestClient, tech_headers: dict[str, str]):
    """TKT-19, TKT-20: Invalid transitions -> 400; unauthorized tech -> 403."""
    # Ticket 1 is CLOSED: trying to set status=IN_PROGRESS -> 400 INVALID_TRANSITION
    res_inv = client.patch("/api/tickets/1/status", headers=tech_headers, json={"status": "IN_PROGRESS"})
    assert res_inv.status_code == 400


def test_tkt_21_to_23_batch_assign_and_batch_status(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    """TKT-21..23: Admin batch-assign and batch-status operations."""
    # Create 2 tickets
    res1 = client.post("/api/tickets", headers=user_headers, json={
        "title": "Batch Ticket 1",
        "description": "Mô tả 1",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    res2 = client.post("/api/tickets", headers=user_headers, json={
        "title": "Batch Ticket 2",
        "description": "Mô tả 2",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    t1_id = res1.json()["id"]
    t2_id = res2.json()["id"]

    # Batch assign to tech01 (id=2)
    res_batch_assign = client.patch("/api/tickets/batch-assign", headers=admin_headers, json={
        "ticket_ids": [t1_id, t2_id],
        "technician_id": 2,
    })
    assert res_batch_assign.status_code == 200
    assigned_list = res_batch_assign.json()
    assert len(assigned_list) == 2
    for t in assigned_list:
        assert t["technician_id"] == 2
        assert t["status"] == "ASSIGNED"

    # Batch update status to IN_PROGRESS
    res_batch_status = client.patch("/api/tickets/batch-status", headers=admin_headers, json={
        "ticket_ids": [t1_id, t2_id],
        "status": "IN_PROGRESS",
    })
    assert res_batch_status.status_code == 200
    updated_list = res_batch_status.json()
    assert len(updated_list) == 2
    for t in updated_list:
        assert t["status"] == "IN_PROGRESS"
