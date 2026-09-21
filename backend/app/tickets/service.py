from __future__ import annotations

import logging

import os
import shutil
import uuid

from fastapi import UploadFile, BackgroundTasks

from app.core.config import get_settings
from app.core.errors import BadRequestError, ForbiddenError, NotFoundError
from app.core.websocket import manager
from app.db.connection import connection_scope
from app.core.notifications import send_telegram_message, send_email_notification
from app.users.repository import get_user_by_id
from app.tickets import repository
from app.tickets.schemas import (
    AssignTicketRequest,
    BatchAssignTicketsRequest,
    BatchUpdateTicketStatusRequest,
    CloseTicketRequest,
    CreateTicketCommentRequest,
    CreateTicketRequest,
    DashboardStatsResponse,
    TicketAttachmentResponse,
    TicketCommentResponse,
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
    "OPEN": set(),
    "ASSIGNED": {"IN_PROGRESS"},
    "IN_PROGRESS": {"RESOLVED"},
    "RESOLVED": set(),
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


def create_ticket(payload: CreateTicketRequest, background_tasks: BackgroundTasks, *, current_user: dict) -> TicketSummaryResponse:
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
    
    background_tasks.add_task(
        manager.broadcast,
        {"type": "TICKET_CREATED", "ticket_id": ticket_id, "user_id": int(current_user["id"]), "message": f"Ticket #{ticket_id} được tạo mới"}
    )

    if payload.priority == "URGENT":
        msg = f"🚨 <b>URGENT TICKET</b> 🚨\n\nTicket #{ticket_id}: {payload.title}\nCategory: {payload.category}\n\nPlease check the dashboard immediately."
        background_tasks.add_task(send_telegram_message, msg)

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
    background_tasks: BackgroundTasks,
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
    
    background_tasks.add_task(
        manager.send_personal_message,
        {"type": event_name, "ticket_id": ticket_id, "message": f"Ticket #{ticket_id} được cập nhật"},
        int(current_ticket["user_id"])
    )
    if current_ticket.get("technician_id"):
        background_tasks.add_task(
            manager.send_personal_message,
            {"type": event_name, "ticket_id": ticket_id, "message": f"Ticket #{ticket_id} được cập nhật"},
            int(current_ticket["technician_id"])
        )

    if updated_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**updated_ticket)


def assign_ticket(
    ticket_id: int,
    payload: AssignTicketRequest,
    background_tasks: BackgroundTasks,
    *,
    current_user: dict,
) -> TicketSummaryResponse:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        if ticket["status"] == "CLOSED":
            raise BadRequestError("INVALID_TICKET_STATE")

        if current_user["vai_tro"] == "TECHNICIAN" and payload.technician_id != int(current_user["id"]):
            raise ForbiddenError("FORBIDDEN")

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
    
    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "TICKET_ASSIGNED", "ticket_id": ticket_id, "message": f"Bạn được phân công Ticket #{ticket_id}"},
        payload.technician_id
    )
    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "TICKET_ASSIGNED", "ticket_id": ticket_id, "message": f"Ticket #{ticket_id} đã được phân công"},
        int(ticket["user_id"])
    )

    if updated_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**updated_ticket)


def batch_assign_tickets(
    payload: BatchAssignTicketsRequest,
    *,
    current_user: dict,
) -> list[TicketSummaryResponse]:
    with connection_scope() as connection:
        technician = repository.get_user_basic_by_id(connection, payload.technician_id)
        if technician is None:
            raise NotFoundError("TECHNICIAN_NOT_FOUND")
        if technician["vai_tro"] != "TECHNICIAN":
            raise BadRequestError("INVALID_TECHNICIAN_ROLE")
        if technician["trang_thai"] != "ACTIVE":
            raise BadRequestError("INACTIVE_TECHNICIAN")

        updated_tickets: list[dict] = []
        try:
            for ticket_id in payload.ticket_ids:
                ticket = repository.get_ticket_by_id(connection, ticket_id)
                if ticket is None:
                    raise NotFoundError("TICKET_NOT_FOUND")
                if ticket["status"] == "CLOSED":
                    raise BadRequestError("INVALID_TICKET_STATE")

                new_status = "ASSIGNED" if ticket["status"] == "OPEN" else ticket["status"]
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
                    detail=f"Batch assigned technician_id={payload.technician_id}",
                )

            connection.commit()
        except Exception:
            connection.rollback()
            raise

        for ticket_id in payload.ticket_ids:
            updated_ticket = repository.get_ticket_by_id(connection, ticket_id)
            if updated_ticket is None:
                raise NotFoundError("TICKET_NOT_FOUND")
            updated_tickets.append(updated_ticket)

    logger.info(
        "TICKET_BATCH_ASSIGNED count=%s technician_id=%s admin_id=%s",
        len(payload.ticket_ids),
        payload.technician_id,
        current_user["id"],
    )
    return [TicketSummaryResponse(**ticket) for ticket in updated_tickets]


