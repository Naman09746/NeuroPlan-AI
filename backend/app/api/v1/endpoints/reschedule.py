from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.services.adaptive_scheduler import AdaptiveSchedulerService
from app.models.user import User

router = APIRouter()

@router.post("/{id}/reschedule")
async def trigger_reschedule(
    id: UUID,
    reason: str = "Missed sessions",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Manually trigger the intelligent recovery engine.
    Used when a user knows they won't be able to study today or wants to catch up.
    """
    service = AdaptiveSchedulerService(db)
    success = await service.trigger_reschedule(id, current_user.id, reason)
    
    if not success:
        return {"status": "no_changes_needed", "detail": "No missed or partial tasks found."}
        
    return {"status": "success", "detail": "Schedule reorganized successfully."}
