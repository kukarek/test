from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.common.models.models import SearchEvent
from app.common.models.base_repository import BaseRepository


class SearchEventRepository(BaseRepository[SearchEvent]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, SearchEvent)

    async def get_user_searches(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SearchEvent]:
        stmt = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_popular_queries(self, limit: int = 10) -> List[dict]:
        stmt = select(
            self.model.query, func.count(self.model.id).label("count")
        ).group_by(self.model.query).order_by(func.count(self.model.id).desc()).limit(limit)
        result = await self.db_session.execute(stmt)
        return [{"query": row[0], "count": row[1]} for row in result.all()]

    async def get_user_daily_searches(self, user_id: int, date: datetime) -> int:
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        stmt = select(func.count(self.model.id)).where(
            and_(
                self.model.user_id == user_id,
                self.model.created_at >= start,
                self.model.created_at < end
            )
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one() or 0
