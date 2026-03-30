"""
Real-time Update Endpoints
Provides Server-Sent Events (SSE) and channel-based WebSocket streams.
"""
import asyncio
import json
import os
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from app.core.auth import auth_service
from app.core.ws_manager import manager

router = APIRouter(tags=["realtime"])

ALLOWED_CHANNELS = {"proposals", "transactions", "alerts"}


# ============================================
# SERVER-SENT EVENTS (SSE)
# ============================================

async def transaction_event_generator():
    """
    Generator function that yields Server-Sent Events
    Simulates real-time transaction updates
    """
    from app.repositories.supabase_transactions_repo import transactions_repo

    last_count = 0

    while True:
        try:
            # Get current transaction count
            transactions = await transactions_repo.get_all_transactions(limit=1)
            current_count = len(transactions) if transactions else 0

            # If new transactions detected, send update
            if current_count != last_count:
                last_count = current_count

                # Send transaction event
                if transactions:
                    txn = transactions[0]
                    event_data = {
                        "type": "transaction_created",
                        "data": {
                            "id": txn.get("id"),
                            "amount": txn.get("amount"),
                            "member_id": txn.get("member_id"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    }

                    yield f"data: {json.dumps(event_data)}\n\n"

            # Heartbeat every 30 seconds
            heartbeat = {
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(heartbeat)}\n\n"

            # Wait before next check
            await asyncio.sleep(5)  # Check every 5 seconds

        except Exception as e:
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            await asyncio.sleep(5)


@router.get("/transactions")
async def stream_transactions():
    """
    Server-Sent Events endpoint for real-time transaction updates

    Usage (JavaScript):
    ```javascript
    const eventSource = new EventSource('/api/v1/realtime/transactions');
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('New transaction:', data);
    };
    ```
    """
    return StreamingResponse(
        transaction_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


# ============================================
# WEBSOCKETS
# ============================================

@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    """
    Channels:
      - "proposals"     → new AI campaign proposals
      - "transactions"  → live transaction events
      - "alerts"        → behavioral detection alerts
      - "kpis/{id}"     → live campaign KPI updates
    """
    if channel not in ALLOWED_CHANNELS and not channel.startswith("kpis"):
        await websocket.close(code=1008, reason="Invalid channel")
        return

    auth_header = websocket.headers.get("authorization", "")
    bearer_token = auth_header.replace("Bearer ", "", 1).strip() if auth_header.startswith("Bearer ") else ""
    cookie_token = websocket.cookies.get("access_token", "").strip()
    allow_query_token = os.getenv("ALLOW_QUERY_ACCESS_TOKEN", "false").lower() == "true"
    query_token = websocket.query_params.get("access_token", "").strip() if allow_query_token else ""
    token = bearer_token or cookie_token or query_token

    if not token:
        await websocket.close(code=4401, reason="Unauthorized")
        return

    try:
        user = await auth_service.get_current_user(token)
    except Exception:
        await websocket.close(code=4401, reason="Unauthorized")
        return

    await manager.connect(websocket, channel)

    try:
        await manager.send_personal(
            websocket,
            {
            "type": "connected",
            "channel": channel,
            "user_id": user.get("id"),
            "message": "WebSocket connected successfully",
            "timestamp": datetime.now().isoformat()
            },
        )

        while True:
            await manager.send_personal(
                websocket,
                {
                "type": "heartbeat",
                "channel": channel,
                "timestamp": datetime.now().isoformat()
                },
            )
            await asyncio.sleep(3)

    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel)
    except Exception:
        await manager.disconnect(websocket, channel)


async def broadcast_to_all(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    for channel in list(manager.active_connections.keys()):
        await manager.broadcast(channel, message)


@router.get("/ws/status")
def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": sum(len(items) for items in manager.active_connections.values()),
        "channels": {key: len(value) for key, value in manager.active_connections.items()},
        "status": "operational"
    }
