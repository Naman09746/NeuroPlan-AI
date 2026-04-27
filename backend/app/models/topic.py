from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Boolean, ForeignKey, func, DateTime, CheckConstraint, Uuid, Integer, JSON
import uuid
from datetime import datetime
from typing import List, Optional

from app.db.session import Base

class Topic(Base):
    __tablename__ = "topics"

    __table_args__ = (
        CheckConstraint("knowledge_level >= 0.0 AND knowledge_level <= 1.0", name="check_knowledge_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # enum: easy|medium|hard
    difficulty: Mapped[str] = mapped_column(String(50), default="medium")
    estimated_hours: Mapped[float] = mapped_column(Float, default=1.0)
    knowledge_level: Mapped[float] = mapped_column(Float, default=0.0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Knowledge Graph Metadata
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    prerequisites: Mapped[dict] = mapped_column(JSON, default=[], server_default='[]')
    key_concepts: Mapped[dict] = mapped_column(JSON, default=[], server_default='[]')

    # Relationships
    subject: Mapped["Subject"] = relationship(back_populates="topics")
    daily_tasks: Mapped[List["DailyTask"]] = relationship(back_populates="topic")
    study_card: Mapped[Optional["StudyCard"]] = relationship(
        back_populates="topic", uselist=False, cascade="all, delete-orphan"
    )
    # test_sessions relationship will be added in later phase
