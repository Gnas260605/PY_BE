from __future__ import annotations

import asyncio
from typing import Any
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

    # View Mode: 'LOGIN' | 'REGISTER'
    auth_state: dict[str, Any] = {
        "mode": "LOGIN",
    }

    with ui.column().classes("w-screen min-h-screen items-center justify-center bg-slate-100/70 p-4 sm:p-6"):
        with ui.card().classes(
            "w-full max-w-4xl p-0 rounded-3xl bg-white border border-slate-200 shadow-xl overflow-hidden flex flex-col md:flex-row"
        ):
            # Left Hero Panel (Enterprise SaaS Branding & Trust Elements)
            with ui.column().classes(
                "w-full md:w-[42%] bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white p-8 sm:p-10 justify-between gap-8 flex-shrink-0"
            ):
                with ui.column().classes("gap-4"):
                    with ui.row().classes("items-center gap-3"):
                        with ui.element("div").classes(
                            "w-11 h-11 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md border border-blue-500"
                        ):
                            ui.icon("support_agent", size="24px")
                        with ui.column().classes("gap-0"):
                            ui.label("CS466 Helpdesk").classes("text-lg font-black tracking-tight text-white")
                            ui.label("IT Service Portal").classes("text-xs text-blue-300 font-semibold tracking-wider uppercase")

                    ui.label("Hệ thống Quản lý Sự cố & Dịch vụ CNTT").classes("text-2xl font-black tracking-tight leading-tight text-white mt-2")
                    ui.label(
                        "Giải pháp toàn diện tiếp nhận yêu cầu, phân công kỹ thuật viên, giám sát SLA và quản lý tài sản thiết bị doanh nghiệp."
                    ).classes("text-sm text-slate-300 leading-relaxed font-normal")

                # Highlights List
                with ui.column().classes("gap-3 pt-4 border-t border-slate-800/80 text-xs text-slate-200 font-medium"):
                    with ui.row().classes("items-center gap-2.5"):
                        ui.icon("check_circle", size="18px").classes("text-blue-400")
                        ui.label("Tiếp nhận & điều phối sự cố thời gian thực")

                    with ui.row().classes("items-center gap-2.5"):
                        ui.icon("check_circle", size="18px").classes("text-blue-400")
                        ui.label("Giám sát chỉ số SLA và cảnh báo khẩn cấp")

                    with ui.row().classes("items-center gap-2.5"):
                        ui.icon("check_circle", size="18px").classes("text-blue-400")
                        ui.label("Bảo mật tài khoản đa tầng chuẩn Bcrypt")

                # Footer Note
                with ui.row().classes("items-center gap-2 text-xs text-slate-400 pt-4"):
                    ui.icon("lock", size="14px")
                    ui.label("Kết nối an toàn chuẩn Enterprise")

            # Right Interactive Form Panel
            with ui.column().classes("w-full md:w-[58%] p-8 sm:p-10 gap-6 justify-center"):
                # Top Segmented Mode Switcher
                with ui.row().classes("w-full p-1 bg-slate-100 rounded-xl border border-slate-200"):
                    def switch_to_login():
                        auth_state["mode"] = "LOGIN"
                        render_form()

                    def switch_to_register():
                        auth_state["mode"] = "REGISTER"
                        render_form()

                    btn_tab_login = ui.button("Đăng nhập tài khoản", on_click=switch_to_login).props("flat dense").classes(
                        "flex-1 py-2 text-sm font-bold rounded-lg transition-all"
                    )
                    btn_tab_register = ui.button("Đăng ký người dùng", on_click=switch_to_register).props("flat dense").classes(
                        "flex-1 py-2 text-sm font-bold rounded-lg transition-all"
                    )

                form_container = ui.column().classes("w-full gap-4")

                def render_form() -> None:
                    form_container.clear()
                    mode = auth_state["mode"]

                    if mode == "LOGIN":
                        btn_tab_login.classes("bg-white text-blue-700 shadow-xs border border-slate-200", remove="text-slate-600")
                        btn_tab_register.classes("text-slate-600 hover:text-slate-900", remove="bg-white text-blue-700 shadow-xs border")

                        with form_container:
                            with ui.column().classes("gap-1 mb-1"):
                                ui.label("Chào mừng trở lại").classes("text-2xl font-black text-slate-900 tracking-tight")
                                ui.label("Nhập tên đăng nhập và mật khẩu để truy cập hệ thống.").classes("text-sm text-slate-500 font-medium")

                            # Login Fields
                            with ui.column().classes("w-full gap-1"):
                                ui.label("Tên đăng nhập *").classes("text-sm font-bold text-slate-700")
                                username_input = ui.input(placeholder="admin / tech01 / user01").props("outlined").classes("w-full text-sm bg-white")

                            with ui.column().classes("w-full gap-1"):
                                ui.label("Mật khẩu *").classes("text-sm font-bold text-slate-700")
                                password_input = ui.input(placeholder="••••••••").props("outlined type=password password-toggle").classes("w-full text-sm bg-white")

                            async def handle_login() -> None:
                                u_val = (username_input.value or "").strip()
                                p_val = (password_input.value or "").strip()

                                if not u_val or not p_val:
                                    toast.warning("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                                    return

                                submit_btn.props("loading")
                                try:
                                    await auth_service.login(u_val, p_val)
                                    cur_u = auth_service.current_user() or {}
                                    u_name = cur_u.get("ho_ten") or u_val
                                    toast.success(f"Đăng nhập thành công! Chào mừng {u_name}.")
                                    await asyncio.sleep(0.4)
                                    if cur_u.get("vai_tro") == "USER":
                                        ui.navigate.to("/user/tickets")
                                    else:
                                        ui.navigate.to("/dashboard")
                                except Exception as exc:
                                    toast.error(f"Đăng nhập thất bại: {exc}")
                                finally:
                                    submit_btn.props(remove="loading")

                            submit_btn = ui.button(
                                "Đăng nhập hệ thống",
                                icon="login",
                                on_click=handle_login,
                            ).props("color=primary unelevated size=md").classes("w-full h-12 text-sm font-bold rounded-xl shadow-sm mt-2")

                            # Demo Accounts Quick Fill
                            with ui.column().classes("w-full mt-4 pt-4 border-t border-slate-100 gap-2"):
                                ui.label("TÀI KHOẢN TRẢI NGHIỆM DEMO (1-CLICK FILL):").classes("text-[11px] font-bold text-slate-400 tracking-wider")
                                with ui.row().classes("w-full gap-2 flex-wrap"):
                                    DEMO_ACCOUNTS = [
                                        ("Quản trị (Admin)", "admin", "bg-purple-50 text-purple-700 border-purple-200"),
                                        ("Kỹ thuật viên (Tech)", "tech01", "bg-blue-50 text-blue-700 border-blue-200"),
                                        ("Người dùng (User)", "user01", "bg-emerald-50 text-emerald-700 border-emerald-200"),
                                    ]
                                    for lbl, acc, badge_c in DEMO_ACCOUNTS:
                                        def make_fill(a=acc):
                                            return lambda: (
                                                username_input.set_value(a),
                                                password_input.set_value("Admin@123" if a == "admin" else "CS466@123"),
                                                toast.info(f"Đã điền tài khoản mẫu: {a}")
                                            )

                                        ui.button(lbl, on_click=make_fill()).props("outline dense size=sm color=slate-700").classes(
                                            f"text-xs font-semibold px-3 py-1.5 rounded-lg border {badge_c} hover:bg-slate-100 transition-colors"
                                        )

                    else:
                        # REGISTER MODE
                        btn_tab_register.classes("bg-white text-blue-700 shadow-xs border border-slate-200", remove="text-slate-600")
                        btn_tab_login.classes("text-slate-600 hover:text-slate-900", remove="bg-white text-blue-700 shadow-xs border")

                        with form_container:
                            with ui.column().classes("gap-1 mb-1"):
                                ui.label("Tạo tài khoản người dùng").classes("text-2xl font-black text-slate-900 tracking-tight")
                                ui.label("Đăng ký tài khoản để gửi yêu cầu và theo dõi tiến độ xử lý sự cố.").classes("text-sm text-slate-500 font-medium")

                            with ui.element("div").classes("w-full grid grid-cols-1 sm:grid-cols-2 gap-3"):
                                # Họ và tên
                                with ui.column().classes("w-full gap-1"):
                                    ui.label("Họ và tên đầy đủ *").classes("text-xs font-bold text-slate-700")
                                    reg_name = ui.input(placeholder="Nguyễn Văn A").props("outlined dense").classes("w-full text-sm bg-white")

                                # Tên đăng nhập
                                with ui.column().classes("w-full gap-1"):
                                    ui.label("Tên đăng nhập *").classes("text-xs font-bold text-slate-700")
                                    reg_user = ui.input(placeholder="nguyenvana").props("outlined dense").classes("w-full text-sm bg-white")

                            # Email
                            with ui.column().classes("w-full gap-1"):
                                ui.label("Địa chỉ Email liên hệ").classes("text-xs font-bold text-slate-700")
                                reg_email = ui.input(placeholder="nguyenvana@company.com").props("outlined dense").classes("w-full text-sm bg-white")

                            # Mật khẩu
                            with ui.column().classes("w-full gap-1"):
                                ui.label("Mật khẩu * (Tối thiểu 8 ký tự)").classes("text-xs font-bold text-slate-700")
                                reg_pwd = ui.input(placeholder="••••••••").props("outlined dense type=password password-toggle").classes("w-full text-sm bg-white")

                            # Strength Indicator
                            strength_bar = ui.linear_progress(value=0, color="red").props("size=4px rounded").classes("w-full rounded-full bg-slate-100")
                            strength_lbl = ui.label("Độ mạnh: Chưa nhập").classes("text-[11px] text-slate-400 font-medium")

                            def on_pwd_change(e):
                                val = e.value or ""
                                l = len(val)
                                if l == 0:
                                    strength_bar.value = 0
                                    strength_bar.props("color=red")
                                    strength_lbl.text = "Độ mạnh: Chưa nhập"
                                    strength_lbl.classes("text-[11px] text-slate-400", remove="text-red-600 text-amber-600 text-emerald-600 font-bold")
                                elif l < 8:
                                    strength_bar.value = 0.33
                                    strength_bar.props("color=red")
                                    strength_lbl.text = "Độ mạnh: Yếu (Cần tối thiểu 8 ký tự)"
                                    strength_lbl.classes("text-[11px] text-red-600 font-bold", remove="text-slate-400 text-amber-600 text-emerald-600")
                                elif l < 12 or val.isdigit() or val.isalpha():
                                    strength_bar.value = 0.66
                                    strength_bar.props("color=amber")
                                    strength_lbl.text = "Độ mạnh: Trung bình"
                                    strength_lbl.classes("text-[11px] text-amber-600 font-bold", remove="text-slate-400 text-red-600 text-emerald-600")
                                else:
                                    strength_bar.value = 1.0
                                    strength_bar.props("color=emerald")
                                    strength_lbl.text = "Độ mạnh: Rất mạnh"
                                    strength_lbl.classes("text-[11px] text-emerald-600 font-bold", remove="text-slate-400 text-red-600 text-amber-600")

                            reg_pwd.on_value_change(on_pwd_change)

                            # Xác nhận mật khẩu
                            with ui.column().classes("w-full gap-1"):
                                ui.label("Xác nhận mật khẩu *").classes("text-xs font-bold text-slate-700")
                                reg_pwd_confirm = ui.input(placeholder="••••••••").props("outlined dense type=password password-toggle").classes("w-full text-sm bg-white")

                            async def handle_register() -> None:
                                name_val = (reg_name.value or "").strip()
                                user_val = (reg_user.value or "").strip()
                                email_val = (reg_email.value or "").strip()
                                pwd_val = (reg_pwd.value or "").strip()
                                cf_val = (reg_pwd_confirm.value or "").strip()

                                if not name_val or not user_val or not pwd_val:
                                    toast.warning("Vui lòng nhập đầy đủ Họ tên, Tên đăng nhập và Mật khẩu.")
                                    return
                                if len(pwd_val) < 8:
                                    toast.warning("Mật khẩu phải có tối thiểu 8 ký tự.")
                                    return
                                if pwd_val != cf_val:
                                    toast.warning("Mật khẩu xác nhận không khớp.")
                                    return

                                reg_btn.props("loading")
                                try:
                                    await auth_service.register(
                                        username=user_val,
                                        password=pwd_val,
                                        ho_ten=name_val,
                                        email=email_val or None,
                                    )
                                    toast.success(f"Đăng ký tài khoản thành công! Chào mừng {name_val}.")
                                    await asyncio.sleep(0.5)
                                    ui.navigate.to("/user/tickets")
                                except Exception as exc:
                                    toast.error(f"Đăng ký thất bại: {exc}")
                                finally:
                                    reg_btn.props(remove="loading")

                            reg_btn = ui.button(
                                "Tạo tài khoản & Đăng nhập ngay",
                                icon="person_add",
                                on_click=handle_register,
                            ).props("color=primary unelevated size=md").classes("w-full h-11 text-sm font-bold rounded-xl shadow-sm mt-1")

                render_form()
