from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.stat_card import stat_card
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, format_relative_time, truncate
from common.styles.breakpoints import RESPONSIVE_GRID
from core.constants import CATEGORY_LABELS
from core.i18n import get_category_label, t
from services.ticket_service import ticket_service


PRIORITY_WEIGHT = {
    "URGENT": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}

STATUS_WEIGHT = {
    "IN_PROGRESS": 3,
    "ASSIGNED": 2,
    "OPEN": 1,
    "RESOLVED": 0,
    "CLOSED": 0,
}


def render_dashboard_view() -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")
        role = user.get("vai_tro", "USER")
        user_name = user.get("ho_ten") or user.get("username", "Kỹ thuật viên")

        # =========================================================================
        # 1. NGƯỜI DÙNG PHỔ THÔNG (USER) -> CHUYỂN ĐẾN MY TICKETS
        # =========================================================================
        if role == "USER":
            ui.navigate.to("/user/tickets")
            return

        # =========================================================================
        # 2. TECHNICIAN PERSONAL WORKSPACE DASHBOARD
        # =========================================================================
        if role == "TECHNICIAN":
            render_technician_dashboard(user)
            return

        # =========================================================================
        # 3. ADMIN ANALYTICS DASHBOARD
        # =========================================================================
        render_admin_dashboard(user)

    def render_technician_dashboard(user: dict) -> None:
        user_id = user.get("id")
        user_name = user.get("ho_ten") or user.get("username", "Kỹ thuật viên")

        state: dict[str, Any] = {
            "my_tickets": [],
            "all_tickets": [],
            "is_loading": True,
            "error": None,
        }

        # Page Header Banner
        with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-200 mb-3 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-2"):
                    ui.label(t("tech_dash_title", name=user_name)).classes("text-2xl font-bold text-slate-900 tracking-tight")
                ui.label(t("tech_dash_sub")).classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                ui.button(
                    t("btn_open_workspace"),
                    icon="assignment",
                    on_click=lambda: ui.navigate.to("/technician/tasks"),
                ).props("color=primary unelevated size=md").classes("h-[38px] px-4 font-bold text-xs rounded-lg shadow-2xs")

                ui.button(
                    t("btn_device_lookup"),
                    icon="search",
                    on_click=lambda: ui.navigate.to("/technician/devices"),
                ).props("outline color=slate-700 size=md").classes("h-[38px] px-3.5 font-medium text-xs rounded-lg bg-white border-slate-300 shadow-2xs")

                ui.button(icon="refresh", on_click=lambda: load_tech_data(refresh=True, show_toast=True)).props(
                    "outline dense color=slate-700 size=sm"
                ).classes("h-[38px] w-[38px] rounded-lg bg-white border-slate-300 shadow-2xs").tooltip(t("btn_refresh"))

        # Container for Personal Work Summary Strip
        summary_container = ui.element("div").classes("w-full grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4")

        # Container for Main Grid (2 Columns: Work Queue 65% / Attention & Actions 35%)
        with ui.element("div").classes("w-full grid grid-cols-1 lg:grid-cols-[1fr_380px] xl:grid-cols-[1fr_420px] gap-4 items-start mb-4"):
            left_col = ui.column().classes("w-full gap-3 min-w-0")
            right_col = ui.column().classes("w-full gap-3")

        # Container for Bottom Recent Activity Feed
        bottom_container = ui.column().classes("w-full gap-2")

        async def render_tech_views() -> None:
            my_tickets = state["my_tickets"]
            all_tickets = state["all_tickets"]

            my_active = [tck for tck in my_tickets if tck.get("status") not in ("RESOLVED", "CLOSED")]
            my_in_progress = [tck for tck in my_tickets if tck.get("status") == "IN_PROGRESS"]
            my_urgent = [tck for tck in my_active if tck.get("priority") in ("URGENT", "HIGH")]
            my_resolved = [tck for tck in my_tickets if tck.get("status") in ("RESOLVED", "CLOSED")]

            # 1. Summary Cards Strip
            summary_container.clear()
            with summary_container:
                # Metric 1: Việc của tôi
                with ui.card().classes(
                    "p-4 rounded-xl bg-white border border-slate-200 shadow-2xs cursor-pointer hover:border-blue-400 hover:shadow-xs transition-all gap-1"
                ).on("click", lambda: ui.navigate.to("/technician/tasks")):
                    ui.label(t("kpi_my_active")).classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")
                    ui.label(str(len(my_active))).classes("text-2xl font-bold text-slate-900 tracking-tight")
                    ui.label(t("kpi_my_active_sub")).classes("text-[11px] text-slate-500")

                # Metric 2: Đang xử lý
                with ui.card().classes(
                    "p-4 rounded-xl bg-white border border-slate-200 shadow-2xs cursor-pointer hover:border-amber-400 hover:shadow-xs transition-all gap-1"
                ).on("click", lambda: ui.navigate.to("/technician/tasks")):
                    ui.label(t("kpi_my_in_progress")).classes("text-[10px] font-bold text-amber-600 uppercase tracking-wider")
                    ui.label(str(len(my_in_progress))).classes("text-2xl font-bold text-amber-700 tracking-tight")
                    ui.label(t("kpi_my_in_progress_sub")).classes("text-[11px] text-slate-500")

                # Metric 3: Cần ưu tiên
                with ui.card().classes(
                    "p-4 rounded-xl bg-white border border-slate-200 shadow-2xs cursor-pointer hover:border-rose-400 hover:shadow-xs transition-all gap-1"
                ).on("click", lambda: ui.navigate.to("/technician/tasks")):
                    ui.label(t("kpi_urgent")).classes("text-[10px] font-bold text-rose-600 uppercase tracking-wider")
                    ui.label(str(len(my_urgent))).classes("text-2xl font-bold text-rose-700 tracking-tight")
                    ui.label(t("kpi_urgent_sub")).classes("text-[11px] text-slate-500")

                # Metric 4: Hoàn thành
                with ui.card().classes(
                    "p-4 rounded-xl bg-white border border-slate-200 shadow-2xs cursor-pointer hover:border-emerald-400 hover:shadow-xs transition-all gap-1"
                ).on("click", lambda: ui.navigate.to("/technician/tasks")):
                    ui.label(t("kpi_resolved")).classes("text-[10px] font-bold text-emerald-600 uppercase tracking-wider")
                    ui.label(str(len(my_resolved))).classes("text-2xl font-bold text-emerald-700 tracking-tight")
                    ui.label(t("kpi_resolved_sub")).classes("text-[11px] text-slate-500")

            # 2. Left Column: My Priority Work Queue
            left_col.clear()
            with left_col:
                with ui.card().classes("w-full p-5 rounded-xl bg-white border border-slate-200 shadow-2xs gap-3"):
                    with ui.row().classes("w-full justify-between items-center pb-2.5 border-b border-slate-100"):
                        with ui.column().classes("gap-0.5"):
                            ui.label(t("sec_work_queue")).classes("text-base font-bold text-slate-900")
                            ui.label(t("sec_work_queue_sub")).classes("text-xs text-slate-500")
                        ui.button(t("btn_all_tickets"), on_click=lambda: ui.navigate.to("/technician/tasks")).props("flat dense size=sm color=primary").classes("text-xs font-semibold")

                    # Sort logic: Urgent/High first, then In_Progress, then oldest
                    sorted_work = list(my_active)
                    sorted_work.sort(
                        key=lambda x: (
                            -PRIORITY_WEIGHT.get(x.get("priority", "MEDIUM"), 2),
                            -STATUS_WEIGHT.get(x.get("status", "OPEN"), 1),
                            -x.get("id", 0),
                        )
                    )

                    if not sorted_work:
                        with ui.column().classes("w-full py-10 items-center justify-center text-center gap-1.5"):
                            ui.icon("task_alt", size="36px").classes("text-emerald-500")
                            ui.label(t("all_work_done")).classes("text-sm font-bold text-slate-800")
                            ui.label(t("all_work_done_sub")).classes("text-xs text-slate-500")
                            ui.button(t("btn_open_queue"), on_click=lambda: ui.navigate.to("/technician/tasks")).props("unelevated color=primary size=sm").classes("mt-2 rounded-lg font-bold px-4")
                    else:
                        with ui.column().classes("w-full divide-y divide-slate-100 gap-0"):
                            for tck in sorted_work[:5]:
                                t_id = tck["id"]
                                priority = tck.get("priority", "MEDIUM")
                                status = tck.get("status", "OPEN")
                                category_text = get_category_label(tck.get("category"))

                                with ui.row().classes(
                                    "w-full justify-between items-center py-3 hover:bg-slate-50/80 px-2 rounded-lg transition-colors gap-2"
                                ):
                                    with ui.column().classes("flex-1 min-w-0 gap-1"):
                                        with ui.row().classes("items-center gap-2 flex-wrap"):
                                            ui.label(f"#TK-{t_id:04d}").classes("font-mono font-bold text-xs text-slate-900")
                                            priority_badge(priority)
                                            status_badge(status)
                                            ui.label(f"· {category_text}").classes("text-[11px] text-slate-400 font-medium")

                                        ui.label(tck.get("title", "-")).classes("text-sm font-semibold text-slate-900 line-clamp-1 leading-snug")

                                        with ui.row().classes("items-center gap-2 text-[11px] text-slate-500"):
                                            ui.label(t("user_label", id=tck.get('user_id')))
                                            ui.label("·").classes("text-slate-300")
                                            ui.label(format_relative_time(tck.get('updated_at') or tck.get('created_at')))

                                    ui.button(
                                        t("btn_continue_work") + " →",
                                        on_click=lambda tid=t_id: ui.navigate.to(f"/tickets/{tid}"),
                                    ).props("outline dense size=sm color=primary").classes("h-8.5 px-3 rounded-lg font-bold text-xs shrink-0 bg-white border-blue-200 hover:bg-blue-50")

            # 3. Right Column: Urgent Block & Work Progress & Shortcuts
            right_col.clear()
            with right_col:
                # Urgent Attention Block
                with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-2xs gap-2.5"):
                    with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-100"):
                        ui.label(t("sec_urgent_attention")).classes("text-xs font-bold text-rose-700 uppercase tracking-wider")
                        ui.label(t("item_count_tickets", count=len(my_urgent))).classes("text-[11px] font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200")

                    if my_urgent:
                        top_urgent = my_urgent[0]
                        u_id = top_urgent["id"]
                        with ui.column().classes("w-full p-3 rounded-lg bg-rose-50/50 border border-rose-200 gap-1.5"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label(f"#TK-{u_id:04d}").classes("font-mono font-bold text-xs text-rose-900")
                                priority_badge(top_urgent.get("priority"))

                            ui.label(top_urgent.get("title", "-")).classes("text-xs font-bold text-slate-900 line-clamp-2 leading-snug")
                            ui.label(t("updated_time", time=format_relative_time(top_urgent.get('updated_at') or top_urgent.get('created_at')))).classes("text-[10px] text-slate-500")

                            ui.button(
                                t("btn_view_now"),
                                on_click=lambda id=u_id: ui.navigate.to(f"/tickets/{id}"),
                            ).props("unelevated color=negative size=sm").classes("w-full h-8 rounded-lg font-bold text-xs mt-1")
                    else:
                        with ui.row().classes("items-center gap-2 py-2 text-emerald-700 text-xs font-medium"):
                            ui.icon("check_circle", size="18px").classes("text-emerald-600")
                            ui.label(t("no_urgent_tickets"))

                # Today's Progress
                with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-2xs gap-2.5"):
                    ui.label(t("sec_progress")).classes("text-xs font-bold text-slate-700 uppercase tracking-wider pb-1 border-b border-slate-100")

                    total_assigned = len(my_tickets)
                    resolved_total = len(my_resolved)
                    pct = int((resolved_total / max(1, total_assigned)) * 100) if total_assigned > 0 else 100

                    with ui.row().classes("w-full justify-between items-baseline text-xs"):
                        ui.label(t("progress_done_text", resolved=resolved_total, total=total_assigned)).classes("font-semibold text-slate-800")
                        ui.label(f"{pct}%").classes("font-bold text-blue-600")

                    ui.linear_progress(value=pct / 100, color="primary").props("rounded size=8px").classes("w-full rounded-full bg-slate-100")

                    with ui.row().classes("w-full justify-between text-[11px] text-slate-500 pt-1"):
                        ui.label(t("progress_working", count=len(my_in_progress)))
                        ui.label(t("progress_waiting", count=len(my_active) - len(my_in_progress)))

                # Quick Actions Shortcuts
                with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-2xs gap-2"):
                    ui.label(t("sec_quick_actions")).classes("text-xs font-bold text-slate-700 uppercase tracking-wider pb-1 border-b border-slate-100")

                    ui.button(
                        t("btn_open_workspace_arrow"),
                        on_click=lambda: ui.navigate.to("/technician/tasks"),
                    ).props("outline color=slate-700 size=sm").classes("w-full justify-start h-9 rounded-lg font-medium text-xs bg-white border-slate-300 hover:bg-slate-50")

                    ui.button(
                        t("btn_device_lookup_arrow"),
                        on_click=lambda: ui.navigate.to("/technician/devices"),
                    ).props("outline color=slate-700 size=sm").classes("w-full justify-start h-9 rounded-lg font-medium text-xs bg-white border-slate-300 hover:bg-slate-50")

            # 4. Bottom Section: Recent Activity / Updates
            bottom_container.clear()
            with bottom_container:
                with ui.card().classes("w-full p-5 rounded-xl bg-white border border-slate-200 shadow-2xs gap-3"):
                    with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-100"):
                        with ui.column().classes("gap-0.5"):
                            ui.label(t("sec_recent_updates")).classes("text-sm font-bold text-slate-900")
                            ui.label(t("sec_recent_updates_sub")).classes("text-xs text-slate-500")

                    recent_tickets = list(all_tickets)
                    recent_tickets.sort(key=lambda x: str(x.get("updated_at") or x.get("created_at") or ""), reverse=True)

                    if not recent_tickets:
                        ui.label("Chưa có cập nhật nào.").classes("text-xs text-slate-400 italic py-2")
                    else:
                        with ui.column().classes("w-full divide-y divide-slate-100 gap-0"):
                            for r_tck in recent_tickets[:5]:
                                r_id = r_tck["id"]
                                r_time = format_relative_time(r_tck.get("updated_at") or r_tck.get("created_at"))

                                with ui.row().classes("w-full justify-between items-center py-2.5 hover:bg-slate-50 px-2 rounded-lg gap-2"):
                                    with ui.row().classes("items-center gap-3 flex-1 min-w-0"):
                                        ui.label(r_time).classes("font-mono text-xs text-slate-500 w-28 shrink-0")
                                        ui.label(f"#TK-{r_id:04d}").classes("font-mono font-bold text-xs text-slate-900 shrink-0")
                                        ui.label(r_tck.get("title", "-")).classes("text-xs font-semibold text-slate-800 truncate")

                                    with ui.row().classes("items-center gap-2 shrink-0"):
                                        status_badge(r_tck.get("status"))
                                        ui.button(
                                            t("view_link"),
                                            on_click=lambda tid=r_id: ui.navigate.to(f"/tickets/{tid}"),
                                        ).props("flat dense size=sm color=primary").classes("text-xs font-semibold")

        async def load_tech_data(refresh: bool = False, show_toast: bool = False) -> None:
            state["is_loading"] = True
            state["error"] = None

            try:
                tickets = await ticket_service.list_tickets(refresh=refresh)
                state["all_tickets"] = tickets
                state["my_tickets"] = [t for t in tickets if t.get("technician_id") == user_id]
                state["is_loading"] = False
                if show_toast:
                    toast.success("Đã làm mới dữ liệu tổng quan!")
            except Exception as exc:
                state["error"] = str(exc)
                state["is_loading"] = False
                toast.error(f"Lỗi tải dữ liệu: {exc}")

            await render_tech_views()

        ui.timer(0.05, lambda: load_tech_data(refresh=True), once=True)

    def render_admin_dashboard(user: dict) -> None:
        user_name = user.get("ho_ten") or user.get("username", "Quản trị viên")

        # Page Header Banner
        with ui.row().classes("w-full justify-between items-center py-2 border-b border-slate-200/80 mb-4"):
            with ui.column().classes("gap-0"):
                ui.label(f"Xin chào, {user_name}").classes("text-2xl font-bold text-slate-900 tracking-tight")
                ui.label("Trung tâm giám sát và phân tích hoạt động hỗ trợ kỹ thuật CS466 Helpdesk.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                ui.button(
                    "Giám sát sự cố",
                    icon="assignment",
                    on_click=lambda: ui.navigate.to("/admin/tickets"),
                ).props("color=primary unelevated size=sm").classes("h-[36px] px-3.5 font-bold rounded-lg shadow-2xs text-xs")

                ui.button(
                    "Quản lý người dùng",
                    icon="group",
                    on_click=lambda: ui.navigate.to("/admin/users"),
                ).props("outline color=slate-700 size=sm").classes("h-[36px] px-3.5 font-semibold rounded-lg bg-white border-slate-300 shadow-2xs text-xs")

        # KPI Metric Ribbon
        cards_grid = ui.element("div").classes(RESPONSIVE_GRID)

        # Charts Section
        charts_row = ui.row().classes("w-full gap-4 items-stretch mb-4")

        # Bottom Feeds Section
        bottom_section = ui.row().classes("w-full gap-4 items-start")

        async def load_admin_data() -> None:
            try:
                stats = await ticket_service.get_dashboard_stats()
            except Exception as exc:
                cards_grid.clear()
                with cards_grid:
                    stat_card("Backend API", "!", f"Lỗi: {exc}", "cloud_off")
                return

            total_tickets = stats.get("total_tickets", 0)
            status_counts = stats.get("status_counts", {})
            priority_counts = stats.get("priority_counts", {})
            category_counts = stats.get("category_counts", {})
            urgent_tickets = stats.get("urgent_tickets", [])

            open_count = status_counts.get("OPEN", 0) + status_counts.get("ASSIGNED", 0) + status_counts.get("IN_PROGRESS", 0)
            resolved_count = status_counts.get("RESOLVED", 0) + status_counts.get("CLOSED", 0)
            urgent_count = priority_counts.get("URGENT", 0) + priority_counts.get("HIGH", 0)

            # 1. Render Metric Cards
            cards_grid.clear()
            with cards_grid:
                stat_card("TỔNG TICKETS", total_tickets, "Toàn bộ yêu cầu", "confirmation_number")
                stat_card("ĐANG XỬ LÝ", open_count, "Open / Assigned / In Progress", "pending_actions")
                stat_card("ĐÃ HOÀN TẤT", resolved_count, "Resolved / Closed", "verified")
                stat_card("SỰ CỐ KHẨN", urgent_count, "Mức High & Urgent", "priority_high")

            # 2. Render Charts (Donut + Bar)
            charts_row.clear()
            with charts_row:
                # Donut Chart - Status Breakdown
                with ui.card().classes("flex-1 min-w-[340px] p-5 rounded-xl bg-white border border-slate-200 shadow-2xs"):
                    with ui.row().classes("w-full justify-between items-center mb-1"):
                        ui.label("Phân bổ trạng thái Ticket").classes("text-sm font-bold text-slate-900")
                        ui.label(f"{total_tickets} yêu cầu").classes("text-xs font-semibold text-slate-400")
                    ui.label("Tỷ lệ phân bố theo từng giai đoạn xử lý.").classes("text-xs text-slate-400 mb-2")

                    donut_data = [
                        {"value": status_counts.get("OPEN", 0), "name": "Mới mở", "itemStyle": {"color": "#3b82f6"}},
                        {"value": status_counts.get("ASSIGNED", 0), "name": "Đã giao KTV", "itemStyle": {"color": "#6366f1"}},
                        {"value": status_counts.get("IN_PROGRESS", 0), "name": "Đang xử lý", "itemStyle": {"color": "#f59e0b"}},
                        {"value": status_counts.get("RESOLVED", 0), "name": "Đã khắc phục", "itemStyle": {"color": "#10b981"}},
                        {"value": status_counts.get("CLOSED", 0), "name": "Đã đóng", "itemStyle": {"color": "#94a3b8"}},
                    ]

                    ui.echart(
                        {
                            "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
                            "legend": {
                                "orient": "vertical",
                                "right": "2%",
                                "top": "middle",
                                "itemWidth": 10,
                                "itemHeight": 10,
                                "itemGap": 12,
                                "textStyle": {"fontSize": 12, "color": "#475569"},
                            },
                            "series": [
                                {
                                    "name": "Trạng thái",
                                    "type": "pie",
                                    "radius": ["50%", "75%"],
                                    "center": ["34%", "50%"],
                                    "avoidLabelOverlap": False,
                                    "itemStyle": {"borderRadius": 5, "borderColor": "#fff", "borderWidth": 2},
                                    "label": {"show": False},
                                    "data": donut_data,
                                }
                            ],
                        }
                    ).classes("w-full h-60")

                # Bar Chart - Category Breakdown
                with ui.card().classes("flex-1 min-w-[340px] p-5 rounded-xl bg-white border border-slate-200 shadow-2xs"):
                    with ui.row().classes("w-full justify-between items-center mb-1"):
                        ui.label("Phân loại danh mục sự cố").classes("text-sm font-bold text-slate-900")
                        ui.label("Theo nhóm kỹ thuật").classes("text-xs font-semibold text-slate-400")
                    ui.label("Số lượng yêu cầu theo nhóm kỹ thuật.").classes("text-xs text-slate-400 mb-2")

                    cat_labels = [CATEGORY_LABELS.get(k, k) for k in category_counts.keys()] or ["Sự cố", "Yêu cầu", "Bảo trì"]
                    cat_values = list(category_counts.values()) or [0, 0, 0]

                    ui.echart(
                        {
                            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                            "grid": {"left": "4%", "right": "4%", "bottom": "8%", "top": "12%", "containLabel": True},
                            "xAxis": {
                                "type": "category",
                                "data": cat_labels,
                                "axisLine": {"lineStyle": {"color": "#e2e8f0"}},
                                "axisLabel": {"fontSize": 12, "color": "#475569"},
                            },
                            "yAxis": {
                                "type": "value",
                                "splitLine": {"lineStyle": {"color": "#f1f5f9"}},
                                "axisLabel": {"fontSize": 11, "color": "#94a3b8"},
                            },
                            "series": [
                                {
                                    "data": cat_values,
                                    "type": "bar",
                                    "barWidth": "32%",
                                    "itemStyle": {"color": "#2563eb", "borderRadius": [5, 5, 0, 0]},
                                }
                            ],
                        }
                    ).classes("w-full h-60")

            # 3. Bottom Feeds Section
            bottom_section.clear()
            with bottom_section:
                with ui.card().classes("flex-1 p-5 rounded-xl bg-white border border-slate-200 shadow-2xs"):
                    ui.label("Sự cố khẩn cấp toàn hệ thống").classes("text-sm font-bold text-slate-900 mb-3 pb-2 border-b border-slate-100")
                    if not urgent_tickets:
                        ui.label("Không có sự cố khẩn cấp tồn đọng.").classes("text-xs text-emerald-700 font-medium py-4")
                    else:
                        with ui.column().classes("w-full divide-y divide-slate-100"):
                            for tck in urgent_tickets[:5]:
                                tck_id = tck.get("id")
                                with ui.row().classes("w-full justify-between items-center py-2.5 hover:bg-slate-50 px-2 rounded-lg gap-2"):
                                    with ui.column().classes("gap-0.5 flex-1 min-w-0"):
                                        ui.label(f"#TK-{tck_id:04d} · {tck.get('title', '-')}").classes("text-xs font-bold text-slate-900 truncate")
                                        ui.label(format_datetime(tck.get("created_at"))).classes("text-[10px] text-slate-400")
                                    with ui.row().classes("items-center gap-1.5"):
                                        priority_badge(tck.get("priority"))
                                        status_badge(tck.get("status"))

        ui.timer(0.05, lambda: load_admin_data(), once=True)

    app_shell("Dashboard", content)
