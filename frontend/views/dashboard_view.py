from nicegui import ui

from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.stat_card import stat_card
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, truncate
from common.styles.breakpoints import RESPONSIVE_GRID
from core.constants import CATEGORY_LABELS
from services.ticket_service import ticket_service


def render_dashboard_view() -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")
        role = user.get("vai_tro", "USER")
        user_name = user.get("ho_ten") or user.get("username")

        # =========================================================================
        # 1. NGƯỜI DÙNG PHỔ THÔNG (USER) -> CHUYỂN THẲNG ĐẾN DANH SÁCH TICKET CỦA MÌNH
        # =========================================================================
        if role == "USER":
            ui.navigate.to("/user/tickets")
            return

        # =========================================================================
        # 2. GIAO DIỆN DÀNH CHO ADMIN & KỸ THUẬT VIÊN (OPERATIONS ANALYTICS DASHBOARD)
        # =========================================================================
        # Page Header Banner
        with ui.row().classes("w-full justify-between items-center py-2 border-b border-slate-200/80 mb-4"):
            with ui.column().classes("gap-0"):
                with ui.row().classes("items-center gap-2"):
                    ui.label(f"Xin chào, {user_name}").classes("text-xl font-bold text-slate-900")
                    ui.label("👋").classes("text-lg")
                ui.label("Trung tâm giám sát và phân tích hoạt động hỗ trợ kỹ thuật CS466 Helpdesk.").classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                if role == "TECHNICIAN":
                    ui.button("Bảng công việc", icon="task_alt", on_click=lambda: ui.navigate.to("/technician/tasks")).props("color=primary unelevated size=sm").classes("px-3 py-1.5")
                else:
                    ui.button("Phân công tickets", icon="assignment", on_click=lambda: ui.navigate.to("/admin/tickets")).props("color=primary unelevated size=sm").classes("px-3 py-1.5")

        # KPI Metric Ribbon
        cards_grid = ui.element("div").classes(RESPONSIVE_GRID)

        # Charts Section
        charts_row = ui.row().classes("w-full gap-4 items-stretch")

        # Bottom Feeds Section
        bottom_section = ui.row().classes("w-full gap-4 items-start")

        async def load_dashboard_data() -> None:
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
            total_devices = stats.get("total_devices", 0)

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
                with ui.card().classes("flex-1 min-w-[340px] p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
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
                                "textStyle": {"fontSize": 12, "fontFamily": "Plus Jakarta Sans", "color": "#475569"},
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
                                    "emphasis": {
                                        "label": {"show": True, "fontSize": 13, "fontWeight": "bold", "fontFamily": "Plus Jakarta Sans"}
                                    },
                                    "labelLine": {"show": False},
                                    "data": donut_data,
                                }
                            ],
                        }
                    ).classes("w-full h-60")

                # Bar Chart - Category Breakdown
                with ui.card().classes("flex-1 min-w-[340px] p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
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
                                "axisLabel": {"fontSize": 12, "fontFamily": "Plus Jakarta Sans", "color": "#475569"},
                            },
                            "yAxis": {
                                "type": "value",
                                "splitLine": {"lineStyle": {"color": "#f1f5f9"}},
                                "axisLabel": {"fontSize": 11, "fontFamily": "Plus Jakarta Sans", "color": "#94a3b8"},
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

            # 3. Render Feeds & Action Shortcuts
            bottom_section.clear()
            with bottom_section:
                # Urgent Incident Feed
                with ui.card().classes("flex-[2] min-w-[340px] p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
                    with ui.row().classes("w-full justify-between items-center mb-2 pb-2 border-b border-slate-100"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("warning", color="warning").classes("text-base")
                            ui.label("Sự cố cần chú ý gần đây").classes("text-sm font-bold text-slate-900")
                        ui.label(f"{len(urgent_tickets)} sự cố").classes("text-xs text-slate-400 font-semibold")

                    if not urgent_tickets:
                        with ui.column().classes("w-full py-8 items-center text-center gap-1"):
                            ui.icon("verified").classes("text-3xl text-emerald-500")
                            ui.label("Không có sự cố khẩn cấp tồn đọng.").classes("text-xs font-semibold text-slate-700")
                    else:
                        with ui.column().classes("w-full divide-y divide-slate-100"):
                            for tck in urgent_tickets[:5]:
                                tck_id = tck.get("id")
                                with ui.row().classes("w-full justify-between items-center py-2.5 hover:bg-slate-50 px-2 rounded-lg transition-colors no-wrap"):
                                    with ui.column().classes("gap-0.5 flex-1 min-w-0 pr-3"):
                                        with ui.row().classes("items-center gap-2 no-wrap"):
                                            ui.label(f"#{tck_id}").classes("text-xs font-bold text-blue-600 shrink-0")
                                            ui.label(tck.get("title", "-")).classes("text-sm font-semibold text-slate-800 line-clamp-1")
                                        ui.label(f"Tạo lúc: {format_datetime(tck.get('created_at'))}").classes("text-[11px] text-slate-400")

                                    with ui.row().classes("items-center gap-2 shrink-0 no-wrap"):
                                        priority_badge(tck.get("priority"))
                                        status_badge(tck.get("status"))
                                        ui.button(
                                            icon="arrow_forward",
                                            on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                                        ).props("flat round dense size=sm color=primary")

                # Quick Help & Role Actions
                with ui.card().classes("flex-1 min-w-[260px] p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
                    ui.label("Thao tác nhanh").classes("text-sm font-bold text-slate-900 mb-3 pb-2 border-b border-slate-100")
                    with ui.column().classes("w-full gap-2.5"):
                        if role == "ADMIN":
                            with ui.button(on_click=lambda: ui.navigate.to("/admin/users")).props("outline color=slate-700").classes("w-full justify-start py-2 px-3"):
                                with ui.row().classes("items-center gap-2.5"):
                                    ui.icon("group").classes("text-slate-500 text-sm")
                                    ui.label("Quản lý tài khoản").classes("text-xs font-semibold")

                            with ui.button(on_click=lambda: ui.navigate.to("/admin/devices")).props("outline color=slate-700").classes("w-full justify-start py-2 px-3"):
                                with ui.row().classes("items-center gap-2.5"):
                                    ui.icon("devices").classes("text-slate-500 text-sm")
                                    ui.label("Danh mục thiết bị").classes("text-xs font-semibold")

                            with ui.button(on_click=lambda: ui.navigate.to("/admin/tickets")).props("outline color=slate-700").classes("w-full justify-start py-2 px-3"):
                                with ui.row().classes("items-center gap-2.5"):
                                    ui.icon("confirmation_number").classes("text-slate-500 text-sm")
                                    ui.label("Giám sát & Phân công").classes("text-xs font-semibold")
                        elif role == "TECHNICIAN":
                            with ui.button(on_click=lambda: ui.navigate.to("/technician/tasks")).props("outline color=slate-700").classes("w-full justify-start py-2 px-3"):
                                with ui.row().classes("items-center gap-2.5"):
                                    ui.icon("view_kanban").classes("text-amber-600 text-sm")
                                    ui.label("Bảng Kanban công việc").classes("text-xs font-semibold")

                            with ui.button(on_click=lambda: ui.navigate.to("/technician/devices")).props("outline color=slate-700").classes("w-full justify-start py-2 px-3"):
                                with ui.row().classes("items-center gap-2.5"):
                                    ui.icon("search").classes("text-blue-600 text-sm")
                                    ui.label("Tra cứu thiết bị & lịch sử").classes("text-xs font-semibold")

        ui.timer(0.1, load_dashboard_data, once=True)

    app_shell("Dashboard", content)
