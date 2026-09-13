from nicegui import ui


ICON_THEMES = {
    "confirmation_number": ("text-blue-600", "bg-blue-50/80 border-blue-100"),
    "pending_actions": ("text-amber-600", "bg-amber-50/80 border-amber-100"),
    "verified": ("text-emerald-600", "bg-emerald-50/80 border-emerald-100"),
    "devices": ("text-purple-600", "bg-purple-50/80 border-purple-100"),
    "groups": ("text-indigo-600", "bg-indigo-50/80 border-indigo-100"),
    "cloud_off": ("text-rose-600", "bg-rose-50/80 border-rose-100"),
}


def stat_card(title: str, value: str | int, subtitle: str, icon: str = "analytics") -> None:
    text_color, bg_color = ICON_THEMES.get(icon, ("text-blue-600", "bg-blue-50/80 border-blue-100"))

    with ui.card().classes("card-hover w-full p-5 rounded-2xl bg-white border border-slate-200/70 shadow-sm relative overflow-hidden"):
        with ui.row().classes("w-full justify-between items-start no-wrap"):
            with ui.column().classes("gap-1.5 flex-1"):
                ui.label(title).classes("text-xs font-bold tracking-wider text-slate-400 uppercase")
                ui.label(str(value)).classes("text-3xl font-extrabold text-slate-900 tracking-tight leading-none my-0.5")
                with ui.row().classes("items-center gap-1.5 mt-1"):
                    ui.element("span").classes("w-1.5 h-1.5 rounded-full bg-slate-300")
                    ui.label(subtitle).classes("text-xs text-slate-500 font-medium")
            with ui.element("div").classes(f"p-3 rounded-xl border {bg_color} flex items-center justify-center shrink-0 shadow-sm"):
                ui.icon(icon).classes(f"text-2xl {text_color}")
