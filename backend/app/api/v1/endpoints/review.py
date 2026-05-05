from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services.review_service import ReviewService

router = APIRouter()

@router.get("/due")
async def get_due_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    threshold: float = 0.8
) -> Any:
    """Get the list of topics due for review based on spaced repetition."""
    service = ReviewService(db)
    return await service.get_due_topics(current_user.id, threshold=threshold)
