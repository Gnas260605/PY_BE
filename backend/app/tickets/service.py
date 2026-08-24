from __future__ import annotations

import logging

from app.core.errors import BadRequestError, ForbiddenError, NotFoundError
from app.db.connection import connection_scope
from app.tickets import repository
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


logger = logging.getLogger(__name__)

ALLOWED_UPDATE_FIELDS = {"title", "description", "category", "priority"}
FIELD_TO_COLUMN = {
    "title": "tieu_de",
    "description": "mo_ta",
    "category": "loai_yeu_cau",
    "priority": "muc_do_uu_tien",
}
ALLOWED_TRANSITIONS = {
    "OPEN": {"ASSIGNED"},
    "ASSIGNED": {"IN_PROGRESS"},
    "IN_PROGRESS": {"RESOLVED"},
    "RESOLVED": {"CLOSED"},
    "CLOSED": set(),
}


def _ensure_visible(ticket: dict, current_user: dict) -> None:
    role = current_user["vai_tro"]
    user_id = current_user["id"]
    if role == "ADMIN":
        return
    if role == "USER" and ticket["user_id"] == user_id:
        return
    if role == "TECHNICIAN" and ticket["technician_id"] == user_id:
        return
    raise ForbiddenError("FORBIDDEN")


def _build_history_detail(changed_fields: list[str]) -> str:
    return "Updated fields: " + ", ".join(changed_fields)


def _ensure_technician_scope(ticket: dict, current_user: dict) -> None:
    if current_user["vai_tro"] == "ADMIN":
        return
    if ticket["technician_id"] != int(current_user["id"]):
        raise ForbiddenError("FORBIDDEN")


