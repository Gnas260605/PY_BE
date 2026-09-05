from nicegui import ui

from core.config import config
from views.admin.device_mgmt_view import render_device_mgmt_view
from views.admin.ticket_dispatch_view import render_ticket_dispatch_view
from views.admin.user_mgmt_view import render_user_mgmt_view
from views.auth.login_view import render_login_view
from views.dashboard_view import render_dashboard_view
from views.technician.device_lookup_view import render_device_lookup_view
from views.technician.task_board_view import render_task_board_view
from views.user.create_ticket_view import render_create_ticket_view
from views.user.my_tickets_view import render_my_tickets_view
from views.user.ticket_timeline_view import render_ticket_timeline_view


@ui.page("/")
@ui.page("/login")
def login_page() -> None:
    render_login_view()


@ui.page("/dashboard")
def dashboard_page() -> None:
    render_dashboard_view()


@ui.page("/admin/users")
def admin_users_page() -> None:
    render_user_mgmt_view()


@ui.page("/admin/devices")
def admin_devices_page() -> None:
    render_device_mgmt_view()


@ui.page("/admin/tickets")
def admin_tickets_page() -> None:
    render_ticket_dispatch_view()


@ui.page("/technician/tasks")
def technician_tasks_page() -> None:
    render_task_board_view()


@ui.page("/technician/devices")
def technician_devices_page() -> None:
    render_device_lookup_view()


@ui.page("/user/tickets")
def user_tickets_page() -> None:
    render_my_tickets_view()


@ui.page("/user/tickets/new")
def create_ticket_page() -> None:
    render_create_ticket_view()


@ui.page("/tickets/{ticket_id}/history")
def ticket_history_page(ticket_id: int) -> None:
    render_ticket_timeline_view(ticket_id)


ui.run(
    title=config.APP_TITLE,
    host=config.HOST,
    port=config.PORT,
    reload=False,
    storage_secret=config.STORAGE_SECRET,
)
