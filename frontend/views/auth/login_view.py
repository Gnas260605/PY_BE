from nicegui import ui

from common.components import toast
from common.styles.theme import apply_theme
from services.auth_service import auth_service


def render_login_view() -> None:
    apply_theme()

    if auth_service.is_authenticated():
        cur_u = auth_service.current_user()
        if cur_u and cur_u.get("vai_tro") == "USER":
            ui.navigate.to("/user/tickets")
        else:
            ui.navigate.to("/dashboard")
        return

    with ui.column().classes("w-screen h-screen items-center justify-center bg-slate-50 p-4"):
        with ui.card().classes("w-full max-w-md p-8 rounded-2xl bg-white border border-slate-200 shadow-sm"):
            # Header
            with ui.column().classes("w-full items-center gap-1.5 mb-6 text-center"):
                with ui.element("div").classes("w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm mb-1"):
                    ui.icon("support_agent").classes("text-2xl")
                ui.label("CS466 Helpdesk Portal").classes("text-xl font-bold text-slate-900")
                ui.label("Đăng nhập để quản lý và tạo yêu cầu hỗ trợ IT").classes("text-xs text-slate-500")

            # Inputs
            username = ui.input("Tên đăng nhập").classes("w-full").props("outlined clearable")
            password = ui.input("Mật khẩu", password=True, password_toggle_button=True).classes("w-full").props("outlined")

            async def submit() -> None:
                if not username.value or not password.value:
                    toast.warning("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                    return
                try:
                    await auth_service.login(username.value, password.value)
                    toast.success("Đăng nhập thành công.")
                    cur_u = auth_service.current_user()
                    if cur_u and cur_u.get("vai_tro") == "USER":
                        ui.navigate.to("/user/tickets")
                    else:
                        ui.navigate.to("/dashboard")
                except Exception as exc:
                    toast.error(str(exc))

            ui.button("Đăng nhập", on_click=submit).classes("w-full mt-2 py-2.5").props("color=primary unelevated")

            # Demo Accounts Helper
            with ui.column().classes("w-full mt-6 pt-4 border-t border-slate-100 items-center gap-2"):
                ui.label("TÀI KHOẢN TRẢI NGHIỆM DEMO:").classes("text-[10px] font-bold text-slate-400 tracking-wider")
                with ui.row().classes("w-full justify-center gap-1.5"):
                    for label, acc in (("Admin", "admin"), ("Kỹ thuật viên", "tech01"), ("Người dùng", "user01")):
                        ui.button(
                            label,
                            on_click=lambda acc=acc: (
                                username.set_value(acc),
                                password.set_value("CS466@123"),
                            ),
                        ).props("outline dense size=sm color=slate-700").classes("text-xs rounded-md")
