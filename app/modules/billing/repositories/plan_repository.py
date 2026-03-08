from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.common.models.models import Plan, UserPlanEnum
from app.common.models.base_repository import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Plan)

    async def get_by_type(self, plan_type: UserPlanEnum) -> Optional[Plan]:
        stmt = select(self.model).where(self.model.plan_type == plan_type)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_active_plans(self) -> list[Plan]:
        stmt = select(self.model).where(self.model.is_active == True)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
