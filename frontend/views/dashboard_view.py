from __future__ import annotations

from nicegui import ui

from common.components.layout import app_shell
from core.http_client import ApiException
from services.ticket_service import ticket_service
from views.user.demo_data import DEMO_TICKETS, RECENT_ACTIVITIES


def render_dashboard_view() -> None:
    from common.components.layout import require_login
    current_u = require_login()
    if current_u and current_u.get("vai_tro") == "ADMIN":
        from views.admin.operations_view import render_admin_operations_view
        render_admin_operations_view()
        return

    def content(user: dict) -> None:
        ho_ten = user.get("ho_ten") or "Mai"
        first_name = ho_ten.split()[-1] if ho_ten else "Mai"

        # -------------------------------------------------------------
        # 1. GREETING BANNER & QUICK ACTIONS (Image 1 Header)
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-start flex-wrap gap-3 pt-0"):
            with ui.column().classes("gap-1.5 max-w-2xl"):
                # System Status Badge
                with ui.row().classes("items-center gap-2"):
                    ui.element("span").classes("w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse")
                    ui.label("HỆ THỐNG IT VẬN HÀNH BÌNH THƯỜNG").classes(
                        "text-[11px] font-bold tracking-wider text-blue-700 uppercase"
                    )

                # Heading
                ui.label(f"Chào buổi sáng, {first_name}").classes(
                    "text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Dưới đây là tình trạng các yêu cầu hỗ trợ và sự cố IT của bạn hôm nay. Tất cả hệ thống cốt lõi đang hoạt động ổn định."
                ).classes("text-xs md:text-sm text-slate-500 leading-relaxed")

            # Action Buttons
            with ui.row().classes("items-center gap-3"):
                with ui.button(
                    "Hướng dẫn nhanh",
                    icon="menu_book",
                    on_click=lambda: ui.notify("Mở sổ tay hướng dẫn người dùng HelpDesk Pro", type="info"),
                ).props("flat no-caps").classes(
                    "bg-white border border-slate-200 text-slate-700 font-semibold px-4 py-2 rounded-xl text-xs shadow-sm hover:bg-slate-50"
                ):
                    pass

                ui.button(
                    "Tạo yêu cầu mới",
                    icon="add",
                    on_click=lambda: ui.navigate.to("/user/tickets/new"),
                ).props("unelevated no-caps").classes(
                    "bg-blue-600 hover:bg-blue-700 text-white font-bold px-5 py-2 rounded-xl text-xs shadow-md shadow-blue-500/20"
                )

        # -------------------------------------------------------------
        # 2. 4 METRIC KPI CARDS (Image 1 Row of 4)
        # -------------------------------------------------------------
        with ui.element("div").classes("grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full mt-1"):
            # Card 1: Ticket đang xử lý
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-start no-wrap"):
                    ui.label("TICKET ĐANG XỬ LÝ").classes("text-[11px] font-bold text-slate-400 uppercase tracking-wider")
                    with ui.element("div").classes(
                        "w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0"
                    ):
                        ui.icon("folder_open").classes("text-lg")
                ui.label("3").classes("text-3xl font-extrabold text-slate-900 tracking-tight my-1")
                with ui.row().classes("items-center gap-2 mt-1"):
                    ui.element("span").classes("w-2 h-2 rounded-full bg-red-500")
                    ui.label("1 sự cố cần phản hồi").classes("text-xs font-semibold text-slate-600")

            # Card 2: Đang thực hiện
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-start no-wrap"):
                    ui.label("ĐANG THỰC HIỆN").classes("text-[11px] font-bold text-slate-400 uppercase tracking-wider")
                    with ui.element("div").classes(
                        "w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0"
                    ):
                        ui.icon("group").classes("text-lg")
                ui.label("2").classes("text-3xl font-extrabold text-slate-900 tracking-tight my-1")
                with ui.row().classes("items-center gap-2 mt-1"):
                    ui.element("span").classes("w-2 h-2 rounded-full bg-indigo-400")
                    ui.label("Kỹ thuật viên đang xử lý").classes("text-xs font-semibold text-slate-600")

            # Card 3: Đã giải quyết tuần này
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-start no-wrap"):
                    ui.label("ĐÃ GIẢI QUYẾT TUẦN NÀY").classes("text-[11px] font-bold text-slate-400 uppercase tracking-wider")
                    with ui.element("div").classes(
                        "w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0"
                    ):
                        ui.icon("check_circle").classes("text-lg")
                ui.label("8").classes("text-3xl font-extrabold text-slate-900 tracking-tight my-1")
                with ui.row().classes("items-center gap-2 mt-1"):
                    ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500")
                    ui.label("100% đúng hạn SLA").classes("text-xs font-semibold text-emerald-700")

            # Card 4: Tổng yêu cầu đã gửi
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-start no-wrap"):
                    ui.label("TỔNG YÊU CẦU ĐÃ GỬI").classes("text-[11px] font-bold text-slate-400 uppercase tracking-wider")
                    with ui.element("div").classes(
                        "w-9 h-9 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center shrink-0"
                    ):
                        ui.icon("grid_view").classes("text-lg")
                ui.label("24").classes("text-3xl font-extrabold text-slate-900 tracking-tight my-1")
                with ui.row().classes("items-center gap-2 mt-1"):
                    ui.element("span").classes("w-2 h-2 rounded-full bg-slate-400")
                    ui.label("Trong năm 2026").classes("text-xs font-semibold text-slate-500")

        # -------------------------------------------------------------
        # 3. MAIN TWO-COLUMN CONTENT
        # -------------------------------------------------------------
        with ui.element("div").classes("grid grid-cols-1 lg:grid-cols-12 gap-5 w-full items-start mt-2"):
            # ================= LEFT COLUMN: ~68% (8 of 12) =================
            with ui.column().classes("lg:col-span-8 w-full gap-5"):
                # Card: Yêu cầu đang xử lý
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    # Header row
                    with ui.row().classes("w-full justify-between items-center pb-4 border-b border-slate-100 flex-wrap gap-2"):
                        with ui.row().classes("items-center gap-2.5"):
                            ui.icon("inbox").classes("text-blue-600 text-lg")
                            ui.label("Yêu cầu đang xử lý").classes("text-base font-bold text-slate-900")
                            with ui.element("span").classes(
                                "px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold leading-tight"
                            ):
                                ui.label("3 active")

                        with ui.row().classes("items-center gap-2"):
                            with ui.button("Lọc dữ liệu", icon="filter_list").props("flat dense no-caps").classes(
                                "text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded-lg"
                            ):
                                pass
                            with ui.button("Sắp xếp", icon="sort").props("flat dense no-caps").classes(
                                "text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded-lg"
                            ):
                                pass

                    # Ticket items list
                    active_tickets = DEMO_TICKETS[:3]
                    with ui.column().classes("w-full gap-3 mt-3"):
                        for ticket in active_tickets:
                            t_id = ticket["id"]
                            with ui.element("div").classes(
                                "w-full p-4 rounded-xl border border-slate-200/70 hover:border-blue-300 hover:bg-blue-50/20 transition-all flex flex-col md:flex-row md:items-center md:justify-between gap-4"
                            ):
                                # Left info
                                with ui.column().classes("gap-1.5 flex-1 min-w-0"):
                                    # Badge tag row
                                    with ui.row().classes("items-center gap-2 flex-wrap"):
                                        ui.label(f"#{t_id}").classes("text-xs font-extrabold text-blue-600")

                                        # Category tag
                                        cat_class = "bg-red-50 text-red-700 border-red-200" if ticket["category_code"] == "INCIDENT" else "bg-blue-50 text-blue-700 border-blue-200"
                                        ui.label(ticket["category_label"]).classes(f"text-[10px] font-bold px-2 py-0.5 rounded border {cat_class}")

                                        # Priority tag
                                        if ticket["priority_code"] == "URGENT":
                                            ui.label("● Khẩn cấp").classes("text-[10px] font-bold px-2 py-0.5 rounded bg-red-100 text-red-700 border border-red-200")
                                        elif ticket["priority_code"] == "HIGH":
                                            ui.label("Cao").classes("text-[10px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200")
                                        else:
                                            ui.label(ticket["priority_label"]).classes("text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600")

                                        # Status tag
                                        status_class = "bg-blue-50 text-blue-700" if ticket["status_code"] in ("OPEN", "IN_PROGRESS", "ASSIGNED") else "bg-emerald-50 text-emerald-700"
                                        ui.label(ticket["status_label"]).classes(f"text-[10px] font-semibold px-2 py-0.5 rounded {status_class}")

                                    # Title
                                    ui.label(ticket["title"]).classes(
                                        "text-sm font-bold text-slate-900 leading-snug cursor-pointer hover:text-blue-600 transition-colors line-clamp-1"
                                    ).on("click", lambda tid=t_id: ui.navigate.to(f"/user/tickets/{tid}"))

                                    # Meta device & time
                                    with ui.row().classes("items-center gap-4 text-xs text-slate-400 mt-0.5"):
                                        with ui.row().classes("items-center gap-1.5"):
                                            ui.icon("print" if "PRN" in ticket["device_code"] else "computer").classes("text-sm text-slate-400")
                                            ui.label(ticket["device_code"]).classes("font-medium text-slate-600")
                                        with ui.row().classes("items-center gap-1.5"):
                                            ui.icon("schedule").classes("text-sm text-slate-400")
                                            ui.label(f"Cập nhật {ticket['updated_time']}").classes("text-slate-500")

                                # Right assigned tech & action
                                with ui.row().classes("items-center gap-4 shrink-0 justify-between md:justify-end"):
                                    # Tech avatar capsule
                                    with ui.row().classes("items-center gap-2"):
                                        tech_initial = ticket.get("tech_initial") or "KTV"
                                        with ui.element("div").classes(
                                            "w-8 h-8 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-xs shrink-0"
                                        ):
                                            ui.label(tech_initial[:2])
                                        with ui.column().classes("gap-0"):
                                            ui.label(ticket["tech_name"]).classes("text-xs font-bold text-slate-800 leading-tight")
                                            ui.label(ticket["tech_role_short"]).classes("text-[10px] text-slate-400 leading-tight")

                                    # Details link
                                    with ui.button(
                                        "Chi tiết >",
                                        on_click=lambda tid=t_id: ui.navigate.to(f"/user/tickets/{tid}"),
                                    ).props("flat dense no-caps").classes(
                                        "text-xs font-bold text-blue-600 hover:text-blue-800 p-0"
                                    ):
                                        pass

                    # Footer
                    with ui.row().classes("w-full justify-between items-center pt-4 mt-2 border-t border-slate-100 text-xs"):
                        ui.label("Hiển thị 3 trên tổng số 3 ticket mở").classes("text-slate-400 font-medium")
                        ui.link("Xem lịch sử tất cả ticket →", "/user/tickets").classes(
                            "font-bold text-blue-600 hover:text-blue-700 no-underline"
                        )

                # Card: Cam kết chất lượng SLA
                with ui.card().classes(
                    "w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4"
                ):
                    with ui.row().classes("items-center gap-3.5 flex-1"):
                        with ui.element("div").classes(
                            "w-11 h-11 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0 shadow-sm"
                        ):
                            ui.icon("verified_user").classes("text-2xl")
                        with ui.column().classes("gap-0.5"):
                            ui.label("Cam kết chất lượng SLA").classes("text-sm font-bold text-slate-900")
                            ui.label("Thời gian phản hồi sự cố khẩn cấp trung bình dưới 15 phút.").classes(
                                "text-xs text-slate-500"
                            )

                    # Circular SLA Progress Chart
                    with ui.row().classes("items-center gap-3 shrink-0"):
                        with ui.column().classes("gap-0 items-end"):
                            ui.label("THỜI GIAN XỬ LÝ TB").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider")
                            ui.label("1.4 giờ").classes("text-xl font-extrabold text-slate-900 leading-none")

                        # SVG Donut Ring
                        ui.html(
                            """
                            <svg class="w-10 h-10 transform -rotate-90" viewBox="0 0 36 36">
                              <path class="text-slate-100" stroke-width="3.5" stroke="currentColor" fill="none"
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                              <path class="text-emerald-500" stroke-dasharray="75, 100" stroke-width="3.5" stroke-linecap="round" stroke="currentColor" fill="none"
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                            </svg>
                            """
                        )

            # ================= RIGHT COLUMN: ~32% (4 of 12) =================
            with ui.column().classes("lg:col-span-4 w-full gap-5"):
                # 1. Hoạt động gần đây (Timeline)
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("history").classes("text-blue-600 text-lg")
                            ui.label("Hoạt động gần đây").classes("text-sm font-bold text-slate-900")
                        ui.element("span").classes("w-2 h-2 rounded-full bg-blue-600")

                    # Steps
                    with ui.column().classes("w-full gap-4 mt-3 pl-1"):
                        for act in RECENT_ACTIVITIES:
                            with ui.row().classes("w-full items-start gap-3 no-wrap"):
                                with ui.element("div").classes("w-2 h-2 rounded-full bg-blue-600 mt-1.5 shrink-0 ring-4 ring-blue-50"):
                                    pass
                                with ui.column().classes("gap-0.5 flex-1"):
                                    with ui.row().classes("items-center gap-1.5"):
                                        ui.label(act["time"]).classes("text-[11px] text-slate-400 font-medium")
                                        ui.label(act["ticket_id"]).classes("text-xs font-bold text-blue-600 cursor-pointer").on(
                                            "click", lambda tid=act["ticket_id"].replace("#", ""): ui.navigate.to(f"/user/tickets/{tid}")
                                        )
                                    ui.label(act["text"]).classes("text-xs text-slate-700 leading-relaxed")

                # 2. Cần hỗ trợ gấp? (Ưu tiên P1)
                with ui.card().classes("w-full p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    with ui.row().classes("w-full justify-between items-start"):
                        with ui.element("div").classes("w-10 h-10 rounded-xl bg-red-50 text-red-600 flex items-center justify-center"):
                            ui.icon("support_agent").classes("text-xl")
                        with ui.element("span").classes(
                            "px-2.5 py-0.5 rounded-md bg-red-100 text-red-700 text-[10px] font-extrabold uppercase tracking-wider"
                        ):
                            ui.label("Ưu tiên P1")

                    ui.label("Cần hỗ trợ gấp?").classes("text-base font-bold text-slate-900 mt-2")
                    ui.label(
                        "Nếu sự cố mạng diện rộng hoặc máy chủ kế toán ngưng trệ ảnh hưởng giao dịch, liên hệ trực tiếp:"
                    ).classes("text-xs text-slate-500 leading-relaxed mt-0.5")

                    with ui.column().classes("w-full gap-2 mt-3 pt-3 border-t border-slate-100 text-xs"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Máy lẻ nội bộ:").classes("text-slate-500 font-medium")
                            ui.label("1102").classes("text-xl font-extrabold text-blue-700")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Địa điểm:").classes("text-slate-500 font-medium")
                            ui.label("Phòng IT Helpdesk (Tầng 2)").classes("font-semibold text-slate-800")

                    ui.button(
                        "Gửi yêu cầu khẩn cấp",
                        icon="warning",
                        on_click=lambda: ui.navigate.to("/user/tickets/new"),
                    ).props("unelevated no-caps").classes(
                        "w-full mt-4 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 rounded-xl text-xs shadow-md shadow-red-500/20"
                    )

                # 3. Ca trực kỹ thuật hiện tại
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm"):
                    with ui.row().classes("w-full items-center gap-3 no-wrap"):
                        with ui.element("div").classes(
                            "w-12 h-12 rounded-xl bg-slate-100 overflow-hidden flex items-center justify-center shrink-0 border border-slate-200"
                        ):
                            ui.icon("desktop_windows").classes("text-2xl text-slate-500")

                        with ui.column().classes("gap-0.5 flex-1"):
                            ui.label("Ca trực kỹ thuật hiện tại").classes("text-xs font-bold text-slate-900")
                            ui.label("2 kỹ thuật viên thường trực sàn").classes("text-[11px] text-slate-500")
                            with ui.row().classes("items-center gap-1.5 mt-0.5"):
                                ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500")
                                ui.label("Sẵn sàng phản hồi").classes("text-[10px] font-bold text-emerald-700")

    app_shell("Tổng quan", content)
