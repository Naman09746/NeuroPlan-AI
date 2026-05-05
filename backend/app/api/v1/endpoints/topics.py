from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.core.limiter import limiter

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
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all topics for a specific subject (Paginated)."""
    service = TopicService(db)
    return await service.get_all_for_subject(current_user.id, subject_id, skip=skip, limit=limit)

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

@router.post("/decompose/{subject_id}")
@limiter.limit("2/minute")
async def ai_decompose_subject(
    subject_id: UUID,
    background_tasks: BackgroundTasks,
    request: Request,
    context: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    AI-powered subject decomposition (Background).
    """
    from fastapi import BackgroundTasks
    from app.services.decomposition_service import DecompositionService

    service = DecompositionService(db)
    
    # 1. Start background task
    background_tasks.add_task(
        service.decompose_subject_task, 
        current_user.id, 
        subject_id, 
        context
    )
    
    return {"detail": "Decomposition started in background", "subject_id": str(subject_id)}

@router.get("/decompose/{subject_id}/status")
async def get_decomposition_status(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Poll the status of subject decomposition."""
    from app.models.subject import Subject
    stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == current_user.id)
    result = await db.execute(stmt)
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return {
        "subject_id": str(subject.id),
        "is_decomposing": subject.is_decomposing,
        "last_decomposed_at": subject.last_decomposed_at.isoformat() if subject.last_decomposed_at else None
    }

@router.get("/graph/{subject_id}")
async def get_subject_knowledge_graph(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get nodes and edges for the subject's knowledge graph."""
    service = TopicService(db)
    return await service.get_knowledge_graph(current_user.id, subject_id)
