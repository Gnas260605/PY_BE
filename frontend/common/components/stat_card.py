from nicegui import ui

ICON_THEMES = {
    "confirmation_number": ("text-blue-600", "bg-blue-50 border-blue-100"),
    "pending_actions": ("text-amber-600", "bg-amber-50 border-amber-100"),
    "verified": ("text-emerald-600", "bg-emerald-50 border-emerald-100"),
    "devices": ("text-indigo-600", "bg-indigo-50 border-indigo-100"),
    "groups": ("text-purple-600", "bg-purple-50 border-purple-100"),
    "priority_high": ("text-red-600", "bg-red-50 border-red-100"),
    "cloud_off": ("text-rose-600", "bg-rose-50 border-rose-100"),
}


def stat_card(title: str, value: str | int, subtitle: str, icon: str = "analytics") -> None:
    text_color, bg_color = ICON_THEMES.get(icon, ("text-blue-600", "bg-blue-50 border-blue-100"))

    with ui.card().classes("card-hover w-full p-5 rounded-xl bg-white border border-slate-200 shadow-sm relative overflow-hidden"):
        with ui.row().classes("w-full justify-between items-start no-wrap"):
            with ui.column().classes("gap-1 flex-1"):
                ui.label(title).classes("text-xs font-bold tracking-wider text-slate-500 uppercase")
                ui.label(str(value)).classes("text-2xl font-extrabold text-slate-900 tracking-tight leading-none my-1")
                with ui.row().classes("items-center gap-1.5 mt-0.5"):
                    ui.label(subtitle).classes("text-xs text-slate-500 font-medium")
            with ui.element("div").classes(f"w-11 h-11 rounded-lg border {bg_color} flex items-center justify-center shrink-0 shadow-sm"):
                ui.icon(icon).classes(f"text-xl {text_color}")
