from nicegui import ui

from core.constants import PRIORITY_LABELS, ROLE_LABELS, STATUS_LABELS

STATUS_CONFIG = {
    "OPEN": ("bg-blue-50 text-blue-700 border-blue-200/80", "fiber_manual_record"),
    "ASSIGNED": ("bg-indigo-50 text-indigo-700 border-indigo-200/80", "person_outline"),
    "IN_PROGRESS": ("bg-amber-50 text-amber-800 border-amber-200/80", "sync"),
    "RESOLVED": ("bg-emerald-50 text-emerald-700 border-emerald-200/80", "check_circle"),
    "CLOSED": ("bg-slate-100 text-slate-600 border-slate-200/80", "lock"),
    "ACTIVE": ("bg-emerald-50 text-emerald-700 border-emerald-200/80", "check"),
    "MAINTENANCE": ("bg-amber-50 text-amber-800 border-amber-200/80", "build"),
    "BROKEN": ("bg-rose-50 text-rose-700 border-rose-200/80", "error_outline"),
    "INACTIVE": ("bg-slate-100 text-slate-500 border-slate-200/80", "block"),
}

PRIORITY_CONFIG = {
    "LOW": ("bg-slate-100 text-slate-600 border-slate-200/80", "south_east"),
    "MEDIUM": ("bg-sky-50 text-sky-700 border-sky-200/80", "remove"),
    "HIGH": ("bg-amber-50 text-amber-800 border-amber-200/80", "north_east"),
    "URGENT": ("bg-rose-50 text-rose-700 border-rose-300 font-bold", "bolt"),
}

ROLE_CONFIG = {
    "ADMIN": ("bg-purple-50 text-purple-700 border-purple-200/80", "admin_panel_settings"),
    "TECHNICIAN": ("bg-amber-50 text-amber-800 border-amber-200/80", "handyman"),
    "USER": ("bg-blue-50 text-blue-700 border-blue-200/80", "person"),
}


def status_badge(value: str | None) -> None:
    normalized = value or "-"
    label = STATUS_LABELS.get(normalized, normalized)
    classes, icon_name = STATUS_CONFIG.get(normalized, ("bg-slate-100 text-slate-700 border-slate-200", "info"))
    with ui.row().classes(f"inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold {classes} no-wrap shrink-0 tracking-tight shadow-2xs"):
        ui.icon(icon_name).classes("text-[10px]")
        ui.label(label)


def priority_badge(value: str | None) -> None:
    normalized = value or "-"
    label = PRIORITY_LABELS.get(normalized, normalized)
    classes, icon_name = PRIORITY_CONFIG.get(normalized, ("bg-slate-100 text-slate-700 border-slate-200", "remove"))
    with ui.row().classes(f"inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold {classes} no-wrap shrink-0 tracking-tight shadow-2xs"):
        ui.icon(icon_name).classes("text-[11px]")
        ui.label(label)


def role_badge(value: str | None) -> None:
    normalized = value or "-"
    label = ROLE_LABELS.get(normalized, normalized)
    classes, icon_name = ROLE_CONFIG.get(normalized, ("bg-slate-100 text-slate-700 border-slate-200", "person"))
    with ui.row().classes(f"inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold {classes} no-wrap shrink-0 tracking-tight shadow-2xs"):
        ui.icon(icon_name).classes("text-[11px]")
        ui.label(label)
