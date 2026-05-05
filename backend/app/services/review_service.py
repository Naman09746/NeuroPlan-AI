from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.topic import Topic
from app.models.subject import Subject
from app.services.ml.mastery_engine import ForgettingCurve

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_due_topics(self, user_id: UUID, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Identify topics where retention probability has dropped below the threshold.
        These topics are 'Due for Review'.
        """
        stmt = (
            select(Topic, Subject.name.label("subject_name"), Subject.color.label("subject_color"))
            .join(Subject, Topic.subject_id == Subject.id)
            .where(and_(
                Subject.user_id == user_id,
                Topic.knowledge_level > 0.1 # Only topics they've actually started
            ))
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        due_topics = []
        now = datetime.now(timezone.utc)
        
        for row in rows:
            topic = row[0]
            knowledge = topic.knowledge_level
            retention = 1.0
            
            if topic.last_reviewed_at:
                # Ensure last_reviewed_at is timezone-aware
                last_rev = topic.last_reviewed_at
                if last_rev.tzinfo is None:
                    last_rev = last_rev.replace(tzinfo=timezone.utc)
                
                days_passed = (now - last_rev).total_seconds() / 86400
                retention = ForgettingCurve.compute_retention(days_passed, topic.stability)
            
            # Topic is due if retention drops below threshold
            if retention < threshold:
                due_topics.append({
                    "topic_id": str(topic.id),
                    "topic_name": topic.name,
                    "subject_name": row.subject_name,
                    "subject_color": row.subject_color,
                    "current_retention": round(retention * 100, 1),
                    "knowledge_level": round(topic.knowledge_level * 100, 1),
                    "last_reviewed": topic.last_reviewed_at.isoformat() if topic.last_reviewed_at else None,
                    "urgency": "high" if retention < 0.6 else "medium"
                })
        
        # Sort by lowest retention first
        due_topics.sort(key=lambda x: x["current_retention"])
        
        return due_topics
