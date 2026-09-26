from __future__ import annotations

from starlette.testclient import TestClient


def test_log_analytics_summary_admin_only(
    client: TestClient,
    admin_headers: dict[str, str],
    user_headers: dict[str, str],
) -> None:
    forbidden = client.get("/api/log-analytics/summary", headers=user_headers)
    assert forbidden.status_code == 403

    response = client.get("/api/log-analytics/summary", headers=admin_headers)
    assert response.status_code == 200

    payload = response.json()
    assert "total_logs" in payload
    assert "top_events" in payload
    assert "security_events" in payload
    assert "artifacts" in payload
    assert isinstance(payload["artifacts"], list)
