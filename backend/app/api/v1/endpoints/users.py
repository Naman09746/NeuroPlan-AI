from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_password_hash

router = APIRouter()

class PreferenceUpdate(BaseModel):
    """Specific schema for NeuroPlan study preferences."""
    daily_hours: Optional[float] = Field(None, ge=1, le=16)
    revision_strategy: Optional[str] = Field(None, pattern="^(standard|aggressive|relaxed)$")
    theme: Optional[str] = None
    timezone: Optional[str] = None
    learning_style: Optional[str] = None
    focus_metabolism: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    privacy_mode: Optional[bool] = None

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get current user details and preferences."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update profile details (name, email)."""
    if user_in.password:
        current_user.password_hash = get_password_hash(user_in.password)
    if user_in.name:
        current_user.name = user_in.name
    if user_in.email:
        current_user.email = user_in.email
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.put("/me/preferences", response_model=UserResponse)
async def update_preferences(
    *,
    db: AsyncSession = Depends(get_db),
    prefs: PreferenceUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update specialized NeuroPlan study preferences.
    This ensures that daily_hours and strategies are within valid bounds.
    """
    current_prefs = dict(current_user.preferences or {})
    update_data = prefs.model_dump(exclude_unset=True)
    
    # Merge and update
    current_prefs.update(update_data)
    current_user.preferences = current_prefs
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.delete("/me/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_history(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Wipe all neural history (progress logs and test sessions)."""
    from sqlalchemy import delete
    from app.models.progress_log import ProgressLog
    from app.models.test_session import TestSession
    
    await db.execute(delete(ProgressLog).where(ProgressLog.user_id == current_user.id))
    await db.execute(delete(TestSession).where(TestSession.user_id == current_user.id))
    
    await db.commit()
    return None
