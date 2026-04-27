from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case
from datetime import date, timedelta, datetime
import statistics

from app.models.daily_task import DailyTask
from app.models.progress_log import ProgressLog
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.study_plan import StudyPlan
from app.services.base import BaseService

class AnalyticsService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db, "analytics_service")

    async def get_overview_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Compute top-level summary for the dashboard."""
        # Total tasks across all plans
        stmt = select(func.count(DailyTask.id)).join(DailyTask.plan).where(StudyPlan.user_id == user_id)
        total_res = await self.db.execute(stmt)
        total_tasks = total_res.scalar() or 0

        # Completed tasks
        stmt_done = stmt.where(DailyTask.status == "done")
        done_res = await self.db.execute(stmt_done)
        completed_tasks = done_res.scalar() or 0

        # Calculation
        completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
        
        # Total time spent
        stmt_time = select(func.sum(DailyTask.actual_minutes)).join(DailyTask.plan).where(StudyPlan.user_id == user_id)
        time_res = await self.db.execute(stmt_time)
        total_minutes = time_res.scalar() or 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
            "total_hours": round(total_minutes / 60, 1),
            "streak": await self._calculate_current_streak(user_id)
        }

    async def get_efficiency_trends(self, user_id: UUID, days: int = 30) -> List[Dict[str, Any]]:
        """Calculate daily completion rate for the trend chart."""
        start_date = date.today() - timedelta(days=days)
        
        # Query: Date, Count Total, Count Done (using CASE for SQLite compatibility)
        stmt = (
            select(
                DailyTask.scheduled_date,
                func.count(DailyTask.id).label("total"),
                func.count(case((DailyTask.status == "done", 1))).label("done")
            )
            .join(DailyTask.plan)
            .where(and_(StudyPlan.user_id == user_id, DailyTask.scheduled_date >= start_date))
            .group_by(DailyTask.scheduled_date)
            .order_by(DailyTask.scheduled_date)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        trends = []
        for row in rows:
            trends.append({
                "date": row.scheduled_date.isoformat(),
                "completion_rate": round((row.done / row.total * 100), 1) if row.total > 0 else 0,
                "tasks_done": row.done
            })
            
        # Fill missing dates with 0
        all_dates = [start_date + timedelta(days=x) for x in range(days + 1)]
        date_map = {t["date"]: t for t in trends}
        
        return [
            date_map.get(d.isoformat(), {"date": d.isoformat(), "completion_rate": 0, "tasks_done": 0})
            for d in all_dates
        ]

    async def get_subject_distribution(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Calculate cognitive load (time) per subject."""
        stmt = (
            select(
                Subject.name,
                Subject.color,
                func.sum(DailyTask.planned_minutes).label("minutes")
            )
            .join(Topic, Topic.subject_id == Subject.id)
            .join(DailyTask, DailyTask.topic_id == Topic.id)
            .where(Subject.user_id == user_id)
            .group_by(Subject.id)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        total_mins = sum(r.minutes for r in rows) if rows else 0
        
        return [
            {
                "subject": r.name,
                "color": r.color,
                "minutes": r.minutes,
                "percentage": round((r.minutes / total_mins * 100), 1) if total_mins > 0 else 0
            }
            for r in rows
        ]

    async def get_knowledge_heatmap(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get aggregate knowledge levels across subjects."""
        stmt = (
            select(
                Subject.name,
                func.avg(Topic.knowledge_level).label("avg_knowledge")
            )
            .join(Topic, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
            .group_by(Subject.id)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        return [
            {
                "subject": r.name,
                "mastery": round(r.avg_knowledge * 100, 1) if r.avg_knowledge is not None else 0
            }
            for r in rows
        ]

    async def _calculate_current_streak(self, user_id: UUID) -> int:
        """Calculate consecutive days of study activity."""
        # Use DailyTask completed_at to find active days
        stmt = (
            select(func.date(DailyTask.completed_at))
            .join(DailyTask.plan)
            .where(and_(
                StudyPlan.user_id == user_id,
                DailyTask.status == "done",
                DailyTask.completed_at.isnot(None)
            ))
            .distinct()
            .order_by(desc(func.date(DailyTask.completed_at)))
        )
        
        result = await self.db.execute(stmt)
        # SQLite returns strings for func.date, convert to date objects
        raw_rows = [row[0] for row in result.all()]
        dates = []
        for r in raw_rows:
            if isinstance(r, str):
                dates.append(date.fromisoformat(r))
            else:
                dates.append(r)
        
        if not dates: return 0
        
        streak = 0
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # If no activity today OR yesterday, streak is broken
        if dates[0] < yesterday:
            return 0
            
        current_check = dates[0]
        for d in dates:
            if d == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            else:
                break
        return streak
