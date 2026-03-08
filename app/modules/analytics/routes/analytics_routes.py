from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db_session
from app.core.di.dependencies import get_current_user
from app.modules.analytics.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/user", response_model=dict)
async def get_user_analytics(
    days: int = Query(30, ge=1, le=365),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = AnalyticsService(db)
    return await service.get_user_analytics(user_id, days)


@router.get("/platform", response_model=dict)
async def get_platform_analytics(
    days: int = Query(30, ge=1, le=365),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = AnalyticsService(db)
    return await service.get_platform_analytics(days)


@router.get("/trends", response_model=list)
async def get_trends(
    limit: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = AnalyticsService(db)
    return await service.get_search_trends(limit=limit)
