from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.loading import skeleton_loader
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, format_relative_time, truncate
from core.constants import CATEGORY_LABELS, STATUS_LABELS, TicketPriority, TicketStatus
from services.ticket_service import ticket_service
from services.user_service import user_service

PRIORITY_WEIGHT = {
    "URGENT": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}

PRIORITY_BORDER_MAP = {
    "URGENT": "border-l-4 border-l-rose-500 bg-rose-50/15",
    "HIGH": "border-l-4 border-l-amber-500 bg-amber-50/10",
    "MEDIUM": "border-l-4 border-l-sky-400 bg-white",
    "LOW": "border-l-4 border-l-slate-300 bg-white",
}


def render_ticket_dispatch_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro")
        if role != "ADMIN":
            ui.label("Bạn không có quyền truy cập màn hình giám sát sự cố.").classes("text-red-600")
            return

        # =========================================================================
        # 1. PAGE HEADER (Compact, Clean Enterprise Style)
        # =========================================================================
        with ui.row().classes("w-full justify-between items-center py-2 border-b border-slate-200/80 mb-3"):
            with ui.column().classes("gap-0.5"):
                ui.label("Giám sát & Điều phối Sự cố").classes("text-xl font-bold text-slate-900 tracking-tight")
                ui.label("Theo dõi, phân công và xử lý các yêu cầu hỗ trợ trong toàn hệ thống.").classes("text-xs text-slate-500")

            ui.button(
                "Tạo ticket",
                icon="add",
                on_click=lambda: ui.navigate.to("/user/tickets/new"),
            ).props("color=primary unelevated size=sm").classes("px-3.5 py-1.5 font-bold shadow-2xs rounded-lg")

        # =========================================================================
        # 2. STATE MANAGEMENT
        # =========================================================================
        state: dict[str, Any] = {
            "raw_tickets": [],
            "technicians": [],
            "active_tab": "ALL",
            "is_loading": True,
            "error": None,
        }

        # Operational Summary KPIs Grid (Grid based - No overflow)
        kpi_container = ui.element("div").classes("w-full grid grid-cols-2 lg:grid-cols-4 gap-3 mb-3")

        # Segmented Filter Tabs Row
        tabs_container = ui.row().classes("w-full gap-1.5 items-center mb-2.5 flex-wrap")

        # Search & Filter Toolbar (2-Tier Well-spaced Layout)
        with ui.card().classes("w-full p-3.5 rounded-xl bg-white border border-slate-200/90 shadow-2xs mb-3 gap-2.5"):
            # Tier 1: Search & Sorting
            with ui.row().classes("w-full gap-2.5 items-center flex-wrap"):
                keyword = ui.input(
                    placeholder="Tìm theo tiêu đề, mã ticket, người gửi...",
                ).props("outlined dense clearable debounce=300").classes("flex-1 min-w-[280px]")

                sort_select = ui.select(
                    {
                        "NEWEST": "🕒 Mới nhất trước",
                        "OLDEST": "⏳ Cũ nhất trước",
                        "PRIORITY_HIGH": "⚡ Ưu tiên cao nhất",
                        "UNASSIGNED_FIRST": "👤 Chưa giao KTV trước",
                    },
                    value="NEWEST",
                    label="Sắp xếp",
                ).props("outlined dense").classes("w-52")

                clear_filter_btn = ui.button("Xóa lọc", icon="filter_alt_off").props("flat dense size=sm color=slate-600").classes("text-xs font-semibold")
                clear_filter_btn.set_visibility(False)

                async def handle_refresh() -> None:
                    await fetch_data(force_refresh=True)
                    toast.success("Đã cập nhật danh sách sự cố mới nhất!")

                ui.button(icon="refresh", on_click=handle_refresh).props("outline dense size=sm color=slate-700").classes("p-2 shrink-0")

            # Tier 2: Filter Selectors (Generous widths - no truncation)
            with ui.row().classes("w-full gap-2.5 items-center flex-wrap pt-1 border-t border-slate-100"):
                status_select = ui.select(
                    {"ALL": "Tất cả trạng thái", **{item.value: STATUS_LABELS.get(item.value, item.value) for item in TicketStatus}},
                    value="ALL",
                    label="Trạng thái",
                ).props("outlined dense").classes("flex-1 min-w-[170px]")

                priority_select = ui.select(
                    {"ALL": "Tất cả mức ưu tiên", **{item.value: f"Ưu tiên: {item.value}" for item in TicketPriority}},
                    value="ALL",
                    label="Mức ưu tiên",
                ).props("outlined dense").classes("flex-1 min-w-[170px]")

                technician_select = ui.select(
                    {"ALL": "Tất cả KTV", "UNASSIGNED": "⚡ Chưa phân công"},
                    value="ALL",
                    label="Kỹ thuật viên",
                ).props("outlined dense").classes("flex-1 min-w-[170px]")

        # Main Incident List Container
        list_container = ui.column().classes("w-full gap-2")

        # =========================================================================
        # 3. ASSIGN TECHNICIAN MODAL
        # =========================================================================
        async def open_assign_modal(tck: dict[str, Any]) -> None:
            tck_id = tck["id"]
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-3 shadow-xl"):
                with ui.row().classes("items-center gap-2 mb-1"):
                    ui.icon("assignment_ind", color="primary").classes("text-xl")
                    ui.label(f"Phân công Kỹ thuật viên · Ticket #{tck_id}").classes("text-base font-bold text-slate-900")

                with ui.column().classes("w-full p-2.5 rounded-lg bg-slate-50 border border-slate-100 gap-0.5 mb-2"):
                    ui.label(tck.get("title", "-")).classes("text-xs font-bold text-slate-800 line-clamp-1")
                    ui.label(truncate(tck.get("description", ""), 80)).classes("text-[11px] text-slate-500 line-clamp-1")

                tech_opts = {t["id"]: f"{t.get('ho_ten')} (@{t.get('username')})" for t in state["technicians"]}
                tech_picker = ui.select(tech_opts, label="Chọn Kỹ thuật viên tiếp nhận").props("outlined").classes("w-full")

                async def submit_assign() -> None:
                    if not tech_picker.value:
                        toast.warning("Vui lòng chọn Kỹ thuật viên.")
                        return
                    selected_tech_id = int(tech_picker.value)
                    tech_name = next((t.get("ho_ten") for t in state["technicians"] if t["id"] == selected_tech_id), f"KTV #{selected_tech_id}")
                    try:
                        await ticket_service.assign_ticket(tck_id, selected_tech_id)
                        dialog.close()
                        toast.show_popup(
                            title="Phân công KTV thành công! 🎉",
                            message=f"Ticket #{tck_id} đã được giao xử lý cho Kỹ thuật viên {tech_name}.",
                            type="success",
                        )
                        await fetch_data(force_refresh=True)
                    except Exception as exc:
                        toast.show_popup(
                            title="Không thể phân công",
                            message="Đã có lỗi xảy ra khi phân công KTV.",
                            type="error",
                            detail=str(exc),
                        )

                with ui.row().classes("w-full justify-end gap-2 mt-4 pt-3 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600")
                    ui.button("Lưu phân công", icon="check", on_click=submit_assign).props("color=primary unelevated")
            dialog.open()

        # =========================================================================
        # 4. RENDERERS (KPIs, Tabs, Aligned Incident Table-Rows)
        # =========================================================================
        def render_kpi_strip() -> None:
            raw = state["raw_tickets"]
            unassigned_c = len([t for t in raw if not t.get("technician_id") and t.get("status") in ("OPEN", "ASSIGNED")])
            urgent_c = len([t for t in raw if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("CLOSED", "RESOLVED")])
            in_prog_c = len([t for t in raw if t.get("status") == "IN_PROGRESS"])
            total_c = len(raw)

            kpi_container.clear()
            with kpi_container:
                # KPI 1: Unassigned
                with ui.card().classes(
                    "p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between min-h-[82px] "
                    + ("bg-amber-500/15 border-amber-400 ring-2 ring-amber-400/20" if state["active_tab"] == "UNASSIGNED" else "bg-white border-slate-200 hover:border-amber-300 hover:bg-amber-50/20")
                ).on("click", lambda: set_tab("UNASSIGNED")):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("CHỜ PHÂN CÔNG").classes("text-[10px] font-bold text-amber-700 uppercase tracking-wider")
                        ui.label("Cần xử lý").classes("text-[9px] font-semibold text-amber-600 bg-amber-100 px-1.5 py-0.2 rounded")
                    with ui.row().classes("w-full justify-between items-end mt-1"):
                        ui.label(str(unassigned_c)).classes("text-2xl font-extrabold text-amber-900 leading-none")
                        ui.icon("person_add").classes("text-lg text-amber-600")

                # KPI 2: Urgent / High
                with ui.card().classes(
                    "p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between min-h-[82px] "
                    + ("bg-rose-500/15 border-rose-400 ring-2 ring-rose-400/20" if state["active_tab"] == "URGENT" else "bg-white border-slate-200 hover:border-rose-300 hover:bg-rose-50/20")
                ).on("click", lambda: set_tab("URGENT")):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("KHẨN CẤP & CAO").classes("text-[10px] font-bold text-rose-700 uppercase tracking-wider")
                        ui.label("Ưu tiên").classes("text-[9px] font-semibold text-rose-600 bg-rose-100 px-1.5 py-0.2 rounded")
                    with ui.row().classes("w-full justify-between items-end mt-1"):
                        ui.label(str(urgent_c)).classes("text-2xl font-extrabold text-rose-900 leading-none")
                        ui.icon("bolt").classes("text-lg text-rose-600")

                # KPI 3: In Progress
                with ui.card().classes(
                    "p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between min-h-[82px] "
                    + ("bg-blue-500/15 border-blue-400 ring-2 ring-blue-400/20" if state["active_tab"] == "IN_PROGRESS" else "bg-white border-slate-200 hover:border-blue-300 hover:bg-blue-50/20")
                ).on("click", lambda: set_tab("IN_PROGRESS")):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("ĐANG XỬ LÝ").classes("text-[10px] font-bold text-blue-700 uppercase tracking-wider")
                        ui.label("Tiến hành").classes("text-[9px] font-semibold text-blue-600 bg-blue-100 px-1.5 py-0.2 rounded")
                    with ui.row().classes("w-full justify-between items-end mt-1"):
                        ui.label(str(in_prog_c)).classes("text-2xl font-extrabold text-blue-900 leading-none")
                        ui.icon("sync").classes("text-lg text-blue-600")

                # KPI 4: Total Tickets
                with ui.card().classes(
                    "p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between min-h-[82px] "
                    + ("bg-slate-900 text-white border-slate-900 ring-2 ring-slate-900/20" if state["active_tab"] == "ALL" else "bg-white border-slate-200 hover:border-slate-400")
                ).on("click", lambda: set_tab("ALL")):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("TỔNG SỰ CỐ").classes(f"text-[10px] font-bold uppercase tracking-wider {'text-slate-300' if state['active_tab'] == 'ALL' else 'text-slate-500'}")
                        ui.label("Hệ thống").classes(f"text-[9px] font-semibold px-1.5 py-0.2 rounded {'bg-slate-800 text-slate-300' if state['active_tab'] == 'ALL' else 'bg-slate-100 text-slate-600'}")
                    with ui.row().classes("w-full justify-between items-end mt-1"):
                        ui.label(str(total_c)).classes(f"text-2xl font-extrabold leading-none {'text-white' if state['active_tab'] == 'ALL' else 'text-slate-900'}")
                        ui.icon("view_list").classes(f"text-lg {'text-slate-300' if state['active_tab'] == 'ALL' else 'text-slate-500'}")

        def render_segmented_tabs() -> None:
            raw = state["raw_tickets"]
            unassigned_c = len([t for t in raw if not t.get("technician_id") and t.get("status") in ("OPEN", "ASSIGNED")])
            urgent_c = len([t for t in raw if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("CLOSED", "RESOLVED")])
            in_prog_c = len([t for t in raw if t.get("status") == "IN_PROGRESS"])
            done_c = len([t for t in raw if t.get("status") in ("RESOLVED", "CLOSED")])
            total_c = len(raw)

            tabs_def = [
                ("ALL", "Tất cả", total_c, "slate"),
                ("UNASSIGNED", "Chưa phân công", unassigned_c, "amber"),
                ("URGENT", "Khẩn cấp & Cao", urgent_c, "rose"),
                ("IN_PROGRESS", "Đang xử lý", in_prog_c, "blue"),
                ("DONE", "Đã xong", done_c, "emerald"),
            ]

            tabs_container.clear()
            with tabs_container:
                for key, label, count, color in tabs_def:
                    is_active = state["active_tab"] == key
                    btn_bg = "bg-slate-900 text-white shadow-2xs font-bold" if is_active else "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200/70"
                    badge_bg = "bg-slate-800 text-white" if is_active else f"bg-{color}-100 text-{color}-800"

                    with ui.element("button").classes(
                        f"px-3 py-1.5 rounded-lg text-xs flex items-center gap-2 cursor-pointer transition-all {btn_bg}"
                    ).on("click", lambda k=key: set_tab(k)):
                        ui.label(label)
                        ui.label(str(count)).classes(f"text-[10px] font-bold px-1.5 py-0.2 rounded-full {badge_bg}")

        def set_tab(tab_key: str) -> None:
            state["active_tab"] = tab_key
            render_kpi_strip()
            render_segmented_tabs()
            render_list()

        def apply_filtering_and_sorting() -> list[dict[str, Any]]:
            raw = list(state["raw_tickets"])

            # 1. Tab filter
            t = state["active_tab"]
            if t == "UNASSIGNED":
                raw = [x for x in raw if not x.get("technician_id") and x.get("status") in ("OPEN", "ASSIGNED")]
            elif t == "URGENT":
                raw = [x for x in raw if x.get("priority") in ("URGENT", "HIGH")]
            elif t == "IN_PROGRESS":
                raw = [x for x in raw if x.get("status") == "IN_PROGRESS"]
            elif t == "DONE":
                raw = [x for x in raw if x.get("status") in ("RESOLVED", "CLOSED")]

            # 2. Status filter
            if status_select.value and status_select.value != "ALL":
                raw = [x for x in raw if x.get("status") == status_select.value]

            # 3. Priority filter
            if priority_select.value and priority_select.value != "ALL":
                raw = [x for x in raw if x.get("priority") == priority_select.value]

            # 4. Technician filter
            if technician_select.value and technician_select.value != "ALL":
                if technician_select.value == "UNASSIGNED":
                    raw = [x for x in raw if not x.get("technician_id")]
                else:
                    raw = [x for x in raw if str(x.get("technician_id")) == str(technician_select.value)]

            # 5. Keyword search
            kw = (keyword.value or "").strip().lower()
            if kw:
                raw = [
                    x for x in raw
                    if kw in str(x.get("id", "")).lower()
                    or kw in str(x.get("title", "")).lower()
                    or kw in str(x.get("description", "")).lower()
                ]

            # 6. Sorting
            s = sort_select.value or "NEWEST"
            if s == "NEWEST":
                raw.sort(key=lambda x: int(x.get("id", 0)), reverse=True)
            elif s == "OLDEST":
                raw.sort(key=lambda x: int(x.get("id", 0)), reverse=False)
            elif s == "PRIORITY_HIGH":
                raw.sort(key=lambda x: (PRIORITY_WEIGHT.get(x.get("priority", "LOW"), 0), int(x.get("id", 0))), reverse=True)
            elif s == "UNASSIGNED_FIRST":
                raw.sort(key=lambda x: (1 if not x.get("technician_id") else 0, int(x.get("id", 0))), reverse=True)

            return raw

        def check_active_filters() -> None:
            is_filtered = bool(
                (keyword.value or "").strip()
                or (status_select.value and status_select.value != "ALL")
                or (priority_select.value and priority_select.value != "ALL")
                or (technician_select.value and technician_select.value != "ALL")
                or state["active_tab"] != "ALL"
            )
            clear_filter_btn.set_visibility(is_filtered)

        def clear_all_filters() -> None:
            keyword.set_value("")
            status_select.set_value("ALL")
            priority_select.set_value("ALL")
            technician_select.set_value("ALL")
            state["active_tab"] = "ALL"
            render_kpi_strip()
            render_segmented_tabs()
            render_list()

        clear_filter_btn.on_click(clear_all_filters)

        def render_list() -> None:
            check_active_filters()
            list_container.clear()

            if state["is_loading"]:
                with list_container:
                    skeleton_loader(count=5, height="h-20")
                return

            if state["error"]:
                with list_container:
                    with ui.card().classes("w-full p-6 rounded-xl bg-red-50 border border-red-200 text-center items-center gap-2"):
                        ui.icon("error", color="negative").classes("text-3xl")
                        ui.label("Không thể tải danh sách sự cố.").classes("text-sm font-bold text-red-900")
                        ui.label(state["error"]).classes("text-xs text-red-600 font-mono")
                        ui.button("Thử lại", icon="refresh", on_click=lambda: fetch_data(force_refresh=True)).props("outline color=negative size=sm").classes("mt-2")
                return

            filtered_tickets = apply_filtering_and_sorting()

            with list_container:
                if not filtered_tickets:
                    empty_state(
                        title="Không tìm thấy sự cố nào phù hợp",
                        subtitle="Hãy thử thay đổi từ khóa tìm kiếm hoặc làm mới các bộ lọc.",
                        icon="search_off",
                        action_label="Xóa tất cả bộ lọc",
                        on_action=clear_all_filters,
                    )
                else:
                    with ui.row().classes("w-full justify-between items-center px-1 mb-1"):
                        ui.label(f"DANH SÁCH HIỂN THỊ ({len(filtered_tickets)} SỰ CỐ)").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")

                    # Dense Incident Table-Cards (CSS Grid for Strict Column Alignment)
                    with ui.column().classes("w-full divide-y divide-slate-100 rounded-xl bg-white border border-slate-200 shadow-2xs overflow-hidden"):
                        for tck in filtered_tickets:
                            tck_id = tck.get("id")
                            prio = tck.get("priority", "LOW")
                            stat = tck.get("status", "OPEN")
                            tech_id = tck.get("technician_id")
                            border_style = PRIORITY_BORDER_MAP.get(prio, "border-l-4 border-l-slate-300 bg-white")
                            cat_label = CATEGORY_LABELS.get(tck.get("category"), "Sự cố kỹ thuật")
                            updated_str = format_relative_time(tck.get("updated_at"))
                            exact_datetime = format_datetime(tck.get("updated_at"))

                            # Tech display resolver
                            tech_obj = next((t for t in state["technicians"] if t["id"] == tech_id), None)
                            tech_name = (tech_obj.get("ho_ten") or tech_obj.get("username")) if tech_obj else (f"KTV #{tech_id}" if tech_id else None)

                            # Grid Row with exact Column Alignments across all tickets
                            with ui.element("div").classes(
                                f"w-full grid grid-cols-12 gap-3 items-center p-3.5 hover:bg-slate-50/90 transition-colors {border_style} cursor-pointer"
                            ).on("click", lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}")):
                                
                                # Col 1: ID, Title, Category, Snippet (Span 5 on Desktop)
                                with ui.column().classes("col-span-12 md:col-span-5 gap-0.5 min-w-0 pr-2"):
                                    with ui.row().classes("items-center gap-2 no-wrap"):
                                        ui.label(f"#{tck_id}").classes("text-xs font-mono font-bold text-slate-600 bg-slate-100 px-1.5 py-0.2 rounded shrink-0")
                                        ui.label(tck.get("title", "-")).classes("text-sm font-bold text-slate-900 leading-snug line-clamp-1")
                                        ui.label(cat_label).classes("text-[10px] font-medium text-slate-500 bg-slate-50 px-2 py-0.2 rounded border border-slate-200 shrink-0 hidden sm:inline-block")

                                    ui.label(truncate(tck.get("description", ""), 100)).classes("text-xs text-slate-500 line-clamp-1")

                                # Col 2: Assignee Status (Span 2 on Desktop)
                                with ui.row().classes("col-span-6 md:col-span-2 items-center"):
                                    if tech_id and tech_name:
                                        with ui.row().classes("items-center gap-1.5 text-blue-700 bg-blue-50/90 px-2.5 py-0.5 rounded-full border border-blue-200/80 text-[11px] font-semibold truncate"):
                                            ui.icon("engineering").classes("text-xs shrink-0")
                                            ui.label(tech_name).classes("truncate")
                                    else:
                                        with ui.row().classes("items-center gap-1 text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-300 font-bold text-[11px] shrink-0"):
                                            ui.icon("error_outline").classes("text-xs text-amber-600")
                                            ui.label("Chưa giao KTV")

                                # Col 3: Updated Time (Span 2 on Desktop)
                                with ui.row().classes("col-span-6 md:col-span-2 items-center gap-1 text-slate-400 text-[11px]"):
                                    ui.icon("schedule").classes("text-xs shrink-0")
                                    time_label = ui.label(updated_str).classes("hover:text-slate-700 font-medium")
                                    time_label.tooltip(f"Cập nhật lúc: {exact_datetime}")

                                # Col 4: Badges (Span 2 on Desktop)
                                with ui.row().classes("col-span-8 md:col-span-2 items-center gap-1.5 flex-wrap"):
                                    priority_badge(prio)
                                    status_badge(stat)

                                # Col 5: Actions (Span 1 on Desktop - Right aligned)
                                with ui.row().classes("col-span-4 md:col-span-1 items-center justify-end gap-1"):
                                    if stat in ("OPEN", "ASSIGNED"):
                                        ui.button(
                                            "Giao KTV",
                                            icon="person_add",
                                            on_click=lambda e, tck=tck: (e.args.get("stop", True), open_assign_modal(tck)),
                                        ).props("outline dense size=sm color=primary").classes("px-2 text-xs font-semibold shrink-0")

                                    ui.button(
                                        icon="chevron_right",
                                        on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                                    ).props("flat round dense size=sm color=slate-400").classes("hover:text-slate-800")

        # =========================================================================
        # 5. DATA FETCHING CONTROLLER
        # =========================================================================
        async def fetch_data(force_refresh: bool = False) -> None:
            state["is_loading"] = True
            render_list()

            try:
                tickets = await ticket_service.list_tickets(refresh=force_refresh)
                techs = await user_service.list_technicians(refresh=force_refresh)
                state["raw_tickets"] = tickets
                state["technicians"] = techs
                state["error"] = None

                tech_opts = {"ALL": "Tất cả KTV", "UNASSIGNED": "⚡ Chưa phân công"}
                for t in techs:
                    tech_opts[str(t["id"])] = f"{t.get('ho_ten')} (@{t.get('username')})"
                technician_select.options = tech_opts
                technician_select.update()

            except Exception as exc:
                state["error"] = str(exc)
            finally:
                state["is_loading"] = False
                render_kpi_strip()
                render_segmented_tabs()
                render_list()

        # Connect toolbar listeners
        keyword.on_value_change(lambda: render_list())
        status_select.on_value_change(lambda: render_list())
        priority_select.on_value_change(lambda: render_list())
        technician_select.on_value_change(lambda: render_list())
        sort_select.on_value_change(lambda: render_list())

        # Trigger initial data fetch
        ui.timer(0.05, lambda: fetch_data(force_refresh=True), once=True)

    app_shell("Giám sát Sự cố", content)
