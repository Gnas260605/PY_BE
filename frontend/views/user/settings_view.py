from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from common.components.status_badge import role_badge
from core.i18n import get_lang, set_lang, t
from services.auth_service import auth_service
from services.user_service import user_service


def render_settings_view() -> None:
    def content(user: dict) -> None:
        user_id = user.get("id")
        user_name = user.get("ho_ten") or user.get("username", "Người dùng")
        username = user.get("username", "")
        role = user.get("vai_tro", "USER")
        email = user.get("email", "")
        phone = user.get("so_dien_thoai", "")

        # Page Header Banner
        with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-200 mb-6 flex-wrap gap-2"):
            with ui.column().classes("gap-0.5"):
                with ui.row().classes("items-center gap-1.5 text-xs text-slate-400 font-medium"):
                    ui.label(t("settings_breadcrumb_home"))
                    ui.label("/").classes("text-slate-300")
                    ui.label(t("settings_breadcrumb_current")).classes("text-slate-700 font-semibold")

                ui.label(t("settings_title")).classes("text-2xl font-bold text-slate-900 tracking-tight")
                ui.label(t("settings_sub")).classes("text-xs text-slate-500")

        # Main 2-Column Grid Layout
        with ui.element("div").classes("w-full grid grid-cols-1 lg:grid-cols-12 gap-6 items-start"):
            
            # Left Column (7/12): Preferences & Language & Security
            with ui.column().classes("lg:col-span-7 w-full gap-5"):
                
                # Card 1: Ngôn ngữ & Giao diện hiển thị
                with ui.card().classes("w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xs gap-4"):
                    with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                        with ui.element("div").classes("w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600"):
                            ui.icon("translate").classes("text-base")
                        with ui.column().classes("gap-0"):
                            ui.label(t("settings_card_lang_title")).classes("text-sm font-bold text-slate-900")
                            ui.label(t("settings_card_lang_sub")).classes("text-[11px] text-slate-500")

                    with ui.column().classes("w-full gap-3 pt-1"):
                        ui.label(t("settings_lang_label")).classes("text-xs font-semibold text-slate-700")
                        
                        lang_select = ui.select(
                            options={
                                "vi": "🇻🇳 Tiếng Việt (Vietnamese - Mặc định)",
                                "en": "🇺🇸 English (US)",
                            },
                            value=get_lang(),
                        ).props("outlined dense").classes("w-full text-xs")

                        ui.label(t("settings_theme_label")).classes("text-xs font-semibold text-slate-700 mt-2")
                        theme_select = ui.select(
                            options={
                                "light": t("settings_theme_light"),
                                "auto": t("settings_theme_auto"),
                            },
                            value="light",
                        ).props("outlined dense").classes("w-full text-xs")

                        ui.label(t("settings_density_label")).classes("text-xs font-semibold text-slate-700 mt-2")
                        density_select = ui.select(
                            options={
                                "compact": t("settings_density_compact"),
                                "comfortable": t("settings_density_comfortable"),
                            },
                            value="compact",
                        ).props("outlined dense").classes("w-full text-xs")

                        def save_preferences() -> None:
                            selected_lang = lang_select.value or "vi"
                            set_lang(selected_lang)
                            msg = "Language updated to English!" if selected_lang == "en" else "Đã cập nhật ngôn ngữ sang Tiếng Việt!"
                            toast.success(msg)
                            ui.navigate.to("/settings")

                        with ui.row().classes("w-full justify-end pt-3 border-t border-slate-100 mt-2"):
                            ui.button(t("settings_btn_save_pref"), icon="check", on_click=save_preferences).props("unelevated color=primary size=sm").classes("px-4 py-2 font-bold rounded-lg text-xs shadow-2xs")

                # Card 2: Tùy chọn Thông báo (Notifications)
                with ui.card().classes("w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xs gap-4"):
                    with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                        with ui.element("div").classes("w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700"):
                            ui.icon("notifications").classes("text-base")
                        with ui.column().classes("gap-0"):
                            ui.label(t("settings_card_notify_title")).classes("text-sm font-bold text-slate-900")
                            ui.label(t("settings_card_notify_sub")).classes("text-[11px] text-slate-500")

                    with ui.column().classes("w-full gap-2.5 pt-1"):
                        notify_popup = ui.checkbox(t("settings_notify_toast"), value=True).classes("text-xs font-medium text-slate-700")
                        notify_urgent = ui.checkbox(t("settings_notify_urgent"), value=True).classes("text-xs font-medium text-slate-700")
                        notify_email = ui.checkbox(t("settings_notify_email"), value=user.get("receive_email_on_resolve", False)).classes("text-xs font-medium text-slate-700")

                        async def save_notifications() -> None:
                            try:
                                if user_id:
                                    await user_service.update_user(
                                        user_id,
                                        {"receive_email_on_resolve": notify_email.value}
                                    )
                                toast.success("Đã cập nhật tùy chọn thông báo.")
                            except Exception as exc:
                                toast.error(f"Lỗi cập nhật: {exc}")

                        with ui.row().classes("w-full justify-end pt-3 border-t border-slate-100 mt-2"):
                            ui.button(t("settings_btn_update_notify"), on_click=save_notifications).props("outline color=slate-700 size=sm").classes("px-3.5 py-1.5 font-medium rounded-lg text-xs bg-white border-slate-300 shadow-2xs")

            # Right Column (5/12): Profile Info & Security
            with ui.column().classes("lg:col-span-5 w-full gap-5"):
                
                # Card 3: Hồ sơ tài khoản cá nhân
                with ui.card().classes("w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xs gap-4"):
                    with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                        with ui.element("div").classes("w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600"):
                            ui.icon("account_circle").classes("text-base")
                        with ui.column().classes("gap-0"):
                            ui.label(t("settings_card_profile_title")).classes("text-sm font-bold text-slate-900")
                            ui.label(t("settings_card_profile_sub")).classes("text-[11px] text-slate-500")

                    with ui.column().classes("w-full items-center py-2 gap-2 text-center"):
                        initials = (user_name or "U")[:2].upper()
                        with ui.avatar(color="primary", text_color="white").props("size=56px font-size=20px").classes("font-bold shadow-md shadow-blue-500/10"):
                            ui.label(initials)
                        with ui.column().classes("gap-0.5 items-center"):
                            ui.label(user_name).classes("text-base font-bold text-slate-900")
                            ui.label(f"@{username} · ID #{user_id}").classes("text-xs text-slate-400 font-mono")
                            with ui.row().classes("mt-1"):
                                role_badge(role)

                    with ui.column().classes("w-full gap-3 pt-2"):
                        name_input = ui.input(t("settings_field_fullname"), value=user_name).props("outlined dense").classes("w-full text-xs")
                        email_input = ui.input(t("settings_field_email"), value=email).props("outlined dense").classes("w-full text-xs")
                        phone_input = ui.input(t("settings_field_phone"), value=phone).props("outlined dense").classes("w-full text-xs")

                        async def handle_update_profile() -> None:
                            new_name = (name_input.value or "").strip()
                            new_email = (email_input.value or "").strip()
                            new_phone = (phone_input.value or "").strip()
                            if not new_name:
                                toast.warning("Vui lòng nhập Họ và tên.")
                                return

                            try:
                                if user_id:
                                    await user_service.update_user(
                                        user_id,
                                        {
                                            "ho_ten": new_name,
                                            "email": new_email or None,
                                            "so_dien_thoai": new_phone or None,
                                        },
                                    )
                                toast.success("Đã cập nhật thông tin cá nhân thành công!")
                            except Exception as exc:
                                toast.error(f"Lỗi cập nhật: {exc}")

                        with ui.row().classes("w-full justify-end pt-3 border-t border-slate-100 mt-2"):
                            ui.button(t("settings_btn_update_profile"), on_click=handle_update_profile).props("unelevated color=primary size=sm").classes("px-4 py-2 font-bold rounded-lg text-xs shadow-2xs")

                # Card 4: Đổi mật khẩu
                with ui.card().classes("w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xs gap-4"):
                    with ui.row().classes("items-center gap-2 pb-2 border-b border-slate-100"):
                        with ui.element("div").classes("w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700"):
                            ui.icon("lock").classes("text-base")
                        with ui.column().classes("gap-0"):
                            ui.label(t("settings_card_security_title")).classes("text-sm font-bold text-slate-900")
                            ui.label(t("settings_card_security_sub")).classes("text-[11px] text-slate-500")

                    with ui.column().classes("w-full gap-3 pt-1"):
                        old_pwd = ui.input(t("settings_field_old_pwd"), password=True).props("outlined dense password-toggle").classes("w-full text-xs")
                        new_pwd = ui.input(t("settings_field_new_pwd"), password=True).props("outlined dense password-toggle").classes("w-full text-xs")
                        confirm_pwd = ui.input(t("settings_field_confirm_pwd"), password=True).props("outlined dense password-toggle").classes("w-full text-xs")

                        async def handle_change_password() -> None:
                            p1 = (new_pwd.value or "").strip()
                            p2 = (confirm_pwd.value or "").strip()
                            if not p1 or len(p1) < 8:
                                toast.warning("Mật khẩu mới phải có tối thiểu 8 ký tự.")
                                return
                            if p1 != p2:
                                toast.warning("Mật khẩu xác nhận không khớp.")
                                return

                            try:
                                if user_id:
                                    await user_service.update_user(user_id, {"password": p1})
                                old_pwd.set_value("")
                                new_pwd.set_value("")
                                confirm_pwd.set_value("")
                                toast.success("Đã đổi mật khẩu thành công!")
                            except Exception as exc:
                                toast.error(f"Lỗi đổi mật khẩu: {exc}")

                        with ui.row().classes("w-full justify-end pt-3 border-t border-slate-100 mt-2"):
                            ui.button(t("settings_btn_change_pwd"), on_click=handle_change_password).props("outline color=slate-700 size=sm").classes("px-4 py-2 font-medium rounded-lg text-xs bg-white border-slate-300 shadow-2xs")

    app_shell(t("nav_settings"), content)
