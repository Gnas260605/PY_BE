from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
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
            "selected_ticket_id": None,
            "selected_ticket_detail": None,
            "selected_device_detail": None,
            "selected_comments": [],
            "view_mode": "SPLIT",  # 'SPLIT' | 'KANBAN'
            "scope": "MY_TASKS",   # 'MY_TASKS' | 'UNASSIGNED' | 'URGENT' | 'ALL'
            "keyword": "",
            "is_loading": True,
            "is_loading_detail": False,
            "error": None,
        }

        # =========================================================================
        # 2. PAGE HEADER (Technician Incident Workspace)
        # =========================================================================
        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-2.5 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-medium"):
                    ui.label("Trang chủ")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Bàn làm việc")
                    ui.icon("chevron_right", size="12px").classes("text-slate-400")
                    ui.label("Tiếp nhận & Xử lý sự cố").classes("text-slate-900 font-semibold")

                ui.label("Bàn làm việc Kỹ thuật viên").classes("text-xl font-bold text-slate-900 tracking-tight")
                ui.label("Không gian tiếp nhận, điều phối và xử lý sự cố kỹ thuật tập trung.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                # View Mode Toggle Buttons
                with ui.row().classes("items-center p-0.5 bg-slate-100 rounded-lg border border-slate-200"):
                    def switch_view(mode: str) -> None:
                        state["view_mode"] = mode
                        render_all()

                    btn_split = ui.button(
                        "Danh sách tập trung",
                        icon="splitscreen",
                        on_click=lambda: switch_view("SPLIT"),
                    ).props("flat dense size=sm").classes("px-2.5 py-1 text-xs rounded-md")

                    btn_kanban = ui.button(
                        "Bảng Kanban",
                        icon="view_kanban",
                        on_click=lambda: switch_view("KANBAN"),
                    ).props("flat dense size=sm").classes("px-2.5 py-1 text-xs rounded-md")

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

        # Container for Workspace Main Body (Split View or Kanban)
        main_workspace_container = ui.column().classes("w-full gap-0")

        # =========================================================================
        # 3. DATA FILTERING LOGIC
        # =========================================================================
        def filter_tickets(tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
            res = tickets
            scope = state["scope"]

            if scope == "MY_TASKS":
                # Assigned to this tech OR unassigned
                res = [t for t in res if t.get("technician_id") == user_id or (t.get("status") == "OPEN" and not t.get("technician_id"))]
            elif scope == "UNASSIGNED":
                res = [t for t in res if not t.get("technician_id") or t.get("status") == "OPEN"]
            elif scope == "URGENT":
                res = [t for t in res if t.get("priority") in ("URGENT", "HIGH")]

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

        # =========================================================================
        # 4. RENDER REAL DATA SUMMARY STRIP
        # =========================================================================
        def render_summary_strip() -> None:
            summary_container.clear()
            tickets = state["raw_tickets"]

            open_count = sum(1 for t in tickets if not t.get("technician_id") or t.get("status") == "OPEN")
            my_progress_count = sum(1 for t in tickets if t.get("technician_id") == user_id and t.get("status") == "IN_PROGRESS")
            urgent_count = sum(1 for t in tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("RESOLVED", "CLOSED"))
            resolved_count = sum(1 for t in tickets if t.get("status") in ("RESOLVED", "CLOSED"))

            cards = [
                ("CHỜ TIẾP NHẬN", open_count, "inbox", "blue", "Sự cố cần nhận việc"),
                ("ĐANG XỬ LÝ", my_progress_count, "engineering", "amber", "Việc của tôi đang làm"),
                ("SỰ CỐ KHẨN CẤP", urgent_count, "bolt", "rose" if urgent_count > 0 else "slate", "Ưu tiên giải quyết ngay"),
                ("ĐÃ HOÀN TẤT / ĐÓNG", resolved_count, "check_circle", "emerald", "Đã khắc phục xong"),
            ]

            with summary_container:
                for label, count, icon_name, color, hint in cards:
                    bg_badge = {
                        "blue": "bg-blue-50 text-blue-700",
                        "amber": "bg-amber-50 text-amber-700",
                        "rose": "bg-rose-50 text-rose-700",
                        "emerald": "bg-emerald-50 text-emerald-700",
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
        # 5. ACTIONS: CLAIM, STATUS TRANSITION, RESOLUTION
        # =========================================================================
        async def handle_claim_ticket(ticket_id: int) -> None:
            try:
                await ticket_service.assign_ticket(ticket_id, int(user_id))
                await ticket_service.update_status(ticket_id, "IN_PROGRESS")
                toast.success(f"Bạn đã nhận và bắt đầu xử lý Ticket #{ticket_id}!")
                await load_tickets_data(refresh=True)
                await select_ticket(ticket_id)
            except Exception as exc:
                toast.error(f"Không thể nhận ticket: {exc}")

        async def handle_advance_status(ticket_id: int, next_status: str, note: str | None = None) -> None:
            try:
                if next_status == "CLOSED":
                    await ticket_service.close_ticket(ticket_id, note)
                else:
                    await ticket_service.update_status(ticket_id, next_status)
                toast.success(f"Đã chuyển trạng thái Ticket #{ticket_id} sang {next_status} thành công.")
                await load_tickets_data(refresh=True)
                await select_ticket(ticket_id)
            except Exception as exc:
                toast.error(f"Lỗi: {exc}")

        def open_resolution_modal(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle", size="18px").classes("text-emerald-600")
                        ui.label(f"Hoàn tất xử lý Ticket #{ticket_id}").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                with ui.column().classes("w-full p-5 gap-3 text-xs"):
                    ui.label("Ghi lại kết quả khắc phục hoặc giải pháp kỹ thuật đã áp dụng:").classes("font-semibold text-slate-700")
                    solution_input = ui.textarea(
                        placeholder="Ví dụ: Đã thay dây nguồn máy tính, kiểm tra cổng mạng LAN kết nối bình thường...",
                    ).props("outlined dense rows=3").classes("w-full")

                with ui.row().classes("w-full justify-end items-center gap-2 p-4 bg-slate-50 border-t border-slate-200"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg px-3")

                    async def confirm_resolve() -> None:
                        note = (solution_input.value or "").strip() or None
                        dialog.close()
                        if note:
                            try:
                                await ticket_service.create_comment(ticket_id, f"[Giải pháp khắc phục] {note}")
                            except Exception:
                                pass
                        await handle_advance_status(ticket_id, "RESOLVED")

                    ui.button("Xác nhận hoàn tất", icon="check", on_click=confirm_resolve).props(
                        "unelevated color=positive size=sm"
                    ).classes("rounded-lg px-3.5 font-medium")

            dialog.open()

        def open_close_ticket_modal(ticket_id: int) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-xl p-0 bg-white border border-slate-200 shadow-xl overflow-hidden"):
                with ui.row().classes("w-full justify-between items-center px-5 py-3.5 bg-slate-50 border-b border-slate-200"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("lock", size="18px").classes("text-slate-700")
                        ui.label(f"Đóng sự cố & Bàn giao #{ticket_id}").classes("text-sm font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat dense round size=xs color=slate-500")

                with ui.column().classes("w-full p-5 gap-3 text-xs"):
                    ui.label("Ghi chú đóng sự cố (tùy chọn):").classes("font-semibold text-slate-700")
                    close_note_input = ui.textarea(
                        placeholder="Ghi chú bàn giao lại cho người dùng...",
                    ).props("outlined dense rows=3").classes("w-full")

                with ui.row().classes("w-full justify-end items-center gap-2 p-4 bg-slate-50 border-t border-slate-200"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=sm").classes("rounded-lg px-3")

                    async def confirm_close() -> None:
                        note = (close_note_input.value or "").strip() or None
                        dialog.close()
                        await handle_advance_status(ticket_id, "CLOSED", note)

                    ui.button("Đóng Ticket", icon="lock", on_click=confirm_close).props(
                        "unelevated color=slate-800 size=sm"
                    ).classes("rounded-lg px-3.5 font-medium")

            dialog.open()

        # =========================================================================
        # 6. SELECT TICKET & LOAD DETAIL
        # =========================================================================
        async def select_ticket(ticket_id: int) -> None:
            state["selected_ticket_id"] = ticket_id
            state["is_loading_detail"] = True
            render_all()

            try:
                ticket_data = await ticket_service.get_ticket(ticket_id)
                state["selected_ticket_detail"] = ticket_data

                # Load device info if linked
                device_id = ticket_data.get("device_id")
                if device_id:
                    try:
                        state["selected_device_detail"] = await device_service.get_device(device_id)
                    except Exception:
                        state["selected_device_detail"] = None
                else:
                    state["selected_device_detail"] = None

                # Load comments
                try:
                    state["selected_comments"] = await ticket_service.list_comments(ticket_id)
                except Exception:
                    state["selected_comments"] = []

            except Exception as exc:
                toast.error(f"Lỗi tải thông tin ticket: {exc}")
            finally:
                state["is_loading_detail"] = False
                render_all()

        # =========================================================================
        # 7. RENDER WORKSPACE BODY: SPLIT VIEW (MODE A)
        # =========================================================================
        def render_split_view() -> None:
            filtered = filter_tickets(state["raw_tickets"])

            # Auto-select first ticket if none selected
            if filtered and (not state["selected_ticket_id"] or not any(t["id"] == state["selected_ticket_id"] for t in filtered)):
                state["selected_ticket_id"] = filtered[0]["id"]
                ui.timer(0.01, lambda: select_ticket(filtered[0]["id"]), once=True)

            with main_workspace_container:
                with ui.row().classes("w-full items-start gap-3 flex-nowrap min-h-[640px]"):
                    # -------------------------------------------------------------
                    # LEFT PANE: QUEUE LIST (~380px)
                    # -------------------------------------------------------------
                    with ui.card().classes(
                        "w-full sm:w-[380px] shrink-0 p-0 rounded-lg bg-white border border-slate-200/90 shadow-2xs flex flex-col overflow-hidden h-[720px]"
                    ):
                        # Filter Toolbar & Search
                        with ui.column().classes("w-full p-2.5 gap-2 border-b border-slate-200/80 bg-slate-50/70"):
                            # Search input
                            search_in = (
                                ui.input(
                                    value=state["keyword"],
                                    placeholder="Tìm kiếm sự cố...",
                                    on_change=lambda e: on_search(e.value),
                                )
                                .props("outlined dense clearable debounce=300")
                                .classes("w-full text-xs")
                            )
                            with search_in.add_slot("prepend"):
                                ui.icon("search", size="16px").classes("text-slate-400")

                            def on_search(val: str | None) -> None:
                                state["keyword"] = val or ""
                                render_all()

                            # Scope Tabs
                            with ui.row().classes("w-full items-center gap-1 p-0.5 bg-slate-200/70 rounded-md"):
                                def set_scope(s: str) -> None:
                                    state["scope"] = s
                                    render_all()

                                scopes = [
                                    ("MY_TASKS", "Việc của tôi"),
                                    ("UNASSIGNED", "Chờ nhận"),
                                    ("URGENT", "Khẩn cấp"),
                                    ("ALL", "Tất cả"),
                                ]
                                for key, label in scopes:
                                    is_active = state["scope"] == key
                                    cls = "bg-white text-slate-900 font-bold shadow-xs" if is_active else "text-slate-600 hover:text-slate-900"
                                    ui.button(label, on_click=lambda k=key: set_scope(k)).props("flat dense").classes(
                                        f"flex-1 py-1 text-[11px] rounded transition-all {cls}"
                                    )

                        # Queue Item List
                        with ui.column().classes("w-full flex-1 overflow-y-auto divide-y divide-slate-100 gap-0"):
                            if not filtered:
                                with ui.column().classes("w-full p-8 items-center justify-center text-slate-400 gap-1.5"):
                                    ui.icon("inbox", size="28px").classes("text-slate-300")
                                    ui.label("Không có sự cố nào phù hợp").classes("text-xs font-medium")
                            else:
                                for tck in filtered:
                                    render_queue_item(tck)

                    # -------------------------------------------------------------
                    # RIGHT PANE: ACTIVE INCIDENT WORKSPACE (Remaining width)
                    # -------------------------------------------------------------
                    with ui.card().classes(
                        "flex-1 min-w-[400px] p-0 rounded-lg bg-white border border-slate-200/90 shadow-2xs flex flex-col overflow-hidden h-[720px]"
                    ):
                        render_active_workspace_panel()

        # =========================================================================
        # 8. RENDER QUEUE ITEM IN LEFT PANE
        # =========================================================================
        def render_queue_item(tck: dict[str, Any]) -> None:
            tck_id = tck["id"]
            is_selected = state["selected_ticket_id"] == tck_id
            priority = tck.get("priority", "MEDIUM")
            status = tck.get("status", "OPEN")

            border_accent = {
                "URGENT": "border-l-4 border-l-rose-500",
                "HIGH": "border-l-4 border-l-amber-500",
                "MEDIUM": "border-l-2 border-l-blue-400",
                "LOW": "border-l-2 border-l-slate-300",
            }.get(priority, "border-l-2 border-l-slate-300")

            bg_selected = "bg-blue-50/70" if is_selected else "hover:bg-slate-50"

            with ui.row().classes(
                f"w-full px-3.5 py-2.5 items-start justify-between cursor-pointer transition-colors duration-150 {border_accent} {bg_selected} gap-2"
            ).on("click", lambda tck_id=tck_id: select_ticket(tck_id)):
                with ui.column().classes("gap-1 flex-1 min-w-0"):
                    with ui.row().classes("items-center gap-1.5 no-wrap"):
                        ui.label(f"#TK-{tck_id:04d}").classes("font-mono text-xs font-bold text-slate-700")
                        priority_badge(priority)
                        if tck.get("technician_id") == user_id:
                            ui.label("Của tôi").classes("text-[9px] font-semibold text-primary px-1 py-0.2 bg-blue-50 border border-blue-200 rounded")

                    ui.label(tck.get("title", "-")).classes(
                        f"text-xs font-bold text-slate-900 truncate leading-snug {'text-primary' if is_selected else ''}"
                    )

                    with ui.row().classes("items-center gap-1.5 text-[10px] text-slate-400 truncate"):
                        ui.label(format_datetime(tck.get("updated_at") or tck.get("created_at")))
                        if tck.get("device_id"):
                            ui.label("·")
                            ui.label(f"Thiết bị #{tck.get('device_id')}")

                with ui.column().classes("items-end shrink-0 gap-1"):
                    status_badge(status)

        # =========================================================================
        # 9. RENDER ACTIVE INCIDENT WORKSPACE (RIGHT PANE)
        # =========================================================================
        def render_active_workspace_panel() -> None:
            tck = state["selected_ticket_detail"]
            if not tck:
                with ui.column().classes("w-full h-full items-center justify-center p-8 text-center text-slate-400 gap-2"):
                    ui.icon("touch_app", size="36px").classes("text-slate-300")
                    ui.label("Chọn một sự cố từ danh sách bên trái để bắt đầu xử lý").classes("text-sm font-semibold text-slate-600")
                    ui.label("Bạn có thể nhận việc, cập nhật tiến độ, ghi chú kỹ thuật và trao đổi với người dùng ngay tại đây.").classes("text-xs text-slate-400 max-w-sm")
                return

            tck_id = tck["id"]
            status = tck.get("status", "OPEN")
            priority = tck.get("priority", "MEDIUM")
            category = tck.get("category", "INCIDENT")
            is_unassigned = not tck.get("technician_id")
            is_my_ticket = tck.get("technician_id") == user_id

            # -------------------------------------------------------------
            # Top Banner & 1-Click Action Bar
            # -------------------------------------------------------------
            with ui.column().classes("w-full p-4 border-b border-slate-200/80 bg-slate-50/50 gap-3"):
                with ui.row().classes("w-full justify-between items-start flex-wrap gap-2"):
                    with ui.column().classes("gap-1 flex-1 min-w-[240px]"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(f"#TK-{tck_id:04d}").classes("font-mono text-base font-bold text-slate-900")
                            priority_badge(priority)
                            status_badge(status)
                            ui.label(CATEGORY_LABELS.get(category, category)).classes("text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200")

                        ui.label(tck.get("title", "-")).classes("text-base font-bold text-slate-900 leading-snug")

                    # Primary 1-Click Action Buttons
                    with ui.row().classes("items-center gap-2"):
                        if is_unassigned or status == "OPEN":
                            ui.button(
                                "Nhận & Bắt đầu xử lý",
                                icon="flash_on",
                                on_click=lambda: handle_claim_ticket(tck_id),
                            ).props("unelevated color=primary size=sm").classes("rounded-lg px-3 font-semibold text-xs shadow-2xs")
                        elif status == "ASSIGNED":
                            ui.button(
                                "Bắt đầu xử lý",
                                icon="play_arrow",
                                on_click=lambda: handle_advance_status(tck_id, "IN_PROGRESS"),
                            ).props("unelevated color=amber-700 size=sm").classes("rounded-lg px-3 font-semibold text-xs text-white shadow-2xs")
                        elif status == "IN_PROGRESS":
                            ui.button(
                                "Đã khắc phục xong",
                                icon="check_circle",
                                on_click=lambda: open_resolution_modal(tck_id),
                            ).props("unelevated color=positive size=sm").classes("rounded-lg px-3 font-semibold text-xs shadow-2xs")
                        elif status == "RESOLVED":
                            ui.button(
                                "Đóng sự cố & Bàn giao",
                                icon="lock",
                                on_click=lambda: open_close_ticket_modal(tck_id),
                            ).props("unelevated color=slate-800 size=sm").classes("rounded-lg px-3 font-semibold text-xs shadow-2xs")

                        ui.button(
                            icon="open_in_new",
                            on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                        ).props("outline dense size=sm color=slate-700").classes("rounded-lg h-8 w-8").tooltip("Mở trang chi tiết đầy đủ")

            # -------------------------------------------------------------
            # Scrollable Workspace Content
            # -------------------------------------------------------------
            with ui.column().classes("w-full flex-1 overflow-y-auto p-4 gap-4"):
                # Problem Description Box
                with ui.card().classes("w-full p-3.5 rounded-lg bg-white border border-slate-200/90 shadow-2xs gap-1.5"):
                    with ui.row().classes("items-center justify-between w-full pb-1 border-b border-slate-100"):
                        ui.label("MÔ TẢ SỰ CỐ TỪ NGƯỜI DÙNG").classes("text-[11px] font-bold text-slate-500 uppercase tracking-tight")
                        ui.label(format_datetime(tck.get("created_at"))).classes("text-[11px] text-slate-400")

                    ui.label(tck.get("description") or "Không có mô tả chi tiết kèm theo.").classes("text-xs text-slate-700 leading-relaxed")

                # Context Info: Requester & Linked Device
                with ui.row().classes("w-full gap-3 items-stretch flex-wrap"):
                    # Requester Card
                    with ui.card().classes("flex-1 min-w-[240px] p-3 rounded-lg bg-slate-50 border border-slate-200/80 shadow-2xs gap-1.5"):
                        ui.label("NGƯỜI YÊU CẦU").classes("text-[10px] font-bold text-slate-500 uppercase tracking-wider")
                        with ui.row().classes("items-center gap-2 mt-0.5"):
                            with ui.avatar(color="primary", text_color="white").props("size=28px font-size=11px").classes("font-bold"):
                                ui.label("U")
                            with ui.column().classes("gap-0"):
                                ui.label(f"User #{tck.get('user_id')}").classes("text-xs font-bold text-slate-900")
                                ui.label("Nhân viên phòng ban").classes("text-[10px] text-slate-500")

                    # Device & Location Card
                    dev = state["selected_device_detail"]
                    with ui.card().classes("flex-1 min-w-[240px] p-3 rounded-lg bg-slate-50 border border-slate-200/80 shadow-2xs gap-1.5"):
                        ui.label("THIẾT BỊ & VỊ TRÍ").classes("text-[10px] font-bold text-slate-500 uppercase tracking-wider")
                        if dev:
                            with ui.column().classes("gap-0.5 mt-0.5"):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.label(dev.get("ma_thiet_bi", "DEV")).classes("text-xs font-bold text-blue-700 font-mono")
                                    ui.label(f"- {dev.get('ten_thiet_bi', '')}").classes("text-xs font-semibold text-slate-800")
                                with ui.row().classes("items-center gap-1 text-[11px] text-slate-500"):
                                    ui.icon("location_on", size="12px").classes("text-slate-400")
                                    ui.label(dev.get("vi_tri") or "Chưa cập nhật vị trí")
                        else:
                            ui.label("Không liên kết với thiết bị cụ thể").classes("text-xs text-slate-400 italic mt-1")

                # Comments / Solution Notes Section
                with ui.card().classes("w-full p-3.5 rounded-lg bg-white border border-slate-200/90 shadow-2xs gap-2.5"):
                    with ui.row().classes("items-center justify-between w-full pb-1 border-b border-slate-100"):
                        ui.label("TRAO ĐỔI & GHI CHÚ KỸ THUẬT").classes("text-[11px] font-bold text-slate-500 uppercase tracking-tight")
                        ui.label(f"{len(state['selected_comments'])} ghi chú").classes("text-[11px] text-slate-400")

                    # Comment list
                    with ui.column().classes("w-full gap-2 max-h-[180px] overflow-y-auto"):
                        if not state["selected_comments"]:
                            ui.label("Chưa có trao đổi hoặc ghi chú nào.").classes("text-xs text-slate-400 italic py-2")
                        else:
                            for cm in state["selected_comments"]:
                                with ui.card().classes("w-full p-2.5 rounded bg-slate-50 border border-slate-100 gap-0.5"):
                                    with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-400"):
                                        ui.label(f"User #{cm.get('user_id')}").classes("font-semibold text-slate-700")
                                        ui.label(format_datetime(cm.get("created_at")))
                                    ui.label(cm.get("content", "")).classes("text-xs text-slate-800 leading-normal")

                    # Post Comment Input
                    with ui.row().classes("w-full items-center gap-2 pt-2 border-t border-slate-100"):
                        comment_input = ui.input(placeholder="Nhập ghi chú xử lý nội bộ hoặc phản hồi...").props("outlined dense").classes("flex-1 text-xs")

                        async def submit_comment() -> None:
                            val = (comment_input.value or "").strip()
                            if not val:
                                return
                            try:
                                await ticket_service.create_comment(tck_id, val)
                                comment_input.value = ""
                                toast.success("Đã thêm ghi chú thành công.")
                                state["selected_comments"] = await ticket_service.list_comments(tck_id)
                                render_all()
                            except Exception as exc:
                                toast.error(f"Lỗi thêm ghi chú: {exc}")

                        ui.button("Gửi", icon="send", on_click=submit_comment).props("unelevated color=primary size=sm").classes("rounded-lg px-3")

        # =========================================================================
        # 10. RENDER WORKSPACE BODY: KANBAN BOARD (MODE B)
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

            with main_workspace_container:
                with ui.row().classes("w-full gap-3 items-start flex-nowrap overflow-x-auto pb-4"):
                    for col_title, ticket_sublist, border_cls, col_icon in columns:
                        with ui.column().classes(f"min-w-[280px] w-72 bg-slate-100/90 p-2.5 rounded-lg border border-slate-200 {border_cls} gap-2.5 flex-shrink-0"):
                            # Column Header
                            with ui.row().classes("w-full justify-between items-center px-1 pb-1"):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon(col_icon, size="16px").classes("text-slate-600")
                                    ui.label(col_title).classes("text-xs font-bold text-slate-800 uppercase tracking-wider")
                                ui.label(str(len(ticket_sublist))).classes("text-[11px] font-bold px-2 py-0.2 bg-white rounded-full text-slate-700 border border-slate-200 shadow-2xs")

                            # Tickets in column
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

                ui.label(tck.get("title", "-")).classes("text-xs font-bold text-slate-900 line-clamp-2 leading-snug cursor-pointer").on(
                    "click", lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}")
                )

                if tck.get("device_id"):
                    with ui.row().classes("items-center gap-1 text-[10px] text-slate-500 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-100"):
                        ui.icon("laptop_mac", size="11px").classes("text-blue-500")
                        ui.label(f"Thiết bị #{tck.get('device_id')}")

                # Quick Action Button
                if cur_status == "OPEN" and is_unassigned:
                    ui.button(
                        "Nhận xử lý",
                        icon="flash_on",
                        on_click=lambda tck_id=tck_id: handle_claim_ticket(tck_id),
                    ).props("unelevated dense size=xs color=primary").classes("w-full font-semibold py-1 rounded")
                elif cur_status in ("OPEN", "ASSIGNED"):
                    ui.button(
                        "Bắt đầu xử lý",
                        icon="play_arrow",
                        on_click=lambda tck_id=tck_id: handle_advance_status(tck_id, "IN_PROGRESS"),
                    ).props("unelevated dense size=xs color=amber-700").classes("w-full font-semibold py-1 rounded text-white")
                elif cur_status == "IN_PROGRESS":
                    ui.button(
                        "Khắc phục xong",
                        icon="check",
                        on_click=lambda tck_id=tck_id: open_resolution_modal(tck_id),
                    ).props("unelevated dense size=xs color=positive").classes("w-full font-semibold py-1 rounded")
                elif cur_status == "RESOLVED":
                    ui.button(
                        "Đóng sự cố",
                        icon="lock",
                        on_click=lambda tck_id=tck_id: open_close_ticket_modal(tck_id),
                    ).props("unelevated dense size=xs color=slate-800").classes("w-full font-semibold py-1 rounded")

        # =========================================================================
        # 11. DATA LOADER
        # =========================================================================
        def render_all() -> None:
            # Update toggle button visual state
            btn_split.props("unelevated color=white text-color=primary" if state["view_mode"] == "SPLIT" else "flat color=slate-600")
            btn_kanban.props("unelevated color=white text-color=primary" if state["view_mode"] == "KANBAN" else "flat color=slate-600")

            render_summary_strip()
            main_workspace_container.clear()
            if state["view_mode"] == "SPLIT":
                render_split_view()
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
