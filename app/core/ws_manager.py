from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket connections per tenant/user.
    Broadcasts events to all connected clients or targeted ones.
    """

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        self.active_connections[channel].append(websocket)

    async def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)
        if channel in self.active_connections and not self.active_connections[channel]:
            del self.active_connections[channel]

    async def broadcast(self, channel: str, message: dict):
        stale = []
        for websocket in self.active_connections.get(channel, []):
            try:
                await websocket.send_json(message)
            except Exception:
                stale.append(websocket)

        for websocket in stale:
            await self.disconnect(websocket, channel)

    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)


manager = ConnectionManager()
