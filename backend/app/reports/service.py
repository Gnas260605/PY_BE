from __future__ import annotations

import csv
from io import StringIO

from app.db.connection import connection_scope
from app.reports import repository
from app.reports.schemas import TechnicianWorkloadResponse
from app.tickets.schemas import TicketListQuery


CSV_FIELDS = [
    "id",
    "title",
    "description",
    "category",
    "priority",
    "status",
    "user_id",
    "creator_name",
    "device_id",
    "device_code",
    "device_name",
    "technician_id",
    "technician_name",
    "created_at",
    "updated_at",
    "resolved_at",
    "closed_at",
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
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return output.getvalue()
