from __future__ import annotations

from pydantic import ValidationError

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.core.auth import require_roles, get_current_user
from app.core.errors import BadRequestError
from app.reports.schemas import TechnicianWorkloadResponse
from app.reports.service import export_tickets_csv, get_technician_workload, export_tickets_excel, export_dashboard_pdf
from app.tickets.service import get_dashboard_stats
from app.tickets.schemas import TicketListQuery


router = APIRouter()


@router.get(
    "/reports/technician-workload",
    response_model=list[TechnicianWorkloadResponse],
    dependencies=[Depends(require_roles("ADMIN"))],
)
def technician_workload_route() -> list[TechnicianWorkloadResponse]:
    return get_technician_workload()


@router.get(
    "/reports/export-tickets",
    dependencies=[Depends(require_roles("ADMIN"))],
)
def export_tickets_route(
    status_value: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    category: str | None = Query(default=None),
    technician_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
) -> StreamingResponse:
    try:
        query = TicketListQuery(
            status=status_value,
            priority=priority,
            category=category,
            technician_id=technician_id,
            user_id=user_id,
            keyword=keyword,
        )
    except ValidationError as exc:
        raise BadRequestError("INVALID_INPUT") from exc

    csv_content = export_tickets_csv(query)
    headers = {"Content-Disposition": 'attachment; filename="tickets.csv"'}
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers=headers,
    )


@router.get(
    "/reports/export-tickets-excel",
    dependencies=[Depends(require_roles("ADMIN", "TECHNICIAN"))],
)
def export_tickets_excel_route(
    status_value: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    category: str | None = Query(default=None),
    technician_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
) -> StreamingResponse:
    try:
        query = TicketListQuery(
            status=status_value,
            priority=priority,
            category=category,
            technician_id=technician_id,
            user_id=user_id,
            keyword=keyword,
        )
    except ValidationError as exc:
        raise BadRequestError("INVALID_INPUT") from exc

    excel_buffer = export_tickets_excel(query)
    headers = {"Content-Disposition": 'attachment; filename="tickets.xlsx"'}
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get(
    "/reports/export-dashboard-pdf",
    dependencies=[Depends(require_roles("ADMIN"))],
)
def export_dashboard_pdf_route(current_user: dict = Depends(get_current_user)) -> StreamingResponse:
    stats = get_dashboard_stats(current_user=current_user)
    pdf_buffer = export_dashboard_pdf(stats)
    headers = {"Content-Disposition": 'attachment; filename="dashboard_stats.pdf"'}
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers=headers,
    )

