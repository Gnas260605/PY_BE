from nicegui import ui

from common.components.sidebar import get_role_sections


def bottom_nav(role: str) -> None:
    sections = get_role_sections(role)
    nav_items = [item for _, items in sections for item in items]
    with ui.footer().classes("md:hidden bg-white border-t border-slate-200 text-slate-700"):
        with ui.row().classes("w-full justify-around"):
            for label, target, icon in nav_items[:4]:
                with ui.link(target=target).classes("no-underline text-slate-700"):
                    with ui.column().classes("items-center gap-0 py-1"):
                        ui.icon(icon).classes("text-xl")
                        ui.label(label).classes("text-[10px]")
