from app.services.behavior_detector import BehaviorDetectorService
from app.services.segment_engine import SegmentEngine
from app.services.campaign_recommender import CampaignRecommender
from app.tasks.detection_tasks import scan_member


behavior_service = BehaviorDetectorService()
segment_engine = SegmentEngine()
campaign_engine = CampaignRecommender()


async def process_event(event):
    """
    Full async pipeline:
    event → signals → state → segment → recommendations
    """

    signals = behavior_service.detect_event(event)
    member_state = behavior_service.update_member_state(event.member_id, signals)

    segment_update = segment_engine.update_member(event.member_id, member_state)
    campaigns = campaign_engine.recommend(member_state, segment_update)

    print(f"[ASYNC] member={event.member_id}")
    print(f"  signals={signals}")
    print(f"  segment={member_state.get('segment')}")
    print(f"  campaigns={len(campaigns)}")


def enqueue_event(member_id: str, payload: dict):
    """
    Queue behavior processing through Celery instead of in-process queue.
    """
    scan_member.delay(member_id, payload)
