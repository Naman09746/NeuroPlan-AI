from typing import Any, List, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.services.analytics_engine import AnalyticsService
from app.models.user import User

router = APIRouter()

@router.get("/overview", response_model=Dict[str, Any])
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get high-level statistics for the dashboard/analytics page."""
    service = AnalyticsService(db)
    return await service.get_overview_stats(current_user.id)

@router.get("/trends", response_model=List[Dict[str, Any]])
async def get_efficiency_trends(
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get daily completion rates for trend visualization."""
    service = AnalyticsService(db)
    return await service.get_efficiency_trends(current_user.id, days)

@router.get("/distribution", response_model=List[Dict[str, Any]])
async def get_subject_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get cognitive load distribution across subjects."""
    service = AnalyticsService(db)
    return await service.get_subject_distribution(current_user.id)

@router.get("/mastery", response_model=List[Dict[str, Any]])
async def get_knowledge_heatmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get average mastery levels per subject."""
    service = AnalyticsService(db)
    return await service.get_knowledge_heatmap(current_user.id)
