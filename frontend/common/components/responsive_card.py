from nicegui import ui

from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime, truncate


def ticket_card(ticket: dict, on_detail=None, on_action=None) -> None:
    title = ticket.get("title") or ticket.get("tieu_de") or f"Ticket #{ticket.get('id', '-')}"
    with ui.card().classes("w-full p-4 rounded-2xl shadow-sm border border-slate-100"):
        with ui.row().classes("w-full justify-between items-start gap-2"):
            ui.label(f"#{ticket.get('id', '-')} · {title}").classes("text-base font-bold text-slate-900")
            status_badge(ticket.get("status") or ticket.get("trang_thai"))
        ui.label(truncate(ticket.get("description") or ticket.get("mo_ta"), 120)).classes("text-sm text-slate-600 line-clamp-2")
        with ui.row().classes("w-full justify-between text-xs text-slate-500 pt-2 border-t border-slate-100"):
            priority_badge(ticket.get("priority") or ticket.get("muc_do_uu_tien"))
            ui.label(format_datetime(ticket.get("updated_at") or ticket.get("created_at")))
        with ui.row().classes("w-full justify-end gap-2 pt-2"):
            if on_detail:
                ui.button("Chi tiết", on_click=lambda ticket=ticket: on_detail(ticket)).props("flat color=primary")
            if on_action:
                ui.button("Thao tác", on_click=lambda ticket=ticket: on_action(ticket)).props("color=primary")
