from nicegui import ui

from common.components.sidebar import NAV_ITEMS


def bottom_nav(role: str) -> None:
    with ui.footer().classes("md:hidden bg-white border-t border-slate-200 text-slate-700"):
        with ui.row().classes("w-full justify-around"):
            for label, target, icon in NAV_ITEMS.get(role, NAV_ITEMS["USER"])[:4]:
                with ui.link(target=target).classes("no-underline text-slate-700"):
                    with ui.column().classes("items-center gap-0 py-1"):
                        ui.icon(icon).classes("text-xl")
                        ui.label(label).classes("text-[10px]")
