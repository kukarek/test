from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from typing import Optional, List
from app.common.models.models import Product
from app.common.models.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Product)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        stmt = select(self.model).where(self.model.sku == sku).options(selectinload(self.model.offers))
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Product]:
        stmt = select(self.model).where(
            or_(self.model.name.ilike(f"%{query}%"), self.model.description.ilike(f"%{query}%"))
        ).options(selectinload(self.model.offers)).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_by_category(self, category: str, skip: int = 0, limit: int = 20) -> List[Product]:
        stmt = select(self.model).where(
            self.model.category == category
        ).options(selectinload(self.model.offers)).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
