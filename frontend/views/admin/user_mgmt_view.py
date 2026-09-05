from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from common.formatters import format_datetime
from core.constants import Role, UserStatus
from services.user_service import user_service


USER_COLUMNS = [
    {"name": "id", "label": "ID", "field": "id", "sortable": True},
    {"name": "username", "label": "Username", "field": "username", "sortable": True},
    {"name": "ho_ten", "label": "Họ tên", "field": "ho_ten", "sortable": True},
    {"name": "email", "label": "Email", "field": "email"},
    {"name": "vai_tro", "label": "Vai trò", "field": "vai_tro", "sortable": True},
    {"name": "trang_thai", "label": "Trạng thái", "field": "trang_thai", "sortable": True},
    {"name": "updated_at", "label": "Cập nhật", "field": "updated_at", "sortable": True},
]


def render_user_mgmt_view() -> None:
    def content(user: dict) -> None:
        if user.get("vai_tro") != "ADMIN":
            ui.label("Bạn không có quyền quản lý người dùng.").classes("text-red-600")
            return

        ui.label("Quản lý người dùng").classes("text-3xl font-bold text-slate-900")
        ui.label("Tạo tài khoản, lọc theo role/trạng thái và khóa/mở tài khoản.").classes("text-sm text-slate-500")

        with ui.row().classes("w-full gap-3 items-end mt-4"):
            keyword = ui.input("Từ khóa").props("outlined clearable debounce=300").classes("w-full md:w-80")
            role = ui.select(["ALL", *[item.value for item in Role]], value="ALL", label="Vai trò").props("outlined").classes("w-full md:w-52")
            status = ui.select(["ALL", *[item.value for item in UserStatus]], value="ALL", label="Trạng thái").props("outlined").classes("w-full md:w-52")

        table_holder = ui.column().classes("w-full mt-4")

        async def reload() -> None:
            try:
                users = await user_service.list_users(
                    role=None if role.value == "ALL" else role.value,
                    status=None if status.value == "ALL" else status.value,
                    keyword=keyword.value,
                    refresh=True,
                )
                rows = [{**item, "updated_at": format_datetime(item.get("updated_at"))} for item in users]
                table_holder.clear()
                with table_holder:
                    ui.table(columns=USER_COLUMNS, rows=rows, row_key="id", pagination=10).classes("w-full")
            except Exception as exc:
                table_holder.clear()
                with table_holder:
                    ui.label(str(exc)).classes("text-red-600")

        async def create_user() -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-lg rounded-2xl"):
                ui.label("Thêm người dùng").classes("text-xl font-bold")
                username = ui.input("Username").props("outlined").classes("w-full")
                password = ui.input("Mật khẩu", password=True).props("outlined").classes("w-full")
                full_name = ui.input("Họ tên").props("outlined").classes("w-full")
                email = ui.input("Email").props("outlined").classes("w-full")
                new_role = ui.select([item.value for item in Role], value="USER", label="Vai trò").props("outlined").classes("w-full")

                async def submit() -> None:
                    try:
                        await user_service.create_user(
                            {
                                "username": username.value,
                                "password": password.value,
                                "ho_ten": full_name.value,
                                "email": email.value or None,
                                "vai_tro": new_role.value,
                            }
                        )
                        toast.success("Đã tạo người dùng.")
                        dialog.close()
                        await reload()
                    except Exception as exc:
                        toast.error(str(exc))

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Hủy", on_click=dialog.close).props("flat")
                    ui.button("Tạo", on_click=submit).props("color=primary")
            dialog.open()

        with ui.row().classes("gap-2 mt-4"):
            ui.button("Tải lại", on_click=reload).props("outline color=primary")
            ui.button("Thêm người dùng", on_click=create_user).props("color=primary")

        ui.timer(0.1, reload, once=True)

    app_shell("Users", content)
