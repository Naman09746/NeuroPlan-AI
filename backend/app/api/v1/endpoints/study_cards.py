"""
Study Cards API endpoints.
GET: Lazy-loads (generates if missing) a study card for a topic.
POST /regenerate: Force regenerate with fresh AI content.
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services.study_card_service import StudyCardService

router = APIRouter()


@router.get("/{topic_id}")
async def get_study_card(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get (or auto-generate) a study card for a topic."""
    service = StudyCardService(db)
    card = await service.get_or_generate(topic_id, current_user.id)
    if not card:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {
        "id": str(card.id),
        "topic_id": str(card.topic_id),
        "summary": card.summary,
        "key_concepts": card.key_concepts,
        "formulas": card.formulas,
        "study_tips": card.study_tips,
        "resources": card.resources,
        "practice_problems": card.practice_problems,
        "generated_at": card.generated_at.isoformat(),
    }


@router.post("/{topic_id}/regenerate")
async def regenerate_study_card(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Force regenerate a study card with fresh AI content."""
    service = StudyCardService(db)
    card = await service.regenerate(topic_id, current_user.id)
    if not card:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {
        "id": str(card.id),
        "topic_id": str(card.topic_id),
        "summary": card.summary,
        "key_concepts": card.key_concepts,
        "formulas": card.formulas,
        "study_tips": card.study_tips,
        "resources": card.resources,
        "practice_problems": card.practice_problems,
        "generated_at": card.generated_at.isoformat(),
    }
