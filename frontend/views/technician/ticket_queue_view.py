from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components.layout import app_shell
from common.components import toast


# 18 realistic tickets in the technician L2 queue
QUEUE_TICKETS: list[dict[str, Any]] = [
    {
        "id": 1048,
        "code": "INC-#1048",
        "title": "Máy in tầng 4 (Phòng Kế toán) không kết nối được mạng Wi-Fi & Báo lỗi kẹt lệnh in SPOOLER",
        "description": "Máy in HP LaserJet tại phòng Kế toán nhấp nháy đèn vàng cam liên tục, màn hình báo lỗi Spooler Error 0x000006ba - Host Connection Timed Out.",
        "priority": "P1 - KHẨN CẤP",
        "priority_level": "P1",
        "priority_color": "bg-rose-50 text-rose-700 border-rose-200",
        "priority_dot": "bg-rose-600",
        "status": "ĐANG XỬ LÝ",
        "status_color": "bg-blue-50 text-blue-700 border-blue-200",
        "status_dot": "bg-blue-600",
        "category": "Mạng & In ấn",
        "requester": "Trần Thị Mai",
        "department": "Phòng Kế toán",
        "location": "Văn phòng Hà Nội • Tòa A • Tầng 4",
        "ext": "402",
        "device": "HP LaserJet Pro M404dn (PRN-ACC-04)",
        "sla_text": "Còn 18 phút (Mục tiêu 2h)",
        "sla_status": "warning",
        "sla_percent": 85,
        "assigned_to": "Nguyễn Văn An (KTV L2 - Bạn)",
        "created_at": "13:42 (46 phút trước)",
        "is_active_target": True,
    },
    {
        "id": 1052,
        "code": "INC-#1052",
        "title": "Rớt kết nối mạng Switch tầng 3 - Toàn bộ nhân sự khối Kinh Doanh offline",
        "description": "Switch SW-T3-A mất uplink về Core Switch, 35 máy tính phòng Sales không truy cập được Internet và CRM.",
        "priority": "P1 - KHẨN CẤP",
        "priority_level": "P1",
        "priority_color": "bg-rose-50 text-rose-700 border-rose-200",
        "priority_dot": "bg-rose-600",
        "status": "ĐANG XỬ LÝ",
        "status_color": "bg-blue-50 text-blue-700 border-blue-200",
        "status_dot": "bg-blue-600",
        "category": "Hạ tầng Mạng",
        "requester": "Phạm Minh Đức",
        "department": "Khối Kinh Doanh",
        "location": "Văn phòng Hà Nội • Tòa A • Tầng 3",
        "ext": "315",
        "device": "Cisco Catalyst 2960X (SW-T3-A)",
        "sla_text": "Còn 25 phút (Mục tiêu 1h)",
        "sla_status": "warning",
        "sla_percent": 75,
        "assigned_to": "Trần Văn Bình (KTV L2)",
        "created_at": "14:05 (23 phút trước)",
        "is_active_target": False,
    },
    {
        "id": 1049,
        "code": "INC-#1049",
        "title": "Lỗi màn hình xanh BSOD (nvlddmkm.sys) khi khởi động phần mềm AutoCAD / Revit",
        "description": "Máy trạm đồ họa của phòng R&D bị crash liên tục khi render bản vẽ 3D, nghi vấn driver card đồ họa NVIDIA RTX 4070 bị lỗi.",
        "priority": "P2 - CAO",
        "priority_level": "P2",
        "priority_color": "bg-amber-50 text-amber-700 border-amber-200",
        "priority_dot": "bg-amber-600",
        "status": "CHỜ TIẾP NHẬN",
        "status_color": "bg-purple-50 text-purple-700 border-purple-200",
        "status_dot": "bg-purple-600",
        "category": "Phần cứng & Đồ họa",
        "requester": "Lê Hoàng Nam",
        "department": "Phòng Kỹ thuật & R&D",
        "location": "Văn phòng Hà Nội • Tòa B • Tầng 2",
        "ext": "218",
        "device": "Dell Precision 3660 Workstation (WS-RD-08)",
        "sla_text": "Còn 48 phút (Mục tiêu 4h)",
        "sla_status": "warning",
        "sla_percent": 80,
        "assigned_to": "Chưa tiếp nhận",
        "created_at": "13:10 (1h 18m trước)",
        "is_active_target": False,
    },
    {
        "id": 1045,
        "code": "REQ-#1045",
        "title": "Xin cấp quyền truy cập phần mềm ERP SAP S/4HANA phân hệ Kế toán Tổng hợp",
        "description": "Nhân sự thử việc chuyển chính thức, cần cấp role SAP_FI_GL_ACCOUNTANT và phân quyền đọc báo cáo tài chính.",
        "priority": "P3 - TRUNG BÌNH",
        "priority_level": "P3",
        "priority_color": "bg-blue-50 text-blue-700 border-blue-200",
        "priority_dot": "bg-blue-600",
        "status": "ĐANG XỬ LÝ",
        "status_color": "bg-blue-50 text-blue-700 border-blue-200",
        "status_dot": "bg-blue-600",
        "category": "Phần mềm & Tài khoản",
        "requester": "Trần Thị Mai",
        "department": "Phòng Kế toán",
        "location": "Văn phòng Hà Nội • Tòa A • Tầng 4",
        "ext": "402",
        "device": "ThinkPad T14 Gen 4 (PC-ACC-012)",
        "sla_text": "Còn 3h 15m (Mục tiêu 8h)",
        "sla_status": "safe",
        "sla_percent": 40,
        "assigned_to": "Nguyễn Văn An (KTV L2 - Bạn)",
        "created_at": "11:20 (3h 08m trước)",
        "is_active_target": False,
    },
    {
        "id": 1039,
        "code": "INC-#1039",
        "title": "Màn hình Dell UltraSharp 27 inch 4K bị chớp sọc ngang và mất tín hiệu chập chờn",
        "description": "Sau khi bật máy 20 phút màn hình bị giật hình, đã đổi thử cáp Type-C sang HDMI nhưng vẫn bị hiện tượng tương tự.",
        "priority": "P2 - CAO",
        "priority_level": "P2",
        "priority_color": "bg-amber-50 text-amber-700 border-amber-200",
        "priority_dot": "bg-amber-600",
        "status": "CHỜ TIẾP NHẬN",
        "status_color": "bg-purple-50 text-purple-700 border-purple-200",
        "status_dot": "bg-purple-600",
        "category": "Thiết bị ngoại vi",
        "requester": "Nguyễn Thu Trang",
        "department": "Phòng Marketing",
        "location": "Văn phòng Hà Nội • Tòa A • Tầng 5",
        "ext": "504",
        "device": "Dell UltraSharp U2723QE (MON-MKT-03)",
        "sla_text": "Còn 1h 25m (Mục tiêu 4h)",
        "sla_status": "warning",
        "sla_percent": 65,
        "assigned_to": "Chưa tiếp nhận",
        "created_at": "12:35 (1h 53m trước)",
        "is_active_target": False,
    },
    {
        "id": 1035,
        "code": "REQ-#1035",
        "title": "Cấu hình VPN FortiClient truy cập mạng nội bộ cho nhân sự đi công tác nước ngoài",
        "description": "Cần cấu hình tài khoản SSL-VPN và bật xác thực 2 bước (2FA) Microsoft Authenticator trước chuyến bay sáng mai.",
        "priority": "P3 - TRUNG BÌNH",
        "priority_level": "P3",
        "priority_color": "bg-blue-50 text-blue-700 border-blue-200",
        "priority_dot": "bg-blue-600",
        "status": "ĐANG XỬ LÝ",
        "status_color": "bg-blue-50 text-blue-700 border-blue-200",
        "status_dot": "bg-blue-600",
        "category": "Bảo mật & VPN",
        "requester": "Đặng Quốc Tuấn",
        "department": "Phòng Pháp chế",
        "location": "Làm việc từ xa (Remote)",
        "ext": "112",
        "device": "MacBook Pro 14 M2 (PC-LEG-003)",
        "sla_text": "Còn 4h 30m (Mục tiêu 8h)",
        "sla_status": "safe",
        "sla_percent": 35,
        "assigned_to": "Hoàng Minh Tú (KTV L1)",
        "created_at": "10:00 (4h 28m trước)",
        "is_active_target": False,
    },
    {
        "id": 1031,
        "code": "INC-#1031",
        "title": "Điện thoại IP Grandstream phòng Giám đốc không có âm hiệu quay số (No Dial Tone)",
        "description": "Điện thoại bàn lễ tân chuyển hướng cuộc gọi vào phòng Giám đốc thì báo bận liên tục, màn hình hiển thị SIP Unregistered.",
        "priority": "P2 - CAO",
        "priority_level": "P2",
        "priority_color": "bg-amber-50 text-amber-700 border-amber-200",
        "priority_dot": "bg-amber-600",
        "status": "CHỜ TIẾP NHẬN",
        "status_color": "bg-purple-50 text-purple-700 border-purple-200",
        "status_dot": "bg-purple-600",
        "category": "Hệ thống Thoại VoIP",
        "requester": "Vũ Thu Hương",
        "department": "Văn phòng Tổng Giám đốc",
        "location": "Văn phòng Hà Nội • Tòa A • Tầng 6",
        "ext": "601",
        "device": "Grandstream GRP2615 (VOIP-BOD-01)",
        "sla_text": "Còn 1h 45m (Mục tiêu 4h)",
        "sla_status": "safe",
        "sla_percent": 55,
        "assigned_to": "Chưa tiếp nhận",
        "created_at": "12:15 (2h 13m trước)",
        "is_active_target": False,
    },
    {
        "id": 1028,
        "code": "REQ-#1028",
        "title": "Cài đặt phần mềm lập trình VS Code, Docker Desktop và Git cho lập trình viên mới",
        "description": "Kỹ sư phần mềm mới onboard tuần này, đã có tài khoản AD, cần setup môi trường dev tiêu chuẩn công ty.",
        "priority": "P4 - THẤP",
        "priority_level": "P4",
        "priority_color": "bg-slate-100 text-slate-700 border-slate-200",
        "priority_dot": "bg-slate-500",
        "status": "CHỜ TIẾP NHẬN",
        "status_color": "bg-slate-100 text-slate-700 border-slate-200",
        "status_dot": "bg-slate-500",
        "category": "Cài đặt & Phần mềm",
        "requester": "Trịnh Công Minh",
        "department": "Khối Công nghệ & Phần mềm",
        "location": "Văn phòng Hà Nội • Tòa B • Tầng 3",
        "ext": "304",
        "device": "Dell Latitude 5530 (PC-DEV-044)",
        "sla_text": "Còn 14h (Mục tiêu 24h)",
        "sla_status": "safe",
        "sla_percent": 25,
        "assigned_to": "Chưa tiếp nhận",
        "created_at": "09:30 (4h 58m trước)",
        "is_active_target": False,
    },
]


