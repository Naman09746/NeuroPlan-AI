from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, Float, Text, Uuid, func
import uuid
from datetime import datetime
from typing import Optional, List

from app.db.session import Base

class CoachingEvent(Base):
    __tablename__ = "coaching_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("study_plans.id", ondelete="SET NULL"), nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'test_failed', 'task_missed'
    
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority_topics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # List of topic names
    suggested_daily_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    motivational_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship()
    plan: Mapped[Optional["StudyPlan"]] = relationship()
