import asyncio

from app.celery_app import celery_app
from app.core.ws_manager import manager
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
    result = asyncio.run(service.get_segment_stats())
    asyncio.run(
        manager.broadcast(
            "alerts",
            {
                "type": "segmentation_refreshed",
                "clusters": result.get("clusters", {}),
            },
        )
    )
    return result


@celery_app.task(
    name="app.tasks.segmentation_tasks.retrain_clustering_model",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def retrain_clustering_model(self):
    service = get_segmentation_service()
    result = asyncio.run(service.retrain())
    asyncio.run(
        manager.broadcast(
            "alerts",
            {
                "type": "segmentation_retrained",
                "result": result,
            },
        )
    )
    return result
