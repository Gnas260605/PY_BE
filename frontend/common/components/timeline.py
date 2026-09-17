from typing import Any
from nicegui import ui

from common.formatters import format_datetime

ACTION_ICONS = {
    "CREATED": ("add_circle", "text-blue-600 bg-blue-50 border-blue-200"),
    "UPDATED": ("edit", "text-slate-600 bg-slate-50 border-slate-200"),
    "ASSIGNED": ("person_add", "text-indigo-600 bg-indigo-50 border-indigo-200"),
    "STATUS_CHANGED": ("sync_alt", "text-amber-600 bg-amber-50 border-amber-200"),
    "CLOSED": ("lock", "text-emerald-600 bg-emerald-50 border-emerald-200"),
}


def audit_timeline(history_items: list[dict[str, Any]]) -> None:
    if not history_items:
        with ui.row().classes("w-full py-4 text-slate-400 text-sm justify-center items-center gap-2"):
            ui.icon("history").classes("text-lg")
            ui.label("Chưa có lịch sử thay đổi.")
        return

    with ui.column().classes("w-full gap-0 pl-2 relative"):
        for idx, item in enumerate(history_items):
            action = item.get("action") or item.get("hanh_dong") or "UPDATED"
            icon_name, style = ACTION_ICONS.get(action, ("circle", "text-slate-500 bg-slate-50 border-slate-200"))
            is_last = idx == len(history_items) - 1

            with ui.row().classes("w-full items-start gap-3 relative pb-6 no-wrap"):
                # Left vertical line
                if not is_last:
                    ui.element("div").classes("absolute left-4 top-8 bottom-0 w-0.5 bg-slate-200")

                # Icon marker
                with ui.element("div").classes(f"w-8 h-8 rounded-full border flex items-center justify-center shrink-0 z-10 {style}"):
                    ui.icon(icon_name).classes("text-sm")

                # Content
                with ui.column().classes("gap-0.5 flex-1 pt-0.5"):
                    with ui.row().classes("items-center gap-2 flex-wrap"):
                        ui.label(action).classes("text-xs font-bold text-slate-800 uppercase tracking-wide")
                        ui.label(format_datetime(item.get("performed_at") or item.get("thoi_gian"))).classes("text-[11px] text-slate-400")

                    old_s = item.get("old_status") or item.get("trang_thai_cu")
                    new_s = item.get("new_status") or item.get("trang_thai_moi")
                    if old_s or new_s:
                        with ui.row().classes("items-center gap-1.5 text-xs text-slate-600 mt-0.5"):
                            ui.label(old_s or "-").classes("font-semibold text-slate-500")
                            ui.icon("arrow_forward").classes("text-xs text-slate-400")
                            ui.label(new_s or "-").classes("font-semibold text-blue-600")

                    detail = item.get("detail") or item.get("chi_tiet_cap_nhat")
                    if detail:
                        ui.label(detail).classes("text-xs text-slate-600 mt-1 bg-slate-50 p-2 rounded-lg border border-slate-100")
