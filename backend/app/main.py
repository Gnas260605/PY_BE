from fastapi import FastAPI

from app.auth.routes import router as auth_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.devices.routes import router as devices_router
from app.health.routes import router as health_router
from app.tickets.routes import router as tickets_router
from app.users.routes import router as users_router


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
register_exception_handlers(app)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(tickets_router, prefix="/api", tags=["tickets"])
app.include_router(devices_router, prefix="/api", tags=["devices"])
