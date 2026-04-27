from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics_engine import AnalyticsService
from app.models.user import User
from sqlalchemy import select

class CognitiveProfiler:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics = AnalyticsService(db)

    async def get_user_cognitive_profile(self, user_id: UUID) -> str:
        """
        Gathers user performance data and preferences into a text summary for LLM context.
        """
        # 1. Fetch Preferences
        stmt = select(User).where(User.id == user_id)
        res = await self.db.execute(stmt)
        user = res.scalar_one_or_none()
        
        prefs = user.preferences if user else {}
        learning_style = prefs.get("learning_style", "Balanced")
        focus_duration = prefs.get("focus_duration", "50 min")
        
        # 2. Fetch Performance Stats
        knowledge = await self.analytics.get_knowledge_heatmap(user_id)
        overview = await self.analytics.get_overview_stats(user_id)
        
        # 3. Format performance string
        perf_summary = []
        for item in knowledge:
            perf_summary.append(f"{item['subject']}: {item['mastery']}% mastery")
        
        perf_str = ", ".join(perf_summary) if perf_summary else "No historical data yet."
        
        profile = (
            f"Learning Style: {learning_style}. "
            f"Preferred Session Duration: {focus_duration}. "
            f"Historical Performance: {perf_str}. "
            f"Overall Completion Rate: {overview['completion_rate']}%."
        )
        
        return profile
