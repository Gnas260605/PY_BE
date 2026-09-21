from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.db.connection import connection_scope
from tests.helpers import get_unique_suffix


def test_col_01_and_03_create_and_list_comments(
    client: TestClient, user_headers: dict[str, str], admin_headers: dict[str, str]
):
    """COL-01, COL-03: Create comment with Vietnamese Unicode accents, verify DB, verify list feed."""
    suffix = get_unique_suffix()
    # Create ticket by user
    t_res = client.post("/api/tickets", headers=user_headers, json={
        "title": f"Ticket bình luận {suffix}",
        "description": "Mô tả ticket",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    assert t_res.status_code == 201
    ticket_id = t_res.json()["id"]

    # User adds comment with Vietnamese accents
    vn_comment = f"Kỹ thuật viên vui lòng kiểm tra giúp mình nhé, xin cảm ơn! {suffix}"
    res = client.post(f"/api/tickets/{ticket_id}/comments", headers=user_headers, json={
        "content": vn_comment,
    })
    assert res.status_code == 201
    comment_data = res.json()
    assert comment_data["content"] == vn_comment
    assert comment_data["user_id"] == 3
    assert comment_data["ticket_id"] == ticket_id

    # Verify DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, noi_dung FROM TICKET_COMMENTS WHERE ticket_id = %s", (ticket_id,))
        rows = cur.fetchall()
        assert len(rows) >= 1
        assert any(r[1] == vn_comment for r in rows)

    # COL-03: List comments feed
    list_res = client.get(f"/api/tickets/{ticket_id}/comments", headers=user_headers)
    assert list_res.status_code == 200
    feed = list_res.json()
    assert len(feed) >= 1
    assert any(c["content"] == vn_comment for c in feed)


def test_col_05_blank_and_xss_comments(client: TestClient, user_headers: dict[str, str]):
    """COL-05: Blank, whitespace-only comments rejected (400/422); XSS string stored safely as plain text."""
    suffix = get_unique_suffix()
    t_res = client.post("/api/tickets", headers=user_headers, json={
        "title": f"Ticket XSS test {suffix}",
        "description": "Mô tả",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    ticket_id = t_res.json()["id"]

    # Empty content -> 400 or 422
    res_empty = client.post(f"/api/tickets/{ticket_id}/comments", headers=user_headers, json={"content": ""})
    assert res_empty.status_code in [400, 422]

    # Whitespace content -> 400 or 422
    res_ws = client.post(f"/api/tickets/{ticket_id}/comments", headers=user_headers, json={"content": "    \n\t   "})
    assert res_ws.status_code in [400, 422]

    # XSS payload
    xss_payload = "<script>alert('XSS_TEST')</script><img src=x onerror=alert(1)>"
    res_xss = client.post(f"/api/tickets/{ticket_id}/comments", headers=user_headers, json={"content": xss_payload})
    assert res_xss.status_code == 201
    assert res_xss.json()["content"] == xss_payload

    # Fetch feed
    feed_res = client.get(f"/api/tickets/{ticket_id}/comments", headers=user_headers)
    assert feed_res.status_code == 200
    # Returned as raw JSON string safely
    assert any(c["content"] == xss_payload for c in feed_res.json())


def test_col_06_idor_protection_on_comments(client: TestClient, user_headers: dict[str, str]):
    """COL-06: Non-owner USER cannot view or post comments on another user's ticket (403)."""
    # Ticket 3 belongs to user03 (user_id=6). Current user01 is user_id=3.
    # Try to list comments
    res_list = client.get("/api/tickets/3/comments", headers=user_headers)
    assert res_list.status_code == 403

    # Try to create comment
    res_post = client.post("/api/tickets/3/comments", headers=user_headers, json={"content": "Thử bình luận IDOR"})
    assert res_post.status_code == 403
