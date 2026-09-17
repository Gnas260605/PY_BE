from __future__ import annotations

import csv
from io import StringIO

from app.db.connection import connection_scope
from app.reports import repository
from app.reports.schemas import TechnicianWorkloadResponse
from app.tickets.schemas import TicketListQuery


CATEGORY_LABELS = {
    "INCIDENT": "Sự cố",
    "SERVICE_REQUEST": "Yêu cầu dịch vụ",
    "MAINTENANCE": "Bảo trì",
    "ACCESS_REQUEST": "Cấp quyền",
}

PRIORITY_LABELS = {
    "URGENT": "Khẩn cấp",
    "HIGH": "Cao",
    "MEDIUM": "Trung bình",
    "LOW": "Thấp",
}

STATUS_LABELS = {
    "OPEN": "Chờ tiếp nhận",
    "ASSIGNED": "Đã phân công",
    "IN_PROGRESS": "Đang xử lý",
    "RESOLVED": "Đã giải quyết",
    "CLOSED": "Đã đóng",
}

CSV_HEADERS = [
    "Mã sự cố",
    "Tiêu đề",
    "Phân loại",
    "Mức độ ưu tiên",
    "Trạng thái",
    "Người yêu cầu",
    "KTV phụ trách",
    "Thiết bị liên quan",
    "Thời gian tạo",
    "Cập nhật lần cuối",
]


def get_technician_workload() -> list[TechnicianWorkloadResponse]:
    with connection_scope() as connection:
        rows = repository.get_technician_workload(connection)
    return [TechnicianWorkloadResponse(**row) for row in rows]


def export_tickets_csv(query: TicketListQuery) -> str:
    with connection_scope() as connection:
        rows = repository.list_tickets_for_export(
            connection,
            status=query.status,
            priority=query.priority,
            category=query.category,
            technician_id=query.technician_id,
            user_id=query.user_id,
            keyword=query.keyword,
        )

    output = StringIO()
    output.write("\ufeff")  # UTF-8 BOM for seamless Excel compatibility
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)

    for row in rows:
        ticket_id = f"#TK-{row['id']:04d}" if row.get("id") else "-"
        category = CATEGORY_LABELS.get(row.get("category"), row.get("category") or "-")
        priority = PRIORITY_LABELS.get(row.get("priority"), row.get("priority") or "-")
        status_val = STATUS_LABELS.get(row.get("status"), row.get("status") or "-")
        creator = row.get("creator_name") or (f"User #{row.get('user_id')}" if row.get("user_id") else "-")
        technician = row.get("technician_name") or "Chưa phân công"

        if row.get("device_code") and row.get("device_name"):
            device = f"{row['device_code']} ({row['device_name']})"
        elif row.get("device_name"):
            device = str(row["device_name"])
        else:
            device = "-"

        created = str(row.get("created_at") or "-")
        updated = str(row.get("updated_at") or "-")

        writer.writerow([
            ticket_id,
            row.get("title") or "-",
            category,
            priority,
            status_val,
            creator,
            technician,
            device,
            created,
            updated,
        ])

    return output.getvalue()
