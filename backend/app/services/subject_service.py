from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate

class SubjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_for_user(self, user_id: UUID) -> List[Subject]:
        """Fetch all subjects for a user, ordered for the dashboard."""
        stmt = select(Subject).where(Subject.user_id == user_id).order_by(Subject.sort_order.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_for_user(self, user_id: UUID, subject_in: SubjectCreate) -> Subject:
        """Create a subject and auto-calculate the sort order."""
        # Get current max sort_order
        stmt = select(func.max(Subject.sort_order)).where(Subject.user_id == user_id)
        result = await self.db.execute(stmt)
        max_order = result.scalar() or 0
        
        db_obj = Subject(
            **subject_in.model_dump(exclude={"sort_order"}),
            user_id=user_id,
            sort_order=max_order + 1
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update_safe(self, user_id: UUID, subject_id: UUID, subject_in: SubjectUpdate) -> Optional[Subject]:
        """Update a subject only if it belongs to the user."""
        stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            return None
            
        update_data = subject_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
