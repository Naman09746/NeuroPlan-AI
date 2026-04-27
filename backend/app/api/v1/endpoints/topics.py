from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.schemas.topic import TopicCreate, TopicResponse, TopicUpdate
from app.services.topic_service import TopicService
from app.models.user import User

router = APIRouter()

@router.get("/subject/{subject_id}", response_model=List[TopicResponse])
async def read_topics(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """List all topics for a specific subject."""
    service = TopicService(db)
    return await service.get_all_for_subject(current_user.id, subject_id)

@router.post("/bulk/{subject_id}", response_model=List[TopicResponse])
async def bulk_create_topics(
    *,
    db: AsyncSession = Depends(get_db),
    subject_id: UUID,
    topics_in: List[TopicCreate],
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Bulk create topics for a subject (Onboarding Wizard)."""
    service = TopicService(db)
    try:
        return await service.create_bulk(current_user.id, subject_id, topics_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}/status", response_model=TopicResponse)
async def update_topic_status(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    is_completed: bool,
    knowledge_level: float = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update progress and knowledge level for a topic."""
    service = TopicService(db)
    topic = await service.update_status(id, is_completed, knowledge_level)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.post("/decompose/{subject_id}", response_model=List[TopicResponse])
async def ai_decompose_subject(
    *,
    db: AsyncSession = Depends(get_db),
    subject_id: UUID,
    context: str = "",
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    AI-powered subject decomposition.
    Takes a subject name and uses LLM to generate all subtopics
    with difficulty, time estimates, and learning order.
    """
    from app.services.decomposition_service import DecompositionService

    service = DecompositionService(db)
    try:
        topics = await service.decompose_subject(
            current_user.id, subject_id, context
        )
        return topics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
