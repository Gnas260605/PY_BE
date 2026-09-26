import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.security import decode_access_token
from app.core.websocket import manager

from app.auth.routes import router as auth_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.devices.routes import router as devices_router
from app.health.routes import router as health_router
from app.reports.routes import router as reports_router
from app.tickets.routes import router as tickets_router
from app.users.routes import router as users_router


settings = get_settings()
configure_logging(settings.log_level, settings.log_to_file, settings.log_file)

app = FastAPI(title=settings.app_name)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(tickets_router, prefix="/api", tags=["tickets"])
app.include_router(devices_router, prefix="/api", tags=["devices"])
app.include_router(reports_router, prefix="/api", tags=["reports"])

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.websocket("/api/ws/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

