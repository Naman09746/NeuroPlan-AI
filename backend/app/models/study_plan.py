from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Date, ForeignKey, func, DateTime, Integer, JSON, Uuid
import uuid
from datetime import datetime, date
from typing import List

from app.db.session import Base

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False) # The Deadline
    daily_hours: Mapped[float] = mapped_column(Float, nullable=False)
    
    # enum: draft|active|completed|archived
    status: Mapped[str] = mapped_column(String(50), default="active")
    config: Mapped[dict] = mapped_column(JSON, default={}, server_default='{}')
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="plans")
    daily_tasks: Mapped[List["DailyTask"]] = relationship(back_populates="plan", cascade="all, delete-orphan")
    reschedule_events: Mapped[List["RescheduleEvent"]] = relationship(back_populates="plan", cascade="all, delete-orphan")
