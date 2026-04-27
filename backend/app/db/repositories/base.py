# backend/app/db/repositories/base.py
from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Industrial-grade Generic Repository for NeuroPlan.
    Provides standardized data access with type safety.
    """
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: UUID) -> Optional[T]:
        return await self.session.get(self.model, id)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: Any) -> T:
        # Accepts pydantic schema or dict
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def update(self, db_obj: T, obj_in: Any) -> T:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj

    async def delete(self, id: UUID) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
