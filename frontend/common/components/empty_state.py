from collections.abc import Callable
from nicegui import ui


def empty_state(
    title: str = "Chưa có dữ liệu",
    subtitle: str = "Hiện không có mục nào để hiển thị trong danh sách.",
    icon: str = "inbox",
    action_label: str | None = None,
    on_action: Callable[[], None] | None = None,
) -> None:
    with ui.column().classes("w-full items-center justify-center py-12 px-4 gap-2 text-center"):
        with ui.element("div").classes("w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-1"):
            ui.icon(icon).classes("text-3xl")
        ui.label(title).classes("text-base font-bold text-slate-800")
        ui.label(subtitle).classes("text-sm text-slate-500 max-w-sm")
        if action_label and on_action:
            ui.button(action_label, on_click=on_action).props("color=primary unelevated").classes("mt-2")
