from nicegui import ui


def stat_card(title: str, value: str | int, subtitle: str, icon: str = "analytics") -> None:
    with ui.card().classes("glass-card w-full p-5 rounded-2xl shadow-sm border border-slate-100"):
        with ui.row().classes("w-full justify-between items-start no-wrap"):
            with ui.column().classes("gap-1"):
                ui.label(title).classes("text-xs font-semibold tracking-wide text-slate-500 uppercase")
                ui.label(str(value)).classes("text-3xl font-bold text-slate-900")
                ui.label(subtitle).classes("text-xs text-slate-500")
            ui.icon(icon).classes("text-3xl text-blue-600 bg-blue-50 rounded-xl p-2")
