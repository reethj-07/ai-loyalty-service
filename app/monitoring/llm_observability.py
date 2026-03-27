from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Deque, Dict, List


_llm_calls: Deque[Dict] = deque(maxlen=100)
_lock = Lock()


def record_llm_call(entry: Dict) -> None:
    with _lock:
        _llm_calls.appendleft(entry)


def get_recent_llm_calls(limit: int = 100) -> List[Dict]:
    with _lock:
        return list(_llm_calls)[:limit]
