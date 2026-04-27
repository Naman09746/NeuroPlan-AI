from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, ForeignKey, func, DateTime, Text, Index, CheckConstraint, Uuid
import uuid
from datetime import datetime, date
from typing import List, Optional

from app.db.session import Base

class DailyTask(Base):
    __tablename__ = "daily_tasks"

    __table_args__ = (
        CheckConstraint("planned_minutes > 0", name="check_minutes_positive"),
        Index("idx_plan_date", "plan_id", "scheduled_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("study_plans.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    
    scheduled_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    
    # enum: study|revision|test|practice
    task_type: Mapped[str] = mapped_column(String(50), default="study")
    
    planned_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # enum: pending|done|skipped|partial
    status: Mapped[str] = mapped_column(String(50), default="pending")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    plan: Mapped["StudyPlan"] = relationship(back_populates="daily_tasks")
    topic: Mapped["Topic"] = relationship(back_populates="daily_tasks")
    progress_logs: Mapped[List["ProgressLog"]] = relationship(back_populates="task", cascade="all, delete-orphan")

# Performance Optimization Notes: idx_plan_date is handled in __table_args__
