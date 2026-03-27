import uuid
from typing import Dict, List


class ReviewRepository:
    """
    In-memory store for pending campaign approvals
    (Replace with DB later)
    """

    def __init__(self):
        self._pending: Dict[str, Dict] = {}

    def create(self, proposal: Dict) -> str:
        review_id = str(uuid.uuid4())
        self._pending[review_id] = {
            "id": review_id,
            "status": "pending",
            "proposal": proposal,
        }
        return review_id

    def list_pending(self) -> List[Dict]:
        return list(self._pending.values())

    def approve(self, review_id: str) -> Dict:
        self._pending[review_id]["status"] = "approved"
        return self._pending[review_id]

    def modify(self, review_id: str, updates: Dict) -> Dict:
        self._pending[review_id]["proposal"].update(updates)
        self._pending[review_id]["status"] = "modified"
        return self._pending[review_id]
