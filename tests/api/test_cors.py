from __future__ import annotations

import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "allowed_origin",
    [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
)
def test_cors_preflight_allowed_origins(client: TestClient, allowed_origin: str):
    """OPTIONS preflight with allowed origins must return 200 and valid CORS headers."""
    headers = {
        "Origin": allowed_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
    }
    response = client.options("/api/login", headers=headers)
    assert response.status_code == 200

    assert response.headers.get("access-control-allow-origin") == allowed_origin
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allowed_methods
    assert "GET" in allowed_methods
    assert "PATCH" in allowed_methods


def test_cors_disallowed_origin(client: TestClient):
    """Requests with disallowed origin must not receive Access-Control-Allow-Origin header."""
    headers = {
        "Origin": "http://malicious-attacker.com",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/api/login", headers=headers)
    # When origin is disallowed, CORS middleware either does not return allow-origin header or rejects
    assert response.headers.get("access-control-allow-origin") != "http://malicious-attacker.com"
