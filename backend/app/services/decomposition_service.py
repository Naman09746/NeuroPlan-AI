"""
Decomposition Service: Orchestrates AI-powered subject breakdown.
Takes a subject_id, calls AI, and bulk-creates Topics with metadata.
"""
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.subject import Subject
from app.models.topic import Topic
from app.services.ai_client import AIClient
from app.services.ml.profiler import CognitiveProfiler
from app.services.ml.knowledge_tracer import KnowledgeTracerService
import logging

logger = logging.getLogger("neuroplan.decomposition")

class DecompositionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai = AIClient()
        self.profiler = CognitiveProfiler(db)
        self.tracer = KnowledgeTracerService(db)

    async def decompose_subject(
        self, user_id: UUID, subject_id: UUID, context: str = ""
    ) -> List[Topic]:
        """
        Full pipeline with DKT-informed decomposition.
        """
        # 1. Verify ownership
        stmt = select(Subject).where(
            Subject.id == subject_id, Subject.user_id == user_id
        )
        result = await self.db.execute(stmt)
        subject = result.scalar_one_or_none()
        if not subject:
            raise ValueError("Subject not found or unauthorized")

        # 2. Fetch Personalization Context
        user_profile = await self.profiler.get_user_cognitive_profile(user_id)
        
        # Get historical topics to check mastery (across all subjects)
        all_topics_stmt = select(Topic.id).join(Subject).where(Subject.user_id == user_id)
        all_t_res = await self.db.execute(all_topics_stmt)
        all_t_ids = all_t_res.scalars().all()
        
        mastery_snapshot = await self.tracer.get_all_mastery_predictions(user_id, all_t_ids) if all_t_ids else {}

        # 3. Call AI with full context
        raw_subtopics = await self.ai.decompose_subject(
            subject_name=subject.name, 
            profile=user_profile,
            mastery_scores={str(k): v for k, v in mastery_snapshot.items()} # Convert UUIDs to strings for JSON
        )

        if not raw_subtopics:
            raise ValueError(
                "AI decomposition returned no results."
            )

        # 4. Create Topic records
        db_topics = []
        for i, st in enumerate(raw_subtopics):
            topic = Topic(
                subject_id=subject_id,
                name=st.get("name", f"Subtopic {i+1}"),
                difficulty=st.get("difficulty", "medium"),
                estimated_hours=float(st.get("estimated_hours", 2.0)),
                knowledge_level=0.0,
                is_completed=False,
                sort_order=st.get("sort_order", i),
                prerequisites=st.get("prerequisites", []),
                key_concepts=st.get("key_concepts", []),
            )
            db_topics.append(topic)

        self.db.add_all(db_topics)
        await self.db.commit()

        # Re-fetch to return
        stmt = (
            select(Topic)
            .where(Topic.subject_id == subject_id)
            .order_by(Topic.sort_order.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
