from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.models.coaching_event import CoachingEvent

router = APIRouter()

@router.get("/notifications")
async def get_coaching_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = 5
) -> Any:
    """Fetch recent coaching notifications for the user."""
    stmt = (
        select(CoachingEvent)
        .where(CoachingEvent.user_id == current_user.id)
        .order_by(CoachingEvent.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    return [
        {
            "id": str(e.id),
            "trigger_type": e.trigger_type,
            "message": e.message,
            "priority_topics": e.priority_topics,
            "suggested_daily_hours": e.suggested_daily_hours,
            "motivational_note": e.motivational_note,
            "is_read": e.is_read,
            "created_at": e.created_at
        }
        for e in events
    ]

@router.post("/notifications/{event_id}/read")
async def mark_notification_read(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Mark a coaching notification as read."""
    stmt = (
        update(CoachingEvent)
        .where((CoachingEvent.id == event_id) & (CoachingEvent.user_id == current_user.id))
        .values(is_read=True)
    )
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}
