"""
Smart Onboarding: One-shot subject + topic creation.
POST /onboarding/quick-setup — Takes a subject name, creates Subject + AI-decomposed Topics.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.models.subject import Subject
from app.services.decomposition_service import DecompositionService

router = APIRouter()


class QuickSetupRequest(BaseModel):
    subject_name: str
    color: str = "#6366f1"
    context: str = ""  # e.g., "VTU 5th semester", "Beginner level"
    career_goal: Optional[str] = None
    target_exam_date: Optional[str] = None # ISO format YYYY-MM-DD


class QuickSetupResponse(BaseModel):
    subject_id: str
    subject_name: str
    topics_count: int
    message: str


@router.post("/quick-setup", response_model=QuickSetupResponse)
async def quick_setup(
    *,
    db: AsyncSession = Depends(get_db),
    setup_in: QuickSetupRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    One-shot onboarding:
    1. Create Subject from name
    2. AI-decompose into subtopics
    3. Return summary
    """
    # 1. Create Subject
    subject = Subject(
        user_id=current_user.id,
        name=setup_in.subject_name,
        color=setup_in.color,
    )
    db.add(subject)
    
    # Update User Preferences if provided
    new_prefs = {**current_user.preferences}
    if setup_in.career_goal:
        new_prefs["career_goal"] = setup_in.career_goal
    if setup_in.target_exam_date:
        new_prefs["target_exam_date"] = setup_in.target_exam_date
    current_user.preferences = new_prefs
    db.add(current_user)
    
    await db.flush()

    # 2. AI Decompose
    decomp_service = DecompositionService(db)
    try:
        topics = await decomp_service.decompose_subject(
            current_user.id, subject.id, setup_in.context
        )
    except ValueError as e:
        # If AI fails, keep the subject but report no topics
        await db.commit()
        return QuickSetupResponse(
            subject_id=str(subject.id),
            subject_name=subject.name,
            topics_count=0,
            message=f"Subject created but AI decomposition failed: {str(e)}. Add topics manually."
        )

    await db.commit()

    return QuickSetupResponse(
        subject_id=str(subject.id),
        subject_name=subject.name,
        topics_count=len(topics),
        message=f"Successfully created '{subject.name}' with {len(topics)} AI-generated subtopics!"
    )
