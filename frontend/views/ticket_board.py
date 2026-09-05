from __future__ import annotations

from typing import Any

from nicegui import ui

from common.components.data_table import adaptive_ticket_list
from common.components.layout import app_shell
from common.components import toast
from common.formatters import format_datetime
from core.constants import TicketPriority, TicketStatus
from services.ticket_service import ticket_service
from services.user_service import user_service


TICKET_COLUMNS = [
    {"name": "id", "label": "ID", "field": "id", "sortable": True},
    {"name": "title", "label": "Tiêu đề", "field": "title", "sortable": True},
    {"name": "priority", "label": "Ưu tiên", "field": "priority", "sortable": True},
    {"name": "status", "label": "Trạng thái", "field": "status", "sortable": True},
    {"name": "user_id", "label": "Người tạo", "field": "user_id"},
    {"name": "technician_id", "label": "KTV", "field": "technician_id"},
    {"name": "updated_at", "label": "Cập nhật", "field": "updated_at", "sortable": True},
]


def normalize_ticket_rows(tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            **ticket,
            "updated_at": format_datetime(ticket.get("updated_at")),
            "technician_id": ticket.get("technician_id") or "-",
        }
        for ticket in tickets
    ]


def render_ticket_board(title: str, *, default_user_scope: bool = False) -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro", "USER")
        can_change_status = role in ("ADMIN", "TECHNICIAN")
        can_assign = role == "ADMIN"

        ui.label(title).classes("text-3xl font-bold text-slate-900")
        ui.label("Tìm kiếm debounce 300ms qua NiceGUI, dữ liệu dùng cache TTL ở service layer.").classes("text-sm text-slate-500")

        with ui.card().classes("w-full p-4 mt-4 rounded-2xl shadow-sm border border-slate-100"):
            with ui.row().classes("w-full gap-3 items-end"):
                keyword = ui.input("Từ khóa").props("outlined clearable debounce=300").classes("w-full md:w-80")
                status = ui.select(["ALL", *[item.value for item in TicketStatus]], value="ALL", label="Trạng thái").props("outlined").classes("w-full md:w-56")
                priority = ui.select(["ALL", *[item.value for item in TicketPriority]], value="ALL", label="Ưu tiên").props("outlined").classes("w-full md:w-56")
                ui.button("Tải lại", on_click=lambda: reload()).props("color=primary")

        container = ui.column().classes("w-full mt-4")

        async def show_detail(ticket: dict[str, Any]) -> None:
            try:
                detail = await ticket_service.get_ticket(int(ticket["id"]))
                history = await ticket_service.get_history(int(ticket["id"]))
            except Exception as exc:
                toast.error(str(exc))
                return

            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-3xl rounded-2xl"):
                ui.label(f"Ticket #{detail.get('id')} · {detail.get('title')}").classes("text-xl font-bold")
                ui.label(detail.get("description", "")).classes("text-sm text-slate-600")
                ui.separator()
                ui.label("Timeline").classes("font-semibold")
                for item in history:
                    ui.label(
                        f"{format_datetime(item.get('performed_at'))} · {item.get('action')} · {item.get('old_status') or '-'} → {item.get('new_status') or '-'}"
                    ).classes("text-sm text-slate-600")
                ui.button("Đóng", on_click=dialog.close).props("flat color=primary")
            dialog.open()

        async def show_action(ticket: dict[str, Any]) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-lg rounded-2xl"):
                ui.label(f"Thao tác Ticket #{ticket.get('id')}").classes("text-xl font-bold")
                technician_select = None
                if can_assign:
                    technician_select = ui.select({}, label="Kỹ thuật viên").props("outlined").classes("w-full")
                    try:
                        technicians = await user_service.list_technicians()
                        technician_select.options = {item["id"]: f"{item['ho_ten']} ({item['username']})" for item in technicians}
                        technician_select.update()
                    except Exception as exc:
                        toast.warning(f"Không tải được danh sách kỹ thuật viên: {exc}")

                status_options = ticket_service.next_statuses(ticket.get("status"))
                status_select = ui.select(status_options, label="Trạng thái kế tiếp").props("outlined").classes("w-full")
                note = ui.textarea("Ghi chú khi đóng ticket").props("outlined").classes("w-full")

                async def submit() -> None:
                    try:
                        if can_assign and technician_select and technician_select.value:
                            await ticket_service.assign_ticket(int(ticket["id"]), int(technician_select.value))
                        if can_change_status and status_select.value:
                            if status_select.value == "CLOSED":
                                await ticket_service.close_ticket(int(ticket["id"]), note.value or None)
                            else:
                                await ticket_service.update_status(int(ticket["id"]), status_select.value)
                        toast.success("Cập nhật ticket thành công.")
                        dialog.close()
                        await reload()
                    except Exception as exc:
                        toast.error(str(exc))

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Hủy", on_click=dialog.close).props("flat")
                    ui.button("Lưu", on_click=submit).props("color=primary")
            dialog.open()

        async def reload() -> None:
            try:
                tickets = await ticket_service.list_tickets(
                    status=None if status.value == "ALL" else status.value,
                    priority=None if priority.value == "ALL" else priority.value,
                    user_id=user.get("id") if default_user_scope else None,
                    keyword=keyword.value,
                    refresh=True,
                )
                rows = normalize_ticket_rows(tickets)
            except Exception as exc:
                container.clear()
                with container:
                    ui.label(str(exc)).classes("text-red-600")
                return

            container.clear()
            with container:
                adaptive_ticket_list(
                    rows,
                    TICKET_COLUMNS,
                    on_detail=show_detail,
                    on_action=show_action if (can_assign or can_change_status) else None,
                )

        ui.timer(0.1, reload, once=True)

    app_shell(title, content)
