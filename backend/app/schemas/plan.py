from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List, Any

class PlanBase(BaseModel):
    title: str
    start_date: date
    end_date: date
    daily_hours: float

class PlanCreate(PlanBase):
    subject_ids: List[UUID]
    config: Optional[dict[str, Any]] = None

class PlanUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    version: Optional[int] = None

class PlanResponse(PlanBase):
    id: UUID
    user_id: UUID
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
