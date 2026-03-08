from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple
from datetime import timedelta
from app.modules.auth.repositories.user_repository import UserRepository
from app.modules.billing.repositories.plan_repository import PlanRepository
from app.modules.billing.repositories.subscription_repository import SubscriptionRepository
from app.core.security.auth import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.config.settings import settings
from app.common.exceptions.exceptions import (
    AuthenticationException, ConflictException, NotFoundException,
)
from app.common.models.models import User, UserPlanEnum


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.plan_repo = PlanRepository(db_session)
        self.subscription_repo = SubscriptionRepository(db_session)

    async def register(self, email: str, username: str, password: str) -> User:
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ConflictException("Email already registered")

        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hash_password(password),
            "plan": UserPlanEnum.FREE,
        }
        user = await self.user_repo.create(user_data)
        free_plan = await self.plan_repo.get_by_type(UserPlanEnum.FREE)
        if free_plan:
            subscription_data = {"user_id": user.id, "plan_id": free_plan.id, "is_active": True}
            await self.subscription_repo.create(subscription_data)
        await self.db_session.commit()
        return user

    async def login(self, email: str, password: str) -> Tuple[str, str, User]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")
        if not user.is_active:
            raise AuthenticationException("User account is inactive")

        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=timedelta(hours=settings.jwt_expiration_hours)
        )
        refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})
        return access_token, refresh_token, user

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user
