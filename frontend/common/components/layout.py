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
    if not auth_service.is_authenticated():
        ui.navigate.to("/login")
        return None
    return auth_service.current_user()


def app_shell(title: str, content: Callable[[dict], None]) -> None:
    apply_theme()
    user = require_login()
    if not user:
        return

    role = user.get("vai_tro", "USER")
    navbar(title, user, logout_and_go_home)
    sidebar(role)
    bottom_nav(role)

    with ui.element("main").classes(RESPONSIVE_PAGE):
        content(user)
