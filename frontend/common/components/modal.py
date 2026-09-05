from collections.abc import Callable

from nicegui import ui


def confirm_dialog(title: str, message: str, on_confirm: Callable[[], None]) -> ui.dialog:
    dialog = ui.dialog()
    with dialog, ui.card().classes("w-full max-w-md rounded-2xl"):
        ui.label(title).classes("text-lg font-bold")
        ui.label(message).classes("text-sm text-slate-600")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Hủy", on_click=dialog.close).props("flat")
            ui.button("Xác nhận", on_click=lambda: (on_confirm(), dialog.close())).props("color=primary")
    return dialog
