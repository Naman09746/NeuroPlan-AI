from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, func, DateTime, Uuid, Boolean
import uuid
from datetime import datetime
from typing import List, Optional

from app.db.session import Base

class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_level: Mapped[str] = mapped_column(String(50), default="intermediate") # beginner, intermediate, advanced, expert
    color: Mapped[str] = mapped_column(String(50), default="#3b82f6") # Default Tailwind Blue
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_decomposing: Mapped[bool] = mapped_column(Boolean, default=False)
    last_decomposed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="subjects")
    topics: Mapped[List["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")
