from nicegui import ui


def skeleton_loader(count: int = 3, height: str = "h-20") -> None:
    """Renders sleek pulsing skeleton cards for async data loading state."""
    with ui.column().classes("w-full gap-3 animate-pulse"):
        for _ in range(count):
            with ui.card().classes(f"w-full {height} rounded-2xl bg-slate-100/90 border border-slate-200/60 p-4 shadow-none"):
                with ui.row().classes("w-full justify-between items-center"):
                    with ui.column().classes("gap-2 flex-1"):
                        ui.element("div").classes("w-1/3 h-4 bg-slate-200 rounded-md")
                        ui.element("div").classes("w-2/3 h-3 bg-slate-200/70 rounded-md")
                    with ui.row().classes("gap-2"):
                        ui.element("div").classes("w-16 h-6 bg-slate-200 rounded-full")
                        ui.element("div").classes("w-16 h-6 bg-slate-200 rounded-full")


def loading_spinner(message: str = "Đang tải dữ liệu...") -> None:
    """Renders a centered spinner with caption."""
    with ui.column().classes("w-full py-12 items-center justify-center gap-3 text-center"):
        ui.spinner(size="lg", color="primary")
        ui.label(message).classes("text-xs font-semibold text-slate-500")
