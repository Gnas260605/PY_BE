from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.layout import app_shell


def render_ticket_dispatch_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro", "TECHNICIAN")

        # -------------------------------------------------------------
        # 1. TOP BREADCRUMB & HEADER
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-center flex-wrap gap-2 text-xs mb-1"):
            with ui.row().classes("items-center gap-1.5 text-slate-500 font-medium"):
                ui.label("Bàn làm việc Kỹ thuật viên").classes("text-slate-500")
                ui.label("›").classes("text-slate-300 font-bold")
                ui.label("Lịch trực & Phân công cá nhân").classes("font-bold text-slate-800")

        with ui.row().classes("w-full justify-between items-start flex-wrap gap-3 mb-2"):
            with ui.column().classes("gap-1"):
                ui.label("Lịch trực, Phân công công việc & Giám sát SLA cá nhân").classes(
                    "text-xl md:text-2xl font-black text-slate-900 tracking-tight"
                )
                with ui.row().classes("items-center gap-2 flex-wrap text-xs"):
                    with ui.element("span").classes(
                        "px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-extrabold text-[11px] flex items-center gap-1.5"
                    ):
                        ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-600 animate-pulse")
                        ui.label("ĐANG TRỰC CA (08:00 - 16:00)")

                    with ui.row().classes("items-center gap-1 font-bold text-slate-800"):
                        ui.icon("verified", size="16px").classes("text-blue-600")
                        ui.label("Nguyễn Văn An (Kỹ thuật viên L2 - Trưởng ca Sáng)")

                    ui.label("• Tải xử lý:").classes("text-slate-400 font-medium")
                    ui.label("5/8 vé").classes("font-bold text-blue-700 font-mono")
                    ui.label("(Còn nhận tối đa 3 vé)").classes("text-slate-500")

            # Right Controls
            with ui.row().classes("items-center gap-2 flex-wrap"):
                with ui.element("div").classes("px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200/80 flex items-center gap-2"):
                    ui.label("Auto-Dispatch Nhận vé tự động:").classes("text-xs font-semibold text-slate-700")
                    ui.switch(value=True).props("dense color=primary")

                with ui.button(
                    "Bàn giao ca trực",
                    icon="sync_alt",
                    on_click=lambda: toast.show("Mở quy trình bàn giao ca trực ISO 20000", type="info"),
                ).props("unelevated dense no-caps").classes(
                    "bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl shadow-xs"
                ):
                    pass

                with ui.button("Đổi ca / Báo vắng", icon="event_busy", on_click=lambda: toast.show("Mở đơn xin đổi ca trực", type="info")).props(
                    "flat dense no-caps"
                ).classes("bg-white border border-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-xl hover:bg-slate-50"):
                    pass

        # -------------------------------------------------------------
        # 2. 4 TOP METRIC CARDS (SLA, FRT, Resolved, Shift Time Left)
        # -------------------------------------------------------------
        with ui.grid(columns=4).classes("w-full gap-3 mb-3"):
            # Metric 1: SLA Tuân thủ
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("SLA Tuân thủ cá nhân").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 flex items-center gap-0.5"):
                        ui.icon("arrow_upward", size="12px")
                        ui.label("+3.2%")
                with ui.column().classes("gap-0.5 mt-1"):
                    with ui.row().classes("items-baseline gap-1"):
                        ui.label("98.2%").classes("text-2xl font-black text-slate-900")
                        ui.label("/ Mục tiêu 95.0%").classes("text-[11px] text-slate-400 font-semibold")
                    ui.label("Vượt chuẩn đội L2 tuần này").classes("text-[11px] text-emerald-600 font-semibold")

            # Metric 2: Phản hồi trung bình FRT
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Phản hồi trung bình (FRT)").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    ui.icon("schedule", size="18px").classes("text-blue-600")
                with ui.column().classes("gap-0.5 mt-1"):
                    ui.label("8.4 phút").classes("text-2xl font-black text-blue-700")
                    with ui.row().classes("items-center gap-1 text-[11px]"):
                        ui.label("Chuẩn SLA: P1 ≤ 15p, P2 ≤ 30p").classes("text-slate-500")
                        with ui.element("span").classes("px-1.5 py-0.2 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700"):
                            ui.label("TỐT")

            # Metric 3: Vé đã xử lý trong ca
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Vé đã xử lý trong ca").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    ui.icon("check_circle", size="18px").classes("text-emerald-600")
                with ui.column().classes("gap-1 mt-1"):
                    with ui.row().classes("items-baseline gap-1"):
                        ui.label("6").classes("text-2xl font-black text-slate-900")
                        ui.label("/ 11 vé tiếp nhận").classes("text-xs text-slate-400 font-semibold")
                    with ui.row().classes("w-full items-center justify-between text-[11px]"):
                        ui.label("Tiến độ ca: 54.5%").classes("text-slate-500 font-medium")
                        ui.label("5 vé còn mở").classes("font-semibold text-blue-600")
                    with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                        ui.element("div").classes("h-full bg-blue-600 rounded-full").style("width: 54.5%")

            # Metric 4: Thời gian còn lại
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Thời gian còn lại của ca").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    ui.element("span").classes("w-2.5 h-2.5 rounded-full bg-emerald-500")
                with ui.column().classes("gap-0.5 mt-1"):
                    ui.label("02h 15m").classes("text-2xl font-black text-slate-900 font-mono")
                    with ui.row().classes("items-center justify-between text-[11px] text-slate-500"):
                        ui.label("Bàn giao cho: Trần Quốc Bảo")
                        with ui.element("span").classes("px-1.5 py-0.2 rounded bg-slate-100 font-mono font-bold text-[10px]"):
                            ui.label("16:00")

        # -------------------------------------------------------------
        # 3. MAIN 2-COLUMN LAYOUT (Left 8 cols: Schedule & Tickets, Right 4 cols: Handover & Policy)
        # -------------------------------------------------------------
        with ui.grid(columns=12).classes("w-full gap-4 items-start"):
            # ================= LEFT COLUMN: 8 COLS =================
            with ui.column().classes("col-span-12 lg:col-span-8 gap-3"):
                # Card: Lịch phân công ca trực tuần này
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-center flex-wrap gap-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("calendar_month", size="18px").classes("text-blue-600")
                            ui.label("Lịch phân công ca trực tuần này").classes("text-xs font-bold text-slate-900")
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-600"):
                                ui.label("Tuần 42 (14/10 - 20/10)")

                        with ui.row().classes("items-center gap-1 text-xs text-slate-500 font-semibold"):
                            ui.icon("chevron_left", size="18px").classes("cursor-pointer hover:text-blue-600")
                            ui.label("Tuần hiện tại")
                            ui.icon("chevron_right", size="18px").classes("cursor-pointer hover:text-blue-600")

                    # 7 Days Grid
                    with ui.grid(columns=7).classes("w-full gap-1.5 text-center text-xs"):
                        # Day 1
                        with ui.element("div").classes("p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between min-h-[90px]"):
                            ui.label("Thứ 2 (14/10)").classes("text-[10px] font-bold text-slate-500")
                            with ui.column().classes("gap-0 my-1"):
                                ui.label("Ca Sáng").classes("font-extrabold text-slate-800 text-[11px]")
                                ui.label("08:00 - 16:00").classes("text-[9px] text-slate-400")
                            ui.label("✓ 14 vé Xong").classes("text-[9px] font-bold text-emerald-600")

                        # Day 2
                        with ui.element("div").classes("p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between min-h-[90px]"):
                            ui.label("Thứ 3 (15/10)").classes("text-[10px] font-bold text-slate-500")
                            with ui.column().classes("gap-0 my-1"):
                                ui.label("Ca Sáng").classes("font-extrabold text-slate-800 text-[11px]")
                                ui.label("08:00 - 16:00").classes("text-[9px] text-slate-400")
                            ui.label("✓ 16 vé Xong").classes("text-[9px] font-bold text-emerald-600")

                        # Day 3 (Hôm nay - Active Blue)
                        with ui.element("div").classes("p-2 rounded-xl bg-blue-600 text-white shadow-md shadow-blue-500/20 flex flex-col justify-between min-h-[90px]"):
                            ui.label("Thứ 4 (Hôm nay)").classes("text-[10px] font-bold text-blue-100")
                            with ui.column().classes("gap-0 my-1"):
                                ui.label("Ca Sáng").classes("font-black text-white text-[12px]")
                                ui.label("08:00 - 16:00").classes("text-[9px] text-blue-200")
                                with ui.element("span").classes("px-1 py-0.2 rounded text-[8px] font-bold bg-white/20 text-white mt-0.5"):
                                    ui.label("TRƯỞNG CA L2")
                            ui.label("Đang trực (5/8 vé)").classes("text-[9px] font-bold text-amber-200")

                        # Day 4
                        with ui.element("div").classes("p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between min-h-[90px]"):
                            ui.label("Thứ 5 (17/10)").classes("text-[10px] font-bold text-slate-500")
                            with ui.column().classes("gap-0 my-1"):
                                ui.label("Ca Chiều").classes("font-extrabold text-slate-800 text-[11px]")
                                ui.label("16:00 - 23:00").classes("text-[9px] text-slate-400")
                            ui.label("KT chính (L2)").classes("text-[9px] text-slate-500")

                        # Day 5
                        with ui.element("div").classes("p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between min-h-[90px]"):
                            ui.label("Thứ 6 (18/10)").classes("text-[10px] font-bold text-slate-500")
                            with ui.column().classes("gap-0 my-1"):
                                ui.label("Ca Sáng").classes("font-extrabold text-slate-800 text-[11px]")
                                ui.label("08:00 - 16:00").classes("text-[9px] text-slate-400")
                            ui.label("Kỹ thuật viên").classes("text-[9px] text-slate-500")

                        # Day 6
                        with ui.element("div").classes("p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between min-h-[90px]"):
                            ui.label("Thứ 7 (19/10)").classes("text-[10px] font-bold text-slate-500")
                            with ui.column().classes("gap-0 my-1"):
                                ui.label("On-call L3").classes("font-bold text-purple-700 text-[11px]")
                                ui.label("Standby tại nhà").classes("text-[9px] text-slate-400")
                            ui.label("Phụ cấp 150%").classes("text-[9px] font-bold text-purple-600")

                        # Day 7
                        with ui.element("div").classes("p-2 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col justify-between min-h-[90px]"):
                            ui.label("Chủ nhật (20/10)").classes("text-[10px] font-bold text-slate-500")
                            with ui.column().classes("gap-0 my-1"):
                                ui.label("Nghỉ ca (Off)").classes("font-bold text-slate-400 text-[11px]")
                                ui.label("Toàn thời gian").classes("text-[9px] text-slate-400")
                            ui.label("Tái tạo năng lượng").classes("text-[9px] text-slate-400")

                # Card: Danh sách vé đang phụ trách & Trạng thái SLA
                with ui.card().classes("w-full p-0 rounded-2xl bg-white border border-slate-200/90 shadow-xs overflow-hidden"):
                    # Top toolbar
                    with ui.row().classes("w-full justify-between items-center p-3.5 border-b border-slate-100 bg-slate-50/50"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("assignment", size="18px").classes("text-blue-600")
                            ui.label("Danh sách vé đang phụ trách & Trạng thái SLA").classes("text-xs font-bold text-slate-900")
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700"):
                                ui.label("5 ĐANG MỞ")

                        with ui.row().classes("items-center gap-1.5 text-xs"):
                            ui.label("Lọc nhanh:").classes("text-slate-400 font-semibold")
                            ui.button("Tất cả (5)").props("unelevated dense no-caps").classes(
                                "bg-slate-900 text-white font-bold text-xs px-2.5 py-0.5 rounded-lg"
                            )
                            with ui.button("Nguy cơ SLA (1)", icon="error").props("flat dense no-caps").classes(
                                "bg-rose-50 text-rose-700 font-bold text-xs px-2.5 py-0.5 rounded-lg"
                            ):
                                pass

                    # Table Header
                    with ui.grid(columns=12).classes("w-full px-4 py-2 bg-slate-100/70 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200/70"):
                        ui.label("MÃ & NỘI DUNG SỰ CỐ").classes("col-span-4")
                        ui.label("ƯU TIÊN").classes("col-span-2 text-center")
                        ui.label("DANH MỤC").classes("col-span-2")
                        ui.label("TIẾP NHẬN").classes("col-span-1 text-center")
                        ui.label("SLA CÒN LẠI").classes("col-span-2")
                        ui.label("THAO TÁC").classes("col-span-1 text-right")

                    # Row 1: #1048 (P1 Khẩn cấp)
                    with ui.grid(columns=12).classes("w-full px-4 py-3 items-center border-b border-slate-100 bg-rose-50/20 hover:bg-rose-50/40 transition-colors text-xs"):
                        with ui.column().classes("col-span-4 gap-0"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.label("#1048").classes("font-mono font-bold text-blue-600 text-[11px]")
                                ui.label("Lỗi Print Spooler Tầng 4").classes("font-extrabold text-slate-900 text-xs")
                            ui.label("Phòng Kế toán tài chính • 12 người ảnh hưởng").classes("text-[10px] text-slate-500")

                        with ui.element("div").classes("col-span-2 text-center"):
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-extrabold bg-rose-100 text-rose-700"):
                                ui.label("P1 - KHẨN CẤP")

                        ui.label("Máy trạm & Ngoại vi").classes("col-span-2 text-[11px] text-slate-700 font-medium")
                        ui.label("11:42 (Ca sáng)").classes("col-span-1 text-center text-[10px] text-slate-500 font-mono")

                        with ui.column().classes("col-span-2 gap-1"):
                            with ui.row().classes("items-center gap-1 text-rose-600 font-bold text-[11px]"):
                                ui.icon("warning", size="13px")
                                ui.label("Còn 18 phút")
                            with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-200 overflow-hidden"):
                                ui.element("div").classes("h-full bg-rose-600 rounded-full").style("width: 85%")

                        with ui.element("div").classes("col-span-1 text-right"):
                            with ui.button("Xử lý ngay", on_click=lambda: ui.navigate.to("/technician/detail/1048")).props(
                                "unelevated dense no-caps"
                            ).classes("bg-blue-600 hover:bg-blue-700 text-white font-bold text-[11px] px-2.5 py-1 rounded-lg shadow-xs"):
                                pass

                    # Row 2: #1052
                    with ui.grid(columns=12).classes("w-full px-4 py-3 items-center border-b border-slate-100 hover:bg-slate-50/80 transition-colors text-xs"):
                        with ui.column().classes("col-span-4 gap-0"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.label("#1052").classes("font-mono font-bold text-blue-600 text-[11px]")
                                ui.label("Cấp quyền truy cập VPN SAP").classes("font-extrabold text-slate-900 text-xs")
                            ui.label("Lê Thị Mai - QL Kho vận").classes("text-[10px] text-slate-500")

                        with ui.element("div").classes("col-span-2 text-center"):
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-extrabold bg-blue-100 text-blue-700"):
                                ui.label("P2 - CAO")

                        ui.label("Mạng & Bảo mật").classes("col-span-2 text-[11px] text-slate-700 font-medium")
                        ui.label("13:05 (Hôm nay)").classes("col-span-1 text-center text-[10px] text-slate-500 font-mono")

                        with ui.column().classes("col-span-2 gap-1"):
                            ui.label("Còn 1h 40m").classes("text-blue-700 font-bold text-[11px]")
                            with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                                ui.element("div").classes("h-full bg-blue-600 rounded-full").style("width: 60%")

                        with ui.element("div").classes("col-span-1 text-right"):
                            with ui.button("Cập nhật", on_click=lambda: toast.show("Mở cập nhật vé #1052", type="info")).props(
                                "flat dense no-caps text-color=slate-700"
                            ).classes("bg-slate-100 hover:bg-slate-200 font-semibold text-[11px] px-2 py-1 rounded-lg"):
                                pass

                    # Row 3: #1053
                    with ui.grid(columns=12).classes("w-full px-4 py-3 items-center border-b border-slate-100 hover:bg-slate-50/80 transition-colors text-xs"):
                        with ui.column().classes("col-span-4 gap-0"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.label("#1053").classes("font-mono font-bold text-blue-600 text-[11px]")
                                ui.label("Cảnh báo ổ đĩa Backup NAS").classes("font-extrabold text-slate-900 text-xs")
                            ui.label("Hạ tầng máy chủ trung tâm dữ liệu").classes("text-[10px] text-slate-500")

                        with ui.element("div").classes("col-span-2 text-center"):
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-extrabold bg-blue-100 text-blue-700"):
                                ui.label("P2 - CAO")

                        ui.label("Hạ tầng & Cloud").classes("col-span-2 text-[11px] text-slate-700 font-medium")
                        ui.label("13:20 (Hôm nay)").classes("col-span-1 text-center text-[10px] text-slate-500 font-mono")

                        with ui.column().classes("col-span-2 gap-1"):
                            ui.label("Còn 2h 15m").classes("text-blue-700 font-bold text-[11px]")
                            with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                                ui.element("div").classes("h-full bg-blue-600 rounded-full").style("width: 50%")

                        with ui.element("div").classes("col-span-1 text-right"):
                            with ui.button("Cập nhật", on_click=lambda: toast.show("Mở cập nhật vé #1053", type="info")).props(
                                "flat dense no-caps text-color=slate-700"
                            ).classes("bg-slate-100 hover:bg-slate-200 font-semibold text-[11px] px-2 py-1 rounded-lg"):
                                pass

                    # Row 4: #1055
                    with ui.grid(columns=12).classes("w-full px-4 py-3 items-center border-b border-slate-100 hover:bg-slate-50/80 transition-colors text-xs"):
                        with ui.column().classes("col-span-4 gap-0"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.label("#1055").classes("font-mono font-bold text-blue-600 text-[11px]")
                                ui.label("Thay thế bộ bàn phím, chuột").classes("font-extrabold text-slate-900 text-xs")
                            ui.label("Trần Hoàng Yến - Marketing Team").classes("text-[10px] text-slate-500")

                        with ui.element("div").classes("col-span-2 text-center"):
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700"):
                                ui.label("P3 - TIÊU CHUẨN")

                        ui.label("Phần cứng Endpoint").classes("col-span-2 text-[11px] text-slate-700 font-medium")
                        ui.label("14:10 (Hôm nay)").classes("col-span-1 text-center text-[10px] text-slate-500 font-mono")

                        with ui.column().classes("col-span-2 gap-1"):
                            ui.label("Còn 3h 15m").classes("text-emerald-700 font-bold text-[11px]")
                            with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                                ui.element("div").classes("h-full bg-emerald-500 rounded-full").style("width: 40%")

                        with ui.element("div").classes("col-span-1 text-right"):
                            with ui.button("Cập nhật", on_click=lambda: toast.show("Mở cập nhật vé #1055", type="info")).props(
                                "flat dense no-caps text-color=slate-700"
                            ).classes("bg-slate-100 hover:bg-slate-200 font-semibold text-[11px] px-2 py-1 rounded-lg"):
                                pass

                    # Row 5: #1058
                    with ui.grid(columns=12).classes("w-full px-4 py-3 items-center border-b border-slate-100 hover:bg-slate-50/80 transition-colors text-xs"):
                        with ui.column().classes("col-span-4 gap-0"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.label("#1058").classes("font-mono font-bold text-blue-600 text-[11px]")
                                ui.label("Cài đặt bộ Office 365 máy n...").classes("font-extrabold text-slate-900 text-xs")
                            ui.label("Nhân sự thử việc - Phòng Pháp chế").classes("text-[10px] text-slate-500")

                        with ui.element("div").classes("col-span-2 text-center"):
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700"):
                                ui.label("P3 - TIÊU CHUẨN")

                        ui.label("Phần mềm văn phòng").classes("col-span-2 text-[11px] text-slate-700 font-medium")
                        ui.label("14:35 (Hôm nay)").classes("col-span-1 text-center text-[10px] text-slate-500 font-mono")

                        with ui.column().classes("col-span-2 gap-1"):
                            ui.label("Còn 5h 20m").classes("text-emerald-700 font-bold text-[11px]")
                            with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                                ui.element("div").classes("h-full bg-emerald-500 rounded-full").style("width: 30%")

                        with ui.element("div").classes("col-span-1 text-right"):
                            with ui.button("Cập nhật", on_click=lambda: toast.show("Mở cập nhật vé #1058", type="info")).props(
                                "flat dense no-caps text-color=slate-700"
                            ).classes("bg-slate-100 hover:bg-slate-200 font-semibold text-[11px] px-2 py-1 rounded-lg"):
                                pass

                    # Table footer
                    with ui.row().classes("w-full justify-between items-center px-4 py-3 bg-slate-50/50 text-xs text-slate-500"):
                        ui.label("Hiển thị 5 trên 5 sự cố cần xử lý")
                        with ui.link("Xem lịch sử vé đã đóng hôm nay (6) →", "#").classes("text-blue-600 font-bold no-underline hover:underline"):
                            pass

            # ================= RIGHT COLUMN: 4 COLS =================
            with ui.column().classes("col-span-12 lg:col-span-4 gap-3"):
                # Card 1: Bàn giao ca trực (ISO 20000)
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("swap_horiz", size="18px").classes("text-blue-600")
                            ui.label("Bàn giao ca trực").classes("text-xs font-bold text-slate-900")
                        with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-600"):
                            ui.label("Chuẩn ISO 20000")

                    # Handover Participants Box
                    with ui.row().classes("w-full items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-200/80"):
                        with ui.row().classes("items-center gap-2"):
                            with ui.element("div").classes("w-7 h-7 rounded-lg bg-blue-600 text-white font-bold text-xs flex items-center justify-center"):
                                ui.label("AN")
                            with ui.column().classes("gap-0"):
                                ui.label("Nguyễn Văn An").classes("font-bold text-xs text-slate-900")
                                ui.label("Bàn giao (Ca sáng)").classes("text-[10px] text-slate-500")

                        ui.icon("arrow_forward", size="16px").classes("text-slate-400")

                        with ui.row().classes("items-center gap-2"):
                            with ui.element("div").classes("w-7 h-7 rounded-lg bg-indigo-600 text-white font-bold text-xs flex items-center justify-center"):
                                ui.label("BẢO")
                            with ui.column().classes("gap-0"):
                                ui.label("Trần Quốc Bảo").classes("font-bold text-xs text-slate-900")
                                ui.label("Tiếp nhận (Ca chiều)").classes("text-[10px] text-slate-500")

                    # Critical handover notices
                    with ui.column().classes("w-full p-2.5 rounded-xl bg-amber-50/70 border border-amber-200/70 gap-1"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("2 vé trọng điểm cần chú ý:").classes("text-xs font-bold text-amber-900")
                            with ui.element("span").classes("px-1.5 py-0.2 rounded text-[9px] font-extrabold bg-amber-200 text-amber-900"):
                                ui.label("CẦN FOLLOW")

                        with ui.row().classes("items-start gap-1 text-[11px] text-amber-950"):
                            ui.label("! #1048:").classes("font-bold text-rose-600 font-mono")
                            ui.label("Đang ping kiểm tra ACL Switch tầng 4. SLA còn 18p.").classes("leading-tight")

                        with ui.row().classes("items-start gap-1 text-[11px] text-amber-950"):
                            ui.label("ℹ #1053:").classes("font-bold text-blue-600 font-mono")
                            ui.label("Cần rà soát cronjob backup NAS lúc 17:00.").classes("leading-tight")

                    # Handover text note
                    with ui.column().classes("w-full gap-1 text-xs"):
                        ui.label("Ghi chú bàn giao nhanh (Shift Handover Note):").classes("font-semibold text-slate-700")
                        ui.textarea(
                            placeholder="Nhập tóm tắt hiện trạng thiết bị phòng server, chìa khóa tủ rack hoặc lưu ý ca kế tiếp..."
                        ).props("outlined autogrow dense").classes("w-full text-xs")

                    # Handover Checkboxes
                    with ui.column().classes("w-full gap-1.5 pt-1 text-xs"):
                        ui.checkbox("Đã cập nhật ghi chú nội bộ toàn bộ 5 vé", value=True).props("dense color=primary")
                        ui.checkbox("Đã bàn giao điện thoại Hotline khẩn cấp", value=True).props("dense color=primary")
                        ui.checkbox("Ký điện tử xác nhận bàn giao giữa 2 bên", value=False).props("dense color=primary")

                    with ui.button(
                        "Ký nhận bàn giao ca (16:00)",
                        icon="draw",
                        on_click=lambda: toast.show("Đã ký xác nhận biên bản bàn giao ca trực!", type="positive"),
                    ).props("unelevated no-caps").classes(
                        "w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2 rounded-xl shadow-xs"
                    ):
                        pass

                # Card 2: Quy định Cam kết SLA
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("verified", size="18px").classes("text-blue-600")
                            ui.label("Quy định Cam kết SLA").classes("text-xs font-bold text-slate-900")
                        with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700"):
                            ui.label("Kỹ năng của bạn")

                    ui.label("Chỉ tiêu cam kết chất lượng dịch vụ nội bộ dựa trên hồ sơ chứng chỉ và phân nhóm chuyên môn:").classes(
                        "text-[11px] text-slate-500 leading-tight"
                    )

                    # Rule 1
                    with ui.element("div").classes("p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1"):
                        with ui.row().classes("w-full justify-between items-center text-xs"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.icon("lan", size="16px").classes("text-blue-600")
                                ui.label("Mạng & Hạ tầng (Network/VPN)").classes("font-bold text-slate-800")
                            with ui.element("span").classes("font-mono font-bold text-blue-700 text-[10px]"):
                                ui.label("FRT ≤ 15m")
                        with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-500"):
                            ui.label("Chứng chỉ: CCNA, Fortinet")
                            ui.label("MTTR ≤ 2h").classes("font-mono font-semibold")

                    # Rule 2
                    with ui.element("div").classes("p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1"):
                        with ui.row().classes("w-full justify-between items-center text-xs"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.icon("devices", size="16px").classes("text-indigo-600")
                                ui.label("Máy trạm & Ngoại vi (Endpoint)").classes("font-bold text-slate-800")
                            with ui.element("span").classes("font-mono font-bold text-indigo-700 text-[10px]"):
                                ui.label("FRT ≤ 30m")
                        with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-500"):
                            ui.label("Phần cứng, Windows, macOS")
                            ui.label("MTTR ≤ 4h").classes("font-mono font-semibold")

                    # Rule 3
                    with ui.element("div").classes("p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1"):
                        with ui.row().classes("w-full justify-between items-center text-xs"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.icon("key", size="16px").classes("text-emerald-600")
                                ui.label("Tài khoản & ERP (AD / SAP)").classes("font-bold text-slate-800")
                            with ui.element("span").classes("font-mono font-bold text-emerald-700 text-[10px]"):
                                ui.label("FRT ≤ 1h")
                        with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-500"):
                            ui.label("Phân quyền, Reset OTP")
                            ui.label("MTTR ≤ 8h").classes("font-mono font-semibold")

                    # Footer
                    with ui.row().classes("w-full justify-between items-center pt-2 border-t border-slate-100 text-[10px] text-slate-400"):
                        with ui.link("Xem sổ tay Quy chuẩn ITIL v4", "#").classes("text-blue-600 font-bold no-underline hover:underline"):
                            pass
                        ui.label("Phiên bản: 2024.3")

    app_shell("Quản lý phân công & SLA", content)
