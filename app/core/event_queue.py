import asyncio
import json
import os
from typing import Any, Dict

from app.core.redis_client import redis_client


class EventQueue:
    """
    Redis-backed async event queue with in-memory fallback.
    """

    def __init__(self):
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self.redis_key = os.getenv("EVENT_QUEUE_KEY", "event_queue")
        self.use_redis = False

        if os.getenv("REDIS_URL"):
            try:
                redis_client.ping()
                self.use_redis = True
            except Exception:
                self.use_redis = False

    def _normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        payload = event.get("payload")
        if hasattr(payload, "model_dump"):
            event = dict(event)
            event["payload"] = payload.model_dump(mode="json")
        return event

    async def publish(self, event: Dict[str, Any]):
        normalized = self._normalize_event(event)

        if self.use_redis:
            await asyncio.to_thread(
                redis_client.lpush,
                self.redis_key,
                json.dumps(normalized),
            )
            return

        await self.queue.put(normalized)

    async def consume(self) -> Dict[str, Any]:
        if self.use_redis:
            while True:
                result = await asyncio.to_thread(
                    redis_client.brpop,
                    self.redis_key,
                    5,
                )
                if not result:
                    await asyncio.sleep(0)
                    continue
                _, raw = result
                return json.loads(raw)

        return await self.queue.get()


# Global singleton (safe for Phase-3A)
event_queue = EventQueue()
