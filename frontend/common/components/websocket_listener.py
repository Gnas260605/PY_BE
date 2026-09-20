import asyncio
import json
import logging
import websockets
from nicegui import app, ui
from core.auth_context import auth_context
from core.config import config
from common.components import toast

logger = logging.getLogger(__name__)

class NotificationListener:
    def __init__(self):
        self.task = None

    def start(self):
        token = auth_context.get_token()
        if not token:
            return
            
        base_ws = config.API_BASE_URL.replace('http', 'ws').replace('/api', '')
        ws_url = f"{base_ws}/api/ws/notifications?token={token}"
        
        # Start listener task
        self.task = asyncio.create_task(self._listen(ws_url))
        
        # Stop on disconnect
        app.on_disconnect(self.stop)
        
    def stop(self):
        if self.task and not self.task.done():
            self.task.cancel()
            self.task = None
            
    async def _listen(self, ws_url: str):
        try:
            async with websockets.connect(ws_url) as ws:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    # Trigger toast directly, nicegui handles context since this task was created from a UI request
                    toast.info(data.get("message", "Có thông báo mới!"))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")

def setup_websocket():
    """Call this in layout.py to initialize websocket listener for the current user."""
    listener = NotificationListener()
    # Use timer to wait for full page load
    ui.timer(0.5, listener.start, once=True)
