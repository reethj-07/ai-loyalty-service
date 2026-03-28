from typing import List, Dict, Any
from app.schemas.events import TransactionEvent
from app.repositories.in_memory_behavior_repository import InMemoryBehaviorRepository


class BehaviorDetectorService:
    """
    Phase-2A Behavior Detection Engine
    """

    def __init__(self):
        self.repo = InMemoryBehaviorRepository()

    def detect(self, event: TransactionEvent) -> List[Dict[str, Any]]:
        signals = []

        # ---- Rule 1: High value transaction ----
        if event.amount >= 500:
            signals.append({
                "type": "high_value_transaction",
                "reason": f"Transaction amount {event.amount} exceeds threshold",
                "confidence": 0.7,
                "amount": event.amount
            })

        # ---- Persist raw event ----
        self.repo.store_event(
            member_id=event.member_id,
            event={
                "type": "transaction",
                "amount": event.amount,
                "currency": event.currency,
                "metadata": event.metadata.model_dump()
            }
        )

        # ---- Update behavior state ----
        state = self.repo.get_behavior_state(event.member_id)
        state["last_transaction_amount"] = event.amount
        self.repo.save_behavior_state(event.member_id, state)

        return signals
