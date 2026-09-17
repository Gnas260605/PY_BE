from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, truncate
from core.constants import TicketStatus
from services.ticket_service import ticket_service


def render_my_tickets_view() -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")

        # Header
        with ui.row().classes("w-full justify-between items-center mb-4"):
            with ui.column().classes("gap-0.5"):
                ui.label("Yêu cầu hỗ trợ của tôi").classes("text-2xl font-bold text-slate-900")
                ui.label("Theo dõi tiến trình giải quyết các sự cố và dịch vụ IT bạn đã gửi.").classes("text-xs text-slate-500")

            ui.button("Tạo yêu cầu mới", icon="add", on_click=lambda: ui.navigate.to("/user/tickets/new")).props("color=primary unelevated")

        # Filters Toolbar
        with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm"):
            with ui.row().classes("w-full gap-3 items-end"):
                keyword = ui.input("Tìm kiếm theo tiêu đề...").props("outlined clearable debounce=300").classes("flex-1 min-w-[240px]")
                status_filter = ui.select(["ALL", *[item.value for item in TicketStatus]], value="ALL", label="Trạng thái").props("outlined").classes("w-48")
                
                async def handle_manual_refresh() -> None:
                    await load_my_tickets()
                    toast.success("Đã làm mới danh sách yêu cầu!")

                ui.button("Tải lại", icon="refresh", on_click=handle_manual_refresh).props("outline size=sm color=slate-700").classes("py-2.5")

        # Ticket List Container
        ticket_container = ui.column().classes("w-full gap-3 mt-4")

        async def load_my_tickets() -> None:
            try:
                tickets = await ticket_service.list_tickets(
                    user_id=user_id,
                    status=None if status_filter.value == "ALL" else status_filter.value,
                    keyword=keyword.value,
                    refresh=True,
                )
            except Exception as exc:
                ticket_container.clear()
                with ticket_container:
                    ui.label(f"Lỗi tải danh sách yêu cầu: {exc}").classes("text-sm text-red-600")
                toast.show_popup("Lỗi tải danh sách", "Không thể tải dữ liệu ticket từ máy chủ.", type="error", detail=str(exc))
                return

            ticket_container.clear()
            with ticket_container:
                if not tickets:
                    empty_state(
                        title="Bạn chưa có yêu cầu nào",
                        subtitle="Khi bạn gặp sự cố máy tính hoặc thiết bị văn phòng, hãy tạo yêu cầu để được hỗ trợ.",
                        icon="receipt_long",
                        action_label="+ Tạo yêu cầu đầu tiên",
                        on_action=lambda: ui.navigate.to("/user/tickets/new"),
                    )
                else:
                    for tck in tickets:
                        tck_id = int(tck.get("id"))
                        with ui.card().classes("card-hover w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm gap-2"):
                            with ui.row().classes("w-full justify-between items-start"):
                                with ui.column().classes("gap-1 flex-1"):
                                    with ui.row().classes("items-center gap-2"):
                                        ui.label(f"#{tck_id}").classes("text-xs font-bold text-blue-600")
                                        ui.label(tck.get("title", "-")).classes("text-base font-bold text-slate-800")
                                    ui.label(truncate(tck.get("description", ""), 120)).classes("text-xs text-slate-500 line-clamp-2")
                                with ui.row().classes("items-center gap-2 shrink-0"):
                                    priority_badge(tck.get("priority"))
                                    status_badge(tck.get("status"))

                            with ui.row().classes("w-full justify-between items-center pt-2 border-t border-slate-100 text-xs text-slate-400"):
                                ui.label(f"Cập nhật lúc: {format_datetime(tck.get('updated_at'))}")
                                ui.button(
                                    "Xem chi tiết & Chat",
                                    icon="chat",
                                    on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                                ).props("unelevated size=sm color=primary")

        ui.timer(0.1, load_my_tickets, once=True)

    app_shell("Yêu cầu của tôi", content)
