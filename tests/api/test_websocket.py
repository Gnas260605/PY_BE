from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.core.websocket import manager


def test_ws_01_connection_invalid_token(client: TestClient):
    """WS-01: WebSocket connection with invalid or missing token closes with 1008."""
    # 1. Missing token
    with pytest.raises(Exception):
        with client.websocket_connect("/api/ws/notifications"):
            pass

    # 2. Invalid token
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/ws/notifications?token=invalid.jwt.token"):
            pass
    assert exc_info.value.code == 1008


def test_ws_01_connection_valid_token(client: TestClient, admin_token: str):
    """WS-01: WebSocket connection with valid token succeeds and can receive notifications."""
    with client.websocket_connect(f"/api/ws/notifications?token={admin_token}") as websocket:
        # Send a personal notification to user_id=1 (admin)
        import anyio
        async def send_msg():
            await manager.send_personal_message({"type": "TEST_EVENT", "data": "hello"}, 1)
        anyio.run(send_msg)

        data = websocket.receive_json()
        assert data["type"] == "TEST_EVENT"
        assert data["data"] == "hello"
