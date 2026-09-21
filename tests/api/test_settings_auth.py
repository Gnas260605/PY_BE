from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.db.connection import connection_scope
from tests.helpers import get_unique_suffix


def test_set_02_to_04_profile_update_and_validation(client: TestClient, user_headers: dict[str, str]):
    """SET-02..04: Update profile (ho_ten, email), invalid email validation, verify DB."""
    # 1. Invalid email format -> 400 or 422
    res_bad_email = client.patch(
        "/api/users/3",
        headers=user_headers,
        json={"email": "not-an-email"},
    )
    assert res_bad_email.status_code in [400, 422]

    # 2. Blank ho_ten -> 400 or 422
    res_blank_name = client.patch(
        "/api/users/3",
        headers=user_headers,
        json={"ho_ten": "   "},
    )
    assert res_blank_name.status_code in [400, 422]

    # 3. Valid update
    suffix = get_unique_suffix()
    new_name = f"Nguyễn Văn User {suffix}"
    new_email = f"user_{suffix}@example.com"
    res_update = client.patch(
        "/api/users/3",
        headers=user_headers,
        json={"ho_ten": new_name, "email": new_email},
    )
    assert res_update.status_code == 200
    data = res_update.json()
    assert data["ho_ten"] == new_name
    assert data["email"] == new_email

    # 4. Verify DB
    with connection_scope() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT ho_ten, email FROM USERS WHERE id = 3")
        row = cur.fetchone()
        assert row["ho_ten"] == new_name
        assert row["email"] == new_email

    # 5. Verify reflected in /api/auth/me
    res_me = client.get("/api/auth/me", headers=user_headers)
    assert res_me.status_code == 200
    assert res_me.json()["ho_ten"] == new_name
    assert res_me.json()["email"] == new_email


def test_set_08_and_09_notification_preference(client: TestClient, user_headers: dict[str, str]):
    """SET-08, SET-09: Toggle receive_email_on_resolve setting and verify persistence in DB."""
    # Toggle to True
    res_true = client.patch(
        "/api/users/3",
        headers=user_headers,
        json={"receive_email_on_resolve": True},
    )
    assert res_true.status_code == 200
    assert res_true.json()["receive_email_on_resolve"] is True

    # Verify DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT receive_email_on_resolve FROM USERS WHERE id = 3")
        assert cur.fetchone()[0] == 1

    # Toggle to False
    res_false = client.patch(
        "/api/users/3",
        headers=user_headers,
        json={"receive_email_on_resolve": False},
    )
    assert res_false.status_code == 200
    assert res_false.json()["receive_email_on_resolve"] is False

    # Verify DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT receive_email_on_resolve FROM USERS WHERE id = 3")
        assert cur.fetchone()[0] == 0
