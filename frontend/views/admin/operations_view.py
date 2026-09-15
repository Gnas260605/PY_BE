from __future__ import annotations

from nicegui import ui

from common.components import toast
from common.components.layout import app_shell


def render_admin_operations_view() -> None:
    def content(user: dict) -> None:
        # -------------------------------------------------------------
        # 1. HEADER & TOP ACTION BUTTONS
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-start flex-wrap gap-3 mb-1"):
            with ui.column().classes("gap-1 max-w-2xl"):
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.label("Cài đặt Hệ thống & Quản trị Vận hành ITSM").classes(
                        "text-xl md:text-2xl font-black text-slate-900 tracking-tight"
                    )
                    with ui.element("span").classes(
                        "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-100 text-blue-700"
                    ):
                        ui.label("v4.6.2 (Build 892)")
                    with ui.element("span").classes(
                        "px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 flex items-center gap-1"
                    ):
                        ui.element("span").classes("w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse")
                        ui.label("Enterprise Core Active")

                ui.label(
                    "Quản trị danh mục dịch vụ, tích hợp hệ thống xác thực LDAP/SSO, quy tắc tự động hóa Ticket Bots, "
                    "phân quyền nhân sự IT và kênh thông báo cảnh báo đa nền tảng."
                ).classes("text-xs text-slate-500 leading-relaxed")

            # Top Action Buttons
            with ui.row().classes("items-center gap-2 flex-wrap"):
                with ui.button(
                    "Sao lưu cấu hình (Backup)",
                    icon="cloud_download",
                    on_click=lambda: toast.show("Đã tạo bản sao lưu cấu hình ITSM thành công!", type="positive"),
                ).props("flat dense no-caps").classes(
                    "bg-white border border-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-xl hover:bg-slate-50"
                ):
                    pass

                with ui.button(
                    "Khôi phục mặc định",
                    icon="restore",
                    on_click=lambda: toast.show("Đã kiểm tra trạng thái cấu hình hệ thống.", type="info"),
                ).props("flat dense no-caps").classes(
                    "bg-white border border-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-xl hover:bg-slate-50"
                ):
                    pass

                with ui.button(
                    "Lưu thay đổi",
                    icon="save",
                    on_click=lambda: toast.show("Đã cập nhật cấu hình vận hành ITSM!", type="positive"),
                ).props("unelevated dense no-caps").classes(
                    "bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-4 py-1.5 rounded-xl shadow-xs"
                ):
                    pass

        # -------------------------------------------------------------
        # 2. NAVIGATION TABS (Service Catalog, RBAC, Integrations)
        # -------------------------------------------------------------
        with ui.row().classes("w-full items-center gap-2 border-b border-slate-200 pb-2 mb-3 flex-wrap"):
            with ui.button("Danh mục Dịch vụ (Service Catalog)", icon="category").props("unelevated dense no-caps").classes(
                "bg-blue-50 text-blue-700 border border-blue-200 font-bold text-xs px-3.5 py-1.5 rounded-xl"
            ):
                pass

            with ui.button("Người dùng & Phân quyền Kỹ thuật viên (RBAC)", icon="admin_panel_settings").props(
                "flat dense no-caps"
            ).classes("text-slate-600 hover:bg-slate-100 font-semibold text-xs px-3.5 py-1.5 rounded-xl"):
                pass

            with ui.button("Tích hợp & Webhook (LDAP, Telegram, Slack, Jira)", icon="hub").props(
                "flat dense no-caps"
            ).classes("text-slate-600 hover:bg-slate-100 font-semibold text-xs px-3.5 py-1.5 rounded-xl"):
                pass

        # -------------------------------------------------------------
        # 3. 4 TOP METRIC CARDS
        # -------------------------------------------------------------
        with ui.grid(columns=4).classes("w-full gap-3 mb-3"):
            # Metric 1
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Dịch vụ đang kích hoạt").classes("text-[11px] font-bold text-slate-500 uppercase tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center"):
                        ui.icon("apps", size="18px")
                with ui.row().classes("items-baseline gap-1.5 mt-1"):
                    ui.label("28").classes("text-2xl font-black text-slate-900")
                    ui.label("/ 32 mục").classes("text-xs text-slate-400 font-semibold")

            # Metric 2
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Active Directory Sync").classes("text-[11px] font-bold text-slate-500 uppercase tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center"):
                        ui.icon("sync", size="18px")
                with ui.row().classes("items-baseline gap-1.5 mt-1"):
                    ui.label("100%").classes("text-2xl font-black text-emerald-600")
                    ui.label("450 Tài khoản").classes("text-xs text-slate-500 font-medium")

            # Metric 3
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("SLA Escalation Bot").classes("text-[11px] font-bold text-slate-500 uppercase tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center"):
                        ui.icon("smart_toy", size="18px")
                with ui.row().classes("items-baseline gap-1.5 mt-1"):
                    ui.label("09").classes("text-2xl font-black text-indigo-700")
                    ui.label("Quy tắc chạy song song").classes("text-xs text-slate-500 font-medium")

            # Metric 4
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Bảo vệ 2FA & Audit Log").classes("text-[11px] font-bold text-slate-500 uppercase tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center"):
                        ui.icon("verified_user", size="18px")
                with ui.row().classes("items-baseline gap-2 mt-1"):
                    ui.label("Tuân thủ").classes("text-2xl font-black text-emerald-700")
                    with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-100 text-emerald-800"):
                        ui.label("ISO 27001")

        # -------------------------------------------------------------
        # 4. MAIN 2-COLUMN LAYOUT (Left: Catalog & SLA, Right: Integrations & Policies)
        # -------------------------------------------------------------
        with ui.grid(columns=12).classes("w-full gap-4 items-start"):
            # ================= LEFT COLUMN: 8 COLS =================
            with ui.column().classes("col-span-12 lg:col-span-8 gap-3"):
                # Header & Add Catalog Button
                with ui.row().classes("w-full justify-between items-center flex-wrap gap-2"):
                    with ui.column().classes("gap-0.5"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("format_list_bulleted", size="18px").classes("text-blue-600")
                            ui.label("Danh mục Dịch vụ ITSM đang áp dụng").classes("text-sm font-extrabold text-slate-900")
                        ui.label("Thiết lập form yêu cầu dịch vụ, quy trình phê duyệt cấp bậc và luồng định tuyến tự động cho từng bộ phận IT.").classes(
                            "text-xs text-slate-500"
                        )

                    with ui.button("Tạo nhóm dịch vụ mới", icon="add", on_click=lambda: toast.show("Mở trình tạo danh mục dịch vụ mới", type="info")).props(
                        "unelevated dense no-caps"
                    ).classes("bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 font-bold text-xs px-3 py-1.5 rounded-xl"):
                        pass

                # Catalog Card 1: Phần cứng & Ngoại vi
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-2"):
                    with ui.row().classes("w-full justify-between items-start no-wrap gap-2"):
                        with ui.row().classes("items-start gap-3"):
                            with ui.element("div").classes("w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 border border-blue-100"):
                                ui.icon("laptop_mac", size="20px")
                            with ui.column().classes("gap-0.5"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label("Dịch vụ Phần cứng & Thiết bị ngoại vi").classes("text-xs font-bold text-slate-900")
                                    with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600"):
                                        ui.label("14 biểu mẫu")
                                ui.label(
                                    "Cung ứng, bảo trì & đổi mới: Laptop doanh nghiệp, Máy in văn phòng, Màn hình mở rộng, Bàn phím & Chuột chuyên dụng."
                                ).classes("text-[11px] text-slate-500")

                        with ui.row().classes("items-center gap-2 shrink-0"):
                            with ui.button("Chỉnh sửa biểu mẫu", icon="edit_note", on_click=lambda: toast.show("Mở cấu hình biểu mẫu phần cứng", type="info")).props("flat dense no-caps").classes(
                                "text-slate-600 hover:text-blue-600 text-[11px] font-semibold"
                            ):
                                pass
                            ui.switch(value=True).props("dense color=primary")

                    with ui.row().classes("w-full items-center gap-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500 flex-wrap"):
                        ui.label("SLA tiêu chuẩn:").classes("font-semibold text-slate-600")
                        with ui.element("span").classes("px-1.5 py-0.5 rounded bg-slate-100 font-mono font-bold text-slate-700"):
                            ui.label("Phản hồi 15m")
                        with ui.element("span").classes("px-1.5 py-0.5 rounded bg-slate-100 font-mono font-bold text-slate-700"):
                            ui.label("Bàn giao 04h")
                        ui.label("• Phê duyệt: Trưởng bộ phận người gửi (L1 Manager)").classes("text-slate-500")

                # Catalog Card 2: Mạng & VPN
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-2"):
                    with ui.row().classes("w-full justify-between items-start no-wrap gap-2"):
                        with ui.row().classes("items-start gap-3"):
                            with ui.element("div").classes("w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 border border-indigo-100"):
                                ui.icon("vpn_key", size="20px")
                            with ui.column().classes("gap-0.5"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label("Mạng nội bộ & VPN truy cập từ xa").classes("text-xs font-bold text-slate-900")
                                    with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600"):
                                        ui.label("8 biểu mẫu")
                                ui.label(
                                    "Cấp phát chứng thực Wi-Fi văn phòng WPA3-Enterprise, Tài khoản OpenVPN Client, Cấp IP tĩnh & Mở Port Firewall nội bộ."
                                ).classes("text-[11px] text-slate-500")

                        with ui.row().classes("items-center gap-2 shrink-0"):
                            with ui.button("Chỉnh sửa biểu mẫu", icon="edit_note", on_click=lambda: toast.show("Mở cấu hình biểu mẫu VPN", type="info")).props("flat dense no-caps").classes(
                                "text-slate-600 hover:text-blue-600 text-[11px] font-semibold"
                            ):
                                pass
                            ui.switch(value=True).props("dense color=primary")

                    with ui.row().classes("w-full items-center gap-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500 flex-wrap"):
                        ui.label("SLA tiêu chuẩn:").classes("font-semibold text-slate-600")
                        with ui.element("span").classes("px-1.5 py-0.5 rounded bg-slate-100 font-mono font-bold text-slate-700"):
                            ui.label("Phản hồi 10m")
                        with ui.element("span").classes("px-1.5 py-0.5 rounded bg-slate-100 font-mono font-bold text-slate-700"):
                            ui.label("Xử lý 02h")
                        ui.label("• Phê duyệt: IT Network Admin Xác minh IP/Device").classes("text-slate-500")

                # Catalog Card 3: Phần mềm Enterprise & 2-Step Workflow
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-start no-wrap gap-2"):
                        with ui.row().classes("items-start gap-3"):
                            with ui.element("div").classes("w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0 border border-purple-100"):
                                ui.icon("admin_panel_settings", size="20px")
                            with ui.column().classes("gap-0.5"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label("Quyền truy cập & Tài khoản phần mềm Enterprise").classes("text-xs font-bold text-slate-900")
                                    with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-700"):
                                        ui.label("2-Step Approval")
                                ui.label(
                                    "Phân quyền hệ thống lõi: SAP S/4HANA ERP, Email Microsoft 365 E5, Hubspot CRM, Kho mã nguồn GitLab/GitHub Organization."
                                ).classes("text-[11px] text-slate-500")

                        with ui.button("Cấu hình Workflow Phê duyệt", icon="schema", on_click=lambda: toast.show("Mở sơ đồ phê duyệt 2 bước", type="info")).props(
                            "unelevated dense no-caps"
                        ).classes("bg-blue-600 text-white text-[11px] font-bold px-3 py-1.5 rounded-xl shrink-0 shadow-xs"):
                            pass

                    # Workflow Stepper Box
                    with ui.row().classes("w-full items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] flex-wrap gap-2"):
                        with ui.row().classes("items-center gap-2"):
                            with ui.element("span").classes("w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-[10px]"):
                                ui.label("1")
                            ui.label("Manager Trực tiếp duyệt").classes("font-semibold text-slate-700")

                        ui.icon("arrow_forward", size="14px").classes("text-slate-400")

                        with ui.row().classes("items-center gap-2"):
                            with ui.element("span").classes("w-5 h-5 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-[10px]"):
                                ui.label("2")
                            ui.label("Data Custodian / SecOps duyệt").classes("font-semibold text-slate-700")

                        ui.icon("arrow_forward", size="14px").classes("text-slate-400")

                        with ui.row().classes("items-center gap-2"):
                            with ui.element("span").classes("px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]"):
                                ui.label("OK")
                            ui.label("Tự động cấp phát API").classes("font-semibold text-emerald-800")

                        with ui.element("span").classes("text-slate-400 text-[10px]"):
                            ui.label("Thời hạn kỳ duyệt: 24h")

                # Catalog Card 4: Phần mềm văn phòng & OS
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-2"):
                    with ui.row().classes("w-full justify-between items-start no-wrap gap-2"):
                        with ui.row().classes("items-start gap-3"):
                            with ui.element("div").classes("w-9 h-9 rounded-xl bg-cyan-50 text-cyan-600 flex items-center justify-center shrink-0 border border-cyan-100"):
                                ui.icon("desktop_windows", size="20px")
                            with ui.column().classes("gap-0.5"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label("Dịch vụ Hỗ trợ Phần mềm văn phòng & OS").classes("text-xs font-bold text-slate-900")
                                    with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-100 text-cyan-700"):
                                        ui.label("Tự động định tuyến L1")
                                ui.label(
                                    "Cài đặt hệ điều hành Windows 11 Enterprise, Bộ ứng dụng Office 365, Phần mềm kế toán MISA, Cài đặt phần mềm diệt virus EDR."
                                ).classes("text-[11px] text-slate-500")

                        with ui.row().classes("items-center gap-2 shrink-0"):
                            with ui.button("Chỉnh sửa", icon="tune", on_click=lambda: toast.show("Mở cấu hình phân phối L1", type="info")).props("flat dense no-caps").classes(
                                "text-slate-600 hover:text-blue-600 text-[11px] font-semibold"
                            ):
                                pass
                            ui.switch(value=True).props("dense color=primary")

                    with ui.row().classes("w-full items-center gap-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500 flex-wrap"):
                        ui.label("Hàng đợi đích:").classes("font-semibold text-slate-600")
                        with ui.element("span").classes("px-1.5 py-0.5 rounded bg-slate-100 font-mono text-[10px] text-slate-700"):
                            ui.label("Queue_Tier1_DesktopSupport")
                        ui.label("• Phân phối: Thuật toán Round-Robin theo ca trực").classes("text-slate-500")

                # SLA Response Matrix Card
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("speed", size="18px").classes("text-emerald-600")
                            ui.label("Ma trận Thời gian Phản hồi SLA theo Danh mục").classes("text-xs font-bold text-slate-900")
                        with ui.element("span").classes("px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold"):
                            ui.label("99.1% SLA Giữ vững")

                    ui.label("Tỷ lệ hoàn thành đúng cam kết trong 30 ngày qua trên từng khối dịch vụ:").classes("text-[11px] text-slate-500")

                    # SLA item 1
                    with ui.column().classes("w-full gap-1"):
                        with ui.row().classes("w-full justify-between items-center text-[11px]"):
                            ui.label("Dịch vụ Phần cứng & Cấp phát").classes("font-semibold text-slate-700")
                            ui.label("98.4% (Cam kết ≤ 4h)").classes("font-mono font-bold text-emerald-700")
                        with ui.element("div").classes("w-full h-2 rounded-full bg-slate-100 overflow-hidden"):
                            ui.element("div").classes("h-full bg-emerald-500 rounded-full").style("width: 98.4%")

                    # SLA item 2
                    with ui.column().classes("w-full gap-1"):
                        with ui.row().classes("w-full justify-between items-center text-[11px]"):
                            ui.label("Mạng & VPN Khẩn cấp").classes("font-semibold text-slate-700")
                            ui.label("99.7% (Cam kết ≤ 2h)").classes("font-mono font-bold text-emerald-700")
                        with ui.element("div").classes("w-full h-2 rounded-full bg-slate-100 overflow-hidden"):
                            ui.element("div").classes("h-full bg-emerald-600 rounded-full").style("width: 99.7%")

                    # SLA item 3
                    with ui.column().classes("w-full gap-1"):
                        with ui.row().classes("w-full justify-between items-center text-[11px]"):
                            ui.label("Quyền truy cập SAP / CRM (Phê duyệt đa tầng)").classes("font-semibold text-slate-700")
                            ui.label("96.2% (Cam kết ≤ 24h)").classes("font-mono font-bold text-indigo-700")
                        with ui.element("div").classes("w-full h-2 rounded-full bg-slate-100 overflow-hidden"):
                            ui.element("div").classes("h-full bg-indigo-500 rounded-full").style("width: 96.2%")

            # ================= RIGHT COLUMN: 4 COLS =================
            with ui.column().classes("col-span-12 lg:col-span-4 gap-3"):
                # Integrations Card
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("electrical_services", size="18px").classes("text-blue-600")
                            ui.label("Tích hợp Hệ thống").classes("text-xs font-bold text-slate-900")
                        with ui.element("span").classes("px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold"):
                            ui.label("● 4 Đang chạy")

                    # Integration 1: Active Directory
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50/70 border border-slate-200/70 space-y-1.5"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("dns", size="16px").classes("text-blue-600")
                                ui.label("Microsoft Active Directory").classes("text-xs font-bold text-slate-800")
                            with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-100 text-blue-800"):
                                ui.label("SYNC: 15m")
                        ui.label("Azure AD / Entra ID liên kết tự động 450 tài khoản nhân sự và sơ đồ tổ chức phòng ban.").classes(
                            "text-[11px] text-slate-500 leading-tight"
                        )
                        with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-400 pt-1"):
                            ui.label("Lần đồng bộ cuối: 4 phút trước")
                            ui.link("Cấu hình", "#").classes("text-blue-600 font-bold no-underline hover:underline")

                    # Integration 2: Telegram Bot
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50/70 border border-slate-200/70 space-y-1.5"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("send", size="16px").classes("text-cyan-600")
                                ui.label("Telegram Alert Bot").classes("text-xs font-bold text-slate-800")
                            with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-mono text-cyan-800 bg-cyan-100"):
                                ui.label("@HelpDeskPro_AlertBot")
                        ui.label("Gửi thông báo khẩn cấp tức thời tới kênh On-call IT khi có ticket P1 Critical chưa nhận sau 10 phút.").classes(
                            "text-[11px] text-slate-500 leading-tight"
                        )
                        with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-400 pt-1"):
                            ui.label("Webhook: 200 OK")
                            ui.link("Kiểm tra Ping", "#").classes("text-blue-600 font-bold no-underline hover:underline")

                    # Integration 3: Zalo ZNS
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50/70 border border-slate-200/70 space-y-1.5"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("sms", size="16px").classes("text-indigo-600")
                                ui.label("Zalo ZNS & SMS Gateway").classes("text-xs font-bold text-slate-800")
                            with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800"):
                                ui.label("CONNECTED")
                        ui.label("Gửi mã OTP khôi phục mật khẩu & SMS thông báo trạng thái vé sửa chữa tới số điện thoại nội bộ.").classes(
                            "text-[11px] text-slate-500 leading-tight"
                        )
                        with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-400 pt-1"):
                            ui.label("Đầu số: Brandname HELPDESK")
                            ui.label("Số dư: 4,800 SMS").classes("font-mono font-semibold text-slate-600")

                    # Integration 4: Jira Software
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50/70 border border-slate-200/70 space-y-1.5"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("integration_instructions", size="16px").classes("text-amber-600")
                                ui.label("Jira Software & GitHub").classes("text-xs font-bold text-slate-800")
                            with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700"):
                                ui.label("READY")
                        ui.label("Tự động chuyển tiếp vé lỗi phần mềm nghiệp vụ sang Issue Tracker cho đội DEV Engineering.").classes(
                            "text-[11px] text-slate-500 leading-tight"
                        )
                        with ui.row().classes("w-full justify-between items-center text-[10px] text-slate-400 pt-1"):
                            ui.label("Project Key: ITENG")
                            ui.link("Liên kết dự án", "#").classes("text-blue-600 font-bold no-underline hover:underline")

                # Security Policy & Audit Log Card
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("security", size="18px").classes("text-rose-600")
                        ui.label("Chính sách Bảo mật & Hệ thống").classes("text-xs font-bold text-slate-900")

                    # Policy 1: 2FA
                    with ui.row().classes("w-full justify-between items-start text-xs"):
                        with ui.column().classes("gap-0.5 max-w-[200px]"):
                            ui.label("Bắt buộc xác thực 2FA / OTP").classes("font-bold text-slate-800")
                            ui.label("Áp dụng bắt buộc cho toàn bộ tài khoản Kỹ thuật viên L1-L3 và Admin hệ thống.").classes(
                                "text-[10px] text-slate-400 leading-tight"
                            )
                        with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800"):
                            ui.label("ĐANG BẬT")

                    # Policy 2: Auto-close 48h
                    with ui.row().classes("w-full justify-between items-start text-xs"):
                        with ui.column().classes("gap-0.5 max-w-[200px]"):
                            ui.label("Tự động đóng Ticket sau 48 giờ").classes("font-bold text-slate-800")
                            ui.label("Tự động hoàn tất và đóng vé nếu người dùng không phản hồi yêu cầu kiểm tra sau 48h.").classes(
                                "text-[10px] text-slate-400 leading-tight"
                            )
                        with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800"):
                            ui.label("ĐANG BẬT")

                    # Policy 3: Audit log 365 days
                    with ui.row().classes("w-full justify-between items-start text-xs"):
                        with ui.column().classes("gap-0.5 max-w-[200px]"):
                            ui.label("Ghi nhật ký Audit Log vĩnh viễn").classes("font-bold text-slate-800")
                            ui.label("Lưu vết 100% lịch sử sửa đổi cấu hình dịch vụ, phân quyền và export dữ liệu (365 ngày).").classes(
                                "text-[10px] text-slate-400 leading-tight"
                            )
                        with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800"):
                            ui.label("365 NGÀY")

                    # Real-time console snippet
                    with ui.column().classes("w-full pt-2 border-t border-slate-100 gap-1 font-mono text-[10px]"):
                        with ui.row().classes("w-full justify-between items-center text-slate-400"):
                            ui.label("Nhật ký quản trị gần nhất")
                            ui.label("Real-time")
                        with ui.element("div").classes("w-full p-2 rounded-lg bg-slate-900 text-slate-300 space-y-0.5"):
                            ui.label("[10:42:15] user:nguyenvanan update_sla_policy: ACC-04")
                            ui.label("[09:15:02] system:bot_sync ldap_synced: 450 accounts OK")

    app_shell("Tổng quan vận hành", content)
