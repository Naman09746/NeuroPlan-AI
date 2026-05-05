from typing import List, Dict, Any, Optional
from uuid import UUID
import random
from sqlalchemy import select, and_, or_, desc
from datetime import datetime, timedelta, date

from app.models.test_session import TestSession
from app.models.topic import Topic
from app.models.subject import Subject
from app.models.daily_task import DailyTask
from app.models.study_plan import StudyPlan
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

    async def generate_weekly_test(self, user_id: UUID) -> Dict[str, Any]:
        """
        Tier 3: Weekly Interleaved Review.
        Pulls topics studied in the last 7 days.
        """
        last_week = date.today() - timedelta(days=7)
        
        # Get topics worked on in the last week
        stmt = (
            select(Topic)
            .join(DailyTask, Topic.id == DailyTask.topic_id)
            .join(StudyPlan, DailyTask.plan_id == StudyPlan.id)
            .where(and_(
                StudyPlan.user_id == user_id,
                DailyTask.status == "done",
                DailyTask.scheduled_date >= last_week
            ))
            .distinct()
        )
        result = await self.db.execute(stmt)
        topics = result.scalars().all()
        
        if not topics:
            # Fallback to general topics the user has studied if week was empty
            stmt = (
                select(Topic)
                .join(Subject, Topic.subject_id == Subject.id)
                .where(and_(Subject.user_id == user_id, Topic.knowledge_level > 0))
                .limit(5)
            )
            result = await self.db.execute(stmt)
            topics = result.scalars().all()

        if not topics:
            raise ValueError("No recently studied topics found for weekly review.")

        # Interleave questions from these topics
        questions = []
        for topic in topics[:5]: # Cap at 5 topics
            topic_questions = await self.ai.generate_assessment(
                topic_name=topic.name,
                difficulty="medium"
            )
            if topic_questions:
                # Add topic context to questions
                for q in topic_questions:
                    q["topic_id"] = str(topic.id)
                    q["topic_name"] = topic.name
                questions.extend(topic_questions[:2]) # Take 2 from each

        random.shuffle(questions)

        return {
            "title": "Weekly Interleaved Review",
            "tier": "weekly",
            "questions": questions
        }

    async def generate_crucible_exam(self, user_id: UUID, subject_id: UUID) -> Dict[str, Any]:
        """
        Tier 4: High-Stakes Crucible Mock Exam.
        Focuses on open-ended interview questions across the subject.
        """
        stmt = select(Subject).where(and_(Subject.id == subject_id, Subject.user_id == user_id))
        result = await self.db.execute(stmt)
        subject = result.scalar_one_or_none()
        
        if not subject:
            raise ValueError("Subject not found or access denied.")

        # Get top 5 most important topics in the subject (by order or difficulty)
        stmt = select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.sort_order.asc()).limit(5)
        result = await self.db.execute(stmt)
        topics = result.scalars().all()

        exam_questions = []
        for topic in topics:
            # Generate one major open-ended interview question per topic
            q = await self.ai.generate_open_ended_questions(
                topic_name=topic.name,
                difficulty="hard",
                num_questions=1
            )
            if q:
                q[0]["topic_id"] = str(topic.id)
                q[0]["topic_name"] = topic.name
                exam_questions.append(q[0])

        return {
            "title": f"The Crucible: {subject.name}",
            "subject_id": str(subject_id),
            "tier": "crucible",
            "questions": exam_questions,
            "is_open_ended": True,
            "time_limit_minutes": 45
        }

    async def evaluate_verbal_answer(
        self,
        user_id: UUID,
        topic_id: UUID,
        question: str,
        user_answer: str,
        key_points: List[str]
    ) -> Dict[str, Any]:
        """Submit an open-ended answer for AI evaluation and update mastery."""
        evaluation = await self.ai.evaluate_answer(
            question=question,
            user_answer=user_answer,
            key_points=key_points
        )
        
        score = evaluation.get("score", 0.0)
        
        # Update Knowledge Tracing
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self.db.execute(stmt)
        topic = result.scalar_one_or_none()
        
        if topic:
            # Open-ended answers have a higher weight in knowledge updates
            new_level = (score * 0.8) + (topic.knowledge_level * 0.2)
            topic.knowledge_level = min(max(new_level, 0.0), 1.0)
            topic.last_reviewed_at = datetime.now()
            self.db.add(topic)
            await self.db.commit()

        return evaluation

