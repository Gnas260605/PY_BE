from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from common.formatters import format_datetime
from core.constants import DeviceStatus
from services.device_service import device_service


DEVICE_COLUMNS = [
    {"name": "id", "label": "ID", "field": "id", "sortable": True},
    {"name": "ma_thiet_bi", "label": "Mã TB", "field": "ma_thiet_bi", "sortable": True},
    {"name": "ten_thiet_bi", "label": "Tên thiết bị", "field": "ten_thiet_bi", "sortable": True},
    {"name": "loai_thiet_bi", "label": "Loại", "field": "loai_thiet_bi"},
    {"name": "vi_tri", "label": "Vị trí", "field": "vi_tri"},
    {"name": "trang_thai", "label": "Trạng thái", "field": "trang_thai", "sortable": True},
    {"name": "updated_at", "label": "Cập nhật", "field": "updated_at", "sortable": True},
]


def render_device_mgmt_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro")
        if role not in ("ADMIN", "TECHNICIAN"):
            ui.label("Bạn không có quyền xem danh mục thiết bị.").classes("text-red-600")
            return

        ui.label("Quản lý thiết bị").classes("text-3xl font-bold text-slate-900")
        ui.label("ADMIN tạo/sửa thiết bị; TECHNICIAN cập nhật trạng thái theo backend RBAC.").classes("text-sm text-slate-500")

        with ui.row().classes("w-full gap-3 items-end mt-4"):
            keyword = ui.input("Từ khóa").props("outlined clearable debounce=300").classes("w-full md:w-80")
            status = ui.select(["ALL", *[item.value for item in DeviceStatus]], value="ALL", label="Trạng thái").props("outlined").classes("w-full md:w-56")

        table_holder = ui.column().classes("w-full mt-4")

        async def reload() -> None:
            try:
                devices = await device_service.list_devices(
                    status=None if status.value == "ALL" else status.value,
                    keyword=keyword.value,
                    refresh=True,
                )
                rows = [{**item, "updated_at": format_datetime(item.get("updated_at"))} for item in devices]
                table_holder.clear()
                with table_holder:
                    ui.table(columns=DEVICE_COLUMNS, rows=rows, row_key="id", pagination=10).classes("w-full")
            except Exception as exc:
                table_holder.clear()
                with table_holder:
                    ui.label(str(exc)).classes("text-red-600")

        async def create_device() -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-lg rounded-2xl"):
                ui.label("Thêm thiết bị").classes("text-xl font-bold")
                code = ui.input("Mã thiết bị").props("outlined").classes("w-full")
                name = ui.input("Tên thiết bị").props("outlined").classes("w-full")
                device_type = ui.input("Loại thiết bị").props("outlined").classes("w-full")
                location = ui.input("Vị trí").props("outlined").classes("w-full")
                device_status = ui.select([item.value for item in DeviceStatus], value="ACTIVE", label="Trạng thái").props("outlined").classes("w-full")
                description = ui.textarea("Mô tả").props("outlined").classes("w-full")

                async def submit() -> None:
                    try:
                        await device_service.create_device(
                            {
                                "ma_thiet_bi": code.value,
                                "ten_thiet_bi": name.value,
                                "loai_thiet_bi": device_type.value or None,
                                "vi_tri": location.value or None,
                                "trang_thai": device_status.value,
                                "mo_ta": description.value or None,
                            }
                        )
                        toast.success("Đã tạo thiết bị.")
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
            if role == "ADMIN":
                ui.button("Thêm thiết bị", on_click=create_device).props("color=primary")

        ui.timer(0.1, reload, once=True)

    app_shell("Devices", content)
