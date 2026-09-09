from __future__ import annotations

import pytest
from starlette.testclient import TestClient


def test_400_invalid_input(client: TestClient, admin_headers: dict[str, str]):
    """Missing required fields returns 400 INVALID_INPUT with errors list."""
    response = client.post("/api/users", headers=admin_headers, json={"username": "missing_fields"})
    assert response.status_code == 400
    body = response.json()
    assert body.get("detail") == "INVALID_INPUT"
    assert "errors" in body


def test_401_invalid_credentials(client: TestClient):
    """Wrong login credentials returns 401 AUTH_FAILED."""
    response = client.post("/api/login", json={"username": "admin", "password": "WrongPassword"})
    assert response.status_code == 401
    body = response.json()
    assert body.get("detail") in {"AUTH_FAILED", "INVALID_CREDENTIALS"}


def test_403_forbidden(client: TestClient, user_headers: dict[str, str]):
    """Authenticated user attempting unauthorized admin action returns 403 FORBIDDEN."""
    response = client.get("/api/users", headers=user_headers)
    assert response.status_code == 403
    body = response.json()
    assert body.get("detail") == "FORBIDDEN"


def test_404_not_found(client: TestClient, admin_headers: dict[str, str]):
    """Requesting non-existent resources returns 404 NOT_FOUND."""
    res_user = client.get("/api/users/99999", headers=admin_headers)
    assert res_user.status_code == 404
    assert res_user.json().get("detail") == "USER_NOT_FOUND"

    res_dev = client.get("/api/devices/99999", headers=admin_headers)
    assert res_dev.status_code == 404
    assert res_dev.json().get("detail") == "DEVICE_NOT_FOUND"


def test_409_conflict(client: TestClient, admin_headers: dict[str, str]):
    """Duplicate entity creation returns 409 CONFLICT."""
    # admin username already exists in seed
    res = client.post(
        "/api/users",
        headers=admin_headers,
        json={
            "username": "admin",
            "password": "CS466@123",
            "ho_ten": "Duplicate Admin",
            "email": "unique_email_test@cs466.local",
            "vai_tro": "ADMIN",
        },
    )
    assert res.status_code == 409


def test_500_sanitized_non_destructive(monkeypatch: pytest.MonkeyPatch):
    """
    Test 500 error handling in a completely safe, non-destructive way.
    Uses monkeypatch to simulate an unexpected server exception, verifying that
    FastAPI's exception handler sanitizes the response completely without touching DB.
    """
    import app.health.routes as health_routes
    from app.main import app

    # Monkeypatch get_health_status in routes to simulate an unhandled application error
    def mock_broken_service():
        raise RuntimeError("Simulated internal server crash with sensitive db_password=secret_db_pass_123")

    monkeypatch.setattr(health_routes, "get_health_status", mock_broken_service)

    # Use TestClient with raise_server_exceptions=False to capture the sanitized HTTP 500 response
    test_client = TestClient(app, raise_server_exceptions=False)
    response = test_client.get("/api/health")
    assert response.status_code == 500

    body = response.json()
    assert body.get("detail") == "INTERNAL_SERVER_ERROR"
    assert "path" in body

    raw_text = response.text
    # Zero leak assertion
    assert "secret_db_pass_123" not in raw_text, "Sensitive mock string leaked in 500 response"
    assert "Traceback" not in raw_text, "Traceback leaked in 500 response"
    assert "RuntimeError" not in raw_text, "Internal exception class leaked in 500 response"
