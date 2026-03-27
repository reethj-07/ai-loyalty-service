import asyncio
from datetime import datetime, timezone

from app.schemas.events import IngestionMetadata, TransactionEvent
from app.workers.event_processor import process_single_event



def test_high_value_transaction_triggers_proposal_candidate():
    """POST /transactions with amount=600 → proposal candidate signal is generated."""
    event = {
        "event_type": "transaction",
        "member_id": "member-pipeline",
        "payload": TransactionEvent(
            transaction_id="txn-pipeline",
            member_id="member-pipeline",
            amount=600,
            currency="USD",
            merchant="Merchant",
            category="shopping",
            channel="online",
            transaction_date=datetime.now(timezone.utc),
            metadata=IngestionMetadata(tenant_id="test", source="integration_test"),
        ).model_dump(mode="json"),
    }

    result = asyncio.run(process_single_event(event))

    assert result["proposal_candidate"] is True
