import asyncio
from typing import Any, Dict

from app.celery_app import celery_app
from app.services.ai_service import get_ai_service


@celery_app.task(
    name="app.tasks.ai_tasks.generate_campaign_proposal",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_campaign_proposal(self, member_id: str, trigger_event: Dict[str, Any] | None = None):
    ai_service = get_ai_service()
    prompt = "Generate campaign proposal from transaction trigger"
    if trigger_event:
        prompt = f"Generate campaign proposal from trigger: {trigger_event}"

    return asyncio.run(ai_service.run_member_pipeline(member_id=member_id, prompt=prompt))
