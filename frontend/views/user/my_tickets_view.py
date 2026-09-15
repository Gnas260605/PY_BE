from __future__ import annotations

from nicegui import ui

from common.components.layout import app_shell
from views.user.demo_data import DEMO_TICKETS


def render_my_tickets_view() -> None:
    def content(user: dict) -> None:
        # State
        tickets_data = list(DEMO_TICKETS)
        selected_status = "ALL"
        selected_priority = "ALL"
        selected_category = "ALL"

        # -------------------------------------------------------------
        # 1. BREADCRUMB & HEADER
        # -------------------------------------------------------------
        with ui.column().classes("w-full gap-2 pt-0"):
            # Breadcrumb
            with ui.row().classes("items-center gap-2 text-xs text-slate-400"):
                ui.link("Trang chủ", "/dashboard").classes("text-slate-400 hover:text-blue-600 no-underline")
                ui.label("/")
                ui.label("Ticket của tôi").classes("text-slate-700 font-semibold")

            # Title Row
            with ui.row().classes("w-full justify-between items-center flex-wrap gap-4"):
                with ui.column().classes("gap-1"):
                    with ui.row().classes("items-center gap-2.5"):
                        ui.label("Ticket của tôi").classes(
                            "text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight"
                        )
                        with ui.element("span").classes(
                            "px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold leading-tight"
                        ):
                            ui.label("24 ticket")

                    ui.label(
                        "Theo dõi, quản lý và kiểm tra tiến độ toàn bộ yêu cầu hỗ trợ IT của bạn với thông tin phản hồi thời gian thực."
                    ).classes("text-xs md:text-sm text-slate-500")

                ui.button(
                    "Tạo yêu cầu mới",
                    icon="add",
                    on_click=lambda: ui.navigate.to("/user/tickets/new"),
                ).props("unelevated no-caps").classes(
                    "bg-blue-600 hover:bg-blue-700 text-white font-bold px-5 py-2.5 rounded-xl text-xs shadow-md shadow-blue-500/20"
                )

        # -------------------------------------------------------------
        # 2. 4 STAT SUMMARY CARDS (Image 2)
        # -------------------------------------------------------------
        with ui.element("div").classes("grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full mt-2"):
            # Card 1: Chờ phân công
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Chờ phân công").classes("text-xs font-bold text-slate-700")
                    ui.icon("schedule").classes("text-blue-600 text-base")
                ui.label("1").classes("text-2xl font-extrabold text-slate-900 my-1")
                ui.label("cần tiếp nhận").classes("text-[11px] text-slate-400 font-medium")

            # Card 2: Đang xử lý
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Đang xử lý").classes("text-xs font-bold text-slate-700")
                    ui.icon("sync").classes("text-slate-400 text-base")
                ui.label("2").classes("text-2xl font-extrabold text-slate-900 my-1")
                with ui.column().classes("w-full gap-1 mt-0.5"):
                    ui.label("đang hoạt động").classes("text-[11px] text-slate-400 font-medium")
                    with ui.element("div").classes("w-full h-1 bg-slate-100 rounded-full overflow-hidden"):
                        ui.element("div").classes("w-1/2 h-full bg-blue-600 rounded-full")

            # Card 3: Đã giải quyết
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Đã giải quyết").classes("text-xs font-bold text-slate-700")
                    ui.icon("check_circle").classes("text-emerald-600 text-base")
                ui.label("8").classes("text-2xl font-extrabold text-slate-900 my-1")
                with ui.column().classes("w-full gap-1 mt-0.5"):
                    ui.label("thành công").classes("text-[11px] text-slate-400 font-medium")
                    with ui.element("div").classes("w-full h-1 bg-slate-100 rounded-full overflow-hidden"):
                        ui.element("div").classes("w-4/5 h-full bg-emerald-500 rounded-full")

            # Card 4: Thời gian xử lý TB
            with ui.card().classes(
                "w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between"
            ):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Thời gian xử lý TB").classes("text-xs font-bold text-slate-700")
                    ui.icon("schedule").classes("text-slate-400 text-base")
                with ui.row().classes("items-baseline gap-1.5 my-1"):
                    ui.label("2.4h").classes("text-2xl font-extrabold text-slate-900")
                    ui.label("↘ 18%").classes("text-xs font-bold text-emerald-600")
                with ui.element("div").classes("w-full h-1 bg-slate-100 rounded-full overflow-hidden mt-0.5"):
                    ui.element("div").classes("w-1/3 h-full bg-slate-700 rounded-full")

        # -------------------------------------------------------------
        # 3. FILTER & SEARCH TOOLBAR (Image 2)
        # -------------------------------------------------------------
        with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm mt-3"):
            # Top row: Search input + Sort + Reset
            with ui.row().classes("w-full justify-between items-center flex-wrap gap-3 pb-3 border-b border-slate-100"):
                search_input = (
                    ui.input(placeholder="Tìm kiếm theo mã ticket, tiêu đề, thiết bị...       Ctrl + /")
                    .props("outlined dense")
                    .classes("flex-1 min-w-[280px] bg-slate-50 text-xs rounded-xl")
                )
                search_input.add_slot(
                    "prepend",
                    '<i class="q-icon material-icons text-slate-400 text-base">search</i>',
                )

                with ui.row().classes("items-center gap-3"):
                    with ui.row().classes("items-center gap-2 text-xs text-slate-600"):
                        ui.label("Sắp xếp:")
                        sort_select = ui.select(
                            ["Cập nhật mới nhất", "Mới nhất", "Cũ nhất", "Ưu tiên cao nhất"],
                            value="Cập nhật mới nhất",
                        ).props("outlined dense options-dense").classes("w-44 text-xs")

                    with ui.button("Xóa bộ lọc", icon="filter_list_off").props("flat dense no-caps").classes(
                        "text-xs font-semibold text-slate-500 hover:text-slate-800"
                    ):
                        pass

            # Bottom row: Dropdown filters & Active tags
            with ui.row().classes("w-full justify-between items-center flex-wrap gap-3 pt-2 text-xs"):
                with ui.row().classes("items-center gap-3 flex-wrap"):
                    status_filter = ui.select(
                        ["Tất cả (24)", "Mới mở", "Đang xử lý", "Đã tiếp nhận", "Đã giải quyết", "Đã đóng"],
                        value="Tất cả (24)",
                        label="Trạng thái",
                    ).props("outlined dense options-dense").classes("w-40 text-xs")

                    priority_filter = ui.select(
                        ["Tất cả", "Khẩn cấp", "Cao", "Trung bình", "Thấp"],
                        value="Tất cả",
                        label="Mức độ ưu tiên",
                    ).props("outlined dense options-dense").classes("w-40 text-xs")

                    category_filter = ui.select(
                        ["Tất cả", "Sự cố", "Yêu cầu dịch vụ", "Bảo trì"],
                        value="Tất cả",
                        label="Phân loại",
                    ).props("outlined dense options-dense").classes("w-40 text-xs")

                # Active Applied Chips
                with ui.row().classes("items-center gap-2 text-xs text-slate-500"):
                    ui.label("Đang áp dụng:").classes("font-medium")
                    with ui.element("div").classes(
                        "px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-medium flex items-center gap-1.5"
                    ):
                        ui.label("Toàn bộ phòng ban")
                        ui.icon("close").classes("text-slate-400 text-xs cursor-pointer")
                    with ui.element("div").classes(
                        "px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-medium flex items-center gap-1.5"
                    ):
                        ui.label("Năm 2026")
                        ui.icon("close").classes("text-slate-400 text-xs cursor-pointer")

        # -------------------------------------------------------------
        # 4. TICKET TABLE LIST (Image 2)
        # -------------------------------------------------------------
        table_card = ui.card().classes("w-full p-0 rounded-2xl bg-white border border-slate-200/80 shadow-sm mt-3 overflow-hidden")
        with table_card:
            # Header Row
            with ui.row().classes(
                "w-full bg-slate-50/90 px-5 py-3 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider items-center no-wrap"
            ):
                ui.label("MÃ & TIÊU ĐỀ").classes("w-64 md:w-72 shrink-0")
                ui.label("PHÂN LOẠI").classes("w-36 shrink-0")
                ui.label("MỨC ĐỘ").classes("w-28 shrink-0")
                ui.label("TRẠNG THÁI").classes("w-32 shrink-0")
                ui.label("KỸ THUẬT VIÊN").classes("w-44 shrink-0")
                ui.label("CẬP NHẬT").classes("w-40 shrink-0")
                ui.label("THAO TÁC").classes("flex-1 text-right")

            # Data Rows
            rows_container = ui.column().classes("w-full p-0 gap-0 divide-y divide-slate-100")

            def render_rows():
                rows_container.clear()
                with rows_container:
                    for ticket in tickets_data:
                        t_id = ticket["id"]
                        dot_color = (
                            "bg-red-500"
                            if ticket["priority_code"] == "URGENT"
                            else (
                                "bg-emerald-500"
                                if ticket["status_code"] == "RESOLVED"
                                else ("bg-blue-500" if ticket["status_code"] == "IN_PROGRESS" else "bg-slate-300")
                            )
                        )

                        with ui.row().classes(
                            "w-full px-5 py-3.5 hover:bg-slate-50/80 transition-colors items-center no-wrap text-xs"
                        ):
                            # Col 1: Mã & Tiêu đề
                            with ui.row().classes("w-64 md:w-72 items-start gap-2.5 shrink-0 no-wrap"):
                                with ui.element("span").classes(f"w-2 h-2 rounded-full {dot_color} mt-1.5 shrink-0"):
                                    pass
                                with ui.column().classes("gap-0.5 overflow-hidden"):
                                    with ui.row().classes("items-center gap-1.5"):
                                        ui.label(f"#{t_id}").classes("font-extrabold text-blue-600 text-xs")
                                        if ticket.get("category_sub"):
                                            ui.label(ticket["category_sub"]).classes(
                                                "text-[10px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-500 font-medium"
                                            )
                                    ui.label(ticket["title"]).classes(
                                        "font-bold text-slate-800 line-clamp-1 leading-snug cursor-pointer hover:text-blue-600"
                                    ).on("click", lambda tid=t_id: ui.navigate.to(f"/user/tickets/{tid}"))
                                    ui.label(f"Mã thiết bị: {ticket['device_code']}").classes(
                                        "text-[10px] text-slate-400 font-mono"
                                    )

                            # Col 2: Phân loại
                            with ui.row().classes("w-36 items-center gap-1.5 shrink-0"):
                                icon_cat = "warning" if ticket["category_code"] == "INCIDENT" else "assignment"
                                ui.icon(icon_cat).classes(
                                    "text-sm " + ("text-red-500" if ticket["category_code"] == "INCIDENT" else "text-blue-500")
                                )
                                ui.label(ticket["category_label"]).classes("font-medium text-slate-700")

                            # Col 3: Mức độ
                            with ui.row().classes("w-28 items-center shrink-0"):
                                if ticket["priority_code"] == "URGENT":
                                    ui.label("Khẩn cấp").classes(
                                        "text-[11px] font-bold px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200"
                                    )
                                elif ticket["priority_code"] == "HIGH":
                                    ui.label("Cao").classes(
                                        "text-[11px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200"
                                    )
                                elif ticket["priority_code"] == "MEDIUM":
                                    ui.label("Trung bình").classes(
                                        "text-[11px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700"
                                    )
                                else:
                                    ui.label("Thấp").classes(
                                        "text-[11px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-500"
                                    )

                            # Col 4: Trạng thái
                            with ui.row().classes("w-32 items-center gap-1.5 shrink-0"):
                                if ticket["status_code"] == "IN_PROGRESS":
                                    ui.label("● Đang xử lý").classes(
                                        "text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700"
                                    )
                                elif ticket["status_code"] == "ASSIGNED":
                                    ui.label("● Đã tiếp nhận").classes(
                                        "text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700"
                                    )
                                elif ticket["status_code"] == "RESOLVED":
                                    ui.label("● Đã giải quyết").classes(
                                        "text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700"
                                    )
                                elif ticket["status_code"] == "CLOSED":
                                    ui.label("● Đã đóng").classes(
                                        "text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600"
                                    )
                                else:
                                    ui.label("● Mới mở").classes(
                                        "text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700"
                                    )

                            # Col 5: Kỹ thuật viên
                            with ui.row().classes("w-44 items-center gap-2 shrink-0"):
                                if ticket.get("tech_name") == "Chờ phân công":
                                    ui.label("Chờ phân công").classes("text-xs text-slate-400 italic")
                                else:
                                    with ui.element("div").classes(
                                        "w-7 h-7 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-[10px] shrink-0"
                                    ):
                                        ui.label((ticket.get("tech_initial") or "KT")[:2])
                                    with ui.column().classes("gap-0 overflow-hidden"):
                                        ui.label(ticket["tech_name"]).classes("text-xs font-bold text-slate-800 truncate")
                                        ui.label(ticket.get("tech_title", "IT Helpdesk")).classes("text-[10px] text-slate-400 truncate")

                            # Col 6: Cập nhật
                            with ui.column().classes("w-40 gap-0 shrink-0"):
                                ui.label(ticket["updated_time"]).classes("text-xs font-semibold text-slate-700")
                                ui.label(ticket.get("updated_note", "")).classes("text-[10px] text-slate-400 truncate")

                            # Col 7: Thao tác
                            with ui.row().classes("flex-1 justify-end items-center gap-2"):
                                if ticket["status_code"] == "OPEN":
                                    with ui.button(
                                        "Chỉnh sửa",
                                        on_click=lambda tid=t_id: ui.navigate.to(f"/user/tickets/{tid}"),
                                    ).props("flat dense no-caps").classes(
                                        "text-xs font-semibold text-slate-600 hover:text-slate-900 px-2 py-1 rounded-lg"
                                    ):
                                        pass
                                with ui.button(
                                    "Xem chi tiết",
                                    on_click=lambda tid=t_id: ui.navigate.to(f"/user/tickets/{tid}"),
                                ).props("flat dense no-caps").classes(
                                    "text-xs font-bold text-blue-600 bg-blue-50/70 hover:bg-blue-100 px-3 py-1 rounded-lg"
                                ):
                                    pass

            render_rows()

        # -------------------------------------------------------------
        # 5. PAGINATION (Image 2)
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-center py-3 px-1 flex-wrap gap-3 text-xs"):
            with ui.row().classes("items-center gap-3 text-slate-500 font-medium"):
                ui.label("Hiển thị 1 - 5 trong số 24 ticket")
                ui.select(["10 ticket / trang", "20 ticket / trang", "50 ticket / trang"], value="10 ticket / trang").props(
                    "outlined dense options-dense"
                ).classes("w-36 text-xs")

            # Page buttons [< 1 2 3 ... 5 >]
            with ui.row().classes("items-center gap-1"):
                ui.button(icon="chevron_left").props("flat dense round color=slate-400")
                ui.button("1").props("unelevated dense color=primary").classes("w-7 h-7 font-bold rounded-lg text-xs")
                ui.button("2").props("flat dense color=slate-600").classes("w-7 h-7 rounded-lg text-xs")
                ui.button("3").props("flat dense color=slate-600").classes("w-7 h-7 rounded-lg text-xs")
                ui.label("...").classes("px-1 text-slate-400")
                ui.button("5").props("flat dense color=slate-600").classes("w-7 h-7 rounded-lg text-xs")
                ui.button(icon="chevron_right").props("flat dense round color=slate-400")

        # -------------------------------------------------------------
        # 6. BOTTOM HOTLINE BANNER (Image 2)
        # -------------------------------------------------------------
        with ui.card().classes(
            "w-full p-4 rounded-2xl bg-blue-50/60 border border-blue-100 flex flex-col md:flex-row md:items-center md:justify-between gap-4 mt-2"
        ):
            with ui.row().classes("items-center gap-3.5"):
                with ui.element("div").classes(
                    "w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center shrink-0"
                ):
                    ui.icon("headset_mic").classes("text-xl")
                with ui.column().classes("gap-0"):
                    ui.label("Cần hỗ trợ khẩn cấp tại chỗ?").classes("text-xs font-bold text-slate-900")
                    ui.label(
                        "Liên hệ trực tiếp bàn tiếp nhận IT Helpdesk tại Tầng 2 hoặc Hotline nội bộ #8888"
                    ).classes("text-xs text-slate-600")

            ui.button("Gọi hỗ trợ nội bộ", icon="call", on_click=lambda: ui.notify("Hotline nội bộ IT Helpdesk: #8888", type="info")).props(
                "outline color=primary no-caps dense"
            ).classes("px-4 py-2 rounded-xl text-xs font-bold bg-white")

    app_shell("Ticket của tôi", content)
