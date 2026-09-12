from __future__ import annotations

import jwt
from datetime import UTC, datetime, timedelta
import pytest
from starlette.testclient import TestClient
from app.core.config import get_settings


def test_missing_token(client: TestClient):
    """Calling protected endpoint without Authorization header must return 401."""
    response = client.get("/api/users")
    assert response.status_code == 401
    body = response.json()
    assert body.get("detail") == "MISSING_TOKEN"
    assert "path" in body


def test_malformed_token(client: TestClient):
    """Calling protected endpoint with non-JWT string must return 401."""
    response = client.get(
        "/api/users",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body.get("detail") == "INVALID_TOKEN"


def test_expired_token(client: TestClient):
    """Token with expiration in the past must return 401 TOKEN_EXPIRED."""
    settings = get_settings()
    expired_payload = {
        "sub": "1",
        "username": "admin",
        "role": "ADMIN",
        "exp": datetime.now(UTC) - timedelta(hours=2),
    }
    expired_token = jwt.encode(
        expired_payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body.get("detail") == "TOKEN_EXPIRED"


def test_invalid_signature_token(client: TestClient):
    """Token signed with wrong secret must return 401 INVALID_TOKEN."""
    payload = {
        "sub": "1",
        "username": "admin",
        "role": "ADMIN",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    tampered_token = jwt.encode(payload, "wrong-secret-key-123", algorithm="HS256")

    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body.get("detail") == "INVALID_TOKEN"


def test_missing_sub_claim_token(client: TestClient):
    """Token missing 'sub' claim must return 401 INVALID_TOKEN."""
    settings = get_settings()
    payload = {
        "username": "admin",
        "role": "ADMIN",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    no_sub_token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {no_sub_token}"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body.get("detail") == "INVALID_TOKEN"


def test_wrong_role_forbidden(client: TestClient, user_headers: dict[str, str]):
    """USER role trying to access ADMIN endpoint /api/users must return 403 FORBIDDEN."""
    response = client.get("/api/users", headers=user_headers)
    assert response.status_code == 403
    body = response.json()
    assert body.get("detail") == "FORBIDDEN"


def test_security_leak_prevention(client: TestClient, user_headers: dict[str, str]):
    """Assert responses never leak traceback, raw SQL, passwords, or secrets."""
    settings = get_settings()
    endpoints = [
        ("GET", "/api/users", {}),
        ("POST", "/api/login", {"username": "admin", "password": "WrongPassword"}),
        ("GET", "/api/users", {"Authorization": "Bearer invalid.token.value"}),
    ]

    for method, path, headers in endpoints:
        response = client.request(method, path, headers=headers)
        raw_text = response.text

        # Zero leaks check
        assert "Traceback (most recent call last)" not in raw_text, "Traceback leaked"
        assert "mysql.connector" not in raw_text, "Internal DB module leaked"
        assert settings.jwt_secret_key not in raw_text, "JWT secret key leaked"
        assert "SELECT " not in raw_text, "Raw SQL query leaked"
        assert "INSERT " not in raw_text, "Raw SQL query leaked"
        assert "password_hash" not in raw_text, "password_hash leaked"
