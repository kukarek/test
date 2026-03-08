from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime
from app.common.models.models import Subscription
from app.common.models.base_repository import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Subscription)

    async def get_by_user(self, user_id: int) -> Optional[Subscription]:
        stmt = select(self.model).where(
            (self.model.user_id == user_id) & (self.model.is_active == True)
        ).options(selectinload(self.model.plan))
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_all_by_user(self, user_id: int) -> list[Subscription]:
        stmt = select(self.model).where(
            self.model.user_id == user_id
        ).options(selectinload(self.model.plan))
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
