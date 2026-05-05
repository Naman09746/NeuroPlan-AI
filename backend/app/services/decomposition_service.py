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
        """Synchronous wrapper for legacy support or small subjects."""
        return await self._run_decomposition(user_id, subject_id, context)

    async def decompose_subject_task(
        self, user_id: UUID, subject_id: UUID, context: str = ""
    ):
        """Background task for long-running decomposition."""
        from app.models.subject import Subject
        from datetime import datetime, timezone
        
        # 1. Mark as decomposing
        stmt = select(Subject).where(Subject.id == subject_id)
        res = await self.db.execute(stmt)
        subject = res.scalar_one_or_none()
        if subject:
            subject.is_decomposing = True
            await self.db.commit()
            
        try:
            # 2. Run the actual work
            await self._run_decomposition(user_id, subject_id, context)
        finally:
            # 3. Mark as finished
            res = await self.db.execute(stmt)
            subject = res.scalar_one_or_none()
            if subject:
                subject.is_decomposing = False
                subject.last_decomposed_at = datetime.now(timezone.utc)
                await self.db.commit()

    async def _run_decomposition(
        self, user_id: UUID, subject_id: UUID, context: str = ""
    ) -> List[Topic]:
        """Internal logic for decomposition."""
        # 1. Verify ownership
        stmt = select(Subject).where(
            Subject.id == subject_id, Subject.user_id == user_id
        )
        result = await self.db.execute(stmt)
        subject = result.scalar_one_or_none()
        if not subject:
            raise ValueError("Subject not found or unauthorized")

        # 1.1 Idempotency Check: Don't decompose twice if already done
        topic_count_stmt = select(Topic.id).where(Topic.subject_id == subject_id).limit(1)
        existing_res = await self.db.execute(topic_count_stmt)
        if existing_res.scalar_one_or_none() and not context.startswith("FORCE_REDO"):
            logger.info(f"Subject {subject_id} already decomposed. Skipping.")
            return await self._get_topics(subject_id)

        # Handle FORCE_REDO
        if context.startswith("FORCE_REDO"):
            from sqlalchemy import delete
            await self.db.execute(delete(Topic).where(Topic.subject_id == subject_id))
            context = context.replace("FORCE_REDO", "").strip()

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
            context=context,
            mastery_scores={str(k): v for k, v in mastery_snapshot.items()}, # Convert UUIDs to strings for JSON
            target_level=subject.target_level
        )

        if not raw_subtopics:
            raise ValueError(
                "AI decomposition failed. Please ensure the local model is running or valid fallback API keys are configured."
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

        return await self._get_topics(subject_id)

    async def _get_topics(self, subject_id: UUID) -> List[Topic]:
        """Helper to fetch topics for a subject."""
        stmt = (
            select(Topic)
            .where(Topic.subject_id == subject_id)
            .order_by(Topic.sort_order.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
