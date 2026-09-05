from nicegui import ui

from common.components import toast
from common.styles.theme import apply_theme
from services.auth_service import auth_service


def render_login_view() -> None:
    apply_theme()

    if auth_service.is_authenticated():
        ui.navigate.to("/dashboard")
        return

    with ui.element("div").classes("min-h-screen flex items-center justify-center px-4"):
        with ui.card().classes("glass-card w-full max-w-md p-8 rounded-3xl shadow-xl border border-slate-100"):
            with ui.column().classes("w-full items-center gap-2 mb-4"):
                ui.icon("support_agent").classes("text-5xl text-blue-600")
                ui.label("HelpDesk Pro").classes("text-2xl font-bold text-slate-900")
                ui.label("Đăng nhập hệ thống CS466").classes("text-sm text-slate-500")

            username = ui.input("Tên đăng nhập").classes("w-full").props("outlined clearable")
            password = ui.input("Mật khẩu", password=True, password_toggle_button=True).classes("w-full").props("outlined")

            async def submit() -> None:
                if not username.value or not password.value:
                    toast.warning("Vui lòng nhập đủ tên đăng nhập và mật khẩu.")
                    return
                try:
                    await auth_service.login(username.value, password.value)
                    toast.success("Đăng nhập thành công.")
                    ui.navigate.to("/dashboard")
                except Exception as exc:
                    toast.error(str(exc))

            ui.button("Đăng nhập", on_click=submit).classes("w-full mt-2").props("color=primary unelevated")

            with ui.row().classes("w-full justify-center gap-2 mt-4"):
                for account in ("admin", "tech01", "user01"):
                    ui.button(
                        account,
                        on_click=lambda account=account: (
                            username.set_value(account),
                            password.set_value("CS466@123"),
                        ),
                    ).props("flat dense color=primary")
