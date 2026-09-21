from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.core.rate_limiter import limiter
from app.db.connection import connection_scope
from tests.helpers import get_unique_suffix


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()


def test_auth_04_wrong_password(client: TestClient):
    """AUTH-04: Login with incorrect password returns 401."""
    res = client.post("/api/login", json={"username": "admin", "password": "WrongPassword@999"})
    assert res.status_code == 401
    data = res.json()
    assert data.get("detail") in ["AUTH_FAILED", "INVALID_CREDENTIALS", "UNAUTHORIZED"]


def test_auth_05_nonexistent_user(client: TestClient):
    """AUTH-05: Login with nonexistent username returns 401."""
    res = client.post("/api/login", json={"username": "ghost_user_9999", "password": "AnyPassword@123"})
    assert res.status_code == 401
    data = res.json()
    assert data.get("detail") in ["AUTH_FAILED", "INVALID_CREDENTIALS", "USER_NOT_FOUND", "UNAUTHORIZED"]


def test_auth_06_inactive_user(client: TestClient):
    """AUTH-06: Login with INACTIVE user returns 401/403."""
    suffix = get_unique_suffix()
    username = f"inactive_{suffix}"
    # Create user directly in DB with INACTIVE status
    with connection_scope() as conn:
        cur = conn.cursor()
        # insert user with known bcrypt hash of 'CS466@123'
        cur.execute("SELECT password_hash FROM USERS WHERE username = 'admin'")
        admin_hash = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO USERS (username, password_hash, ho_ten, email, vai_tro, trang_thai)
            VALUES (%s, %s, %s, %s, 'USER', 'INACTIVE')
            """,
            (username, admin_hash, "Inactive User", f"{username}@test.com")
        )
        conn.commit()

    res = client.post("/api/login", json={"username": username, "password": "CS466@123"})
    assert res.status_code in [401, 403]
    data = res.json()
    assert any(err in str(data.get("detail", "")) for err in ["INACTIVE", "LOCKED", "DISABLED", "FORBIDDEN", "INVALID", "AUTH_FAILED"])


def test_auth_07_invalid_json_payloads(client: TestClient):
    """AUTH-07: Malformed payload, missing username, missing password returns 400 or 422."""
    # Missing password
    res1 = client.post("/api/login", json={"username": "admin"})
    assert res1.status_code in [400, 422]

    # Missing username
    res2 = client.post("/api/login", json={"password": "CS466@123"})
    assert res2.status_code in [400, 422]

    # Empty payload
    res3 = client.post("/api/login", json={})
    assert res3.status_code in [400, 422]


def test_auth_08_get_me_contract(client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]):
    """AUTH-08: GET /api/auth/me returns valid user info, strictly no password_hash."""
    res_admin = client.get("/api/auth/me", headers=admin_headers)
    assert res_admin.status_code == 200
    data_admin = res_admin.json()
    assert data_admin["username"] == "admin"
    assert data_admin["vai_tro"] == "ADMIN"
    assert "mat_khau_hash" not in data_admin
    assert "password_hash" not in data_admin
    assert "password" not in data_admin

    res_user = client.get("/api/auth/me", headers=user_headers)
    assert res_user.status_code == 200
    data_user = res_user.json()
    assert data_user["username"] == "user01"
    assert data_user["vai_tro"] == "USER"
    assert "mat_khau_hash" not in data_user
    assert "password_hash" not in data_user


def test_auth_09_get_me_unauthorized(client: TestClient):
    """AUTH-09: Calling /api/auth/me without token or invalid token returns 401."""
    # No token
    res_none = client.get("/api/auth/me")
    assert res_none.status_code == 401

    # Bad token
    res_bad = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.valid.jwt"})
    assert res_bad.status_code == 401


def test_auth_11_and_12_change_password(client: TestClient):
    """AUTH-11, AUTH-12: Valid and invalid password changes."""
    suffix = get_unique_suffix()
    username = f"chpass_{suffix}"
    # Create a user to test password change
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM USERS WHERE username = 'admin'")
        admin_hash = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO USERS (username, password_hash, ho_ten, email, vai_tro, trang_thai)
            VALUES (%s, %s, %s, %s, 'USER', 'ACTIVE')
            """,
            (username, admin_hash, "Pass Changer", f"{username}@test.com")
        )
        conn.commit()

    # Login to get token
    login_res = client.post("/api/login", json={"username": username, "password": "CS466@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # AUTH-12: Invalid change - wrong current password
    res_wrong_old = client.patch(
        "/api/auth/change-password",
        headers=headers,
        json={"current_password": "WrongCurrentPassword@123", "new_password": "NewValidPassword@123"},
    )
    assert res_wrong_old.status_code in [400, 401]

    # AUTH-12: Invalid change - new password too short / weak
    res_too_short = client.patch(
        "/api/auth/change-password",
        headers=headers,
        json={"current_password": "CS466@123", "new_password": "123"},
    )
    assert res_too_short.status_code in [400, 422]

    # AUTH-11: Valid password change
    new_pass = f"ValidNewPass@{suffix}!"
    res_valid = client.patch(
        "/api/auth/change-password",
        headers=headers,
        json={"current_password": "CS466@123", "new_password": new_pass},
    )
    assert res_valid.status_code == 200

    # Verify DB has updated hash and not plaintext
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM USERS WHERE username = %s", (username,))
        row = cur.fetchone()
        assert row is not None
        new_hash = row[0]
        assert new_hash != admin_hash
        assert new_pass not in new_hash
        assert new_hash.startswith("$2b$") or new_hash.startswith("$2a$")

    # Verify login with new password works
    login_new = client.post("/api/login", json={"username": username, "password": new_pass})
    assert login_new.status_code == 200
