from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from common.components.status_badge import role_badge, status_badge
from common.formatters import format_datetime
from core.constants import Role, UserStatus
from services.user_service import user_service


def render_user_mgmt_view() -> None:
    def content(user: dict) -> None:
        if user.get("vai_tro") != "ADMIN":
            ui.label("Bạn không có quyền quản lý người dùng.").classes("text-red-600")
            return

        # Header
        with ui.row().classes("w-full justify-between items-center mb-4"):
            with ui.column().classes("gap-0.5"):
                ui.label("Quản trị Người dùng & Phân quyền").classes("text-2xl font-bold text-slate-900")
                ui.label("Quản lý danh sách tài khoản, vai trò và trạng thái hoạt động trong hệ thống.").classes("text-xs text-slate-500")

            ui.button("Thêm người dùng", icon="person_add", on_click=lambda: create_user_dialog()).props("color=primary unelevated")

        # Filters Toolbar
        with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm"):
            with ui.row().classes("w-full gap-3 items-end"):
                keyword = ui.input("Tìm theo username, họ tên, email...").props("outlined clearable debounce=300").classes("flex-1 min-w-[240px]")
                role = ui.select(["ALL", *[item.value for item in Role]], value="ALL", label="Vai trò").props("outlined").classes("w-44")
                status = ui.select(["ALL", *[item.value for item in UserStatus]], value="ALL", label="Trạng thái").props("outlined").classes("w-44")
                ui.button("Tải lại", icon="refresh", on_click=lambda: reload_users()).props("outline size=sm color=slate-700").classes("py-2.5")

        table_holder = ui.column().classes("w-full mt-4")

        async def toggle_status(u: dict[str, Any]) -> None:
            user_id = u["id"]
            current_s = u.get("trang_thai") or u.get("status")
            new_s = "INACTIVE" if current_s == "ACTIVE" else "ACTIVE"

            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-sm rounded-xl p-5"):
                ui.label(f"{'Khóa' if new_s == 'INACTIVE' else 'Mở khóa'} tài khoản").classes("text-base font-bold text-slate-900 mb-1")
                ui.label(f"Bạn có chắc muốn chuyển trạng thái user @{u.get('username')} sang {new_s}?").classes("text-xs text-slate-600 mb-4")

                async def do_toggle() -> None:
                    try:
                        await user_service.update_user_status(user_id, new_s)
                        toast.success(f"Đã cập nhật trạng thái user sang {new_s}")
                        dialog.close()
                        await reload_users()
                    except Exception as exc:
                        toast.error(str(exc))

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Hủy", on_click=dialog.close).props("flat")
                    ui.button("Xác nhận", on_click=do_toggle).props(f"color={'negative' if new_s == 'INACTIVE' else 'primary'} unelevated")
            dialog.open()

        async def reload_users() -> None:
            try:
                users = await user_service.list_users(
                    role=None if role.value == "ALL" else role.value,
                    status=None if status.value == "ALL" else status.value,
                    keyword=keyword.value,
                    refresh=True,
                )
            except Exception as exc:
                table_holder.clear()
                with table_holder:
                    ui.label(f"Lỗi tải danh sách người dùng: {exc}").classes("text-sm text-red-600")
                return

            table_holder.clear()
            with table_holder:
                with ui.card().classes("w-full p-0 rounded-xl bg-white border border-slate-200 shadow-sm overflow-hidden"):
                    with ui.row().classes("w-full justify-between items-center p-4 border-b border-slate-100"):
                        ui.label(f"Danh sách người dùng ({len(users)})").classes("text-sm font-bold text-slate-800")

                    with ui.column().classes("w-full divide-y divide-slate-100"):
                        for u in users:
                            with ui.row().classes("w-full justify-between items-center p-3.5 hover:bg-slate-50 transition-colors"):
                                # Avatar & Info
                                with ui.row().classes("items-center gap-3"):
                                    with ui.avatar(color="primary", text_color="white").props("size=34px font-size=12px").classes("font-bold"):
                                        ui.label((u.get("ho_ten") or u.get("username") or "U")[:2].upper())
                                    with ui.column().classes("gap-0"):
                                        ui.label(u.get("ho_ten") or u.get("username")).classes("text-sm font-bold text-slate-800")
                                        ui.label(f"@{u.get('username')} · {u.get('email') or 'Chưa có email'}").classes("text-xs text-slate-400")

                                # Roles & Badges
                                with ui.row().classes("items-center gap-2"):
                                    role_badge(u.get("vai_tro"))
                                    status_badge(u.get("trang_thai"))

                                    # Action button
                                    is_active = (u.get("trang_thai") or u.get("status")) == "ACTIVE"
                                    ui.button(
                                        "Khóa" if is_active else "Kích hoạt",
                                        icon="lock" if is_active else "lock_open",
                                        on_click=lambda u=u: toggle_status(u),
                                    ).props(f"flat dense size=sm color={'negative' if is_active else 'positive'}").classes("rounded-md")

        def create_user_dialog() -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-3"):
                ui.label("Thêm tài khoản mới").classes("text-lg font-bold text-slate-900")
                ui.label("Tạo tài khoản người dùng và thiết lập phân quyền ban đầu.").classes("text-xs text-slate-500 mb-1")

                username = ui.input("Tên đăng nhập *").props("outlined").classes("w-full")
                password = ui.input("Mật khẩu *", password=True).props("outlined").classes("w-full")
                full_name = ui.input("Họ và tên *").props("outlined").classes("w-full")
                email = ui.input("Email liên hệ").props("outlined").classes("w-full")
                new_role = ui.select([item.value for item in Role], value="USER", label="Vai trò hệ thống").props("outlined").classes("w-full")

                async def submit() -> None:
                    if not (username.value or "").strip():
                        toast.warning("Vui lòng nhập Username.")
                        return
                    if not (password.value or "").strip():
                        toast.warning("Vui lòng nhập Mật khẩu.")
                        return
                    if not (full_name.value or "").strip():
                        toast.warning("Vui lòng nhập Họ tên.")
                        return

                    try:
                        await user_service.create_user(
                            {
                                "username": username.value.strip(),
                                "password": password.value.strip(),
                                "ho_ten": full_name.value.strip(),
                                "email": email.value.strip() if email.value else None,
                                "vai_tro": new_role.value,
                            }
                        )
                        toast.success("Đã tạo người dùng thành công.")
                        dialog.close()
                        await reload_users()
                    except Exception as exc:
                        toast.error(str(exc))

                with ui.row().classes("w-full justify-end gap-2 mt-4 pt-3 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600")
                    ui.button("Tạo tài khoản", on_click=submit).props("color=primary unelevated")
            dialog.open()

        ui.timer(0.1, reload_users, once=True)

    app_shell("Người dùng", content)
