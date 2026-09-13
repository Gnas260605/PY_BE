from collections.abc import Callable

from nicegui import ui

from core.constants import ROLE_LABELS


ROLE_BADGES = {
    "ADMIN": "bg-purple-100 text-purple-800 border-purple-200",
    "TECHNICIAN": "bg-amber-100 text-amber-800 border-amber-200",
    "USER": "bg-blue-100 text-blue-800 border-blue-200",
}


def navbar(
    title: str,
    user: dict,
    on_logout: Callable[[], None],
    on_toggle_sidebar: Callable[[], None] | None = None,
) -> None:
    initials = (user.get("ho_ten") or user.get("username") or "U")[:2].upper()
    role_raw = user.get("vai_tro", "USER")
    role_label = ROLE_LABELS.get(role_raw, role_raw)
    badge_style = ROLE_BADGES.get(role_raw, "bg-slate-100 text-slate-700 border-slate-200")

    with ui.header().classes("bg-white/90 backdrop-blur-md text-slate-900 border-b border-slate-200/80 px-4 md:px-6 py-2.5 shadow-sm sticky top-0 z-20"):
        with ui.row().classes("w-full items-center justify-between no-wrap"):
            # Left: Toggle & Title
            with ui.row().classes("items-center gap-3 no-wrap"):
                if on_toggle_sidebar:
                    ui.button(icon="menu", on_click=on_toggle_sidebar).props("flat round dense color=slate-700").classes("hover:bg-slate-100")
                with ui.column().classes("gap-0"):
                    with ui.row().classes("items-center gap-2"):
                        ui.label("HelpDesk").classes("text-xs font-semibold text-slate-400 hidden sm:block")
                        ui.label("/").classes("text-xs text-slate-300 hidden sm:block")
                        ui.label(title).classes("text-base font-bold text-slate-900 tracking-tight")

            # Right: User Profile & Actions
            with ui.row().classes("items-center gap-3 no-wrap"):
                # Role Badge
                ui.label(role_label).classes(f"hidden sm:inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold border {badge_style}")

                # User Info & Avatar
                with ui.row().classes("items-center gap-2.5 bg-slate-50/80 hover:bg-slate-100/80 transition-colors border border-slate-200/60 rounded-full py-1 px-2.5"):
                    with ui.avatar(color="primary", text_color="white").props("size=32px font-size=12px").classes("shadow-sm font-bold"):
                        ui.label(initials)
                    with ui.column().classes("gap-0 hidden md:flex"):
                        ui.label(user.get("ho_ten") or user.get("username")).classes("text-xs font-bold text-slate-800 leading-tight")
                        ui.label(f"@{user.get('username')}").classes("text-[10px] text-slate-500 leading-tight")

                # Logout button
                with ui.button(icon="logout", on_click=on_logout).props("flat round dense color=negative").classes("hover:bg-red-50 text-slate-600 hover:text-red-600 transition-colors"):
                    ui.tooltip("Đăng xuất khỏi hệ thống")
