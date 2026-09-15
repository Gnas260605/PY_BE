from __future__ import annotations

from datetime import datetime
from nicegui import ui

from common.components import toast
from common.components.layout import app_shell


def render_task_board_view(ticket_id: int = 1048) -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro", "TECHNICIAN")

        # -------------------------------------------------------------
        # 0. LOCAL INTERACTIVE STATE
        # -------------------------------------------------------------
        ticket_state = {
            "id": ticket_id,
            "status": "ĐANG XỬ LÝ",
            "is_resolved": False,
            "sla_time_left": "Còn 18 phút",
            "resolution_summary": (
                "Đã truy cập Switch SW-T4-A via SSH, cập nhật lại ACL rules cho phép lưu lượng "
                "Port 9100 từ Subnet Kế toán 192.168.4.0/24 đến IP máy in 192.168.4.155. "
                "Khởi động lại Spooler service trên máy in và in thử thành công trang test page."
            ),
        }

        timeline_events = [
            {
                "author": "Nguyễn Văn An (KTV L2 - Bạn)",
                "time": "14:15 • 13 phút trước",
                "badge": "HÀNH ĐỘNG",
                "badge_color": "bg-blue-100 text-blue-700",
                "dot_color": "bg-blue-600",
                "content": (
                    "Đã SSH vào Switch SW-T4-A, kiểm tra lại ACL rules và đẩy cấu hình mở Port 9100 "
                    "cho Subnet 192.168.4.0/24. Khởi động lại dịch vụ Print Spooler qua PowerShell script từ xa."
                ),
            },
            {
                "author": "Hệ thống Tự động (HelpDesk Bot)",
                "time": "13:50 • 38 phút trước",
                "badge": "SLA MET",
                "badge_color": "bg-emerald-100 text-emerald-700",
                "dot_color": "bg-emerald-500",
                "content": (
                    "Đã gửi phản hồi đầu tiên thành công tới người dùng lúc 13:50 "
                    "(Mất 8 phút, đạt chuẩn SLA cam kết < 30 phút)."
                ),
            },
            {
                "author": "Trần Thị Mai (Người yêu cầu)",
                "time": "13:42 • 46 phút trước",
                "badge": "TẠO VÉ",
                "badge_color": "bg-slate-100 text-slate-700",
                "dot_color": "bg-slate-400",
                "content": (
                    "Khởi tạo yêu cầu qua cổng Portal: Báo lỗi máy in phòng Kế toán không kết nối được mạng Wi-Fi "
                    "& Báo lỗi kẹt lệnh in SPOOLER."
                ),
            },
        ]

        # -------------------------------------------------------------
        # DIALOG: GIẢI QUYẾT VÉ (IMAGE 2)
        # -------------------------------------------------------------
        with ui.dialog() as resolve_dialog, ui.card().classes(
            "w-full max-w-2xl p-6 rounded-3xl bg-white shadow-2xl border border-slate-100 space-y-4"
        ):
            with ui.column().classes("w-full gap-3"):
                # Header & Root Cause Category
                with ui.row().classes("w-full justify-between items-center no-wrap"):
                    ui.label("Mã nguyên nhân gốc (Root Cause Category) *").classes(
                        "text-xs font-bold text-slate-900"
                    )
                    with ui.element("span").classes(
                        "text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-500"
                    ):
                        ui.label("ISO/IEC 20000")

                root_cause_select = (
                    ui.select(
                        options=[
                            "Lỗi cấu hình mạng / Cổng Port Switch (Network Configuration - Port ACL Drop)",
                            "Lỗi phần cứng máy in / Kẹt cơ học (Hardware Failure - Roller / Spooler)",
                            "Lỗi phần mềm trình điều khiển máy in (Driver / Spooler Service Crash)",
                            "Lỗi phân quyền người dùng (Active Directory / Access Denied)",
                        ],
                        value="Lỗi cấu hình mạng / Cổng Port Switch (Network Configuration - Port ACL Drop)",
                    )
                    .props("outlined dense")
                    .classes("w-full text-xs")
                )
                ui.label(
                    "Phân loại này giúp hệ sinh thái ITAM tự động phân tích tỷ lệ lỗi lặp lại trong kỳ."
                ).classes("text-[11px] text-slate-400 -mt-1")

                # Resolution Summary Textarea
                with ui.row().classes("w-full justify-between items-center mt-1"):
                    ui.label("Hành động khắc phục đã thực hiện (Resolution Summary) *").classes(
                        "text-xs font-bold text-slate-900"
                    )
                    with ui.row().classes("items-center gap-1 text-[11px] font-semibold text-emerald-600"):
                        ui.icon("check_circle", size="14px")
                        ui.label("Đã xác thực thực địa")

                summary_input = (
                    ui.textarea(value=ticket_state["resolution_summary"])
                    .props("outlined autogrow")
                    .classes("w-full text-xs")
                )
                with ui.row().classes("w-full justify-between items-center -mt-1 text-[11px] text-slate-400"):
                    ui.label("Yêu cầu mô tả cụ thể các bước cấu hình/thay thế.")
                    ui.label("238 ký tự")

                # Metrics: Time & SLA
                with ui.grid(columns=2).classes("w-full gap-3 mt-1"):
                    # Metric 1
                    with ui.element("div").classes("p-3 rounded-2xl bg-slate-50 border border-slate-200/80"):
                        ui.label("Thời gian xử lý thực tế").classes("text-[11px] font-semibold text-slate-500")
                        with ui.row().classes("items-center gap-1.5 mt-1"):
                            ui.icon("schedule", size="16px").classes("text-slate-600")
                            ui.label("55 phút").classes("text-sm font-bold text-slate-900")
                        ui.label("Tổng thời gian công tác & debug").classes("text-[10px] text-slate-400 mt-0.5")

                    # Metric 2
                    with ui.element("div").classes("p-3 rounded-2xl bg-slate-50 border border-slate-200/80"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Chỉ số cam kết SLA").classes("text-[11px] font-semibold text-slate-500")
                            with ui.element("span").classes(
                                "text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 flex items-center gap-1"
                            ):
                                ui.icon("done", size="12px")
                                ui.label("Đạt chuẩn SLA 100%")
                        with ui.row().classes("items-center gap-1 mt-1"):
                            ui.label("1h 42m / 2h").classes("text-sm font-bold text-slate-900")
                        with ui.element("div").classes("w-full bg-slate-200 rounded-full h-1.5 mt-2"):
                            ui.element("div").classes("bg-emerald-500 h-1.5 rounded-full w-full")

                # Checkboxes
                with ui.column().classes("w-full gap-2.5 mt-2"):
                    with ui.row().classes("items-start gap-2.5"):
                        cb_email = ui.checkbox(value=True).props("dense size=sm color=primary")
                        with ui.column().classes("gap-0"):
                            ui.label("Gửi email & thông báo portal cho người yêu cầu (Trần Thị Mai)").classes(
                                "text-xs font-bold text-slate-800"
                            )
                            ui.label("Đính kèm biên bản xử lý và hướng dẫn xóa lệnh in tồn").classes(
                                "text-[11px] text-slate-400"
                            )

                    with ui.row().classes("items-start gap-2.5"):
                        cb_kb = ui.checkbox(value=True).props("dense size=sm color=primary")
                        with ui.column().classes("gap-0"):
                            ui.label("Lưu thành bài viết mới vào Cơ sở tri thức (KB) để tái sử dụng").classes(
                                "text-xs font-bold text-slate-800"
                            )
                            ui.label(
                                'Tạo bản nháp KB: "Khắc phục ACL Switch chặn Port In 9100 VLAN Kế Toán"'
                            ).classes("text-[11px] text-slate-400")

                    with ui.row().classes("items-start gap-2.5"):
                        cb_csat = ui.checkbox(value=False).props("dense size=sm color=primary")
                        with ui.column().classes("gap-0"):
                            ui.label("Gửi khảo sát đánh giá độ hài lòng (CSAT)").classes(
                                "text-xs font-bold text-slate-800"
                            )
                            ui.label("Tự động kích hoạt form chấm điểm 5 sao sau 15 phút").classes(
                                "text-[11px] text-slate-400"
                            )

                # Footer Actions
                with ui.row().classes("w-full justify-between items-center pt-3 border-t border-slate-100"):
                    with ui.row().classes("items-center gap-1.5 text-[11px] text-slate-500"):
                        ui.icon("lock", size="14px")
                        ui.label("Trạng thái sau khi đóng:").classes("font-medium")
                        ui.label("RESOLVED (Closed-Loop)").classes("font-bold text-slate-700")

                    with ui.row().classes("items-center gap-2"):
                        ui.button("Hủy bỏ / Quay lại kiểm tra", on_click=resolve_dialog.close).props(
                            "flat no-caps"
                        ).classes("text-slate-600 text-xs font-semibold px-3 py-2 rounded-xl hover:bg-slate-50")

                        def on_confirm_resolve():
                            ticket_state["is_resolved"] = True
                            ticket_state["status"] = "ĐÃ GIẢI QUYẾT"
                            status_badge.classes(replace="bg-emerald-600 text-white")
                            status_label.text = "• ĐÃ GIẢI QUYẾT"
                            resolve_dialog.close()
                            toast.show(
                                "Đã hoàn tất và đóng ticket #1048 thành công!",
                                type="positive",
                            )
                            # Add resolved entry to timeline
                            timeline_container.clear()
                            with timeline_container:
                                render_timeline(
                                    [
                                        {
                                            "author": "Nguyễn Văn An (KTV L2 - Bạn)",
                                            "time": "Vừa xong",
                                            "badge": "GIẢI QUYẾT",
                                            "badge_color": "bg-emerald-100 text-emerald-700",
                                            "dot_color": "bg-emerald-600",
                                            "content": summary_input.value or ticket_state["resolution_summary"],
                                        }
                                    ]
                                    + timeline_events
                                )

                        ui.button(
                            "Hoàn tất & Đóng vé (Resolve & Complete Ticket)",
                            icon="check_circle",
                            on_click=on_confirm_resolve,
                        ).props("unelevated no-caps").classes(
                            "bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-sm"
                        )

        # -------------------------------------------------------------
        # 1. BREADCRUMBS & LAST SYNC BAR
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-center flex-wrap gap-2 text-xs"):
            with ui.row().classes("items-center gap-1.5 text-slate-500 font-medium"):
                with ui.button("Hàng đợi", icon="arrow_back", on_click=lambda: ui.navigate.to("/technician/tasks")).props(
                    "flat dense no-caps"
                ).classes("text-slate-600 hover:text-blue-600 -ml-1 text-xs font-semibold"):
                    pass
                ui.label("›").classes("text-slate-300 font-bold")
                ui.label(f"#{ticket_id}").classes("font-mono font-bold text-blue-600")
                ui.label("›").classes("text-slate-300 font-bold")
                ui.label("Bàn làm việc Kỹ thuật viên (L2)").classes("text-slate-900 font-semibold")

            with ui.row().classes("items-center gap-2 text-[11px] text-slate-400"):
                sync_label = ui.label("Lần đồng bộ cuối: 14:28:19")

                def refresh_sync():
                    now_str = datetime.now().strftime("%H:%M:%S")
                    sync_label.text = f"Lần đồng bộ cuối: {now_str}"
                    toast.show("Đã làm mới dữ liệu sự cố và telemetry mạng!", type="info")

                with ui.button("Làm mới", icon="sync", on_click=refresh_sync).props("flat dense no-caps").classes(
                    "text-blue-600 hover:bg-blue-50 px-2 py-0.5 rounded-lg text-xs font-semibold"
                ):
                    pass

        # -------------------------------------------------------------
        # 2. TICKET HEADER & ACTION BAR
        # -------------------------------------------------------------
        with ui.card().classes(
            "w-full p-4 md:p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-3"
        ):
            # Top row: Badges and Action buttons
            with ui.row().classes("w-full justify-between items-center flex-wrap gap-3"):
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    with ui.element("span").classes(
                        "px-2.5 py-1 rounded-md bg-red-600 text-white text-[11px] font-black tracking-wider flex items-center gap-1"
                    ):
                        ui.icon("error", size="13px")
                        ui.label("P1 - KHẨN CẤP")

                    status_badge = ui.element("span").classes(
                        "px-2.5 py-1 rounded-md bg-blue-600 text-white text-[11px] font-bold flex items-center gap-1.5"
                    )
                    with status_badge:
                        status_label = ui.label("• ĐANG XỬ LÝ")

                    with ui.element("span").classes(
                        "px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-mono text-[11px] font-bold border border-slate-200"
                    ):
                        ui.label("INC-#1048")

                    with ui.element("span").classes(
                        "px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 text-[11px] font-medium flex items-center gap-1"
                    ):
                        ui.icon("place", size="13px").classes("text-slate-400")
                        ui.label("Văn phòng Hà Nội • Tòa A • Tầng 4")

                # Action Buttons
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.button(
                        "Chuyển L3",
                        icon="alt_route",
                        on_click=lambda: toast.show("Đã gửi yêu cầu escalate lên Network Level 3!", type="info"),
                    ).props("outline dense no-caps").classes(
                        "border-slate-200 text-slate-700 text-xs font-semibold px-2.5 py-1.5 rounded-xl hover:bg-slate-50"
                    )

                    ui.button(
                        "Phân công lại",
                        icon="person_add",
                        on_click=lambda: toast.show("Mở hộp thoại chuyển giao kỹ thuật viên", type="info"),
                    ).props("outline dense no-caps").classes(
                        "border-slate-200 text-slate-700 text-xs font-semibold px-2.5 py-1.5 rounded-xl hover:bg-slate-50"
                    )

                    ui.button(
                        "Tạm dừng (Pending)",
                        icon="pause_circle",
                        on_click=lambda: toast.show("Đã chuyển vé sang trạng thái Chờ phản hồi (Pending)", type="warning"),
                    ).props("outline dense no-caps").classes(
                        "border-slate-200 text-slate-700 text-xs font-semibold px-2.5 py-1.5 rounded-xl hover:bg-slate-50"
                    )

                    ui.button(
                        "Giải quyết vé",
                        icon="check_circle",
                        on_click=resolve_dialog.open,
                    ).props("unelevated dense no-caps").classes(
                        "bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl shadow-sm"
                    )

            # Ticket Title
            ui.label(
                "Máy in tầng 4 (Phòng Kế toán) không kết nối được mạng Wi-Fi & Báo lỗi kẹt lệnh in SPOOLER"
            ).classes("text-lg md:text-xl font-extrabold text-slate-900 tracking-tight leading-snug")

            # SLA Progress Meter Bar
            with ui.row().classes("w-full items-center gap-3 pt-1 flex-wrap"):
                with ui.row().classes("items-center gap-1.5 text-xs font-bold text-red-600 shrink-0"):
                    ui.icon("alarm", size="16px")
                    ui.label("SLA Giải quyết: Còn 18 phút")

                with ui.element("div").classes("flex-1 min-w-[160px] max-w-md bg-slate-100 rounded-full h-2 overflow-hidden"):
                    ui.element("div").classes("bg-red-500 h-2 rounded-full w-[85%]")

                ui.label("85% hạn ngạch (Mục tiêu 2h)").classes("text-xs text-slate-500 shrink-0")

        # -------------------------------------------------------------
        # 3. TWO-COLUMN MAIN CONTENT (LEFT: 8 COLS, RIGHT: 4 COLS)
        # -------------------------------------------------------------
        with ui.grid(columns=12).classes("w-full gap-4 items-start"):
            # =========================================================
            # LEFT MAIN COLUMN (8 cols)
            # =========================================================
            with ui.column().classes("col-span-12 lg:col-span-8 gap-4"):
                # -----------------------------------------------------
                # CARD 1: BÁO CÁO SỰ CỐ TỪ NGƯỜI DÙNG
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2 text-blue-600"):
                            ui.icon("description", size="18px")
                            ui.label("Báo cáo sự cố từ Người dùng").classes("text-xs font-bold text-slate-900")
                        ui.label("Đã gửi lúc 13:42 • 46 phút trước").classes("text-[11px] text-slate-400 font-medium")

                    # Quoted Message Box
                    with ui.element("div").classes(
                        "w-full p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 text-xs text-slate-700 leading-relaxed"
                    ):
                        ui.label(
                            '"Chào đội ngũ IT, cả phòng Kế toán hiện tại không thể in báo cáo thuế và hóa đơn quý gửi khách hàng. '
                            'Máy in HP LaserJet tầng 4 đèn Wi-Fi nhấp nháy liên tục màu vàng cam, màn hình báo lỗi '
                            "'Spooler Error 0x000006ba - Host Connection Timed Out'. "
                            'Đã thử khởi động lại máy in 2 lần nhưng không nhận được IP nội bộ."'
                        ).classes("italic")

                        with ui.row().classes("items-center gap-4 mt-2.5 pt-2 border-t border-slate-200/60 text-[11px] font-semibold text-slate-600 flex-wrap"):
                            ui.label("Dải IP khai báo: 192.168.4.155").classes("font-mono text-slate-800")
                            ui.label("•")
                            ui.label("Ảnh hưởng: 5 nhân sự")
                            ui.label("•")
                            with ui.element("span").classes("text-red-600 font-bold"):
                                ui.label("Mức độ cản trở: Cao (Chặn xuất hóa đơn)")

                    # Attachments List
                    ui.label("Tệp tin đính kèm & Ảnh chụp màn hình lỗi:").classes(
                        "text-[11px] font-bold text-slate-600 mt-1"
                    )
                    with ui.grid(columns=1).classes("sm:grid-cols-3 w-full gap-2.5"):
                        # File 1
                        with ui.row().classes(
                            "items-center gap-2.5 p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all no-wrap"
                        ):
                            ui.icon("image", size="20px").classes("text-blue-600 shrink-0")
                            with ui.column().classes("gap-0 overflow-hidden"):
                                ui.label("man_hinh_loi_spooler....").classes("text-xs font-bold text-slate-800 truncate")
                                ui.label("1.4 MB • Ảnh chụp").classes("text-[10px] text-slate-400 truncate")

                        # File 2
                        with ui.row().classes(
                            "items-center gap-2.5 p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all no-wrap"
                        ):
                            ui.icon("photo_camera", size="20px").classes("text-purple-600 shrink-0")
                            with ui.column().classes("gap-0 overflow-hidden"):
                                ui.label("mat_sau_may_in.png").classes("text-xs font-bold text-slate-800 truncate")
                                ui.label("2.1 MB • Thiết bị").classes("text-[10px] text-slate-400 truncate")

                        # File 3
                        with ui.row().classes(
                            "items-center gap-2.5 p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all no-wrap"
                        ):
                            ui.icon("terminal", size="20px").classes("text-slate-600 shrink-0")
                            with ui.column().classes("gap-0 overflow-hidden"):
                                ui.label("windows_spool_dump....").classes("text-xs font-bold text-slate-800 truncate")
                                ui.label("384 KB • Event Log").classes("text-[10px] text-slate-400 truncate")

                # -----------------------------------------------------
                # CARD 2: CHẨN ĐOÁN TỪ XA & GIÁM SÁT PORT
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2 text-indigo-600"):
                            ui.icon("router", size="18px")
                            ui.label("Chẩn đoán từ xa & Giám sát Port").classes("text-xs font-bold text-slate-900")
                        with ui.row().classes("items-center gap-1.5 text-[11px] text-red-600 font-bold"):
                            ui.element("span").classes("w-2 h-2 rounded-full bg-red-500 animate-pulse")
                            ui.label("Phát hiện bất thường mạng")

                    # 3 Metric Telemetry Cards
                    with ui.grid(columns=1).classes("sm:grid-cols-3 w-full gap-2.5"):
                        # Telemetry 1: ICMP Ping
                        with ui.element("div").classes("p-3 rounded-xl border border-slate-200 bg-slate-50/70"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("ICMP Ping (Gateway -> IP)").classes("text-[10px] font-bold text-slate-500 uppercase tracking-wide")
                                ui.icon("check_circle", size="14px").classes("text-emerald-600")
                            ui.label("Thành công (4ms)").classes("text-sm font-extrabold text-emerald-700 mt-1")
                            ui.label("Gói tin: 4/4 • Loss: 0%").classes("text-[10px] text-slate-500 mt-0.5")

                        # Telemetry 2: Port 9100 RAW
                        with ui.element("div").classes("p-3 rounded-xl border border-red-200 bg-red-50/60"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("Port 9100 / RAW Print").classes("text-[10px] font-bold text-red-700 uppercase tracking-wide")
                                ui.icon("block", size="14px").classes("text-red-600")
                            ui.label("Bị chặn (ACL Drop)").classes("text-sm font-extrabold text-red-700 mt-1")
                            ui.label("Switch SW-T4-A Port Gi1/0/14").classes("text-[10px] text-red-600 mt-0.5")

                        # Telemetry 3: VLAN & Subnet
                        with ui.element("div").classes("p-3 rounded-xl border border-slate-200 bg-slate-50/70"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("VLAN & Subnet").classes("text-[10px] font-bold text-slate-500 uppercase tracking-wide")
                                ui.icon("hub", size="14px").classes("text-blue-600")
                            ui.label("VLAN-20 (Accounting)").classes("text-sm font-extrabold text-blue-800 mt-1")
                            ui.label("DHCP Reservation: Mismatch").classes("text-[10px] text-amber-600 font-semibold mt-0.5")

                    # AI Knowledge Recommendation Box
                    with ui.element("div").classes(
                        "w-full p-3.5 rounded-xl border border-blue-200 bg-blue-50/50 flex items-start justify-between gap-3 flex-wrap sm:flex-nowrap"
                    ):
                        with ui.row().classes("items-start gap-2.5 flex-1"):
                            ui.icon("auto_awesome", size="20px").classes("text-blue-600 shrink-0 mt-0.5")
                            with ui.column().classes("gap-1"):
                                ui.label("Gợi ý AI & Cơ sở tri thức (KB-849)").classes(
                                    "text-xs font-bold text-blue-900 leading-tight"
                                )
                                ui.label(
                                    "Nguyên nhân phát hiện: Đợt nâng cấp firmware Switch Cisco lúc 02:00 sáng đã reset access-list chặn Port 9100 và cấp nhầm dải VLAN-10 thay vì VLAN-20."
                                ).classes("text-xs text-slate-600 leading-relaxed")

                        def apply_ai_fix():
                            toast.show(
                                "Đã kích hoạt script tự động điều chỉnh ACL rules trên Switch SW-T4-A!",
                                type="positive",
                            )

                        ui.button(
                            "Áp dụng kịch bản xử lý",
                            icon="build",
                            on_click=apply_ai_fix,
                        ).props("unelevated dense no-caps").classes(
                            "bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-3 py-2 rounded-xl shrink-0"
                        )

                # -----------------------------------------------------
                # CARD 3: TABBED TECHNICIAN WORK AREA (INTERNAL NOTE)
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-3"):
                    with ui.tabs().classes("w-full border-b border-slate-200 text-xs font-bold text-slate-600") as work_tabs:
                        t_internal = ui.tab("Ghi chú nội bộ IT (Internal Note)", icon="lock")
                        t_reply = ui.tab("Phản hồi khách hàng (Trần Thị Mai)", icon="forum")
                        t_audit = ui.tab("Nhật ký audit log (6)", icon="history")

                    with ui.tab_panels(work_tabs, value=t_internal).classes("w-full p-0 bg-transparent"):
                        with ui.tab_panel(t_internal).classes("p-0 pt-2 gap-3 flex flex-col"):
                            # Privacy Notice Banner
                            with ui.row().classes(
                                "w-full justify-between items-center p-2.5 rounded-xl bg-amber-50/80 border border-amber-200/80 text-amber-900 text-xs"
                            ):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon("visibility_off", size="16px").classes("text-amber-700")
                                    ui.label("Nội dung này chỉ hiển thị với nội bộ kỹ thuật viên IT HelpDesk. Khách hàng sẽ không thấy.").classes(
                                        "text-[11px] font-medium"
                                    )

                                with ui.row().classes("items-center gap-2 text-[10px] font-bold text-amber-800"):
                                    ui.link("#chèn_cấu_hình_mẫu", "").classes("hover:underline cursor-pointer")
                                    ui.label("•")
                                    ui.link("#macro_clear_spooler", "").classes("hover:underline cursor-pointer")

                            tech_note_input = (
                                ui.textarea(
                                    placeholder="Nhập ghi chú kỹ thuật, các lệnh CLI đã chạy, tình trạng linh kiện hoặc phân tích nguyên nhân sự cố..."
                                )
                                .props("outlined autogrow")
                                .classes("w-full text-xs")
                            )

                            # Action Toolbar
                            with ui.row().classes("w-full justify-between items-center flex-wrap gap-2 pt-1"):
                                with ui.row().classes("items-center gap-3 flex-wrap text-xs"):
                                    with ui.button("Đính kèm log/ảnh", icon="attach_file").props("flat dense no-caps").classes(
                                        "text-slate-600 hover:bg-slate-50 text-xs"
                                    ):
                                        pass

                                    with ui.row().classes("items-center gap-1 text-slate-600 text-xs font-semibold"):
                                        ui.icon("schedule", size="15px")
                                        ui.label("Ghi giờ (Log time):")
                                        with ui.element("span").classes("px-1.5 py-0.5 rounded bg-slate-100 font-mono text-[11px] font-bold"):
                                            ui.label("45 phút")

                                    ui.checkbox("Gửi cảnh báo đến nhóm Network L3", value=True).props("dense size=xs").classes(
                                        "text-xs font-semibold text-slate-700"
                                    )

                                with ui.row().classes("items-center gap-2"):
                                    ui.button("Hủy", on_click=lambda: tech_note_input.set_value("")).props("flat no-caps").classes(
                                        "text-slate-500 text-xs px-3 py-1.5 rounded-xl hover:bg-slate-50 font-semibold"
                                    )

                                    def on_save_note():
                                        txt = tech_note_input.value.strip()
                                        if not txt:
                                            toast.show("Vui lòng nhập nội dung ghi chú nội bộ!", type="warning")
                                            return
                                        toast.show("Đã lưu ghi chú kỹ thuật viên thành công!", type="positive")
                                        # Add to timeline
                                        new_entry = {
                                            "author": "Nguyễn Văn An (KTV L2 - Bạn)",
                                            "time": "Vừa xong",
                                            "badge": "GHI CHÚ KTV",
                                            "badge_color": "bg-indigo-100 text-indigo-700",
                                            "dot_color": "bg-indigo-600",
                                            "content": txt,
                                        }
                                        timeline_events.insert(0, new_entry)
                                        tech_note_input.set_value("")
                                        timeline_container.clear()
                                        with timeline_container:
                                            render_timeline(timeline_events)

                                    ui.button("Lưu ghi chú nội bộ", icon="save", on_click=on_save_note).props(
                                        "unelevated no-caps"
                                    ).classes("bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl")

                        with ui.tab_panel(t_reply).classes("p-0 pt-2 gap-3 flex flex-col"):
                            reply_input = ui.textarea(
                                placeholder="Gửi phản hồi trực tiếp tới người yêu cầu (Trần Thị Mai)..."
                            ).props("outlined autogrow").classes("w-full text-xs")
                            with ui.row().classes("w-full justify-end"):
                                ui.button("Gửi cho người dùng", icon="send", on_click=lambda: toast.show("Đã gửi phản hồi!", type="positive")).props(
                                    "unelevated no-caps"
                                ).classes("bg-blue-600 text-white text-xs font-bold px-4 py-1.5 rounded-xl")

                        with ui.tab_panel(t_audit).classes("p-0 pt-2"):
                            ui.label("Hệ thống ghi nhận 6 thay đổi trạng thái và phân bổ tài nguyên tự động.").classes(
                                "text-xs text-slate-500"
                            )

                # -----------------------------------------------------
                # CARD 4: TIẾN ĐỘ & NHẬT KÝ HOẠT ĐỘNG (TIMELINE)
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-3"):
                    ui.label("Tiến độ & Nhật ký hoạt động").classes("text-xs font-bold text-slate-900")

                    timeline_container = ui.column().classes("w-full gap-3 pl-1")

                    def render_timeline(events: list[dict]):
                        for ev in events:
                            with ui.row().classes("items-start gap-3 w-full no-wrap"):
                                with ui.element("div").classes(
                                    f"w-2.5 h-2.5 rounded-full {ev['dot_color']} mt-1.5 shrink-0"
                                ):
                                    pass
                                with ui.column().classes("gap-1 flex-1"):
                                    with ui.row().classes("items-center gap-2 flex-wrap"):
                                        ui.label(ev["author"]).classes("text-xs font-bold text-slate-900")
                                        ui.label(ev["time"]).classes("text-[11px] text-slate-400")
                                        with ui.element("span").classes(
                                            f"px-1.5 py-0.5 rounded text-[10px] font-bold {ev['badge_color']}"
                                        ):
                                            ui.label(ev["badge"])
                                    ui.label(ev["content"]).classes("text-xs text-slate-600 leading-relaxed")

                    with timeline_container:
                        render_timeline(timeline_events)

            # =========================================================
            # RIGHT SIDEBAR COLUMN (4 cols)
            # =========================================================
            with ui.column().classes("col-span-12 lg:col-span-4 gap-4"):
                # -----------------------------------------------------
                # RIGHT CARD 1: MỤC TIÊU & HẠN CAM KẾT SLA
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-3"):
                    with ui.row().classes("w-full justify-between items-center text-slate-900"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("timer", size="18px").classes("text-blue-600")
                            ui.label("Mục tiêu & Hạn cam kết SLA").classes("text-xs font-bold")
                        ui.icon("pie_chart", size="16px").classes("text-blue-600")

                    with ui.column().classes("w-full gap-2.5 text-xs"):
                        # First response SLA
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("SLA Phản hồi lần đầu").classes("text-slate-600 font-medium")
                            with ui.row().classes("items-center gap-1 text-emerald-600 font-bold"):
                                ui.icon("done", size="14px")
                                ui.label("Đạt (8m / 30m)")

                        # Resolution SLA
                        with ui.column().classes("w-full gap-1"):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("SLA Hoàn tất giải quyết").classes("text-slate-600 font-medium")
                                with ui.row().classes("items-center gap-1 text-red-600 font-bold text-[11px]"):
                                    ui.icon("warning", size="13px")
                                    ui.label("Còn 18 phút (1h 42m / 2h)")

                            with ui.element("div").classes("w-full bg-slate-100 rounded-full h-1.5 overflow-hidden"):
                                ui.element("div").classes("bg-red-500 h-1.5 rounded-full w-[85%]")

                        # Total time
                        with ui.row().classes("w-full justify-between items-center pt-2 border-t border-slate-100"):
                            ui.label("Tổng thời gian xử lý:").classes("text-slate-500")
                            ui.label("52 phút (1 kỹ thuật viên)").classes("font-bold text-slate-900 font-mono")

                # -----------------------------------------------------
                # RIGHT CARD 2: TÀI SẢN IT LIÊN QUAN
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2 text-slate-900"):
                            ui.icon("devices", size="18px").classes("text-blue-600")
                            ui.label("Tài sản IT liên quan").classes("text-xs font-bold")
                        ui.link("Chi tiết ITAM ↗", "/technician/devices").classes(
                            "text-[11px] text-blue-600 font-bold hover:underline no-underline"
                        )

                    # Device Capsule
                    with ui.row().classes("w-full items-center gap-3 p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 no-wrap"):
                        with ui.element("div").classes("w-9 h-9 rounded-lg bg-white border border-slate-200 flex items-center justify-center shrink-0"):
                            ui.icon("print", size="20px").classes("text-slate-700")
                        with ui.column().classes("gap-0.5 overflow-hidden"):
                            ui.label("HP LaserJet Pro M404dn").classes("text-xs font-extrabold text-slate-900 truncate")
                            with ui.row().classes("items-center gap-1.5 flex-wrap"):
                                with ui.element("span").classes("px-1.5 py-0.2 rounded bg-blue-100 text-blue-700 font-mono font-bold text-[10px]"):
                                    ui.label("Mã: PRN-ACC-04")
                                ui.label("Bảo hành: Đến 12/2026 (Chính hãng)").classes("text-[10px] text-slate-400 truncate")

                    # Metadata Grid
                    with ui.grid(columns=2).classes("w-full gap-2 text-xs pt-1"):
                        with ui.column().classes("gap-0.5"):
                            ui.label("Vị trí thiết bị:").classes("text-[10px] text-slate-400 font-medium")
                            ui.label("Tòa A - P.402 (Kế toán)").classes("text-xs font-bold text-slate-800")

                        with ui.column().classes("gap-0.5"):
                            ui.label("Địa chỉ MAC:").classes("text-[10px] text-slate-400 font-medium")
                            ui.label("00:1E:68:5B:32:11").classes("text-xs font-mono font-bold text-slate-800")

                        with ui.column().classes("gap-0.5"):
                            ui.label("IP Tĩnh cấu hình:").classes("text-[10px] text-slate-400 font-medium")
                            ui.label("192.168.4.155").classes("text-xs font-mono font-bold text-slate-800")

                        with ui.column().classes("gap-0.5"):
                            ui.label("Lịch sử 60 ngày:").classes("text-[10px] text-slate-400 font-medium")
                            ui.label("3 lần báo sự cố").classes("text-xs font-bold text-red-600")

                # -----------------------------------------------------
                # RIGHT CARD 3: NGƯỜI YÊU CẦU
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2 text-slate-900"):
                            ui.icon("person", size="18px").classes("text-blue-600")
                            ui.label("Người yêu cầu").classes("text-xs font-bold")
                        ui.icon("badge", size="16px").classes("text-slate-400")

                    # User Avatar & Info
                    with ui.row().classes("items-center gap-3 no-wrap"):
                        with ui.avatar().props("size=36px").classes("bg-blue-600 text-white font-bold text-xs shrink-0"):
                            ui.label("TM")
                        with ui.column().classes("gap-0 overflow-hidden"):
                            ui.label("Trần Thị Mai").classes("text-xs font-extrabold text-slate-900 leading-tight")
                            ui.label("Chuyên viên Kế toán Tổng hợp").classes("text-[11px] text-slate-500 leading-tight")
                            with ui.row().classes("items-center gap-1 text-[10px] font-bold text-amber-600 mt-0.5"):
                                ui.label("⭐ CSAT đánh giá: 5/5 sao")

                    with ui.column().classes("w-full gap-1.5 text-xs pt-1 border-t border-slate-100 text-slate-600"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("call", size="14px").classes("text-slate-400")
                            ui.label("Máy lẻ: 402 (Di động: 0988.xxx.412)")

                        with ui.row().classes("items-center gap-2"):
                            ui.icon("mail", size="14px").classes("text-slate-400")
                            ui.label("mai.tran@congty.com.vn")

                        with ui.row().classes("items-center gap-2"):
                            ui.icon("laptop_mac", size="14px").classes("text-slate-400")
                            ui.label("Laptop: ThinkPad T14 Gen 4 (PC-ACC-012)")

                # -----------------------------------------------------
                # RIGHT CARD 4: PHÂN LOẠI ITSM & TÁC ĐỘNG
                # -----------------------------------------------------
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-sm gap-2.5"):
                    ui.label("Phân loại ITSM & Tác động").classes("text-xs font-bold text-slate-900")

                    with ui.column().classes("w-full gap-2 text-xs"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Dịch vụ IT (Service):").classes("text-slate-500")
                            ui.label("Hạ tầng In ấn Văn phòng").classes("font-bold text-slate-800")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Danh mục sự cố (Category):").classes("text-slate-500")
                            ui.label("Mạng nội bộ / Port ACL").classes("font-bold text-slate-800")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Phạm vi ảnh hưởng:").classes("text-slate-500")
                            ui.label("Phòng ban (5 nhân sự)").classes("font-bold text-red-600")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Kỹ thuật viên phụ trách:").classes("text-slate-500")
                            ui.link("Nguyễn Văn An (L2)", "/technician/tasks").classes("font-bold text-blue-600 no-underline hover:underline")

                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("Kênh tiếp nhận:").classes("text-slate-500")
                            ui.label("Self-Service Portal").classes("font-bold text-slate-800")

    app_shell("Bàn làm việc Kỹ thuật viên (L2)", content)
