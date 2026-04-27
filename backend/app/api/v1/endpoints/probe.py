"""
Knowledge Probing API.
GET /probe/{topic_id} — Generate 3 quick verification questions.
POST /probe/{task_id}/result — Submit probe results, auto-update mastery.
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.models.topic import Topic
from app.models.daily_task import DailyTask
from app.services.ai_client import AIClient
from pydantic import BaseModel

router = APIRouter()


class ProbeResult(BaseModel):
    task_id: UUID
    correct_count: int
    total_count: int


@router.get("/{topic_id}")
async def generate_probe(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Generate 3 quick verification questions for a topic."""
    stmt = select(Topic).where(Topic.id == topic_id)
    result = await db.execute(stmt)
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Verify access would be through subject ownership usually
    # For now, simplistic

    ai = AIClient()
    questions = await ai.generate_probe_questions(topic.name, num_questions=3)
    return {
        "topic_id": str(topic_id),
        "topic_name": topic.name,
        "questions": questions,
    }


@router.post("/result")
async def submit_probe_result(
    result_in: ProbeResult,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Process probe results:
    - If score >= 67% (2/3): Keep task as 'done', boost knowledge_level
    - If score < 67%: Mark task as 'partial', knowledge_level stays low
    """
    stmt = select(DailyTask).where(DailyTask.id == result_in.task_id)
    task_res = await db.execute(stmt)
    task = task_res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    score = result_in.correct_count / result_in.total_count if result_in.total_count > 0 else 0

    # Update topic knowledge level
    topic_stmt = select(Topic).where(Topic.id == task.topic_id)
    topic_res = await db.execute(topic_stmt)
    topic = topic_res.scalar_one_or_none()

    if score >= 0.67:
        # Passed! Keep as done, boost mastery
        task.status = "done"
        if topic:
            topic.knowledge_level = min(1.0, topic.knowledge_level + 0.15)
            topic.is_completed = (topic.knowledge_level >= 0.95)
        verdict = "passed"
    else:
        # Failed! Mark as partial — triggers rescheduling
        task.status = "partial"
        if topic:
            topic.knowledge_level = max(0.0, topic.knowledge_level - 0.05)
        verdict = "failed"

    await db.commit()

    return {
        "verdict": verdict,
        "score": round(score * 100, 1),
        "new_status": task.status,
        "new_mastery": round(topic.knowledge_level * 100, 1) if topic else 0,
        "message": "Great understanding!" if verdict == "passed" else "This topic needs more review. We've rescheduled it for you."
    }
