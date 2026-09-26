from __future__ import annotations

# pyrefly: ignore [missing-import]
from pydantic import ValidationError

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query, status, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse

from app.core.auth import get_current_user, require_roles
from app.core.errors import BadRequestError
from app.tickets.schemas import (
    AssignTicketRequest,
    BatchAssignTicketsRequest,
    BatchUpdateTicketStatusRequest,
    CloseTicketRequest,
    CreateTicketCommentRequest,
    CreateTicketRequest,
    DashboardStatsResponse,
    TicketCommentResponse,
    TicketDetailResponse,
    TicketHistoryResponse,
    TicketListQuery,
    TicketSummaryResponse,
    TicketAttachmentResponse,
    UpdateTicketRequest,
    UpdateTicketStatusRequest,
)
from app.tickets.service import (
    assign_ticket,
    batch_assign_tickets,
    batch_update_ticket_status,
    close_ticket,
    create_ticket,
    create_ticket_comment,
    get_dashboard_stats,
    get_ticket_detail,
    get_ticket_history,
    list_ticket_comments,
    list_tickets,
    update_ticket,
    update_ticket_status,
    list_ticket_attachments,
    upload_ticket_attachment,
    get_ticket_attachment_file,
)



router = APIRouter()


@router.get(
    "/dashboard/stats",
    response_model=DashboardStatsResponse,
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def get_dashboard_stats_route(
    current_user: dict = Depends(get_current_user),
) -> DashboardStatsResponse:
    return get_dashboard_stats(current_user=current_user)


@router.get(
    "/tickets",
    response_model=list[TicketSummaryResponse],
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def list_tickets_route(
    status_value: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    category: str | None = Query(default=None),
    technician_id: int | None = Query(default=None),
    user_id: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> list[TicketSummaryResponse]:
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
    return list_tickets(query, current_user=current_user)


@router.post(
    "/tickets",
    response_model=TicketSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("USER", "ADMIN"))],
)
def create_ticket_route(
    payload: CreateTicketRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return create_ticket(payload, background_tasks, current_user=current_user)


@router.patch(
    "/tickets/batch-assign",
    response_model=list[TicketSummaryResponse],
    dependencies=[Depends(require_roles("ADMIN"))],
)
def batch_assign_tickets_route(
    payload: BatchAssignTicketsRequest,
    current_user: dict = Depends(get_current_user),
) -> list[TicketSummaryResponse]:
    return batch_assign_tickets(payload, current_user=current_user)


@router.patch(
    "/tickets/batch-status",
    response_model=list[TicketSummaryResponse],
    dependencies=[Depends(require_roles("ADMIN"))],
)
def batch_update_ticket_status_route(
    payload: BatchUpdateTicketStatusRequest,
    current_user: dict = Depends(get_current_user),
) -> list[TicketSummaryResponse]:
    return batch_update_ticket_status(payload, current_user=current_user)


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketDetailResponse,
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def get_ticket_route(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
) -> TicketDetailResponse:
    return get_ticket_detail(ticket_id, current_user=current_user)


@router.patch(
    "/tickets/{ticket_id}",
    response_model=TicketSummaryResponse,
    dependencies=[Depends(require_roles("USER", "ADMIN"))],
)
def update_ticket_route(
    ticket_id: int,
    payload: UpdateTicketRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return update_ticket(ticket_id, payload, background_tasks, current_user=current_user)


@router.patch(
    "/tickets/{ticket_id}/assign",
    response_model=TicketSummaryResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def assign_ticket_route(
    ticket_id: int,
    payload: AssignTicketRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return assign_ticket(ticket_id, payload, background_tasks, current_user=current_user)


@router.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketSummaryResponse,
    dependencies=[Depends(require_roles("TECHNICIAN", "ADMIN"))],
)
def update_ticket_status_route(
    ticket_id: int,
    payload: UpdateTicketStatusRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return update_ticket_status(ticket_id, payload, background_tasks, current_user=current_user)


@router.patch(
    "/tickets/{ticket_id}/close",
    response_model=TicketSummaryResponse,
    dependencies=[Depends(require_roles("TECHNICIAN", "ADMIN"))],
)
def close_ticket_route(
    ticket_id: int,
    payload: CloseTicketRequest,
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return close_ticket(ticket_id, payload, current_user=current_user)


@router.get(
    "/tickets/{ticket_id}/history",
    response_model=list[TicketHistoryResponse],
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def get_ticket_history_route(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
) -> list[TicketHistoryResponse]:
    return get_ticket_history(ticket_id, current_user=current_user)


@router.get(
    "/tickets/{ticket_id}/comments",
    response_model=list[TicketCommentResponse],
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def list_ticket_comments_route(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
) -> list[TicketCommentResponse]:
    return list_ticket_comments(ticket_id, current_user=current_user)


@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=TicketCommentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def create_ticket_comment_route(
    ticket_id: int,
    payload: CreateTicketCommentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> TicketCommentResponse:
    return create_ticket_comment(ticket_id, payload, background_tasks, current_user=current_user)

@router.get(
    "/tickets/{ticket_id}/attachments",
    response_model=list[TicketAttachmentResponse],
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def list_ticket_attachments_route(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
) -> list[TicketAttachmentResponse]:
    return list_ticket_attachments(ticket_id, current_user=current_user)

@router.post(
    "/tickets/{ticket_id}/attachments",
    response_model=TicketAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def upload_ticket_attachment_route(
    ticket_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> TicketAttachmentResponse:
    return upload_ticket_attachment(ticket_id, file, current_user=current_user)


@router.get(
    "/tickets/{ticket_id}/attachments/{attachment_id}/download",
    dependencies=[Depends(require_roles("USER", "TECHNICIAN", "ADMIN"))],
)
def download_ticket_attachment_route(
    ticket_id: int,
    attachment_id: int,
    current_user: dict = Depends(get_current_user),
) -> FileResponse:
    file_path, file_name, file_type = get_ticket_attachment_file(
        ticket_id, attachment_id, current_user=current_user
    )
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type=file_type or "application/octet-stream",
    )

