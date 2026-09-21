from __future__ import annotations

from typing import Any
from nicegui import ui

from common.formatters import format_datetime, format_relative_time
from core.constants import ACTION_LABELS, STATUS_LABELS

ACTION_CONFIG: dict[str, dict[str, str]] = {
    "CREATED": {
        "title": "Tạo phiếu sự cố",
        "icon": "add_circle",
        "badge": "bg-blue-50 text-blue-700 border-blue-200",
        "color": "text-blue-600",
    },
    "UPDATED": {
        "title": "Cập nhật thông tin",
        "icon": "edit",
        "badge": "bg-slate-50 text-slate-700 border-slate-200",
        "color": "text-slate-600",
    },
    "ASSIGNED": {
        "title": "Phân công kỹ thuật viên",
        "icon": "person_add",
        "badge": "bg-indigo-50 text-indigo-700 border-indigo-200",
        "color": "text-indigo-600",
    },
    "STATUS_CHANGED": {
        "title": "Thay đổi trạng thái",
        "icon": "sync_alt",
        "badge": "bg-amber-50 text-amber-800 border-amber-200",
        "color": "text-amber-600",
    },
    "RESOLVED": {
        "title": "Đã giải quyết sự cố",
        "icon": "check_circle",
        "badge": "bg-emerald-50 text-emerald-700 border-emerald-200",
        "color": "text-emerald-600",
    },
    "CLOSED": {
        "title": "Đóng phiếu hoàn tất",
        "icon": "lock",
        "badge": "bg-slate-100 text-slate-800 border-slate-300",
        "color": "text-slate-700",
    },
    "REOPENED": {
        "title": "Mở lại sự cố",
        "icon": "replay",
        "badge": "bg-rose-50 text-rose-700 border-rose-200",
        "color": "text-rose-600",
    },
}


def translate_detail(text: str | None) -> str | None:
    if not text:
        return None
    translated = text
    translated = translated.replace("Status changed to RESOLVED", "Chuyển trạng thái sang Đã giải quyết")
    translated = translated.replace("Status changed to IN_PROGRESS", "Chuyển trạng thái sang Đang xử lý")
    translated = translated.replace("Status changed to CLOSED", "Chuyển trạng thái sang Đã đóng")
    translated = translated.replace("Status changed to ASSIGNED", "Chuyển trạng thái sang Đã phân công")
    translated = translated.replace("Status changed to OPEN", "Chuyển trạng thái sang Mở lại")
    translated = translated.replace("Assigned to technician", "Phân công cho kỹ thuật viên")
    return translated


def audit_timeline(history_items: list[dict[str, Any]]) -> None:
    if not history_items:
        with ui.column().classes("w-full py-10 items-center justify-center text-center gap-2 bg-slate-50/60 rounded-xl border border-dashed border-slate-200"):
            ui.icon("history", size="32px").classes("text-slate-400")
            ui.label("Chưa có lịch sử hoạt động ghi nhận").classes("text-sm font-bold text-slate-700")
            ui.label("Mọi thao tác thay đổi trạng thái và phân công sẽ được tự động lưu lại tại đây.").classes("text-xs text-slate-500 max-w-sm")
        return

    with ui.column().classes("w-full gap-0 pl-3 relative py-2"):
        for idx, item in enumerate(history_items):
            raw_action = item.get("action") or item.get("hanh_dong") or "UPDATED"
            cfg = ACTION_CONFIG.get(raw_action, {
                "title": ACTION_LABELS.get(raw_action, raw_action),
                "icon": "radio_button_checked",
                "badge": "bg-slate-50 text-slate-700 border-slate-200",
                "color": "text-slate-600",
            })

            is_last = idx == len(history_items) - 1
            raw_time = item.get("performed_at") or item.get("thoi_gian")
            time_str = format_datetime(raw_time)
            rel_time = format_relative_time(raw_time)

            with ui.row().classes("w-full items-start gap-4 relative pb-7 no-wrap"):
                # Left continuous vertical line
                if not is_last:
                    ui.element("div").classes("absolute left-4 top-9 bottom-0 w-0.5 bg-slate-200")

                # Icon marker
                with ui.element("div").classes(
                    f"w-8 h-8 rounded-full border flex items-center justify-center shrink-0 z-10 bg-white shadow-2xs {cfg['badge']}"
                ):
                    ui.icon(cfg["icon"], size="18px").classes(cfg["color"])

                # Content card
                with ui.column().classes("gap-1.5 flex-1 pt-0.5"):
                    with ui.row().classes("items-center justify-between flex-wrap gap-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(cfg["title"]).classes("text-sm font-bold text-slate-900")
                            ui.label(f"• {rel_time}").classes("text-xs text-slate-400 font-medium")

                        ui.label(time_str).classes("text-xs text-slate-400 font-mono")

                    old_s = item.get("old_status") or item.get("trang_thai_cu")
                    new_s = item.get("new_status") or item.get("trang_thai_moi")
                    if old_s or new_s:
                        old_label = STATUS_LABELS.get(old_s, old_s or "-")
                        new_label = STATUS_LABELS.get(new_s, new_s or "-")
                        with ui.row().classes("items-center gap-2 text-xs py-1 px-2.5 rounded-lg bg-slate-50 border border-slate-200 w-fit"):
                            ui.label("Trạng thái:").classes("text-slate-500 font-medium")
                            ui.label(old_label).classes("font-semibold text-slate-600")
                            ui.icon("arrow_forward", size="14px").classes("text-slate-400")
                            ui.label(new_label).classes("font-bold text-blue-700")

                    raw_detail = item.get("detail") or item.get("chi_tiet_cap_nhat")
                    detail = translate_detail(raw_detail)
                    if detail:
                        with ui.element("div").classes("text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-100/90 leading-relaxed"):
                            ui.label(detail)
