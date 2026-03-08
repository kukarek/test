from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db_session
from app.core.di.dependencies import get_current_user
from app.common.schemas.schemas import SubscriptionCreate, SubscriptionResponse, PlanResponse
from app.modules.billing.services.billing_service import BillingService

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/plans", response_model=list)
async def get_plans(db: AsyncSession = Depends(get_db_session)):
    service = BillingService(db)
    return await service.get_available_plans()


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    service = BillingService(db)
    return await service.get_plan(plan_id)


@router.get("/subscription", response_model=dict)
async def get_subscription(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = BillingService(db)
    subscription = await service.get_user_subscription(user_id)
    return subscription or {"message": "No active subscription"}


@router.post("/subscription", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    billing_period: str = "monthly",
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = BillingService(db)
    return await service.subscribe_to_plan(user_id, subscription.plan_id, billing_period)


@router.delete("/subscription", status_code=status.HTTP_200_OK)
async def cancel_subscription(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    service = BillingService(db)
    return await service.cancel_subscription(user_id)
