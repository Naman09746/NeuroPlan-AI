from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services.subject_service import SubjectService
from app.models.user import User
from app.models.subject import Subject

router = APIRouter()

@router.get("/", response_model=List[SubjectResponse])
async def read_subjects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """List all subjects for the current user."""
    service = SubjectService(db)
    return await service.get_all_for_user(current_user.id)

@router.post("/", response_model=SubjectResponse)
async def create_subject(
    *,
    db: AsyncSession = Depends(get_db),
    subject_in: SubjectCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new subject."""
    service = SubjectService(db)
    return await service.create_for_user(current_user.id, subject_in)

@router.put("/{id}", response_model=SubjectResponse)
async def update_subject(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    subject_in: SubjectUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update a subject."""
    service = SubjectService(db)
    subject = await service.update_safe(current_user.id, id, subject_in)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.delete("/{id}")
async def delete_subject(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a subject (with ownership check). Cascade deletes all child topics."""
    stmt = select(Subject).where(Subject.id == id, Subject.user_id == current_user.id)
    result = await db.execute(stmt)
    subject = result.scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    await db.delete(subject)
    await db.commit()
    return {"detail": "Subject deleted successfully"}

