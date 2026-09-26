import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps user_id -> List of active WebSockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info("WEBSOCKET_CONNECTED user_id=%s", user_id)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info("WEBSOCKET_DISCONNECTED user_id=%s", user_id)

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            # Create a list of failed connections to remove later
            failed_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as exc:
                    logger.error(
                        "WEBSOCKET_SEND_FAILED user_id=%s error_type=%s",
                        user_id,
                        type(exc).__name__,
                    )
                    failed_connections.append(connection)
            
            for failed in failed_connections:
                self.disconnect(failed, user_id)

    async def broadcast(self, message: dict):
        for user_id, connections in list(self.active_connections.items()):
            failed_connections = []
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as exc:
                    logger.error(
                        "WEBSOCKET_BROADCAST_FAILED user_id=%s error_type=%s",
                        user_id,
                        type(exc).__name__,
                    )
                    failed_connections.append(connection)
                    
            for failed in failed_connections:
                self.disconnect(failed, user_id)

manager = ConnectionManager()
