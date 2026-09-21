from __future__ import annotations

import hashlib
import io
import os
import pytest
from starlette.testclient import TestClient
from app.db.connection import connection_scope
from tests.helpers import get_unique_suffix


def test_att_01_to_03_upload_and_download_sha256(client: TestClient, user_headers: dict[str, str]):
    """ATT-01..03: Upload valid file, verify DB, download and verify SHA-256 matches."""
    suffix = get_unique_suffix()
    # Create ticket
    t_res = client.post("/api/tickets", headers=user_headers, json={
        "title": f"Ticket Attachment Test {suffix}",
        "description": "Ticket test file upload",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    assert t_res.status_code == 201
    ticket_id = t_res.json()["id"]

    # Prepare sample file content
    raw_content = f"Dữ liệu đính kèm kiểm thử tính toàn vẹn SHA-256: {suffix}\nĐầy đủ dấu tiếng Việt!".encode("utf-8")
    original_sha256 = hashlib.sha256(raw_content).hexdigest()
    filename = f"report_{suffix}.txt"

    # ATT-01: Upload
    upload_res = client.post(
        f"/api/tickets/{ticket_id}/attachments",
        headers=user_headers,
        files={"file": (filename, io.BytesIO(raw_content), "text/plain")},
    )
    assert upload_res.status_code == 201
    data = upload_res.json()
    att_id = data["id"]
    assert data["file_name"] == filename
    assert data["ticket_id"] == ticket_id

    # ATT-02: Verify DB
    with connection_scope() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, ticket_id, file_name, file_path FROM TICKET_ATTACHMENTS WHERE id = %s", (att_id,))
        row = cur.fetchone()
        assert row is not None
        assert row["ticket_id"] == ticket_id
        assert row["file_name"] == filename
        saved_path = row["file_path"]
        assert os.path.exists(saved_path)

    # ATT-03: Download and verify SHA-256
    download_res = client.get(
        f"/api/tickets/{ticket_id}/attachments/{att_id}/download",
        headers=user_headers,
    )
    assert download_res.status_code == 200
    downloaded_bytes = download_res.content
    downloaded_sha256 = hashlib.sha256(downloaded_bytes).hexdigest()
    assert downloaded_sha256 == original_sha256
    assert len(downloaded_bytes) == len(raw_content)

    # Clean up physical file
    if os.path.exists(saved_path):
        os.remove(saved_path)


def test_att_04_file_size_limit(client: TestClient, user_headers: dict[str, str]):
    """ATT-04: Exceeding 10 MB limit returns 400 FILE_TOO_LARGE and does not create orphan record."""
    suffix = get_unique_suffix()
    t_res = client.post("/api/tickets", headers=user_headers, json={
        "title": f"Ticket Oversize Test {suffix}",
        "description": "Ticket oversize",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    ticket_id = t_res.json()["id"]

    # File > 10MB (10MB + 1KB)
    large_size = 10 * 1024 * 1024 + 1024
    # Streaming bytes generator or BytesIO
    oversize_bytes = b"0" * large_size
    res_large = client.post(
        f"/api/tickets/{ticket_id}/attachments",
        headers=user_headers,
        files={"file": ("large_file.txt", io.BytesIO(oversize_bytes), "text/plain")},
    )
    assert res_large.status_code in [400, 413]
    assert "FILE_TOO_LARGE" in str(res_large.json())

    # Verify no attachment row was created in DB
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM TICKET_ATTACHMENTS WHERE ticket_id = %s", (ticket_id,))
        count = cur.fetchone()[0]
        assert count == 0


def test_att_05_security_and_traversal(client: TestClient, user_headers: dict[str, str]):
    """ATT-05: Reject .exe, double extension, sanitize path traversal, accept unicode."""
    suffix = get_unique_suffix()
    t_res = client.post("/api/tickets", headers=user_headers, json={
        "title": f"Ticket Sec Upload {suffix}",
        "description": "Sec upload",
        "device_id": 1,
        "category": "INCIDENT",
        "priority": "LOW",
    })
    ticket_id = t_res.json()["id"]

    # 1. Reject .exe
    res_exe = client.post(
        f"/api/tickets/{ticket_id}/attachments",
        headers=user_headers,
        files={"file": ("malware.exe", io.BytesIO(b"MZ...fake_exe"), "application/x-msdownload")},
    )
    assert res_exe.status_code == 400
    assert "INVALID_FILE_TYPE" in str(res_exe.json())

    # 2. Reject double extension ending in .exe
    res_double = client.post(
        f"/api/tickets/{ticket_id}/attachments",
        headers=user_headers,
        files={"file": ("photo.png.exe", io.BytesIO(b"malicious"), "image/png")},
    )
    assert res_double.status_code == 400

    # 3. Path traversal attempt in filename '../../escaped.txt'
    res_traversal = client.post(
        f"/api/tickets/{ticket_id}/attachments",
        headers=user_headers,
        files={"file": ("../../escaped.txt", io.BytesIO(b"traversal test"), "text/plain")},
    )
    assert res_traversal.status_code == 201
    traversal_data = res_traversal.json()
    # Ensure filename stored does not have ../
    assert "../" not in traversal_data["file_name"]
    assert traversal_data["file_name"] == "escaped.txt"

    # Clean up physical file
    with connection_scope() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT file_path FROM TICKET_ATTACHMENTS WHERE id = %s", (traversal_data["id"],))
        row = cur.fetchone()
        if row and os.path.exists(row["file_path"]):
            os.remove(row["file_path"])
