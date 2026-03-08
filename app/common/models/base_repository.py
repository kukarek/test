from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import TypeVar, Generic, List, Optional, Type
from abc import ABC, abstractmethod

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, db_session: AsyncSession, model: Type[T]):
        self.db_session = db_session
        self.model = model

    async def create(self, obj_in: dict) -> T:
        db_obj = self.model(**obj_in)
        self.db_session.add(db_obj)
        await self.db_session.flush()
        return db_obj

    async def get_by_id(self, obj_id: int) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def update(self, obj_id: int, obj_in: dict) -> Optional[T]:
        db_obj = await self.get_by_id(obj_id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            await self.db_session.flush()
        return db_obj

    async def delete(self, obj_id: int) -> bool:
        db_obj = await self.get_by_id(obj_id)
        if db_obj:
            await self.db_session.delete(db_obj)
            await self.db_session.flush()
            return True
        return False

    async def commit(self):
        await self.db_session.commit()
