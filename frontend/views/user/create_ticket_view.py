from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from core.constants import TicketCategory, TicketPriority
from services.device_service import device_service
from services.ticket_service import ticket_service


def render_create_ticket_view() -> None:
    def content(user: dict) -> None:
        if user.get("vai_tro") == "TECHNICIAN":
            ui.label("Kỹ thuật viên không có quyền tạo ticket theo contract hiện tại.").classes("text-red-600")
            return

        ui.label("Tạo yêu cầu hỗ trợ").classes("text-3xl font-bold text-slate-900")
        ui.label("Form gửi trực tiếp `POST /api/tickets`.").classes("text-sm text-slate-500")

        with ui.card().classes("w-full max-w-2xl mt-4 p-5 rounded-2xl shadow-sm border border-slate-100"):
            title = ui.input("Tiêu đề").props("outlined").classes("w-full")
            description = ui.textarea("Mô tả chi tiết").props("outlined").classes("w-full")
            device = ui.select({}, label="Thiết bị liên quan").props("outlined clearable").classes("w-full")
            category = ui.select([item.value for item in TicketCategory], value="INCIDENT", label="Phân loại").props("outlined").classes("w-full")
            priority = ui.select([item.value for item in TicketPriority], value="MEDIUM", label="Mức ưu tiên").props("outlined").classes("w-full")

            async def load_devices() -> None:
                try:
                    devices = await device_service.list_devices()
                    device.options = {item["id"]: f"{item['ma_thiet_bi']} · {item['ten_thiet_bi']}" for item in devices}
                    device.update()
                except Exception:
                    device.options = {}

            async def submit() -> None:
                try:
                    await ticket_service.create_ticket(
                        {
                            "title": title.value,
                            "description": description.value,
                            "device_id": device.value,
                            "category": category.value,
                            "priority": priority.value,
                        }
                    )
                    toast.success("Đã tạo ticket.")
                    ui.navigate.to("/user/tickets")
                except Exception as exc:
                    toast.error(str(exc))

            ui.button("Gửi ticket", on_click=submit).props("color=primary")
            ui.timer(0.1, load_devices, once=True)

    app_shell("Create Ticket", content)
