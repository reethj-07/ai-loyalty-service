from typing import Dict
from app.schemas.segments import SegmentState


class SegmentRepository:
    """
    In-memory store for current segment snapshots
    """

    def __init__(self):
        self._store: Dict[str, SegmentState] = {}

    def replace(self, segments: Dict[str, SegmentState]):
        """
        Replace entire segment state atomically
        """
        self._store = segments

    def get_all(self) -> Dict[str, SegmentState]:
        return self._store
