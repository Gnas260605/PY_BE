from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.db.connection import connection_scope
from tests.helpers import get_unique_suffix


def test_dev_01_list_and_filter_devices(client: TestClient, admin_headers: dict[str, str]):
    """DEV-01: List devices, filter by status (ACTIVE, MAINTENANCE, BROKEN) and type."""
    res = client.get("/api/devices", headers=admin_headers)
    assert res.status_code == 200
    devices = res.json()
    assert isinstance(devices, list)
    assert len(devices) >= 7

    # Filter by status
    res_maint = client.get("/api/devices?status=MAINTENANCE", headers=admin_headers)
    assert res_maint.status_code == 200
    for d in res_maint.json():
        assert d["trang_thai"] == "MAINTENANCE"

    # Filter by type
    res_type = client.get("/api/devices?type=PRINTER", headers=admin_headers)
    assert res_type.status_code == 200
    for d in res_type.json():
        assert d["loai_thiet_bi"] == "PRINTER"


def test_dev_02_and_03_create_device_and_duplicate(client: TestClient, admin_headers: dict[str, str]):
    """DEV-02, DEV-03: Create device (201); Duplicate device code returns 409."""
    suffix = get_unique_suffix()
    code = f"DEV-{suffix[:10].upper()}"
    payload = {
        "ma_thiet_bi": code,
        "ten_thiet_bi": f"Laptop QA {suffix}",
        "loai_thiet_bi": "LAPTOP",
        "vi_tri": "Tầng 3",
        "trang_thai": "ACTIVE",
        "mo_ta": "Mô tả thiết bị kiểm thử",
    }
    # DEV-02: Create valid device
    res = client.post("/api/devices", headers=admin_headers, json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["ma_thiet_bi"] == code
    assert created["trang_thai"] == "ACTIVE"

    # Verify DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, ma_thiet_bi, trang_thai FROM DEVICES WHERE ma_thiet_bi = %s", (code,))
        row = cur.fetchone()
        assert row is not None
        assert row[1] == code

    # DEV-03: Duplicate code -> 409 Conflict
    dup_payload = dict(payload)
    dup_payload["ten_thiet_bi"] = "Thiết bị trùng mã"
    res_dup = client.post("/api/devices", headers=admin_headers, json=dup_payload)
    assert res_dup.status_code == 409


def test_dev_04_boundary_validation(client: TestClient, admin_headers: dict[str, str]):
    """DEV-04: Missing fields, blank code, invalid status, string too long."""
    # Blank code
    res_blank = client.post("/api/devices", headers=admin_headers, json={
        "ma_thiet_bi": "",
        "ten_thiet_bi": "Test Name",
    })
    assert res_blank.status_code == 400

    # Invalid status
    res_status = client.post("/api/devices", headers=admin_headers, json={
        "ma_thiet_bi": f"CODE-{get_unique_suffix()[:8]}",
        "ten_thiet_bi": "Test Name",
        "trang_thai": "EXPLODED",
    })
    assert res_status.status_code == 400

    # Code too long (>50 chars)
    res_long = client.post("/api/devices", headers=admin_headers, json={
        "ma_thiet_bi": "A" * 60,
        "ten_thiet_bi": "Test Name",
    })
    assert res_long.status_code == 400


def test_dev_05_update_device(client: TestClient, admin_headers: dict[str, str]):
    """DEV-05: Admin updates name, location, description, status."""
    suffix = get_unique_suffix()
    update_payload = {
        "ten_thiet_bi": f"Tên mới {suffix}",
        "vi_tri": "Phòng IT Mới",
        "trang_thai": "MAINTENANCE",
        "mo_ta": "Đã bảo trì định kỳ",
    }
    res = client.patch("/api/devices/1", headers=admin_headers, json=update_payload)
    assert res.status_code == 200
    updated = res.json()
    assert updated["ten_thiet_bi"] == update_payload["ten_thiet_bi"]
    assert updated["trang_thai"] == "MAINTENANCE"

    # Verify DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT ten_thiet_bi, vi_tri, trang_thai FROM DEVICES WHERE id = 1")
        row = cur.fetchone()
        assert row[0] == update_payload["ten_thiet_bi"]
        assert row[2] == "MAINTENANCE"


def test_dev_06_technician_device_permissions(client: TestClient, tech_headers: dict[str, str]):
    """DEV-06: Technician can view devices and update allowed status."""
    # Tech can view
    res = client.get("/api/devices", headers=tech_headers)
    assert res.status_code == 200

    # Tech can view single device
    res_one = client.get("/api/devices/1", headers=tech_headers)
    assert res_one.status_code == 200

    # Tech updates status
    res_update = client.patch("/api/devices/1", headers=tech_headers, json={"trang_thai": "ACTIVE"})
    assert res_update.status_code == 200
    assert res_update.json()["trang_thai"] == "ACTIVE"


def test_dev_07_user_forbidden(client: TestClient, user_headers: dict[str, str]):
    """DEV-07: USER is forbidden from admin/tech device endpoints."""
    assert client.get("/api/devices", headers=user_headers).status_code == 403
    assert client.post("/api/devices", headers=user_headers, json={"ma_thiet_bi": "DEV-X"}).status_code == 403
    assert client.patch("/api/devices/1", headers=user_headers, json={"trang_thai": "ACTIVE"}).status_code == 403


def test_dev_08_device_tickets(client: TestClient, admin_headers: dict[str, str]):
    """DEV-08: GET /devices/{id}/tickets with and without tickets (empty returns [])."""
    # Device 1 has tickets in seed
    res_with = client.get("/api/devices/1/tickets", headers=admin_headers)
    assert res_with.status_code == 200
    assert isinstance(res_with.json(), list)

    # Device 4 has no tickets
    res_empty = client.get("/api/devices/4/tickets", headers=admin_headers)
    assert res_empty.status_code == 200
    assert res_empty.json() == []


def test_dev_09_nonexistent_device(client: TestClient, admin_headers: dict[str, str]):
    """DEV-09: Nonexistent device ID -> 404; Invalid ID -> 400/422."""
    assert client.get("/api/devices/999999", headers=admin_headers).status_code == 404
    assert client.patch("/api/devices/999999", headers=admin_headers, json={"ten_thiet_bi": "X"}).status_code == 404


def test_dev_10_broken_device_excluded_from_active_list(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    """DEV-10: Broken/maintenance device is excluded from /devices/active-list for ticket creation."""
    # Set device 2 to BROKEN
    client.patch("/api/devices/2", headers=admin_headers, json={"trang_thai": "BROKEN"})

    # Check active-list
    res = client.get("/api/devices/active-list", headers=user_headers)
    assert res.status_code == 200
    active_devices = res.json()
    # Device 2 must not be in active list
    assert not any(d["id"] == 2 for d in active_devices)
    assert all(d["trang_thai"] == "ACTIVE" for d in active_devices)

    # Restore device 2 to ACTIVE
    client.patch("/api/devices/2", headers=admin_headers, json={"trang_thai": "ACTIVE"})
