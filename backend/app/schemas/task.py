from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Optional

class TaskBase(BaseModel):
    scheduled_date: date
    task_type: str = "study"
    planned_minutes: int
    sort_order: int = 0

class TaskStatusUpdate(BaseModel):
    status: str
    actual_minutes: Optional[int] = None
    notes: Optional[str] = None

class TaskResponse(TaskBase):
    id: UUID
    plan_id: UUID
    topic_id: UUID
    topic_name: Optional[str] = None
    actual_minutes: Optional[int]
    status: str
    notes: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
