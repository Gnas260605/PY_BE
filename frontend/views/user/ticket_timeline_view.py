from nicegui import ui

from common.components.layout import app_shell
from common.formatters import format_datetime
from services.ticket_service import ticket_service


def render_ticket_timeline_view(ticket_id: int) -> None:
    def content(user: dict) -> None:
        ui.label(f"Lịch sử Ticket #{ticket_id}").classes("text-3xl font-bold text-slate-900")
        holder = ui.column().classes("w-full mt-4 gap-2")

        async def load() -> None:
            try:
                history = await ticket_service.get_history(ticket_id)
                holder.clear()
                with holder:
                    for item in history:
                        with ui.card().classes("w-full p-4 rounded-2xl border border-slate-100"):
                            ui.label(item.get("action", "-")).classes("font-bold")
                            ui.label(f"{item.get('old_status') or '-'} → {item.get('new_status') or '-'}").classes("text-sm text-slate-600")
                            ui.label(format_datetime(item.get("performed_at"))).classes("text-xs text-slate-500")
                            if item.get("detail"):
                                ui.label(item["detail"]).classes("text-sm")
            except Exception as exc:
                holder.clear()
                with holder:
                    ui.label(str(exc)).classes("text-red-600")

        ui.timer(0.1, load, once=True)

    app_shell("Ticket Timeline", content)
