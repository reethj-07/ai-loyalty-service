import json
from fastapi import Request
from fastapi.responses import StreamingResponse

from app.monitoring.broadcaster import dashboard_broadcaster


async def dashboard_event_stream(request: Request):
    queue = await dashboard_broadcaster.subscribe()

    try:
        while True:
            if await request.is_disconnected():
                break

            data = await queue.get()
            yield f"data: {json.dumps(data)}\n\n"

    finally:
        dashboard_broadcaster.unsubscribe(queue)


def sse_response(request: Request):
    return StreamingResponse(
        dashboard_event_stream(request),
        media_type="text/event-stream",
    )
