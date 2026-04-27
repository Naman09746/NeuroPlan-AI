from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api import deps
from app.db.session import get_db
from app.schemas.task import TaskResponse, TaskStatusUpdate
from app.services.execution_tracker import ExecutionTrackerService
from app.models.user import User

router = APIRouter()

@router.get("/today/{plan_id}", response_model=List[TaskResponse])
async def read_today_tasks(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get tasks scheduled for today in the active plan."""
    service = ExecutionTrackerService(db)
    return await service.get_today_tasks(current_user.id, plan_id)

@router.put("/{id}/progress", response_model=TaskResponse)
async def update_task_progress(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    update_in: TaskStatusUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Mark a task as done, skipped, or partial and log study time."""
    service = ExecutionTrackerService(db)
    task = await service.update_task_progress(current_user.id, id, update_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
