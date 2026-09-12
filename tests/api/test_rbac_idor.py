from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from tests.helpers import (
    generate_user_data,
    generate_device_data,
    generate_ticket_data,
    get_unique_suffix,
)


def test_admin_rbac_and_duplicates(client: TestClient, admin_headers: dict[str, str]):
    """ADMIN can create users and devices, and duplicates are rejected with 409."""
    # 1. Create unique user
    u_data = generate_user_data("USER")
    res_u = client.post("/api/users", headers=admin_headers, json=u_data)
    assert res_u.status_code == 201
    created_user = res_u.json()
    assert created_user["username"] == u_data["username"]

    # 2. Duplicate Username -> 409
    dup_u = generate_user_data("USER")
    dup_u["username"] = u_data["username"]  # Same username
    res_dup_u = client.post("/api/users", headers=admin_headers, json=dup_u)
    assert res_dup_u.status_code == 409

    # 3. Create unique device
    dev_data = generate_device_data()
    res_dev = client.post("/api/devices", headers=admin_headers, json=dev_data)
    assert res_dev.status_code == 201
    created_dev = res_dev.json()
    assert created_dev["ma_thiet_bi"] == dev_data["ma_thiet_bi"]

    # 4. Duplicate Device Code -> 409
    dup_dev = generate_device_data()
    dup_dev["ma_thiet_bi"] = dev_data["ma_thiet_bi"]  # Same code
    res_dup_dev = client.post("/api/devices", headers=admin_headers, json=dup_dev)
    assert res_dup_dev.status_code == 409


def test_user_rbac_and_idor_protection(
    client: TestClient, user_headers: dict[str, str], admin_headers: dict[str, str]
):
    """USER cannot access admin routes, and cannot access other users' tickets (IDOR protection)."""
    # 1. Blocked Admin Routes -> 403
    assert client.get("/api/users", headers=user_headers).status_code == 403
    assert client.post("/api/devices", headers=user_headers, json={"ma_thiet_bi": "DEV-X"}).status_code == 403
    assert client.patch("/api/tickets/1/assign", headers=user_headers, json={"technician_id": 2}).status_code == 403

    # 2. USER creates ticket (user_id taken from JWT)
    t_data = generate_ticket_data(device_id=1)
    res_create = client.post("/api/tickets", headers=user_headers, json=t_data)
    assert res_create.status_code == 201
    user_ticket = res_create.json()
    user_ticket_id = user_ticket["id"]
    assert user_ticket["user_id"] == 3  # user01 id is 3

    # 3. USER can view own ticket
    res_own = client.get(f"/api/tickets/{user_ticket_id}", headers=user_headers)
    assert res_own.status_code == 200

    # 4. IDOR Check: Ticket 1 belongs to user01 or another user?
    # In seed data, ticket 1 was created by user_id 3 (user01).
    # Let's create another ticket as ADMIN (user_id 1) and verify user01 cannot view it
    admin_ticket_data = generate_ticket_data(device_id=1)
    res_admin_t = client.post("/api/tickets", headers=admin_headers, json=admin_ticket_data)
    assert res_admin_t.status_code == 201
    admin_ticket_id = res_admin_t.json()["id"]

    # USER calls GET /api/tickets/{admin_ticket_id} -> MUST return 403 FORBIDDEN
    res_idor = client.get(f"/api/tickets/{admin_ticket_id}", headers=user_headers)
    assert res_idor.status_code == 403, f"Expected 403 for IDOR cross-tenant access, got {res_idor.status_code}"
    assert res_idor.json().get("detail") == "FORBIDDEN"

    # USER calls GET /api/tickets/{admin_ticket_id}/history -> MUST return 403 FORBIDDEN
    res_idor_hist = client.get(f"/api/tickets/{admin_ticket_id}/history", headers=user_headers)
    assert res_idor_hist.status_code == 403


def test_technician_rbac_and_field_permissions(
    client: TestClient, tech_headers: dict[str, str], admin_headers: dict[str, str]
):
    """TECHNICIAN permissions check on devices and tickets."""
    # 1. Blocked Admin Routes -> 403
    assert client.get("/api/users", headers=tech_headers).status_code == 403
    assert client.post("/api/devices", headers=tech_headers, json={"ma_thiet_bi": "DEV-T"}).status_code == 403
    assert client.patch("/api/tickets/1/assign", headers=tech_headers, json={"technician_id": 2}).status_code == 403

    # 2. Technician can view devices
    res_devs = client.get("/api/devices", headers=tech_headers)
    assert res_devs.status_code == 200

    # 3. Technician updating allowed fields (trang_thai, mo_ta) -> 200
    res_patch_allowed = client.patch(
        "/api/devices/1",
        headers=tech_headers,
        json={"trang_thai": "MAINTENANCE", "mo_ta": "KTV đang kiểm tra"},
    )
    assert res_patch_allowed.status_code == 200

    # 4. Technician updating forbidden fields (ten_thiet_bi, vi_tri, etc.) -> 403 FORBIDDEN
    res_patch_forbidden = client.patch(
        "/api/devices/1",
        headers=tech_headers,
        json={"ten_thiet_bi": "Tên thiết bị trái phép", "vi_tri": "Tầng 99"},
    )
    assert res_patch_forbidden.status_code == 403, f"Expected 403 for forbidden fields, got {res_patch_forbidden.status_code}"
    assert res_patch_forbidden.json().get("detail") == "FORBIDDEN"
