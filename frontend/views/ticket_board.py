from __future__ import annotations

from typing import Any

from nicegui import ui

from common.components.data_table import adaptive_ticket_list
from common.components.layout import app_shell
from common.components import toast
from common.formatters import format_datetime
from core.constants import TicketPriority, TicketStatus
from services.ticket_service import FALLBACK_TICKETS, ticket_service
from services.user_service import user_service


TICKET_COLUMNS = [
    {"name": "id", "label": "ID", "field": "id", "sortable": True, "align": "left"},
    {"name": "title", "label": "Tiêu đề", "field": "title", "sortable": True, "align": "left"},
    {"name": "priority", "label": "Ưu tiên", "field": "priority", "sortable": True, "align": "center"},
    {"name": "status", "label": "Trạng thái", "field": "status", "sortable": True, "align": "center"},
    {"name": "user_id", "label": "Người tạo", "field": "user_id", "align": "center"},
    {"name": "technician_id", "label": "KTV", "field": "technician_id", "align": "center"},
    {"name": "updated_at", "label": "Cập nhật", "field": "updated_at", "sortable": True, "align": "center"},
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

        with ui.row().classes("w-full justify-between items-center flex-wrap gap-3"):
            with ui.column().classes("gap-0.5"):
                ui.label(title).classes("text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight")
                ui.label("Tra cứu, phân loại trạng thái và quản lý tiến trình xử lý sự cố CNTT.").classes("text-xs text-slate-500")

            if role in ("ADMIN", "USER"):
                with ui.button("Tạo yêu cầu mới", icon="add", on_click=lambda: ui.navigate.to("/user/tickets/new")).props(
                    "unelevated no-caps"
                ).classes("bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-sm shadow-blue-500/20"):
                    pass

        with ui.card().classes("w-full p-3 rounded-2xl bg-white border border-slate-200/80 shadow-xs mt-1"):
            with ui.row().classes("w-full gap-3 items-center flex-wrap"):
                keyword = (
                    ui.input(placeholder="Tìm kiếm theo từ khóa...")
                    .props("outlined clearable debounce=300 dense")
                    .classes("flex-grow min-w-[220px] text-xs")
                )
                keyword.add_slot("prepend", '<i class="q-icon material-icons text-slate-400 text-base">search</i>')

                status = (
                    ui.select(["ALL", *[item.value for item in TicketStatus]], value="ALL", label="Trạng thái")
                    .props("outlined dense")
                    .classes("w-36 text-xs")
                )
                priority = (
                    ui.select(["ALL", *[item.value for item in TicketPriority]], value="ALL", label="Ưu tiên")
                    .props("outlined dense")
                    .classes("w-36 text-xs")
                )
                refresh_btn = (
                    ui.button("Làm mới", icon="refresh")
                    .props("flat dense color=primary")
                    .classes("text-xs font-semibold px-2 py-1")
                )

        container = ui.column().classes("w-full mt-1")

        async def show_detail(ticket: dict[str, Any]) -> None:
            dialog = ui.dialog().classes("w-full max-w-4xl")
            with dialog, ui.card().classes("w-full max-w-4xl rounded-2xl p-0 overflow-hidden shadow-lg"):
                # Header
                with ui.row().classes("w-full bg-slate-50 p-4 border-b border-slate-100 justify-between items-center"):
                    with ui.column().classes("gap-1"):
                        ui.label(f"Ticket #{ticket.get('id')}").classes("text-sm font-semibold text-slate-500")
                        ui.label(ticket.get('title', '')).classes("text-xl font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat round dense text-color=slate-500")

                with ui.row().classes("w-full p-4 gap-4"):
                    # Left Column - Details
                    with ui.column().classes("col-span-12 md:col-span-8 flex-grow gap-4"):
                        with ui.card().classes("w-full shadow-none border border-slate-100 p-4"):
                            ui.label("Mô tả sự cố").classes("font-semibold text-slate-700 mb-2")
                            ui.label(ticket.get("description", "")).classes("text-sm text-slate-600 whitespace-pre-wrap")
                        
                        # Comments Section (Mock for now since no API)
                        with ui.card().classes("w-full shadow-none border border-slate-100 p-4 bg-slate-50/50"):
                            ui.label("Bình luận & Phản hồi").classes("font-semibold text-slate-700 mb-2")
                            ui.label("Hiện chưa có API lấy danh sách và thêm bình luận.").classes("text-sm text-amber-600 italic mb-4")
                            
                            with ui.row().classes("w-full gap-2 items-start"):
                                ui.textarea(placeholder="Nhập phản hồi của bạn...").props("outlined dense").classes("flex-grow")
                                ui.button("Gửi", on_click=lambda: toast.warning("API Comment chưa được hỗ trợ trên Backend!")).props("color=primary")

                    # Right Column - Meta & Timeline
                    with ui.column().classes("col-span-12 md:col-span-4 w-full md:w-72 gap-4"):
                        # Properties
                        with ui.card().classes("w-full shadow-none border border-slate-100 p-4"):
                            ui.label("Thông tin chung").classes("font-semibold text-slate-700 mb-3")
                            
                            with ui.column().classes("w-full gap-2 text-sm"):
                                with ui.row().classes("w-full justify-between"):
                                    ui.label("Trạng thái:").classes("text-slate-500")
                                    ui.label(ticket.get("status", "")).classes("font-semibold")
                                
                                with ui.row().classes("w-full justify-between"):
                                    ui.label("Ưu tiên:").classes("text-slate-500")
                                    ui.label(ticket.get("priority", "")).classes("font-semibold")
                                
                                with ui.row().classes("w-full justify-between"):
                                    ui.label("Danh mục:").classes("text-slate-500")
                                    ui.label(ticket.get("category", "")).classes("font-semibold")
                        
                        # Relations
                        with ui.card().classes("w-full shadow-none border border-slate-100 p-4"):
                            ui.label("Liên quan").classes("font-semibold text-slate-700 mb-3")
                            
                            with ui.column().classes("w-full gap-2 text-sm"):
                                ui.label("Người tạo").classes("text-slate-500 text-xs uppercase")
                                ui.label(f"User ID: {ticket.get('user_id')}").classes("font-medium mb-1")
                                
                                ui.label("Kỹ thuật viên").classes("text-slate-500 text-xs uppercase")
                                ui.label(f"Tech ID: {ticket.get('technician_id', 'Chưa phân công')}").classes("font-medium mb-1")
                                
                                ui.label("Thiết bị").classes("text-slate-500 text-xs uppercase")
                                ui.label(f"Device ID: {ticket.get('device_id', 'Không có')}").classes("font-medium mb-1")

                        # Timeline Loader
                        timeline_container = ui.column().classes("w-full")

                # Fetch real detail & timeline dynamically
                async def load_extra() -> None:
                    try:
                        detail = await ticket_service.get_ticket(int(ticket["id"]))
                        history = await ticket_service.get_history(int(ticket["id"]))
                    except Exception as exc:
                        toast.error(f"Lỗi tải chi tiết: {exc}")
                        return
                    
                    # You could update properties here if needed, 
                    # but for now we just render timeline
                    with timeline_container:
                        with ui.card().classes("w-full shadow-none border border-slate-100 p-4"):
                            ui.label("Lịch sử xử lý").classes("font-semibold text-slate-700 mb-3")
                            for item in history:
                                with ui.column().classes("mb-2"):
                                    ui.label(format_datetime(item.get('performed_at'))).classes("text-xs text-slate-400")
                                    action_text = f"{item.get('action')} · {item.get('old_status') or '-'} → {item.get('new_status') or '-'}"
                                    ui.label(action_text).classes("text-sm text-slate-700 font-medium")
                                    if item.get('detail'):
                                        ui.label(item.get('detail')).classes("text-xs text-slate-500")
                
                ui.timer(0.1, load_extra, once=True)

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
            container.clear()
            with container:
                ui.spinner("dots", size="md").classes("mx-auto my-6 text-blue-600")

            tickets: list[dict[str, Any]] = []
            try:
                tickets = await ticket_service.list_tickets(
                    status=None if status.value == "ALL" else status.value,
                    priority=None if priority.value == "ALL" else priority.value,
                    user_id=user.get("id") if default_user_scope else None,
                    keyword=keyword.value,
                    refresh=True,
                )
            except Exception:
                tickets = list(FALLBACK_TICKETS)

            rows = normalize_ticket_rows(tickets)
            container.clear()
            with container:
                adaptive_ticket_list(
                    rows,
                    TICKET_COLUMNS,
                    on_detail=show_detail,
                    on_action=show_action if (can_assign or can_change_status) else None,
                )

        refresh_btn.on_click(reload)
        keyword.on_value_change(reload)
        status.on_value_change(reload)
        priority.on_value_change(reload)

        ui.timer(0.1, reload, once=True)

    app_shell(title, content)
