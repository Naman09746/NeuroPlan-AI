from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel

from app.api import deps
from app.db.session import get_db
from app.services.test_service import TestService
from app.models.user import User
from app.models.topic import Topic

router = APIRouter()

class TestSubmission(BaseModel):
    topic_id: UUID
    correct_count: int
    total_count: int
    time_seconds: int
    questions_data: List[Dict[str, Any]]

@router.get("/generate/{topic_id}", response_model=Dict[str, Any])
async def generate_test(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Initialize a cognitive assessment for a specific topic."""
    service = TestService(db)
    try:
        return await service.generate_mock_test(current_user.id, topic_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/submit", response_model=Dict[str, Any])
async def submit_test(
    submission: TestSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Submit assessment results to update neural mastery levels."""
    service = TestService(db)
    session = await service.submit_test_result(
        user_id=current_user.id,
        topic_id=submission.topic_id,
        correct_count=submission.correct_count,
        total_count=submission.total_count,
        time_seconds=submission.time_seconds,
        questions_data=submission.questions_data
    )
    return {
        "session_id": session.id,
        "score_percentage": session.score_percentage,
        "new_mastery": (await db.get(Topic, submission.topic_id)).knowledge_level
    }

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_test_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve historical assessment performance."""
    service = TestService(db)
    history = await service.get_user_test_history(current_user.id)
    # Simple formatting for response
    return [
        {
            "id": h.id,
            "topic_id": h.topic_id,
            "score": round(h.score_percentage * 100, 1),
            "taken_at": h.taken_at
        }
        for h in history
    ]
