from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class TopicBase(BaseModel):
    name: str
    difficulty: str = "medium"
    estimated_hours: float = 1.0

class TopicCreate(TopicBase):
    subject_id: Optional[UUID] = None

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[float] = None
    knowledge_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_completed: Optional[bool] = None

class TopicResponse(TopicBase):
    id: UUID
    subject_id: UUID
    knowledge_level: float
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
