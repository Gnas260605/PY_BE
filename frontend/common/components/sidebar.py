from collections.abc import Callable
from nicegui import ui

ROLE_SECTIONS = {
    "ADMIN": [
        (
            "TỔNG QUAN",
            [
                ("Dashboard", "/dashboard", "grid_view"),
                ("Giám sát sự cố", "/admin/tickets", "confirmation_number"),
            ],
        ),
        (
            "QUẢN TRỊ TÀI NGUYÊN",
            [
                ("Danh mục thiết bị", "/admin/devices", "devices"),
                ("Quản lý người dùng", "/admin/users", "manage_accounts"),
            ],
        ),
        (
            "TIỆN ÍCH & CÀI ĐẶT",
            [
                ("Tạo ticket mới", "/user/tickets/new", "add_circle"),
                ("Tra cứu lịch sử máy", "/technician/devices", "search"),
                ("Cài đặt cá nhân", "/settings", "settings"),
            ],
        ),
    ],
    "TECHNICIAN": [
        (
            "BÀN LÀM VIỆC",
            [
                ("Dashboard", "/dashboard", "grid_view"),
                ("Bàn làm việc KTV", "/technician/tasks", "assignment"),
            ],
        ),
        (
            "CÔNG CỤ & CÀI ĐẶT",
            [
                ("Tra cứu thiết bị", "/technician/devices", "search"),
                ("Cài đặt cá nhân", "/settings", "settings"),
            ],
        ),
    ],
    "USER": [
        (
            "HỖ TRỢ DỊCH VỤ",
            [
                ("Yêu cầu của tôi", "/user/tickets", "confirmation_number"),
                ("Tạo yêu cầu hỗ trợ", "/user/tickets/new", "add_circle"),
                ("Cài đặt cá nhân", "/settings", "settings"),
            ],
        ),
    ],
}

ROLE_TAGS = {
    "ADMIN": ("bg-purple-500/20 text-purple-300 border-purple-500/40", "ADMIN PORTAL"),
    "TECHNICIAN": ("bg-amber-500/20 text-amber-300 border-amber-500/40", "TECH WORKSPACE"),
    "USER": ("bg-blue-500/20 text-blue-300 border-blue-500/40", "USER DESK"),
}

NAV_ITEMS = {
    role: [item for _, items in section_list for item in items]
    for role, section_list in ROLE_SECTIONS.items()
}



def sidebar(role: str, user: dict | None = None, on_logout: Callable[[], None] | None = None):
    tag_class, tag_text = ROLE_TAGS.get(role, ("bg-slate-700 text-slate-300 border-slate-600", "PORTAL"))
    sections = ROLE_SECTIONS.get(role, ROLE_SECTIONS["USER"])

    initials = ((user.get("ho_ten") or user.get("username") or "U") if user else "U")[:2].upper()
    display_name = (user.get("ho_ten") or user.get("username") or "Người dùng") if user else "Người dùng"
    username = (user.get("username") or "") if user else ""

    with ui.left_drawer(value=True).classes("bg-slate-900 text-slate-200 border-r border-slate-800 flex flex-col justify-between p-0").props("width=250 bordered") as drawer:
        with ui.column().classes("w-full p-0 gap-0"):
            # Brand Header
            with ui.row().classes("w-full items-center gap-2.5 p-4 border-b border-slate-800 no-wrap"):
                with ui.element("div").classes("w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md shadow-blue-500/10"):
                    ui.icon("support_agent").classes("text-lg")
                with ui.column().classes("gap-0.5"):
                    ui.label("CS466 Helpdesk").classes("text-sm font-bold text-white tracking-tight leading-none")
                    ui.label(tag_text).classes(f"text-[9px] font-bold px-1.5 py-0.2 rounded border {tag_class} uppercase tracking-wider inline-block mt-0.5")

            # Grouped Navigation Sections
            with ui.column().classes("w-full px-3 py-2 gap-3"):
                for section_title, items in sections:
                    with ui.column().classes("w-full gap-1"):
                        ui.label(section_title).classes("text-[10px] font-bold tracking-wider text-slate-400 uppercase px-2 pt-1")
                        for label, target, icon in items:
                            with ui.link(target=target).classes("no-underline text-slate-300 hover:text-white w-full block"):
                                with ui.item().classes("rounded-lg px-2.5 py-2 hover:bg-slate-800/80 transition-all flex items-center gap-2.5"):
                                    with ui.item_section().props("avatar min-width=0").classes("min-w-0 pr-0"):
                                        ui.icon(icon).classes("text-slate-400 text-base")
                                    with ui.item_section():
                                        ui.label(label).classes("text-xs font-semibold")

        # Bottom User Profile Card (Replaces the "Trực tuyến" status)
        with ui.column().classes("w-full p-3 border-t border-slate-800 bg-slate-950/50"):
            with ui.row().classes("w-full items-center justify-between no-wrap p-1.5 rounded-lg bg-slate-900 border border-slate-800/80"):
                with ui.row().classes("items-center gap-2 no-wrap flex-1 min-w-0"):
                    with ui.avatar(color="primary", text_color="white").props("size=30px font-size=11px").classes("font-bold shrink-0"):
                        ui.label(initials)
                    with ui.column().classes("gap-0 min-w-0 flex-1"):
                        ui.label(display_name).classes("text-xs font-bold text-white leading-tight truncate")
                        ui.label(f"@{username}").classes("text-[10px] text-slate-400 leading-tight truncate")

                if on_logout:
                    with ui.button(icon="logout", on_click=on_logout).props("flat round dense size=sm color=slate-400").classes("hover:text-red-400 shrink-0"):
                        ui.tooltip("Đăng xuất")

    return drawer
