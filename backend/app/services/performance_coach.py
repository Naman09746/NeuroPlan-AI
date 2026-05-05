import logging
import json
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.ai_client import AIClient
from app.services.ml.profiler import CognitiveProfiler
from app.services.ml.knowledge_tracer import KnowledgeTracerService
from app.models.coaching_event import CoachingEvent
from app.models.study_plan import StudyPlan
from app.models.topic import Topic

logger = logging.getLogger("neuroplan.coach")

class PerformanceCoach:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai = AIClient()
        self.profiler = CognitiveProfiler(db)
        self.tracer = KnowledgeTracerService(db)

    async def get_performance_summary(self, user_id: UUID) -> Dict[str, Any]:
        """Fetch the latest coaching event or generate a default one."""
        stmt = (
            select(CoachingEvent)
            .where(CoachingEvent.user_id == user_id)
            .order_by(CoachingEvent.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()

        if event:
            return {
                "message": event.message,
                "priority_topics": event.priority_topics,
                "suggested_daily_hours": event.suggested_daily_hours,
                "motivational_note": event.motivational_note
            }

        # Baseline insight if no events exist
        return {
            "message": "Initializing neural tracking. Complete your first study node to unlock AI coaching.",
            "priority_topics": [],
            "suggested_daily_hours": None,
            "motivational_note": "Every expert was once a beginner."
        }

    async def on_test_completed(self, user_id: UUID, topic_id: UUID, score: float):
        """Triggered when a user completes a topic assessment."""
        if score >= 0.8:
            return # User is doing well, no urgent intervention needed

        # 1. Gather context
        profile = await self.profiler.get_user_cognitive_profile(user_id)
        
        # Get topic name
        stmt = select(Topic.name).where(Topic.id == topic_id)
        res = await self.db.execute(stmt)
        topic_name = res.scalar_one_or_none() or "Unknown Topic"

        # Get mastery snapshot for related topics
        # (For simplicity, we'll just use the current topic score as the struggle indicator)
        struggles = f"User scored {score*100:.0f}% on assessment for {topic_name}. This is below mastery threshold."
        
        # 2. Get AI recommendation
        recommendation = await self.ai.generate_adaptive_recommendation(
            profile=profile,
            plan_status="In Progress",
            struggles=struggles,
            mastery_snapshot={topic_name: score}
        )

        # 3. Save coaching event
        await self._save_event(
            user_id=user_id,
            trigger_type="test_struggle",
            recommendation=recommendation
        )

    async def on_task_missed(self, user_id: UUID, plan_id: UUID, task_title: str, reason: str = "Skipped"):
        """Triggered when a user misses or skips a scheduled task."""
        profile = await self.profiler.get_user_cognitive_profile(user_id)
        
        struggles = f"User missed/skipped the task '{task_title}'. Reason: {reason}."
        
        recommendation = await self.ai.generate_adaptive_recommendation(
            profile=profile,
            plan_status="Needs Adjustment",
            struggles=struggles
        )

        await self._save_event(
            user_id=user_id,
            plan_id=plan_id,
            trigger_type="task_missed",
            recommendation=recommendation
        )

    async def _save_event(self, user_id: UUID, trigger_type: str, recommendation: Dict[str, Any], plan_id: Optional[UUID] = None):
        """Internal helper to persist coaching events."""
        event = CoachingEvent(
            user_id=user_id,
            plan_id=plan_id,
            trigger_type=trigger_type,
            message=recommendation.get("message", "Keep going! You're making progress."),
            priority_topics=recommendation.get("priority_topics", []),
            suggested_daily_hours=recommendation.get("suggested_daily_hours"),
            motivational_note=recommendation.get("motivational_note", "Consistency is the key to mastery.")
        )
        self.db.add(event)
        await self.db.commit()
        logger.info(f"Coach intervention created for user {user_id} (trigger: {trigger_type})")
