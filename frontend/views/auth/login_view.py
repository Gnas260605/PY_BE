from __future__ import annotations

import asyncio
from typing import Any
from nicegui import ui

from common.components import toast
from common.styles.theme import apply_theme
from core.constants import ERROR_MESSAGES
from services.auth_service import auth_service


def render_login_view() -> None:
    apply_theme()

    # If already logged in, redirect immediately to the right workspace
    if auth_service.is_authenticated():
        cur_u = auth_service.current_user()
        if cur_u and cur_u.get("vai_tro") == "USER":
            ui.navigate.to("/user/tickets")
        else:
            ui.navigate.to("/dashboard")
        return

    # View State: 'LOGIN' | 'REGISTER'
    state = {
        "mode": "LOGIN",
        "error_msg": "",
    }

    # Outer Layout Wrapper
    with ui.element("div").classes(
        "min-h-screen w-full bg-[#f8f9ff] text-[#0b1c30] flex flex-col justify-between selection:bg-blue-100 selection:text-blue-900"
    ):
        # =========================================================================
        # TOP HEADER
        # =========================================================================
        with ui.element("header").classes(
            "w-full py-4 px-4 sm:px-8 flex items-center justify-between z-10"
        ):
            with ui.row().classes("items-center gap-2.5"):
                with ui.element("div").classes(
                    "w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm"
                ):
                    ui.icon("dns", size="18px")
                with ui.element("span").classes("text-sm font-bold tracking-tight text-slate-900"):
                    ui.html('CS466<span class="text-blue-600">IT</span> Helpdesk')

            with ui.row().classes("items-center gap-3"):
                with ui.element("div").classes(
                    "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50/80 text-blue-700 text-[11px] font-medium border border-blue-100"
                ):
                    ui.element("span").classes("w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse")
                    ui.label("Enterprise Gateway Active")

                with ui.row().classes("items-center gap-1 text-slate-500 text-xs font-medium"):
                    ui.icon("verified_user", size="15px").classes("text-emerald-600")
                    ui.label("Hệ thống trực tuyến")

        # =========================================================================
        # MAIN AUTH CARD CONTAINER
        # =========================================================================
        with ui.element("main").classes(
            "flex-1 flex items-center justify-center p-3 sm:p-6 w-full max-w-5xl mx-auto"
        ):
            with ui.element("div").classes(
                "w-full max-w-[1000px] mx-auto bg-white rounded-2xl shadow-xl border border-slate-200/90 overflow-hidden grid grid-cols-1 lg:grid-cols-[40%_60%]"
            ):
                # -----------------------------------------------------------------
                # LEFT PANEL: Enterprise Brand & Infrastructure Trust
                # -----------------------------------------------------------------
                with ui.element("div").classes(
                    "relative bg-[#0f172a] text-white p-7 sm:p-9 flex flex-col justify-between overflow-hidden border-r border-slate-800"
                ):
                    # Ambient Depth Illumination (Subtle glows)
                    ui.html(
                        '<div class="absolute -top-24 -left-24 w-72 h-72 bg-blue-600/15 rounded-full blur-3xl pointer-events-none"></div>'
                        '<div class="absolute -bottom-24 -right-24 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>'
                    )

                    with ui.column().classes("relative z-10 gap-6 w-full"):
                        # Brand Header & Portal Title
                        with ui.row().classes("items-center gap-3"):
                            with ui.element("div").classes(
                                "w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md border border-blue-400/30"
                            ):
                                ui.icon("terminal", size="22px")
                            with ui.column().classes("gap-0"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label("CS466 Helpdesk").classes("text-base font-black tracking-tight text-white")
                                    with ui.element("span").classes(
                                        "inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 uppercase tracking-wider"
                                    ):
                                        ui.label("ITIL v4")
                                ui.label("IT SERVICE MANAGEMENT").classes(
                                    "text-[10px] font-bold tracking-widest uppercase text-blue-400"
                                )

                        # Headline & Description
                        with ui.column().classes("gap-2 pt-1"):
                            ui.label("Hệ thống Quản trị Sự cố & Dịch vụ CNTT").classes(
                                "text-xl sm:text-2xl font-black text-white leading-tight tracking-tight"
                            )
                            ui.label(
                                "Tiếp nhận, phân công và tự động hóa theo dõi yêu cầu hỗ trợ CNTT tập trung trong toàn doanh nghiệp."
                            ).classes("text-xs text-slate-300 leading-relaxed font-normal max-w-sm")

                        # Strategic Deliverables Checklist
                        with ui.column().classes("gap-3.5 pt-2 text-xs text-slate-300"):
                            deliverables = [
                                ("verified", "Tiếp nhận & điều phối sự cố", "Phân loại luồng ticket theo mức độ khẩn cấp (P1 - P4)."),
                                ("timer", "Theo dõi SLA & tiến độ xử lý", "Cập nhật trạng thái thời gian thực và thông báo đa kênh."),
                                ("security", "Quản lý thiết bị & phân quyền an toàn", "Bảo mật tài khoản RBAC, xác thực chuẩn Bcrypt."),
                            ]
                            for icon_name, title, desc in deliverables:
                                with ui.row().classes("items-start gap-2.5"):
                                    with ui.element("div").classes(
                                        "w-5 h-5 rounded-full bg-blue-500/20 text-blue-300 flex items-center justify-center shrink-0 mt-0.5"
                                    ):
                                        ui.icon(icon_name, size="13px")
                                    with ui.column().classes("gap-0"):
                                        ui.label(title).classes("font-bold text-white text-xs")
                                        ui.label(desc).classes("text-[11px] text-slate-400")

                    # Footer Security Stamp
                    with ui.row().classes(
                        "relative z-10 pt-5 mt-4 flex items-center justify-between gap-2 text-slate-400 text-[11px] border-t border-slate-800/80"
                    ):
                        with ui.row().classes("items-center gap-1.5 text-slate-300"):
                            ui.icon("lock", size="14px").classes("text-blue-400")
                            ui.label("Bảo mật SSL/TLS 256-bit")
                        with ui.element("span").classes(
                            "px-2 py-0.5 rounded bg-white/10 text-white text-[10px] font-bold tracking-wide"
                        ):
                            ui.label("v2.4.0-enterprise")

                # -----------------------------------------------------------------
                # RIGHT PANEL: Authentication Form & Interactive Controls
                # -----------------------------------------------------------------
                with ui.element("div").classes(
                    "p-6 sm:p-8 lg:p-9 flex flex-col justify-between bg-white"
                ):
                    with ui.column().classes("w-full gap-4"):
                        # Segmented Tab Bar (Login / Register)
                        with ui.element("div").classes(
                            "w-full flex p-1 rounded-xl bg-slate-100/90 border border-slate-200/80"
                        ):
                            def switch_to_login() -> None:
                                state["mode"] = "LOGIN"
                                state["error_msg"] = ""
                                render_form()

                            def switch_to_register() -> None:
                                state["mode"] = "REGISTER"
                                state["error_msg"] = ""
                                render_form()

                            btn_tab_login = (
                                ui.button("Đăng nhập", icon="login", on_click=switch_to_login)
                                .props("flat dense")
                                .classes("flex-1 py-1.5 rounded-lg text-xs font-bold transition-all")
                            )
                            btn_tab_register = (
                                ui.button("Đăng ký tài khoản", icon="person_add", on_click=switch_to_register)
                                .props("flat dense")
                                .classes("flex-1 py-1.5 rounded-lg text-xs font-bold transition-all")
                            )

                        # Dynamic Form Container
                        form_box = ui.column().classes("w-full gap-3.5")

                        def render_form() -> None:
                            form_box.clear()
                            is_login = state["mode"] == "LOGIN"

                            if is_login:
                                btn_tab_login.classes(
                                    "bg-white text-blue-700 shadow-xs border border-slate-200",
                                    remove="text-slate-600 hover:text-slate-900",
                                )
                                btn_tab_register.classes(
                                    "text-slate-600 hover:text-slate-900",
                                    remove="bg-white text-blue-700 shadow-xs border border-slate-200",
                                )
                            else:
                                btn_tab_register.classes(
                                    "bg-white text-blue-700 shadow-xs border border-slate-200",
                                    remove="text-slate-600 hover:text-slate-900",
                                )
                                btn_tab_login.classes(
                                    "text-slate-600 hover:text-slate-900",
                                    remove="bg-white text-blue-700 shadow-xs border border-slate-200",
                                )

                            with form_box:
                                # Header Titles
                                with ui.column().classes("gap-0.5"):
                                    ui.label("Đăng nhập hệ thống" if is_login else "Đăng ký tài khoản người dùng").classes(
                                        "text-xl sm:text-2xl font-black text-slate-900 tracking-tight"
                                    )
                                    ui.label(
                                        "Chào mừng trở lại. Vui lòng nhập thông tin xác thực để truy cập CS466 Helpdesk."
                                        if is_login
                                        else "Tạo tài khoản để gửi yêu cầu hỗ trợ và theo dõi tiến độ xử lý sự cố."
                                    ).classes("text-xs text-slate-500 font-medium")

                                # Inline Alert Banner (Vietnamese Human-Readable Error)
                                inline_alert = ui.element("div").classes(
                                    "w-full p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-start gap-2.5 text-xs font-semibold"
                                    if state["error_msg"]
                                    else "hidden"
                                )
                                with inline_alert:
                                    ui.icon("error", size="18px").classes("text-red-500 shrink-0 mt-0.5")
                                    ui.label(state["error_msg"]).classes("flex-1 leading-snug")

                                def show_error(msg: str) -> None:
                                    state["error_msg"] = msg
                                    inline_alert.clear()
                                    with inline_alert:
                                        ui.icon("error", size="18px").classes("text-red-500 shrink-0 mt-0.5")
                                        ui.label(msg).classes("flex-1 leading-snug")
                                    inline_alert.classes(
                                        "w-full p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-start gap-2.5 text-xs font-semibold",
                                        remove="hidden",
                                    )

                                if is_login:
                                    # =========================================
                                    # LOGIN INPUTS
                                    # =========================================
                                    with ui.column().classes("w-full gap-3"):
                                        # Username Field
                                        with ui.column().classes("w-full gap-1"):
                                            with ui.row().classes("w-full justify-between items-center"):
                                                ui.label("Tên đăng nhập *").classes("text-xs font-bold text-slate-700")
                                                ui.label("admin / tech01 / user01").classes("text-[11px] text-slate-400 font-mono")
                                            u_input = (
                                                ui.input(placeholder="Nhập tên đăng nhập")
                                                .props('outlined dense autocomplete="username"')
                                                .classes("w-full text-xs sm:text-sm bg-slate-50/50 rounded-lg")
                                            )

                                        # Password Field
                                        with ui.column().classes("w-full gap-1"):
                                            with ui.row().classes("w-full justify-between items-center"):
                                                ui.label("Mật khẩu *").classes("text-xs font-bold text-slate-700")
                                            p_input = (
                                                ui.input(placeholder="••••••••")
                                                .props('outlined dense type=password password-toggle autocomplete="current-password"')
                                                .classes("w-full text-xs sm:text-sm bg-slate-50/50 rounded-lg")
                                            )

                                        # Utility Row (Remember checkbox + 2FA info)
                                        with ui.row().classes("w-full items-center justify-between pt-0.5 text-xs text-slate-500"):
                                            with ui.row().classes("items-center gap-1.5"):
                                                ui.checkbox("Duy trì phiên đăng nhập", value=True).props("dense size=xs").classes("text-xs")
                                            with ui.row().classes("items-center gap-1 text-[11px] text-blue-600 font-medium"):
                                                ui.icon("lock", size="13px")
                                                ui.label("Bảo mật tài khoản")

                                        # Enter key handler
                                        async def on_enter_key(e: Any) -> None:
                                            if getattr(e, "key", "") == "Enter" or getattr(e, "args", {}).get("key") == "Enter":
                                                await handle_login_submit()

                                        u_input.on("keydown.enter", on_enter_key)
                                        p_input.on("keydown.enter", on_enter_key)

                                        # Login Action
                                        async def handle_login_submit() -> None:
                                            u = (u_input.value or "").strip()
                                            p = (p_input.value or "").strip()

                                            if not u or not p:
                                                show_error("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
                                                return

                                            btn_submit.props("loading")
                                            btn_submit.disable()
                                            state["error_msg"] = ""
                                            inline_alert.classes("hidden", remove="flex")

                                            try:
                                                await auth_service.login(u, p)
                                                cur_u = auth_service.current_user() or {}
                                                u_name = cur_u.get("ho_ten") or u
                                                toast.success(f"Đăng nhập thành công! Chào mừng {u_name}.")
                                                await asyncio.sleep(0.3)
                                                if cur_u.get("vai_tro") == "USER":
                                                    ui.navigate.to("/user/tickets")
                                                else:
                                                    ui.navigate.to("/dashboard")
                                            except Exception as exc:
                                                err = str(exc)
                                                if "Lỗi không xác định: " in err:
                                                    err = err.replace("Lỗi không xác định: ", "")
                                                show_error(err)
                                            finally:
                                                btn_submit.props(remove="loading")
                                                btn_submit.enable()

                                        # Submit Button
                                        btn_submit = (
                                            ui.button(
                                                "Đăng nhập",
                                                icon="arrow_forward",
                                                on_click=handle_login_submit,
                                            )
                                            .props("color=primary unelevated")
                                            .classes(
                                                "w-full h-11 text-xs sm:text-sm font-bold rounded-lg shadow-sm mt-1 bg-blue-600 hover:bg-blue-700 text-white"
                                            )
                                        )

                                    # 1-Click Demo Quick Switcher Cards (Clean, spacious, zero text overlap)
                                    with ui.element("div").classes(
                                        "w-full p-3 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col gap-2 mt-2"
                                    ):
                                        with ui.row().classes("w-full justify-between items-center no-wrap"):
                                            ui.label("TÀI KHOẢN TRẢI NGHIỆM DEMO (1-CLICK):").classes(
                                                "text-[10px] font-bold text-slate-400 tracking-wider"
                                            )
                                            with ui.element("span").classes(
                                                "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-200/80 text-slate-600"
                                            ):
                                                ui.label("Sandbox")

                                        with ui.element("div").classes("grid grid-cols-3 gap-2.5 w-full"):
                                            demo_configs = [
                                                ("Admin", "admin", "Admin@123", "Quản trị", "admin_panel_settings", "text-purple-600", "hover:border-purple-300 hover:bg-purple-50/50"),
                                                ("Tech", "tech01", "CS466@123", "Kỹ thuật", "build", "text-blue-600", "hover:border-blue-300 hover:bg-blue-50/50"),
                                                ("User", "user01", "CS466@123", "Người dùng", "person", "text-emerald-600", "hover:border-emerald-300 hover:bg-emerald-50/50"),
                                            ]
                                            for role_name, username, pwd, role_desc, icon_n, icon_c, hover_s in demo_configs:
                                                def make_demo_handler(u=username, p=pwd, r=role_name):
                                                    return lambda: (
                                                        u_input.set_value(u),
                                                        p_input.set_value(p),
                                                        state.update({"error_msg": ""}),
                                                        inline_alert.classes("hidden", remove="flex"),
                                                        toast.info(f"Đã chọn hồ sơ demo {r}: {u}")
                                                    )

                                                with ui.element("button").classes(
                                                    f"w-full py-2.5 px-1 rounded-xl bg-white border border-slate-200 {hover_s} transition-all flex flex-col items-center justify-center gap-1 shadow-2xs cursor-pointer select-none"
                                                ).on("click", make_demo_handler()):
                                                    with ui.row().classes("items-center justify-center gap-1.5 no-wrap leading-none"):
                                                        ui.icon(icon_n, size="16px").classes(f"{icon_c} shrink-0")
                                                        ui.label(role_name).classes("font-bold text-xs text-slate-800 leading-none")
                                                    ui.label(role_desc).classes("text-[10px] text-slate-400 font-medium leading-none")

                                else:
                                    # =========================================
                                    # REGISTER INPUTS
                                    # =========================================
                                    with ui.column().classes("w-full gap-2.5"):
                                        with ui.element("div").classes("grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full"):
                                            # Full Name
                                            with ui.column().classes("w-full gap-1"):
                                                ui.label("Họ và tên đầy đủ *").classes("text-xs font-bold text-slate-700")
                                                reg_name = (
                                                    ui.input(placeholder="Nguyễn Văn A")
                                                    .props("outlined dense")
                                                    .classes("w-full text-xs sm:text-sm bg-slate-50/50 rounded-lg")
                                                )

                                            # Username
                                            with ui.column().classes("w-full gap-1"):
                                                ui.label("Tên đăng nhập *").classes("text-xs font-bold text-slate-700")
                                                reg_user = (
                                                    ui.input(placeholder="nguyenvana")
                                                    .props("outlined dense")
                                                    .classes("w-full text-xs sm:text-sm bg-slate-50/50 rounded-lg")
                                                )

                                        # Email (Optional)
                                        with ui.column().classes("w-full gap-1"):
                                            ui.label("Địa chỉ Email liên hệ").classes("text-xs font-bold text-slate-700")
                                            reg_email = (
                                                ui.input(placeholder="nguyenvana@company.com")
                                                .props("outlined dense")
                                                .classes("w-full text-xs sm:text-sm bg-slate-50/50 rounded-lg")
                                            )

                                        # Password & Strength Meter
                                        with ui.column().classes("w-full gap-1"):
                                            ui.label("Mật khẩu * (Tối thiểu 8 ký tự)").classes("text-xs font-bold text-slate-700")
                                            reg_pwd = (
                                                ui.input(placeholder="••••••••")
                                                .props("outlined dense type=password password-toggle")
                                                .classes("w-full text-xs sm:text-sm bg-slate-50/50 rounded-lg")
                                            )

                                        # Password Strength Meter
                                        pwd_meter = ui.linear_progress(value=0, color="red").props("size=3px rounded").classes("w-full")
                                        pwd_label = ui.label("Độ mạnh: Chưa nhập").classes("text-[10px] text-slate-400 font-medium")

                                        def update_meter(e: Any) -> None:
                                            v = getattr(e, "value", "") or ""
                                            val_len = len(v)
                                            if val_len == 0:
                                                pwd_meter.value = 0
                                                pwd_meter.props("color=red")
                                                pwd_label.text = "Độ mạnh: Chưa nhập"
                                                pwd_label.classes("text-[10px] text-slate-400", remove="text-red-600 text-amber-600 text-emerald-600 font-bold")
                                            elif val_len < 8:
                                                pwd_meter.value = 0.33
                                                pwd_meter.props("color=red")
                                                pwd_label.text = "Độ mạnh: Yếu (Cần tối thiểu 8 ký tự)"
                                                pwd_label.classes("text-[10px] text-red-600 font-bold", remove="text-slate-400 text-amber-600 text-emerald-600")
                                            elif val_len < 12 or v.isdigit() or v.isalpha():
                                                pwd_meter.value = 0.66
                                                pwd_meter.props("color=amber")
                                                pwd_label.text = "Độ mạnh: Trung bình"
                                                pwd_label.classes("text-[10px] text-amber-600 font-bold", remove="text-slate-400 text-red-600 text-emerald-600")
                                            else:
                                                pwd_meter.value = 1.0
                                                pwd_meter.props("color=emerald")
                                                pwd_label.text = "Độ mạnh: Rất tốt"
                                                pwd_label.classes("text-[10px] text-emerald-600 font-bold", remove="text-slate-400 text-red-600 text-amber-600")

                                        reg_pwd.on_value_change(update_meter)

                                        # Confirm Password
                                        with ui.column().classes("w-full gap-1"):
                                            ui.label("Xác nhận mật khẩu *").classes("text-xs font-bold text-slate-700")
                                            reg_cf_pwd = (
                                                ui.input(placeholder="••••••••")
                                                .props("outlined dense type=password password-toggle")
                                                .classes("w-full text-xs sm:text-sm bg-slate-50/50 rounded-lg")
                                            )

                                        # Register Submit Handler
                                        async def handle_register_submit() -> None:
                                            n = (reg_name.value or "").strip()
                                            u = (reg_user.value or "").strip()
                                            em = (reg_email.value or "").strip()
                                            p = (reg_pwd.value or "").strip()
                                            cf = (reg_cf_pwd.value or "").strip()

                                            if not n or not u or not p:
                                                show_error("Vui lòng nhập đầy đủ Họ tên, Tên đăng nhập và Mật khẩu.")
                                                return
                                            if len(p) < 8:
                                                show_error("Mật khẩu phải có tối thiểu 8 ký tự.")
                                                return
                                            if p != cf:
                                                show_error("Mật khẩu xác nhận không khớp.")
                                                return

                                            btn_reg.props("loading")
                                            btn_reg.disable()
                                            state["error_msg"] = ""
                                            inline_alert.classes("hidden", remove="flex")

                                            try:
                                                await auth_service.register(
                                                    username=u,
                                                    password=p,
                                                    ho_ten=n,
                                                    email=em or None,
                                                )
                                                toast.success(f"Đăng ký thành công! Chào mừng {n}.")
                                                await asyncio.sleep(0.3)
                                                ui.navigate.to("/user/tickets")
                                            except Exception as exc:
                                                err = str(exc)
                                                if "Lỗi không xác định: " in err:
                                                    err = err.replace("Lỗi không xác định: ", "")
                                                show_error(err)
                                            finally:
                                                btn_reg.props(remove="loading")
                                                btn_reg.enable()

                                        # Register Submit Button
                                        btn_reg = (
                                            ui.button(
                                                "Tạo tài khoản & Đăng nhập ngay",
                                                icon="how_to_reg",
                                                on_click=handle_register_submit,
                                            )
                                            .props("color=primary unelevated")
                                            .classes(
                                                "w-full h-11 text-xs sm:text-sm font-bold rounded-lg shadow-sm mt-1 bg-blue-600 hover:bg-blue-700 text-white"
                                            )
                                        )

                                # Footer Mode Switch Prompt
                                with ui.row().classes("w-full justify-center items-center gap-1.5 pt-1 text-xs text-slate-500"):
                                    if is_login:
                                        ui.label("Chưa có tài khoản CS466 Helpdesk?")
                                        ui.button("Đăng ký tài khoản ngay", on_click=switch_to_register).props("flat dense").classes(
                                            "text-xs font-bold text-blue-600 hover:underline p-0 min-h-0"
                                        )
                                    else:
                                        ui.label("Đã có tài khoản hệ thống?")
                                        ui.button("Đăng nhập tại đây", on_click=switch_to_login).props("flat dense").classes(
                                            "text-xs font-bold text-blue-600 hover:underline p-0 min-h-0"
                                        )

                        render_form()

        # =========================================================================
        # PAGE FOOTER
        # =========================================================================
        with ui.element("footer").classes(
            "w-full py-4 px-4 sm:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-slate-400 text-xs z-10 border-t border-slate-200/60"
        ):
            ui.label("© 2025 CS466 Enterprise IT Infrastructure Services. All rights reserved.")
            with ui.row().classes("items-center gap-4 text-slate-500"):
                ui.label("Bảo mật & Tuân thủ")
                ui.label("Hỗ trợ khẩn cấp")
                with ui.row().classes("items-center gap-1 text-slate-400"):
                    ui.icon("lock", size="13px")
                    ui.label("SOC2 Type II")
