from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, truncate
from core.constants import CATEGORY_LABELS
from services.ticket_service import ticket_service


def render_task_board_view() -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")
        user_role = user.get("vai_tro", "TECHNICIAN")

        # Active filter state
        filter_scope = {"value": "MY_TASKS"}  # 'MY_TASKS' | 'ALL' | 'URGENT'

        # Page Header Banner
        with ui.row().classes("w-full justify-between items-center py-2 border-b border-slate-200 mb-4"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("Bàn làm việc Kỹ thuật viên").classes("text-xl font-bold text-slate-900")
                    ui.label("PROD-WORKSPACE").classes("text-[10px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 tracking-wider uppercase")
                ui.label("Theo dõi, nhận việc và cập nhật tiến độ xử lý sự cố trực tiếp theo thời gian thực.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                ui.button("Tra cứu thiết bị", icon="search", on_click=lambda: ui.navigate.to("/technician/devices")).props("outline dense size=sm color=slate-700").classes("px-3 py-1.5")
                ui.button("Tải lại", icon="refresh", on_click=lambda: load_board_data()).props("unelevated dense size=sm color=primary").classes("px-3 py-1.5")

        # Top Metric Counters Ribbon
        metrics_ribbon = ui.row().classes("w-full gap-3 mb-4 items-stretch")

        # Filter Controls Bar
        with ui.card().classes("w-full p-3 rounded-xl bg-white border border-slate-200 shadow-sm mb-4"):
            with ui.row().classes("w-full justify-between items-center flex-wrap gap-3"):
                # Filter Scope Tabs
                with ui.row().classes("items-center gap-1.5 p-1 bg-slate-100 rounded-lg border border-slate-200/80"):
                    btn_my = ui.button("👤 Việc của tôi", on_click=lambda: set_filter("MY_TASKS")).props("dense unelevated size=sm").classes("px-3 py-1 text-xs font-semibold")
                    btn_all = ui.button("🌐 Tất cả hàng đợi", on_click=lambda: set_filter("ALL")).props("dense flat size=sm").classes("px-3 py-1 text-xs font-semibold text-slate-600")
                    btn_urgent = ui.button("⚡ Sự cố khẩn cấp", on_click=lambda: set_filter("URGENT")).props("dense flat size=sm").classes("px-3 py-1 text-xs font-semibold text-slate-600")

                # Keyword Search
                search_input = ui.input(placeholder="Tìm nhanh theo tiêu đề sự cố...").props("outlined dense clearable debounce=300").classes("w-72")

        # Kanban 4 Columns Container
        board_container = ui.row().classes("w-full gap-4 items-start flex-nowrap overflow-x-auto pb-4")

        def set_filter(scope: str) -> None:
            filter_scope["value"] = scope
            btn_my.props("unelevated" if scope == "MY_TASKS" else "flat")
            btn_my.classes("bg-white text-blue-700 shadow-sm" if scope == "MY_TASKS" else "text-slate-600")
            btn_all.props("unelevated" if scope == "ALL" else "flat")
            btn_all.classes("bg-white text-blue-700 shadow-sm" if scope == "ALL" else "text-slate-600")
            btn_urgent.props("unelevated" if scope == "URGENT" else "flat")
            btn_urgent.classes("bg-white text-red-700 shadow-sm" if scope == "URGENT" else "text-slate-600")
            load_board_data()

        async def claim_ticket(ticket_id: int) -> None:
            try:
                await ticket_service.assign_ticket(ticket_id, int(user_id))
                toast.success(f"Bạn đã nhận xử lý Ticket #{ticket_id} thành công!")
                await load_board_data()
            except Exception as exc:
                toast.error(f"Không thể nhận ticket: {exc}")

        async def update_status(ticket_id: int, target_status: str, note: str | None = None) -> None:
            try:
                if target_status == "CLOSED":
                    await ticket_service.close_ticket(ticket_id, note)
                else:
                    await ticket_service.update_status(ticket_id, target_status)
                toast.success(f"Đã cập nhật trạng thái Ticket #{ticket_id} sang {target_status}")
                await load_board_data()
            except Exception as exc:
                toast.error(f"Lỗi: {exc}")

        def open_resolution_modal(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-3"):
                ui.label(f"Hoàn tất & Đóng Ticket #{ticket_id}").classes("text-base font-bold text-slate-900")
                ui.label("Ghi lại giải pháp xử lý hoặc kết quả khắc phục sự cố:").classes("text-xs text-slate-500 mb-1")
                solution_text = ui.textarea(placeholder="Ví dụ: Đã thay cáp mạng mới tại cổng số 4, máy in đã kết nối ổn định...").props("outlined rows=3").classes("w-full")

                async def confirm_close() -> None:
                    dialog.close()
                    await update_status(ticket_id, "CLOSED", solution_text.value or None)

                with ui.row().classes("w-full justify-end gap-2 mt-4 pt-3 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600")
                    ui.button("Xác nhận đóng", icon="check_circle", on_click=confirm_close).props("color=primary unelevated")
            dialog.open()

        async def load_board_data() -> None:
            try:
                all_tickets = await ticket_service.list_tickets(refresh=True)
            except Exception as exc:
                board_container.clear()
                with board_container:
                    ui.label(f"Lỗi tải dữ liệu: {exc}").classes("text-sm text-red-600")
                return

            keyword = (search_input.value or "").strip().lower()

            # Filter tickets according to active scope
            filtered_tickets = []
            for t in all_tickets:
                # Text filter
                if keyword and keyword not in (t.get("title", "") or "").lower():
                    continue

                scope = filter_scope["value"]
                if scope == "MY_TASKS":
                    # My assigned or unassigned OPEN tickets
                    if t.get("technician_id") == user_id or t.get("status") == "OPEN":
                        filtered_tickets.append(t)
                elif scope == "URGENT":
                    if t.get("priority") in ("URGENT", "HIGH"):
                        filtered_tickets.append(t)
                else:
                    filtered_tickets.append(t)

            # Calculate counts
            open_list = [t for t in filtered_tickets if t.get("status") in ("OPEN", "ASSIGNED")]
            progress_list = [t for t in filtered_tickets if t.get("status") == "IN_PROGRESS"]
            resolved_list = [t for t in filtered_tickets if t.get("status") == "RESOLVED"]
            closed_list = [t for t in filtered_tickets if t.get("status") == "CLOSED"]

            # 1. Render Top Metric Counters
            metrics_ribbon.clear()
            with metrics_ribbon:
                with ui.card().classes("flex-1 p-3 rounded-xl bg-blue-50/70 border border-blue-200/80 shadow-none"):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("CHỜ TIẾP NHẬN").classes("text-[10px] font-bold text-blue-700 tracking-wider")
                            ui.label(str(len(open_list))).classes("text-xl font-extrabold text-blue-900")
                        ui.icon("inbox").classes("text-2xl text-blue-400")

                with ui.card().classes("flex-1 p-3 rounded-xl bg-amber-50/70 border border-amber-200/80 shadow-none"):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("ĐANG XỬ LÝ").classes("text-[10px] font-bold text-amber-700 tracking-wider")
                            ui.label(str(len(progress_list))).classes("text-xl font-extrabold text-amber-900")
                        ui.icon("pending").classes("text-2xl text-amber-400")

                with ui.card().classes("flex-1 p-3 rounded-xl bg-emerald-50/70 border border-emerald-200/80 shadow-none"):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("ĐÃ KHẮC PHỤC").classes("text-[10px] font-bold text-emerald-700 tracking-wider")
                            ui.label(str(len(resolved_list))).classes("text-xl font-extrabold text-emerald-900")
                        ui.icon("check_circle").classes("text-2xl text-emerald-400")

                with ui.card().classes("flex-1 p-3 rounded-xl bg-slate-100 border border-slate-200 shadow-none"):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("ĐÃ HOÀN TẤT & ĐÓNG").classes("text-[10px] font-bold text-slate-600 tracking-wider")
                            ui.label(str(len(closed_list))).classes("text-xl font-extrabold text-slate-800")
                        ui.icon("lock").classes("text-2xl text-slate-400")

            # 2. Render 4-Column Kanban
            columns_def = [
                ("CHỜ TIẾP NHẬN", open_list, "border-t-4 border-t-blue-600", "bg-blue-600", "inbox"),
                ("ĐANG KHẮC PHỤC", progress_list, "border-t-4 border-t-amber-500", "bg-amber-500", "pending"),
                ("ĐÃ KHẮC PHỤC", resolved_list, "border-t-4 border-t-emerald-500", "bg-emerald-500", "check_circle"),
                ("ĐÃ HOÀN TẤT & ĐÓNG", closed_list, "border-t-4 border-t-slate-400", "bg-slate-400", "lock"),
            ]

            board_container.clear()
            with board_container:
                for col_title, ticket_sublist, border_class, badge_bg, col_icon in columns_def:
                    with ui.column().classes(f"min-w-[310px] w-80 bg-slate-100/90 p-3 rounded-xl border border-slate-200 {border_class} gap-3 flex-shrink-0"):
                        # Column Header
                        with ui.row().classes("w-full justify-between items-center px-1 pb-1"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.icon(col_icon).classes("text-sm text-slate-600")
                                ui.label(col_title).classes("text-xs font-bold text-slate-800 uppercase tracking-wider")
                            ui.label(str(len(ticket_sublist))).classes("text-xs font-bold px-2 py-0.5 bg-white rounded-full text-slate-700 border border-slate-200 shadow-sm")

                        # Tickets in column
                        if not ticket_sublist:
                            with ui.column().classes("w-full py-10 items-center justify-center text-slate-400 gap-1"):
                                ui.icon("inbox").classes("text-2xl text-slate-300")
                                ui.label("Không có ticket nào").classes("text-xs font-medium")
                        else:
                            for tck in ticket_sublist:
                                tck_id = int(tck.get("id"))
                                cur_status = tck.get("status")
                                is_my_assigned = tck.get("technician_id") == user_id
                                is_unassigned = tck.get("technician_id") is None
                                cat_label = CATEGORY_LABELS.get(tck.get("category"), "Sự cố")

                                with ui.card().classes("card-hover w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm gap-2.5 relative overflow-hidden"):
                                    # Card Top: ID, Category & Priority
                                    with ui.row().classes("w-full justify-between items-center no-wrap"):
                                        with ui.row().classes("items-center gap-1.5"):
                                            ui.label(f"#{tck_id}").classes("text-xs font-extrabold text-blue-600")
                                            ui.label(cat_label).classes("text-[10px] font-semibold px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 border border-slate-200")
                                        priority_badge(tck.get("priority"))

                                    # Title & Description
                                    ui.label(tck.get("title", "-")).classes("text-sm font-bold text-slate-900 line-clamp-2 leading-snug")
                                    if tck.get("description"):
                                        ui.label(truncate(tck["description"], 80)).classes("text-xs text-slate-500 line-clamp-2 leading-relaxed")

                                    # Device & Location Meta
                                    device_id = tck.get("device_id")
                                    if device_id:
                                        with ui.row().classes("items-center gap-1.5 py-1 px-2 rounded bg-slate-50 border border-slate-100 text-[11px] text-slate-600"):
                                            ui.icon("laptop_mac").classes("text-xs text-blue-500")
                                            ui.label(f"Thiết bị #{device_id}").classes("font-semibold text-slate-700")

                                    # Footer: Time & Detail Link
                                    with ui.row().classes("w-full justify-between items-center pt-2 border-t border-slate-100 text-[11px] text-slate-400"):
                                        ui.label(format_datetime(tck.get("updated_at")))
                                        ui.button(
                                            "Chi tiết & Chat",
                                            icon="chat_bubble_outline",
                                            on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                                        ).props("flat dense size=xs color=primary").classes("font-semibold")

                                    # Action Buttons according to workflow
                                    if cur_status == "OPEN":
                                        if is_unassigned:
                                            ui.button(
                                                "⚡ Nhận xử lý sự cố này",
                                                on_click=lambda tck_id=tck_id: claim_ticket(tck_id),
                                            ).props("unelevated dense size=sm color=primary").classes("w-full text-xs font-bold py-1.5 shadow-sm")
                                        else:
                                            ui.button(
                                                "▶ Bắt đầu khắc phục",
                                                on_click=lambda tck_id=tck_id: update_status(tck_id, "IN_PROGRESS"),
                                            ).props("unelevated dense size=sm color=amber-700").classes("w-full text-xs font-bold py-1.5")
                                    elif cur_status == "ASSIGNED":
                                        ui.button(
                                            "▶ Bắt đầu khắc phục",
                                            on_click=lambda tck_id=tck_id: update_status(tck_id, "IN_PROGRESS"),
                                        ).props("unelevated dense size=sm color=amber-700").classes("w-full text-xs font-bold py-1.5")
                                    elif cur_status == "IN_PROGRESS":
                                        ui.button(
                                            "✅ Đã khắc phục xong",
                                            on_click=lambda tck_id=tck_id: update_status(tck_id, "RESOLVED"),
                                        ).props("unelevated dense size=sm color=emerald-700").classes("w-full text-xs font-bold py-1.5 shadow-sm")
                                    elif cur_status == "RESOLVED":
                                        ui.button(
                                            "🔒 Đóng sự cố & Ghi chú",
                                            on_click=lambda tck_id=tck_id: open_resolution_modal(tck_id),
                                        ).props("outline dense size=sm color=slate-700").classes("w-full text-xs font-bold py-1.5")

        search_input.on("update:model-value", lambda: load_board_data())
        ui.timer(0.1, load_board_data, once=True)

    app_shell("Bảng công việc Kỹ thuật viên", content)
