from nicegui import ui

from common.components.layout import app_shell
from common.components.stat_card import stat_card
from common.styles.breakpoints import RESPONSIVE_GRID
from core.http_client import ApiException
from services.device_service import device_service
from services.ticket_service import ticket_service
from services.user_service import user_service


def render_dashboard_view() -> None:
    def content(user: dict) -> None:
        role = user.get("vai_tro", "USER")
        ui.label(f"Xin chào, {user.get('ho_ten') or user.get('username')}").classes("text-3xl font-bold text-slate-900")
        ui.label("Tổng quan nhanh theo đúng quyền truy cập hiện tại.").classes("text-sm text-slate-500 mb-4")

        cards = ui.element("div").classes(RESPONSIVE_GRID)
        activity = ui.card().classes("w-full mt-6 p-5 rounded-2xl shadow-sm border border-slate-100")

        async def reload() -> None:
            try:
                tickets = await ticket_service.list_tickets(refresh=True)
                devices = []
                users = []
                if role in ("ADMIN", "TECHNICIAN"):
                    devices = await device_service.list_devices(refresh=True)
                if role == "ADMIN":
                    users = await user_service.list_users(refresh=True)

                open_count = len([ticket for ticket in tickets if ticket.get("status") in ("OPEN", "ASSIGNED", "IN_PROGRESS")])
                resolved_count = len([ticket for ticket in tickets if ticket.get("status") in ("RESOLVED", "CLOSED")])

                cards.clear()
                with cards:
                    stat_card("Tổng tickets", len(tickets), "Theo RBAC backend", "confirmation_number")
                    stat_card("Đang xử lý", open_count, "OPEN/ASSIGNED/IN_PROGRESS", "pending_actions")
                    stat_card("Đã hoàn tất", resolved_count, "RESOLVED/CLOSED", "verified")
                    if role in ("ADMIN", "TECHNICIAN"):
                        stat_card("Thiết bị", len(devices), "Danh mục được phép xem", "devices")
                    if role == "ADMIN":
                        stat_card("Người dùng", len(users), "Tài khoản hệ thống", "groups")

                activity.clear()
                with activity:
                    ui.label("Gợi ý thao tác").classes("text-lg font-bold")
                    if role == "ADMIN":
                        ui.label("Quản lý users/devices, phân công kỹ thuật viên, theo dõi toàn bộ ticket.")
                    elif role == "TECHNICIAN":
                        ui.label("Xem ticket được giao/chung, cập nhật tiến độ và tra cứu thiết bị.")
                    else:
                        ui.label("Tạo ticket hỗ trợ mới và theo dõi tiến độ xử lý của ticket của bạn.")
            except ApiException as exc:
                cards.clear()
                with cards:
                    stat_card("Backend", "!", exc.message, "cloud_off")

        ui.button("Tải lại dữ liệu", on_click=reload).props("outline color=primary").classes("mt-4")
        ui.timer(0.1, reload, once=True)

    app_shell("Dashboard", content)
