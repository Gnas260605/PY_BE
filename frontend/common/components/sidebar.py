from nicegui import ui


NAV_ITEMS = {
    "ADMIN": [
        ("Dashboard", "/dashboard", "dashboard"),
        ("Tickets", "/admin/tickets", "confirmation_number"),
        ("Users", "/admin/users", "groups"),
        ("Devices", "/admin/devices", "devices"),
    ],
    "TECHNICIAN": [
        ("Dashboard", "/dashboard", "dashboard"),
        ("My Tasks", "/technician/tasks", "task_alt"),
        ("Devices", "/technician/devices", "devices"),
    ],
    "USER": [
        ("Dashboard", "/dashboard", "dashboard"),
        ("My Tickets", "/user/tickets", "confirmation_number"),
        ("Create Ticket", "/user/tickets/new", "add_circle"),
    ],
}


ROLE_TAGS = {
    "ADMIN": ("bg-purple-500/20 text-purple-300 border-purple-500/30", "ADMIN PORTAL"),
    "TECHNICIAN": ("bg-amber-500/20 text-amber-300 border-amber-500/30", "TECH WORKSPACE"),
    "USER": ("bg-blue-500/20 text-blue-300 border-blue-500/30", "USER DESK"),
}


def sidebar(role: str):
    tag_class, tag_text = ROLE_TAGS.get(role, ("bg-slate-700 text-slate-300 border-slate-600", "PORTAL"))
    items = NAV_ITEMS.get(role, NAV_ITEMS["USER"])

    with ui.left_drawer(value=True).classes("bg-slate-950 text-slate-200 border-r border-slate-800/80 flex flex-col justify-between p-0").props("width=260 bordered") as drawer:
        with ui.column().classes("w-full p-0 gap-0"):
            # Brand Header
            with ui.row().classes("w-full items-center gap-3 p-5 border-b border-slate-800/80 no-wrap"):
                with ui.element("div").classes("w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20 shrink-0"):
                    ui.icon("support_agent").classes("text-xl text-white")
                with ui.column().classes("gap-0.5"):
                    ui.label("HelpDesk Pro").classes("text-base font-bold text-white tracking-tight leading-none")
                    ui.label(tag_text).classes(f"text-[10px] font-bold px-2 py-0.5 rounded-full border {tag_class} uppercase tracking-wider inline-block mt-1")

            # Section Title
            with ui.row().classes("px-5 pt-4 pb-2"):
                ui.label("ĐIỀU HƯỚNG").classes("text-[11px] font-bold tracking-wider text-slate-500 uppercase")

            # Menu items
            with ui.column().classes("w-full px-2 gap-1"):
                for label, target, icon in items:
                    with ui.link(target=target).classes("no-underline text-slate-300 hover:text-white w-full block"):
                        with ui.item().classes("rounded-xl px-3 py-2.5 hover:bg-slate-800/60 transition-all duration-150 flex items-center gap-3"):
                            with ui.item_section().props("avatar min-width=0").classes("min-w-0 pr-0"):
                                ui.icon(icon).classes("text-slate-400 text-lg group-hover:text-blue-400")
                            with ui.item_section():
                                ui.label(label).classes("text-sm font-medium")

        # Bottom System Card
        with ui.column().classes("w-full p-4 border-t border-slate-800/80 gap-2"):
            with ui.card().classes("w-full bg-slate-900/80 border border-slate-800 p-3 rounded-xl shadow-none"):
                with ui.row().classes("items-center gap-2"):
                    ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-400 animate-pulse")
                    ui.label("Hệ thống: Sẵn sàng").classes("text-xs font-semibold text-slate-300")
                ui.label("FastAPI · MySQL 8.0 · NiceGUI").classes("text-[11px] text-slate-500 mt-1")

    return drawer
