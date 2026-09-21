from __future__ import annotations

import json
from typing import Any
from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from common.components.status_badge import role_badge
from common.sound import play_notification_sound
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
        receive_email_pref = bool(user.get("receive_email_on_resolve", False))

        # =====================================================================
        # 1. STATE MANAGEMENT
        # =====================================================================
        state: dict[str, Any] = {
            "active_tab": "PROFILE",  # 'PROFILE' | 'APPEARANCE' | 'NOTIFICATIONS' | 'SECURITY'
            "save_status": "SAVED",   # 'SAVED' | 'SAVING' | 'UNSAVED' | 'ERROR'
            "profile_name": user_name,
            "profile_email": email,
            "selected_theme": "light",
            "selected_density": "compact",
            "selected_lang": get_lang(),
            "notify_comments": True,
            "notify_assigned": True,
            "notify_status_change": True,
            "notify_sla_urgent": True,
            "notify_sound": True,
            "notify_email_resolve": receive_email_pref,
            "is_saving": False,
        }

        original_profile = {
            "name": user_name,
            "email": email,
        }

        # Check unsaved changes helper
        def check_unsaved() -> None:
            has_changes = (
                (state["profile_name"] or "").strip() != (original_profile["name"] or "").strip()
                or (state["profile_email"] or "").strip() != (original_profile["email"] or "").strip()
            )
            if has_changes:
                state["save_status"] = "UNSAVED"
            elif state["save_status"] == "UNSAVED":
                state["save_status"] = "SAVED"
            render_status_badge()
            render_sticky_bar()

        # =====================================================================
        # 2. PAGE HEADER WITH DYNAMIC SAVE STATUS (W-FULL MAX-W-6XL)
        # =====================================================================
        with ui.column().classes("w-full max-w-6xl mx-auto gap-5 pb-16"):
            with ui.row().classes("w-full justify-between items-center pb-4 border-b border-slate-200 flex-wrap gap-4"):
                with ui.column().classes("gap-1"):
                    with ui.row().classes("items-center gap-2 text-sm text-slate-500 font-medium"):
                        ui.label("Trang chủ")
                        ui.icon("chevron_right", size="14px").classes("text-slate-400")
                        ui.label("Cài đặt cá nhân").classes("text-slate-900 font-bold")

                    ui.label("Cài đặt cá nhân").classes("text-3xl font-extrabold text-slate-900 tracking-tight")
                    ui.label("Quản lý hồ sơ tài khoản, giao diện hiển thị, tùy chọn thông báo và cấu hình bảo mật hệ thống.").classes("text-sm text-slate-600 font-medium")

                # Save status container
                status_container = ui.row().classes("items-center")

            def render_status_badge() -> None:
                status_container.clear()
                with status_container:
                    st = state["save_status"]
                    if st == "SAVING":
                        with ui.row().classes("items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-sm font-semibold shadow-2xs"):
                            ui.spinner("dots", size="sm", color="primary")
                            ui.label("Đang lưu dữ liệu...")
                    elif st == "UNSAVED":
                        with ui.row().classes("items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-sm font-bold shadow-2xs"):
                            ui.element("div").classes("w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse")
                            ui.label("Có thay đổi chưa lưu")
                    elif st == "ERROR":
                        with ui.row().classes("items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-red-700 text-sm font-bold shadow-2xs"):
                            ui.icon("error", size="18px").classes("text-red-500")
                            ui.label("Lỗi khi lưu")
                    else:
                        with ui.row().classes("items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold shadow-2xs"):
                            ui.icon("check_circle", size="18px").classes("text-emerald-600")
                            ui.label("Đã đồng bộ hệ thống")

            render_status_badge()

            # =====================================================================
            # 3. SEGMENTED NAVIGATION TABS (Large, Visible, Accessible)
            # =====================================================================
            tabs_container = ui.row().classes("w-full border-b border-slate-200 mb-2 gap-3 overflow-x-auto no-wrap")

            TABS = [
                ("PROFILE", "Hồ sơ cá nhân", "person"),
                ("APPEARANCE", "Giao diện & Hiển thị", "palette"),
                ("NOTIFICATIONS", "Thông báo & SLA", "notifications"),
                ("SECURITY", "Bảo mật tài khoản", "shield"),
            ]

            def render_tabs() -> None:
                tabs_container.clear()
                with tabs_container:
                    for tab_key, label, icon_name in TABS:
                        is_active = state["active_tab"] == tab_key
                        active_cls = (
                            "border-b-2 border-blue-600 text-blue-600 font-bold bg-blue-50/50 shadow-2xs"
                            if is_active
                            else "text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-semibold border-b-2 border-transparent"
                        )

                        def make_handler(k=tab_key):
                            return lambda: switch_tab(k)

                        with ui.button(on_click=make_handler()).props("flat dense").classes(
                            f"px-5 py-3 text-sm rounded-t-xl transition-all {active_cls}"
                        ):
                            with ui.row().classes("items-center gap-2.5 no-wrap"):
                                ui.icon(icon_name, size="18px").classes("text-inherit")
                                ui.label(label)

            def switch_tab(tab_key: str) -> None:
                state["active_tab"] = tab_key
                render_tabs()
                render_content_pane()

            render_tabs()

            # =====================================================================
            # 4. TAB CONTENT CONTAINER
            # =====================================================================
            content_pane = ui.column().classes("w-full gap-6")

            # =====================================================================
            # TAB 1: HỒ SƠ CÁ NHÂN (PROFILE)
            # =====================================================================
            def render_tab_profile() -> None:
                with content_pane:
                    # Identity Overview Card
                    with ui.card().classes("w-full p-6 sm:p-7 rounded-2xl bg-white border border-slate-200 shadow-sm gap-5"):
                        with ui.row().classes("items-center justify-between flex-wrap gap-5"):
                            with ui.row().classes("items-center gap-5"):
                                initials = (state["profile_name"] or username or "U")[:2].upper()
                                with ui.element("div").classes("w-16 h-16 rounded-2xl bg-blue-600 text-white font-black text-2xl flex items-center justify-center shadow-md border-2 border-blue-700"):
                                    ui.label(initials)

                                with ui.column().classes("gap-1"):
                                    with ui.row().classes("items-center gap-3 flex-wrap"):
                                        ui.label(state["profile_name"]).classes("text-xl font-bold text-slate-900")
                                        role_badge(role)
                                    ui.label(f"Tên đăng nhập: @{username}  •  Mã nhân viên: ID #{user_id}").classes("text-sm text-slate-500 font-medium")

                            with ui.row().classes("items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800"):
                                ui.element("div").classes("w-2.5 h-2.5 rounded-full bg-emerald-500")
                                ui.label("Tài khoản đang hoạt động (ACTIVE)")

                    # Form Details
                    with ui.card().classes("w-full p-6 sm:p-8 rounded-2xl bg-white border border-slate-200 shadow-sm gap-6"):
                        with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                            with ui.column().classes("gap-1"):
                                ui.label("Thông tin định danh người dùng").classes("text-lg font-bold text-slate-900")
                                ui.label("Thông tin này được hiển thị công khai trên các phiếu yêu cầu sự cố và nhật ký xử lý.").classes("text-sm text-slate-500")

                        with ui.element("div").classes("w-full grid grid-cols-1 md:grid-cols-2 gap-6"):
                            # Họ và tên
                            with ui.column().classes("w-full gap-1.5"):
                                ui.label("Họ và tên *").classes("text-sm font-bold text-slate-700")
                                name_input = ui.input(
                                    value=state["profile_name"],
                                    placeholder="Nhập họ và tên đầy đủ...",
                                ).props("outlined").classes("w-full text-sm bg-white")

                                def on_name_change(e):
                                    state["profile_name"] = e.value
                                    check_unsaved()

                                name_input.on_value_change(on_name_change)

                            # Email
                            with ui.column().classes("w-full gap-1.5"):
                                ui.label("Địa chỉ Email liên hệ").classes("text-sm font-bold text-slate-700")
                                email_input = ui.input(
                                    value=state["profile_email"],
                                    placeholder="ten.nguoidung@congty.com",
                                ).props("outlined").classes("w-full text-sm bg-white")

                                def on_email_change(e):
                                    state["profile_email"] = e.value
                                    check_unsaved()

                                email_input.on_value_change(on_email_change)

                            # Tên đăng nhập (Readonly)
                            with ui.column().classes("w-full gap-1.5"):
                                with ui.row().classes("items-center justify-between"):
                                    ui.label("Tên đăng nhập (Username)").classes("text-sm font-bold text-slate-700")
                                    ui.label("Chỉ đọc").classes("text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded")
                                username_input = ui.input(value=username).props("outlined readonly").classes("w-full text-sm bg-slate-50")
                                with username_input.add_slot("append"):
                                    ui.icon("lock", size="18px").classes("text-slate-400")
                                ui.label("Tên đăng nhập do Quản trị viên cấp khi khởi tạo tài khoản và không thể tự thay đổi.").classes("text-xs text-slate-400")

                            # Vai trò hệ thống (Readonly)
                            with ui.column().classes("w-full gap-1.5"):
                                with ui.row().classes("items-center justify-between"):
                                    ui.label("Vai trò & Phân quyền").classes("text-sm font-bold text-slate-700")
                                    ui.label("Cấp độ hệ thống").classes("text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded")
                                role_label_txt = "Quản trị viên (ADMIN)" if role == "ADMIN" else ("Kỹ thuật viên (TECHNICIAN)" if role == "TECHNICIAN" else "Người dùng phổ thông (USER)")
                                role_input = ui.input(value=role_label_txt).props("outlined readonly").classes("w-full text-sm bg-slate-50 font-semibold")
                                with role_input.add_slot("append"):
                                    ui.icon("shield", size="18px").classes("text-slate-400")
                                ui.label("Quyền hạn truy cập và thao tác được gán bởi Quản trị viên hệ thống.").classes("text-xs text-slate-400")

                        # Bottom Action Buttons
                        with ui.row().classes("w-full justify-between items-center pt-5 border-t border-slate-100 flex-wrap gap-4"):
                            ui.label("Lưu ý: Mọi thay đổi về họ tên và email sẽ cập nhật ngay trong các ticket sắp tới.").classes("text-xs text-slate-500 italic")

                            async def handle_save_profile() -> None:
                                val_name = (state["profile_name"] or "").strip()
                                val_email = (state["profile_email"] or "").strip()

                                if not val_name:
                                    toast.warning("Vui lòng nhập Họ và tên đầy đủ.")
                                    return

                                state["save_status"] = "SAVING"
                                render_status_badge()
                                save_btn.props("loading")

                                try:
                                    toast.info("Đang cập nhật thông tin hồ sơ...")
                                    await user_service.update_user(
                                        user_id,
                                        {
                                            "ho_ten": val_name,
                                            "email": val_email or None,
                                        }
                                    )
                                    original_profile["name"] = val_name
                                    original_profile["email"] = val_email
                                    state["save_status"] = "SAVED"
                                    toast.success("Đã cập nhật hồ sơ cá nhân thành công!")
                                except Exception as exc:
                                    state["save_status"] = "ERROR"
                                    toast.error(f"Lỗi cập nhật hồ sơ: {exc}")
                                finally:
                                    save_btn.props(remove="loading")
                                    render_status_badge()
                                    render_sticky_bar()

                            save_btn = ui.button(
                                "Lưu thay đổi hồ sơ",
                                icon="save",
                                on_click=handle_save_profile,
                            ).props("color=primary unelevated size=md").classes("h-11 px-6 font-bold text-sm rounded-xl shadow-sm")

            # =====================================================================
            # TAB 2: GIAO DIỆN & HIỂN THỊ (APPEARANCE)
            # =====================================================================
            def render_tab_appearance() -> None:
                with content_pane:
                    with ui.card().classes("w-full p-6 sm:p-8 rounded-2xl bg-white border border-slate-200 shadow-sm gap-7"):
                        with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                            with ui.column().classes("gap-1"):
                                ui.label("Tùy chọn giao diện & Vùng làm việc").classes("text-lg font-bold text-slate-900")
                                ui.label("Tùy biến chủ đề hiển thị, mật độ bảng dữ liệu và ngôn ngữ làm việc theo sở thích.").classes("text-sm text-slate-500")

                        # 1. Visual Theme Selector (No simple dropdowns)
                        with ui.column().classes("w-full gap-3"):
                            ui.label("Chế độ giao diện (Theme Mode)").classes("text-sm font-bold text-slate-800")
                            
                            theme_row = ui.row().classes("w-full grid grid-cols-1 sm:grid-cols-3 gap-4")
                            
                            THEMES = [
                                ("light", "Giao diện Sáng", "light_mode", "Giao diện trắng sáng sắc nét, tối ưu cho môi trường văn phòng ban ngày.", "bg-white border-slate-200"),
                                ("dark", "Giao diện Tối", "dark_mode", "Tông màu than trầm dịu mắt, giảm mỏi mắt khi làm việc ban đêm (Beta).", "bg-slate-900 text-white border-slate-800"),
                                ("auto", "Theo thiết bị", "settings_brightness", "Tự động chuyển đổi giao diện đồng bộ theo cài đặt hệ điều hành máy tính.", "bg-slate-100 border-slate-200"),
                            ]

                            def select_theme(th_code: str):
                                state["selected_theme"] = th_code
                                toast.info(f"Đã chọn giao diện: {th_code.upper()} (Đã lưu vào bộ nhớ máy)")
                                render_tab_appearance_rebuild()

                            with theme_row:
                                for code, title_t, icon_t, desc_t, bg_preview in THEMES:
                                    is_sel = state["selected_theme"] == code
                                    border_theme = "border-2 border-blue-600 bg-blue-50/40 shadow-sm ring-2 ring-blue-100" if is_sel else "border border-slate-200 bg-white hover:border-slate-300 hover:shadow-2xs"
                                    with ui.card().classes(f"p-5 rounded-2xl {border_theme} cursor-pointer transition-all gap-3").on("click", lambda c=code: select_theme(c)):
                                        with ui.row().classes("w-full justify-between items-center"):
                                            with ui.row().classes("items-center gap-2.5"):
                                                ui.icon(icon_t, size="22px").classes("text-blue-600" if is_sel else "text-slate-600")
                                                ui.label(title_t).classes("text-base font-bold text-slate-900")
                                            if is_sel:
                                                ui.icon("check_circle", size="20px").classes("text-blue-600")

                                        ui.label(desc_t).classes("text-xs text-slate-600 leading-relaxed")

                        ui.separator().classes("my-2")

                        # 2. Ngôn ngữ giao diện (Language Selector)
                        with ui.column().classes("w-full gap-3"):
                            ui.label("Ngôn ngữ hiển thị (System Language)").classes("text-sm font-bold text-slate-800")
                            
                            lang_grid = ui.row().classes("w-full grid grid-cols-1 sm:grid-cols-2 gap-4")
                            LANGS = [
                                ("vi", "Tiếng Việt (Vietnamese)", "translate", "Toàn bộ giao diện, nhãn trường và thông báo theo chuẩn Tiếng Việt."),
                                ("en", "English (United States)", "language", "System interface, navigation labels, and notifications in English."),
                            ]

                            def select_language(l_code: str):
                                state["selected_lang"] = l_code
                                set_lang(l_code)
                                msg = "Language changed to English!" if l_code == "en" else "Đã đổi ngôn ngữ sang Tiếng Việt!"
                                toast.success(msg)
                                ui.timer(0.3, lambda: ui.navigate.to("/settings"), once=True)

                            with lang_grid:
                                for l_code, l_title, l_icon_name, l_desc in LANGS:
                                    is_l_sel = state["selected_lang"] == l_code
                                    border_l = "border-2 border-blue-600 bg-blue-50/40 shadow-sm ring-2 ring-blue-100" if is_l_sel else "border border-slate-200 bg-white hover:border-slate-300 hover:shadow-2xs"
                                    with ui.card().classes(f"p-5 rounded-2xl {border_l} cursor-pointer transition-all gap-2.5").on("click", lambda c=l_code: select_language(c)):
                                        with ui.row().classes("w-full justify-between items-center"):
                                            with ui.row().classes("items-center gap-3"):
                                                ui.icon(l_icon_name, size="22px").classes("text-blue-600" if is_l_sel else "text-slate-600")
                                                ui.label(l_title).classes("text-base font-bold text-slate-900")
                                            if is_l_sel:
                                                ui.icon("check_circle", size="20px").classes("text-blue-600")
                                        ui.label(l_desc).classes("text-xs text-slate-600 leading-relaxed")

                        ui.separator().classes("my-2")

                        # 3. Mật độ hiển thị danh sách (Table Density)
                        with ui.column().classes("w-full gap-3"):
                            ui.label("Mật độ hiển thị bảng danh sách (Table Density)").classes("text-sm font-bold text-slate-800")

                            density_grid = ui.row().classes("w-full grid grid-cols-1 sm:grid-cols-3 gap-4")
                            DENSITIES = [
                                ("compact", "Gọn gàng (Compact)", "view_headline", "Hiển thị tối đa nhiều hàng dữ liệu trên một trang. Phù hợp cho Kỹ thuật viên xử lý nhanh."),
                                ("standard", "Tiêu chuẩn (Standard)", "view_agenda", "Cân bằng hoàn hảo giữa khoảng cách và khả năng đọc, chuẩn mực doanh nghiệp."),
                                ("comfortable", "Thoáng đãng (Comfortable)", "table_rows", "Khoảng cách giữa các dòng rộng rãi, trực quan và dễ chịu khi theo dõi tổng thể."),
                            ]

                            def select_density(d_code: str):
                                state["selected_density"] = d_code
                                toast.info(f"Mật độ bảng: {d_code.capitalize()} (Đã lưu vào bộ nhớ máy)")
                                render_tab_appearance_rebuild()

                            with density_grid:
                                for d_code, d_title, d_icon, d_desc in DENSITIES:
                                    is_d_sel = state["selected_density"] == d_code
                                    border_d = "border-2 border-blue-600 bg-blue-50/40 shadow-sm ring-2 ring-blue-100" if is_d_sel else "border border-slate-200 bg-white hover:border-slate-300 hover:shadow-2xs"
                                    with ui.card().classes(f"p-5 rounded-2xl {border_d} cursor-pointer transition-all gap-2.5").on("click", lambda c=d_code: select_density(c)):
                                        with ui.row().classes("w-full justify-between items-center"):
                                            with ui.row().classes("items-center gap-2.5"):
                                                ui.icon(d_icon, size="20px").classes("text-blue-600" if is_d_sel else "text-slate-600")
                                                ui.label(d_title).classes("text-base font-bold text-slate-900")
                                            if is_d_sel:
                                                ui.icon("check_circle", size="20px").classes("text-blue-600")
                                        ui.label(d_desc).classes("text-xs text-slate-600 leading-relaxed")

                        ui.separator().classes("my-2")

                        # 4. Múi giờ & Định dạng ngày
                        with ui.element("div").classes("w-full grid grid-cols-1 sm:grid-cols-2 gap-5 pt-1"):
                            with ui.column().classes("gap-1.5"):
                                ui.label("Múi giờ hệ thống").classes("text-sm font-bold text-slate-700")
                                ui.input(value="(GMT+07:00) Asia/Ho_Chi_Minh - Giờ Đông Dương (ICT)").props("outlined readonly").classes("w-full text-sm bg-slate-50")
                            with ui.column().classes("gap-1.5"):
                                ui.label("Định dạng ngày giờ chuẩn").classes("text-sm font-bold text-slate-700")
                                ui.input(value="DD/MM/YYYY HH:mm:ss (Ví dụ: 21/09/2026 14:00:00)").props("outlined readonly").classes("w-full text-sm bg-slate-50")

            def render_tab_appearance_rebuild():
                content_pane.clear()
                render_tab_appearance()

            # =====================================================================
            # TAB 3: THÔNG BÁO & CẢNH BÁO (NOTIFICATIONS)
            # =====================================================================
            def render_tab_notifications() -> None:
                with content_pane:
                    with ui.card().classes("w-full p-6 sm:p-8 rounded-2xl bg-white border border-slate-200 shadow-sm gap-7"):
                        with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                            with ui.column().classes("gap-1"):
                                ui.label("Cấu hình thông báo & Kênh cảnh báo").classes("text-lg font-bold text-slate-900")
                                ui.label("Tùy biến cách thức hệ thống gửi cảnh báo và cập nhật khi có sự cố phát sinh.").classes("text-sm text-slate-500")

                        # Group A: Trong ứng dụng (In-App)
                        with ui.column().classes("w-full gap-3.5"):
                            ui.label("A. THÔNG BÁO TRONG ỨNG DỤNG (IN-APP)").classes("text-xs font-bold text-slate-500 uppercase tracking-wider")

                            with ui.column().classes("w-full divide-y divide-slate-100 bg-slate-50/80 p-4 rounded-2xl border border-slate-200 gap-0"):
                                # Item 1
                                with ui.row().classes("w-full justify-between items-center py-3.5 gap-4"):
                                    with ui.column().classes("gap-1 flex-1"):
                                        ui.label("Phản hồi & Trao đổi ticket mới").classes("text-base font-bold text-slate-900")
                                        ui.label("Nhận Popup Toast thông báo ngay khi có bình luận hoặc trao đổi mới trên ticket bạn đang theo dõi.").classes("text-sm text-slate-600")
                                    ui.switch(value=state["notify_comments"], on_change=lambda e: state.update({"notify_comments": e.value})).props("size=md color=primary")

                                # Item 2
                                with ui.row().classes("w-full justify-between items-center py-3.5 gap-4"):
                                    with ui.column().classes("gap-1 flex-1"):
                                        ui.label("Phân công sự cố mới (Dành cho KTV & Admin)").classes("text-base font-bold text-slate-900")
                                        ui.label("Cảnh báo tức thời trên chuông thông báo khi sự cố được phân công trực tiếp cho bạn.").classes("text-sm text-slate-600")
                                    ui.switch(value=state["notify_assigned"], on_change=lambda e: state.update({"notify_assigned": e.value})).props("size=md color=primary")

                                # Item 3
                                with ui.row().classes("w-full justify-between items-center py-3.5 gap-4"):
                                    with ui.column().classes("gap-1 flex-1"):
                                        ui.label("Thay đổi trạng thái ticket").classes("text-base font-bold text-slate-900")
                                        ui.label("Nhận cập nhật khi sự cố chuyển tiếp trạng thái (Mở → Đang xử lý → Đã giải quyết → Đóng).").classes("text-sm text-slate-600")
                                    ui.switch(value=state["notify_status_change"], on_change=lambda e: state.update({"notify_status_change": e.value})).props("size=md color=primary")

                        # Group B: SLA & Âm thanh
                        with ui.column().classes("w-full gap-3.5"):
                            ui.label("B. CẢNH BÁO SỰ CỐ KHẨN CẤP & ÂM THANH").classes("text-xs font-bold text-slate-500 uppercase tracking-wider")

                            with ui.column().classes("w-full divide-y divide-slate-100 bg-slate-50/80 p-4 rounded-2xl border border-slate-200 gap-0"):
                                # Item 1
                                with ui.row().classes("w-full justify-between items-center py-3.5 gap-4"):
                                    with ui.column().classes("gap-1 flex-1"):
                                        ui.label("Cảnh báo sự cố mức độ Khẩn cấp (Urgent SLA)").classes("text-base font-bold text-rose-700")
                                        ui.label("Đánh dấu nổi bật và cảnh báo ưu tiên cao đối với các sự cố có nguy cơ vi phạm SLA.").classes("text-sm text-slate-600")
                                    ui.switch(value=state["notify_sla_urgent"], on_change=lambda e: state.update({"notify_sla_urgent": e.value})).props("size=md color=negative")

                                # Item 2
                                with ui.row().classes("w-full justify-between items-center py-3.5 gap-4"):
                                    with ui.column().classes("gap-1 flex-1"):
                                        ui.label("Âm thanh cảnh báo khi có thông báo mới").classes("text-base font-bold text-slate-900")
                                        ui.label("Phát âm thanh ngắn (Beep alert) khi xuất hiện thông báo mới hoặc sự cố khẩn cấp.").classes("text-sm text-slate-600")

                                    with ui.row().classes("items-center gap-3"):
                                        def handle_play_sound() -> None:
                                            play_notification_sound()
                                            toast.info("Đã phát âm thanh cảnh báo!")

                                        ui.button("Phát thử âm thanh", icon="volume_up", on_click=handle_play_sound).props("outline size=sm color=slate-700").classes("text-xs font-semibold px-3.5 py-1.5 rounded-lg")
                                        ui.switch(value=state["notify_sound"], on_change=lambda e: state.update({"notify_sound": e.value})).props("size=md color=primary")

                        # Group C: Email Notifications (Real Backend Binding)
                        with ui.column().classes("w-full gap-3.5"):
                            ui.label("C. THÔNG BÁO QUA EMAIL (BACKEND INTEGRATED)").classes("text-xs font-bold text-slate-500 uppercase tracking-wider")

                            with ui.column().classes("w-full divide-y divide-slate-100 bg-slate-50/80 p-4 rounded-2xl border border-slate-200 gap-0"):
                                # Email Resolve Notification
                                with ui.row().classes("w-full justify-between items-center py-3.5 gap-4"):
                                    with ui.column().classes("gap-1 flex-1"):
                                        ui.label("Nhận Email tóm tắt khi sự cố được giải quyết").classes("text-base font-bold text-slate-900")
                                        ui.label("Hệ thống tự động gửi email thông báo chi tiết khi kỹ thuật viên hoàn tất xử lý ticket của bạn.").classes("text-sm text-slate-600")

                                    async def on_email_toggle(e):
                                        new_val = e.value
                                        state["notify_email_resolve"] = new_val
                                        try:
                                            toast.info("Đang đồng bộ cấu hình Email với máy chủ...")
                                            await user_service.update_user(user_id, {"receive_email_on_resolve": new_val})
                                            toast.success("Đã lưu tùy chọn thông báo Email thành công!")
                                        except Exception as exc:
                                            toast.error(f"Lỗi cập nhật tùy chọn Email: {exc}")

                                    ui.switch(value=state["notify_email_resolve"], on_change=on_email_toggle).props("size=md color=primary")

            # =====================================================================
            # TAB 4: BẢO MẬT & MẬT KHẨU (SECURITY - RICH ENTERPRISE OVERVIEW)
            # =====================================================================
            def render_tab_security() -> None:
                with content_pane:
                    with ui.card().classes("w-full p-6 sm:p-8 rounded-2xl bg-white border border-slate-200 shadow-sm gap-7"):
                        with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                            with ui.column().classes("gap-1"):
                                ui.label("Tổng quan an toàn & Bảo mật tài khoản").classes("text-lg font-bold text-slate-900")
                                ui.label("Quản lý mật khẩu truy cập, phương thức xác thực và thông tin phiên làm việc an toàn.").classes("text-sm text-slate-500")

                        # Grid 2-column or full width security cards
                        with ui.column().classes("w-full gap-4"):
                            # Section 1: Password Management
                            with ui.card().classes("w-full p-5 sm:p-6 rounded-2xl bg-slate-50/90 border border-slate-200 gap-4 hover:border-slate-300 transition-all"):
                                with ui.row().classes("w-full justify-between items-center flex-wrap gap-4"):
                                    with ui.row().classes("items-center gap-4 flex-1 min-w-[280px]"):
                                        with ui.element("div").classes("w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold shadow-2xs"):
                                            ui.icon("lock", size="24px")
                                        with ui.column().classes("gap-1"):
                                            ui.label("Mật khẩu đăng nhập").classes("text-base font-bold text-slate-900")
                                            ui.label("Mật khẩu tài khoản được mã hóa một chiều bằng chuẩn thuật toán Bcrypt an toàn.").classes("text-sm text-slate-600")

                                    ui.button(
                                        "Đổi mật khẩu tài khoản",
                                        icon="key",
                                        on_click=open_change_password_modal,
                                    ).props("unelevated color=primary size=md").classes("h-11 px-5 font-bold text-sm rounded-xl shadow-sm")

                            # Section 2: Two-Factor Authentication (2FA) - Real Status
                            with ui.card().classes("w-full p-5 sm:p-6 rounded-2xl bg-slate-50/90 border border-slate-200 gap-4 hover:border-slate-300 transition-all"):
                                with ui.row().classes("w-full justify-between items-center flex-wrap gap-4"):
                                    with ui.row().classes("items-center gap-4 flex-1 min-w-[280px]"):
                                        with ui.element("div").classes("w-12 h-12 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold shadow-2xs"):
                                            ui.icon("security", size="24px")
                                        with ui.column().classes("gap-1"):
                                            with ui.row().classes("items-center gap-2.5"):
                                                ui.label("Xác thực 2 yếu tố (2FA / OTP)").classes("text-base font-bold text-slate-900")
                                                ui.label("Tính năng nâng cao").classes("text-xs font-bold px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200")
                                            ui.label("Tăng cường an toàn bằng mã OTP xác minh qua ứng dụng Authenticator (Google/Microsoft).").classes("text-sm text-slate-600")

                                    ui.button("Chưa hỗ trợ", icon="lock_clock").props("outline size=md color=slate-400 dense disabled").classes("h-10 px-4 text-xs font-semibold bg-white rounded-xl")

                            # Section 3: Active Sessions
                            with ui.card().classes("w-full p-5 sm:p-6 rounded-2xl bg-slate-50/90 border border-slate-200 gap-4 hover:border-slate-300 transition-all"):
                                with ui.row().classes("w-full justify-between items-center flex-wrap gap-4"):
                                    with ui.row().classes("items-center gap-4 flex-1 min-w-[280px]"):
                                        with ui.element("div").classes("w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold shadow-2xs"):
                                            ui.icon("devices", size="24px")
                                        with ui.column().classes("gap-1"):
                                            with ui.row().classes("items-center gap-2.5"):
                                                ui.label("Phiên đăng nhập hiện tại").classes("text-base font-bold text-slate-900")
                                                ui.label("Đang hoạt động").classes("text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200")
                                            ui.label("Xác thực bằng JWT Bearer Token (Hiệu lực: 480 phút theo chính sách bảo mật hệ thống).").classes("text-sm text-slate-600")

                                    with ui.row().classes("items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800"):
                                        ui.icon("check_circle", size="16px").classes("text-emerald-600")
                                        ui.label("Phiên kết nối an toàn")

            # =====================================================================
            # 5. MODAL ĐỔI MẬT KHẨU (CHANGE PASSWORD MODAL)
            # =====================================================================
            def open_change_password_modal() -> None:
                dialog = ui.dialog()
                with dialog, ui.card().classes("w-full max-w-lg rounded-2xl p-7 bg-white border border-slate-200 shadow-2xl gap-5"):
                    with ui.row().classes("w-full justify-between items-center pb-3 border-b border-slate-100"):
                        with ui.row().classes("items-center gap-2.5"):
                            ui.icon("lock_reset", size="24px").classes("text-primary")
                            ui.label("Đổi mật khẩu tài khoản").classes("text-lg font-bold text-slate-900")
                        ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm color=slate-400")

                    ui.label("Nhập mật khẩu hiện tại và mật khẩu mới để cập nhật thông tin xác thực an toàn.").classes("text-sm text-slate-600")

                    # Form
                    with ui.column().classes("w-full gap-4 pt-1"):
                        with ui.column().classes("w-full gap-1.5"):
                            ui.label("Mật khẩu hiện tại *").classes("text-sm font-bold text-slate-700")
                            curr_pwd = ui.input(placeholder="••••••••").props("outlined type=password password-toggle").classes("w-full text-sm bg-white")

                        with ui.column().classes("w-full gap-1.5"):
                            ui.label("Mật khẩu mới * (Tối thiểu 8 ký tự)").classes("text-sm font-bold text-slate-700")
                            new_pwd_input = ui.input(placeholder="••••••••").props("outlined type=password password-toggle").classes("w-full text-sm bg-white")

                        # Realtime Password Strength Indicator
                        strength_bar = ui.linear_progress(value=0, color="red").props("size=6px rounded").classes("w-full rounded-full bg-slate-100 mt-1")
                        strength_label = ui.label("Độ mạnh: Chưa nhập").classes("text-xs text-slate-400 font-medium")

                        def check_pwd_strength(e):
                            val = e.value or ""
                            l = len(val)
                            if l == 0:
                                strength_bar.value = 0
                                strength_bar.props("color=red")
                                strength_label.text = "Độ mạnh: Chưa nhập"
                                strength_label.classes("text-xs text-slate-400", remove="text-red-600 text-amber-600 text-emerald-600 font-bold")
                            elif l < 8:
                                strength_bar.value = 0.33
                                strength_bar.props("color=red")
                                strength_label.text = "Độ mạnh: Yếu (Cần tối thiểu 8 ký tự)"
                                strength_label.classes("text-xs text-red-600 font-bold", remove="text-slate-400 text-amber-600 text-emerald-600")
                            elif l < 12 or val.isdigit() or val.isalpha():
                                strength_bar.value = 0.66
                                strength_bar.props("color=amber")
                                strength_label.text = "Độ mạnh: Trung bình (Nên kết hợp chữ, số và ký tự đặc biệt)"
                                strength_label.classes("text-xs text-amber-600 font-bold", remove="text-slate-400 text-red-600 text-emerald-600")
                            else:
                                strength_bar.value = 1.0
                                strength_bar.props("color=emerald")
                                strength_label.text = "Độ mạnh: Rất mạnh (An toàn tuyệt đối)"
                                strength_label.classes("text-xs text-emerald-600 font-bold", remove="text-slate-400 text-red-600 text-amber-600")

                        new_pwd_input.on_value_change(check_pwd_strength)

                        with ui.column().classes("w-full gap-1.5 mt-1"):
                            ui.label("Xác nhận mật khẩu mới *").classes("text-sm font-bold text-slate-700")
                            confirm_pwd_input = ui.input(placeholder="••••••••").props("outlined type=password password-toggle").classes("w-full text-sm bg-white")

                    # Action Buttons
                    async def submit_password_change() -> None:
                        c_pwd = (curr_pwd.value or "").strip()
                        n_pwd = (new_pwd_input.value or "").strip()
                        cf_pwd = (confirm_pwd_input.value or "").strip()

                        if not c_pwd:
                            toast.warning("Vui lòng nhập mật khẩu hiện tại.")
                            return
                        if not n_pwd or len(n_pwd) < 8:
                            toast.warning("Mật khẩu mới phải có tối thiểu 8 ký tự.")
                            return
                        if n_pwd != cf_pwd:
                            toast.warning("Mật khẩu xác nhận không khớp. Vui lòng kiểm tra lại.")
                            return
                        if c_pwd == n_pwd:
                            toast.warning("Mật khẩu mới không được trùng với mật khẩu hiện tại.")
                            return

                        modal_submit_btn.props("loading")
                        try:
                            toast.info("Đang tiến hành đổi mật khẩu...")
                            await auth_service.change_password(c_pwd, n_pwd)
                            toast.success("Đã đổi mật khẩu tài khoản thành công!")
                            dialog.close()
                        except Exception as exc:
                            toast.show_popup(
                                title="Lỗi đổi mật khẩu",
                                message="Không thể cập nhật mật khẩu mới.",
                                type="error",
                                detail=str(exc),
                            )
                        finally:
                            modal_submit_btn.props(remove="loading")

                    with ui.row().classes("w-full justify-end gap-3 pt-4 border-t border-slate-100 mt-2"):
                        ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600 size=md").classes("px-4 text-sm font-semibold")
                        modal_submit_btn = ui.button(
                            "Xác nhận đổi mật khẩu",
                            icon="lock",
                            on_click=submit_password_change,
                        ).props("color=primary unelevated size=md").classes("px-5 py-2.5 text-sm font-bold rounded-xl shadow-sm")

                dialog.open()

            # =====================================================================
            # 6. RENDER ACTIVE TAB CONTENT
            # =====================================================================
            def render_content_pane() -> None:
                content_pane.clear()
                tab = state["active_tab"]
                if tab == "PROFILE":
                    render_tab_profile()
                elif tab == "APPEARANCE":
                    render_tab_appearance()
                elif tab == "NOTIFICATIONS":
                    render_tab_notifications()
                elif tab == "SECURITY":
                    render_tab_security()

            render_content_pane()

            # =====================================================================
            # 7. STICKY ACTION BAR FOR UNSAVED CHANGES
            # =====================================================================
            sticky_bar_container = ui.element("div").classes(
                "fixed bottom-6 left-1/2 -translate-x-1/2 z-30 transition-all duration-300 pointer-events-none"
            )

            def render_sticky_bar() -> None:
                sticky_bar_container.clear()
                has_changes = state["save_status"] == "UNSAVED"
                if not has_changes:
                    return

                with sticky_bar_container:
                    with ui.card().classes(
                        "pointer-events-auto p-4 px-6 rounded-2xl bg-slate-900 text-white border border-slate-700 shadow-2xl gap-5 items-center flex-row flex-wrap"
                    ):
                        with ui.row().classes("items-center gap-3"):
                            ui.icon("error_outline", size="22px").classes("text-amber-400")
                            ui.label("Bạn có thay đổi thông tin hồ sơ chưa được lưu.").classes("text-sm font-bold text-slate-100")

                        with ui.row().classes("items-center gap-3"):
                            def discard_changes():
                                state["profile_name"] = original_profile["name"]
                                state["profile_email"] = original_profile["email"]
                                state["save_status"] = "SAVED"
                                render_status_badge()
                                render_sticky_bar()
                                render_content_pane()
                                toast.info("Đã hủy bỏ các thay đổi chưa lưu.")

                            async def save_sticky_changes():
                                val_name = (state["profile_name"] or "").strip()
                                val_email = (state["profile_email"] or "").strip()
                                if not val_name:
                                    toast.warning("Vui lòng nhập Họ và tên đầy đủ.")
                                    return
                                state["save_status"] = "SAVING"
                                render_status_badge()
                                try:
                                    toast.info("Đang lưu thay đổi...")
                                    await user_service.update_user(user_id, {"ho_ten": val_name, "email": val_email or None})
                                    original_profile["name"] = val_name
                                    original_profile["email"] = val_email
                                    state["save_status"] = "SAVED"
                                    toast.success("Đã lưu thay đổi hồ sơ thành công!")
                                except Exception as exc:
                                    state["save_status"] = "ERROR"
                                    toast.error(f"Lỗi lưu thay đổi: {exc}")
                                finally:
                                    render_status_badge()
                                    render_sticky_bar()
                                    render_content_pane()

                            ui.button("Hủy thay đổi", on_click=discard_changes).props("flat color=slate-300 size=md").classes("text-sm font-semibold px-4")
                            ui.button("Lưu thay đổi", icon="save", on_click=save_sticky_changes).props("unelevated color=primary size=md").classes("text-sm font-bold px-5 py-2 rounded-xl shadow-md")

            render_sticky_bar()

    app_shell("Cài đặt cá nhân", content)