def render_ticket_queue_view() -> None:
    def content(user: dict) -> None:
        selected_filter = {"tab": "ALL", "search": "", "dept": "ALL"}

        # -------------------------------------------------------------
        # 1. TOP BREADCRUMBS & SYNC STATUS
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-center flex-wrap gap-2 text-xs mb-1"):
            with ui.row().classes("items-center gap-1.5 text-slate-500 font-medium"):
                ui.label("Vận hành Kỹ thuật L2").classes("text-slate-500")
                ui.label("›").classes("text-slate-300 font-bold")
                ui.label("Hàng đợi xử lý sự cố & yêu cầu").classes("font-bold text-slate-800")
                with ui.element("span").classes("px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-[10px] font-extrabold ml-1"):
                    ui.label("18 TICKET ĐANG CHỜ")

            with ui.row().classes("items-center gap-3 text-slate-400 text-[11px]"):
                ui.label("Lần đồng bộ cuối: 14:28:19")
                with ui.row().classes("items-center gap-1 text-blue-600 font-semibold cursor-pointer hover:underline").on(
                    "click", lambda: toast.show("Đã đồng bộ hàng đợi xử lý mới nhất!", type="positive")
                ):
                    ui.icon("refresh", size="14px")
                    ui.label("Làm mới")

        # -------------------------------------------------------------
        # 2. PAGE TITLE & QUICK ACTIONS
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-center flex-wrap gap-3 mb-2"):
            with ui.column().classes("gap-0.5"):
                ui.label("Hàng đợi xử lý (Incident & Task Queue)").classes(
                    "text-xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Danh sách các ticket cần được tiếp nhận, phân loại và xử lý theo cam kết SLA của dịch vụ IT."
                ).classes("text-xs text-slate-500")

            with ui.row().classes("items-center gap-2"):
                with ui.button("Bàn làm việc vé hiện hành (#1048)", icon="troubleshoot", on_click=lambda: ui.navigate.to("/technician/detail/1048")).props(
                    "unelevated no-caps"
                ).classes("bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-sm shadow-blue-500/20"):
                    pass

        # -------------------------------------------------------------
        # 3. KPI SUMMARY STATS CARDS
        # -------------------------------------------------------------
        with ui.grid(columns=4).classes("w-full gap-3 mb-3"):
            # Card 1: Tất cả
            with ui.card().classes(
                "p-3 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between hover:border-blue-400 transition-all cursor-pointer"
            ).on("click", lambda: set_filter("ALL")):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Tất cả trong hàng đợi").classes("text-[11px] font-bold text-slate-500 uppercase tracking-wider")
                    ui.icon("inbox", size="18px").classes("text-slate-400")
                with ui.row().classes("items-baseline gap-2 mt-1"):
                    ui.label("18").classes("text-2xl font-black text-slate-900")
                    ui.label("vé tồn").classes("text-[11px] text-slate-400")

            # Card 2: P1 Khẩn cấp
            with ui.card().classes(
                "p-3 rounded-2xl bg-rose-50/50 border border-rose-200 shadow-xs flex flex-col justify-between hover:border-rose-400 transition-all cursor-pointer"
            ).on("click", lambda: set_filter("P1")):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("P1 - Khẩn cấp").classes("text-[11px] font-bold text-rose-700 uppercase tracking-wider")
                    ui.icon("warning", size="18px").classes("text-rose-500")
                with ui.row().classes("items-baseline gap-2 mt-1"):
                    ui.label("02").classes("text-2xl font-black text-rose-700")
                    ui.label("sát hạn SLA").classes("text-[11px] text-rose-500 font-medium")

            # Card 3: Đang xử lý
            with ui.card().classes(
                "p-3 rounded-2xl bg-blue-50/50 border border-blue-200 shadow-xs flex flex-col justify-between hover:border-blue-400 transition-all cursor-pointer"
            ).on("click", lambda: set_filter("IN_PROGRESS")):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Đang xử lý").classes("text-[11px] font-bold text-blue-700 uppercase tracking-wider")
                    ui.icon("pending_actions", size="18px").classes("text-blue-500")
                with ui.row().classes("items-baseline gap-2 mt-1"):
                    ui.label("05").classes("text-2xl font-black text-blue-700")
                    ui.label("bạn phụ trách 2").classes("text-[11px] text-blue-500 font-medium")

            # Card 4: Chờ tiếp nhận
            with ui.card().classes(
                "p-3 rounded-2xl bg-purple-50/50 border border-purple-200 shadow-xs flex flex-col justify-between hover:border-purple-400 transition-all cursor-pointer"
            ).on("click", lambda: set_filter("UNASSIGNED")):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Chờ tiếp nhận").classes("text-[11px] font-bold text-purple-700 uppercase tracking-wider")
                    ui.icon("assignment_late", size="18px").classes("text-purple-500")
                with ui.row().classes("items-baseline gap-2 mt-1"):
                    ui.label("07").classes("text-2xl font-black text-purple-700")
                    ui.label("cần phân công").classes("text-[11px] text-purple-500 font-medium")

        # -------------------------------------------------------------
        # 4. FILTER BAR & SEARCH
        # -------------------------------------------------------------
        with ui.card().classes("w-full p-3 rounded-2xl bg-white border border-slate-200/80 shadow-xs mb-3 space-y-2"):
            with ui.row().classes("w-full justify-between items-center flex-wrap gap-3"):
                # Search Input
                search_input = (
                    ui.input(placeholder="Tìm kiếm theo mã vé, tiêu đề, người yêu cầu, địa điểm (Ctrl + K)...")
                    .props("outlined dense clearable debounce=200")
                    .classes("flex-grow min-w-[300px] text-xs")
                )
                search_input.add_slot(
                    "prepend",
                    '<i class="q-icon material-icons text-slate-400 text-base">search</i>',
                )

                dept_select = (
                    ui.select(
                        options=["Tất cả phòng ban", "Phòng Kế toán", "Khối Kinh Doanh", "Phòng Kỹ thuật & R&D", "Phòng Marketing"],
                        value="Tất cả phòng ban",
                    )
                    .props("outlined dense")
                    .classes("w-48 text-xs")
                )

            # Filter Tab Pills
            with ui.row().classes("items-center gap-1.5 pt-1 border-t border-slate-100"):
                tab_all = ui.button("Tất cả (18)", on_click=lambda: set_filter("ALL")).props("unelevated dense no-caps").classes(
                    "px-3 py-1 rounded-lg text-xs font-bold bg-blue-600 text-white"
                )
                tab_p1 = ui.button("P1 - Khẩn cấp (2)", on_click=lambda: set_filter("P1")).props("flat dense no-caps").classes(
                    "px-3 py-1 rounded-lg text-xs font-semibold text-rose-700 hover:bg-rose-50"
                )
                tab_prog = ui.button("Đang xử lý (5)", on_click=lambda: set_filter("IN_PROGRESS")).props("flat dense no-caps").classes(
                    "px-3 py-1 rounded-lg text-xs font-semibold text-blue-700 hover:bg-blue-50"
                )
                tab_wait = ui.button("Chờ tiếp nhận (7)", on_click=lambda: set_filter("UNASSIGNED")).props("flat dense no-caps").classes(
                    "px-3 py-1 rounded-lg text-xs font-semibold text-purple-700 hover:bg-purple-50"
                )
                tab_sla = ui.button("Cảnh báo SLA (4)", on_click=lambda: set_filter("SLA")).props("flat dense no-caps").classes(
                    "px-3 py-1 rounded-lg text-xs font-semibold text-amber-700 hover:bg-amber-50"
                )

        # -------------------------------------------------------------
        # 5. TICKET LIST CONTAINER
        # -------------------------------------------------------------
        ticket_list_container = ui.column().classes("w-full gap-3")

        def set_filter(filter_type: str):
            selected_filter["tab"] = filter_type
            # Update button visual states
            tabs = [
                ("ALL", tab_all, "bg-blue-600 text-white font-bold", "flat text-slate-600 hover:bg-slate-100"),
                ("P1", tab_p1, "bg-rose-600 text-white font-bold", "flat text-rose-700 hover:bg-rose-50"),
                ("IN_PROGRESS", tab_prog, "bg-blue-600 text-white font-bold", "flat text-blue-700 hover:bg-blue-50"),
                ("UNASSIGNED", tab_wait, "bg-purple-600 text-white font-bold", "flat text-purple-700 hover:bg-purple-50"),
                ("SLA", tab_sla, "bg-amber-600 text-white font-bold", "flat text-amber-700 hover:bg-amber-50"),
            ]
            for t_type, btn, active_cls, inactive_props in tabs:
                if t_type == filter_type:
                    btn.props(remove="flat", add="unelevated")
                    btn.classes(replace=f"px-3 py-1 rounded-lg text-xs {active_cls}")
                else:
                    btn.props(remove="unelevated", add="flat")
                    btn.classes(replace=f"px-3 py-1 rounded-lg text-xs font-semibold {inactive_props.split(' ', 1)[1]}")

            render_queue_items()

        def render_queue_items():
            ticket_list_container.clear()
            query = (search_input.value or "").strip().lower()
            dept_val = dept_select.value
            tab = selected_filter["tab"]

            filtered = list(QUEUE_TICKETS)
            if tab == "P1":
                filtered = [t for t in filtered if t["priority_level"] == "P1"]
            elif tab == "IN_PROGRESS":
                filtered = [t for t in filtered if t["status"] == "ĐANG XỬ LÝ"]
            elif tab == "UNASSIGNED":
                filtered = [t for t in filtered if t["status"] == "CHỜ TIẾP NHẬN"]
            elif tab == "SLA":
                filtered = [t for t in filtered if t["sla_status"] == "warning"]

            if dept_val and dept_val != "Tất cả phòng ban":
                filtered = [t for t in filtered if dept_val.lower() in t["department"].lower()]

            if query:
                filtered = [
                    t for t in filtered
                    if query in t["title"].lower()
                    or query in t["code"].lower()
                    or query in t["requester"].lower()
                    or query in t["device"].lower()
                    or query in t["location"].lower()
                ]

            with ticket_list_container:
                if not filtered:
                    with ui.card().classes("w-full p-8 rounded-2xl bg-white border border-slate-200 text-center"):
                        ui.icon("search_off", size="40px").classes("text-slate-300 mx-auto mb-2")
                        ui.label("Không tìm thấy vé phù hợp").classes("text-sm font-bold text-slate-700")
                        ui.label("Vui lòng thử tìm với từ khóa hoặc bộ lọc khác.").classes("text-xs text-slate-400 mt-0.5")
                    return

                for ticket in filtered:
                    is_p1 = ticket["priority_level"] == "P1"
                    card_border = "border-rose-200 hover:border-rose-400 bg-rose-50/10" if is_p1 else "border-slate-200/80 hover:border-blue-400 bg-white"
                    active_highlight = "ring-2 ring-blue-500/20" if ticket.get("is_active_target") else ""

                    with ui.card().classes(
                        f"w-full p-4 rounded-2xl {card_border} {active_highlight} shadow-xs hover:shadow-md transition-all cursor-pointer group"
                    ).on("click", lambda t=ticket: ui.navigate.to(f"/technician/detail/{t['id']}")):
                        # Row 1: Header tags & SLA
                        with ui.row().classes("w-full justify-between items-start no-wrap gap-2"):
                            with ui.row().classes("items-center gap-2 flex-wrap"):
                                # Priority Pill
                                with ui.element("span").classes(
                                    f"px-2.5 py-0.5 rounded-md text-[11px] font-extrabold border {ticket['priority_color']} flex items-center gap-1.5 shadow-2xs"
                                ):
                                    ui.element("span").classes(f"w-1.5 h-1.5 rounded-full {ticket['priority_dot']}")
                                    ui.label(ticket["priority"])

                                # Status Pill
                                with ui.element("span").classes(
                                    f"px-2.5 py-0.5 rounded-md text-[11px] font-extrabold border {ticket['status_color']} flex items-center gap-1.5"
                                ):
                                    ui.element("span").classes(f"w-1.5 h-1.5 rounded-full {ticket['status_dot']}")
                                    ui.label(ticket["status"])

                                # Ticket Code
                                with ui.element("span").classes(
                                    "px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-slate-100 text-slate-700"
                                ):
                                    ui.label(ticket["code"])

                                # Category
                                with ui.element("span").classes(
                                    "text-[11px] font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200/60"
                                ):
                                    ui.label(ticket["category"])

                            # SLA Timer
                            with ui.row().classes("items-center gap-1.5 text-xs font-bold no-wrap"):
                                if ticket["sla_status"] == "warning":
                                    ui.icon("alarm", size="16px").classes("text-rose-600 animate-pulse")
                                    ui.label(ticket["sla_text"]).classes("text-rose-600 font-extrabold")
                                else:
                                    ui.icon("schedule", size="16px").classes("text-emerald-600")
                                    ui.label(ticket["sla_text"]).classes("text-slate-600")

                        # Row 2: Title
                        with ui.row().classes("w-full items-baseline justify-between gap-3 mt-1.5"):
                            ui.label(ticket["title"]).classes(
                                "text-sm md:text-base font-extrabold text-slate-900 group-hover:text-blue-600 transition-colors leading-snug"
                            )

                        # Row 3: Description snippet
                        ui.label(ticket["description"]).classes(
                            "text-xs text-slate-500 line-clamp-1 mt-0.5"
                        )

                        # Row 4: Details & Actions Footer
                        with ui.row().classes("w-full justify-between items-center pt-3 mt-2 border-t border-slate-100 flex-wrap gap-2 text-xs"):
                            with ui.row().classes("items-center gap-4 text-slate-600 flex-wrap"):
                                # Requester
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon("person", size="15px").classes("text-slate-400")
                                    ui.label(f"{ticket['requester']} ({ticket['department']})").classes("font-semibold text-slate-800")

                                # Location
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon("place", size="15px").classes("text-slate-400")
                                    ui.label(ticket["location"]).classes("text-slate-500")

                                # Device
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon("devices", size="15px").classes("text-slate-400")
                                    ui.label(ticket["device"]).classes("font-mono text-slate-700 text-[11px]")

                                # Assigned Tech
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon("engineering", size="15px").classes("text-blue-500")
                                    ui.label(ticket["assigned_to"]).classes("text-blue-700 font-medium")

                            # Action button
                            with ui.row().classes("items-center gap-2"):
                                with ui.button(
                                    "Xử lý chi tiết",
                                    icon="troubleshoot",
                                    on_click=lambda t=ticket: ui.navigate.to(f"/technician/detail/{t['id']}"),
                                ).props("unelevated dense no-caps").classes(
                                    "bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-3 py-1.5 rounded-xl shadow-xs"
                                ):
                                    pass

        search_input.on("update:model-value", lambda _: render_queue_items())
        dept_select.on("update:model-value", lambda _: render_queue_items())

        # Initial render
        render_queue_items()

    app_shell("Hàng đợi xử lý", content)
