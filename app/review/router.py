from fastapi import APIRouter
from app.review.repository import ReviewRepository

router = APIRouter(prefix="/review", tags=["review"])

repo = ReviewRepository()


@router.get("/pending")
def list_pending_reviews():
    return repo.list_pending()


@router.post("/{review_id}/approve")
def approve_campaign(review_id: str):
    return repo.approve(review_id)


@router.post("/{review_id}/modify")
def modify_campaign(review_id: str, updates: dict):
    return repo.modify(review_id, updates)