def update_ticket_status(
    ticket_id: int,
    payload: UpdateTicketStatusRequest,
    background_tasks: BackgroundTasks,
    *,
    current_user: dict,
) -> TicketSummaryResponse:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")

        if current_user["vai_tro"] == "TECHNICIAN":
            _ensure_technician_scope(ticket, current_user)

        _ensure_transition_allowed(ticket["status"], payload.status)

        updates: dict[str, object] = {"trang_thai": payload.status}
        if payload.status == "RESOLVED":
            updates["resolved_at"] = "CURRENT_TIMESTAMP"

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
    
    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "TICKET_STATUS_CHANGED", "ticket_id": ticket_id, "status": payload.status, "message": f"Ticket #{ticket_id} chuyển sang trạng thái {payload.status}"},
        int(ticket["user_id"])
    )

    if payload.status == "RESOLVED":
        with connection_scope() as conn:
            ticket_creator = get_user_by_id(conn, int(ticket["user_id"]))
        if ticket_creator and ticket_creator.get("receive_email_on_resolve") and ticket_creator.get("email"):
            msg = f"Sự cố/yêu cầu #{ticket_id} của bạn đã được giải quyết.\nTrạng thái hiện tại: {payload.status}\n\nVui lòng kiểm tra lại hệ thống để biết thêm chi tiết."
            background_tasks.add_task(send_email_notification, ticket_creator["email"], f"[CS466] Ticket #{ticket_id} đã được giải quyết", msg)

    if updated_ticket is None:
        raise NotFoundError("TICKET_NOT_FOUND")
    return TicketSummaryResponse(**updated_ticket)


def batch_update_ticket_status(
    payload: BatchUpdateTicketStatusRequest,
    *,
    current_user: dict,
) -> list[TicketSummaryResponse]:
    with connection_scope() as connection:
        updated_tickets: list[dict] = []
        try:
            for ticket_id in payload.ticket_ids:
                ticket = repository.get_ticket_by_id(connection, ticket_id)
                if ticket is None:
                    raise NotFoundError("TICKET_NOT_FOUND")

                if payload.status == "CLOSED":
                    if ticket["status"] != "RESOLVED":
                        raise BadRequestError("INVALID_TRANSITION")
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
                    continue

                _ensure_transition_allowed(ticket["status"], payload.status)
                updates: dict[str, object] = {"trang_thai": payload.status}
                if payload.status == "RESOLVED":
                    updates["resolved_at"] = "CURRENT_TIMESTAMP"

                repository.update_ticket_fields(connection, ticket_id, updates)
                repository.insert_ticket_history(
                    connection,
                    ticket_id=ticket_id,
                    actor_user_id=int(current_user["id"]),
                    action="STATUS_CHANGED",
                    old_status=ticket["status"],
                    new_status=payload.status,
                    detail=f"Batch status changed to {payload.status}",
                )

            connection.commit()
        except Exception:
            connection.rollback()
            raise

        for ticket_id in payload.ticket_ids:
            updated_ticket = repository.get_ticket_by_id(connection, ticket_id)
            if updated_ticket is None:
                raise NotFoundError("TICKET_NOT_FOUND")
            updated_tickets.append(updated_ticket)

    logger.info(
        "TICKET_BATCH_STATUS_CHANGED count=%s status=%s admin_id=%s",
        len(payload.ticket_ids),
        payload.status,
        current_user["id"],
    )
    return [TicketSummaryResponse(**ticket) for ticket in updated_tickets]


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


def list_ticket_comments(ticket_id: int, *, current_user: dict) -> list[TicketCommentResponse]:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        _ensure_visible(ticket, current_user)
        comments = repository.list_comments(connection, ticket_id)

    return [TicketCommentResponse(**comment) for comment in comments]


