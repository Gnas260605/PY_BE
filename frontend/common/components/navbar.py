from collections.abc import Callable
from nicegui import ui

from core.constants import ROLE_LABELS


def navbar(
    title: str,
    user: dict,
    on_logout: Callable[[], None],
    on_toggle_sidebar: Callable[[], None] | None = None,
) -> None:
    ho_ten = user.get("ho_ten") or "Trần Thị Mai"
    role_raw = user.get("vai_tro", "USER")
    role_label = ROLE_LABELS.get(role_raw, "Nhân viên")
    if role_raw == "USER":
        role_label = "Nhân viên"
    elif role_raw == "TECHNICIAN":
        role_label = "Quản trị viên & Kỹ thuật viên L2"
        ho_ten = user.get("ho_ten") or "Nguyễn Văn An"

    search_ph = "Tìm kiếm ticket, tài sản, nhân sự (Ctrl + K)..." if role_raw == "TECHNICIAN" else "Tìm kiếm ticket theo mã hoặc tiêu đề... (Ctrl + K)"

    with ui.header().classes(
        "bg-white text-slate-900 border-b border-slate-200/90 px-4 md:px-6 py-0 shadow-none h-12 flex items-center"
    ):
        with ui.row().classes("w-full items-center justify-between no-wrap gap-3 h-full"):
            # Left: Mobile Toggle & Quick Search Bar
            with ui.row().classes("items-center gap-2.5 no-wrap flex-1 max-w-xl"):
                if on_toggle_sidebar:
                    ui.button(icon="menu", on_click=on_toggle_sidebar).props(
                        "flat round dense color=slate-600"
                    ).classes("md:hidden hover:bg-slate-100")

                # Global Search Input
                with ui.element("div").classes(
                    "relative w-full max-w-md hidden sm:flex items-center"
                ):
                    search_input = (
                        ui.input(
                            placeholder=search_ph
                        )
                        .props("outlined dense")
                        .classes(
                            "w-full bg-slate-50/80 text-xs text-slate-700 rounded-lg border-slate-200"
                        )
                    )
                    search_input.add_slot(
                        "prepend",
                        '<i class="q-icon material-icons text-slate-400 text-base">search</i>',
                    )
                    search_input.add_slot(
                        "append",
                        '<span class="text-[10px] font-mono font-bold text-slate-400 bg-slate-200/60 px-1.5 py-0.5 rounded border border-slate-300/60">Ctrl K</span>',
                    )

            # Right: Notifications & Profile Dropdown
            with ui.row().classes("items-center gap-3 no-wrap shrink-0"):
                if role_raw == "TECHNICIAN":
                    with ui.element("div").classes(
                        "hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700 text-xs font-semibold cursor-pointer"
                    ):
                        ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500")
                        ui.label("Online").classes("text-[11px]")
                        ui.icon("arrow_drop_down", size="16px").classes("text-emerald-600")

                # Notification Bell with Red Badge
                with ui.button(icon="notifications_none").props("flat round dense").classes(
                    "text-slate-600 hover:bg-slate-100 relative"
                ):
                    with ui.element("span").classes(
                        "absolute top-0.5 right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-red-600 text-white text-[10px] font-extrabold flex items-center justify-center leading-none"
                    ):
                        ui.label("5" if role_raw == "TECHNICIAN" else "3")
                    ui.tooltip("Thông báo mới")

                # User Profile Capsule
                with ui.row().classes(
                    "items-center gap-2 cursor-pointer hover:bg-slate-50 px-2 py-1 rounded-lg transition-all"
                ):
                    # Avatar circle
                    with ui.avatar().props("size=30px").classes(
                        "bg-gradient-to-tr from-amber-400 to-rose-400 text-white font-bold shadow-sm"
                    ):
                        ui.icon("face").classes("text-base")

                    with ui.column().classes("gap-0 hidden md:flex"):
                        ui.label(ho_ten).classes("text-xs font-bold text-slate-900 leading-tight")
                        ui.label(role_label).classes("text-[10px] text-slate-500 leading-tight")

                    with ui.button(icon="keyboard_arrow_down").props("flat round dense").classes("text-slate-400 p-0"):
                        with ui.menu().classes("rounded-2xl shadow-xl border border-slate-100 p-1.5 min-w-[200px]"):
                            with ui.menu_item(on_click=lambda: ui.navigate.to("/dashboard")):
                                with ui.row().classes("items-center gap-2 text-xs font-semibold text-slate-700"):
                                    ui.icon("space_dashboard").classes("text-base text-blue-600")
                                    ui.label("Tổng quan")

                            ui.separator().classes("my-1")
                            ui.label("CHUYỂN VAI TRÒ (DEMO)").classes("px-3 py-1 text-[10px] font-bold text-slate-400 tracking-wider")

                            def switch_role(uname: str, target: str):
                                from core.auth_context import auth_context
                                from services.auth_service import DEMO_USERS
                                if uname in DEMO_USERS:
                                    auth_context.set_session(f"demo-token-{uname}", DEMO_USERS[uname])
                                    ui.navigate.to(target)

                            with ui.menu_item(on_click=lambda: switch_role("admin", "/admin/users")):
                                with ui.row().classes("items-center gap-2 text-xs font-semibold text-slate-700"):
                                    ui.icon("admin_panel_settings").classes("text-base text-purple-600")
                                    ui.label("Quản trị viên (Admin)")

                            with ui.menu_item(on_click=lambda: switch_role("tech01", "/technician/tasks")):
                                with ui.row().classes("items-center gap-2 text-xs font-semibold text-slate-700"):
                                    ui.icon("engineering").classes("text-base text-amber-600")
                                    ui.label("Kỹ thuật viên (Tech)")

                            with ui.menu_item(on_click=lambda: switch_role("user01", "/dashboard")):
                                with ui.row().classes("items-center gap-2 text-xs font-semibold text-slate-700"):
                                    ui.icon("person").classes("text-base text-blue-600")
                                    ui.label("Người dùng (User)")

                            ui.separator().classes("my-1")
                            with ui.menu_item(on_click=on_logout):
                                with ui.row().classes("items-center gap-2 text-xs font-semibold text-red-600"):
                                    ui.icon("logout").classes("text-base")
                                    ui.label("Đăng xuất")
