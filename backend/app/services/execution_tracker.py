from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.daily_task import DailyTask
from app.models.progress_log import ProgressLog
from app.models.topic import Topic
from app.schemas.task import TaskStatusUpdate
from app.services.ml.mastery_engine import MasteryEngine

class ExecutionTrackerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mastery_engine = MasteryEngine(db)

    async def get_today_tasks(self, user_id: UUID, plan_id: UUID) -> List[DailyTask]:
        """Fetch tasks scheduled for today for the specific user and plan."""
        # 1. Ownership check: Ensure the plan belongs to the user
        plan_stmt = select(StudyPlan.id).where(
            and_(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
        )
        plan_res = await self.db.execute(plan_stmt)
        if not plan_res.scalar():
            return []

        today = date.today()
        stmt = select(DailyTask).where(
            and_(DailyTask.plan_id == plan_id, DailyTask.scheduled_date == today)
        ).order_by(DailyTask.sort_order.asc()).options(
            selectinload(DailyTask.topic)
        )
        
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())
        
        # Attach topic_name for frontend consumption
        for task in tasks:
            if task.topic:
                task.topic_name = task.topic.name
        
        return tasks

    async def get_week_tasks(self, user_id: UUID, plan_id: UUID) -> List[DailyTask]:
        """Fetch tasks for the next 7 days for the specific user and plan."""
        # 1. Ownership check
        plan_stmt = select(StudyPlan.id).where(
            and_(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
        )
        plan_res = await self.db.execute(plan_stmt)
        if not plan_res.scalar():
            return []

        today = date.today()
        next_week = today + timedelta(days=7)
        
        stmt = select(DailyTask).where(
            and_(
                DailyTask.plan_id == plan_id, 
                DailyTask.scheduled_date >= today,
                DailyTask.scheduled_date < next_week
            )
        ).order_by(DailyTask.scheduled_date.asc(), DailyTask.sort_order.asc()).options(
            selectinload(DailyTask.topic)
        )
        
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())
        
        for task in tasks:
            if task.topic:
                task.topic_name = task.topic.name
        
        return tasks

    async def update_task_progress(
        self, 
        user_id: UUID, 
        task_id: UUID, 
        update_in: TaskStatusUpdate
    ) -> Optional[DailyTask]:
        """
        Update task status and compute intelligent mastery adjustment.
        Uses MasteryEngine for multi-signal scoring instead of hardcoded +0.1.
        """
        # 1. Fetch Task + Plan ownership in one join
        stmt = (
            select(DailyTask)
            .join(StudyPlan)
            .where(and_(DailyTask.id == task_id, StudyPlan.user_id == user_id))
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return None
            
        # 1. Update Task Record
        task.status = update_in.status
        if update_in.actual_minutes is not None:
            task.actual_minutes = update_in.actual_minutes
        if update_in.notes:
            task.notes = update_in.notes
        if update_in.status == "done":
            task.completed_at = datetime.now()
            
        # 2. Create Audit/Progress Log
        log = ProgressLog(
            task_id=task_id,
            user_id=user_id,
            time_spent_minutes=update_in.actual_minutes or 0,
            status=update_in.status,
            notes=update_in.notes
        )
        self.db.add(log)
        
        # 3. INTELLIGENT Knowledge Update (replaces crude += 0.1)
        topic_stmt = select(Topic).where(Topic.id == task.topic_id)
        topic_res = await self.db.execute(topic_stmt)
        topic = topic_res.scalar_one_or_none()
        
        if topic:
            mastery_delta = await self.mastery_engine.compute_mastery_update(
                topic_id=task.topic_id,
                user_id=user_id,
                time_spent=update_in.actual_minutes,
                time_expected=task.planned_minutes,
                completion_status=update_in.status,
                session_quality=update_in.log_data if hasattr(update_in, 'log_data') else None,
            )
            
            topic.knowledge_level = min(1.0, max(0.0, topic.knowledge_level + mastery_delta))
            
            # Auto-complete topic if mastery exceeds threshold
            if topic.knowledge_level >= 0.85:
                topic.is_completed = True
            
            self.db.add(topic)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task_by_id(self, user_id: UUID, task_id: UUID) -> Optional[DailyTask]:
        """Fetch a single task with ownership verification."""
        stmt = (
            select(DailyTask)
            .join(StudyPlan)
            .where(and_(DailyTask.id == task_id, StudyPlan.user_id == user_id))
            .options(selectinload(DailyTask.topic))
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if task and task.topic:
            task.topic_name = task.topic.name
            
        return task

    async def update_task_notes(self, user_id: UUID, task_id: UUID, notes: str) -> Optional[DailyTask]:
        """Update notes for a task without changing status."""
        stmt = (
            select(DailyTask)
            .join(StudyPlan)
            .where(and_(DailyTask.id == task_id, StudyPlan.user_id == user_id))
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return None
            
        task.notes = notes
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update_task_heartbeat(self, user_id: UUID, task_id: UUID, actual_minutes: int) -> Optional[DailyTask]:
        """Update study time for a task without changing status."""
        stmt = (
            select(DailyTask)
            .join(StudyPlan)
            .where(and_(DailyTask.id == task_id, StudyPlan.user_id == user_id))
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return None
            
        task.actual_minutes = actual_minutes
        await self.db.commit()
        await self.db.refresh(task)
        return task
