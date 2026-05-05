from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.study_plan import StudyPlan
from app.models.daily_task import DailyTask
from app.models.progress_log import ProgressLog
from app.models.reschedule_event import RescheduleEvent
from app.models.test_session import TestSession
from app.models.study_card import StudyCard
from app.models.coaching_event import CoachingEvent

# All models must be imported here for Alembic to detect them
__all__ = [
    "User",
    "Subject",
    "Topic",
    "StudyPlan",
    "DailyTask",
    "ProgressLog",
    "RescheduleEvent",
    "TestSession",
    "StudyCard",
    "CoachingEvent"
]