def create_ticket_comment(
    ticket_id: int,
    payload: CreateTicketCommentRequest,
    background_tasks: BackgroundTasks,
    *,
    current_user: dict,
) -> TicketCommentResponse:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        _ensure_visible(ticket, current_user)

        try:
            comment_id = repository.create_comment(
                connection,
                ticket_id=ticket_id,
                user_id=int(current_user["id"]),
                content=payload.content,
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

        new_comment = repository.get_comment_by_id(connection, comment_id)

    logger.info("TICKET_COMMENT_CREATED ticket_id=%s user_id=%s", ticket_id, current_user["id"])
    
    notify_user_id = int(ticket["technician_id"]) if ticket.get("technician_id") and int(current_user["id"]) == int(ticket["user_id"]) else int(ticket["user_id"])
    if notify_user_id and notify_user_id != int(current_user["id"]):
        background_tasks.add_task(
            manager.send_personal_message,
            {"type": "NEW_COMMENT", "ticket_id": ticket_id, "message": f"Có bình luận mới trong Ticket #{ticket_id}"},
            notify_user_id
        )

    if new_comment is None:
        raise NotFoundError("COMMENT_NOT_FOUND")
    return TicketCommentResponse(**new_comment)


def get_dashboard_stats(*, current_user: dict) -> DashboardStatsResponse:
    role = current_user["vai_tro"]
    user_id = int(current_user["id"])

    with connection_scope() as connection:
        stats = repository.get_dashboard_stats(connection, role, user_id)

    urgent_tickets = [TicketSummaryResponse(**t) for t in stats["urgent_tickets"]]
    return DashboardStatsResponse(
        total_tickets=stats["total_tickets"],
        total_devices=stats["total_devices"],
        total_users=stats["total_users"],
        status_counts=stats["status_counts"],
        priority_counts=stats["priority_counts"],
        category_counts=stats["category_counts"],
        urgent_tickets=urgent_tickets,
    )


def upload_ticket_attachment(
    ticket_id: int,
    file: UploadFile,
    *,
    current_user: dict,
) -> TicketAttachmentResponse:
    settings = get_settings()

    original_filename = os.path.basename(file.filename or "attachment")
    ext = os.path.splitext(original_filename)[1].lstrip(".").lower()

    if ext not in settings.allowed_upload_extensions:
        raise BadRequestError("INVALID_FILE_TYPE")

    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        _ensure_visible(ticket, current_user)

        os.makedirs("uploads", exist_ok=True)
        unique_token = uuid.uuid4().hex[:12]
        safe_filename = f"{ticket_id}_{unique_token}.{ext}" if ext else f"{ticket_id}_{unique_token}"
        file_path = os.path.join("uploads", safe_filename)

        total_bytes = 0
        chunk_size = 64 * 1024  # 64 KB
        with open(file_path, "wb") as buffer:
            while True:
                chunk = file.file.read(chunk_size)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > settings.max_upload_size_bytes:
                    buffer.close()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise BadRequestError("FILE_TOO_LARGE")
                buffer.write(chunk)

        try:
            attachment_id = repository.create_attachment(
                connection,
                ticket_id=ticket_id,
                file_path=file_path,
                file_name=original_filename,
                file_type=file.content_type or "application/octet-stream",
                uploaded_by=int(current_user["id"]),
            )
            connection.commit()
        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            connection.rollback()
            raise

        attachments = repository.get_attachments_by_ticket_id(connection, ticket_id)
        for att in attachments:
            if att["id"] == attachment_id:
                return TicketAttachmentResponse(**att)

        raise NotFoundError("ATTACHMENT_NOT_FOUND")


def get_ticket_attachment_file(
    ticket_id: int,
    attachment_id: int,
    *,
    current_user: dict,
) -> tuple[str, str, str | None]:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        _ensure_visible(ticket, current_user)

        attachments = repository.get_attachments_by_ticket_id(connection, ticket_id)
        target_att = next((att for att in attachments if att["id"] == attachment_id), None)
        if target_att is None:
            raise NotFoundError("ATTACHMENT_NOT_FOUND")

        file_path = target_att["file_path"]
        if not os.path.exists(file_path):
            raise NotFoundError("FILE_NOT_FOUND")

        return file_path, target_att["file_name"], target_att.get("file_type")


def list_ticket_attachments(
    ticket_id: int,
    *,
    current_user: dict,
) -> list[TicketAttachmentResponse]:
    with connection_scope() as connection:
        ticket = repository.get_ticket_by_id(connection, ticket_id)
        if ticket is None:
            raise NotFoundError("TICKET_NOT_FOUND")
        _ensure_visible(ticket, current_user)
        attachments = repository.get_attachments_by_ticket_id(connection, ticket_id)

    return [TicketAttachmentResponse(**att) for att in attachments]

