from fastapi import APIRouter

from app.schemas.events import TransactionEvent
from app.schemas.ai_response import AIResponse, MemberState
from app.tasks.detection_tasks import scan_member

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/transaction", response_model=AIResponse)
async def ingest_transaction(event: TransactionEvent):
    """
    Phase-3A:
    - Async ingestion
    - Fire-and-forget event publishing
    """

    scan_member.delay(event.member_id, event.model_dump(mode="json"))

    return AIResponse(
        status="accepted",
        member_id=event.member_id,
        behavioral_signals=[],

        # NEVER None
        member_state=MemberState(
            segment="processing",
            lifecycle_stage="unknown",
            risk_score=0.0,
        ),

        campaign_recommendations=[],
        next_actions=[
            "processing_async",
            "await_signal_detection",
        ],
    )
