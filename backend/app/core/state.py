from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from typing import List, Optional, Dict, Any

class StateTask(BaseModel):
    """Immutable snapshot of a task within the state transition."""
    id: Optional[UUID] = None
    topic_id: UUID
    scheduled_date: date
    planned_minutes: int
    task_type: str
    priority_score: float = 0.0

class PlanState(BaseModel):
    """
    The Central Data Contract for the NeuroPlan Engine.
    Mirroring the 'PipelineState' from the AMA2 project.
    
    This object is used to pass the current plan's status to the AI
    and the Rescheduler, ensuring we have a 'Trial Run' of changes
    before updating the main database.
    """
    plan_id: UUID
    user_id: UUID
    deadline: date
    daily_hours_limit: float
    
    # Internal representation of the schedule
    tasks: List[StateTask]
    
    # Audit trail for the current transition
    changes_suggested: List[Dict[str, Any]] = []
    conflict_detected: bool = False
    rationale: Optional[str] = None
    
    def get_tasks_for_date(self, target_date: date) -> List[StateTask]:
        return [t for t in self.tasks if t.scheduled_date == target_date]

    def calculate_daily_load(self, target_date: date) -> int:
        return sum(t.planned_minutes for t in self.get_tasks_for_date(target_date))
