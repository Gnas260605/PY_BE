from nicegui import ui


def resolution_note_field() -> ui.textarea:
    return ui.textarea("Ghi chú xử lý").props("outlined").classes("w-full")
