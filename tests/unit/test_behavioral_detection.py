from datetime import datetime, timezone

from app.schemas.events import IngestionMetadata, TransactionEvent
from app.services.behavior_detector import BehaviorDetectorService



def test_high_value_transaction_triggers_signal():
    detector = BehaviorDetectorService()

    event = TransactionEvent(
        transaction_id="txn-1",
        member_id="member-1",
        amount=600,
        currency="USD",
        merchant="Test Merchant",
        category="shopping",
        channel="online",
        transaction_date=datetime.now(timezone.utc),
        metadata=IngestionMetadata(tenant_id="test", source="unit_test"),
    )

    signals = detector.detect(event)

    assert any(signal["type"] == "high_value_transaction" for signal in signals)
