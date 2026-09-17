from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.loading import skeleton_loader
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, truncate
from common.styles.theme import (
    PROPS_BUTTON_PRIMARY,
    STYLE_CARD,
    STYLE_PAGE_HEADER,
    STYLE_SUBTITLE,
    STYLE_TITLE_LG,
)
from core.constants import CATEGORY_LABELS, TicketStatus
from services.ticket_service import ticket_service


def render_my_tickets_view() -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")

        # 1. Page Header
        with ui.row().classes(STYLE_PAGE_HEADER):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("Yêu cầu hỗ trợ của tôi").classes(STYLE_TITLE_LG)
                    ui.label("USER DESK").classes("text-[9px] font-bold px-1.5 py-0.2 rounded bg-blue-100 text-blue-800 border border-blue-200 uppercase")
                ui.label("Theo dõi tiến trình giải quyết các sự cố và dịch vụ IT bạn đã gửi.").classes(STYLE_SUBTITLE)

            ui.button(
                "Tạo yêu cầu mới",
                icon="add",
                on_click=lambda: ui.navigate.to("/user/tickets/new"),
            ).props(PROPS_BUTTON_PRIMARY).classes("px-4 py-2 font-bold shadow-xs")

        # 2. Filters Toolbar
        with ui.card().classes("w-full p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs mb-3"):
            with ui.row().classes("w-full gap-3 items-end flex-wrap"):
                keyword = ui.input(placeholder="Tìm kiếm theo tiêu đề sự cố...").props("outlined dense clearable debounce=300").classes("flex-1 min-w-[220px]")
                status_filter = ui.select(["ALL", *[item.value for item in TicketStatus]], value="ALL", label="Trạng thái").props("outlined dense").classes("w-44")

                async def handle_manual_refresh() -> None:
                    tickets_list_refresh.refresh(is_loading=True)
                    await fetch_and_refresh()
                    toast.success("Đã làm mới danh sách yêu cầu!")

                ui.button("Tải lại", icon="refresh", on_click=handle_manual_refresh).props("outline dense size=sm color=slate-700").classes("py-2 px-3")

        # 3. Reactive Refreshable List
        state: dict[str, Any] = {"tickets": [], "loaded": False, "error": None}

        @ui.refreshable
        def tickets_list_refresh(is_loading: bool = False) -> None:
            if is_loading or not state["loaded"]:
                skeleton_loader(count=3, height="h-24")
                return

            if state["error"]:
                ui.label(f"Lỗi tải dữ liệu: {state['error']}").classes("text-sm text-red-600")
                return

            tickets = state["tickets"]
            if not tickets:
                empty_state(
                    title="Bạn chưa có yêu cầu nào",
                    subtitle="Khi bạn gặp sự cố máy tính hoặc thiết bị văn phòng, hãy tạo yêu cầu để được hỗ trợ.",
                    icon="support_agent",
                    action_label="+ Tạo yêu cầu đầu tiên",
                    on_action=lambda: ui.navigate.to("/user/tickets/new"),
                )
            else:
                with ui.column().classes("w-full gap-2.5"):
                    with ui.row().classes("w-full justify-between items-center px-1 mb-0.5"):
                        ui.label(f"DANH SÁCH YÊU CẦU ({len(tickets)})").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")

                    for tck in tickets:
                        tck_id = int(tck.get("id"))
                        cat_label = CATEGORY_LABELS.get(tck.get("category"), "Sự cố kỹ thuật")
                        with ui.card().classes(
                            f"w-full {STYLE_CARD} gap-2 hover:border-slate-300"
                        ):
                            with ui.row().classes("w-full justify-between items-start gap-3"):
                                with ui.column().classes("gap-1 flex-1 min-w-[240px]"):
                                    with ui.row().classes("items-center gap-2 flex-wrap"):
                                        ui.label(f"#{tck_id}").classes("text-xs font-mono font-bold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded")
                                        ui.label(tck.get("title", "-")).classes("text-sm font-bold text-slate-900 leading-snug")
                                        ui.label(cat_label).classes("text-[10px] font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200")
                                    ui.label(truncate(tck.get("description", ""), 130)).classes("text-xs text-slate-600 line-clamp-1")

                                with ui.row().classes("items-center gap-2 shrink-0"):
                                    priority_badge(tck.get("priority"))
                                    status_badge(tck.get("status"))

                            with ui.row().classes("w-full justify-between items-center pt-2.5 border-t border-slate-100 text-xs text-slate-500 flex-wrap gap-2"):
                                ui.label(f"🕒 Cập nhật: {format_datetime(tck.get('updated_at'))}").classes("text-[11px] text-slate-400")
                                ui.button(
                                    "Xem chi tiết & Chat",
                                    icon="chat",
                                    on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                                ).props(PROPS_BUTTON_PRIMARY + " size=sm").classes("px-3 text-xs font-bold")

        async def fetch_and_refresh() -> None:
            try:
                state["tickets"] = await ticket_service.list_tickets(
                    user_id=user_id,
                    status=None if status_filter.value == "ALL" else status_filter.value,
                    keyword=keyword.value,
                    refresh=True,
                )
                state["error"] = None
            except Exception as exc:
                state["error"] = str(exc)
                toast.show_popup("Lỗi tải danh sách", "Không thể tải dữ liệu ticket từ máy chủ.", type="error", detail=str(exc))
            finally:
                state["loaded"] = True
                tickets_list_refresh.refresh()

        # Mount initial view & listeners
        tickets_list_refresh()
        keyword.on_value_change(fetch_and_refresh)
        status_filter.on_value_change(fetch_and_refresh)
        ui.timer(0.05, fetch_and_refresh, once=True)

    app_shell("Yêu cầu của tôi", content)
