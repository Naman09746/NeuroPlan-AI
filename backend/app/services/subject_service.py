from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate

class SubjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_for_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Subject]:
        """Fetch all subjects for a user, joined with topic counts (Paginated)."""
        from app.models.topic import Topic
        
        stmt = (
            select(Subject, func.count(Topic.id).label("topic_count"))
            .outerjoin(Topic)
            .where(Subject.user_id == user_id)
            .group_by(Subject.id)
            .order_by(Subject.sort_order.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        
        subjects_with_counts = []
        for subject, count in result.all():
            # Inject count for schema mapping
            subject.topic_count = count
            subjects_with_counts.append(subject)
            
        return subjects_with_counts

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
    async def get_recommendations(self, user_id: UUID) -> List[Dict[str, Any]]:
        """AI-powered subject recommendations based on career goals."""
        from app.models.user import User
        from app.services.ai_client import AIClient
        
        # 1. Fetch context
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user: return []
        
        current_subjects = await self.get_all_for_user(user_id)
        subject_names = [s.name for s in current_subjects]
        career_goal = user.preferences.get("career_goal", "General Learning")
        
        # 2. Call AI
        ai = AIClient()
        recommendations = await ai.get_structured_completion(
            prompt=f"User Career Goal: {career_goal}\nCurrent Subjects: {', '.join(subject_names)}",
            system_prompt="Suggest 3 new subjects the user should learn to achieve their goal. Return a list of objects with 'name' and 'reason'.",
            response_model=None 
        )
        
        return recommendations if isinstance(recommendations, list) else []
