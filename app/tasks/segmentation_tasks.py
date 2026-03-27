import asyncio

from app.celery_app import celery_app
from app.services.segmentation_service import get_segmentation_service


@celery_app.task(
    name="app.tasks.segmentation_tasks.run_full_segmentation",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def run_full_segmentation(self):
    service = get_segmentation_service()
    return asyncio.run(service.get_segment_stats())


@celery_app.task(
    name="app.tasks.segmentation_tasks.retrain_clustering_model",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def retrain_clustering_model(self):
    service = get_segmentation_service()
    return asyncio.run(service.retrain())
