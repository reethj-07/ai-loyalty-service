import asyncio
from typing import Any, Dict

from app.celery_app import celery_app
from app.repositories.supabase_members_repo import members_repo
from app.workers.event_processor import process_single_event
from app.tasks.ai_tasks import generate_campaign_proposal


@celery_app.task(
    name="app.tasks.detection_tasks.scan_member",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def scan_member(self, member_id: str, payload: Dict[str, Any]):
    result = asyncio.run(
        process_single_event(
            {
                "event_type": "transaction",
                "member_id": member_id,
                "payload": payload,
            }
        )
    )

    if result.get("proposal_candidate"):
        generate_campaign_proposal.delay(member_id, payload)

    return result


@celery_app.task(
    name="app.tasks.detection_tasks.scan_all_members",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def scan_all_members(self):
    members, _total = members_repo.list_members(limit=500, offset=0)
    queued = 0
    for member in members:
        scan_member.delay(member.id, {"member_id": member.id, "amount": 0.0, "currency": "USD"})
        queued += 1

    return {"status": "queued", "members": queued}
