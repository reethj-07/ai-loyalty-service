import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.monitoring.repository import campaign_kpi_repo

router = APIRouter(prefix="/stream", tags=["streaming"])


@router.get("/dashboard")
async def stream_dashboard():
    async def generator():
        last_state = {}

        while True:
            await asyncio.sleep(1)

            for kpi in campaign_kpi_repo.all_active():
                payload = kpi.to_json()
                cid = kpi.campaign_id

                if last_state.get(cid) != payload:
                    last_state[cid] = payload
                    yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
