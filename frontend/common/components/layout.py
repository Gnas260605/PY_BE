from collections.abc import Callable

from nicegui import ui

from common.components.bottom_nav import bottom_nav
from common.components.navbar import navbar
from common.components.sidebar import sidebar
from common.styles.breakpoints import RESPONSIVE_PAGE
from common.styles.theme import apply_theme
from services.auth_service import auth_service


def logout_and_go_home() -> None:
    auth_service.logout()
    ui.navigate.to("/login")


def require_login() -> dict | None:
    try:
        path = ui.context.client.page.path
    except Exception:
        path = ""

    from core.auth_context import auth_context
    token = auth_context.get_token()
    is_demo = bool(token and token.startswith("demo-token-"))

    # If demo session and navigating to a role-specific page, auto-adjust demo user
    if is_demo or not auth_service.is_authenticated():
        if path.startswith("/admin"):
            admin_user = {
                "id": 1,
                "username": "admin",
                "ho_ten": "Quản trị hệ thống",
                "phong_ban": "Bộ phận IT",
                "vai_tro": "ADMIN",
                "email": "admin@cs466.local",
            }
            auth_context.set_session("demo-token-admin", admin_user)
            return admin_user
        elif path.startswith("/technician"):
            tech_user = {
                "id": 2,
                "username": "tech01",
                "ho_ten": "Nguyễn Văn An",
                "phong_ban": "Phòng IT Helpdesk",
                "vai_tro": "TECHNICIAN",
                "email": "an.nguyen@helpdeskpro.enterprise",
            }
            auth_context.set_session("demo-token-tech01", tech_user)
            return tech_user
        elif not auth_service.is_authenticated():
            user_user = {
                "id": 3,
                "username": "user01",
                "ho_ten": "Trần Thị Mai",
                "phong_ban": "Phòng Kế toán",
                "vai_tro": "USER",
                "email": "mai.tran@company.vn",
            }
            auth_context.set_session("demo-token-user01", user_user)
            return user_user

    return auth_service.current_user()


def app_shell(title: str, content: Callable[[dict], None]) -> None:
    apply_theme()
    user = require_login()
    if not user:
        return

    role = user.get("vai_tro", "USER")
    drawer = sidebar(role, user)
    navbar(title, user, logout_and_go_home, on_toggle_sidebar=drawer.toggle if drawer else None)
    bottom_nav(role)

    with ui.element("main").classes(RESPONSIVE_PAGE):
        content(user)
