from nicegui import ui

NAV_ITEMS = {
    "ADMIN": [
        ("Tổng quan vận hành", "/dashboard", "grid_view", None),
        ("Quản lý phân công & SLA", "/admin/tickets", "assignment_ind", None),
        ("Thiết bị & Tài sản", "/admin/devices", "devices", None),
        ("Người dùng & Phân quyền", "/admin/users", "group", None),
        ("Cài đặt hệ thống", "/admin/settings", "settings", None),
    ],
    "TECHNICIAN": [
        ("Tổng quan vận hành", "/dashboard", "grid_view", None),
        ("Hàng đợi xử lý", "/technician/tasks", "inbox", "18"),
        ("Xử lý chi tiết", "/technician/detail", "troubleshoot", None),
        ("Quản lý phân công & SLA", "/technician/sla", "assignment_ind", None),
        ("Thiết bị & Tài sản", "/technician/devices", "devices", None),
        ("Cài đặt hệ thống", "/technician/settings", "settings", None),
    ],
    "USER": [
        ("Tổng quan", "/dashboard", "grid_view", None),
        ("Ticket của tôi", "/user/tickets", "confirmation_number", "3"),
        ("Tạo yêu cầu", "/user/tickets/new", "add_circle_outline", None),
    ],
}


def sidebar(role: str, user_info: dict | None = None):
    items = NAV_ITEMS.get(role, NAV_ITEMS["USER"])
    user = user_info or {}
    ho_ten = user.get("ho_ten") or ("Nguyễn Văn An" if role == "TECHNICIAN" else "Trần Thị Mai")
    phong_ban = user.get("phong_ban") or ("Phòng IT Helpdesk" if role == "TECHNICIAN" else "Phòng Kế toán")
    initial = (ho_ten[0] if ho_ten else "A").upper()

    try:
        current_path = ui.context.client.page.path
    except Exception:
        current_path = ""

    subtitle = "Cổng Vận Hành IT" if role == "TECHNICIAN" else "Cổng hỗ trợ IT"

    with ui.left_drawer(value=True).classes(
        "bg-white text-slate-700 border-r border-slate-200 flex flex-col justify-between p-0 shadow-none z-30"
    ).props("width=260 bordered") as drawer:
        with ui.column().classes("w-full p-0 gap-0"):
            # Brand Header
            with ui.row().classes("w-full items-center gap-3 px-5 py-4 border-b border-slate-100 no-wrap"):
                with ui.element("div").classes(
                    "w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20 shrink-0"
                ):
                    ui.icon("support_agent").classes("text-xl text-white")
                with ui.column().classes("gap-0"):
                    ui.label("HelpDesk Pro").classes("text-base font-bold text-slate-900 tracking-tight leading-none")
                    ui.label(subtitle).classes("text-xs text-slate-500 mt-1")

            # Technician Online Status Banner
            if role == "TECHNICIAN":
                with ui.row().classes(
                    "w-full items-center justify-between px-4 py-2 bg-emerald-50/60 border-b border-emerald-100/80 no-wrap"
                ):
                    with ui.row().classes("items-center gap-2 no-wrap"):
                        ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500 animate-pulse")
                        ui.label("Sẵn sàng nhận việc").classes("text-[11px] font-semibold text-emerald-800")
                    with ui.element("span").classes(
                        "px-1.5 py-0.5 rounded text-[10px] font-extrabold tracking-wider bg-emerald-100 text-emerald-700 border border-emerald-200"
                    ):
                        ui.label("ONLINE")

            # Nav items
            with ui.column().classes("w-full px-3 py-3 gap-1"):
                for label, target, icon, badge in items:
                    if target == "/technician/tasks":
                        is_active = current_path in ("/technician/tasks", "/technician/queue", "/technician")
                    elif target == "/technician/detail":
                        is_active = current_path.startswith("/technician/detail")
                    elif target in ("/technician/sla", "/admin/tickets"):
                        is_active = current_path in ("/technician/sla", "/admin/tickets", "/admin/sla")
                    elif target in ("/technician/devices", "/admin/devices"):
                        is_active = current_path in ("/technician/devices", "/admin/devices")
                    elif target in ("/technician/settings", "/admin/settings"):
                        is_active = current_path in ("/technician/settings", "/admin/settings")
                    else:
                        is_active = (current_path == target)
                    link_classes = (
                        "rounded-xl px-3 py-2 flex items-center justify-between transition-all "
                        + ("bg-blue-600 text-white font-semibold shadow-sm" if is_active else "text-slate-600 hover:bg-slate-50 hover:text-blue-600")
                    )
                    icon_color = "text-white" if is_active else "text-slate-400 group-hover:text-blue-600"
                    label_color = "text-white font-bold" if is_active else "text-slate-700 font-medium"

                    with ui.link(target=target).classes("no-underline w-full block"):
                        with ui.item().classes(link_classes):
                            with ui.row().classes("items-center gap-3 no-wrap"):
                                ui.icon(icon).classes(f"{icon_color} text-lg")
                                ui.label(label).classes(f"text-xs {label_color}")
                            if badge:
                                badge_bg = "bg-white/20 text-white" if is_active else "bg-blue-100 text-blue-700"
                                with ui.element("span").classes(
                                    f"px-2 py-0.5 rounded-md {badge_bg} text-[11px] font-bold leading-tight"
                                ):
                                    ui.label(str(badge))

        # Bottom Section
        with ui.column().classes("w-full p-4 border-t border-slate-100 gap-3"):
            if role == "TECHNICIAN":
                # Technician SLA Warning Box from Image 1
                with ui.element("div").classes(
                    "w-full p-3 rounded-2xl bg-rose-50/80 border border-rose-200 text-rose-800 flex items-center justify-between"
                ):
                    with ui.column().classes("gap-0"):
                        ui.label("SLA Vi phạm hôm nay").classes("text-[11px] font-medium text-rose-600 leading-tight")
                        ui.label("02 ticket").classes("text-base font-extrabold text-rose-700 leading-tight mt-0.5")
                    ui.icon("warning", size="22px").classes("text-rose-500 shrink-0")
            else:
                # Help Center link
                with ui.item().classes("rounded-xl px-2 py-1.5 hover:bg-slate-50 transition-all flex items-center gap-3 cursor-pointer"):
                    ui.icon("help_outline").classes("text-slate-400 text-lg")
                    ui.label("Trung tâm trợ giúp").classes("text-xs font-medium text-slate-600")

                # User Profile Pill
                with ui.element("div").classes(
                    "w-full bg-blue-50/70 border border-blue-100/80 p-3 rounded-2xl flex items-center gap-3"
                ):
                    with ui.element("div").classes(
                        "w-9 h-9 rounded-xl bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-sm shrink-0"
                    ):
                        ui.label(initial)
                    with ui.column().classes("gap-0 overflow-hidden"):
                        ui.label(ho_ten).classes("text-xs font-bold text-slate-900 truncate leading-tight")
                        ui.label(phong_ban).classes("text-[11px] text-slate-500 truncate leading-tight")

    return drawer

    return drawer
