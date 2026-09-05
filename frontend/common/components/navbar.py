from collections.abc import Callable

from nicegui import ui

from core.constants import ROLE_LABELS


def navbar(title: str, user: dict, on_logout: Callable[[], None]) -> None:
    initials = (user.get("ho_ten") or user.get("username") or "U")[:2].upper()
    role = ROLE_LABELS.get(user.get("vai_tro"), user.get("vai_tro", "-"))

    with ui.header().classes("bg-white text-slate-900 border-b border-slate-200 px-4 md:px-6"):
        with ui.row().classes("w-full items-center justify-between no-wrap"):
            with ui.row().classes("items-center gap-3 no-wrap"):
                ui.icon("support_agent").classes("text-blue-600 text-3xl")
                with ui.column().classes("gap-0"):
                    ui.label(title).classes("text-lg font-bold")
                    ui.label(role).classes("text-xs text-slate-500")
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label(user.get("ho_ten") or user.get("username")).classes("hidden sm:block text-sm text-slate-600")
                ui.avatar(text=initials, color="primary", text_color="white")
                ui.button(icon="logout", on_click=on_logout).props("flat round color=primary")
