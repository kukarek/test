from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.common.models.models import User, UserPlanEnum
from app.common.models.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.username == username)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
