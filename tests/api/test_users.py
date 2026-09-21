from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.db.connection import connection_scope
from tests.helpers import get_unique_suffix


def test_usr_01_and_02_list_and_filter_users(client: TestClient, admin_headers: dict[str, str]):
    """USR-01, USR-02: Admin lists users, searches, and filters by role and status."""
    # USR-01: List all users
    res = client.get("/api/users", headers=admin_headers)
    assert res.status_code == 200
    users = res.json()
    assert isinstance(users, list)
    assert len(users) >= 7

    # Check that no password_hash is leaked
    for u in users:
        assert "password_hash" not in u
        assert "password" not in u

    # USR-02: Filter by role
    res_tech = client.get("/api/users?role=TECHNICIAN", headers=admin_headers)
    assert res_tech.status_code == 200
    techs = res_tech.json()
    assert all(u["vai_tro"] == "TECHNICIAN" for u in techs)

    # Filter by status
    res_inactive = client.get("/api/users?status=INACTIVE", headers=admin_headers)
    assert res_inactive.status_code == 200
    inactives = res_inactive.json()
    assert any(u["username"] == "user04" for u in inactives)
    assert all(u["trang_thai"] == "INACTIVE" for u in inactives)

    # Search keyword
    res_search = client.get("/api/users?keyword=admin", headers=admin_headers)
    assert res_search.status_code == 200
    assert any(u["username"] == "admin" for u in res_search.json())


