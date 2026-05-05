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

    async def get_all_for_subject(self, user_id: UUID, subject_id: UUID, skip: int = 0, limit: int = 100) -> List[Topic]:
        """Fetch all topics with pagination, ensuring subject ownership."""
        # Verify subject ownership
        subject_check = await self.db.execute(
            select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        )
        if not subject_check.scalar_one_or_none():
            return []
            
        stmt = (
            select(Topic)
            .where(Topic.subject_id == subject_id)
            .order_by(Topic.sort_order.asc())
            .offset(skip)
            .limit(limit)
        )
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
            
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_knowledge_graph(self, user_id: UUID, subject_id: UUID) -> Dict[str, Any]:
        """Generate nodes and edges for knowledge graph visualization."""
        topics = await self.get_all_for_subject(user_id, subject_id, limit=500)
        
        nodes = []
        edges = []
        
        # Build node map
        name_to_id = {t.name.lower().strip(): str(t.id) for t in topics}
        
        for t in topics:
            nodes.append({
                "id": str(t.id),
                "label": t.name,
                "mastery": t.knowledge_level,
                "difficulty": t.difficulty,
                "is_completed": t.is_completed
            })
            
            # Add edges based on prerequisites
            if t.prerequisites:
                for prereq in t.prerequisites:
                    prereq_id = name_to_id.get(prereq.lower().strip())
                    if prereq_id:
                        edges.append({
                            "source": prereq_id,
                            "target": str(t.id)
                        })
        
        return {"nodes": nodes, "edges": edges}
