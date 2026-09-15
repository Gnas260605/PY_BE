from nicegui import ui

from common.components import toast
from common.styles.theme import apply_theme
from services.auth_service import auth_service


def render_login_view() -> None:
    apply_theme()

    if auth_service.is_authenticated():
        ui.navigate.to("/dashboard")
        return

    # Fullscreen fixed backdrop ensuring 100% horizontal & vertical centering
    with ui.element("div").classes("login-bg"):
        # Grid overlay pattern
        ui.element("div").classes("login-grid-pattern")

        # Glowing ambient orbs
        ui.element("div").classes(
            "absolute w-[450px] h-[450px] -top-24 -left-24 rounded-full bg-blue-600/25 blur-[120px] pointer-events-none animate-pulse"
        )
        ui.element("div").classes(
            "absolute w-[450px] h-[450px] -bottom-24 -right-24 rounded-full bg-indigo-600/25 blur-[120px] pointer-events-none"
        )
        ui.element("div").classes(
            "absolute w-[320px] h-[320px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/15 blur-[90px] pointer-events-none"
        )

        # Floating decorative status pills (desktop)
        with ui.element("div").classes(
            "hidden lg:flex absolute top-14 left-16 floating-chip items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-white shadow-xl pointer-events-none"
        ):
            ui.icon("verified_user").classes("text-emerald-400 text-lg")
            with ui.column().classes("gap-0"):
                ui.label("Hệ thống IT Sẵn sàng").classes("text-xs font-bold text-white leading-tight")
                ui.label("Cam kết SLA phản hồi 15p").classes("text-[10px] text-slate-300 leading-tight")

        with ui.element("div").classes(
            "hidden lg:flex absolute bottom-14 right-16 floating-chip-delayed items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-white shadow-xl pointer-events-none"
        ):
            ui.icon("lock").classes("text-blue-400 text-lg")
            with ui.column().classes("gap-0"):
                ui.label("Bảo mật phân quyền CS466").classes("text-xs font-bold text-white leading-tight")
                ui.label("JWT Authentication 8.0").classes("text-[10px] text-slate-300 leading-tight")

        # Centered Login Card
        with ui.card().classes(
            "w-full max-w-[410px] p-7 md:p-8 rounded-3xl login-card-glass relative z-20 flex flex-col items-center"
        ):
            # Glowing Brand Header
            with ui.element("div").classes(
                "w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-500 flex items-center justify-center shadow-xl shadow-blue-500/35 mb-2 ring-4 ring-blue-50/80"
            ):
                ui.icon("support_agent").classes("text-3xl text-white")

            ui.label("HelpDesk Pro").classes("text-2xl font-black text-slate-900 tracking-tight")

            with ui.row().classes("items-center gap-1.5 mt-0.5 mb-5"):
                ui.element("span").classes("w-2 h-2 rounded-full bg-emerald-500 animate-pulse")
                ui.label("Cổng hỗ trợ kỹ thuật CS466 trực tuyến").classes("text-xs font-semibold text-slate-500")

            # Form fields
            with ui.column().classes("w-full gap-3.5"):
                username = (
                    ui.input("Tên đăng nhập", value="user01")
                    .classes("w-full text-sm")
                    .props("outlined dense clearable")
                )
                username.add_slot("prepend", '<i class="q-icon material-icons text-slate-400 text-base">person</i>')

                password = (
                    ui.input("Mật khẩu", value="CS466@123", password=True, password_toggle_button=True)
                    .classes("w-full text-sm")
                    .props("outlined dense")
                )
                password.add_slot("prepend", '<i class="q-icon material-icons text-slate-400 text-base">lock</i>')

                role_hint = ui.label("Đang chọn: Người dùng (user01) - Phòng Kế toán").classes(
                    "text-[11px] text-blue-600 font-semibold text-center w-full"
                )

                async def submit() -> None:
                    if not username.value or not password.value:
                        toast.warning("Vui lòng nhập đủ tên đăng nhập và mật khẩu.")
                        return
                    try:
                        res = await auth_service.login(username.value, password.value)
                        toast.success("Đăng nhập thành công! Đang chuyển hướng...")
                        ui.navigate.to("/dashboard")
                    except Exception as exc:
                        toast.error(f"Lỗi đăng nhập: {exc}")

                ui.button("Đăng nhập hệ thống", on_click=submit).classes(
                    "w-full py-2.5 mt-1 text-white font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-600 hover:from-blue-700 hover:to-indigo-700 rounded-xl shadow-lg shadow-blue-500/25 text-sm transition-all"
                ).props("unelevated no-caps icon-right=arrow_forward")

            # Quick role chips
            with ui.column().classes("w-full mt-5 pt-4 border-t border-slate-200/80 gap-2 items-center"):
                ui.label("TÀI KHOẢN MẪU (CLICK ĐỂ ĐIỀN):").classes(
                    "text-[10px] font-bold text-slate-400 tracking-wider"
                )
                with ui.row().classes("w-full justify-center gap-2"):
                    # Admin button
                    def pick_admin():
                        username.set_value("admin")
                        password.set_value("CS466@123")
                        role_hint.set_text("Đang chọn: Quản trị viên (admin) - Toàn quyền")

                    ui.button("admin", on_click=pick_admin).props("dense outline color=purple").classes(
                        "text-xs px-2.5 py-0.5 rounded-lg font-bold"
                    )

                    # Tech button
                    def pick_tech():
                        username.set_value("tech01")
                        password.set_value("CS466@123")
                        role_hint.set_text("Đang chọn: Kỹ thuật viên (tech01) - Xử lý ticket")

                    ui.button("tech01", on_click=pick_tech).props("dense outline color=amber").classes(
                        "text-xs px-2.5 py-0.5 rounded-lg font-bold"
                    )

                    # User button
                    def pick_user():
                        username.set_value("user01")
                        password.set_value("CS466@123")
                        role_hint.set_text("Đang chọn: Người dùng (user01) - Phòng Kế toán")

                    ui.button("user01", on_click=pick_user).props("dense outline color=primary").classes(
                        "text-xs px-2.5 py-0.5 rounded-lg font-bold"
                    )

            # Footer note
            with ui.row().classes("w-full justify-center mt-3"):
                ui.label("Dự án CS466 · HelpDesk Management System").classes("text-[10px] text-slate-400")
