from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, subjects, topics, tasks, plans, reschedule, analytics, tests, study_cards, probe, onboarding

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(reschedule.router, prefix="/reschedule", tags=["reschedule"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(study_cards.router, prefix="/study-cards", tags=["study-cards"])
api_router.include_router(probe.router, prefix="/probe", tags=["probe"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
