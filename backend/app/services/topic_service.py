from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.topic import Topic
from app.models.subject import Subject
from app.schemas.topic import TopicCreate, TopicUpdate

class TopicService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_for_subject(self, user_id: UUID, subject_id: UUID) -> List[Topic]:
        """Fetch all topics, ensuring the subject belongs to the requesting user."""
        # Verify subject ownership
        subject_check = await self.db.execute(
            select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        )
        if not subject_check.scalar_one_or_none():
            return []
            
        stmt = select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_bulk(self, user_id: UUID, subject_id: UUID, topics_in: List[TopicCreate]) -> List[Topic]:
        """
        High-performance bulk ingestion for the Onboarding Wizard.
        Validates subject ownership before batch inserting topics.
        """
        # Security: Verify subject ownership
        subject_check = await self.db.execute(
            select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        )
        if not subject_check.scalar_one_or_none():
            raise ValueError("Invalid subject ID or unauthorized access")

        db_topics = [
            Topic(**t.model_dump(exclude={"subject_id"}), subject_id=subject_id)
            for t in topics_in
        ]
        self.db.add_all(db_topics)
        await self.db.commit()
        # Refreshing bulk objects can be slow, usually we return the counts or re-query
        return db_topics

    async def update_status(self, topic_id: UUID, is_completed: bool, knowledge_level: Optional[float] = None) -> Optional[Topic]:
        """Update specialized topic progress metrics."""
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            return None
            
        db_obj.is_completed = is_completed
        if knowledge_level is not None:
            db_obj.knowledge_level = knowledge_level
            
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
