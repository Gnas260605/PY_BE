from __future__ import annotations

import io
import openpyxl
import pytest
from starlette.testclient import TestClient
from app.db.connection import connection_scope


def test_rpt_01_and_02_dashboard_stats(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    """RPT-01, RPT-02: Dashboard stats exact COUNT(*) match against MySQL."""
    res_admin = client.get("/api/dashboard/stats", headers=admin_headers)
    assert res_admin.status_code == 200
    data = res_admin.json()

    # Direct MySQL count verification
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM TICKETS")
        db_tickets = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM DEVICES")
        db_devices = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM USERS WHERE trang_thai = 'ACTIVE'")
        db_users = cur.fetchone()[0]

    assert data["total_tickets"] == db_tickets
    assert data["total_devices"] == db_devices
    assert data["total_users"] == db_users
    assert "status_counts" in data


def test_rpt_03_technician_workload(client: TestClient, admin_headers: dict[str, str]):
    """RPT-03: Technician workload query returns accurate counts per tech."""
    res = client.get("/api/reports/technician-workload", headers=admin_headers)
    assert res.status_code == 200
    workload = res.json()
    assert isinstance(workload, list)
    for item in workload:
        assert "technician_id" in item
        assert "username" in item
        assert "ho_ten" in item
        assert "active_tickets" in item
        assert "resolved_tickets" in item
        assert "closed_tickets" in item
        assert "total_assigned_tickets" in item


def test_rpt_04_export_csv(client: TestClient, admin_headers: dict[str, str]):
    """RPT-04: Export tickets as CSV UTF-8, verify headers and line count."""
    res = client.get("/api/reports/export-tickets", headers=admin_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment" in res.headers["content-disposition"]

    csv_text = res.text
    lines = [line for line in csv_text.strip().split("\n") if line.strip()]
    assert len(lines) >= 1  # At least header
    # Check header has key Vietnamese columns with UTF-8 BOM
    header = lines[0]
    assert any(col in header for col in ["Mã sự cố", "Tiêu đề", "Trạng thái", "Phân loại"])


def test_rpt_05_export_excel(
    client: TestClient, admin_headers: dict[str, str], tech_headers: dict[str, str]
):
    """RPT-05: Export tickets as Excel XLSX, verify openxml zip header and openpyxl parse."""
    # Test for Admin
    res_admin = client.get("/api/reports/export-tickets-excel", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res_admin.headers["content-type"]
    wb = openpyxl.load_workbook(io.BytesIO(res_admin.content))
    assert len(wb.sheetnames) >= 1

    # Test for Technician (allowed)
    res_tech = client.get("/api/reports/export-tickets-excel", headers=tech_headers)
    assert res_tech.status_code == 200


def test_rpt_06_export_dashboard_pdf(client: TestClient, admin_headers: dict[str, str]):
    """RPT-06: Export dashboard as PDF, verify PDF magic header %PDF."""
    res = client.get("/api/reports/export-dashboard-pdf", headers=admin_headers)
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 500


def test_rpt_08_rbac_on_reports(client: TestClient, user_headers: dict[str, str], tech_headers: dict[str, str]):
    """RPT-08: USER and TECH forbidden from admin reports (403)."""
    # USER forbidden from workload
    assert client.get("/api/reports/technician-workload", headers=user_headers).status_code == 403

    # USER forbidden from CSV export
    assert client.get("/api/reports/export-tickets", headers=user_headers).status_code == 403

    # USER forbidden from Excel export
    assert client.get("/api/reports/export-tickets-excel", headers=user_headers).status_code == 403

    # USER forbidden from PDF export
    assert client.get("/api/reports/export-dashboard-pdf", headers=user_headers).status_code == 403

    # TECH forbidden from PDF export
    assert client.get("/api/reports/export-dashboard-pdf", headers=tech_headers).status_code == 403

    # TECH forbidden from workload
    assert client.get("/api/reports/technician-workload", headers=tech_headers).status_code == 403
