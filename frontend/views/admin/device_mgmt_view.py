from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.layout import app_shell


ITAM_DEVICES: list[dict[str, Any]] = [
    {
        "code": "PRN-ACC-04",
        "name": "HP LaserJet Pro M404dn",
        "icon": "print",
        "icon_color": "text-blue-600 bg-blue-50 border-blue-100",
        "category": "Máy in & Ngoại vi",
        "specs": "Duplex, Ethernet, 38 ppm",
        "user_name": "Trần Thị Mai",
        "dept_location": "Phòng Kế toán - Tòa A (P.402)",
        "ip": "192.168.4.155",
        "mac": "00:1E:68:5B:32:11",
        "status": "IN_USE",
    },
    {
        "code": "LAP-DEV-089",
        "name": "Apple MacBook Pro 16\"",
        "icon": "laptop_mac",
        "icon_color": "text-indigo-600 bg-indigo-50 border-indigo-100",
        "category": "Laptop Cao Cấp",
        "specs": "M3 Pro, 36GB, 512GB SSD",
        "user_name": "Nguyễn Hoàng Quân",
        "dept_location": "Kỹ sư Phần mềm - Tòa B (P.601)",
        "ip": "10.20.1.45",
        "mac": "A4:83:E7:22:91:04",
        "status": "IN_USE",
    },
    {
        "code": "LAP-FIN-012",
        "name": "Lenovo ThinkPad T14 G4",
        "icon": "laptop",
        "icon_color": "text-slate-700 bg-slate-100 border-slate-200",
        "category": "Laptop Doanh nghiệp",
        "specs": "Intel Core i7, 16GB, 512GB",
        "user_name": "Đỗ Thu Hà",
        "dept_location": "Trưởng phòng HR - Tòa A (P.301)",
        "ip": "192.168.4.88",
        "mac": "54:E1:AD:77:23:41",
        "status": "IN_USE",
    },
    {
        "code": "SW-T4-A",
        "name": "Cisco Catalyst 9300",
        "icon": "router",
        "icon_color": "text-emerald-600 bg-emerald-50 border-emerald-100",
        "category": "Thiết bị Mạng Switch",
        "specs": "48-Port PoE+, 10G Uplink",
        "user_name": "Hạ tầng Mạng Tầng 4",
        "dept_location": "Phòng Kỹ thuật Network Ops",
        "ip": "192.168.1.4",
        "mac": "70:69:79:AB:09:12",
        "status": "IN_USE",
    },
    {
        "code": "SRV-APP-01",
        "name": "Dell PowerEdge R750",
        "icon": "dns",
        "icon_color": "text-purple-600 bg-purple-50 border-purple-100",
        "category": "Máy chủ Ứng dụng",
        "specs": "2x Xeon Silver, 128GB RAM",
        "user_name": "ERP SAP Nội Bộ",
        "dept_location": "Data Center DC-01 (Rack 04)",
        "ip": "10.10.0.12",
        "mac": "18:66:DA:21:40:99",
        "status": "IN_USE",
    },
]