def test_usr_03_create_user_and_password_hashing(client: TestClient, admin_headers: dict[str, str]):
    """USR-03: Create USER with valid data, verify bcrypt hash in DB, not plain text."""
    suffix = get_unique_suffix()
    username = f"usr3_{suffix}"
    raw_password = "SecurePassword@123"

    payload = {
        "username": username,
        "password": raw_password,
        "ho_ten": f"User Test {suffix}",
        "email": f"u3_{suffix}@cs466.test",
        "vai_tro": "USER",
    }
    res = client.post("/api/users", headers=admin_headers, json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == username
    assert data["vai_tro"] == "USER"
    assert "password_hash" not in data

    # Verify DB: bcrypt hash stored, plain text NOT stored
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM USERS WHERE username = %s", (username,))
        row = cur.fetchone()
        assert row is not None
        db_hash = row[0]
        assert db_hash != raw_password
        assert db_hash.startswith("$2b$") or db_hash.startswith("$2a$") or len(db_hash) >= 50


def test_usr_04_create_technician_and_admin(client: TestClient, admin_headers: dict[str, str]):
    """USR-04: Create TECHNICIAN and ADMIN roles, verify successful creation."""
    suffix = get_unique_suffix()
    for role in ["TECHNICIAN", "ADMIN"]:
        uname = f"{role.lower()}_{suffix}"
        payload = {
            "username": uname,
            "password": "CS466@123",
            "ho_ten": f"Name {role} {suffix}",
            "email": f"{uname}@cs466.test",
            "vai_tro": role,
        }
        res = client.post("/api/users", headers=admin_headers, json=payload)
        assert res.status_code == 201
        assert res.json()["vai_tro"] == role


def test_usr_05_create_duplicate_username_and_email(client: TestClient, admin_headers: dict[str, str]):
    """USR-05: Duplicate username or email must return 409 Conflict."""
    suffix = get_unique_suffix()
    base_payload = {
        "username": f"dup_u_{suffix}",
        "password": "CS466@123",
        "ho_ten": f"Dup User {suffix}",
        "email": f"dup_{suffix}@cs466.test",
        "vai_tro": "USER",
    }
    # First create
    res1 = client.post("/api/users", headers=admin_headers, json=base_payload)
    assert res1.status_code == 201

    # Duplicate username
    dup_uname = dict(base_payload)
    dup_uname["email"] = f"other_{suffix}@cs466.test"
    res_dup_u = client.post("/api/users", headers=admin_headers, json=dup_uname)
    assert res_dup_u.status_code == 409

    # Duplicate email
    dup_email = dict(base_payload)
    dup_email["username"] = f"other_u_{suffix}"
    res_dup_e = client.post("/api/users", headers=admin_headers, json=dup_email)
    assert res_dup_e.status_code == 409


def test_usr_06_boundary_validation(client: TestClient, admin_headers: dict[str, str]):
    """USR-06: Test boundary inputs: short username, short password, bad email, bad role."""
    suffix = get_unique_suffix()

    # Short username (<3 chars)
    res_short_u = client.post("/api/users", headers=admin_headers, json={
        "username": "ab",
        "password": "CS466@123",
        "ho_ten": "Short User",
        "email": f"short_{suffix}@cs466.test",
        "vai_tro": "USER",
    })
    assert res_short_u.status_code == 400

    # Short password (<8 chars)
    res_short_p = client.post("/api/users", headers=admin_headers, json={
        "username": f"pwd_{suffix}",
        "password": "short",
        "ho_ten": "Short Pwd",
        "email": f"pwd_{suffix}@cs466.test",
        "vai_tro": "USER",
    })
    assert res_short_p.status_code == 400

    # Bad email format
    res_bad_e = client.post("/api/users", headers=admin_headers, json={
        "username": f"email_{suffix}",
        "password": "CS466@123",
        "ho_ten": "Bad Email",
        "email": "not-an-email",
        "vai_tro": "USER",
    })
    assert res_bad_e.status_code == 400

    # Bad role
    res_bad_r = client.post("/api/users", headers=admin_headers, json={
        "username": f"role_{suffix}",
        "password": "CS466@123",
        "ho_ten": "Bad Role",
        "email": f"role_{suffix}@cs466.test",
        "vai_tro": "SUPERMAN",
    })
    assert res_bad_r.status_code == 400


def test_usr_07_update_user_details(client: TestClient, admin_headers: dict[str, str]):
    """USR-07: Update ho_ten, email; verify updated_at changes in DB."""
    suffix = get_unique_suffix()
    new_name = f"Ho Ten Moi {suffix}"
    new_email = f"updated_{suffix}@cs466.test"

    res = client.patch("/api/users/4", headers=admin_headers, json={"ho_ten": new_name, "email": new_email})
    assert res.status_code == 200
    data = res.json()
    assert data["ho_ten"] == new_name
    assert data["email"] == new_email

    # Verify DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT ho_ten, email, updated_at FROM USERS WHERE id = 4")
        row = cur.fetchone()
        assert row[0] == new_name
        assert row[1] == new_email


def test_usr_08_and_09_user_status_toggle(client: TestClient, admin_headers: dict[str, str]):
    """USR-08, USR-09: Inactive user cannot login; reactivating restores login."""
    # User 4 (user02) is currently ACTIVE
    # Deactivate user 4
    res_deact = client.patch("/api/users/4/status", headers=admin_headers, json={"status": "INACTIVE"})
    assert res_deact.status_code == 200
    assert res_deact.json()["trang_thai"] == "INACTIVE"

    # Try login as user02 -> 401 ACCOUNT_INACTIVE
    res_login = client.post("/api/login", json={"username": "user02", "password": "CS466@123"})
    assert res_login.status_code == 401

    # Reactivate user 4 (USR-09)
    res_act = client.patch("/api/users/4/status", headers=admin_headers, json={"status": "ACTIVE"})
    assert res_act.status_code == 200
    assert res_act.json()["trang_thai"] == "ACTIVE"

    # Try login again -> 200 OK
    res_login_ok = client.post("/api/login", json={"username": "user02", "password": "CS466@123"})
    assert res_login_ok.status_code == 200


def test_usr_10_role_protection_on_users_endpoints(
    client: TestClient, tech_headers: dict[str, str], user_headers: dict[str, str]
):
    """USR-10: USER and TECHNICIAN forbidden from GET/POST /api/users."""
    assert client.get("/api/users", headers=user_headers).status_code == 403
    assert client.get("/api/users", headers=tech_headers).status_code == 403
    assert client.post("/api/users", headers=user_headers, json={}).status_code == 403
    assert client.post("/api/users", headers=tech_headers, json={}).status_code == 403