def _ensure_transition_allowed(current_status: str, target_status: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise BadRequestError("INVALID_TRANSITION")


def create_ticket(payload: CreateTicketRequest, *, current_user: dict) -> TicketSummaryResponse:
    with connection_scope() as connection:
        if payload.device_id is not None and not repository.device_exists(connection, payload.device_id):
            raise NotFoundError("DEVICE_NOT_FOUND")

        try:
            ticket_id = repository.create_ticket(
                connection,
                title=payload.title,
                description=payload.description,
                category=payload.category,
                priority=payload.priority,
                user_id=int(current_user["id"]),
                device_id=payload.device_id,
            )
            repository.insert_ticket_history(
                connection,
                ticket_id=ticket_id,
                actor_user_id=int(current_user["id"]),
                action="CREATED",
                old_status=None,
                new_status="OPEN",
                detail="Ticket created",
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

        created_ticket = repository.get_ticket_by_id(connection, ticket_id)

    logger.info("TICKET_CREATED ticket_id=%s user_id=%s", ticket_id, current_user["id"])

    if created_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**created_ticket)


def list_tickets(query: TicketListQuery, *, current_user: dict) -> list[TicketSummaryResponse]:
    effective_user_id = query.user_id
    effective_technician_id = query.technician_id

    if current_user["vai_tro"] == "USER":
        effective_user_id = int(current_user["id"])
    elif current_user["vai_tro"] == "TECHNICIAN":
        effective_technician_id = int(current_user["id"])

    with connection_scope() as connection:
        tickets = repository.list_tickets(
            connection,
            role=current_user["vai_tro"],
            current_user_id=int(current_user["id"]),
            status=query.status,
            priority=query.priority,
            category=query.category,
            technician_id=effective_technician_id,
            user_id=effective_user_id,
            keyword=query.keyword,
        )

    return [TicketSummaryResponse(**ticket) for ticket in tickets]


def get_ticket_detail(ticket_id: int, *, current_user: dict) -> TicketDetailResponse:
    with connection_scope() as connection:
        ticket = repository.get_ticket_detail(connection, ticket_id)
    if ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")

    _ensure_visible(ticket, current_user)
    return TicketDetailResponse(**ticket)


def update_ticket(
    ticket_id: int,
    payload: UpdateTicketRequest,
    *,
    current_user: dict,
) -> TicketSummaryResponse:
    requested_updates = payload.model_dump(exclude_none=True)
    updates = {
        key: value for key, value in requested_updates.items() if key in ALLOWED_UPDATE_FIELDS
    }
    if not updates:
        raise BadRequestError("NO_ALLOWED_FIELDS")

    with connection_scope() as connection:
        current_ticket = repository.get_ticket_by_id(connection, ticket_id)
        if current_ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")

        role = current_user["vai_tro"]
        if role == "USER":
            if current_ticket["user_id"] != int(current_user["id"]):
                raise ForbiddenError("FORBIDDEN")
            if current_ticket["status"] != "OPEN":
                raise ForbiddenError("FORBIDDEN")
        elif role == "ADMIN":
            pass
        else:
            raise ForbiddenError("FORBIDDEN")

        changed_fields = [
            field for field, value in updates.items() if current_ticket[field] != value
        ]
        if not changed_fields:
            raise BadRequestError("NO_ALLOWED_FIELDS")

        history_action = "UPDATED"
        if any(field in {"category", "priority"} for field in changed_fields):
            history_action = "CLASSIFIED"
        if (
            any(field in {"category", "priority"} for field in changed_fields)
            and any(field in {"title", "description"} for field in changed_fields)
        ):
            history_action = "CLASSIFIED"

        db_updates = {FIELD_TO_COLUMN[field]: updates[field] for field in changed_fields}

        try:
            repository.update_ticket_fields(connection, ticket_id, db_updates)
            repository.insert_ticket_history(
                connection,
                ticket_id=ticket_id,
                actor_user_id=int(current_user["id"]),
                action=history_action,
                old_status=current_ticket["status"],
                new_status=current_ticket["status"],
                detail=_build_history_detail(changed_fields),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

        updated_ticket = repository.get_ticket_by_id(connection, ticket_id)

    event_name = "TICKET_CLASSIFIED" if history_action == "CLASSIFIED" else "TICKET_UPDATED"
    logger.info(
        "%s ticket_id=%s fields=%s",
        event_name,
        ticket_id,
        ",".join(sorted(changed_fields)),
    )

    if updated_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**updated_ticket)


def assign_ticket(
    ticket_id: int,
    payload: AssignTicketRequest,
    *,
    current_user: dict,
) -> TicketSummaryResponse:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        if ticket["status"] == "CLOSED":
            raise BadRequestError("INVALID_TICKET_STATE")

        technician = repository.get_user_basic_by_id(connection, payload.technician_id)
        if technician is None:
            raise NotFoundError("TECHNICIAN_NOT_FOUND")
        if technician["vai_tro"] != "TECHNICIAN":
            raise BadRequestError("INVALID_TECHNICIAN_ROLE")
        if technician["trang_thai"] != "ACTIVE":
            raise BadRequestError("INACTIVE_TECHNICIAN")

        new_status = ticket["status"]
        if ticket["status"] == "OPEN":
            new_status = "ASSIGNED"

        try:
            repository.update_ticket_fields(
                connection,
                ticket_id,
                {
                    "technician_id": payload.technician_id,
                    "trang_thai": new_status,
                },
            )
            repository.insert_ticket_history(
                connection,
                ticket_id=ticket_id,
                actor_user_id=int(current_user["id"]),
                action="ASSIGNED",
                old_status=ticket["status"],
                new_status=new_status,
                detail=f"Assigned technician_id={payload.technician_id}",
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

        updated_ticket = repository.get_ticket_by_id(connection, ticket_id)

    logger.info(
        "TICKET_ASSIGNED ticket_id=%s technician_id=%s admin_id=%s",
        ticket_id,
        payload.technician_id,
        current_user["id"],
    )

    if updated_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**updated_ticket)


def update_ticket_status(
    ticket_id: int,
    payload: UpdateTicketStatusRequest,
    *,
    current_user: dict,
) -> TicketSummaryResponse:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")

        if current_user["vai_tro"] == "TECHNICIAN":
            _ensure_technician_scope(ticket, current_user)

        if ticket["status"] == "OPEN" and payload.status == "ASSIGNED":
            raise BadRequestError("INVALID_TRANSITION")

        _ensure_transition_allowed(ticket["status"], payload.status)

        updates: dict[str, object] = {"trang_thai": payload.status}
        if payload.status == "RESOLVED":
            updates["resolved_at"] = "CURRENT_TIMESTAMP"
        elif payload.status == "CLOSED":
            updates["closed_at"] = "CURRENT_TIMESTAMP"

        try:
            repository.update_ticket_fields(connection, ticket_id, updates)
            repository.insert_ticket_history(
                connection,
                ticket_id=ticket_id,
                actor_user_id=int(current_user["id"]),
                action="STATUS_CHANGED",
                old_status=ticket["status"],
                new_status=payload.status,
                detail=f"Status changed to {payload.status}",
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

        updated_ticket = repository.get_ticket_by_id(connection, ticket_id)

    logger.info(
        "TICKET_STATUS_CHANGED ticket_id=%s old=%s new=%s user_id=%s",
        ticket_id,
        ticket["status"],
        payload.status,
        current_user["id"],
    )

    if updated_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**updated_ticket)


def close_ticket(
    ticket_id: int,
    payload: CloseTicketRequest,
    *,
    current_user: dict,
) -> TicketSummaryResponse:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")

        if current_user["vai_tro"] == "TECHNICIAN":
            _ensure_technician_scope(ticket, current_user)

        if ticket["status"] == "CLOSED":
            raise BadRequestError("INVALID_TRANSITION")
        if ticket["status"] != "RESOLVED":
            raise BadRequestError("INVALID_TRANSITION")

        try:
            repository.update_ticket_fields(
                connection,
                ticket_id,
                {
                    "trang_thai": "CLOSED",
                    "closed_at": "CURRENT_TIMESTAMP",
                },
            )
            repository.insert_ticket_history(
                connection,
                ticket_id=ticket_id,
                actor_user_id=int(current_user["id"]),
                action="CLOSED",
                old_status="RESOLVED",
                new_status="CLOSED",
                detail=payload.note,
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

        updated_ticket = repository.get_ticket_by_id(connection, ticket_id)

    logger.info("TICKET_CLOSED ticket_id=%s user_id=%s", ticket_id, current_user["id"])

    if updated_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**updated_ticket)


def get_ticket_history(ticket_id: int, *, current_user: dict) -> list[TicketHistoryResponse]:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        _ensure_visible(ticket, current_user)
        history_rows = repository.get_ticket_history(connection, ticket_id)

    return [TicketHistoryResponse(**row) for row in history_rows]
