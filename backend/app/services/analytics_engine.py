from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case
from datetime import date, timedelta, datetime
import statistics

from app.models.daily_task import DailyTask
from app.models.progress_log import ProgressLog
from app.config import settings
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.study_plan import StudyPlan
from app.services.ai_client import AIClient
from app.services.base import BaseService

class AnalyticsService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db, "analytics_service")

    async def get_overview_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Compute top-level summary for the dashboard."""
        # 1. Unified Aggregation: Count Total, Done, and sum time in one pass
        stmt = (
            select(
                func.count(DailyTask.id).label("total"),
                func.sum(case((DailyTask.status == "done", 1), else_=0)).label("done"),
                func.sum(DailyTask.actual_minutes).label("total_minutes")
            )
            .join(DailyTask.plan)
            .where(StudyPlan.user_id == user_id)
        )
        
        res = await self.db.execute(stmt)
        row = res.one()
        
        total_tasks = row.total or 0
        completed_tasks = row.done or 0
        total_minutes = row.total_minutes or 0

        completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
        
        # 2. AI Coaching Insights (Cached or generated)
        from app.services.performance_coach import PerformanceCoach
        coach = PerformanceCoach(self.db)
        # Fetch most recent coaching session or generate a quick summary
        insights = await coach.get_performance_summary(user_id)

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
            "total_hours": round(total_minutes / 60, 1),
            "streak": await self._calculate_current_streak(user_id),
            "insights": insights
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
        """Get aggregate knowledge levels across subjects with Forgetting Curve decay."""
        from app.services.ml.mastery_engine import ForgettingCurve
        
        stmt = (
            select(
                Subject.name,
                Topic.knowledge_level,
                Topic.stability,
                Topic.last_reviewed_at
            )
            .join(Topic, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # Aggregate manually to apply decay to each topic first
        subject_mastery: Dict[str, List[float]] = {}
        now = datetime.now(rows[0].last_reviewed_at.tzinfo) if rows and rows[0].last_reviewed_at else datetime.now()
        
        for row in rows:
            knowledge = row.knowledge_level
            if row.last_reviewed_at:
                days_passed = (now - row.last_reviewed_at).total_seconds() / 86400
                retention = ForgettingCurve.compute_retention(days_passed, row.stability)
                knowledge *= retention
            
            if row.name not in subject_mastery:
                subject_mastery[row.name] = []
            subject_mastery[row.name].append(knowledge)
        
        return [
            {
                "subject": name,
                "mastery": round((sum(levels) / len(levels)) * 100, 1) if levels else 0
            }
            for name, levels in subject_mastery.items()
        ]

    async def get_goal_progress(self, user_id: UUID) -> Dict[str, Any]:
        """Calculate daily and weekly goal completion percentage."""
        from app.models.user import User
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        
        if not user: return {}
        
        # Default goals if not set
        daily_goal_mins = user.preferences.get("daily_goal_hours", 2) * 60
        weekly_goal_mins = daily_goal_mins * 5 # Assuming 5 days a week target
        
        # Today's Progress
        today = date.today()
        stmt_today = (
            select(func.sum(DailyTask.actual_minutes))
            .join(DailyTask.plan)
            .where(and_(
                StudyPlan.user_id == user_id,
                DailyTask.scheduled_date == today,
                DailyTask.status == "done"
            ))
        )
        res_today = await self.db.execute(stmt_today)
        actual_today = res_today.scalar() or 0
        
        # Weekly Progress (last 7 days)
        start_week = today - timedelta(days=6)
        stmt_week = (
            select(func.sum(DailyTask.actual_minutes))
            .join(DailyTask.plan)
            .where(and_(
                StudyPlan.user_id == user_id,
                DailyTask.scheduled_date >= start_week,
                DailyTask.status == "done"
            ))
        )
        res_week = await self.db.execute(stmt_week)
        actual_week = res_week.scalar() or 0
        
        return {
            "daily": {
                "actual": actual_today,
                "goal": daily_goal_mins,
                "percentage": min(100, round((actual_today / daily_goal_mins * 100), 1)) if daily_goal_mins > 0 else 0
            },
            "weekly": {
                "actual": actual_week,
                "goal": weekly_goal_mins,
                "percentage": min(100, round((actual_week / weekly_goal_mins * 100), 1)) if weekly_goal_mins > 0 else 0
            }
        }

    async def get_countdown(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Calculate days remaining until the target exam/deadline."""
        from app.models.user import User
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        
        if not user or not user.preferences.get("target_exam_date"):
            return None
            
        try:
            target_date = date.fromisoformat(user.preferences["target_exam_date"])
            today = date.today()
            days_left = (target_date - today).days
            
            return {
                "label": user.preferences.get("exam_label", "Target Exam"),
                "days_remaining": max(0, days_left),
                "is_urgent": days_left < 7 and days_left >= 0,
                "target_date": target_date.isoformat()
            }
        except Exception:
            return None

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
