from collections.abc import Callable
from nicegui import ui


def success(message: str, caption: str | None = None) -> None:
    ui.notify(
        message,
        type="positive",
        position="top",
        caption=caption,
        icon="check_circle",
        close_button=True,
        duration=4000,
    )


def error(message: str, caption: str | None = None) -> None:
    ui.notify(
        message,
        type="negative",
        position="top",
        caption=caption,
        icon="error",
        close_button=True,
        duration=5000,
    )


def warning(message: str, caption: str | None = None) -> None:
    ui.notify(
        message,
        type="warning",
        position="top",
        caption=caption,
        icon="warning",
        close_button=True,
        duration=4000,
    )


def info(message: str, caption: str | None = None) -> None:
    ui.notify(
        message,
        type="info",
        position="top",
        caption=caption,
        icon="info",
        close_button=True,
        duration=3500,
    )


def show_popup(
    title: str,
    message: str,
    *,
    type: str = "success",
    detail: str | None = None,
    on_confirm: Callable[[], None] | None = None,
    confirm_text: str = "Đồng ý",
) -> None:
    """Shows a modern modal dialog popup with explicit status indicator."""
    dialog = ui.dialog()
    
    icon_map = {
        "success": ("check_circle", "text-emerald-500", "bg-emerald-50", "border-emerald-200"),
        "error": ("error", "text-red-500", "bg-red-50", "border-red-200"),
        "warning": ("warning", "text-amber-500", "bg-amber-50", "border-amber-200"),
        "info": ("info", "text-blue-500", "bg-blue-50", "border-blue-200"),
    }
    icon_name, icon_color, bg_color, border_color = icon_map.get(
        type, ("info", "text-blue-500", "bg-blue-50", "border-blue-200")
    )

    with dialog, ui.card().classes("w-full max-w-md p-6 rounded-2xl bg-white border border-slate-200 shadow-xl gap-4"):
        with ui.row().classes("w-full items-start gap-3.5"):
            with ui.element("div").classes(f"w-10 h-10 rounded-xl {bg_color} {border_color} border flex items-center justify-center shrink-0"):
                ui.icon(icon_name).classes(f"text-2xl {icon_color}")
            with ui.column().classes("flex-1 gap-1"):
                ui.label(title).classes("text-base font-bold text-slate-900 leading-snug")
                ui.label(message).classes("text-xs text-slate-600 leading-relaxed")
                if detail:
                    ui.label(detail).classes("text-[11px] text-slate-400 mt-1 font-mono bg-slate-50 p-2 rounded border border-slate-100 whitespace-pre-wrap")

        with ui.row().classes("w-full justify-end gap-2 pt-2 border-t border-slate-100"):
            def handle_close() -> None:
                dialog.close()
                if on_confirm:
                    on_confirm()

            btn_color = "primary" if type in ("success", "info") else ("red" if type == "error" else "amber")
            ui.button(confirm_text, on_click=handle_close).props(f"color={btn_color} unelevated").classes("px-4 text-xs font-bold")

    dialog.open()
