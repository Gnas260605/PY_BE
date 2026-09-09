from __future__ import annotations

import os
import sys
import time
import uuid
from typing import Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from app.db.connection import connection_scope, check_connection  # type: ignore
except ImportError:
    from backend.app.db.connection import connection_scope, check_connection  # type: ignore


def is_database_connected() -> bool:
    """Check if MySQL test database is reachable."""
    res: dict[str, Any] = check_connection()
    return bool(res.get("ok", False))


def get_unique_suffix() -> str:
    """Generate timestamp + hex suffix for data isolation."""
    ts = int(time.time())
    rand_hex = uuid.uuid4().hex[:6]
    return f"{ts}_{rand_hex}"


def generate_user_data(role: str = "USER") -> dict[str, str]:
    suffix = get_unique_suffix()
    return {
        "username": f"qa_user_{suffix}",
        "password": "CS466@123",
        "ho_ten": f"QA User {suffix}",
        "email": f"qa_{suffix}@cs466.local",
        "vai_tro": role,
    }


def generate_device_data() -> dict[str, Any]:
    suffix = get_unique_suffix()
    return {
        "ma_thiet_bi": f"QA-DEV-{suffix[:12].upper()}",
        "ten_thiet_bi": f"Thiết bị kiểm thử QA {suffix}",
        "loai_thiet_bi": "COMPUTER",
        "vi_tri": "Phòng QA Lab",
        "trang_thai": "ACTIVE",
        "mo_ta": f"Device created during QA test run {suffix}",
    }


def generate_ticket_data(device_id: int | None = 1) -> dict[str, Any]:
    suffix = get_unique_suffix()
    return {
        "title": f"[QA-{suffix}] Sự cố kiểm thử",
        "description": f"Mô tả chi tiết sự cố kiểm thử cho test run {suffix}",
        "device_id": device_id,
        "category": "INCIDENT",
        "priority": "HIGH",
    }


def query_ticket_by_id(ticket_id: int) -> dict[str, Any] | None:
    """Query ticket record directly from MySQL database."""
    if not is_database_connected():
        return None
    with connection_scope() as conn:
        cursor: Any = conn.cursor(dictionary=True)  # type: ignore
        cursor.execute(
            "SELECT id, tieu_de, mo_ta, loai_yeu_cau, muc_do_uu_tien, trang_thai, "
            "user_id, device_id, technician_id, created_at, updated_at, resolved_at, closed_at "
            "FROM TICKETS WHERE id = %s",
            (ticket_id,),
        )
        row: Any = cursor.fetchone()
        return dict(row) if row else None


def query_ticket_history(ticket_id: int) -> list[dict[str, Any]]:
    """Query history records directly for a specific ticket."""
    if not is_database_connected():
        return []
    with connection_scope() as conn:
        cursor: Any = conn.cursor(dictionary=True)  # type: ignore
        cursor.execute(
            "SELECT id, ticket_id, nguoi_thuc_hien_id, hanh_dong, trang_thai_cu, trang_thai_moi, chi_tiet_cap_nhat, thoi_gian "
            "FROM TICKET_HISTORY WHERE ticket_id = %s ORDER BY thoi_gian ASC, id ASC",
            (ticket_id,),
        )
        rows: Any = cursor.fetchall()
        return [dict(r) for r in rows] if rows else []


class BugReportCollector:
    """Collects failure evidence and formats it into the 15-field Bug Report standard."""

    def __init__(self, backend_commit: str = "e2b610838226b2c414caf6d3c01c78af5405c08f") -> None:
        self.backend_commit = backend_commit
        self.reports: list[dict[str, Any]] = []

    def add_bug(
        self,
        bug_id: str,
        module: str,
        endpoint: str,
        role: str,
        severity: str,
        precondition: str,
        steps: str,
        expected: str,
        actual: str,
        http_status: str,
        request_info: str,
        response_info: str,
        db_state: str = "N/A",
        reproducible: str = "YES",
    ) -> None:
        self.reports.append({
            "BUG_ID": bug_id,
            "MODULE": module,
            "ENDPOINT": endpoint,
            "ROLE": role,
            "SEVERITY": severity,
            "PRECONDITION": precondition,
            "STEPS": steps,
            "EXPECTED": expected,
            "ACTUAL": actual,
            "HTTP_STATUS": http_status,
            "REQUEST": request_info,
            "RESPONSE": response_info,
            "DB_STATE": db_state,
            "BACKEND_COMMIT": self.backend_commit,
            "REPRODUCIBLE": reproducible,
        })

    def format_report(self, report: dict[str, Any]) -> str:
        lines = [
            "=" * 80,
            "BUG REPORT",
            "=" * 80,
            f"BUG_ID:         {report['BUG_ID']}",
            f"MODULE:         {report['MODULE']}",
            f"ENDPOINT:       {report['ENDPOINT']}",
            f"ROLE:           {report['ROLE']}",
            f"SEVERITY:       {report['SEVERITY']}",
            f"PRECONDITION:   {report['PRECONDITION']}",
            f"STEPS:          {report['STEPS']}",
            f"EXPECTED:       {report['EXPECTED']}",
            f"ACTUAL:         {report['ACTUAL']}",
            f"HTTP_STATUS:    {report['HTTP_STATUS']}",
            f"REQUEST:        {report['REQUEST']}",
            f"RESPONSE:       {report['RESPONSE']}",
            f"DB_STATE:       {report['DB_STATE']}",
            f"BACKEND_COMMIT: {report['BACKEND_COMMIT']}",
            f"REPRODUCIBLE:   {report['REPRODUCIBLE']}",
            "=" * 80,
        ]
        return "\n".join(lines)

    def print_all(self) -> None:
        if not self.reports:
            print("\n[BUG REPORT] 0 bugs detected. All assertions passed.")
            return
        print(f"\n[BUG REPORT] Total bugs found: {len(self.reports)}")
        for r in self.reports:
            print(self.format_report(r))
