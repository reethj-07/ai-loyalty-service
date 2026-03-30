import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app


def test_websocket_rejects_unauthenticated_connections():
    client = TestClient(app)

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/api/v1/realtime/ws/transactions"):
            pass

    assert exc.value.code == 4401


def test_websocket_accepts_valid_bearer_token(monkeypatch):
    client = TestClient(app)

    async def _fake_get_current_user(token: str) -> dict:
        assert token == "valid-token"
        return {"id": "user-123", "email": "user@example.com", "role": "authenticated"}

    monkeypatch.setattr("app.api.v1.realtime.auth_service.get_current_user", _fake_get_current_user)

    with client.websocket_connect(
        "/api/v1/realtime/ws/transactions",
        headers={"Authorization": "Bearer valid-token"},
    ) as ws:
        connected = ws.receive_json()

    assert connected["type"] == "connected"
    assert connected["channel"] == "transactions"
    assert connected["user_id"] == "user-123"
