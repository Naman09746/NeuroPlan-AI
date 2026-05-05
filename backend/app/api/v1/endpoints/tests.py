from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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

class VerbalSubmission(BaseModel):
    topic_id: UUID
    question: str
    user_answer: str
    key_points: List[str]

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
    background_tasks: BackgroundTasks,
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
    from app.services.performance_coach import PerformanceCoach
    coach = PerformanceCoach(db)
    # Trigger adaptive feedback in background
    background_tasks.add_task(
        coach.on_test_completed,
        user_id=current_user.id,
        topic_id=submission.topic_id,
        score=session.score_percentage
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

@router.get("/generate-weekly", response_model=Dict[str, Any])
async def generate_weekly_test(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Generate a Tier 3: Weekly Interleaved Review test."""
    service = TestService(db)
    try:
        return await service.generate_weekly_test(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/generate-crucible/{subject_id}", response_model=Dict[str, Any])
async def generate_crucible_exam(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Generate a Tier 4: Subject-wide Crucible Mock Exam."""
    service = TestService(db)
    try:
        return await service.generate_crucible_exam(current_user.id, subject_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/evaluate-verbal", response_model=Dict[str, Any])
async def evaluate_verbal(
    submission: VerbalSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Submit a verbal interview answer for AI evaluation and mastery update."""
    service = TestService(db)
    evaluation = await service.evaluate_verbal_answer(
        user_id=current_user.id,
        topic_id=submission.topic_id,
        question=submission.question,
        user_answer=submission.user_answer,
        key_points=submission.key_points
    )
    return evaluation

