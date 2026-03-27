from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.ai import router as ai_router
from app.api.v1.members import router as members_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.human_review import router as review_router
from app.api.v1.realtime import router as realtime_router
from app.api.v1.agents import router as agents_router
from app.api.v1.segments import router as segments_router
from app.api.v1.ml import router as ml_router

api_router = APIRouter()

api_router.include_router(auth_router, tags=["Authentication"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(agents_router, prefix="/agents", tags=["Autonomous Agents"])
api_router.include_router(members_router, prefix="/members", tags=["Members"])
api_router.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(segments_router, prefix="/segments", tags=["Segments"])
api_router.include_router(ml_router, prefix="/ml", tags=["ML"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(review_router, tags=["Review"])
api_router.include_router(realtime_router, prefix="/realtime", tags=["Realtime"])