from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.services.segmentation_service import get_segmentation_service

router = APIRouter(tags=["ml"])


@router.post("/retrain")
async def retrain_model(_user: dict = Depends(get_current_user)):
    """
    Protected endpoint to retrain RFM + KMeans segmentation model.
    """
    service = get_segmentation_service()
    return await service.retrain()
