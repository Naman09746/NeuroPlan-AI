from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.daily_task import DailyTask
from app.models.study_plan import StudyPlan
from app.models.reschedule_event import RescheduleEvent
from app.core.constants import STATUS_PENDING, STATUS_SKIPPED, STATUS_PARTIAL

class AdaptiveSchedulerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_plan_daily_density(self, plan_id: UUID) -> Dict[date, int]:
        """Calculate the current minute-load for every day in the plan."""
        stmt = select(
            DailyTask.scheduled_date, 
            func.sum(DailyTask.planned_minutes)
        ).where(DailyTask.plan_id == plan_id).group_by(DailyTask.scheduled_date)
        
        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def trigger_reschedule(self, plan_id: UUID, user_id: UUID, reason: str) -> bool:
        """
        The Intelligent Elastic Rescheduler.
        Redistributes missed tasks into future 'low-density' days.
        """
        # 1. Fetch Plan & Capacity with user verification
        stmt = select(StudyPlan).where(and_(StudyPlan.id == plan_id, StudyPlan.user_id == user_id))
        res = await self.db.execute(stmt)
        plan = res.scalar_one_or_none()
        if not plan: return False
        
        daily_limit_mins = plan.daily_hours * 60
        today = date.today()

        # 2. Fetch Missed Tasks
        missed_stmt = select(DailyTask).where(
            and_(
                DailyTask.plan_id == plan_id, 
                DailyTask.scheduled_date <= today,
                DailyTask.status.in_([STATUS_SKIPPED, STATUS_PARTIAL])
            )
        )
        missed_res = await self.db.execute(missed_stmt)
        missed_tasks = list(missed_res.scalars().all())
        if not missed_tasks: return False

        # 3. Get Current Density
        density = await self.get_plan_daily_density(plan_id)
        
        changes = []
        for task in missed_tasks:
            # Search for a future day with capacity
            search_date = today + timedelta(days=1)
            found_slot = False
            
            while search_date <= plan.end_date:
                current_load = density.get(search_date, 0)
                if current_load + task.planned_minutes <= daily_limit_mins:
                    # Found a slot!
                    old_date = task.scheduled_date
                    task.scheduled_date = search_date
                    task.status = STATUS_PENDING
                    
                    # Update internal density tracker
                    density[search_date] = current_load + task.planned_minutes
                    
                    changes.append({
                        "task_id": str(task.id),
                        "old_date": str(old_date),
                        "new_date": str(search_date)
                    })
                    found_slot = True
                    break
                search_date += timedelta(days=1)
            
            if not found_slot:
                # Deadline breach! Force shift into the last day or suggest extension
                changes.append({"warning": f"Task {task.id} could not fit before deadline."})

        # 4. Finalize version and audit log
        plan.version += 1
        event = RescheduleEvent(
            plan_id=plan_id,
            reason=reason,
            changes_applied={"rescheduled_tasks": changes}
        )
        self.db.add(event)
        
        await self.db.commit()
        return True
