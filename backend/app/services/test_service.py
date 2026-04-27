from typing import List, Dict, Any, Optional
from uuid import UUID
import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.test_session import TestSession
from app.models.topic import Topic
from app.services.base import BaseService
from app.services.ai_client import AIClient
from app.services.ml.knowledge_tracer import KnowledgeTracerService

class TestService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db, "test_service")
        self.ai = AIClient()
        self.tracer = KnowledgeTracerService(db)

    async def generate_mock_test(self, user_id: UUID, topic_id: UUID, count: int = 5) -> Dict[str, Any]:
        """
        Generate an adaptive assessment for a specific topic.
        Uses DKT to predict mastery and AI to generate matching questions.
        """
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()
        
        if not topic:
            raise ValueError("Topic node not found")

        # 1. Predict Mastery via DKT
        mastery_score = await self.tracer.predict_mastery(user_id, topic_id)
        
        # 2. Map mastery to dynamic difficulty
        if mastery_score < 0.4:
            difficulty = "easy"
        elif mastery_score < 0.7:
            difficulty = "medium"
        else:
            difficulty = "hard"

        # 3. Call Fine-tuned AI Assessment Engine
        questions = await self.ai.generate_assessment(
            topic_name=topic.name,
            difficulty=difficulty,
            mastery_score=mastery_score
        )

        return {
            "topic_id": topic_id,
            "topic_name": topic.name,
            "difficulty": difficulty,
            "mastery_score": round(mastery_score, 2),
            "questions": questions[:count] if questions else []
        }

    async def submit_test_result(
        self, 
        user_id: UUID, 
        topic_id: UUID, 
        correct_count: int, 
        total_count: int,
        time_seconds: int,
        questions_data: List[Dict[str, Any]]
    ) -> TestSession:
        """
        Analyze test performance and update records.
        """
        score_percentage = (correct_count / total_count) if total_count > 0 else 0
        
        # 1. Fetch topic current mastery
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()
        
        # 2. Create the TestSession log
        session = TestSession(
            user_id=user_id,
            topic_id=topic_id,
            difficulty="medium", # Simplified
            total_questions=total_count,
            correct_answers=correct_count,
            score_percentage=score_percentage,
            questions_data={"results": questions_data},
            time_taken_seconds=time_seconds
        )
        self.db.add(session)
        
        # 3. Knowledge Update (MasteryEngine handles the complex logic in ExecutionTracker, 
        # but we also update knowledge_level here for consistency if needed)
        if topic:
            # Simple weighted update for immediate feedback
            # In a production setup, MasteryEngine would be the source of truth
            new_level = (score_percentage * 0.7) + (topic.knowledge_level * 0.3)
            topic.knowledge_level = min(max(new_level, 0.0), 1.0)
            if score_percentage > 0.8:
                topic.is_completed = True
            self.db.add(topic)
            
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_user_test_history(self, user_id: UUID) -> List[TestSession]:
        """Fetch historical performance data for longitudinal analysis."""
        stmt = (
            select(TestSession)
            .where(TestSession.user_id == user_id)
            .order_by(TestSession.taken_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
