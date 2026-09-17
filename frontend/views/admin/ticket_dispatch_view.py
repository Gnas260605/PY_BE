from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, truncate
from core.constants import CATEGORY_LABELS, TicketPriority
from services.ticket_service import ticket_service
from services.user_service import user_service

PRIORITY_WEIGHT = {
    "URGENT": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}

PRIORITY_BORDER_MAP = {
    "URGENT": "border-l-4 border-l-rose-500 bg-rose-50/10",
    "HIGH": "border-l-4 border-l-amber-500 bg-amber-50/10",
    "MEDIUM": "border-l-4 border-l-sky-500 bg-white",
    "LOW": "border-l-4 border-l-slate-300 bg-white",
}


def render_ticket_dispatch_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro")
        if role != "ADMIN":
            ui.label("Bạn không có quyền truy cập màn hình giám sát sự cố.").classes("text-red-600")
            return

        # 1. Header Section
        with ui.row().classes("w-full justify-between items-center py-1 mb-3 border-b border-slate-200/80"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("Giám sát & Điều phối Sự cố").classes("text-xl font-bold text-slate-900 tracking-tight")
                    ui.label("DISPATCH DECK").classes("text-[9px] font-bold px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 border border-purple-200 uppercase")
                ui.label("Trung tâm kiểm soát hàng đợi kỹ thuật, phân bổ tài nguyên và giám sát tiến độ xử lý.").classes("text-xs text-slate-500")

            ui.button("Tạo ticket mới", icon="add", on_click=lambda: ui.navigate.to("/user/tickets/new")).props("color=primary unelevated size=sm").classes("px-3 py-1.5 font-bold shadow-xs")

        # 2. Metric Strip (Linear / Vercel style)
        metrics_container = ui.row().classes("w-full gap-3 mb-4 items-stretch")

        # 3. Control & Filter Deck
        active_tab = {"value": "ALL"}
        tabs_row = ui.row().classes("w-full gap-1.5 items-center")

        with ui.card().classes("w-full p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs mb-3"):
            with ui.column().classes("w-full gap-3"):
                # Top: Tab selector
                tabs_row

                # Bottom: Search & Sort bar
                with ui.row().classes("w-full gap-2.5 items-center flex-wrap"):
                    keyword = ui.input(placeholder="Tìm kiếm sự cố theo tiêu đề, mã ticket...").props("outlined dense clearable debounce=300").classes("flex-1 min-w-[240px]")
                    
                    sort_selector = ui.select(
                        {
                            "NEWEST": "🕒 Mới nhất trước",
                            "OLDEST": "⏳ Cũ nhất trước",
                            "PRIORITY_HIGH": "⚡ Độ ưu tiên cao nhất",
                            "UNASSIGNED_FIRST": "👤 Chưa giao KTV lên đầu",
                        },
                        value="NEWEST",
                    ).props("outlined dense").classes("w-56")

                    priority_filter = ui.select(
                        {"ALL": "Tất cả mức ưu tiên", **{item.value: f"Ưu tiên: {item.value}" for item in TicketPriority}},
                        value="ALL",
                    ).props("outlined dense").classes("w-44")

                    async def handle_manual_refresh() -> None:
                        await reload_tickets()
                        toast.success("Đã cập nhật danh sách sự cố mới nhất!")

                    ui.button(icon="refresh", on_click=handle_manual_refresh).props("outline dense size=sm color=slate-700").classes("p-2 shrink-0")

        # 4. Main List Container
        ticket_container = ui.column().classes("w-full gap-2.5")

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

                tech_select = ui.select({}, label="Chọn Kỹ thuật viên tiếp nhận").props("outlined").classes("w-full")

                techs_map: dict[int, str] = {}
                try:
                    techs = await user_service.list_technicians()
                    techs_map = {t["id"]: t.get("ho_ten") or t.get("username") for t in techs}
                    tech_select.options = {t["id"]: f"{t.get('ho_ten')} (@{t.get('username')})" for t in techs}
                    tech_select.update()
                except Exception as exc:
                    toast.error(f"Lỗi tải danh sách KTV: {exc}")

                async def submit_assign() -> None:
                    if not tech_select.value:
                        toast.warning("Vui lòng chọn Kỹ thuật viên.")
                        return
                    selected_tech_id = int(tech_select.value)
                    tech_name = techs_map.get(selected_tech_id, f"KTV #{selected_tech_id}")
                    try:
                        await ticket_service.assign_ticket(tck_id, selected_tech_id)
                        dialog.close()
                        toast.show_popup(
                            title="Phân công KTV thành công! 🎉",
                            message=f"Ticket #{tck_id} đã được chuyển giao cho Kỹ thuật viên {tech_name}.",
                            type="success",
                        )
                        await reload_tickets()
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

        async def reload_tickets() -> None:
            try:
                raw_tickets = await ticket_service.list_tickets(
                    priority=None if priority_filter.value == "ALL" else priority_filter.value,
                    keyword=keyword.value,
                    refresh=True,
                )
            except Exception as exc:
                ticket_container.clear()
                with ticket_container:
                    ui.label(f"Lỗi tải danh sách: {exc}").classes("text-sm text-red-600")
                toast.show_popup("Lỗi kết nối", "Không thể tải dữ liệu từ server.", type="error", detail=str(exc))
                return

            total_count = len(raw_tickets)
            unassigned_tickets = [t for t in raw_tickets if not t.get("technician_id") and t.get("status") in ("OPEN", "ASSIGNED")]
            urgent_tickets = [t for t in raw_tickets if t.get("priority") in ("URGENT", "HIGH") and t.get("status") not in ("CLOSED", "RESOLVED")]
            in_progress_tickets = [t for t in raw_tickets if t.get("status") == "IN_PROGRESS"]
            done_tickets = [t for t in raw_tickets if t.get("status") in ("RESOLVED", "CLOSED")]

            # 1. Render Metrics Strip
            metrics_container.clear()
            with metrics_container:
                # Card 1: Unassigned (High Priority Focus)
                with ui.card().classes(
                    "flex-1 min-w-[170px] p-3.5 rounded-xl border transition-all cursor-pointer "
                    + ("bg-amber-500/10 border-amber-400 ring-2 ring-amber-400/20" if active_tab["value"] == "UNASSIGNED" else "bg-white border-slate-200 hover:border-amber-300")
                ).on("click", lambda: switch_tab("UNASSIGNED")):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("CHỜ PHÂN CÔNG").classes("text-[10px] font-bold text-amber-700 uppercase tracking-wider")
                            ui.label(str(len(unassigned_tickets))).classes("text-xl font-extrabold text-amber-900")
                        with ui.element("div").classes("w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center text-amber-700"):
                            ui.icon("person_add").classes("text-base")

                # Card 2: Urgent / High
                with ui.card().classes(
                    "flex-1 min-w-[170px] p-3.5 rounded-xl border transition-all cursor-pointer "
                    + ("bg-rose-500/10 border-rose-400 ring-2 ring-rose-400/20" if active_tab["value"] == "URGENT" else "bg-white border-slate-200 hover:border-rose-300")
                ).on("click", lambda: switch_tab("URGENT")):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("KHẨN CẤP & CAO").classes("text-[10px] font-bold text-rose-700 uppercase tracking-wider")
                            ui.label(str(len(urgent_tickets))).classes("text-xl font-extrabold text-rose-900")
                        with ui.element("div").classes("w-8 h-8 rounded-lg bg-rose-100 flex items-center justify-center text-rose-700"):
                            ui.icon("bolt").classes("text-base")

                # Card 3: In Progress
                with ui.card().classes(
                    "flex-1 min-w-[170px] p-3.5 rounded-xl border transition-all cursor-pointer "
                    + ("bg-blue-500/10 border-blue-400 ring-2 ring-blue-400/20" if active_tab["value"] == "IN_PROGRESS" else "bg-white border-slate-200 hover:border-blue-300")
                ).on("click", lambda: switch_tab("IN_PROGRESS")):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("ĐANG XỬ LÝ").classes("text-[10px] font-bold text-blue-700 uppercase tracking-wider")
                            ui.label(str(len(in_progress_tickets))).classes("text-xl font-extrabold text-blue-900")
                        with ui.element("div").classes("w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700"):
                            ui.icon("sync").classes("text-base")

                # Card 4: Total
                with ui.card().classes(
                    "flex-1 min-w-[170px] p-3.5 rounded-xl border transition-all cursor-pointer "
                    + ("bg-slate-900 text-white border-slate-900" if active_tab["value"] == "ALL" else "bg-white border-slate-200 hover:border-slate-400")
                ).on("click", lambda: switch_tab("ALL")):
                    with ui.row().classes("items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label("TỔNG SỰ CỐ").classes(f"text-[10px] font-bold uppercase tracking-wider {'text-slate-300' if active_tab['value'] == 'ALL' else 'text-slate-500'}")
                            ui.label(str(total_count)).classes(f"text-xl font-extrabold {'text-white' if active_tab['value'] == 'ALL' else 'text-slate-900'}")
                        with ui.element("div").classes(f"w-8 h-8 rounded-lg flex items-center justify-center {'bg-slate-800 text-white' if active_tab['value'] == 'ALL' else 'bg-slate-100 text-slate-700'}"):
                            ui.icon("view_list").classes("text-base")

            def switch_tab(tab_key: str) -> None:
                active_tab["value"] = tab_key
                render_tabs()
                render_incident_list()

            def get_filtered() -> list[dict[str, Any]]:
                t = active_tab["value"]
                if t == "UNASSIGNED":
                    return unassigned_tickets
                elif t == "URGENT":
                    return urgent_tickets
                elif t == "IN_PROGRESS":
                    return in_progress_tickets
                elif t == "DONE":
                    return done_tickets
                return list(raw_tickets)

            def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
                mode = sort_selector.value or "NEWEST"
                if mode == "NEWEST":
                    return sorted(items, key=lambda x: int(x.get("id", 0)), reverse=True)
                elif mode == "OLDEST":
                    return sorted(items, key=lambda x: int(x.get("id", 0)), reverse=False)
                elif mode == "PRIORITY_HIGH":
                    return sorted(items, key=lambda x: (PRIORITY_WEIGHT.get(x.get("priority", "LOW"), 0), int(x.get("id", 0))), reverse=True)
                elif mode == "UNASSIGNED_FIRST":
                    return sorted(items, key=lambda x: (1 if not x.get("technician_id") else 0, int(x.get("id", 0))), reverse=True)
                return sorted(items, key=lambda x: int(x.get("id", 0)), reverse=True)

            def render_tabs() -> None:
                tabs_row.clear()
                with tabs_row:
                    tab_defs = [
                        ("ALL", "Tất cả", total_count, "slate"),
                        ("UNASSIGNED", "Chưa giao KTV", len(unassigned_tickets), "amber"),
                        ("URGENT", "Khẩn cấp & Cao", len(urgent_tickets), "rose"),
                        ("IN_PROGRESS", "Đang xử lý", len(in_progress_tickets), "blue"),
                        ("DONE", "Đã xong", len(done_tickets), "emerald"),
                    ]
                    for key, label, count, color in tab_defs:
                        is_active = active_tab["value"] == key
                        badge_bg = "bg-white text-slate-900" if is_active else f"bg-{color}-100 text-{color}-800"
                        btn_bg = "bg-slate-900 text-white" if is_active else "bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200"

                        with ui.element("button").classes(
                            f"px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all {btn_bg}"
                        ).on("click", lambda k=key: switch_tab(k)):
                            ui.label(label)
                            ui.label(str(count)).classes(f"text-[10px] font-bold px-1.5 py-0.2 rounded-full {badge_bg}")

            def render_incident_list() -> None:
                ticket_container.clear()
                filtered = get_filtered()
                sorted_items = sort_items(filtered)

                with ticket_container:
                    if not sorted_items:
                        empty_state(
                            title="Không có sự cố nào trong mục này",
                            subtitle="Bạn có thể chuyển sang tab khác hoặc điều chỉnh từ khóa tìm kiếm.",
                            icon="task_alt",
                        )
                    else:
                        with ui.row().classes("w-full justify-between items-center px-1 mb-1"):
                            ui.label(f"HIỂN THỊ {len(sorted_items)} SỰ CỐ").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")

                        for tck in sorted_items:
                            tck_id = tck.get("id")
                            prio = tck.get("priority", "LOW")
                            stat = tck.get("status", "OPEN")
                            tech_id = tck.get("technician_id")
                            is_unassigned = not tech_id and stat in ("OPEN", "ASSIGNED")
                            border_class = PRIORITY_BORDER_MAP.get(prio, "border-l-4 border-l-slate-300 bg-white")
                            cat_label = CATEGORY_LABELS.get(tck.get("category"), "Sự cố kỹ thuật")

                            with ui.card().classes(
                                f"w-full p-4 rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-sm transition-all {border_class} gap-2.5"
                            ):
                                with ui.row().classes("w-full justify-between items-start gap-3"):
                                    # Top info row
                                    with ui.column().classes("gap-1 flex-1 min-w-[260px]"):
                                        with ui.row().classes("items-center gap-2 flex-wrap"):
                                            ui.label(f"#{tck_id}").classes("text-xs font-mono font-bold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded")
                                            ui.label(tck.get("title", "-")).classes("text-sm font-bold text-slate-900 leading-snug")
                                            ui.label(cat_label).classes("text-[10px] font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200")

                                        ui.label(truncate(tck.get("description", ""), 140)).classes("text-xs text-slate-600 line-clamp-1")

                                    # Badges column
                                    with ui.row().classes("items-center gap-2 shrink-0"):
                                        priority_badge(prio)
                                        status_badge(stat)

                                # Bottom Metadata & Action Bar
                                with ui.row().classes("w-full justify-between items-center pt-2.5 border-t border-slate-100 text-xs text-slate-500 flex-wrap gap-2"):
                                    with ui.row().classes("items-center gap-3"):
                                        # Tech indicator
                                        if tech_id:
                                            with ui.row().classes("items-center gap-1.5 text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200/60 font-semibold text-[11px]"):
                                                ui.icon("engineering").classes("text-xs")
                                                ui.label(f"KTV #{tech_id}")
                                        else:
                                            with ui.row().classes("items-center gap-1.5 text-amber-800 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200 font-bold text-[11px]"):
                                                ui.icon("error_outline").classes("text-xs text-amber-600")
                                                ui.label("Chưa phân công KTV")

                                        ui.label(f"🕒 Cập nhật: {format_datetime(tck.get('updated_at'))}").classes("text-[11px] text-slate-400")

                                    with ui.row().classes("items-center gap-2"):
                                        if stat in ("OPEN", "ASSIGNED"):
                                            ui.button(
                                                "Phân công KTV",
                                                icon="person_add",
                                                on_click=lambda tck=tck: open_assign_modal(tck),
                                            ).props("unelevated dense size=sm color=primary").classes("px-3 text-xs font-bold")

                                        ui.button(
                                            "Xem chi tiết",
                                            icon="arrow_forward",
                                            on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                                        ).props("flat dense size=sm color=slate-700").classes("px-2 text-xs font-semibold")

            render_tabs()
            render_incident_list()

            # Dynamic listener
            sort_selector.on_value_change(render_incident_list)

        ui.timer(0.1, reload_tickets, once=True)

    app_shell("Giám sát Sự cố", content)
