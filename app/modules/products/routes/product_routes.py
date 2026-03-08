from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db_session
from app.core.di.dependencies import get_current_user
from app.common.schemas.schemas import ProductCreate, ProductResponse
from app.modules.products.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = ProductService(db)
    return await service.create_product(product.dict())


@router.get("/", response_model=list)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = ProductService(db)
    return await service.product_repo.get_all(skip, limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = ProductService(db)
    return await service.product_repo.get_by_id(product_id)


@router.get("/search", response_model=list)
async def search_products(
    q: str = Query(..., min_length=1, max_length=500),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = ProductService(db)
    return await service.search_products(q, skip, limit)


@router.get("/category/{category}", response_model=list)
async def get_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = ProductService(db)
    return await service.get_products_by_category(category, skip, limit)
