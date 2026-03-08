from fastapi import APIRouter, Depends, Query
from app.core.di.dependencies import get_current_user
from app.modules.marketplace.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/api/marketplaces", tags=["marketplaces"])

marketplace_service = None


async def get_marketplace_service() -> MarketplaceService:
    global marketplace_service
    if marketplace_service is None:
        marketplace_service = MarketplaceService()
    return marketplace_service


@router.get("/available", response_model=dict)
async def get_available_marketplaces(user_id: int = Depends(get_current_user)):
    return {
        "marketplaces": [
            {"id": "wildberries", "name": "Wildberries", "available": True},
            {"id": "ozon", "name": "Ozon", "available": True},
            {"id": "avito", "name": "Avito", "available": True}
        ]
    }


@router.get("/{marketplace}/search", response_model=dict)
async def search_marketplace(
    marketplace: str,
    q: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(20, ge=1, le=50),
    user_id: int = Depends(get_current_user),
    service: MarketplaceService = Depends(get_marketplace_service),
):
    try:
        results = await service.search_marketplace(marketplace, q, limit)
        return {
            "marketplace": marketplace,
            "query": q,
            "results_count": len(results),
            "results": results
        }
    except ValueError as e:
        return {"error": str(e)}
