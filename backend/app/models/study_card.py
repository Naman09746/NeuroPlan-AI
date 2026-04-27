"""
StudyCard Model: AI-generated learning content for each topic.
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func, DateTime, Text, JSON, Uuid
import uuid
from datetime import datetime
from typing import Optional

from app.db.session import Base


class StudyCard(Base):
    __tablename__ = "study_cards"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), unique=True, index=True
    )

    # AI-generated content
    summary: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # 2-3 sentence overview
    key_concepts: Mapped[dict] = mapped_column(
        JSON, default=[]
    )  # ["concept1", "concept2", ...]
    formulas: Mapped[dict] = mapped_column(
        JSON, default=[]
    )  # ["formula1", "formula2", ...]
    study_tips: Mapped[dict] = mapped_column(
        JSON, default=[]
    )  # ["tip1", "tip2", ...]
    resources: Mapped[dict] = mapped_column(
        JSON, default=[]
    )  # [{"title": "...", "url": "...", "type": "video|article|book"}, ...]
    practice_problems: Mapped[dict] = mapped_column(
        JSON, default=[]
    )  # ["problem1", "problem2", ...]

    # Metadata
    ai_model_used: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    topic: Mapped["Topic"] = relationship(back_populates="study_card")
