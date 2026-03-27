import asyncio
from app.core.event_bus import event_bus
from app.workers.behavior_worker import process_event


async def background_event_consumer():
    while True:
        event = await event_bus.consume()
        try:
            await process_event(event)
        except Exception as e:
            print(f"[Worker Error] {e}")
