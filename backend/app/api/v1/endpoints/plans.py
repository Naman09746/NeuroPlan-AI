from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid

from app.api import deps
from app.db.session import get_db
from app.schemas.plan import PlanCreate, PlanResponse
from app.models.user import User
from app.models.topic import Topic
from app.models.subject import Subject
from app.models.study_plan import StudyPlan
from app.models.daily_task import DailyTask
from app.services.plan_generator import PlanGeneratorService
from app.services.ai_client import AIClient

router = APIRouter()

@router.get("/", response_model=List[PlanResponse])
async def read_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = 10,
) -> Any:
    """Retrieve all study plans for the authenticated user."""
    stmt = select(StudyPlan).where(StudyPlan.user_id == current_user.id).order_by(StudyPlan.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.post("/generate", response_model=PlanResponse)
async def generate_plan(
    *,
    db: AsyncSession = Depends(get_db),
    plan_in: PlanCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate a new optimized study plan using AI + Algorithms.
    1. Verify subject ownership
    2. Fetch topics
    3. Run Spacing Algorithm
    4. Save to DB
    """
    # 1. Security check: Verify all subject_ids belong to current_user
    subject_stmt = select(Subject.id).where(
        and_(Subject.id.in_(plan_in.subject_ids), Subject.user_id == current_user.id)
    )
    subject_res = await db.execute(subject_stmt)
    valid_ids = [row[0] for row in subject_res.all()]
    
    if len(valid_ids) != len(plan_in.subject_ids):
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized: One or more subjects do not belong to you."
        )

    # 2. Fetch all selected topics
    stmt = select(Topic).where(Topic.subject_id.in_(valid_ids))
    result = await db.execute(stmt)
    topics = list(result.scalars().all())
    
    if not topics:
        raise HTTPException(status_code=400, detail="No topics found for selected subjects.")

    # 3. Run the algorithmic generation (Constraint Satisfaction)
    generator = PlanGeneratorService(daily_hours=plan_in.daily_hours)
    raw_tasks = generator.generate_raw_schedule(topics, plan_in.start_date)

    # 4. PERSONALIZATION: AI Optimization based on User Profile
    from app.services.ml.profiler import CognitiveProfiler
    profiler = CognitiveProfiler(db)
    user_profile = await profiler.get_user_cognitive_profile(current_user.id)
    
    ai = AIClient()
    # Summarize raw plan for AI (just names and dates) to save tokens
    plan_summary = [{"topic": t["topic_name"], "date": str(t["date"])} for t in raw_tasks[:30]]
    
    try:
        optimization_text = await ai.optimize_schedule(plan_summary, context=user_profile)
    except Exception as e:
        import logging
        logging.getLogger("neuroplan.plans").warning(f"AI Optimization failed: {e}")
        optimization_text = "AI optimization temporarily unavailable. Your plan has been generated using standard neuro-scientific spacing algorithms."

    # 5. Create the StudyPlan record
    db_plan = StudyPlan(
        user_id=current_user.id,
        title=plan_in.title,
        start_date=plan_in.start_date,
        end_date=plan_in.end_date,
        daily_hours=plan_in.daily_hours,
        config={
            **(plan_in.config or {}),
            "optimization_suggestions": optimization_text
        }
    )
    db.add(db_plan)
    await db.flush() # Get the plan ID

    # 6. Save bulk tasks
    for i, task_data in enumerate(raw_tasks):
        db_task = DailyTask(
            plan_id=db_plan.id,
            topic_id=task_data["topic_id"],
            scheduled_date=task_data["date"],
            task_type=task_data["type"],
            planned_minutes=task_data["minutes"],
            status="pending",
            sort_order=i
        )
        db.add(db_task)

    await db.commit()
    await db.refresh(db_plan)
    return db_plan
