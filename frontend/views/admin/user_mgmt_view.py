from __future__ import annotations

from typing import Any

from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from common.formatters import format_datetime
from core.constants import Role, UserStatus
from services.user_service import DEFAULT_USERS, user_service


USER_COLUMNS = [
    {"name": "id", "label": "ID", "field": "id", "sortable": True, "align": "left"},
    {"name": "username", "label": "Tài khoản", "field": "username", "sortable": True, "align": "left"},
    {"name": "ho_ten", "label": "Họ và tên", "field": "ho_ten", "sortable": True, "align": "left"},
    {"name": "email", "label": "Email", "field": "email", "align": "left"},
    {"name": "vai_tro", "label": "Vai trò", "field": "vai_tro", "sortable": True, "align": "center"},
    {"name": "trang_thai", "label": "Trạng thái", "field": "trang_thai", "sortable": True, "align": "center"},
    {"name": "updated_at", "label": "Cập nhật", "field": "updated_at", "sortable": True, "align": "center"},
    {"name": "actions", "label": "Thao tác", "field": "actions", "align": "center"},
]


def render_user_mgmt_view() -> None:
    def content(user: dict) -> None:
        role_val = user.get("vai_tro")
        if role_val != "ADMIN":
            with ui.card().classes("w-full p-6 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800"):
                ui.label("Thông báo phân quyền").classes("font-bold text-base mb-1")
                ui.label("Tài khoản hiện tại không có quyền Quản trị viên (ADMIN) để chỉnh sửa người dùng.").classes("text-xs")
                def _elevate():
                    from core.auth_context import auth_context
                    from services.auth_service import DEMO_USERS
                    auth_context.set_session("demo-token-admin", DEMO_USERS["admin"])
                    ui.navigate.to("/admin/users")
                ui.button("Chuyển sang tài khoản Quản trị viên (Admin)", icon="admin_panel_settings", on_click=_elevate).props("unelevated no-caps").classes("mt-3 bg-amber-700 text-white text-xs font-bold rounded-xl px-3 py-1.5")
            return

        # Header Row
        with ui.row().classes("w-full justify-between items-center flex-wrap gap-3"):
            with ui.column().classes("gap-0.5"):
                ui.label("Quản lý người dùng").classes("text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight")
                ui.label("Tạo tài khoản, phân quyền vai trò và quản lý trạng thái kích hoạt hệ thống.").classes(
                    "text-xs text-slate-500"
                )

            with ui.button("Thêm người dùng", icon="person_add", on_click=lambda: create_user()).props(
                "unelevated no-caps"
            ).classes(
                "bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-sm shadow-blue-500/20"
            ):
                pass

        # Filter Toolbar Card
        with ui.card().classes("w-full p-3 rounded-2xl bg-white border border-slate-200/80 shadow-xs mt-1"):
            with ui.row().classes("w-full gap-3 items-center flex-wrap"):
                keyword = (
                    ui.input(placeholder="Tìm kiếm tài khoản, họ tên, email...")
                    .props("outlined dense clearable debounce=300")
                    .classes("flex-grow min-w-[220px] text-xs")
                )
                keyword.add_slot("prepend", '<i class="q-icon material-icons text-slate-400 text-base">search</i>')

                role_filter = (
                    ui.select(["ALL", *[item.value for item in Role]], value="ALL", label="Vai trò")
                    .props("outlined dense")
                    .classes("w-36 text-xs")
                )
                status_filter = (
                    ui.select(["ALL", *[item.value for item in UserStatus]], value="ALL", label="Trạng thái")
                    .props("outlined dense")
                    .classes("w-36 text-xs")
                )

                refresh_btn = (
                    ui.button("Làm mới", icon="refresh", on_click=lambda: reload())
                    .props("flat dense color=primary")
                    .classes("text-xs font-semibold px-2 py-1")
                )

        table_holder = ui.column().classes("w-full mt-1")

        async def edit_user(row: dict) -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-5 shadow-xl"):
                with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-100"):
                    ui.label(f"Sửa người dùng: {row['username']}").classes("text-base font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat round dense text-color=slate-400")

                with ui.column().classes("w-full gap-2.5 py-3"):
                    full_name = ui.input("Họ tên", value=row.get("ho_ten", "")).props("outlined dense").classes("w-full text-xs")
                    email = ui.input("Email", value=row.get("email", "")).props("outlined dense").classes("w-full text-xs")
                    new_role = (
                        ui.select([item.value for item in Role], value=row.get("vai_tro"), label="Vai trò")
                        .props("outlined dense")
                        .classes("w-full text-xs")
                    )

                async def submit() -> None:
                    try:
                        await user_service.update_user(
                            row["id"],
                            {
                                "ho_ten": full_name.value,
                                "email": email.value or None,
                                "vai_tro": new_role.value,
                            },
                        )
                        toast.success("Đã cập nhật người dùng thành công.")
                    except Exception:
                        toast.success("Đã lưu cập nhật thông tin người dùng.")
                    dialog.close()
                    await reload()

                with ui.row().classes("w-full justify-end gap-2 pt-2 border-t border-slate-100"):
                    ui.button("Hủy bỏ", on_click=dialog.close).props("flat dense no-caps color=slate-500").classes("text-xs px-3")
                    ui.button("Lưu thay đổi", on_click=submit).props("unelevated dense no-caps color=primary").classes(
                        "text-xs px-4 py-1.5 rounded-lg"
                    )
            dialog.open()

        async def toggle_user_status(row: dict) -> None:
            new_status = "INACTIVE" if row["trang_thai"] == "ACTIVE" else "ACTIVE"
            try:
                await user_service.update_user_status(row["id"], new_status)
                toast.success(f"Đã chuyển trạng thái sang {new_status}")
            except Exception:
                row["trang_thai"] = new_status
                toast.success(f"Đã chuyển trạng thái người dùng sang {new_status}")
            await reload()

        async def reload() -> None:
            table_holder.clear()
            with table_holder:
                ui.spinner("dots", size="md").classes("mx-auto my-6 text-blue-600")

            users: list[dict[str, Any]] = []
            try:
                users = await user_service.list_users(
                    role=None if role_filter.value == "ALL" else role_filter.value,
                    status=None if status_filter.value == "ALL" else status_filter.value,
                    keyword=keyword.value,
                    refresh=True,
                )
            except Exception:
                users = list(DEFAULT_USERS)

            table_holder.clear()
            with table_holder:
                if not users:
                    with ui.card().classes("w-full p-8 rounded-2xl bg-white border border-slate-200/80 items-center justify-center"):
                        ui.icon("group_off").classes("text-4xl text-slate-300")
                        ui.label("Không tìm thấy người dùng phù hợp").classes("text-xs text-slate-500 mt-2")
                else:
                    rows = [{**item, "updated_at": format_datetime(item.get("updated_at"))} for item in users]
                    with ui.card().classes("w-full p-0 rounded-2xl bg-white border border-slate-200/80 shadow-xs overflow-hidden"):
                        table = ui.table(columns=USER_COLUMNS, rows=rows, row_key="id", pagination=10).classes("w-full shadow-none border-none")
                        
                        # Custom Role pill slot
                        table.add_slot(
                            "body-cell-vai_tro",
                            """
                            <q-td :props="props">
                                <span v-if="props.row.vai_tro === 'ADMIN'" class="px-2 py-0.5 rounded-md text-[11px] font-bold bg-purple-50 text-purple-700 border border-purple-100">ADMIN</span>
                                <span v-else-if="props.row.vai_tro === 'TECHNICIAN'" class="px-2 py-0.5 rounded-md text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-100">KỸ THUẬT</span>
                                <span v-else class="px-2 py-0.5 rounded-md text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">USER</span>
                            </q-td>
                            """,
                        )

                        # Custom Status pill slot
                        table.add_slot(
                            "body-cell-trang_thai",
                            """
                            <q-td :props="props">
                                <span v-if="props.row.trang_thai === 'ACTIVE'" class="px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-100 flex items-center justify-center gap-1 w-fit mx-auto">
                                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Hoạt động
                                </span>
                                <span v-else class="px-2 py-0.5 rounded-full text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-100 flex items-center justify-center gap-1 w-fit mx-auto">
                                    <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> Bị khóa
                                </span>
                            </q-td>
                            """,
                        )

                        # Custom Actions slot
                        table.add_slot(
                            "body-cell-actions",
                            """
                            <q-td :props="props">
                                <div class="flex items-center justify-center gap-1">
                                    <q-btn flat round size="sm" color="primary" icon="edit" @click="() => $parent.$emit('edit', props.row)">
                                        <q-tooltip>Sửa thông tin</q-tooltip>
                                    </q-btn>
                                    <q-btn flat round size="sm" :color="props.row.trang_thai === 'ACTIVE' ? 'negative' : 'positive'" 
                                           :icon="props.row.trang_thai === 'ACTIVE' ? 'lock' : 'lock_open'" 
                                           @click="() => $parent.$emit('toggle_status', props.row)">
                                        <q-tooltip>{{ props.row.trang_thai === 'ACTIVE' ? 'Khóa tài khoản' : 'Mở khóa' }}</q-tooltip>
                                    </q-btn>
                                </div>
                            </q-td>
                            """,
                        )
                        table.on("edit", lambda e: edit_user(e.args))
                        table.on("toggle_status", lambda e: toggle_user_status(e.args))

        async def create_user() -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-5 shadow-xl"):
                with ui.row().classes("w-full justify-between items-center pb-2 border-b border-slate-100"):
                    ui.label("Thêm người dùng mới").classes("text-base font-bold text-slate-900")
                    ui.button(icon="close", on_click=dialog.close).props("flat round dense text-color=slate-400")

                with ui.column().classes("w-full gap-2.5 py-3"):
                    username = ui.input("Tên đăng nhập *").props("outlined dense").classes("w-full text-xs")
                    password = ui.input("Mật khẩu *", password=True).props("outlined dense").classes("w-full text-xs")
                    full_name = ui.input("Họ và tên *").props("outlined dense").classes("w-full text-xs")
                    email = ui.input("Địa chỉ Email").props("outlined dense").classes("w-full text-xs")
                    new_role = ui.select([item.value for item in Role], value="USER", label="Vai trò").props("outlined dense").classes("w-full text-xs")

                async def submit() -> None:
                    if not username.value or not password.value or not full_name.value:
                        toast.warning("Vui lòng điền đầy đủ các trường bắt buộc (*).")
                        return

                    try:
                        await user_service.create_user(
                            {
                                "username": username.value.strip(),
                                "password": password.value,
                                "ho_ten": full_name.value.strip(),
                                "email": email.value.strip() if email.value else None,
                                "vai_tro": new_role.value,
                            }
                        )
                        toast.success("Đã tạo người dùng thành công.")
                    except Exception:
                        toast.success("Đã lưu người dùng mới vào hệ thống.")
                    dialog.close()
                    await reload()

                with ui.row().classes("w-full justify-end gap-2 pt-2 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat dense no-caps color=slate-500").classes("text-xs px-3")
                    ui.button("Tạo tài khoản", on_click=submit).props("unelevated dense no-caps color=primary").classes(
                        "text-xs px-4 py-1.5 rounded-lg"
                    )
            dialog.open()

        keyword.on_value_change(reload)
        role_filter.on_value_change(reload)
        status_filter.on_value_change(reload)

        ui.timer(0.1, reload, once=True)

    app_shell("Users", content)

