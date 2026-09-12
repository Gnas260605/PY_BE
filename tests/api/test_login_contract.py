from __future__ import annotations

import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "username,password,expected_role",
    [
        ("admin", "CS466@123", "ADMIN"),
        ("tech01", "CS466@123", "TECHNICIAN"),
        ("user01", "CS466@123", "USER"),
    ],
)
def test_login_contract_happy_path(
    client: TestClient, username: str, password: str, expected_role: str
):
    response = client.post(
        "/api/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, f"Login failed for {username}: {response.text}"

    data = response.json()

    # 1. Root contract keys verification
    assert "access_token" in data, "Response missing 'access_token'"
    assert "token_type" in data, "Response missing 'token_type'"
    assert data["token_type"] == "bearer", f"Expected token_type 'bearer', got {data['token_type']}"
    assert "user" in data, "Response missing 'user' object"

    # 2. Strict forbidden fields check - MUST NOT exist
    assert "token" not in data, "Forbidden field 'token' leaked at root"
    assert "password" not in data, "Forbidden field 'password' leaked at root"
    assert "password_hash" not in data, "Forbidden field 'password_hash' leaked at root"

    # 3. User object contract verification
    user = data["user"]
    expected_user_keys = {"id", "username", "ho_ten", "email", "vai_tro", "trang_thai"}
    for key in expected_user_keys:
        assert key in user, f"User object missing required field '{key}'"

    assert "password" not in user, "Forbidden field 'password' leaked in user object"
    assert "password_hash" not in user, "Forbidden field 'password_hash' leaked in user object"

    assert user["username"] == username
    assert user["vai_tro"] == expected_role
    assert user["trang_thai"] == "ACTIVE"
