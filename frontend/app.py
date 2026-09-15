from nicegui import ui

from core.config import config
from views.admin.device_mgmt_view import render_device_mgmt_view
from views.admin.operations_view import render_admin_operations_view
from views.admin.ticket_dispatch_view import render_ticket_dispatch_view
from views.admin.user_mgmt_view import render_user_mgmt_view
from views.auth.login_view import render_login_view
from views.dashboard_view import render_dashboard_view
from views.technician.device_lookup_view import render_device_lookup_view
from views.technician.task_board_view import render_task_board_view
from views.technician.ticket_queue_view import render_ticket_queue_view
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
@ui.page("/admin/sla")
@ui.page("/technician/sla")
def ticket_dispatch_page() -> None:
    render_ticket_dispatch_view()


@ui.page("/admin/settings")
@ui.page("/technician/settings")
def system_settings_page() -> None:
    render_admin_operations_view()


@ui.page("/technician/tasks")
@ui.page("/technician/queue")
def technician_tasks_page() -> None:
    render_ticket_queue_view()


@ui.page("/technician/detail")
def technician_detail_default_page() -> None:
    render_task_board_view(1048)


@ui.page("/technician/detail/{ticket_id}")
def technician_detail_page(ticket_id: int) -> None:
    render_task_board_view(ticket_id)


@ui.page("/technician/devices")
def technician_devices_page() -> None:
    render_device_lookup_view()


@ui.page("/user/tickets")
def user_tickets_page() -> None:
    render_my_tickets_view()


@ui.page("/user/tickets/new")
def create_ticket_page() -> None:
    render_create_ticket_view()


@ui.page("/admin")
def admin_home() -> None:
    render_admin_operations_view()


@ui.page("/technician")
def tech_home() -> None:
    ui.navigate.to("/technician/tasks")


@ui.page("/logout")
def logout_page() -> None:
    from services.auth_service import auth_service
    auth_service.logout()
    ui.navigate.to("/login")


@ui.page("/create-ticket")
def create_ticket_alias() -> None:
    render_create_ticket_view()


@ui.page("/my-tickets")
def my_tickets_alias() -> None:
    render_my_tickets_view()


@ui.page("/user/tickets/{ticket_id}")
@ui.page("/tickets/{ticket_id}/history")
def ticket_detail_page(ticket_id: int) -> None:
    render_ticket_timeline_view(ticket_id)


ui.run(
    title=config.APP_TITLE,
    host=config.HOST,
    port=config.PORT,
    reload=False,
    storage_secret=config.STORAGE_SECRET,
)
