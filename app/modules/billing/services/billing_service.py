from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.modules.billing.repositories.plan_repository import PlanRepository
from app.modules.billing.repositories.subscription_repository import SubscriptionRepository
from app.modules.auth.repositories.user_repository import UserRepository
from app.common.exceptions.exceptions import NotFoundException, ConflictException
from app.common.models.models import UserPlanEnum


class BillingService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.plan_repo = PlanRepository(db_session)
        self.subscription_repo = SubscriptionRepository(db_session)
        self.user_repo = UserRepository(db_session)

    async def get_available_plans(self) -> list:
        return await self.plan_repo.get_active_plans()

    async def get_plan(self, plan_id: int) -> dict:
        plan = await self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise NotFoundException("Plan not found")
        return plan

    async def subscribe_to_plan(self, user_id: int, plan_id: int, billing_period: str = "monthly") -> Dict:
        plan = await self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise NotFoundException("Plan not found")

        existing = await self.subscription_repo.get_by_user(user_id)
        if existing:
            await self.subscription_repo.cancel_subscription(existing.id)

        expires_at = datetime.utcnow() + timedelta(days=365 if billing_period == "annual" else 30)

        subscription_data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "is_active": True,
            "expires_at": expires_at,
            "renewal_date": expires_at,
        }

        subscription = await self.subscription_repo.create(subscription_data)
        await self.user_repo.update(user_id, {"plan": plan.plan_type})
        await self.db_session.commit()

        return {
            "subscription_id": subscription.id,
            "plan_id": plan_id,
            "plan_name": plan.name,
            "is_active": True,
            "expires_at": expires_at,
            "billing_period": billing_period,
        }

    async def cancel_subscription(self, user_id: int) -> Dict:
        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription:
            raise NotFoundException("No active subscription found")

        await self.subscription_repo.cancel_subscription(subscription.id)
        await self.user_repo.update(user_id, {"plan": UserPlanEnum.FREE})
        await self.db_session.commit()

        return {
            "subscription_id": subscription.id,
            "status": "cancelled",
        }

    async def get_user_subscription(self, user_id: int) -> Optional[Dict]:
        subscription = await self.subscription_repo.get_by_user(user_id)
        if not subscription:
            return None

        return {
            "subscription_id": subscription.id,
            "plan_id": subscription.plan.id,
            "plan_name": subscription.plan.name,
            "daily_search_limit": subscription.plan.daily_search_limit,
            "is_active": subscription.is_active,
            "started_at": subscription.started_at,
            "expires_at": subscription.expires_at,
        }
