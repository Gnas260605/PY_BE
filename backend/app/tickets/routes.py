from __future__ import annotations

from pydantic import ValidationError

from fastapi import APIRouter, Depends, Query, status

from app.core.auth import get_current_user, require_roles
from app.core.errors import BadRequestError
from app.tickets.schemas import (
    AssignTicketRequest,
    CloseTicketRequest,
    CreateTicketRequest,
    TicketDetailResponse,
    TicketHistoryResponse,
    TicketListQuery,
    TicketSummaryResponse,
    UpdateTicketRequest,
    UpdateTicketStatusRequest,
)
from app.tickets.service import (
    assign_ticket,
    close_ticket,
    create_ticket,
    get_ticket_detail,
    get_ticket_history,
    list_tickets,
    update_ticket,
    update_ticket_status,
)


router = APIRouter()


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
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return create_ticket(payload, current_user=current_user)


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
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return update_ticket(ticket_id, payload, current_user=current_user)


@router.patch(
    "/tickets/{ticket_id}/assign",
    response_model=TicketSummaryResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def assign_ticket_route(
    ticket_id: int,
    payload: AssignTicketRequest,
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return assign_ticket(ticket_id, payload, current_user=current_user)


@router.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketSummaryResponse,
    dependencies=[Depends(require_roles("TECHNICIAN", "ADMIN"))],
)
def update_ticket_status_route(
    ticket_id: int,
    payload: UpdateTicketStatusRequest,
    current_user: dict = Depends(get_current_user),
) -> TicketSummaryResponse:
    return update_ticket_status(ticket_id, payload, current_user=current_user)


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
