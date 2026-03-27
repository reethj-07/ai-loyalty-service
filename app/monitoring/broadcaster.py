import asyncio
from typing import Dict, Any, List


class DashboardBroadcaster:
    """
    Async pub-sub broadcaster for SSE dashboards.
    """

    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []

    async def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def publish(self, event: Dict[str, Any]):
        """
        Push event to all connected dashboards.
        """
        for queue in list(self._subscribers):
            await queue.put(event)


# ✅ Singleton broadcaster instance
dashboard_broadcaster = DashboardBroadcaster()
