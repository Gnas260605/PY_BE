from __future__ import annotations

from typing import Any
from nicegui import ui

from common.components import toast
from common.components.empty_state import empty_state
from common.components.layout import app_shell
from common.components.status_badge import priority_badge, status_badge
from common.formatters import format_datetime
from services.device_service import device_service


def render_device_lookup_view() -> None:
    def content(user: dict) -> None:
        # Header
        with ui.row().classes("w-full justify-between items-center mb-4"):
            with ui.column().classes("gap-0.5"):
                ui.label("Tra cứu thiết bị & Lịch sử sửa chữa").classes("text-2xl font-bold text-slate-900")
                ui.label("Tìm kiếm thiết bị và theo dõi các sự cố đã từng xảy ra trên thiết bị đó.").classes("text-xs text-slate-500")

        # Search Bar & Device Picker
        with ui.card().classes("w-full p-4 rounded-xl bg-white border border-slate-200 shadow-sm"):
            with ui.row().classes("w-full gap-3 items-end"):
                device_select = ui.select({}, label="Chọn thiết bị cần tra cứu").props("outlined use-input").classes("flex-1 min-w-[280px]")
                ui.button("Tra cứu", icon="search", on_click=lambda: on_device_selected()).props("color=primary unelevated").classes("py-2.5 px-4")

        # Result Container
        result_container = ui.column().classes("w-full gap-4 mt-4")

        async def load_all_devices() -> None:
            try:
                devices = await device_service.list_devices()
                device_select.options = {d["id"]: f"{d.get('ma_thiet_bi')} · {d.get('ten_thiet_bi')} ({d.get('vi_tri') or 'Không rõ vị trí'})" for d in devices}
                device_select.update()
                if devices:
                    device_select.set_value(devices[0]["id"])
                    await on_device_selected()
            except Exception as exc:
                toast.error(f"Lỗi tải danh mục thiết bị: {exc}")

        async def on_device_selected() -> None:
            if not device_select.value:
                toast.warning("Vui lòng chọn một thiết bị.")
                return

            dev_id = int(device_select.value)
            try:
                device_info = await device_service.get_device(dev_id)
                tickets = await device_service.get_device_tickets(dev_id)
            except Exception as exc:
                result_container.clear()
                with result_container:
                    ui.label(f"Lỗi tra cứu: {exc}").classes("text-sm text-red-600")
                return

            result_container.clear()
            with result_container:
                # Device Specs Card
                with ui.card().classes("w-full p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
                    with ui.row().classes("w-full justify-between items-start"):
                        with ui.column().classes("gap-1"):
                            with ui.row().classes("items-center gap-2"):
                                ui.label(device_info.get("ten_thiet_bi", "-")).classes("text-lg font-bold text-slate-900")
                                status_badge(device_info.get("trang_thai"))
                            ui.label(f"Mã thiết bị: {device_info.get('ma_thiet_bi', '-')}").classes("text-xs font-semibold text-blue-600")
                        with ui.column().classes("items-end gap-0.5 text-xs text-slate-500"):
                            ui.label(f"Loại: {device_info.get('loai_thiet_bi') or 'Khác'}")
                            ui.label(f"Vị trí: {device_info.get('vi_tri') or 'Chưa cấu hình'}")

                    if device_info.get("mo_ta"):
                        ui.separator().classes("my-3")
                        ui.label("Ghi chú thiết bị:").classes("text-xs font-bold text-slate-400 uppercase tracking-wider mb-0.5")
                        ui.label(device_info["mo_ta"]).classes("text-xs text-slate-600")

                # Associated Tickets Card
                with ui.card().classes("w-full p-5 rounded-xl bg-white border border-slate-200 shadow-sm"):
                    with ui.row().classes("w-full justify-between items-center mb-3"):
                        ui.label("Lịch sử sự cố & Yêu cầu trên thiết bị này").classes("text-sm font-bold text-slate-900")
                        ui.label(f"Tổng: {len(tickets)} tickets").classes("text-xs font-semibold text-slate-400")

                    if not tickets:
                        empty_state(
                            title="Chưa có sự cố nào trên thiết bị này",
                            subtitle="Thiết bị đang hoạt động ổn định và chưa từng có báo hỏng.",
                            icon="check_circle",
                        )
                    else:
                        with ui.column().classes("w-full divide-y divide-slate-100"):
                            for tck in tickets:
                                tck_id = tck.get("id")
                                with ui.row().classes("w-full justify-between items-center py-3 hover:bg-slate-50 px-2 rounded-lg transition-colors"):
                                    with ui.column().classes("gap-1 flex-1"):
                                        with ui.row().classes("items-center gap-2"):
                                            ui.label(f"#{tck_id}").classes("text-xs font-bold text-blue-600")
                                            ui.label(tck.get("title", "-")).classes("text-sm font-bold text-slate-800")
                                        ui.label(f"Cập nhật lúc: {format_datetime(tck.get('updated_at'))}").classes("text-[11px] text-slate-400")

                                    with ui.row().classes("items-center gap-2 shrink-0"):
                                        priority_badge(tck.get("priority"))
                                        status_badge(tck.get("status"))
                                        ui.button(
                                            "Xem chi tiết",
                                            icon="arrow_forward",
                                            on_click=lambda tck_id=tck_id: ui.navigate.to(f"/tickets/{tck_id}"),
                                        ).props("flat dense size=sm color=primary")

        ui.timer(0.1, load_all_devices, once=True)

    app_shell("Tra cứu thiết bị", content)
