import asyncio
from typing import Any

class EventBus:
    """
    Async event queue (replaceable with Redis/Kafka later)
    """
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()

    async def publish(self, event: Any):
        await self.queue.put(event)

    async def consume(self):
        return await self.queue.get()


# Global singleton
event_bus = EventBus()
