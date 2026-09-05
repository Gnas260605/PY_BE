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


def sidebar(role: str) -> None:
    with ui.left_drawer(value=True).classes("bg-slate-900 text-white"):
        ui.label("HelpDesk Pro").classes("text-xl font-bold p-4")
        for label, target, icon in NAV_ITEMS.get(role, NAV_ITEMS["USER"]):
            with ui.link(target=target).classes("no-underline text-white"):
                with ui.item().classes("rounded-lg mx-2 my-1"):
                    with ui.item_section().props("avatar"):
                        ui.icon(icon)
                    ui.item_section(label)
