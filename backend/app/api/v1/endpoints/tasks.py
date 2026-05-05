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

@router.get("/week/{plan_id}", response_model=List[TaskResponse])
async def read_week_tasks(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get tasks for the next 7 days in the specific plan."""
    service = ExecutionTrackerService(db)
    return await service.get_week_tasks(current_user.id, plan_id)

@router.patch("/{id}/heartbeat", response_model=TaskResponse)
async def update_task_heartbeat(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    actual_minutes: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update study time heartbeat without completing the task."""
    service = ExecutionTrackerService(db)
    task = await service.update_task_heartbeat(current_user.id, id, actual_minutes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    return task

@router.patch("/{id}/notes", response_model=TaskResponse)
async def update_task_notes(
    *,
    db: AsyncSession = Depends(get_db),
    id: UUID,
    notes: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update study notes for a task."""
    service = ExecutionTrackerService(db)
    task = await service.update_task_notes(current_user.id, id, notes)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    return task

@router.get("/{id}", response_model=TaskResponse)
async def read_task(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve a single task by ID with ownership verification."""
    service = ExecutionTrackerService(db)
    task = await service.get_task_by_id(current_user.id, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    return task

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
