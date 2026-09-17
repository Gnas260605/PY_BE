from collections.abc import Callable
from nicegui import ui


def navbar(
    title: str,
    user: dict,
    on_logout: Callable[[], None],
    on_toggle_sidebar: Callable[[], None] | None = None,
) -> None:
    initials = (user.get("ho_ten") or user.get("username") or "U")[:2].upper()
    display_name = user.get("ho_ten") or user.get("username")

    with ui.header().classes("bg-white text-slate-900 border-b border-slate-200 px-4 md:px-6 py-2.5 shadow-none sticky top-0 z-20"):
        with ui.row().classes("w-full items-center justify-between no-wrap"):
            # Left: Sidebar Toggle & Clean Title
            with ui.row().classes("items-center gap-3 no-wrap"):
                if on_toggle_sidebar:
                    ui.button(icon="menu", on_click=on_toggle_sidebar).props("flat round dense color=slate-700").classes("hover:bg-slate-100")
                ui.label(title).classes("text-base font-bold text-slate-900")

            # Right: User Avatar & Logout
            with ui.row().classes("items-center gap-3 no-wrap"):
                # User Chip
                with ui.row().classes("items-center gap-2 py-1 px-2.5 bg-slate-50 border border-slate-200 rounded-full"):
                    with ui.avatar(color="primary", text_color="white").props("size=26px font-size=11px").classes("font-bold"):
                        ui.label(initials)
                    ui.label(display_name).classes("text-xs font-semibold text-slate-700 hidden sm:block")

                # Logout button
                with ui.button(icon="logout", on_click=on_logout).props("flat round dense size=sm color=slate-500").classes("hover:bg-red-50 hover:text-red-600 transition-colors"):
                    ui.tooltip("Đăng xuất")
