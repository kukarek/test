from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db_session
from app.core.di.dependencies import get_current_user
from app.common.schemas.schemas import SearchRequest, SearchResponse
from app.modules.search.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/", response_model=dict, status_code=status.HTTP_200_OK)
async def search(
    query: SearchRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = SearchService(db)
    try:
        result = await service.search(
            user_id=user_id,
            query=query.query,
            marketplaces=query.marketplaces,
            use_ai_router=query.use_ai_router,
            limit=query.limit,
        )
        return result
    finally:
        await service.close()


@router.get("/suggestions", response_model=dict)
async def get_suggestions(
    prefix: str = Query(..., min_length=1, max_length=100),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = SearchService(db)
    try:
        return {"suggestions": ["Example 1", "Example 2"]}
    finally:
        await service.close()
