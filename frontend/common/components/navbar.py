from collections.abc import Callable
from nicegui import ui


def navbar(
    title: str,
    user: dict,
    on_logout: Callable[[], None],
    on_toggle_sidebar: Callable[[], None] | None = None,
) -> None:
    initials = (user.get("ho_ten") or user.get("username") or "U")[:2].upper()
    display_name = user.get("ho_ten") or user.get("username")

    with ui.header().classes("bg-white text-slate-900 border-b border-slate-200 px-4 md:px-6 py-2.5 shadow-none sticky top-0 z-20"):
        with ui.row().classes("w-full items-center justify-between no-wrap"):
            # Left: Sidebar Toggle & Clean Title
            with ui.row().classes("items-center gap-3 no-wrap"):
                if on_toggle_sidebar:
                    ui.button(icon="menu", on_click=on_toggle_sidebar).props("flat round dense color=slate-700").classes("hover:bg-slate-100")
                ui.label(title).classes("text-base font-bold text-slate-900")

            # Right: Settings, User Avatar & Logout
            with ui.row().classes("items-center gap-2 md:gap-3 no-wrap"):
                
                # Notification button (cho Technician)
                if user.get("vai_tro") in ("TECHNICIAN", "ADMIN"):
                    with ui.button(icon="notifications").props("flat round dense color=slate-600").classes("hover:bg-slate-100 transition-colors"):
                        badge = ui.badge("", color="red").props("floating")
                        badge.set_visibility(False)
                        ui.tooltip("Thông báo")
                        with ui.menu().classes("w-80 p-0"):
                            notif_container = ui.column().classes("w-full gap-0")

                    async def load_notifications():
                        try:
                            from services.ticket_service import ticket_service
                            from common.formatters import format_datetime
                            
                            if user.get("vai_tro") == "TECHNICIAN":
                                tickets = await ticket_service.list_tickets(technician_id=user["id"], status="ASSIGNED", refresh=True)
                                title_text = "Phân công mới"
                                msg_text = "Bạn vừa được phân công xử lý Ticket này."
                                icon_name = "assignment_ind"
                            else:
                                tickets = await ticket_service.list_tickets(status="OPEN", refresh=True)
                                title_text = "Ticket mới"
                                msg_text = "Có yêu cầu hỗ trợ mới đang chờ tiếp nhận."
                                icon_name = "new_releases"

                            count = len(tickets)
                            if count > 0:
                                badge.set_text(str(count))
                                badge.set_visibility(True)
                            else:
                                badge.set_visibility(False)

                            notif_container.clear()
                            with notif_container:
                                with ui.row().classes("w-full items-center justify-between p-3 border-b border-slate-100"):
                                    ui.label("Thông báo").classes("text-sm font-bold text-slate-800")
                                    ui.label("Đánh dấu đã đọc").classes("text-xs text-primary cursor-pointer hover:underline")

                                if count == 0:
                                    ui.label("Bạn không có thông báo mới.").classes("p-4 text-sm text-slate-500 text-center w-full")
                                else:
                                    # Sort by updated_at desc and take top 5
                                    tickets = sorted(tickets, key=lambda x: x.get("updated_at", ""), reverse=True)[:5]
                                    for t in tickets:
                                        t_id = t["id"]
                                        with ui.menu_item(on_click=lambda t_id=t_id: ui.navigate.to(f"/tickets/{t_id}/history")).classes("p-3 border-b border-slate-50 hover:bg-slate-50 transition-colors cursor-pointer w-full"):
                                            with ui.row().classes("items-start gap-3 no-wrap w-full"):
                                                with ui.avatar(color="blue-100", text_color="blue-600").props("size=32px"):
                                                    ui.icon(icon_name).classes("text-sm")
                                                with ui.column().classes("gap-0 w-full"):
                                                    ui.label(f"{title_text} #{t_id}").classes("text-sm font-bold text-slate-700")
                                                    ui.label(msg_text).classes("text-xs text-slate-500")
                                                    ui.label(format_datetime(t.get("updated_at"))).classes("text-[10px] text-slate-400 mt-1")
                        except Exception as e:
                            print(f"Error loading notifications: {e}")

                    ui.timer(0.5, load_notifications, once=True)

                # Settings button
                with ui.button(icon="settings", on_click=lambda: ui.navigate.to("/settings")).props("flat round dense size=sm color=slate-600").classes("hover:bg-slate-100 transition-colors"):
                    ui.tooltip("Cài đặt & Ngôn ngữ")

                # User Chip
                with ui.row().classes("items-center gap-2 py-1 px-2.5 bg-slate-50 border border-slate-200 rounded-full cursor-pointer hover:bg-slate-100 transition-colors").on("click", lambda: ui.navigate.to("/settings")):
                    with ui.avatar(color="primary", text_color="white").props("size=26px font-size=11px").classes("font-bold"):
                        ui.label(initials)
                    ui.label(display_name).classes("text-xs font-semibold text-slate-700 hidden sm:block")

                # Logout button
                with ui.button(icon="logout", on_click=on_logout).props("flat round dense size=sm color=slate-500").classes("hover:bg-red-50 hover:text-red-600 transition-colors"):
                    ui.tooltip("Đăng xuất")
