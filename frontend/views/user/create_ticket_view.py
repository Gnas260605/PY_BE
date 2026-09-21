from nicegui import ui

from common.components import toast
from common.components.layout import app_shell
from core.constants import CATEGORY_LABELS, PRIORITY_LABELS, TicketCategory, TicketPriority
from services.device_service import device_service
from services.ticket_service import ticket_service


def render_create_ticket_view() -> None:
    def content(user: dict) -> None:
        if user.get("vai_tro") == "TECHNICIAN":
            ui.label("Kỹ thuật viên không có quyền tạo ticket theo quy trình hệ thống.").classes("text-red-600")
            return

        # Header
        with ui.row().classes("w-full justify-between items-center mb-6"):
            with ui.column().classes("gap-0.5"):
                ui.label("Tạo yêu cầu hỗ trợ IT").classes("text-2xl font-bold text-slate-900")
                ui.label("Điền thông tin sự cố để đội ngũ Kỹ thuật viên tiếp nhận và xử lý nhanh chóng.").classes("text-xs text-slate-500")

        with ui.card().classes("w-full max-w-2xl mx-auto p-6 rounded-2xl bg-white border border-slate-200 shadow-sm gap-4"):
            # Section 1: Issue Info
            ui.label("1. THÔNG TIN SỰ CỐ").classes("text-xs font-bold text-slate-400 tracking-wider uppercase")
            title = ui.input("Tiêu đề sự cố", placeholder="Ví dụ: Máy in phòng Kế toán bị kẹt giấy liên tục").props("outlined").classes("w-full")

            with ui.row().classes("w-full gap-4"):
                category = ui.select(
                    {item.value: CATEGORY_LABELS.get(item.value, item.value) for item in TicketCategory},
                    value="INCIDENT",
                    label="Phân loại yêu cầu",
                ).props("outlined").classes("flex-1")

                priority = ui.select(
                    {item.value: PRIORITY_LABELS.get(item.value, item.value) for item in TicketPriority},
                    value="MEDIUM",
                    label="Mức độ ưu tiên",
                ).props("outlined").classes("flex-1")

            # Section 2: Device Association
            ui.label("2. THIẾT BỊ LIÊN QUAN").classes("text-xs font-bold text-slate-400 tracking-wider uppercase mt-2")
            device = ui.select({}, label="Chọn thiết bị gặp sự cố (tùy chọn)").props("outlined clearable use-input").classes("w-full")

            # Section 3: Description
            ui.label("3. MÔ TẢ CHI TIẾT").classes("text-xs font-bold text-slate-400 tracking-wider uppercase mt-2")
            description = ui.textarea(
                "Mô tả hiện tượng và các bước tái hiện lỗi...",
                placeholder="- Hiện tượng xảy ra khi nào?\n- Có thông báo lỗi nào xuất hiện không?\n- Đã thử khởi động lại máy chưa?",
            ).props("outlined rows=4").classes("w-full")

            async def load_devices() -> None:
                try:
                    devices = await device_service.list_devices()
                    device.options = {d["id"]: f"{d.get('ma_thiet_bi')} · {d.get('ten_thiet_bi')} ({d.get('vi_tri') or 'Không rõ vị trí'})" for d in devices}
                    device.update()
                except Exception:
                    device.options = {}

            async def submit() -> None:
                if not (title.value or "").strip():
                    toast.warning("Vui lòng nhập tiêu đề sự cố.")
                    return
                if not (description.value or "").strip():
                    toast.warning("Vui lòng nhập mô tả chi tiết.")
                    return

                try:
                    submit_btn.props("loading")
                    toast.info("Đang khởi tạo yêu cầu hỗ trợ...")
                    res = await ticket_service.create_ticket(
                        {
                            "title": title.value.strip(),
                            "description": description.value.strip(),
                            "device_id": int(device.value) if device.value else None,
                            "category": category.value,
                            "priority": priority.value,
                        }
                    )
                    new_ticket_id = res.get("id")
                    toast.success(f"Tạo yêu cầu #{new_ticket_id} thành công!")
                    toast.show_popup(
                        title="Gửi yêu cầu hỗ trợ thành công!",
                        message=f"Yêu cầu sự cố của bạn đã được tạo thành công với mã #{new_ticket_id}. Kỹ thuật viên sẽ tiếp nhận và xử lý trong thời gian sớm nhất.",
                        type="success",
                        confirm_text="Xem chi tiết & Chat",
                        on_confirm=lambda: ui.navigate.to(f"/tickets/{new_ticket_id}") if new_ticket_id else ui.navigate.to("/user/tickets"),
                    )
                except Exception as exc:
                    toast.show_popup(
                        title="Không thể gửi yêu cầu",
                        message="Đã có lỗi xảy ra trong quá trình tạo ticket.",
                        type="error",
                        detail=str(exc),
                    )
                finally:
                    submit_btn.props(remove="loading")

            with ui.row().classes("w-full justify-end gap-3 mt-4 pt-4 border-t border-slate-100"):
                ui.button("Hủy", on_click=lambda: ui.navigate.to("/user/tickets")).props("flat color=slate-600")
                submit_btn = ui.button("Gửi yêu cầu hỗ trợ", icon="send", on_click=submit).props("color=primary unelevated").classes("px-5 py-2")

        ui.timer(0.1, load_devices, once=True)

    app_shell("Tạo yêu cầu hỗ trợ", content)
