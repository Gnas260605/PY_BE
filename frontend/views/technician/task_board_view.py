from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.comments_thread import comments_thread
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, format_relative_time, truncate
from core.constants import CATEGORY_LABELS
from services.device_service import device_service
from services.ticket_service import ticket_service


def render_task_board_view(initial_tab: str = "MY_TASKS") -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")

        # =========================================================================
        # 1. STATE MANAGEMENT
        # =========================================================================
        state: dict[str, Any] = {
            "raw_tickets": [],
            "devices_cache": {},
            "active_tab": initial_tab,  # 'MY_TASKS' | 'UNASSIGNED' | 'URGENT' | 'IN_PROGRESS' | 'RESOLVED' | 'ALL'
            "selected_ticket_id": None,
            "keyword": "",
            "is_loading": True,
            "error": None,
        }

        # =========================================================================
        # 2. PAGE HEADER (Clean Enterprise Toolbar)
        # =========================================================================
        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-2.5 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-400 font-medium"):
                    ui.label("Trang chủ")
                    ui.label("/").classes("text-slate-300")
                    ui.label("Bàn làm việc KTV")
                    ui.label("/").classes("text-slate-300")
                    ui.label("Công việc").classes("text-slate-700 font-semibold")

                ui.label("Bàn làm việc Kỹ thuật viên").classes("text-2xl font-bold text-slate-900 tracking-tight")
                ui.label("Tiếp nhận, xử lý sự cố và trao đổi trực tiếp với người yêu cầu.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                ui.button(
                    "Tra cứu thiết bị",
                    icon="search",
                    on_click=lambda: ui.navigate.to("/technician/devices"),
                ).props("outline color=slate-700 size=md").classes("h-[36px] rounded-lg font-medium px-3.5 text-xs bg-white border-slate-300 shadow-2xs")

                ui.button(icon="refresh", on_click=lambda: load_tickets_data(refresh=True)).props(
                    "outline dense color=slate-700 size=sm"
                ).classes("h-[36px] w-[36px] rounded-lg bg-white border-slate-300 shadow-2xs").tooltip("Tải lại danh sách")

        # Container for Segmented Queue Tabs (Quick Filter Strip)
        tabs_container = ui.row().classes("w-full mb-3")

        # =========================================================================
        # 3. MASTER-DETAIL 2-COLUMN GRID (Side-by-Side on Desktop)
        # =========================================================================
        with ui.element("div").classes("w-full grid grid-cols-1 lg:grid-cols-[400px_1fr] xl:grid-cols-[430px_1fr] gap-4 items-start"):
            left_pane = ui.column().classes("w-full gap-2.5")
            right_pane = ui.column().classes("w-full gap-3 min-w-0")

        # =========================================================================
        # 4. FILTERING LOGIC
        # =========================================================================
        def filter_tickets(tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
            res = tickets
            tab = state["active_tab"]

            if tab == "MY_TASKS":
                res = [t for t in res if t.get("technician_id") == user_id and t.get("status") != "CLOSED"]
            elif tab == "UNASSIGNED":
                res = [t for t in res if not t.get("technician_id") or t.get("status") == "OPEN"]
            elif tab == "URGENT":
                res = [t for t in res if t.get("priority") in ("URGENT", "HIGH") and t.get("status") != "CLOSED"]
            elif tab == "IN_PROGRESS":
                res = [t for t in res if t.get("status") == "IN_PROGRESS"]
            elif tab == "RESOLVED":
                res = [t for t in res if t.get("status") in ("RESOLVED", "CLOSED")]

            kw = (state["keyword"] or "").strip().lower()
            if kw:
                res = [
                    t
                    for t in res
                    if kw in str(t.get("id", "")).lower()
                    or kw in str(t.get("title", "")).lower()
                    or kw in str(t.get("description", "")).lower()
                ]

            return res

        async def set_active_tab(tab_name: str) -> None:
            state["active_tab"] = tab_name
            filtered = filter_tickets(state["raw_tickets"])
            if filtered:
                if not any(t["id"] == state["selected_ticket_id"] for t in filtered):
                    state["selected_ticket_id"] = filtered[0]["id"]
            else:
                state["selected_ticket_id"] = None
            await render_all()

        # =========================================================================
        # 5. RENDER QUEUE TABS (Compact Segmented Navigation)
        # =========================================================================
        def render_tabs() -> None:
            tabs_container.clear()
            tickets = state["raw_tickets"]
            active_tab = state["active_tab"]

            counts = {
                "MY_TASKS": sum(1 for t in tickets if t.get("technician_id") == user_id and t.get("status") != "CLOSED"),
                "UNASSIGNED": sum(1 for t in tickets if not t.get("technician_id") or t.get("status") == "OPEN"),
                "URGENT": sum(1 for t in tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") != "CLOSED"),
                "IN_PROGRESS": sum(1 for t in tickets if t.get("status") == "IN_PROGRESS"),
                "RESOLVED": sum(1 for t in tickets if t.get("status") in ("RESOLVED", "CLOSED")),
                "ALL": len(tickets),
            }

            tab_items = [
                ("MY_TASKS", "Việc của tôi", counts["MY_TASKS"]),
                ("UNASSIGNED", "Chờ tiếp nhận", counts["UNASSIGNED"]),
                ("URGENT", "Khẩn cấp", counts["URGENT"]),
                ("IN_PROGRESS", "Đang xử lý", counts["IN_PROGRESS"]),
                ("RESOLVED", "Đã giải quyết", counts["RESOLVED"]),
                ("ALL", "Tất cả sự cố", counts["ALL"]),
            ]

            with tabs_container:
                with ui.row().classes(
                    "w-full justify-between items-center bg-white p-1 rounded-xl border border-slate-200 shadow-2xs flex-wrap gap-1"
                ):
                    with ui.row().classes("items-center gap-1 flex-wrap"):
                        for key, label, count in tab_items:
                            is_selected = active_tab == key
                            tab_classes = (
                                "bg-slate-900 text-white font-bold shadow-xs"
                                if is_selected
                                else "text-slate-600 hover:text-slate-900 hover:bg-slate-100 font-medium"
                            )
                            pill_classes = (
                                "bg-slate-800 text-slate-100"
                                if is_selected
                                else "bg-slate-100 text-slate-600 font-semibold"
                            )

                            with (
                                ui.button(on_click=lambda k=key: set_active_tab(k))
                                .props("flat dense")
                                .classes(f"px-3.5 py-1.5 rounded-lg text-xs transition-all {tab_classes}")
                            ):
                                with ui.row().classes("items-center gap-2 no-wrap"):
                                    ui.label(label)
                                    ui.label(str(count)).classes(
                                        f"text-[10px] px-1.5 py-0.2 rounded-full {pill_classes}"
                                    )

                    with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 pr-3 hidden md:flex"):
                        ui.label(f"Tổng: {len(tickets)} sự cố").classes("text-[11px] font-medium")

        # =========================================================================
        # 6. ACTION WORKFLOW METHODS
        # =========================================================================
        async def handle_claim_ticket(ticket_id: int) -> None:
            try:
                await ticket_service.assign_ticket(ticket_id, int(user_id))
                await ticket_service.update_status(ticket_id, "IN_PROGRESS")
                toast.success(f"Bạn đã tiếp nhận và bắt đầu xử lý Ticket #{ticket_id}!")
                await load_tickets_data(refresh=True)
            except Exception as exc:
                toast.error(f"Không thể tiếp nhận ticket: {exc}")

        async def handle_update_status(ticket_id: int, next_status: str, note: str | None = None) -> None:
            try:
                if next_status == "CLOSED":
                    await ticket_service.close_ticket(ticket_id, note)
                else:
                    await ticket_service.update_status(ticket_id, next_status)
                toast.success(f"Đã cập nhật trạng thái sang {next_status}.")
                await load_tickets_data(refresh=True)
            except Exception as exc:
                toast.error(f"Lỗi: {exc}")

        def open_resolution_dialog(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    ui.label(f"Khắc phục sự cố #{ticket_id}").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                with ui.column().classes("w-full p-5 gap-3 text-xs"):
                    ui.label("Ghi chú giải pháp xử lý:").classes("font-semibold text-slate-700")
                    res_note = ui.textarea(
                        placeholder="Mô tả tóm tắt nguyên nhân lỗi và giải pháp khắc phục..."
                    ).props("outlined dense rows=3").classes("w-full text-xs")

                    async def confirm_resolution() -> None:
                        val = (res_note.value or "").strip()
                        dialog.close()
                        await handle_update_status(ticket_id, "RESOLVED", val or None)

                    with ui.row().classes("w-full justify-end gap-2 pt-2 border-t border-slate-100"):
                        ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg px-3")
                        ui.button("Xác nhận Khắc phục xong", on_click=confirm_resolution).props("unelevated color=positive size=sm").classes("rounded-lg font-bold px-4 h-9 shadow-2xs text-xs")

            dialog.open()

        def open_close_dialog(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    ui.label(f"Đóng & Hoàn tất sự cố #{ticket_id}").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                with ui.column().classes("w-full p-5 gap-3 text-xs"):
                    ui.label("Ghi chú bàn giao:").classes("font-semibold text-slate-700")
                    close_note = ui.textarea(
                        placeholder="Ghi chú hoàn tất xử lý và nghiệm thu..."
                    ).props("outlined dense rows=3").classes("w-full text-xs")

                    async def confirm_close() -> None:
                        val = (close_note.value or "").strip()
                        dialog.close()
                        await handle_update_status(ticket_id, "CLOSED", val or None)

                    with ui.row().classes("w-full justify-end gap-2 pt-2 border-t border-slate-100"):
                        ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg px-3")
                        ui.button("Xác nhận Đóng sự cố", on_click=confirm_close).props("unelevated color=slate-800 size=sm").classes("rounded-lg font-bold px-4 h-9 shadow-2xs text-xs")

            dialog.open()

        # =========================================================================
        # 7. RENDER LEFT QUEUE PANEL (Ticket Work Queue)
        # =========================================================================
        def render_left_pane() -> None:
            left_pane.clear()
            filtered = filter_tickets(state["raw_tickets"])

            with left_pane:
                # Queue Header + Search Box
                with ui.card().classes("w-full p-3 rounded-xl bg-white border border-slate-200 shadow-2xs gap-2"):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("CÔNG VIỆC").classes("text-xs font-bold text-slate-700 uppercase tracking-wider")
                        ui.label(f"{len(filtered)} ticket").classes("text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full")

                    search_box = (
                        ui.input(
                            placeholder="Tìm mã ticket hoặc tiêu đề...",
                            value=state["keyword"],
                            on_change=lambda e: on_search_changed(e.value),
                        )
                        .props("outlined dense clearable debounce=250")
                        .classes("w-full text-xs")
                    )
                    with search_box.add_slot("prepend"):
                        ui.icon("search", size="16px").classes("text-slate-400")

                # Ticket Cards List
                if not filtered:
                    with ui.card().classes("w-full p-6 bg-white border border-slate-200 rounded-xl text-center items-center gap-2 shadow-2xs"):
                        ui.label("Không có ticket trong danh sách này.").classes("text-xs font-bold text-slate-700")
                        if state["keyword"]:
                            ui.label("Không tìm thấy ticket phù hợp.").classes("text-[11px] text-slate-400")
                            ui.button("Xóa bộ lọc", on_click=lambda: on_search_changed("")).props("outline dense size=xs color=primary").classes("px-3 py-1")
                else:
                    with ui.column().classes("w-full gap-2 max-h-[calc(100vh-250px)] overflow-y-auto pr-1"):
                        for tck in filtered:
                            t_id = tck["id"]
                            is_selected = t_id == state["selected_ticket_id"]
                            priority = tck.get("priority", "MEDIUM")
                            status = tck.get("status", "OPEN")
                            category_text = CATEGORY_LABELS.get(tck.get("category", ""), "Sự cố kỹ thuật")

                            card_border = (
                                "border-l-4 border-l-blue-600 border-t border-r border-b border-blue-300 bg-blue-50/40 shadow-xs"
                                if is_selected
                                else "border border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/70 shadow-2xs"
                            )

                            async def select_this_ticket(target_id: int = t_id) -> None:
                                state["selected_ticket_id"] = target_id
                                await render_all()

                            with ui.card().classes(
                                f"w-full p-3 rounded-xl {card_border} cursor-pointer transition-all duration-150 gap-1.5"
                            ).on("click", select_this_ticket):
                                # Top Row: ID + Priority
                                with ui.row().classes("w-full justify-between items-center no-wrap"):
                                    ui.label(f"#TK-{t_id:04d}").classes("font-mono font-bold text-xs text-slate-900")
                                    priority_badge(priority)

                                # Title
                                ui.label(tck.get("title", "-")).classes("font-semibold text-slate-900 text-[13px] line-clamp-1 leading-snug")

                                # Subtext: Requester & Category
                                with ui.row().classes("items-center gap-1.5 text-[11px] text-slate-500 truncate"):
                                    ui.label(f"Người dùng #{tck.get('user_id')}")
                                    ui.label("·").classes("text-slate-300")
                                    ui.label(category_text).classes("truncate")

                                # Bottom Row: Status + Time
                                with ui.row().classes("w-full justify-between items-center pt-1 border-t border-slate-100/80 text-[10px] text-slate-400"):
                                    status_badge(status)
                                    ui.label(format_relative_time(tck.get("updated_at") or tck.get("created_at")))

        async def on_search_changed(val: str | None) -> None:
            state["keyword"] = val or ""
            filtered = filter_tickets(state["raw_tickets"])
            if filtered:
                if not any(t["id"] == state["selected_ticket_id"] for t in filtered):
                    state["selected_ticket_id"] = filtered[0]["id"]
            else:
                state["selected_ticket_id"] = None
            await render_all()

        # =========================================================================
        # 8. RENDER RIGHT DETAIL PANEL (Working Workspace & Live Chat)
        # =========================================================================
        async def render_right_pane() -> None:
            right_pane.clear()
            sel_id = state["selected_ticket_id"]

            if not sel_id:
                with right_pane:
                    with ui.card().classes("w-full p-12 bg-white border border-slate-200 rounded-xl shadow-2xs text-center items-center justify-center min-h-[460px] gap-2"):
                        ui.icon("assignment_turned_in", size="36px").classes("text-slate-300")
                        ui.label("Chọn một ticket để bắt đầu xử lý").classes("text-base font-bold text-slate-800")
                        ui.label("Chọn một yêu cầu bên trái để xem thông tin và thực hiện các thao tác kỹ thuật.").classes("text-xs text-slate-500 max-w-sm")
                return

            try:
                tck = await ticket_service.get_ticket(sel_id)
                dev = None
                if tck.get("device_id"):
                    try:
                        dev = await device_service.get_device(tck["device_id"])
                    except Exception:
                        dev = None
                history = await ticket_service.get_history(sel_id)
            except Exception as exc:
                with right_pane:
                    with ui.card().classes("w-full p-6 bg-white border border-slate-200 rounded-xl shadow-2xs text-center items-center gap-2"):
                        ui.label(f"Không thể tải thông tin ticket: {exc}").classes("text-xs text-red-600 font-semibold")
                        ui.button("Thử lại", on_click=lambda: render_right_pane()).props("outline dense size=sm color=primary").classes("px-3")
                return

            status = tck.get("status", "OPEN")
            priority = tck.get("priority", "MEDIUM")
            category_text = CATEGORY_LABELS.get(tck.get("category", ""), "Sự cố kỹ thuật")
            is_unassigned = not tck.get("technician_id")

            with right_pane:
                # 1. Main Detail Card
                with ui.card().classes("w-full p-5 rounded-xl bg-white border border-slate-200 shadow-2xs gap-3.5"):
                    # Top Header: Ticket ID, Badges & Open Full Page Link
                    with ui.row().classes("w-full justify-between items-center flex-wrap gap-2 pb-2.5 border-b border-slate-100"):
                        with ui.row().classes("items-center gap-2 flex-wrap"):
                            ui.label(f"#TK-{sel_id:04d}").classes("font-mono text-base font-bold text-slate-900")
                            priority_badge(priority)
                            status_badge(status)
                            ui.label(f"· {category_text}").classes("text-xs text-slate-500 font-medium")

                        ui.button(
                            "Mở trang chi tiết ↗",
                            on_click=lambda id=sel_id: ui.navigate.to(f"/tickets/{id}"),
                        ).props("flat color=slate-700 size=sm").classes("text-xs font-semibold")

                    # Title
                    ui.label(tck.get("title", "-")).classes("text-xl font-bold text-slate-900 leading-snug")

                    # Primary Technician Action Bar
                    with ui.row().classes("w-full justify-between items-center p-3 bg-slate-50 border border-slate-200/90 rounded-xl flex-wrap gap-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label("Thao tác kỹ thuật:").classes("font-bold text-slate-800 text-xs")

                        with ui.row().classes("items-center gap-2 flex-wrap"):
                            if is_unassigned or status == "OPEN":
                                ui.button(
                                    "Tiếp nhận sự cố",
                                    icon="bolt",
                                    on_click=lambda id=sel_id: handle_claim_ticket(id),
                                ).props("unelevated color=primary size=sm").classes("h-9 px-4 rounded-lg font-bold text-xs shadow-2xs")
                            elif status == "ASSIGNED":
                                ui.button(
                                    "Bắt đầu xử lý",
                                    icon="play_arrow",
                                    on_click=lambda id=sel_id: handle_update_status(id, "IN_PROGRESS"),
                                ).props("unelevated color=amber-700 size=sm").classes("h-9 px-4 rounded-lg font-bold text-xs text-white shadow-2xs")
                            elif status == "IN_PROGRESS":
                                ui.button(
                                    "Đánh dấu đã xử lý",
                                    icon="check_circle",
                                    on_click=lambda id=sel_id: open_resolution_dialog(id),
                                ).props("unelevated color=positive size=sm").classes("h-9 px-4 rounded-lg font-bold text-xs shadow-2xs")
                            elif status == "RESOLVED":
                                ui.button(
                                    "Hoàn tất & Đóng sự cố",
                                    icon="lock",
                                    on_click=lambda id=sel_id: open_close_dialog(id),
                                ).props("unelevated color=slate-800 size=sm").classes("h-9 px-4 rounded-lg font-bold text-xs shadow-2xs")
                            else:
                                ui.label("Sự cố đã được đóng hoàn tất.").classes("text-xs text-slate-500 italic")

                    # Structured Description Section
                    with ui.column().classes("w-full gap-1 pt-1"):
                        ui.label("MÔ TẢ SỰ CỐ").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")
                        with ui.element("div").classes("w-full p-3 rounded-lg bg-slate-50/70 border border-slate-200/80 text-xs text-slate-800 leading-relaxed whitespace-pre-wrap"):
                            ui.label(tck.get("description") or "Không có mô tả chi tiết.")

                    # Compact Information Grid
                    with ui.column().classes("w-full gap-1 pt-1"):
                        ui.label("THÔNG TIN LIÊN QUAN").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")
                        with ui.element("div").classes("w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 p-3 rounded-lg bg-slate-50/70 border border-slate-200/80 text-xs"):
                            # Item 1: Requester
                            with ui.column().classes("gap-0"):
                                ui.label("Người yêu cầu").classes("text-[10px] text-slate-400")
                                ui.label(f"User #{tck.get('user_id')}").classes("font-semibold text-slate-800")

                            # Item 2: Device
                            with ui.column().classes("gap-0"):
                                ui.label("Thiết bị").classes("text-[10px] text-slate-400")
                                if dev:
                                    ui.label(f"{dev.get('ma_thiet_bi')} - {dev.get('ten_thiet_bi')}").classes("font-semibold text-blue-700 truncate")
                                else:
                                    ui.label("Không liên kết").classes("text-slate-500 italic")

                            # Item 3: Location
                            with ui.column().classes("gap-0"):
                                ui.label("Vị trí thiết bị").classes("text-[10px] text-slate-400")
                                ui.label(dev.get("vi_tri") if dev else "Chưa có thông tin").classes("font-semibold text-slate-800 truncate")

                            # Item 4: Created At
                            with ui.column().classes("gap-0"):
                                ui.label("Thời gian tạo").classes("text-[10px] text-slate-400")
                                ui.label(format_datetime(tck.get("created_at"))).classes("font-medium text-slate-700")

                            # Item 5: Updated At
                            with ui.column().classes("gap-0"):
                                ui.label("Cập nhật gần nhất").classes("text-[10px] text-slate-400")
                                ui.label(format_datetime(tck.get("updated_at") or tck.get("created_at"))).classes("font-medium text-slate-700")

                            # Item 6: Category
                            with ui.column().classes("gap-0"):
                                ui.label("Phân loại").classes("text-[10px] text-slate-400")
                                ui.label(category_text).classes("font-medium text-slate-700")

                    # Activity Timeline
                    if history:
                        with ui.column().classes("w-full gap-1 pt-1 border-t border-slate-100"):
                            ui.label("LỊCH SỬ TIẾN TRÌNH").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")
                            with ui.column().classes("w-full gap-2 pl-2 py-1"):
                                for ev in history[-4:]:
                                    ev_time = format_datetime(ev.get("performed_at") or ev.get("created_at"))
                                    ev_action = ev.get("action") or "Cập nhật"
                                    ev_old = ev.get("old_status")
                                    ev_new = ev.get("new_status")
                                    status_info = f" ({ev_old} → {ev_new})" if ev_old and ev_new else ""

                                    with ui.row().classes("items-center gap-2 text-xs"):
                                        ui.element("div").classes("w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0")
                                        ui.label(ev_time).classes("text-[11px] text-slate-400 font-mono")
                                        ui.label(f"{ev_action}{status_info}").classes("text-slate-700 font-medium")

                # 2. Embedded Real-time Chat Thread
                comments_thread(sel_id, user, compact=False, max_height="280px")

        # =========================================================================
        # 9. DATA LOADER & RENDER ALL
        # =========================================================================
        async def render_all() -> None:
            render_tabs()
            render_left_pane()
            await render_right_pane()

        async def load_tickets_data(refresh: bool = False) -> None:
            state["is_loading"] = True
            state["error"] = None

            try:
                tickets = await ticket_service.list_tickets(refresh=refresh)
                state["raw_tickets"] = tickets
                state["is_loading"] = False

                filtered = filter_tickets(tickets)
                if filtered and not state["selected_ticket_id"]:
                    state["selected_ticket_id"] = filtered[0]["id"]
            except Exception as exc:
                state["error"] = str(exc)
                state["is_loading"] = False

            await render_all()

        ui.timer(0.05, lambda: load_tickets_data(refresh=True), once=True)

    app_shell("Bàn làm việc Kỹ thuật viên", content)
