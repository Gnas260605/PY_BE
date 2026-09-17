from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.comments_thread import comments_thread
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, truncate
from core.constants import CATEGORY_LABELS
from services.device_service import device_service
from services.ticket_service import ticket_service


def render_task_board_view() -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")

        # =========================================================================
        # 1. STATE MANAGEMENT
        # =========================================================================
        state: dict[str, Any] = {
            "raw_tickets": [],
            "devices_cache": {},
            "active_tab": "MY_TASKS",  # 'MY_TASKS' | 'UNASSIGNED' | 'URGENT' | 'IN_PROGRESS' | 'ALL'
            "view_mode": "TABLE",      # 'TABLE' | 'KANBAN'
            "keyword": "",
            "is_loading": True,
            "error": None,
            "page": 1,
            "page_size": 25,
        }

        # =========================================================================
        # 2. PAGE HEADER (Jira Service Management / Zendesk Standard)
        # =========================================================================
        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-2.5 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-medium"):
                    ui.label("Trang chủ")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Bàn làm việc KTV")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Tiếp nhận & Xử lý sự cố").classes("text-slate-900 font-semibold")

                ui.label("Bàn làm việc Kỹ thuật viên").classes("text-xl font-bold text-slate-900 tracking-tight")
                ui.label("Theo dõi hàng đợi sự cố, tiếp nhận và xử lý yêu cầu kỹ thuật tập trung.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                # View Mode Toggle (Table / Kanban)
                with ui.row().classes("items-center p-0.5 bg-slate-100 rounded-lg border border-slate-200"):
                    def switch_view(mode: str) -> None:
                        state["view_mode"] = mode
                        render_all()

                    btn_table = ui.button(
                        "Danh sách",
                        icon="view_list",
                        on_click=lambda: switch_view("TABLE"),
                    ).props("flat dense size=sm").classes("px-3 py-1 text-xs rounded-md")

                    btn_kanban = ui.button(
                        "Bảng Kanban",
                        icon="view_kanban",
                        on_click=lambda: switch_view("KANBAN"),
                    ).props("flat dense size=sm").classes("px-3 py-1 text-xs rounded-md")

                ui.button(
                    "Tra cứu thiết bị",
                    icon="search",
                    on_click=lambda: ui.navigate.to("/technician/devices"),
                ).props("outline color=slate-700 size=md").classes("h-[36px] rounded-lg font-medium px-3 text-xs bg-white")

                ui.button(icon="refresh", on_click=lambda: load_tickets_data(refresh=True)).props(
                    "outline dense color=slate-700 size=sm"
                ).classes("h-[36px] w-[36px] rounded-lg bg-white").tooltip("Tải lại danh sách")

        # Container for Real Data Summary Strip
        summary_container = ui.row().classes("w-full gap-2.5 mb-2.5 flex-wrap")

        # Container for Segmented Queue Tabs (JSM Queues)
        tabs_container = ui.row().classes("w-full mb-2.5")

        # Container for Search & Filter Bar
        with ui.card().classes("w-full p-2.5 rounded-lg bg-white border border-slate-200/90 shadow-2xs mb-2.5"):
            with ui.row().classes("w-full items-center gap-2 flex-wrap"):
                search_input = (
                    ui.input(
                        placeholder="Tìm theo mã sự cố, tiêu đề, mô tả, người gửi...",
                        on_change=lambda e: on_search_changed(e.value),
                    )
                    .props("outlined dense clearable debounce=300")
                    .classes("flex-1 min-w-[280px] text-xs")
                )
                with search_input.add_slot("prepend"):
                    ui.icon("search", size="16px").classes("text-slate-400")

                clear_filter_btn = (
                    ui.button("Xóa lọc", icon="close", on_click=lambda: clear_filters())
                    .props("flat dense color=slate-600 size=sm")
                    .classes("h-[38px] px-2.5 rounded-lg text-xs font-medium")
                )
                clear_filter_btn.set_visibility(False)

        # Container for Workspace Body (Table View or Kanban View)
        body_container = ui.column().classes("w-full gap-0")

        # =========================================================================
        # 3. FILTERING LOGIC
        # =========================================================================
        def filter_tickets(tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
            res = tickets
            tab = state["active_tab"]

            if tab == "MY_TASKS":
                # Assigned to this tech and not closed
                res = [t for t in res if t.get("technician_id") == user_id and t.get("status") != "CLOSED"]
            elif tab == "UNASSIGNED":
                # Not assigned to anyone or OPEN
                res = [t for t in res if not t.get("technician_id") or t.get("status") == "OPEN"]
            elif tab == "URGENT":
                # Urgent / High priority
                res = [t for t in res if t.get("priority") in ("URGENT", "HIGH") and t.get("status") != "CLOSED"]
            elif tab == "IN_PROGRESS":
                # Currently in progress
                res = [t for t in res if t.get("status") == "IN_PROGRESS"]
            elif tab == "RESOLVED":
                # Resolved / Closed
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

        def on_search_changed(val: str | None) -> None:
            state["keyword"] = val or ""
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def set_active_tab(tab_name: str) -> None:
            state["active_tab"] = tab_name
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def clear_filters() -> None:
            search_input.value = ""
            state["keyword"] = ""
            state["active_tab"] = "MY_TASKS"
            state["page"] = 1
            update_clear_button_visibility()
            render_all()

        def update_clear_button_visibility() -> None:
            is_active = bool(state["keyword"] or state["active_tab"] != "MY_TASKS")
            clear_filter_btn.set_visibility(is_active)

        # =========================================================================
        # 4. RENDER REAL DATA SUMMARY STRIP
        # =========================================================================
        def render_summary_strip() -> None:
            summary_container.clear()
            tickets = state["raw_tickets"]

            my_count = sum(1 for t in tickets if t.get("technician_id") == user_id and t.get("status") != "CLOSED")
            unassigned_count = sum(1 for t in tickets if not t.get("technician_id") or t.get("status") == "OPEN")
            urgent_count = sum(1 for t in tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") != "CLOSED")
            in_prog_count = sum(1 for t in tickets if t.get("status") == "IN_PROGRESS")

            cards = [
                ("VIỆC CỦA TÔI", my_count, "assignment_ind", "blue", "Sự cố đang phụ trách"),
                ("CHỜ TIẾP NHẬN", unassigned_count, "inbox", "amber", "Cần KTV nhận việc"),
                ("SỰ CỐ KHẨN CẤP", urgent_count, "bolt", "rose" if urgent_count > 0 else "slate", "Ưu tiên xử lý ngay"),
                ("ĐANG XỬ LÝ TOÀN HT", in_prog_count, "engineering", "purple", "Tiến trình kỹ thuật"),
            ]

            with summary_container:
                for label, count, icon_name, color, hint in cards:
                    bg_badge = {
                        "blue": "bg-blue-50 text-blue-700",
                        "amber": "bg-amber-50 text-amber-700",
                        "rose": "bg-rose-50 text-rose-700",
                        "purple": "bg-purple-50 text-purple-700",
                        "slate": "bg-slate-100 text-slate-700",
                    }.get(color, "bg-slate-100 text-slate-700")

                    with ui.card().classes(
                        "flex-1 min-w-[160px] p-2.5 rounded-lg bg-white border border-slate-200/90 shadow-2xs flex flex-col justify-between"
                    ):
                        with ui.row().classes("w-full justify-between items-center no-wrap"):
                            ui.label(label).classes("text-[11px] font-semibold text-slate-500 uppercase tracking-tight")
                            with ui.row().classes(f"w-6 h-6 rounded-md items-center justify-center {bg_badge}"):
                                ui.icon(icon_name, size="14px")

                        with ui.row().classes("items-baseline gap-1.5 mt-1"):
                            ui.label(str(count)).classes("text-xl font-bold text-slate-900 tracking-tight")
                            ui.label(hint).classes("text-[10px] text-slate-400 truncate")

        # =========================================================================
        # 5. RENDER QUEUE TABS (Segmented Control)
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
                ("URGENT", "Khẩn cấp (P1/P2)", counts["URGENT"]),
                ("IN_PROGRESS", "Đang xử lý", counts["IN_PROGRESS"]),
                ("RESOLVED", "Đã giải quyết", counts["RESOLVED"]),
                ("ALL", "Tất cả sự cố", counts["ALL"]),
            ]

            with tabs_container:
                with ui.row().classes(
                    "w-full justify-between items-center bg-white p-1 rounded-lg border border-slate-200/90 shadow-2xs flex-wrap gap-2"
                ):
                    with ui.row().classes("items-center gap-1 flex-wrap"):
                        for key, label, count in tab_items:
                            is_selected = active_tab == key
                            tab_classes = (
                                "bg-slate-900 text-white font-medium shadow-xs"
                                if is_selected
                                else "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                            )
                            pill_classes = (
                                "bg-slate-800 text-slate-100"
                                if is_selected
                                else "bg-slate-100 text-slate-600 font-semibold"
                            )

                            with (
                                ui.button(on_click=lambda k=key: set_active_tab(k))
                                .props("flat dense")
                                .classes(f"px-3 py-1 rounded-md text-xs transition-all {tab_classes}")
                            ):
                                with ui.row().classes("items-center gap-1.5 no-wrap"):
                                    ui.label(label)
                                    ui.label(str(count)).classes(
                                        f"text-[10px] px-1.5 py-0.2 rounded-full {pill_classes}"
                                    )

                    with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 pr-2 hidden sm:flex"):
                        ui.icon("task_alt", size="14px").classes("text-emerald-600")
                        ui.label(f"Hàng đợi: {len(tickets)} sự cố").classes("text-[11px] font-medium")

        # =========================================================================
        # 6. ACTION WORKFLOW METHODS
        # =========================================================================
        async def handle_claim_ticket(ticket_id: int) -> None:
            try:
                await ticket_service.assign_ticket(ticket_id, int(user_id))
                await ticket_service.update_status(ticket_id, "IN_PROGRESS")
                toast.success(f"Bạn đã nhận và bắt đầu xử lý Ticket #{ticket_id}!")
                await load_tickets_data(refresh=True)
            except Exception as exc:
                toast.error(f"Không thể nhận ticket: {exc}")

        async def handle_update_status(ticket_id: int, next_status: str, note: str | None = None) -> None:
            try:
                if next_status == "CLOSED":
                    await ticket_service.close_ticket(ticket_id, note)
                else:
                    await ticket_service.update_status(ticket_id, next_status)
                toast.success(f"Đã cập nhật Ticket #{ticket_id} sang {next_status}.")
                await load_tickets_data(refresh=True)
            except Exception as exc:
                toast.error(f"Lỗi: {exc}")

        def open_resolution_dialog(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle", size="18px").classes("text-emerald-600")
                        ui.label(f"Khắc phục sự cố #{ticket_id}").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                with ui.column().classes("w-full p-5 gap-3 text-xs"):
                    ui.label("Ghi lại giải pháp xử lý hoặc kết quả khắc phục:").classes("font-semibold text-slate-700")
                    solution_input = ui.textarea(
                        placeholder="Ví dụ: Đã thay thế cáp mạng RJ45, máy tính đã nhận IP và truy cập internet bình thường...",
                    ).props("outlined dense rows=3").classes("w-full")

                with ui.row().classes("w-full justify-end items-center gap-2 p-4 bg-slate-50 border-t border-slate-200"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg px-3")

                    async def confirm_resolve() -> None:
                        note = (solution_input.value or "").strip()
                        dialog.close()
                        if note:
                            try:
                                await ticket_service.create_comment(ticket_id, f"[Giải pháp] {note}")
                            except Exception:
                                pass
                        await handle_update_status(ticket_id, "RESOLVED")

                    ui.button("Xác nhận hoàn tất", icon="check", on_click=confirm_resolve).props(
                        "unelevated color=positive size=sm"
                    ).classes("rounded-lg px-3.5 font-medium")

            dialog.open()

        def open_close_dialog(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("lock", size="18px").classes("text-slate-700")
                        ui.label(f"Đóng Ticket & Bàn giao #{ticket_id}").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                with ui.column().classes("w-full p-5 gap-3 text-xs"):
                    ui.label("Ghi chú bàn giao hoàn tất (tùy chọn):").classes("font-semibold text-slate-700")
                    close_note = ui.textarea(
                        placeholder="Ghi chú bàn giao nghiệm thu lại cho người dùng...",
                    ).props("outlined dense rows=3").classes("w-full")

                with ui.row().classes("w-full justify-end items-center gap-2 p-4 bg-slate-50 border-t border-slate-200"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg px-3")

                    async def confirm_close() -> None:
                        note = (close_note.value or "").strip() or None
                        dialog.close()
                        await handle_update_status(ticket_id, "CLOSED", note)

                    ui.button("Đóng sự cố", icon="lock", on_click=confirm_close).props(
                        "unelevated color=slate-800 size=sm"
                    ).classes("rounded-lg px-3.5 font-medium")

            dialog.open()

        # =========================================================================
        # 7. FAST SIDE DRAWER (View Ticket Details & Fast Action)
        # =========================================================================
        async def show_ticket_drawer(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-lg rounded-xl p-0 bg-white border border-slate-200 shadow-2xl overflow-hidden"):
                # Header
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.label(f"#TK-{ticket_id:04d}").classes("font-mono text-sm font-bold text-slate-900")
                        ui.label("Chi tiết sự cố & Bàn làm việc").classes("text-xs text-slate-500")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                # Body
                with ui.column().classes("w-full p-5 gap-3.5 text-xs max-h-[75vh] overflow-y-auto"):
                    try:
                        tck = await ticket_service.get_ticket(ticket_id)
                        dev = None
                        if tck.get("device_id"):
                            try:
                                dev = await device_service.get_device(tck["device_id"])
                            except Exception:
                                dev = None
                    except Exception as exc:
                        ui.label(f"Lỗi tải dữ liệu: {exc}").classes("text-red-600")
                        return

                    status = tck.get("status", "OPEN")
                    priority = tck.get("priority", "MEDIUM")
                    category = tck.get("category", "INCIDENT")
                    is_unassigned = not tck.get("technician_id")

                    # Title & Badges
                    with ui.column().classes("w-full gap-1 pb-2.5 border-b border-slate-100"):
                        with ui.row().classes("items-center gap-2 flex-wrap"):
                            priority_badge(priority)
                            status_badge(status)
                            ui.label(CATEGORY_LABELS.get(category, category)).classes("text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200")

                        ui.label(tck.get("title", "-")).classes("text-base font-bold text-slate-900 leading-snug mt-1")

                    # 1-Click Action Bar inside Drawer
                    with ui.row().classes("w-full justify-between items-center p-2.5 bg-blue-50/70 border border-blue-200/80 rounded-lg"):
                        with ui.row().classes("items-center gap-1.5"):
                            ui.icon("bolt", size="16px").classes("text-blue-700")
                            ui.label("Thao tác kỹ thuật:").classes("font-bold text-blue-900 text-xs")

                        if is_unassigned or status == "OPEN":
                            ui.button(
                                "⚡ Nhận xử lý ngay",
                                on_click=lambda: (dialog.close(), handle_claim_ticket(ticket_id)),
                            ).props("unelevated color=primary size=sm").classes("rounded font-bold text-xs")
                        elif status == "ASSIGNED":
                            ui.button(
                                "▶ Bắt đầu xử lý",
                                on_click=lambda: (dialog.close(), handle_update_status(ticket_id, "IN_PROGRESS")),
                            ).props("unelevated color=amber-700 size=sm").classes("rounded font-bold text-xs text-white")
                        elif status == "IN_PROGRESS":
                            ui.button(
                                "✅ Đã khắc phục xong",
                                on_click=lambda: (dialog.close(), open_resolution_dialog(ticket_id)),
                            ).props("unelevated color=positive size=sm").classes("rounded font-bold text-xs")
                        elif status == "RESOLVED":
                            ui.button(
                                "🔒 Đóng & Bàn giao",
                                on_click=lambda: (dialog.close(), open_close_dialog(ticket_id)),
                            ).props("unelevated color=slate-800 size=sm").classes("rounded font-bold text-xs")

                    # Description
                    with ui.card().classes("w-full p-3 rounded-lg bg-slate-50 border border-slate-200/80 gap-1"):
                        ui.label("MÔ TẢ SỰ CỐ").classes("text-[10px] font-bold text-slate-500 uppercase tracking-wider")
                        ui.label(tck.get("description") or "Không có mô tả chi tiết.").classes("text-xs text-slate-800 leading-relaxed")

                    # Device & Requester Info
                    with ui.row().classes("w-full gap-2.5"):
                        with ui.card().classes("flex-1 p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 gap-0.5"):
                            ui.label("NGƯỜI YÊU CẦU").classes("text-[10px] font-bold text-slate-500 uppercase tracking-wider")
                            ui.label(f"User #{tck.get('user_id')}").classes("font-bold text-slate-900 text-xs")
                            ui.label(format_datetime(tck.get("created_at"))).classes("text-[10px] text-slate-400")

                        with ui.card().classes("flex-1 p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 gap-0.5"):
                            ui.label("THIẾT BỊ").classes("text-[10px] font-bold text-slate-500 uppercase tracking-wider")
                            if dev:
                                ui.label(f"{dev.get('ma_thiet_bi')} - {dev.get('ten_thiet_bi')}").classes("font-bold text-blue-700 text-xs truncate")
                                ui.label(dev.get("vi_tri") or "Vị trí máy").classes("text-[10px] text-slate-500 truncate")
                            else:
                                ui.label("Không liên kết").classes("text-xs text-slate-400 italic")

                    # Comments / Notes Thread
                    comments_thread(ticket_id, user, compact=True, max_height="220px")

                # Footer
                with ui.row().classes("w-full justify-between items-center p-3.5 bg-slate-50 border-t border-slate-200"):
                    ui.button(
                        "Mở trang chi tiết đầy đủ ↗",
                        on_click=lambda: (dialog.close(), ui.navigate.to(f"/tickets/{ticket_id}")),
                    ).props("flat color=slate-700 size=sm").classes("text-xs")

                    ui.button("Đóng", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded")

            dialog.open()

        # =========================================================================
        # 8. RENDER TABLE VIEW (ENTERPRISE QUEUE)
        # =========================================================================
        def render_table_view() -> None:
            filtered = filter_tickets(state["raw_tickets"])

            if not filtered:
                with body_container:
                    with ui.card().classes("w-full p-8 bg-white border border-slate-200/90 rounded-lg shadow-2xs"):
                        empty_state(
                            title="Không có sự cố nào trong hàng đợi",
                            subtitle="Không có ticket nào khớp với bộ lọc hiện tại.",
                            icon="assignment_turned_in",
                            action_label="Xóa bộ lọc",
                            on_action=clear_filters,
                        )
                return

            total_items = len(filtered)
            page_size = state["page_size"]
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            if state["page"] > total_pages:
                state["page"] = total_pages

            start_idx = (state["page"] - 1) * page_size
            end_idx = min(start_idx + page_size, total_items)
            paged_tickets = filtered[start_idx:end_idx]

            with body_container:
                with ui.card().classes("w-full p-0 rounded-lg bg-white border border-slate-200/90 shadow-2xs overflow-hidden"):
                    # Table Header
                    with ui.row().classes("w-full px-4 py-2.5 bg-slate-50/90 border-b border-slate-200/80 items-center text-[11px] font-semibold text-slate-600 uppercase tracking-wider no-wrap gap-2"):
                        ui.label("MÃ & ƯU TIÊN").classes("w-32 shrink-0")
                        ui.label("SỰ CỐ & NỘI DUNG").classes("flex-1 min-w-[220px]")
                        ui.label("THIẾT BỊ & VỊ TRÍ").classes("w-44 shrink-0")
                        ui.label("CẬP NHẬT").classes("w-32 shrink-0")
                        ui.label("TRẠNG THÁI").classes("w-36 shrink-0")
                        ui.label("THAO TÁC NHANH").classes("w-44 shrink-0 text-right")

                    # Table Rows
                    with ui.column().classes("w-full divide-y divide-slate-100 gap-0"):
                        for tck in paged_tickets:
                            render_ticket_row(tck)

                    # Pagination Footer
                    with ui.row().classes("w-full justify-between items-center px-4 py-2 bg-slate-50/50 border-t border-slate-200/80 text-xs text-slate-600 flex-wrap gap-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(f"Hiển thị {start_idx + 1}–{end_idx} trong số {total_items} sự cố").classes("font-medium text-slate-700")

                            def on_page_size_change(val: int) -> None:
                                state["page_size"] = val
                                state["page"] = 1
                                render_all()

                            ui.select(
                                [10, 25, 50, 100],
                                value=state["page_size"],
                                on_change=lambda e: on_page_size_change(e.value),
                            ).props("outlined dense options-dense").classes("w-20 text-xs")

                        with ui.row().classes("items-center gap-1"):
                            def go_prev() -> None:
                                if state["page"] > 1:
                                    state["page"] -= 1
                                    render_all()

                            def go_next() -> None:
                                if state["page"] < total_pages:
                                    state["page"] += 1
                                    render_all()

                            prev_btn = ui.button(icon="chevron_left", on_click=go_prev).props("flat dense size=sm").classes("h-7 w-7 rounded")
                            if state["page"] <= 1:
                                prev_btn.props("disable")

                            ui.label(f"Trang {state['page']} / {total_pages}").classes("px-2 font-medium text-slate-700 text-xs")

                            next_btn = ui.button(icon="chevron_right", on_click=go_next).props("flat dense size=sm").classes("h-7 w-7 rounded")
                            if state["page"] >= total_pages:
                                next_btn.props("disable")

        def render_ticket_row(tck: dict[str, Any]) -> None:
            tck_id = tck["id"]
            priority = tck.get("priority", "MEDIUM")
            status = tck.get("status", "OPEN")
            is_unassigned = not tck.get("technician_id")
            is_my_ticket = tck.get("technician_id") == user_id

            # Priority border accent
            border_accent = {
                "URGENT": "border-l-4 border-l-rose-500 bg-rose-50/15",
                "HIGH": "border-l-4 border-l-amber-500 bg-amber-50/10",
                "MEDIUM": "border-l-2 border-l-blue-400",
                "LOW": "border-l-2 border-l-slate-200",
            }.get(priority, "border-l-2 border-l-slate-200")

            with ui.row().classes(
                f"w-full px-4 py-2.5 items-center justify-between hover:bg-slate-50/80 transition-colors duration-150 text-xs no-wrap gap-2 {border_accent}"
            ):
                # 1. ID & Priority
                with ui.column().classes("w-32 shrink-0 gap-1 items-start"):
                    with ui.row().classes("items-center gap-1.5"):
                        ui.label(f"#TK-{tck_id:04d}").classes("font-mono text-xs font-bold text-slate-900")
                        if is_my_ticket:
                            ui.label("Của tôi").classes("text-[9px] font-bold text-primary px-1 py-0.2 bg-blue-50 border border-blue-200 rounded")
                    priority_badge(priority)

                # 2. Title & Description
                with ui.column().classes("flex-1 min-w-[220px] gap-0.5 cursor-pointer").on("click", lambda tck_id=tck_id: show_ticket_drawer(tck_id)):
                    ui.label(tck.get("title", "-")).classes("font-semibold text-slate-900 text-[13px] truncate hover:text-primary leading-snug")
                    if tck.get("description"):
                        ui.label(truncate(tck["description"], 80)).classes("text-[11px] text-slate-500 truncate")

                # 3. Device & Location
                with ui.column().classes("w-44 shrink-0 gap-0 text-slate-600 text-[11px]"):
                    if tck.get("device_id"):
                        with ui.row().classes("items-center gap-1 no-wrap"):
                            ui.icon("laptop_mac", size="12px").classes("text-blue-500")
                            ui.label(f"Thiết bị #{tck.get('device_id')}").classes("font-semibold text-slate-700 truncate")
                    else:
                        ui.label("-").classes("text-slate-400")

                # 4. Updated Date
                with ui.column().classes("w-32 shrink-0 gap-0 text-slate-500 text-[11px]"):
                    ui.label(format_datetime(tck.get("updated_at") or tck.get("created_at"))).classes("truncate")

                # 5. Status
                with ui.row().classes("w-36 shrink-0 items-center no-wrap"):
                    status_badge(status)

                # 6. Fast 1-Click Action Button
                with ui.row().classes("w-44 shrink-0 justify-end items-center gap-1.5"):
                    if is_unassigned or status == "OPEN":
                        ui.button(
                            "⚡ Nhận việc",
                            on_click=lambda tck_id=tck_id: handle_claim_ticket(tck_id),
                        ).props("unelevated dense size=xs color=primary").classes("rounded-lg px-2.5 font-bold shadow-2xs text-[11px]")
                    elif status == "ASSIGNED":
                        ui.button(
                            "▶ Bắt đầu xử lý",
                            on_click=lambda tck_id=tck_id: handle_update_status(tck_id, "IN_PROGRESS"),
                        ).props("unelevated dense size=xs color=amber-700").classes("rounded-lg px-2.5 font-bold text-white shadow-2xs text-[11px]")
                    elif status == "IN_PROGRESS":
                        ui.button(
                            "✅ Khắc phục xong",
                            on_click=lambda tck_id=tck_id: open_resolution_dialog(tck_id),
                        ).props("unelevated dense size=xs color=positive").classes("rounded-lg px-2.5 font-bold shadow-2xs text-[11px]")
                    elif status == "RESOLVED":
                        ui.button(
                            "🔒 Đóng sự cố",
                            on_click=lambda tck_id=tck_id: open_close_dialog(tck_id),
                        ).props("unelevated dense size=xs color=slate-800").classes("rounded-lg px-2.5 font-bold shadow-2xs text-[11px]")

                    ui.button(
                        icon="visibility",
                        on_click=lambda tck_id=tck_id: show_ticket_drawer(tck_id),
                    ).props("flat dense round size=xs color=slate-600").tooltip("Xem chi tiết & Ghi chú")

        # =========================================================================
        # 9. RENDER KANBAN VIEW
        # =========================================================================
        def render_kanban_view() -> None:
            filtered = filter_tickets(state["raw_tickets"])

            open_list = [t for t in filtered if t.get("status") in ("OPEN", "ASSIGNED")]
            progress_list = [t for t in filtered if t.get("status") == "IN_PROGRESS"]
            resolved_list = [t for t in filtered if t.get("status") == "RESOLVED"]
            closed_list = [t for t in filtered if t.get("status") == "CLOSED"]

            columns = [
                ("CHỜ TIẾP NHẬN", open_list, "border-t-4 border-t-blue-600", "inbox"),
                ("ĐANG XỬ LÝ", progress_list, "border-t-4 border-t-amber-500", "engineering"),
                ("ĐÃ KHẮC PHỤC", resolved_list, "border-t-4 border-t-emerald-500", "check_circle"),
                ("ĐÃ ĐÓNG", closed_list, "border-t-4 border-t-slate-400", "lock"),
            ]

            with body_container:
                with ui.row().classes("w-full gap-3 items-start flex-nowrap overflow-x-auto pb-4"):
                    for col_title, ticket_sublist, border_cls, col_icon in columns:
                        with ui.column().classes(f"min-w-[280px] w-72 bg-slate-100/90 p-2.5 rounded-lg border border-slate-200 {border_cls} gap-2.5 flex-shrink-0"):
                            with ui.row().classes("w-full justify-between items-center px-1 pb-1"):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon(col_icon, size="16px").classes("text-slate-600")
                                    ui.label(col_title).classes("text-xs font-bold text-slate-800 uppercase tracking-wider")
                                ui.label(str(len(ticket_sublist))).classes("text-[11px] font-bold px-2 py-0.2 bg-white rounded-full text-slate-700 border border-slate-200 shadow-2xs")

                            if not ticket_sublist:
                                with ui.column().classes("w-full py-8 items-center justify-center text-slate-400 gap-1"):
                                    ui.icon("inbox", size="24px").classes("text-slate-300")
                                    ui.label("Không có sự cố nào").classes("text-[11px] font-medium")
                            else:
                                for tck in ticket_sublist:
                                    render_kanban_card(tck)

        def render_kanban_card(tck: dict[str, Any]) -> None:
            tck_id = tck["id"]
            cur_status = tck.get("status")
            priority = tck.get("priority", "MEDIUM")
            is_unassigned = not tck.get("technician_id")

            with ui.card().classes("w-full p-3 rounded-lg bg-white border border-slate-200/90 shadow-2xs gap-2 relative hover:shadow-xs transition-shadow"):
                with ui.row().classes("w-full justify-between items-center no-wrap"):
                    ui.label(f"#TK-{tck_id:04d}").classes("text-xs font-mono font-bold text-blue-700")
                    priority_badge(priority)

                ui.label(tck.get("title", "-")).classes("text-xs font-bold text-slate-900 line-clamp-2 leading-snug cursor-pointer hover:text-primary").on(
                    "click", lambda tck_id=tck_id: show_ticket_drawer(tck_id)
                )

                if tck.get("device_id"):
                    with ui.row().classes("items-center gap-1 text-[10px] text-slate-500 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-100"):
                        ui.icon("laptop_mac", size="11px").classes("text-blue-500")
                        ui.label(f"Thiết bị #{tck.get('device_id')}")

                # Quick Action Button
                if cur_status == "OPEN" and is_unassigned:
                    ui.button(
                        "⚡ Nhận việc",
                        on_click=lambda tck_id=tck_id: handle_claim_ticket(tck_id),
                    ).props("unelevated dense size=xs color=primary").classes("w-full font-semibold py-1 rounded text-xs")
                elif cur_status in ("OPEN", "ASSIGNED"):
                    ui.button(
                        "▶ Bắt đầu xử lý",
                        on_click=lambda tck_id=tck_id: handle_update_status(tck_id, "IN_PROGRESS"),
                    ).props("unelevated dense size=xs color=amber-700").classes("w-full font-semibold py-1 rounded text-white text-xs")
                elif cur_status == "IN_PROGRESS":
                    ui.button(
                        "✅ Khắc phục xong",
                        on_click=lambda tck_id=tck_id: open_resolution_dialog(tck_id),
                    ).props("unelevated dense size=xs color=positive").classes("w-full font-semibold py-1 rounded text-xs")
                elif cur_status == "RESOLVED":
                    ui.button(
                        "🔒 Đóng sự cố",
                        on_click=lambda tck_id=tck_id: open_close_dialog(tck_id),
                    ).props("unelevated dense size=xs color=slate-800").classes("w-full font-semibold py-1 rounded text-xs")

        # =========================================================================
        # 10. DATA LOADER & RENDER ALL
        # =========================================================================
        def render_all() -> None:
            btn_table.props("unelevated color=white text-color=primary shadow-2xs" if state["view_mode"] == "TABLE" else "flat color=slate-600")
            btn_kanban.props("unelevated color=white text-color=primary shadow-2xs" if state["view_mode"] == "KANBAN" else "flat color=slate-600")

            render_summary_strip()
            render_tabs()
            body_container.clear()
            if state["view_mode"] == "TABLE":
                render_table_view()
            else:
                render_kanban_view()

        async def load_tickets_data(refresh: bool = False) -> None:
            state["is_loading"] = True
            state["error"] = None

            try:
                tickets = await ticket_service.list_tickets(refresh=refresh)
                state["raw_tickets"] = tickets
                state["is_loading"] = False
            except Exception as exc:
                state["error"] = str(exc)
                state["is_loading"] = False

            render_all()

        ui.timer(0.05, lambda: load_tickets_data(refresh=True), once=True)

    app_shell("Bàn làm việc Kỹ thuật viên", content)
