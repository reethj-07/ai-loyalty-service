import asyncio
import logging
import os
from typing import Dict
from uuid import uuid4

from app.core.event_queue import event_queue
from app.services.behavior_detector import BehaviorDetectorService
from app.schemas.ai_response import MemberState
from app.automation.engine import AutomationEngine
from app.review.repository import ReviewRepository
from app.segments.aggregator import SegmentAggregator
from app.segments.repository import SegmentRepository
from app.segments.detector import SegmentShiftDetector
from app.monitoring.kpi_engine import kpi_engine
from app.repositories.campaign_proposal_repository import campaign_proposal_repo
from app.schemas.campaign_proposal import CampaignProposal
from app.repositories.supabase_campaigns_repo import campaigns_repo
from app.schemas.events import TransactionEvent
from app.services.campaign_executor import CampaignExecutor
from app.core.ws_manager import manager

logger = logging.getLogger(__name__)

behavior_service = BehaviorDetectorService()
automation_engine = AutomationEngine()
review_repo = ReviewRepository()
campaign_executor = CampaignExecutor()

member_state_store: Dict[str, MemberState] = {}

segment_repo = SegmentRepository()
segment_aggregator = SegmentAggregator()
segment_detector = SegmentShiftDetector()


async def process_single_event(event: Dict):
    member_id = event["member_id"]
    payload = event["payload"]
    if isinstance(payload, dict):
        payload = TransactionEvent(**payload)

    signals = behavior_service.detect(payload)

    member_state = MemberState(
        segment="high_value_active" if signals else "regular",
        lifecycle_stage="growth" if signals else "stable",
        risk_score=0.15 if signals else 0.35,
    )

    member_state_store[member_id] = member_state

    proposals = automation_engine.evaluate(
        {
            "member_id": member_id,
            "signals": signals,
            "segment": member_state.segment,
        }
    )

    auto_approve = os.getenv("AUTO_APPROVE_CAMPAIGNS", "false").lower() == "true"
    auto_execute = os.getenv("AUTO_EXECUTE_CAMPAIGNS", "false").lower() == "true"
    tenant_id = None
    if os.getenv("TENANT_MODE", "false").lower() == "true":
        tenant_id = os.getenv("DEFAULT_TENANT_ID")

    for proposal in proposals:
        campaign_proposal = CampaignProposal(
            proposal_id=str(uuid4()),
            campaign_type=proposal.get("campaign_type", "promotion"),
            objective=proposal.get("objective", "engagement"),
            suggested_offer=proposal.get("offer", "bonus_points"),
            validity_hours=int(proposal.get("validity_hours", 48)),
            estimated_uplift=round(float(proposal.get("estimated_roi", 0.1)) * 0.15, 2),
            estimated_roi=float(proposal.get("estimated_roi", 0.1)),
            segment=member_state.segment,
            status="pending",
        )

        campaign_proposal_repo.save(campaign_proposal)

        if auto_approve:
            created = campaigns_repo.create_campaign(
                {
                    "name": f"AI {campaign_proposal.segment} - {campaign_proposal.campaign_type}",
                    "description": campaign_proposal.suggested_offer,
                    "campaign_type": campaign_proposal.campaign_type,
                    "objective": campaign_proposal.objective,
                    "channel": "email",
                    "status": "scheduled",
                    "estimated_roi": campaign_proposal.estimated_roi,
                    "estimated_cost": 0,
                    "estimated_revenue": 0,
                },
                tenant_id=tenant_id,
            )

            if auto_execute and created:
                await campaign_executor.launch_campaign(
                    campaign_id=created.id,
                    campaign_data={
                        "name": created.name,
                        "channel": created.channel or "email",
                        "target_segment": campaign_proposal.segment,
                        "offer_details": campaign_proposal.suggested_offer,
                    },
                )

    previous_segments = segment_repo.get_all()
    current_segments = segment_aggregator.aggregate(list(member_state_store.values()))
    segment_repo.replace(current_segments)

    campaign_id = event.get("campaign_id")
    if campaign_id:
        await kpi_engine.register_participation(campaign_id)
        await kpi_engine.register_transaction(
            campaign_id,
            amount=payload.amount,
            incentive_cost=payload.amount * 0.02,
        )
        await manager.broadcast(
            f"kpis/{campaign_id}",
            {
                "type": "campaign_kpi_update",
                "campaign_id": campaign_id,
                "amount": payload.amount,
                "member_id": member_id,
            },
        )

    return {
        "member_id": member_id,
        "signals_count": len(signals),
        "proposal_candidate": len(proposals) > 0,
        "segment": member_state.segment,
    }


async def event_worker():
    logger.info("event_worker_started")

    while True:
        event = await event_queue.consume()

        try:
            await process_single_event(event)
        except Exception:
            logger.exception("event_processing_failed")

        await asyncio.sleep(0)
