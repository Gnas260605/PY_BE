from nicegui import ui

from core.constants import PRIORITY_LABELS, STATUS_LABELS


STATUS_CLASSES = {
    "OPEN": "bg-blue-100 text-blue-800 border-blue-200",
    "ASSIGNED": "bg-indigo-100 text-indigo-800 border-indigo-200",
    "IN_PROGRESS": "bg-amber-100 text-amber-800 border-amber-200",
    "RESOLVED": "bg-emerald-100 text-emerald-800 border-emerald-200",
    "CLOSED": "bg-slate-100 text-slate-700 border-slate-200",
    "ACTIVE": "bg-emerald-100 text-emerald-800 border-emerald-200",
    "MAINTENANCE": "bg-amber-100 text-amber-800 border-amber-200",
    "BROKEN": "bg-red-100 text-red-800 border-red-200",
    "INACTIVE": "bg-slate-100 text-slate-700 border-slate-200",
}

PRIORITY_CLASSES = {
    "LOW": "bg-slate-100 text-slate-700 border-slate-200",
    "MEDIUM": "bg-blue-100 text-blue-800 border-blue-200",
    "HIGH": "bg-orange-100 text-orange-800 border-orange-200",
    "URGENT": "bg-red-100 text-red-800 border-red-200",
}


def status_badge(value: str | None) -> None:
    normalized = value or "-"
    label = STATUS_LABELS.get(normalized, normalized)
    ui.label(label).classes(
        f"inline-flex px-3 py-1 rounded-full border text-xs font-semibold {STATUS_CLASSES.get(normalized, 'bg-slate-100 text-slate-700 border-slate-200')}"
    )


def priority_badge(value: str | None) -> None:
    normalized = value or "-"
    label = PRIORITY_LABELS.get(normalized, normalized)
    ui.label(label).classes(
        f"inline-flex px-3 py-1 rounded-full border text-xs font-semibold {PRIORITY_CLASSES.get(normalized, 'bg-slate-100 text-slate-700 border-slate-200')}"
    )
