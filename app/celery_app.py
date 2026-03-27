from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


celery_app = Celery(
    "loyalty_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.detection_tasks",
        "app.tasks.segmentation_tasks",
        "app.tasks.ai_tasks",
    ],
)

celery_app.conf.beat_schedule = {
    "re-segment-members": {
        "task": "app.tasks.segmentation_tasks.run_full_segmentation",
        "schedule": crontab(minute="0", hour="*/2"),
    },
    "scan-behavioral-alerts": {
        "task": "app.tasks.detection_tasks.scan_all_members",
        "schedule": crontab(minute="*/5"),
    },
    "retrain-rfm-model": {
        "task": "app.tasks.segmentation_tasks.retrain_clustering_model",
        "schedule": crontab(minute="0", hour="3"),
    },
}