def render_device_mgmt_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro", "TECHNICIAN")

        # -------------------------------------------------------------
        # 1. HEADER & TOP ACTION BUTTONS
        # -------------------------------------------------------------
        with ui.row().classes("w-full justify-between items-start flex-wrap gap-3 mb-1"):
            with ui.column().classes("gap-1 max-w-2xl"):
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.label("Quản lý Tài sản CNTT & Thiết bị (IT Asset Management - ITAM)").classes(
                        "text-xl md:text-2xl font-black text-slate-900 tracking-tight"
                    )
                    with ui.element("span").classes(
                        "px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-100 text-blue-700"
                    ):
                        ui.label("CMDB Lifecycle v3.2 - ISO/IEC 19770")

                ui.label(
                    "Theo dõi vòng đời phần cứng, phần mềm, giấy phép bản quyền và gán thiết bị theo người dùng/phòng ban "
                    "với cảnh báo bảo hành thời gian thực."
                ).classes("text-xs text-slate-500 leading-relaxed")

            # Action Buttons
            with ui.row().classes("items-center gap-2 flex-wrap"):
                with ui.button(
                    "Thêm thiết bị mới",
                    icon="add",
                    on_click=lambda: toast.show("Mở biểu mẫu nhập tài sản IT mới", type="info"),
                ).props("unelevated dense no-caps").classes(
                    "bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl shadow-xs"
                ):
                    pass

                with ui.button(
                    "Nhập CSV / AD",
                    icon="file_upload",
                    on_click=lambda: toast.show("Mở wizard đồng bộ danh sách thiết bị từ Active Directory", type="info"),
                ).props("flat dense no-caps").classes(
                    "bg-white border border-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-xl hover:bg-slate-50"
                ):
                    pass

                with ui.button(
                    "Quét mạng (Discovery)",
                    icon="track_changes",
                    on_click=lambda: toast.show("Đang bắt đầu quét SNMP/ARP trên các subnet VLAN nội bộ...", type="info"),
                ).props("flat dense no-caps").classes(
                    "bg-white border border-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-xl hover:bg-slate-50"
                ):
                    pass

        # -------------------------------------------------------------
        # 2. 4 TOP METRIC STATS CARDS
        # -------------------------------------------------------------
        with ui.grid(columns=4).classes("w-full gap-3 mb-3"):
            # Metric 1: Tổng tài sản
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("TỔNG TÀI SẢN QUẢN LÝ").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center"):
                        ui.icon("devices", size="18px")
                with ui.column().classes("gap-0.5 mt-1"):
                    ui.label("1,428").classes("text-2xl font-black text-slate-900")
                    with ui.row().classes("items-center gap-1 text-[11px] text-emerald-600 font-semibold"):
                        ui.icon("arrow_upward", size="13px")
                        ui.label("+12 thiết bị mới tháng này")

            # Metric 2: Đang sử dụng
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("ĐANG SỬ DỤNG (IN-USE)").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center"):
                        ui.icon("power", size="18px")
                with ui.column().classes("gap-1 mt-1"):
                    ui.label("1,280").classes("text-2xl font-black text-slate-900")
                    with ui.row().classes("w-full items-center justify-between text-[11px]"):
                        ui.label("Tỷ lệ phân bổ:").classes("text-slate-400")
                        ui.label("89.6%").classes("font-bold text-emerald-700 font-mono")
                    with ui.element("div").classes("w-full h-1.5 rounded-full bg-slate-100 overflow-hidden"):
                        ui.element("div").classes("h-full bg-emerald-500 rounded-full").style("width: 89.6%")

            # Metric 3: Cảnh báo bảo hành
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("CẢNH BÁO BẢO HÀNH & BẢO TRÌ").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center"):
                        ui.icon("notification_important", size="18px")
                with ui.column().classes("gap-0.5 mt-1"):
                    ui.label("24").classes("text-2xl font-black text-rose-600")
                    with ui.row().classes("items-center gap-1 text-[11px] text-rose-600 font-semibold"):
                        ui.icon("warning", size="13px")
                        ui.label("Cần gia hạn trong 30 ngày tới")

            # Metric 4: Báo sự cố
            with ui.card().classes("p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs flex flex-col justify-between"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("BÁO SỰ CỐ / TRONG SỬA CHỮA").classes("text-[11px] font-bold text-slate-500 tracking-wider")
                    with ui.element("div").classes("w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center"):
                        ui.icon("build", size="18px")
                with ui.column().classes("gap-0.5 mt-1"):
                    ui.label("15").classes("text-2xl font-black text-slate-900")
                    with ui.row().classes("items-center gap-1 text-[11px] text-blue-600 font-semibold"):
                        ui.label("18 Ticket đang mở liên kết trực tiếp")

        # -------------------------------------------------------------
        # 3. FILTER TOOLBAR & SEARCH
        # -------------------------------------------------------------
        with ui.card().classes("w-full p-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs mb-3 space-y-2.5"):
            with ui.row().classes("w-full justify-between items-center flex-wrap gap-2"):
                search_input = (
                    ui.input(placeholder="Tìm theo Tên máy, Số Serial, Địa chỉ MAC, Người dùng phụ trách, IP...")
                    .props("outlined dense clearable debounce=200")
                    .classes("flex-grow min-w-[320px] text-xs")
                )
                search_input.add_slot("prepend", '<i class="q-icon material-icons text-slate-400 text-base">search</i>')

                with ui.row().classes("items-center gap-1.5"):
                    ui.button("Tất cả (1,428)").props("unelevated dense no-caps").classes(
                        "bg-slate-900 text-white font-bold text-xs px-3 py-1.5 rounded-xl"
                    )
                    ui.button("Cảnh báo (39)").props("flat dense no-caps").classes(
                        "bg-slate-100 text-slate-700 hover:bg-slate-200 font-semibold text-xs px-3 py-1.5 rounded-xl"
                    )
                    ui.button("Xuất báo cáo (Excel/PDF)", icon="file_download", on_click=lambda: toast.show("Đang xuất báo cáo tài sản ITAM...", type="info")).props(
                        "flat dense no-caps"
                    ).classes("bg-slate-100 text-slate-700 hover:bg-slate-200 font-semibold text-xs px-3 py-1.5 rounded-xl")

            with ui.row().classes("w-full items-center justify-between pt-2 border-t border-slate-100 flex-wrap gap-2 text-xs"):
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.label("Lọc theo:").classes("text-slate-400 font-semibold")
                    ui.select(
                        options=["Tất cả danh mục (Category)", "Máy in & Ngoại vi", "Laptop", "Thiết bị Mạng", "Máy chủ"],
                        value="Tất cả danh mục (Category)",
                    ).props("outlined dense").classes("w-44 text-xs")

                    ui.select(
                        options=["Tất cả trạng thái (Status)", "Đang sử dụng (IN-USE)", "Bảo trì / Sửa chữa", "Trong kho"],
                        value="Tất cả trạng thái (Status)",
                    ).props("outlined dense").classes("w-44 text-xs")

                    ui.select(
                        options=["Tất cả vị trí (Location)", "Tòa A", "Tòa B", "Data Center DC-01"],
                        value="Tất cả vị trí (Location)",
                    ).props("outlined dense").classes("w-44 text-xs")

                    with ui.element("span").classes("px-2 py-1 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold flex items-center gap-1"):
                        ui.label("Tòa A & B")
                        ui.icon("close", size="14px").classes("cursor-pointer hover:text-blue-900")

                ui.link("Xóa tất cả bộ lọc", "#").classes("text-slate-400 hover:text-blue-600 text-xs font-semibold no-underline")

        # -------------------------------------------------------------
        # 4. MAIN 2-COLUMN LAYOUT (Table 8 cols + Sidebar 4 cols)
        # -------------------------------------------------------------
        with ui.grid(columns=12).classes("w-full gap-4 items-start"):
            # ================= LEFT COLUMN: TABLE (8 COLS) =================
            with ui.column().classes("col-span-12 lg:col-span-8 gap-3"):
                with ui.card().classes("w-full p-0 rounded-2xl bg-white border border-slate-200/90 shadow-xs overflow-hidden"):
                    # Table Top Bar
                    with ui.row().classes("w-full justify-between items-center p-3.5 border-b border-slate-100 bg-slate-50/50"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("inventory_2", size="18px").classes("text-blue-600")
                            ui.label("Danh mục Tài sản CNTT (IT Asset Registry)").classes("text-xs font-bold text-slate-900")
                            with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-mono text-slate-500 bg-slate-100"):
                                ui.label("1,428 items")

                        with ui.row().classes("items-center gap-1"):
                            with ui.button(icon="refresh", on_click=lambda: toast.show("Đã cập nhật danh mục thiết bị!", type="positive")).props("flat dense round text-color=slate-500"):
                                pass
                            with ui.button(icon="view_column").props("flat dense round text-color=slate-500"):
                                pass

                    # Table Header
                    with ui.grid(columns=12).classes("w-full px-4 py-2.5 bg-slate-100/70 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200/70"):
                        ui.label("MÃ & TÊN THIẾT BỊ").classes("col-span-4")
                        ui.label("DANH MỤC / CẤU HÌNH").classes("col-span-3")
                        ui.label("NGƯỜI SỬ DỤNG / VỊ TRÍ").classes("col-span-3")
                        ui.label("MẠNG (IP & MAC)").classes("col-span-2 text-right")

                    # Table Rows
                    for dev in ITAM_DEVICES:
                        with ui.grid(columns=12).classes(
                            "w-full px-4 py-3 items-center border-b border-slate-100 hover:bg-slate-50/80 transition-colors text-xs"
                        ):
                            # Col 1: Mã & Tên thiết bị
                            with ui.row().classes("col-span-4 items-center gap-3 no-wrap"):
                                with ui.element("div").classes(
                                    f"w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border {dev['icon_color']}"
                                ):
                                    ui.icon(dev["icon"], size="18px")
                                with ui.column().classes("gap-0"):
                                    ui.label(dev["code"]).classes("font-mono font-bold text-blue-600 text-[11px]")
                                    ui.label(dev["name"]).classes("font-extrabold text-slate-900 text-xs")

                            # Col 2: Danh mục & Cấu hình
                            with ui.column().classes("col-span-3 gap-0"):
                                ui.label(dev["category"]).classes("font-semibold text-slate-800 text-[11px]")
                                ui.label(dev["specs"]).classes("text-[10px] text-slate-400 font-mono")

                            # Col 3: Người dùng & Vị trí
                            with ui.column().classes("col-span-3 gap-0"):
                                ui.label(dev["user_name"]).classes("font-bold text-slate-800 text-[11px]")
                                ui.label(dev["dept_location"]).classes("text-[10px] text-slate-500")

                            # Col 4: Mạng (IP & MAC)
                            with ui.column().classes("col-span-2 gap-0 text-right font-mono"):
                                ui.label(dev["ip"]).classes("font-bold text-slate-800 text-[11px]")
                                ui.label(dev["mac"]).classes("text-[10px] text-slate-400")

                    # Pagination Footer
                    with ui.row().classes("w-full justify-between items-center px-4 py-3 bg-slate-50/50 text-xs text-slate-500 flex-wrap gap-2"):
                        ui.label("Hiển thị 1 - 5 của 1,428 tài sản | Trang 1/286")
                        with ui.row().classes("items-center gap-1"):
                            ui.button("Trước").props("flat dense no-caps text-color=slate-500").classes("text-xs")
                            ui.button("1").props("unelevated dense no-caps").classes("bg-blue-600 text-white font-bold text-xs px-2.5 py-0.5 rounded-lg")
                            ui.button("2").props("flat dense no-caps text-color=slate-700").classes("text-xs px-2.5 py-0.5")
                            ui.button("3").props("flat dense no-caps text-color=slate-700").classes("text-xs px-2.5 py-0.5")
                            ui.label("...").classes("px-1 text-slate-400")
                            ui.button("286").props("flat dense no-caps text-color=slate-700").classes("text-xs px-2.5 py-0.5")
                            ui.button("Sau").props("flat dense no-caps text-color=slate-500").classes("text-xs")

            # ================= RIGHT COLUMN: CARDS (4 COLS) =================
            with ui.column().classes("col-span-12 lg:col-span-4 gap-3"):
                # Card 1: Cảnh báo vòng đời (Lifecycle)
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("warning_amber", size="18px").classes("text-rose-600")
                            ui.label("Cảnh báo vòng đời (Lifecycle)").classes("text-xs font-bold text-slate-900")
                        with ui.element("span").classes("px-2 py-0.5 rounded-full bg-rose-100 text-rose-700 text-[10px] font-bold"):
                            ui.label("2 Cần xử lý")

                    # Lifecycle item 1
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50/70 border border-slate-200/70 space-y-1.5"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.element("span").classes("w-2 h-2 rounded-full bg-rose-600")
                                ui.label("Khấu hao thiết bị Laptop").classes("text-xs font-bold text-slate-800")
                            with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700"):
                                ui.label("5 Thiết bị")
                        ui.label(
                            "5 Laptop Dell Latitude 5400 của phòng Sales đã đạt chu kỳ 36 tháng khấu hao tài chính. Đề xuất lập kế hoạch thay thế đợt Q4."
                        ).classes("text-[11px] text-slate-500 leading-tight")
                        with ui.row().classes("w-full justify-between items-center text-[10px] pt-1"):
                            ui.label("Hạn kiểm kê: 15/11/2024").classes("text-slate-400")
                            ui.link("Tạo kế hoạch đổi máy", "#").classes("text-blue-600 font-bold no-underline hover:underline")

                    # Lifecycle item 2
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50/70 border border-slate-200/70 space-y-1.5"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.element("span").classes("w-2 h-2 rounded-full bg-rose-600")
                                ui.label("Bản quyền Microsoft 365 E5").classes("text-xs font-bold text-slate-800")
                            with ui.element("span").classes("px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700 font-mono"):
                                ui.label("12 License")
                        ui.label(
                            "12 gói giấy phép phần mềm M365 E5 cấp phát cho khối Quản lý sẽ hết hạn trong 15 ngày tới. Tránh gián đoạn hòm thư Exchange."
                        ).classes("text-[11px] text-slate-500 leading-tight")
                        with ui.row().classes("w-full justify-between items-center text-[10px] pt-1"):
                            ui.label("Hạn chót: 10 ngày nữa").classes("text-rose-600 font-semibold")
                            ui.link("Gia hạn PO bản quyền", "#").classes("text-blue-600 font-bold no-underline hover:underline")

                # Card 2: Phân bổ theo phòng ban
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-3"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("pie_chart", size="18px").classes("text-blue-600")
                            ui.label("Phân bổ theo phòng ban").classes("text-xs font-bold text-slate-900")
                        with ui.element("span").classes("px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold"):
                            ui.label("89.6% Đã gán")

                    # Donut chart + legend
                    with ui.row().classes("w-full items-center justify-between gap-3"):
                        # Center Donut mockup
                        with ui.element("div").classes(
                            "w-24 h-24 rounded-full border-8 border-blue-600 border-t-emerald-500 border-r-amber-500 flex flex-col items-center justify-center shrink-0"
                        ):
                            ui.label("1,280").classes("text-base font-black text-slate-900 leading-none")
                            ui.label("ĐANG GÁN").classes("text-[8px] font-bold text-slate-400 mt-0.5")

                        # Department distribution list
                        with ui.column().classes("gap-1 text-[11px] flex-grow"):
                            with ui.row().classes("w-full justify-between items-center"):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.element("span").classes("w-2 h-2 rounded-full bg-blue-600")
                                    ui.label("Khối Kỹ thuật (Dev&R&D)").classes("text-slate-700")
                                ui.label("538 (42%)").classes("font-mono font-bold text-slate-900")

                            with ui.row().classes("w-full justify-between items-center"):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500")
                                    ui.label("Kinh doanh & Marketing").classes("text-slate-700")
                                ui.label("332 (26%)").classes("font-mono font-bold text-slate-900")

                            with ui.row().classes("w-full justify-between items-center"):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.element("span").classes("w-2 h-2 rounded-full bg-amber-500")
                                    ui.label("Vận hành, HR & Tài chính").classes("text-slate-700")
                                ui.label("230 (18%)").classes("font-mono font-bold text-slate-900")

                            with ui.row().classes("w-full justify-between items-center"):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.element("span").classes("w-2 h-2 rounded-full bg-slate-400")
                                    ui.label("Hạ tầng chung & DataCenter").classes("text-slate-700")
                                ui.label("180 (14%)").classes("font-mono font-bold text-slate-900")

                    # Physical device bar
                    with ui.column().classes("w-full pt-2 border-t border-slate-100 gap-1"):
                        ui.label("Phân bổ Loại thiết bị vật lý:").classes("text-[10px] font-bold text-slate-400")
                        with ui.element("div").classes("w-full h-2 rounded-full bg-slate-100 flex overflow-hidden"):
                            ui.element("div").classes("h-full bg-blue-600").style("width: 55%")
                            ui.element("div").classes("h-full bg-indigo-500").style("width: 25%")
                            ui.element("div").classes("h-full bg-emerald-500").style("width: 12%")
                            ui.element("div").classes("h-full bg-slate-400").style("width: 8%")
                        with ui.row().classes("w-full justify-between text-[9px] text-slate-500 pt-0.5"):
                            ui.label("Laptop (55%)")
                            ui.label("Monitor (25%)")
                            ui.label("Network (12%)")
                            ui.label("Khác (8%)")

                # Card 3: Discovery Scanner Daemon
                with ui.card().classes("w-full p-4 rounded-2xl bg-white border border-slate-200/90 shadow-xs space-y-2"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("sensors", size="18px").classes("text-emerald-600")
                            ui.label("Discovery Scanner Daemon").classes("text-xs font-bold text-slate-900")
                        with ui.element("span").classes("px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800"):
                            ui.label("ACTIVE")

                    ui.label(
                        "Dải mạng VLAN 10 (Hạ tầng Máy chủ) và VLAN 40 (Thiết bị Khối Kế toán) vừa hoàn tất quét ARP & SNMP tự động 10 phút trước."
                    ).classes("text-[11px] text-slate-500 leading-tight")

                    with ui.row().classes("w-full justify-between items-center pt-1 text-[11px]"):
                        ui.label("Phát hiện 0 thiết bị lạ (Rogue Devices)").classes("font-semibold text-slate-600")
                        with ui.link("Cấu hình subnet →", "#").classes("text-blue-600 font-bold no-underline hover:underline"):
                            pass

    app_shell("Quản lý thiết bị & Tài sản IT", content)
