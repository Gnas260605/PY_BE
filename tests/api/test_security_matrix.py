from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.core.rate_limiter import limiter


def test_sec_02_no_token_on_protected_endpoints(client: TestClient):
    """SEC-02: Calling protected endpoints without token must return 401."""
    protected_endpoints = [
        ("GET", "/api/auth/me"),
        ("GET", "/api/users"),
        ("POST", "/api/users"),
        ("GET", "/api/devices"),
        ("POST", "/api/devices"),
        ("GET", "/api/tickets"),
        ("POST", "/api/tickets"),
        ("GET", "/api/dashboard/stats"),
        ("GET", "/api/reports/technician-workload"),
        ("GET", "/api/reports/export-tickets"),
        ("GET", "/api/reports/export-tickets-excel"),
        ("GET", "/api/reports/export-dashboard-pdf"),
    ]
    for method, path in protected_endpoints:
        res = client.request(method, path)
        assert res.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {res.status_code}"


def test_sec_02_and_04_user_role_blocked_from_admin_endpoints(client: TestClient, user_headers: dict[str, str]):
    """SEC-02: USER role strictly forbidden (403) from admin management and reports endpoints."""
    admin_endpoints = [
        ("GET", "/api/users"),
        ("POST", "/api/users"),
        ("PATCH", "/api/users/2"),
        ("POST", "/api/devices"),
        ("PATCH", "/api/devices/1"),
        ("PATCH", "/api/tickets/batch-assign"),
        ("PATCH", "/api/tickets/batch-status"),
        ("GET", "/api/reports/technician-workload"),
        ("GET", "/api/reports/export-tickets"),
        ("GET", "/api/reports/export-tickets-excel"),
        ("GET", "/api/reports/export-dashboard-pdf"),
    ]
    for method, path in admin_endpoints:
        res = client.request(method, path, headers=user_headers, json={})
        assert res.status_code == 403, f"Expected 403 for USER accessing {method} {path}, got {res.status_code}"


def test_sec_06_sqli_resilience(client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]):
    """SEC-06: SQL Injection payloads on search filters, username, and query params do not cause 500 or bypass."""
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE TICKETS; --",
        "1' UNION SELECT NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL --",
        "admin'--",
    ]
    for payload in sqli_payloads:
        # Search users with SQLi
        res_users = client.get(f"/api/users?keyword={payload}", headers=admin_headers)
        assert res_users.status_code in [200, 400], f"SQLi crashed /api/users: {res_users.status_code}"
        assert "mysql" not in res_users.text.lower()
        assert "syntax error" not in res_users.text.lower()

        # Search devices with SQLi
        res_dev = client.get(f"/api/devices?keyword={payload}", headers=admin_headers)
        assert res_dev.status_code in [200, 400]
        assert "mysql" not in res_dev.text.lower()

        # Search tickets with SQLi
        res_tkt = client.get(f"/api/tickets?keyword={payload}", headers=user_headers)
        assert res_tkt.status_code in [200, 400]
        assert "mysql" not in res_tkt.text.lower()


def test_sec_11_zero_password_hash_leak_scan(
    client: TestClient, admin_headers: dict[str, str], tech_headers: dict[str, str], user_headers: dict[str, str]
):
    """SEC-11: Scan all major GET API responses across roles, asserting 100% absence of password_hash."""
    test_targets = [
        ("GET", "/api/auth/me", admin_headers),
        ("GET", "/api/auth/me", user_headers),
        ("GET", "/api/users", admin_headers),
        ("GET", "/api/users/1", admin_headers),
        ("GET", "/api/users/3", admin_headers),
        ("GET", "/api/devices", admin_headers),
        ("GET", "/api/devices", tech_headers),
        ("GET", "/api/tickets", admin_headers),
        ("GET", "/api/tickets", tech_headers),
        ("GET", "/api/tickets", user_headers),
        ("GET", "/api/dashboard/stats", admin_headers),
        ("GET", "/api/reports/technician-workload", admin_headers),
    ]

    forbidden_strings = ["password_hash", "mat_khau_hash", "$2b$", "$2a$"]

    for method, path, headers in test_targets:
        res = client.request(method, path, headers=headers)
        if res.status_code == 200:
            text = res.text
            for forbidden in forbidden_strings:
                assert forbidden not in text, f"Security Leak: Found '{forbidden}' in response of {method} {path}"


def test_sec_12_rate_limiter_brute_force(client: TestClient):
    """SEC-12: Sending more than 10 login requests within window triggers 429 and doesn't crash."""
    limiter.reset()
    client_ip = "192.168.100.55"
    headers = {"x-forwarded-for": client_ip}

    # First 10 requests are handled (401 because bad password)
    for i in range(10):
        res = client.post("/api/login", headers=headers, json={"username": "admin", "password": f"Wrong_{i}"})
        assert res.status_code == 401

    # 11th request must be rejected with 429
    res_limit = client.post("/api/login", headers=headers, json={"username": "admin", "password": "Wrong_11"})
    assert res_limit.status_code == 429
    assert "RATE_LIMIT_EXCEEDED" in res_limit.text

    limiter.reset()
