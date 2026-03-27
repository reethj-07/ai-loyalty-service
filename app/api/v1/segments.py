from fastapi import APIRouter

from app.services.segmentation_service import get_segmentation_service

router = APIRouter(tags=["segments"])


@router.get("/stats")
async def get_segment_stats():
    """
    Returns cluster stats and feature importances for RFM segmentation.
    """
    service = get_segmentation_service()
    return await service.get_segment_stats()
