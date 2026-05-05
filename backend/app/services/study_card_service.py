import os
import sys
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.topic import Topic
from app.models.subject import Subject
from app.models.study_card import StudyCard
from app.services.ai_client import AIClient
from app.services.ml.profiler import CognitiveProfiler
from app.services.ml.knowledge_tracer import KnowledgeTracerService
from app.config import settings
import logging

# RAG Integration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from ml.rag.retriever import StudyContentRetriever

logger = logging.getLogger("neuroplan.study_cards")

class StudyCardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai = AIClient()
        self.retriever = StudyContentRetriever(settings.CHROMADB_PATH)
        self.profiler = CognitiveProfiler(db)
        self.tracer = KnowledgeTracerService(db)

    async def get_or_generate(self, topic_id: UUID, user_id: UUID) -> Optional[StudyCard]:
        """
        Lazy generation pattern grounded in RAG and DKT.
        """
        # Check if card already exists
        stmt = select(StudyCard).where(StudyCard.topic_id == topic_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        # Fetch topic with subject info
        topic_stmt = (
            select(Topic)
            .options(selectinload(Topic.subject))
            .where(Topic.id == topic_id)
        )
        topic_res = await self.db.execute(topic_stmt)
        topic = topic_res.scalar_one_or_none()
        if not topic:
            return None

        # Verify ownership through subject
        if topic.subject.user_id != user_id:
            return None

        # 1. Gather Personalization Context
        profile_summary = await self.profiler.get_user_cognitive_profile(user_id)
        topic_mastery = await self.tracer.predict_mastery(user_id, topic_id)
        
        # 2. RAG Retrieval: Grounding the AI
        context = self.retriever.retrieve_context(topic.name, topic.subject.name)
        
        formatted_profile = f"{profile_summary}\n\nREFERENCE MATERIAL:\n{context}" if context else profile_summary

        # 3. Generate with AI
        card_data = await self.ai.generate_study_card(
            topic_name=topic.name,
            subject_name=topic.subject.name,
            profile=formatted_profile,
            topic_mastery=topic_mastery
        )

        # Save to DB
        card = StudyCard(
            topic_id=topic_id,
            summary=card_data.get("summary", ""),
            key_concepts=card_data.get("key_concepts", []),
            formulas=card_data.get("formulas", []),
            study_tips=card_data.get("study_tips", []),
            resources=card_data.get("resources", []),
            practice_problems=card_data.get("practice_problems", []),
            ai_model_used=self.ai.custom_model if self.ai.custom_client else "generic"
        )
        self.db.add(card)
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def regenerate(self, topic_id: UUID, user_id: UUID) -> Optional[StudyCard]:
        """Force regenerate a study card (user requests fresh content)."""
        stmt = select(StudyCard).where(StudyCard.topic_id == topic_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            await self.db.delete(existing)
            await self.db.commit()

        return await self.get_or_generate(topic_id, user_id)

    async def stream_generation(self, topic_id: UUID, user_id: UUID):
        """Stream the AI generation process."""
        # 1. Fetch topic and context
        topic_stmt = select(Topic).options(selectinload(Topic.subject)).where(Topic.id == topic_id)
        topic_res = await self.db.execute(topic_stmt)
        topic = topic_res.scalar_one_or_none()
        if not topic or topic.subject.user_id != user_id:
            yield "data: Error: Unauthorized or Topic not found\n\n"
            return

        profile_summary = await self.profiler.get_user_cognitive_profile(user_id)
        topic_mastery = await self.tracer.predict_mastery(user_id, topic_id)
        context = self.retriever.retrieve_context(topic.name, topic.subject.name)
        formatted_profile = f"{profile_summary}\n\nREFERENCE MATERIAL:\n{context}" if context else profile_summary

        prompt = f"Topic: {topic.name}\nSubject: {topic.subject.name}\nMastery: {topic_mastery}\nContext: {formatted_profile}"
        system_msg = "Generate a structured study card JSON for this topic. Use the standard NeuroPlan schema."
        
        async for chunk in self.ai.stream_ai(prompt, system_msg):
            yield f"data: {chunk}\n\n"
