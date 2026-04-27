from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func, DateTime, Text, JSON, Uuid
import uuid
from datetime import datetime

from app.db.session import Base

class RescheduleEvent(Base):
    __tablename__ = "reschedule_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("study_plans.id", ondelete="CASCADE"), index=True)
    
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    changes_applied: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    plan: Mapped["StudyPlan"] = relationship(back_populates="reschedule_events")
