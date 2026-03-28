from fastapi import APIRouter, Depends

from app.core.auth import require_roles
from app.services.segmentation_service import get_segmentation_service

router = APIRouter(tags=["ml"])


@router.post("/retrain")
async def retrain_model(_user: dict = Depends(require_roles("admin"))):
    """
    Protected endpoint to retrain RFM + KMeans segmentation model.
    """
    service = get_segmentation_service()
    return await service.retrain()
