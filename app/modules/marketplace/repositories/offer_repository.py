from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import Optional, List
from app.common.models.models import Offer
from app.common.models.base_repository import BaseRepository


class OfferRepository(BaseRepository[Offer]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Offer)

    async def get_by_product(self, product_id: int) -> List[Offer]:
        stmt = select(self.model).where(self.model.product_id == product_id).order_by(self.model.price.asc())
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_cheapest_offer(self, product_id: int) -> Optional[Offer]:
        stmt = select(self.model).where(self.model.product_id == product_id).order_by(
            self.model.price.asc()
        ).limit(1)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_by_marketplace(self, marketplace: str, skip: int = 0, limit: int = 100) -> List[Offer]:
        stmt = select(self.model).where(self.model.marketplace == marketplace).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_marketplace_product(self, marketplace: str, marketplace_product_id: str) -> Optional[Offer]:
        stmt = select(self.model).where(
            and_(self.model.marketplace == marketplace, self.model.marketplace_product_id == marketplace_product_id)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().first()
