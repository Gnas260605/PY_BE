from typing import Optional, Dict, Any
from nicegui import app
from core.constants import Role

class AuthContext:
    @staticmethod
    def get_token() -> Optional[str]:
        return app.storage.user.get("access_token")

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        return app.storage.user.get("current_user")

    @staticmethod
    def set_session(token: str, user: Dict[str, Any]):
        app.storage.user["access_token"] = token
        app.storage.user["current_user"] = user

    @staticmethod
    def clear_session():
        app.storage.user.pop("access_token", None)
        app.storage.user.pop("current_user", None)

    @staticmethod
    def is_authenticated() -> bool:
        return bool(AuthContext.get_token() and AuthContext.get_current_user())

    @staticmethod
    def get_role() -> Optional[str]:
        user = AuthContext.get_current_user()
        return user.get("vai_tro") if user else None

    @staticmethod
    def is_admin() -> bool:
        return AuthContext.get_role() == Role.ADMIN.value

    @staticmethod
    def is_technician() -> bool:
        return AuthContext.get_role() == Role.TECHNICIAN.value

    @staticmethod
    def is_user() -> bool:
        return AuthContext.get_role() == Role.USER.value

auth_context = AuthContext()
