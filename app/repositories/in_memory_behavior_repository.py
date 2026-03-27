from typing import Dict
from app.repositories.behavior_repository import BehaviorRepository


class InMemoryBehaviorRepository(BehaviorRepository):
    """
    Phase-2A: In-memory behavior store
    (Later replace with Redis / DB)
    """

    def __init__(self):
        self._events = {}
        self._states = {}

    def get_behavior_state(self, member_id: str) -> Dict:
        return self._states.get(member_id, {})

    def save_behavior_state(self, member_id: str, state: Dict):
        self._states[member_id] = state
        print(f"[DB] Saved behavior state for member={member_id}")

    def store_event(self, member_id: str, event: Dict):
        self._events.setdefault(member_id, []).append(event)
        print(f"[DB] Stored event for member={member_id}: {event}")
