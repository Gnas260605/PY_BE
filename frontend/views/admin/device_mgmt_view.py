from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import status_badge
from common.formatters import format_datetime
from core.constants import DeviceStatus
from services.device_service import device_service


def render_device_mgmt_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro")
        if role not in ("ADMIN", "TECHNICIAN"):
            ui.label("Bạn không có quyền xem danh mục thiết bị.").classes("text-red-600")
            return

        # Header
        with ui.row().classes("w-full justify-between items-center mb-4"):
            with ui.column().classes("gap-0.5"):
                ui.label("Quản trị Danh mục Thiết bị IT").classes("text-2xl font-bold text-slate-900")
                ui.label("Theo dõi toàn bộ trang thiết bị máy tính, máy in và phần cứng trong tổ chức.").classes("text-xs text-slate-500")

            if role == "ADMIN":
                ui.button("Thêm thiết bị mới", icon="add", on_click=lambda: create_device_dialog()).props("color=primary unelevated")

        # Filters Toolbar
        with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm"):
            with ui.row().classes("w-full gap-3 items-end"):
                keyword = ui.input("Tìm theo mã, tên thiết bị, vị trí...").props("outlined clearable debounce=300").classes("flex-1 min-w-[240px]")
                status = ui.select(["ALL", *[item.value for item in DeviceStatus]], value="ALL", label="Trạng thái").props("outlined").classes("w-48")
                ui.button("Tải lại", icon="refresh", on_click=lambda: reload_devices()).props("outline size=sm color=slate-700").classes("py-2.5")

        device_container = ui.column().classes("w-full mt-4")

        async def view_device_history(dev: dict[str, Any]) -> None:
            dev_id = dev["id"]
            try:
                tickets = await device_service.get_device_tickets(dev_id)
            except Exception as exc:
                toast.error(f"Lỗi tải lịch sử ticket: {exc}")
                return

            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-2xl rounded-2xl p-6 bg-white"):
                with ui.row().classes("w-full justify-between items-center mb-3"):
                    with ui.column().classes("gap-0.5"):
                        ui.label(f"{dev.get('ma_thiet_bi')} · {dev.get('ten_thiet_bi')}").classes("text-base font-bold text-slate-900")
                        ui.label(f"Vị trí: {dev.get('vi_tri') or 'Chưa rõ'}").classes("text-xs text-slate-500")
                    status_badge(dev.get("trang_thai"))

                ui.separator().classes("my-2")
                ui.label(f"Lịch sử sự cố đã báo ({len(tickets)} tickets)").classes("text-xs font-bold text-slate-400 uppercase tracking-wider mb-2")

                if not tickets:
                    empty_state("Không có sự cố nào", "Thiết bị chưa từng có ticket báo lỗi.", "verified")
                else:
                    with ui.column().classes("w-full divide-y divide-slate-100 max-h-80 overflow-y-auto"):
                        for tck in tickets:
                            with ui.row().classes("w-full justify-between items-center py-2.5"):
                                with ui.column().classes("gap-0.5"):
                                    ui.label(f"#{tck.get('id')} · {tck.get('title', '-')}").classes("text-xs font-bold text-slate-800")
                                    ui.label(format_datetime(tck.get("created_at"))).classes("text-[10px] text-slate-400")
                                ui.button(
                                    "Mở ticket",
                                    icon="open_in_new",
                                    on_click=lambda tck_id=tck.get("id"): ui.navigate.to(f"/tickets/{tck_id}"),
                                ).props("flat dense size=xs color=primary")

                with ui.row().classes("w-full justify-end mt-4"):
                    ui.button("Đóng", on_click=dialog.close).props("flat color=primary")
            dialog.open()

        async def reload_devices() -> None:
            try:
                devices = await device_service.list_devices(
                    status=None if status.value == "ALL" else status.value,
                    keyword=keyword.value,
                    refresh=True,
                )
            except Exception as exc:
                device_container.clear()
                with device_container:
                    ui.label(f"Lỗi tải danh mục thiết bị: {exc}").classes("text-sm text-red-600")
                return

            device_container.clear()
            with device_container:
                with ui.card().classes("w-full p-0 rounded-xl bg-white border border-slate-200 shadow-sm overflow-hidden"):
                    with ui.row().classes("w-full justify-between items-center p-4 border-b border-slate-100"):
                        ui.label(f"Danh mục thiết bị ({len(devices)})").classes("text-sm font-bold text-slate-800")

                    with ui.column().classes("w-full divide-y divide-slate-100"):
                        for dev in devices:
                            with ui.row().classes("w-full justify-between items-center p-3.5 hover:bg-slate-50 transition-colors"):
                                # Code & Info
                                with ui.row().classes("items-center gap-3"):
                                    with ui.element("div").classes("w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 shrink-0"):
                                        ui.icon("devices").classes("text-lg")
                                    with ui.column().classes("gap-0"):
                                        with ui.row().classes("items-center gap-2"):
                                            ui.label(dev.get("ma_thiet_bi", "-")).classes("text-xs font-bold px-1.5 py-0.2 bg-slate-100 text-slate-800 rounded border border-slate-200")
                                            ui.label(dev.get("ten_thiet_bi", "-")).classes("text-sm font-bold text-slate-800")
                                        ui.label(f"Loại: {dev.get('loai_thiet_bi') or 'Khác'} · Vị trí: {dev.get('vi_tri') or 'Chưa rõ'}").classes("text-xs text-slate-400")

                                # Badges & Actions
                                with ui.row().classes("items-center gap-2"):
                                    status_badge(dev.get("trang_thai"))
                                    ui.button("Lịch sử sự cố", icon="history", on_click=lambda dev=dev: view_device_history(dev)).props("outline dense size=sm color=slate-700")

        def create_device_dialog() -> None:
            dialog = ui.dialog()
            with dialog, ui.card().classes("w-full max-w-md rounded-2xl p-6 bg-white gap-3"):
                ui.label("Thêm thiết bị mới").classes("text-lg font-bold text-slate-900")
                ui.label("Nhập thông số kỹ thuật của thiết bị để quản lý.").classes("text-xs text-slate-500 mb-1")

                code = ui.input("Mã thiết bị (VD: PC-010) *").props("outlined").classes("w-full")
                name = ui.input("Tên thiết bị (VD: Dell OptiPlex 7090) *").props("outlined").classes("w-full")
                device_type = ui.input("Loại thiết bị (COMPUTER, PRINTER...)").props("outlined").classes("w-full")
                location = ui.input("Vị trí đặt máy (Phòng Kế toán, Tầng 3...)").props("outlined").classes("w-full")
                device_status = ui.select([item.value for item in DeviceStatus], value="ACTIVE", label="Trạng thái").props("outlined").classes("w-full")
                description = ui.textarea("Mô tả / Ghi chú cấu hình").props("outlined").classes("w-full")

                async def submit() -> None:
                    if not (code.value or "").strip():
                        toast.warning("Vui lòng nhập Mã thiết bị.")
                        return
                    if not (name.value or "").strip():
                        toast.warning("Vui lòng nhập Tên thiết bị.")
                        return

                    try:
                        await device_service.create_device(
                            {
                                "ma_thiet_bi": code.value.strip(),
                                "ten_thiet_bi": name.value.strip(),
                                "loai_thiet_bi": device_type.value.strip() if device_type.value else None,
                                "vi_tri": location.value.strip() if location.value else None,
                                "trang_thai": device_status.value,
                                "mo_ta": description.value.strip() if description.value else None,
                            }
                        )
                        toast.success("Đã thêm thiết bị thành công.")
                        dialog.close()
                        await reload_devices()
                    except Exception as exc:
                        toast.error(str(exc))

                with ui.row().classes("w-full justify-end gap-2 mt-4 pt-3 border-t border-slate-100"):
                    ui.button("Hủy", on_click=dialog.close).props("flat color=slate-600")
                    ui.button("Thêm thiết bị", on_click=submit).props("color=primary unelevated")
            dialog.open()

        ui.timer(0.1, reload_devices, once=True)

    app_shell("Thiết bị", content)
