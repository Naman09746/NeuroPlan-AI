from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    target_level: str = "intermediate"
    color: str = "#3b82f6"
    sort_order: int = 0

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    target_level: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None

class SubjectResponse(SubjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    topic_count: int = 0

    model_config = ConfigDict(from_attributes=True)
